"""EXOGENOUS_ENTITY_AVAILABILITY_THINNING_V1. Frozen before oracle stress."""

from __future__ import annotations

from typing import Any

from raven_mcs.sag.stress_mask import MASK_NAMESPACE, SEED, mask_rule_hash, mask_rule_payload
from raven_mcs.utils.hashing import sha256_json

PROTOCOL_VERSION = "E3V2_AVAIL_STRESS_V1"
NATURAL_PROTOCOL_VERSION = "e3-v2-time-aligned-v1"
A_GRID = (1.00, 0.80, 0.60, 0.40, 0.20)
TAU_COV = 0.05
BOUNDARY_NEAR_MARGIN = 0.01
BOUNDARY_RICH_SAFE_LO = 0.20
BOUNDARY_RICH_SAFE_HI = 0.80
BOUNDARY_RICH_MIN_SAFE = 5
BOUNDARY_RICH_MIN_UNSAFE = 5
MIN_CROSSING_WINDOWS = 5
TINY_CLUSTER_MAX = 3
REPRO_TOL = 1e-10
MONO_TOL = 1e-10


def stress_level_payload() -> dict[str, Any]:
    return {
        "mechanism": "EXOGENOUS_ENTITY_AVAILABILITY_THINNING_V1",
        "physical_meaning": (
            "Before each real E3-v2 window, an exogenous availability retention a in (0,1] "
            "is applied to deployment entities (spatial_id). Unavailable entities contribute "
            "no opportunity records in that window."
        ),
        "A_GRID": list(A_GRID),
        "a_1_reproduces_natural": True,
        "coarse_fixed_grid": True,
        "level_search_from_r1h": False,
        "forbidden_midpoints": [0.50, 0.55, 0.65],
        "pair_level_deletion": False,
        "pi_tar_weighted_deletion": False,
        "opportunity_richness_deletion": False,
        "dataset_specific_adaptive_rule": False,
        "seed": SEED,
        "tau_cov": TAU_COV,
    }


def stress_level_hash() -> str:
    return sha256_json(stress_level_payload())


def information_boundary_payload() -> dict[str, Any]:
    return {
        "availability_level_a": "scenario-level public exogenous parameter; known before the window starts",
        "realized_entity_mask": "not pre-window fully observed information",
        "future_predictor_may_use": ["a"],
        "future_predictor_may_not_use": ["current-window realized availability mask"],
        "this_round": "oracle only; no predictor",
    }


def routing_rule_payload() -> dict[str, Any]:
    return {
        "BOUNDARY_RICH": {
            "fraction_safe_lo": BOUNDARY_RICH_SAFE_LO,
            "fraction_safe_hi": BOUNDARY_RICH_SAFE_HI,
            "n_safe_min": BOUNDARY_RICH_MIN_SAFE,
            "n_unsafe_min": BOUNDARY_RICH_MIN_UNSAFE,
            "not_all_on_split_edge": True,
            "not_single_tiny_cluster_max": TINY_CLUSTER_MAX,
            "not_all_partial": True,
            "note": "20/80 is an internal routing rule, not a paper theorem",
        },
        "BOUNDARY_NEAR": {
            "abs_margin_max": BOUNDARY_NEAR_MARGIN,
            "role": "visualization / subgroup audit only; next round must still use the full track",
        },
        "MILD_SAFE_EXISTS": {"a_in": [1.00, 0.80], "fraction_safe_min": 0.80},
        "SEVERE_UNSAFE_EXISTS": {"a_in": [0.40, 0.20], "fraction_safe_max": 0.20},
        "MIN_CROSSING_WINDOWS": MIN_CROSSING_WINDOWS,
        "frozen_before_oracle_summary": True,
    }


def routing_rule_hash() -> str:
    return sha256_json(routing_rule_payload())


def boundary_near_rule_payload() -> dict[str, Any]:
    return {
        "rule_id": "BOUNDARY_NEAR_V1",
        "abs_C_oracle_safe_minus_tau_cov": BOUNDARY_NEAR_MARGIN,
        "tau_cov": TAU_COV,
        "frozen_before_oracle_summary": True,
    }
