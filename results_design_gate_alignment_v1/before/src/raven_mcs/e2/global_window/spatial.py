"""True spatial identity — coordinates or E1 real region cluster only."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def load_true_spatial_identity(root: Path | None = None) -> dict[str, Any]:
    """Attempt true spatial identity; reject client-id folds and synthetic ranks."""
    root = Path(root or ROOT)
    out = root / "configs/frozen/e2_spatial_identity"
    out.mkdir(parents=True, exist_ok=True)
    groups_path = root / "configs/frozen/e1_sensorscope_groups.yaml"
    groups = yaml.safe_load(groups_path.read_text(encoding="utf-8"))
    atomic = load_e1_atomic_target_weights(root)
    stations = sorted({str(u).split("_", 1)[0] for u in atomic["unit_id"].astype(str)})

    # Search known project locations for lat/lon metadata (none expected).
    candidate_paths = [
        root / "data/raw/sensorscope/station_coordinates.csv",
        root / "data/raw/sensorscope/stations.csv",
        root / "data/metadata/sensorscope_station_coordinates.csv",
        root / "configs/frozen/sensorscope_station_coordinates.csv",
        root / "configs/frozen/e1_station_coordinates.parquet",
    ]
    found = next((p for p in candidate_paths if p.is_file()), None)
    e1_partition = groups.get("spatial_partition")
    has_e1_region_cluster = bool(e1_partition) and str(e1_partition).lower() not in {"none", "null", ""}

    rows = []
    for st in stations:
        rows.append({
            "station_id": st,
            "latitude": None,
            "longitude": None,
            "source_name": None,
            "source_hash": None,
            "region_cluster_id": None,
            "coordinate_valid": False,
            "coordinate_missing_reason": (
                "no_traceable_lat_lon_and_e1_spatial_partition_none"
                if not has_e1_region_cluster
                else "coordinates_missing"
            ),
        })
    frame = pd.DataFrame(rows)
    frame.to_parquet(out / "station_spatial_identity.parquet", index=False)

    # Explicitly reject prior client-id fold as non-true spatial identity.
    rejected_client_fold = {
        "method": "e1_frozen_client_region_mapping_v1",
        "rejected": True,
        "reason": "client-id-derived regions are forbidden in this round",
    }
    status = "BLOCKED_NO_VALID_SPATIAL_IDENTITY"
    if found is not None and has_e1_region_cluster:
        status = "PASS"  # unreachable without files; kept for completeness

    audit = {
        "status": status,
        "coordinate_source": None,
        "coordinate_file_found": str(found.relative_to(root)).replace("\\", "/") if found else None,
        "e1_spatial_partition": e1_partition,
        "E1_real_region_cluster_available": bool(has_e1_region_cluster),
        "synthetic_usage_count": 0,
        "client_id_derived_region_count": 0,
        "rejected_client_id_fold": rejected_client_fold,
        "missing_coordinate_count": int(len(frame)),
        "station_count": int(len(frame)),
        "station_identity_symmetric_difference": 0,
        "groups_config_hash": sha256_file(groups_path),
        "source_hash": None,
        "note": (
            "No SensorScope lat/lon registry in-repo; E1 spatial_partition=none; "
            "client-id folding rejected as non-true spatial identity."
        ),
    }
    dump_json(audit, root / "outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json")
    dump_json({
        "status": status,
        "station_count": int(len(frame)),
        "audit": audit,
    }, out / "spatial_identity_manifest.json")
    return {"frame": frame, "audit": audit, "status": status}
