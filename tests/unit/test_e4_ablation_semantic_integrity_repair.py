"""Unit tests for E4 ablation semantic integrity repair."""
from __future__ import annotations

import numpy as np
import pytest

from raven_mcs.aggregation.feasibility import validate_p2_lambdas
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import (
    RavenAggregator,
    RavenWoInstAggregator,
    get_aggregator,
)
from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.aggregation.p2_cvxpy import solve_p2
from raven_mcs.e4.semantic_repair.task_a import ablation_switch_regression
from raven_mcs.e4.semantic_repair.task_b import one_factor_regression_before_after


FLAGS = (
    "uses_design_ratio",
    "uses_observation_ipw",
    "uses_usable_ipw",
    "uses_instant_calibration",
    "uses_debt",
)


def _payload() -> WindowAggregateInput:
    return WindowAggregateInput(
        client_ids=["c0", "c1", "c2", "c3"],
        raw_counts=np.ones(4),
        total_masses=np.ones(4),
        compositions=np.array(
            [[0.9, 0.1, 0.2, 0.3], [0.1, 0.9, 0.8, 0.7]], dtype=np.float64
        ),
        beta_hat=np.array([0.1, 0.7, 0.1, 0.1], dtype=np.float64),
        staleness=np.array([0.0, 1.0, 0.5, 0.2]),
        variance_diag=np.array([1.0, 5.0, 1.0, 1.0]),
        debt=np.array([2.0, -1.5], dtype=np.float64),
        mu=np.array([0.5, 0.5], dtype=np.float64),
    )


def test_ablation_switch_regression_pass():
    out = ablation_switch_regression()
    assert out["status"] == "PASS"
    assert out["full_mode_p2_fixture"]["passes"]


def test_raven_wo_inst_aggregator_invokes_p2_with_disabled_group_cal():
    agg = RavenWoInstAggregator(e_min=1.0)
    assert isinstance(agg, RavenWoInstAggregator)
    assert agg.lambda_group == 0.0
    assert agg.lambda_beta == 1.0
    assert agg.instant_calibration is False
    payload = _payload()
    alpha = agg.compute_server_weights(payload)
    assert len(agg.solve_results) == 1
    assert abs(float(alpha.sum()) - 1.0) < 1e-8
    assert not np.allclose(alpha, payload.beta_hat)


def test_full_raven_unchanged_rejects_lambda_group_zero():
    with pytest.raises(ValueError, match="lambda_group"):
        validate_p2_lambdas(
            lambda_beta=1.0,
            lambda_group=0.0,
            max_server_learning_rate=1.0,
            instant_calibration=True,
        )
    validate_p2_lambdas(
        lambda_beta=1e-8,
        lambda_group=0.0,
        max_server_learning_rate=1.0,
        instant_calibration=False,
    )
    raven = RavenAggregator()
    alpha = raven.compute_server_weights(_payload())
    assert len(raven.solve_results) == 1
    assert raven.instant_calibration is True
    assert abs(float(alpha.sum()) - 1.0) < 1e-8


def test_one_factor_regression_documents_bug_and_fix():
    out = one_factor_regression_before_after()
    assert out["before_fix"]["p2_invoked"] is False
    assert out["after_fix"]["p2_invoked"] is True
    assert out["passes"] is True


def test_policies_still_one_factor():
    full = get_method_policy("raven")
    assert all(getattr(full, f) for f in FLAGS)
    mapping = {
        "raven_wo_design": "uses_design_ratio",
        "raven_wo_obs": "uses_observation_ipw",
        "raven_wo_use": "uses_usable_ipw",
        "raven_wo_inst": "uses_instant_calibration",
        "raven_wo_debt": "uses_debt",
    }
    for method, disabled in mapping.items():
        pol = get_method_policy(method)
        flips = [f for f in FLAGS if getattr(pol, f) != getattr(full, f)]
        assert flips == [disabled]


def test_solve_p2_accepts_instant_calibration_false():
    coverage = np.array([[0.7, 0.2, 0.4], [0.3, 0.8, 0.6]], dtype=float)
    result = solve_p2(
        coverage,
        np.array([0.5, 0.5]),
        np.ones(3) / 3.0,
        np.array([0.1, -0.05]),
        np.ones(3),
        np.zeros(3),
        lambda_group=0.0,
        lambda_beta=1e-8,
        lambda_variance=0.1,
        lambda_staleness=0.1,
        alpha_max=0.5,
        e_min=3.0,
        max_server_learning_rate=1.0,
        instant_calibration=False,
    )
    assert abs(float(result.alpha.sum()) - 1.0) < 1e-8
