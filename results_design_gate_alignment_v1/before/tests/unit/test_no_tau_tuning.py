"""R1f must not tune tau_cov."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_tau_tuning() -> None:
    freeze = ROOT / "results_sag_g1/round_r1f/audit/R1F_FREEZE_AUDIT.json"
    payload = json.loads(freeze.read_text(encoding="utf-8"))
    assert float(payload.get("tau_cov")) == 0.05
