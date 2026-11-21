"""Refuse scheduling of the sealed E2 Traffic Complete-aligned 100-run block."""

from __future__ import annotations

from typing import Iterable

from raven_mcs.e3.protocol_closure.constants import (
    E2_TRAFFIC_REUSED_METHODS,
    FORMAL_SEEDS,
    SCENARIO,
)


class DuplicateReusedTrafficRunBlocked(RuntimeError):
    """Raised when a scheduler attempts to rerun a sealed reusable Traffic block."""

    CODE = "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED"


def is_reused_e2_traffic_block(
    *,
    dataset: str,
    scenario: str,
    seed: int,
    method: str,
) -> bool:
    return (
        str(dataset).lower() == "traffic"
        and str(scenario).lower() == SCENARIO
        and int(seed) in set(FORMAL_SEEDS)
        and str(method).lower() in set(E2_TRAFFIC_REUSED_METHODS)
    )


def assert_schedulable_e3_run(
    *,
    dataset: str,
    scenario: str,
    seed: int,
    method: str,
) -> None:
    if is_reused_e2_traffic_block(
        dataset=dataset, scenario=scenario, seed=seed, method=method
    ):
        raise DuplicateReusedTrafficRunBlocked(
            f"{DuplicateReusedTrafficRunBlocked.CODE}: "
            f"dataset={dataset} scenario={scenario} seed={seed} method={method} "
            "is REUSE_ONLY_NO_RERUN from sealed E2 Traffic Complete-aligned."
        )


def filter_new_schedule(
    rows: Iterable[dict],
) -> list[dict]:
    """Drop any schedule rows that collide with the reusable Traffic block."""
    out: list[dict] = []
    for row in rows:
        if is_reused_e2_traffic_block(
            dataset=str(row["dataset"]),
            scenario=str(row.get("scenario", SCENARIO)),
            seed=int(row["seed"]),
            method=str(row["method"]),
        ):
            continue
        out.append(row)
    return out
