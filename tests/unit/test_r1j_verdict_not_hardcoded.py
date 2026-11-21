from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION",
    "READY_FOR_LIMITED_SAG_1SEED_VALIDATION",
    "R1J_CERTIFICATE_TOO_CONSERVATIVE",
    "R1J_CERTIFICATE_NOT_CALIBRATED",
    "R1J_IMPLEMENTATION_OR_EVIDENCE_FAILURE",
}

def test_r1j_verdict_not_hardcoded() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1j.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1j/summary/R1J_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
