"""WARMUP / CERTIFIED / RESET. RESET and WARMUP both force Gate OFF and C_LCB=0."""

from __future__ import annotations

from typing import Any, Sequence

from raven_mcs.sag.r1l_conformal import c_lcb, finite_sample_conformal_quantile, gate_on
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, TAU_COV


def next_state(*, regime_certified: bool, n_cal: int, had_active_certified_regime: bool) -> str:
    if not regime_certified:
        return "RESET" if had_active_certified_regime else "WARMUP"
    if int(n_cal) < int(N_MIN):
        return "WARMUP"
    return "CERTIFIED"


def certificate_step(
    *,
    regime_certified: bool,
    had_active_certified_regime: bool,
    scores: Sequence[float],
    c_hat: float,
    alpha: float = ALPHA,
    tau_cov: float = TAU_COV,
) -> dict[str, Any]:
    q, n_cal, warmup_q = finite_sample_conformal_quantile(scores, alpha=alpha)
    state = next_state(
        regime_certified=regime_certified,
        n_cal=n_cal,
        had_active_certified_regime=had_active_certified_regime,
    )
    if state != "CERTIFIED" or warmup_q:
        if state == "CERTIFIED":
            state = "WARMUP"
        return {
            "certificate_state": state,
            "C_hat": float(c_hat),
            "n_cal": int(n_cal),
            "q": float("nan"),
            "C_LCB": 0.0,
            "Gate": False,
            "Gate_label": "OFF",
        }
    lower = c_lcb(c_hat, q)
    on = gate_on(lower, tau_cov)
    return {
        "certificate_state": "CERTIFIED",
        "C_hat": float(c_hat),
        "n_cal": int(n_cal),
        "q": float(q),
        "C_LCB": float(lower),
        "Gate": bool(on),
        "Gate_label": "ON" if on else "OFF",
    }
