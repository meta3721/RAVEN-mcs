"""Empty same-block history falls back to global last-L."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import rolling_pi_hat, tod_conditioned_rolling_pi_hat


def test_r1e_tod_predictor_global_fallback() -> None:
    pairs = [("k", "s")]
    hist = [{("k", "s"): 0.5}] * 8
    blocks = [0] * 8
    hat = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=3, lookback=8)
    fallback = rolling_pi_hat(hist, pairs, lookback=8)
    assert hat[("k", "s")] == fallback[("k", "s")]
