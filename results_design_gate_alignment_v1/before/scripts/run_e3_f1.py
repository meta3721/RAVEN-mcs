#!/usr/bin/env python3
"""F-1 execution driver.

Implements the execution half of ccfa-review-reports/raven-mcs-f1-experiment-design.md.
Never writes under artifacts/e3_formal_runs_r1/.

Two arms, two artifact roots:
  arm N  artifacts/e3_f1_score_dependent_r1/  published EventTraces copied in, theta_O = 0
  arm S  artifacts/e3_f1_theta1_r1/           F-1-O traces generated with theta_O = 1.0

Stages
  copy-traces : arm N only. Copy the published EventTraces so the N arms run on bit-identical
                data (no regeneration, no RNG drift).
  gen-theta   : arm S only. Materialize the within-stratum theta_O traces.
  run         : execute cells through the canary real path (one process, one import).
  status      : summarize accepted runs.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PUB = ROOT / "artifacts" / "e3_formal_runs_r1"
ARMS = {
    "N": ROOT / "artifacts" / "e3_f1_score_dependent_r1",
    "S": ROOT / "artifacts" / "e3_f1_theta1_r1",
}
DEFAULT_DATASETS = ["sensorscope", "uair"]
DEFAULT_METHODS = ["raven", "raven_oracle_p"]
SEEDS = list(range(30001, 30021))
THETA = 1.0


def trace_dir(root: Path, dataset: str, seed: int) -> Path:
    return root / "eventtraces" / dataset / f"seed{seed}"


def copy_traces(art: Path, datasets: list[str], seeds: list[int]) -> int:
    n = 0
    for ds in datasets:
        for seed in seeds:
            src, dst = trace_dir(PUB, ds, seed), trace_dir(art, ds, seed)
            if not src.is_dir():
                print(f"MISSING published trace: {src}")
                continue
            if dst.is_dir():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            n += 1
    print(f"copied {n} trace dirs into {art.relative_to(ROOT)}")
    return n


def gen_theta(art: Path, datasets: list[str], seeds: list[int], theta: float) -> int:
    from raven_mcs.e3.canary.constants import M_MC
    from raven_mcs.e3.canary.dataset_load import (
        load_horizon, load_paper_dataset, load_spatial_to_client,
    )
    from raven_mcs.e3.real_runner.generator_r3_score import materialize_f1o_trace
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
    from raven_mcs.utils.serialization import dump_json

    n = 0
    for ds in datasets:
        dataset = load_paper_dataset(ROOT, ds)
        mapping = load_spatial_to_client(ROOT, ds)
        atomic, stratum_meta = apply_sealed_opportunity_stratum(
            dataset.atomic_df, dataset=ds, root=ROOT)
        n_windows = int(load_horizon(ROOT, ds)["chosen_E3_formal_windows"])
        for seed in seeds:
            out = trace_dir(art, ds, seed)
            if (out / "training_eventtrace" / "trace_identity.json").is_file():
                continue
            mat = materialize_f1o_trace(
                dataset=ds, atomic=atomic, spatial_to_client=mapping, out_dir=out,
                seed=int(seed), num_windows=n_windows, theta=float(theta), m_mc=M_MC,
            )
            dump_json({"stratum_meta": stratum_meta, "num_windows": n_windows,
                       "m_mc": M_MC, "theta_O": float(theta), "arm": "S"},
                      out / "generation_meta.json")
            n += 1
            print(f"theta={theta} {ds} seed{seed}: {mat['status']}")
    return n


def check_traces(art: Path, datasets: list[str], seeds: list[int], theta: float) -> None:
    """Refuse to run an arm whose traces are missing or carry the wrong theta_O.

    ensure_eventtrace regenerates a missing trace with the *published* generator (theta = 0),
    which would silently turn an S-arm cell into an N-arm cell. This guard makes that impossible.
    """
    bad = []
    for ds in datasets:
        for seed in seeds:
            out = trace_dir(art, ds, seed)
            ident = out / "training_eventtrace" / "trace_identity.json"
            meta = out / "generation_meta.json"
            if not ident.is_file():
                bad.append(f"{ds}/seed{seed}: no trace")
                continue
            if theta != 0.0:
                if not meta.is_file():
                    bad.append(f"{ds}/seed{seed}: no generation_meta.json")
                    continue
                got = json.loads(meta.read_text(encoding="utf-8")).get("theta_O")
                if got is None or abs(float(got) - float(theta)) > 1e-12:
                    bad.append(f"{ds}/seed{seed}: theta_O={got}, expected {theta}")
    if bad:
        raise SystemExit("TRACE_GUARD_FAILED:\n  " + "\n  ".join(bad[:20])
                         + (f"\n  ... and {len(bad)-20} more" if len(bad) > 20 else ""))
    print(f"trace guard OK: {len(datasets)*len(seeds)} traces, theta_O={theta}")


def run_cells(art: Path, datasets: list[str], methods: list[str], seeds: list[int],
              force: bool) -> list[dict]:
    from raven_mcs.e3.canary.execute import run_logical

    rows: list[dict] = []
    for ds in datasets:
        for method in methods:
            for seed in seeds:
                row = run_logical(root=ROOT, art=art, dataset=ds, method=method,
                                  seed=int(seed), local_steps=2, force=force)
                rows.append(row)
                print(f"{ds:<12}{method:<18}seed{seed}  "
                      f"{row.get('status') or row.get('execution_status'):<18}"
                      f"RMSE_mu={row.get('RMSE_mu')}", flush=True)
    out = art / "f1_run_status.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return rows


def status(art: Path, datasets: list[str], methods: list[str]) -> None:
    print(f"{'dataset':<12}{'method':<18}{'runs':>6}{'RMSE_mu mean':>16}")
    for ds in datasets:
        for method in methods:
            vals = []
            d = art / "runs" / ds / method
            for seed in sorted(d.glob("seed*")) if d.is_dir() else []:
                f = seed / "final_metrics.json"
                if f.is_file():
                    vals.append(json.loads(f.read_text(encoding="utf-8"))["RMSE_mu"])
            mean = f"{sum(vals)/len(vals):.6f}" if vals else "-"
            print(f"{ds:<12}{method:<18}{len(vals):>6}{mean:>16}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=["copy-traces", "gen-theta", "check-traces", "run", "status"])
    ap.add_argument("--arm", default="N", choices=sorted(ARMS))
    ap.add_argument("--datasets", nargs="*", default=DEFAULT_DATASETS)
    ap.add_argument("--methods", nargs="*", default=DEFAULT_METHODS)
    ap.add_argument("--seeds", nargs="*", type=int, default=None)
    ap.add_argument("--theta", type=float, default=THETA)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    seeds = args.seeds if args.seeds else SEEDS
    art = ARMS[args.arm]
    # arm N runs on the published (theta_O = 0) traces; only arm S carries a manipulation.
    theta = 0.0 if args.arm == "N" else args.theta

    if args.stage == "copy-traces":
        copy_traces(art, args.datasets, seeds)
    elif args.stage == "gen-theta":
        gen_theta(art, args.datasets, seeds, theta)
    elif args.stage == "check-traces":
        check_traces(art, args.datasets, seeds, theta)
    elif args.stage == "run":
        check_traces(art, args.datasets, seeds, theta)
        run_cells(art, args.datasets, args.methods, seeds, args.force)
    elif args.stage == "status":
        status(art, args.datasets, args.methods)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
