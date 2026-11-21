#!/usr/bin/env python3
"""Compact evidence presence gate for traffic mapping readiness."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_MAPPING_AND_READINESS_CLOSURE_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"

REQUIRED = [
    "outputs/audits/E2_TRAFFIC_PROVISIONAL_SELECTION_TOMBSTONE.json",
    "outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json",
    "outputs/traffic_mapping/E2_TRAFFIC_DENSE_MATRIX_AUDIT.json",
    "outputs/traffic_mapping/E2_TRAFFIC_STATION_TIME_COVERAGE.csv",
    "configs/frozen/e2_traffic/global_windows_100.parquet",
    "configs/frozen/e2_traffic/global_windows_identity.json",
    "configs/frozen/e2_traffic/atomic_window_assignment.parquet",
    "outputs/audits/E2_TRAFFIC_GLOBAL_WINDOW_AUDIT.json",
    "outputs/traffic_mapping/E2_TRAFFIC_REFERENCE_PARSE_AUDIT.json",
    "configs/frozen/e2_traffic/station_spatial_identity.parquet",
    "configs/frozen/e2_traffic/station_spatial_identity.json",
    "outputs/audits/E2_TRAFFIC_SPATIAL_METADATA_AUDIT.json",
    "outputs/traffic_mapping/E2_TRAFFIC_TARGET_FIELD_AUDIT.csv",
    "configs/frozen/e2_traffic/target_field_identity.json",
    "configs/frozen/e2_traffic/traffic_theory_mapping.yaml",
    "configs/frozen/e2_traffic/traffic_theory_mapping_identity.json",
    "configs/frozen/e2_traffic/atomic_target_table.parquet",
    "configs/frozen/e2_traffic/client_stratum_target.parquet",
    "outputs/audits/E2_TRAFFIC_TWO_STAGE_MAPPING_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_THEORY_COMPATIBILITY_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_THEORY_COMPATIBILITY.md",
    "outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_MANIFEST.json",
    "outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_COUNTS.csv",
    "outputs/e2_traffic_canary/E2_TRAFFIC_MAPPING_CANARY_GATE.json",
    "outputs/traffic_mapping/E2_TRAFFIC_STOP_STATUS.json",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt",
]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    stop = {}
    stop_path = ROOT / "outputs/traffic_mapping/E2_TRAFFIC_STOP_STATUS.json"
    if stop_path.is_file():
        stop = json.loads(stop_path.read_text(encoding="utf-8"))
    payload = {
        "package": PACKAGE,
        "status": "PASS" if not missing else "FAIL",
        "missing_required_paths": missing,
        "round_outcome": stop.get("status"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
