from raven_mcs.aggregation.method_policy import POLICY_MAP, get_method_policy


def test_formal_policy_unique() -> None:
    papers = [k for k, p in POLICY_MAP.items() if p.paper_method]
    assert papers == ["raven_mcs"]
    assert get_method_policy("raven_mcs").design_control == "configured"
    assert sum(1 for p in POLICY_MAP.values() if p.paper_method) == 1
