"""Target law must not be selected or moved by outcomes."""

from __future__ import annotations

from raven_mcs.sag.target_law import build_target_law_v1
from tests.unit.test_target_compatibility import _toy_atomic


def test_target_no_outcome_selection() -> None:
    atomic, mapping, h_map = _toy_atomic()
    base = build_target_law_v1(atomic, mapping, h_map, dataset="toy")
    mutated = atomic.copy()
    test = mutated["split"].astype(str) == "test"
    mutated.loc[test, "y"] = mutated.loc[test, "y"] + 999.0
    mutated["rmse"] = 12.3
    mutated["gate_on"] = 1.0
    after = build_target_law_v1(mutated, mapping, h_map, dataset="toy")
    assert after.law_hash == base.law_hash
    assert after.mu.tolist() == base.mu.tolist()
    assert after.pi_target == base.pi_target
