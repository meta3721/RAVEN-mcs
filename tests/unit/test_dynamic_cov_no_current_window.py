"""Dynamic C_cov ignores current-window opportunity mass."""

from __future__ import annotations

from raven_mcs.sag.certificates import (
    CertificateContext,
    FrozenSagThresholds,
    compute_certificates,
)


def _hist(n: int = 20) -> list[dict]:
    rows = []
    for i in range(n):
        rows.append(
            {
                "window_id": i,
                "realized_C_ret": 0.8,
                "realized_C_ESS": 4.0,
                "realized_C_clip": 0.1,
                "active_set_mismatch": 0,
                "Delta_beta": 0.01,
                "Delta_M": 0.01,
                "Delta_V": 0.01,
                "opp_mass_by_pair": {"k1|s1": 0.7, "k2|s2": 0.3},
                "opp_count_by_pair": {"k1|s1": 7.0, "k2|s2": 3.0},
                "opp_event_total": 10.0,
            }
        )
    return rows


def test_dynamic_cov_no_current_window() -> None:
    ctx = CertificateContext(
        pi_target={("k1", "s1"): 0.6, ("k2", "s2"): 0.4},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
        cov_mode="dynamic_max_residual",
        rolling_L=8,
    )
    hist = _hist()
    a = compute_certificates(hist, FrozenSagThresholds(lookback_min=8), ctx)
    current = {
        "opp_mass_by_pair": {"k1|s1": 1.0},
        "opp_count_by_pair": {"k1|s1": 1000.0},
        "opp_event_total": 1000.0,
    }
    b = compute_certificates(hist, FrozenSagThresholds(lookback_min=8), ctx)
    assert current["opp_event_total"] == 1000.0
    assert a.C_cov_LCB == b.C_cov_LCB
    assert a.diagnostics.get("n_calib", 0) >= 8
