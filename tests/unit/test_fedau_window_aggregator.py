"""FedAU-Window: lagged inverse-participation aggregator (windowed adaptation)."""

from __future__ import annotations

import numpy as np

from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import (
    FedAUWindowAggregator,
    FedAvgWindowAggregator,
    get_aggregator,
)


def _payload(raw_counts, participation_rate):
    n = len(raw_counts)
    return WindowAggregateInput(
        client_ids=[f"c{i}" for i in range(n)],
        raw_counts=np.asarray(raw_counts, dtype=np.float64),
        total_masses=np.asarray(raw_counts, dtype=np.float64),
        compositions=np.ones((2, n), dtype=np.float64) / 2.0,
        extras={"participation_rate": participation_rate},
    )


def test_fedau_registered() -> None:
    agg = get_aggregator("fedau_window")
    assert isinstance(agg, FedAUWindowAggregator)
    assert get_aggregator("fedau").name == "fedau_window"


def test_fedau_policy_usable_layer_only() -> None:
    pol = get_method_policy("fedau_window")
    assert pol.uses_usable_ipw is True
    assert pol.uses_design_ratio is False
    assert pol.uses_observation_ipw is False
    assert pol.uses_hajek_local_loss is False
    assert pol.uses_instant_calibration is False
    assert pol.uses_debt is False
    assert pol.uses_reference_penalty is False
    assert pol.uses_variance_penalty is False
    assert pol.uses_staleness_penalty is False
    assert get_method_policy("fedau").uses_usable_ipw is True


def test_fedau_matches_fedavg_when_rates_are_one() -> None:
    raw = np.array([5.0, 3.0, 2.0])
    rates = {"c0": 1.0, "c1": 1.0, "c2": 1.0}
    payload = _payload(raw, rates)
    fedau = FedAUWindowAggregator().compute_server_weights(payload)
    fedavg = FedAvgWindowAggregator().compute_server_weights(payload)
    np.testing.assert_allclose(fedau, fedavg, atol=1e-12)


def test_fedau_upweights_low_participation() -> None:
    raw = np.array([4.0, 4.0])
    rates = {"c0": 0.25, "c1": 1.0}
    alpha = FedAUWindowAggregator().compute_server_weights(_payload(raw, rates))
    assert alpha[0] > alpha[1]
    np.testing.assert_allclose(alpha.sum(), 1.0, atol=1e-12)


def test_fedau_requires_lagged_rates() -> None:
    payload = WindowAggregateInput(
        client_ids=["c0"],
        raw_counts=np.array([1.0]),
        total_masses=np.array([1.0]),
        compositions=np.ones((1, 1)),
    )
    try:
        FedAUWindowAggregator().compute_server_weights(payload)
    except ValueError as exc:
        assert "participation_rate" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing participation_rate")
