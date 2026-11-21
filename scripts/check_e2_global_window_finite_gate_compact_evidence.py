#!/usr/bin/env python3
"""Compact evidence gate for E2 global-window finite-sample repair."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"


def main() -> int:
    required = [
        "outputs/audits/E2_PRIOR_LOCAL_WINDOW_AND_GATE_TOMBSTONE.json",
        "outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json",
        "outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json",
        "outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json",
        "outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json",
        "outputs/audits/E2_FINITE_SAMPLE_GATE_JUSTIFICATION.json",
        "outputs/e2_global_window/E2_STOP_STATUS.json",
        "configs/frozen/e2_global_windows/global_server_windows_identity.json",
        "configs/frozen/e2_finite_sample_gate/validation_gate_protocol.json",
        "configs/frozen/e2_finite_sample_gate/validation_prediction_intervals.json",
        "configs/frozen/e2_finite_sample_gate/validation_gate_identity.json",
        "src/raven_mcs/e2/global_window/windows.py",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    stop = json.loads((ROOT / "outputs/e2_global_window/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    iso = json.loads((ROOT / "outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json").read_text(encoding="utf-8"))
    val_traces = 0
    for seed in (29101, 29102, 29103, 29104, 29105):
        if (ROOT / "outputs/e2_global_window/traces" / str(seed)).exists():
            val_traces += 1
    ok = (
        not missing
        and int(iso.get("validation_read_count", 1)) == 0
        and val_traces == 0
        and stop.get("profile_selection") == "NOT_STARTED"
    )
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "missing_required_paths": missing,
        "validation_trace_count": val_traces,
        "round_outcome": stop.get("status"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
