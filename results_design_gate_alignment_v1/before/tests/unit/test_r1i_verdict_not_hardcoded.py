from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "READY_FOR_DYNAMIC_CERTIFICATE_STRESS_AUDIT",
    "READY_FOR_LIMITED_DYNAMIC_CERTIFICATE_STRESS_AUDIT",
    "R1I_STRESS_BOUNDARY_NOT_USABLE",
    "R1I_STRESS_IMPLEMENTATION_FAILURE",
}

def test_r1i_verdict_not_hardcoded() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1i.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
