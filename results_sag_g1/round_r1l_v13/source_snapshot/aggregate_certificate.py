"""Formal SAG coverage certificate: aggregate C_t with WARMUP/CERTIFIED/RESET.

Pairwise simultaneous positive LCBs are diagnostic only. Predictor snapshot
f_b is frozen within a certified block and may be refit only after RESET.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from raven_mcs.sag.r1l_block import (
    fit_predictor_snapshot,
    scores_under_frozen_snapshot,
)
from raven_mcs.sag.r1l_spec import ALPHA, FORMAL_COV_MODE, N_MIN, TAU_COV
from raven_mcs.sag.r1l_state import certificate_step

FORBIDDEN_CURRENT = (
    "current_mask",
    "current_available_entities",
    "current_R",
    "current_O",
    "current_U",
    "current_pi_opp",
    "current_C",
    "current_oracle_safe",
    "future_windows",
)


def realized_aggregate_coverage(
    pi_target: Mapping[tuple[str, str], float],
    opp_mass: Mapping[tuple[str, str], float],
    pi_safe: float,
) -> float:
    """C_t = sum_i pi_i^tar 1{pi_{i,t}^opp >= pi_safe}."""
    total = 0.0
    certified = 0.0
    for key, weight in pi_target.items():
        try:
            w = float(weight)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(w) or w <= 0.0:
            continue
        total += w
        try:
            mass = float(opp_mass.get(key, 0.0))
        except (TypeError, ValueError):
            mass = 0.0
        if np.isfinite(mass) and mass >= float(pi_safe):
            certified += w
    if total <= 0.0:
        return float("nan")
    return float(certified / total)


def lagged_mean_predictor(past_realized: Sequence[float]) -> float:
    """Legal F_{t-}-measurable placeholder. Not the R1m frozen predictor."""
    xs = [float(x) for x in past_realized if np.isfinite(float(x))]
    if not xs:
        return 0.0
    return float(np.mean(xs))


def historical_scores(realized: Sequence[float]) -> list[float]:
    """S_j = C_hat_j - C_j with C_hat_j using only windows strictly before j."""
    scores: list[float] = []
    for j, c_j in enumerate(realized):
        if not np.isfinite(float(c_j)):
            continue
        hat = lagged_mean_predictor(realized[:j])
        scores.append(float(hat) - float(c_j))
    return scores


def _row_realized_c(
    row: Mapping[str, Any],
    pi_target: Mapping[tuple[str, str], float],
    pi_safe: float | None,
) -> float:
    raw = row.get("realized_C_cov")
    try:
        val = float(raw)
        if np.isfinite(val):
            return val
    except (TypeError, ValueError):
        pass
    if pi_safe is None:
        return float("nan")
    from raven_mcs.sag.certificates import opportunity_mass_map

    return realized_aggregate_coverage(pi_target, opportunity_mass_map(row), float(pi_safe))


def formal_aggregate_coverage(
    history: Sequence[Mapping[str, Any]],
    *,
    pi_target: Mapping[tuple[str, str], float],
    pi_safe: float | None,
    regime_certified: bool = True,
    had_active_certified_regime: bool = True,
    c_hat: float | None = None,
    alpha: float = ALPHA,
    tau_cov: float = TAU_COV,
) -> dict[str, Any]:
    """Formal Gate coverage object. No current-window mask/R/O/U/C_t."""
    for row in history:
        illegal = set(row).intersection(FORBIDDEN_CURRENT)
        if illegal:
            raise ValueError(f"forbidden current-window keys in history: {sorted(illegal)}")

    realized = [_row_realized_c(row, pi_target, pi_safe) for row in history]
    realized_finite = [x for x in realized if np.isfinite(x)]
    # Block-0 snapshot is frozen at WARMUP entry from pre-block past only
    # (empty here). In-block outcomes are not used to refit f_b.
    snap = fit_predictor_snapshot([], block_id=0)
    hat = float(c_hat) if c_hat is not None else snap.predict()
    predictor_id = (
        "CONTEXT_OVERRIDE_MEASURABLE_F_TMINUS" if c_hat is not None else snap.snapshot_id
    )
    scores = scores_under_frozen_snapshot(realized_finite, snap)

    step = certificate_step(
        regime_certified=bool(regime_certified),
        had_active_certified_regime=bool(had_active_certified_regime),
        scores=scores,
        c_hat=hat,
        alpha=alpha,
        tau_cov=tau_cov,
    )
    step.update(
        {
            "C_cov_LCB": float(step["C_LCB"]),
            "formal_certificate": FORMAL_COV_MODE,
            "pairwise_formal_core": False,
            "predictor_id": predictor_id,
            "predictor_snapshot_frozen": True,
            "block_id": 0,
            "n_min": int(N_MIN),
            "alpha": float(alpha),
            "tau_cov": float(tau_cov),
            "lower_pi_opp_method": "retired_from_formal_core",
            "C_cov_history_policy": "aggregate_stable_regime_completed_windows_only",
            "n_realized": len(realized_finite),
            "current_window_in_own_calibration": False,
        }
    )
    return step
