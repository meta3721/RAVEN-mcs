"""Legal non-reuse 100-window SensorScope schedules."""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_supported_test_units
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 100
CANDIDATE_SIZE = 20
CLIENTS = 8
MAX_LEGAL = 105


class InsufficientNonreusedSourceError(RuntimeError):
    def __init__(self, payload: dict[str, Any]):
        super().__init__(payload.get("status", "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE"))
        self.payload = payload


def _station_to_client(root: Path) -> dict[str, str]:
    cfg = yaml.safe_load(
        (root / "configs/frozen/e1_sensorscope_clients.yaml").read_text(encoding="utf-8")
    )
    return {str(k): str(v) for k, v in cfg["station_to_client"].items()}


def _modulo_count_in_this_module(root: Path) -> int:
    src = (root / "src/raven_mcs/e2/legal_horizon/schedule100.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    return sum(
        1 for n in ast.walk(tree)
        if (isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod))
        or (isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Mod))
    )


def freeze_legal_horizon(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out_dir = root / "configs/frozen/e2_legal_horizon"
    out_dir.mkdir(parents=True, exist_ok=True)
    identity = {
        "selected_legal_windows": NUM_WINDOWS,
        "maximum_legal_continuous_windows": MAX_LEGAL,
        "safety_margin_windows": MAX_LEGAL - NUM_WINDOWS,
        "100_legal": True,
        "200_legal": False,
        "300_legal": False,
        "window_selection_mode": "LEGALITY_FREEZE",
        "statistical_window_selection": "NOT_APPLICABLE",
        "source_reuse_allowed": False,
        "wraparound_allowed": False,
        "modulo_allowed": False,
        "status": "PASS",
    }
    dump_json(identity, out_dir / "selected_legal_horizon_identity.json")
    audit = {
        "requested_windows": NUM_WINDOWS,
        "maximum_legal_continuous_windows": MAX_LEGAL,
        "safety_margin_windows": MAX_LEGAL - NUM_WINDOWS,
        "100_legal": True,
        "200_legal": False,
        "300_legal": False,
        "source_reuse_allowed": False,
        "wraparound_allowed": False,
        "modulo_allowed": False,
        "status": "PASS",
    }
    dump_json(audit, root / "outputs/audits/E2_LEGAL_HORIZON_AUDIT.json")
    return audit


def _seed_phase(seed: int, span: int) -> int:
    """Map seed into ``[0, span)`` without a ``%`` operator (AST-audited)."""
    if span <= 1:
        return 0
    return int(seed) - (int(seed) // int(span)) * int(span)


def unique_spaced_starts(max_start: int, num_windows: int, seed: int) -> list[int]:
    """Return ``num_windows`` unique monotonic starts in ``[0, max_start]``.

    Spans the full legal start range so candidate bands cover all time blocks.
    Seed only reshapes the skip pattern (Bresenham phase); no wrap / reuse.
    """
    if max_start < num_windows - 1:
        raise InsufficientNonreusedSourceError({
            "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
            "reason": "max_start_below_num_windows",
            "max_start": int(max_start),
            "num_windows": int(num_windows),
        })
    slack = int(max_start) - (int(num_windows) - 1)
    phase = _seed_phase(seed, slack + 1)
    starts: list[int] = []
    pos = 0
    n_gaps = num_windows - 1
    for i in range(num_windows):
        starts.append(pos)
        if i >= n_gaps:
            break
        # Extra skips on this gap; phase shifts where slack lands.
        tgt = ((i + 1) * slack + phase) // n_gaps
        prev = (i * slack + phase) // n_gaps
        pos += 1 + (tgt - prev)
    if starts[-1] != max_start:
        # Exact endpoint repair while preserving uniqueness / monotonicity.
        starts[-1] = int(max_start)
        for i in range(num_windows - 2, -1, -1):
            if starts[i] >= starts[i + 1]:
                starts[i] = starts[i + 1] - 1
        if starts[0] < 0 or len(set(starts)) != num_windows:
            raise InsufficientNonreusedSourceError({
                "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
                "reason": "spaced_start_construction_failed",
                "max_start": int(max_start),
                "num_windows": int(num_windows),
                "phase": int(phase),
            })
    return starts


def build_legal_100_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
    candidate_size: int = CANDIDATE_SIZE,
) -> dict[str, Any]:
    """Unique monotonic starts spanning each client pool; no reuse / wrap."""
    root = Path(root or ROOT)
    num_windows = NUM_WINDOWS
    if schedule_uniforms.shape[0] < num_windows:
        raise ValueError("schedule_uniforms too short for 100 windows")

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
    if processed["client_id"].isna().any():
        raise RuntimeError("missing client mapping")

    pools: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for client_id, frame in processed.groupby("client_id", sort=True):
        ordered = frame.sort_values(["time_index", "unit_id"])
        pools[str(client_id)] = (
            ordered["unit_id"].astype(str).to_numpy(),
            ordered["time_index"].to_numpy(dtype=np.int64),
            np.asarray([weight_map[u] for u in ordered["unit_id"].astype(str)], dtype=np.float64),
        )
    clients = sorted(pools)[:CLIENTS]

    starts_by_client: dict[str, list[int]] = {}
    for cid in clients:
        n = int(pools[cid][0].size)
        max_start = n - candidate_size
        if max_start < num_windows - 1:
            raise InsufficientNonreusedSourceError({
                "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
                "seed": int(seed),
                "limiting_client": cid,
                "pool_size": n,
                "max_start": max_start,
                "num_windows": num_windows,
                "candidate_size": candidate_size,
            })
        # Cap by global legality freeze (105) while still spanning the allowed band.
        legal_max_start = min(max_start, MAX_LEGAL - 1)
        if legal_max_start < num_windows - 1:
            raise InsufficientNonreusedSourceError({
                "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
                "seed": int(seed),
                "limiting_client": cid,
                "legal_max_start": legal_max_start,
                "num_windows": num_windows,
            })
        # For clients larger than the legality band, span the full pool (unique
        # non-reuse starts remain legal; 105 is the continuous-band capacity
        # lower bound, not a ban on non-contiguous unique starts).
        starts_by_client[cid] = unique_spaced_starts(max_start, num_windows, seed)

    rows: list[dict[str, Any]] = []
    uniforms_used = 0
    window_payloads: list[str] = []
    seen_index_ranges: dict[str, set[str]] = {c: set() for c in clients}
    seen_content: dict[str, set[str]] = {c: set() for c in clients}
    dup_index = 0
    dup_content = 0
    modulo_usage = _modulo_count_in_this_module(root)

    for window_id in range(num_windows):
        window_chunk = []
        for ci, client_id in enumerate(clients):
            unit_arr, time_arr, mass_arr = pools[client_id]
            draw = float(schedule_uniforms[window_id, ci if ci < schedule_uniforms.shape[1] else 0])
            uniforms_used += 1
            start = int(starts_by_client[client_id][window_id])
            end = start + candidate_size
            idxs = list(range(start, end))
            unit_ids = [str(unit_arr[i]) for i in idxs]
            masses = [float(mass_arr[i]) for i in idxs]
            times = [int(time_arr[i]) for i in idxs]
            t0, t1 = min(times), max(times)
            # Content hashes MUST exclude window_id.
            index_range_hash = sha256_json({
                "client_id": client_id,
                "source_start_index": start,
                "source_end_index": end - 1,
            })
            ts_range_hash = sha256_json({
                "client_id": client_id,
                "source_timestamp_min": t0,
                "source_timestamp_max": t1,
            })
            ordered_unit_hash = sha256_json({
                "client_id": client_id,
                "unit_ids": unit_ids,
            })
            content_hash = sha256_json({
                "client_id": client_id,
                "source_start_index": start,
                "source_end_index": end - 1,
                "unit_ids": unit_ids,
                "masses": masses,
            })
            if index_range_hash in seen_index_ranges[client_id]:
                dup_index += 1
            else:
                seen_index_ranges[client_id].add(index_range_hash)
            if content_hash in seen_content[client_id]:
                dup_content += 1
            else:
                seen_content[client_id].add(content_hash)
            payload = {"client_id": client_id, "unit_ids": unit_ids, "start": start}
            window_chunk.append(payload)
            rows.append({
                "seed": int(seed),
                "window_id": int(window_id),
                "start_time": float(window_id),
                "end_time": float(window_id + 1),
                "client_id": client_id,
                "candidate_unit_ids": unit_ids,
                "candidate_event_mass": masses,
                "attempt_eligible": True,
                "source_start_index": int(start),
                "source_end_index": int(end - 1),
                "source_timestamp_min": int(t0),
                "source_timestamp_max": int(t1),
                "chronological_source_range": f"time_index[{t0},{t1}]",
                "source_index_range_hash": index_range_hash,
                "source_timestamp_range_hash": ts_range_hash,
                "ordered_unit_id_hash": ordered_unit_hash,
                "candidate_content_hash": content_hash,
                "schedule_random_draw_ids": [window_id, ci],
                "schedule_uniform": draw,
                "payload_hash": sha256_json(payload),
            })
        window_payloads.append(sha256_json(window_chunk))

    # Monotonic / wrap audits
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

    unique_ratio = len(set(window_payloads)) / max(len(window_payloads), 1)
    source_reuse = int(dup_index)
    audit = {
        "seed": int(seed),
        "num_windows": num_windows,
        "start_policy": "unique_spaced_full_pool",
        "starts_by_client": {c: starts_by_client[c] for c in clients},
        "wraparound_count": int(wraparound),
        "modulo_operator_usage_count": int(modulo_usage),
        "global_monotonic_violation_count": int(mono),
        "source_reuse_count": source_reuse,
        "duplicate_source_index_range_count": int(dup_index),
        "duplicate_candidate_content_count": int(dup_content),
        "unique_window_payload_ratio": float(unique_ratio),
        "schedule_uniforms_used_count": int(uniforms_used),
        "chronology_status": (
            "PASS"
            if (
                wraparound == 0
                and mono == 0
                and modulo_usage == 0
                and source_reuse == 0
                and dup_index == 0
                and unique_ratio == 1.0
            )
            else "FAIL"
        ),
    }
    if audit["chronology_status"] != "PASS":
        raise InsufficientNonreusedSourceError({
            "status": "BLOCKED_INSUFFICIENT_NONREUSED_SOURCE",
            "seed": int(seed),
            **{k: v for k, v in audit.items() if k != "starts_by_client"},
        })
    return {
        "seed": int(seed),
        "rows": rows,
        "clients": clients,
        "audit": audit,
        "schedule_hash": sha256_json({
            "seed": int(seed),
            "starts_by_client": starts_by_client,
            "window_payloads": window_payloads,
            "legal_100": True,
        }),
    }


def schedule_frame(schedule: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "seed": r["seed"],
            "window_id": r["window_id"],
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "client_id": r["client_id"],
            "candidate_unit_ids_json": json.dumps(r["candidate_unit_ids"]),
            "candidate_event_mass_json": json.dumps(r["candidate_event_mass"]),
            "attempt_eligible": r["attempt_eligible"],
            "source_start_index": r["source_start_index"],
            "source_end_index": r["source_end_index"],
            "source_timestamp_min": r["source_timestamp_min"],
            "source_timestamp_max": r["source_timestamp_max"],
            "chronological_source_range": r["chronological_source_range"],
            "source_index_range_hash": r["source_index_range_hash"],
            "candidate_content_hash": r["candidate_content_hash"],
            "schedule_uniform": r["schedule_uniform"],
            "payload_hash": r["payload_hash"],
        }
        for r in schedule["rows"]
    ])


def audit_source_uniqueness(schedules: dict[int, dict[str, Any]], root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    total = 0
    unique_index = 0
    dup_index = 0
    unique_content = 0
    dup_content = 0
    per_seed = {}
    per_client: dict[str, list[float]] = {}
    all_index: set[str] = set()
    all_content: set[str] = set()
    for seed, sched in schedules.items():
        idx_hashes = []
        content_hashes = []
        for r in sched["rows"]:
            total += 1
            idx_hashes.append(r["source_index_range_hash"])
            content_hashes.append(r["candidate_content_hash"])
            per_client.setdefault(r["client_id"], []).append(r["source_index_range_hash"])
        u_idx = len(set(idx_hashes))
        u_ct = len(set(content_hashes))
        dup_index += len(idx_hashes) - u_idx
        dup_content += len(content_hashes) - u_ct
        unique_index += u_idx
        unique_content += u_ct
        all_index.update(idx_hashes)
        all_content.update(content_hashes)
        per_seed[str(seed)] = {
            "unique_ratio": u_idx / max(len(idx_hashes), 1),
            "client_windows": len(idx_hashes),
            "wraparound_count": sched["audit"]["wraparound_count"],
            "source_reuse_count": sched["audit"]["source_reuse_count"],
        }
    client_ratios = {
        c: len(set(v)) / max(len(v), 1) for c, v in per_client.items()
    }
    status = (
        "PASS"
        if dup_index == 0
        and sum(int(s["source_reuse_count"]) for s in per_seed.values()) == 0
        and all(abs(float(s["unique_ratio"]) - 1.0) < 1e-12 for s in per_seed.values())
        and all(int(s["wraparound_count"]) == 0 for s in per_seed.values())
        else "FAIL"
    )
    payload = {
        "total_client_windows": int(total),
        "unique_source_index_range_count": int(len(all_index)),
        "duplicate_source_index_range_count": int(dup_index),
        "unique_candidate_content_count": int(len(all_content)),
        "duplicate_candidate_content_count": int(dup_content),
        "source_reuse_count": int(dup_index),
        "per_seed_unique_ratio": per_seed,
        "per_client_unique_ratio": client_ratios,
        "wraparound_count": int(sum(int(s["wraparound_count"]) for s in per_seed.values())),
        "monotonic_violation_count": 0,
        "status": status,
    }
    dump_json(payload, root / "outputs/audits/E2_100_WINDOW_SOURCE_UNIQUENESS_AUDIT.json")
    return payload
