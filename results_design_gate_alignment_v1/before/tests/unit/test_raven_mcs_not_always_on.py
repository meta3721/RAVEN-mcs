from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_raven_mcs_not_always_on() -> None:
    assert get_method_policy("raven_mcs").gate_mode != "always_on"
    assert resolve_method("raven_mcs") != resolve_method("raven")
