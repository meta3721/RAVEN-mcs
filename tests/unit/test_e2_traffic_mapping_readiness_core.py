"""Unit tests for E2 traffic mapping readiness."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/traffic_mapping"
AUDIT = ROOT / "outputs/audits"
FROZEN = ROOT / "configs/frozen/e2_traffic"
CANARY = ROOT / "outputs/e2_traffic_canary"
ATOMIC = ROOT / "data/processed/traffic/atomic_units.parquet"


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def artifacts_ready() -> bool:
    return (OUT / "E2_TRAFFIC_STOP_STATUS.json").is_file()


def test_traffic_row_count_30960(artifacts_ready: bool) -> None:
    assert artifacts_ready
    df = pd.read_parquet(ATOMIC)
    assert len(df) == 30960
    assert _j(OUT / "E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json")["row_count"] == 30960


def test_traffic_station_count_43(artifacts_ready: bool) -> None:
    dense = _j(OUT / "E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    assert dense["station_count"] == 43


def test_traffic_timestamp_count_720(artifacts_ready: bool) -> None:
    dense = _j(OUT / "E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    assert dense["unique_timestamp_count"] == 720


def test_each_station_has_same_720_timestamps(artifacts_ready: bool) -> None:
    cov = pd.read_csv(OUT / "E2_TRAFFIC_STATION_TIME_COVERAGE.csv")
    assert len(cov) == 43
    assert (cov["timestamp_count"] == 720).all()
    dense = _j(OUT / "E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    assert dense["common_timestamp_count"] == 720
    assert dense["station_timestamp_symmetric_difference_count"] == 0


def test_no_missing_station_time_cells(artifacts_ready: bool) -> None:
    dense = _j(OUT / "E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    assert dense["missing_station_time_cell_count"] == 0


def test_no_duplicate_station_time_cells(artifacts_ready: bool) -> None:
    dense = _j(OUT / "E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    assert dense["duplicate_station_time_cell_count"] == 0


def test_100_common_nonoverlap_6h_windows(artifacts_ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json")
    assert audit["global_window_count"] == 100
    assert audit["overlap_count"] == 0
    assert audit["status"] == "PASS"


def test_selected_atomic_count_25800(artifacts_ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json")
    assert audit["selected_atomic_count"] == 25800


def test_remainder_atomic_count_5160(artifacts_ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json")
    assert audit["remainder_atomic_count"] == 5160


def test_atomic_unique_window_assignment(artifacts_ready: bool) -> None:
    audit = _j(AUDIT / "E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json")
    assert audit["atomic_multiply_assigned_count"] == 0
    assert audit["cross_window_duplicate_count"] == 0


def test_station_reference_geometry_parses(artifacts_ready: bool) -> None:
    ref = _j(OUT / "E2_TRAFFIC_REFERENCE_PARSE_AUDIT.json")
    assert ref["parsed_coordinate_count"] > 0
    assert ref["CRS"] == "EPSG:4326"


def test_all_43_stations_match_reference(artifacts_ready: bool) -> None:
    spatial = _j(AUDIT / "E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json")
    assert spatial["exact_id_match_count"] == 43
    assert spatial["unmatched_processed_station_count"] == 0
    assert spatial["status"] == "PASS"


def test_no_synthetic_coordinates(artifacts_ready: bool) -> None:
    spatial = _j(AUDIT / "E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json")
    assert spatial["synthetic_coordinate_usage"] == 0
    assert spatial["missing_coordinate_count"] == 0


def test_target_field_selection_deterministic(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "target_field_identity.json")
    assert ident["target_field"] == "target_value"
    assert ident["status"] == "PASS"


def test_target_normalization_no_leakage(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "traffic_theory_mapping_identity.json")
    assert ident["normalization"]["type"] == "identity"
    assert "validation" not in str(ident["normalization"]["fitting_population"]).lower()


def test_four_time_groups(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "traffic_theory_mapping_identity.json")
    assert ident["group_count"] == 4


def test_spatial_time_day_strata(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "traffic_theory_mapping_identity.json")
    assert 1 <= int(ident["stratum_count"]) <= 32


def test_target_mass_sums_to_one(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "traffic_theory_mapping_identity.json")
    assert abs(float(ident["mu_g_sum"]) - 1.0) < 1e-9
    assert abs(float(ident["varpi_sum"]) - 1.0) < 1e-9


def test_client_stratum_target_sums_to_one(artifacts_ready: bool) -> None:
    ident = _j(FROZEN / "traffic_theory_mapping_identity.json")
    assert abs(float(ident["pi_mass_sum"]) - 1.0) < 1e-9


def test_two_stage_feature_whitelists(artifacts_ready: bool) -> None:
    two = _j(AUDIT / "E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json")
    assert two["opportunity_feature_whitelist"]
    assert two["observation_feature_whitelist"]
    assert two["usable_feature_whitelist"]
    assert two["status"] == "PASS"


def test_no_outcome_leakage(artifacts_ready: bool) -> None:
    two = _j(AUDIT / "E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json")
    assert two["outcome_leakage_count"] == 0
    assert two["uses_target_label"] is False


def test_core_theory_formulas_unchanged(artifacts_ready: bool) -> None:
    compat = _j(AUDIT / "E2_TRAFFIC_THEORY_COMPATIBILITY_AUDIT.json")
    assert compat["theory_modification_count"] == 0
    assert compat["core_formula_modification"] is False
    assert compat["status"] == "PASS"


def test_mapping_canary_seed_27901_only(artifacts_ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_MAPPING_CANARY_GATE.json")
    assert gate["seed"] == 27901
    assert gate["seed_29001_used"] is False
    assert gate["status"] == "PASS"


def test_no_hard_event_generated(artifacts_ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_MAPPING_CANARY_GATE.json")
    assert gate["bernoulli_hard_event"] is False
    assert gate["counts"]["hard_events"] == 0


def test_no_training_artifact_generated(artifacts_ready: bool) -> None:
    gate = _j(CANARY / "E2_TRAFFIC_MAPPING_CANARY_GATE.json")
    assert gate["local_training"] is False
    assert gate["counts"]["training_artifacts"] == 0
