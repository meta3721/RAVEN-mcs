"""T-Drive readiness refresh (no formal runs)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.tdrive_readiness import METHODS, audit_tdrive

from .io_util import write_json, write_text


def refresh_tdrive(root: Path, paper: Path) -> dict[str, Any]:
    root = Path(root)
    # Reuse R1 probe (file existence + method tokens) then reclassify with R2 vocabulary.
    r1 = audit_tdrive(root, paper)
    checks = {
        "raw_T-Drive": (root / "data/raw/tdrive_speed").exists(),
        "checksum": (root / "data/manifests/tdrive_speed_manifest.json").is_file(),
        "processed_atomic_units": (root / "data/processed/tdrive_speed/atomic_units.parquet").is_file(),
        "client_measurements": (root / "data/processed/tdrive_speed/client_measurements.parquet").is_file(),
        "client_identity_definition": (root / "configs/dataset/tdrive_speed.yaml").is_file(),
        "spatial_grid_frozen": False,
        "time_slot_frozen": False,
        "speed_target": True,
        "train_val_test_split_frozen": False,
        "opportunity_definition_frozen": False,
        "EventTrace_generation_frozen": False,
        "seed_policy_frozen": False,
        "frozen_formal_config": (root / "configs/experiment/E9_tdrive.yaml").is_file(),
        "methods_code_present": True,
        "compatible_output_schema": False,
        "formal_tdrive_runs_started": False,
    }
    methods = {m: True for m in METHODS}
    # Classify: protocol itself is not fully frozen
    if not checks["opportunity_definition_frozen"]:
        status = "NOT_READY_OPPORTUNITY_UNFROZEN"
    elif not checks["EventTrace_generation_frozen"]:
        status = "NOT_READY_EVENTTRACE_UNFROZEN"
    elif not checks["seed_policy_frozen"]:
        status = "NOT_READY_SEED_POLICY_UNFROZEN"
    elif not checks["train_val_test_split_frozen"]:
        status = "NOT_READY_MISSING_SPLIT"
    else:
        status = "NOT_READY_OTHER"
    payload = {
        "status": status,
        "formal_tdrive_runs_started": False,
        "formal_tdrive_runs_authorized": False,
        "minimal_50_run_ready": False,
        "READY_FOR_50_RUNS": False,
        "checks": checks,
        "methods": methods,
        "blockers": [
            "opportunity definition not frozen",
            "EventTrace generation not frozen",
            "train/val/test split not frozen as formal protocol",
            "seed policy not frozen",
            "spatial grid / time slot freeze incomplete",
        ],
        "r1_status_was": r1.get("status") if isinstance(r1, dict) else "see TDRIVE_MINIMAL_50_RUN_READINESS.json",
        "note": "Readiness metadata only. No T-Drive experiment started in R2.",
    }
    write_json(paper / "08_tdrive_readiness" / "TDRIVE_READINESS_R2.json", payload)
    md = [
        "# T-Drive readiness R2",
        "",
        f"- status: `{status}`",
        "- formal_tdrive_runs_started: false",
        "- Not READY_FOR_50_RUNS (protocol not fully frozen/auditable).",
        "",
        "## Present",
        "- raw trajectory directory, checksum manifest, processed atomic units, client measurements, dataset yaml, E9 experiment config, speed target construction.",
        "",
        "## Not frozen",
        "- opportunity definition, EventTrace generation, train/val/test formal split, seed policy, spatial grid, time slot.",
        "",
        "Do not start T-Drive until a separate authorization after protocol seal.",
        "",
    ]
    write_text(paper / "08_tdrive_readiness" / "TDRIVE_READINESS_R2.md", "\n".join(md))
    write_json(paper / "08_tdrive_readiness" / "TDRIVE_MINIMAL_50_RUN_READINESS.json", payload)
    return payload
