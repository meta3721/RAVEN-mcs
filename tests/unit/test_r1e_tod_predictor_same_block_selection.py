"""Same-block history is preferred over mixed TOD windows."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import tod_conditioned_rolling_pi_hat


def test_r1e_tod_predictor_same_block_selection() -> None:
    pairs = [("k", "s")]
    hist = [{("k", "s"): 1.0}, {("k", "s"): 0.0}, {("k", "s"): 0.4}]
    blocks = [0, 1, 1]
    hat = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=1, lookback=8)
    assert abs(hat[("k", "s")] - 0.2) < 1e-12
