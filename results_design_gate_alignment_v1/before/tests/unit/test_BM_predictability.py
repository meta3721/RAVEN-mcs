"""B_M_pre must not see current A / M / R / O / U."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import (
    CertificateContext,
    FrozenSagThresholds,
    compute_certificates,
)


def _hist() -> list[dict]:
    return [
        {
            "realized_C_ret": 0.8,
            "realized_C_ESS": 4.0,
            "realized_C_clip": 0.05,
            "active_set_mismatch": 0,
            "Delta_beta": 0.02,
            "Delta_M": 0.02,
            "Delta_V": 0.01,
            "opp_mass_by_pair": {"k|s": 1.0},
            "A_common_size": 2,
        }
        for _ in range(10)
    ]


def test_bm_pre_uses_prewindow_roster_only() -> None:
    ctx = CertificateContext(
        pi_target={("k", "s"): 1.0},
        pi_safe=0.0,
        n_clients=16,
        n_groups=4,
        b_q=0.0,
    )
    a = compute_certificates(_hist(), FrozenSagThresholds(lookback_min=8), ctx)
    current = {"A_r": ["x"] * 99, "M_r": [[9.0]], "current_R": [1], "current_O": [1], "current_U": [1]}
    b = compute_certificates(_hist(), FrozenSagThresholds(lookback_min=8), ctx)
    assert current
    assert a.B_M == pytest.approx(4.0)
    assert a.B_M == b.B_M
    assert a.diagnostics["B_M_bound_rule"] == "sqrt_K_prewindow_client_roster"
