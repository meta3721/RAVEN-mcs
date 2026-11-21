from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "R1H_ROOTCAUSE_CLOSED_BOUNDARY_CLOSED",
    "R1H_ROOTCAUSE_PARTIAL_BOUNDARY_CLOSED",
    "R1H_BOUNDARY_INCONCLUSIVE",
    "R1H_EVIDENCE_FAILURE",
}

def test_r1h_no_hardcoded_verdict() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
