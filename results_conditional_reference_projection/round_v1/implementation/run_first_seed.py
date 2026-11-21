"""S1 checks, then seed 33001 five-arm training.

Does not train 33002 or 33003. Does not edit src or the paper.
"""

from __future__ import annotations

import csv
import ctypes
import gc
import json
import os
import sys
import time
import traceback
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ["CUDA_VISIBLE_DEVICES"] = ""

ROOT = Path(__file__).resolve().parents[3]
ROUND = ROOT / "results_conditional_reference_projection" / "round_v1"
S1 = ROUND / "s1"
FIRST = ROUND / "first_seed"
IMPL = ROUND / "implementation"
TRACE_ROOT = ROOT / "artifacts" / "e3_joint_ou_cs_p2_eventtraces_v1"
OCC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "occupancy_units.parquet"
CACHE = ROOT / "results_cityscanner_lowcost_screen" / "round_v1" / "shared" / "predictions" / "measured-O"
MU = [
    0.6496975806451613,
    0.1350806451612903,
    0.07258064516129033,
    0.14264112903225806,
]
REGION = ("region0", "region1", "region2", "region3")
ARMS = [
    ("FedAvg-Window", "fedavg_window", "external"),
    ("TwoStage-Hajek", "twostage_hajek", "external"),
    ("U_matched_uniform", "raven_mcs", "uniform"),
    ("P_reference_projection", "raven_mcs", "projection"),
    ("F_full_raven_design", "raven_mcs", "full_p2"),
]
S1_CPU_LIMIT = 120.0
S1_WALL_LIMIT = 300.0
SEED_CPU_LIMIT = 400.0
SEED_WALL_LIMIT = 600.0
# Measured elapsed time of the two failed probes. Their window CPU was not instrumented.
PRIOR_FAILED_WALL = 14.414 + 6.164
PRIOR_FAILED_IMPORT_CPU = 2.922 + 2.078
# Measured from the attempt that finished four arms and stopped inside F.
PRIOR_SEED_CPU = 123.2
PRIOR_SEED_WALL = 141.517
P2_CALLS = {"n": 0}
F_CLIP = {"count": 0, "worst": 0.0}
SOLVER_NEGATIVE_LIMIT = 1e-6


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_bytes() -> int:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(status.ullAvailPhys)


def lower_priority() -> None:
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)


class Budget:
    def __init__(self) -> None:
        self.cpu0 = time.process_time()
        self.wall0 = time.perf_counter()
        self.segments: list[dict] = []
        self.import_cpu = None
        self.import_wall = None

    def mark(self, name: str, cpu: float, wall: float) -> None:
        self.segments.append({"name": name, "cpu": cpu, "wall": wall})

    @property
    def cpu(self) -> float:
        return time.process_time() - self.cpu0

    @property
    def wall(self) -> float:
        return time.perf_counter() - self.wall0


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def score_prediction(groups, y_true, y_pred, mu) -> dict:
    import numpy as np

    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    groups = np.asarray(groups, dtype=int)
    rows = []
    weighted = 0.0
    worst = None
    missing = []
    for group, mass in enumerate(mu):
        mask = groups == group
        count = int(mask.sum())
        if mass > 0 and count == 0:
            missing.append(group)
            rows.append({"group": group, "n": 0, "mu": float(mass), "mse": None})
            continue
        if count == 0:
            rows.append({"group": group, "n": 0, "mu": float(mass), "mse": None})
            continue
        mse = float(np.mean((y_pred[mask] - y_true[mask]) ** 2))
        weighted += float(mass) * mse
        rmse_g = float(np.sqrt(mse))
        worst = rmse_g if worst is None else max(worst, rmse_g)
        rows.append({"group": group, "n": count, "mu": float(mass), "mse": mse})
    if missing:
        return {"status": "FAIL_VALIDATION_TARGET_COVERAGE", "missing": missing, "rows": rows}
    covered = float(sum(float(mu[g]) for g in range(len(mu)) if rows[g]["n"]))
    rmse = float(np.sqrt(weighted))
    legacy = float(np.sqrt(weighted / covered)) if covered > 0 else None
    return {
        "status": "OK",
        "rows": rows,
        "rmse_mu": rmse,
        "worst": worst,
        "covered_mass": covered,
        "formula_gap": None if legacy is None else abs(rmse - legacy),
    }


def main() -> int:
    lower_priority()
    budget = Budget()
    before = free_bytes()
    print(f"FREE_BEFORE_IMPORT {before}", flush=True)
    if before < 4 * 1024**3:
        write_json(
            S1 / "S1_READINESS.json",
            {
                "stage": "PAUSED_RESOURCE_BEFORE_TRAINING",
                "ready_for_first_seed": False,
                "training_started": False,
                "free_bytes": before,
                "resource": "PAUSED_BELOW_4GIB",
            },
        )
        print("PAUSED_RESOURCE_BEFORE_TRAINING", flush=True)
        return 3

    import_cpu = time.process_time()
    import_wall = time.perf_counter()
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(IMPL))
    import numpy as np
    import pandas as pd
    import torch

    torch.set_num_threads(1)
    import cvxpy as cp
    from raven_mcs.aggregation.method_policy import MethodPolicy
    from raven_mcs.correction.pi_target import build_pi_target
    from raven_mcs.data.base import DatasetMetadata
    from raven_mcs.data.processed_dataset import ProcessedDataset
    from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.e3.target_pair.pair_state_v4 import bind_alpha_by_client, bind_w_by_unit
    from raven_mcs.metrics.distribution import delta_c_s, delta_group
    from raven_mcs.simulation.event_trace import load_event_trace
    from raven_mcs.training.client import _flatten_params
    from raven_mcs.training.window_runner import build_full_runner
    import raven_mcs.training.client as client_mod
    from aggregators import ReferenceProjectionAggregator, UniformAggregator, constraint_residual, max_residual
    from w1_v51a_oracle import project_Cr

    budget.import_cpu = time.process_time() - import_cpu
    budget.import_wall = time.perf_counter() - import_wall
    print(f"IMPORT cpu={budget.import_cpu:.3f} wall={budget.import_wall:.3f}", flush=True)
    install_deploy_guards()

    metadata = DatasetMetadata(
        dataset="cityscanner_nyc_p2_measured_o",
        target_name="pm25",
        target_unit="ug_per_m3",
        spatial_unit="grid_cell_500m",
        time_unit="30min",
        source_name="MIT Senseable City Lab City Scanner hyperlocal environmental CSVs",
        source_url="https://doi.org/10.5281/zenodo.7961851",
        raw_license="cc-by-4.0",
        filtering_rules=("Drop non-finite latitude, longitude, time, or pm25", "Drop pm25 < 0 or pm25 > 1000"),
    )
    metadata.validate()
    dataset = ProcessedDataset(ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o", metadata)
    apply_train_zscore_standardization(dataset)
    encoding = {str(k): int(v) for k, v in dataset._target_group_str_to_int.items()}
    if encoding != {name: index for index, name in enumerate(REGION)}:
        raise RuntimeError(f"group encoding mismatch: {encoding}")
    mu = np.asarray(MU, dtype=np.float64)
    mu = mu / float(mu.sum())
    if float(np.max(np.abs(mu - np.asarray(MU)))) > 1e-12:
        raise RuntimeError("frozen mu changed after normalization")

    units = dataset.get_atomic_units(split="validation")
    groups = [int(unit.target_group) for unit in units]
    coverage_rows = []
    missing = []
    for group, mass in enumerate(mu):
        count = sum(item == group for item in groups)
        if mass > 0 and count == 0:
            missing.append(group)
        coverage_rows.append({"source": "dataset_validation", "group": group, "n": count, "mu": float(mass)})
    if missing:
        raise RuntimeError(f"FAIL_VALIDATION_TARGET_COVERAGE {missing}")

    occ = pd.read_parquet(OCC_PATH)
    spatial_to_client = {str(item): str(item) for item in occ["spatial_id"].astype(str).unique()}
    atomic_for_pi = occ.copy()
    atomic_for_pi["target_group"] = atomic_for_pi["target_group"].astype(str)
    atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"]
    atomic_for_pi["support_flag"] = True
    pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
    pi_target = {
        (str(row.client_id), str(row.opportunity_stratum)): float(row.pi_k_s_tar)
        for row in pi_frame.itertuples()
    }
    train_occ = occ.loc[occ["split"].astype(str) == "train"].copy()
    train_occ["client_id"] = train_occ["spatial_id"].astype(str)
    train_occ["opportunity_stratum"] = train_occ["opportunity_stratum"].astype(str)
    counts = train_occ.groupby(["client_id", "opportunity_stratum"]).size()
    total = float(counts.sum())
    pi_opp = {(str(key[0]), str(key[1])): float(value) / total for key, value in counts.items() if float(value) > 0}

    cache_rows = []
    cache_scores = {}
    val_ids = {str(unit.unit_id): unit for unit in units}
    for method in ("Delivered-SpatialMean", "Delivered-CellBlockMean"):
        frame = pd.read_parquet(CACHE / f"{method}_seed33001.parquet")
        part = frame.loc[frame["split"].astype(str) == "validation"].copy()
        if part.empty:
            cache_rows.append({"method": method, "seed": 33001, "status": "WRONG_SPLIT", "reason": "no validation rows"})
            continue
        merged = []
        gaps = []
        for row in part.itertuples(index=False):
            unit = val_ids.get(str(row.unit_id))
            if unit is None:
                continue
            gaps.append(abs(float(row.y_true_z) - float(unit.target_value)))
            merged.append((int(unit.target_group), float(unit.target_value), float(row.y_pred_z)))
        if len(merged) != len(val_ids):
            cache_rows.append(
                {
                    "method": method,
                    "seed": 33001,
                    "status": "MISSING",
                    "reason": f"aligned {len(merged)} of {len(val_ids)} validation units",
                }
            )
            continue
        if max(gaps) > 1e-6:
            cache_rows.append({"method": method, "seed": 33001, "status": "DIFFERENT_PROTOCOL", "reason": f"target gap {max(gaps)}"})
            continue
        scored = score_prediction([item[0] for item in merged], [item[1] for item in merged], [item[2] for item in merged], mu)
        if scored["status"] != "OK" or scored["formula_gap"] > 1e-10:
            cache_rows.append({"method": method, "seed": 33001, "status": "NEEDS_RESCORING", "reason": scored["status"]})
            continue
        cache_scores[method] = scored
        cache_rows.append(
            {
                "method": method,
                "seed": 33001,
                "status": "ACCEPTED",
                "reason": f"validation n={len(merged)} gap={scored['formula_gap']} rmse={scored['rmse_mu']}",
            }
        )
    for method, folder in (("FedAU-Window", "fedau_window"), ("ObsUse-Window", "obsuse_window")):
        path = ROOT / "results_joint_ou" / "round_v1" / "runs" / "cityscanner_nyc_p2_measured_o" / folder / "seed33001" / "JO_ACCEPTED.json"
        cache_rows.append(
            {
                "method": method,
                "seed": 33001,
                "status": "MISSING",
                "reason": "aggregate JO_ACCEPTED only; no unit-level validation predictions" if path.is_file() else "no aggregate file",
            }
        )
    if any(row["status"] != "ACCEPTED" for row in cache_rows if row["method"].startswith("Delivered")):
        write_cache(cache_rows)
        raise RuntimeError("cheap baseline validation path is not accepted")

    synthetic_u = UniformAggregator()

    class Payload:
        def __init__(self, beta):
            self.client_ids = list(range(len(beta)))
            self.beta_hat = np.asarray(beta, dtype=np.float64)

    uniform_alpha = synthetic_u.compute_server_weights(Payload(np.array([0.2, 0.8])))
    if float(np.max(np.abs(uniform_alpha - 0.5))) > 1e-15:
        raise RuntimeError("uniform arm is not 1/K")
    projected, kind, _ = project_Cr(np.array([0.2, 0.8]), 0.5, 2.0)
    if float(np.max(np.abs(projected - 0.5))) > 1e-8:
        raise RuntimeError(f"K=2 projection did not degenerate to uniform: {kind}")

    probe = prepare_runner(dataset, "raven_mcs", "projection", 33001, mu, pi_target, pi_opp, np)
    probe_result = run_probe(probe, np, cp, project_Cr, _flatten_params, client_mod, budget)
    del probe
    gc.collect()
    if budget.cpu + PRIOR_FAILED_IMPORT_CPU > S1_CPU_LIMIT or budget.wall + PRIOR_FAILED_WALL > S1_WALL_LIMIT:
        raise RuntimeError(f"S1 budget exceeded cpu={budget.cpu} wall={budget.wall}")
    write_s1(coverage_rows, cache_rows, cache_scores, probe_result, budget, before)
    print("S1_PASS", flush=True)

    freeze_path = ROUND / "EXPERIMENT_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze["training_started"] = True
    freeze["stage"] = "FIRST_SEED_RUNNING"
    freeze["training_authorized_by"] = "user message: 现在再试一下训练，内存应该够了; S1 passed before the first arm"
    write_json(freeze_path, freeze)

    results = []
    seed_cpu0 = time.process_time()
    seed_wall0 = time.perf_counter()
    min_free = free_bytes()
    peak_rss = 0
    try:
        import psutil  # noqa: F401
    except Exception:
        psutil = None
    for name, method, kind in ARMS:
        remaining_cpu = SEED_CPU_LIMIT - PRIOR_SEED_CPU - (time.process_time() - seed_cpu0)
        remaining_wall = SEED_WALL_LIMIT - PRIOR_SEED_WALL - (time.perf_counter() - seed_wall0)
        saved = load_completed_arm(name)
        if saved is not None:
            results.append(saved)
            print(f"ARM_REUSE {name} rmse={saved['RMSE_mu_final']} steps={saved['server_steps']}", flush=True)
            continue
        print(f"ARM_START {name} remaining_cpu={remaining_cpu:.1f} remaining_wall={remaining_wall:.1f}", flush=True)
        if remaining_cpu <= 0 or remaining_wall <= 0:
            raise RuntimeError(f"first-seed budget exhausted before {name}")
        now_free = free_bytes()
        min_free = min(min_free, now_free)
        if now_free < 2 * 1024**3:
            time.sleep(30)
            now_free = free_bytes()
            min_free = min(min_free, now_free)
            if now_free < 2 * 1024**3:
                raise RuntimeError(f"PAUSED_RESOURCE free={now_free} before {name}")
        row = run_arm(
            dataset, occ, name, method, kind, mu, pi_target, pi_opp, np, torch, _predict,
            delta_group, delta_c_s, bind_alpha_by_client, bind_w_by_unit,
        )
        results.append(row)
        min_free = min(min_free, free_bytes())
        print(f"ARM_DONE {name} rmse={row['RMSE_mu_final']} steps={row['server_steps']}", flush=True)
        gc.collect()
    write_outputs(results, cache_scores, budget, seed_cpu0, seed_wall0, min_free, probe_result)
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze["stage"] = "S1_PASS_FIRST_SEED_COMPLETE"
    freeze["three_seed_screen"] = "THREE_SEED_SCREEN_NOT_EVALUATED"
    freeze["conditional_branch_B"] = "NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT"
    write_json(freeze_path, freeze)
    print("FIRST_SEED_COMPLETE", flush=True)
    return 0


def prepare_runner(dataset, method, kind, seed, mu, pi_target, pi_opp, np):
    from raven_mcs.simulation.event_trace import load_event_trace
    from raven_mcs.training.window_runner import build_full_runner
    from aggregators import ReferenceProjectionAggregator, UniformAggregator
    from dataclasses import replace

    trace_dir = TRACE_ROOT / "cityscanner_nyc_p2_measured_o" / f"seed{seed}" / "training_eventtrace"
    trace, identity = load_event_trace(trace_dir)
    design = "on" if method == "raven_mcs" else None
    runner = build_full_runner(
        trace,
        dataset,
        method=method,
        design=design,
        n_groups=4,
        model_seed=int(seed),
        local_steps=2,
        learning_rate=0.01,
        target_mu=mu,
        pi_target=pi_target,
        s_max=5,
        device="cpu",
        use_coarse_time_groups=False,
        pi_opp_joint=pi_opp,
        design_source="conditional_reference_projection_v1",
    )
    if int(runner.local_steps) != 2 or abs(float(runner.learning_rate) - 0.01) > 0 or abs(float(runner.eta) - 0.01) > 0:
        raise RuntimeError("runner local steps or learning rates are not frozen")
    detach_server_theta(runner)
    if kind in {"projection", "uniform"}:
        runner.policy = replace(
            runner.policy,
            uses_debt=False,
            uses_instant_calibration=False,
            uses_reference_penalty=False,
            uses_variance_penalty=False,
            uses_staleness_penalty=False,
        )
        runner.aggregator = ReferenceProjectionAggregator() if kind == "projection" else UniformAggregator()
    install_version_pruning(runner, trace, np)
    runner.trace_identity = identity
    return runner


def detach_server_theta(runner) -> None:
    """Copy the server vector out of the live parameter storage.

    The runner takes theta from state_dict(), which aliases the model.
    Local SGD then overwrites that vector before the server step reads it,
    so the first update is not theta - eta * sum(alpha * u).
    """
    runner.theta = {key: value.detach().cpu().clone() for key, value in runner.theta.items()}


def install_deploy_guards() -> None:
    """Keep solve_p2 off the shared post-update audit.

    F still calls it inside its own aggregator. The counterfactual audit is
    not part of the deployed weights, and running it would make P solve P2
    and then discard the result.
    """
    import numpy as np
    import raven_mcs.aggregation.methods as methods
    import raven_mcs.sag.counterfactual_audit as audit_mod
    import raven_mcs.training.window_runner as window_runner

    class SkippedAudit:
        def as_dict(self) -> dict:
            return {
                "p2_audit": "SKIPPED_NOT_ON_DEPLOY_PATH",
                "active_set_mismatch": 1,
                "both_empty": 0,
                "raw_state": {},
            }

    def skipped_audit(**kwargs):
        return SkippedAudit()

    window_runner.audit_design_vs_nodesign = skipped_audit
    real_methods = methods.solve_p2
    real_audit = audit_mod.solve_p2

    def counted_methods(*args, **kwargs):
        P2_CALLS["n"] += 1
        return real_methods(*args, **kwargs)

    def counted_audit(*args, **kwargs):
        P2_CALLS["n"] += 1
        return real_audit(*args, **kwargs)

    methods.solve_p2 = counted_methods
    audit_mod.solve_p2 = counted_audit

    def normalize_solver_noise(weights):
        w = np.asarray(weights, dtype=np.float64).copy()
        worst = float(np.min(w)) if w.size else 0.0
        if worst < -SOLVER_NEGATIVE_LIMIT:
            raise ValueError(f"REAL_CONSTRAINT_VIOLATION min_alpha={worst}")
        if worst < 0.0:
            F_CLIP["count"] += 1
            F_CLIP["worst"] = worst if F_CLIP["count"] == 1 else min(F_CLIP["worst"], worst)
            w = np.clip(w, 0.0, None)
        total = float(w.sum())
        if total <= 0.0:
            raise ValueError("server weights sum to zero")
        return w / total

    methods._normalize = normalize_solver_noise


def load_completed_arm(name: str) -> dict | None:
    path = FIRST / "seed33001" / name / "arm_result.json"
    if not path.is_file():
        return None
    row = json.loads(path.read_text(encoding="utf-8"))
    if row.get("completion_status") != "COMPLETE" or int(row.get("server_steps", 0)) != 100:
        return None
    if row.get("method_identity") != name or int(row.get("seed", 0)) != 33001:
        return None
    row.setdefault("f_solver_negative_clips", 0)
    row.setdefault("f_solver_worst_negative", 0.0)
    return row


def install_version_pruning(runner, trace, np) -> None:
    nwin = int(trace.metadata.num_windows)
    versions = {window: set() for window in range(nwin)}
    for window_id, version in zip(trace.events["window_id"].astype(int).tolist(), trace.events["downloaded_version"].astype(int).tolist()):
        if 0 <= int(window_id) < nwin:
            versions[int(window_id)].add(int(version))
    future: dict[int, set[int]] = {}
    accumulated: set[int] = set()
    for window in range(nwin - 1, -1, -1):
        future[window] = set(accumulated)
        accumulated |= versions[window]
    original = runner._process_window

    def wrapped(window_id, events, original=original):
        result = original(window_id, events)
        needed = set(future.get(int(window_id), set()))
        needed.add(int(runner.clock.model_version))
        for version in list(runner.model_versions):
            if int(version) not in needed:
                del runner.model_versions[version]
        return result

    runner._process_window = wrapped


def run_probe(runner, np, cp, project_Cr, flatten, client_mod, budget: Budget) -> dict:
    p2_before = P2_CALLS["n"]
    calls = {"hajek": 0}
    real_loss = client_mod.local_hajek_loss

    def counted_loss(*args, **kwargs):
        calls["hajek"] += 1
        return real_loss(*args, **kwargs)

    client_mod.local_hajek_loss = counted_loss
    captured = {"updates": [], "steps": []}
    real_train = runner._trainer.train_step

    def train_step(*args, **kwargs):
        update, loss = real_train(*args, **kwargs)
        steps = int(args[3] if len(args) > 3 else kwargs["local_steps"])
        captured["updates"].append(np.array(update, dtype=np.float64, copy=True))
        captured["steps"].append(steps)
        return update, loss

    runner._trainer.train_step = train_step
    original = runner._process_window
    found = {"projection": None, "formula": None, "empty": None, "design": []}

    def wrapped(window_id, events):
        before_count = len(runner.diagnostics)
        before_theta = flatten(runner.theta).copy()
        captured["updates"].clear()
        captured["steps"].clear()
        before_records = len(getattr(runner.aggregator, "records", []))
        result = original(window_id, events)
        logs = list(getattr(runner, "design_window_logs", []))
        if logs:
            last = logs[-1]
            found["design"].append(
                {
                    "window": int(window_id),
                    "configured": int(last.get("configured_design", -1)),
                    "actual": int(last.get("actual_design", last.get("Design_t", -1))),
                }
            )
        if not bool(getattr(result, "active", False)):
            after_theta = flatten(runner.theta)
            found["empty"] = {
                "window": int(window_id),
                "theta_unchanged": bool(np.max(np.abs(after_theta - before_theta)) == 0.0),
            }
            return result
        new_diag = runner.diagnostics[before_count:]
        if len(new_diag) != len(captured["updates"]):
            raise RuntimeError("local update capture does not match diagnostics")
        if any(step != 2 for step in captured["steps"]):
            raise RuntimeError(f"local steps were not 2: {captured['steps'][:5]}")
        alpha = np.asarray(result.alpha, dtype=np.float64)
        by_client = {}
        for diag, update in zip(new_diag, captured["updates"]):
            by_client[str(diag["client_id"])] = update
        expected = before_theta.copy()
        applied = np.zeros_like(before_theta)
        client_ids = [str(item) for item in result.active_clients]
        if len(client_ids) != len(alpha):
            raise RuntimeError("alpha is not aligned with active clients")
        used = 0
        for weight, cid in zip(alpha, client_ids):
            update = by_client.get(cid)
            if update is None or update.size == 0:
                continue
            if update.size != expected.size:
                raise RuntimeError("update length does not match theta")
            applied = applied + float(weight) * update
            used += 1
        after = flatten(runner.theta)
        delta = after - before_theta
        eta = float(runner.eta)
        gap = float(np.max(np.abs(delta + eta * applied)))
        if found["formula"] is None:
            numerator = float(np.dot(delta, applied))
            denom = float(np.dot(applied, applied))
            scale = numerator / denom if denom > 0 else None
            found["formula"] = {
                "window": int(window_id),
                "max_abs": gap,
                "local_steps": 2,
                "used_updates": used,
                "active": len(client_ids),
                "captured": len(captured["updates"]),
                "delta_max": float(np.max(np.abs(delta))),
                "applied_max": float(np.max(np.abs(applied))),
                "best_scale": scale,
            }
        records = getattr(runner.aggregator, "records", [])
        if len(records) > before_records:
            record = records[-1]
            if int(record["K"]) > 3 and found["projection"] is None:
                beta = np.asarray(record["beta"], dtype=np.float64)
                alpha_hat = np.asarray(record["alpha"], dtype=np.float64)
                variable = cp.Variable(int(record["K"]))
                problem = cp.Problem(
                    cp.Minimize(0.5 * cp.sum_squares(variable - beta)),
                    [
                        cp.sum(variable) == 1,
                        variable >= 0,
                        variable <= float(record["a_bar"]),
                        cp.sum_squares(variable) <= 1.0 / float(record["e_bar"]),
                    ],
                )
                problem.solve(solver=cp.CLARABEL, verbose=False)
                if variable.value is None:
                    raise RuntimeError(f"independent projection failed: {problem.status}")
                other = np.asarray(variable.value, dtype=np.float64).reshape(-1)
                ours = 0.5 * float(np.sum((alpha_hat - beta) ** 2))
                theirs = 0.5 * float(np.sum((other - beta) ** 2))
                found["projection"] = {
                    "window": int(window_id),
                    "K": int(record["K"]),
                    "kind": record["kind"],
                    "objective_gap": abs(ours - theirs),
                    "vector_gap": float(np.max(np.abs(alpha_hat - other))),
                    "feasibility": record["residual"],
                    "solver_status": str(problem.status),
                }
        if found["projection"] is not None and found["formula"] is not None:
            raise StopIteration
        return result

    trace = runner.trace
    events = trace.events
    try:
        for window_id in range(int(trace.metadata.num_windows)):
            try:
                wrapped(window_id, events)
            except StopIteration:
                break
            if budget.wall > S1_WALL_LIMIT or window_id >= 19:
                break
    finally:
        client_mod.local_hajek_loss = real_loss
    empty_events = events.iloc[0:0]
    before_empty = flatten(runner.theta).copy()
    empty_result = original(0, empty_events)
    after_empty = flatten(runner.theta)
    empty_gap = float(np.max(np.abs(after_empty - before_empty)))
    found["empty"] = {
        "window": "synthetic_empty_frame_after_probe",
        "active": bool(getattr(empty_result, "active", True)),
        "theta_max_abs": empty_gap,
    }
    if found["empty"]["active"] or empty_gap != 0.0:
        raise RuntimeError(f"empty-window carry-forward failed: {found['empty']}")
    found["p2_calls"] = P2_CALLS["n"] - p2_before
    if found["p2_calls"] != 0:
        raise RuntimeError(f"projection probe called solve_p2 {found['p2_calls']} times")
    if not found["projection"] or found["projection"]["objective_gap"] > 1e-6 or found["projection"]["feasibility"] > 1e-8:
        raise RuntimeError(f"projection check failed: {found['projection']}")
    if not found["formula"] or found["formula"]["max_abs"] > 1e-6:
        raise RuntimeError(f"server update check failed: {found['formula']}")
    if calls["hajek"] <= 0:
        raise RuntimeError("Hajek local loss was not called")
    if any(item["configured"] != 1 or item["actual"] != 1 for item in found["design"]):
        raise RuntimeError(f"design identity failed: {found['design'][:3]}")
    found["hajek_calls"] = calls["hajek"]
    found["uniform_k2"] = "PASS"
    return found


def run_arm(dataset, occ, name, method, kind, mu, pi_target, pi_opp, np, torch, predict, delta_group, delta_c_s, bind_alpha, bind_w):
    cpu0 = time.process_time()
    wall0 = time.perf_counter()
    init0 = time.perf_counter()
    init_cpu0 = time.process_time()
    runner = prepare_runner(dataset, method, kind, 33001, mu, pi_target, pi_opp, np)
    init_cpu = time.process_time() - init_cpu0
    init_wall = time.perf_counter() - init0
    deploy_cpu0 = time.process_time()
    deploy_wall0 = time.perf_counter()
    if kind == "full_p2":
        F_CLIP["count"] = 0
        F_CLIP["worst"] = 0.0
    p2_before = P2_CALLS["n"]
    metrics = runner.run()
    p2_calls = P2_CALLS["n"] - p2_before
    if kind in {"projection", "uniform", "external"} and p2_calls != 0:
        raise RuntimeError(f"{name} deploy path called solve_p2 {p2_calls} times")
    if kind == "full_p2" and p2_calls <= 0:
        raise RuntimeError(f"{name} did not call solve_p2")
    deploy_cpu = time.process_time() - deploy_cpu0
    deploy_wall = time.perf_counter() - deploy_wall0
    score_cpu0 = time.process_time()
    score_wall0 = time.perf_counter()
    prediction = predict(runner, dataset, split="validation")
    scored = score_prediction(prediction["groups"], prediction["y_true"], prediction["y_pred"], mu)
    if scored["status"] != "OK":
        raise RuntimeError(f"{name} {scored['status']}")
    try:
        group_distance = float(delta_group(runner.omega_bar(), mu))
    except Exception:
        group_distance = float("nan")
    stratum = client_stratum_distance(metrics, runner.diagnostics, occ, pi_target, "raven" if kind != "external" else method, np, delta_c_s, bind_alpha, bind_w)
    score_cpu = time.process_time() - score_cpu0
    score_wall = time.perf_counter() - score_wall0
    out = FIRST / "seed33001" / name
    out.mkdir(parents=True, exist_ok=True)
    torch.save(runner.theta, out / "final.pt")
    active = sum(1 for item in metrics if bool(getattr(item, "active", False)))
    design_bad = []
    if kind != "external":
        for item in runner.design_window_logs:
            if int(item.get("configured_design", -1)) != 1 or int(item.get("actual_design", item.get("Design_t", -1))) != 1:
                design_bad.append(item.get("window_id"))
        if design_bad:
            raise RuntimeError(f"{name} design left the frozen on setting at {design_bad[:5]}")
    residuals = []
    for record in getattr(runner.aggregator, "records", []):
        if "residual" in record:
            residuals.append(float(record["residual"]))
    row = {
        "seed": 33001,
        "method_identity": name,
        "split": "validation",
        "windows": 100,
        "server_steps": active,
        "n0": scored["rows"][0]["n"],
        "n1": scored["rows"][1]["n"],
        "n2": scored["rows"][2]["n"],
        "n3": scored["rows"][3]["n"],
        "mse0": scored["rows"][0]["mse"],
        "mse1": scored["rows"][1]["mse"],
        "mse2": scored["rows"][2]["mse"],
        "mse3": scored["rows"][3]["mse"],
        "RMSE_mu_final": scored["rmse_mu"],
        "WorstGroup_final": scored["worst"],
        "Delta_group": group_distance,
        "Delta_cs": stratum,
        "deploy_CPU_s": deploy_cpu,
        "deploy_wall_s": deploy_wall,
        "init_CPU_s": init_cpu,
        "init_wall_s": init_wall,
        "score_CPU_s": score_cpu,
        "score_wall_s": score_wall,
        "total_CPU_s": time.process_time() - cpu0,
        "total_wall_s": time.perf_counter() - wall0,
        "max_projection_residual": max(residuals) if residuals else "",
        "deploy_p2_solves": p2_calls,
        "f_solver_negative_clips": F_CLIP["count"] if kind == "full_p2" else 0,
        "f_solver_worst_negative": F_CLIP["worst"] if kind == "full_p2" else 0.0,
        "cost_source": "this_process",
        "completion_status": "COMPLETE",
        "resume_state": "FINAL_WEIGHTS_ONLY_NOT_FULL_FEDERATED_RESUME",
    }
    write_json(out / "arm_result.json", row)
    del runner
    return row


def client_stratum_distance(metrics, diagnostics, atomic, pi_target, method, np, delta_c_s, bind_alpha, bind_w):
    unit_s = {str(row.unit_id): str(row.opportunity_stratum) for row in atomic.itertuples(index=False)}
    pi_tar = {f"{key}::{stratum}": float(value) for (key, stratum), value in pi_target.items()}
    contrib: dict[str, float] = {}
    steps = 0.0
    for metric in metrics:
        if not bool(getattr(metric, "active", False)):
            continue
        steps += 1.0
        alpha_map = bind_alpha(metric)
        window_diag = [item for item in diagnostics if int(item.get("window_id", -1)) == int(metric.window_id)]
        for item in window_diag:
            cid = str(item["client_id"])
            if cid not in alpha_map:
                continue
            weight = float(alpha_map[cid])
            for unit_id, local_weight in bind_w(item, method=method).items():
                key = f"{cid}::{unit_s[str(unit_id)]}"
                contrib[key] = contrib.get(key, 0.0) + float(weight * local_weight)
    keys = sorted(set(contrib) | set(pi_tar))
    denom = steps if steps > 0 else 1.0
    estimate = np.asarray([contrib.get(key, 0.0) / denom for key in keys], dtype=np.float64)
    target = np.asarray([pi_tar.get(key, 0.0) for key in keys], dtype=np.float64)
    if float(estimate.sum()) > 0:
        estimate = estimate / float(estimate.sum())
    return float(delta_c_s(estimate, target))


def write_cache(rows) -> None:
    path = S1 / "BASELINE_CACHE_AUDIT.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["method", "seed", "status", "reason"])
        writer.writeheader()
        writer.writerows(rows)


def write_s1(coverage, cache_rows, cache_scores, probe, budget: Budget, free_before: int) -> None:
    S1.mkdir(parents=True, exist_ok=True)
    with (S1 / "VALIDATION_COVERAGE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "group", "n", "mu", "mse", "rmse_mu", "status"])
        writer.writeheader()
        for row in coverage:
            writer.writerow({**row, "mse": "", "rmse_mu": "", "status": "COVERED"})
    write_cache(cache_rows)
    projection = probe["projection"]
    (S1 / "SCORING_ALIGNMENT.md").write_text(
        "\n".join(
            [
                "# SCORING_ALIGNMENT",
                "",
                "真实 validation 单元已按 unit_id 对齐。四个组都有样本，没有缺组再归一化。",
                f"两个廉价基线的 validation 预测与数据集目标的最大差不超过 1e-6。公式差分别是 "
                + ", ".join(f"{name} {score['formula_gap']}" for name, score in cache_scores.items())
                + "。",
                "FedAU 和 ObsUse 仍只有历史汇总值，状态 MISSING，不阻断五臂，也不能写成已经被超过。",
                "旧 JO 汇总没有逐单元预测，本轮终点不用那张表填入。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (S1 / "IMPLEMENTATION_CHECK.md").write_text(
        "\n".join(
            [
                "# IMPLEMENTATION_CHECK",
                "",
                f"首个 K>3 的投影窗口是 {projection['window']}，K={projection['K']}，kind={projection['kind']}。",
                f"约束残差 {projection['feasibility']}，独立目标差 {projection['objective_gap']}，求解状态 {projection['solver_status']}。",
                f"同一次真实更新的公式最大绝对差是 {probe['formula']['max_abs']}，局部步数是 2。",
                "服务器向量在开跑前从模型参数存储中克隆出来。否则 state_dict 别名会让局部 SGD 改掉服务器即将读取的基准，第一条更新就不是 theta - eta * sum(alpha * u)。",
                f"Hájek 局部损失调用次数 {probe['hajek_calls']}。K=2 的合成投影退化为 Uniform。",
                f"空窗口承接：{probe['empty']}。",
                f"投影探针里的 solve_p2 调用次数是 {probe['p2_calls']}。共享的事后反事实审计已从五条部署路径移除；F 仍在自己的聚合器里求解 P2。",
                "P/U 关闭债务、即时校准、参考、方差和陈旧惩罚。src 没有修改。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_json(
        S1 / "S1_READINESS.json",
        {
            "scoring": "PASS",
            "cache": "CHEAP_BASELINES_ACCEPTED_FEDAU_OBSUSE_MISSING",
            "local_loss": "PASS",
            "local_steps": "PASS",
            "design_identity": "PASS",
            "projection_feasibility": "PASS",
            "projection_objective": "PASS",
            "resource": "PASS",
            "ready_for_first_seed": True,
            "free_bytes_before_import": free_before,
            "s1_cpu": budget.cpu,
            "s1_wall": budget.wall,
            "import_cpu": budget.import_cpu,
            "import_wall": budget.import_wall,
            "projection": {key: value for key, value in projection.items()},
        },
    )


def write_outputs(results, cache_scores, budget: Budget, seed_cpu0, seed_wall0, min_free, probe) -> None:
    FIRST.mkdir(parents=True, exist_ok=True)
    stale_failure = ROUND / "FAILURE_REPORT.md"
    if stale_failure.is_file():
        stale_failure.unlink()
    fields = list(results[0].keys())
    with (FIRST / "PER_ARM_RESULTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    by_name = {row["method_identity"]: row for row in results}
    base = by_name["P_reference_projection"]
    comparisons = []
    opponents = [
        ("U_matched_uniform", "mechanism"),
        ("F_full_raven_design", "mechanism"),
        ("TwoStage-Hajek", "practical"),
        ("FedAvg-Window", "practical"),
    ]
    for name, kind in opponents:
        other = by_name[name]
        comparisons.append(compare_row(base, other, kind))
    for name, scored in cache_scores.items():
        comparisons.append(
            {
                "opponent": name,
                "kind": "cheap_baseline",
                "rmse_p": base["RMSE_mu_final"],
                "rmse_b": scored["rmse_mu"],
                "rmse_rel": base["RMSE_mu_final"] / scored["rmse_mu"] - 1.0,
                "worst_p": base["WorstGroup_final"],
                "worst_b": scored["worst"],
                "group_pp": "",
                "deploy_cpu_ratio": "",
                "deploy_wall_ratio": "",
                "screen_status": "NOT_EVALUATED_FIRST_SEED_ONLY",
            }
        )
    with (FIRST / "PAIRED_COMPARISONS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0].keys()))
        writer.writeheader()
        writer.writerows(comparisons)
    lines = [
        "# FIRST_SEED_REPORT",
        "",
        "运行状态：S1_PASS_FIRST_SEED_COMPLETE。三种子筛选：THREE_SEED_SCREEN_NOT_EVALUATED。",
        "分支 B：NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT。一个种子不能确定全局 B*，也不能宣布 GO。",
        "",
        "| 方法 | RMSE_mu | WorstGroup | Delta_group | Delta_cs | 部署 CPU | 部署 wall | 服务器步 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        lines.append(
            f"| {row['method_identity']} | {row['RMSE_mu_final']:.6f} | {row['WorstGroup_final']:.6f} | "
            f"{row['Delta_group']:.6f} | {row['Delta_cs']:.6f} | {row['deploy_CPU_s']:.3f} | "
            f"{row['deploy_wall_s']:.3f} | {row['server_steps']} |"
        )
    lines.extend(["", "配对差是 P 减对手；相对 RMSE 是 P/对手 - 1。结构百分点是 50 乘 L1 差。", ""])
    for row in comparisons:
        lines.append(
            f"- {row['opponent']}: RMSE 相对 {row['rmse_rel']}, group pp {row['group_pp']}, "
            f"部署 CPU 比 {row['deploy_cpu_ratio']}, wall 比 {row['deploy_wall_ratio']}。"
        )
    f_row = by_name["F_full_raven_design"]
    lines.append("")
    lines.append(
        f"F 的求解器负权重清理：{f_row.get('f_solver_negative_clips', 0)} 次，最深 {f_row.get('f_solver_worst_negative', 0)}。"
        "只接受不差于求解器容差 1e-6 的数值负值，然后截断到 0 再归一化。更差的负值会停止，不更换 F。"
    )
    lines.append("FedAU 与 ObsUse 没有合法的逐单元 validation 缓存，不估计它们是否被 P 超过。")
    (FIRST / "FIRST_SEED_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    seed_cpu = time.process_time() - seed_cpu0
    seed_wall = time.perf_counter() - seed_wall0
    (ROUND / "RESOURCE_AND_BUDGET.md").write_text(
        "\n".join(
            [
                "# RESOURCE_AND_BUDGET",
                "",
                "S0 仍是 UNMETERED_PREPARATION。",
                f"导入依赖单列：CPU {budget.import_cpu:.6f} 秒，wall {budget.import_wall:.6f} 秒。它不计入某一臂的部署时间。",
                f"两次公式探针的已测 wall 合计 {PRIOR_FAILED_WALL:.3f} 秒，已测导入 CPU 合计 {PRIOR_FAILED_IMPORT_CPU:.3f} 秒。那两次没有正式臂，窗口训练 CPU 未单列。",
                f"四臂完成后的 F 中断：进入 F 之前已测 CPU {PRIOR_SEED_CPU:.1f} 秒、进程 wall {PRIOR_SEED_WALL:.3f} 秒。F 的失败片段没有单独的 CPU。",
                "成功进程的 S1 数字以 s1/S1_READINESS.json 为准，不把进程结束时的累计时间写成 S1。",
                f"本进程在写报告时的新增 CPU {seed_cpu:.6f} 秒、wall {seed_wall:.6f} 秒，只覆盖这次实际训练的臂。五条臂的部署时间在 first_seed/PER_ARM_RESULTS.csv。",
                f"本进程观察到的最低可用内存 {min_free} bytes。",
                "历史 JO wall 没有拿来当本轮部署 wall。限额是 S1 120/300、第一种子 400/600、S2–S3 合计 1200/1800。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ROUND / "NEXT_STAGE_REQUEST.md").write_text(next_stage_text(results), encoding="utf-8")


def compare_row(base, other, kind) -> dict:
    group_pp = ""
    if base["Delta_group"] != "" and other["Delta_group"] != "":
        group_pp = 50.0 * (float(other["Delta_group"]) - float(base["Delta_group"]))
    return {
        "opponent": other["method_identity"],
        "kind": kind,
        "rmse_p": base["RMSE_mu_final"],
        "rmse_b": other["RMSE_mu_final"],
        "rmse_rel": float(base["RMSE_mu_final"]) / float(other["RMSE_mu_final"]) - 1.0,
        "worst_p": base["WorstGroup_final"],
        "worst_b": other["WorstGroup_final"],
        "group_pp": group_pp,
        "deploy_cpu_ratio": float(base["deploy_CPU_s"]) / float(other["deploy_CPU_s"]),
        "deploy_wall_ratio": float(base["deploy_wall_s"]) / float(other["deploy_wall_s"]),
        "screen_status": "NOT_EVALUATED_FIRST_SEED_ONLY",
    }


def next_stage_text(results) -> str:
    by_name = {row["method_identity"]: row for row in results}
    p_row = by_name["P_reference_projection"]
    f_row = by_name["F_full_raven_design"]
    cpu_ratio = float(p_row["deploy_CPU_s"]) / float(f_row["deploy_CPU_s"])
    wall_ratio = float(p_row["deploy_wall_s"]) / float(f_row["deploy_wall_s"])
    rmse_rel = float(p_row["RMSE_mu_final"]) / float(f_row["RMSE_mu_final"]) - 1.0
    group_pp = 50.0 * (float(p_row["Delta_group"]) - float(f_row["Delta_group"]))
    two = by_name["TwoStage-Hajek"]
    two_rel = float(p_row["RMSE_mu_final"]) / float(two["RMSE_mu_final"]) - 1.0
    return "\n".join(
        [
            "# NEXT_STAGE_REQUEST",
            "",
            f"第一种子里，P 相对 F 的部署 CPU 少 {1.0 - cpu_ratio:.1%}，wall 少 {1.0 - wall_ratio:.1%}，RMSE 相对差 {rmse_rel:.2%}，组分布 L1 差 {group_pp:.2f} 个百分点。端到端节省不大，组结构也没有一起变好。",
            f"相对 TwoStage，P 的 RMSE 相对差是 {two_rel:.2%}。这只是 seed 33001，不能证明三种子不可能通过，也不能当成已经通过。",
            "33002 和 33003 的十条还没有运行。是否继续由用户决定。",
            "分支 B 仍没有部署合同，不能把更快写成条件替代通过。",
            "",
        ]
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        failure = ROUND / "FAILURE_REPORT.md"
        failure.write_text("# FAILURE_REPORT\n\n```\n" + traceback.format_exc() + "\n```\n", encoding="utf-8")
        print(traceback.format_exc(), flush=True)
        raise
