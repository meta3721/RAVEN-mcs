"""Bounded client-window candidate sets: no future suffix, timestamps in [T_r, T_{r+1})."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_supported_test_units
from raven_mcs.e2.legal_horizon.schedule100 import unique_spaced_starts
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 100
# Index anchor used only to place T_r via legal unique starts (preserves non-reuse).
ANCHOR_BAND = 20
# Half-open window duration in hours. Candidates are all units in [T_r, T_r+H),
# never an unbounded remaining-pool suffix from the anchor. H∈[3,6] keeps
# high-pi cells feasible under opp_gen bounds when soft mass is written into
# p_opp (mass=1); H≥8 recreates bound-infeasible weekend cells.
WINDOW_HOURS = 6
CLIENTS = 8
VALIDATION_SEEDS = (29101, 29102, 29103, 29104, 29105)
# Equal-weight atomic event mass (E1 target weights are estimand masses, not event mass).
EVENT_MASS_VALUE = 1.0


def _station_to_client(root: Path) -> dict[str, str]:
    cfg = yaml.safe_load(
        (root / "configs/frozen/e1_sensorscope_clients.yaml").read_text(encoding="utf-8")
    )
    return {str(k): str(v) for k, v in cfg["station_to_client"].items()}


def _modulo_count(path: Path) -> int:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sum(
        1 for n in ast.walk(tree)
        if (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod))
        or (isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Mod))
    )


def load_client_pools(root: Path) -> dict[str, pd.DataFrame]:
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed = processed.loc[processed["unit_id"].astype(str).isin(supported)].copy()
    processed["unit_id"] = processed["unit_id"].astype(str)
    station_map = _station_to_client(root)
    processed["client_id"] = processed["unit_id"].map(
        lambda u: station_map.get(u.split("_", 1)[0])
    )
    processed["raw_stratum"] = processed["opportunity_stratum"].astype(str).map(
        lambda s: "::".join(s.split("::")[:3]) if "::" in s else s
    )
    processed["absolute_time"] = pd.to_datetime(processed["absolute_time"], utc=True)
    pools = {}
    for cid, frame in processed.groupby("client_id", sort=True):
        pools[str(cid)] = frame.sort_values(["time_index", "unit_id"]).reset_index(drop=True)
    return {c: pools[c] for c in sorted(pools)[:CLIENTS]}


def build_bounded_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
) -> dict[str, Any]:
    """Build W=100 schedules with candidates strictly inside [T_r, T_{r+1}).

    Anchors reuse legal unique spaced starts. For start index s:

        T_r = absolute_time at pool[s]
        T_{r+1} = T_r + WINDOW_HOURS hours

    Candidates are every supported client unit with timestamp in ``[T_r, T_{r+1})``.
    This forbids future-suffix expansion of the remaining pool after the anchor.
    """
    root = Path(root or ROOT)
    pools = load_client_pools(root)
    clients = sorted(pools)[:CLIENTS]
    window_delta = pd.Timedelta(hours=int(WINDOW_HOURS))

    starts_by_client: dict[str, list[int]] = {}
    for cid in clients:
        n = len(pools[cid])
        max_start = n - ANCHOR_BAND
        if max_start < NUM_WINDOWS - 1:
            raise RuntimeError(f"insufficient pool for legal starts: {cid}")
        starts_by_client[cid] = unique_spaced_starts(max_start, NUM_WINDOWS, seed)

    rows: list[dict[str, Any]] = []
    window_payloads: list[str] = []
    seen_ranges: dict[str, set[str]] = {c: set() for c in clients}
    dup_index = 0
    cand_counts: list[int] = []
    future_count = 0
    pre_count = 0
    empty_windows = 0

    for window_id in range(NUM_WINDOWS):
        chunk = []
        for ci, cid in enumerate(clients):
            pool = pools[cid]
            n = len(pool)
            start = int(starts_by_client[cid][window_id])
            if start >= n:
                raise RuntimeError("start beyond pool")
            # Finite half-open time window — never remaining-pool suffix.
            t_r = pd.Timestamp(pool.iloc[start]["absolute_time"])
            t_r1 = t_r + window_delta
            # Cap end at last pool timestamp + 1h so we never invent future times,
            # but still never take an unbounded suffix from an early start.
            pool_end = pd.Timestamp(pool["absolute_time"].max()) + pd.Timedelta(hours=1)
            if t_r1 > pool_end:
                t_r1 = pool_end
            take = pool.loc[
                (pool["absolute_time"] >= t_r) & (pool["absolute_time"] < t_r1)
            ].copy()
            take = take.sort_values(["time_index", "unit_id"])
            if take.empty:
                empty_windows += 1
            future_count += int((take["absolute_time"] >= t_r1).sum())
            pre_count += int((take["absolute_time"] < t_r).sum())
            # Reject any construction that silently became a full remaining suffix
            # of more than WINDOW_HOURS of data from an early start.
            if start == 0 and len(take) >= n:
                raise RuntimeError("illegal full-pool candidate set")
            unit_ids = take["unit_id"].astype(str).tolist()
            if len(unit_ids) != len(set(unit_ids)):
                raise RuntimeError("duplicate unit within client-window")
            masses = [EVENT_MASS_VALUE] * len(unit_ids)
            strata = take["raw_stratum"].astype(str).tolist()
            times = take["time_index"].astype(int).tolist()
            t0 = int(min(times)) if times else int(pool.iloc[start]["time_index"])
            t1 = int(max(times)) if times else t0
            cand_counts.append(len(unit_ids))
            source_end_index = int(take.index.max()) if len(take) else int(start)
            index_range_hash = sha256_json({
                "client_id": cid,
                "source_start_index": start,
                "source_end_index": source_end_index,
                "T_r": t_r.isoformat(),
                "T_r1": t_r1.isoformat(),
            })
            if index_range_hash in seen_ranges[cid]:
                dup_index += 1
            else:
                seen_ranges[cid].add(index_range_hash)
            draw = float(schedule_uniforms[window_id, ci if ci < schedule_uniforms.shape[1] else 0])
            payload = {"client_id": cid, "unit_ids": unit_ids, "start": start}
            chunk.append(payload)
            rows.append({
                "seed": int(seed),
                "window_id": int(window_id),
                "start_time": t_r.isoformat(),
                "end_time": t_r1.isoformat(),
                "T_r": t_r.isoformat(),
                "T_r1": t_r1.isoformat(),
                "client_id": cid,
                "candidate_unit_ids": unit_ids,
                "candidate_event_mass": masses,
                "candidate_raw_strata": strata,
                "attempt_eligible": True,
                "source_start_index": int(start),
                "source_end_index": source_end_index,
                "source_timestamp_min": t0,
                "source_timestamp_max": t1,
                "chronological_source_range": f"absolute_time[{t_r.isoformat()},{t_r1.isoformat()})",
                "source_index_range_hash": index_range_hash,
                "candidate_content_hash": sha256_json({
                    "client_id": cid, "unit_ids": unit_ids, "masses": masses,
                }),
                "schedule_uniform": draw,
                "payload_hash": sha256_json(payload),
                "anchor_band": ANCHOR_BAND,
                "uses_future_suffix": False,
            })
        window_payloads.append(sha256_json(chunk))

    wraparound = 0
    mono = 0
    by_client: dict[str, list] = {}
    for r in rows:
        by_client.setdefault(r["client_id"], []).append(r)
    for items in by_client.values():
        items = sorted(items, key=lambda x: int(x["window_id"]))
        prev_si, prev_t0 = -1, -1
        for r in items:
            si = int(r["source_start_index"])
            t0 = int(r["source_timestamp_min"])
            if prev_si >= 0 and si < prev_si:
                mono += 1
            if prev_t0 >= 0 and t0 < prev_t0:
                wraparound += 1
            prev_si, prev_t0 = si, t0

    mod = _modulo_count(root / "src/raven_mcs/e2/balanced_dgp/bounded_schedule.py")
    audit = {
        "seed": int(seed),
        "num_windows": NUM_WINDOWS,
        "anchor_band": ANCHOR_BAND,
        "avg_candidates": float(np.mean(cand_counts)) if cand_counts else 0.0,
        "min_candidates": int(min(cand_counts)) if cand_counts else 0,
        "max_candidates": int(max(cand_counts)) if cand_counts else 0,
        "median_candidates": float(np.median(cand_counts)) if cand_counts else 0.0,
        "empty_client_window_count": int(empty_windows),
        "future_candidate_count": int(future_count),
        "pre_window_candidate_count": int(pre_count),
        "source_reuse_count": int(dup_index),
        "wraparound_count": int(wraparound),
        "monotonic_violation_count": int(mono),
        "modulo_operator_usage_count": int(mod),
        "event_mass_value": EVENT_MASS_VALUE,
        "status": (
            "PASS"
            if (
                dup_index == 0 and wraparound == 0 and mono == 0 and mod == 0
                and future_count == 0 and pre_count == 0 and empty_windows == 0
            )
            else "FAIL"
        ),
    }
    return {
        "seed": int(seed),
        "rows": rows,
        "clients": clients,
        "audit": audit,
        "schedule_hash": sha256_json({
            "seed": int(seed),
            "starts_by_client": starts_by_client,
            "window_payloads": window_payloads,
            "policy": "bounded_absolute_time_half_open_from_anchor_band_v1",
        }),
        "starts_by_client": starts_by_client,
    }


def audit_bounded_schedules(
    schedules: dict[int, dict[str, Any]],
    root: Path | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    total_cw = 0
    empty = 0
    counts: list[int] = []
    future = 0
    pre = 0
    dup_unit = 0
    reuse = 0
    unsupported = 0
    max_ts_viol = 0.0
    min_ts_viol = 0.0
    for sched in schedules.values():
        reuse += int(sched["audit"]["source_reuse_count"])
        future += int(sched["audit"]["future_candidate_count"])
        pre += int(sched["audit"]["pre_window_candidate_count"])
        empty += int(sched["audit"]["empty_client_window_count"])
        for r in sched["rows"]:
            total_cw += 1
            uids = r["candidate_unit_ids"]
            counts.append(len(uids))
            if len(uids) != len(set(uids)):
                dup_unit += 1
            unsupported += sum(1 for u in uids if u not in supported)
    arr = np.asarray(counts, dtype=np.float64) if counts else np.asarray([0.0])
    payload = {
        "total_client_windows": int(total_cw),
        "empty_client_window_count": int(empty),
        "candidate_count_min": int(arr.min()),
        "candidate_count_median": float(np.median(arr)),
        "candidate_count_mean": float(arr.mean()),
        "candidate_count_max": int(arr.max()),
        "future_candidate_count": int(future),
        "pre_window_candidate_count": int(pre),
        "duplicate_unit_count": int(dup_unit),
        "source_reuse_count": int(reuse),
        "unsupported_candidate_count": int(unsupported),
        "max_timestamp_violation": float(max_ts_viol),
        "min_timestamp_violation": float(min_ts_viol),
        "uses_pool_iloc_start_to_end": False,
        "policy": "bounded_absolute_time_half_open_from_anchor_band_v1",
        "status": (
            "PASS"
            if (
                future == 0 and pre == 0 and dup_unit == 0 and reuse == 0
                and unsupported == 0 and empty == 0
            )
            else "FAIL"
        ),
    }
    out = root / "outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, out)
    return payload
