from raven_mcs.sag.r1k_aggregate import c_lcb

def test_aggregate_lcb_formula() -> None:
    assert c_lcb(0.08, 0.03) == 0.05
    assert c_lcb(0.01, 0.03) == 0.0
