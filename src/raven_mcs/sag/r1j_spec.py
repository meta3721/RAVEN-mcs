"""Frozen R1j predictor / calibration / routing specs. Frozen before certificate run."""

from __future__ import annotations

from typing import Any

from raven_mcs.sag.availability_stress import A_GRID, BOUNDARY_NEAR_MARGIN
from raven_mcs.sag.stress_mask import MASK_NAMESPACE, SEED
from raven_mcs.utils.hashing import sha256_json

LOOKBACK_L = 8
LOOKBACK_MIN = 8
DELTA_CAL = 0.05
TAU_COV = 0.05
LOGISTIC_C = 1.0
MODEL_ID = "CONTEXT_AVAILABILITY_PRESENCE_V1"
CALIBRATION_ID = "CONTEXT_STRATIFIED_WINDOW_MAX_CONFORMAL_V1"
RIDGE_SOLVER = "lbfgs"
RANDOM_STATE = SEED
FALSE_SAFE_MAX = 0.05
JOINT_VALID_MIN = 0.95
BALANCED_ACC_MIN = 0.70
NONVACUOUS_ZERO_MAX = 0.80
NUM_TOL = 1e-12

FEATURE_NAMES = (
    "log1p_hist_active_count",
    "lag1_active",
    "lag2_active",
    "rolling_active_rate_L8",
    "rolling_pi_opp_mean_L8",
    "rolling_pi_opp_trend_L8",
    "hour_of_day_unit",
    "weekend_flag",
    "availability_level",
    "rolling_active_rate_times_a",
)


def predictor_spec_payload() -> dict[str, Any]:
    return {
        "model_id": MODEL_ID,
        "implementation": "sklearn.linear_model.LogisticRegression L2",
        "C": LOGISTIC_C,
        "solver": RIDGE_SOLVER,
        "random_state": RANDOM_STATE,
        "lookback_L": LOOKBACK_L,
        "fit_protocol": "expanding_window_refit_windows_strictly_before_r",
        "label": "1{pi_opp_realized >= pi_safe}",
        "hat_pi_opp_map": "p * max(pi_safe, pair_expanding_mean_realized_mass_same_a)",
        "features": list(FEATURE_NAMES),
        "uses_current_mask": False,
        "uses_current_ROU": False,
        "uses_oracle_label": False,
        "model_zoo": False,
        "tie_break": "sklearn lbfgs deterministic random_state=30001",
        "numerical_tolerance": NUM_TOL,
        "seed": SEED,
    }


def calibration_spec_payload() -> dict[str, Any]:
    return {
        "calibration_id": CALIBRATION_ID,
        "residual": "max_{target-positive pairs} (hat_pi_opp - pi_opp_realized)",
        "stratum": "availability_level a",
        "same_a_only": True,
        "no_cross_a_borrow": True,
        "no_oracle_grouping": True,
        "delta_cal": DELTA_CAL,
        "quantile": "conformal_upper_residual from dynamic_cov.py (R1d formula)",
        "lookback_min": LOOKBACK_MIN,
        "warmup_if_calib_lt": LOOKBACK_MIN,
        "lower_pi_opp": "max(0, hat_pi_opp - q_{r,a})",
        "C_cov_dynamic": "sum pi_tar * 1{lower_pi_opp >= pi_safe}",
        "tau_cov": TAU_COV,
    }


def routing_spec_payload() -> dict[str, Any]:
    return {
        "FALSE_SAFE_MAX": FALSE_SAFE_MAX,
        "JOINT_VALID_MIN": JOINT_VALID_MIN,
        "BALANCED_ACC_MIN": BALANCED_ACC_MIN,
        "NONVACUOUS_ZERO_MAX": NONVACUOUS_ZERO_MAX,
        "BOUNDARY_NEAR_MARGIN": BOUNDARY_NEAR_MARGIN,
        "A_GRID": list(A_GRID),
        "primary_boundary": {"dataset": "sensorscope", "availability_level": 0.40},
        "secondary_boundary": {"dataset": "uair", "availability_level": 0.20},
        "note": "internal routing thresholds, not paper theorems",
    }


def predictor_spec_hash() -> str:
    return sha256_json(predictor_spec_payload())


def calibration_spec_hash() -> str:
    return sha256_json(calibration_spec_payload())
