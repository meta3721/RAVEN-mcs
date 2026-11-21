"""R1l-v1.2 unique Design authority: Design_t := Gate_t.

Formal RAVEN-MCS window-close reads Gate_t from the aggregate coverage
certificate. Dataset name, static Design flags, oracle labels, current C_t,
and the current mask are not Design controls.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from raven_mcs.sag.gate import zeta_tilde
from raven_mcs.sag.r1l_spec import TAU_COV

FORMAL_GATE_MODE = "aggregate_coverage"
LEGACY_GATE_MODES = frozenset({"always_on", "always_off", "policy", "sag"})

DESIGN_ON = "DESIGN_ON"
DESIGN_OFF = "DESIGN_OFF"

FORBIDDEN_DESIGN_CONTROLS = (
    "dataset_name",
    "dataset_id",
    "dataset_design_flag",
    "design_enabled",
    "gated_default",
    "oracle_safe",
    "oracle_safe_t",
    "current_C",
    "current_C_t",
    "current_mask",
    "current_available_entities",
    "current_R",
    "current_O",
    "current_U",
)

PROVENANCE_FIELDS = (
    "dataset",
    "window_id",
    "block_id",
    "predictor_snapshot_id",
    "certificate_state",
    "n_cal",
    "C_hat",
    "q",
    "C_LCB",
    "tau_cov",
    "Gate_t",
    "Design_t",
    "design_branch",
)


def design_from_gate(gate_t: int | bool) -> int:
    """Unique frozen equality: Design_t := Gate_t."""
    return 1 if bool(int(gate_t)) else 0


def design_branch(design_t: int | bool) -> str:
    return DESIGN_ON if int(design_from_gate(design_t)) == 1 else DESIGN_OFF


def gate_from_certificate(
    *,
    certificate_state: str,
    c_lcb: float,
    tau_cov: float = TAU_COV,
) -> int:
    """Gate_t from the aggregate certificate only.

    WARMUP/RESET force OFF. CERTIFIED uses 1{C_LCB >= tau_cov}.
    """
    state = str(certificate_state or "").strip().upper()
    if state in {"WARMUP", "RESET"}:
        return 0
    if state != "CERTIFIED":
        return 0
    try:
        lower = float(c_lcb)
    except (TypeError, ValueError):
        return 0
    if not np.isfinite(lower):
        return 0
    return 1 if lower >= float(tau_cov) else 0


def apply_formal_design_zeta(zeta_d: np.ndarray, gate_t: int | bool) -> np.ndarray:
    """Design-ON uses lagged zeta; Design-OFF falls back to ones. Design_t := Gate_t."""
    return zeta_tilde(np.asarray(zeta_d, dtype=np.float64), int(design_from_gate(gate_t)))


def _as_float(value: Any, default: float = float("nan")) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float(default)
    return out if np.isfinite(out) else float(default)


def formal_decide_gate_and_design(
    diagnostics: Mapping[str, Any] | None = None,
    *,
    tau_cov: float = TAU_COV,
    window_id: int = -1,
    dataset: str | None = None,
    c_cov_lcb: float | None = None,
    oracle_safe: Any = None,
    current_C: Any = None,
    current_mask: Any = None,
    dataset_design_flag: Any = None,
    design_enabled: Any = None,
) -> dict[str, Any]:
    """Unique formal Design decision.

    ``dataset``, oracle, current C_t, current mask, and static flags may be
    recorded or ignored; they never control Gate_t or Design_t.
    """
    del oracle_safe, current_C, current_mask, dataset_design_flag, design_enabled
    diag = dict(diagnostics or {})
    state = str(diag.get("certificate_state") or "WARMUP")
    if c_cov_lcb is not None and np.isfinite(float(c_cov_lcb)):
        c_lcb = float(c_cov_lcb)
    else:
        c_lcb = _as_float(diag.get("C_LCB"), 0.0)
        if not np.isfinite(c_lcb):
            c_lcb = _as_float(diag.get("C_cov_LCB"), 0.0)
        if not np.isfinite(c_lcb):
            c_lcb = 0.0
    tau = _as_float(diag.get("tau_cov"), float(tau_cov))
    if not np.isfinite(tau):
        tau = float(tau_cov)
    gate_t = gate_from_certificate(
        certificate_state=state, c_lcb=c_lcb, tau_cov=tau,
    )
    design_t = design_from_gate(gate_t)
    q_raw = diag.get("q")
    q_val = _as_float(q_raw, float("nan"))
    snap = diag.get("predictor_snapshot_id") or diag.get("predictor_id") or ""
    rec = {
        "dataset": "" if dataset is None else str(dataset),
        "window_id": int(window_id),
        "block_id": int(diag.get("block_id") or 0),
        "predictor_snapshot_id": str(snap),
        "certificate_state": str(state),
        "n_cal": int(diag.get("n_cal") or diag.get("n_realized") or 0),
        "C_hat": _as_float(diag.get("C_hat"), float("nan")),
        "q": q_val,
        "C_LCB": float(c_lcb),
        "tau_cov": float(tau),
        "Gate_t": int(gate_t),
        "Design_t": int(design_t),
        "design_branch": design_branch(design_t),
        "authority": "aggregate_coverage_certificate",
        "design_equals_gate": bool(gate_t == design_t),
        "dataset_name_controls_design": False,
        "oracle_controls_design": False,
        "current_mask_controls_design": False,
        "current_C_controls_design": False,
        "static_flag_controls_design": False,
        "fallback_reason": None if gate_t else "OFF_AGGREGATE_COVERAGE_GATE",
    }
    if rec["design_branch"] == DESIGN_ON and int(rec["Gate_t"]) != 1:
        raise RuntimeError("DESIGN_ON requires Gate_t=1")
    if rec["design_branch"] == DESIGN_OFF and int(rec["Gate_t"]) != 0:
        raise RuntimeError("DESIGN_OFF requires Gate_t=0")
    if int(rec["Gate_t"]) != int(rec["Design_t"]):
        raise RuntimeError("Design_t must equal Gate_t")
    return rec
