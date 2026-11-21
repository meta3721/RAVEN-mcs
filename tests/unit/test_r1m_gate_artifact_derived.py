import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "results_sag_g1/round_r1m/gates/R1M_GATE_REPORT.json"


def test_r1m_gate_artifact_derived() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    gates = payload["gates"]
    ids = [g["id"] for g in gates]
    assert ids[0] == "R1M-S0"
    assert ids[-1] == "R1M-S35"
    assert len(ids) == 36
    for g in gates:
        assert "pass" in g
        assert "evidence" in g
        assert g["evidence"]
