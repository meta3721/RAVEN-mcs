from raven_mcs.sag.r1k_spec import aggregate_calibration_payload

def test_aggregate_same_a_calibration() -> None:
    payload = aggregate_calibration_payload()
    assert payload["same_a_only"] is True
    assert payload["no_cross_a_borrow"] is True
