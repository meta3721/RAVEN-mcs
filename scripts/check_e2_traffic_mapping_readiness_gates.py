#!/usr/bin/env python3
"""E2TR-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_MAPPING_AND_READINESS_CLOSURE_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    dense = j("outputs/traffic_mapping/E2_TRAFFIC_DENSE_MATRIX_AUDIT.json")
    window = j("outputs/audits/E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json")
    spatial = j("outputs/audits/E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json")
    theory = j("configs/frozen/e2_traffic/traffic_theory_mapping_identity.json")
    two = j("outputs/audits/E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json")
    compat = j("outputs/audits/E2_TRAFFIC_THEORY_COMPATIBILITY_AUDIT.json")
    canary = j("outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_GATE.json")
    stop = j("outputs/traffic_mapping/E2_TRAFFIC_STOP_STATUS.json")
    nonleak = j("outputs/audits/E2_TRAFFIC_MAPPING_NONLEAKAGE_AUDIT.json")

    ledger_entries = failed = forced_zero = 0
    first = None
    missing_logs = 0
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
            if "sys.exit(0)" in cmd and "gate" in row.get("label", ""):
                forced_zero += 1

    g1 = dense.get("status") == "PASS" and dense.get("station_count") == 43 and dense.get("unique_timestamp_count") == 720
    g2 = window.get("status") == "PASS" and window.get("global_window_count") == 100
    g3 = int(window.get("cross_window_duplicate_count", 1)) == 0 and int(window.get("selected_atomic_count", 0)) == 25800
    g4 = spatial.get("status") == "PASS" and int(spatial.get("exact_id_match_count", 0)) == 43 and int(spatial.get("missing_coordinate_count", 1)) == 0
    g5 = (
        (ROOT / "configs/frozen/e2_traffic/traffic_theory_mapping.yaml").is_file()
        and theory.get("status") == "PASS"
        and abs(float(theory.get("pi_mass_sum", 0)) - 1.0) < 1e-9
    )
    g6 = two.get("status") == "PASS" and int(two.get("outcome_leakage_count", 1)) == 0
    g7 = compat.get("status") == "PASS" and int(compat.get("theory_modification_count", 1)) == 0
    g8 = canary.get("status") == "PASS" and canary.get("seed") == 27901
    g9 = (
        (ROOT / "tests/unit/test_e2_traffic_mapping_readiness_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_traffic_mapping_readiness_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed == 0 and missing_logs == 0 and forced_zero == 0
            and first == "atomic_table_audit"
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
        and nonleak.get("status") == "PASS"
        and stop.get("status") in {
            "READY_FOR_TRAFFIC_BALANCED_DESIGN_CANARY",
            "BLOCKED_TRAFFIC_MAPPING_NOT_READY",
        }
    )
    gates = {f"E2TR-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    # G1-G8 determine readiness; G9/G10 packaging
    core_ok = all(gates[f"E2TR-G{i}"] == "PASS" for i in range(1, 9))
    ok = all(v == "PASS" for v in gates.values())
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "core_gates_pass": core_ok,
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
