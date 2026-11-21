"""Nested deterministic entity availability mask for R1i. Outcome-independent."""

from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping, Sequence

from raven_mcs.utils.hashing import sha256_json

MASK_NAMESPACE = "RAVEN_MCS_R1I_AVAIL_V1"
SEED = 30001


def mask_rule_payload() -> dict[str, Any]:
    return {
        "rule_id": "R1I_NESTED_HASH_MASK_V1",
        "namespace": MASK_NAMESPACE,
        "u_definition": "SHA256(namespace|dataset|base_seed|window_id|entity_id)[:8] / 2^64 in [0,1)",
        "available_iff": "u_e_r < a",
        "nested": True,
        "independent_redraw_per_level": False,
        "outcome_fields_forbidden": [
            "C_oracle_safe",
            "oracle_pass",
            "C_cov",
            "Gate",
            "pi_tar_weight",
            "opportunity_richness",
        ],
        "entity_id": "spatial_id",
        "salt_varies_by_dataset": False,
        "salt_varies_by_oracle": False,
        "base_seed": SEED,
    }


def mask_rule_hash() -> str:
    return sha256_json(mask_rule_payload())


def hash_to_unit_interval(
    *,
    dataset: str,
    base_seed: int,
    window_id: int,
    entity_id: str,
) -> float:
    material = "|".join(
        [
            MASK_NAMESPACE,
            str(dataset),
            str(int(base_seed)),
            str(int(window_id)),
            str(entity_id),
        ]
    )
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    n = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return n / float(2**64)


def entity_available(u: float, availability_level: float) -> bool:
    return float(u) < float(availability_level)


def available_entities(
    *,
    dataset: str,
    base_seed: int,
    window_id: int,
    entity_ids: Sequence[str],
    availability_level: float,
) -> dict[str, Any]:
    unique = sorted({str(e) for e in entity_ids})
    kept: list[str] = []
    scores: dict[str, float] = {}
    for entity in unique:
        u = hash_to_unit_interval(
            dataset=dataset,
            base_seed=base_seed,
            window_id=window_id,
            entity_id=entity,
        )
        scores[entity] = u
        if entity_available(u, availability_level):
            kept.append(entity)
    return {
        "available": kept,
        "n_natural": len(unique),
        "n_available": len(kept),
        "n_removed": len(unique) - len(kept),
        "realized_retention_fraction": (len(kept) / len(unique)) if unique else float("nan"),
        "u_by_entity": scores,
    }


def filter_units_by_entities(
    unit_ids: Iterable[str],
    unit_meta: Mapping[str, Mapping[str, str]],
    available: Sequence[str],
) -> list[str]:
    keep = set(str(e) for e in available)
    out: list[str] = []
    for uid in unit_ids:
        info = unit_meta.get(str(uid))
        if info is None:
            continue
        if str(info["spatial"]) in keep:
            out.append(str(uid))
    return out
