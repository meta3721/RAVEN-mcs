"""R1f must not run new calibration."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_calibration_repair() -> None:
    freeze = ROOT / "results_sag_g1/round_r1f/audit/R1F_FREEZE_AUDIT.json"
    payload = json.loads(freeze.read_text(encoding="utf-8"))
    assert payload.get("calibration_repair_executed") is False
    r1g = ROOT / "results_sag_g1/round_r1g/summary/R1G_VERDICT.json"
    if r1g.is_file():
        payload = json.loads(r1g.read_text(encoding="utf-8"))
        assert payload.get("calibration_repair_executed") is False
    r1h = ROOT / "results_sag_g1/round_r1h/summary/R1H_VERDICT.json"
    if r1h.is_file():
        payload = json.loads(r1h.read_text(encoding="utf-8"))
        assert payload.get("calibration_repair_executed") is False
