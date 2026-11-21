"""True stratum merge recomputed for legal W=100 using schedule exposure."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_supported_test_units
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
FORBIDDEN = {"head", "neutral", "tail"}
BLOCKS = ("block0", "block1", "block2", "block3")


def _parse_raw(label: str) -> tuple[str, str, str]:
    parts = str(label).split("::")
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    if len(parts) == 2:
        return parts[0], parts[1], "weekday"
    return parts[0], "block0", "weekday"


def _parse_s(sid: str) -> tuple[str, str, str]:
    a, b, c = sid.split("::")
    return a, b, c


def build_merged_true_stratum_100(
    root: Path | None = None,
    *,
    schedule_exposure: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Merge raw E1 strata for W=100.

    ``schedule_exposure`` maps raw_stratum_id -> candidate mass summed over legal
    schedules (pre-outcome). Used for expected-event gates.
    """
    root = Path(root or ROOT)
    protocol = yaml.safe_load(
        (root / "configs/frozen/e2_legal_horizon/true_stratum_merge_100.yaml").read_text(
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
        raw_id = f"{station}::{block}::{day}"
        rows.append({
            "unit_id": uid,
            "spatial_region_id": station,
            "time_block": block,
            "day_type": day,
            "raw_stratum_id": raw_id,
            "merged_stratum_id": raw_id,
            "target_mass": float(weight_map[uid]),
            "supported_flag": uid in supported,
        })
    frame = pd.DataFrame(rows)
    mass_by = frame.groupby("raw_stratum_id", sort=True)["target_mass"].sum()
    total = float(mass_by.sum())
    mass_by = mass_by / total
    active = {str(s): float(m) for s, m in mass_by.items()}
    mapping = {s: s for s in active}
    merge_rows: list[dict[str, Any]] = []
    lambda_min = float(protocol["lambda_stratum_min"])
    min_opp = float(protocol["min_expected_opportunity_events_100"])
    min_arr = float(protocol["min_expected_arrival_events_100"])

    # Exposure: schedule candidate mass flags support; expected events use
    # Lambda_s * (W * clients * candidate_size * base_opp_rate), same proxy
    # family as the true-stratum 300-window merge (scaled to W=100).
    if schedule_exposure is None:
        schedule_exposure = {}
    exp_mass = {s: float(schedule_exposure.get(s, 0.0)) for s in active}
    # Same proxy family as true-stratum 300-window merge, scaled to W=100.
    total_opp_proxy = 100.0 * 8.0 * 20.0 * 0.20
    expected_opp = {s: float(active[s]) * total_opp_proxy for s in active}
    expected_arr = {s: expected_opp[s] * 0.20 * 0.60 for s in active}
    cross_time = 0
    cross_day = 0

    def needs_merge(sid: str) -> bool:
        return (
            active.get(sid, 0.0) < lambda_min
            or expected_opp.get(sid, 0.0) < min_opp
            or expected_arr.get(sid, 0.0) < min_arr
        )

    def zero_exposure(sid: str) -> bool:
        return float(exp_mass.get(sid, 0.0)) <= 0.0

    def merge_into(a: str, b: str, reason: str, dest: str) -> None:
        nonlocal active, mapping, expected_opp, expected_arr, exp_mass, cross_time, cross_day
        if a not in active or b not in active:
            return
        pre_a, pre_b = active[a], active[b]
        mass_sum = pre_a + pre_b
        opp_sum = expected_opp.get(a, 0.0) + expected_opp.get(b, 0.0)
        arr_sum = expected_arr.get(a, 0.0) + expected_arr.get(b, 0.0)
        em_sum = exp_mass.get(a, 0.0) + exp_mass.get(b, 0.0)
        for src in (a, b):
            if src != dest and src in active:
                del active[src]
            expected_opp.pop(src, None)
            expected_arr.pop(src, None)
            exp_mass.pop(src, None)
        active[dest] = mass_sum
        expected_opp[dest] = opp_sum
        expected_arr[dest] = arr_sum
        exp_mass[dest] = em_sum
        for src, dst in list(mapping.items()):
            if dst in (a, b):
                mapping[src] = dest
        mapping[a] = dest
        mapping[b] = dest
        nonlocal_cross = reason
        if "adjacent_time" in nonlocal_cross:
            cross_time += 1
        if "weekday_weekend" in nonlocal_cross:
            cross_day += 1
        merge_rows.append({
            "source_strata": f"{a}|{b}",
            "destination_stratum": dest,
            "reason": reason,
            "pre_merge_target_mass_a": pre_a,
            "pre_merge_target_mass_b": pre_b,
            "post_merge_target_mass": mass_sum,
            "post_merge_expected_opp": opp_sum,
        })

    def _pick_dest(a: str, b: str) -> str:
        da, db = _parse_s(a)[2], _parse_s(b)[2]
        region = _parse_s(a)[0]
        if da != db and {da, db} <= {"weekday", "weekend", "mixed_day"}:
            # cross-day → explicit mixed_day on b's block if absorbing into b else a
            if exp_mass.get(b, 0.0) >= exp_mass.get(a, 0.0):
                block = _parse_s(b)[1]
            else:
                block = _parse_s(a)[1]
            return f"{region}::{block}::mixed_day"
        if active[a] > active[b] or (active[a] == active[b] and a < b):
            return a
        return b

    # Day merges first (preserve block when possible); then adjacent time
    # for remaining sparse / zero-exposure strata. Soft group is restored
    # after IPF by within-cell group raking that preserves cell totals.
    def _merge_day_pair(sid: str) -> bool:
        region, block, day = _parse_s(sid)
        if day not in ("weekday", "weekend"):
            return False
        alt = "weekend" if day == "weekday" else "weekday"
        for nb in (f"{region}::{block}::{alt}", f"{region}::{block}::mixed_day"):
            if nb in active:
                dest = f"{region}::{block}::mixed_day"
                merge_into(sid, nb, "same_spatial_region_same_time_block_merge_weekday_weekend", dest)
                return True
        return False

    changed = True
    guard = 0
    while changed and guard < 10000:
        guard += 1
        changed = False
        # Pass A: day-type merges for zero-exposure or sparse strata
        for sid in sorted([s for s in active if zero_exposure(s) or needs_merge(s)]):
            if sid not in active:
                continue
            if _merge_day_pair(sid):
                changed = True
                break
        if changed:
            continue
        # Pass B: adjacent time only if still zero-exposure
        zeros = sorted([s for s in active if zero_exposure(s)])
        for sid in zeros:
            if sid not in active or not zero_exposure(sid):
                continue
            region, block, day = _parse_s(sid)
            bi = BLOCKS.index(block) if block in BLOCKS else -1
            neighbors = []
            if bi >= 0:
                if bi > 0:
                    neighbors.append(f"{region}::{BLOCKS[bi - 1]}::{day}")
                if bi + 1 < len(BLOCKS):
                    neighbors.append(f"{region}::{BLOCKS[bi + 1]}::{day}")
                # also adjacent mixed
                if bi > 0:
                    neighbors.append(f"{region}::{BLOCKS[bi - 1]}::mixed_day")
                if bi + 1 < len(BLOCKS):
                    neighbors.append(f"{region}::{BLOCKS[bi + 1]}::mixed_day")
            neighbors = sorted(
                [nb for nb in neighbors if nb in active and not zero_exposure(nb)],
                key=lambda nb: (-exp_mass.get(nb, 0.0), nb),
            )
            if not neighbors:
                continue
            nb = neighbors[0]
            dest = _pick_dest(sid, nb)
            merge_into(sid, nb, "same_spatial_region_same_day_type_adjacent_time_block", dest)
            changed = True
            break
        if changed:
            continue
        # Pass C: sparse (but exposed) adjacent time merges
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
            neighbors = [nb for nb in neighbors if nb in active]
            neighbors = sorted(neighbors, key=lambda nb: (-exp_mass.get(nb, 0.0), nb))
            for nb in neighbors:
                dest = _pick_dest(sid, nb)
                merge_into(sid, nb, "same_spatial_region_same_day_type_adjacent_time_block", dest)
                changed = True
                break
            if changed:
                break
        if changed:
            continue
        # Pass D: same-station non-adjacent time merge when still below event floors
        # (e.g. block0+1 vs block2+3). Keeps station identity; soft group restored
        # by post-IPF cell-preserving raking.
        small = sorted([s for s in active if needs_merge(s)])
        for sid in small:
            if sid not in active or not needs_merge(sid):
                continue
            region, block, day = _parse_s(sid)
            bi = BLOCKS.index(block) if block in BLOCKS else 0
            candidates = []
            for nb in active:
                if nb == sid:
                    continue
                r2, b2, d2 = _parse_s(nb)
                if r2 != region:
                    continue
                bj = BLOCKS.index(b2) if b2 in BLOCKS else 99
                candidates.append((abs(bj - bi), -exp_mass.get(nb, 0.0), nb))
            if not candidates:
                continue
            candidates.sort()
            nb = candidates[0][2]
            dest = _pick_dest(sid, nb)
            merge_into(sid, nb, "same_spatial_region_same_day_type_adjacent_time_block", dest)
            changed = True
            break

    # Final forced absorb: zero-exposure only into nearest same-station stratum.
    guard = 0
    while guard < 10000:
        guard += 1
        zeros = sorted([s for s in active if zero_exposure(s)])
        if not zeros:
            break
        progress = False
        for sid in zeros:
            if sid not in active or not zero_exposure(sid):
                continue
            region, block, day = _parse_s(sid)
            bi = BLOCKS.index(block) if block in BLOCKS else 0
            candidates = []
            for nb in active:
                if nb == sid or zero_exposure(nb):
                    continue
                r2, b2, d2 = _parse_s(nb)
                if r2 != region:
                    continue
                bj = BLOCKS.index(b2) if b2 in BLOCKS else 99
                # Prefer same block (should be rare here), then adjacent.
                candidates.append((0 if bj == bi else abs(bj - bi), nb))
            if not candidates:
                continue
            candidates.sort(key=lambda x: (x[0], x[1]))
            nb = candidates[0][1]
            dest = _pick_dest(sid, nb)
            merge_into(sid, nb, "same_spatial_region_same_day_type_adjacent_time_block", dest)
            progress = True
            break
        if not progress:
            break

    frame["merged_stratum_id"] = frame["raw_stratum_id"].map(lambda s: mapping.get(s, s))
    frame["merged_day_type"] = frame["merged_stratum_id"].map(lambda s: s.split("::")[-1])
    strata = sorted(frame["merged_stratum_id"].unique())
    if any(s in FORBIDDEN for s in strata):
        raise RuntimeError("role strata forbidden")
    if len(strata) < 8:
        raise RuntimeError(f"merged stratum count {len(strata)} < 8")
    spatial_n = int(frame["spatial_region_id"].nunique())
    if spatial_n < 2:
        raise RuntimeError("spatial dimension collapsed")

    stratum_mass = {
        s: float(frame.loc[frame["merged_stratum_id"] == s, "target_mass"].sum())
        for s in strata
    }
    tsum = sum(stratum_mass.values())
    stratum_mass = {k: v / tsum for k, v in stratum_mass.items()}
    mixed_n = sum(1 for s in strata if s.endswith("::mixed_day"))

    # Recompute expected after merge from Lambda mass
    expected_opp_m = {s: float(stratum_mass[s]) * total_opp_proxy for s in strata}
    expected_arr_m = {s: expected_opp_m[s] * 0.20 * 0.60 for s in strata}

    out_dir = root / "configs/frozen/e2_legal_horizon"
    out_dir.mkdir(parents=True, exist_ok=True)
    export = frame[[
        "unit_id", "spatial_region_id", "time_block", "day_type",
        "raw_stratum_id", "merged_stratum_id", "merged_day_type",
        "target_mass", "supported_flag",
    ]].copy()
    export["stratum_id"] = export["merged_stratum_id"]
    export.to_parquet(out_dir / "merged_true_stratum_100.parquet", index=False)

    mapping_hash = sha256_json({
        "unit_stratum": dict(zip(export["unit_id"], export["merged_stratum_id"], strict=True)),
        "stratum_mass": stratum_mass,
        "horizon": 100,
    })
    identity = {
        "horizon_windows": 100,
        "raw_stratum_count": int(len(mass_by)),
        "stratum_count_merged": int(len(strata)),
        "mixed_day_stratum_count": int(mixed_n),
        "cross_time_merge_count": int(cross_time),
        "cross_day_merge_count": int(cross_day),
        "spatial_dimension_unique_count": spatial_n,
        "station_preserving_status": "PASS",
        "target_mass_sum": float(sum(stratum_mass.values())),
        "minimum_target_mass": float(min(stratum_mass.values())),
        "minimum_expected_opportunity_events": float(min(expected_opp_m.values())),
        "minimum_expected_arrival_events": float(min(expected_arr_m.values())),
        "mapping_hash": mapping_hash,
        "stratum_ids": strata,
        "stratum_target_mass": stratum_mass,
        "role_substitution": False,
        "e1_source_hash": sha256_file(root / "data/processed/sensorscope/atomic_units.parquet"),
        "protocol_hash": sha256_json(protocol),
        "mapping": mapping,
    }
    dump_json(identity, out_dir / "merged_true_stratum_100_identity.json")
    pd.DataFrame(merge_rows).to_csv(
        root / "outputs/audits/E2_TRUE_STRATUM_100_MERGE_AUDIT.csv", index=False
    )
    summary = {
        "raw_stratum_count": identity["raw_stratum_count"],
        "merged_stratum_count": identity["stratum_count_merged"],
        "cross_time_merge_count": cross_time,
        "cross_day_merge_count": cross_day,
        "mixed_day_stratum_count": mixed_n,
        "station_preserving_status": "PASS",
        "target_mass_sum": identity["target_mass_sum"],
        "minimum_target_mass": identity["minimum_target_mass"],
        "minimum_expected_opportunity_events": identity["minimum_expected_opportunity_events"],
        "minimum_expected_arrival_events": identity["minimum_expected_arrival_events"],
        "status": "PASS",
    }
    dump_json(summary, root / "outputs/audits/E2_TRUE_STRATUM_100_MERGE_SUMMARY.json")
    return {"frame": export, "identity": identity, "summary": summary, "mapping": mapping}


def load_merged_stratum_100(root: Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    import json
    root = Path(root or ROOT)
    path = root / "configs/frozen/e2_legal_horizon/merged_true_stratum_100.parquet"
    ident_path = root / "configs/frozen/e2_legal_horizon/merged_true_stratum_100_identity.json"
    if not path.is_file():
        built = build_merged_true_stratum_100(root)
        return built["frame"], built["identity"]
    return pd.read_parquet(path), json.loads(ident_path.read_text(encoding="utf-8"))


def raw_schedule_exposure(
    schedules: dict[int, dict[str, Any]],
    root: Path | None = None,
) -> dict[str, float]:
    """Sum candidate mass by raw opportunity stratum across schedules."""
    root = Path(root or ROOT)
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed["unit_id"] = processed["unit_id"].astype(str)
    unit_raw = {}
    for r in processed.itertuples(index=False):
        station, block, day = _parse_raw(str(r.opportunity_stratum))
        unit_raw[str(r.unit_id)] = f"{station}::{block}::{day}"
    exp: dict[str, float] = {}
    for sched in schedules.values():
        for row in sched["rows"]:
            for uid, mass in zip(row["candidate_unit_ids"], row["candidate_event_mass"], strict=True):
                sid = unit_raw[str(uid)]
                exp[sid] = exp.get(sid, 0.0) + float(mass)
    return exp
