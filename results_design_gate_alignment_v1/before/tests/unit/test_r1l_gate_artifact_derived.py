from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]

def test_r1l_gate_artifact_derived() -> None:
    gate = json.loads((ROOT / "results_sag_g1/round_r1l/summary/R1L_GATE_REPORT.json").read_text(encoding="utf-8"))
    verdict = json.loads((ROOT / "results_sag_g1/round_r1l/summary/R1L_VERDICT.json").read_text(encoding="utf-8"))
    ids = [g["gate_id"] for g in gate["gates"]]
    assert ids[0] == "R1L-T0" and "R1L-T19" in ids
    assert gate["verdict"] == verdict["executive_verdict"]
    assert len(gate["gates"]) >= 20
