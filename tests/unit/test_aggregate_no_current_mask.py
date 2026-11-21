from raven_mcs.sag.r1k_aggregate import aggregate_features

def test_aggregate_no_current_mask() -> None:
    feat = aggregate_features([0.08], hour_of_day=1, weekend_flag=1, availability_level=0.2)
    assert "current_mask" not in feat
    assert "available_entities" not in feat
