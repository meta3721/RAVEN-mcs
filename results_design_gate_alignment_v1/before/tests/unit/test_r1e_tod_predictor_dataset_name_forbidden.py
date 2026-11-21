"""Dataset name is not a predictor argument."""

from __future__ import annotations

import inspect

from raven_mcs.sag.dynamic_cov import tod_conditioned_rolling_pi_hat
from raven_mcs.sag.window_context import dataset_name_is_forbidden_context


def test_r1e_tod_predictor_dataset_name_forbidden() -> None:
    names = set(inspect.signature(tod_conditioned_rolling_pi_hat).parameters)
    assert "dataset" not in names
    assert "dataset_name" not in names
    assert dataset_name_is_forbidden_context("uair")
    assert dataset_name_is_forbidden_context("sensorscope")
