"""Integration / stop tests for public-target q-seal."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_TRAFFIC_PUBLIC_TARGET_AND_Q_FEATURE_SEAL_R1"
STOP = ROOT / "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def stop() -> dict:
    if not STOP.is_file():
        pytest.skip("prepare missing")
    return _j(STOP)


def test_seed29001_not_read(stop: dict) -> None:
    assert int(stop.get("seed_29001_read_count", -1)) == 0


def test_validation_seed_noninspection(stop: dict) -> None:
    assert int(stop.get("validation_seed_read_count", -1)) == 0


def test_formal_seed_noninspection(stop: dict) -> None:
    assert int(stop.get("formal_seed_read_count", -1)) == 0


def test_full_repository_pytest_command() -> None:
    seq = (ROOT / "scripts/_run_e2pt_ledger_sequence.py").read_text(encoding="utf-8")
    assert "full_repository_tests" in seq
    assert "pytest" in seq


def test_complete_ledger_starts_with_public_target_generation() -> None:
    if not LEDGER.is_file():
        pytest.skip("ledger not yet written")
    lines = [ln for ln in LEDGER.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines
    assert json.loads(lines[0])["label"] == "public_target_generation"
    assert all(int(json.loads(ln).get("exit_code", 1)) == 0 for ln in lines)


def test_external_hash_verifies_three_artifacts() -> None:
    verify = DELIV / "FINAL_DELIVERABLE_HASHES_VERIFY.json"
    if not verify.is_file():
        pytest.skip("hash verify not yet written")
    v = _j(verify)
    assert v["status"] == "PASS"
    assert int(v["verified_count"]) == 3
    assert int(v["hash_mismatch_count"]) == 0


def test_final_export_order() -> None:
    seq = (ROOT / "scripts/_run_e2pt_ledger_sequence.py").read_text(encoding="utf-8")
    assert seq.index('"export"') < seq.index('"hash_verify"')


def test_stop_status_allowed(stop: dict) -> None:
    assert stop["status"] in {
        "READY_FOR_TRAFFIC_BALANCED_DESIGN_CANARY",
        "BLOCKED_TRAFFIC_PUBLIC_TARGET_SEAL_FAILED",
    }
    assert stop["profile_selection"] == "NOT_STARTED"
    assert stop["e3_e9_status"] == "NOT_STARTED"
    assert int(stop["hard_trace_count"]) == 0
