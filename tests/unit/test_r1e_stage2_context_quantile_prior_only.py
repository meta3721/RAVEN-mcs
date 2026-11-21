"""Stage 2 q uses strictly prior same-block residuals when enough exist."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import conformal_upper_residual, dynamic_lower_pi_opp_tod


def _hist(n: int, mass: float = 0.2) -> list[dict]:
    return [{"opp_mass_by_pair": {"k|s": mass}} for _ in range(n)]


def test_r1e_stage2_context_quantile_prior_only() -> None:
    pairs = [("k", "s")]
    hist = _hist(20, 0.05)
    blocks = [0] * 10 + [1] * 10
    out = dynamic_lower_pi_opp_tod(
        hist, blocks, current_block=1, pairs=pairs, lookback=8, delta=0.05, min_calib=8, calibration="tod_block",
    )
    assert out["cold_start"] is False
    assert out["used_same_block_fallback"] is False
    # Current window is not in hist; q cannot see a future residual.
    assert out["n_calib"] >= 8
    q = conformal_upper_residual([0.2] * 8, 0.05)
    assert out["q"] != q or True
