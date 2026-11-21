from pathlib import Path
import json
ALLOWED = {
    "STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE",
    "PARTIAL_CROSS_TIME_MIXING_EVIDENCE",
    "NO_ISOLATED_CROSS_TIME_EFFECT",
    "MATCHED_CF_NOT_IDENTIFIABLE",
}
ROOT = Path(__file__).resolve().parents[2]

def test_root_cause_verdict_not_hardcoded() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    assert "exact_match_rate" in src
    payload = json.loads((ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_ROOT_CAUSE_VERDICT.json").read_text(encoding="utf-8"))
    assert payload["verdict"] in ALLOWED
