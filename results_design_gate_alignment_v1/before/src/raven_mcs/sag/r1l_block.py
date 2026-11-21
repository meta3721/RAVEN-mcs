"""Frozen predictor snapshot per certified calibration block.

Refit is allowed only after RESET, using completed past data. The current
window is never in its own calibration buffer. Operational CERTIFIED does
not prove Assumption A.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from raven_mcs.sag.r1l_conformal import c_lcb, finite_sample_conformal_quantile, gate_on
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, TAU_COV
from raven_mcs.sag.r1l_state import next_state


@dataclass(frozen=True)
class PredictorSnapshot:
    snapshot_id: str
    block_id: int
    frozen_parameter: float
    frozen: bool = True
    fit_n: int = 0

    def predict(self, _z_t: Any = None) -> float:
        if not self.frozen:
            raise RuntimeError("predictor snapshot is not frozen")
        return float(self.frozen_parameter)


def fit_predictor_snapshot(
    completed_past: Sequence[float],
    *,
    block_id: int,
) -> PredictorSnapshot:
    """Fit using only completed past windows. Current window is excluded."""
    xs = [float(x) for x in completed_past if np.isfinite(float(x))]
    mu = float(np.mean(xs)) if xs else 0.0
    return PredictorSnapshot(
        snapshot_id=f"block{int(block_id)}_frozen_mean",
        block_id=int(block_id),
        frozen_parameter=mu,
        frozen=True,
        fit_n=len(xs),
    )


def scores_under_frozen_snapshot(
    realized: Sequence[float],
    snapshot: PredictorSnapshot,
) -> list[float]:
    hat = snapshot.predict()
    return [float(hat) - float(c) for c in realized if np.isfinite(float(c))]


@dataclass
class BlockMachine:
    block_id: int = 0
    regime_id: str = "g0"
    state: str = "WARMUP"
    calibration_buffer: list[float] = field(default_factory=list)
    snapshot: PredictorSnapshot | None = None
    refit_count: int = 0
    had_active_certified_regime: bool = False

    def predictor_snapshot_id(self) -> str:
        if self.snapshot is None:
            return ""
        return self.snapshot.snapshot_id

    def _ensure_frozen_snapshot(self) -> PredictorSnapshot:
        if self.snapshot is None:
            self.snapshot = fit_predictor_snapshot([], block_id=self.block_id)
            self.refit_count += 1
        if not self.snapshot.frozen:
            raise RuntimeError("in-block predictor must stay frozen")
        if int(self.snapshot.block_id) != int(self.block_id):
            raise RuntimeError("snapshot block_id mismatch")
        return self.snapshot

    def refit_forbidden_in_current_block(self) -> None:
        raise RuntimeError("refit is forbidden in WARMUP/CERTIFIED; only after RESET")

    def reset_and_open_next_block(self, completed_past: Sequence[float]) -> dict[str, Any]:
        """RESET: clear buffer, freeze a new snapshot from completed past only, WARMUP."""
        self.block_id = int(self.block_id) + 1
        self.calibration_buffer = []
        self.snapshot = fit_predictor_snapshot(completed_past, block_id=self.block_id)
        self.refit_count += 1
        self.state = "WARMUP"
        self.had_active_certified_regime = False
        return {
            "certificate_state": "RESET",
            "block_id": int(self.block_id),
            "predictor_snapshot_id": self.predictor_snapshot_id(),
            "regime_id": self.regime_id,
            "n_cal": 0,
            "C_LCB": 0.0,
            "Gate": False,
            "Gate_label": "OFF",
            "calibration_buffer_cleared": True,
            "refit_after_reset": True,
        }

    def prewindow_step(
        self,
        *,
        regime_change_detected: bool,
        completed_past_for_refit: Sequence[float],
        alpha: float = ALPHA,
        tau_cov: float = TAU_COV,
    ) -> dict[str, Any]:
        if regime_change_detected:
            return self.reset_and_open_next_block(completed_past_for_refit)

        snap = self._ensure_frozen_snapshot()
        scores = list(self.calibration_buffer)
        c_hat = snap.predict()
        q, n_cal, warmup_q = finite_sample_conformal_quantile(scores, alpha=alpha)
        state = next_state(
            regime_certified=True,
            n_cal=n_cal,
            had_active_certified_regime=self.had_active_certified_regime,
        )
        if warmup_q or n_cal < int(N_MIN) or state != "CERTIFIED":
            self.state = "WARMUP"
            return {
                "certificate_state": "WARMUP",
                "block_id": int(self.block_id),
                "predictor_snapshot_id": snap.snapshot_id,
                "regime_id": self.regime_id,
                "n_cal": int(n_cal),
                "C_hat": float(c_hat),
                "q": float("nan"),
                "C_LCB": 0.0,
                "Gate": False,
                "Gate_label": "OFF",
                "assumption_A_proved_by_state": False,
            }
        self.state = "CERTIFIED"
        self.had_active_certified_regime = True
        lower = c_lcb(c_hat, q)
        on = gate_on(lower, tau_cov)
        return {
            "certificate_state": "CERTIFIED",
            "block_id": int(self.block_id),
            "predictor_snapshot_id": snap.snapshot_id,
            "regime_id": self.regime_id,
            "n_cal": int(n_cal),
            "C_hat": float(c_hat),
            "q": float(q),
            "C_LCB": float(lower),
            "Gate": bool(on),
            "Gate_label": "ON" if on else "OFF",
            "assumption_A_proved_by_state": False,
            "theorem_conditional_on_assumption_A": True,
        }

    def append_completed_window(self, realized_c: float) -> None:
        """Current window may enter the buffer only after it completes."""
        if not np.isfinite(float(realized_c)):
            return
        snap = self._ensure_frozen_snapshot()
        score = float(snap.predict()) - float(realized_c)
        self.calibration_buffer.append(score)
