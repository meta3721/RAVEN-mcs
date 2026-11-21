#!/usr/bin/env python3
"""Run ObsUse-Window on sealed E3 SensorScope/U-Air traces without touching formal artifacts.

Reuses EventTraces and seeds 30001-30020 from artifacts/e3_formal_runs_r1.
Writes new runs to artifacts/e3_obsuse_window_r1.
Does not run Traffic. Does not overwrite sealed FedAvg/TwoStage/RAVEN or FedAU runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.formal.constants import FORMAL_SEEDS
from raven_mcs.e3.real_runner.runner import run_e3_real

FORMAL_ART = _ROOT / "artifacts" / "e3_formal_runs_r1"
OUT_ART = _ROOT / "artifacts" / "e3_obsuse_window_r1"
DATASETS = ("sensorscope", "uair")
METHOD = "obsuse_window"
LOCAL_STEPS = 2


def eventtrace_dir(dataset: str, seed: int) -> Path:
    return (
        FORMAL_ART
        / "eventtraces"
        / dataset
        / f"seed{seed}"
        / "training_eventtrace"
    )


def run_one(dataset: str, seed: int, *, force: bool = False) -> dict:
    run_dir = OUT_ART / "runs" / dataset / METHOD / f"seed{seed}"
    marker = run_dir / "final_metrics.json"
    if marker.is_file() and not force:
        metrics = json.loads(marker.read_text(encoding="utf-8"))
        return {
            "status": "REUSED",
            "dataset": dataset,
            "seed": seed,
            "RMSE_mu": metrics.get("RMSE_mu"),
            "Tail_RMSE": metrics.get("Tail_RMSE"),
            "Delta_group": metrics.get("Delta_group"),
            "Delta_c_s": metrics.get("Delta_c_s"),
        }
    et = eventtrace_dir(dataset, seed)
    if not (et / "events.parquet").is_file():
        raise FileNotFoundError(f"missing sealed EventTrace: {et}")
    ds = load_paper_dataset(_ROOT, dataset)
    mapping = load_spatial_to_client(_ROOT, dataset)
    result = run_e3_real(
        root=_ROOT,
        run_dir=run_dir,
        dataset=ds,
        method=METHOD,
        seed=int(seed),
        eventtrace_dir=et,
        spatial_to_client=mapping,
        dataset_name=dataset,
        local_steps=LOCAL_STEPS,
        source_identity={
            "git_commit": "obsuse_window_sidepath_r1",
            "note": "windowed Obs+Use inverse weighting; not an official reproduction",
        },
    )
    metrics = result.get("metrics") or {}
    return {
        "status": result.get("status", "DONE"),
        "dataset": dataset,
        "seed": seed,
        "RMSE_mu": metrics.get("RMSE_mu"),
        "Tail_RMSE": metrics.get("Tail_RMSE"),
        "Delta_group": metrics.get("Delta_group"),
        "Delta_c_s": metrics.get("Delta_c_s"),
        "runtime_seconds": metrics.get("runtime_seconds"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["sensorscope", "uair", "all"], default="all")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    datasets = DATASETS if args.dataset == "all" else (args.dataset,)
    seeds = [args.seed] if args.seed is not None else list(FORMAL_SEEDS)
    OUT_ART.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    for dataset in datasets:
        for seed in seeds:
            print(f"START {dataset} {METHOD} seed{seed}", flush=True)
            try:
                row = run_one(dataset, seed, force=args.force)
                print(
                    f"DONE {dataset} seed{seed} status={row['status']} "
                    f"RMSE_mu={row.get('RMSE_mu')} Delta_c_s={row.get('Delta_c_s')}",
                    flush=True,
                )
                rows.append(row)
            except Exception as exc:  # noqa: BLE001
                print(f"FAIL {dataset} seed{seed}: {exc}", flush=True)
                failures.append({"dataset": dataset, "seed": seed, "error": str(exc)})
    ledger = OUT_ART / "run_ledger.json"
    ledger.write_text(json.dumps({"rows": rows, "failures": failures}, indent=2), encoding="utf-8")
    if failures:
        print(f"FAILED {len(failures)} / {len(rows) + len(failures)}", flush=True)
        return 1
    print(f"OK {len(rows)} runs", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
