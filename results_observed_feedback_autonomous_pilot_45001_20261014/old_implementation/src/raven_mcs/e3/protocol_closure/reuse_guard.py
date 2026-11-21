"""Refuse scheduling of the sealed E2 Traffic Complete-aligned 100-run block.

Exemption (2026-10-08): `assert_schedulable_e3_run` accepts an explicit, default-False
`allow_reused_traffic_rerun` opt-in.  The default behaviour is unchanged for every existing caller;
only a caller that passes the flag can schedule a reused-block cell, and `run_e3_real` reads that flag
from its own `source_identity`, The run ledger carries only `git_commit`, `source_manifest_hash`, `method_source_hash`, `runner_source_hash` and `dataset_hash` from `source_identity` (runner.py L307-L311), so the exemption itself must be recorded by the caller - in this workspace the S1' driver writes `REUSE_GUARD_EXEMPTION.json` and a `reuse_guard_exemption` field in `SERVER_OPT_META.json` into every exempted run directory.  The
exemption is announced with a `RuntimeWarning` so it cannot be exercised silently.  Authorized
explicitly by the user; recorded in the diagnosis ledger Part IX item 65.
"""

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
    allow_reused_traffic_rerun: bool = False,
) -> None:
    if allow_reused_traffic_rerun and is_reused_e2_traffic_block(
        dataset=dataset, scenario=scenario, seed=seed, method=method
    ):
        import warnings

        warnings.warn(
            "REUSED_TRAFFIC_RERUN_ALLOWED: scheduling "
            f"dataset={dataset} scenario={scenario} seed={seed} method={method}, which is "
            "REUSE_ONLY_NO_RERUN from the sealed E2 Traffic Complete-aligned block, because the "
            "caller passed allow_reused_traffic_rerun=True. The artifacts this run writes are NOT "
            "the sealed objects.",
            RuntimeWarning,
            stacklevel=2,
        )
        return
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
