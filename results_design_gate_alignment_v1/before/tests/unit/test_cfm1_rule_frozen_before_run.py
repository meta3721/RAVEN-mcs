from pathlib import Path
from raven_mcs.sag.cfm1 import matching_rule_hash
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_rule_frozen_before_run() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    assert src.find("CFM1_MATCHING_RULE_FREEZE.md") < src.find("for window_id in range(n_e3)")
    stored = (ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_MATCHING_RULE_FREEZE.md").read_text(encoding="utf-8")
    assert matching_rule_hash() in stored
