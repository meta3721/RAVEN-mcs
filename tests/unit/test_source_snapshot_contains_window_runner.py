"""Historical Design=Gate behavior only; configured behavior is tested in test_configured_design_runner."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_source_snapshot_contains_window_runner() -> None:
    frame = pd.read_csv(
        ROOT / "results_sag_g1/round_r1l_v12/source_snapshot/R1L_V12_SOURCE_SNAPSHOT_MANIFEST.csv"
    )
    paths = " ".join(frame["source_path"].astype(str).tolist())
    assert "window_runner.py" in paths
    snap = ROOT / "results_sag_g1/round_r1l_v12/source_snapshot/window_runner.py"
    assert snap.is_file()
    text = snap.read_text(encoding="utf-8")
    assert "formal_decide_gate_and_design" in text
