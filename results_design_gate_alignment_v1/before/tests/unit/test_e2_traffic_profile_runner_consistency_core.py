"""Unit tests for Traffic profile–runner consistency hotfix."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_runner_consistency"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles"
SEEDS = (28201, 28202, 28203)
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json").is_file()


def test_runtime_uses_registry_a_opp(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    assert int(p["a_opp_mismatch_count"]) == 0


def test_runtime_uses_registry_a_obs(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    assert int(p["a_obs_mismatch_count"]) == 0


def test_runtime_uses_registry_a_q(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    assert int(p["a_q_mismatch_count"]) == 0


def test_no_per_seed_intercept_solve(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    assert int(p["per_seed_intercept_solve_count"]) == 0
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["per_seed_intercept_solve_count"]) == 0


def test_registry_runtime_probability_bounds_equal(ready: bool) -> None:
    assert ready
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    assert reg["probability_bounds"] == p["probability_bounds"] == {
        "opp": [0.05, 0.95], "obs": [0.05, 0.95], "q": [0.05, 0.95],
    }
    assert int(p["bounds_mismatch_count"]) == 0


def test_subset_probabilities_sum_one(ready: bool) -> None:
    assert ready
    exact = _j(AUDIT / "E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json")
    for sid, audit in exact["by_scenario"].items():
        assert float(audit["subset_probability_sum_max_abs_error"]) <= 1e-12


def test_exact_expected_arrival_by_subset_enumeration(ready: bool) -> None:
    assert ready
    exact = _j(AUDIT / "E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json")
    assert exact["status"] == "PASS"
    assert int(exact["exact_enumeration_window_count"]) == 4300
    df = pd.read_parquet(OUT / "scenarios/balanced/exact_expected_arrival_mass.parquet")
    assert len(df) == 25800


def test_exact_expected_usable_activity(ready: bool) -> None:
    assert ready
    cw = pd.read_parquet(OUT / "scenarios/balanced/exact_expected_client_window_activity.parquet")
    assert "expected_usable_attempt" in cw.columns
    assert len(cw) == 4300


def test_expected_mass_monotonicity(ready: bool) -> None:
    assert ready
    exact = _j(AUDIT / "E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json")
    for sid, audit in exact["by_scenario"].items():
        assert audit["expected_mass_monotonicity"] is True


def test_profile_clip_rates_reported(ready: bool) -> None:
    assert ready
    clip = _j(AUDIT / "E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json")
    for sid in SCENARIOS:
        assert sid in clip["clip_by_scenario"]
        assert "opportunity_lower_clip_rate" in clip["clip_by_scenario"][sid]


def test_minimum_expected_support_reported(ready: bool) -> None:
    assert ready
    clip = _j(AUDIT / "E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json")
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    for sid in SCENARIOS:
        s = clip["support_by_scenario"][sid]
        assert "minimum_positive_group_expected_arrivals" in s
        assert "minimum_positive_stratum_expected_arrivals" in s
        assert "minimum_positive_client_stratum_expected_arrivals" in s
    # Degeneration hard-gate: group<20 or stratum<5 => overall BLOCKED, else READY.
    degenerated = any(
        float(clip["support_by_scenario"][sid]["minimum_positive_group_expected_arrivals"]) < 20
        or float(clip["support_by_scenario"][sid]["minimum_positive_stratum_expected_arrivals"]) < 5
        for sid in SCENARIOS
    )
    if degenerated:
        assert stop["status"] == "BLOCKED_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_FAILED"
        assert clip["status"] == "FAIL"
    else:
        assert clip["status"] == "PASS"


def test_old_seed_recalibrated_traces_tombstoned(ready: bool) -> None:
    assert ready
    t = _j(AUDIT / "E2_TRAFFIC_OLD_TRACE_TOMBSTONE.json")
    assert t["invalid_due_to_seed_specific_intercept_recalibration"] is True
    assert len(t["paths"]) == 18


def test_18_fixed_parameter_single_arm_traces(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["hard_trace_count"]) == 18
    for sid in SCENARIOS:
        for seed in SEEDS:
            m = _j(OUT / "scenarios" / sid / "traces" / str(seed) / "eventtrace_manifest.json")
            assert m["arms"] == 1
            assert m["frozen_intercepts"] is True


def test_hard_opportunity_direction_computed(ready: bool) -> None:
    assert ready
    cert = _j(FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json")
    for sid in SCENARIOS:
        assert "opp" in cert["by_scenario"][sid]["hard_signed"]


def test_hard_observation_direction_computed(ready: bool) -> None:
    assert ready
    cert = _j(FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json")
    for sid in SCENARIOS:
        assert "obs" in cert["by_scenario"][sid]["hard_signed"]


def test_hard_arrival_direction_computed(ready: bool) -> None:
    assert ready
    cert = _j(FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json")
    for sid in SCENARIOS:
        assert "arr" in cert["by_scenario"][sid]["hard_signed"]


def test_s5_hard_direction_accumulates(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/complete_aligned/DIRECTION_CERTIFICATE.json")
    assert c["hard_certificate"]["checks"]["accumulation"] is True


def test_s6_hard_cancellation_not_hardcoded(ready: bool) -> None:
    assert ready
    src = (ROOT / "src/raven_mcs/e2/traffic_profiles/runner_consistency.py").read_text(encoding="utf-8")
    assert "hard_cancellation_visible = True" not in src
    c = _j(OUT / "scenarios/complete_counteracting/DIRECTION_CERTIFICATE.json")
    assert c["hard_certificate"]["notes"].get("hardcoded_pass_used") is False


def test_s6_hard_cancellation_inequality(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/complete_counteracting/DIRECTION_CERTIFICATE.json")
    assert c["hard_certificate"]["checks"]["cancellation"] is True
    hs = c["hard_certificate"]["hard_signed"]
    assert abs(hs["arr"]) < abs(hs["obs"])


def test_atomic_hard_tv_not_primary_gate(ready: bool) -> None:
    assert ready
    cert = _j(FROZEN / "traffic_s1_s6_runner_consistent_direction_certificate.json")
    assert cert["atomic_hard_tv_primary_gate"] is False


def test_no_profile_strength_search(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["profile_strength_search_count"]) == 0
    assert stop["selected_strength"] == "PROFILE-S2"


def test_no_training_artifacts(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["training_artifact_count"]) == 0


def test_seed29001_not_read(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["seed_29001_read_count"]) == 0


def test_validation_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["validation_seed_read_count"]) == 0


def test_formal_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    assert int(stop["formal_seed_read_count"]) == 0


def test_complete_runner_consistent_registry(ready: bool) -> None:
    assert ready
    for name in (
        "traffic_s1_s6_profile_registry.json",
        "traffic_s1_s6_profile_registry.yaml",
        "traffic_s1_s6_runner_consistent_direction_certificate.json",
        "traffic_s1_s6_identity.json",
    ):
        assert (FROZEN / name).is_file()
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    assert reg.get("no_per_seed_intercept_recalibration") is True
