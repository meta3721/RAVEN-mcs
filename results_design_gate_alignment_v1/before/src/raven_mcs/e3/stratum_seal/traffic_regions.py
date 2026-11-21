"""Frozen Traffic station → 4 real-region mapping (E2 public-target identity)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.e2.traffic_public_target.core import build_label_free_regions
from raven_mcs.e3.stratum_seal.constants import TRAFFIC_PUBLIC_TARGET_MAPPING_HASH
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json


class TrafficStratumIdentityError(RuntimeError):
    CODE = "TRAFFIC_STRATUM_IDENTITY_ERROR"


def load_frozen_traffic_station_regions(root: Path) -> tuple[dict[str, str], dict[str, Any]]:
    """Recover sealed label-free 43→4 region mapping (no reclustering invent)."""
    coords = root / "configs/frozen/e2_traffic/station_spatial_identity.parquet"
    if not coords.is_file():
        raise TrafficStratumIdentityError(
            "TRAFFIC_STRATUM_IDENTITY_ERROR: missing station_spatial_identity.parquet"
        )
    spatial = pd.read_parquet(coords)
    mapping_df, audit = build_label_free_regions(spatial)
    if audit.get("mapping_hash") != TRAFFIC_PUBLIC_TARGET_MAPPING_HASH:
        raise TrafficStratumIdentityError(
            "TRAFFIC_STRATUM_IDENTITY_ERROR: mapping_hash mismatch vs frozen public-target identity"
        )
    if int(audit.get("region_count", 0)) != 4 or int(audit.get("station_count", 0)) != 43:
        raise TrafficStratumIdentityError(
            "TRAFFIC_STRATUM_IDENTITY_ERROR: expected 43 stations and 4 regions"
        )
    station_to_region = {
        str(r.station_id): str(r.region_id) for r in mapping_df.itertuples(index=False)
    }
    if len(station_to_region) != 43 or len(set(station_to_region.values())) != 4:
        raise TrafficStratumIdentityError(
            "TRAFFIC_STRATUM_IDENTITY_ERROR: station/region cardinality failed"
        )
    meta = {
        **audit,
        "source": "e2_traffic_public_target.build_label_free_regions",
        "coordinate_source_path": str(coords.relative_to(root)).replace("\\", "/"),
        "coordinate_source_hash": sha256_file(coords),
        "prior_frozen_identity": "configs/frozen/e2_traffic_public_target/station_region_identity.json",
        "expected_mapping_hash": TRAFFIC_PUBLIC_TARGET_MAPPING_HASH,
        "no_recluster": True,
        "region_ids": sorted(set(station_to_region.values())),
        "station_ids": sorted(station_to_region.keys()),
        "s_construction": "region_id::time_block::weekday|weekend",
        "max_raw_strata": 32,
        "status": "FROZEN_IDENTITY_RECOVERED",
    }
    return station_to_region, meta


def freeze_traffic_region_mapping_artifacts(root: Path, out_dir: Path) -> dict[str, Any]:
    station_to_region, meta = load_frozen_traffic_station_regions(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        {"station_id": s, "region_id": r} for s, r in sorted(station_to_region.items())
    ]
    frame = pd.DataFrame(rows)
    frame.to_csv(out_dir / "traffic_station_region_mapping.csv", index=False)
    frame.to_parquet(out_dir / "traffic_station_region_mapping.parquet", index=False)
    dump_json(meta, out_dir / "traffic_station_region_identity.json")
    return meta
