"""Four implementation tests. They do not train and do not read City Scanner labels."""

from __future__ import annotations

import os
import pickle
import sys
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

ROUND_DIR = Path(__file__).resolve().parent
SRC = ROUND_DIR.parents[1] / "src"
for entry in (str(ROUND_DIR), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from accounting import require_start_memory

require_start_memory()

import numpy as np

from cache_scheduler import (
    NotAuthorized,
    PoolMessage,
    ProtocolRunner,
    Scheduler,
    SchedulerFault,
    synthetic_attempt,
)
from support_distance import DistanceFailure, DistanceSolver


def _assert(condition: bool, text: str) -> None:
    if not condition:
        raise AssertionError(text)


def test_hold_complement_deadline_and_expiry() -> dict:
    mu = np.asarray([0.5, 0.5], dtype=np.float64)
    complement = [
        synthetic_attempt("a", 0, (1.0, 0.0)),
        synthetic_attempt("b", 1, (0.0, 1.0)),
    ]
    scheduler = Scheduler("S-Proj", mu)
    scheduler.begin_close(0)
    scheduler.register(complement[0])
    scheduler.deliver(complement[0].attempt_id)
    first = scheduler.close(0)
    _assert(first["action"] == "HOLD" and first["reason"] == "HOLD_NO_COMPLEMENT", "first arrival did not hold")
    _assert(scheduler.version == 0 and scheduler.optimizer["step_count"] == 0, "hold moved the model")
    scheduler.begin_close(1)
    scheduler.register(complement[1])
    scheduler.deliver(complement[1].attempt_id)
    second = scheduler.close(1)
    _assert(second["reason"] == "COMPLEMENTARY_RELEASE", "complementary pair did not release")
    _assert(second["d_p"] <= min(second["d_h"], second["d_a"]) - 0.01, "margin was not applied")
    _assert(scheduler.version == 1 and scheduler.optimizer["step_count"] == 1, "release did not create one update")

    same = [
        synthetic_attempt("a", 0, (1.0, 0.0)),
        synthetic_attempt("c", 1, (1.0, 0.0)),
    ]
    held = Scheduler("S-Proj", mu)
    for window, attempt in enumerate(same):
        held.begin_close(window)
        held.register(attempt)
        held.deliver(attempt.attempt_id)
        record = held.close(window)
        _assert(record["action"] == "HOLD", f"same-group close {window} released")
    held.begin_close(2)
    deadline = held.close(2)
    _assert(deadline["reason"] == "DEADLINE_RELEASE", "age 2 did not release")
    _assert("a|0|0" in deadline["committed_attempt_ids"], "the aged message was dropped")

    expired = Scheduler("S-Proj", mu)
    expired.begin_close(3)
    stale = PoolMessage(
        attempt_id="stale|0|0",
        client_id="stale",
        registration_window=0,
        registration_time=0.1,
        arrival_time=0.2,
        arrival_close=0,
        retry=0,
        download_version=0,
        m=1.0,
        composition=(1.0, 0.0),
        group_mass=(1.0, 0.0),
        raw_workload=1.0,
    )
    expired.insert_pending_for_test(stale)
    record = expired.close(3)
    _assert(stale.state == "expired" and stale.attempt_id not in expired.committed_ids, "over-age message was consumed")
    _assert(record["action"] == "HOLD" and expired.version == 0, "expiry created an update")
    return {
        "first_reason": first["reason"],
        "complement_reason": second["reason"],
        "complement_distances": {"H": second["d_h"], "A": second["d_a"], "P": second["d_p"]},
        "deadline_reason": deadline["reason"],
        "expired_state": stale.state,
    }


def test_replacement_endpoint_and_reentry() -> dict:
    mu = np.asarray([0.5, 0.5], dtype=np.float64)
    scheduler = Scheduler("S-Proj", mu)
    first = synthetic_attempt("a", 0, (1.0, 0.0))
    second = synthetic_attempt("a", 1, (0.0, 1.0))
    for attempt in (first, second):
        scheduler.begin_close(attempt.registration_window)
        scheduler.register(attempt)
        scheduler.deliver(attempt.attempt_id)
        scheduler.close(attempt.registration_window)
    _assert(scheduler.terminal[first.attempt_id].state == "superseded", "older same-client update survived")
    scheduler.begin_close(2)
    scheduler.close(2)
    scheduler.begin_close(3)
    release = scheduler.close(3)
    _assert(release["reason"] == "DEADLINE_RELEASE", "replacement pool did not reach the deadline")
    _assert(release["committed_attempt_ids"] == [second.attempt_id], "superseded update re-entered the release")
    try:
        scheduler.begin_close(4)
        scheduler.register(second)
        raise AssertionError("committed attempt was registered again")
    except SchedulerFault:
        pass

    endpoint = Scheduler("S-Proj", mu)
    only = synthetic_attempt("z", 0, (1.0, 0.0))
    endpoint.begin_close(0)
    endpoint.register(only)
    endpoint.deliver(only.attempt_id)
    endpoint.close(0)
    endpoint.finish()
    _assert(endpoint.terminal[only.attempt_id].state == "endpoint_unconsumed", "endpoint message was consumed")
    try:
        endpoint.begin_close(1)
        raise AssertionError("endpoint inventory accepted another close")
    except SchedulerFault:
        pass
    return {
        "superseded": first.attempt_id,
        "committed": release["committed_attempt_ids"],
        "endpoint_state": endpoint.terminal[only.attempt_id].state,
    }


def test_solver_empty_pool_and_design() -> dict:
    mu = np.asarray([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    solver = DistanceSolver(mu)
    identity = np.eye(4, dtype=np.float64)
    distance, alpha = solver.solve(identity)
    _assert(abs(distance) <= 1e-8, "balanced compositions were not feasible at distance zero")
    _assert(float(alpha.max()) <= 0.5 + 1e-6, "cap was violated")
    _assert(float(np.square(alpha).sum()) <= (1.0 / 3.0) + 1e-6, "ESS ball was violated")
    try:
        solver.solve(identity, cap_override=0.1)
        raise AssertionError("infeasible cap returned a distance")
    except DistanceFailure as exc:
        _assert(not hasattr(exc, "value"), "failed solve exposed a reusable value")
    again, _alpha = solver.solve(identity)
    _assert(abs(again) <= 1e-8, "a failed solve poisoned the next solve")

    empty = Scheduler("S-Proj", mu)
    empty.begin_close(0)
    record = empty.close(0)
    _assert(record["reason"] == "HOLD_EMPTY", "empty pool did not hold")
    _assert(empty.solver.calls == 0 and empty.optimizer["step_count"] == 0, "empty pool created a solve or a step")

    from raven_mcs.sag.r1l_design import (
        DesignConfiguration,
        apply_configured_design_zeta,
        configured_decide_gate_and_design,
    )

    configuration = DesignConfiguration(enabled=True, source="support-consumption-v1")
    decision = configured_decide_gate_and_design(
        {"certificate_state": "WARMUP", "C_LCB": 0.0},
        configuration=configuration,
        window_id=0,
    )
    zeta = apply_configured_design_zeta(np.asarray([2.0, 0.5], dtype=np.float64), decision["Design_t"])
    _assert(decision["Design_t"] == 1 and decision["Gate_t"] == 0, "configured Design followed the gate")
    _assert(np.allclose(zeta, [2.0, 0.5]), "Design 1 did not keep the configured ratio")
    runner = ProtocolRunner()
    for name in ("TwoStage-Hájek", "FedAvg-Window"):
        try:
            runner.run_external(name)
            raise AssertionError(f"{name} executed without training approval")
        except NotAuthorized:
            pass
    try:
        runner.measure(None)
        raise AssertionError("measurement ran without a checkpoint")
    except NotAuthorized:
        pass
    return {
        "distance": distance,
        "alpha_max": float(alpha.max()),
        "ess_square": float(np.square(alpha).sum()),
        "empty_solver_calls": empty.solver.calls,
        "design_t": int(decision["Design_t"]),
        "gate_t": int(decision["Gate_t"]),
        "configured_zeta": zeta.tolist(),
    }


def test_save_restore() -> dict:
    mu = np.asarray([0.5, 0.5], dtype=np.float64)
    scheduler = Scheduler("S-Proj", mu, rng_seed=11)
    first = synthetic_attempt("a", 0, (1.0, 0.0))
    second = synthetic_attempt("b", 1, (0.0, 1.0))
    scheduler.begin_close(0)
    scheduler.register(first)
    scheduler.deliver(first.attempt_id)
    scheduler.close(0)
    scheduler.begin_close(1)
    scheduler.register(second)
    scheduler.deliver(second.attempt_id)
    scheduler.close(1)
    snap = pickle.loads(pickle.dumps(scheduler.snapshot()))
    draw = float(scheduler.rng.random())
    scheduler.version = 99
    scheduler.optimizer["step_count"] = 99
    try:
        scheduler.restore({"weights": [0.0]})
        raise AssertionError("weights-only snapshot was accepted")
    except SchedulerFault:
        pass
    scheduler.restore(snap)
    _assert(float(scheduler.rng.random()) == draw, "RNG state was not restored")
    _assert(scheduler.version == 1, "version was not restored")
    _assert(scheduler.optimizer["step_count"] == 1, "optimizer state was not restored")
    _assert(len(scheduler.ledger) == 2, "ledger was not restored")
    _assert(scheduler.budget["releases"] == 1, "budget was not restored")
    _assert(set(scheduler.committed_ids) == {first.attempt_id, second.attempt_id}, "pool commit set changed")
    return {
        "version": scheduler.version,
        "optimizer_steps": scheduler.optimizer["step_count"],
        "ledger_rows": len(scheduler.ledger),
        "releases": scheduler.budget["releases"],
    }


def run_fixture_tests() -> dict:
    return {
        "hold_complement_deadline_expiry": test_hold_complement_deadline_and_expiry(),
        "replacement_endpoint_reentry": test_replacement_endpoint_and_reentry(),
        "solver_empty_pool_design": test_solver_empty_pool_and_design(),
        "save_restore": test_save_restore(),
        "status": "PASS",
    }


if __name__ == "__main__":
    result = run_fixture_tests()
    print(result["status"])
