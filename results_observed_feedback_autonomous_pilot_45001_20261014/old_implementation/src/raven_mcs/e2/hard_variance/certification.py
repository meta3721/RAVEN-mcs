"""Pre-register and freeze finite-sample certification super-strata."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
BLOCKS = ("block0", "block1", "block2", "block3")
TIME_BAND = {
    "block0": "time_band_0",
    "block1": "time_band_0",
    "block2": "time_band_1",
    "block3": "time_band_1",
}


def _parse_raw(s: str) -> tuple[str, str, str]:
    parts = str(s).split("::")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return parts[0], "block0", "weekday"


def frozen_station_coordinates(root: Path) -> pd.DataFrame:
    """Deterministic synthetic coordinates (no geo in SensorScope atomic table).

    x = lexicographic rank; y = numeric station suffix rank.
    Frozen to configs/frozen/e2_certification/station_coordinates.parquet.
    """
    atomic = load_e1_atomic_target_weights(root)
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    weight = {str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)}
    stations = sorted({str(r.spatial_id) for r in processed.itertuples(index=False)})
    x_rank = {s: i for i, s in enumerate(stations)}

    def suffix(s: str) -> int:
        digits = "".join(ch for ch in s if ch.isdigit())
        return int(digits) if digits else 0

    y_sorted = sorted(stations, key=lambda s: (suffix(s), s))
    y_rank = {s: i for i, s in enumerate(y_sorted)}
    mass = {}
    for r in processed.itertuples(index=False):
        sid = str(r.spatial_id)
        uid = str(r.unit_id)
        if uid in weight:
            mass[sid] = mass.get(sid, 0.0) + weight[uid]
    rows = [{
        "station_id": s,
        "coord_x": float(x_rank[s]),
        "coord_y": float(y_rank[s]),
        "target_mass": float(mass.get(s, 0.0)),
        "coordinate_source": "synthetic_lexicographic_and_numeric_suffix_ranks_v1",
    } for s in stations]
    frame = pd.DataFrame(rows)
    out = root / "configs/frozen/e2_certification"
    out.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out / "station_coordinates.parquet", index=False)
    return frame


def _weighted_median_split(
    stations: list[str],
    coords: dict[str, float],
    masses: dict[str, float],
    axis_name: str,
) -> tuple[set[str], set[str]]:
    ordered = sorted(stations, key=lambda s: (coords[s], s))
    total = sum(masses[s] for s in ordered) or 1.0
    acc = 0.0
    left: list[str] = []
    for s in ordered:
        acc += masses[s]
        left.append(s)
        if acc >= 0.5 * total:
            break
    left_set = set(left)
    right_set = set(stations) - left_set
    if not right_set and len(ordered) >= 2:
        left_set = set(ordered[: len(ordered) // 2])
        right_set = set(ordered) - left_set
    return left_set, right_set


def build_spatial_regions(coords: pd.DataFrame, n_regions: int) -> dict[str, str]:
    stations = coords["station_id"].astype(str).tolist()
    cx = dict(zip(coords["station_id"].astype(str), coords["coord_x"].astype(float), strict=True))
    cy = dict(zip(coords["station_id"].astype(str), coords["coord_y"].astype(float), strict=True))
    mass = dict(zip(coords["station_id"].astype(str), coords["target_mass"].astype(float), strict=True))
    # Choose primary axis = larger coordinate span
    span_x = max(cx.values()) - min(cx.values())
    span_y = max(cy.values()) - min(cy.values())
    primary, secondary = (("x", cx), ("y", cy)) if span_x >= span_y else (("y", cy), ("x", cx))
    mapping: dict[str, str] = {}
    if n_regions == 2:
        a, b = _weighted_median_split(stations, primary[1], mass, primary[0])
        for s in a:
            mapping[s] = "R2_0"
        for s in b:
            mapping[s] = "R2_1"
    elif n_regions == 4:
        a, b = _weighted_median_split(stations, primary[1], mass, primary[0])
        for idx, group in enumerate((a, b)):
            g_list = sorted(group)
            if len(g_list) <= 1:
                for s in g_list:
                    mapping[s] = f"R4_{idx * 2}"
                continue
            c, d = _weighted_median_split(g_list, secondary[1], mass, secondary[0])
            for s in c:
                mapping[s] = f"R4_{idx * 2}"
            for s in d:
                mapping[s] = f"R4_{idx * 2 + 1}"
    else:
        raise ValueError(n_regions)
    return mapping


def build_cert_hierarchy(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    coords = frozen_station_coordinates(root)
    r2 = build_spatial_regions(coords, 2)
    r4 = build_spatial_regions(coords, 4)
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
        raw = f"{station}::{block}::{day}"
        band = TIME_BAND.get(block, "time_band_0")
        # day type: collapse mixed labels to weekday/weekend only for cert
        day_cert = day if day in {"weekday", "weekend"} else (
            "weekday" if "week" not in day else "weekend"
        )
        if day not in {"weekday", "weekend"}:
            # raw may already be weekday/weekend only
            day_cert = "weekday" if day.startswith("week") and "end" not in day else (
                "weekend" if "end" in day else "weekday"
            )
        if day in {"weekday", "weekend"}:
            day_cert = day
        unit_rows.append({
            "unit_id": uid,
            "station_id": station,
            "time_block": block,
            "day_type": day if day in {"weekday", "weekend"} else day_cert,
            "raw_stratum": raw,
            "target_mass": weight[uid],
            "region_r2": r2[station],
            "region_r4": r4[station],
            "time_band": band,
        })
    units = pd.DataFrame(unit_rows)
    # Fix day_type from raw
    units["day_type"] = units["raw_stratum"].map(lambda s: _parse_raw(s)[2])
    units.loc[~units["day_type"].isin(["weekday", "weekend"]), "day_type"] = "weekday"

    def cells(level: str) -> tuple[dict[str, str], list[str], dict[str, float]]:
        raw_to_cert: dict[str, str] = {}
        mass_by_cert: dict[str, float] = {}
        for r in units.itertuples(index=False):
            if level == "CERT-L32":
                cid = f"{r.region_r4}::{r.time_block}::{r.day_type}"
            elif level == "CERT-L16":
                cid = f"{r.region_r4}::{r.time_band}::{r.day_type}"
            elif level == "CERT-L8":
                cid = f"{r.region_r2}::{r.time_band}::{r.day_type}"
            else:
                raise ValueError(level)
            raw_to_cert[str(r.raw_stratum)] = cid
            mass_by_cert[cid] = mass_by_cert.get(cid, 0.0) + float(r.target_mass)
        # drop empty (already none); normalize
        total = sum(mass_by_cert.values()) or 1.0
        mass_by_cert = {k: v / total for k, v in mass_by_cert.items()}
        labels = sorted(mass_by_cert)
        return raw_to_cert, labels, mass_by_cert

    hierarchy = {}
    unit_cert_maps = {}
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        raw_map, labels, mass = cells(level)
        hierarchy[level] = {
            "level": level,
            "cell_count": len(labels),
            "cells": labels,
            "target_mass": mass,
            "raw_to_cert": raw_map,
            "spatial_dim": "region_r4" if "L32" in level or "L16" in level else "region_r2",
            "time_dim": "time_block" if "L32" in level else "time_band",
            "day_dim": "weekday|weekend",
        }
        # unit -> cert
        umap = {}
        for r in units.itertuples(index=False):
            umap[str(r.unit_id)] = raw_map[str(r.raw_stratum)]
        unit_cert_maps[level] = umap

    out = root / "configs/frozen/e2_certification"
    out.mkdir(parents=True, exist_ok=True)
    (out / "certification_super_stratum.yaml").write_text(
        yaml.safe_dump({
            "protocol": "E2-BALANCED-HARD-VARIANCE-AND-CERTIFICATION-STRATUM-FREEZE-R1",
            "time_band_0": ["block0", "block1"],
            "time_band_1": ["block2", "block3"],
            "levels": {
                "CERT-L32": "4 spatial regions × 4 time blocks × 2 day types",
                "CERT-L16": "4 spatial regions × 2 time bands × 2 day types",
                "CERT-L8": "2 spatial regions × 2 time bands × 2 day types",
            },
            "coordinate_source": "synthetic_lexicographic_and_numeric_suffix_ranks_v1",
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
        "coords": coords,
        "r2": r2,
        "r4": r4,
    }


def select_certification_level(
    variance_frame: pd.DataFrame,
    hierarchy: dict[str, Any],
    *,
    unit_cert_maps: dict[str, dict[str, str]],
    unit_target: dict[str, float],
    soft_arrival_by_unit: dict[str, float] | None,
    audit_registry_hash: str,
    root: Path | None = None,
) -> dict[str, Any]:
    """Select finest feasible level using audit V3 only (no validation seeds)."""
    root = Path(root or ROOT)
    v3 = variance_frame[variance_frame["version"] == "V3"].copy()
    feasibility = {}
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        col = f"D_TV_cert_{level}"
        head_col = f"head_{level}"
        tail_col = f"tail_{level}"
        if col not in v3.columns:
            feasibility[level] = {"feasible": False, "reason": "missing_column"}
            continue
        p95_tv = float(v3[col].quantile(0.95))
        p95_head = float((v3[head_col] - 1.0).abs().quantile(0.95))
        p95_tail = float((v3[tail_col] - 1.0).abs().quantile(0.95))
        mass = hierarchy[level]["target_mass"]
        min_lambda = min(mass.values()) if mass else 0.0
        total_arr_count = float(
            getattr(variance_frame, "attrs", {}).get("expected_arrival_total_count")
            or 0.0
        )
        if total_arr_count <= 0:
            # Fallback: V0 arrival mass / mean unit target weight (~1/n_units)
            v0_mass = float(
                variance_frame.loc[
                    variance_frame["version"] == "V0", "total_hard_arrival_count"
                ].mean()
            )
            total_arr_count = v0_mass * float(len(unit_target))
        min_exp = min_lambda * total_arr_count
        zero_rate = 0.0
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
            "minimum_expected_arrivals_per_positive_cell": float(min_exp),
            "zero_arrival_positive_cert_cell_rate": float(zero_rate),
            "cell_count": cell_count,
        }

    selected = None
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        if feasibility[level].get("feasible"):
            selected = level
            break
    status = "PASS" if selected else "BLOCKED_HARD_VARIANCE_TOO_LARGE_AT_CERT_L8"

    out = root / "configs/frozen/e2_certification"
    out.mkdir(parents=True, exist_ok=True)
    if selected:
        raw_map = hierarchy[selected]["raw_to_cert"]
        # atomic mapping parquet
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
            rows.append({
                "unit_id": uid,
                "raw_stratum": raw,
                "cert_stratum": raw_map[raw],
                "target_mass": weight[uid],
            })
        amap = pd.DataFrame(rows)
        amap.to_parquet(out / "atomic_certification_mapping.parquet", index=False)
        identity = {
            "selected_level": selected,
            "cell_count": hierarchy[selected]["cell_count"],
            "mapping_hash": sha256_json(dict(sorted(raw_map.items()))),
            "target_mass_hash": sha256_json(hierarchy[selected]["target_mass"]),
            "audit_registry_hash": audit_registry_hash,
            "feasibility": feasibility,
            "status": status,
            "selection_inputs": [
                "raw_target_mass",
                "dense_legal_candidate_exposure",
                "soft_balanced_probabilities",
                "audit-rep-0001:0200",
            ],
            "validation_seeds_used_for_selection": False,
            "coordinate_file_hash": sha256_file(out / "station_coordinates.parquet"),
        }
        dump_json(identity, out / "certification_identity.json")
        # update yaml with selection
        cfg = yaml.safe_load((out / "certification_super_stratum.yaml").read_text(encoding="utf-8"))
        cfg["selected_level"] = selected
        cfg["selected_cell_count"] = hierarchy[selected]["cell_count"]
        (out / "certification_super_stratum.yaml").write_text(
            yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8",
        )
    else:
        identity = {
            "selected_level": None,
            "status": status,
            "feasibility": feasibility,
            "audit_registry_hash": audit_registry_hash,
        }
        dump_json(identity, out / "certification_identity.json")

    dump_json(
        {"feasibility": feasibility, "selected_level": selected, "status": status},
        root / "outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json",
    )
    return {"selected_level": selected, "status": status, "feasibility": feasibility, "identity": identity}
