from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_cooccurrence_metric() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_COOCCURRENCE_RETENTION.csv")
    assert {"users_per_window", "active_pairs_per_window", "target_mass_weighted_support"} <= set(frame.columns)
    assert set(frame["regime"]) >= {"raw_natural", "e3v1"}
