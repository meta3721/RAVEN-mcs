#!/usr/bin/env python3
"""Compact evidence gate for traffic balanced canary."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_BALANCED_DESIGN_CANARY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"

REQUIRED = [
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_INPUT_IDENTITY.json",
    "outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_OPPORTUNITY_CALIBRATION.json",
    "outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_OPPORTUNITY_PROBABILITIES.parquet",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_STAGE2_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_FAILED_ATTEMPT_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_Q_LEAKAGE_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_EVENT_MASS_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_WINDOW_REUSE_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_BALANCED_CANARY_POOLED_DISTRIBUTION_AUDIT.json",
    "outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json",
    "outputs/e2_traffic_balanced_canary/traces/28101/hard_arrival_events.parquet",
    "outputs/e2_traffic_balanced_canary/traces/28102/hard_arrival_events.parquet",
    "outputs/e2_traffic_balanced_canary/traces/28103/hard_arrival_events.parquet",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt",
]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    stop = {}
    sp = ROOT / "outputs/e2_traffic_balanced_canary/E2_TRAFFIC_BALANCED_CANARY_STOP_STATUS.json"
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
