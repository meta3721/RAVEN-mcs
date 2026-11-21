"""Mock Cases A–D for raven_mcs vs isolated legacy. Not an experiment."""

from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method
from raven_mcs.sag.r1l_design import DESIGN_OFF, DESIGN_ON, formal_decide_gate_and_design


def test_mock_raven_mcs_case_a_gate_off() -> None:
    assert resolve_method("raven_mcs") == "raven_mcs"
    rec = formal_decide_gate_and_design({"certificate_state": "WARMUP", "C_LCB": 0.0})
    assert rec["Gate_t"] == 0 and rec["Design_t"] == 0
    assert rec["design_branch"] == DESIGN_OFF


def test_mock_raven_mcs_case_b_gate_on() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
    )
    assert rec["Gate_t"] == 1 and rec["Design_t"] == 1
    assert rec["design_branch"] == DESIGN_ON


def test_mock_raven_mcs_case_c_no_dataset_flag() -> None:
    rec = formal_decide_gate_and_design(
        {"certificate_state": "CERTIFIED", "C_LCB": 0.06, "tau_cov": 0.05},
        dataset="uair",
        dataset_design_flag=0,
    )
    assert rec["Design_t"] == 1
    assert rec["dataset_name_controls_design"] is False
    assert get_method_policy("raven_mcs").gate_mode == "aggregate_coverage"


def test_mock_case_d_legacy_always_on_isolated() -> None:
    legacy = get_method_policy("raven_legacy_always_on")
    formal = get_method_policy("raven_mcs")
    assert legacy.gate_mode == "always_on"
    assert legacy.legacy_only is True
    assert formal.gate_mode == "aggregate_coverage"
    assert formal.legacy_only is False
