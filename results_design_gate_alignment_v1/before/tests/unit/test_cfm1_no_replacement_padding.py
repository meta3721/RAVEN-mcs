from pathlib import Path
import pandas as pd
from raven_mcs.sag.cfm1 import matching_rule_payload
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_no_replacement_padding() -> None:
    assert matching_rule_payload()["replacement_padding"] is False
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_MATCHING_AUDIT.csv")
    assert not frame["replacement_padding"].astype(bool).any()
