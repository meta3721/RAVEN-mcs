"""Canary-specific Traffic sealed-five exclusion (beyond formal-seed reuse guard)."""

from __future__ import annotations

from typing import Any

from raven_mcs.e3.canary.constants import (
    CANARY_SEED,
    E2_TRAFFIC_REUSED_METHODS,
    FORMAL_SEEDS,
    SCENARIO,
    TRAFFIC_CANARY_METHODS,
)
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
    is_reused_e2_traffic_block,
)


class CanaryTrafficSealedMethodBlocked(RuntimeError):
    CODE = "REUSED_METHOD_PATH_NOT_EXECUTED_IN_TRAFFIC_CANARY"


def is_traffic_canary_sealed_method(*, dataset: str, method: str) -> bool:
    return (
        str(dataset).lower() == "traffic"
        and str(method).lower() in set(E2_TRAFFIC_REUSED_METHODS)
    )


def assert_canary_schedulable(*, dataset: str, method: str, seed: int) -> None:
    # Formal sealed block (seeds 30001-30020)
    assert_schedulable_e3_run(
        dataset=dataset, scenario=SCENARIO, seed=int(seed), method=method
    )
    # Canary must never schedule the sealed five on Traffic at any seed
    if is_traffic_canary_sealed_method(dataset=dataset, method=method):
        raise CanaryTrafficSealedMethodBlocked(
            f"{CanaryTrafficSealedMethodBlocked.CODE}: "
            f"dataset={dataset} method={method} seed={seed}"
        )


def build_traffic_reuse_guard_evidence() -> dict[str, Any]:
    attempted = []
    blocked = True
    for method in E2_TRAFFIC_REUSED_METHODS:
        try:
            assert_canary_schedulable(
                dataset="traffic", method=method, seed=CANARY_SEED
            )
            attempted.append({"method": method, "blocked": False})
            blocked = False
        except (CanaryTrafficSealedMethodBlocked, DuplicateReusedTrafficRunBlocked) as exc:
            attempted.append(
                {"method": method, "blocked": True, "code": getattr(exc, "CODE", str(exc))}
            )
    # Also prove formal-seed path still blocked by protocol guard
    formal_blocked = True
    formal_attempts = []
    for method in E2_TRAFFIC_REUSED_METHODS[:1]:
        for seed in (FORMAL_SEEDS[0], FORMAL_SEEDS[-1]):
            try:
                assert_schedulable_e3_run(
                    dataset="traffic", scenario=SCENARIO, seed=seed, method=method
                )
                formal_blocked = False
                formal_attempts.append({"seed": seed, "blocked": False})
            except DuplicateReusedTrafficRunBlocked:
                formal_attempts.append({"seed": seed, "blocked": True})
    return {
        "sealed_methods": list(E2_TRAFFIC_REUSED_METHODS),
        "protected_formal_seeds": FORMAL_SEEDS,
        "canary_seed": CANARY_SEED,
        "canary_allowed_traffic_methods": list(TRAFFIC_CANARY_METHODS),
        "scheduler_exclusion_proof": attempted,
        "attempted_duplicate_scheduling_test": attempted,
        "duplicate_blocked": blocked and all(r["blocked"] for r in attempted),
        "formal_block_still_active": formal_blocked,
        "formal_attempts": formal_attempts,
        "is_reused_e2_helper": is_reused_e2_traffic_block(
            dataset="traffic",
            scenario=SCENARIO,
            seed=FORMAL_SEEDS[0],
            method=E2_TRAFFIC_REUSED_METHODS[0],
        ),
        "status": "PASS" if blocked and formal_blocked else "FAIL",
    }
