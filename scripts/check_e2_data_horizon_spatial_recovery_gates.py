#!/usr/bin/env python3
"""E2DR-G1..G10 gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    inv = pd.read_csv(ROOT / "outputs/data_recovery/E2_DATA_ASSET_INVENTORY.csv")
    arch = pd.read_csv(ROOT / "outputs/data_recovery/E2_ARCHIVE_CONTENT_INVENTORY.csv")
    prov = j("outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json")
    horizon = j("outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json")
    spatial = j("outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json")
    joint = j("outputs/data_recovery/E2_FULL_SENSORSCOPE_FEASIBILITY_GATE.json")
    ranking = j("outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json")
    decision = j("outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json")
    nonleak = j("outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json")
    stop = j("outputs/data_recovery/E2_STOP_STATUS.json")

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

    g1 = len(inv) > 0 and len(arch) > 0 and "duplicate_group_id" in inv.columns
    g2 = prov.get("status") in {
        "FULL_RAW_SOURCE_CONFIRMED", "TEST_SLICE_CONFIRMED", "DEBUG_SUBSET_CONFIRMED",
        "PREPROCESSING_TRUNCATION_CONFIRMED", "SOURCE_PROVENANCE_INCOMPLETE",
    }
    g3 = "status" in horizon and ("common_overlap_span_hours" in horizon or horizon["status"].endswith("MISSING"))
    g4 = spatial.get("status") in {"PASS", "SPATIAL_METADATA_NOT_RECOVERED"} and int(spatial.get("synthetic_usage_count", 1)) == 0
    g5 = "status" in joint and "conditions" in joint
    g6 = Path(ROOT / "outputs/data_recovery/E2_REPLACEMENT_DATASET_FEASIBILITY_MATRIX.csv").is_file() and "ranking" in ranking
    g7 = decision.get("status") in {
        "READY_WITH_FULL_SENSORSCOPE", "READY_WITH_REPLACEMENT_DATASET", "BLOCKED_DATA_RECOVERY_REQUIRED",
    } and (ROOT / "outputs/data_recovery/E2_PROTOCOL_ROUTE_IMPACT_ASSESSMENT.md").is_file()
    g8 = nonleak.get("status") == "PASS" and int(nonleak.get("validation_seed_read_count", 1)) == 0
    g9 = (
        (ROOT / "tests/unit/test_e2_data_horizon_spatial_recovery_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_data_horizon_spatial_recovery_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed == 0
            and first in {"inventory", "prepare", "recursive_search", "asset_inventory"}
        ))
    )
    g10 = (
        int(stop.get("experimental_trace_count", -1)) == 0
        and stop.get("profile_selection") == "NOT_STARTED"
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and int(stop.get("validation_seed_read_count", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
    )
    gates = {f"E2DR-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
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
        "ledger_first_label": first,
        "selected_route": decision.get("selected_route"),
        "replacement_dataset": ranking.get("selected_dataset"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    dump_json(payload, ROOT / "outputs/gates/e2_data_horizon_spatial_recovery_gate.json")
    print(json.dumps({"status": payload["status"], "round_outcome": payload["round_outcome"], "gates": gates}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
