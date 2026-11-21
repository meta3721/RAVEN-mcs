from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "E3V1_ROOT_CAUSE_CLOSED_E3V2_SPEC_FROZEN",
    "READY_FOR_E3V2_DYNAMIC_CERTIFICATE_AUDIT",
    "E3V2_ORACLE_REGIME_NOT_USABLE",
    "R1G_PROTOCOL_EVIDENCE_FAILURE",
}


def test_r1g_no_hardcoded_verdict() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1g.py").read_text(encoding="utf-8")
    assert "pass=True" not in src.replace(" ", "")
    verdict = json.loads((ROOT / "results_sag_g1/round_r1g/summary/R1G_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["executive_verdict"] in ALLOWED
