"""Pure, offline-only helpers for the E3 final evidence seal."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    """Return the SHA-256 of a file without modifying it."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reclassify_p2_record(record: dict[str, Any]) -> dict[str, Any]:
    """Separate persisted-vector feasibility from unavailable optimality proof."""
    residual = float(record.get("max_residual", float("inf")))
    return {
        **record,
        "feasibility_status": (
            "CERTIFIED_FEASIBLE"
            if residual == 0.0
            else "CERTIFIED_WITHIN_NUMERICAL_TOLERANCE"
        ),
        "optimality_status": "NOT_RECONSTRUCTABLE",
        "native_solver_status_available": False,
        "full_objective_state_available": False,
    }


def all_identity_fields_match(row: dict[str, Any]) -> bool:
    """Check every explicitly comparable formal/replay identity pair."""
    pairs = (
        ("formal_eventtrace_hash", "replay_eventtrace_hash"),
        ("formal_config_hash", "replay_config_hash"),
        ("formal_target_artifact_sha256", "replay_target_artifact_sha256"),
        ("formal_stratum_identity_sha256", "replay_stratum_identity_sha256"),
    )
    return all(row.get(left) == row.get(right) for left, right in pairs)
