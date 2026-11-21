"""Aggregate coverage scalar predictor + same-a conformal. Feasibility audit only."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from raven_mcs.sag.dynamic_cov import conformal_upper_residual
from raven_mcs.sag.r1k_spec import (
    AGG_FEATURE_NAMES,
    DELTA_CAL,
    LOOKBACK_L,
    LOOKBACK_MIN,
    NUM_TOL,
    RIDGE_ALPHA,
)


def aggregate_features(
    hist_c: Sequence[float],
    *,
    hour_of_day: int,
    weekend_flag: int,
    availability_level: float,
) -> dict[str, float]:
    """Features from completed same-a C_oracle history only (windows < r)."""
    L = int(LOOKBACK_L)
    xs = [float(x) for x in hist_c if np.isfinite(float(x))]
    recent = xs[-L:]
    lag1 = float(xs[-1]) if xs else 0.0
    lag2 = float(xs[-2]) if len(xs) >= 2 else 0.0
    roll = float(np.mean(recent)) if recent else 0.0
    if len(recent) >= 2:
        mid = max(1, len(recent) // 2)
        trend = float(np.mean(recent[-mid:]) - np.mean(recent[:mid]))
    else:
        trend = 0.0
    a = float(availability_level)
    return {
        "lag1_C": lag1,
        "lag2_C": lag2,
        "rolling_mean_C_L8": roll,
        "rolling_trend_C_L8": trend,
        "hour_of_day_unit": float(int(hour_of_day) % 24) / 23.0,
        "weekend_flag": float(weekend_flag),
        "availability_level": a,
        "rolling_mean_times_a": roll * a,
    }


def feature_vector(feat: dict[str, float]) -> np.ndarray:
    return np.asarray([float(feat[name]) for name in AGG_FEATURE_NAMES], dtype=np.float64)


def fit_ridge(X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    y = np.asarray(y, dtype=np.float64)
    if len(y) < 2:
        mu = float(y.mean()) if len(y) else 0.0
        return {"kind": "mean", "mu": mu, "coef": None, "intercept": None}
    from sklearn.linear_model import Ridge

    clf = Ridge(alpha=float(RIDGE_ALPHA))
    clf.fit(X, y)
    return {
        "kind": "ridge",
        "mu": None,
        "coef": clf.coef_.astype(float).ravel().tolist(),
        "intercept": float(clf.intercept_),
    }


def predict_c(model: dict[str, Any], x: np.ndarray) -> float:
    if model["kind"] == "mean":
        return float(model["mu"])
    coef = np.asarray(model["coef"], dtype=np.float64)
    return float(x @ coef + float(model["intercept"]))


def same_a_q(residuals: Sequence[float], *, delta: float = DELTA_CAL, min_calib: int = LOOKBACK_MIN) -> tuple[float, int, bool]:
    xs = [float(x) for x in residuals if np.isfinite(float(x))]
    n = len(xs)
    if n < int(min_calib):
        return float("nan"), n, True
    return float(conformal_upper_residual(xs, float(delta))), n, False


def c_lcb(c_hat: float, q: float) -> float:
    if not np.isfinite(float(c_hat)) or not np.isfinite(float(q)):
        return float("nan")
    return float(max(0.0, float(c_hat) - float(q)))


def agg_valid(c_lcb_val: float, c_oracle: float, *, tol: float = NUM_TOL) -> bool:
    if not np.isfinite(float(c_lcb_val)) or not np.isfinite(float(c_oracle)):
        return False
    return float(c_lcb_val) <= float(c_oracle) + float(tol)
