"""Finite-value acceptance checks for E3 numerical integrity."""

from __future__ import annotations

import math

import pytest

from raven_mcs.e3.numerical.finite import (
    NonfiniteNumericalState,
    assert_finite_metric,
    is_finite_number,
    metric_status,
)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), None, "bad"])
def test_nonfinite_values_are_rejected(value: object) -> None:
    assert not is_finite_number(value)
    with pytest.raises(NonfiniteNumericalState):
        assert_finite_metric(value, name="metric")


def test_finite_values_and_applicability_statuses() -> None:
    assert is_finite_number(1.5)
    assert metric_status(1.5, applicable=True) == "OK"
    assert metric_status(None, applicable=True) == "MISSING"
    assert metric_status(math.nan, applicable=True) == "NONFINITE"
    assert metric_status(math.nan, applicable=False) == "N_A"
