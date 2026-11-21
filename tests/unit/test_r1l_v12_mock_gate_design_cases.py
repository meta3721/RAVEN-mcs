"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
"""Mock Cases A–D: interface only, not an experiment."""

from raven_mcs.sag.r1l_design import (
    DESIGN_OFF,
    DESIGN_ON,
    apply_formal_design_zeta,
    legacy_decide_gate_and_design,
)
import numpy as np


def test_legacy_mock_case_a_warmup() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "WARMUP", "C_LCB": 0.0, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 0 and rec["design_branch"] == DESIGN_OFF


def test_legacy_mock_case_b_reset() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "RESET", "C_LCB": 0.0, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 0 and rec["design_branch"] == DESIGN_OFF


def test_legacy_mock_case_c_certified_below_tau() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.04, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 0 and rec["design_branch"] == DESIGN_OFF


def test_legacy_mock_case_d_certified_above_tau() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 1 and rec["design_branch"] == DESIGN_ON
    zeta = apply_formal_design_zeta(np.array([2.0, 3.0]), rec["Gate_t"])
    assert np.allclose(zeta, [2.0, 3.0])
    off = apply_formal_design_zeta(np.array([2.0, 3.0]), 0)
    assert np.allclose(off, [1.0, 1.0])
