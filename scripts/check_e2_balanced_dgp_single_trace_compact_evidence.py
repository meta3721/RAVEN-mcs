#!/usr/bin/env python3
"""Compact evidence replay gate for E2 balanced DGP repair."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"
SEEDS = (29101, 29102, 29103, 29104, 29105)


def main() -> int:
    required = [
        "outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json",
        "outputs/audits/E2_EVENT_MASS_SEMANTICS_AUDIT.json",
        "outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json",
        "outputs/audits/E2_PRIOR_ANTITHETIC_CERTIFICATION_TOMBSTONE.json",
        "outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json",
        "outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json",
        "outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json",
        "outputs/e2_balanced_dgp/E2_STOP_STATUS.json",
        "src/raven_mcs/e2/balanced_dgp/bounded_schedule.py",
        "src/raven_mcs/e2/balanced_dgp/opp_calibrate.py",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    stop = json.loads((ROOT / "outputs/e2_balanced_dgp/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    sel = json.loads((ROOT / "outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json").read_text(encoding="utf-8"))
    soft = json.loads(
        (ROOT / "outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json").read_text(encoding="utf-8")
    )
    src = (ROOT / "src/raven_mcs/e2/balanced_dgp/bounded_schedule.py").read_text(encoding="utf-8")

    # If traces exist, verify A×O×U chain files.
    trace_ok = True
    present_traces = 0
    for seed in SEEDS:
        d = ROOT / "outputs/e2_balanced_dgp/traces" / str(seed) / "balanced"
        if not d.is_dir():
            continue
        present_traces += 1
        for name in (
            "opportunity_events.parquet", "observation_events.parquet",
            "usable_events.parquet", "hard_arrival_events.parquet",
        ):
            if not (d / name).is_file():
                trace_ok = False

    blocked_ok = sel.get("status") == "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE"
    success_ok = (
        stop.get("status") == "READY_FOR_PROFILE_REFREEZE"
        and present_traces == 5
        and trace_ok
    )
    status_ok = (
        soft.get("status") == "PASS"
        and "iloc[start:n]" not in src
        and not missing
        and (blocked_ok or success_ok)
    )
    payload = {
        "package": PACKAGE,
        "status": "PASS" if status_ok else "FAIL",
        "missing_required_paths": missing,
        "complete_event_trace_count": present_traces,
        "round_outcome": stop.get("status"),
        "soft_status": soft.get("status"),
        "cert_selection_status": sel.get("status"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if status_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
