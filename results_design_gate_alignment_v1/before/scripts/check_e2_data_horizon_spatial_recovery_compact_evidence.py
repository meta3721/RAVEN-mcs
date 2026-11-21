#!/usr/bin/env python3
"""Compact evidence gate for E2 data recovery."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"


def main() -> int:
    required = [
        "outputs/data_recovery/E2_DATA_ASSET_INVENTORY.csv",
        "outputs/data_recovery/E2_ARCHIVE_CONTENT_INVENTORY.csv",
        "outputs/data_recovery/E2_DATA_SEARCH_LOG.txt",
        "outputs/data_recovery/E2_CURRENT_SUBSET_PROVENANCE.json",
        "outputs/data_recovery/E2_SENSORSCOPE_GLOBAL_WINDOW_CAPACITY.json",
        "outputs/data_recovery/E2_SPATIAL_METADATA_RECOVERY_AUDIT.json",
        "outputs/data_recovery/E2_FULL_SENSORSCOPE_FEASIBILITY_GATE.json",
        "outputs/data_recovery/E2_REPLACEMENT_DATASET_FEASIBILITY_MATRIX.csv",
        "outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json",
        "outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json",
        "outputs/data_recovery/E2_PROTOCOL_ROUTE_IMPACT_ASSESSMENT.md",
        "outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json",
        "outputs/data_recovery/E2_STOP_STATUS.json",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    stop = json.loads((ROOT / "outputs/data_recovery/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    ok = not missing and int(stop.get("experimental_trace_count", 1)) == 0
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "missing_required_paths": missing,
        "round_outcome": stop.get("status"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
