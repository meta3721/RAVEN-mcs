#!/usr/bin/env python3
"""Compact evidence gate for PROFILE-S1 final freeze."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]
LABELS = ["S1", "S2", "S3", "S4", "S5", "S6"]

REQUIRED = [
    "outputs/audits/E2_TRAFFIC_PROFILE_S1_INPUT_IDENTITY_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json",
    "outputs/audits/E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json",
    "outputs/audits/E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json",
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_s1_candidate_registry.json",
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_direction_certificate.json",
    "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_runner_identity.json",
    "outputs/e2_traffic_profile_s1/E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json",
    "outputs/e2_traffic_profile_s1/expected_client_window_activity.parquet",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_REPORT.docx",
    f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt",
]
for label in LABELS:
    REQUIRED.append(f"outputs/e2_traffic_profile_s1/{label}_exact_expected_arrival_mass.parquet")
for sid in SCENARIOS:
    REQUIRED.extend([
        f"outputs/e2_traffic_profile_s1/scenarios/{sid}/traces/28201/hard_arrival_events.parquet",
        f"outputs/e2_traffic_profile_s1/scenarios/{sid}/traces/28202/runtime_parameter_snapshot.json",
        f"outputs/e2_traffic_profile_s1/scenarios/{sid}/traces/28203/hard_arrival_events.parquet",
    ])


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    stop = {}
    sp = ROOT / "outputs/e2_traffic_profile_s1/E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_STOP_STATUS.json"
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
