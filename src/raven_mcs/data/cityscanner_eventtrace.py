"""City Scanner EventTrace: real visit R, controlled Complete-aligned O/U.

Does not train. Does not import tdrive_protocol_seal_r1.
Windows are 100 chronological bins of the 1666 train 30-min slots.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.controlled import time_of_day_block
from raven_mcs.e3.real_runner.constants import S_MAX, WINDOW_DURATION
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata

DATASET = "cityscanner_nyc_pm25"
NUM_WINDOWS = 100
EXPECTED_TRAIN_SLOTS = 1666
MEAN_OBSERVATION_RATE = 0.35
GENERATOR = "cityscanner-real-r-complete-aligned-ou-v1"


def window_id_by_time_index(train: pd.DataFrame) -> dict[int, int]:
    times = sorted(int(t) for t in train["time_index"].unique())
    n = len(times)
    if n != EXPECTED_TRAIN_SLOTS:
        raise RuntimeError(
            f"train unique time_index {n} != frozen {EXPECTED_TRAIN_SLOTS}"
        )
    mapping = {t: min(NUM_WINDOWS - 1, i * NUM_WINDOWS // n) for i, t in enumerate(times)}
    if set(mapping.values()) != set(range(NUM_WINDOWS)):
        raise RuntimeError("window_id does not cover 0..99")
    return mapping


def generate_cityscanner_eventtrace(
    *,
    atomic: pd.DataFrame,
    measurements: pd.DataFrame,
    seed: int,
    dataset: str = DATASET,
    mean_observation_rate: float = MEAN_OBSERVATION_RATE,
    s_max: int = S_MAX,
    method: str | None = None,
) -> tuple[EventTrace, pd.DataFrame, dict[str, Any]]:
    """Method-independent hybrid EventTrace (real R, controlled O/U)."""
    del method
    rng = np.random.default_rng(int(seed) + 13)
    atomic = atomic.copy()
    atomic["unit_id"] = atomic["unit_id"].astype(str)
    atomic["spatial_id"] = atomic["spatial_id"].astype(str)
    atomic["split"] = atomic["split"].astype(str)
    atomic["target_group"] = atomic["target_group"].astype(str)
    atomic["opportunity_stratum"] = atomic["opportunity_stratum"].astype(str)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    train = atomic.loc[atomic["split"] == "train"].copy()
    if train.empty:
        raise RuntimeError("City Scanner EventTrace requires non-empty train units")
    if train["spatial_id"].str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID leaked into spatial_id")

    win_of = window_id_by_time_index(train)
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
        }
        for r in atomic.itertuples(index=False)
        if str(r.split) == "train"
    }

    meas = measurements.copy()
    meas["client_id"] = meas["client_id"].astype(str)
    meas["unit_id"] = meas["unit_id"].astype(str)
    train_units = set(train["unit_id"].astype(str))
    meas = meas.loc[meas["unit_id"].isin(train_units)].copy()
    if meas["client_id"].str.startswith("NYCP").any():
        raise RuntimeError("vehicle/SensorID used as FL client")
    if set(meas["client_id"]) != set(train["spatial_id"]):
        raise RuntimeError("client_id must equal spatial_id on train units")

    clients_by_unit: dict[str, list[str]] = {}
    for r in meas.itertuples(index=False):
        clients_by_unit.setdefault(str(r.unit_id), []).append(str(r.client_id))
    for uid in clients_by_unit:
        clients_by_unit[uid] = sorted(set(clients_by_unit[uid]))

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
            p_obs_by_unit = {uid: float(mean_observation_rate) for uid in risk}
            o_flags = (
                rng.random(len(risk))
                < np.asarray([p_obs_by_unit[u] for u in risk], dtype=float)
                if risk
                else np.asarray([], dtype=bool)
            )
            observed = [uid for uid, flag in zip(risk, o_flags) if bool(flag)]
            usable = compute_usable_r3(
                rng=rng,
                registration_time=float(window_id) + 0.1,
                window_deadline=deadline,
                window_id=int(window_id),
                s_max=int(s_max),
                has_observations=bool(observed),
            )
            q_use = float(usable["U"])
            time_indices = sorted({int(unit_meta[uid]["time_index"]) for uid in risk})
            event_rows.append(
                {
                    "window_id": int(window_id),
                    "client_id": client_id,
                    "risk_set_unit_ids": list(risk),
                    "opportunity_features": {
                        "time_index": int(time_indices[0]) if time_indices else int(window_id),
                        "time_indices": time_indices,
                        "p_obs_true": float(mean_observation_rate),
                        "p_obs_true_by_unit": dict(p_obs_by_unit),
                        "q_use_true": q_use,
                        "device_tier": usable["device_tier"],
                        "prestate_only": True,
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
                    "oracle_p": float(mean_observation_rate),
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
                        "p_obs": float(mean_observation_rate),
                        "q_use": q_use,
                        "deadline_pass": int(usable["deadline_pass"]),
                        "staleness_tau": int(usable["tau"]),
                        "timestamp": str(meta["absolute_time"]),
                        "source": "cityscanner_visits+complete_aligned_controlled_OU",
                    }
                )

    events = pd.DataFrame(event_rows)
    if events.empty:
        raise RuntimeError("City Scanner EventTrace produced no client×window rows")
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
            "R from occupied City Scanner cell x 30min visits",
            "O/U Complete-aligned controlled transfer from E3",
            "100 windows = chronological bins of 1666 train slots",
            "method-independent",
        ),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    long_df = pd.DataFrame(long_rows)
    audit = {
        "n_windows": NUM_WINDOWS,
        "n_train_slots": EXPECTED_TRAIN_SLOTS,
        "window_map": "rank(time_index)*100//1666",
        "n_event_rows": int(len(events)),
        "n_long_rows": int(len(long_df)),
        "n_clients": int(events["client_id"].nunique()),
        "mean_observation_rate": float(mean_observation_rate),
        "s_max": int(s_max),
        "method_argument_ignored": True,
        "r_source": "client_measurements inner-joined to train atomic units",
        "o_source": "controlled Bernoulli p_obs=0.35 on R=1",
        "u_source": "e3.real_runner.stage2_r3.compute_usable_r3",
        "hashing_rule": "raven_mcs.simulation.event_trace.freeze_event_trace / compute_trace_hash",
    }
    return trace, long_df, audit
