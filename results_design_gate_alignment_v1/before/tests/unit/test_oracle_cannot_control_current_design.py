from raven_mcs.sag.r1l_design import formal_decide_gate_and_design


def test_oracle_cannot_control_current_design() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "WARMUP", "C_LCB": 0.0, "tau_cov": 0.05},
        oracle_safe=1,
        current_C=1.0,
    )
    assert rec["Gate_t"] == 0
    assert rec["Design_t"] == 0
    assert rec["oracle_controls_design"] is False
    assert rec["current_C_controls_design"] is False
