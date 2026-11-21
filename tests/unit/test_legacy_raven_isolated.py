from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def test_legacy_raven_isolated() -> None:
    legacy = get_method_policy("raven_legacy_always_on")
    hist = get_method_policy("raven")
    formal = get_method_policy("raven_mcs")
    assert legacy.gate_mode == "always_on"
    assert hist.gate_mode == "always_on"
    assert legacy.legacy_only is True
    assert hist.legacy_only is True
    assert formal.design_control == "configured"
    assert resolve_method("raven_legacy_always_on") != "raven_mcs"
    assert resolve_method("raven_full_design_legacy") == "raven_legacy_always_on"
