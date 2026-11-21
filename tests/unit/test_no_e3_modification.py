"""R1f must not modify E3 traces."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_e3_modification() -> None:
    freeze = ROOT / "results_sag_g1/round_r1f/audit/R1F_FREEZE_AUDIT.json"
    payload = json.loads(freeze.read_text(encoding="utf-8"))
    assert payload.get("e3_modified") is False
