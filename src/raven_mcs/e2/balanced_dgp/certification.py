"""CERT-L32/L16/L8 from real E1 spatial identity; single-arm selection only."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.balanced_dgp.spatial import load_e1_client_spatial_identity
from raven_mcs.e2.identity import load_e1_atomic_target_weights
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
TIME_BAND = {
    "block0": "time_band_0", "block1": "time_band_0",
    "block2": "time_band_1", "block3": "time_band_1",
}


def _parse_raw(s: str) -> tuple[str, str, str]:
    parts = str(s).split("::")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return parts[0], "block0", "weekday"


def build_cert_hierarchy(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    spatial = load_e1_client_spatial_identity(root)
    frame = spatial["frame"].set_index("station_id")
    atomic = load_e1_atomic_target_weights(root)
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    weight = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}

    unit_rows = []
    for r in processed.itertuples(index=False):
        uid = str(r.unit_id)
        if uid not in weight:
            continue
        station, block, day = _parse_raw(str(r.opportunity_stratum))
        if station not in frame.index:
            continue
        raw = f"{station}::{block}::{day}"
        day_cert = day if day in {"weekday", "weekend"} else "weekday"
        unit_rows.append({
            "unit_id": uid,
            "station_id": station,
            "time_block": block,
            "day_type": day_cert,
            "raw_stratum": raw,
            "target_mass": weight[uid],
            "region_r2": str(frame.loc[station, "region_r2"]),
            "region_r4": str(frame.loc[station, "region_r4"]),
            "time_band": TIME_BAND.get(block, "time_band_0"),
        })
    units = pd.DataFrame(unit_rows)
    units["day_type"] = units["raw_stratum"].map(lambda s: _parse_raw(s)[2])
    units.loc[~units["day_type"].isin(["weekday", "weekend"]), "day_type"] = "weekday"

    hierarchy = {}
    unit_cert_maps = {}
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        raw_to_cert: dict[str, str] = {}
        mass_by_cert: dict[str, float] = {}
        for r in units.itertuples(index=False):
            if level == "CERT-L32":
                cid = f"{r.region_r4}::{r.time_block}::{r.day_type}"
            elif level == "CERT-L16":
                cid = f"{r.region_r4}::{r.time_band}::{r.day_type}"
            else:
                cid = f"{r.region_r2}::{r.time_band}::{r.day_type}"
            raw_to_cert[str(r.raw_stratum)] = cid
            mass_by_cert[cid] = mass_by_cert.get(cid, 0.0) + float(r.target_mass)
        total = sum(mass_by_cert.values()) or 1.0
        mass_by_cert = {k: v / total for k, v in mass_by_cert.items()}
        labels = sorted(mass_by_cert)
        hierarchy[level] = {
            "level": level,
            "cell_count": len(labels),
            "cells": labels,
            "target_mass": mass_by_cert,
            "raw_to_cert": raw_to_cert,
        }
        umap = {str(r.unit_id): raw_to_cert[str(r.raw_stratum)] for r in units.itertuples(index=False)}
        unit_cert_maps[level] = umap

    out = root / "configs/frozen/e2_dgp_certification"
    out.mkdir(parents=True, exist_ok=True)
    (out / "certification_super_stratum.yaml").write_text(
        yaml.safe_dump({
            "protocol": "E2-BALANCED-DGP-AND-SINGLE-TRACE-CERTIFICATION-REPAIR-R1",
            "spatial_source": "e1_frozen_client_region_mapping_v1",
            "time_band_0": ["block0", "block1"],
            "time_band_1": ["block2", "block3"],
            "levels": {
                "CERT-L32": "4 real spatial regions × 4 time blocks × 2 day types",
                "CERT-L16": "4 real spatial regions × 2 time bands × 2 day types",
                "CERT-L8": "2 real spatial regions × 2 time bands × 2 day types",
            },
        }, sort_keys=False),
        encoding="utf-8",
    )
    dump_json(
        {k: {"cell_count": v["cell_count"], "cells": v["cells"]} for k, v in hierarchy.items()},
        out / "certification_hierarchy_definition.json",
    )
    return {
        "hierarchy": hierarchy,
        "unit_cert_maps": unit_cert_maps,
        "units": units,
        "spatial": spatial,
    }


def select_certification_level(
    variance_frame: pd.DataFrame,
    hierarchy: dict[str, Any],
    *,
    expected_arrival_total_count: float,
    audit_registry_hash: str,
    root: Path | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    v3 = variance_frame[variance_frame["version"] == "V3"].copy()
    feasibility = {}
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        col = f"D_TV_cert_{level}"
        zero_col = f"zero_arrival_rate_{level}"
        p95_tv = float(v3[col].quantile(0.95))
        p95_head = float((v3["head_mass_ratio"] - 1.0).abs().quantile(0.95))
        p95_tail = float((v3["tail_mass_ratio"] - 1.0).abs().quantile(0.95))
        mass = hierarchy[level]["target_mass"]
        min_lambda = min(mass.values()) if mass else 0.0
        min_exp = float(min_lambda * expected_arrival_total_count)
        zero_rate = float(v3[zero_col].mean()) if zero_col in v3.columns else 1.0
        cell_count = int(hierarchy[level]["cell_count"])
        feasible = (
            p95_tv <= 0.045
            and p95_head <= 0.045
            and p95_tail <= 0.045
            and min_exp >= 20.0
            and zero_rate <= 0.01
            and cell_count >= 8
        )
        feasibility[level] = {
            "feasible": bool(feasible),
            "P95_D_TV_cert": p95_tv,
            "P95_abs_head_dev": p95_head,
            "P95_abs_tail_dev": p95_tail,
            "minimum_expected_arrivals_per_positive_cell": min_exp,
            "zero_arrival_positive_cert_cell_rate": zero_rate,
            "cell_count": cell_count,
        }

    selected = None
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        if feasibility[level]["feasible"]:
            selected = level
            break
    # Finest feasible must match selection order above.
    finest = selected
    status = "PASS" if selected else "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE"

    out = root / "configs/frozen/e2_dgp_certification"
    out.mkdir(parents=True, exist_ok=True)
    identity: dict[str, Any]
    if selected:
        raw_map = hierarchy[selected]["raw_to_cert"]
        rows = []
        processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
        atomic = load_e1_atomic_target_weights(root)
        weight = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
        for r in processed.itertuples(index=False):
            uid = str(r.unit_id)
            if uid not in weight:
                continue
            station, block, day = _parse_raw(str(r.opportunity_stratum))
            raw = f"{station}::{block}::{day}"
            if raw not in raw_map:
                continue
            rows.append({
                "unit_id": uid,
                "raw_stratum": raw,
                "cert_stratum": raw_map[raw],
                "target_mass": weight[uid],
            })
        pd.DataFrame(rows).to_parquet(out / "atomic_certification_mapping.parquet", index=False)
        identity = {
            "selected_level": selected,
            "finest_feasible_level": finest,
            "cell_count": hierarchy[selected]["cell_count"],
            "mapping_hash": sha256_json(dict(sorted(raw_map.items()))),
            "target_mass_hash": sha256_json(hierarchy[selected]["target_mass"]),
            "audit_registry_hash": audit_registry_hash,
            "feasibility": feasibility,
            "status": status,
            "selection_inputs": [
                "raw_target_mass",
                "bounded_legal_candidate_exposure",
                "soft_balanced_p_opp",
                "single-arm-audit-rep-0001:0200",
            ],
            "validation_seeds_used_for_selection": False,
            "antithetic_used_for_selection": False,
            "spatial_identity_hash": sha256_file(out / "station_spatial_identity.parquet"),
        }
        dump_json(identity, out / "certification_identity.json")
        cfg = yaml.safe_load((out / "certification_super_stratum.yaml").read_text(encoding="utf-8"))
        cfg["selected_level"] = selected
        cfg["selected_cell_count"] = hierarchy[selected]["cell_count"]
        (out / "certification_super_stratum.yaml").write_text(
            yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8",
        )
    else:
        identity = {
            "selected_level": None,
            "finest_feasible_level": None,
            "status": status,
            "feasibility": feasibility,
            "audit_registry_hash": audit_registry_hash,
            "antithetic_used_for_selection": False,
        }
        dump_json(identity, out / "certification_identity.json")

    dump_json(
        {
            "feasibility": feasibility,
            "selected_level": selected,
            "finest_feasible_level": finest,
            "status": status,
            "antithetic_used_for_selection": False,
        },
        root / "outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json",
    )
    return {
        "selected_level": selected,
        "finest_feasible_level": finest,
        "status": status,
        "feasibility": feasibility,
        "identity": identity,
    }
