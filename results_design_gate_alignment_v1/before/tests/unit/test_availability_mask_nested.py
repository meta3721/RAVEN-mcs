from raven_mcs.sag.stress_mask import available_entities, entity_available, hash_to_unit_interval

def test_availability_mask_nested() -> None:
    entities = [f"e{i}" for i in range(20)]
    low = available_entities(dataset="sensorscope", base_seed=30001, window_id=2, entity_ids=entities, availability_level=0.40)
    high = available_entities(dataset="sensorscope", base_seed=30001, window_id=2, entity_ids=entities, availability_level=0.80)
    assert set(low["available"]) <= set(high["available"])
    u = hash_to_unit_interval(dataset="uair", base_seed=30001, window_id=0, entity_id="x")
    assert (not entity_available(u, 0.20)) or entity_available(u, 0.80)
    assert entity_available(u, 1.00)
