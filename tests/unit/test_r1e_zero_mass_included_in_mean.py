"""Zero opportunity mass enters the TOD rolling mean."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import tod_conditioned_rolling_pi_hat


def test_r1e_zero_mass_included_in_mean() -> None:
    pairs = [("k", "s")]
    hist = [{("k", "s"): 0.4}, {("k", "s"): 0.0}, {("k", "s"): 0.2}]
    blocks = [2, 2, 2]
    hat = tod_conditioned_rolling_pi_hat(hist, blocks, pairs, current_block=2, lookback=8)
    assert abs(hat[("k", "s")] - 0.2) < 1e-12
