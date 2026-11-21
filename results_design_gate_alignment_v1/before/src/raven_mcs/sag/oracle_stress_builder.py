"""Build stressed window identities and oracle mass. Does not rewrite natural E3-v2."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from raven_mcs.sag.availability_stress import PROTOCOL_VERSION, TAU_COV
from raven_mcs.sag.e3v1_root_cause import oracle_from_mass, realized_mass_from_units
from raven_mcs.sag.oracle_ceiling import ge_threshold
from raven_mcs.sag.stress_mask import SEED, available_entities, filter_units_by_entities, mask_rule_hash
from raven_mcs.utils.hashing import sha256_json


def entities_from_units(unit_ids: Sequence[str], unit_meta: Mapping[str, Mapping[str, str]]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for uid in unit_ids:
        info = unit_meta.get(str(uid))
        if info is None:
            continue
        entity = str(info["spatial"])
        if entity not in seen:
            seen.add(entity)
            out.append(entity)
    return out


def stressed_window(
    *,
    dataset: str,
    window_id: int,
    unit_ids: Sequence[str],
    unit_meta: Mapping[str, Mapping[str, str]],
    availability_level: float,
    pi_tar: Mapping[tuple[str, str], float],
    pi_safe: float,
    natural_trace_hash: str,
    base_seed: int = SEED,
) -> dict[str, Any]:
    entities = entities_from_units(unit_ids, unit_meta)
    mask = available_entities(
        dataset=dataset,
        base_seed=base_seed,
        window_id=window_id,
        entity_ids=entities,
        availability_level=availability_level,
    )
    kept_units = filter_units_by_entities(unit_ids, unit_meta, mask["available"])
    mass = realized_mass_from_units(kept_units, unit_meta)
    ora = oracle_from_mass(mass, pi_tar, pi_safe)
    stressed_hash = sha256_json(
        {
            "protocol_version": PROTOCOL_VERSION,
            "dataset": dataset,
            "window_id": int(window_id),
            "availability_level": float(availability_level),
            "available_entities": mask["available"],
            "kept_unit_ids": sorted(kept_units),
        }
    )
    c_oracle = float(ora["C_oracle_safe"])
    return {
        "protocol_version": PROTOCOL_VERSION,
        "dataset": dataset,
        "seed": int(base_seed),
        "window_id": int(window_id),
        "availability_level": float(availability_level),
        "natural_trace_hash": natural_trace_hash,
        "availability_mask_hash": mask_rule_hash(),
        "stressed_trace_hash": stressed_hash,
        "n_entities_natural": mask["n_natural"],
        "n_entities_available": mask["n_available"],
        "n_entities_removed": mask["n_removed"],
        "realized_retention_fraction": mask["realized_retention_fraction"],
        "C_real_support": float(ora["C_real_support"]),
        "C_oracle_safe": c_oracle,
        "tau_cov": TAU_COV,
        "oracle_safe": ge_threshold(c_oracle, TAU_COV),
        "oracle_margin": c_oracle - TAU_COV,
        "mask_hash": mask_rule_hash(),
    }
