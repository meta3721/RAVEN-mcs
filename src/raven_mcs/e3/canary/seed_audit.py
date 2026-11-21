"""Prove Canary seed 31001 is disjoint from formal/tuning families."""

from __future__ import annotations

from typing import Any

from raven_mcs.e3.canary.constants import CANARY_SEED, FORMAL_SEEDS


# Known non-formal reserved / tuning / profile seed families (not exhaustive scan of all history)
KNOWN_RESERVED = {
    29001: "E2 Traffic real-runner canary",
    31999: "E3 real-runner debug fixture",
    32999: "E3 stratum/target-pair debug fixture",
    20001: "legacy/profile family lower bound (documented)",
}


def audit_canary_seed(seed: int = CANARY_SEED) -> dict[str, Any]:
    collisions: list[dict[str, Any]] = []
    if int(seed) in set(FORMAL_SEEDS):
        collisions.append({"family": "E3_FORMAL_SEEDS_30001_30020", "seed": int(seed)})
    if int(seed) in KNOWN_RESERVED:
        collisions.append(
            {"family": KNOWN_RESERVED[int(seed)], "seed": int(seed)}
        )
    # Held-out formal statistical family: formal block only; 31001 is outside by construction
    disjoint = {
        "not_formal_30001_30020": int(seed) not in set(FORMAL_SEEDS),
        "not_e2_traffic_canary_29001": int(seed) != 29001,
        "not_debug_31999": int(seed) != 31999,
        "not_debug_32999": int(seed) != 32999,
        "outside_formal_block": int(seed) < 30001 or int(seed) > 30020,
    }
    status = "PASS" if not collisions and all(disjoint.values()) else "CANARY_SEED_COLLISION"
    return {
        "canary_seed": int(seed),
        "formal_seeds": FORMAL_SEEDS,
        "known_reserved_checked": sorted(KNOWN_RESERVED),
        "disjoint_proof": disjoint,
        "collisions": collisions,
        "status": status,
    }
