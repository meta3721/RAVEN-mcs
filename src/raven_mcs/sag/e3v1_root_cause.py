"""E3-v1 root-cause diagnostics. Not a certificate. Not E3-v2."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from raven_mcs.sag.certificates import window_opportunity_masses
from raven_mcs.sag.oracle_ceiling import NUM_TOL, c_oracle_safe_from_pairs, c_real_support_from_pairs, ge_threshold

E3V1_K_RISK = 4
CF_IDS = ("CF0", "CF1", "CF2")


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return float("nan")
    return float(len(a & b) / len(union))


def lag_overlap(sets: Sequence[set], lag: int) -> float:
    if len(sets) <= lag:
        return float("nan")
    vals = [jaccard(sets[i], sets[i + lag]) for i in range(len(sets) - lag)]
    return float(np.mean(vals)) if vals else float("nan")


def persistence_lengths(sets: Sequence[set]) -> list[int]:
    runs: list[int] = []
    seen: dict[Any, int] = {}
    for window_set in sets:
        active = set(window_set)
        dead = [k for k in list(seen) if k not in active]
        for k in dead:
            runs.append(seen.pop(k))
        for k in active:
            seen[k] = seen.get(k, 0) + 1
    runs.extend(seen.values())
    return runs


def return_intervals(sets: Sequence[set]) -> list[int]:
    last: dict[Any, int] = {}
    gaps: list[int] = []
    for i, window_set in enumerate(sets):
        for key in window_set:
            if key in last:
                gaps.append(i - last[key])
            last[key] = i
    return gaps


def autocorr_lag1(xs: Sequence[float]) -> float:
    arr = np.asarray(xs, dtype=np.float64)
    if len(arr) < 3 or np.nanstd(arr) <= NUM_TOL:
        return float("nan")
    a = arr[:-1]
    b = arr[1:]
    if np.nanstd(a) <= NUM_TOL or np.nanstd(b) <= NUM_TOL:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def tv_distance(p: Mapping[Any, float], q: Mapping[Any, float]) -> float:
    keys = set(p) | set(q)
    if not keys:
        return float("nan")
    return 0.5 * float(sum(abs(float(p.get(k, 0.0)) - float(q.get(k, 0.0))) for k in keys))


def as_prob(mass: Mapping[Any, float]) -> dict[Any, float]:
    tot = float(sum(mass.values()))
    if tot <= NUM_TOL:
        return {k: 0.0 for k in mass}
    return {k: float(v) / tot for k, v in mass.items()}


def pair_from_unit(uid: str, unit_meta: Mapping[str, dict[str, str]]) -> tuple[str, str] | None:
    rec = unit_meta.get(str(uid))
    if rec is None:
        return None
    return str(rec["client"]), str(rec["stratum"])


def active_pairs_from_units(unit_ids: Iterable[str], unit_meta: Mapping[str, dict[str, str]]) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for uid in unit_ids:
        pair = pair_from_unit(uid, unit_meta)
        if pair is not None:
            out.add(pair)
    return out


def realized_mass_from_units(unit_ids: Sequence[str], unit_meta: Mapping[str, dict[str, str]]) -> dict[tuple[str, str], float]:
    pairs = []
    for uid in unit_ids:
        pair = pair_from_unit(uid, unit_meta)
        if pair is not None:
            pairs.append(pair)
    return window_opportunity_masses(pairs)


def oracle_from_mass(
    mass: Mapping[tuple[str, str], float],
    pi_tar: Mapping[tuple[str, str], float],
    pi_safe: float,
) -> dict[str, float]:
    keys = [(k, s) for (k, s), v in pi_tar.items() if float(v) > NUM_TOL]
    tar = [float(pi_tar[key]) for key in keys]
    realized = [float(mass.get(key, 0.0)) for key in keys]
    c_real, n_real, n_pos, tot = c_real_support_from_pairs(tar, realized)
    c_oracle, n_safe = c_oracle_safe_from_pairs(tar, realized, pi_safe)
    return {
        "C_real_support": c_real,
        "C_oracle_safe": c_oracle,
        "n_real_positive_pairs": n_real,
        "n_real_pi_safe_pairs": n_safe,
        "n_target_positive_pairs": n_pos,
        "target_mass_total": tot,
        "active_pair_count": len({key for key, m in mass.items() if m > NUM_TOL}),
        "target_mass_weighted_support": c_real,
    }


def unit_meta_from_atomic(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in atomic.itertuples(index=False):
        client = spatial_to_client.get(str(row.spatial_id))
        if client is None:
            continue
        out[str(row.unit_id)] = {
            "client": str(client),
            "stratum": str(row.opportunity_stratum),
            "spatial": str(row.spatial_id),
            "split": str(row.split),
            "time_index": str(int(row.time_index)),
        }
    return out


def natural_windows_from_atomic(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    *,
    split: str | None = None,
) -> list[dict[str, Any]]:
    work = atomic.copy()
    if split is not None:
        work = work.loc[work["split"].astype(str) == split]
    work["absolute_time"] = pd.to_datetime(work["absolute_time"], utc=True)
    rows: list[dict[str, Any]] = []
    for time_index, chunk in work.groupby(work["time_index"].astype(int), sort=True):
        units = [str(u) for u in chunk["unit_id"].tolist()]
        ts = pd.Timestamp(chunk["absolute_time"].min())
        clients = sorted({spatial_to_client.get(str(s), "") for s in chunk["spatial_id"].astype(str)})
        clients = [c for c in clients if c]
        rows.append(
            {
                "time_index": int(time_index),
                "window_start_utc": ts.isoformat(),
                "n_units": len(units),
                "n_users": int(chunk["spatial_id"].nunique()),
                "n_clients": len(clients),
                "unit_ids": units,
                "split": str(chunk["split"].iloc[0]),
            }
        )
    return rows


def e3v1_windows_from_trace(
    events: pd.DataFrame,
    unit_meta: Mapping[str, dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for window_id, chunk in events.groupby(events["window_id"].astype(int), sort=True):
        units: list[str] = []
        for risk in chunk["risk_set_unit_ids"].tolist():
            if isinstance(risk, (list, tuple, np.ndarray)):
                units.extend(str(u) for u in risk)
        rows.append(
            {
                "window_id": int(window_id),
                "n_units": len(units),
                "n_clients": int(chunk["client_id"].nunique()),
                "unit_ids": units,
            }
        )
    return rows


def subsample_within_window(
    unit_ids: Sequence[str],
    unit_meta: Mapping[str, dict[str, str]],
    *,
    k: int,
    rng: np.random.Generator,
) -> list[str]:
    by_client: dict[str, list[str]] = defaultdict(list)
    for uid in unit_ids:
        rec = unit_meta.get(str(uid))
        if rec is None:
            continue
        by_client[str(rec["client"])].append(str(uid))
    chosen: list[str] = []
    for client in sorted(by_client):
        pool = sorted(set(by_client[client]))
        take = min(int(k), len(pool))
        if take <= 0:
            continue
        if take < len(pool):
            idx = rng.choice(len(pool), size=take, replace=False)
            chosen.extend(pool[int(i)] for i in idx)
        else:
            chosen.extend(pool)
    return chosen


def summarize_temporal(sets: Sequence[set], masses: Sequence[float], label: str, dataset: str) -> dict[str, Any]:
    persist = persistence_lengths(sets)
    gaps = return_intervals(sets)
    counts = [len(s) for s in sets]
    arr = np.asarray(masses, dtype=np.float64)
    variation = float(np.mean(np.abs(np.diff(arr)))) if len(arr) > 1 else float("nan")
    return {
        "dataset": dataset,
        "regime": label,
        "n_windows": len(sets),
        "mean_active_pair_count": float(np.mean(counts)) if counts else float("nan"),
        "median_active_pair_count": float(np.median(counts)) if counts else float("nan"),
        "lag1_jaccard": lag_overlap(sets, 1),
        "lag2_jaccard": lag_overlap(sets, 2),
        "mean_persistence_length": float(np.mean(persist)) if persist else float("nan"),
        "median_persistence_length": float(np.median(persist)) if persist else float("nan"),
        "mean_return_interval": float(np.mean(gaps)) if gaps else float("nan"),
        "opportunity_mass_autocorr_lag1": autocorr_lag1(masses),
        "window_to_window_mass_variation": variation,
    }


def activation_stats(
    window_pairs: Sequence[set[tuple[str, str]]],
    pi_tar: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    pos = [(k, s) for (k, s), v in pi_tar.items() if float(v) > NUM_TOL]
    n_w = max(len(window_pairs), 1)
    freq = {key: float(sum(1 for s in window_pairs if key in s) / n_w) for key in pos}
    never = [key for key, f in freq.items() if f <= NUM_TOL]
    rare = [key for key, f in freq.items() if 0 < f < 0.10]
    activated_mass = float(sum(float(pi_tar[k]) for k, f in freq.items() if f > NUM_TOL))
    tot = float(sum(float(pi_tar[k]) for k in pos)) or float("nan")
    return {
        "n_target_positive_pairs": len(pos),
        "n_never_activated": len(never),
        "n_rarely_activated": len(rare),
        "mean_activation_frequency": float(np.mean(list(freq.values()))) if freq else float("nan"),
        "support_coverage_ratio": float((len(pos) - len(never)) / len(pos)) if pos else float("nan"),
        "target_mass_ever_activated": activated_mass,
        "target_mass_never_activated": float(tot - activated_mass) if np.isfinite(tot) else float("nan"),
        "freq": freq,
        "target_mass_total": tot,
    }
