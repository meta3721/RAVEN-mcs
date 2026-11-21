"""Dense legal candidate exposure: remove fixed-20 truncation."""
from __future__ import annotations

import ast
import json
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
PRIOR_CANDIDATE_CAP = 20
# Primary policy: all unique legal candidates in each source-range suffix.
# Cap is only a unified resource safety limit; None = no truncation.
DENSE_CANDIDATE_CAP: int | None = None
CLIENTS = 8
VALIDATION_SEEDS = (29101, 29102, 29103, 29104, 29105)


def _hash_subsample_legal(
    legal: pd.DataFrame,
    cap: int,
    *,
    client_id: str,
    window_id: int,
    source_start: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deterministic unbiased unit_id-hash subsample when exceeding unified cap."""
    if len(legal) <= cap:
        return legal, legal.iloc[0:0]
    scores = []
    for uid in legal["unit_id"].astype(str).tolist():
        h = sha256_json({
            "unit_id": uid,
            "client_id": client_id,
            "window_id": int(window_id),
            "source_start_index": int(source_start),
            "policy": "dense_legal_hash_subsample_v1",
        })
        scores.append(int(h[:16], 16))
    order = np.argsort(np.asarray(scores, dtype=np.uint64), kind="mergesort")
    keep_idx = np.sort(order[:cap])
    drop_idx = np.sort(order[cap:])
    return legal.iloc[keep_idx].reset_index(drop=True), legal.iloc[drop_idx].reset_index(drop=True)


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
    atomic = load_e1_atomic_target_weights(root)
    weight_map = {
        str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)
    }
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed = processed.loc[processed["unit_id"].astype(str).isin(supported)].copy()
    processed["unit_id"] = processed["unit_id"].astype(str)
    station_map = _station_to_client(root)
    processed["client_id"] = processed["unit_id"].map(
        lambda u: station_map.get(u.split("_", 1)[0])
    )
    processed["target_weight"] = processed["unit_id"].map(weight_map)
    processed["raw_stratum"] = processed["opportunity_stratum"].astype(str).map(
        lambda s: "::".join(s.split("::")[:3]) if "::" in s else s
    )
    pools = {}
    for cid, frame in processed.groupby("client_id", sort=True):
        pools[str(cid)] = frame.sort_values(["time_index", "unit_id"]).reset_index(drop=True)
    return {c: pools[c] for c in sorted(pools)[:CLIENTS]}


def audit_candidate_truncation(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    pools = load_client_pools(root)
    avail = []
    dropped_mass = 0.0
    dropped_count = 0
    affected = set()
    for cid, pool in pools.items():
        n = len(pool)
        # Prior construction: first-N slice of length 20 from each start.
        max_start = n - PRIOR_CANDIDATE_CAP
        for start in range(max(0, max_start + 1)):
            legal_all = pool.iloc[start:n]
            taken = pool.iloc[start: start + PRIOR_CANDIDATE_CAP]
            drop = legal_all.iloc[PRIOR_CANDIDATE_CAP:]
            avail.append(len(legal_all))
            dropped_count += len(drop)
            dropped_mass += float(drop["target_weight"].sum())
            affected.update(drop["raw_stratum"].astype(str).tolist())
    # Code locations
    locs = [
        "src/raven_mcs/e2/legal_horizon/schedule100.py:CANDIDATE_SIZE=20",
        "src/raven_mcs/e2/legal_horizon/schedule100.py:end=start+candidate_size",
        "scripts/prepare_e2_legal_horizon_and_balanced_calibration.py:max_risk_set=20",
    ]
    payload = {
        "truncation_present": True,
        "configured_cap": PRIOR_CANDIDATE_CAP,
        "truncation_type": "fixed_size_first_N_unit_slice",
        "available_candidate_count_distribution": {
            "mean": float(np.mean(avail)) if avail else 0.0,
            "min": int(min(avail)) if avail else 0,
            "median": float(np.median(avail)) if avail else 0.0,
            "max": int(max(avail)) if avail else 0,
        },
        "dropped_legal_candidate_count_over_all_starts": int(dropped_count),
        "dropped_target_mass_over_all_starts": float(dropped_mass),
        "affected_strata_count": int(len(affected)),
        "source_code_locations": locs,
        "status": "PASS",
    }
    dump_json(payload, root / "outputs/audits/E2_CANDIDATE_TRUNCATION_AUDIT.json")
    return payload


def build_dense_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
    dense_cap: int | None = DENSE_CANDIDATE_CAP,
) -> dict[str, Any]:
    """Keep unique spaced starts; use full legal suffix (no fixed-20 cut)."""
    root = Path(root or ROOT)
    pools = load_client_pools(root)
    clients = sorted(pools)[:CLIENTS]
    # Preserve legal-100 start construction (same unique spaced starts as prior
    # round); only expand forward width beyond the old fixed-20 truncation.
    starts_by_client: dict[str, list[int]] = {}
    for cid in clients:
        n = len(pools[cid])
        max_start = n - PRIOR_CANDIDATE_CAP
        if max_start < NUM_WINDOWS - 1:
            raise RuntimeError(f"insufficient pool for legal starts: {cid}")
        starts_by_client[cid] = unique_spaced_starts(max_start, NUM_WINDOWS, seed)

    rows: list[dict[str, Any]] = []
    window_payloads: list[str] = []
    seen_ranges: dict[str, set[str]] = {c: set() for c in clients}
    dup_index = 0
    dropped_by_cap = 0
    dropped_mass_by_cap = 0.0
    cand_counts: list[int] = []
    prior_counts: list[int] = []

    for window_id in range(NUM_WINDOWS):
        chunk = []
        for ci, cid in enumerate(clients):
            pool = pools[cid]
            n = len(pool)
            start = int(starts_by_client[cid][window_id])
            # Dense policy: full legal suffix; optional unified cap via hash subsample.
            legal = pool.iloc[start:n].reset_index(drop=True)
            uncapped_n = len(legal)
            if dense_cap is None:
                take, dropped = legal, legal.iloc[0:0]
            else:
                take, dropped = _hash_subsample_legal(
                    legal, int(dense_cap),
                    client_id=cid, window_id=window_id, source_start=start,
                )
            if len(dropped):
                dropped_by_cap += len(dropped)
                dropped_mass_by_cap += float(dropped["target_weight"].sum())
            unit_ids = take["unit_id"].astype(str).tolist()
            if len(unit_ids) != len(set(unit_ids)):
                raise RuntimeError("duplicate unit within client-window")
            masses = take["target_weight"].astype(float).tolist()
            times = take["time_index"].astype(int).tolist()
            strata = take["raw_stratum"].astype(str).tolist()
            t0, t1 = (min(times), max(times)) if times else (0, 0)
            prior_counts.append(min(PRIOR_CANDIDATE_CAP, max(0, n - start)))
            cand_counts.append(len(unit_ids))
            # Source range identity remains the legal start; end is pool end (legal suffix).
            source_end_index = n - 1
            index_range_hash = sha256_json({
                "client_id": cid,
                "source_start_index": start,
                "source_end_index": source_end_index,
                "legal_suffix_len": uncapped_n,
                "selected_candidate_count": len(unit_ids),
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
                "start_time": float(window_id),
                "end_time": float(window_id + 1),
                "client_id": cid,
                "candidate_unit_ids": unit_ids,
                "candidate_event_mass": masses,
                "candidate_raw_strata": strata,
                "attempt_eligible": True,
                "source_start_index": int(start),
                "source_end_index": int(source_end_index),
                "source_timestamp_min": int(t0),
                "source_timestamp_max": int(t1),
                "chronological_source_range": f"time_index[{t0},{t1}]",
                "source_index_range_hash": index_range_hash,
                "candidate_content_hash": sha256_json({
                    "client_id": cid, "unit_ids": unit_ids, "masses": masses,
                }),
                "schedule_uniform": draw,
                "payload_hash": sha256_json(payload),
                "dense_cap": dense_cap,
                "prior_cap": PRIOR_CANDIDATE_CAP,
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
            if prev_si >= 0 and si <= prev_si:
                mono += 1
            if prev_t0 >= 0 and t0 < prev_t0:
                wraparound += 1
            prev_si, prev_t0 = si, t0

    mod = _modulo_count(root / "src/raven_mcs/e2/hard_variance/dense_exposure.py")
    audit = {
        "seed": int(seed),
        "num_windows": NUM_WINDOWS,
        "dense_candidate_cap": dense_cap,
        "prior_candidate_cap": PRIOR_CANDIDATE_CAP,
        "avg_candidates_before": float(np.mean(prior_counts)),
        "avg_candidates_after": float(np.mean(cand_counts)),
        "min_candidates_after": int(min(cand_counts)),
        "max_candidates_after": int(max(cand_counts)),
        "dropped_legal_candidate_count_by_cap": int(dropped_by_cap),
        "dropped_legal_candidate_mass_by_cap": float(dropped_mass_by_cap),
        "source_reuse_count": int(dup_index),
        "duplicate_source_index_range_count": int(dup_index),
        "wraparound_count": int(wraparound),
        "monotonic_violation_count": int(mono),
        "modulo_operator_usage_count": int(mod),
        "unique_window_payload_ratio": len(set(window_payloads)) / max(len(window_payloads), 1),
        "status": (
            "PASS"
            if dup_index == 0 and wraparound == 0 and mono == 0 and mod == 0
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
            "dense_cap": dense_cap,
            "window_payloads": window_payloads,
        }),
        "starts_by_client": starts_by_client,
    }


def audit_dense_exposure(
    schedules: dict[int, dict[str, Any]],
    root: Path | None = None,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    total_cw = 0
    unsupported = 0
    dup_unit = 0
    reuse = 0
    before = []
    after = []
    dropped_count = 0
    dropped_mass = 0.0
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    for sched in schedules.values():
        reuse += int(sched["audit"]["source_reuse_count"])
        before.append(sched["audit"]["avg_candidates_before"])
        after.append(sched["audit"]["avg_candidates_after"])
        dropped_count += int(sched["audit"]["dropped_legal_candidate_count_by_cap"])
        dropped_mass += float(sched["audit"]["dropped_legal_candidate_mass_by_cap"])
        for r in sched["rows"]:
            total_cw += 1
            uids = r["candidate_unit_ids"]
            if len(uids) != len(set(uids)):
                dup_unit += 1
            unsupported += sum(1 for u in uids if u not in supported)
    payload = {
        "total_client_windows": int(total_cw),
        "source_reuse_count": int(reuse),
        "duplicate_unit_within_client_window_count": int(dup_unit),
        "unsupported_candidate_count": int(unsupported),
        "average_candidates_before": float(np.mean(before)),
        "average_candidates_after": float(np.mean(after)),
        "dropped_legal_candidate_count": int(dropped_count),
        "dropped_legal_candidate_mass": float(dropped_mass),
        "dense_candidate_cap": DENSE_CANDIDATE_CAP,
        "unified_resource_cap_policy": (
            "deterministic_unit_id_hash_subsample_when_exceeding_cap"
            if DENSE_CANDIDATE_CAP is not None
            else "full_legal_suffix_no_cap"
        ),
        "status": (
            "PASS"
            if (
                reuse == 0
                and dup_unit == 0
                and unsupported == 0
                and (dropped_count == 0 or DENSE_CANDIDATE_CAP is not None)
            )
            else "FAIL"
        ),
    }
    dump_json(payload, root / "outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json")
    return payload
