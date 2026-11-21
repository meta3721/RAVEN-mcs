"""C_real_support must not be a Gate feature."""

from __future__ import annotations

from raven_mcs.sag.gate import LEGAL_GATE_FEATURES, decide_gate
from raven_mcs.sag.certificates import FrozenSagThresholds


def test_r1e_real_support_is_diagnostic_only() -> None:
    assert "C_real_support" not in LEGAL_GATE_FEATURES
    th = FrozenSagThresholds()
    decision = decide_gate(
        {
            "C_cov_LCB": 1.0,
            "C_ret_LCB": 1.0,
            "C_ESS_LCB": 4.0,
            "C_clip_UCB": 0.1,
            "delta_A_UCB": 0.0,
            "B_tot_UCB": 0.1,
        },
        th.gate_thresholds(),
    )
    assert "C_real_support" not in (decision.fallback_reason or "")
    assert "C_real_support" not in decision.features
