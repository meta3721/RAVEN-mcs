from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method
from raven_mcs.sag.r1l_design import design_from_gate


def test_r1m_no_legacy_gate_bypass() -> None:
    assert get_method_policy("raven_mcs").gate_mode == "aggregate_coverage"
    assert get_method_policy("raven").legacy_only is True
    assert resolve_method("raven_mcs") != "raven"
    assert design_from_gate(0) == 0
    assert design_from_gate(1) == 1
