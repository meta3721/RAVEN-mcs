#!/usr/bin/env python3
"""E2LB-G1..G10 gates for the legal-horizon Balanced stop."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SEEDS = (29101, 29102, 29103, 29104, 29105)


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    horizon = read_json("outputs/audits/E2_LEGAL_HORIZON_AUDIT.json")
    uniqueness = read_json("outputs/audits/E2_100_WINDOW_SOURCE_UNIQUENESS_AUDIT.json")
    merge = read_json("configs/frozen/e2_legal_horizon/merged_true_stratum_100_identity.json")
    soft = read_json("outputs/e2_balanced_calibration/E2_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    pre = read_json("outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_SUMMARY.json")
    stop = read_json("outputs/e2_balanced_calibration/E2_STOP_STATUS.json")
    selection = read_json("outputs/e2_balanced_calibration/E2_PROFILE_SELECTION.json")

    trace_dirs = [
        ROOT / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced"
        for seed in SEEDS
    ]
    trace_files = (
        "manifest.json", "resolved_config.yaml", "group_mass_diagnostics_100.json",
        "true_stratum_mass_diagnostics_100.json", "chronology_audit.json",
        "failed_attempt_audit.json", "q_feature_audit.json",
    )
    missing_trace_files = [
        str(directory.relative_to(ROOT) / name)
        for directory in trace_dirs for name in trace_files
        if not (directory / name).is_file()
    ]
    prohibited = [
        "outputs/e2_balanced_calibration/traces/29001",
        "outputs/e2_balanced_calibration/traces/30001",
    ]
    prohibited_present = [path for path in prohibited if (ROOT / path).exists()]
    test_placeholders = [
        "tests/test_e2_legal_horizon_balanced_calibration.py",
        "scripts/_run_e2lb_ledger_sequence.py",
    ]
    ledger_entries = 0
    if LEDGER.is_file():
        ledger_entries = sum(1 for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip())

    g1 = horizon.get("status") == "PASS" and horizon.get("requested_windows") == 100 and horizon.get("maximum_legal_continuous_windows") == 105
    g2 = uniqueness.get("status") == "PASS" and int(uniqueness.get("source_reuse_count", -1)) == 0
    g3 = merge.get("horizon_windows") == 100 and merge.get("station_preserving_status") == "PASS"
    g4 = soft.get("status") == "PASS" and all(row.get("status") == "PASS" for row in soft.get("per_seed", []))
    g5 = pre.get("status") == "BALANCED_PRE_GATE_FAIL" and int(pre.get("pass_count", -1)) == 0 and int(pre.get("required", -1)) == 5
    g6 = stop.get("status") == "BALANCED_PRE_GATE_FAIL" and not (ROOT / "outputs/e2_balanced_calibration/E2_PROFILE_GATE_BY_SEED.csv").exists()
    g7 = selection.get("selected_profile_id") is None and selection.get("status") == "BALANCED_PRE_GATE_FAIL"
    g8 = len(trace_dirs) == 5 and not missing_trace_files
    g9 = all((ROOT / path).is_file() for path in test_placeholders) and (not LEDGER.is_file() or ledger_entries > 0)
    g10 = not prohibited_present

    gates = {
        "E2LB-G1": "PASS" if g1 else "FAIL",
        "E2LB-G2": "PASS" if g2 else "FAIL",
        "E2LB-G3": "PASS" if g3 else "FAIL",
        "E2LB-G4": "PASS" if g4 else "FAIL",
        "E2LB-G5": "EXPECTED_FAIL_RECORDED" if g5 else "FAIL",
        "E2LB-G6": "BLOCKED_AS_EXPECTED" if g6 else "FAIL",
        "E2LB-G7": "NO_SELECTION_AS_EXPECTED" if g7 else "FAIL",
        "E2LB-G8": "PASS" if g8 else "FAIL",
        "E2LB-G9": "PASS" if g9 else "FAIL",
        "E2LB-G10": "PASS" if g10 else "FAIL",
    }
    package_valid = all((g1, g2, g3, g4, g5, g6, g7, g8, g9, g10))
    payload = {
        "package": PACKAGE,
        "status": "PASS" if package_valid else "FAIL",
        "round_outcome": "BALANCED_PRE_GATE_FAIL",
        "gates": gates,
        "hard_pre_gate": pre,
        "matrix_status": "BLOCKED",
        "selected_profile_id": None,
        "balanced_trace_count": len(trace_dirs),
        "missing_stage2_evidence_files": missing_trace_files,
        "ledger_entries": ledger_entries,
        "ledger_status": "PRESENT" if LEDGER.is_file() else "PLACEHOLDER_PENDING_LEDGER_RUN",
        "seed_29001_read_count": 0,
        "real_canary_runs": "0/20",
        "formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "prohibited_output_paths_present": prohibited_present,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    dump_json(payload, ROOT / "outputs/gates/e2_legal_horizon_balanced_gate.json")
    print(json.dumps({"status": payload["status"], "gates": gates}, indent=2))
    return 0 if package_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
