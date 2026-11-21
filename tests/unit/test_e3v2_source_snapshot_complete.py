from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_e3v2_source_snapshot_complete() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/source_snapshot/E3V2_SOURCE_SNAPSHOT_MANIFEST.csv")
    assert (frame["sha256"] != "MISSING").all()
    assert "e3_v2_protocol" in set(frame["component"])
