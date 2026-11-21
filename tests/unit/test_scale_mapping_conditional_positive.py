from raven_mcs.sag.r1k_scale import hat_pi_cond, mean_mass_positive

def test_scale_mapping_conditional_positive() -> None:
    assert mean_mass_positive([0.0, 0.0, 0.04, 0.06]) == 0.05
    assert abs(hat_pi_cond(0.5, pi_safe=0.01, mean_pos=0.04) - 0.02) < 1e-12
