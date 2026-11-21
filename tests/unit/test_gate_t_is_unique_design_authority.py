"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.sag.r1l_design import FORMAL_GATE_MODE, legacy_decide_gate_and_design


def test_legacy_gate_t_is_unique_design_authority() -> None:
    rec = legacy_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
        dataset_design_flag=0,
        design_enabled=False,
    )
    assert rec["Gate_t"] == 1
    assert rec["Design_t"] == 1
    assert rec["authority"] == "aggregate_coverage_certificate"
    assert rec["static_flag_controls_design"] is False
    pol = get_method_policy("raven_coverage_legacy")
    assert pol.gate_mode == FORMAL_GATE_MODE
