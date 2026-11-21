from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_sampling_distortion_metric() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_SAMPLING_DISTORTION_SUMMARY.csv")
    assert {"raw_mean_risk_set_size", "e3_mean_risk_set_size"} <= set(frame.columns)
    assert (frame["raw_mean_risk_set_size"] > frame["e3_mean_risk_set_size"]).all()
