from raven_mcs.sag.r1m_spec import FEATURE_NAMES, feature_spec_hash


def test_feature_spec_fixed() -> None:
    assert FEATURE_NAMES[0] == "intercept"
    assert "availability_level" in FEATURE_NAMES
    assert "lag1_C" in FEATURE_NAMES
    assert "lag2_C" in FEATURE_NAMES
    assert "rolling_mean_C_L8" in FEATURE_NAMES
    assert "rolling_trend_C_L8" in FEATURE_NAMES
    assert "hour_sin" in FEATURE_NAMES
    assert "hour_cos" in FEATURE_NAMES
    assert "weekend_flag" in FEATURE_NAMES
    assert "hour_of_day_unit" not in FEATURE_NAMES
    assert "rolling_mean_times_a" not in FEATURE_NAMES
    assert len(feature_spec_hash()) == 64
