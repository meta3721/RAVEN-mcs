"""TARGET_LAW_RULE_V1 hash stays the R1d freeze."""

from __future__ import annotations

from raven_mcs.sag.target_law import freeze_target_law_rule_v1, target_law_rule_hash

EXPECTED = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"


def test_r1e_target_rule_hash_unchanged() -> None:
    assert target_law_rule_hash() == EXPECTED
    assert freeze_target_law_rule_v1()["hash"] == EXPECTED
