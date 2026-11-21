"""TARGET_LAW_RULE_V1 hash frozen for R1f."""

from __future__ import annotations

import json
from pathlib import Path

from raven_mcs.sag.target_law import freeze_target_law_rule_v1

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"


def test_r1f_target_law_frozen() -> None:
    rule = freeze_target_law_rule_v1()
    assert rule["hash"] == EXPECTED
    r1d = json.loads((ROOT / "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json").read_text(encoding="utf-8"))
    assert r1d.get("hash") == EXPECTED
