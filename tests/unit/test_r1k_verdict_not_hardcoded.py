from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED",
    "PAIRWISE_IMPLEMENTATION_REPAIR_RECOMMENDED",
    "PAIRWISE_ARCHITECTURE_REMAINS_VIABLE",
    "R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE",
    "R1K_IMPLEMENTATION_OR_EVIDENCE_FAILURE",
}

def test_r1k_verdict_not_hardcoded() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1k.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1k/summary/R1K_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
