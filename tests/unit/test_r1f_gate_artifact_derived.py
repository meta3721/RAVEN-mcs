"""Gate report must be derived from artifacts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_r1f_gate_artifact_derived() -> None:
    gate = json.loads((ROOT / "results_sag_g1/round_r1f/summary/R1F_GATE_REPORT.json").read_text(encoding="utf-8"))
    assert len(gate.get("gates", [])) >= 20
    verdict = json.loads((ROOT / "results_sag_g1/round_r1f/summary/R1F_VERDICT.json").read_text(encoding="utf-8"))
    assert gate.get("verdict") == verdict.get("executive_verdict")
