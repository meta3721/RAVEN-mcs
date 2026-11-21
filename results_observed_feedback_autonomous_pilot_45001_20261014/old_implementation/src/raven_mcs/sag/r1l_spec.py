"""Frozen R1l theory-closure constants. No experiment. Optional drift extension omitted."""

from __future__ import annotations

import math
from typing import Any

from raven_mcs.sag.availability_stress import A_GRID
from raven_mcs.utils.hashing import sha256_json

ALPHA = 0.05
TAU_COV = 0.05
NUM_TOL = 1e-12
N_MIN = int(math.ceil(1.0 / ALPHA)) - 1  # 19
FORMAL_COV_MODE = "aggregate_stable_regime"
STATES = ("WARMUP", "CERTIFIED", "RESET")
FORBIDDEN_PREWINDOW = (
    "current_mask",
    "current_available_entities",
    "current_R",
    "current_O",
    "current_U",
    "current_pi_opp",
    "current_C",
    "current_oracle_safe",
    "future_windows",
)
ALLOWED_PREWINDOW = (
    "lagged_C",
    "rolling_historical_summaries",
    "hour_of_day",
    "weekday_weekend",
    "availability_level_a",
    "frozen_public_context",
)
PAPER_TEX = (
    "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
    "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex",
    "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex",
)
ALLOWED_VERDICTS = (
    "THEORY_CLOSURE_PASS",
    "THEORY_CLOSURE_PASS_WITH_OPTIONAL_DRIFT_EXTENSION_PENDING",
    "THEORY_CLOSURE_NOT_READY",
)


def n_min(alpha: float = ALPHA) -> int:
    return int(math.ceil(1.0 / float(alpha))) - 1


def k_n(n: int, alpha: float = ALPHA) -> int:
    return int(math.ceil((int(n) + 1) * (1.0 - float(alpha))))


def theory_stack_payload() -> dict[str, Any]:
    return {
        "certification_object": "aggregate_realized_coverage_C_t",
        "formal_cov_mode": FORMAL_COV_MODE,
        "pairwise_formal_core": False,
        "alpha": ALPHA,
        "tau_cov": TAU_COV,
        "n_min": N_MIN,
        "clip_k_to_n_forbidden": True,
        "warmup_n_equals_8_forbidden_for_nominal_95": True,
        "states": list(STATES),
        "assumption_A": "local_score_exchangeability_within_certified_stable_regime",
        "optional_bounded_drift_extension": False,
        "A_GRID": list(A_GRID),
        "theorem_1": "stable_regime_aggregate_lower_coverage",
        "corollary_2": "false_safe_gate_bound",
        "proposition_1": "positive_pairwise_lcb_barrier",
        "corollary_1": "availability_induced_barrier",
        "proposition_2": "arbitrary_drift_applicability_boundary",
        "next_experiment": "R1m_aggregate_certificate_implementation",
        "sag_after": "only_if_R1m_passes",
    }


def theory_stack_hash() -> str:
    return sha256_json(theory_stack_payload())


assert N_MIN == 19
assert n_min() == 19
assert k_n(19) == 19
assert k_n(18) == 19  # 19 > 18 => no finite quantile
