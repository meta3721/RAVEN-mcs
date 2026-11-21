"""Historical legacy R1m aggregate-certificate implementation spec. One predictor, one RESET rule."""

from __future__ import annotations

from typing import Any

from raven_mcs.aggregation.method_policy import FORMAL_GATE_MODE, LEGACY_COVERAGE_METHOD
from raven_mcs.sag.availability_stress import A_GRID, BOUNDARY_NEAR_MARGIN
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, NUM_TOL, TAU_COV
from raven_mcs.sag.stress_mask import SEED
from raven_mcs.utils.hashing import sha256_json

RIDGE_ALPHA = 1.0
LOOKBACK_L = 8
PREDICTOR_ID = "AGGREGATE_COVERAGE_RIDGE_V1"
RESET_RULE_ID = "MISCOVERAGE_TRIGGERED_RESET_V1"
PAPER_METHOD = LEGACY_COVERAGE_METHOD
DATASETS = ("sensorscope", "uair")
PRIMARY = {"dataset": "sensorscope", "availability_level": 0.40}
SECONDARY = {"dataset": "uair", "availability_level": 0.20}

FEATURE_NAMES = (
    "intercept",
    "availability_level",
    "lag1_C",
    "lag2_C",
    "rolling_mean_C_L8",
    "rolling_trend_C_L8",
    "hour_sin",
    "hour_cos",
    "weekend_flag",
)

FEATURE_SPEC = {
    "predictor_id": PREDICTOR_ID,
    "ridge_alpha": RIDGE_ALPHA,
    "features": list(FEATURE_NAMES),
    "lookback_L": LOOKBACK_L,
    "lag_missing": "last_available_historical_aggregate_coverage",
    "no_history": "pretest_training_mean",
    "uses_current_C": False,
    "uses_current_oracle": False,
    "uses_current_mask": False,
    "interaction_terms": False,
    "hour_encoding": "sin_cos_24",
}


def feature_spec_hash() -> str:
    return sha256_json(FEATURE_SPEC)


def predictor_family_payload() -> dict[str, Any]:
    return {
        "predictor_id": PREDICTOR_ID,
        "implementation": "numpy_ridge_closed_form",
        "ridge_alpha": RIDGE_ALPHA,
        "model_zoo": False,
        "scan_alphas": False,
        "seed": SEED,
        "legacy_method": PAPER_METHOD,
        "method_version": "coverage-controlled-v1",
        "coverage_role": "controls_legacy_design",
        "gate_mode": FORMAL_GATE_MODE,
    }


def reset_rule_payload() -> dict[str, Any]:
    return {
        "rule_id": RESET_RULE_ID,
        "trigger": "C_LCB > C_t + tol after a CERTIFIED window completes",
        "tol": NUM_TOL,
        "second_detector": False,
        "proves_exchangeability": False,
        "protects_first_unseen_shift": False,
        "violation_window_retained": True,
        "next_window": "RESET then new-block WARMUP",
        "n_min": N_MIN,
        "alpha": ALPHA,
        "tau_cov": TAU_COV,
    }


ALLOWED_OVERALL = (
    "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION",
    "READY_FOR_LIMITED_SAG_1SEED_VALIDATION",
    "R1M_CERTIFICATE_TOO_CONSERVATIVE",
    "R1M_SAFETY_NOT_ESTABLISHED",
    "R1M_IMPLEMENTATION_FAILURE",
    "R1M_INSUFFICIENT_PRETEST_HISTORY",
)

ALLOWED_TRACK = (
    "FORMAL_CERTIFICATE_USABLE",
    "SAFE_BUT_CONSERVATIVE",
    "INSUFFICIENT_CERTIFIED_DUTY",
    "SAFETY_NOT_ESTABLISHED",
    "NO_DISCRIMINATION",
    "IMPLEMENTATION_FAILURE",
)

assert RIDGE_ALPHA == 1.0
assert N_MIN == 19
assert TAU_COV == 0.05
assert ALPHA == 0.05
assert list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]
assert BOUNDARY_NEAR_MARGIN == 0.01
assert PAPER_METHOD == LEGACY_COVERAGE_METHOD
