"""MISCOVERAGE_TRIGGERED_RESET_V1. Unique R1m detector. Does not prove Assumption A."""

from __future__ import annotations

from raven_mcs.sag.r1l_spec import NUM_TOL
from raven_mcs.sag.r1m_spec import RESET_RULE_ID


def miscoverage_reset_trigger(
    *,
    state: str,
    c_lcb: float,
    c_t: float,
    tol: float = NUM_TOL,
) -> bool:
    """True iff a completed CERTIFIED window has C_LCB > C_t + tol.

    The violating window stays CERTIFIED. The next window is RESET then new-block WARMUP.
    """
    if str(state) != "CERTIFIED":
        return False
    return float(c_lcb) > float(c_t) + float(tol)


def reset_window_gate_forced_off(state: str) -> bool:
    return str(state) == "RESET"


assert RESET_RULE_ID == "MISCOVERAGE_TRIGGERED_RESET_V1"
