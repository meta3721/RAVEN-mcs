"""U-Air must not be hardcoded as unsafe in the Gate."""

from __future__ import annotations

from raven_mcs.sag.certificates import (
    CertificateContext,
    FrozenSagThresholds,
    compute_certificates,
)
from raven_mcs.sag.gate import FORBIDDEN_GATE_FEATURES, decide_gate


def test_uair_not_hardcoded_unsafe() -> None:
    assert "dataset_id" in FORBIDDEN_GATE_FEATURES
    hist = [
        {
            "realized_C_ret": 0.8,
            "realized_C_ESS": 4.0,
            "realized_C_clip": 0.1,
            "active_set_mismatch": 0,
            "Delta_beta": 0.01,
            "Delta_M": 0.01,
            "Delta_V": 0.01,
            "opp_mass_by_pair": {"k|s": 1.0},
            "opp_count_by_pair": {"k|s": 8.0},
            "opp_event_total": 8.0,
        }
        for _ in range(16)
    ]
    ctx_a = CertificateContext(
        pi_target={("k", "s"): 1.0},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
        cov_mode="dynamic_max_residual",
        rolling_L=8,
    )
    ctx_b = CertificateContext(
        pi_target={("k", "s"): 1.0},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
        cov_mode="dynamic_max_residual",
        rolling_L=8,
        source="uair",
    )
    th = FrozenSagThresholds(lookback_min=8)
    a = compute_certificates(hist, th, ctx_a)
    b = compute_certificates(hist, th, ctx_b)
    assert a.C_cov_LCB == b.C_cov_LCB
    da = decide_gate(a.as_gate_inputs(), th.gate_thresholds())
    db = decide_gate(b.as_gate_inputs(), th.gate_thresholds())
    assert da.G_r == db.G_r
    assert "uair" not in (da.fallback_reason or "").lower()
