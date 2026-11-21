"""Measured-O EventTrace for NYC Pilot2: R from occupancy, O from o_observed, U controlled."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.controlled import time_of_day_block
from raven_mcs.e3.real_runner.constants import S_MAX, WINDOW_DURATION
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata

DATASET = "cityscanner_nyc_p2_measured_o"
NUM_WINDOWS = 100
GENERATOR = "cityscanner-p2-measured-o-controlled-u-v1"


def window_id_by_time_index(train: pd.DataFrame) -> dict[int, int]:
    times = sorted(int(t) for t in train["time_index"].unique())
    n = len(times)
    if n < NUM_WINDOWS:
        raise RuntimeError(f"train unique time_index {n} < {NUM_WINDOWS}")
    mapping = {t: min(NUM_WINDOWS - 1, i * NUM_WINDOWS // n) for i, t in enumerate(times)}
    if set(mapping.values()) != set(range(NUM_WINDOWS)):
        raise RuntimeError("window_id does not cover 0..99")
    return mapping


def generate_p2_measured_o_eventtrace(
    *,
    occupancy: pd.DataFrame,
    seed: int,
    dataset: str = DATASET,
    s_max: int = S_MAX,
    method: str | None = None,
) -> tuple[EventTrace, pd.DataFrame, dict[str, object]]:
    del method
    rng = np.random.default_rng(int(seed) + 13)
    occ = occupancy.copy()
    occ["unit_id"] = occ["unit_id"].astype(str)
    occ["spatial_id"] = occ["spatial_id"].astype(str)
    occ["split"] = occ["split"].astype(str)
    occ["o_observed"] = occ["o_observed"].astype(int)
    train = occ.loc[occ["split"] == "train"].copy()
    if train.empty:
        raise RuntimeError("measured-O EventTrace requires non-empty train occupancy")
    if train["spatial_id"].str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID leaked into spatial_id")

    win_of = window_id_by_time_index(train)
    n_train_slots = int(train["time_index"].nunique())
    o_of = {str(r.unit_id): int(r.o_observed) for r in train.itertuples(index=False)}
    unit_meta = {
        str(r.unit_id): {
            "spatial_id": str(r.spatial_id),
            "time_index": int(r.time_index),
            "absolute_time": pd.Timestamp(r.absolute_time),
            "processed_target_group": str(r.target_group),
            "opportunity_stratum": str(r.opportunity_stratum),
            "h_id": str(r.target_group),
            "time_block": int(time_of_day_block(r.absolute_time)),
            "window_id": int(win_of[int(r.time_index)]),
            "o_observed": int(r.o_observed),
        }
        for r in train.itertuples(index=False)
    }
    clients_by_unit: dict[str, list[str]] = {}
    for uid, meta in unit_meta.items():
        clients_by_unit.setdefault(uid, []).append(str(meta["spatial_id"]))
    units_by_window: dict[int, list[str]] = {w: [] for w in range(NUM_WINDOWS)}
    for uid, meta in unit_meta.items():
        units_by_window[int(meta["window_id"])].append(uid)
    for w in units_by_window:
        units_by_window[w] = sorted(set(units_by_window[w]))

    event_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    for window_id in range(NUM_WINDOWS):
        deadline = float(window_id) + WINDOW_DURATION
        slot_units = units_by_window[window_id]
        clients = sorted({c for uid in slot_units for c in clients_by_unit.get(uid, [])})
        for client_id in clients:
            risk = [uid for uid in slot_units if client_id in clients_by_unit.get(uid, [])]
            o_flags = np.asarray([bool(o_of[uid]) for uid in risk], dtype=bool)
            observed = [uid for uid, flag in zip(risk, o_flags) if bool(flag)]
            p_obs_by_unit = {uid: float(o_of[uid]) for uid in risk}
            usable = compute_usable_r3(
                rng=rng,
                registration_time=float(window_id) + 0.1,
                window_deadline=deadline,
                window_id=int(window_id),
                s_max=int(s_max),
                has_observations=bool(observed),
            )
            q_use = float(usable["U"])
            emp_p = float(np.mean([p_obs_by_unit[u] for u in risk])) if risk else 0.0
            time_indices = sorted({int(unit_meta[uid]["time_index"]) for uid in risk})
            region_to_i = {"region0": 0, "region1": 1, "region2": 2, "region3": 3}
            stratum_by_unit = {uid: str(unit_meta[uid]["opportunity_stratum"]) for uid in risk}
            group_by_unit = {
                uid: int(region_to_i[str(unit_meta[uid]["processed_target_group"])])
                for uid in risk
            }
            event_rows.append(
                {
                    "window_id": int(window_id),
                    "client_id": client_id,
                    "risk_set_unit_ids": list(risk),
                    "opportunity_features": {
                        "time_index": int(time_indices[0]) if time_indices else int(window_id),
                        "time_indices": time_indices,
                        "p_obs_true": emp_p,
                        "p_obs_true_by_unit": dict(p_obs_by_unit),
                        "opportunity_stratum_by_unit": dict(stratum_by_unit),
                        "target_group_by_unit": dict(group_by_unit),
                        "q_use_true": q_use,
                        "device_tier": usable["device_tier"],
                        "prestate_only": True,
                        "o_source": "measured_finite_pm25",
                    },
                    "observed_unit_ids": list(observed),
                    "O": {uid: True for uid in observed},
                    "registration_time": float(usable["T_reg"]),
                    "downloaded_version": int(usable["downloaded_version"]),
                    "model_age": int(usable["tau"]),
                    "tau": int(usable["tau"]),
                    "device_profile": usable["device_profile"],
                    "network_profile": usable["network_profile"],
                    "compute_success": bool(usable["compute_success"]),
                    "compute_duration": float(usable["T_cmp"]),
                    "network_success": bool(usable["network_success"]),
                    "network_duration": float(usable["T_net"]),
                    "arrival_time": float(usable["T_arr"]),
                    "U": int(usable["U"]),
                    "raw_workload": float(len(observed)),
                    "oracle_p": max(emp_p, 1e-12),
                    "oracle_q": max(float(q_use), 1e-12),
                    "hidden_confounder": 0.0,
                }
            )
            for uid in risk:
                meta = unit_meta[uid]
                long_rows.append(
                    {
                        "dataset": dataset,
                        "seed": int(seed),
                        "client_id": client_id,
                        "atomic_unit_id": uid,
                        "spatial_id": meta["spatial_id"],
                        "time_slot": int(meta["time_index"]),
                        "window_id": int(window_id),
                        "target_group_h": meta["h_id"],
                        "processed_target_group": meta["processed_target_group"],
                        "opportunity_stratum_s": meta["opportunity_stratum"],
                        "R_opportunity": 1,
                        "O_observed": int(uid in observed),
                        "E_eligibility": int(
                            bool(usable["compute_success"])
                            and bool(usable["network_success"])
                            and bool(usable["deadline_pass"])
                            and bool(usable["staleness_pass"])
                            and bool(observed)
                        ),
                        "U_usable": int(usable["U"]),
                        "p_obs": float(o_of[uid]),
                        "q_use": q_use,
                        "deadline_pass": int(usable["deadline_pass"]),
                        "staleness_tau": int(usable["tau"]),
                        "timestamp": str(meta["absolute_time"]),
                        "source": "cityscanner_p2_union_gps+measured_pm_O+controlled_U",
                    }
                )

    events = pd.DataFrame(event_rows)
    if events.empty:
        raise RuntimeError("measured-O EventTrace produced no client×window rows")
    if int(events["window_id"].nunique()) != NUM_WINDOWS:
        raise RuntimeError(
            f"expected {NUM_WINDOWS} windows, got {int(events['window_id'].nunique())}"
        )
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=NUM_WINDOWS,
        num_clients=int(events["client_id"].nunique()),
        s_max=int(s_max),
        generator=GENERATOR,
        notes=(
            "R from Pilot2 PM∪NO2 GPS cell x 30min visits",
            "O measured finite pm25; not Bernoulli p_obs",
            "U Complete-aligned compute_usable_r3",
            "method-independent",
        ),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    long_df = pd.DataFrame(long_rows)
    audit = {
        "n_windows": NUM_WINDOWS,
        "n_train_slots": n_train_slots,
        "n_event_rows": int(len(events)),
        "n_long_rows": int(len(long_df)),
        "n_clients": int(events["client_id"].nunique()),
        "s_max": int(s_max),
        "method_argument_ignored": True,
        "r_source": "occupancy_units.parquet union GPS",
        "o_source": "measured o_observed from finite pm25",
        "u_source": "e3.real_runner.stage2_r3.compute_usable_r3",
        "p_obs_bernoulli": False,
        "mean_O_on_R": float(train["o_observed"].mean()),
    }
    return trace, long_df, audit
