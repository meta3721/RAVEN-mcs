#!/usr/bin/env python3
"""E2-GLOBAL-WINDOW-AND-FINITE-SAMPLE-GATE-REPAIR-R1 prepare (protocol freeze)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.shared import Pt

from raven_mcs.e2.global_window.isolation import write_design_registry_and_isolation
from raven_mcs.e2.global_window.justification import write_gate_justification
from raven_mcs.e2.global_window.spatial import load_true_spatial_identity
from raven_mcs.e2.global_window.tombstone import write_prior_tombstone
from raven_mcs.e2.global_window.unique_assign import write_blocked_unique_assignment
from raven_mcs.e2.global_window.windows import (
    DESIGN_SEEDS,
    VALIDATION_SEEDS,
    build_global_server_windows,
)
from raven_mcs.e2.legal_horizon.schedule100 import freeze_legal_horizon
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _write_report(root: Path, front: list[tuple], sections: list[tuple]) -> Path:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading(PACKAGE, level=0)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    for k, v in front:
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(body))
    out = root / f"deliverables/TO_SUBMIT_{PACKAGE}"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{PACKAGE}_REPORT.docx"
    doc.save(path)
    return path


def main() -> int:
    root = ROOT
    for d in (
        "outputs/e2_global_window",
        "outputs/audits",
        "outputs/gates",
        "configs/frozen/e2_global_windows",
        "configs/frozen/e2_spatial_identity",
        "configs/frozen/e2_finite_sample_gate",
        "logs",
        f"deliverables/TO_SUBMIT_{PACKAGE}",
    ):
        (root / d).mkdir(parents=True, exist_ok=True)

    write_prior_tombstone(root)
    freeze_legal_horizon(root)

    windows = build_global_server_windows(root)
    capacity = windows["capacity"]
    unique = write_blocked_unique_assignment(
        frame=windows["frame"],
        capacity=capacity,
        root=root,
        reason=windows["status"],
    )
    spatial = load_true_spatial_identity(root)
    isolation = write_design_registry_and_isolation(root)

    # Do not run design replicates / validation when capacity or spatial blocked.
    stop_status = windows["status"]
    if stop_status == "PASS" and spatial["status"] != "PASS":
        stop_status = spatial["status"]
    if stop_status == "PASS" and unique["status"] != "PASS":
        stop_status = unique["status"]

    justification = write_gate_justification(
        stop_status=stop_status, capacity=capacity, root=root,
    )

    # Gate protocol skeleton — values marked NOT_ESTIMATED when blocked.
    gate_dir = root / "configs/frozen/e2_finite_sample_gate"
    protocol = {
        "name": "e2_finite_sample_validation_gate_v1",
        "status": "PREREGISTERED_STRUCTURE_ONLY" if stop_status != "PASS" else "PREREGISTERED",
        "design_seeds": list(DESIGN_SEEDS),
        "validation_seeds": list(VALIDATION_SEEDS),
        "validation_execution": "NOT_RUN_THIS_ROUND",
        "aggregate_thresholds": {
            "D_TV_mean_group_mass": 0.02,
            "D_TV_mean_cert_mass": 0.03,
            "abs_mean_head_ratio_minus_1": 0.03,
            "abs_mean_tail_ratio_minus_1": 0.03,
        },
        "outside_interval_allowance": 2,
        "core_metrics": ["D_TV_group", "D_TV_cert", "head_mass_ratio", "tail_mass_ratio"],
        "system_bias_thresholds_design": {
            "D_TV_mean_empirical_vs_target": 0.02,
            "max_abs_mean_group_deviation": 0.015,
            "abs_mean_head_ratio_minus_1": 0.02,
            "abs_mean_tail_ratio_minus_1": 0.02,
        },
        "old_five_of_five_fixed_threshold_rule": "TOMBSTONED",
        "runtime_commit": _git_head(),
        "freeze_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(protocol, gate_dir / "validation_gate_protocol.json")
    (gate_dir / "validation_gate_protocol.yaml").write_text(
        "\n".join([
            f"name: {protocol['name']}",
            f"status: {protocol['status']}",
            "validation_execution: NOT_RUN_THIS_ROUND",
            "old_five_of_five_fixed_threshold_rule: TOMBSTONED",
            f"outside_interval_allowance: {protocol['outside_interval_allowance']}",
            f"runtime_commit: {_git_head()}",
            "",
        ]),
        encoding="utf-8",
    )
    intervals = {
        "status": "NOT_ESTIMATED",
        "reason": stop_status,
        "design_replicate_target": 1000,
        "design_replicate_completed": 0,
        "intervals": {},
    }
    dump_json(intervals, gate_dir / "validation_prediction_intervals.json")
    identity = {
        "status": stop_status,
        "design_seed_registry_hash": isolation["design"]["registry_hash"],
        "global_window_identity_hash": windows["identity"].get("identity_hash"),
        "atomic_window_mapping_hash": unique.get("mapping_hash"),
        "spatial_identity_hash": spatial["audit"].get("groups_config_hash"),
        "certification_mapping_hash": None,
        "prediction_intervals_status": intervals["status"],
        "aggregate_thresholds": protocol["aggregate_thresholds"],
        "outside_interval_allowance": 2,
        "runtime_commit": _git_head(),
        "freeze_timestamp_utc": protocol["freeze_timestamp_utc"],
        "identity_hash": sha256_json({
            "stop": stop_status,
            "design": isolation["design"]["registry_hash"],
            "window": windows["identity"].get("identity_hash"),
            "unique": unique.get("mapping_hash"),
        }),
    }
    dump_json(identity, gate_dir / "validation_gate_identity.json")

    stop = {
        "status": stop_status,
        "global_window_status": windows["status"],
        "unique_assignment_status": unique["status"],
        "spatial_status": spatial["status"],
        "isolation_status": isolation["audit"]["status"],
        "design_seed_count": len(DESIGN_SEEDS),
        "validation_seed_read_count": isolation["audit"]["validation_read_count"],
        "single_arm_replicate_count": 0,
        "validation_traces": 0,
        "non_balanced_trace_count": 0,
        "profile_selection": "NOT_STARTED",
        "seed_29001_read_count": 0,
        "real_canary_runs": "0/20",
        "formal_seed_reads": 0,
        "e2_formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "capacity": capacity,
        "authorization_next_round": (
            "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION"
            if stop_status == "READY_FOR_BALANCED_CONFIRMATORY_VALIDATION"
            else "NOT_AUTHORIZED_UNTIL_PROTOCOL_PASS"
        ),
    }
    dump_json(stop, root / "outputs/e2_global_window/E2_STOP_STATUS.json")

    # Placeholder summaries for evidence completeness.
    dump_json({
        "n_replicates": 0,
        "target_replicates": 1000,
        "antithetic_used": False,
        "status": "NOT_RUN",
        "reason": stop_status,
    }, root / "outputs/e2_global_window/E2_GLOBAL_WINDOW_SINGLE_ARM_DESIGN_SUMMARY.json")
    dump_json({
        "status": "NOT_RUN",
        "reason": stop_status,
    }, root / "outputs/e2_global_window/E2_GLOBAL_WINDOW_VARIANCE_DECOMPOSITION_SUMMARY.json")
    (root / "outputs/e2_global_window/E2_GLOBAL_WINDOW_SINGLE_ARM_DESIGN_REPLICATES.csv").write_text(
        "design_seed,replicate,version,status\n", encoding="utf-8",
    )

    front = [
        ("global window count", 0 if windows["status"] != "PASS" else 100),
        ("common-boundary status", windows["audit"].get("common_boundary_status")),
        ("requested window hours", capacity.get("window_hours")),
        ("max legal global windows", capacity.get("max_legal_global_windows")),
        ("supported span hours", capacity.get("supported_span_hours")),
        ("atomic multiply-assigned count", unique.get("multiply_assigned_unit_count")),
        ("cross-window unit reuse count", unique.get("cross_window_duplicate_unit_count")),
        ("spatial identity source", spatial["audit"].get("coordinate_source")),
        ("synthetic spatial usage count", spatial["audit"].get("synthetic_usage_count")),
        ("design seed count", len(DESIGN_SEEDS)),
        ("validation read count", isolation["audit"]["validation_read_count"]),
        ("single-arm replicate count", 0),
        ("selected certification level", None),
        ("prediction intervals", intervals["status"]),
        ("aggregate validation thresholds", json.dumps(protocol["aggregate_thresholds"])),
        ("outside-interval allowance", 2),
        ("validation traces", 0),
        ("non-balanced traces", 0),
        ("Profile selection", "NOT_STARTED"),
        ("seed29001 reads", 0),
        ("E2 formal runs", 0),
        ("round stop status", stop_status),
    ]
    report = _write_report(root, front, [
        ("1. Executive Summary", json.dumps(stop, indent=2, default=str)),
        ("2. Prior Tombstone", "INVALID_PENDING_GLOBAL_WINDOW_AND_GATE_REPAIR"),
        ("3. Global Windows / Capacity", json.dumps(windows["audit"], indent=2, default=str)),
        ("4. Unique Assignment", json.dumps(unique, indent=2, default=str)),
        ("5. Spatial Identity", json.dumps(spatial["audit"], indent=2, default=str)),
        ("6. Design/Validation Isolation", json.dumps(isolation["audit"], indent=2, default=str)),
        ("7. Finite-Sample Gate Justification", json.dumps(justification, indent=2, default=str)),
        ("8. Stop Position", "validation=0; non-balanced=0; profile=NOT_STARTED; 29001=0; canary=0/20; formal=0; E3-E9=NOT_STARTED"),
    ])
    readme = root / f"deliverables/TO_SUBMIT_{PACKAGE}/{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text("\n".join([
        PACKAGE,
        f"runtime_commit={_git_head()}",
        f"stop_status={stop_status}",
        f"max_legal_global_windows={capacity.get('max_legal_global_windows')}",
        f"window_hours={capacity.get('window_hours')}",
        f"supported_span_hours={capacity.get('supported_span_hours')}",
        f"spatial_status={spatial['status']}",
        "validation_traces=0",
        "design_seeds=28101-28120",
        "validation_seeds=29101-29105 NOT_RUN",
        "profile_selection=NOT_STARTED",
        "E3-E9=NOT_STARTED",
        "",
        "Replay:",
        "  set PYTHONPATH=src",
        "  pytest -q tests/unit/test_e2_global_window_finite_gate_*.py",
        "  pytest -q tests/integration/test_e2_global_window_finite_gate_*.py",
        "  python scripts/check_e2_global_window_finite_gate_compact_evidence.py",
        "",
    ]), encoding="utf-8")
    dump_json({
        "package": PACKAGE,
        "report": str(report.relative_to(root)).replace("\\", "/"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }, root / "outputs/e2_global_window/E2_CONTEXT.json")
    print(json.dumps({
        "status": stop_status,
        "max_legal_global_windows": capacity.get("max_legal_global_windows"),
        "spatial": spatial["status"],
        "isolation": isolation["audit"]["status"],
        "validation_reads": isolation["audit"]["validation_read_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
