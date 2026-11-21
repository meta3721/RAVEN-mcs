"""Unit tests for traffic balanced design canary."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_balanced_canary"
AUDIT = ROOT / "outputs/audits"
SEEDS = (28101, 28102, 28103)


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json").is_file()


def test_balanced_canary_uses_three_frozen_seeds(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")
    assert stop["design_seeds"] == list(SEEDS)


def test_one_single_arm_per_seed(ready: bool) -> None:
    for seed in SEEDS:
        m = _j(OUT / "traces" / str(seed) / "eventtrace_manifest.json")
        assert m["arms"] == 1
        assert m["antithetic_arm_count"] == 1


def test_no_antithetic_average(ready: bool) -> None:
    for seed in SEEDS:
        m = _j(OUT / "traces" / str(seed) / "eventtrace_manifest.json")
        assert m["antithetic_arm_count"] == 1


def test_opportunity_calibration_changes_p_opp(ready: bool) -> None:
    cal = _j(OUT / "E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json")
    assert cal["status"] == "PASS"
    assert "p_opp_mean" in cal
    assert abs(float(cal["p_opp_mean"]) - 0.55) < 1e-6


def test_event_mass_not_reweighted(ready: bool) -> None:
    cal = _j(OUT / "E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json")
    assert cal["event_mass_unchanged"] is True
    mass = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_EVENT_MASS_AUDIT.json")
    assert mass["event_mass_reweighted"] is False


def test_observation_features_pre_outcome_only(ready: bool) -> None:
    q = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_Q_LEAKAGE_AUDIT.json")
    assert q["target_value_feature_dependency_count"] == 0


def test_stage2_eligibility_observed_count_positive(ready: bool) -> None:
    s = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json")
    assert s["stage2_eligibility_violation_count"] == 0


def test_observed_count_not_in_q_features(ready: bool) -> None:
    q = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_Q_LEAKAGE_AUDIT.json")
    assert q["observed_count_used_as_q_feature_count"] == 0


def test_failed_attempts_retained(ready: bool) -> None:
    f = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_FAILED_ATTEMPT_AUDIT.json")
    assert f["failed_attempt_omission_count"] == 0
    assert f["failed_attempts_retained"] > 0


def test_hard_arrival_equals_A_O_U(ready: bool) -> None:
    for seed in SEEDS:
        arr = pd.read_parquet(OUT / "traces" / str(seed) / "hard_arrival_events.parquet")
        recomputed = arr["A_opp"] & arr["O"] & arr["U"]
        assert bool((recomputed == arr["I_arr"]).all())


def test_no_cross_window_atomic_reuse(ready: bool) -> None:
    w = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_WINDOW_REUSE_AUDIT.json")
    assert w["cross_window_duplicate_count"] == 0
    assert w["multiply_assigned_atomic_count"] == 0


def test_complete_trace_parquets_present(ready: bool) -> None:
    names = [
        "opportunity_events.parquet",
        "observation_events.parquet",
        "usable_events.parquet",
        "failed_attempts.parquet",
        "hard_arrival_events.parquet",
        "empirical_atomic_mass.parquet",
        "expected_atomic_mass.parquet",
        "client_window_activity.parquet",
        "eventtrace_manifest.json",
    ]
    for seed in SEEDS:
        for name in names:
            assert (OUT / "traces" / str(seed) / name).is_file()


def test_pooled_balanced_metrics_replay(ready: bool) -> None:
    pooled = _j(AUDIT / "E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json")
    assert "D_TV_group_pooled" in pooled
    assert "D_TV_stratum_pooled" in pooled
    assert "D_TV_client_stratum_pooled" in pooled


def test_no_training_artifacts(ready: bool) -> None:
    stop = _j(OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")
    assert int(stop["training_artifact_count"]) == 0


def test_no_profile_execution(ready: bool) -> None:
    stop = _j(OUT / "E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")
    assert int(stop["profile_execution_count"]) == 0
    assert stop["profile_selection"] == "NOT_STARTED"
