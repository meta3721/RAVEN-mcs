"""Offline P2 alpha residual checks; this never solves or changes a run."""

from __future__ import annotations

from typing import Any

import numpy as np

HARD_RESIDUAL_GATE = 1e-7
SOLVE_TOLERANCE = 1e-6


def audit_alpha(alpha: list[float] | None, *, upper_bound: float | None = None) -> dict[str, Any]:
    """Certify saved simplex state where native solver state was not persisted."""
    if alpha is None:
        return _missing()
    value = np.asarray(alpha, dtype=float)
    if value.size == 0 or not bool(np.all(np.isfinite(value))):
        return _missing()
    simplex = abs(float(value.sum()) - 1.0)
    lower = max(0.0, -float(value.min()))
    upper = max(0.0, float(value.max()) - float(upper_bound)) if upper_bound is not None else None
    maximum = max([simplex, lower] + ([] if upper is None else [upper]))
    if maximum <= HARD_RESIDUAL_GATE:
        status = "CERTIFIED_FEASIBLE"
    elif maximum <= SOLVE_TOLERANCE:
        status = "CERTIFIED_WITHIN_NUMERICAL_TOLERANCE"
    else:
        status = "INFEASIBLE"
    return {
        "normalization_residual": simplex,
        "equality_residuals": simplex,
        "inequality_residuals": lower if upper is None else max(lower, upper),
        "lower_bound_violation": lower,
        "upper_bound_violation": upper,
        "simplex_violation": simplex,
        "primal_feasibility_summary": maximum,
        "finite_state": True,
        "certificate_status": status,
    }


def _missing() -> dict[str, Any]:
    return {
        "normalization_residual": None, "equality_residuals": None, "inequality_residuals": None,
        "lower_bound_violation": None, "upper_bound_violation": None, "simplex_violation": None,
        "primal_feasibility_summary": None, "finite_state": False, "certificate_status": "MISSING_STATE",
    }
