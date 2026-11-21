from raven_mcs.sag.stress_mask import hash_to_unit_interval

def test_availability_mask_deterministic() -> None:
    kwargs = dict(dataset="uair", base_seed=30001, window_id=3, entity_id="sensor-7")
    assert hash_to_unit_interval(**kwargs) == hash_to_unit_interval(**kwargs)
    assert 0.0 <= hash_to_unit_interval(**kwargs) < 1.0
