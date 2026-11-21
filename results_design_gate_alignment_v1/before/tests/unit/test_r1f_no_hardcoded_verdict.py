"""Verdict must not be hardcoded in source."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src/raven_mcs/experiments/run_sag_g1_r1f.py"


def test_r1f_no_hardcoded_verdict() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "pass=True" not in text.replace(" ", "")
    assert "derive_final_verdict" in text
    verdict = json.loads((ROOT / "results_sag_g1/round_r1f/summary/R1F_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict.get("executive_verdict") in {
        "READY_FOR_CERTIFICATE_REPAIR",
        "E3_THRESHOLD_MARGINAL",
        "E3_THRESHOLD_INCOMPATIBLE",
        "R1F_EVIDENCE_FAILURE",
    }
