"""P1 one-step common-state diagnostic for seed 33001.

The nine windows are copied from the already frozen list. This process does
not reselect them, does not read final.pt, and does not modify src.
"""

from __future__ import annotations

import copy
import csv
import ctypes
import hashlib
import json
import math
import os
import sys
import threading
import time
import traceback
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

ROOT = Path(__file__).resolve().parents[3]
ROUND = ROOT / "results_conditional_reference_projection" / "round_v1"
OUT = Path(__file__).resolve().parent
PRIOR_FREEZE = ROUND / "p1_controlled_diagnostic_20261020_1002" / "P1_FREEZE.json"
IMPL = ROUND / "implementation"
TRACE = (
    ROOT
    / "artifacts"
    / "e3_joint_ou_cs_p2_eventtraces_v1"
    / "cityscanner_nyc_p2_measured_o"
    / "seed33001"
    / "training_eventtrace"
)
OCC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "occupancy_units.parquet"
MU = [
    0.6496975806451613,
    0.1350806451612903,
    0.07258064516129033,
    0.14264112903225806,
]
EXPECTED_N = {"0": 1242, "1": 331, "2": 108, "3": 408}
CPU_LIMIT = 180.0
WALL_LIMIT = 360.0
GIB4 = 4 * 1024**3
GIB2 = 2 * 1024**3
FORMULA_LIMIT = 1e-6
SCORE_REPEAT_LIMIT = 1e-6
METHODS = (
    "P_reference_projection",
    "U_matched_uniform",
    "F_full_raven_design",
    "TwoStage-Hajek",
)


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
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def client_sha(ids: list[str]) -> str:
    payload = "\n".join(sorted(str(item) for item in ids)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def theta_clone(theta: dict):
    import torch

    return {key: value.detach().cpu().clone() for key, value in theta.items()}


def theta_gap(left: dict, right: dict) -> float:
    import numpy as np

    gap = 0.0
    for key in left:
        gap = max(
            gap,
            float(
                np.max(
                    np.abs(
                        left[key].detach().cpu().numpy()
                        - right[key].detach().cpu().numpy()
                    )
                )
            ),
        )
    return gap


def main() -> int:
    lower_priority()
    cpu0 = time.process_time()
    wall0 = time.perf_counter()
    free_before = free_bytes()
    print(f"FREE_BEFORE_IMPORT {free_before}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    prior = json.loads(PRIOR_FREEZE.read_text(encoding="utf-8"))
    selected = [int(item) for item in prior["selected_windows"]]
    if selected != [0, 1, 2, 33, 34, 35, 66, 67, 68]:
        raise RuntimeError(f"frozen window list changed: {selected}")
    freeze = {
        "protocol": "conditional-reference-projection-v1",
        "stage": "P1_CONTROLLED_DIAGNOSTIC",
        "status": "RUNNING",
        "seed": 33001,
        "selected_windows": selected,
        "N": len(selected),
        "copied_from": str(PRIOR_FREEZE.relative_to(ROOT)).replace("\\", "/"),
        "reselected": False,
        "labels_used_for_selection": False,
        "final_pt_opened": False,
        "epsilon_score": None,
        "free_bytes_before_import": free_before,
    }
    write_json(OUT / "P1_FREEZE.json", freeze)
    if free_before < GIB4:
        freeze["status"] = "RESOURCE_DEFERRED"
        write_json(OUT / "P1_FREEZE.json", freeze)
        write_json(
            OUT / "RESOURCE_AND_BUDGET.json",
            {
                "status": "RESOURCE_DEFERRED",
                "free_bytes_before_import": free_before,
                "threshold_bytes": GIB4,
                "anchor_cpu_seconds": "NOT_STARTED",
                "shadow_cpu_seconds": "NOT_STARTED",
                "scoring_cpu_seconds": "NOT_STARTED",
            },
        )
        (OUT / "P1_REPORT.md").write_text(
            "# P1 受控诊断\n\n状态：`RESOURCE_DEFERRED`。\n\n启动时空闲内存仍低于 4 GiB，锚轨迹没有开始。\n",
            encoding="utf-8",
        )
        (OUT / "WINDOW_PAIR_RESULTS.csv").write_text(
            "seed,window,method_identity,anchor_model_event_id,K,client_id_summary,beta_alpha_asset,feasibility_residual,update_vector_asset,R_before,R_after,mse0,mse1,mse2,mse3,WorstGroup,structure_mismatch,status\n",
            encoding="utf-8",
        )
        print("RESOURCE_DEFERRED", flush=True)
        return 3

    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(IMPL))
    import numpy as np
    import pandas as pd
    import torch

    torch.set_num_threads(1)
    from raven_mcs.aggregation.debt import coverage_mix
    from raven_mcs.aggregation.method_policy import get_method_policy
    from raven_mcs.aggregation.methods import get_aggregator
    from raven_mcs.correction.pi_target import build_pi_target
    from raven_mcs.data.base import DatasetMetadata
    from raven_mcs.data.processed_dataset import ProcessedDataset
    from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.e3.target_pair.pair_state_v4 import bind_alpha_by_client, bind_w_by_unit
    from raven_mcs.metrics.distribution import delta_c_s, delta_group
    from raven_mcs.simulation.event_trace import load_event_trace
    from raven_mcs.training.client import unflatten_params
    from raven_mcs.training.client import _flatten_params as flatten_params
    import raven_mcs.aggregation.methods as methods
    import raven_mcs.sag.counterfactual_audit as audit_mod
    import raven_mcs.training.window_runner as window_runner
    from aggregators import constraint_residual, max_residual
    from guards import LowMemoryTracker, clean_server_weights
    from w1_v51a_oracle import project_Cr

    import_cpu = time.process_time() - cpu0
    import_wall = time.perf_counter() - wall0
    print(f"IMPORT cpu={import_cpu:.3f} wall={import_wall:.3f}", flush=True)

    stop = {"reason": None}
    tracker = LowMemoryTracker()
    sampler = {"min_free": free_before, "rss": "UNMEASURED", "rss_error": None}

    def watch() -> None:
        psapi = ctypes.WinDLL("psapi")
        kernel = ctypes.WinDLL("kernel32")

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
        psapi.GetProcessMemoryInfo.restype = ctypes.c_int
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        counters = Counters()
        counters.cb = ctypes.sizeof(Counters)
        while stop["reason"] is None:
            now_free = free_bytes()
            sampler["min_free"] = min(int(sampler["min_free"]), now_free)
            tracker.observe(now_free, time.perf_counter())
            ok = psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
            if ok:
                sampler["rss"] = max(int(sampler["rss"] if sampler["rss"] != "UNMEASURED" else 0), int(counters.PeakWorkingSetSize))
            else:
                sampler["rss"] = "UNMEASURED"
                sampler["rss_error"] = int(kernel.GetLastError())
            if tracker.breached and stop["reason"] is None:
                stop["reason"] = "LOW_MEMORY_30S"
            time.sleep(1.0)

    threading.Thread(target=watch, name="p1-memory", daemon=True).start()

    p2_calls = {"n": 0}

    def counted_solve(*args, **kwargs):
        p2_calls["n"] += 1
        return methods.solve_p2.__wrapped__(*args, **kwargs) if hasattr(methods.solve_p2, "__wrapped__") else original_solve(*args, **kwargs)

    original_solve = methods.solve_p2

    def counted(*args, **kwargs):
        p2_calls["n"] += 1
        return original_solve(*args, **kwargs)

    methods.solve_p2 = counted
    audit_mod.solve_p2 = counted

    class SkippedAudit:
        def as_dict(self) -> dict:
            return {"p2_audit": "SKIPPED_NOT_ON_DEPLOY_PATH", "active_set_mismatch": 1, "both_empty": 0, "raw_state": {}}

    window_runner.audit_design_vs_nodesign = lambda **kwargs: SkippedAudit()

    def normalize(weights):
        cleaned, _record = clean_server_weights(weights)
        return cleaned

    methods._normalize = normalize

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
    mu = np.asarray(MU, dtype=np.float64)
    occ = pd.read_parquet(OCC_PATH)
    spatial_to_client = {str(item): str(item) for item in occ["spatial_id"].astype(str).unique()}
    atomic = occ.copy()
    atomic["target_group"] = atomic["target_group"].astype(str)
    atomic["target_group_main"] = atomic["target_group"]
    atomic["support_flag"] = True
    pi_frame = build_pi_target(atomic, spatial_to_client, split="test")
    pi_target = {
        (str(row.client_id), str(row.opportunity_stratum)): float(row.pi_k_s_tar)
        for row in pi_frame.itertuples()
    }
    train_occ = occ.loc[occ["split"].astype(str) == "train"].copy()
    train_occ["client_id"] = train_occ["spatial_id"].astype(str)
    train_occ["opportunity_stratum"] = train_occ["opportunity_stratum"].astype(str)
    counts = train_occ.groupby(["client_id", "opportunity_stratum"]).size()
    total = float(counts.sum())
    pi_opp = {
        (str(key[0]), str(key[1])): float(value) / total
        for key, value in counts.items()
        if float(value) > 0
    }
    degenerate, _kind, _mult = project_Cr(np.array([0.2, 0.8]), 0.5, 2.0)
    if float(np.max(np.abs(degenerate - 0.5))) > 1e-8:
        raise RuntimeError("K=2 projection did not degenerate to uniform")

    trace, identity = load_event_trace(TRACE)
    from raven_mcs.training.window_runner import build_full_runner

    runner = build_full_runner(
        trace,
        dataset,
        method="raven_mcs",
        design="on",
        n_groups=4,
        model_seed=33001,
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
    if int(runner.local_steps) != 2 or abs(float(runner.eta) - 0.01) > 0:
        raise RuntimeError("runner hyperparameters are not frozen")
    runner.theta = theta_clone(runner.theta)
    runner.model_versions[0] = theta_clone(runner.theta)
    f_policy = runner.policy
    f_aggregator = runner.aggregator
    twostage_policy = get_method_policy("twostage_hajek")

    nwin = int(trace.metadata.num_windows)
    versions = {window: set() for window in range(nwin)}
    for window_id, version in zip(
        trace.events["window_id"].astype(int).tolist(),
        trace.events["downloaded_version"].astype(int).tolist(),
    ):
        if 0 <= int(window_id) < nwin:
            versions[int(window_id)].add(int(version))
    future: dict[int, set[int]] = {}
    accumulated: set[int] = set()
    for window in range(nwin - 1, -1, -1):
        future[window] = set(accumulated)
        accumulated |= versions[window]
    original_process = runner._process_window

    def process_and_prune(window_id, events, original=original_process):
        result = original(window_id, events)
        needed = set(future.get(int(window_id), set()))
        needed.add(int(runner.clock.model_version))
        for version in list(runner.model_versions):
            if int(version) not in needed:
                del runner.model_versions[version]
        return result

    runner._process_window = process_and_prune

    def snapshot():
        return {
            "theta": theta_clone(runner.theta),
            "model_versions": {int(key): theta_clone(value) for key, value in runner.model_versions.items()},
            "debt": np.array(runner.debt, copy=True),
            "omega_sum": np.array(runner.omega_sum, copy=True),
            "scale": float(runner.scale),
            "variance_state": dict(runner.variance_state),
            "variance_mean": {key: np.array(value, copy=True) for key, value in runner.variance_mean.items()},
            "variance_count": dict(runner.variance_count),
            "clock": copy.deepcopy(runner.clock),
            "opportunity": copy.deepcopy(runner.opportunity_estimator),
            "obs": copy.deepcopy(runner.obs_propensity),
            "usable": copy.deepcopy(runner.usable_propensity),
            "sag_state": copy.deepcopy(runner.sag_state),
            "p_model_version": int(runner.p_model_version),
            "q_model_version": int(runner.q_model_version),
            "fedau_u": dict(runner._fedau_usable_count),
            "fedau_a": dict(runner._fedau_attempt_count),
            "diag_len": len(runner.diagnostics),
            "metrics_len": len(runner.metrics),
            "design_len": len(runner.design_window_logs),
            "p_len": len(runner.p_propensity_history),
            "q_len": len(runner.q_propensity_history),
            "q_attempt_len": len(runner.q_attempt_diagnostics),
            "sag_len": len(runner.sag_window_logs),
            "sag_raw_len": len(runner.sag_raw_states),
            "torch_rng": torch.get_rng_state().clone(),
            "numpy_rng": np.random.get_state(),
        }

    def restore(state) -> None:
        runner.theta = theta_clone(state["theta"])
        runner.model.load_state_dict(runner.theta)
        runner.model_versions = {key: theta_clone(value) for key, value in state["model_versions"].items()}
        runner.debt = np.array(state["debt"], copy=True)
        runner.omega_sum = np.array(state["omega_sum"], copy=True)
        runner.scale = float(state["scale"])
        runner.variance_state = dict(state["variance_state"])
        runner.variance_mean = {key: np.array(value, copy=True) for key, value in state["variance_mean"].items()}
        runner.variance_count = dict(state["variance_count"])
        runner.clock = copy.deepcopy(state["clock"])
        runner.opportunity_estimator = copy.deepcopy(state["opportunity"])
        runner.obs_propensity = copy.deepcopy(state["obs"])
        runner.usable_propensity = copy.deepcopy(state["usable"])
        runner.sag_state = copy.deepcopy(state["sag_state"])
        runner.p_model_version = int(state["p_model_version"])
        runner.q_model_version = int(state["q_model_version"])
        runner._fedau_usable_count = dict(state["fedau_u"])
        runner._fedau_attempt_count = dict(state["fedau_a"])
        del runner.diagnostics[state["diag_len"]:]
        del runner.metrics[state["metrics_len"]:]
        del runner.design_window_logs[state["design_len"]:]
        del runner.p_propensity_history[state["p_len"]:]
        del runner.q_propensity_history[state["q_len"]:]
        del runner.q_attempt_diagnostics[state["q_attempt_len"]:]
        del runner.sag_window_logs[state["sag_len"]:]
        del runner.sag_raw_states[state["sag_raw_len"]:]
        runner.policy = f_policy
        runner.aggregator = f_aggregator
        torch.set_rng_state(state["torch_rng"].clone())
        np.random.set_state(state["numpy_rng"])

    real_train = runner._trainer.train_step
    captured = {"updates": []}
    mix_box = {"M": None}
    real_mix = window_runner.coverage_mix

    def remembered_mix(compositions, alpha):
        mix_box["M"] = np.asarray(compositions, dtype=np.float64).copy()
        return real_mix(compositions, alpha)

    window_runner.coverage_mix = remembered_mix

    def train_step(*args, **kwargs):
        update, loss = real_train(*args, **kwargs)
        captured["updates"].append(np.asarray(update, dtype=np.float64).copy())
        return update, loss

    def run_window(window_id: int, policy, aggregator):
        captured["updates"] = []
        before_diag = len(runner.diagnostics)
        p2_before = p2_calls["n"]
        runner.policy = policy
        runner.aggregator = aggregator
        runner._trainer.train_step = train_step
        metrics = runner._process_window(window_id, trace.events)
        runner._trainer.train_step = real_train
        composition = None if mix_box["M"] is None else np.array(mix_box["M"], copy=True)
        fresh = list(runner.diagnostics[before_diag:])
        if len(fresh) != len(captured["updates"]):
            raise RuntimeError(
                f"update/diagnostic mismatch window {window_id}: {len(captured['updates'])} vs {len(fresh)}"
            )
        updates = {}
        for item, vector in zip(fresh, captured["updates"]):
            cid = str(item["client_id"])
            if cid in updates:
                raise RuntimeError(f"duplicate client update {cid}")
            updates[cid] = vector
        return metrics, updates, fresh, p2_calls["n"] - p2_before, composition

    def apply_alpha(theta, clients, updates, alpha):
        flat = flatten_params(theta).copy()
        for index, cid in enumerate(clients):
            vector = updates.get(str(cid))
            if vector is not None and len(vector) > 0:
                flat = flat - float(runner.eta) * float(alpha[index]) * vector
        return unflatten_params(flat, theta), flat

    def score_theta(theta) -> dict:
        anchor = theta_clone(runner.theta)
        runner.model.load_state_dict(theta)
        prediction = _predict(runner, dataset, split="validation")
        runner.model.load_state_dict(anchor)
        if theta_gap(anchor, runner.theta) != 0.0:
            raise RuntimeError("scoring changed the anchor theta")
        groups = np.asarray(prediction["groups"], dtype=int)
        y_true = np.asarray(prediction["y_true"], dtype=np.float64)
        y_pred = np.asarray(prediction["y_pred"], dtype=np.float64)
        mses = []
        counts = []
        weighted = 0.0
        worst = None
        for group, mass in enumerate(mu):
            mask = groups == group
            count = int(mask.sum())
            counts.append(count)
            if mass > 0 and count == 0:
                raise RuntimeError(f"FAIL_VALIDATION_TARGET_COVERAGE group {group}")
            mse = float(np.mean((y_pred[mask] - y_true[mask]) ** 2))
            mses.append(mse)
            weighted += float(mass) * mse
            worst = math.sqrt(mse) if worst is None else max(worst, math.sqrt(mse))
        if counts != [1242, 331, 108, 408]:
            raise RuntimeError(f"validation coverage changed: {counts}")
        return {"R": weighted, "mse": mses, "worst": worst, "rmse": math.sqrt(weighted)}

    def stratum_distance(alpha, clients, diagnostics, window_id: int) -> float:
        class Row:
            active = True

        row = Row()
        row.alpha = [float(item) for item in alpha]
        row.active_clients = [str(item) for item in clients]
        row.window_id = int(window_id)
        return float(
            client_stratum_one(row, diagnostics, alpha)
        )

    def client_stratum_one(row, diagnostics, alpha) -> float:
        unit_s = {str(item.unit_id): str(item.opportunity_stratum) for item in atomic.itertuples(index=False)}
        pi_tar = {f"{key}::{stratum}": float(value) for (key, stratum), value in pi_target.items()}
        alpha_map = {str(cid): float(weight) for cid, weight in zip(row.active_clients, alpha)}
        contrib: dict[str, float] = {}
        for item in diagnostics:
            cid = str(item["client_id"])
            if cid not in alpha_map:
                continue
            for unit_id, local_weight in bind_w_by_unit(item, method="raven").items():
                key = f"{cid}::{unit_s[str(unit_id)]}"
                contrib[key] = contrib.get(key, 0.0) + float(alpha_map[cid] * local_weight)
        keys = sorted(set(contrib) | set(pi_tar))
        estimate = np.asarray([contrib.get(key, 0.0) for key in keys], dtype=np.float64)
        target = np.asarray([pi_tar.get(key, 0.0) for key in keys], dtype=np.float64)
        if float(estimate.sum()) > 0:
            estimate = estimate / float(estimate.sum())
        return float(delta_c_s(estimate, target))

    rows: list[dict] = []
    window_records: list[dict] = []
    segments = {"anchor_cpu": 0.0, "anchor_wall": 0.0, "shadow_cpu": 0.0, "shadow_wall": 0.0, "score_cpu": 0.0, "score_wall": 0.0}
    epsilon = None
    status = "RUNNING"
    failure = None
    last_window = max(selected)

    def budget_exceeded() -> bool:
        return (time.process_time() - cpu0) > CPU_LIMIT or (time.perf_counter() - wall0) > WALL_LIMIT

    def persist_rows() -> None:
        fieldnames = [
            "seed", "window", "method_identity", "anchor_model_event_id", "K",
            "client_id_summary", "beta_alpha_asset", "feasibility_residual",
            "update_vector_asset", "R_before", "R_after", "mse0", "mse1", "mse2", "mse3",
            "WorstGroup", "structure_mismatch", "delta_cs", "theta_step_l2", "status",
        ]
        with (OUT / "WINDOW_PAIR_RESULTS.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    try:
        for window_id in range(last_window + 1):
            if stop["reason"] is not None or budget_exceeded():
                status = "RESOURCE_DEFERRED" if stop["reason"] == "LOW_MEMORY_30S" else status
                if budget_exceeded() and status == "RUNNING":
                    failure = "budget limit reached before the frozen windows were finished"
                    status = "RESOURCE_DEFERRED"
                break
            if window_id not in selected:
                cpu_a = time.process_time()
                wall_a = time.perf_counter()
                metrics = runner._process_window(window_id, trace.events)
                segments["anchor_cpu"] += time.process_time() - cpu_a
                segments["anchor_wall"] += time.perf_counter() - wall_a
                if int(metrics.configured_design or 0) != 1 or int(metrics.actual_design or 0) != 1:
                    status = "FAIL_IMPLEMENTATION"
                    failure = f"anchor Design left the frozen on setting at window {window_id}"
                    break
                continue

            print(f"DECISION_WINDOW {window_id}", flush=True)
            try:
                state = snapshot()
            except Exception as exc:
                status = "BLOCKED_MATCHED_STATE"
                failure = f"F state could not be copied at window {window_id}: {exc}"
                break
            pre_theta = theta_clone(state["theta"])
            pre_version = int(state["clock"].model_version)
            anchor_id = (
                f"seed33001:{identity.trace_hash if hasattr(identity, 'trace_hash') else identity.get('trace_hash')}"
                f":pre_version={pre_version}:window={window_id}"
            )
            shadow_cpu = time.process_time()
            shadow_wall = time.perf_counter()
            try:
                mix_box["M"] = None
                ts_metrics, ts_updates, ts_diags, ts_p2, ts_composition = run_window(
                    window_id, twostage_policy, get_aggregator("twostage_hajek")
                )
                ts_theta = theta_clone(runner.theta)
            except Exception as exc:
                status = "BLOCKED_MATCHED_STATE"
                failure = f"TwoStage could not run from the shared start state at window {window_id}: {exc}"
                break
            segments["shadow_cpu"] += time.process_time() - shadow_cpu
            segments["shadow_wall"] += time.perf_counter() - shadow_wall
            restore(state)
            restore_gap = theta_gap(pre_theta, runner.theta)
            if restore_gap != 0.0 or int(runner.clock.model_version) != pre_version:
                status = "BLOCKED_MATCHED_STATE"
                failure = f"restored anchor diverged at window {window_id}: theta_gap={restore_gap}"
                break
            anchor_cpu = time.process_time()
            anchor_wall = time.perf_counter()
            mix_box["M"] = None
            f_metrics, f_updates, f_diags, f_p2, f_composition = run_window(window_id, f_policy, f_aggregator)
            f_theta = theta_clone(runner.theta)
            segments["anchor_cpu"] += time.process_time() - anchor_cpu
            segments["anchor_wall"] += time.perf_counter() - anchor_wall
            clients = [str(cid) for cid in f_metrics.active_clients]
            beta = np.asarray(f_metrics.beta_hat, dtype=np.float64)
            alpha_f = np.asarray(f_metrics.alpha, dtype=np.float64)
            if (not bool(f_metrics.active)) or len(clients) < 4 or len(alpha_f) != len(clients):
                status = "FAIL_IMPLEMENTATION"
                failure = f"window {window_id} runtime support is not a K>=4 active set"
                break
            if abs(float(beta.sum()) - 1.0) > 1e-8 or np.any(beta < -1e-12):
                status = "FAIL_IMPLEMENTATION"
                failure = f"window {window_id} beta is not a probability vector"
                break
            count = len(clients)
            a_bar = min(1.0, max(0.5, 1.0 / count))
            e_bar = min(3.0, float(count))
            p2_mark = p2_calls["n"]
            alpha_p, kind, _multipliers = project_Cr(beta, a_bar, e_bar)
            alpha_p = np.asarray(alpha_p, dtype=np.float64)
            p_solved = p2_calls["n"] - p2_mark
            alpha_u = np.full(count, 1.0 / count, dtype=np.float64)
            widths = {len(vector) for vector in f_updates.values()}
            flat_width = int(flatten_params(pre_theta).size)
            residual = {
                "P": constraint_residual(alpha_p, a_bar, e_bar),
                "U": constraint_residual(alpha_u, a_bar, e_bar),
                "F": constraint_residual(alpha_f, a_bar, e_bar),
            }
            ts_clients = [str(cid) for cid in ts_metrics.active_clients]
            alpha_ts = np.asarray(ts_metrics.alpha, dtype=np.float64)
            beta_ts = np.asarray(ts_metrics.beta_hat, dtype=np.float64)
            if len(alpha_ts) == len(ts_clients) and len(ts_clients) > 0:
                ts_bar, ts_ess = min(1.0, max(0.5, 1.0 / len(ts_clients))), min(3.0, float(len(ts_clients)))
                residual["TwoStage"] = constraint_residual(alpha_ts, ts_bar, ts_ess)
            manual_f, flat_f = apply_alpha(pre_theta, clients, f_updates, alpha_f)
            formula_gap = theta_gap(manual_f, f_theta)
            theta_p, flat_p = apply_alpha(pre_theta, clients, f_updates, alpha_p)
            theta_u, flat_u = apply_alpha(pre_theta, clients, f_updates, alpha_u)
            flat_before = flatten_params(pre_theta)
            flat_ts = flatten_params(ts_theta)
            checks = {
                "shared_clients": True,
                "vector_width": widths == {flat_width},
                "p_does_not_solve_p2": p_solved == 0,
                "f_solves_p2": f_p2 >= 1,
                "twostage_does_not_solve_p2": ts_p2 == 0,
                "design_on": int(f_metrics.configured_design or 0) == 1 and int(f_metrics.actual_design or 0) == 1,
                "formula_gap": formula_gap,
                "residuals": {name: max_residual(parts) for name, parts in residual.items()},
                "restore_gap": restore_gap,
                "metadata_client_sha_match": client_sha(clients) == prior["selected_detail"][selected.index(window_id)]["client_id_sha256"],
                "projection_kind": str(kind),
            }
            critical = (
                checks["vector_width"]
                and checks["p_does_not_solve_p2"]
                and checks["f_solves_p2"]
                and checks["twostage_does_not_solve_p2"]
                and checks["design_on"]
                and formula_gap <= FORMULA_LIMIT
                and all(value <= 1e-8 for value in checks["residuals"].values())
                and restore_gap == 0.0
            )
            if window_id == selected[0] and not critical:
                status = "FAIL_IMPLEMENTATION"
                failure = f"first-window implementation check failed: {checks}"
                write_json(OUT / "FIRST_WINDOW_CHECK.json", checks)
                break
            if not critical:
                status = "FAIL_IMPLEMENTATION"
                failure = f"implementation check failed at window {window_id}: {checks}"
                write_json(OUT / "FIRST_WINDOW_CHECK.json", checks)
                break

            def pack(name, alpha, theta, diagnostics, beta_vector, method_clients, composition):
                if composition is None or len(method_clients) == 0:
                    omega = None
                    group = ""
                    cs = ""
                else:
                    omega = coverage_mix(composition, alpha)
                    group = float(delta_group(omega, mu))
                    cs = float(stratum_distance(alpha, method_clients, diagnostics, window_id))
                return {
                    "name": name,
                    "alpha": np.asarray(alpha, dtype=np.float64),
                    "theta": theta,
                    "flat": flatten_params(theta),
                    "diagnostics": diagnostics,
                    "clients": method_clients,
                    "beta": np.asarray(beta_vector, dtype=np.float64),
                    "omega": omega,
                    "group": group,
                    "cs": cs,
                }

            prepared = {
                "P_reference_projection": pack("P_reference_projection", alpha_p, theta_p, f_diags, beta, clients, f_composition),
                "U_matched_uniform": pack("U_matched_uniform", alpha_u, theta_u, f_diags, beta, clients, f_composition),
                "F_full_raven_design": pack("F_full_raven_design", alpha_f, f_theta, f_diags, beta, clients, f_composition),
                "TwoStage-Hajek": pack("TwoStage-Hajek", alpha_ts, ts_theta, ts_diags, beta_ts, ts_clients, ts_composition),
            }
            if window_id == selected[0]:
                score_cpu = time.process_time()
                score_wall = time.perf_counter()
                first_before = score_theta(pre_theta)
                second_before = score_theta(pre_theta)
                first_f = score_theta(f_theta)
                second_f = score_theta(f_theta)
                segments["score_cpu"] += time.process_time() - score_cpu
                segments["score_wall"] += time.perf_counter() - score_wall
                repeat_gap = max(
                    abs(first_before["R"] - second_before["R"]),
                    abs(first_f["R"] - second_f["R"]),
                    max(abs(a - b) for a, b in zip(first_before["mse"], second_before["mse"])),
                    max(abs(a - b) for a, b in zip(first_f["mse"], second_f["mse"])),
                )
                checks["repeat_gap"] = repeat_gap
                write_json(OUT / "FIRST_WINDOW_CHECK.json", checks)
                if repeat_gap > SCORE_REPEAT_LIMIT or theta_gap(f_theta, runner.theta) != 0.0:
                    status = "FAIL_IMPLEMENTATION"
                    failure = f"repeat scoring or isolation failed: repeat_gap={repeat_gap}"
                    break
                epsilon = max(repeat_gap, 1e-7)
                freeze["epsilon_score"] = epsilon
                write_json(OUT / "P1_FREEZE.json", freeze)
                print(f"EPSILON_SCORE {epsilon}", flush=True)
            if epsilon is None:
                status = "FAIL_IMPLEMENTATION"
                failure = "epsilon was not frozen before scoring"
                break
            score_cpu = time.process_time()
            score_wall = time.perf_counter()
            before_score = score_theta(pre_theta) if window_id != selected[0] else first_before
            scored = {}
            for name in METHODS:
                if window_id == selected[0] and name == "F_full_raven_design":
                    scored[name] = first_f
                else:
                    scored[name] = score_theta(prepared[name]["theta"])
            segments["score_cpu"] += time.process_time() - score_cpu
            segments["score_wall"] += time.perf_counter() - score_wall
            if theta_gap(f_theta, runner.theta) != 0.0:
                status = "FAIL_IMPLEMENTATION"
                failure = f"shadow scoring changed the anchor at window {window_id}"
                break
            asset = OUT / "assets" / f"window_{window_id}"
            asset.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                asset / "weights_and_updates.npz",
                clients=np.asarray(clients),
                beta=beta,
                alpha_p=alpha_p,
                alpha_u=alpha_u,
                alpha_f=alpha_f,
                twostage_clients=np.asarray(ts_clients),
                alpha_twostage=alpha_ts,
                beta_twostage=beta_ts,
                updates_f=np.stack([f_updates[cid] for cid in clients]),
                updates_twostage=np.stack([ts_updates[cid] for cid in ts_clients]) if ts_clients else np.zeros((0, flat_width)),
            )
            shared = set(clients)
            only_f = sorted(shared - set(ts_clients))
            only_ts = sorted(set(ts_clients) - shared)
            local_gap = []
            f_local = {str(item["client_id"]): np.asarray(item.get("applied_local_weights"), dtype=np.float64) for item in f_diags}
            ts_local = {str(item["client_id"]): np.asarray(item.get("applied_local_weights"), dtype=np.float64) for item in ts_diags}
            for cid in sorted(shared & set(ts_clients)):
                left, right = f_local.get(cid), ts_local.get(cid)
                if left is None or right is None or left.shape != right.shape:
                    local_gap.append(None)
                else:
                    local_gap.append(float(np.sum(np.abs(left - right))))
            record = {
                "window": window_id,
                "K": count,
                "K_twostage": len(ts_clients),
                "client_sha": client_sha(clients),
                "metadata_match": checks["metadata_client_sha_match"],
                "weight_l1": {
                    "P_U": float(np.sum(np.abs(alpha_p - alpha_u))),
                    "F_P": float(np.sum(np.abs(alpha_f - alpha_p))),
                    "F_U": float(np.sum(np.abs(alpha_f - alpha_u))),
                },
                "step_l2": {
                    "P_U": float(np.linalg.norm(flat_p - flat_u)),
                    "F_P": float(np.linalg.norm(flat_f - flat_p)),
                    "F_U": float(np.linalg.norm(prepared["F_full_raven_design"]["flat"] - flat_u)),
                },
                "twostage_client_only_f": only_f,
                "twostage_client_only_twostage": only_ts,
                "twostage_local_weight_l1_on_overlap": local_gap,
                "formula_gap": formula_gap,
                "projection_kind": str(kind),
                "p2": {"F": f_p2, "TwoStage": ts_p2, "P": p_solved},
            }
            window_records.append(record)
            write_json(OUT / "WINDOW_MECHANISM.json", {"windows": window_records, "epsilon_score": epsilon})
            rel_weight = str((asset / "weights_and_updates.npz").relative_to(ROOT)).replace("\\", "/")
            for name in METHODS:
                item = prepared[name]
                score = scored[name]
                rows.append(
                    {
                        "seed": 33001,
                        "window": window_id,
                        "method_identity": name,
                        "anchor_model_event_id": anchor_id,
                        "K": len(item["clients"]),
                        "client_id_summary": client_sha(item["clients"]),
                        "beta_alpha_asset": rel_weight,
                        "feasibility_residual": max_residual(residual[name.split("_")[0] if False else ("P" if name.startswith("P_") else "U" if name.startswith("U_") else "F" if name.startswith("F_") else "TwoStage")]),
                        "update_vector_asset": rel_weight,
                        "R_before": before_score["R"],
                        "R_after": score["R"],
                        "mse0": score["mse"][0],
                        "mse1": score["mse"][1],
                        "mse2": score["mse"][2],
                        "mse3": score["mse"][3],
                        "WorstGroup": score["worst"],
                        "structure_mismatch": item["group"],
                        "delta_cs": item["cs"],
                        "theta_step_l2": float(np.linalg.norm(item["flat"] - flat_before)),
                        "status": "OK",
                    }
                )
            persist_rows()
            print(f"WINDOW_DONE {window_id} R_P={scored['P_reference_projection']['R']}", flush=True)
        else:
            if status == "RUNNING":
                status, _narrative = judge(rows, epsilon, window_records)
    except Exception:
        status = "FAIL_IMPLEMENTATION"
        failure = traceback.format_exc()
        (OUT / "FAILURE_TRACE.txt").write_text(failure, encoding="utf-8")
    finally:
        stop["reason"] = stop["reason"] or "FINISHED"
        persist_rows()
        write_outputs(status, failure, rows, window_records, epsilon, freeze, segments, sampler, cpu0, wall0, import_cpu, import_wall)
    print(status, flush=True)
    return 0 if status in {"P1_NO_TASK_SIGNAL", "P1_MECHANISM_SIGNAL_ONLY"} else 2


def captured_composition(diagnostics, clients):
    import numpy as np

    matrix = []
    by_client = {str(item["client_id"]): item for item in diagnostics}
    for cid in clients:
        item = by_client[str(cid)]
        groups = item.get("c_g")
        if groups is None:
            raise RuntimeError("composition was not retained on the diagnostic")
        matrix.append(np.asarray(groups, dtype=np.float64))
    return np.stack(matrix, axis=1)


def judge(rows: list[dict], epsilon: float, records: list[dict]) -> tuple[str, str]:
    finished = sorted({int(row["window"]) for row in rows if row["status"] == "OK"})
    if len(finished) < 6 or epsilon is None:
        return "P1_NO_TASK_SIGNAL", "完成的预选窗口少于六个，不能给出任务信号。"
    index = {}
    for row in rows:
        index[(int(row["window"]), row["method_identity"])] = row
    need = math.ceil(0.75 * len(finished))
    lines = []
    passed = {}
    for method in ("P_reference_projection", "F_full_raven_design"):
        for baseline in ("U_matched_uniform", "TwoStage-Hajek"):
            gains = []
            wins = 0
            scales = []
            for window in finished:
                risk_m = float(index[(window, method)]["R_after"])
                risk_b = float(index[(window, baseline)]["R_after"])
                before = float(index[(window, baseline)]["R_before"])
                gains.append(risk_b - risk_m)
                scales.append(abs(before - risk_b))
                if risk_m < risk_b - 10.0 * float(epsilon):
                    wins += 1
            mean_gain = sum(gains) / len(gains)
            bar = max(10.0 * float(epsilon), 0.10 * (sum(scales) / len(scales)))
            ok = wins >= need and mean_gain >= bar
            passed[(method, baseline)] = ok
            lines.append(
                f"{method} 相对 {baseline}：严格窗口 {wins}/{len(finished)}，需要至少 {need}；"
                f"平均配对收益 {mean_gain}，门槛 {bar}；{'通过' if ok else '未通过'}。"
            )
    p_signal = passed[("P_reference_projection", "U_matched_uniform")] and passed[("P_reference_projection", "TwoStage-Hajek")]
    f_signal = passed[("F_full_raven_design", "U_matched_uniform")] and passed[("F_full_raven_design", "TwoStage-Hajek")]
    if p_signal or f_signal:
        which = []
        if p_signal:
            which.append("P")
        if f_signal:
            which.append("F")
        lines.append(f"过门槛的臂：{', '.join(which)}。这只是局部机制信号，不是部署收益，也不改变 NO_GO。")
        return "P1_MECHANISM_SIGNAL_ONLY", "\n".join(lines)
    u_better = passed[("P_reference_projection", "U_matched_uniform")] or passed[("F_full_raven_design", "U_matched_uniform")]
    if u_better:
        lines.append("相对同支持消融有局部作用，尚无强基线效用。")
    lines.append("相对 TwoStage 没有达到事先固定的诊断门槛。结果不是训练扩展的依据。")
    return "P1_NO_TASK_SIGNAL", "\n".join(lines)


def write_outputs(status, failure, rows, records, epsilon, freeze, segments, sampler, cpu0, wall0, import_cpu, import_wall) -> None:
    freeze["status"] = status
    freeze["epsilon_score"] = epsilon
    freeze["failure"] = failure
    write_json(OUT / "P1_FREEZE.json", freeze)
    write_json(
        OUT / "RESOURCE_AND_BUDGET.json",
        {
            "status": status,
            "cpu_limit_seconds": CPU_LIMIT,
            "wall_limit_seconds": WALL_LIMIT,
            "import_cpu_seconds": import_cpu,
            "import_wall_seconds": import_wall,
            "anchor_cpu_seconds": segments["anchor_cpu"],
            "anchor_wall_seconds": segments["anchor_wall"],
            "shadow_cpu_seconds": segments["shadow_cpu"],
            "shadow_wall_seconds": segments["shadow_wall"],
            "scoring_cpu_seconds": segments["score_cpu"],
            "scoring_wall_seconds": segments["score_wall"],
            "total_cpu_seconds": time.process_time() - cpu0,
            "total_wall_seconds": time.perf_counter() - wall0,
            "min_free_bytes_sampled": sampler["min_free"],
            "peak_rss_bytes": sampler["rss"],
            "rss_error": sampler["rss_error"],
            "note": "anchor and shadow timers overlap on the decision-window F step because that step is both the anchor advance and the shared-update source",
        },
    )
    (OUT / "P1_REPORT.md").write_text(render_report(status, failure, rows, records, epsilon), encoding="utf-8")


def render_report(status, failure, rows, records, epsilon) -> str:
    narrative = ""
    if rows and epsilon is not None and status in {"P1_NO_TASK_SIGNAL", "P1_MECHANISM_SIGNAL_ONLY"}:
        _status, narrative = judge(rows, epsilon, records)
    lines = [
        "# P1 受控诊断",
        "",
        f"状态：`{status}`。",
        "",
        "这是种子 33001 上的一步机制诊断。P、U、F 使用同一次局部更新，只更换服务器权重。TwoStage 从同一起点和同一外生窗口按自己的协议另算局部更新。它不改变 `NO_GO_PREDICTIVE_SCREEN`，也不进入论文。",
        "",
    ]
    if failure:
        lines.extend([f"失败记录：", "", "```", str(failure), "```", ""])
    lines.append(f"重复评分得到的 epsilon_score = `{epsilon}`。门槛使用 `10 * epsilon_score`。")
    lines.append("")
    lines.append("窗口名单复制自 `p1_controlled_diagnostic_20261020_1002/P1_FREEZE.json`，没有用验证标签重新挑选。")
    lines.append("")
    if records:
        lines.extend(["## 权重差和服务器步差", "", "| 窗口 | K | ||alpha_P-alpha_U||_1 | ||alpha_F-alpha_P||_1 | ||theta_P-theta_U||_2 | ||theta_F-theta_P||_2 |", "|---|---:|---:|---:|---:|---:|"])
        for item in records:
            lines.append(
                f"| {item['window']} | {item['K']} | {item['weight_l1']['P_U']} | {item['weight_l1']['F_P']} | {item['step_l2']['P_U']} | {item['step_l2']['F_P']} |"
            )
        lines.append("")
    if rows:
        lines.extend(["## 一步风险", "", "R 是 `sum_g mu_g MSE_g`，越低越好。差为前者减后者，负数表示前者风险更低。", "", "| 窗口 | R_before | R_P | R_U | R_F | R_TwoStage | R_P-R_U | R_F-R_P | R_P-R_TwoStage | R_F-R_TwoStage |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
        windows = sorted({int(row["window"]) for row in rows})
        index = {(int(row["window"]), row["method_identity"]): row for row in rows}
        for window in windows:
            def risk(name, window=window):
                return float(index[(window, name)]["R_after"])
            before = float(index[(window, "P_reference_projection")]["R_before"])
            rp, ru, rf, rt = (risk(name) for name in METHODS)
            lines.append(
                f"| {window} | {before} | {rp} | {ru} | {rf} | {rt} | {rp - ru} | {rf - rp} | {rp - rt} | {rf - rt} |"
            )
        lines.append("")
    if narrative:
        lines.extend(["## 门槛", "", narrative, ""])
    weight_values = [item["weight_l1"]["P_U"] for item in records]
    if weight_values:
        lines.append(
            f"P 与 U 的权重 L1 范围是 {min(weight_values)} 到 {max(weight_values)}。"
            "权重差、参数步差和风险差是三件不同的事。"
        )
        lines.append("")
    lines.append("没有追加种子，没有改 mu、eta 或约束，也没有启动新的三种子训练。")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise
