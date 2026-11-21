from raven_mcs.aggregation.method_policy import get_method_policy


def test_raven_mcs_not_legacy() -> None:
    assert get_method_policy("raven_mcs").legacy_only is False
    assert get_method_policy("raven").legacy_only is True
