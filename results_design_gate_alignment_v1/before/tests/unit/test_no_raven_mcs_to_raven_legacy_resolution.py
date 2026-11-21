from raven_mcs.aggregation.method_policy import METHOD_ALIASES, resolve_method


def test_no_raven_mcs_to_raven_legacy_resolution() -> None:
    assert METHOD_ALIASES.get("raven_mcs") != "raven"
    assert "raven_mcs" not in METHOD_ALIASES or METHOD_ALIASES["raven_mcs"] == "raven_mcs"
    assert resolve_method("raven_mcs") == "raven_mcs"
    assert resolve_method("raven_mcs") != "raven"
    assert resolve_method("raven_mcs") != "raven_legacy_always_on"
