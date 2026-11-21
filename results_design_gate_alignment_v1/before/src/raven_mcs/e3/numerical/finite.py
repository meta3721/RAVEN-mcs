"""Finite-value hard checks for E3 production metrics/states."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


class NonfiniteNumericalState(RuntimeError):
    CODE = "NONFINITE_NUMERICAL_STATE"


def is_finite_number(value: Any) -> bool:
    if value is None:
        return False
    try:
        return bool(math.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def assert_finite_scalar(value: Any, *, name: str) -> float:
    if not is_finite_number(value):
        raise NonfiniteNumericalState(
            f"{NonfiniteNumericalState.CODE}: {name}={value!r}"
        )
    return float(value)


def assert_finite_tensor(value: Any, *, name: str) -> np.ndarray:
    arr = np.asarray(value)
    if arr.size == 0:
        return arr
    if not np.all(np.isfinite(arr)):
        raise NonfiniteNumericalState(
            f"{NonfiniteNumericalState.CODE}: {name} has nonfinite entries"
        )
    return arr


def assert_finite_metric(value: Any, *, name: str, applicable: bool = True) -> Any:
    if not applicable:
        return value
    return assert_finite_scalar(value, name=name)


def metric_status(value: Any, *, applicable: bool) -> str:
    """Status token for Canary run-status tables."""
    if not applicable:
        return "N_A"
    if value is None:
        return "MISSING"
    if not is_finite_number(value):
        return "NONFINITE"
    return "OK"


def required_metrics_finite(metrics: dict[str, Any], required: list[str]) -> bool:
    for key in required:
        app = metrics.get(f"{key}_applicability", "APPLICABLE")
        if app in {"NOT_APPLICABLE", "N_A", "N/A"}:
            continue
        if not is_finite_number(metrics.get(key)):
            return False
    return True
