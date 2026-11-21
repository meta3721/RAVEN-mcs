#!/usr/bin/env python3
"""E2PT-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PUBLIC_TARGET_AND_Q_FEATURE_SEAL_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    public = j("configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json")
    group = j("outputs/audits/E2_TRAFFIC_GROUP_TARGET_AUDIT.json")
    region = j("outputs/audits/E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json")
    stratum = j("configs/frozen/e2_traffic_public_target/public_target_identity.json")
    q = j("outputs/audits/E2_TRAFFIC_Q_FEATURE_AUDIT.json")
    leak = j("outputs/audits/E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json")
    theory = j("outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json")
    canary = j("outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json")
    stop = j("outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json")

    ledger_entries = failed = forced_zero = missing_logs = 0
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
            for key in ("stdout_log", "stderr_log"):
                rel = row.get(key)
                if rel and not (ROOT / rel).is_file():
                    missing_logs += 1
            cmd = " ".join(str(x) for x in row.get("command", []))
            if "sys.exit(0)" in cmd and row.get("label") == "gates":
                forced_zero += 1

    g1 = (
        public.get("status") == "PASS"
        and abs(float(public.get("varpi_sum", 0)) - 1.0) <= 1e-12
        and int(public.get("target_value_dependency_count", 1)) == 0
    )
    g2 = group.get("status") == "PASS" and abs(float(group.get("mass_sum", 0)) - 1.0) <= 1e-12
    g3 = (
        region.get("status") == "PASS"
        and int(region.get("region_count", 0)) == 4
        and int(region.get("target_value_dependency_count", 1)) == 0
        and region.get("weighting") == "station_equal_weight"
    )
    g4 = (
        stratum.get("status") == "PASS"
        and abs(float(stratum.get("Lambda_sum", 0)) - 1.0) <= 1e-12
        and abs(float(stratum.get("pi_sum", 0)) - 1.0) <= 1e-12
        and int(stratum.get("stratum_count", 99)) <= 32
    )
    g5 = (
        q.get("status") == "PASS"
        and int(q.get("observed_count_dependency_count", 1)) == 0
        and "observed_count" not in q.get("actual_feature_list", ["observed_count"])
    )
    g6 = leak.get("status") == "PASS" and int(leak.get("observed_count_dependency_in_q_features", 1)) == 0
    g7 = theory.get("status") == "PASS" and int(theory.get("core_formula_modification_count", 1)) == 0
    g8 = canary.get("status") == "PASS" and canary.get("seed") == 27901
    g9 = (
        (ROOT / "tests/unit/test_e2_traffic_public_target_qseal_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_traffic_public_target_qseal_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed == 0 and missing_logs == 0 and forced_zero == 0
            and first == "public_target_generation"
        ))
    )
    g10 = (
        int(stop.get("hard_trace_count", -1)) == 0
        and int(stop.get("training_artifact_count", -1)) == 0
        and stop.get("profile_selection") == "NOT_STARTED"
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and int(stop.get("validation_seed_read_count", -1)) == 0
        and int(stop.get("formal_seed_read_count", -1)) == 0
        and int(stop.get("e2_formal_runs", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
        and stop.get("status") in {
            "READY_FOR_TRAFFIC_BALANCED_DESIGN_CANARY",
            "BLOCKED_TRAFFIC_PUBLIC_TARGET_SEAL_FAILED",
        }
    )
    gates = {f"E2PT-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    ok = all(v == "PASS" for v in gates.values())
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "gates": gates,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed,
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
