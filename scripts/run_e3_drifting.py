#!/usr/bin/env python3
"""Run the five-method E3 family under drifting EventTraces.

Does not touch sealed complete_aligned artifacts.
Writes artifacts/e3_drifting_r1/runs/{dataset}/{method}/seed{seed}/.
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

OUT_ART = _ROOT / "artifacts" / "e3_drifting_r1"
DATASETS = ("sensorscope", "uair")
METHODS = (
    "fedavg_window",
    "fedau_window",
    "obsuse_window",
    "twostage_hajek",
    "raven",
)
LOCAL_STEPS = 2
SCENARIO = "drifting"


def eventtrace_dir(dataset: str, seed: int) -> Path:
    return OUT_ART / "eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"


def run_one(dataset: str, method: str, seed: int, *, force: bool = False) -> dict:
    run_dir = OUT_ART / "runs" / dataset / method / f"seed{seed}"
    marker = run_dir / "final_metrics.json"
    if marker.is_file() and not force:
        metrics = json.loads(marker.read_text(encoding="utf-8"))
        return {
            "status": "REUSED",
            "dataset": dataset,
            "method": method,
            "seed": seed,
            "RMSE_mu": metrics.get("RMSE_mu"),
            "Tail_RMSE": metrics.get("Tail_RMSE"),
            "Delta_group": metrics.get("Delta_group"),
            "Delta_c_s": metrics.get("Delta_c_s"),
            "Q_norm1_over_S": metrics.get("Q_norm1_over_S"),
        }
    et = eventtrace_dir(dataset, seed)
    if not (et / "events.parquet").is_file():
        raise FileNotFoundError(
            f"missing drifting EventTrace: {et}. "
            "Run scripts/generate_e3_drifting_traces.py first."
        )
    ds = load_paper_dataset(_ROOT, dataset)
    mapping = load_spatial_to_client(_ROOT, dataset)
    result = run_e3_real(
        root=_ROOT,
        run_dir=run_dir,
        dataset=ds,
        method=method,
        seed=int(seed),
        eventtrace_dir=et,
        spatial_to_client=mapping,
        dataset_name=dataset,
        scenario=SCENARIO,
        local_steps=LOCAL_STEPS,
        source_identity={
            "git_commit": "e3_drifting_r1",
            "note": "opportunity-drift stress; isolated from sealed complete_aligned",
        },
    )
    metrics = result.get("metrics") or {}
    return {
        "status": result.get("status", "DONE"),
        "dataset": dataset,
        "method": method,
        "seed": seed,
        "RMSE_mu": metrics.get("RMSE_mu"),
        "Tail_RMSE": metrics.get("Tail_RMSE"),
        "Delta_group": metrics.get("Delta_group"),
        "Delta_c_s": metrics.get("Delta_c_s"),
        "Q_norm1_over_S": metrics.get("Q_norm1_over_S"),
        "runtime_seconds": metrics.get("runtime_seconds"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["sensorscope", "uair", "all"], default="all")
    parser.add_argument(
        "--method",
        choices=list(METHODS) + ["all"],
        default="all",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--start-seed", type=int, default=None)
    parser.add_argument("--end-seed", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    datasets = DATASETS if args.dataset == "all" else (args.dataset,)
    methods = METHODS if args.method == "all" else (args.method,)
    if args.seed is not None:
        seeds = [args.seed]
    elif args.start_seed is not None or args.end_seed is not None:
        start = int(args.start_seed or FORMAL_SEEDS[0])
        end = int(args.end_seed or FORMAL_SEEDS[-1])
        seeds = [s for s in FORMAL_SEEDS if start <= s <= end]
    else:
        seeds = list(FORMAL_SEEDS)
    OUT_ART.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    for dataset in datasets:
        for method in methods:
            for seed in seeds:
                print(f"START {dataset} {method} seed{seed}", flush=True)
                try:
                    row = run_one(dataset, method, seed, force=args.force)
                    print(
                        f"DONE {dataset} {method} seed{seed} status={row['status']} "
                        f"RMSE_mu={row.get('RMSE_mu')} Delta_c_s={row.get('Delta_c_s')}",
                        flush=True,
                    )
                    rows.append(row)
                except Exception as exc:  # noqa: BLE001
                    print(f"FAIL {dataset} {method} seed{seed}: {exc}", flush=True)
                    failures.append(
                        {
                            "dataset": dataset,
                            "method": method,
                            "seed": seed,
                            "error": str(exc),
                        }
                    )
    ledger = OUT_ART / "run_ledger.json"
    ledger.write_text(
        json.dumps({"rows": rows, "failures": failures}, indent=2),
        encoding="utf-8",
    )
    if failures:
        print(f"FAILED {len(failures)} / {len(rows) + len(failures)}", flush=True)
        return 1
    print(f"OK {len(rows)} runs", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
