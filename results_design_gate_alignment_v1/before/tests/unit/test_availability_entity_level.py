from raven_mcs.sag.stress_mask import filter_units_by_entities, mask_rule_payload

def test_availability_entity_level() -> None:
    assert mask_rule_payload()["entity_id"] == "spatial_id"
    meta = {
        "u1": {"spatial": "e1", "client": "c0", "stratum": "s0"},
        "u2": {"spatial": "e1", "client": "c0", "stratum": "s1"},
        "u3": {"spatial": "e2", "client": "c1", "stratum": "s0"},
    }
    kept = filter_units_by_entities(["u1", "u2", "u3"], meta, ["e1"])
    assert set(kept) == {"u1", "u2"}
