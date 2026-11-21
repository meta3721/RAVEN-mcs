from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_r1h_gate_artifact_derived() -> None:
    gate = json.loads((ROOT / "results_sag_g1/round_r1h/summary/R1H_GATE_REPORT.json").read_text(encoding="utf-8"))
    verdict = json.loads((ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json").read_text(encoding="utf-8"))
    assert len(gate["gates"]) >= 26
    assert gate["verdict"] == verdict["executive_verdict"]
