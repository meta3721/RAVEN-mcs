"""Pair-level sufficient-statistic materialization for Delta_pair / Delta_c-s."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from raven_mcs.metrics.distribution import delta_c_s, delta_pair
from raven_mcs.utils.hashing import sha256_json

PAIR_STATE_SCHEMA_VERSION = "E3_PAIR_STATE_SCHEMA_V1"

REQUIRED_COLUMNS = [
    "dataset",
    "seed",
    "scenario",
    "method",
    "window",
    "pair_id",
    "source_group",
    "target_group",
    "observed_pair_mass",
    "estimated_pair_mass",
    "target_pair_mass",
    "support_mask",
    "normalization_denominator",
    "validity_mask",
]


def pair_state_schema() -> dict[str, Any]:
    return {
        "schema_version": PAIR_STATE_SCHEMA_VERSION,
        "formula": {
            "Delta_pair": "||Pi_hat - pi_tar||_1",
            "Delta_c_s": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
            "code": [
                "raven_mcs.metrics.distribution.delta_pair",
                "raven_mcs.metrics.distribution.delta_c_s",
            ],
        },
        "required_columns": REQUIRED_COLUMNS,
        "aggregation": {
            "Pi_hat": "sum estimated_pair_mass over windows with validity_mask, then renormalize",
            "pi_tar": "sum target_pair_mass over same support, then renormalize",
        },
        "information_boundary": [
            "no future/test labels in estimated_pair_mass construction",
            "target_pair_mass from frozen public target only",
            "no post-delivery private features",
        ],
    }


def normalize_mass(mass: np.ndarray, eps: float = 0.0) -> np.ndarray:
    m = np.asarray(mass, dtype=np.float64)
    m = np.where(np.isfinite(m) & (m >= 0), m, 0.0)
    total = float(m.sum())
    if total <= eps:
        return np.zeros_like(m)
    return m / total


def build_pair_state_frame(
    *,
    dataset: str,
    seed: int,
    scenario: str,
    method: str,
    window: int,
    pair_ids: Sequence[str],
    source_groups: Sequence[str | int],
    target_groups: Sequence[str | int],
    observed_pair_mass: Sequence[float],
    estimated_pair_mass: Sequence[float],
    target_pair_mass: Sequence[float],
    support_mask: Sequence[bool] | None = None,
    validity_mask: Sequence[bool] | None = None,
) -> pd.DataFrame:
    n = len(pair_ids)
    if not all(
        len(x) == n
        for x in (
            source_groups,
            target_groups,
            observed_pair_mass,
            estimated_pair_mass,
            target_pair_mass,
        )
    ):
        raise ValueError("pair-state arrays must share length")
    support = np.ones(n, dtype=bool) if support_mask is None else np.asarray(support_mask, dtype=bool)
    valid = np.ones(n, dtype=bool) if validity_mask is None else np.asarray(validity_mask, dtype=bool)
    est = np.asarray(estimated_pair_mass, dtype=np.float64)
    tar = np.asarray(target_pair_mass, dtype=np.float64)
    if np.any(~np.isfinite(est)) or np.any(~np.isfinite(tar)):
        raise ValueError("pair masses must be finite")
    if np.any(est[support & valid] < 0) or np.any(tar[support & valid] < 0):
        raise ValueError("pair masses must be nonnegative on supported valid pairs")
    denom = float(est[support & valid].sum())
    rows = {
        "dataset": dataset,
        "seed": int(seed),
        "scenario": scenario,
        "method": method,
        "window": int(window),
        "pair_id": list(map(str, pair_ids)),
        "source_group": list(source_groups),
        "target_group": list(target_groups),
        "observed_pair_mass": np.asarray(observed_pair_mass, dtype=np.float64),
        "estimated_pair_mass": est,
        "target_pair_mass": tar,
        "support_mask": support,
        "normalization_denominator": denom,
        "validity_mask": valid,
    }
    return pd.DataFrame(rows)


def aggregate_run_pair_distributions(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Aggregate window-level pair masses to run-level Pi_hat and pi_tar on shared support."""
    if frame.empty:
        raise ValueError("empty pair state")
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"pair state missing columns: {missing}")
    active = frame.loc[frame["support_mask"].astype(bool) & frame["validity_mask"].astype(bool)]
    if active.empty:
        raise ValueError("no supported valid pairs")
    grouped = active.groupby("pair_id", sort=True)
    pair_ids = list(grouped.groups.keys())
    pi_hat = normalize_mass(np.asarray([grouped.get_group(p)["estimated_pair_mass"].sum() for p in pair_ids]))
    pi_tar = normalize_mass(np.asarray([grouped.get_group(p)["target_pair_mass"].sum() for p in pair_ids]))
    return pi_hat, pi_tar, pair_ids


def compute_pair_metrics_from_state(frame: pd.DataFrame) -> dict[str, Any]:
    pi_hat, pi_tar, pair_ids = aggregate_run_pair_distributions(frame)
    d_pair = delta_pair(pi_hat, pi_tar)
    # Optional client-stratum view when pair_id encodes client::stratum
    if all("::" in p for p in pair_ids):
        d_cs = delta_c_s(pi_hat, pi_tar)
    else:
        d_cs = d_pair
    return {
        "Delta_pair": float(d_pair),
        "Delta_c_s": float(d_cs),
        "pair_support_size": int(len(pair_ids)),
        "pi_hat_hash": sha256_json({"pair_ids": pair_ids, "pi_hat": pi_hat.tolist()}),
        "pi_tar_hash": sha256_json({"pair_ids": pair_ids, "pi_tar": pi_tar.tolist()}),
        "schema_version": PAIR_STATE_SCHEMA_VERSION,
    }


def emit_pair_metrics_payload(
    frame: pd.DataFrame,
    *,
    extras: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = compute_pair_metrics_from_state(frame)
    if extras:
        payload.update(dict(extras))
    return payload
