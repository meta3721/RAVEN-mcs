"""Unit tests for Traffic S1-S6 profile freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from raven_mcs.e2.stage2.usable import ALLOWED_Q_FEATURES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_profiles"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic_profiles"
SEEDS = (28201, 28202, 28203)
SCENARIOS = [
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
]


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json").is_file()


def test_pooled_hard_client_stratum_tv_is_diagnostic(ready: bool) -> None:
    assert ready
    corr = _j(FROZEN / "balanced_canary_gate_correction.json")
    assert corr["diagnostic_only"][0]["metric"] == "pooled_hard_client_stratum_TV"
    assert corr["diagnostic_only"][0]["absolute_veto"] is False


def test_stage2_eligible_not_q_numeric_feature(ready: bool) -> None:
    assert "stage2_eligible" not in ALLOWED_Q_FEATURES
    q = _j(AUDIT / "E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json")
    assert int(q["stage2_eligible_in_q_numeric_features"]) == 0


def test_observed_count_not_q_numeric_feature(ready: bool) -> None:
    assert "observed_count" not in ALLOWED_Q_FEATURES
    q = _j(AUDIT / "E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json")
    assert int(q["observed_count_in_q_numeric_features"]) == 0


def test_expected_opportunity_mass_formula(ready: bool) -> None:
    assert ready
    df = pd.read_parquet(OUT / "scenarios/balanced/expected_opportunity_mass.parquet")
    assert "expected_mass" in df.columns
    assert abs(float(df["expected_mass"].mean()) - 0.55) < 0.02


def test_expected_observation_mass_formula(ready: bool) -> None:
    assert ready
    opp = pd.read_parquet(OUT / "scenarios/balanced/expected_opportunity_mass.parquet")
    obs = pd.read_parquet(OUT / "scenarios/balanced/expected_observation_mass.parquet")
    ratio = float((obs["expected_mass"] / opp["expected_mass"].clip(lower=1e-12)).mean())
    assert abs(ratio - 0.2) < 0.02


def test_expected_arrival_mass_formula(ready: bool) -> None:
    assert ready
    obs = pd.read_parquet(OUT / "scenarios/balanced/expected_observation_mass.parquet")
    arr = pd.read_parquet(OUT / "scenarios/balanced/expected_arrival_mass.parquet")
    ratio = float((arr["expected_mass"] / obs["expected_mass"].clip(lower=1e-12)).mean())
    assert abs(ratio - 0.6) < 0.05


def test_expected_eligibility_probability_formula(ready: bool) -> None:
    assert ready
    cw = pd.read_parquet(OUT / "scenarios/balanced/expected_client_window_activity.parquet")
    assert "P_eligible" in cw.columns
    assert float(cw["P_eligible"].min()) > 0
    assert float(cw["P_eligible"].max()) <= 1.0
    assert "expected_usable_attempt" in cw.columns


def test_s1_s6_registry_exactly_six_scenarios(ready: bool) -> None:
    assert ready
    reg = _j(FROZEN / "traffic_s1_s6_profile_registry.json")
    assert set(reg["scenarios"]) == set(SCENARIOS)
    assert len(reg["scenarios"]) == 6


def test_one_parameter_set_per_scenario(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["parameter_sets_per_scenario"]) == 1


def test_no_grid_search(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["grid_search_count"]) == 0


def test_global_marginal_rates_preserved(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        cert = _j(OUT / "scenarios" / sid / "DIRECTION_CERTIFICATE.json")
        assert cert["rates"]["rate_pass"] is True


def test_s2_opportunity_only_direction(ready: bool) -> None:
    assert ready
    cert = _j(OUT / "scenarios/opportunity_only/DIRECTION_CERTIFICATE.json")
    assert cert["status"] == "PASS"
    assert cert["expected"]["signed"]["opp"] > 0


def test_s3_observation_only_direction(ready: bool) -> None:
    assert ready
    cert = _j(OUT / "scenarios/observation_only/DIRECTION_CERTIFICATE.json")
    assert cert["status"] == "PASS"
    assert abs(cert["expected"]["D_opp"]) <= 0.01
    assert cert["expected"]["signed"]["obs"] > 0


def test_s4_usable_only_direction(ready: bool) -> None:
    assert ready
    cert = _j(OUT / "scenarios/usable_only/DIRECTION_CERTIFICATE.json")
    assert cert["status"] == "PASS"
    assert cert["expected"]["signed"]["arr"] > 0


def test_s5_aligned_direction(ready: bool) -> None:
    assert ready
    cert = _j(OUT / "scenarios/complete_aligned/DIRECTION_CERTIFICATE.json")
    assert cert["status"] == "PASS"
    s = cert["expected"]["signed"]
    assert s["opp"] > 0 and s["obs"] > 0 and s["arr"] > 0


def test_s6_counteracting_direction(ready: bool) -> None:
    assert ready
    cert = _j(OUT / "scenarios/complete_counteracting/DIRECTION_CERTIFICATE.json")
    assert cert["status"] == "PASS"
    s = cert["expected"]["signed"]
    assert s["arr"] < s["obs"]


def test_three_single_arm_seeds_per_scenario(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        for seed in SEEDS:
            m = _j(OUT / "scenarios" / sid / "traces" / str(seed) / "eventtrace_manifest.json")
            assert m["arms"] == 1
            assert m["seed"] == seed


def test_no_antithetic_average(ready: bool) -> None:
    assert ready
    for sid in SCENARIOS:
        for seed in SEEDS:
            m = _j(OUT / "scenarios" / sid / "traces" / str(seed) / "eventtrace_manifest.json")
            assert m["antithetic_arm_count"] == 1


def test_no_training_artifacts(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["training_artifact_count"]) == 0


def test_seed29001_not_read(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["seed_29001_read_count"]) == 0


def test_validation_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["validation_seed_read_count"]) == 0


def test_formal_seed_noninspection(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    assert int(stop["formal_seed_read_count"]) == 0


def test_complete_profile_registry(ready: bool) -> None:
    assert ready
    for name in (
        "traffic_s1_s6_profile_registry.json",
        "traffic_s1_s6_profile_registry.yaml",
        "traffic_s1_s6_direction_certificate.json",
        "traffic_s1_s6_identity.json",
    ):
        assert (FROZEN / name).is_file()
