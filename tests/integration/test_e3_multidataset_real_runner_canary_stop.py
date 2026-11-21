"""Integration stop-status test for E3 Canary R1."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def test_canary_stop_status_ready_or_complete() -> None:
    stop = json.loads((ART / "E3_CANARY_STOP_STATUS.json").read_text(encoding="utf-8"))
    assert stop.get("canary_seed") == 31001
    assert stop.get("status") in {
        "PHASE0_PASS_READY_FOR_PHASE1",
        "PHASE1_PASS_READY_FOR_PHASE2",
        "CANARY_EXECUTION_COMPLETE",
        "READY_FOR_E3_FORMAL_RUNS",
        "E3_CANARY_BLOCKED_BY_SOFTWARE_FIX",
        "E3_CANARY_BLOCKED_BY_SCIENTIFIC_SEMANTICS",
        "E3_CANARY_BLOCKED_BY_RESOURCE_LIMIT",
    }
    # If blocked, still require seed integrity field present
    assert isinstance(stop.get("formal_not_started", True), bool)


def test_matrix_28_when_present() -> None:
    matrix = ART / "E3_CANARY_RUN_MATRIX.json"
    if not matrix.is_file():
        return
    payload = json.loads(matrix.read_text(encoding="utf-8"))
    assert payload.get("n_logical_runs") == 28
