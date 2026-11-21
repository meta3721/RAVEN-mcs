"""Frozen R1k architecture-audit constants. Not a paper-method replacement."""

from __future__ import annotations

from typing import Any

from raven_mcs.sag.availability_stress import A_GRID, BOUNDARY_NEAR_MARGIN
from raven_mcs.sag.stress_mask import SEED
from raven_mcs.utils.hashing import sha256_json

LOOKBACK_L = 8
LOOKBACK_MIN = 8
DELTA_CAL = 0.05
TAU_COV = 0.05
ONE_MINUS_DELTA = 1.0 - DELTA_CAL
RIDGE_ALPHA = 1.0
NUM_TOL = 1e-12
FALSE_SAFE_MAX = 0.05
VALIDITY_MIN = 0.95
BALANCED_ACC_MIN = 0.70
NONVACUOUS_ZERO_MAX = 0.80
SCALE_LIFT_MIN = 1.20

AGG_MODEL_ID = "AGGREGATE_COVERAGE_LINEAR_V1"
AGG_CALIBRATION_ID = "AGGREGATE_SCALAR_SAME_A_CONFORMAL_V1"
OLD_MAP_ID = "R1J_P_TIMES_MEAN_MASS_ALL"
COND_MAP_ID = "P_TIMES_MEAN_MASS_POSITIVE"

PAPER_TEX = (
    "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
    "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex",
    "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex",
)

AGG_FEATURE_NAMES = (
    "lag1_C",
    "lag2_C",
    "rolling_mean_C_L8",
    "rolling_trend_C_L8",
    "hour_of_day_unit",
    "weekend_flag",
    "availability_level",
    "rolling_mean_times_a",
)

ALLOWED_OVERALL = (
    "CERTIFICATE_ARCHITECTURE_REDESIGN_RECOMMENDED",
    "PAIRWISE_IMPLEMENTATION_REPAIR_RECOMMENDED",
    "PAIRWISE_ARCHITECTURE_REMAINS_VIABLE",
    "R1K_ARCHITECTURE_AUDIT_INCONCLUSIVE",
    "R1K_IMPLEMENTATION_OR_EVIDENCE_FAILURE",
)


def aggregate_predictor_payload() -> dict[str, Any]:
    return {
        "model_id": AGG_MODEL_ID,
        "implementation": "sklearn.linear_model.Ridge",
        "alpha": RIDGE_ALPHA,
        "lookback_L": LOOKBACK_L,
        "features": list(AGG_FEATURE_NAMES),
        "target": "historical C_oracle_safe same-a windows strictly before r",
        "uses_current_mask": False,
        "uses_current_oracle": False,
        "model_zoo": False,
        "seed": SEED,
        "feasibility_audit_only": True,
        "not_a_paper_method_replacement": True,
    }


def aggregate_calibration_payload() -> dict[str, Any]:
    return {
        "calibration_id": AGG_CALIBRATION_ID,
        "residual": "C_hat - C_oracle",
        "stratum": "availability_level a",
        "same_a_only": True,
        "no_cross_a_borrow": True,
        "delta_cal": DELTA_CAL,
        "quantile": "conformal_upper_residual from dynamic_cov.py",
        "lookback_min": LOOKBACK_MIN,
        "C_LCB": "max(0, C_hat - qC)",
        "tau_cov": TAU_COV,
        "feasibility_audit_only": True,
    }


def aggregate_predictor_hash() -> str:
    return sha256_json(aggregate_predictor_payload())


def aggregate_calibration_hash() -> str:
    return sha256_json(aggregate_calibration_payload())


def routing_payload() -> dict[str, Any]:
    return {
        "FALSE_SAFE_MAX": FALSE_SAFE_MAX,
        "VALIDITY_MIN": VALIDITY_MIN,
        "BALANCED_ACC_MIN": BALANCED_ACC_MIN,
        "NONVACUOUS_ZERO_MAX": NONVACUOUS_ZERO_MAX,
        "SCALE_LIFT_MIN": SCALE_LIFT_MIN,
        "BOUNDARY_NEAR_MARGIN": BOUNDARY_NEAR_MARGIN,
        "A_GRID": list(A_GRID),
        "primary_boundary": {"dataset": "sensorscope", "availability_level": 0.40},
        "secondary_boundary": {"dataset": "uair", "availability_level": 0.20},
        "note": "internal routing; not a paper theorem; aggregate is a feasibility candidate only",
    }
