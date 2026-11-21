from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_source_snapshot_complete() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_SOURCE_SNAPSHOT_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
    assert "generator" in set(frame["role"])
