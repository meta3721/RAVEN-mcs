"""Stage 1 residual remains one number per window."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import window_max_residual


def test_r1e_global_max_residual_window_unit() -> None:
    pairs = [("a", "s"), ("b", "s"), ("c", "s")]
    hat = {("a", "s"): 0.4, ("b", "s"): 0.3, ("c", "s"): 0.1}
    realized = {("a", "s"): 0.1, ("b", "s"): 0.2, ("c", "s"): 0.1}
    r = window_max_residual(hat, realized, pairs)
    assert abs(r - 0.3) < 1e-12
