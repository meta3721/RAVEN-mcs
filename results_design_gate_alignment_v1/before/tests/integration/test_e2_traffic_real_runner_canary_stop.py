"""Integration stop-status tests for Traffic Real Runner Canary."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/e2_traffic_real_runner_canary"
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"


def _j(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ready() -> bool:
    return (OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json").is_file()


def test_stop_status_ready_or_blocked(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert stop["status"] in {
        "READY_FOR_TRAFFIC_E2_FORMAL_RUNS",
        "PENDING_LEDGER_GATES",
        "BLOCKED_TRAFFIC_REAL_RUNNER_CANARY_FAILED",
        "BLOCKED_TRAFFIC_REAL_RUNNER_LEDGER_NOT_CLOSED",
    }


def test_ready_implies_formal_next_round(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    if stop["status"] == "READY_FOR_TRAFFIC_E2_FORMAL_RUNS":
        assert stop["next_authorized_round"] == "E2-TRAFFIC-FORMAL-RUNS-R1"
        assert int(stop["completed_run_count"]) == 30
        assert int(stop["failed_run_count"]) == 0
        assert int(stop["eventtrace_count"]) == 6
        assert int(stop["cross_method_trace_mismatch_count"]) == 0
        assert stop.get("reaudit_only") is False
        assert stop.get("fresh_rerun") is True
    if stop["status"] == "BLOCKED_TRAFFIC_REAL_RUNNER_LEDGER_NOT_CLOSED":
        assert stop.get("next_authorized_round") is None


def test_e3_e9_not_started(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert stop["e3_e9_status"] == "NOT_STARTED"


def test_profile_s1_selected(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    assert stop["selected_strength"] == "PROFILE-S1"


def test_deliverables_exist_when_ready(ready: bool) -> None:
    assert ready
    stop = _j(OUT / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    if stop["status"] != "READY_FOR_TRAFFIC_E2_FORMAL_RUNS":
        pytest.skip("blocked canary")
    d = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1"
    if not d.is_dir():
        pytest.skip("ledger-closure deliverables not exported yet")
    assert (d / "E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1_REPORT.docx").is_file()
    assert (d / "E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1_SUBMISSION_README.txt").is_file()
    assert (d / "TO_SUBMIT_E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1.zip").is_file()
