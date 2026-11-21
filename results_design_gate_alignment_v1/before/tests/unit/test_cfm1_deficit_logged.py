from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_deficit_logged() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_MATCHING_AUDIT.csv")
    assert "sample_count_deficit" in frame.columns
    assert (frame["sample_count_deficit"] >= 0).all()
