"""tau_cov frozen at 0.05 for R1f."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_r1f_tau_cov_frozen() -> None:
    th = json.loads((ROOT / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    assert float(th["tau_cov"]) == 0.05
    assert float(th["delta_cal"]) == 0.05
