#!/usr/bin/env python3
"""Compact evidence gate for public-target q-seal."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PUBLIC_TARGET_AND_Q_FEATURE_SEAL_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"

REQUIRED = [
    "outputs/traffic_public_target/E2_TRAFFIC_PARENT_IDENTITY_FREEZE.json",
    "configs/frozen/e2_traffic_public_target/atomic_public_target.parquet",
    "configs/frozen/e2_traffic_public_target/atomic_public_target_identity.json",
    "configs/frozen/e2_traffic_public_target/target_group_mass.parquet",
    "outputs/audits/E2_TRAFFIC_GROUP_TARGET_AUDIT.json",
    "configs/frozen/e2_traffic_public_target/station_region_mapping.parquet",
    "configs/frozen/e2_traffic_public_target/station_region_identity.json",
    "outputs/audits/E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json",
    "configs/frozen/e2_traffic_public_target/opportunity_stratum_target.parquet",
    "configs/frozen/e2_traffic_public_target/client_stratum_target.parquet",
    "configs/frozen/e2_traffic_public_target/public_target_identity.json",
    "configs/frozen/e2_traffic_public_target/q_feature_manifest.json",
    "configs/frozen/e2_traffic_public_target/q_forbidden_feature_manifest.json",
    "outputs/audits/E2_TRAFFIC_Q_FEATURE_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json",
    "outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json",
    "outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.md",
    "outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_MANIFEST.json",
    "outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_COUNTS.csv",
    "outputs/e2_traffic_public_target_canary/E2_TRAFFIC_PUBLIC_TARGET_CANARY_GATE.json",
    "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt",
]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    stop = {}
    sp = ROOT / "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json"
    if sp.is_file():
        stop = json.loads(sp.read_text(encoding="utf-8"))
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
