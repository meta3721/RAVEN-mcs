#!/usr/bin/env python3
"""Measured-O Pilot2 ranking: real union R, measured PM O, controlled U.

Read post_review/JOINT_MEASURED_OU_RANK/TARGET_SPEC.json.
Does not recompute phi. Does not mix into Table II. Gate unused. Device=cpu.
"""

from __future__ import annotations

import argparse
import gc
import json
import shutil
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

from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.data.base import DatasetMetadata  # noqa: E402
from raven_mcs.data.cityscanner_p2_measured_o_eventtrace import (  # noqa: E402
    NUM_WINDOWS,
    generate_p2_measured_o_eventtrace,
)
from raven_mcs.data.processed_dataset import ProcessedDataset  # noqa: E402
from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization  # noqa: E402
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict  # noqa: E402
from raven_mcs.e3.target_pair.pair_state_v4 import (  # noqa: E402
    METHODS_REQUIRE_ATOMIC_W,
    bind_alpha_by_client,
    bind_w_by_unit,
)
from raven_mcs.aggregation import methods as _agg_methods  # noqa: E402
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu  # noqa: E402
from raven_mcs.metrics.distribution import delta_c_s, delta_group  # noqa: E402
from raven_mcs.simulation.event_trace import freeze_event_trace, load_event_trace  # noqa: E402
from raven_mcs.training.window_runner import build_full_runner  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def _normalize_clip_solver_noise(weights: np.ndarray) -> np.ndarray:
    """Clip tiny P2 solver negatives. Does not retune lambdas."""
    w = np.asarray(weights, dtype=np.float64)
    if np.any(w < 0):
        w = np.clip(w, 0.0, None)
    total = float(w.sum())
    if total <= 0:
        raise ValueError("server weights sum to zero")
    return w / total


_agg_methods._normalize = _normalize_clip_solver_noise

SPEC_PATH = ROOT / "post_review" / "JOINT_MEASURED_OU_RANK" / "TARGET_SPEC.json"
OUT = ROOT / "results_joint_ou" / "round_v1"
TRACE_ROOT = ROOT / "artifacts" / "e3_joint_ou_cs_p2_eventtraces_v1"
ATOMIC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "atomic_units.parquet"
OCC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "occupancy_units.parquet"
MEAS_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "client_measurements.parquet"
CANARY_SEED = 33001
FORMAL_SEEDS = list(range(33001, 33011))
EXPECTED_HASH = "06e2953afad17b27facfbf593d399be92255775c5c298e5c89924903a30a2de8"
EXPECTED_TRAIN_UNITS = 10141
EXPECTED_TRAIN_SLOTS = 1441
DATASET = "cityscanner_nyc_p2_measured_o"
LOCAL_STEPS = 2
S_MAX = 5
REGION_ORDER = ("region0", "region1", "region2", "region3")
SHARED_METHODS = ("fedavg_window", "twostage_hajek", "fedau_window", "obsuse_window")
REQUIRE_W = set(METHODS_REQUIRE_ATOMIC_W) | {"raven_wo_design"}
KILL_BAR = -0.005
GO_FIELDS = (
    "phi_train_unit",
    "n_train_units",
    "n_train_zero",
    "design_on",
    "scd_method",
    "train_full_design_extra",
    "used_y_or_rmse",
)


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "UNKNOWN"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(line: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "EXECUTION_LOG.md"
    if not path.is_file():
        path.write_text("# Measured-O Pilot2 execution log\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"- {_now()} {line}\n")
    print(line, flush=True)


def load_spec() -> dict[str, Any]:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if spec.get("status") != "LOCKED":
        raise SystemExit("TARGET_SPEC.json is not LOCKED")
    if spec.get("chosen_option") != "CS_NYC_P2_DUAL_SENSOR_MEASURED_O":
        raise SystemExit("this runner only implements CS_NYC_P2_DUAL_SENSOR_MEASURED_O")
    return spec


def load_go() -> dict[str, Any]:
    go_path = OUT / "GO.json"
    dec_path = OUT / "JO_PHI_DECISION.json"
    if not go_path.is_file() or not dec_path.is_file():
        raise FileNotFoundError("GO.json / JO_PHI_DECISION.json missing; do not recompute phi")
    go = json.loads(go_path.read_text(encoding="utf-8"))
    dec = json.loads(dec_path.read_text(encoding="utf-8"))
    expected = {
        "phi_train_unit": 0.0,
        "n_train_units": EXPECTED_TRAIN_UNITS,
        "n_train_zero": 0,
        "design_on": True,
        "scd_method": "raven",
        "train_full_design_extra": False,
        "used_y_or_rmse": False,
    }
    for key in GO_FIELDS:
        if go.get(key) != dec.get(key):
            raise RuntimeError(f"GO.{key} != DECISION.{key}")
        if go.get(key) != expected[key]:
            raise RuntimeError(f"GO.{key}={go.get(key)!r} != frozen {expected[key]!r}")
    ingest = json.loads((OUT / "INGEST_REPORT.json").read_text(encoding="utf-8"))
    if ingest.get("status") != "INGEST_FROZEN":
        raise RuntimeError(f"ingest status={ingest.get('status')}")
    if ingest.get("data_hash") != EXPECTED_HASH:
        raise RuntimeError("INGEST_REPORT data_hash mismatch")
    if ingest.get("clients") != "spatial_id":
        raise RuntimeError("clients must be spatial_id")
    return go


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    atomic = pd.read_parquet(ATOMIC_PATH)
    occ = pd.read_parquet(OCC_PATH)
    if int(len(occ)) != 14960:
        raise RuntimeError(f"occupancy rows {len(occ)} != 14960")
    if int(len(atomic)) != 13029:
        raise RuntimeError(f"atomic rows {len(atomic)} != 13029")
    train = occ.loc[occ["split"].astype(str) == "train"]
    if int(train["unit_id"].nunique()) != EXPECTED_TRAIN_UNITS:
        raise RuntimeError("train unique occupancy unit_id mismatch")
    if int(train["time_index"].nunique()) != EXPECTED_TRAIN_SLOTS:
        raise RuntimeError("train unique time_index mismatch")
    if float(occ["o_observed"].mean()) <= 0.0:
        raise RuntimeError("occupancy missing measured O")
    if occ["spatial_id"].astype(str).str.startswith("NYCP").any():
        raise RuntimeError("vehicle ids used as FL clients")
    return atomic, occ


def _device() -> str:
    return "cpu"


def stage_generate(*, seeds: list[int], force: bool) -> dict[str, Any]:
    load_spec()
    load_go()
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    atomic, occ = load_tables()
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        out = (
            TRACE_ROOT
            / DATASET
            / f"seed{seed}"
            / "training_eventtrace"
        )
        ident_path = out / "trace_identity.json"
        if ident_path.is_file() and not force:
            ident = json.loads(ident_path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "status": "REUSED",
                    "seed": int(seed),
                    "trace_hash": ident.get("trace_hash"),
                    "path": str(out.relative_to(ROOT)).replace("\\", "/"),
                    "n_windows": NUM_WINDOWS,
                }
            )
            _log(f"REUSED trace seed{seed}")
            continue
        if out.exists() and force:
            shutil.rmtree(out, ignore_errors=True)
        _log(f"START trace seed{seed}")
        t0 = time.perf_counter()
        method_independence_canary = False
        if seed == CANARY_SEED:
            trace_a, _, audit = generate_p2_measured_o_eventtrace(
                occupancy=occ,
                seed=int(seed),
                method="raven",
            )
            trace_b, _, _ = generate_p2_measured_o_eventtrace(
                occupancy=occ,
                seed=int(seed),
                method="fedavg_window",
            )
            if not trace_a.events.equals(trace_b.events):
                raise RuntimeError("EventTrace hash/content depends on method name")
            ident = freeze_event_trace(trace_a, out)
            audit["method_independence_canary"] = True
            method_independence_canary = True
        else:
            trace, _, audit = generate_p2_measured_o_eventtrace(
                occupancy=occ,
                seed=int(seed),
                method=None,
            )
            ident = freeze_event_trace(trace, out)
        if int(audit["n_windows"]) != NUM_WINDOWS:
            raise RuntimeError(f"expected {NUM_WINDOWS} windows")
        dump_json(audit, out.parent / "generation_meta.json")
        row = {
            "status": "CREATED",
            "seed": int(seed),
            "trace_hash": ident.get("trace_hash"),
            "path": str(out.relative_to(ROOT)).replace("\\", "/"),
            "n_windows": audit.get("n_windows"),
            "n_event_rows": audit.get("n_event_rows"),
            "n_clients": audit.get("n_clients"),
            "elapsed_sec": float(time.perf_counter() - t0),
            "method_independence_canary": method_independence_canary,
        }
        rows.append(row)
        _log(
            f"DONE trace seed{seed} windows={row['n_windows']} rows={row['n_event_rows']} "
            f"hash={row['trace_hash']}"
        )
    manifest = {
        "experiment_id": "JOINT-MEASURED-O-CS-NYC-P2",
        "trace_root": "artifacts/e3_joint_ou_cs_p2_eventtraces_v1/",
        "r_layer": "REAL_FROM_UNION_PM_NO2_GPS",
        "o_layer": "MEASURED_FINITE_PM25",
        "u_layer": "CONTROLLED_EXPERIMENTAL compute_usable_r3 s_max=5",
        "num_windows": NUM_WINDOWS,
        "window_map": "rank(time_index)*100//n_train_slots",
        "hybrid": True,
        "measured_o": True,
        "p_obs_bernoulli": False,
        "gate_unused": True,
        "method_independent": True,
        "rows": rows,
        "git_commit": _git_commit(),
        "generated_utc": _now(),
    }
    dump_json(manifest, OUT / "JO_TRACE_MANIFEST.json")
    complete = all(
        (
            TRACE_ROOT
            / "cityscanner_nyc_p2_measured_o"
            / f"seed{s}"
            / "training_eventtrace"
            / "trace_identity.json"
        ).is_file()
        for s in FORMAL_SEEDS
    )
    ingest_path = OUT / "INGEST_REPORT.json"
    ingest = json.loads(ingest_path.read_text(encoding="utf-8"))
    ingest["eventtrace_run"] = bool(complete)
    ingest.setdefault("train_run", False)
    dump_json(ingest, ingest_path)
    return manifest


def mandatory_methods(go: dict[str, Any]) -> list[str]:
    methods = list(SHARED_METHODS)
    scd = str(go["scd_method"])
    if scd not in methods:
        methods.append(scd)
    if bool(go.get("train_full_design_extra")) and "raven" not in methods:
        methods.append("raven")
    return methods


def _skip_unused_gate(self, window_id: int = -1):
    self._last_cert_diagnostics = {}
    self._last_gate_to_design = {}
    mode = str(getattr(self.policy, "gate_mode", "policy") or "policy")
    if mode == "always_on":
        return 1, {}, None, {}
    if mode == "always_off":
        return 0, {}, "OFF_MODE_NO_DESIGN", {}
    if bool(getattr(self.policy, "uses_design_ratio", False)):
        return 1, {}, None, {}
    return 0, {}, "OFF_MODE_NO_DESIGN", {}


def load_cityscanner_dataset() -> ProcessedDataset:
    metadata = DatasetMetadata(
        dataset="cityscanner_nyc_p2_measured_o",
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
    ds = ProcessedDataset(ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o", metadata)
    apply_train_zscore_standardization(ds)
    return ds


def build_occupancy_pi_opp(atomic: pd.DataFrame) -> dict[tuple[str, str], float]:
    train = atomic.loc[atomic["split"].astype(str) == "train"].copy()
    train["client_id"] = train["spatial_id"].astype(str)
    train["opportunity_stratum"] = train["opportunity_stratum"].astype(str)
    counts = train.groupby(["client_id", "opportunity_stratum"]).size()
    total = float(counts.sum())
    if total <= 0:
        raise RuntimeError("empty occupancy pi_opp")
    return {
        (str(k[0]), str(k[1])): float(v) / total
        for k, v in counts.items()
        if float(v) > 0.0
    }


def _wrmse_block(y_true, y_pred, mask, mu_w) -> float:
    if not np.any(mask):
        return float("nan")
    ww = mu_w[mask].copy()
    s = float(ww.sum())
    ww = ww / s if s > 0 else np.full(int(mask.sum()), 1.0 / int(mask.sum()))
    err = y_true[mask] - y_pred[mask]
    return float(np.sqrt(np.sum(ww * err * err)))


def accumulate_delta_cs(
    *,
    window_metrics,
    diagnostics,
    atomic: pd.DataFrame,
    pi_target: dict[tuple[str, str], float],
    method: str,
) -> dict[str, Any]:
    unit_s = {
        str(r.unit_id): str(r.opportunity_stratum) for r in atomic.itertuples(index=False)
    }
    pi_tar = {f"{k}::{s}": float(v) for (k, s), v in pi_target.items()}
    contrib: dict[str, float] = {}
    s_r = 0.0
    for wm in window_metrics:
        if not bool(getattr(wm, "active", False)):
            continue
        s_r += 1.0
        alpha_map = bind_alpha_by_client(wm)
        win_diag = [d for d in diagnostics if int(d.get("window_id", -1)) == int(wm.window_id)]
        for d in win_diag:
            cid = str(d["client_id"])
            if cid not in alpha_map:
                continue
            a = float(alpha_map[cid])
            w_map = bind_w_by_unit(d, method=method if method in REQUIRE_W else method)
            for uid, w in w_map.items():
                sid = f"{cid}::{unit_s[str(uid)]}"
                contrib[sid] = contrib.get(sid, 0.0) + float(a * w)
    denom = float(s_r) if s_r > 0 else 1.0
    keys = sorted(set(list(contrib.keys()) + list(pi_tar.keys())))
    pi_hat = np.asarray([contrib.get(k, 0.0) / denom for k in keys], dtype=np.float64)
    pi_t = np.asarray([pi_tar.get(k, 0.0) for k in keys], dtype=np.float64)
    if float(pi_hat.sum()) > 0:
        pi_hat = pi_hat / float(pi_hat.sum())
    return {"Delta_c_s": float(delta_c_s(pi_hat, pi_t)), "status": "OK"}


def train_one(
    *,
    ds,
    atomic: pd.DataFrame,
    method: str,
    seed: int,
    pi_target: dict[tuple[str, str], float],
    pi_opp: dict[tuple[str, str], float],
    mu: np.ndarray,
    device: str,
) -> dict[str, Any]:
    run_dir = OUT / "runs" / "cityscanner_nyc_p2_measured_o" / method / f"seed{seed}"
    marker = run_dir / "JO_ACCEPTED.json"
    if marker.is_file():
        prev = json.loads(marker.read_text(encoding="utf-8"))
        return {"status": "REUSED", **prev}
    et = TRACE_ROOT / "cityscanner_nyc_p2_measured_o" / f"seed{seed}" / "training_eventtrace"
    if not (et / "events.parquet").is_file():
        raise FileNotFoundError(et)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    trace, identity = load_event_trace(et)
    if int(trace.metadata.num_windows) != NUM_WINDOWS:
        raise RuntimeError(
            f"expected {NUM_WINDOWS} windows, got {trace.metadata.num_windows}"
        )
    runner = build_full_runner(
        trace,
        ds,
        method=method,
        n_groups=4,
        model_seed=int(seed),
        local_steps=LOCAL_STEPS,
        target_mu=mu,
        pi_target=pi_target,
        s_max=S_MAX,
        device=device,
        use_coarse_time_groups=False,
        pi_opp_joint=pi_opp,
    )
    runner._decide_g_r = _skip_unused_gate.__get__(runner, type(runner))
    nwin = int(trace.metadata.num_windows)
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
        if (wid + 1) % 25 == 0 or wid + 1 == nwin:
            _log(f"    window {wid+1}/{nwin} {method} seed{seed}")
        return out

    runner._process_window = _pw
    try:
        window_metrics = runner.run()
    except Exception:
        err_path = run_dir / "JO_TRAIN_TRACEBACK.txt"
        import traceback

        err_path.write_text(traceback.format_exc(), encoding="utf-8")
        _log(f"TRAIN failed {method} seed{seed}; traceback {err_path}")
        raise
    (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    torch.save(runner.theta, run_dir / "checkpoints" / "final.pt")
    pred = _predict(runner, ds, split="test")
    mu_w = _mu_weights_for_test(pred, mu)
    rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
    mae = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
    gids = pred["groups"]
    wg_vals = [
        _wrmse_block(pred["y_true"], pred["y_pred"], gids == g, mu_w) for g in range(4)
    ]
    worst = float(np.nanmax(np.asarray(wg_vals, dtype=np.float64)))
    try:
        d_group = float(delta_group(runner.omega_bar(), mu))
    except Exception:
        d_group = float("nan")
    d_cs = accumulate_delta_cs(
        window_metrics=window_metrics,
        diagnostics=list(runner.diagnostics),
        atomic=atomic,
        pi_target=pi_target,
        method=method,
    )
    accepted = {
        "dataset": "cityscanner_nyc_p2_measured_o",
        "method": method,
        "seed": int(seed),
        "RMSE_mu": rmse,
        "MAE_mu": mae,
        "WorstGroupRMSE": worst,
        "WorstGroupRMSE_R0": wg_vals[0],
        "WorstGroupRMSE_R1": wg_vals[1],
        "WorstGroupRMSE_R2": wg_vals[2],
        "WorstGroupRMSE_R3": wg_vals[3],
        "Delta_group": d_group,
        "Delta_c_s": float(d_cs["Delta_c_s"]),
        "n_windows": NUM_WINDOWS,
        "eventtrace_hash": identity.get("trace_hash"),
        "path_status": "REAL_PATH_EXECUTED",
        "device": device,
        "runtime_seconds": float(time.perf_counter() - t0),
        "git_commit": _git_commit(),
        "gate_unused": True,
        "hybrid": True,
        "design_on": True,
    }
    dump_json(accepted, marker)
    return {"status": "CREATED", **accepted}


def _append_ledger(row: dict[str, Any]) -> None:
    path = OUT / "JO_TRAIN_LEDGER.json"
    payload = {"rows": []}
    if path.is_file():
        payload = json.loads(path.read_text(encoding="utf-8"))
    rows = list(payload.get("rows") or [])
    key = (row.get("dataset"), row.get("method"), row.get("seed"))
    rows = [r for r in rows if (r.get("dataset"), r.get("method"), r.get("seed")) != key]
    rows.append(row)
    dump_json({"rows": rows, "updated_utc": _now()}, path)


def stage_train(*, max_runs: int | None, smoke: bool, seeds: list[int] | None) -> list[dict[str, Any]]:
    load_spec()
    go = load_go()
    seed_list = [CANARY_SEED] if smoke else list(seeds or FORMAL_SEEDS)
    methods = mandatory_methods(go)
    schedule = []
    for seed in seed_list:
        for method in methods:
            schedule.append({"seed": int(seed), "method": method})
    if smoke:
        schedule = [
            r
            for r in schedule
            if r["method"] == "fedavg_window" and r["seed"] == CANARY_SEED
        ]
    if max_runs is not None:
        schedule = schedule[: int(max_runs)]
    device = _device()
    _log(f"TRAIN start n={len(schedule)} device={device} smoke={smoke} methods={methods}")
    atomic, occ = load_tables()
    ds = load_cityscanner_dataset()
    decision = json.loads((OUT / "JO_PHI_DECISION.json").read_text(encoding="utf-8"))
    mu = np.asarray([float(decision["mu"][r]) for r in REGION_ORDER], dtype=np.float64)
    g2i = {str(g): i for g, i in ds._target_group_str_to_int.items()}
    mu_aligned = np.zeros(4, dtype=np.float64)
    for r, val in zip(REGION_ORDER, mu):
        mu_aligned[int(g2i[r])] = float(val)
    mu = mu_aligned / float(mu_aligned.sum())
    spatial_to_client = {
        str(s): str(s) for s in occ["spatial_id"].astype(str).unique()
    }
    atomic_for_pi = occ.copy()
    atomic_for_pi["target_group"] = atomic_for_pi["target_group"].astype(str)
    atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"]
    atomic_for_pi["support_flag"] = True
    missing_h = sorted(set(REGION_ORDER) - set(atomic_for_pi["target_group"].unique()))
    if missing_h:
        raise RuntimeError(f"atomic missing region labels: {missing_h}")
    if set(g2i) != set(REGION_ORDER):
        raise RuntimeError(f"dataset h encoding {g2i} != {REGION_ORDER}")
    pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
    pi_target = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples()
    }
    pi_opp = build_occupancy_pi_opp(occ)
    dump_json(
        {
            "n_pi_target_keys": int(len(pi_target)),
            "n_pi_opp_keys": int(len(pi_opp)),
            "mu": mu.tolist(),
            "h_encoding": ds._target_group_str_to_int,
            "methods": methods,
            "gate_unused": True,
            "device": device,
        },
        OUT / "JO_TRAIN_SETUP.json",
    )
    results = []
    for i, job in enumerate(schedule, 1):
        method = str(job["method"])
        seed = int(job["seed"])
        _log(f"[{i}/{len(schedule)}] TRAIN cityscanner_nyc_p2_measured_o {method} seed{seed}")
        row = train_one(
            ds=ds,
            atomic=atomic,
            method=method,
            seed=seed,
            pi_target=pi_target,
            pi_opp=pi_opp,
            mu=mu,
            device=device,
        )
        _append_ledger(row)
        results.append(row)
        _log(
            f"  status={row.get('status')} RMSE_mu={row.get('RMSE_mu')} "
            f"WG={row.get('WorstGroupRMSE')} sec={row.get('runtime_seconds')}"
        )
        if smoke and row.get("path_status") != "REAL_PATH_EXECUTED" and row.get("status") != "REUSED":
            raise RuntimeError(f"smoke did not execute real path: {row}")
    if not smoke:
        ingest_path = OUT / "INGEST_REPORT.json"
        ingest = json.loads(ingest_path.read_text(encoding="utf-8"))
        ingest["train_run"] = True
        dump_json(ingest, ingest_path)
    return results


def _mean_std(vals: list[float], n_expected: int) -> tuple[str, str]:
    arr = np.asarray(vals, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    if arr.size != n_expected:
        return "TBD", "TBD"
    return f"{float(arr.mean()):.4f}", f"{float(arr.std(ddof=1)):.4f}"


def _kill_on_metric(paired: list[dict[str, Any]], metric: str) -> bool:
    need = {"fedau_window": None, "obsuse_window": None}
    for row in paired:
        comp = str(row.get("comparator"))
        if comp in need:
            need[comp] = row.get(f"{metric}_paired_rel_mean")
    if any(v is None for v in need.values()):
        return False
    return bool(float(need["fedau_window"]) <= KILL_BAR and float(need["obsuse_window"]) <= KILL_BAR)


def stage_tables() -> dict[str, Any]:
    go = load_go()
    ledger = OUT / "JO_TRAIN_LEDGER.json"
    if not ledger.is_file():
        raise FileNotFoundError(ledger)
    rows = list(json.loads(ledger.read_text(encoding="utf-8")).get("rows") or [])
    methods = mandatory_methods(go)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    seed_rows = []
    for r in rows:
        seed_rows.append(
            {
                "dataset": r.get("dataset"),
                "method": r.get("method"),
                "seed": r.get("seed"),
                "RMSE_mu": r.get("RMSE_mu"),
                "WorstGroupRMSE": r.get("WorstGroupRMSE"),
                "Delta_group": r.get("Delta_group"),
                "Delta_c_s": r.get("Delta_c_s"),
                "path_status": r.get("path_status"),
                "eventtrace_hash": r.get("eventtrace_hash"),
            }
        )
    pd.DataFrame(seed_rows).to_csv(OUT / "tables" / "JO_E3.csv", index=False)
    n_seeds = len({int(r["seed"]) for r in rows if r.get("seed") is not None})
    summary = []
    for method in methods:
        sub = [r for r in rows if r.get("method") == method]
        rec: dict[str, Any] = {
            "dataset": "cityscanner_nyc_p2_measured_o",
            "method": method,
            "n": len(sub),
        }
        for src, dst in {
            "RMSE_mu": "rmse_mu",
            "WorstGroupRMSE": "worstgroup",
            "Delta_group": "delta_group",
            "Delta_c_s": "delta_cs",
        }.items():
            vals = [float(r[src]) for r in sub if r.get(src) is not None]
            mean_s, std_s = _mean_std(vals, n_seeds if n_seeds else 10)
            rec[f"{dst}_mean"] = mean_s
            rec[f"{dst}_std"] = std_s
        summary.append(rec)
    pd.DataFrame(summary).to_csv(OUT / "tables" / "JO_E3_SUMMARY.csv", index=False)
    scd = str(go["scd_method"])
    paired_rows = []
    scd_by = {int(r["seed"]): r for r in rows if r.get("method") == scd}
    for comp in ("fedau_window", "obsuse_window", "fedavg_window"):
        other = {int(r["seed"]): r for r in rows if r.get("method") == comp}
        common = sorted(set(scd_by) & set(other))
        rec = {"scd_method": scd, "comparator": comp, "n_paired": len(common)}
        if len(common) >= 2:
            for metric in ("RMSE_mu", "WorstGroupRMSE", "Delta_group", "Delta_c_s"):
                a = np.asarray([float(scd_by[s][metric]) for s in common], dtype=np.float64)
                b = np.asarray([float(other[s][metric]) for s in common], dtype=np.float64)
                rel = (a - b) / np.where(np.abs(b) > 0, b, np.nan)
                rec[f"{metric}_paired_mean_diff"] = float((a - b).mean())
                rec[f"{metric}_paired_rel_mean"] = float(np.nanmean(rel))
        paired_rows.append(rec)
    pd.DataFrame(paired_rows).to_csv(OUT / "tables" / "JO_E3_PAIRED.csv", index=False)
    expected = 10 * len(methods)
    complete = len(rows) >= expected and all(
        r.get("path_status") == "REAL_PATH_EXECUTED" or r.get("status") == "REUSED"
        for r in rows
    )
    c1_kill = False
    if complete and len(scd_by) == 10:
        c1_kill = _kill_on_metric(paired_rows, "WorstGroupRMSE") or _kill_on_metric(
            paired_rows, "RMSE_mu"
        )
    audit = {
        "experiment_id": "JOINT-MEASURED-O-CS-NYC-P2",
        "status": "PASS" if complete else "INCOMPLETE",
        "c1_kill": bool(c1_kill),
        "scd_method": scd,
        "n_ledger_rows": len(rows),
        "n_expected": expected,
        "kill_bar": KILL_BAR,
        "hybrid": True,
        "measured_o": True,
        "p_obs_bernoulli": False,
        "not_mixed_into_table_ii": True,
        "paired": paired_rows,
        "updated_utc": _now(),
    }
    dump_json(audit, OUT / "JO_KILL_AUDIT.json")
    report = OUT / "JO_KILL_REPORT.md"
    lines = [
        "# Measured-O Pilot2 ranking report",
        "",
        f"AUDIT.status={audit['status']}",
        f"c1_kill={audit['c1_kill']}",
        f"scd_method={scd} (Design ON iff phi=0)",
        f"n_rows={len(rows)} expected={expected}",
        "",
        "Kill bar frozen before RMSE: SCD paired mean relative vs both FedAU and ObsUse ≤ −0.5% on WorstGroupRMSE or RMSE_μ.",
        "Measured-O hybrid: union GPS R, finite PM O, controlled U. Not mixed into Table II.",
        "",
    ]
    if not c1_kill:
        lines.append("Kill bar missed. Legal negative. No main-claim manuscript edit.")
    else:
        lines.append("Kill bar met. Independent appendix table only; do not mix into Table II.")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"summary": summary, "paired": paired_rows, "audit": audit}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--stage",
        choices=("phi", "generate", "smoke", "train", "tables", "all"),
        default="generate",
    )
    p.add_argument("--force", action="store_true")
    p.add_argument("--max-runs", type=int, default=None)
    p.add_argument("--seeds", type=str, default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    seeds = [int(x) for x in args.seeds.split(",") if x.strip()] or list(FORMAL_SEEDS)
    if args.stage == "phi":
        go = load_go()
        _log(f"PHI frozen design_on={go['design_on']} phi={go['phi_train_unit']}")
        return 0
    if args.stage in {"generate", "all"}:
        stage_generate(seeds=seeds, force=bool(args.force))
    if args.stage == "smoke":
        stage_train(max_runs=args.max_runs, smoke=True, seeds=seeds)
        return 0
    if args.stage in {"train", "all"}:
        stage_train(max_runs=args.max_runs, smoke=False, seeds=seeds)
        stage_tables()
    if args.stage == "tables":
        stage_tables()
    _log(f"STAGE {args.stage} complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

