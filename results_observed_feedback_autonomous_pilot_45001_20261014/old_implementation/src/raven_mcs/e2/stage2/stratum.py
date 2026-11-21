"""True opportunity stratum mapping and deterministic merge."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_supported_test_units
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
FORBIDDEN = {"head", "neutral", "tail"}


def _parse_raw(label: str) -> tuple[str, str, str]:
    parts = str(label).split("::")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], parts[1], "weekday"
    return parts[0], "block0", "weekday"


def build_opportunity_stratum_table(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    protocol = yaml.safe_load(
        (root / "configs/frozen/e2_stratum/stratum_merge_protocol.yaml").read_text(
            encoding="utf-8"
        )
    )
    atomic = load_e1_atomic_target_weights(root)
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    weight_map = {
        str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)
    }
    rows = []
    for r in processed.itertuples(index=False):
        uid = str(r.unit_id)
        if uid not in weight_map:
            continue
        station, block, day = _parse_raw(str(r.opportunity_stratum))
        # Protocol coarsens day_type at construction: campus × time-of-day.
        # Day type remains recorded but is not a free stratum axis after merge.
        stratum_id = f"sensorscope_campus::{block}::all_days"
        rows.append({
            "unit_id": uid,
            "region_id": "sensorscope_campus",
            "time_of_day_bin": block,
            "day_type": "all_days",
            "raw_day_type": day,
            "raw_opportunity_stratum": str(r.opportunity_stratum),
            "station_id": station,
            "stratum_id": stratum_id,
            "target_mass": float(weight_map[uid]),
            "supported_flag": uid in supported,
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("empty opportunity stratum table")

    # Deterministic merge of strata below lambda_stratum_min.
    lambda_min = float(protocol["lambda_stratum_min"])
    mass_by = frame.groupby("stratum_id", sort=True)["target_mass"].sum()
    total = float(mass_by.sum())
    mass_by = mass_by / total
    merge_rows = []
    active = {s: float(m) for s, m in mass_by.items()}
    mapping = {s: s for s in active}

    def _parse_s(sid: str) -> tuple[str, str, str]:
        a, b, c = sid.split("::")
        return a, b, c

    blocks = list(protocol["time_of_day_bins"])
    days = list(protocol["day_types"])

    def merge_pair(a: str, b: str, reason: str) -> None:
        nonlocal active, mapping
        if a not in active or b not in active or a == b:
            return
        keep, drop = sorted([a, b])  # lex tie-break: keep smaller id, absorb larger into...
        # Prefer keep the larger mass; tie -> lex smaller.
        if active[a] > active[b] or (active[a] == active[b] and a < b):
            keep, drop = a, b
        else:
            keep, drop = b, a
        active[keep] = active[keep] + active[drop]
        del active[drop]
        for src, dst in list(mapping.items()):
            if dst == drop:
                mapping[src] = keep
        mapping[drop] = keep
        merge_rows.append({
            "dropped_stratum_id": drop,
            "kept_stratum_id": keep,
            "reason": reason,
            "merged_mass": active[keep],
        })

    # Merge undersized strata: adjacent time bins same day, then adjacent day types.
    changed = True
    while changed:
        changed = False
        small = sorted([s for s, m in active.items() if m < lambda_min])
        for sid in small:
            if sid not in active or active[sid] >= lambda_min:
                continue
            region, block, day = _parse_s(sid)
            bi = blocks.index(block) if block in blocks else -1
            neighbors = []
            if bi >= 0:
                if bi > 0:
                    neighbors.append(f"{region}::{blocks[bi - 1]}::{day}")
                if bi + 1 < len(blocks):
                    neighbors.append(f"{region}::{blocks[bi + 1]}::{day}")
            for nb in neighbors:
                if nb in active:
                    merge_pair(sid, nb, "same_region_same_day_type_adjacent_time_bin")
                    changed = True
                    break
            if changed:
                break
        if changed:
            continue
        small = sorted([s for s, m in active.items() if m < lambda_min])
        for sid in small:
            if sid not in active or active[sid] >= lambda_min:
                continue
            region, block, day = _parse_s(sid)
            di = days.index(day) if day in days else -1
            if di >= 0:
                for dj in (di - 1, di + 1):
                    if 0 <= dj < len(days):
                        nb = f"{region}::{block}::{days[dj]}"
                        if nb in active:
                            merge_pair(sid, nb, "same_region_adjacent_day_type")
                            changed = True
                            break
            if changed:
                break

    frame["stratum_id"] = frame["stratum_id"].map(lambda s: mapping.get(s, s))
    # Renormalize target mass after merge.
    mass = frame.groupby("stratum_id", sort=True)["target_mass"].transform("sum")
    frame["stratum_target_mass"] = frame["target_mass"]  # unit mass
    strata = sorted(frame["stratum_id"].unique())
    if any(s in FORBIDDEN for s in strata):
        raise RuntimeError("role stratum ids forbidden")
    stratum_mass = {
        s: float(frame.loc[frame["stratum_id"] == s, "target_mass"].sum()) for s in strata
    }
    tsum = sum(stratum_mass.values())
    stratum_mass = {k: v / tsum for k, v in stratum_mass.items()}

    out_dir = root / "configs/frozen/e2_stratum"
    out_dir.mkdir(parents=True, exist_ok=True)
    parquet = out_dir / "atomic_opportunity_stratum.parquet"
    export = frame[[
        "unit_id", "region_id", "time_of_day_bin", "day_type", "stratum_id",
        "target_mass", "supported_flag",
    ]].copy()
    # Store unit target mass; stratum masses live in identity.
    export.to_parquet(parquet, index=False)

    identity = {
        "source_file": "data/processed/sensorscope/atomic_units.parquet",
        "source_rule": protocol["source_rule"],
        "source_hash": sha256_file(root / "data/processed/sensorscope/atomic_units.parquet"),
        "mapping_hash": sha256_json({
            "unit_stratum": dict(zip(export["unit_id"], export["stratum_id"], strict=True)),
            "stratum_mass": stratum_mass,
        }),
        "stratum_count_raw": int(len(mass_by)),
        "stratum_count_merged": int(len(strata)),
        "target_mass_sum": float(sum(stratum_mass.values())),
        "empty_stratum_count": 0,
        "unsupported_unit_count": int((~export["supported_flag"]).sum()),
        "stratum_ids": strata,
        "stratum_target_mass": stratum_mass,
        "role_substitution": False,
        "lambda_stratum_min": lambda_min,
        "protocol_hash": sha256_json(protocol),
    }
    if abs(identity["target_mass_sum"] - 1.0) > 1e-9:
        raise RuntimeError("stratum target mass must sum to 1")
    dump_json(identity, out_dir / "opportunity_stratum_identity.json")

    audit = pd.DataFrame(merge_rows)
    audit_path = root / "outputs/audits/E2_STRATUM_MERGE_AUDIT.csv"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(audit_path, index=False)
    return {
        "frame": export,
        "identity": identity,
        "merge_audit_rows": len(merge_rows),
        "parquet": str(parquet),
    }


def load_opportunity_stratum(root: Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    root = Path(root or ROOT)
    path = root / "configs/frozen/e2_stratum/atomic_opportunity_stratum.parquet"
    identity = root / "configs/frozen/e2_stratum/opportunity_stratum_identity.json"
    if not path.is_file() or not identity.is_file():
        build_opportunity_stratum_table(root)
    frame = pd.read_parquet(path)
    ident = __import__("json").loads(identity.read_text(encoding="utf-8"))
    if any(s in FORBIDDEN for s in ident["stratum_ids"]):
        raise RuntimeError("forbidden role strata in identity")
    return frame, ident
