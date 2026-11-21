from raven_mcs.aggregation.method_policy import FORMAL_GATE_MODE, get_method_policy, resolve_method


def test_r1m_raven_mcs_formal_alias() -> None:
    assert resolve_method("raven_mcs") == "raven_mcs"
    assert resolve_method("raven_mcs_formal") == "raven_mcs"
    assert get_method_policy("raven_mcs").gate_mode == FORMAL_GATE_MODE
    assert get_method_policy("raven_mcs_formal") == get_method_policy("raven_mcs")
    assert get_method_policy("raven_mcs").paper_method is True
