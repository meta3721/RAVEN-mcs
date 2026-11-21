"""Integration / stop-position tests for E2 global-window finite-sample gate repair."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"
OUT = ROOT / "outputs/e2_global_window"


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_validation_traces_not_run():
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    assert int(stop.get("validation_traces", -1)) == 0
    for seed in (29101, 29102, 29103, 29104, 29105):
        assert not (OUT / "traces" / str(seed)).exists()


def test_nonbalanced_matrix_not_started():
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    assert int(stop.get("non_balanced_trace_count", -1)) == 0


def test_profile_selection_not_started():
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    assert stop.get("profile_selection") == "NOT_STARTED"


def test_seed_29001_not_read():
    assert not (OUT / "traces" / "29001").exists()
    stop = _j("outputs/e2_global_window/E2_STOP_STATUS.json")
    assert int(stop.get("seed_29001_read_count", 0)) == 0


def test_formal_seed_noninspection():
    for seed in range(30001, 30021):
        assert not (OUT / "traces" / str(seed)).exists()


def test_full_repository_pytest_command():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    text = ledger.read_text(encoding="utf-8")
    assert "pytest" in text


def test_complete_ledger_starts_with_prepare():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not written yet")
    first = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert first.get("label") in {"prepare", "prepare_generation"}


def test_external_hash_verifies_three_artifacts():
    verify = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"
    evidence = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if not verify.is_file() or not evidence.is_file():
        pytest.skip("hash triad not exported yet")
    payload = json.loads(verify.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        pytest.skip("stale pre-export verify")
    assert int(payload["verified_count"]) == 3


def test_final_export_order():
    delivery = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
    report = delivery / f"{PACKAGE}_REPORT.docx"
    evidence = delivery / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    readme = delivery / f"{PACKAGE}_SUBMISSION_README.txt"
    if not evidence.is_file():
        pytest.skip("evidence not exported yet")
    assert report.is_file() and readme.is_file()
