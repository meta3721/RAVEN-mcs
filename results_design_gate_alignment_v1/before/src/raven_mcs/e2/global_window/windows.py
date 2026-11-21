"""Construct shared global server windows W_r = [T_r, T_{r+1})."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.identity import load_e1_supported_test_units
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]
NUM_WINDOWS = 100
WINDOW_HOURS = 6  # frozen prior width; must not silently widen/narrow
DESIGN_SEEDS = tuple(range(28101, 28121))
VALIDATION_SEEDS = (29101, 29102, 29103, 29104, 29105)


def _supported_frame(root: Path) -> pd.DataFrame:
    units = pd.read_parquet(root / "data/processed/sensorscope/atomic_units.parquet")
    supported = set(load_e1_supported_test_units(root)["unit_id"].astype(str))
    frame = units[units["unit_id"].astype(str).isin(supported)].copy()
    frame["unit_id"] = frame["unit_id"].astype(str)
    frame["absolute_time"] = pd.to_datetime(frame["absolute_time"], utc=True)
    frame["spatial_id"] = frame["spatial_id"].astype(str)
    return frame.sort_values(["absolute_time", "unit_id"]).reset_index(drop=True)


def max_nonoverlapping_capacity(frame: pd.DataFrame, window_hours: int = WINDOW_HOURS) -> dict[str, Any]:
    t0 = pd.Timestamp(frame["absolute_time"].min())
    t1 = pd.Timestamp(frame["absolute_time"].max())
    span_sec = float((t1 - t0).total_seconds())
    width_sec = float(window_hours * 3600)
    # Half-open tiles covering [t0, t1]; last partial tile does not count as full window.
    max_full = int(span_sec // width_sec)
    return {
        "supported_time_start": t0.isoformat(),
        "supported_time_end": t1.isoformat(),
        "supported_span_hours": span_sec / 3600.0,
        "window_hours": int(window_hours),
        "max_legal_global_windows": int(max_full),
        "requested_windows": NUM_WINDOWS,
        "unique_timestamp_count": int(frame["absolute_time"].nunique()),
        "supported_unit_count": int(frame["unit_id"].nunique()),
    }


def build_global_server_windows(root: Path | None = None) -> dict[str, Any]:
    """Attempt 100 shared non-overlapping WINDOW_HOURS windows; block if capacity short."""
    root = Path(root or ROOT)
    frame = _supported_frame(root)
    capacity = max_nonoverlapping_capacity(frame, WINDOW_HOURS)
    out_dir = root / "configs/frozen/e2_global_windows"
    out_dir.mkdir(parents=True, exist_ok=True)

    if capacity["max_legal_global_windows"] < NUM_WINDOWS:
        audit = {
            "status": "BLOCKED_GLOBAL_WINDOW_CAPACITY_INSUFFICIENT",
            "global_window_count": 0,
            "requested_windows": NUM_WINDOWS,
            "window_hours": WINDOW_HOURS,
            "overlap_count": 0,
            "gap_count": None,
            "nonmonotonic_count": 0,
            "wraparound_count": 0,
            "client_specific_boundary_count": 0,
            "common_boundary_status": "NOT_BUILT",
            "capacity": capacity,
            "note": (
                "Supported-test atomic units span fewer than 100 non-overlapping "
                f"{WINDOW_HOURS}-hour global windows. Width must not be silently changed."
            ),
        }
        dump_json(audit, root / "outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json")
        identity = {
            "status": audit["status"],
            "requested_windows": NUM_WINDOWS,
            "window_hours": WINDOW_HOURS,
            "capacity": capacity,
            "identity_hash": sha256_json({
                "requested": NUM_WINDOWS,
                "window_hours": WINDOW_HOURS,
                "capacity": capacity,
            }),
        }
        dump_json(identity, out_dir / "global_server_windows_identity.json")
        # Empty parquet placeholder for evidence completeness.
        pd.DataFrame(columns=[
            "window_id", "start_time", "end_time", "duration_sec",
            "global_sequence_index", "supported_client_count", "total_supported_unit_count",
            "identity_hash",
        ]).to_parquet(out_dir / "global_server_windows_100.parquet", index=False)
        return {"status": audit["status"], "audit": audit, "identity": identity, "capacity": capacity, "frame": frame}

    # Feasible path (not expected on current SensorScope supported span).
    t0 = pd.Timestamp(frame["absolute_time"].min())
    rows = []
    for r in range(NUM_WINDOWS):
        start = t0 + pd.Timedelta(hours=WINDOW_HOURS * r)
        end = start + pd.Timedelta(hours=WINDOW_HOURS)
        take = frame[(frame["absolute_time"] >= start) & (frame["absolute_time"] < end)]
        clients = sorted(take["spatial_id"].map(lambda s: s).unique())  # filled later via station map
        rows.append({
            "window_id": r,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "duration_sec": float(WINDOW_HOURS * 3600),
            "global_sequence_index": r,
            "supported_client_count": int(take["spatial_id"].nunique()),
            "total_supported_unit_count": int(len(take)),
        })
    win = pd.DataFrame(rows)
    identity_hash = sha256_json(win.to_dict(orient="list"))
    win["identity_hash"] = identity_hash
    win.to_parquet(out_dir / "global_server_windows_100.parquet", index=False)
    identity = {
        "status": "PASS",
        "global_window_count": NUM_WINDOWS,
        "window_hours": WINDOW_HOURS,
        "identity_hash": identity_hash,
        "capacity": capacity,
        "start_time": win.iloc[0]["start_time"],
        "end_time": win.iloc[-1]["end_time"],
    }
    dump_json(identity, out_dir / "global_server_windows_identity.json")
    audit = {
        "status": "PASS",
        "global_window_count": NUM_WINDOWS,
        "common_boundary_status": "PASS",
        "overlap_count": 0,
        "gap_count": 0,
        "nonmonotonic_count": 0,
        "wraparound_count": 0,
        "client_specific_boundary_count": 0,
        "capacity": capacity,
        "identity_hash": identity_hash,
    }
    dump_json(audit, root / "outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json")
    return {"status": "PASS", "audit": audit, "identity": identity, "windows": win, "capacity": capacity, "frame": frame}
