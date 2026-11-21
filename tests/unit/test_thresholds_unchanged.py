"""Frozen SAG thresholds must stay at the sealed G0 values."""

from __future__ import annotations

import json
from pathlib import Path

from raven_mcs.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS = ROOT / "configs" / "sag_g0" / "thresholds.json"
SEALED_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"


def test_thresholds_unchanged() -> None:
    payload = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    assert payload["tau_cov"] == 0.05
    assert payload["tau_ret"] == 0.05
    assert payload["tau_ESS"] == 1.0
    assert payload["tau_clip"] == 0.95
    assert payload["tau_A"] == 0.35
    assert payload["tau_safe"] == 4.0
    assert payload["delta_cal"] == 0.05
    assert payload["lookback_min"] == 8
    assert payload["lookback_max"] == 32
    assert payload["coverage_target"] == 0.95
    assert sha256_file(THRESHOLDS) == SEALED_HASH
