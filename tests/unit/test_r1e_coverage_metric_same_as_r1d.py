"""R1e reuses the R1d window-joint coverage metric."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import coverage_flags


def test_r1e_coverage_metric_same_as_r1d() -> None:
    pi = {("a", "s"): 0.75, ("b", "s"): 0.25}
    lowers = {("a", "s"): {"lower_pi_opp": 0.1}, ("b", "s"): {"lower_pi_opp": 0.2}}
    ok = coverage_flags(lowers, {("a", "s"): 0.2, ("b", "s"): 0.3}, pi)
    bad = coverage_flags(lowers, {("a", "s"): 0.2, ("b", "s"): 0.05}, pi)
    assert ok["joint_window_coverage"] == 1
    assert bad["joint_window_coverage"] == 0
    assert abs(bad["target_mass_weighted_coverage"] - 0.75) < 1e-12
