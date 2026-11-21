"""Seed-major E4 logical run matrix."""
from .constants import ABLATIONS, DATASETS, FORMAL_SEEDS, ROUND, SCENARIO

def logical_run_id(dataset: str, method: str, seed: int) -> str:
    return f"e4::{dataset}::{SCENARIO}::{method}::seed{seed}"

def build_matrix() -> dict:
    rows = [
        {"dataset": dataset, "method": method, "seed": seed,
         "scenario": SCENARIO, "kind": "new",
         "logical_run_id": logical_run_id(dataset, method, seed)}
        for seed in FORMAL_SEEDS for dataset in DATASETS for method in ABLATIONS
    ]
    assert len(rows) == 200
    return {"round": ROUND, "ordering": "seed-major", "n_new": len(rows), "rows": rows}
