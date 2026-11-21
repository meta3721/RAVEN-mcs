"""Train seeds 33002 and 33003. Does not rerun seed 33001 or edit src."""

from __future__ import annotations

import csv
import ctypes
import gc
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ["CUDA_VISIBLE_DEVICES"] = ""

ROOT = Path(__file__).resolve().parents[3]
ROUND = ROOT / "results_conditional_reference_projection" / "round_v1"
FIRST = ROUND / "first_seed"
REMAINING = ROUND / "remaining"
IMPL = ROUND / "implementation"
TRACE_ROOT = ROOT / "artifacts" / "e3_joint_ou_cs_p2_eventtraces_v1"
OCC_PATH = ROOT / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "occupancy_units.parquet"
CACHE = ROOT / "results_cityscanner_lowcost_screen" / "round_v1" / "shared" / "predictions" / "measured-O"
LEDGER_PATH = REMAINING / "BUDGET_STATE.json"
CPU_LIMIT = 600.0
WALL_LIMIT = 900.0
MU = [
    0.6496975806451613,
    0.1350806451612903,
    0.07258064516129033,
    0.14264112903225806,
]
REGION = ("region0", "region1", "region2", "region3")
SCHEDULE = {
    33002: [
        ("TwoStage-Hajek", "twostage_hajek", "external"),
        ("U_matched_uniform", "raven_mcs", "uniform"),
        ("P_reference_projection", "raven_mcs", "projection"),
        ("F_full_raven_design", "raven_mcs", "full_p2"),
        ("FedAvg-Window", "fedavg_window", "external"),
    ],
    33003: [
        ("U_matched_uniform", "raven_mcs", "uniform"),
        ("P_reference_projection", "raven_mcs", "projection"),
        ("F_full_raven_design", "raven_mcs", "full_p2"),
        ("FedAvg-Window", "fedavg_window", "external"),
        ("TwoStage-Hajek", "twostage_hajek", "external"),
    ],
}
FEDERAL = ("FedAvg-Window", "TwoStage-Hajek", "U_matched_uniform")
STATE = {
    "seed": None,
    "arm": None,
    "window": None,
    "completed": [],
    "trigger": None,
}


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


class ProcessMemoryCounters(ctypes.Structure):
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


def free_bytes() -> int:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(status.ullAvailPhys)


def rss_bytes() -> dict:
    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(ProcessMemoryCounters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    if not ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        return {"working_set": None, "peak_working_set": None}
    return {
        "working_set": int(counters.WorkingSetSize),
        "peak_working_set": int(counters.PeakWorkingSetSize),
    }


def lower_priority() -> None:
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def historical_ledger() -> list[dict]:
    return [
        {
            "id": "formula_probe_1",
            "stage": "S1",
            "wall_seconds": 14.414,
            "import_cpu_seconds": 2.922,
            "window_cpu_seconds": "UNKNOWN",
            "contains": [],
            "included_in": None,
            "note": "Failed the server-update check. No official arm.",
        },
        {
            "id": "formula_probe_2",
            "stage": "S1",
            "wall_seconds": 6.164,
            "import_cpu_seconds": 2.078,
            "window_cpu_seconds": "UNKNOWN",
            "contains": [],
            "included_in": None,
            "note": "Diagnostic probe. No official arm.",
        },
        {
            "id": "four_arm_process",
            "stage": "first_seed",
            "wall_seconds": 141.517,
            "cpu_before_F_seconds": 123.2,
            "partial_F_cpu_seconds": "UNKNOWN",
            "contains": ["FedAvg-Window", "TwoStage-Hajek", "U_matched_uniform", "P_reference_projection", "partial F"],
            "included_in": None,
            "note": "Process total already contains the four completed arm rows. Do not add those rows again. Peak RSS is UNMEASURED_FULL_RUN.",
        },
        {
            "id": "F_rerun_process",
            "stage": "first_seed",
            "wall_seconds": 36.866,
            "process_cpu_seconds": "UNKNOWN",
            "included_components": {
                "s1_cpu_seconds": 3.375,
                "s1_wall_seconds": 3.497,
                "F_deploy_cpu_seconds": 30.125,
                "F_deploy_wall_seconds": 30.502,
            },
            "contains": ["F_full_raven_design"],
            "included_in": None,
            "note": "The arm row is inside this process. Peak RSS is UNMEASURED_FULL_RUN.",
        },
        {
            "id": "first_seed_budget_reservation",
            "cpu_seconds": 400,
            "wall_seconds": 600,
            "measured_spend": False,
            "note": "Reservation used to size the continuation cap. Not a measured cost and not an upper bound that has been proved.",
        },
    ]


class ResourceMonitor:
    def __init__(self, tracker) -> None:
        self.tracker = tracker
        self.stop = threading.Event()
        self.min_free = None
        self.peak_rss = None
        self.samples = 0
        self.thread = threading.Thread(target=self._loop, name="memory-sample", daemon=True)

    def sample(self) -> dict:
        free = free_bytes()
        memory = rss_bytes()
        self.samples += 1
        self.min_free = free if self.min_free is None else min(self.min_free, free)
        rss = memory["working_set"]
        if rss is not None:
            self.peak_rss = rss if self.peak_rss is None else max(self.peak_rss, rss)
        peak = memory["peak_working_set"]
        if peak is not None:
            self.peak_rss = peak if self.peak_rss is None else max(self.peak_rss, peak)
        self.tracker.observe(free, time.perf_counter())
        return {"free": free, "rss": rss, "peak": self.peak_rss}

    def _loop(self) -> None:
        while not self.stop.wait(1.0):
            self.sample()

    def start(self) -> None:
        self.sample()
        self.thread.start()

    def close(self) -> None:
        self.stop.set()


def install_runtime(F_MODE: dict, F_EVENTS: list, P2_CALLS: dict) -> None:
    import raven_mcs.aggregation.methods as methods
    import raven_mcs.sag.counterfactual_audit as audit_mod
    import raven_mcs.training.window_runner as window_runner
    from guards import clean_server_weights

    class SkippedAudit:
        def as_dict(self) -> dict:
            return {
                "p2_audit": "SKIPPED_NOT_ON_DEPLOY_PATH",
                "active_set_mismatch": 1,
                "both_empty": 0,
                "raw_state": {},
            }

    window_runner.audit_design_vs_nodesign = lambda **kwargs: SkippedAudit()
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
    original_normalize = methods._normalize

    def normalize(weights):
        if not F_MODE["on"]:
            return original_normalize(weights)
        cleaned, record = clean_server_weights(weights)
        F_EVENTS.append(record)
        return cleaned

    methods._normalize = normalize


def prepare_runner(dataset, method, kind, seed, mu, pi_target, pi_opp, np, monitor, ledger, cpu0, wall0, F_MODE, F_EVENTS, P2_CALLS):
    from dataclasses import replace

    from raven_mcs.simulation.event_trace import load_event_trace
    from raven_mcs.training.window_runner import build_full_runner

    sys.path.insert(0, str(IMPL))
    from aggregators import ReferenceProjectionAggregator, UniformAggregator
    from run_first_seed import detach_server_theta

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
    install_window_guard(runner, trace, seed, method, kind, monitor, ledger, cpu0, wall0, F_EVENTS, P2_CALLS)
    runner.trace_identity = identity
    return runner


def install_window_guard(runner, trace, seed, arm, kind, monitor, ledger, cpu0, wall0, F_EVENTS, P2_CALLS) -> None:
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
    original = runner._process_window
    log_path = REMAINING / f"seed{seed}" / arm / "windows.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handle = log_path.open("w", encoding="utf-8")

    def check(window_id: int, phase: str) -> dict:
        STATE["window"] = int(window_id)
        sample = monitor.sample()
        process_cpu = time.process_time() - cpu0
        process_wall = time.perf_counter() - wall0
        ledger.snapshot(process_cpu, process_wall, f"{seed}:{arm}:{window_id}:{phase}")
        if monitor.tracker.breached:
            raise RuntimeError(
                "LOW_MEMORY_30S "
                + json.dumps(
                    {
                        "seed": seed,
                        "arm": arm,
                        "window": int(window_id),
                        "phase": phase,
                        "free": sample["free"],
                        "continuous_seconds": monitor.tracker.max_continuous,
                    }
                )
            )
        if ledger.exceeds(process_cpu, process_wall):
            spent_cpu, spent_wall = ledger.spent(process_cpu, process_wall)
            raise RuntimeError(
                "BUDGET_EXCEEDED "
                + json.dumps({"seed": seed, "arm": arm, "window": int(window_id), "cpu": spent_cpu, "wall": spent_wall})
            )
        return sample

    def wrapped(window_id, events, original=original):
        if int(runner.local_steps) != 2 or abs(float(runner.eta) - 0.01) > 0:
            raise RuntimeError(f"identity drifted at window {window_id}")
        before_events = len(F_EVENTS)
        before_p2 = P2_CALLS["n"]
        before_records = len(getattr(runner.aggregator, "records", []))
        sample = check(window_id, "before")
        result = original(window_id, events)
        needed = set(future.get(int(window_id), set()))
        needed.add(int(runner.clock.model_version))
        for version in list(runner.model_versions):
            if int(version) not in needed:
                del runner.model_versions[version]
        residual = None
        records = getattr(runner.aggregator, "records", [])
        if len(records) > before_records and "residual" in records[-1]:
            residual = records[-1]["residual"]
        feasibility = None
        if len(F_EVENTS) > before_events:
            feasibility = F_EVENTS[-1]["after"]
            residual = max(feasibility.values())
        line = {
            "seed": int(seed),
            "arm": arm,
            "window": int(window_id),
            "active": bool(getattr(result, "active", False)),
            "server_step": int(bool(getattr(result, "active", False))),
            "local_steps": int(runner.local_steps),
            "eta": float(runner.eta),
            "free_bytes": sample["free"],
            "rss_bytes": sample["rss"],
            "low_continuous_seconds": monitor.tracker.max_continuous,
            "p2_calls": P2_CALLS["n"] - before_p2,
            "projection_or_final_residual": residual,
            "f_after": feasibility,
        }
        handle.write(json.dumps(line) + "\n")
        handle.flush()
        check(window_id, "after")
        return result

    runner._process_window = wrapped
    runner._window_log_handle = handle


def load_context(np, pd, torch):
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(IMPL))
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    from raven_mcs.correction.pi_target import build_pi_target
    from raven_mcs.data.base import DatasetMetadata
    from raven_mcs.data.processed_dataset import ProcessedDataset
    from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.e3.target_pair.pair_state_v4 import bind_alpha_by_client, bind_w_by_unit
    from raven_mcs.metrics.distribution import delta_c_s, delta_group
    from run_first_seed import client_stratum_distance, score_prediction

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
    encoding = {str(key): int(value) for key, value in dataset._target_group_str_to_int.items()}
    if encoding != {name: index for index, name in enumerate(REGION)}:
        raise RuntimeError(f"group encoding mismatch: {encoding}")
    mu = np.asarray(MU, dtype=np.float64)
    mu = mu / float(mu.sum())
    if float(np.max(np.abs(mu - np.asarray(MU)))) > 1e-12:
        raise RuntimeError("frozen mu changed after normalization")
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
    return {
        "dataset": dataset,
        "occ": occ,
        "mu": mu,
        "pi_target": pi_target,
        "pi_opp": pi_opp,
        "predict": _predict,
        "delta_group": delta_group,
        "delta_c_s": delta_c_s,
        "bind_alpha": bind_alpha_by_client,
        "bind_w": bind_w_by_unit,
        "stratum": client_stratum_distance,
        "score": score_prediction,
    }


def audit_caches(dataset, mu, score) -> dict:
    rows = []
    scores = {}
    units = {str(unit.unit_id): unit for unit in dataset.get_atomic_units(split="validation")}
    for seed in (33001, 33002, 33003):
        for method in ("Delivered-SpatialMean", "Delivered-CellBlockMean"):
            path = CACHE / f"{method}_seed{seed}.parquet"
            if not path.is_file():
                rows.append({"method": method, "seed": seed, "status": "MISSING", "reason": "no seed-matched cache"})
                continue
            frame = __import__("pandas").read_parquet(path)
            part = frame.loc[frame["split"].astype(str) == "validation"].copy()
            merged = []
            gaps = []
            for row in part.itertuples(index=False):
                unit = units.get(str(row.unit_id))
                if unit is None:
                    continue
                gaps.append(abs(float(row.y_true_z) - float(unit.target_value)))
                merged.append((int(unit.target_group), float(unit.target_value), float(row.y_pred_z)))
            if len(merged) != len(units) or not gaps or max(gaps) > 1e-6:
                rows.append({"method": method, "seed": seed, "status": "NOT_ACCEPTED", "reason": f"aligned {len(merged)} of {len(units)}"})
                continue
            scored = score([item[0] for item in merged], [item[1] for item in merged], [item[2] for item in merged], mu)
            if scored["status"] != "OK" or scored["formula_gap"] > 1e-10:
                rows.append({"method": method, "seed": seed, "status": "NEEDS_RESCORING", "reason": scored["status"]})
                continue
            scores[(method, seed)] = scored
            rows.append({"method": method, "seed": seed, "status": "ACCEPTED", "reason": f"rmse={scored['rmse_mu']}"})
        for method in ("FedAU-Window", "ObsUse-Window"):
            rows.append(
                {
                    "method": method,
                    "seed": seed,
                    "status": "MISSING",
                    "reason": "no legal unit-level validation asset for this protocol; lowcost files are not accepted and no new training slot is added",
                }
            )
    path = REMAINING / "BASELINE_CACHE_AUDIT.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["method", "seed", "status", "reason"])
        writer.writeheader()
        writer.writerows(rows)
    return {"rows": rows, "scores": scores}


def arm_floor(name: str) -> tuple[float, float]:
    path = FIRST / "seed33001" / name / "arm_result.json"
    row = json.loads(path.read_text(encoding="utf-8"))
    return float(row["total_CPU_s"]), float(row["total_wall_s"])


def completed_row(seed: int, name: str) -> dict | None:
    path = REMAINING / f"seed{seed}" / name / "arm_result.json"
    if not path.is_file():
        return None
    row = json.loads(path.read_text(encoding="utf-8"))
    if row.get("completion_status") == "COMPLETE" and int(row.get("windows", 0)) == 100 and row.get("method_identity") == name:
        return row
    return None


def run_arm(context, seed, name, method, kind, np, torch, monitor, ledger, cpu0, wall0, F_MODE, F_EVENTS, P2_CALLS) -> dict:
    saved = completed_row(seed, name)
    if saved is not None:
        print(f"ARM_REUSE {seed} {name} rmse={saved['RMSE_mu_final']}", flush=True)
        return saved
    floor_cpu, floor_wall = arm_floor(name)
    remaining_cpu, remaining_wall = ledger.remaining(time.process_time() - cpu0, time.perf_counter() - wall0)
    print(f"ARM_START {seed} {name} remaining_cpu={remaining_cpu:.1f} remaining_wall={remaining_wall:.1f}", flush=True)
    if remaining_cpu < floor_cpu or remaining_wall < floor_wall:
        raise RuntimeError(
            f"REMAINING_BUDGET_TOO_SMALL before {seed} {name}: cpu {remaining_cpu} < {floor_cpu} or wall {remaining_wall} < {floor_wall}"
        )
    STATE["seed"] = seed
    STATE["arm"] = name
    STATE["window"] = None
    init_cpu0 = time.process_time()
    init_wall0 = time.perf_counter()
    runner = prepare_runner(
        context["dataset"], method, kind, seed, context["mu"], context["pi_target"], context["pi_opp"],
        np, monitor, ledger, cpu0, wall0, F_MODE, F_EVENTS, P2_CALLS,
    )
    init_cpu = time.process_time() - init_cpu0
    init_wall = time.perf_counter() - init_wall0
    F_MODE["on"] = kind == "full_p2"
    F_EVENTS.clear()
    p2_before = P2_CALLS["n"]
    deploy_cpu0 = time.process_time()
    deploy_wall0 = time.perf_counter()
    try:
        metrics = runner.run()
    finally:
        F_MODE["on"] = False
        handle = getattr(runner, "_window_log_handle", None)
        if handle is not None:
            handle.close()
    p2_calls = P2_CALLS["n"] - p2_before
    if kind in {"projection", "uniform", "external"} and p2_calls != 0:
        raise RuntimeError(f"{name} called solve_p2 {p2_calls} times")
    if kind == "full_p2" and p2_calls <= 0:
        raise RuntimeError(f"{name} did not call solve_p2")
    active_steps = sum(1 for item in metrics if bool(getattr(item, "active", False)))
    if kind == "full_p2" and len(F_EVENTS) != active_steps:
        raise RuntimeError(f"{name} checked {len(F_EVENTS)} F windows but took {active_steps} server steps")
    deploy_cpu = time.process_time() - deploy_cpu0
    deploy_wall = time.perf_counter() - deploy_wall0
    if int(runner.trace.metadata.num_windows) != 100 or len(metrics) != 100:
        raise RuntimeError(f"{name} did not finish 100 logical windows")
    if kind != "external":
        logs = list(runner.design_window_logs)
        if len(logs) != 100 or any(int(item.get("configured_design", -1)) != 1 or int(item.get("actual_design", item.get("Design_t", -1))) != 1 for item in logs):
            raise RuntimeError(f"{name} design identity failed, logs={len(logs)}")
    score_cpu0 = time.process_time()
    score_wall0 = time.perf_counter()
    prediction = context["predict"](runner, context["dataset"], split="validation")
    if not np.all(np.isfinite(prediction["y_pred"])) or not np.all(np.isfinite(prediction["y_true"])):
        raise RuntimeError(f"{name} prediction is not finite")
    scored = context["score"](prediction["groups"], prediction["y_true"], prediction["y_pred"], context["mu"])
    if scored["status"] != "OK":
        raise RuntimeError(f"{name} {scored['status']}")
    group_distance = float(context["delta_group"](runner.omega_bar(), context["mu"]))
    stratum = float(context["stratum"](
        metrics,
        runner.diagnostics,
        context["occ"],
        context["pi_target"],
        "raven" if kind != "external" else method,
        np,
        context["delta_c_s"],
        context["bind_alpha"],
        context["bind_w"],
    )
    )
    if not np.isfinite(group_distance) or not np.isfinite(stratum):
        raise RuntimeError(f"{name} structure distance is not finite")
    out = REMAINING / f"seed{seed}" / name
    out.mkdir(parents=True, exist_ok=True)
    with (out / "validation_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["unit_id", "target_group", "y_true_z", "y_pred_z"])
        for unit_id, group, y_true, y_pred in zip(
            prediction["unit_ids"], prediction["groups"], prediction["y_true"], prediction["y_pred"]
        ):
            writer.writerow([unit_id, int(group), float(y_true), float(y_pred)])
    torch.save(runner.theta, out / "final.pt")
    residuals = [float(record["residual"]) for record in getattr(runner.aggregator, "records", []) if "residual" in record]
    negatives = [float(record["before"]["negative"]) for record in F_EVENTS]
    finals = [max(record["after"].values()) for record in F_EVENTS]
    corrections = [float(record["correction_max_abs"]) for record in F_EVENTS]
    row = {
        "seed": int(seed),
        "method_identity": name,
        "split": "validation",
        "windows": 100,
        "server_steps": active_steps,
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
        "score_CPU_s": time.process_time() - score_cpu0,
        "score_wall_s": time.perf_counter() - score_wall0,
        "max_projection_residual": max(residuals) if residuals else "",
        "deploy_p2_solves": p2_calls,
        "f_windows_checked": len(F_EVENTS),
        "f_solver_negative_clips": sum(1 for record in F_EVENTS if record["clipped_negative"]),
        "f_solver_worst_negative": -max(negatives) if negatives else 0.0,
        "f_max_final_residual": max(finals) if finals else "",
        "f_max_correction": max(corrections) if corrections else 0.0,
        "completion_status": "COMPLETE",
        "resume_state": "FINAL_WEIGHTS_ONLY_NOT_FULL_FEDERATED_RESUME",
        "unit_ids": [str(item) for item in prediction["unit_ids"]],
        "y_true_hash": float(np.sum(np.asarray(prediction["y_true"], dtype=np.float64))),
    }
    public = {key: value for key, value in row.items() if key not in {"unit_ids", "y_true_hash"}}
    write_json(out / "arm_result.json", public)
    print(f"ARM_DONE {seed} {name} rmse={row['RMSE_mu_final']} steps={row['server_steps']}", flush=True)
    del runner
    gc.collect()
    return row


def first_seed_rows() -> list[dict]:
    rows = []
    for path in sorted((FIRST / "seed33001").glob("*/arm_result.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.get("completion_status") != "COMPLETE":
            raise RuntimeError(f"first seed row is incomplete: {path}")
        rows.append(row)
    return rows


def mean(values) -> float:
    return float(sum(values) / len(values))


def write_decision(rows: list[dict], cache: dict) -> None:
    trained = [row for row in rows if row["method_identity"] in {item[0] for item in SCHEDULE[33002]}]
    by_key = {(int(row["seed"]), row["method_identity"]): row for row in trained}
    seeds = (33001, 33002, 33003)
    methods = [item[0] for item in SCHEDULE[33002]]
    for seed in seeds:
        ids = None
        y_hash = None
        for name in methods:
            row = by_key[(seed, name)]
            if "unit_ids" in row:
                if ids is None:
                    ids = tuple(row["unit_ids"])
                    y_hash = row["y_true_hash"]
                elif tuple(row["unit_ids"]) != ids or abs(float(row["y_true_hash"]) - float(y_hash)) > 1e-6:
                    raise RuntimeError(f"validation targets differ inside seed {seed}")
    fields = [
        "seed", "method_identity", "split", "windows", "server_steps", "n0", "n1", "n2", "n3",
        "mse0", "mse1", "mse2", "mse3", "RMSE_mu_final", "WorstGroup_final", "Delta_group", "Delta_cs",
        "deploy_CPU_s", "deploy_wall_s", "init_CPU_s", "init_wall_s", "score_CPU_s", "score_wall_s",
        "max_projection_residual", "deploy_p2_solves", "f_windows_checked", "f_solver_negative_clips",
        "f_solver_worst_negative", "f_max_final_residual", "f_max_correction", "completion_status",
    ]
    with (ROUND / "PER_SEED_RESULTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in trained:
            writer.writerow(row)

    def series(name: str, field: str) -> list[float]:
        return [float(by_key[(seed, name)][field]) for seed in seeds]

    candidates = []
    for name in ("FedAvg-Window", "TwoStage-Hajek", "U_matched_uniform"):
        candidates.append(name)
    cheap_ready = []
    for method in ("Delivered-SpatialMean", "Delivered-CellBlockMean"):
        if all(cache["scores"].get((method, seed)) for seed in seeds):
            cheap_ready.append(method)
            candidates.append(method)

    def rmse_of(name: str) -> list[float]:
        if name in FEDERAL or name in ("FedAvg-Window", "TwoStage-Hajek", "U_matched_uniform", "P_reference_projection", "F_full_raven_design"):
            return series(name, "RMSE_mu_final")
        return [float(cache["scores"][(name, seed)]["rmse_mu"]) for seed in seeds]

    def worst_of(name: str) -> list[float]:
        if name.startswith("Delivered"):
            return [float(cache["scores"][(name, seed)]["worst"]) for seed in seeds]
        return series(name, "WorstGroup_final")

    b_star = min(candidates, key=lambda name: mean(rmse_of(name)))
    federal_star = min(FEDERAL, key=lambda name: mean(series(name, "RMSE_mu_final")))
    p_rmse = series("P_reference_projection", "RMSE_mu_final")
    comparisons = []
    opponents = candidates + ["F_full_raven_design"]
    for name in opponents:
        other_rmse = rmse_of(name)
        other_worst = worst_of(name)
        row = {
            "opponent": name,
            "is_B_star": name == b_star,
            "is_federal_cost_opponent": name == federal_star,
            "mean_rmse_p": mean(p_rmse),
            "mean_rmse_b": mean(other_rmse),
            "rmse_rel": mean(p_rmse) / mean(other_rmse) - 1.0,
            "seeds_p_better": sum(left < right for left, right in zip(p_rmse, other_rmse)),
            "mean_worst_p": mean(series("P_reference_projection", "WorstGroup_final")),
            "mean_worst_b": mean(other_worst),
            "worst_rel": mean(series("P_reference_projection", "WorstGroup_final")) / mean(other_worst) - 1.0,
            "group_pp": "",
            "cs_pp": "",
            "cpu_ratio": "",
            "wall_ratio": "",
        }
        if not name.startswith("Delivered"):
            row["group_pp"] = 50.0 * (mean(series("P_reference_projection", "Delta_group")) - mean(series(name, "Delta_group")))
            row["cs_pp"] = 50.0 * (mean(series("P_reference_projection", "Delta_cs")) - mean(series(name, "Delta_cs")))
            row["cpu_ratio"] = mean(series("P_reference_projection", "deploy_CPU_s")) / mean(series(name, "deploy_CPU_s"))
            row["wall_ratio"] = mean(series("P_reference_projection", "deploy_wall_s")) / mean(series(name, "deploy_wall_s"))
        for seed, left, right in zip(seeds, p_rmse, other_rmse):
            row[f"rmse_p_{seed}"] = left
            row[f"rmse_b_{seed}"] = right
            row[f"rmse_rel_{seed}"] = left / right - 1.0
        comparisons.append(row)
    with (ROUND / "THREE_SEED_COMPARISON.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0].keys()))
        writer.writeheader()
        writer.writerows(comparisons)
    by_name = {row["opponent"]: row for row in comparisons}
    b_row = by_name[b_star]
    f_row = by_name["F_full_raven_design"]
    cost_row = by_name[federal_star]
    other_rows = [row for row in comparisons if row["opponent"] not in {b_star, "F_full_raven_design", "P_reference_projection"}]
    decisions = [
        decision_row("A1_rmse_gain", (1.0 - (b_row["rmse_rel"] + 1.0)) >= 0.02, 1.0 - (b_row["rmse_rel"] + 1.0), 0.02, b_star),
        decision_row("A1_direction", b_row["seeds_p_better"] >= 2, b_row["seeds_p_better"], 2, b_star),
        decision_row("A2_worstgroup", b_row["worst_rel"] <= 0.01, b_row["worst_rel"], 0.01, b_star),
    ]
    if other_rows:
        worst_other = max(other_rows, key=lambda item: item["rmse_rel"])
        decisions.append(decision_row("A3_other_baselines", worst_other["rmse_rel"] <= 0.01, worst_other["rmse_rel"], 0.01, worst_other["opponent"]))
    else:
        decisions.append(decision_row("A3_other_baselines", False, "UNRESOLVED", 0.01, "none"))
    decisions.append(decision_row("A4_cpu", cost_row["cpu_ratio"] - 1.0 <= 0.20, cost_row["cpu_ratio"] - 1.0, 0.20, federal_star))
    decisions.append(decision_row("A4_wall", cost_row["wall_ratio"] - 1.0 <= 0.20, cost_row["wall_ratio"] - 1.0, 0.20, federal_star))
    predictive_pass = all(item["status"] == "PASS" for item in decisions)
    decisions.append(decision_row("A_overall", predictive_pass, "GO_PREDICTIVE_SCREEN" if predictive_pass else "NO_GO_PREDICTIVE_SCREEN", "all A rows PASS", "three seeds"))
    decisions.append(
        {
            "condition": "B_registration",
            "status": "NOT_REGISTERED",
            "value": "NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT",
            "threshold": "deployment contract required",
            "evidence": "frozen",
        }
    )
    s_rows = [
        decision_row("S_rmse", f_row["rmse_rel"] <= 0.01, f_row["rmse_rel"], 0.01, "F"),
        decision_row("S_worst", f_row["worst_rel"] <= 0.01, f_row["worst_rel"], 0.01, "F"),
        decision_row("S_group_pp", float(f_row["group_pp"]) <= 0.5, f_row["group_pp"], 0.5, "F"),
        decision_row("S_cs_pp", float(f_row["cs_pp"]) <= 0.5, f_row["cs_pp"], 0.5, "F"),
        decision_row("S_cpu", float(f_row["cpu_ratio"]) <= 0.80, f_row["cpu_ratio"], 0.80, "F"),
        decision_row("S_wall", float(f_row["wall_ratio"]) <= 0.80, f_row["wall_ratio"], 0.80, "F"),
    ]
    decisions.extend(s_rows)
    simplification_pass = all(item["status"] == "PASS" for item in s_rows)
    any_partial = any(item["status"] == "PASS" for item in s_rows)
    simplification = "SIMPLIFICATION_PASS_BUT_B_NOT_REGISTERED" if simplification_pass else ("PARTIAL_TRADEOFF_EVIDENCE" if any_partial else "SIMPLIFICATION_NOT_MET")
    decisions.append(decision_row("S_overall", simplification_pass, simplification, "all S rows PASS", "F"))
    with (ROUND / "SCREEN_DECISION.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["condition", "status", "value", "threshold", "evidence"])
        writer.writeheader()
        writer.writerows(decisions)
    screen = "GO_PREDICTIVE_SCREEN" if predictive_pass else "NO_GO_PREDICTIVE_SCREEN"
    write_reports(screen, simplification, b_star, federal_star, by_name, decisions)


def decision_row(condition: str, passed: bool, value, threshold, evidence: str) -> dict:
    return {
        "condition": condition,
        "status": "PASS" if passed else "FAIL",
        "value": value,
        "threshold": threshold,
        "evidence": evidence,
    }


def write_reports(screen: str, simplification: str, b_star: str, federal_star: str, by_name: dict, decisions: list[dict]) -> None:
    b_row = by_name[b_star]
    f_row = by_name["F_full_raven_design"]
    u_row = by_name["U_matched_uniform"]
    lines = [
        "# DECISION_REPORT",
        "",
        f"三种子筛选是 {screen}。分支 B 是 NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT。",
        f"全局 B* 按三种子平均 validation RMSE 选择，是 {b_star}。联邦成本对手是 {federal_star}。",
        f"P 相对 B* 的平均 RMSE 相对差是 {b_row['rmse_rel']:.4f}，有利种子 {b_row['seeds_p_better']}/3，WorstGroup 相对差是 {b_row['worst_rel']:.4f}。",
        f"P 相对 Uniform 的平均 RMSE 相对差是 {u_row['rmse_rel']:.4f}，group pp 是 {u_row['group_pp']:.4f}。",
        f"P 相对 F 的平均 RMSE 相对差是 {f_row['rmse_rel']:.4f}，group pp 是 {f_row['group_pp']:.4f}，client-stratum pp 是 {f_row['cs_pp']:.4f}，CPU 比是 {f_row['cpu_ratio']:.4f}，wall 比是 {f_row['wall_ratio']:.4f}。",
        f"简化条件的汇总是 {simplification}。它没有部署合同，不能写成替代通过。",
        "FedAU 和 ObsUse 没有本协议的合法逐单元 validation 资产，结论不包括这两条。",
        "首批历史成本有 UNKNOWN 项，见 COST_LEDGER.json。新轨迹都使用了服务器参数克隆，绝对分数不能直接写成原论文方法的新收益。",
        "比较使用三种子均值之比，不做显著性或非劣证明。",
        "",
    ]
    if screen == "GO_PREDICTIVE_SCREEN":
        lines.append("预测筛有通过记录，但这只表示可以申请有限的独立确认，确认本身没有做。")
    else:
        lines.append("预测筛没有通过。本路线不再追加种子、目标或新候选。")
    (ROUND / "DECISION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if screen == "GO_PREDICTIVE_SCREEN":
        request = [
            "# NEXT_STAGE_REQUEST",
            "",
            "预测筛的冻结条件在这三种子上通过。可以申请一次有限的独立确认。",
            "FedAU 与 ObsUse 仍不在比较范围内。分支 B 没有注册。",
            "在用户明确同意之前，不开始确认实验。",
            "",
        ]
    else:
        request = [
            "# NEXT_STAGE_REQUEST",
            "",
            f"预测筛是 {screen}。建议停止这条路线上的新计算，只整理已经得到的证据。",
            f"B* 是 {b_star}。P 的平均 RMSE 相对差是 {b_row['rmse_rel']:.4f}。",
            f"相对 F 的取舍保留在结果里：RMSE 相对差 {f_row['rmse_rel']:.4f}，group pp {f_row['group_pp']:.4f}，CPU 比 {f_row['cpu_ratio']:.4f}。汇总标记是 {simplification}。",
            "不建议加种子、改目标或重做首批。",
            "",
        ]
    (ROUND / "NEXT_STAGE_REQUEST.md").write_text("\n".join(request), encoding="utf-8")
    freeze = json.loads((ROUND / "EXPERIMENT_FREEZE.json").read_text(encoding="utf-8"))
    freeze["stage"] = screen
    freeze["three_seed_screen"] = screen
    freeze["conditional_branch_B"] = "NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT"
    freeze["B_star"] = b_star
    freeze["federal_cost_opponent"] = federal_star
    freeze["simplification"] = simplification
    write_json(ROUND / "EXPERIMENT_FREEZE.json", freeze)


def write_failure(message: str) -> None:
    spent = ""
    if LEDGER_PATH.is_file():
        spent = LEDGER_PATH.read_text(encoding="utf-8")
    text = "\n".join(
        [
            "# FAILURE_REPORT",
            "",
            f"触发：{STATE['trigger'] or message}",
            f"位置：seed {STATE['seed']}, arm {STATE['arm']}, window {STATE['window']}",
            "已完成资产：seed 33001 的五臂，以及本次已经写成 COMPLETE 的臂。",
            f"已完成的后续臂：{STATE['completed']}",
            "取消：触发点之后的臂，以及任何新的数据、候选和论文修改。",
            "预算：后续两种子合计上限 600 CPU 秒、900 秒 wall。首批 400/600 只是预留，不是已证明的精确历史成本。",
            "最小修复：先看原始日志。不要放宽 1e-8，不要删掉 F，不要自动重跑。",
            "",
            "原始日志：",
            "",
            "```",
            traceback.format_exc(),
            message,
            spent,
            "```",
            "",
        ]
    )
    (ROUND / "FAILURE_REPORT.md").write_text(text, encoding="utf-8")


def main() -> int:
    lower_priority()
    cpu0 = time.process_time()
    wall0 = time.perf_counter()
    before = free_bytes()
    print(f"FREE_BEFORE_IMPORT {before}", flush=True)
    if before < 4 * 1024**3:
        write_json(
            REMAINING / "RESOURCE_PAUSE.json",
            {"stage": "PAUSED_RESOURCE_BEFORE_TRAINING", "free_bytes": before, "training_started": False},
        )
        print("PAUSED_RESOURCE_BEFORE_TRAINING", flush=True)
        return 3
    sys.path.insert(0, str(IMPL))
    import numpy as np
    import pandas as pd
    import torch
    from guards import BudgetLedger, LowMemoryTracker

    ledger = BudgetLedger(LEDGER_PATH, CPU_LIMIT, WALL_LIMIT)
    ledger.load()
    F_MODE = {"on": False}
    F_EVENTS: list = []
    P2_CALLS = {"n": 0}
    install_runtime(F_MODE, F_EVENTS, P2_CALLS)
    context = load_context(np, pd, torch)
    cache = audit_caches(context["dataset"], context["mu"], context["score"])
    monitor = ResourceMonitor(LowMemoryTracker())
    monitor.start()
    rows = first_seed_rows()
    try:
        for seed, arms in SCHEDULE.items():
            for name, method, kind in arms:
                row = run_arm(context, seed, name, method, kind, np, torch, monitor, ledger, cpu0, wall0, F_MODE, F_EVENTS, P2_CALLS)
                rows.append(row)
                STATE["completed"].append(f"{seed}:{name}")
                ledger.snapshot(time.process_time() - cpu0, time.perf_counter() - wall0, f"after:{seed}:{name}")
        write_decision(rows, cache)
        ledger.close_process(time.process_time() - cpu0, time.perf_counter() - wall0, "continuation_complete")
        write_json(
            ROUND / "COST_LEDGER.json",
            {
                "historical": historical_ledger(),
                "historical_peak_rss": "UNMEASURED_FULL_RUN",
                "continuation_limit_cpu": CPU_LIMIT,
                "continuation_limit_wall": WALL_LIMIT,
                "continuation_spent_cpu": ledger.cpu_closed,
                "continuation_spent_wall": ledger.wall_closed,
                "sampled_min_free": monitor.min_free,
                "sampled_peak_rss": monitor.peak_rss,
                "memory_samples": monitor.samples,
                "sample_interval_seconds": 1,
                "note": "Historical rows with UNKNOWN stay unknown. Arm rows inside a listed process are not added again. Continuation figures are this authorized batch only.",
            },
        )
        (ROUND / "RESOURCE_AND_BUDGET.md").write_text(
            "\n".join(
                [
                    "# RESOURCE_AND_BUDGET",
                    "",
                    "历史进程的未知 CPU 仍是 UNKNOWN，详见 COST_LEDGER.json。首批 400/600 是预留，不是已测支出。",
                    f"本次两种子合计实测 CPU {ledger.cpu_closed:.3f} 秒，wall {ledger.wall_closed:.3f} 秒。上限 600 / 900。",
                    f"采样到的最低可用内存 {monitor.min_free} bytes，采样到的 RSS 峰值 {monitor.peak_rss} bytes。采样间隔 1 秒，共 {monitor.samples} 次。",
                    "首批峰值是 UNMEASURED_FULL_RUN。",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print("REMAINING_SEEDS_COMPLETE", flush=True)
        return 0
    finally:
        monitor.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        STATE["trigger"] = str(exc)
        write_failure(str(exc))
        print(traceback.format_exc(), flush=True)
        raise
