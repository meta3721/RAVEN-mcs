"""Soft artifact checks for the E3 numerical-integrity clean canary."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_numerical_integrity_clean_canary_fix_r1"


def test_stop_status_is_present_when_prepared() -> None:
    stop = ART / "E3_CANARY_STOP_STATUS.json"
    if not stop.is_file():
        return
    payload = json.loads(stop.read_text(encoding="utf-8"))
    assert payload["canary_seed"] == 31001
    assert "status" in payload


def test_evidence_package_is_optional_until_export() -> None:
    archive = ROOT / "deliverables/TO_SUBMIT_E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1.zip"
    assert not archive.exists() or archive.stat().st_size > 0
