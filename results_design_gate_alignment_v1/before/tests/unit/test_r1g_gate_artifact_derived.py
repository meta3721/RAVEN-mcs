from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def test_r1g_gate_artifact_derived() -> None:
    gate = json.loads((ROOT / "results_sag_g1/round_r1g/summary/R1G_GATE_REPORT.json").read_text(encoding="utf-8"))
    verdict = json.loads((ROOT / "results_sag_g1/round_r1g/summary/R1G_VERDICT.json").read_text(encoding="utf-8"))
    assert len(gate["gates"]) >= 25
    assert gate["verdict"] == verdict["executive_verdict"]
