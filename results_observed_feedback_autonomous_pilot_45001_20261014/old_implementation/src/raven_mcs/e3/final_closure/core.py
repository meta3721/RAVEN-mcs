"""Pure helpers for the offline E3 final closure."""
from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound

HARD_GATE = 1e-7


def certify_returned_alpha(alpha: list[float] | None) -> dict[str, Any]:
    """Certify only the persisted decision vector; never invoke a solver."""
    if alpha is None:
        return {"classification": "UNCERTIFIED_MISSING_STATE", "finite": False}
    value = np.asarray(alpha, dtype=float)
    if not value.size or not np.all(np.isfinite(value)):
        return {"classification": "UNCERTIFIED_MISSING_STATE", "finite": False}
    n = int(value.size)
    upper = alpha_bar(alpha_max=0.5, n_active=n)
    e_bar = ess_ball_bound(e_min=min(3, n), n_active=n)
    residuals = {
        "simplex_residual": abs(float(value.sum()) - 1.0),
        "nonnegative_violation": max(0.0, -float(value.min())),
        "upper_bound_violation": max(0.0, float(value.max()) - upper),
        "ess_ball_violation": max(0.0, float(np.square(value).sum()) - 1.0 / e_bar),
    }
    maximum = max(residuals.values())
    return {
        **residuals,
        "finite": True,
        "n_active": n,
        "alpha_upper_bound": upper,
        "ess_ball_bound": e_bar,
        "max_residual": maximum,
        "classification": (
            "CERTIFIED_WITHIN_NUMERICAL_TOLERANCE"
            if maximum <= HARD_GATE else "CONSTRAINT_VIOLATION"
        ),
    }


def summarize_weights(weights: list[float]) -> dict[str, Any]:
    value = np.asarray(weights, dtype=float)
    return {
        "n_samples": int(value.size),
        "weight_min": float(value.min()),
        "weight_max": float(value.max()),
        "weight_mean": float(value.mean()),
        "weight_std": float(value.std()),
        "weight_range": float(value.max() - value.min()),
        "is_uniform_eps": bool(float(value.max() - value.min()) <= 1e-12),
    }
