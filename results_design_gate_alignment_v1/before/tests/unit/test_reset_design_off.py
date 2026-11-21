from raven_mcs.sag.r1l_design import DESIGN_OFF, formal_decide_gate_and_design


def test_reset_design_off() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "RESET", "C_LCB": 0.99, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 0
    assert rec["Design_t"] == 0
    assert rec["design_branch"] == DESIGN_OFF
