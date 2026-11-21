"""Non-wrap continuous 300-window SensorScope schedule (no modulo indexing)."""
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

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 300
CANDIDATE_SIZE = 20
CLIENTS = 8


class InsufficientContinuousWindowsError(RuntimeError):
    """Raised when a legal non-wrap 300-window schedule cannot be formed."""

    def __init__(self, payload: dict[str, Any]):
        super().__init__(payload.get("status", "BLOCKED_INSUFFICIENT_CONTINUOUS_WINDOWS"))
        self.payload = payload


def _station_to_client(root: Path) -> dict[str, str]:
    cfg = yaml.safe_load(
        (root / "configs/frozen/e1_sensorscope_clients.yaml").read_text(encoding="utf-8")
    )
    return {str(k): str(v) for k, v in cfg["station_to_client"].items()}


def _source_has_modulo_operator(root: Path) -> int:
    """Count modulo operators used for schedule indexing in this module's AST."""
    src = (root / "src/raven_mcs/e2/true_stratum/schedule.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            count += 1
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Mod):
            count += 1
    return int(count)


def compute_max_legal_continuous_windows(
    root: Path | None = None,
    *,
    candidate_size: int = CANDIDATE_SIZE,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed = processed.loc[processed["unit_id"].astype(str).isin(supported)].copy()
    station_map = _station_to_client(root)
    processed["client_id"] = processed["unit_id"].astype(str).map(
        lambda u: station_map.get(u.split("_", 1)[0])
    )
    sizes = processed.groupby("client_id").size().to_dict()
    legal = {}
    for cid, n in sizes.items():
        legal[str(cid)] = int(max(0, int(n) - int(candidate_size) + 1))
    limiting = min(legal, key=legal.get) if legal else None
    maximum = int(min(legal.values())) if legal else 0
    suggested = [L for L in (100, 200, 300) if L <= maximum]
    return {
        "per_client_max_legal_windows": legal,
        "maximum_legal_continuous_windows": maximum,
        "limiting_client": limiting,
        "candidate_size": int(candidate_size),
        "suggested_legal_candidate_lengths": suggested,
        "earliest_time_index": int(processed["time_index"].min()) if len(processed) else -1,
        "latest_time_index": int(processed["time_index"].max()) if len(processed) else -1,
    }


def build_nonwrap_continuous_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
    num_windows: int = NUM_WINDOWS,
    candidate_size: int = CANDIDATE_SIZE,
) -> dict[str, Any]:
    """Build a non-wrapping continuous schedule over supported test units.

    Start indices are non-decreasing staircases in ``[0, n - candidate_size]``.
    No ``% n`` pool indexing is used. If any client pool is shorter than
    ``candidate_size``, raise ``InsufficientContinuousWindowsError``.
    """
    root = Path(root or ROOT)
    if int(num_windows) != NUM_WINDOWS:
        raise ValueError(f"requires num_windows={NUM_WINDOWS}")
    if schedule_uniforms.shape[0] < num_windows:
        raise ValueError("schedule_uniforms too short")

    capacity = compute_max_legal_continuous_windows(root, candidate_size=candidate_size)
    if int(capacity["maximum_legal_continuous_windows"]) < 1:
        raise InsufficientContinuousWindowsError({
            "status": "BLOCKED_INSUFFICIENT_CONTINUOUS_WINDOWS",
            "seed": int(seed),
            **capacity,
        })

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
        raise RuntimeError("missing client mapping for supported units")

    pools: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for client_id, frame in processed.groupby("client_id", sort=True):
        ordered = frame.sort_values(["time_index", "unit_id"])
        unit_arr = ordered["unit_id"].astype(str).to_numpy()
        time_arr = ordered["time_index"].to_numpy(dtype=np.int64)
        mass_arr = np.asarray([weight_map[u] for u in unit_arr], dtype=np.float64)
        pools[str(client_id)] = (unit_arr, time_arr, mass_arr)
    clients = sorted(pools)[:CLIENTS]
    if not clients:
        raise RuntimeError("no clients available for schedule")

    # Per-client max start for a contiguous candidate block (no wrap).
    max_start: dict[str, int] = {}
    for cid in clients:
        n = int(pools[cid][0].size)
        ms = n - int(candidate_size)
        if ms < 0:
            raise InsufficientContinuousWindowsError({
                "status": "BLOCKED_INSUFFICIENT_CONTINUOUS_WINDOWS",
                "seed": int(seed),
                "limiting_client": cid,
                "pool_size": n,
                "candidate_size": int(candidate_size),
                **capacity,
            })
        max_start[cid] = int(ms)

    rows: list[dict[str, Any]] = []
    uniforms_used = 0
    window_payloads: list[str] = []
    source_reuse = 0
    seen_ranges: dict[str, set[tuple[int, int]]] = {c: set() for c in clients}
    prev_start = {c: 0 for c in clients}
    modulo_usage = _source_has_modulo_operator(root)

    for window_id in range(int(num_windows)):
        window_chunk = []
        for ci, client_id in enumerate(clients):
            unit_arr, time_arr, mass_arr = pools[client_id]
            n = int(unit_arr.size)
            draw = float(schedule_uniforms[window_id, ci if ci < schedule_uniforms.shape[1] else 0])
            uniforms_used += 1
            ms = max_start[client_id]
            # Non-decreasing staircase: compress window_id into [0, ms].
            if num_windows <= 1:
                base = 0
            else:
                base = (window_id * ms) // (num_windows - 1)
            # Forward-only jitter in {0,1} that cannot decrease start or exceed ms.
            jitter = 1 if draw >= 0.5 and base < ms else 0
            start = base + jitter
            if start < prev_start[client_id]:
                start = prev_start[client_id]
            if start > ms:
                start = ms
            prev_start[client_id] = start
            size = int(candidate_size)
            # Contiguous forward slice — no modular wrap.
            end = start + size
            if end > n:
                raise InsufficientContinuousWindowsError({
                    "status": "BLOCKED_INSUFFICIENT_CONTINUOUS_WINDOWS",
                    "seed": int(seed),
                    "window_id": int(window_id),
                    "limiting_client": client_id,
                    "start": int(start),
                    "end": int(end),
                    "pool_size": n,
                    **capacity,
                })
            idxs = list(range(start, end))
            unit_ids = [str(unit_arr[i]) for i in idxs]
            masses = [float(mass_arr[i]) for i in idxs]
            times = [int(time_arr[i]) for i in idxs]
            t0, t1 = (min(times), max(times)) if times else (-1, -1)
            key = (t0, t1)
            if key in seen_ranges[client_id]:
                source_reuse += 1
            else:
                seen_ranges[client_id].add(key)
            payload = {
                "window_id": window_id,
                "client_id": client_id,
                "unit_ids": unit_ids,
            }
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
                "schedule_random_draw_ids": [window_id, ci],
                "schedule_uniform": draw,
                "payload_hash": sha256_json(payload),
            })
        window_payloads.append(sha256_json(window_chunk))

    block0 = sha256_json(window_payloads[0:100])
    block1 = sha256_json(window_payloads[100:200])
    block2 = sha256_json(window_payloads[200:300])
    unique_ratio = len(set(window_payloads)) / max(len(window_payloads), 1)
    # Monotonic audits
    mono_viol = 0
    wraparound = 0
    by_client: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_client.setdefault(str(r["client_id"]), []).append(r)
    for cid, items in by_client.items():
        items = sorted(items, key=lambda x: int(x["window_id"]))
        prev_si = -1
        prev_t0 = -1
        for r in items:
            si = int(r["source_start_index"])
            t0 = int(r["source_timestamp_min"])
            if prev_si >= 0 and si < prev_si:
                mono_viol += 1
            if prev_t0 >= 0 and t0 < prev_t0:
                wraparound += 1
            prev_si = si
            prev_t0 = t0

    audit = {
        "seed": int(seed),
        "block_0_99_hash": block0,
        "block_100_199_hash": block1,
        "block_200_299_hash": block2,
        "block_hashes_all_equal": block0 == block1 == block2,
        "duplicate_window_payload_count": int(
            len(window_payloads) - len(set(window_payloads))
        ),
        "unique_window_payload_ratio": float(unique_ratio),
        "wraparound_count": int(wraparound),
        "modulo_operator_usage_count": int(modulo_usage),
        "global_monotonic_violation_count": int(mono_viol),
        "source_reuse_count": int(source_reuse),
        "repeated_block_count": int(1 if block0 == block1 == block2 else 0),
        "schedule_uniforms_used_count": int(uniforms_used),
        "maximum_legal_continuous_windows": capacity["maximum_legal_continuous_windows"],
        "limiting_client": capacity["limiting_client"],
        "chronological_order_status": (
            "PASS"
            if (
                wraparound == 0
                and mono_viol == 0
                and modulo_usage == 0
                and unique_ratio >= 0.80
                and not (block0 == block1 == block2)
                and uniforms_used > 0
            )
            else "FAIL"
        ),
        "status": "PASS",
    }
    audit["status"] = audit["chronological_order_status"]
    if audit["status"] != "PASS":
        raise RuntimeError(f"nonwrap schedule audit failed: {audit}")
    return {
        "seed": int(seed),
        "rows": rows,
        "clients": clients,
        "audit": audit,
        "capacity": capacity,
        "schedule_hash": sha256_json({
            "seed": int(seed),
            "window_payloads": window_payloads,
            "nonwrap": True,
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
            "schedule_random_draw_ids_json": json.dumps(r["schedule_random_draw_ids"]),
            "schedule_uniform": r["schedule_uniform"],
            "payload_hash": r["payload_hash"],
        }
        for r in schedule["rows"]
    ])
