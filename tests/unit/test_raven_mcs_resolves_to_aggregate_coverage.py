from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_configured_and_legacy_coverage_resolve_separately() -> None:
    assert get_method_policy("raven_mcs").design_control == "configured"
    assert resolve_method("raven_mcs") != "raven"

    assert get_method_policy("raven_coverage_legacy").gate_mode == "aggregate_coverage"
    assert get_method_policy("raven_coverage_legacy").legacy_only
