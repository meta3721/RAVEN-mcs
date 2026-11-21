"""Unit tests for E2 global-window / finite-sample gate repair."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"
OUT = ROOT / "outputs/e2_global_window"
DESIGN = set(range(28101, 28121))
VALIDATION = {29101, 29102, 29103, 29104, 29105}


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_same_global_window_boundaries_for_all_clients():
    audit = _j("outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json")
    assert int(audit.get("client_specific_boundary_count", 0)) == 0
    # Either PASS with common boundaries, or capacity-blocked before build.
    assert audit["status"] in {"PASS", "BLOCKED_GLOBAL_WINDOW_CAPACITY_INSUFFICIENT"}
    if audit["status"] == "PASS":
        assert audit.get("common_boundary_status") == "PASS"


def test_global_windows_nonoverlapping():
    audit = _j("outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json")
    assert int(audit.get("overlap_count", 0)) == 0


def test_atomic_unit_assigned_to_exactly_one_window():
    audit = _j("outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json")
    assert int(audit.get("multiply_assigned_unit_count", 0)) == 0
    if audit["status"] == "PASS":
        assert int(audit["unassigned_unit_count"]) == 0


def test_no_cross_window_atomic_reuse():
    audit = _j("outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json")
    assert int(audit.get("cross_window_duplicate_unit_count", 0)) == 0


def test_true_spatial_identity_not_client_id_fold():
    spatial = _j("outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json")
    assert int(spatial.get("client_id_derived_region_count", 0)) == 0
    rejected = spatial.get("rejected_client_id_fold") or {}
    assert rejected.get("rejected") is True


def test_no_synthetic_coordinate_usage():
    spatial = _j("outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json")
    assert int(spatial.get("synthetic_usage_count", 0)) == 0


def test_design_validation_seed_disjoint():
    iso = _j("outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json")
    assert int(iso["intersection_count"]) == 0
    assert set(iso["design_seed_registry"]) == DESIGN
    assert set(iso["validation_seed_registry"]) == VALIDATION


def test_validation_seed_files_not_read():
    iso = _j("outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json")
    assert int(iso["validation_read_count"]) == 0


def test_global_window_identity_fixed_across_design_seeds():
    identity = _j("configs/frozen/e2_global_windows/global_server_windows_identity.json")
    assert "identity_hash" in identity
    # Identity does not embed design seed ids.
    assert "28101" not in json.dumps(identity)


def test_single_arm_design_replicate_count_1000():
    summary = _j("outputs/e2_global_window/E2_GLOBAL_WINDOW_SINGLE_ARM_DESIGN_SUMMARY.json")
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    if stop["status"] != "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION":
        assert int(summary.get("n_replicates", 0)) == 0
        assert summary.get("status") == "NOT_RUN"
    else:
        assert int(summary["n_replicates"]) == 1000


def test_antithetic_not_used():
    summary = _j("outputs/e2_global_window/E2_GLOBAL_WINDOW_SINGLE_ARM_DESIGN_SUMMARY.json")
    assert summary.get("antithetic_used") is False


def test_cert_l32_l16_l8_use_real_spatial_mapping():
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    if stop["status"] != "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION":
        pytest.skip("cert mappings not frozen under protocol block")
    for name in ("cert_l32_mapping.parquet", "cert_l16_mapping.parquet", "cert_l8_mapping.parquet"):
        assert (ROOT / "configs/frozen/e2_finite_sample_gate" / name).is_file()


def test_finite_sample_gate_uses_design_only():
    proto = _j("configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json")
    assert set(proto["design_seeds"]) == DESIGN
    assert proto["validation_execution"] == "NOT_RUN_THIS_ROUND"


def test_prediction_intervals_frozen_before_validation():
    intervals = _j("configs/frozen/e2_finite_sample_gate/validation_prediction_intervals.json")
    iso = _j("outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json")
    assert int(iso["validation_read_count"]) == 0
    assert intervals["status"] in {"FROZEN", "NOT_ESTIMATED"}


def test_aggregate_bias_thresholds_frozen():
    proto = _j("configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json")
    thr = proto["aggregate_thresholds"]
    assert float(thr["D_TV_mean_group_mass"]) == 0.02
    assert float(thr["D_TV_mean_cert_mass"]) == 0.03


def test_outside_interval_allowance_fixed():
    proto = _j("configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json")
    assert int(proto["outside_interval_allowance"]) == 2


def test_old_five_of_five_rule_tombstoned():
    tomb = _j("outputs/audits/E2_PRIOR_LOCAL_WINDOW_AND_GATE_TOMBSTONE.json")
    assert tomb.get("invalid_reason_five_of_five_fixed_threshold_gate") is True
    proto = _j("configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json")
    assert proto.get("old_five_of_five_fixed_threshold_rule") == "TOMBSTONED"
