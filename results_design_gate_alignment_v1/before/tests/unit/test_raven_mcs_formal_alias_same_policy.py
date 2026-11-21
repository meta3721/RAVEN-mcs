from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_raven_mcs_formal_alias_same_policy() -> None:
    assert resolve_method("raven_mcs_formal") == resolve_method("raven_mcs")
    assert get_method_policy("raven_mcs_formal").gate_mode == "aggregate_coverage"
