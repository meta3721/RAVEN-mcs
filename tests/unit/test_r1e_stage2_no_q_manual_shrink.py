"""Stage 2 q is a conformal quantile, not a hand-tuned shrink of Stage 1 q."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.sag.dynamic_cov import conformal_upper_residual, dynamic_lower_pi_opp_tod

SRC = Path(__file__).resolve().parents[2] / "src" / "raven_mcs" / "sag" / "dynamic_cov.py"


def test_r1e_stage2_no_q_manual_shrink() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "q * 0.5" not in text
    assert "q *= 0.5" not in text
    assert "clip q" not in text.lower()
    pairs = [("k", "s")]
    hist = [{"opp_mass_by_pair": {"k|s": 0.05}} for _ in range(16)]
    blocks = [1] * 16
    out = dynamic_lower_pi_opp_tod(
        hist, blocks, current_block=1, pairs=pairs, lookback=8, delta=0.05, min_calib=8, calibration="tod_block",
    )
    hats = [0.05] * 8
    # Constant history => residual 0 after lookback; q is that conformal value, not a shrink.
    assert out["cold_start"] is False
    q_expected = conformal_upper_residual([0.0] * out["n_calib"], 0.05)
    assert abs(float(out["q"]) - float(q_expected)) < 1e-12
