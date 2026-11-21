from pathlib import Path
from raven_mcs.sag.r1k_spec import AGG_FEATURE_NAMES
from raven_mcs.sag.r1k_aggregate import aggregate_features

def test_aggregate_feature_causal() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1k_aggregate.py").read_text(encoding="utf-8")
    assert "windows < r" in src
    feat = aggregate_features([0.1, 0.2], hour_of_day=3, weekend_flag=0, availability_level=0.4)
    assert set(feat) == set(AGG_FEATURE_NAMES)
    assert "current_mask" not in feat
