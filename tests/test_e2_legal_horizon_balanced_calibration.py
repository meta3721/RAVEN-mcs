"""Regression tests for the legal-horizon Balanced calibration stop."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
SEEDS = (29101, 29102, 29103, 29104, 29105)


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_legal_horizon_is_100_with_maximum_105():
    audit = read_json("outputs/audits/E2_LEGAL_HORIZON_AUDIT.json")
    assert audit["status"] == "PASS"
    assert audit["requested_windows"] == 100
    assert audit["maximum_legal_continuous_windows"] == 105


def test_source_reuse_is_zero():
    audit = read_json("outputs/audits/E2_100_WINDOW_SOURCE_UNIQUENESS_AUDIT.json")
    assert audit["status"] == "PASS"
    assert audit["source_reuse_count"] == 0


def test_soft_balanced_calibration_passes():
    audit = read_json("outputs/e2_balanced_calibration/E2_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    assert audit["status"] == "PASS"
    assert len(audit["per_seed"]) == 5
    assert all(row["status"] == "PASS" for row in audit["per_seed"])
    assert audit["unsupported_target_cell_count"] == 0


def test_hard_pre_gate_failure_is_recorded_not_hidden():
    pre = read_json("outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_SUMMARY.json")
    stop = read_json("outputs/e2_balanced_calibration/E2_STOP_STATUS.json")
    assert pre["status"] == "BALANCED_PRE_GATE_FAIL"
    assert pre["pass_count"] == 0
    assert pre["required"] == 5
    assert stop["status"] == "BALANCED_PRE_GATE_FAIL"


def test_five_balanced_traces_have_stage2_evidence():
    required = (
        "manifest.json", "resolved_config.yaml", "group_mass_diagnostics_100.json",
        "true_stratum_mass_diagnostics_100.json", "chronology_audit.json",
        "failed_attempt_audit.json", "q_feature_audit.json",
    )
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced"
        for name in required:
            assert (trace / name).is_file(), f"missing {trace / name}"


def test_matrix_155_is_blocked():
    if (ROOT / "outputs/e2_balanced_calibration/E2_PROFILE_GATE_BY_SEED.csv").is_file():
        pytest.fail("matrix-155 must remain blocked after hard Balanced pre-gate failure")
    selection = read_json("outputs/e2_balanced_calibration/E2_PROFILE_SELECTION.json")
    assert selection["selected_profile_id"] is None


def test_seed_29001_and_formal_outputs_are_absent():
    traces = ROOT / "outputs/e2_balanced_calibration/traces"
    assert not (traces / "29001").exists()
    assert not (traces / "30001").exists()


def test_gate_records_expected_stop_when_available():
    path = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
    if not path.is_file():
        pytest.skip("gate runner has not executed yet")
    gate = json.loads(path.read_text(encoding="utf-8"))
    assert gate["status"] == "PASS"
    assert gate["gates"]["E2LB-G5"] == "EXPECTED_FAIL_RECORDED"
    assert gate["gates"]["E2LB-G6"] == "BLOCKED_AS_EXPECTED"
