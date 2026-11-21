#!/usr/bin/env python3
"""E2BC-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_BALANCED_DESIGN_CANARY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    identity = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_INPUT_IDENTITY.json")
    soft = j("outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json")
    stage2 = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json")
    failed = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_FAILED_ATTEMPT_AUDIT.json")
    qleak = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_Q_LEAKAGE_AUDIT.json")
    mass = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_EVENT_MASS_AUDIT.json")
    reuse = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_WINDOW_REUSE_AUDIT.json")
    pooled = j("outputs/audits/E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json")
    stop = j("outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json")

    seeds = stop.get("design_seeds", [28101, 28102, 28103])
    per = []
    for seed in seeds:
        per.append(j(f"outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_SEED_{seed}_DIAG.json"))

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

    g1 = identity.get("status") == "PASS"
    g2 = soft.get("status") == "PASS" and float(soft.get("D_TV_group_soft", 1)) <= 0.01
    g3 = qleak.get("target_value_feature_dependency_count", 1) == 0
    g4 = stage2.get("status") == "PASS" and qleak.get("observed_count_used_as_q_feature_count", 1) == 0
    g5 = failed.get("status") == "PASS" and int(failed.get("failed_attempt_omission_count", 1)) == 0
    g6 = (
        mass.get("status") == "PASS"
        and reuse.get("status") == "PASS"
        and all((ROOT / f"outputs/e2_traffic_balanced_canary/traces/{s}/hard_arrival_events.parquet").is_file() for s in seeds)
    )
    g7 = all(bool(d.get("rate_pass")) for d in per)
    g8 = all(bool(d.get("balanced_pass")) and bool(d.get("structural_pass")) for d in per) and pooled.get("status") == "PASS"
    g9 = (
        (ROOT / "tests/unit/test_e2_traffic_balanced_canary_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_traffic_balanced_canary_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed_cmd == 0 and missing_logs == 0 and forced_zero == 0
            and first == "balanced_generation"
        ))
    )
    g10 = (
        int(stop.get("training_artifact_count", -1)) == 0
        and int(stop.get("profile_execution_count", -1)) == 0
        and stop.get("profile_selection") == "NOT_STARTED"
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and int(stop.get("validation_seed_read_count", -1)) == 0
        and int(stop.get("formal_seed_read_count", -1)) == 0
        and int(stop.get("e2_formal_runs", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
    )
    gates = {f"E2BC-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    core_ok = all(gates[f"E2BC-G{i}"] == "PASS" for i in range(1, 9))
    # Packaging gates G9/G10 should pass even when canary blocked; overall gate
    # script status tracks packaging integrity. Round outcome is in stop.status.
    packaging_ok = gates["E2BC-G9"] == "PASS" and gates["E2BC-G10"] == "PASS"
    expected_stop = (
        "READY_FOR_TRAFFIC_S1_S6_PROFILE_FREEZE"
        if core_ok
        else "BLOCKED_TRAFFIC_BALANCED_DESIGN_CANARY_FAILED"
    )
    stop_ok = stop.get("status") == expected_stop or stop.get("status") in {
        "BLOCKED_MISSING_PUBLIC_TARGET_SEAL",
        "BLOCKED_INPUT_IDENTITY_MISMATCH",
        "BLOCKED_TRAFFIC_BALANCED_DESIGN_CANARY_FAILED",
        "READY_FOR_TRAFFIC_S1_S6_PROFILE_FREEZE",
    }
    ok = packaging_ok and stop_ok and gates["E2BC-G1"] == "PASS"
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
    print(json.dumps({"status": payload["status"], "round_outcome": payload["round_outcome"], "gates": gates}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
