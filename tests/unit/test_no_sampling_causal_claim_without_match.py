from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_no_sampling_causal_claim_without_match() -> None:
    payload = json.loads((ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_ROOT_CAUSE_VERDICT.json").read_text(encoding="utf-8"))
    if payload.get("sampling_caused_ceiling_strict"):
        assert payload["verdict"] == "STRONG_CROSS_TIME_MIXING_CAUSAL_EVIDENCE"
        rates = payload["exact_match_rate_by_dataset"]
        assert min(rates.values()) >= 0.80
