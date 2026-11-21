from raven_mcs.sag.stress_mask import hash_to_unit_interval, mask_rule_payload

def test_availability_mask_outcome_independent() -> None:
    payload = mask_rule_payload()
    u = hash_to_unit_interval(dataset="uair", base_seed=30001, window_id=4, entity_id="e")
    u2 = hash_to_unit_interval(dataset="uair", base_seed=30001, window_id=4, entity_id="e")
    assert u == u2
    for key in ("C_oracle_safe", "oracle_pass", "C_cov", "Gate"):
        assert key not in payload
        assert key in payload["outcome_fields_forbidden"]
