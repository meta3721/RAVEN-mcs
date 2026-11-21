"""C_cov equals target-mass sum of certified pairs, not certified pair ratio."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb


def test_c_cov_target_mass_weighted() -> None:
    pi_target = {
        ("a", "s1"): 0.9,
        ("b", "s2"): 0.1,
    }
    lowers = {
        ("a", "s1"): {"lower_pi_opp": 0.2, "pi_hat_opp": 0.3},
        ("b", "s2"): {"lower_pi_opp": 0.0, "pi_hat_opp": 0.01},
    }
    out = c_cov_from_opportunity_lcb(pi_target, lowers, pi_safe=0.05)
    assert out["C_cov_LCB"] == pytest.approx(0.9)
    assert out["C_cov_LCB"] != pytest.approx(0.5)
    assert out["target_mass_certified"] == pytest.approx(0.9)
    assert out["number_target_positive_pairs"] == 2
