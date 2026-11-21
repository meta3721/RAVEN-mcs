"""Load frozen spatial×time target into the production runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.e3.semantic_alignment.target_semantics import (
    freeze_target_semantics,
    parse_time_block,
)
from raven_mcs.e3.target_pair.constants import FROZEN_TARGET_ARTIFACTS
from raven_mcs.e3.target_pair.errors import HeadTailWiringError, TargetWiringError
from raven_mcs.utils.hashing import sha256_json


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_target_artifact(root: Path, dataset: str) -> dict[str, Any]:
    """Load frozen target semantics; STOP if missing (no silent time-only rebuild)."""
    rel = FROZEN_TARGET_ARTIFACTS.get(str(dataset).lower())
    if rel is None:
        # Fixture / non-paper datasets may carry an inline frozen artifact
        raise TargetWiringError(
            f"TARGET_ARTIFACT_MISSING: no frozen path registered for dataset={dataset}"
        )
    path = Path(root) / rel
    if not path.is_file():
        raise TargetWiringError(f"TARGET_ARTIFACT_MISSING: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("uses_e1_time_only_target") is True:
        raise TargetWiringError("TARGET_WIRING_ERROR: artifact is time-only")
    if int(payload.get("n_groups", 0)) <= 4 and str(dataset).lower() in {"sensorscope", "uair"}:
        # SensorScope/U-Air must be spatial×time with >>4 groups
        raise TargetWiringError(
            f"TARGET_WIRING_ERROR: n_groups={payload.get('n_groups')} looks time-only for {dataset}"
        )
    sample_g = next(iter(payload.get("mu", {})), "")
    if "::" not in str(sample_g):
        raise TargetWiringError("TARGET_WIRING_ERROR: group ids are not spatial×time")
    payload["_artifact_path"] = str(path.relative_to(root)).replace("\\", "/")
    payload["_artifact_sha256"] = _sha_file(path)
    return payload


def freeze_fixture_target(atomic: pd.DataFrame, *, dataset: str = "fixture") -> dict[str, Any]:
    """Freeze spatial×time target for a non-paper correctness fixture."""
    return freeze_target_semantics(atomic, dataset=dataset)


def align_mu_to_dataset(
    dataset: ProcessedDataset,
    target_artifact: dict[str, Any],
) -> tuple[np.ndarray, list[str], dict[str, int]]:
    """Align frozen mu dict onto ProcessedDataset integer group encoding.

    Returns (mu_vector, group_id_by_index, group_str_to_int).
    Groups present in the dataset but absent from frozen TEST mu receive mass 0.
    """
    # Dataset encoding order
    raw_groups = sorted(dataset.atomic_df["target_group"].astype(str).unique())
    g2i = {g: i for i, g in enumerate(raw_groups)}
    n = len(raw_groups)
    mu_dict = {str(k): float(v) for k, v in target_artifact.get("mu", {}).items()}
    if not mu_dict:
        raise TargetWiringError("TARGET_WIRING_ERROR: empty mu in frozen artifact")
    # Frozen TEST groups must exist in dataset encoding
    missing = [g for g in mu_dict if g not in g2i]
    if missing:
        raise TargetWiringError(
            f"TARGET_WIRING_ERROR: frozen groups missing from dataset encoding: {missing[:5]}"
        )
    mu = np.zeros(n, dtype=np.float64)
    for g, v in mu_dict.items():
        mu[g2i[g]] = float(v)
    total = float(mu.sum())
    if total <= 0:
        raise TargetWiringError("TARGET_WIRING_ERROR: mu sums to 0 after alignment")
    if abs(total - 1.0) > 1e-8:
        mu = mu / total
    return mu, raw_groups, g2i


def resolve_head_tail(
    target_artifact: dict[str, Any],
    group_str_to_int: dict[str, int],
) -> dict[str, Any]:
    """Map frozen Head/Tail string groups onto production integer ids."""
    head = [str(g) for g in target_artifact.get("head_groups") or []]
    tail = [str(g) for g in target_artifact.get("tail_groups") or []]
    if not head or not tail:
        raise HeadTailWiringError("HEAD_TAIL_WIRING_ERROR: empty Head/Tail in artifact")
    # Reject time-only half-split defaults for spatial×time artifacts
    if all(g.isdigit() for g in head + tail):
        raise HeadTailWiringError(
            "HEAD_TAIL_WIRING_ERROR: integer-only Head/Tail is not the frozen spatial×time partition"
        )
    missing = [g for g in head + tail if g not in group_str_to_int]
    if missing:
        raise HeadTailWiringError(
            f"HEAD_TAIL_WIRING_ERROR: groups not in dataset encoding: {missing[:5]}"
        )
    head_ids = sorted({group_str_to_int[g] for g in head})
    tail_ids = sorted({group_str_to_int[g] for g in tail})
    return {
        "head_groups": head,
        "tail_groups": tail,
        "head_group_ids": head_ids,
        "tail_group_ids": tail_ids,
        "head_hash": sha256_json(head),
        "tail_hash": sha256_json(tail),
        "rule": target_artifact.get("head_tail_rule"),
        "n_head": len(head),
        "n_tail": len(tail),
    }


def production_target_bundle(
    *,
    root: Path,
    dataset_name: str,
    dataset: ProcessedDataset,
    fixture_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve the production target wiring bundle for a run."""
    name = str(dataset_name).lower()
    if name in FROZEN_TARGET_ARTIFACTS:
        artifact = load_frozen_target_artifact(root, name)
    elif fixture_artifact is not None:
        artifact = dict(fixture_artifact)
        artifact["_artifact_path"] = "inline_fixture_freeze"
        artifact["_artifact_sha256"] = sha256_json(
            {k: artifact[k] for k in ("mu", "head_groups", "tail_groups", "n_groups") if k in artifact}
        )
    elif name in {"fixture", "traffic"} or name.startswith("e3_"):
        # Traffic has no separate R2 artifact file in-repo; freeze from processed atomic
        # spatial×time groups (same construction rule as SensorScope/U-Air).
        artifact = freeze_fixture_target(dataset.atomic_df, dataset=name)
        artifact["_artifact_path"] = "freeze_fixture_target(atomic)"
        artifact["_artifact_sha256"] = sha256_json(
            {k: artifact[k] for k in ("mu", "head_groups", "tail_groups", "n_groups") if k in artifact}
        )
    else:
        raise TargetWiringError(f"TARGET_ARTIFACT_MISSING: dataset={dataset_name}")

    if artifact.get("uses_e1_time_only_target") is True:
        raise TargetWiringError("TARGET_WIRING_ERROR: refusing time-only target")

    mu, group_ids, g2i = align_mu_to_dataset(dataset, artifact)
    # Production n_groups is the frozen TEST support cardinality for paper datasets;
    # for fixtures use dataset encoding length (must match spatial×time groups).
    n_groups_frozen = int(artifact["n_groups"])
    n_groups_runtime = int(len(group_ids))
    if name in {"sensorscope", "uair"}:
        # Runtime encoding may include train-only groups with mu=0; n_groups for P2
        # must match debt/composition length = runtime encoding size, while evidence
        # records frozen TEST n_groups separately.
        if n_groups_frozen != len(artifact["mu"]):
            raise TargetWiringError("TARGET_WIRING_ERROR: frozen n_groups != len(mu)")
    ht = resolve_head_tail(artifact, g2i)
    # Hard reject: production must not claim n_groups==4 time-only for SS/UA
    if name in {"sensorscope", "uair"} and n_groups_frozen == 4:
        raise TargetWiringError("TARGET_WIRING_ERROR: n_groups=4 time-only forbidden")

    return {
        "dataset": name,
        "artifact_path": artifact.get("_artifact_path"),
        "artifact_sha256": artifact.get("_artifact_sha256"),
        "n_groups_frozen": n_groups_frozen,
        "n_groups_runtime": n_groups_runtime,
        "uses_spatial_time": True,
        "uses_repeatable_time_of_day_mapper": False,
        "mu": mu,
        "group_id_by_index": group_ids,
        "group_str_to_int": g2i,
        "head_tail": ht,
        "mu_hash": sha256_json(artifact["mu"]),
        "group_map_hash": artifact.get("hashes", {}).get("group_map_hash"),
        "target_artifact": artifact,
        "parse_time_block_ok": all(parse_time_block(g) in {0, 1, 2, 3} for g in artifact["mu"]),
    }
