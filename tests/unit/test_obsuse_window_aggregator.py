"""ObsUse-Window: lagged observation + usable inverse weighting."""

from __future__ import annotations

import numpy as np

from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import (
    FedAUWindowAggregator,
    ObsUseWindowAggregator,
    get_aggregator,
)


def _payload(raw_counts, participation_rate, observation_rate):
    n = len(raw_counts)
    return WindowAggregateInput(
        client_ids=[f"c{i}" for i in range(n)],
        raw_counts=np.asarray(raw_counts, dtype=np.float64),
        total_masses=np.asarray(raw_counts, dtype=np.float64),
        compositions=np.ones((2, n), dtype=np.float64) / 2.0,
        extras={
            "participation_rate": participation_rate,
            "observation_rate": observation_rate,
        },
    )


def test_obsuse_registered() -> None:
    agg = get_aggregator("obsuse_window")
    assert isinstance(agg, ObsUseWindowAggregator)
    assert get_aggregator("obsuse").name == "obsuse_window"


def test_obsuse_policy_obs_and_use_only() -> None:
    pol = get_method_policy("obsuse_window")
    assert pol.uses_observation_ipw is True
    assert pol.uses_usable_ipw is True
    assert pol.uses_design_ratio is False
    assert pol.uses_hajek_local_loss is False
    assert pol.uses_instant_calibration is False
    assert pol.uses_debt is False


def test_obsuse_matches_fedau_when_obs_rates_are_one() -> None:
    raw = np.array([5.0, 3.0, 2.0])
    part = {"c0": 0.5, "c1": 1.0, "c2": 0.25}
    ones = {"c0": 1.0, "c1": 1.0, "c2": 1.0}
    obsuse = ObsUseWindowAggregator().compute_server_weights(
        _payload(raw, part, ones)
    )
    fedau = FedAUWindowAggregator().compute_server_weights(
        WindowAggregateInput(
            client_ids=["c0", "c1", "c2"],
            raw_counts=raw,
            total_masses=raw,
            compositions=np.ones((2, 3)) / 2.0,
            extras={"participation_rate": part},
        )
    )
    np.testing.assert_allclose(obsuse, fedau, atol=1e-12)


def test_obsuse_upweights_low_observation() -> None:
    raw = np.array([4.0, 4.0])
    part = {"c0": 1.0, "c1": 1.0}
    obs = {"c0": 0.25, "c1": 1.0}
    alpha = ObsUseWindowAggregator().compute_server_weights(_payload(raw, part, obs))
    assert alpha[0] > alpha[1]
    np.testing.assert_allclose(alpha.sum(), 1.0, atol=1e-12)


def test_obsuse_requires_both_rates() -> None:
    payload = WindowAggregateInput(
        client_ids=["c0"],
        raw_counts=np.array([1.0]),
        total_masses=np.array([1.0]),
        compositions=np.ones((1, 1)),
        extras={"participation_rate": {"c0": 1.0}},
    )
    try:
        ObsUseWindowAggregator().compute_server_weights(payload)
    except ValueError as exc:
        assert "observation_rate" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing observation_rate")
