from raven_mcs.sag.r1l_design import DESIGN_ON, formal_decide_gate_and_design


def test_certified_above_tau_design_on() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 1
    assert rec["Design_t"] == 1
    assert rec["design_branch"] == DESIGN_ON
