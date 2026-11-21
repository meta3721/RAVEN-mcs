"""Dataset-specific Complete-aligned EventTrace generator for SensorScope / U-Air."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata, freeze_event_trace


def utc_block(hour: int) -> int:
    h = int(hour) % 24
    if h < 6:
        return 0
    if h < 12:
        return 1
    if h < 18:
        return 2
    return 3


def _stable_int(text: str) -> int:
    return int.from_bytes(str(text).encode("utf-8"), "little", signed=False) % (2**31 - 1)


def _utc_hour(ts: Any) -> int:
    t = pd.Timestamp(ts)
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
    else:
        t = t.tz_convert("UTC")
    return int(t.hour)


def freeze_public_target_from_atomic(
    atomic: pd.DataFrame,
    *,
    dataset: str,
) -> dict[str, Any]:
    """Freeze coarse UTC-block public target using TRAIN split masses only."""
    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    times = pd.to_datetime(train["absolute_time"], utc=True)
    blocks = times.dt.hour.map(utc_block)
    counts = blocks.value_counts().reindex([0, 1, 2, 3], fill_value=0).astype(float)
    masses = (counts / max(float(counts.sum()), 1.0)).to_dict()
    head = sorted(masses, key=lambda g: masses[g], reverse=True)[:2]
    tail = [g for g in (0, 1, 2, 3) if g not in head]
    return {
        "dataset": dataset,
        "group_definition": "repeatable_utc_time_of_day_4",
        "group_ids": [0, 1, 2, 3],
        "group_names": ["UTC_00_06", "UTC_06_12", "UTC_12_18", "UTC_18_24"],
        "mu": {str(k): float(v) for k, v in masses.items()},
        "head_groups": head,
        "tail_groups": tail,
        "construction": "train_split_utc_block_mass_only_no_test_labels",
        "n_train_atomic": int(len(train)),
    }


def freeze_opportunity_strata_from_atomic(atomic: pd.DataFrame, *, dataset: str) -> dict[str, Any]:
    strata = sorted(atomic["opportunity_stratum"].astype(str).unique().tolist())
    return {
        "dataset": dataset,
        "definition": "processed opportunity_stratum = spatial_id::time_block::weekday_flag",
        "n_strata": len(strata),
        "support_hash_n": len(strata),
        "deterministic_construction": True,
        "no_target_leakage": True,
        "note": "Stratum labels come from processed public features only; not model residuals.",
    }


def _client_unit_pools(
    atomic: pd.DataFrame,
    clients: pd.DataFrame,
) -> dict[str, list[str]]:
    client_units = (
        clients.loc[clients["split"].astype(str) == "train", ["client_id", "unit_id"]]
        .drop_duplicates()
        .astype(str)
    )
    # Restrict to atomic train units that exist
    train_units = set(atomic.loc[atomic["split"].astype(str) == "train", "unit_id"].astype(str))
    pools: dict[str, list[str]] = {}
    for cid, grp in client_units.groupby("client_id"):
        units = [u for u in grp["unit_id"].tolist() if u in train_units]
        pools[str(cid)] = sorted(units)
    return pools


def generate_complete_aligned_eventtrace(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    clients: pd.DataFrame,
    seed: int,
    num_windows: int,
    s_max: int = 5,
    mean_observation_rate: float = 0.20,
    mean_usable_rate: float = 0.60,
) -> EventTrace:
    """Deterministic Complete-aligned EventTrace (no test outcomes used)."""
    rng = np.random.default_rng(int(seed) + 17 * (0 if dataset == "sensorscope" else 1))
    pools = _client_unit_pools(atomic, clients)
    client_ids = sorted(pools)
    if not client_ids:
        raise RuntimeError(f"no client unit pools for {dataset}")

    # Align opportunity/observation toward underrepresented UTC blocks using train mu.
    target = freeze_public_target_from_atomic(atomic, dataset=dataset)
    mu = np.asarray([target["mu"][str(g)] for g in range(4)], dtype=np.float64)
    # Higher sampling pressure on low-mu blocks (complete-aligned scientific intent).
    align = (mu.max() + 1e-6) / (mu + 1e-6)
    align = align / align.mean()

    unit_block = {}
    train = atomic.loc[atomic["split"].astype(str) == "train"]
    for row in train.itertuples(index=False):
        unit_block[str(row.unit_id)] = utc_block(_utc_hour(row.absolute_time))

    rows: list[dict[str, Any]] = []
    for window_id in range(int(num_windows)):
        for client_id in client_ids:
            pool = pools[client_id]
            if not pool:
                continue
            # Risk set: deterministic sample of units for this window
            k = min(8, len(pool))
            # Cyclic deterministic slice + small rng shuffle of indices
            start = (window_id * 3 + _stable_int(client_id) % 7) % max(len(pool), 1)
            risk = [pool[(start + j) % len(pool)] for j in range(k)]
            # Observation bias by alignment weights of units' UTC blocks
            p_obs = []
            for uid in risk:
                g = unit_block.get(uid, window_id % 4)
                p_obs.append(float(np.clip(mean_observation_rate * align[g], 0.02, 0.95)))
            o_flags = rng.random(len(risk)) < np.asarray(p_obs)
            observed = [u for u, flag in zip(risk, o_flags) if flag]
            # Usable aligned similarly
            p_use = float(np.clip(mean_usable_rate * float(np.mean([align[unit_block.get(u, 0)] for u in (observed or risk)])), 0.05, 0.95))
            compute_success = True
            network_success = bool(rng.random() < 0.98)
            usable = bool(network_success and compute_success and (rng.random() < p_use) and len(observed) > 0)
            # Stage-2 eligibility: failed attempt => U=0 with attempt still logged via O
            downloaded = int(window_id)  # fresh download; tau=0 dominant (aligned delivery)
            if rng.random() < 0.15:
                downloaded = max(0, window_id - int(rng.integers(1, s_max + 1)))
            tau = int(window_id - downloaded)
            if tau > s_max:
                usable = False
            rows.append(
                {
                    "window_id": int(window_id),
                    "client_id": client_id,
                    "risk_set_unit_ids": list(risk),
                    "opportunity_features": {
                        "hour_block": int(window_id % 4),
                        "dataset": dataset,
                        "scenario": "complete_aligned",
                    },
                    "observed_unit_ids": list(observed),
                    "O": {unit: True for unit in observed},
                    "registration_time": float(window_id) + 0.1 * (client_ids.index(client_id)),
                    "downloaded_version": downloaded,
                    "model_age": float(tau),
                    "tau": tau,
                    "device_profile": f"{dataset}-device",
                    "network_profile": f"{dataset}-net",
                    "compute_success": compute_success,
                    "compute_duration": float(rng.uniform(0.1, 1.0)),
                    "network_success": network_success,
                    "network_duration": float(rng.uniform(0.05, 0.5)),
                    "arrival_time": float(window_id) + 0.5 + 0.01 * client_ids.index(client_id),
                    "U": int(usable),
                    "raw_workload": float(len(observed)),
                    "oracle_p": float(np.mean(p_obs)) if p_obs else float(mean_observation_rate),
                    "oracle_q": float(p_use),
                    "hidden_confounder": 0.0,
                }
            )
    events = pd.DataFrame(rows)
    meta = EventTraceMetadata(
        dataset=dataset,
        seed=int(seed),
        num_windows=int(num_windows),
        num_clients=len(client_ids),
        s_max=int(s_max),
        generator="e3-complete-aligned-v1",
        notes=(
            "E3 Complete-aligned controlled generator",
            "deterministic given seed+dataset+num_windows",
            "no test outcomes used",
        ),
    )
    trace = EventTrace(events=events, metadata=meta)
    trace.validate()
    return trace


def materialize_canary_trace_probe(
    *,
    dataset: str,
    atomic: pd.DataFrame,
    clients: pd.DataFrame,
    out_dir,
    seed: int,
    num_windows: int,
) -> dict[str, Any]:
    """Write a short probe EventTrace proving generator readiness (not a formal run)."""
    from pathlib import Path

    out_dir = Path(out_dir)
    if out_dir.exists():
        # allow overwrite of probe only by clearing empty or regenerating via replace
        import shutil

        shutil.rmtree(out_dir)
    trace = generate_complete_aligned_eventtrace(
        dataset=dataset,
        atomic=atomic,
        clients=clients,
        seed=seed,
        num_windows=num_windows,
    )
    identity = freeze_event_trace(trace, out_dir)
    return {
        "dataset": dataset,
        "seed": int(seed),
        "num_windows": int(num_windows),
        "n_event_rows": int(len(trace.events)),
        "identity": identity,
        "status": "EVENTTRACE_PATH_READY",
    }
