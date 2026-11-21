from raven_mcs.aggregation.method_policy import get_method_policy


def test_raven_mcs_not_legacy_static_gate() -> None:
    pol = get_method_policy("raven_mcs")
    assert pol.legacy_only is False
    assert pol.design_control == "configured"
    assert pol.paper_method is True
