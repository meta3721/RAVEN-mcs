"""Tombstone prior local-window / fixed 5/5 gate result."""
from __future__ import annotations

from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def write_prior_tombstone(root: Path | None = None) -> dict:
    root = Path(root or ROOT)
    payload = {
        "prior_package": "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1",
        "prior_certification_result": "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE",
        "prior_design_schedule_source": "validation seed 29101",
        "prior_spatial_identity": "client-id folding",
        "prior_gate": "per-seed fixed thresholds + 5/5 rule",
        "prior_status": "INVALID_PENDING_GLOBAL_WINDOW_AND_GATE_REPAIR",
        "invalid_reason_client_specific_window_boundaries": True,
        "invalid_reason_cross_window_atomic_reuse": True,
        "invalid_reason_client_id_spatial_fold": True,
        "invalid_reason_validation_schedule_used_for_design_audit": True,
        "invalid_reason_five_of_five_fixed_threshold_gate": True,
        "must_rebuild_global_windows": True,
        "must_preregister_finite_sample_gate": True,
        "status": "TOMBSTONED",
    }
    out = root / "outputs/audits/E2_PRIOR_LOCAL_WINDOW_AND_GATE_TOMBSTONE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    return payload
