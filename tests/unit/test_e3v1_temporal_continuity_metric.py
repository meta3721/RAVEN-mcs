from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_temporal_continuity_metric() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_TEMPORAL_RETENTION_SUMMARY.csv")
    assert "lag1_jaccard" in frame.columns
    raw = frame.loc[frame["regime"] == "raw_natural", "lag1_jaccard"].mean()
    e3 = frame.loc[frame["regime"] == "e3v1", "lag1_jaccard"].mean()
    assert raw > e3
