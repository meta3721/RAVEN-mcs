"""Hats use only strictly prior completed windows."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import tod_conditioned_rolling_pi_hat


def test_r1e_tod_predictor_strictly_prior() -> None:
    pairs = [("k", "s")]
    hist = [{("k", "s"): 0.1}, {("k", "s"): 0.3}]
    blocks = [1, 1]
    hat = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=1, lookback=8)
    assert abs(hat[("k", "s")] - 0.2) < 1e-12
    later = hist + [{("k", "s"): 0.9}]
    later_blocks = blocks + [1]
    hat_later = tod_conditioned_rolling_pi_hat(later, later_blocks, pairs, current_block=1, lookback=8)
    assert abs(hat_later[("k", "s")] - (0.1 + 0.3 + 0.9) / 3.0) < 1e-12
    assert hat[("k", "s")] != hat_later[("k", "s")]
