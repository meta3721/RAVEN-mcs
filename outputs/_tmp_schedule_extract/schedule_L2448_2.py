"""Continuous non-repeating 300-window SensorScope schedule."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from raven_mcs.e2.identity import (
    load_e1_atomic_target_weights,
    load_e1_head_tail_mapping,
    load_e1_supported_test_units,
)
from raven_mcs.utils.hashing import sha256_json

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 300
CANDIDATE_SIZE = 18
CLIENTS = 8


def _station_to_client(root: Path) -> dict[str, str]:
    cfg = yaml.safe_load(
        (root / "configs/frozen/e1_sensorscope_clients.yaml").read_text(encoding="utf-8")
    )
    return {str(k): str(v) for k, v in cfg["station_to_client"].items()}


def _take_roll(ids: list[str], start: int, count: int) -> list[str]:
    if not ids:
        return []
    out = []
    for k in range(count):
        out.append(ids[(start + k) % len(ids)])
    # unique preserve order
    seen = set()
    uniq = []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def build_continuous_schedule(
    seed: int,
    *,
    schedule_uniforms: np.ndarray,
    root: Path | None = None,
    num_windows: int = NUM_WINDOWS,
    candidate_size: int = CANDIDATE_SIZE,
) -> dict[str, Any]:
    """Build a continuous 300-window schedule over supported test units.

    Chronological SensorScope time order is preserved within role pools per client.
    Schedule uniforms jitter the cursor so payloads are non-repeating and not formed
    by copying identical 100-window blocks.
    """
    root = Path(root or ROOT)
    if int(num_windows) != NUM_WINDOWS:
        raise ValueError(f"requires num_windows={NUM_WINDOWS}")
    if schedule_uniforms.shape[0] < num_windows:
        raise ValueError("schedule_uniforms too short")

    supported = load_e1_supported_test_units(root)
    atomic = load_e1_atomic_target_weights(root)
    head_tail = load_e1_head_tail_mapping(root).set_index("unit_id")
    weight_map = {
        str(r.unit_id): float(r.target_weight) for r in atomic.itertuples(index=False)
    }
    role_map = {
        str(u): str(head_tail.loc[u, "role"]) for u in atomic["unit_id"].astype(str)
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

    by_client_role: dict[str, dict[str, list[str]]] = {}
    by_client_time: dict[str, dict[str, int]] = {}
    for client_id, frame in processed.groupby("client_id", sort=True):
        ordered = frame.sort_values(["time_index", "unit_id"])
        roles: dict[str, list[str]] = {"head": [], "tail": [], "neutral": []}
        times: dict[str, int] = {}
        for row in ordered.itertuples(index=False):
            uid = str(row.unit_id)
            role = role_map.get(uid, "neutral")
            if role not in roles:
                role = "neutral"
            roles[role].append(uid)
            times[uid] = int(row.time_index)
        by_client_role[str(client_id)] = roles
        by_client_time[str(client_id)] = times
    clients = sorted(by_client_role)[:CLIENTS]
    if not clients:
        raise RuntimeError("no clients available for schedule")

    rows: list[dict[str, Any]] = []
    uniforms_used = 0
    window_payloads: list[str] = []
    for window_id in range(int(num_windows)):
        window_chunk = []
        for ci, client_id in enumerate(clients):
            roles = by_client_role[client_id]
            draw = float(schedule_uniforms[window_id, ci % schedule_uniforms.shape[1]])
            uniforms_used += 1
            # Role-balanced composition: ~6 head, 4 tail, 8 neutral (18).
            n_head = max(2, candidate_size // 3)
            n_tail = max(2, candidate_size // 4)
            n_neu = max(2, candidate_size - n_head - n_tail)
            # Chronological cursors advance every window; uniform jitters offset.
            cursors = {}
            for role_name, pool in roles.items():
                n = max(len(pool), 1)
                stride = max(1, n // num_windows)
                jitter = int(np.floor(draw * max(n - 1, 1)))
                cursors[role_name] = (window_id * stride + jitter) % n
            unit_ids = (
                _take_roll(roles["head"], cursors["head"], n_head)
                + _take_roll(roles["tail"], cursors["tail"], n_tail)
                + _take_roll(roles["neutral"], cursors["neutral"], n_neu)
            )
            # Deduplicate while preserving order; refill from full chronological pool.
            seen = set()
            uniq = []
            for u in unit_ids:
                if u not in seen:
                    seen.add(u)
                    uniq.append(u)
            if len(uniq) < min(candidate_size, sum(len(v) for v in roles.values())):
                all_ids = roles["head"] + roles["tail"] + roles["neutral"]
                for u in all_ids:
                    if u not in seen:
                        seen.add(u)
                        uniq.append(u)
                    if len(uniq) >= candidate_size:
                        break
            unit_ids = uniq[:candidate_size]
            masses = [weight_map[u] for u in unit_ids]
            times = [by_client_time[client_id][u] for u in unit_ids]
            t0, t1 = (min(times), max(times)) if times else (-1, -1)
            payload = {
                "window_id": window_id,
                "client_id": client_id,
                "unit_ids": unit_ids,
                "masses": masses,
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
            "candidate_unit_ids_json": json.dumps(r["candidate_unit_ids"]),
            "candidate_event_mass_json": json.dumps(r["candidate_event_mass"]),
            "attempt_eligible": r["attempt_eligible"],
            "chronological_source_range": r["chronological_source_range"],
            "schedule_random_draw_ids_json": json.dumps(r["schedule_random_draw_ids"]),
            "schedule_uniform": r["schedule_uniform"],
            "payload_hash": r["payload_hash"],
        })
    return pd.DataFrame(rows)
