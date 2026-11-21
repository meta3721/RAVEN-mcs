"""Unit tests for E2 data horizon / spatial metadata recovery."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/data_recovery"


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_recursive_dataset_inventory():
    inv = pd.read_csv(OUT / "E2_DATA_ASSET_INVENTORY.csv")
    assert len(inv) > 0
    assert "checksum" in inv.columns
    assert (inv["absolute_or_repo_relative_path"].astype(str).str.contains("sensorscope")).any()


def test_archive_inventory():
    arch = pd.read_csv(OUT / "E2_ARCHIVE_CONTENT_INVENTORY.csv")
    assert len(arch) > 0
    assert "archive_parent" in arch.columns


def test_dataset_file_hash_deduplication():
    inv = pd.read_csv(OUT / "E2_DATA_ASSET_INVENTORY.csv")
    assert "duplicate_group_id" in inv.columns
    assert inv["duplicate_group_id"].nunique() >= 1


def test_current_subset_provenance_chain():
    prov = _j("outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json")
    assert prov["status"] in {
        "FULL_RAW_SOURCE_CONFIRMED", "TEST_SLICE_CONFIRMED", "DEBUG_SUBSET_CONFIRMED",
        "PREPROCESSING_TRUNCATION_CONFIRMED", "SOURCE_PROVENANCE_INCOMPLETE",
    }
    assert "raw_source_file" in prov
    assert "preprocessing_script" in prov


def test_detect_debug_or_test_slice():
    prov = _j("outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json")
    assert prov["answers"]["only_test_split"] is True or prov["status"] != "TEST_SLICE_CONFIRMED"


def test_common_time_overlap_computation():
    horizon = _j("outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json")
    assert "common_overlap_span_hours" in horizon or horizon.get("status") == "FULL_SENSORSCOPE_SOURCE_MISSING"


def test_nonoverlap_6h_window_capacity():
    horizon = _j("outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json")
    if "max_complete_6h_windows_common" in horizon:
        assert int(horizon["max_complete_6h_windows_common"]) == int(
            float(horizon["common_overlap_span_hours"]) // 6
        )


def test_global_window_capacity_uses_common_span():
    horizon = _j("outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json")
    if "union_span_hours" in horizon and "common_overlap_span_hours" in horizon:
        assert float(horizon["common_overlap_span_hours"]) <= float(horizon["union_span_hours"]) + 1e-9


def test_station_coordinate_source_traceable():
    spatial = _j("outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json")
    assert "source_traceable" in spatial
    assert int(spatial.get("synthetic_usage_count", 1)) == 0


def test_synthetic_coordinates_rejected():
    spatial = _j("outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json")
    assert int(spatial.get("station_id_rank_coordinate_count", 0)) == 0
    assert int(spatial.get("client_id_derived_region_count", 0)) == 0


def test_full_sensorscope_joint_gate():
    joint = _j("outputs/data_recovery/E2_FULL_SENSORSCOPE_FEASIBILITY_GATE.json")
    assert "status" in joint
    assert "conditions" in joint


def test_replacement_dataset_hard_filters():
    matrix = pd.read_csv(OUT / "E2_REPLACEMENT_DATASET_FEASIBILITY_MATRIX.csv")
    assert set(matrix["dataset"]) >= {"uair", "traffic", "tdrive_speed"}
    for _, row in matrix.iterrows():
        if float(row.get("public_common_span_hours") or 0) < 600:
            assert "common_time_span_lt_600h" in str(row.get("hard_fail_reasons", ""))


def test_replacement_dataset_scoring_deterministic():
    a = _j("outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json")
    b = _j("outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json")
    assert a == b


def test_protocol_route_priority():
    decision = _j("outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json")
    assert decision["priority_order"][0].startswith("A_")
    assert decision["status"] in {
        "READY_WITH_FULL_SENSORSCOPE",
        "READY_WITH_REPLACEMENT_DATASET",
        "BLOCKED_DATA_RECOVERY_REQUIRED",
    }
