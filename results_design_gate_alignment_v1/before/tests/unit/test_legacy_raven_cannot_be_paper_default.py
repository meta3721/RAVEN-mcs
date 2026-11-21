from raven_mcs.aggregation.method_policy import PAPER_METHOD_KEY, get_method_policy


def test_legacy_raven_cannot_be_paper_default() -> None:
    pol = get_method_policy("raven")
    assert pol.legacy_only is True
    assert pol.paper_method is False
    assert pol.gate_mode == "always_on"
    assert PAPER_METHOD_KEY != "raven"
    assert get_method_policy("raven_mcs").paper_method is True
