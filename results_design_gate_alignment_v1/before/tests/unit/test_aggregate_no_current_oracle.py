from raven_mcs.sag.r1k_spec import AGG_FEATURE_NAMES
from raven_mcs.sag.r1k_aggregate import aggregate_features

def test_aggregate_no_current_oracle() -> None:
    assert "C_oracle" not in AGG_FEATURE_NAMES
    feat = aggregate_features([0.1], hour_of_day=0, weekend_flag=0, availability_level=1.0)
    assert "C_oracle" not in feat
    assert "Y_oracle" not in feat
