from pathlib import Path
import pandas as pd
from raven_mcs.sag.cfm1 import matching_rule_payload
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_no_cross_time_fill() -> None:
    assert matching_rule_payload()["cross_time_fill"] is False
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_MATCHING_AUDIT.csv")
    assert not frame["cross_time_fill"].astype(bool).any()
