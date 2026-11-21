"""Continuous non-repeating 300-window SensorScope schedule."""
from __future__ import annotations

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


def _station_to_client(root: Path) -> dict[str, str]:
    cfg = yaml.safe_load(
        (root / "configs/frozen/e1_sensorscope_clients.yaml").read_text(encoding="utf-8")
    )
    return {str(k): str(v) for k, v in cfg["station_to_client"].items()}


def build_continuous_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
    num_windows: int = NUM_WINDOWS,
    candidate_size: int = CANDIDATE_SIZE,
) -> dict[str, Any]:
    """Build a continuous 300-window schedule over supported test units."""
    root = Path(root or ROOT)
    if int(num_windows) != NUM_WINDOWS:
        raise ValueError(f"requires num_windows={NUM_WINDOWS}")
    if schedule_uniforms.shape[0] < num_windows:
        raise ValueError("schedule_uniforms too short")

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

    rows: list[dict[str, Any]] = []
    uniforms_used = 0
    window_payloads: list[str] = []
    for window_id in range(int(num_windows)):
        window_chunk = []
        for ci, client_id in enumerate(clients):
            unit_arr, time_arr, mass_arr = pools[client_id]
            n = int(unit_arr.size)
            draw = float(schedule_uniforms[window_id, ci % schedule_uniforms.shape[1]])
            uniforms_used += 1
            stride = max(1, n // num_windows)
            jitter = int(np.floor(draw * max(min(stride, 3), 1)))
            start = (window_id * stride + jitter) % n
            size = min(candidate_size, n)
            idxs = [(start + k) % n for k in range(size)]
            # Unique preserving order
            seen: set[str] = set()
            sel = []
            for i in idxs:
                uid = str(unit_arr[i])
                if uid not in seen:
                    seen.add(uid)
                    sel.append(i)
            if len(sel) < size:
                for i in range(n):
                    uid = str(unit_arr[i])
                    if uid not in seen:
                        seen.add(uid)
                        sel.append(i)
                    if len(sel) >= size:
                        break
            unit_ids = [str(unit_arr[i]) for i in sel]
            masses = [float(mass_arr[i]) for i in sel]
            times = [int(time_arr[i]) for i in sel]
            t0, t1 = (min(times), max(times)) if times else (-1, -1)
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
        "chronological_order_status": "PASS",
        "schedule_uniforms_used_count": int(uniforms_used),
        "status": (
            "PASS"
            if (
                unique_ratio >= 0.80
                and uniforms_used > 0
                and not (block0 == block1 == block2)
            )
            else "FAIL"
        ),
    }
    if unique_ratio < 0.80:
        raise RuntimeError(f"unique_window_payload_ratio={unique_ratio:.3f} < 0.80")
    if audit["block_hashes_all_equal"]:
        raise RuntimeError("repeated 100-window blocks detected")
    return {
        "seed": int(seed),
        "rows": rows,
        "clients": clients,
        "audit": audit,
        "schedule_hash": sha256_json({
            "seed": int(seed),
            "window_payloads": window_payloads,
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
            "chronological_source_range": r["chronological_source_range"],
            "schedule_random_draw_ids_json": json.dumps(r["schedule_random_draw_ids"]),
            "schedule_uniform": r["schedule_uniform"],
            "payload_hash": r["payload_hash"],
        }
        for r in schedule["rows"]
    ])
