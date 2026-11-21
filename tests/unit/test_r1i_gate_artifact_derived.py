from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_r1i_gate_artifact_derived() -> None:
    gate = json.loads((ROOT / "results_sag_g1/round_r1i/summary/R1I_GATE_REPORT.json").read_text(encoding="utf-8"))
    verdict = json.loads((ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json").read_text(encoding="utf-8"))
    assert len(gate["gates"]) >= 25
    assert gate["verdict"] == verdict["executive_verdict"]
    ids = [g["gate_id"] for g in gate["gates"]]
    assert ids[0] == "R1I-S0" and ids[-1] == "R1I-S24"
