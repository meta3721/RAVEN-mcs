"""Formal matrix; sealed Traffic methods are evidence rows, never scheduled."""
from __future__ import annotations
from typing import Any
from .constants import ALL_METHODS, FORMAL_SEEDS, NEW_TRAFFIC_METHODS, REUSED_TRAFFIC_METHODS, SCENARIO

def logical_run_id(dataset: str, method: str, seed: int) -> str:
    return f"e3::{dataset}::{SCENARIO}::{method}::seed{seed}"

def build_formal_matrix() -> dict[str, Any]:
    rows = []
    for seed in FORMAL_SEEDS:
        for dataset in ("sensorscope", "uair"):
            for method in ALL_METHODS:
                rows.append({"dataset": dataset, "method": method, "seed": seed, "stage": "A" if dataset == "sensorscope" else "B", "kind": "new", "logical_run_id": logical_run_id(dataset, method, seed)})
        for method in NEW_TRAFFIC_METHODS:
            rows.append({"dataset": "traffic", "method": method, "seed": seed, "stage": "C", "kind": "new", "logical_run_id": logical_run_id("traffic", method, seed)})
        for method in REUSED_TRAFFIC_METHODS:
            rows.append({"dataset": "traffic", "method": method, "seed": seed, "stage": "reused", "kind": "reused", "logical_run_id": logical_run_id("traffic", method, seed)})
    new = [r for r in rows if r["kind"] == "new"]
    reused = [r for r in rows if r["kind"] == "reused"]
    assert len(new) == 560 and len(reused) == 100 and len(rows) == 660
    assert not {r["method"] for r in new if r["dataset"] == "traffic"} & set(REUSED_TRAFFIC_METHODS)
    return {"round": "E3-FORMAL-RUNS-R1", "scenario": SCENARIO, "n_new": len(new), "n_reused": len(reused), "n_total": len(rows), "rows": rows}
