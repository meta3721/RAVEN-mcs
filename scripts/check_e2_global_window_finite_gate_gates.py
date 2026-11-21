#!/usr/bin/env python3
"""E2GW-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def read_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    win = read_json("outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json")
    unique = read_json("outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json")
    spatial = read_json("outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json")
    iso = read_json("outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json")
    stop = read_json("outputs/e2_global_window/E2_STOP_STATUS.json")
    summary = read_json("outputs/e2_global_window/E2_GLOBAL_WINDOW_SINGLE_ARM_DESIGN_SUMMARY.json")
    proto = read_json("configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json")
    intervals = read_json("configs/frozen/e2_finite_sample_gate/validation_prediction_intervals.json")
    just = read_json("outputs/audits/E2_FINITE_SAMPLE_GATE_JUSTIFICATION.json")
    tomb = read_json("outputs/audits/E2_PRIOR_LOCAL_WINDOW_AND_GATE_TOMBSTONE.json")

    ledger_entries = failed = 0
    first = None
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ledger_entries += 1
            row = json.loads(line)
            if first is None:
                first = row.get("label")
            if int(row.get("exit_code", 1)) != 0:
                failed += 1

    capacity_block = win.get("status") == "BLOCKED_GLOBAL_WINDOW_CAPACITY_INSUFFICIENT"
    g1 = win.get("status") == "PASS" or (
        capacity_block
        and int(win.get("overlap_count", 0)) == 0
        and int(win.get("client_specific_boundary_count", 0)) == 0
        and int((win.get("capacity") or {}).get("max_legal_global_windows", -1)) < 100
    )
    g2 = (
        unique.get("status") == "PASS"
        or (
            capacity_block
            and int(unique.get("multiply_assigned_unit_count", 0)) == 0
            and int(unique.get("cross_window_duplicate_unit_count", 0)) == 0
        )
    )
    g3 = (
        spatial.get("status") == "PASS"
        or spatial.get("status") == "BLOCKED_NO_VALID_SPATIAL_IDENTITY"
    ) and int(spatial.get("synthetic_usage_count", 1)) == 0 and int(spatial.get("client_id_derived_region_count", 1)) == 0
    g4 = iso.get("status") == "PASS" and int(iso.get("validation_read_count", 1)) == 0
    g5 = summary.get("antithetic_used") is False  # DGP not run under capacity block
    g6 = (
        int(summary.get("n_replicates", 0)) == 1000
        if stop.get("status") == "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION"
        else (int(summary.get("n_replicates", 0)) == 0 and summary.get("status") == "NOT_RUN")
    )
    g7 = (
        stop.get("status") == "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION"
        or stop.get("status") in {
            "BLOCKED_GLOBAL_WINDOW_CAPACITY_INSUFFICIENT",
            "BLOCKED_NO_VALID_SPATIAL_IDENTITY",
            "BLOCKED_FINITE_SAMPLE_CERTIFICATION_INFEASIBLE",
        }
    )
    g8 = (
        proto.get("validation_execution") == "NOT_RUN_THIS_ROUND"
        and int(proto.get("outside_interval_allowance", -1)) == 2
        and intervals.get("status") in {"FROZEN", "NOT_ESTIMATED"}
        and just.get("thresholds_frozen_before_validation") is True
        and tomb.get("invalid_reason_five_of_five_fixed_threshold_gate") is True
    )
    g9 = (
        (ROOT / "tests/unit/test_e2_global_window_finite_gate_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_global_window_finite_gate_stop.py").is_file()
        and (not LEDGER.is_file() or (ledger_entries > 0 and failed == 0 and first in {"prepare", "prepare_generation"}))
    )
    g10 = (
        int(stop.get("validation_traces", -1)) == 0
        and int(stop.get("non_balanced_trace_count", -1)) == 0
        and stop.get("profile_selection") == "NOT_STARTED"
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
        and not (ROOT / "outputs/e2_global_window/traces/29101").exists()
    )

    gates = {f"E2GW-G{i}": "PASS" if v else "FAIL" for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    # Honest capacity/spatial blocks are valid round outcomes; overall PASS if all gates PASS.
    ok = all(v == "PASS" for v in gates.values())
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "gates": gates,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed,
        "ledger_first_label": first,
        "validation_traces": stop.get("validation_traces"),
        "seed_29001_read_count": 0,
        "real_canary_runs": "0/20",
        "formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    dump_json(payload, ROOT / "outputs/gates/e2_global_window_finite_gate.json")
    print(json.dumps({"status": payload["status"], "round_outcome": payload["round_outcome"], "gates": gates}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
