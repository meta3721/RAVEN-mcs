from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_raven_mcs_resolves_to_aggregate_coverage() -> None:
    assert get_method_policy("raven_mcs").gate_mode == "aggregate_coverage"
    assert resolve_method("raven_mcs") != "raven"
