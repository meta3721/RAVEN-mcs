#!/usr/bin/env python3
"""Compact evidence gate — only checks what light Evidence ZIP contains."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1"
COMPACT = (
    "manifest.json",
    "group_mass_diagnostics_300.json",
    "true_stratum_mass_diagnostics_300.json",
    "chronology_audit.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
)


def main() -> int:
    root = ROOT
    traces = root / "outputs/e2_true_stratum/traces"
    missing = []
    present = 0
    for manifest in traces.glob("*/*/*/manifest.json") if traces.is_dir() else []:
        present += 1
        d = manifest.parent
        for name in COMPACT:
            if not (d / name).is_file():
                missing.append(f"{d.relative_to(root)}/{name}")
    selection = json.loads(
        (root / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    full_gate = root / "outputs/gates/full_repository_gate.json"
    required_meta = [
        "outputs/e2_true_stratum/E2_PROFILE_GATE_BY_SEED.csv",
        "outputs/e2_true_stratum/E2_PROFILE_GATE_SUMMARY.csv",
        "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json",
        "outputs/e2_true_stratum/E2_WINDOW_SELECTION.json",
        "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json",
        "outputs/audits/E2_GROUP_STRATUM_INDEPENDENCE_AUDIT.json",
        "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json",
        "configs/frozen/e2_true_stratum/stratum_merge_protocol.yaml",
    ]
    meta_missing = [p for p in required_meta if not (root / p).is_file()]
    # Do NOT require 150 non-selected full event dirs.
    selected = selection.get("selected_profile_id")
    selected_full_ok = True
    if selected:
        for seed_dir in traces.glob("*"):
            for scen_dir in (seed_dir / selected).glob("*"):
                if scen_dir.is_dir() and not (scen_dir / "hard_arrival_events.parquet").is_file():
                    selected_full_ok = False
    status = (
        "PASS"
        if (
            present == 180
            and not missing
            and not meta_missing
            and selected_full_ok
        )
        else "FAIL"
    )
    payload = {
        "package": PACKAGE,
        "status": status,
        "manifest_count": present,
        "missing_compact_files": missing[:50],
        "missing_compact_file_count": len(missing),
        "meta_missing": meta_missing,
        "selected_profile_id": selected,
        "requires_nonselected_full_traces": False,
        "full_gate_present": full_gate.is_file(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    out = root / "outputs/gates/E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1_COMPACT_EVIDENCE_GATE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    dump_json(payload, root / "outputs/gates/compact_evidence_gate.json")
    print(json.dumps({"status": status, "manifest_count": present, "missing": len(missing)}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
