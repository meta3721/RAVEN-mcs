"""Pair-state V2 emission for the unified E3 runner."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.semantic_alignment.constants import PAIR_STATE_SCHEMA_VERSION
from raven_mcs.metrics.distribution import delta_pair
from raven_mcs.utils.hashing import sha256_json

REQUIRED_COLUMNS_V2 = [
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
    "eventtrace_hash",
    "config_hash",
    "schema_version",
]


def pair_state_schema_v2() -> dict[str, Any]:
    return {
        "schema_version": PAIR_STATE_SCHEMA_VERSION,
        "required_columns": REQUIRED_COLUMNS_V2,
        "formula": {
            "Delta_pair": "||Pi_hat - pi_tar||_1",
            "code": "raven_mcs.metrics.distribution.delta_pair",
        },
        "outputs": ["pair_state.parquet", "pair_metric_summary.json"],
    }


def emit_pair_state_from_trace(
    *,
    events: pd.DataFrame,
    dataset: str,
    seed: int,
    scenario: str,
    method: str,
    target_mu: dict[str, float],
    unit_to_group: dict[str, str],
    eventtrace_hash: str | None,
    config_hash: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Emit per-window pair masses from observed units vs frozen target mu (group-level pairs)."""
    groups = sorted(target_mu)
    rows: list[dict[str, Any]] = []
    for window_id, wdf in events.groupby("window_id"):
        obs_counts = {g: 0.0 for g in groups}
        for _, rec in wdf.iterrows():
            observed = rec["observed_unit_ids"] or []
            if isinstance(observed, str):
                observed = json_loads_list(observed)
            for uid in observed:
                g = unit_to_group.get(str(uid))
                if g in obs_counts:
                    obs_counts[g] += 1.0
        total_obs = float(sum(obs_counts.values()))
        for g in groups:
            est = (obs_counts[g] / total_obs) if total_obs > 0 else 0.0
            tar = float(target_mu[g])
            rows.append(
                {
                    "dataset": dataset,
                    "seed": int(seed),
                    "scenario": scenario,
                    "method": method,
                    "window": int(window_id),
                    "pair_id": g,
                    "source_group": g,
                    "target_group": g,
                    "observed_pair_mass": float(obs_counts[g]),
                    "estimated_pair_mass": float(est),
                    "target_pair_mass": tar,
                    "support_mask": True,
                    "normalization_denominator": total_obs,
                    "validity_mask": True,
                    "eventtrace_hash": eventtrace_hash,
                    "config_hash": config_hash,
                    "schema_version": PAIR_STATE_SCHEMA_VERSION,
                }
            )
    frame = pd.DataFrame(rows)
    if frame.empty:
        summary = {
            "Delta_pair": 0.0,
            "pair_support_size": 0,
            "schema_version": PAIR_STATE_SCHEMA_VERSION,
            "status": "EMPTY",
        }
        return frame, summary

    # Aggregate across windows
    est = frame.groupby("pair_id")["estimated_pair_mass"].sum().reindex(groups).fillna(0.0).to_numpy()
    tar = frame.groupby("pair_id")["target_pair_mass"].mean().reindex(groups).fillna(0.0).to_numpy()
    if float(est.sum()) > 0:
        est = est / float(est.sum())
    if float(tar.sum()) > 0:
        tar = tar / float(tar.sum())
    dpair = float(delta_pair(est, tar))
    summary = {
        "Delta_pair": dpair,
        "Delta_c_s": dpair,
        "pair_support_size": int(len(groups)),
        "pi_hat_hash": sha256_json({"groups": groups, "pi_hat": est.tolist()}),
        "pi_tar_hash": sha256_json({"groups": groups, "pi_tar": tar.tolist()}),
        "schema_version": PAIR_STATE_SCHEMA_VERSION,
        "eventtrace_hash": eventtrace_hash,
        "config_hash": config_hash,
        "status": "OK",
    }
    return frame, summary


def json_loads_list(value: str) -> list:
    import json

    return list(json.loads(value))
