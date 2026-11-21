"""Dynamic predictor uses only t<r history."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import rolling_pi_hat


def test_dynamic_cov_history_only() -> None:
    hist = [
        {("a", "s"): 0.1, ("b", "s"): 0.9},
        {("a", "s"): 0.2, ("b", "s"): 0.8},
        {("a", "s"): 0.3, ("b", "s"): 0.7},
    ]
    future = {("a", "s"): 1.0, ("b", "s"): 0.0}
    hat = rolling_pi_hat(hist, [("a", "s"), ("b", "s")], lookback=2)
    hat_with_future = rolling_pi_hat(hist + [future], [("a", "s"), ("b", "s")], lookback=2)
    assert abs(hat[("a", "s")] - 0.25) < 1e-12
    assert hat_with_future[("a", "s")] != hat[("a", "s")]
    # F_{r-} for the next window after hist is hat, not hat_with_future.
    assert hat[("a", "s")] == rolling_pi_hat(hist, [("a", "s")], lookback=2)[("a", "s")]
