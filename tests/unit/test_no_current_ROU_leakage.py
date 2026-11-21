from raven_mcs.sag.r1j_features import FORBIDDEN_FEATURE_KEYS, pair_features

def test_no_current_ROU_leakage() -> None:
    feat = pair_features(hist_active=[], hist_mass=[], hour_of_day=0, weekend_flag=1, availability_level=1.0)
    for k in ("current_R", "current_O", "current_U"):
        assert k in FORBIDDEN_FEATURE_KEYS
        assert k not in feat
