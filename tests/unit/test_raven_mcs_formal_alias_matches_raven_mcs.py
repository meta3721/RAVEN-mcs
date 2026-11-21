from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_raven_mcs_formal_alias_matches_raven_mcs() -> None:
    assert resolve_method("raven_mcs_formal") == "raven_mcs"
    assert get_method_policy("raven_mcs_formal") == get_method_policy("raven_mcs")
    assert get_method_policy("raven_formal") == get_method_policy("raven_mcs")
