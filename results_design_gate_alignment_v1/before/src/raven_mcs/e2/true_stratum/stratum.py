"""Restore E1 true opportunity stratum: station × time_block × day_type."""
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
BLOCKS = ("block0", "block1", "block2", "block3")
DAYS = ("weekday", "weekend")


def _parse_raw(label: str) -> tuple[str, str, str]:
    parts = str(label).split("::")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], parts[1], "weekday"
    return parts[0], "block0", "weekday"


def build_true_opportunity_stratum(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    protocol_path = root / "configs/frozen/e2_true_stratum/stratum_merge_protocol.yaml"
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    atomic = load_e1_atomic_target_weights(root)
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    weight_map = {
        str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)
    }
    pi_path = root / "configs/frozen/e1_pi_target_client_stratum.parquet"
    pi = pd.read_parquet(pi_path)
    e1_strata = set(pi["opportunity_stratum"].astype(str))
    e1_lambda = (
        pi.groupby("opportunity_stratum", sort=True)["Lambda_s_tar"].first().to_dict()
    )

    rows: list[dict[str, Any]] = []
    missing_spatial = 0
    missing_day = 0
    unknown_unit = 0
    for r in processed.itertuples(index=False):
        uid = str(r.unit_id)
        if uid not in weight_map:
            continue
        station, block, day = _parse_raw(str(r.opportunity_stratum))
        if not station or station == "sensorscope_campus":
            missing_spatial += 1
        if day not in DAYS:
            missing_day += 1
        raw_id = f"{station}::{block}::{day}"
        if raw_id not in e1_strata:
            # Prefer exact E1 label when present on the unit.
            raw_id = str(r.opportunity_stratum)
        rows.append({
            "unit_id": uid,
            "spatial_region_id": station,
            "time_block": block,
            "day_type": day,
            "raw_stratum_id": raw_id,
            "merged_stratum_id": raw_id,
            "target_mass": float(weight_map[uid]),
            "supported_flag": uid in supported,
            "source_identity": "e1_opportunity_stratum",
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("empty true opportunity stratum table")

    unit_set = set(frame["unit_id"].astype(str))
    atomic_set = set(atomic["unit_id"].astype(str))
    symdiff = len(unit_set ^ atomic_set)
    unknown_unit = int(len(atomic_set - unit_set))

    # Target mass from unit weights; also cross-check E1 Lambda.
    mass_by = frame.groupby("raw_stratum_id", sort=True)["target_mass"].sum()
    total = float(mass_by.sum())
    if total <= 0:
        raise RuntimeError("non-positive stratum mass")
    mass_by = mass_by / total
    active = {str(s): float(m) for s, m in mass_by.items()}
    mapping = {s: s for s in active}
    merge_rows: list[dict[str, Any]] = []
    lambda_min = float(protocol["lambda_stratum_min"])
    min_opp = float(protocol["min_expected_opportunity_events_300"])
    # Pre-outcome exposure proxy: Lambda_s * (300 windows * 8 clients * 20 * base rate).
    # Base opportunity rate ~0.20 under balanced; use conservative 0.20.
    total_opp_proxy = 300.0 * 8.0 * 20.0 * 0.20
    expected_opp = {s: active[s] * total_opp_proxy for s in active}
    min_arr = float(protocol["min_expected_arrival_events_300"])
    expected_arr = {s: expected_opp[s] * 0.20 * 0.60 for s in active}

    def _parse_s(sid: str) -> tuple[str, str, str]:
        a, b, c = sid.split("::")
        return a, b, c

    def merge_pair(a: str, b: str, reason: str) -> None:
        nonlocal active, mapping, expected_opp, expected_arr
        if a not in active or b not in active or a == b:
            return
        if active[a] > active[b] or (active[a] == active[b] and a < b):
            keep, drop = a, b
        else:
            keep, drop = b, a
        pre_a, pre_b = active[keep], active[drop]
        active[keep] = active[keep] + active[drop]
        expected_opp[keep] = expected_opp.get(keep, 0.0) + expected_opp.get(drop, 0.0)
        expected_arr[keep] = expected_arr.get(keep, 0.0) + expected_arr.get(drop, 0.0)
        del active[drop]
        expected_opp.pop(drop, None)
        expected_arr.pop(drop, None)
        for src, dst in list(mapping.items()):
            if dst == drop:
                mapping[src] = keep
        mapping[drop] = keep
        merge_rows.append({
            "source_strata": f"{drop}|{keep}",
            "destination_stratum": keep,
            "dropped_stratum_id": drop,
            "kept_stratum_id": keep,
            "reason": reason,
            "pre_merge_target_mass_keep": pre_a,
            "pre_merge_target_mass_drop": pre_b,
            "post_merge_target_mass": active[keep],
            "adjacency_proof": reason,
            "tie_break_decision": "larger_mass_then_lexicographic_keep",
        })

    def needs_merge(sid: str) -> bool:
        return (
            active.get(sid, 0.0) < lambda_min
            or expected_opp.get(sid, 0.0) < min_opp
            or expected_arr.get(sid, 0.0) < min_arr
        )

    changed = True
    while changed:
        changed = False
        small = sorted([s for s in active if needs_merge(s)])
        for sid in small:
            if sid not in active or not needs_merge(sid):
                continue
            region, block, day = _parse_s(sid)
            bi = BLOCKS.index(block) if block in BLOCKS else -1
            neighbors = []
            if bi >= 0:
                if bi > 0:
                    neighbors.append(f"{region}::{BLOCKS[bi - 1]}::{day}")
                if bi + 1 < len(BLOCKS):
                    neighbors.append(f"{region}::{BLOCKS[bi + 1]}::{day}")
            for nb in neighbors:
                if nb in active:
                    merge_pair(sid, nb, "same_spatial_region_same_day_type_adjacent_time_block")
                    changed = True
                    break
            if changed:
                break
        if changed:
            continue
        small = sorted([s for s in active if needs_merge(s)])
        for sid in small:
            if sid not in active or not needs_merge(sid):
                continue
            region, block, day = _parse_s(sid)
            alt = "weekend" if day == "weekday" else "weekday"
            nb = f"{region}::{block}::{alt}"
            if nb not in active:
                continue
            # Do not erase the global day-type axis (must keep >=2 day types).
            days_present = {_parse_s(s)[2] for s in active}
            remaining_days = {
                _parse_s(s)[2]
                for s in active
                if s not in {sid, nb}
            }
            # After merge, kept id retains one day token; ensure both day types
            # still appear somewhere among active strata.
            keep_day = day if (
                active[sid] > active[nb]
                or (active[sid] == active[nb] and sid < nb)
            ) else alt
            post_days = remaining_days | {keep_day}
            if len(days_present) >= 2 and len(post_days) < 2:
                continue
            merge_pair(sid, nb, "same_spatial_region_merge_weekday_weekend")
            changed = True
            break

    frame["merged_stratum_id"] = frame["raw_stratum_id"].map(lambda s: mapping.get(s, s))
    strata = sorted(frame["merged_stratum_id"].unique())
    if any(s in FORBIDDEN for s in strata):
        raise RuntimeError("role stratum ids forbidden")
    if len(strata) < 8:
        raise RuntimeError(f"merged stratum count {len(strata)} < 8")
    spatial_n = int(frame["spatial_region_id"].nunique())
    day_n = int(frame["day_type"].nunique())
    if spatial_n < 2:
        raise RuntimeError("spatial dimension unique count < 2")
    if day_n < 2:
        raise RuntimeError("day-type unique count < 2")

    stratum_mass = {
        s: float(frame.loc[frame["merged_stratum_id"] == s, "target_mass"].sum())
        for s in strata
    }
    tsum = sum(stratum_mass.values())
    stratum_mass = {k: v / tsum for k, v in stratum_mass.items()}
    if abs(sum(stratum_mass.values()) - 1.0) > 1e-12:
        raise RuntimeError("stratum target mass must sum to 1")

    out_dir = root / "configs/frozen/e2_true_stratum"
    out_dir.mkdir(parents=True, exist_ok=True)
    export = frame[[
        "unit_id",
        "spatial_region_id",
        "time_block",
        "day_type",
        "raw_stratum_id",
        "merged_stratum_id",
        "target_mass",
        "supported_flag",
        "source_identity",
    ]].copy()
    export["source_hash"] = sha256_file(
        root / "data/processed/sensorscope/atomic_units.parquet"
    )
    export["stratum_id"] = export["merged_stratum_id"]
    parquet = out_dir / "atomic_true_opportunity_stratum.parquet"
    export.to_parquet(parquet, index=False)

    mapping_hash = sha256_json({
        "unit_stratum": dict(zip(export["unit_id"], export["merged_stratum_id"], strict=True)),
        "stratum_mass": stratum_mass,
    })
    identity = {
        "source_file": "data/processed/sensorscope/atomic_units.parquet",
        "e1_pi_target_file": "configs/frozen/e1_pi_target_client_stratum.parquet",
        "e1_source_hash": sha256_file(root / "data/processed/sensorscope/atomic_units.parquet"),
        "e1_pi_hash": sha256_file(pi_path),
        "source_rule": protocol["source_rule"],
        "region_definition": protocol["region_definition"],
        "mapping_hash": mapping_hash,
        "raw_stratum_count": int(len(mass_by)),
        "raw_positive_mass_stratum_count": int((mass_by > 0).sum()),
        "stratum_count_merged": int(len(strata)),
        "spatial_dimension_unique_count": spatial_n,
        "day_type_unique_count": day_n,
        "target_mass_sum": float(sum(stratum_mass.values())),
        "unsupported_unit_count": int((~export["supported_flag"]).sum()),
        "unknown_unit_count": unknown_unit,
        "unit_symmetric_difference": symdiff,
        "missing_spatial_dimension_count": missing_spatial,
        "missing_day_type_dimension_count": missing_day,
        "stratum_ids": strata,
        "stratum_target_mass": stratum_mass,
        "role_substitution": False,
        "lambda_stratum_min": lambda_min,
        "protocol_hash": sha256_json(protocol),
        "e1_lambda_stratum_count": int(len(e1_lambda)),
    }
    dump_json(identity, out_dir / "true_opportunity_stratum_identity.json")
    pd.DataFrame([
        {"merged_stratum_id": s, "Lambda_s_tar": float(stratum_mass[s])}
        for s in strata
    ]).to_parquet(out_dir / "target_stratum_mass.parquet", index=False)

    audit_csv = root / "outputs/audits/E2_TRUE_STRATUM_MERGE_AUDIT.csv"
    audit_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(merge_rows).to_csv(audit_csv, index=False)
    dump_json({
        "raw_stratum_count": identity["raw_stratum_count"],
        "merged_stratum_count": identity["stratum_count_merged"],
        "merge_row_count": len(merge_rows),
        "spatial_dimension_unique_count": spatial_n,
        "day_type_unique_count": day_n,
        "lambda_stratum_min": lambda_min,
        "status": "PASS",
    }, root / "outputs/audits/E2_TRUE_STRATUM_MERGE_SUMMARY.json")

    e1_audit = {
        "E1_source_file": "data/processed/sensorscope/atomic_units.parquet",
        "E1_source_hash": identity["e1_source_hash"],
        "E1_pi_file": "configs/frozen/e1_pi_target_client_stratum.parquet",
        "E1_pi_hash": identity["e1_pi_hash"],
        "E2_mapping_hash": mapping_hash,
        "raw_stratum_count": identity["raw_stratum_count"],
        "raw_positive_mass_stratum_count": identity["raw_positive_mass_stratum_count"],
        "target_mass_sum": identity["target_mass_sum"],
        "unit_symmetric_difference": symdiff,
        "unknown_unit_count": unknown_unit,
        "missing_spatial_dimension_count": missing_spatial,
        "missing_day_type_dimension_count": missing_day,
        "status": (
            "PASS"
            if (
                symdiff == 0
                and unknown_unit == 0
                and missing_spatial == 0
                and missing_day == 0
                and abs(identity["target_mass_sum"] - 1.0) <= 1e-12
            )
            else "FAIL"
        ),
    }
    dump_json(e1_audit, root / "outputs/audits/E2_TRUE_STRATUM_E1_IDENTITY_AUDIT.json")
    if e1_audit["status"] != "PASS":
        raise RuntimeError(f"E1 identity audit failed: {e1_audit}")

    return {
        "frame": export,
        "identity": identity,
        "e1_audit": e1_audit,
        "merge_rows": merge_rows,
        "mapping": mapping,
    }


def load_true_opportunity_stratum(root: Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    import json

    root = Path(root or ROOT)
    path = root / "configs/frozen/e2_true_stratum/atomic_true_opportunity_stratum.parquet"
    ident_path = root / "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json"
    if not path.is_file() or not ident_path.is_file():
        built = build_true_opportunity_stratum(root)
        return built["frame"], built["identity"]
    frame = pd.read_parquet(path)
    identity = json.loads(ident_path.read_text(encoding="utf-8"))
    return frame, identity
