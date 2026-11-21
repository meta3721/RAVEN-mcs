#!/usr/bin/env python3
"""Compact evidence gate for E2 hard-variance certification freeze."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
SEEDS = (29101, 29102, 29103, 29104, 29105)
TRACE_FILES = (
    "manifest.json",
    "group_mass_diagnostics_100.json",
    "certification_mass_diagnostics_100.json",
    "chronology_audit.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
    "stdout.log",
)
META_FILES = (
    "outputs/audits/E2_CANDIDATE_TRUNCATION_AUDIT.json",
    "outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json",
    "outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json",
    "outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json",
    "outputs/e2_hard_variance/E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json",
    "outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json",
    "outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json",
    "outputs/e2_hard_variance/E2_STOP_STATUS.json",
    "configs/frozen/e2_certification/certification_identity.json",
    "configs/frozen/e2_certification/atomic_certification_mapping.parquet",
    f"outputs/gates/{PACKAGE}_GATES.json",
)


def main() -> int:
    missing = []
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_hard_variance/traces" / str(seed) / "balanced"
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
            (ROOT / "outputs/e2_hard_variance/traces" / str(seed) / "balanced/manifest.json").is_file()
            for seed in SEEDS
        ),
        "expected_balanced_manifest_count": 5,
        "missing_compact_files": missing,
        "missing_meta_files": meta_missing,
        "gate_status": gate_status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    out = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
