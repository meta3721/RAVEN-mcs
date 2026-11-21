"""Canary logical-run schedule (max 28 identities)."""

from __future__ import annotations

from typing import Any

from raven_mcs.e3.canary.constants import (
    ALL_CANONICAL_METHODS,
    CANARY_SEED,
    E2_TRAFFIC_REUSED_METHODS,
    PHASE1,
    PHASE2,
    SCENARIO,
    TRAFFIC_CANARY_METHODS,
)


def logical_run_id(dataset: str, method: str, seed: int = CANARY_SEED) -> str:
    return f"e3::{dataset}::{SCENARIO}::{method}::seed{seed}"


def build_canary_matrix() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for phase, pairs in ((1, PHASE1), (2, PHASE2)):
        for dataset, method in pairs:
            rows.append(
                {
                    "phase": phase,
                    "dataset": dataset,
                    "method": method,
                    "seed": CANARY_SEED,
                    "scenario": SCENARIO,
                    "logical_run_id": logical_run_id(dataset, method),
                }
            )
    assert len(rows) == 28, len(rows)
    assert len({r["logical_run_id"] for r in rows}) == 28
    # Traffic sealed five absent
    for r in rows:
        if r["dataset"] == "traffic":
            assert r["method"] in TRAFFIC_CANARY_METHODS
            assert r["method"] not in E2_TRAFFIC_REUSED_METHODS
    return {
        "canary_seed": CANARY_SEED,
        "n_logical_runs": len(rows),
        "phase1": 11,
        "phase2": 17,
        "sensorscope": 11,
        "uair": 11,
        "traffic": 6,
        "excluded_flamf_original": True,
        "traffic_do_not_rerun": list(E2_TRAFFIC_REUSED_METHODS),
        "all_canonical_methods_reference": list(ALL_CANONICAL_METHODS),
        "rows": rows,
    }
