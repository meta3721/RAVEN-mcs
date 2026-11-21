"""Formal C_cov remains sum pi_tar 1{lower >= pi_safe}."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb


def test_r1e_c_cov_formula_unchanged() -> None:
    pi = {("a", "s"): 0.6, ("b", "s"): 0.4, ("z", "s"): 0.0}
    lowers = {("a", "s"): {"lower_pi_opp": 0.02}, ("b", "s"): {"lower_pi_opp": 0.0}}
    out = c_cov_from_opportunity_lcb(pi, lowers, 0.01)
    assert out["C_cov_LCB"] == pytest.approx(0.6)
    assert out["target_mass_certified"] == pytest.approx(0.6)
