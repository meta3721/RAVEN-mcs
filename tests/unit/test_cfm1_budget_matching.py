from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_budget_matching() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_MATCHING_AUDIT.csv")
    assert {"cf0_sample_count", "cfm1_sample_count", "exact_budget_match"} <= set(frame.columns)
    assert frame["exact_budget_match"].notna().all()
