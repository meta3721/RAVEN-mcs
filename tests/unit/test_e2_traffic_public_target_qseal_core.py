"""Unit tests for traffic public-target / q-feature seal."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "configs/frozen/e2_traffic_public_target"
AUDIT = ROOT / "outputs/audits"
CANARY = ROOT / "outputs/e2_traffic_public_target_canary"
OUT = ROOT / "outputs/traffic_public_target"
N = 25800
W = 1.0 / N


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json").is_file()


def test_uniform_atomic_target_weight(ready: bool) -> None:
    assert ready
    df = pd.read_parquet(FROZEN / "atomic_public_target.parquet")
    assert (df["varpi_i_tar"] - W).abs().max() <= 1e-15


def test_atomic_target_weight_sum_one(ready: bool) -> None:
    df = pd.read_parquet(FROZEN / "atomic_public_target.parquet")
    assert abs(float(df["varpi_i_tar"].sum()) - 1.0) <= 1e-12
    assert len(df) == N


def test_target_weight_independent_of_target_value(ready: bool) -> None:
    ident = _j(FROZEN / "atomic_public_target_identity.json")
    assert ident["target_value_dependency_count"] == 0
    df = pd.read_parquet(FROZEN / "atomic_public_target.parquet")
    assert "target_value" not in df.columns


def test_mu_derived_from_atomic_counts_only(ready: bool) -> None:
    group = pd.read_parquet(FROZEN / "target_group_mass.parquet")
    audit = _j(AUDIT / "E2_TRAFFIC_GROUP_TARGET_AUDIT.json")
    assert abs(float(group["mu_g"].sum()) - 1.0) <= 1e-12
    assert audit["target_value_dependency_count"] == 0
    # mu == count / 25800
    for r in group.itertuples():
        assert abs(float(r.mu_g) - float(r.atomic_count) / N) <= 1e-12


def test_region_mapping_uses_coordinates_only(ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json")
    assert audit["weighting"] == "station_equal_weight"
    assert audit["target_value_dependency_count"] == 0


def test_region_mapping_station_equal_weight(ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json")
    assert audit["weighting"] == "station_equal_weight"
    assert "mass" not in audit.get("first_split_axis", "")


def test_region_mapping_independent_of_target_value(ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json")
    assert audit["target_value_dependency_count"] == 0
    assert audit["status"] == "PASS"


def test_all_43_stations_unique_region(ready: bool) -> None:
    m = pd.read_parquet(FROZEN / "station_region_mapping.parquet")
    assert m["station_id"].nunique() == 43
    assert len(m) == 43
    assert m["region_id"].nunique() == 4
    assert not m["station_id"].duplicated().any()


def test_stratum_is_region_time_day(ready: bool) -> None:
    s = pd.read_parquet(FROZEN / "opportunity_stratum_target.parquet")
    for sid in s["stratum_id"].astype(str):
        parts = sid.split("::")
        assert len(parts) == 3
        assert parts[0].startswith("region")
        assert parts[1].startswith("block")
        assert parts[2] in {"weekday", "weekend"}


def test_lambda_mass_sum_one(ready: bool) -> None:
    s = pd.read_parquet(FROZEN / "opportunity_stratum_target.parquet")
    assert abs(float(s["Lambda_s_tar"].sum()) - 1.0) <= 1e-12


def test_pi_mass_sum_one(ready: bool) -> None:
    cs = pd.read_parquet(FROZEN / "client_stratum_target.parquet")
    assert abs(float(cs["pi_k_s_tar"].sum()) - 1.0) <= 1e-12


def test_observed_count_only_for_stage2_eligibility(ready: bool) -> None:
    q = _j(FROZEN / "q_feature_manifest.json")
    assert q["stage2_eligibility"] == "1{observed_count > 0}"
    assert q["observed_count_role"] == "eligibility_only_not_q_input"


def test_observed_count_not_in_q_features(ready: bool) -> None:
    q = _j(FROZEN / "q_feature_manifest.json")
    assert "observed_count" not in q["actual_features"]
    assert "observed_count" not in q["allowed_features"]
    audit = _j(AUDIT / "E2_TRAFFIC_Q_FEATURE_AUDIT.json")
    assert audit["observed_count_dependency_count"] == 0


def test_target_value_not_in_q_features(ready: bool) -> None:
    q = _j(FROZEN / "q_feature_manifest.json")
    assert "target_value" not in q["actual_features"]
    audit = _j(AUDIT / "E2_TRAFFIC_Q_FEATURE_AUDIT.json")
    assert audit["target_value_dependency_count"] == 0


def test_target_value_not_in_opportunity_features(ready: bool) -> None:
    leak = _j(AUDIT / "E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json")
    assert leak["target_value_dependency_in_opportunity_features"] == 0


def test_target_value_not_in_observation_features(ready: bool) -> None:
    leak = _j(AUDIT / "E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json")
    assert leak["target_value_dependency_in_observation_features"] == 0


def test_end_to_end_leakage_scan_not_hardcoded(ready: bool) -> None:
    leak = _j(AUDIT / "E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json")
    assert "source_scan_hits" in leak
    assert leak["hard_coded_leakage_pass_constant_count"] == 0
    assert leak["status"] == "PASS"


def test_core_theory_formula_count_zero(ready: bool) -> None:
    theory = _j(AUDIT / "E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json")
    assert theory["core_formula_modification_count"] == 0
    assert theory["status"] == "PASS"


def test_static_canary_seed_27901_only(ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json")
    assert gate["seed"] == 27901
    assert gate["seed_29001_used"] is False
    assert gate["status"] == "PASS"


def test_no_hard_trace_generated(ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json")
    assert gate["bernoulli_hard_event"] is False
    assert gate["counts"]["hard_trace_count"] == 0


def test_no_training_artifact_generated(ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json")
    assert gate["local_training"] is False
    assert gate["counts"]["training_artifact_count"] == 0
