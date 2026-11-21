from raven_mcs.sag.r1k_aggregate import agg_valid

def test_aggregate_validity_builder() -> None:
    assert agg_valid(0.01, 0.02) is True
    assert agg_valid(0.05, 0.01) is False
