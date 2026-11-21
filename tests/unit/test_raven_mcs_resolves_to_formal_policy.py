from raven_mcs.aggregation.method_policy import FORMAL_GATE_MODE, get_method_policy, resolve_method


def test_raven_mcs_resolves_to_formal_policy() -> None:
    assert resolve_method("raven_mcs") == "raven_mcs"
    assert get_method_policy("raven_mcs").design_control == "configured"
    assert get_method_policy("raven_mcs").paper_method is True
