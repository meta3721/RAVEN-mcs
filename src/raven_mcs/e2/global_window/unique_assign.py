"""Atomic unique-window assignment audit (requires feasible global windows)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def write_blocked_unique_assignment(
    *,
    frame: pd.DataFrame,
    capacity: dict[str, Any],
    root: Path | None = None,
    reason: str,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    payload = {
        "status": "BLOCKED_GLOBAL_WINDOW_CAPACITY_INSUFFICIENT",
        "reason": reason,
        "supported_atomic_unit_count": int(frame["unit_id"].nunique()),
        "assigned_unit_count": 0,
        "unassigned_unit_count": int(frame["unit_id"].nunique()),
        "multiply_assigned_unit_count": 0,
        "cross_window_duplicate_unit_count": 0,
        "within_window_duplicate_unit_count": 0,
        "empty_global_window_count": None,
        "empty_client_window_count": None,
        "per_window_unit_count_min": None,
        "per_window_unit_count_median": None,
        "per_window_unit_count_mean": None,
        "per_window_unit_count_max": None,
        "capacity": capacity,
        "mapping_hash": sha256_json({"blocked": True, "capacity": capacity}),
        "note": (
            "Unique non-overlapping assignment to 100 global windows is impossible "
            "without sliding/overlap reuse; overlap is forbidden."
        ),
    }
    out = root / "outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    map_dir = root / "configs/frozen/e2_global_windows"
    map_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["unit_id", "window_id", "absolute_time", "spatial_id"]).to_parquet(
        map_dir / "atomic_unique_window_mapping.parquet", index=False,
    )
    return payload
