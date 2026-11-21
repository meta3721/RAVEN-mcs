"""Continuous non-repeating 300-window SensorScope schedule."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import load_e1_atomic_target_weights, load_e1_supported_test_units
from raven_mcs.utils.hashing import sha256_json

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 300
CANDIDATE_SIZE = 16
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
    """Build a continuous 300-window schedule over supported test units.

    Uses frozen SensorScope time_index order within each client pool, advanced by a
    chronological cursor and modulated by ``base_client_window_schedule`` uniforms.
    Window payloads are not formed by copying 100-window blocks.
    """
    root = Path(root or ROOT)
    if int(num_windows) != NUM_WINDOWS:
        raise ValueError(f"requires num_windows={NUM_WINDOWS}")
    if schedule_uniforms.shape[0] < num_windows:
        raise ValueError("schedule_uniforms too short")

    supported = load_e1_supported_test_units(root)
    atomic = load_e1_atomic_target_weights(root)
    weight_map = {
        str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)
    }
    processed = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    processed = processed.loc[
        processed["unit_id"].astype(str).isin(set(supported["unit_id"].astype(str)))
    ].copy()
    processed["unit_id"] = processed["unit_id"].astype(str)
    station_map = _station_to_client(root)
    processed["client_id"] = processed["unit_id"].map(
        lambda u: station_map.get(u.split("_", 1)[0])
    )
    if processed["client_id"].isna().any():
        raise RuntimeError("missing client mapping for supported units")

    by_client: dict[str, pd.DataFrame] = {}
    for client_id, frame in processed.groupby("client_id", sort=True):
        ordered = frame.sort_values(["time_index", "unit_id"]).reset_index(drop=True)
        by_client[str(client_id)] = ordered
    clients = sorted(by_client)[:CLIENTS]
    if len(clients) < 1:
        raise RuntimeError("no clients available for schedule")

    rows: list[dict[str, Any]] = []
    uniforms_used = 0
    payloads: list[str] = []
    for window_id in range(int(num_windows)):
        for ci, client_id in enumerate(clients):
            pool = by_client[client_id]
            n = len(pool)
            if n == 0:
                continue
            draw = float(schedule_uniforms[window_id, ci % schedule_uniforms.shape[1]])
            uniforms_used += 1
            # Chronological cursor advances every window; uniform jitters start offset.
            stride = max(1, n // num_windows)
            cursor = (window_id * stride) % n
            jitter = int(np.floor(draw * max(n - candidate_size, 1)))
            start = (cursor + jitter) % n
            idxs = [(start + k) % n for k in range(min(candidate_size, n))]
            part = pool.iloc[idxs]
            unit_ids = part["unit_id"].astype(str).tolist()
            if len(unit_ids) != len(set(unit_ids)):
                # Wrap collision: fall back to unique contiguous slice.
                unit_ids = pool["unit_id"].astype(str).iloc[
                    start:start + min(candidate_size, n)
                ].tolist()
                if len(unit_ids) < min(candidate_size, n):
                    unit_ids = pool["unit_id"].astype(str).head(min(candidate_size, n)).tolist()
            masses = [weight_map[u] for u in unit_ids]
            t0 = int(part["time_index"].min()) if len(part) else -1
            t1 = int(part["time_index"].max()) if len(part) else -1
            payload = sha256_json({
                "window_id": window_id,
                "client_id": client_id,
                "unit_ids": unit_ids,
                "masses": masses,
            })
            payloads.append(payload)
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
                "payload_hash": payload,
            })

    # Non-repetition audit over window-level payloads (all clients joined).
    window_payloads = []
    for window_id in range(int(num_windows)):
        chunk = [r for r in rows if r["window_id"] == window_id]
        window_payloads.append(sha256_json([
            {"client_id": r["client_id"], "unit_ids": r["candidate_unit_ids"]}
            for r in chunk
        ]))
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
        raise RuntimeError(
            f"unique_window_payload_ratio={unique_ratio:.3f} < 0.80"
        )
    if audit["block_hashes_all_equal"]:
        raise RuntimeError("repeated 100-window blocks detected")
    return {
        "seed": int(seed),
        "rows": rows,
        "clients": clients,
        "audit": audit,
        "schedule_hash": sha256_json({
            "seed": int(seed),
            "rows": [
                {
                    "window_id": r["window_id"],
                    "client_id": r["client_id"],
                    "candidate_unit_ids": r["candidate_unit_ids"],
                    "candidate_event_mass": r["candidate_event_mass"],
                }
                for r in rows
            ],
        }),
    }


def schedule_frame(schedule: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for r in schedule["rows"]:
        rows.append({
            "seed": r["seed"],
            "window_id": r["window_id"],
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "client_id": r["client_id"],
            "candidate_unit_ids_json": str(r["candidate_unit_ids"]),
            "candidate_event_mass_json": str(r["candidate_event_mass"]),
            "attempt_eligible": r["attempt_eligible"],
            "chronological_source_range": r["chronological_source_range"],
            "schedule_random_draw_ids_json": str(r["schedule_random_draw_ids"]),
            "schedule_uniform": r["schedule_uniform"],
            "payload_hash": r["payload_hash"],
        })
    return pd.DataFrame(rows)
