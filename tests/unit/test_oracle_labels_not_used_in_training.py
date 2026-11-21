from pathlib import Path
from raven_mcs.sag.r1j_features import pair_features

def test_oracle_labels_not_used_in_training() -> None:
    src = (Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1j_predictor.py").read_text(encoding="utf-8")
    assert "Y_oracle" not in src
    feat = pair_features(hist_active=[1], hist_mass=[0.02], hour_of_day=4, weekend_flag=0, availability_level=0.8)
    assert "Y_oracle" not in feat
    assert "C_oracle_safe" not in feat
