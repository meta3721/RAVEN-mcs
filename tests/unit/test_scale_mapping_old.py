from raven_mcs.sag.r1k_scale import hat_pi_old

def test_scale_mapping_old() -> None:
    assert abs(hat_pi_old(0.5, pi_safe=0.01, mean_all=0.04) - 0.02) < 1e-12
    assert abs(hat_pi_old(0.5, pi_safe=0.01, mean_all=0.0) - 0.005) < 1e-12
