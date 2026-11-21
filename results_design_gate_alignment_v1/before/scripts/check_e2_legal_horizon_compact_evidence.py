#!/usr/bin/env python3
"""Validate the compact evidence required for E2 legal-horizon Balanced stop."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
SEEDS = (29101, 29102, 29103, 29104, 29105)
TRACE_FILES = (
    "manifest.json", "resolved_config.yaml", "group_mass_diagnostics_100.json",
    "true_stratum_mass_diagnostics_100.json", "chronology_audit.json",
    "failed_attempt_audit.json", "q_feature_audit.json", "stdout.log",
)
META_FILES = (
    "outputs/audits/E2_ILLEGAL_300_AND_UNCALIBRATED_BALANCED_TOMBSTONE.json",
    "outputs/audits/E2_LEGAL_HORIZON_AUDIT.json",
    "outputs/audits/E2_100_WINDOW_SOURCE_UNIQUENESS_AUDIT.json",
    "outputs/e2_balanced_calibration/E2_BALANCED_SOFT_CALIBRATION_AUDIT.json",
    "outputs/e2_balanced_calibration/E2_BALANCED_PRE_GATE_SUMMARY.json",
    "outputs/e2_balanced_calibration/E2_STOP_STATUS.json",
    "outputs/e2_balanced_calibration/E2_PROFILE_SELECTION.json",
    "outputs/e2_balanced_calibration/E2_WINDOW_SELECTION.json",
    "configs/frozen/e2_legal_horizon/merged_true_stratum_100_identity.json",
    "configs/frozen/e2_legal_horizon/selected_legal_horizon_identity.json",
    f"outputs/gates/{PACKAGE}_GATES.json",
)


def main() -> int:
    missing = []
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced"
        for name in TRACE_FILES:
            if not (trace / name).is_file():
                missing.append(str((trace / name).relative_to(ROOT)))
    meta_missing = [path for path in META_FILES if not (ROOT / path).is_file()]
    gate_path = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
    gate_status = None
    if gate_path.is_file():
        gate_status = json.loads(gate_path.read_text(encoding="utf-8")).get("status")
    payload = {
        "package": PACKAGE,
        "status": "PASS" if not missing and not meta_missing and gate_status == "PASS" else "FAIL",
        "balanced_manifest_count": sum(
            (ROOT / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced/manifest.json").is_file()
            for seed in SEEDS
        ),
        "expected_balanced_manifest_count": 5,
        "missing_compact_files": missing,
        "missing_meta_files": meta_missing,
        "full_matrix_required": False,
        "matrix_status": "BLOCKED",
        "gate_status": gate_status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    out = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    dump_json(payload, ROOT / "outputs/gates/e2_legal_horizon_compact_evidence_gate.json")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
