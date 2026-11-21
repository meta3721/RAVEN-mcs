"""C_cov remains target-mass weighted certified support, not a pair count."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb


def test_c_cov_formula() -> None:
    pi_target = {
        ("a", "s1"): 0.8,
        ("b", "s2"): 0.15,
        ("c", "s3"): 0.05,
        ("z", "s0"): 0.0,
    }
    lowers = {
        ("a", "s1"): {"lower_pi_opp": 0.02, "pi_hat_opp": 0.1},
        ("b", "s2"): {"lower_pi_opp": 0.001, "pi_hat_opp": 0.02},
        ("c", "s3"): {"lower_pi_opp": 0.02, "pi_hat_opp": 0.05},
    }
    out = c_cov_from_opportunity_lcb(pi_target, lowers, pi_safe=0.01)
    assert out["C_cov_LCB"] == pytest.approx(0.85)
    assert out["target_mass_certified"] == pytest.approx(0.85)
    assert out["target_mass_total"] == pytest.approx(1.0)
    assert out["number_target_positive_pairs"] == 3
    assert out["C_cov_LCB"] != pytest.approx(2.0 / 3.0)
