"""R1e does not retune frozen thresholds."""

from __future__ import annotations

import json
from pathlib import Path

from raven_mcs.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "raven_mcs" / "experiments" / "run_sag_g1_r1e.py"
THRESHOLDS = ROOT / "configs" / "sag_g0" / "thresholds.json"


def test_r1e_no_threshold_tuning() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "tau_cov =" not in text
    assert "delta_cal = 0.01" not in text
    payload = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    assert payload["tau_cov"] == 0.05
    assert payload["delta_cal"] == 0.05
    assert sha256_file(THRESHOLDS) == "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
