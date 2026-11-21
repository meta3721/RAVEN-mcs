"""TOD predictor never consumes current-window mass."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import tod_conditioned_rolling_pi_hat


def test_r1e_tod_predictor_no_current_window() -> None:
    pairs = [("k", "s")]
    hist = [{("k", "s"): 0.2}] * 8
    blocks = [0] * 8
    hat = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=0, lookback=8)
    current = {("k", "s"): 1.0}
    hat2 = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=0, lookback=8)
    assert current[("k", "s")] == 1.0
    assert hat[("k", "s")] == hat2[("k", "s")] == 0.2
