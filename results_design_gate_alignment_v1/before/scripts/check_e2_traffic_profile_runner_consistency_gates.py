#!/usr/bin/env python3
"""E2RC-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_HOTFIX_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]
SEEDS = (28201, 28202, 28203)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    identity = j("outputs/audits/E2_TRAFFIC_RUNNER_CONSISTENCY_INPUT_IDENTITY.json")
    param = j("outputs/audits/E2_TRAFFIC_PROFILE_PARAMETER_CONSISTENCY_AUDIT.json")
    exact = j("outputs/audits/E2_TRAFFIC_EXACT_EXPECTED_MASS_AUDIT.json")
    clip = j("outputs/audits/E2_TRAFFIC_PROFILE_CLIP_AND_SUPPORT_AUDIT.json")
    cert = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_runner_consistent_direction_certificate.json")
    registry = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.json")
    identity_f = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_identity.json")
    stop = j("outputs/e2_traffic_runner_consistency/E2_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_STOP_STATUS.json")
    tomb = j("outputs/audits/E2_TRAFFIC_OLD_TRACE_TOMBSTONE.json")

    ledger_entries = failed_cmd = forced_zero = missing_logs = 0
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
                failed_cmd += 1
            for key in ("stdout_log", "stderr_log"):
                rel = row.get(key)
                if rel and not (ROOT / rel).is_file():
                    missing_logs += 1
            cmd = " ".join(str(x) for x in row.get("command", []))
            if "sys.exit(0)" in cmd and row.get("label") == "gates":
                forced_zero += 1

    traces_ok = all(
        (ROOT / f"outputs/e2_traffic_runner_consistency/scenarios/{sid}/traces/{seed}/hard_arrival_events.parquet").is_file()
        and (ROOT / f"outputs/e2_traffic_runner_consistency/scenarios/{sid}/traces/{seed}/runtime_parameter_snapshot.json").is_file()
        for sid in SCENARIOS for seed in SEEDS
    )
    bounds_ok = (
        registry.get("probability_bounds") == {"opp": [0.05, 0.95], "obs": [0.05, 0.95], "q": [0.05, 0.95]}
        and param.get("probability_bounds") == registry.get("probability_bounds")
    )

    g1 = identity.get("status") == "PASS"
    g2 = param.get("status") == "PASS" and int(param.get("per_seed_intercept_solve_count", 1)) == 0
    g3 = exact.get("status") == "PASS" and int(exact.get("exact_enumeration_window_count", 0)) == 4300
    g4 = bounds_ok and int(param.get("bounds_mismatch_count", 1)) == 0
    g5 = clip.get("status") == "PASS" and int(clip.get("profile_strength_search_count", 1)) == 0
    g6 = traces_ok and int(stop.get("hard_trace_count", 0)) == 18 and bool(
        tomb.get("invalid_due_to_seed_specific_intercept_recalibration")
    )
    g7 = int(cert.get("pass_count", 0)) == 6 and int(cert.get("hardcoded_pass_count", 1)) == 0
    g8 = identity_f.get("status") == "FROZEN" and registry.get("status") == "FROZEN" and cert.get("status") == "PASS"
    g9 = (
        (ROOT / "tests/unit/test_e2_traffic_profile_runner_consistency_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_traffic_profile_runner_consistency_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed_cmd == 0 and missing_logs == 0 and forced_zero == 0
            and first == "hotfix_generation"
        ))
    )
    g10 = (
        int(stop.get("training_artifact_count", -1)) == 0
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and int(stop.get("validation_seed_read_count", -1)) == 0
        and int(stop.get("formal_seed_read_count", -1)) == 0
        and int(stop.get("e2_formal_runs", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
    )
    gates = {f"E2RC-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    core_ok = all(gates[f"E2RC-G{i}"] == "PASS" for i in range(1, 9))
    packaging_ok = gates["E2RC-G9"] == "PASS" and gates["E2RC-G10"] == "PASS"
    stop_ok = stop.get("status") in {
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY",
        "BLOCKED_TRAFFIC_PROFILE_RUNNER_CONSISTENCY_FAILED",
    }
    ok = packaging_ok and stop_ok and gates["E2RC-G1"] == "PASS"
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "core_gates_pass": core_ok,
        "gates": gates,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed_cmd,
        "missing_log_count": missing_logs,
        "forced_zero_wrapper_count": forced_zero,
        "ledger_first_label": first,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
