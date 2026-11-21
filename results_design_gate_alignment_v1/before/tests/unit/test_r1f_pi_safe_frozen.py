"""PI_SAFE_RULE_V1 q10 frozen for R1f."""

from __future__ import annotations

import json
from pathlib import Path

from raven_mcs.sag.target_law import PI_SAFE_RULE_V1, pi_safe_rule_hash

ROOT = Path(__file__).resolve().parents[2]


def test_r1f_pi_safe_frozen() -> None:
    assert PI_SAFE_RULE_V1["quantile"] == 0.10
    r1e = json.loads((ROOT / "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8"))
    assert r1e.get("rule_id") == "PI_SAFE_RULE_V1"
    assert r1e.get("hash") == pi_safe_rule_hash()
