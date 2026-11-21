"""Integration / stop tests for Traffic S1-S6 profile freeze."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_R1"
STOP = ROOT / "outputs/e2_traffic_profiles/E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
DELIV = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def stop() -> dict:
    if not STOP.is_file():
        pytest.skip("prepare missing")
    return _j(STOP)


def test_full_repository_pytest_command() -> None:
    seq = (ROOT / "scripts/_run_e2pf_ledger_sequence.py").read_text(encoding="utf-8")
    assert "full_repository_tests" in seq
    assert "pytest" in seq


def test_ledger_starts_with_real_profile_generation() -> None:
    if not LEDGER.is_file():
        pytest.skip("ledger not yet written")
    lines = [ln for ln in LEDGER.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines
    assert json.loads(lines[0])["label"] == "profile_generation"
    assert "prepare_e2_traffic_s1_s6_profile_freeze.py" in " ".join(
        str(x) for x in json.loads(lines[0])["command"]
    )
    assert all(int(json.loads(ln).get("exit_code", 1)) == 0 for ln in lines)


def test_external_hash_verifies_three_artifacts() -> None:
    verify = DELIV / "FINAL_DELIVERABLE_HASHES_VERIFY.json"
    if not verify.is_file():
        pytest.skip("hash verify not yet written")
    v = _j(verify)
    assert v["status"] == "PASS"
    assert int(v["verified_count"]) == 3


def test_final_export_order() -> None:
    seq = (ROOT / "scripts/_run_e2pf_ledger_sequence.py").read_text(encoding="utf-8")
    assert seq.index('"export"') < seq.index('"hash_verify"')


def test_seed29001_not_read(stop: dict) -> None:
    assert int(stop.get("seed_29001_read_count", -1)) == 0


def test_validation_seed_noninspection(stop: dict) -> None:
    assert int(stop.get("validation_seed_read_count", -1)) == 0


def test_formal_seed_noninspection(stop: dict) -> None:
    assert int(stop.get("formal_seed_read_count", -1)) == 0


def test_stop_status_allowed(stop: dict) -> None:
    assert stop["status"] in {
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY",
        "BLOCKED_TRAFFIC_PROFILE_FREEZE_FAILED",
        "BLOCKED_INPUT_IDENTITY_MISMATCH",
        "BLOCKED_MISSING_S1_S6_DIRECTION_REGISTRY",
    }
