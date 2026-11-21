from raven_mcs.sag.r1j_spec import calibration_spec_payload

def test_same_a_stratum_only() -> None:
    payload = calibration_spec_payload()
    assert payload["same_a_only"] is True
    assert payload["no_cross_a_borrow"] is True
