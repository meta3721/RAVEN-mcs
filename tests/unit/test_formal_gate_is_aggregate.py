from pathlib import Path
from raven_mcs.sag.aggregate_certificate import formal_aggregate_coverage
from raven_mcs.sag.certificates import CertificateContext, FrozenSagThresholds, compute_certificates
from raven_mcs.sag.r1l_spec import FORMAL_COV_MODE, N_MIN

ROOT = Path(__file__).resolve().parents[2]


def test_window_runner_default_is_aggregate() -> None:
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    assert 'sag_cov_mode", "aggregate_stable_regime"' in src
    assert 'sag_cov_mode", "event_count_cp"' not in src


def test_compute_certificates_aggregate_uses_state_machine() -> None:
    hist = [
        {
            "window_id": i,
            "realized_C_cov": 0.2,
            "realized_C_ret": 0.8,
            "realized_C_ESS": 4.0,
            "realized_C_clip": 0.1,
            "active_set_mismatch": 0,
            "Delta_beta": 0.01,
            "Delta_M": 0.01,
            "Delta_V": 0.01,
        }
        for i in range(8)
    ]
    ctx = CertificateContext(
        pi_target={("k", "s"): 1.0},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
        cov_mode=FORMAL_COV_MODE,
    )
    bundle = compute_certificates(hist, FrozenSagThresholds(), ctx)
    assert bundle.C_cov_LCB == 0.0
    assert bundle.diagnostics["certificate_state"] == "WARMUP"
    assert bundle.diagnostics["pairwise_formal_core"] is False
    step = formal_aggregate_coverage(
        hist, pi_target=ctx.pi_target, pi_safe=ctx.pi_safe
    )
    assert step["certificate_state"] == "WARMUP"
    assert step["n_min"] == N_MIN


def test_pairwise_mode_still_callable_as_diagnostic() -> None:
    ctx = CertificateContext(
        pi_target={("k1", "s1"): 1.0},
        pi_safe=0.01,
        n_clients=4,
        n_groups=4,
        cov_mode="event_count_cp",
    )
    hist = [
        {
            "opp_count_by_pair": {"k1|s1": 8.0},
            "opp_event_total": 8.0,
            "opp_mass_by_pair": {"k1|s1": 1.0},
            "realized_C_ret": 0.8,
            "realized_C_ESS": 4.0,
            "realized_C_clip": 0.1,
            "active_set_mismatch": 0,
            "Delta_beta": 0.01,
            "Delta_M": 0.01,
            "Delta_V": 0.01,
        }
        for _ in range(10)
    ]
    bundle = compute_certificates(hist, FrozenSagThresholds(lookback_min=8), ctx)
    assert bundle.diagnostics.get("lower_pi_opp_method") == "clopper_pearson_event_count_bonferroni"
