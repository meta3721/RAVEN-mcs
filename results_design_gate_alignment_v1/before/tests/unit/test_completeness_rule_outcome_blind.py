from raven_mcs.sag.window_completeness import completeness_rule_payload

def test_completeness_rule_outcome_blind() -> None:
    payload = completeness_rule_payload()
    assert payload["uses_oracle"] is False
    assert payload["uses_c_cov"] is False
    assert "C_oracle_safe" in payload["forbidden_fields"]
