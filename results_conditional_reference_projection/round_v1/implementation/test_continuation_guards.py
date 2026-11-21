"""Branch checks for the continuation guards. No model training."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np

from guards import (
    FEASIBILITY_LIMIT,
    BudgetLedger,
    LowMemoryTracker,
    RealConstraintViolation,
    clean_server_weights,
    constraint_parts,
)


def test_low_memory_requires_thirty_continuous_seconds() -> None:
    tracker = LowMemoryTracker()
    low = 1 * 1024**3
    tracker.observe(low, 0.0)
    tracker.observe(low, 29.0)
    assert tracker.breached is False
    tracker.observe(low, 30.0)
    assert tracker.breached is True
    recovered = LowMemoryTracker()
    recovered.observe(low, 0.0)
    recovered.observe(low, 20.0)
    recovered.observe(5 * 1024**3, 21.0)
    recovered.observe(low, 22.0)
    recovered.observe(low, 51.0)
    assert recovered.breached is False
    recovered.observe(low, 52.0)
    assert recovered.breached is True


def test_tiny_negative_is_cleaned_and_large_violation_is_not() -> None:
    raw = np.array(
        [(1.0 + 1e-12) / 3.0, (1.0 + 1e-12) / 3.0, (1.0 + 1e-12) / 3.0, -1e-12],
        dtype=np.float64,
    )
    cleaned, record = clean_server_weights(raw)
    assert record["clipped_negative"] is True
    assert max(record["after"].values()) <= FEASIBILITY_LIMIT
    assert float(np.min(cleaned)) >= 0.0
    too_negative = np.array(
        [(1.0 + 1e-7) / 3.0, (1.0 + 1e-7) / 3.0, (1.0 + 1e-7) / 3.0, -1e-7],
        dtype=np.float64,
    )
    try:
        clean_server_weights(too_negative)
    except RealConstraintViolation as exc:
        assert exc.payload["stage"] == "before_cleanup"
        assert exc.payload["before"]["negative"] > FEASIBILITY_LIMIT
    else:
        raise AssertionError("negative beyond 1e-8 was cleaned")
    capped = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float64)
    try:
        clean_server_weights(capped)
    except RealConstraintViolation as exc:
        assert exc.payload["before"]["cap"] > FEASIBILITY_LIMIT
    else:
        raise AssertionError("cap violation was accepted")
    uniform = np.full(4, 0.25)
    cleaned_uniform, record_uniform = clean_server_weights(uniform)
    assert record_uniform["correction_max_abs"] == 0.0
    assert max(constraint_parts(cleaned_uniform, 0.5, 3.0).values()) <= FEASIBILITY_LIMIT


def test_budget_crash_is_counted_once() -> None:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "budget.json"
        ledger = BudgetLedger(path, 600.0, 900.0)
        ledger.snapshot(3.0, 4.0, "open")
        restarted = BudgetLedger(path, 600.0, 900.0)
        restarted.load()
        assert restarted.cpu_closed == 3.0
        assert restarted.wall_closed == 4.0
        cpu, wall = restarted.spent(1.0, 2.0)
        assert cpu == 4.0 and wall == 6.0
        restarted.close_process(1.0, 2.0, "done")
        third = BudgetLedger(path, 600.0, 900.0)
        third.load()
        assert third.cpu_closed == 4.0
        assert third.wall_closed == 6.0


def main() -> None:
    test_low_memory_requires_thirty_continuous_seconds()
    test_tiny_negative_is_cleaned_and_large_violation_is_not()
    test_budget_crash_is_counted_once()
    print("GUARD_TESTS_PASS", flush=True)


if __name__ == "__main__":
    main()
