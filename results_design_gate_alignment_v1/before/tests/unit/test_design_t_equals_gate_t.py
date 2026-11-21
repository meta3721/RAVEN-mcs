from raven_mcs.sag.r1l_design import design_from_gate, formal_decide_gate_and_design


def test_design_t_equals_gate_t() -> None:
    assert design_from_gate(0) == 0
    assert design_from_gate(1) == 1
    assert design_from_gate(True) == 1
    for state, c_lcb in (("WARMUP", 0.0), ("RESET", 0.0), ("CERTIFIED", 0.04), ("CERTIFIED", 0.06)):
        rec = formal_decide_gate_and_design(
            {"certificate_state": state, "C_LCB": c_lcb, "tau_cov": 0.05},
        )
        assert rec["Gate_t"] == rec["Design_t"]
        assert rec["design_equals_gate"] is True
