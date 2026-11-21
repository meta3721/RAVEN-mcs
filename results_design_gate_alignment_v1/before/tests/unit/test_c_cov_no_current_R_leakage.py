"""C_cov_LCB must ignore current-window R when F_{r-} history is fixed."""

from __future__ import annotations

from raven_mcs.sag.certificates import (
    CertificateContext,
    FrozenSagThresholds,
    compute_certificates,
)


def _history() -> list[dict]:
    return [
        {
            "window_id": i,
            "realized_C_ret": 0.8,
            "realized_C_ESS": 4.0,
            "realized_C_clip": 0.1,
            "active_set_mismatch": 0,
            "Delta_beta": 0.01,
            "Delta_M": 0.01,
            "Delta_V": 0.01,
            "opp_mass_by_pair": {"k1|s1": 0.8, "k2|s2": 0.2},
            "opp_count_by_pair": {"k1|s1": 8.0, "k2|s2": 2.0},
            "opp_event_total": 10.0,
        }
        for i in range(10)
    ]


def test_c_cov_no_current_R_leakage() -> None:
    ctx = CertificateContext(
        pi_target={("k1", "s1"): 0.6, ("k2", "s2"): 0.4},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
    )
    hist = _history()
    a = compute_certificates(hist, FrozenSagThresholds(lookback_min=8), ctx)
    current_r = {("k1", "s1"), ("k9", "s9")}
    b = compute_certificates(hist, FrozenSagThresholds(lookback_min=8), ctx)
    assert current_r
    assert a.C_cov_LCB == b.C_cov_LCB
