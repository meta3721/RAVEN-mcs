"""E3 deployment target: spatial × time-of-day groups; mu from TEST support."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.target import GroupMapper, TargetBuilder, audit_target_support
from raven_mcs.utils.hashing import sha256_json


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_time_block(group_id: str) -> int:
    """Parse trailing block index from 'spatial::blockK'."""
    text = str(group_id)
    if "::" not in text:
        raise ValueError(f"group_id not spatial×time: {text}")
    block = text.split("::")[-1]
    if block.startswith("block"):
        return int(block.replace("block", ""))
    raise ValueError(f"unrecognized time block in group_id: {text}")


def freeze_target_semantics(atomic: pd.DataFrame, *, dataset: str) -> dict[str, Any]:
    """Freeze spatial×time target from TEST support (no train-label dependence)."""
    if "target_group" not in atomic.columns:
        raise RuntimeError(f"{dataset}: missing target_group column")
    test = atomic.loc[atomic["split"].astype(str) == "test"].copy()
    if test.empty:
        raise RuntimeError(f"{dataset}: empty test split")

    # Ensure groups are spatial×time
    groups = test["target_group"].astype(str)
    sample = groups.iloc[0]
    if "::" not in sample:
        raise RuntimeError(f"{dataset}: target_group is not spatial×time ({sample})")
    n_time_only_like = groups.map(lambda g: g.count("::") == 0).sum()
    if n_time_only_like:
        raise RuntimeError(f"{dataset}: found time-only group ids")

    builder = TargetBuilder(group_mapper=GroupMapper(column="target_group"))
    masses = builder.build(atomic, split="test")
    errors = audit_target_support(masses)
    if errors:
        raise RuntimeError(f"{dataset} target audit failed: {errors}")

    group_mass = {str(k): float(v) for k, v in masses.group_mass.items()}
    # Head/Tail by protocol time-block rule (prediction-independent; matches Traffic block convention)
    head_groups = sorted([g for g in group_mass if parse_time_block(g) in {0, 1}])
    tail_groups = sorted([g for g in group_mass if parse_time_block(g) in {2, 3}])
    if not head_groups or not tail_groups:
        raise RuntimeError(f"{dataset}: Head/Tail partition empty")

    support_units = sorted(masses.atom_mass.index.astype(str).tolist())
    group_map = {
        str(r.unit_id): str(r.target_group)
        for r in test.loc[test["support_flag"].astype(bool)].itertuples(index=False)
    }

    payload = {
        "dataset": dataset,
        "atomic_unit_definition": "i=(spatial_unit, timestamp)",
        "group_definition": "h(i)=(spatial_unit, time_of_day_block)",
        "group_id_pattern": "spatial_id::block{0..3}",
        "mu_construction": "uniform over supported TEST atomic units; mu_g = count(g)/count(all)",
        "mu_not_from": [
            "training label magnitude",
            "training performance",
            "delivered-observation frequency",
            "post hoc E3 results",
        ],
        "n_test_atomic_supported": int(len(support_units)),
        "n_spatial_units_in_test": int(test.loc[test["support_flag"].astype(bool), "spatial_id"].nunique()),
        "n_groups": int(len(group_mass)),
        "mu": group_mass,
        "mu_sum": float(sum(group_mass.values())),
        "head_groups": head_groups,
        "tail_groups": tail_groups,
        "head_tail_rule": "time_block in {0,1}=Head; {2,3}=Tail (protocol, not performance)",
        "hashes": {
            "atomic_support_hash": sha256_json(support_units),
            "group_map_hash": sha256_json(group_map),
            "mu_vector_hash": sha256_json(group_mass),
            "head_tail_hash": sha256_json({"head": head_groups, "tail": tail_groups}),
        },
        "uses_e1_time_only_target": False,
    }
    # Normalize status strings
    if dataset == "sensorscope":
        payload["status"] = "SENSORSCOPE_TARGET_SEMANTICS_READY"
    elif dataset == "uair":
        payload["status"] = "UAIR_TARGET_SEMANTICS_READY"
    else:
        payload["status"] = f"{dataset.upper()}_TARGET_SEMANTICS_READY"
    return payload


def assert_no_train_label_mu(atomic: pd.DataFrame, mu: dict[str, float]) -> None:
    """Guard: mu must match TEST support counts, not train label frequencies."""
    test = atomic.loc[
        (atomic["split"].astype(str) == "test") & atomic["support_flag"].astype(bool)
    ]
    counts = test["target_group"].astype(str).value_counts()
    expected = (counts / float(counts.sum())).to_dict()
    for g, v in expected.items():
        if abs(float(mu.get(g, 0.0)) - float(v)) > 1e-9:
            raise AssertionError(f"mu mismatch vs test support for group {g}")
