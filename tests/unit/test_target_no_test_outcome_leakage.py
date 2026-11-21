"""Test Y / predictions / residuals must not move ϖ, μ, or π^{tar}."""

from __future__ import annotations

import pandas as pd

from raven_mcs.sag.target_law import build_frozen_atomic_target_law
from tests.unit.test_target_compatibility import _toy_atomic


def test_target_no_test_outcome_leakage() -> None:
    atomic, mapping, h_map = _toy_atomic()
    base = build_frozen_atomic_target_law(atomic, mapping, h_map, dataset="toy")

    mutated = atomic.copy()
    test = mutated["split"].astype(str) == "test"
    mutated.loc[test, "y"] = mutated.loc[test, "y"] + 999.0
    mutated["y_pred"] = 0.0
    mutated.loc[test, "y_pred"] = -123.0
    mutated["residual"] = mutated["y"] - mutated["y_pred"]
    after = build_frozen_atomic_target_law(mutated, mapping, h_map, dataset="toy")

    assert after.law_hash == base.law_hash
    assert after.varpi == base.varpi
    assert after.pi_target == base.pi_target
    assert after.mu.tolist() == base.mu.tolist()
