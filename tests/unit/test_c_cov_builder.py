from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb

def test_c_cov_builder() -> None:
    pi_tar = {("c0", "s0"): 1.0}
    lowers = {("c0", "s0"): {"lower_pi_opp": 0.01, "pi_hat_opp": 0.02}}
    out = c_cov_from_opportunity_lcb(pi_tar, lowers, 0.005)
    assert abs(out["C_cov_LCB"] - 1.0) < 1e-12
    lowers = {("c0", "s0"): {"lower_pi_opp": 0.001, "pi_hat_opp": 0.02}}
    out = c_cov_from_opportunity_lcb(pi_tar, lowers, 0.005)
    assert abs(out["C_cov_LCB"] - 0.0) < 1e-12
