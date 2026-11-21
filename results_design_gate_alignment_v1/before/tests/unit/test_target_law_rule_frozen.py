"""TARGET_LAW_RULE_V1 is frozen and does not depend on outcomes."""

from __future__ import annotations

from raven_mcs.sag.target_law import TARGET_LAW_RULE_V1, freeze_target_law_rule_v1, target_law_rule_hash


def test_target_law_rule_frozen() -> None:
    assert TARGET_LAW_RULE_V1["rule_id"] == "TARGET_LAW_RULE_V1"
    assert "test_Y" in TARGET_LAW_RULE_V1["forbidden_outcome_information"]
    assert "gate_ON_OFF" in TARGET_LAW_RULE_V1["forbidden_outcome_information"]
    frozen = freeze_target_law_rule_v1()
    assert frozen["frozen"] is True
    assert frozen["hash"] == target_law_rule_hash()
    assert "RMSE" in frozen["forbidden_outcome_information"]
