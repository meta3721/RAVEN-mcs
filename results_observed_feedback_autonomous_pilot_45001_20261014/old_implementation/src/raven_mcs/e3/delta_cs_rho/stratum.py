"""Frozen opportunity stratum s(i) recovery (independent of target group h)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.data.controlled import time_of_day_block, weekday_label


def map_atomic_to_stratum(
    *,
    spatial_id: str,
    absolute_time: pd.Timestamp,
    blocks: int = 4,
) -> str:
    """Deterministic station-level s(i) = spatial_id::block{k}::{weekday|weekend}."""
    block = time_of_day_block(pd.Timestamp(absolute_time), blocks=blocks)
    day = weekday_label(pd.Timestamp(absolute_time))
    return f"{spatial_id}::block{block}::{day}"


def parse_stratum(stratum_id: str) -> dict[str, Any]:
    parts = str(stratum_id).split("::")
    if len(parts) < 3:
        return {
            "coarse_spatial_region": parts[0] if parts else "",
            "time_block": parts[1] if len(parts) > 1 else "",
            "weekday_weekend_flag": "",
        }
    return {
        "coarse_spatial_region": parts[0],
        "time_block": parts[1],
        "weekday_weekend_flag": parts[2],
    }


def opportunity_stratum_definition(root: Path) -> dict[str, Any]:
    """Recover exact frozen opportunity-stratum definition per dataset."""
    datasets = {}
    for ds in ("sensorscope", "uair", "traffic"):
        path = (
            root
            / "configs/frozen/e3_multidataset_protocol_closure"
            / ds
            / "opportunity_strata.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        datasets[ds] = {
            "n_legal_opportunity_strata": int(payload["n_strata"]),
            "definition": payload["definition"],
            "nonempty_strata": int(payload.get("n_strata", 0)),
            "stratum_support_hash": digest,
            "config_path": str(path.relative_to(root)).replace("\\", "/"),
            "source_hash": digest,
            "spatial_coarsening": payload.get(
                "spatial_coarsening",
                "station/node spatial_id (no coarsening)" if ds != "traffic" else "4 real regions",
            ),
        }
    return {
        "stratum_dimensions": [
            "coarse spatial region",
            "time-of-day block (UTC hour//6 → block0..block3)",
            "weekday/weekend",
        ],
        "sensorscope_spatial_rule": "station_id is the spatial region (55×4×2=440)",
        "uair_spatial_rule": "station/node spatial_id is the spatial region (36×4×2=288)",
        "traffic_spatial_rule": (
            "frozen E2 public-target 4 real regions (43 stations→region0..3); "
            "s=region×block×day; max raw 32"
        ),
        "time_block_rule": "time_of_day_block(timestamp, blocks=4) = UTC.hour // 6",
        "weekday_weekend_rule": "weekday_label: weekend if UTC.dayofweek>=5 else weekday",
        "deterministic_mapping_function": {
            "sensorscope": "s(i)=spatial_id::block{k}::{weekday|weekend}",
            "uair": "s(i)=spatial_id::block{k}::{weekday|weekend}",
            "traffic": "s(i)=frozen_region_id::block{k}::{weekday|weekend}",
        },
        "code_sources": [
            "src/raven_mcs/data/matrix_adapter.py",
            "src/raven_mcs/data/controlled.py",
            "src/raven_mcs/e3/stratum_seal/remap.py",
            "src/raven_mcs/e3/stratum_seal/traffic_regions.py",
            "configs/frozen/e2_traffic_public_target/station_region_identity.json",
            "configs/frozen/e3_multidataset_protocol_closure/*/opportunity_strata.json",
        ],
        "independent_of_performance_outcomes": True,
        "distinct_from_target_group_h": True,
        "h_definition": "h(i)=(spatial_unit, time_of_day_block) → spatial_id::block{k} (no day-type)",
        "datasets": datasets,
        "status": "RECOVERED",
    }
