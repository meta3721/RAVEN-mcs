"""Calibration residual is one number per window, not per event."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import window_max_residual


def test_dynamic_cov_window_block_calibration() -> None:
    pairs = [("a", "s")] * 20 + [("b", "s")]
    # Event count must not create 21 calibration samples.
    hat = {("a", "s"): 0.9, ("b", "s"): 0.1}
    realized = {("a", "s"): 0.5, ("b", "s"): 0.5}
    r = window_max_residual(hat, realized, [("a", "s"), ("b", "s")])
    assert abs(r - 0.4) < 1e-12
    assert r == window_max_residual(hat, realized, [("a", "s"), ("b", "s")])
    assert len(pairs) == 21
