from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "THEORY_CLOSURE_PASS",
    "THEORY_CLOSURE_PASS_WITH_OPTIONAL_DRIFT_EXTENSION_PENDING",
    "THEORY_CLOSURE_NOT_READY",
}

def test_r1l_verdict_not_hardcoded() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1l.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1l/summary/R1L_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
