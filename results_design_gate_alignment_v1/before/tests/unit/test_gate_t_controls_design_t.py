from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.sag.r1l_design import formal_decide_gate_and_design


def test_gate_t_controls_design_t() -> None:
    assert get_method_policy("raven_mcs").gate_mode == "aggregate_coverage"
    off = formal_decide_gate_and_design({"certificate_state": "WARMUP", "C_LCB": 0.0})
    on = formal_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
    )
    assert off["Gate_t"] == off["Design_t"] == 0
    assert on["Gate_t"] == on["Design_t"] == 1
