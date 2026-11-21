"""Apply sealed opportunity-stratum identity per dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.data.controlled import time_of_day_block, weekday_label
from raven_mcs.e3.stratum_seal.traffic_regions import (
    TrafficStratumIdentityError,
    load_frozen_traffic_station_regions,
)


def apply_sealed_opportunity_stratum(
    atomic: pd.DataFrame,
    *,
    dataset: str,
    root: Path | None = None,
    station_to_region: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return atomic copy with sealed s(i); Traffic remapped to 4-region strata.

    SensorScope / U-Air / fixtures: retain processed station-level s(i).
    Traffic: s(i) = frozen_region :: time_block :: weekday|weekend (max 32).
    """
    ds = str(dataset).strip().lower()
    out = atomic.copy()
    if ds != "traffic":
        strata = sorted(out["opportunity_stratum"].astype(str).unique())
        return out, {
            "dataset": ds,
            "remapped": False,
            "spatial_rule": "station/node spatial_id (no coarsening)",
            "n_unique_strata": len(strata),
            "status": "FROZEN_IDENTITY_CONFIRMED",
        }

    if station_to_region is None:
        if root is None:
            raise TrafficStratumIdentityError(
                "TRAFFIC_STRATUM_IDENTITY_ERROR: root required to load region mapping"
            )
        station_to_region, _ = load_frozen_traffic_station_regions(root)

    new_s = []
    for row in out.itertuples(index=False):
        sid = str(row.spatial_id)
        region = station_to_region.get(sid)
        if region is None:
            # try without leading zeros / string normalize
            raise TrafficStratumIdentityError(
                f"TRAFFIC_STRATUM_IDENTITY_ERROR: station {sid} missing region mapping"
            )
        parts = str(row.opportunity_stratum).split("::")
        if len(parts) >= 3 and parts[1].startswith("block"):
            block, day = parts[1], parts[2]
        elif "absolute_time" in out.columns:
            ts = pd.Timestamp(getattr(row, "absolute_time"))
            block = f"block{time_of_day_block(ts)}"
            day = weekday_label(ts)
        else:
            raise TrafficStratumIdentityError(
                "TRAFFIC_STRATUM_IDENTITY_ERROR: cannot derive time/day for remapping"
            )
        new_s.append(f"{region}::{block}::{day}")
    out["opportunity_stratum"] = new_s
    # Keep station-level target_group h(i) unchanged
    strata = sorted(set(new_s))
    if len(strata) > 32:
        raise TrafficStratumIdentityError(
            f"TRAFFIC_STRATUM_IDENTITY_ERROR: nonempty strata {len(strata)} > 32"
        )
    # Hard fail if still station-level (station id appears as first token of many strata)
    first_tokens = {s.split("::")[0] for s in strata}
    if any(t.startswith("region") for t in first_tokens) is False:
        raise TrafficStratumIdentityError(
            "TRAFFIC_STRATUM_IDENTITY_ERROR: remapped strata lack region* prefixes"
        )
    if len(first_tokens) > 4:
        raise TrafficStratumIdentityError(
            f"TRAFFIC_STRATUM_IDENTITY_ERROR: {len(first_tokens)} spatial tokens (want ≤4 regions)"
        )
    return out, {
        "dataset": "traffic",
        "remapped": True,
        "spatial_rule": "frozen 4 real regions (E2 public-target label-free)",
        "n_unique_strata": len(strata),
        "max_raw_strata": 32,
        "region_ids": sorted(first_tokens),
        "status": "FROZEN_IDENTITY_RECOVERED",
    }
