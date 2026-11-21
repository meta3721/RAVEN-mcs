"""Window-joint coverage is 1 only if every target-positive pair is covered."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import coverage_flags


def test_dynamic_cov_joint_coverage_metric() -> None:
    pi = {("a", "s"): 0.8, ("b", "s"): 0.2}
    lowers = {
        ("a", "s"): {"lower_pi_opp": 0.1},
        ("b", "s"): {"lower_pi_opp": 0.1},
    }
    realized_ok = {("a", "s"): 0.8, ("b", "s"): 0.2}
    realized_fail = {("a", "s"): 0.8, ("b", "s"): 0.05}
    ok = coverage_flags(lowers, realized_ok, pi)
    bad = coverage_flags(lowers, realized_fail, pi)
    assert ok["joint_window_coverage"] == 1
    assert ok["pairwise_coverage"] == 1.0
    assert bad["joint_window_coverage"] == 0
    assert bad["pairwise_coverage"] == 0.5
    assert abs(bad["target_mass_weighted_coverage"] - 0.8) < 1e-12
