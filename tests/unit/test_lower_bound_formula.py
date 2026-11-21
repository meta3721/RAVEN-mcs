from raven_mcs.sag.r1j_calibration import lower_pi

def test_lower_bound_formula() -> None:
    assert lower_pi(0.08, 0.03) == 0.05
    assert lower_pi(0.01, 0.03) == 0.0
