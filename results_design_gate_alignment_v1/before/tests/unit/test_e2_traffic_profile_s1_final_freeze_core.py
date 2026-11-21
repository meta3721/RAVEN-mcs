"""Unit tests for PROFILE-S1 final freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_profile_s1"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles_s1"
SEEDS = (28201, 28202, 28203)
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json").is_file()


def test_only_profile_s1_executed(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert stop["selected_strength"] == "PROFILE-S1"
    for sid in SCENARIOS:
        for seed in SEEDS:
            snap = _j(OUT / "scenarios" / sid / "traces" / str(seed) / "runtime_parameter_snapshot.json")
            assert snap["profile_id"] == "PROFILE-S1"


def test_profile_s2_tombstoned(ready: bool) -> None:
    assert ready
    t = _j(AUDIT / "E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json")
    assert t["prior_strength"] == "PROFILE-S2"
    assert t["profile_s2_must_not_be_reused"] is True
    assert t["blocking_scenario"] == "S5_COMPLETE_ALIGNED"


def test_no_other_strength_executed(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["other_strength_executed_count"]) == 0


def test_no_strength_grid_search(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["strength_grid_search_count"]) == 0


def test_one_intercept_solve_per_scenario(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json")
    assert all(int(v) == 1 for v in p["intercept_solve_count_per_scenario"].values())


def test_no_per_seed_intercept_solve(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["per_seed_intercept_solve_count"]) == 0


def test_runtime_parameters_equal_registry(ready: bool) -> None:
    assert ready
    p = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json")
    assert p["status"] == "PASS"
    assert all(int(r["mismatch_count"]) == 0 for r in p["rows"])


def test_exact_expected_mass_reused(ready: bool) -> None:
    assert ready
    exact = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json")
    assert "exact_expected_masses" in exact["implementation"]
    assert exact["status"] == "PASS"
    assert int(exact["exact_enumeration_window_count"]) == 4300


def test_profile_s1_probability_bounds(ready: bool) -> None:
    assert ready
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    assert reg["probability_bounds"] == {"opp": [0.05, 0.95], "obs": [0.05, 0.95], "q": [0.05, 0.95]}


def test_profile_s1_clip_rates_reported(ready: bool) -> None:
    assert ready
    clip = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json")
    for sid in SCENARIOS:
        assert "opportunity_lower_clip_rate" in clip["clip_by_scenario"][sid]


def test_profile_s1_group_support_gate(ready: bool) -> None:
    assert ready
    clip = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json")
    for sid in SCENARIOS:
        assert float(clip["support_by_scenario"][sid]["minimum_positive_group_expected_arrivals"]) >= 20


def test_profile_s1_stratum_support_gate(ready: bool) -> None:
    assert ready
    clip = _j(AUDIT / "E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json")
    for sid in SCENARIOS:
        assert float(clip["support_by_scenario"][sid]["minimum_positive_stratum_expected_arrivals"]) >= 5


def test_18_profile_s1_single_arm_traces(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["hard_trace_count"]) == 18
    for sid in SCENARIOS:
        for seed in SEEDS:
            m = _j(OUT / "scenarios" / sid / "traces" / str(seed) / "eventtrace_manifest.json")
            assert m["arms"] == 1
            assert m["frozen_intercepts"] is True


def test_s1_balanced_direction(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/balanced/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"


def test_s2_opportunity_only_direction(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/opportunity_only/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"


def test_s3_observation_only_direction(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/observation_only/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"


def test_s4_usable_only_direction(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/usable_only/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"


def test_s5_aligned_accumulation(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/complete_aligned/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"
    assert c["hard_certificate"]["checks"]["accumulation"] is True


def test_s6_counteraction(ready: bool) -> None:
    assert ready
    c = _j(OUT / "scenarios/complete_counteracting/DIRECTION_CERTIFICATE.json")
    assert c["status"] == "PASS"
    assert c["hard_certificate"]["checks"]["cancellation"] is True


def test_no_hardcoded_direction_pass(ready: bool) -> None:
    assert ready
    src = (ROOT / "src/raven_mcs/e2/traffic_profiles/runner_consistency.py").read_text(encoding="utf-8")
    assert "hard_cancellation_visible = True" not in src
    cert = _j(FROZEN / "traffic_s1_s6_direction_certificate.json")
    assert int(cert["hardcoded_pass_count"]) == 0


def test_no_atomic_tv_primary_gate(ready: bool) -> None:
    assert ready
    cert = _j(FROZEN / "traffic_s1_s6_direction_certificate.json")
    assert cert["atomic_hard_tv_primary_gate"] is False


def test_no_training_artifacts(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["training_artifact_count"]) == 0


def test_seed29001_not_read(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["seed_29001_read_count"]) == 0


def test_validation_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["validation_seed_read_count"]) == 0


def test_formal_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json")
    assert int(stop["formal_seed_read_count"]) == 0


def test_final_profile_s1_registry(ready: bool) -> None:
    assert ready
    for name in (
        "traffic_s1_s6_profile_registry.json",
        "traffic_s1_s6_profile_registry.yaml",
        "traffic_s1_s6_direction_certificate.json",
        "traffic_s1_s6_runner_identity.json",
        "traffic_s1_s6_profile_s1_candidate_registry.json",
    ):
        assert (FROZEN / name).is_file()
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    assert reg["status"] == "FROZEN"
    assert reg["selected_strength"] == "PROFILE-S1"
    assert reg["selection_reason"] == "deterministic_support_fallback"
