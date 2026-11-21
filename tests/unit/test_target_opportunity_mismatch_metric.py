from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_target_opportunity_mismatch_metric() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_TARGET_OPPORTUNITY_MISMATCH_SUMMARY.csv")
    assert frame["same_support"].astype(str).str.lower().isin(["true", "1"]).all()
    assert (frame["tv_distance"] >= 0).all()
