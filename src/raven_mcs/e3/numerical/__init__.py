"""Numerical integrity helpers for E3 real-runner / Canary."""

from raven_mcs.e3.numerical.finite import (
    NonfiniteNumericalState,
    assert_finite_metric,
    assert_finite_scalar,
    assert_finite_tensor,
    is_finite_number,
    metric_status,
)

__all__ = [
    "NonfiniteNumericalState",
    "assert_finite_metric",
    "assert_finite_scalar",
    "assert_finite_tensor",
    "is_finite_number",
    "metric_status",
]
