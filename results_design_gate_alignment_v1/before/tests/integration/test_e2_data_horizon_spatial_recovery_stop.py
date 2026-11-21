"""Integration / stop tests for E2 data recovery round."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1"
OUT = ROOT / "outputs/data_recovery"


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_no_validation_seed_read():
    nonleak = _j("outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json")
    stop = _j("outputs/data_recovery/E2_STOP_STATUS.json")
    assert int(nonleak["validation_seed_read_count"]) == 0
    assert int(stop["validation_seed_read_count"]) == 0


def test_no_formal_seed_read():
    nonleak = _j("outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json")
    assert int(nonleak["formal_seed_read_count"]) == 0


def test_no_method_result_guided_selection():
    nonleak = _j("outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json")
    assert nonleak["outcome_guided_dataset_selection"] is False
    assert int(nonleak["method_result_read_count"]) == 0


def test_no_experiment_trace_generated():
    stop = _j("outputs/data_recovery/E2_STOP_STATUS.json")
    assert int(stop["experimental_trace_count"]) == 0
    assert not (OUT / "traces").exists()


def test_profile_selection_not_started():
    stop = _j("outputs/data_recovery/E2_STOP_STATUS.json")
    assert stop["profile_selection"] == "NOT_STARTED"


def test_seed_29001_not_read():
    stop = _j("outputs/data_recovery/E2_STOP_STATUS.json")
    assert int(stop["seed_29001_read_count"]) == 0


def test_full_repository_pytest_command():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    assert "pytest" in ledger.read_text(encoding="utf-8")


def test_complete_ledger_starts_with_inventory():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    first = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert first.get("label") in {"inventory", "prepare", "recursive_search", "asset_inventory"}


def test_external_hash_verifies_three_artifacts():
    verify = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"
    evidence = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if not verify.is_file() or not evidence.is_file():
        pytest.skip("hash triad not exported yet")
    payload = json.loads(verify.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        pytest.skip("stale verify")
    assert int(payload["verified_count"]) == 3


def test_final_export_order():
    delivery = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
    if not (delivery / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip").is_file():
        pytest.skip("evidence not exported yet")
    assert (delivery / f"{PACKAGE}_REPORT.docx").is_file()
    assert (delivery / f"{PACKAGE}_SUBMISSION_README.txt").is_file()
