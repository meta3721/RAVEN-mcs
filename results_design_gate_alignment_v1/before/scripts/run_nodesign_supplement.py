#!/usr/bin/env python3
"""NoDesign supplement for City Scanner visit-occupancy and Pilot2 measured-O.

Uniform reporting rule: RAVEN-NoDesign (raven_wo_design) is the primary row on
every block, RAVEN-Design the secondary row.  The frozen City Scanner and
Pilot2 matrices only have RAVEN-Design, so this driver trains raven_wo_design
on the same frozen EventTraces, seeds, s_max, windows and lambdas.

The original City Scanner driver (scripts/run_c1_cityscanner.py) was lost;
this driver rebuilds its training stage.  A reproduction gate must pass before
any new row is trained: re-run frozen RAVEN-Design on the canary seed and
match the frozen RMSE_mu.  Outputs go to results_nodesign_supplement/ only;
frozen result folders are read, never written.
"""

from __future__ import annotations

import argparse
import gc
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_joint_ou_cs_p2 as p2  # noqa: E402  (also installs solver-noise clip)
from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.data.base import DatasetMetadata  # noqa: E402
from raven_mcs.data.processed_dataset import ProcessedDataset  # noqa: E402
from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization  # noqa: E402
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict  # noqa: E402
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu  # noqa: E402
from raven_mcs.metrics.distribution import delta_group  # noqa: E402
from raven_mcs.simulation.event_trace import load_event_trace  # noqa: E402
from raven_mcs.training.window_runner import build_full_runner  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

OUT = ROOT / "results_nodesign_supplement" / "round_v1"
REGION_ORDER = ("region0", "region1", "region2", "region3")
REPRO_TOL = 1e-9

BLOCKS: dict[str, dict[str, Any]] = {
    "cityscanner": {
        "dataset": "cityscanner_nyc_pm25",
        "trace_root": ROOT / "artifacts" / "e3_c1_cityscanner_eventtraces_v1",
        "frozen_runs": ROOT / "results_c1_cityscanner" / "round_v1" / "runs",
        "frozen_marker": "CS_ACCEPTED.json",
        "frozen_setup": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_TRAIN_SETUP.json",
        "decision": ROOT / "results_c1_cityscanner" / "round_v1" / "CS_PHI_DECISION.json",
        "seeds": list(range(32001, 32011)),
    },
    "pilot2": {
        "dataset": "cityscanner_nyc_p2_measured_o",
        "trace_root": p2.TRACE_ROOT,
        "frozen_runs": p2.OUT / "runs",
        "frozen_marker": "JO_ACCEPTED.json",
        "frozen_setup": p2.OUT / "JO_TRAIN_SETUP.json",
        "decision": p2.OUT / "JO_PHI_DECISION.json",
        "seeds": list(p2.FORMAL_SEEDS),
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _log(line: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "EXECUTION_LOG.md"
    if not path.is_file():
        path.write_text("# NoDesign supplement execution log\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"- {_now()} {line}\n")
    print(line, flush=True)


def _load_cityscanner() -> tuple[ProcessedDataset, pd.DataFrame, pd.DataFrame]:
    metadata = DatasetMetadata(
        dataset="cityscanner_nyc_pm25",
        target_name="pm25",
        target_unit="ug_per_m3",
        spatial_unit="grid_cell_500m",
        time_unit="30min",
        source_name="MIT Senseable City Lab City Scanner hyperlocal environmental CSVs",
        source_url="https://doi.org/10.5281/zenodo.7961851",
        raw_license="cc-by-4.0",
        filtering_rules=(
            "Drop non-finite latitude, longitude, time, or pm25",
            "Drop pm25 < 0 or pm25 > 1000",
        ),
    )
    metadata.validate()
    ds = ProcessedDataset(ROOT / "data" / "processed" / "cityscanner_nyc_pm25", metadata)
    apply_train_zscore_standardization(ds)
    atomic = pd.read_parquet(ROOT / "data" / "processed" / "cityscanner_nyc_pm25" / "atomic_units.parquet")
    return ds, atomic, atomic


def _load_pilot2() -> tuple[ProcessedDataset, pd.DataFrame, pd.DataFrame]:
    atomic, occ = p2.load_tables()
    return p2.load_cityscanner_dataset(), atomic, occ


def build_setup(block: str) -> dict[str, Any]:
    cfg = BLOCKS[block]
    ds, atomic, occ = _load_cityscanner() if block == "cityscanner" else _load_pilot2()
    decision = json.loads(Path(cfg["decision"]).read_text(encoding="utf-8"))
    g2i = {str(g): i for g, i in ds._target_group_str_to_int.items()}
    if set(g2i) != set(REGION_ORDER):
        raise RuntimeError(f"h encoding {g2i} != {REGION_ORDER}")
    mu = np.zeros(4, dtype=np.float64)
    for r in REGION_ORDER:
        mu[int(g2i[r])] = float(decision["mu"][r])
    mu = mu / float(mu.sum())
    spatial_to_client = {str(s): str(s) for s in occ["spatial_id"].astype(str).unique()}
    frame = occ.copy()
    frame["target_group"] = frame["target_group"].astype(str)
    frame["target_group_main"] = frame["target_group"]
    frame["support_flag"] = True
    pi_frame = build_pi_target(frame, spatial_to_client, split="test")
    pi_target = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples()
    }
    pi_opp = p2.build_occupancy_pi_opp(occ)
    frozen = json.loads(Path(cfg["frozen_setup"]).read_text(encoding="utf-8"))
    checks = {
        "n_pi_target_keys": (len(pi_target), int(frozen["n_pi_target_keys"])),
        "n_pi_opp_keys": (len(pi_opp), int(frozen["n_pi_opp_keys"])),
        "mu_max_abs_diff": (
            float(np.max(np.abs(mu - np.asarray(frozen["mu"], dtype=np.float64)))),
            0.0,
        ),
    }
    if checks["n_pi_target_keys"][0] != checks["n_pi_target_keys"][1]:
        raise RuntimeError(f"pi_target keys {checks['n_pi_target_keys']}")
    if checks["n_pi_opp_keys"][0] != checks["n_pi_opp_keys"][1]:
        raise RuntimeError(f"pi_opp keys {checks['n_pi_opp_keys']}")
    if checks["mu_max_abs_diff"][0] > 1e-12:
        raise RuntimeError(f"mu differs from frozen setup: {checks['mu_max_abs_diff']}")
    return {
        "ds": ds,
        "atomic": atomic,
        "mu": mu,
        "pi_target": pi_target,
        "pi_opp": pi_opp,
        "setup_checks": {k: list(v) for k, v in checks.items()},
    }


def train_one(block: str, setup: dict[str, Any], *, method: str, seed: int, tag: str) -> dict[str, Any]:
    cfg = BLOCKS[block]
    dataset = cfg["dataset"]
    run_dir = OUT / tag / dataset / method / f"seed{seed}"
    marker = run_dir / "ACCEPTED.json"
    if marker.is_file():
        return {"status": "REUSED", **json.loads(marker.read_text(encoding="utf-8"))}
    et = Path(cfg["trace_root"]) / dataset / f"seed{seed}" / "training_eventtrace"
    if not (et / "events.parquet").is_file():
        raise FileNotFoundError(et)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    trace, identity = load_event_trace(et)
    nwin = int(trace.metadata.num_windows)
    if nwin != 100:
        raise RuntimeError(f"expected 100 windows, got {nwin}")
    runner = build_full_runner(
        trace,
        setup["ds"],
        method=method,
        n_groups=4,
        model_seed=int(seed),
        local_steps=p2.LOCAL_STEPS,
        target_mu=setup["mu"],
        pi_target=setup["pi_target"],
        s_max=p2.S_MAX,
        device="cpu",
        use_coarse_time_groups=False,
        pi_opp_joint=setup["pi_opp"],
    )
    runner._decide_g_r = p2._skip_unused_gate.__get__(runner, type(runner))
    orig_pw = runner._process_window
    vers_by_window: dict[int, set[int]] = {w: set() for w in range(nwin)}
    for w_id, v_id in zip(
        trace.events["window_id"].astype(int).tolist(),
        trace.events["downloaded_version"].astype(int).tolist(),
    ):
        if 0 <= int(w_id) < nwin:
            vers_by_window[int(w_id)].add(int(v_id))
    future_versions: dict[int, set[int]] = {}
    acc: set[int] = set()
    for w in range(nwin - 1, -1, -1):
        future_versions[w] = set(acc)
        acc |= vers_by_window[w]

    def _pw(window_id, events, orig_pw=orig_pw):
        out = orig_pw(window_id, events)
        wid = int(window_id)
        needed = set(future_versions.get(wid, set()))
        needed.add(int(runner.clock.model_version))
        for ver in list(runner.model_versions):
            if int(ver) not in needed:
                del runner.model_versions[ver]
        gc.collect()
        return out

    runner._process_window = _pw
    try:
        window_metrics = runner.run()
    except Exception:
        import traceback

        (run_dir / "TRAIN_TRACEBACK.txt").write_text(traceback.format_exc(), encoding="utf-8")
        _log(f"TRAIN failed {block} {method} seed{seed}")
        raise
    pred = _predict(runner, setup["ds"], split="test")
    mu_w = _mu_weights_for_test(pred, setup["mu"])
    rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w))
    mae = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w))
    gids = pred["groups"]
    wg_vals = [p2._wrmse_block(pred["y_true"], pred["y_pred"], gids == g, mu_w) for g in range(4)]
    try:
        d_group = float(delta_group(runner.omega_bar(), setup["mu"]))
    except Exception:
        d_group = float("nan")
    d_cs = p2.accumulate_delta_cs(
        window_metrics=window_metrics,
        diagnostics=list(runner.diagnostics),
        atomic=setup["atomic"],
        pi_target=setup["pi_target"],
        method=method,
    )
    accepted = {
        "block": block,
        "dataset": dataset,
        "method": method,
        "seed": int(seed),
        "RMSE_mu": rmse,
        "MAE_mu": mae,
        "WorstGroupRMSE": float(np.nanmax(np.asarray(wg_vals, dtype=np.float64))),
        "WorstGroupRMSE_R0": wg_vals[0],
        "WorstGroupRMSE_R1": wg_vals[1],
        "WorstGroupRMSE_R2": wg_vals[2],
        "WorstGroupRMSE_R3": wg_vals[3],
        "Delta_group": d_group,
        "Delta_c_s": float(d_cs["Delta_c_s"]),
        "n_windows": nwin,
        "eventtrace_hash": identity.get("trace_hash"),
        "design_on": method != "raven_wo_design",
        "path_status": "REAL_PATH_EXECUTED",
        "device": "cpu",
        "runtime_seconds": float(time.perf_counter() - t0),
        "git_commit": _git_commit(),
        "gate_unused": True,
        "hybrid": True,
    }
    dump_json(accepted, marker)
    return {"status": "CREATED", **accepted}


def stage_repro(block: str, setup: dict[str, Any]) -> dict[str, Any]:
    cfg = BLOCKS[block]
    seed = int(cfg["seeds"][0])
    frozen = json.loads(
        (Path(cfg["frozen_runs"]) / cfg["dataset"] / "raven" / f"seed{seed}" / cfg["frozen_marker"]).read_text(
            encoding="utf-8"
        )
    )
    row = train_one(block, setup, method="raven", seed=seed, tag="repro")
    fields = ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
    diffs = {f: abs(float(row[f]) - float(frozen[f])) for f in fields}
    gate = {
        "block": block,
        "seed": seed,
        "frozen": {f: float(frozen[f]) for f in fields},
        "rerun": {f: float(row[f]) for f in fields},
        "abs_diff": diffs,
        "eventtrace_hash_match": row["eventtrace_hash"] == frozen["eventtrace_hash"],
        "tolerance": REPRO_TOL,
        "pass": bool(diffs["RMSE_mu"] <= REPRO_TOL and row["eventtrace_hash"] == frozen["eventtrace_hash"]),
        "setup_checks": setup["setup_checks"],
        "utc": _now(),
    }
    dump_json(gate, OUT / f"REPRO_GATE_{block}.json")
    _log(f"REPRO {block} seed{seed} pass={gate['pass']} dRMSE={diffs['RMSE_mu']:.3e}")
    return gate


def stage_train(block: str, setup: dict[str, Any], seeds: list[int]) -> None:
    gate_path = OUT / f"REPRO_GATE_{block}.json"
    if not gate_path.is_file() or not json.loads(gate_path.read_text(encoding="utf-8")).get("pass"):
        raise SystemExit(f"reproduction gate for {block} has not passed")
    for seed in seeds:
        row = train_one(block, setup, method="raven_wo_design", seed=seed, tag="runs")
        _log(
            f"{block} raven_wo_design seed{seed} {row['status']} RMSE_mu={row['RMSE_mu']:.6f} "
            f"WG={row['WorstGroupRMSE']:.6f} sec={row['runtime_seconds']:.1f}"
        )


def stage_tables(block: str) -> None:
    cfg = BLOCKS[block]
    dataset = cfg["dataset"]
    rows = []
    for method in ("fedavg_window", "twostage_hajek", "fedau_window", "obsuse_window", "raven"):
        for seed in cfg["seeds"]:
            path = Path(cfg["frozen_runs"]) / dataset / method / f"seed{seed}" / cfg["frozen_marker"]
            rec = json.loads(path.read_text(encoding="utf-8"))
            rows.append({"method": method, "seed": seed, "source": "frozen", **{
                k: rec[k] for k in ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
            }})
    for seed in cfg["seeds"]:
        path = OUT / "runs" / dataset / "raven_wo_design" / f"seed{seed}" / "ACCEPTED.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        rec = json.loads(path.read_text(encoding="utf-8"))
        rows.append({"method": "raven_wo_design", "seed": seed, "source": "supplement", **{
            k: rec[k] for k in ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
        }})
    df = pd.DataFrame(rows)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "tables" / f"{block}_seed_rows.csv", index=False)
    metrics = ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s")
    summary = (
        df.groupby("method")[list(metrics)]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = ["method"] + [f"{m}_{s}" for m, s in summary.columns[1:]]
    summary.to_csv(OUT / "tables" / f"{block}_summary.csv", index=False)
    paired = []
    for primary in ("raven_wo_design", "raven"):
        a_df = df[df["method"] == primary].set_index("seed")
        for comp in ("fedau_window", "obsuse_window", "fedavg_window", "twostage_hajek", "raven", "raven_wo_design"):
            if comp == primary:
                continue
            b_df = df[df["method"] == comp].set_index("seed")
            common = sorted(set(a_df.index) & set(b_df.index))
            rec: dict[str, Any] = {"primary": primary, "comparator": comp, "n_paired": len(common)}
            for m in metrics:
                a = a_df.loc[common, m].to_numpy(dtype=np.float64)
                b = b_df.loc[common, m].to_numpy(dtype=np.float64)
                rel = (a - b) / b
                rec[f"{m}_rel_mean"] = float(rel.mean())
                rec[f"{m}_rel_sd"] = float(rel.std(ddof=1))
                rec[f"{m}_wins"] = int((a < b).sum())
            paired.append(rec)
    pd.DataFrame(paired).to_csv(OUT / "tables" / f"{block}_paired.csv", index=False)
    _log(f"TABLES {block} written")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", choices=tuple(BLOCKS), required=True)
    ap.add_argument("--stage", choices=("repro", "train", "tables", "all"), required=True)
    ap.add_argument("--seeds", default="")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(BLOCKS[args.block]["seeds"])
    if args.stage == "tables":
        stage_tables(args.block)
        return 0
    setup = build_setup(args.block)
    if args.stage in ("repro", "all"):
        if not stage_repro(args.block, setup)["pass"] and args.stage == "all":
            return 2
    if args.stage in ("train", "all"):
        stage_train(args.block, setup, seeds)
        stage_tables(args.block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
