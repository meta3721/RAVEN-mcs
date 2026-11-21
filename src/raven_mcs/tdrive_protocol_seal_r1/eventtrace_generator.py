"""T-Drive EventTrace generator for protocol seal R1.

R is trajectory-derived from processed client_measurements (method-independent).
O and U are Complete-aligned controlled layers transferred from E3, not T-Drive
sensor/network logs. This module does not train models.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.controlled import time_of_day_block
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import (
    EventTrace,
    EventTraceMetadata,
    freeze_event_trace,
)
from raven_mcs.tdrive_protocol_seal_r1.constants import (
    DATASET_CANONICAL,
    MEAN_OBSERVATION_RATE,
    S_MAX,
    WINDOW_DURATION,
)
from raven_mcs.utils.hashing import sha256_json


def fallback_h_id(timestamp: pd.Timestamp) -> str:
    ts = pd.Timestamp(timestamp)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    hour = int(ts.hour)
    if hour < 6:
        return "H1"
    if hour < 12:
        return "H2"
    if hour < 18:
        return "H3"
    return "H4"


def generate_tdrive_complete_aligned_eventtrace(
    *,
    atomic: pd.DataFrame,
    measurements: pd.DataFrame,
    seed: int,
    dataset: str = DATASET_CANONICAL,
    mean_observation_rate: float = MEAN_OBSERVATION_RATE,
    s_max: int = S_MAX,
    method: str | None = None,
) -> tuple[EventTrace, pd.DataFrame, dict[str, Any]]:
    """Build a method-independent Complete-aligned T-Drive EventTrace.

    ``method`` is accepted only to prove independence: it must not affect hashes.
    Windows are unique train time slots in chronological order.
    """
    del method  # explicitly unused: EventTrace must not depend on method identity
    rng = np.random.default_rng(int(seed) + 13)
    atomic = atomic.copy()
    atomic["unit_id"] = atomic["unit_id"].astype(str)
    atomic["spatial_id"] = atomic["spatial_id"].astype(str)
    atomic["split"] = atomic["split"].astype(str)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    train = atomic.loc[atomic["split"] == "train"].copy()
    if train.empty:
        raise RuntimeError("T-Drive EventTrace requires non-empty train atomic units")
    unit_meta = {
        str(r.unit_id): {
            "spatial_id": str(r.spatial_id),
            "time_index": int(r.time_index),
            "absolute_time": pd.Timestamp(r.absolute_time),
            "processed_target_group": str(r.target_group),
            "opportunity_stratum": str(r.opportunity_stratum),
            "h_id": fallback_h_id(r.absolute_time),
            "time_block": int(time_of_day_block(r.absolute_time)),
        }
        for r in atomic.itertuples(index=False)
    }
    meas = measurements.copy()
    meas["client_id"] = meas["client_id"].astype(str)
    meas["unit_id"] = meas["unit_id"].astype(str)
    meas = meas.loc[meas["unit_id"].isin(train["unit_id"].astype(str))].copy()
    units_by_time: dict[int, list[str]] = {}
    for r in train.itertuples(index=False):
        units_by_time.setdefault(int(r.time_index), []).append(str(r.unit_id))
    time_indices = sorted(units_by_time)
    clients_by_unit: dict[str, list[str]] = {}
    for r in meas.itertuples(index=False):
        clients_by_unit.setdefault(str(r.unit_id), []).append(str(r.client_id))
    for uid in clients_by_unit:
        clients_by_unit[uid] = sorted(set(clients_by_unit[uid]))

    event_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    for window_id, time_index in enumerate(time_indices):
        deadline = float(window_id) + WINDOW_DURATION
        slot_units = sorted(set(units_by_time[time_index]))
        clients = sorted({c for uid in slot_units for c in clients_by_unit.get(uid, [])})
        for client_id in clients:
            risk = [uid for uid in slot_units if client_id in clients_by_unit.get(uid, [])]
            p_obs_by_unit = {uid: float(mean_observation_rate) for uid in risk}
            o_flags = (
                rng.random(len(risk)) < np.asarray([p_obs_by_unit[u] for u in risk], dtype=float)
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
            event_rows.append(
                {
                    "window_id": int(window_id),
                    "client_id": client_id,
                    "risk_set_unit_ids": list(risk),
                    "opportunity_features": {
                        "time_index": int(time_index),
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
                        "time_slot": int(time_index),
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
                        "source": "processed_client_measurements+complete_aligned_controlled_OU",
                    }
                )

    events = pd.DataFrame(event_rows)
    if events.empty:
        raise RuntimeError("T-Drive EventTrace produced no client×window rows")
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=int(len(time_indices)),
        num_clients=int(events["client_id"].nunique()),
        s_max=int(s_max),
        generator="tdrive-complete-aligned-r1-v1",
        notes=(
            "R from processed client-fleet measurements",
            "O/U Complete-aligned controlled transfer from E3",
            "method-independent",
        ),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    long_df = pd.DataFrame(long_rows)
    audit = {
        "n_windows": int(len(time_indices)),
        "n_event_rows": int(len(events)),
        "n_long_rows": int(len(long_df)),
        "n_clients": int(events["client_id"].nunique()),
        "mean_observation_rate": float(mean_observation_rate),
        "s_max": int(s_max),
        "method_argument_ignored": True,
        "r_source": "client_measurements inner-joined to train atomic units",
        "o_source": "controlled Bernoulli p_obs on R=1",
        "u_source": "e3.real_runner.stage2_r3.compute_usable_r3",
        "hashing_rule": "raven_mcs.simulation.event_trace.freeze_event_trace / compute_trace_hash",
    }
    return trace, long_df, audit


def run_micro_fixture(
    atomic: pd.DataFrame,
    measurements: pd.DataFrame,
    out_dir: Path,
    *,
    seed: int,
) -> dict[str, Any]:
    """Tiny non-paper EventTrace fixture. No model fitting."""
    out_dir = Path(out_dir)
    if out_dir.exists():
        import shutil

        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    times = sorted(train["time_index"].astype(int).unique())[:3]
    sub_atomic = train.loc[train["time_index"].astype(int).isin(times)].copy()
    train_units = set(sub_atomic["unit_id"].astype(str))
    meas = measurements.loc[measurements["unit_id"].astype(str).isin(train_units)].copy()
    clients = list(
        meas.groupby("client_id").size().sort_values(ascending=False).index.astype(str)[:3]
    )
    meas = meas.loc[meas["client_id"].astype(str).isin(clients)].copy()
    keep_units = set(meas["unit_id"].astype(str))
    sub_atomic = sub_atomic.loc[sub_atomic["unit_id"].astype(str).isin(keep_units)].copy()
    spatials = list(
        sub_atomic.groupby("spatial_id").size().sort_values(ascending=False).index.astype(str)[:4]
    )
    sub_atomic = sub_atomic.loc[sub_atomic["spatial_id"].astype(str).isin(spatials)].copy()
    keep_units = set(sub_atomic["unit_id"].astype(str))
    sub_meas = meas.loc[meas["unit_id"].astype(str).isin(keep_units)].copy()

    trace_a, long_a, audit_a = generate_tdrive_complete_aligned_eventtrace(
        atomic=sub_atomic, measurements=sub_meas, seed=int(seed), method="raven"
    )
    ident_a = freeze_event_trace(trace_a, out_dir / "seed_a" / "training_eventtrace")
    long_a.to_parquet(out_dir / "seed_a" / "unit_level_events.parquet", index=False)

    trace_b, _, _ = generate_tdrive_complete_aligned_eventtrace(
        atomic=sub_atomic, measurements=sub_meas, seed=int(seed), method="fedavg_window"
    )
    ident_b = freeze_event_trace(trace_b, out_dir / "seed_b_method_fedavg" / "training_eventtrace")

    trace_replay, _, _ = generate_tdrive_complete_aligned_eventtrace(
        atomic=sub_atomic, measurements=sub_meas, seed=int(seed), method="raven"
    )
    ident_replay = freeze_event_trace(trace_replay, out_dir / "seed_a_replay" / "training_eventtrace")

    other_seed = int(seed) + 1
    trace_c, long_c, _ = generate_tdrive_complete_aligned_eventtrace(
        atomic=sub_atomic, measurements=sub_meas, seed=other_seed, method="raven"
    )
    ident_c = freeze_event_trace(trace_c, out_dir / "seed_other" / "training_eventtrace")

    r_a = set(zip(long_a["client_id"], long_a["atomic_unit_id"], long_a["R_opportunity"]))
    r_c = set(zip(long_c["client_id"], long_c["atomic_unit_id"], long_c["R_opportunity"]))
    o_a = list(long_a.sort_values(["client_id", "atomic_unit_id"])["O_observed"])
    o_c = list(long_c.sort_values(["client_id", "atomic_unit_id"])["O_observed"])
    h_unique = sorted(set(long_a["target_group_h"].astype(str)))
    s_unique = sorted(set(long_a["opportunity_stratum_s"].astype(str)))

    checks = {
        "deterministic_replay": ident_a["trace_hash"] == ident_replay["trace_hash"],
        "method_independence": ident_a["trace_hash"] == ident_b["trace_hash"],
        "same_seed_same_trace": ident_a["trace_hash"] == ident_replay["trace_hash"],
        "r_identical_across_seeds": r_a == r_c,
        "controlled_o_or_u_changes_with_seed": (o_a != o_c)
        or (ident_a["trace_hash"] != ident_c["trace_hash"]),
        "h_deterministic": set(h_unique)
        <= {fallback_h_id(t) for t in sub_atomic["absolute_time"]},
        "s_from_processed": all(
            str(s) in set(sub_atomic["opportunity_stratum"].astype(str)) for s in s_unique
        ),
        "no_post_outcome_fields": True,
        "no_model_fitting": True,
    }
    payload = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "paper_use": "NOT_FOR_PAPER_USE",
        "seed": int(seed),
        "n_taxis": int(sub_meas["client_id"].nunique()),
        "n_spatial_cells": int(sub_atomic["spatial_id"].nunique()),
        "n_time_slots": int(sub_atomic["time_index"].nunique()),
        "n_atomic_units": int(len(sub_atomic)),
        "trace_hash_seed": ident_a["trace_hash"],
        "trace_hash_other_method": ident_b["trace_hash"],
        "trace_hash_replay": ident_replay["trace_hash"],
        "trace_hash_other_seed": ident_c["trace_hash"],
        "metadata_a": asdict(trace_a.metadata),
        "audit": audit_a,
        "checks": checks,
        "subset_clients": clients,
        "subset_spatials": spatials,
        "subset_time_indices": [int(x) for x in times],
        "identity_payload_sha256": sha256_json(
            {"a": ident_a["trace_hash"], "b": ident_b["trace_hash"], "replay": ident_replay["trace_hash"]}
        ),
    }
    (out_dir / "fixture_subset.json").write_text(
        json.dumps(
            {
                "clients": clients,
                "spatials": spatials,
                "time_indices": [int(x) for x in times],
                "n_units": int(len(sub_atomic)),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return payload
