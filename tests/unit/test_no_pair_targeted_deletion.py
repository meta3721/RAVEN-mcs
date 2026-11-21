from raven_mcs.sag.availability_stress import stress_level_payload
from raven_mcs.sag.stress_mask import filter_units_by_entities

def test_no_pair_targeted_deletion() -> None:
    assert stress_level_payload()["pair_level_deletion"] is False
    meta = {
        "u1": {"spatial": "e1", "client": "c0", "stratum": "hard"},
        "u2": {"spatial": "e1", "client": "c0", "stratum": "easy"},
    }
    kept = filter_units_by_entities(["u1", "u2"], meta, ["e1"])
    assert set(kept) == {"u1", "u2"}
    dropped = filter_units_by_entities(["u1", "u2"], meta, [])
    assert dropped == []
