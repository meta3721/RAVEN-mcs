from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {"FULL_INTERIOR", "FULL_BOUNDARY", "PARTIAL_LEFT", "PARTIAL_RIGHT", "PARTIAL_BOTH", "UNKNOWN_COMPLETENESS"}

def test_window_boundary_status() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT.csv")
    assert set(frame["boundary_status"]) <= ALLOWED
