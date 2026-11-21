"""Stage 2 falls back to global residuals when same-block history is short."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import dynamic_lower_pi_opp_tod


def test_r1e_stage2_fallback_global_when_context_short() -> None:
    pairs = [("k", "s")]
    hist = [{"opp_mass_by_pair": {"k|s": 0.1}} for _ in range(16)]
    blocks = [0] * 16
    out = dynamic_lower_pi_opp_tod(
        hist, blocks, current_block=3, pairs=pairs, lookback=8, delta=0.05, min_calib=8, calibration="tod_block",
    )
    assert out["cold_start"] is False
    assert out["used_same_block_fallback"] is True
    assert out["n_calib"] >= 8
