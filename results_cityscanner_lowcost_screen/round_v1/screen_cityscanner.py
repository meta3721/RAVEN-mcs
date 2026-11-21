"""Read-only City Scanner hotspot screen.

This driver loads frozen checkpoints and scores a fixed inspection budget.
It does not train, does not call the training runner, and does not edit the paper.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "results_cityscanner_lowcost_screen" / "round_v1"
SHARED = ROUND / "shared"
HOTSPOT = ROUND / "hotspot"
PREDICTIONS = SHARED / "predictions"
FREEZE_PATH = SHARED / "PROTOCOL_FREEZE.json"
ASSET_PATH = SHARED / "ASSET_MANIFEST.csv"
POOL_PATH = HOTSPOT / "POOL_MANIFEST.csv"
H0_STATUS_PATH = SHARED / "H0_STATUS.json"
LEDGER_PATH = SHARED / "BUDGET_LEDGER.json"
AUDIT_PATH = SHARED / "AUDIT_STATUS.json"
CANARY_PATH = SHARED / "CANARY_STATUS.json"
REPRO_PATH = SHARED / "REPRODUCTION_CHECK.csv"
REPRO_JSON = SHARED / "reproduction_rows.json"
BASELINE_STATUS = HOTSPOT / "BASELINE_STATUS.json"
SELECTION_PATH = HOTSPOT / "BASELINE_SELECTION.json"
FAILURE_PATH = HOTSPOT / "FAILURE_REPORT.md"
RESOURCE_PATH = HOTSPOT / "RESOURCE_AND_BUDGET.md"
DECISION_PATH = HOTSPOT / "DECISION_REPORT.md"
SCREEN_PATH = HOTSPOT / "SCREEN_DECISION.json"

GIB = 1024**3
MIN_FREE_START = int(2.5 * GIB)
MIN_FREE_PAUSE = 2 * GIB
MIN_FREE_EXIT = 1 * GIB
MAX_RSS = int(1.5 * GIB)
INFER_CPU = 600.0
INFER_WALL = 20 * 60.0
STAT_CPU = 180.0
STAT_WALL = 10 * 60.0
BOOTSTRAP_DRAWS = 10000
BOOTSTRAP_SEED = 2026101801
METRIC_NAMES = (
    "RMSE_mu",
    "MAE_mu",
    "WorstGroupRMSE",
    "WorstGroupRMSE_R0",
    "WorstGroupRMSE_R1",
    "WorstGroupRMSE_R2",
    "WorstGroupRMSE_R3",
)
BUDGETS = (
    {"name": "0.2", "label": "20%", "numerator": 1, "denominator": 5, "primary": True},
    {"name": "0.1", "label": "10%", "numerator": 1, "denominator": 10, "primary": False},
    {"name": "0.3", "label": "30%", "numerator": 3, "denominator": 10, "primary": False},
)
SIMPLE_BASELINES = (
    "Delivered-SpatialMean",
    "Delivered-CellBlockMean",
    "Fixed-Ensemble",
)
EXPECTED_SPLIT_ROWS = {
    "visit": {"train": 9343, "validation": 3290, "test": 2090},
    "measured-O": {"train": 9253, "validation": 2089, "test": 1687},
}
PRED_COLUMNS = [
    "block",
    "method",
    "seed",
    "split",
    "unit_id",
    "spatial_id",
    "absolute_time_utc",
    "date_utc",
    "target_group",
    "y_true_z",
    "y_pred_z",
    "y_true_phys",
    "y_pred_phys",
]


class ScientificStop(Exception):
    def __init__(self, payload: dict):
        super().__init__(payload.get("measured", "scientific stop"))
        self.payload = payload


class ResourceBlock(Exception):
    def __init__(self, measured: str, resume: str):
        super().__init__(measured)
        self.measured = measured
        self.resume = resume


class StrictMap(dict):
    def get(self, key, default=None):
        if key not in self:
            raise KeyError(key)
        return dict.__getitem__(self, key)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_freeze() -> dict:
    if not FREEZE_PATH.is_file():
        raise ScientificStop(
            {
                "stage": "audit",
                "threshold": "shared/PROTOCOL_FREEZE.json exists",
                "measured": "freeze file is absent",
                "scope": "both blocks",
                "evidence": str(FREEZE_PATH),
                "resume": "H0 freeze must be restored before this driver runs",
                "pending": "predict, baselines, select-baseline, hotspot, report numbers",
                "optional_fix": "Restore the H0 freeze. Rewriting thresholds would change the protocol.",
                "changes_protocol": True,
            }
        )
    return read_json(FREEZE_PATH)


def selected_blocks(freeze: dict, block: str | None) -> list[str]:
    names = list(freeze["blocks"])
    if block is None:
        return names
    if block not in freeze["blocks"]:
        raise ScientificStop(
            {
                "stage": "arguments",
                "threshold": "block is visit or measured-O",
                "measured": block,
                "scope": block,
                "evidence": "argument --block",
                "resume": "rerun with a frozen block name",
                "pending": "the requested stage",
                "optional_fix": "Use a block name already present in the freeze.",
                "changes_protocol": False,
            }
        )
    return [block]


def ledger_rows() -> list[dict]:
    if not LEDGER_PATH.is_file():
        return []
    return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))


def append_ledger(record: dict) -> None:
    rows = ledger_rows()
    rows.append(record)
    write_json(LEDGER_PATH, rows)


def pool_usage(pool: str) -> tuple[float, float]:
    cpu = 0.0
    wall = 0.0
    for row in ledger_rows():
        if row.get("pool") == pool:
            cpu += float(row.get("cpu_seconds", 0.0))
            wall += float(row.get("wall_seconds", 0.0))
    return cpu, wall


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def available_bytes() -> int:
    import ctypes
    from ctypes import wintypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    kernel.GlobalMemoryStatusEx.restype = wintypes.BOOL
    if not kernel.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError(ctypes.get_last_error())
    return int(status.ullAvailPhys)


def process_memory() -> tuple[int, int]:
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ok = psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(),
        ctypes.byref(counters),
        counters.cb,
    )
    if not ok:
        raise OSError(ctypes.get_last_error())
    return int(counters.PeakWorkingSetSize), int(counters.WorkingSetSize)


def process_cpu_seconds() -> float:
    import ctypes
    from ctypes import wintypes

    class FileTime(ctypes.Structure):
        _fields_ = [("lo", wintypes.DWORD), ("hi", wintypes.DWORD)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
    ]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    created, exited, kernel_time, user_time = FileTime(), FileTime(), FileTime(), FileTime()
    ok = kernel.GetProcessTimes(
        kernel.GetCurrentProcess(),
        ctypes.byref(created),
        ctypes.byref(exited),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    )
    if not ok:
        raise OSError(ctypes.get_last_error())

    def seconds(stamp: FileTime) -> float:
        return ((stamp.hi << 32) | stamp.lo) / 10_000_000

    return seconds(kernel_time) + seconds(user_time)


class ResourceWatch:
    def __init__(self, pool: str, command: str):
        self.pool = pool
        self.command = command
        self.session = utc_now()
        self.started = time.perf_counter()
        self.cpu_origin = process_cpu_seconds()
        self.min_available = available_bytes()
        self.peak_rss = process_memory()[0]
        self.failure_cpu = 0.0
        self.accounted_cpu = 0.0
        self.accounted_wall = 0.0

    def sample(self) -> tuple[int, int]:
        avail = available_bytes()
        peak, current = process_memory()
        self.min_available = min(self.min_available, avail)
        self.peak_rss = max(self.peak_rss, peak)
        return avail, current

    def elapsed_cpu(self) -> float:
        return process_cpu_seconds() - self.cpu_origin

    def elapsed_wall(self) -> float:
        return time.perf_counter() - self.started

    def charge(self, cpu_seconds: float, wall_seconds: float, **extra) -> None:
        self.sample()
        self.accounted_cpu += float(cpu_seconds)
        self.accounted_wall += float(wall_seconds)
        append_ledger(
            {
                "pool": self.pool,
                "command": self.command,
                "session": self.session,
                "ended": utc_now(),
                "cpu_seconds": float(cpu_seconds),
                "wall_seconds": float(wall_seconds),
                "peak_rss_bytes": self.peak_rss,
                "min_available_bytes": self.min_available,
                "failure_cpu_seconds": extra.pop("failure_cpu_seconds", 0.0),
                **extra,
            }
        )

    def raise_if_over_budget(self, resume: str) -> None:
        used_cpu, used_wall = pool_usage(self.pool)
        cpu_cap = INFER_CPU if self.pool == "inference" else STAT_CPU
        wall_cap = INFER_WALL if self.pool == "inference" else STAT_WALL
        cpu_now = used_cpu + (self.elapsed_cpu() - self.accounted_cpu)
        wall_now = used_wall + (self.elapsed_wall() - self.accounted_wall)
        if cpu_now >= cpu_cap or wall_now >= wall_cap:
            raise ResourceBlock(
                (
                    f"{self.pool} budget reached: cpu {cpu_now:.3f}s of {cpu_cap:.0f}s, "
                    f"wall {wall_now:.3f}s of {wall_cap:.0f}s"
                ),
                resume,
            )

    def raise_if_memory(self, resume: str) -> None:
        avail, current = self.sample()
        if current > MAX_RSS:
            raise ResourceBlock(
                f"process RSS {current} bytes exceeds {MAX_RSS} bytes",
                resume,
            )
        if avail < MIN_FREE_EXIT:
            raise ResourceBlock(
                f"available memory {avail} bytes is below 1 GiB",
                resume,
            )
        if avail >= MIN_FREE_PAUSE:
            return
        deadline = time.perf_counter() + 30.0
        while time.perf_counter() < deadline:
            time.sleep(5.0)
            avail, current = self.sample()
            if current > MAX_RSS:
                raise ResourceBlock(
                    f"process RSS {current} bytes exceeds {MAX_RSS} bytes",
                    resume,
                )
            if avail < MIN_FREE_EXIT:
                raise ResourceBlock(
                    f"available memory {avail} bytes is below 1 GiB",
                    resume,
                )
            if avail >= MIN_FREE_PAUSE:
                return
        raise ResourceBlock(
            f"available memory stayed below 2 GiB for 30 seconds (last {avail} bytes)",
            resume,
        )

    def record(self, **extra) -> None:
        self.charge(
            max(0.0, self.elapsed_cpu() - self.accounted_cpu),
            max(0.0, self.elapsed_wall() - self.accounted_wall),
            **extra,
        )


def require_start_memory() -> None:
    avail = available_bytes()
    if avail < MIN_FREE_START:
        raise ResourceBlock(
            f"available memory {avail} bytes is below 2.5 GiB before heavy imports",
            "rerun the same command when at least 2.5 GiB is free",
        )


def write_failure(payload: dict) -> None:
    HOTSPOT.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Hotspot screen failure report",
        "",
        f"- Written: {utc_now()}",
        f"- Stage: {payload.get('stage', '')}",
        f"- Scope: {payload.get('scope', '')}",
        f"- Preset threshold: {payload.get('threshold', '')}",
        f"- Measured value: {payload.get('measured', '')}",
        f"- Log evidence: {payload.get('evidence', '')}",
        f"- Resume point: {payload.get('resume', '')}",
        f"- Not yet run: {payload.get('pending', '')}",
        f"- Smallest optional fix: {payload.get('optional_fix', '')}",
        f"- That fix changes the protocol: {payload.get('changes_protocol', '')}",
        "",
        "The measured values above are the observation. A cause that was not measured is not stated.",
        "",
    ]
    FAILURE_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_resource_md() -> None:
    infer_cpu, infer_wall = pool_usage("inference")
    stat_cpu, stat_wall = pool_usage("statistics")
    audit_cpu, audit_wall = pool_usage("audit")
    peaks = [int(row.get("peak_rss_bytes", 0)) for row in ledger_rows()]
    avail_values = [
        int(row["min_available_bytes"])
        for row in ledger_rows()
        if "min_available_bytes" in row
    ]
    failure_cpu = sum(float(row.get("failure_cpu_seconds", 0.0)) for row in ledger_rows())
    reuse = sum(
        int(row.get("cache_reuse_models", 0))
        for row in ledger_rows()
        if row.get("kind") == "model"
    )
    h0 = (SHARED / "H0_RESOURCE.md").read_text(encoding="utf-8") if (SHARED / "H0_RESOURCE.md").is_file() else ""
    lines = [
        "# Hotspot screen resources",
        "",
        "H0 asset audit is recorded separately and is outside the inference cap.",
        "",
        "## H0 audit file",
        "",
        h0.rstrip(),
        "",
        "## This driver",
        "",
        f"- Audit CPU seconds: {audit_cpu:.6f}",
        f"- Audit wall seconds: {audit_wall:.6f}",
        f"- Inference CPU seconds, including failed attempts and cache verification: {infer_cpu:.6f}",
        *(
            [
                "- Rows with cpu_not_sampled exited before the CPU watch. Their CPU is absent from the total and their wall is included."
            ]
            if any(row.get("cpu_not_sampled") for row in ledger_rows())
            else []
        ),
        f"- Inference cap CPU seconds: {INFER_CPU:.0f}",
        f"- Inference active wall seconds: {infer_wall:.6f}",
        f"- Inference cap wall seconds: {INFER_WALL:.0f}",
        f"- Statistics CPU seconds: {stat_cpu:.6f}",
        f"- Statistics cap CPU seconds: {STAT_CPU:.0f}",
        f"- Statistics active wall seconds: {stat_wall:.6f}",
        f"- Statistics cap wall seconds: {STAT_WALL:.0f}",
        f"- Peak RSS bytes across driver commands: {max(peaks) if peaks else 0}",
        f"- Minimum available bytes observed: {min(avail_values) if avail_values else ''}",
        f"- Cache-reuse model count: {reuse}",
        f"- Failure CPU seconds, already included in the pool totals: {failure_cpu:.6f}",
        "",
        "Shared prediction cost is recorded once in the inference pool. Later stages read the shards and charge their own statistics time.",
        "",
    ]
    RESOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESOURCE_PATH.write_text("\n".join(lines), encoding="utf-8")


def require_file(path: Path, stage: str, resume: str) -> None:
    if not path.is_file():
        raise ScientificStop(
            {
                "stage": stage,
                "threshold": f"{path.name} exists",
                "measured": "file is absent",
                "scope": "requested blocks",
                "evidence": str(path),
                "resume": resume,
                "pending": "later stages that depend on this file",
                "optional_fix": "Run the missing stage. Changing its rule would change the protocol.",
                "changes_protocol": False,
            }
        )


def cmd_audit(block: str | None) -> int:
    watch = ResourceWatch("audit", "audit --experiment hotspot")
    freeze = load_freeze()
    blocks = selected_blocks(freeze, block)
    status = read_json(H0_STATUS_PATH)
    assets = read_csv(ASSET_PATH)
    problems = []
    for name in blocks:
        block_status = status["blocks"][name]["status"]
        if block_status != "ready":
            problems.append(f"{name} H0 status {block_status}")
        rows = [row for row in assets if row["block"] == name]
        if len(rows) != 50:
            problems.append(f"{name} asset rows {len(rows)}")
        bad = [row for row in rows if row["status"] != "ok"]
        if bad:
            problems.append(f"{name} non-ok assets {len(bad)}")
        methods = {row["method"] for row in rows}
        if methods != set(freeze["methods"]):
            problems.append(f"{name} methods {sorted(methods)}")
        seeds = {int(row["seed"]) for row in rows}
        if seeds != set(freeze["blocks"][name]["seeds"]):
            problems.append(f"{name} seeds differ from the freeze")
    tie = list(freeze["non_raven_tie_order_unicode"])
    if tie != sorted(tie):
        problems.append("freeze tie order is not Unicode code-point order")
    payload = {
        "experiment": "hotspot",
        "ended": utc_now(),
        "blocks": blocks,
        "h0_ready": not problems,
        "problems": problems,
        "plan_authorizes_screen": True,
        "freeze_rewritten": False,
        "pool_rewritten": False,
        "step_2_flag_left_unchanged": True,
    }
    write_json(AUDIT_PATH, payload)
    watch.record(cache_reuse_models=0, problems=len(problems))
    write_resource_md()
    if problems:
        write_failure(
            {
                "stage": "audit",
                "threshold": "H0 status ready and 50 ok assets per requested block",
                "measured": "; ".join(problems),
                "scope": ", ".join(blocks),
                "evidence": str(AUDIT_PATH),
                "resume": "resolve the H0 status before predict",
                "pending": "predict, baselines, select-baseline, hotspot",
                "optional_fix": "Repair the missing asset. Dropping a seed would change the protocol.",
                "changes_protocol": True,
            }
        )
        return 2
    print("audit ready", ", ".join(blocks))
    return 0


def import_scientific():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import numpy as np
    import pandas as pd

    return np, pd


def import_torch():
    import torch

    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    torch.set_num_threads(1)
    return torch


def apply_train_zscore_once(dataset) -> dict[str, float]:
    """Match dataset_load.apply_train_zscore_standardization, applied once."""
    if getattr(dataset, "_screen_zscore_applied", False):
        raise RuntimeError("train z-score was already applied")
    mean = float(dataset.target_mean)
    std = float(dataset.target_std) if float(dataset.target_std) > 0 else 1.0
    dataset._client_df = dataset._client_df.copy()
    dataset._client_df["potential_measurement"] = (
        dataset._client_df["potential_measurement"].astype(float) - mean
    ) / std
    dataset._atomic_df = dataset._atomic_df.copy()
    dataset._atomic_df["target_value"] = (
        dataset._atomic_df["target_value"].astype(float) - mean
    ) / std
    dataset._measurement_index = {
        (str(row["client_id"]), str(row["unit_id"])): float(row["potential_measurement"])
        for _, row in dataset._client_df.iterrows()
    }
    dataset._standardized = True
    dataset._scaler_mean = mean
    dataset._scaler_std = std
    dataset._screen_zscore_applied = True
    return {"scaler_mean": mean, "scaler_std": std}


def absolute_time_hours(value) -> float:
    if hasattr(value, "timestamp"):
        return float(value.timestamp()) / 3600.0
    return float(value)


def time_iso(value, pd) -> str:
    stamp = pd.to_datetime(value, utc=True)
    return pd.Timestamp(stamp).isoformat()


def date_utc(value, pd) -> str:
    stamp = pd.to_datetime(value, utc=True)
    return pd.Timestamp(stamp).strftime("%Y-%m-%d")


def budget_k(n_grids: int, numerator: int, denominator: int) -> int:
    if n_grids < 10:
        raise ScientificStop(
            {
                "stage": "H3",
                "threshold": "qualified slot has at least 10 grids",
                "measured": f"N={n_grids}",
                "scope": "slot scoring",
                "evidence": "pool row marked included",
                "resume": "stop before changing the 10-grid floor",
                "pending": "endpoint aggregation",
                "optional_fix": "Lowering the floor would change the protocol.",
                "changes_protocol": True,
            }
        )
    k = (n_grids * numerator + denominator - 1) // denominator
    if k < 1 or k > n_grids:
        raise ScientificStop(
            {
                "stage": "H3",
                "threshold": "1 <= k <= N",
                "measured": f"k={k}, N={n_grids}",
                "scope": "slot scoring",
                "evidence": "integer ceil",
                "resume": "stop before scoring this slot",
                "pending": "endpoint aggregation",
                "optional_fix": "Changing k would change the protocol.",
                "changes_protocol": True,
            }
        )
    return k


def load_dataset(block: str, spec: dict, np, pd):
    from raven_mcs.data.base import DatasetMetadata
    from raven_mcs.data.processed_dataset import ProcessedDataset

    metadata = DatasetMetadata(
        dataset=spec["dataset"],
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
    dataset = ProcessedDataset(ROOT / "data" / "processed" / spec["dataset"], metadata)
    counts = {
        split: int((dataset._atomic_df["split"] == split).sum())
        for split in ("train", "validation", "test")
    }
    expected = EXPECTED_SPLIT_ROWS[block]
    if counts != expected:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": f"split row counts {expected}",
                "measured": str(counts),
                "scope": block,
                "evidence": spec["atomic_units"],
                "resume": "stop this block before inference",
                "pending": "prediction and hotspot endpoints",
                "optional_fix": "Using a different row set would change the scored test.",
                "changes_protocol": True,
            }
        )
    encoding = {str(key): int(value) for key, value in dataset._target_group_str_to_int.items()}
    frozen_encoding = {str(key): int(value) for key, value in spec["h_encoding"].items()}
    if encoding != frozen_encoding:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": f"h encoding {frozen_encoding}",
                "measured": str(encoding),
                "scope": block,
                "evidence": "ProcessedDataset group map on the full table",
                "resume": "stop this block before inference",
                "pending": "prediction and hotspot endpoints",
                "optional_fix": "Remapping groups would change the protocol.",
                "changes_protocol": True,
            }
        )
    raw_y = {
        str(unit): float(value)
        for unit, value in zip(
            dataset._atomic_df["unit_id"].tolist(),
            dataset._atomic_df["target_value"].tolist(),
        )
    }
    scaler = apply_train_zscore_once(dataset)
    spatial = {str(key): int(value) for key, value in dataset._spatial_to_idx.items()}
    if len(spatial) != dataset.num_spatial:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "spatial ids remain unique after string conversion",
                "measured": f"keys {len(spatial)} num_spatial {dataset.num_spatial}",
                "scope": block,
                "evidence": "ProcessedDataset._spatial_to_idx",
                "resume": "stop this block before inference",
                "pending": "prediction",
                "optional_fix": "Collapsing spatial ids would change the model index.",
                "changes_protocol": True,
            }
        )
    total_slots = int(dataset.atomic_df["time_index"].max()) + 1
    pool = read_csv(POOL_PATH)
    for split in ("validation", "test"):
        part = dataset.atomic_df[dataset.atomic_df["split"] == split]
        got = {time_iso(value, pd) for value in part["absolute_time"].tolist()}
        want = {
            row["absolute_time"]
            for row in pool
            if row["block"] == block and row["split"] == split
        }
        if got != want:
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "prediction time keys equal the H0 pool",
                    "measured": f"{split} got {len(got)} pool {len(want)} overlap {len(got & want)}",
                    "scope": block,
                    "evidence": f"sample got {next(iter(got))} pool {next(iter(want))}",
                    "resume": "stop before inference until the time key matches H0",
                    "pending": "prediction",
                    "optional_fix": "Changing slot keys would change the protocol.",
                    "changes_protocol": True,
                }
            )
    spatial_ids = [""] * len(spatial)
    for sid, index in spatial.items():
        spatial_ids[index] = sid
    scaler_doc = {
        "block": block,
        "mean": scaler["scaler_mean"],
        "std": scaler["scaler_std"],
        "mean_repr": repr(scaler["scaler_mean"]),
        "std_repr": repr(scaler["scaler_std"]),
        "ddof": 0,
        "h_encoding": frozen_encoding,
        "num_spatial": int(dataset.num_spatial),
        "spatial_ids": spatial_ids,
        "total_time_slots": total_slots,
        "split_rows": counts,
        "mu": spec["mu"],
    }
    scaler_path = PREDICTIONS / block / "scaler.json"
    if scaler_path.is_file():
        old = read_json(scaler_path)
        if old.get("mean_repr") != scaler_doc["mean_repr"] or old.get("std_repr") != scaler_doc["std_repr"]:
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "existing scaler identity matches this load",
                    "measured": f"stored {old.get('mean_repr')} {old.get('std_repr')}",
                    "scope": block,
                    "evidence": str(scaler_path),
                    "resume": "stop without overwriting the scaler",
                    "pending": "prediction",
                    "optional_fix": "Overwriting a conflicting scaler would replace old evidence.",
                    "changes_protocol": True,
                }
            )
    else:
        write_json(scaler_path, scaler_doc)
    return dataset, scaler, spatial, total_slots, raw_y


def mu_weights(groups, mu, np):
    groups = np.asarray(groups, dtype=int)
    weights = np.zeros(len(groups), dtype=np.float64)
    counts = {int(group): int(np.sum(groups == group)) for group in range(4)}
    for index, group in enumerate(groups.tolist()):
        weights[index] = float(mu[group]) / max(counts[int(group)], 1)
    total = float(weights.sum())
    if total <= 0:
        weights[:] = 1.0 / len(weights)
    else:
        weights /= total
    return weights


def group_rmse(y_true, y_pred, mask, weights, np) -> float:
    if not np.any(mask):
        return float("nan")
    subset = weights[mask].copy()
    total = float(subset.sum())
    subset = subset / total if total > 0 else np.full(int(mask.sum()), 1.0 / int(mask.sum()))
    error = y_true[mask] - y_pred[mask]
    return float(np.sqrt(np.sum(subset * error * error)))


def metric_bundle(y_true, y_pred, groups, mu, np) -> dict[str, float]:
    from raven_mcs.metrics.accuracy import mae_mu, rmse_mu

    weights = mu_weights(groups, mu, np)
    values = [
        group_rmse(y_true, y_pred, groups == group, weights, np) for group in range(4)
    ]
    return {
        "RMSE_mu": float(rmse_mu(y_pred, y_true, weights)),
        "MAE_mu": float(mae_mu(y_pred, y_true, weights)),
        "WorstGroupRMSE": float(np.nanmax(np.asarray(values, dtype=np.float64))),
        "WorstGroupRMSE_R0": float(values[0]),
        "WorstGroupRMSE_R1": float(values[1]),
        "WorstGroupRMSE_R2": float(values[2]),
        "WorstGroupRMSE_R3": float(values[3]),
    }


def tolerance(old: float) -> float:
    return 1e-6 + 1e-5 * abs(old)


def within_tolerance(new: float, old: float) -> bool:
    if not math.isfinite(new) or not math.isfinite(old):
        return False
    return abs(new - old) <= tolerance(old)


def forward_batch(model, spatial_ids, hours, indices, spatial, total_slots, torch):
    from raven_mcs.models.features import extract_features

    spatial_index, hour, weekday, trend = extract_features(
        spatial_ids,
        hours,
        indices,
        StrictMap(spatial),
        total_slots,
    )
    with torch.inference_mode():
        pred = model(spatial_index, hour, weekday, trend).detach().cpu().numpy().reshape(-1)
    return pred


def batch_agreement(model, spatial_ids, hours, indices, spatial, total_slots, torch, np) -> float:
    take = min(8, len(spatial_ids))
    singles = []
    for index in range(take):
        pred = forward_batch(
            model,
            [spatial_ids[index]],
            [hours[index]],
            [indices[index]],
            spatial,
            total_slots,
            torch,
        )
        singles.append(float(pred[0]))
    batched = forward_batch(
        model,
        spatial_ids[:take],
        hours[:take],
        indices[:take],
        spatial,
        total_slots,
        torch,
    )
    return float(np.max(np.abs(np.asarray(singles) - batched[:take])))


def frame_arrays(frame, spatial, pd):
    spatial_ids = frame["spatial_id"].astype(str).tolist()
    missing = sorted({sid for sid in spatial_ids if sid not in spatial})
    if missing:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "every spatial id is in the full-table index",
                "measured": f"{len(missing)} unknown ids, first {missing[:3]}",
                "scope": "prediction frame",
                "evidence": "extract_features would otherwise map an unknown id to 0",
                "resume": "stop this model before the forward pass",
                "pending": "remaining models and hotspot endpoints",
                "optional_fix": "Mapping an unknown id to 0 would change the protocol.",
                "changes_protocol": True,
            }
        )
    hours = [absolute_time_hours(value) for value in frame["absolute_time"].tolist()]
    indices = [int(value) for value in frame["time_index"].tolist()]
    return spatial_ids, hours, indices


def predict_frame(model, frame, spatial, total_slots, torch, np):
    spatial_ids, hours, indices = frame_arrays(frame, spatial, None)
    preds = np.empty(len(frame), dtype=np.float64)
    model.eval()
    for start in range(0, len(frame), 256):
        stop = min(start + 256, len(frame))
        preds[start:stop] = forward_batch(
            model,
            spatial_ids[start:stop],
            hours[start:stop],
            indices[start:stop],
            spatial,
            total_slots,
            torch,
        )
    return preds


def load_checkpoint(path: Path, num_spatial: int, torch):
    from raven_mcs.models.common_ndmf import CommonNDMF

    try:
        payload = torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        payload = torch.load(path, map_location="cpu")
    if isinstance(payload, dict) and "state_dict" in payload and isinstance(payload["state_dict"], dict):
        state = payload["state_dict"]
    elif isinstance(payload, dict):
        state = payload
    else:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "checkpoint is a state_dict",
                "measured": type(payload).__name__,
                "scope": str(path),
                "evidence": "torch.load return type",
                "resume": "stop this model; do not substitute another checkpoint",
                "pending": "later models on this block if the identity is wrong",
                "optional_fix": "Loading a partial_model would change the protocol.",
                "changes_protocol": True,
            }
        )
    weight = state.get("spatial.weight")
    if weight is None or int(weight.shape[0]) != int(num_spatial):
        got = None if weight is None else int(weight.shape[0])
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": f"spatial embedding rows equal full-table num_spatial {num_spatial}",
                "measured": str(got),
                "scope": str(path),
                "evidence": "state_dict spatial.weight",
                "resume": "stop this model",
                "pending": "hotspot endpoints for this block",
                "optional_fix": "Rebuilding the index from the test split would change the protocol.",
                "changes_protocol": True,
            }
        )
    model = CommonNDMF(num_spatial=num_spatial)
    model.load_state_dict(state)
    model.eval()
    return model


def shard_paths(block: str, method: str, seed: int) -> tuple[Path, Path]:
    directory = PREDICTIONS / block
    directory.mkdir(parents=True, exist_ok=True)
    stem = f"{method}_seed{seed}"
    return directory / f"{stem}.parquet", directory / f"{stem}.json"


def expected_ids(dataset, split: str) -> list[str]:
    part = dataset.atomic_df[dataset.atomic_df["split"] == split]
    return [str(value) for value in part["unit_id"].tolist()]


def id_hash(unit_ids: list[str]) -> str:
    return sha256_text("\n".join(unit_ids))


def reproduction_rows() -> list[dict]:
    if not REPRO_JSON.is_file():
        return []
    return json.loads(REPRO_JSON.read_text(encoding="utf-8"))


def store_reproduction(rows_for_model: list[dict]) -> None:
    existing = [
        row
        for row in reproduction_rows()
        if not (
            row["block"] == rows_for_model[0]["block"]
            and row["method"] == rows_for_model[0]["method"]
            and int(row["seed"]) == int(rows_for_model[0]["seed"])
        )
    ]
    existing.extend(rows_for_model)
    write_json(REPRO_JSON, existing)
    write_csv(
        REPRO_PATH,
        existing,
        ["block", "method", "seed", "metric", "old", "new", "diff", "tolerance", "pass"],
    )


def build_prediction_table(block, method, seed, dataset, preds_by_split, scaler, raw_y, np, pd):
    rows = []
    mean = float(scaler["scaler_mean"])
    std = float(scaler["scaler_std"])
    max_truth_gap = 0.0
    for split, pred_z in preds_by_split.items():
        frame = dataset.atomic_df[dataset.atomic_df["split"] == split].reset_index(drop=True)
        if len(frame) != len(pred_z):
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "prediction length equals the split",
                    "measured": f"{split} rows {len(frame)} preds {len(pred_z)}",
                    "scope": f"{block} {method} {seed}",
                    "evidence": "predict_frame",
                    "resume": "stop this model",
                    "pending": "later stages",
                    "optional_fix": "Dropping rows would change the protocol.",
                    "changes_protocol": True,
                }
            )
        y_true_z = frame["target_value"].to_numpy(dtype=np.float64)
        y_true_phys = y_true_z * std + mean
        y_pred_phys = pred_z * std + mean
        for index in range(len(frame)):
            unit_id = str(frame.at[index, "unit_id"])
            gap = abs(float(y_true_phys[index]) - raw_y[unit_id])
            max_truth_gap = max(max_truth_gap, gap)
            rows.append(
                {
                    "block": block,
                    "method": method,
                    "seed": int(seed),
                    "split": split,
                    "unit_id": unit_id,
                    "spatial_id": str(frame.at[index, "spatial_id"]),
                    "absolute_time_utc": time_iso(frame.at[index, "absolute_time"], pd),
                    "date_utc": date_utc(frame.at[index, "absolute_time"], pd),
                    "target_group": str(frame.at[index, "target_group"]),
                    "y_true_z": float(y_true_z[index]),
                    "y_pred_z": float(pred_z[index]),
                    "y_true_phys": float(y_true_phys[index]),
                    "y_pred_phys": float(y_pred_phys[index]),
                }
            )
    if max_truth_gap > 1e-6:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "inverse z-score matches the raw train-scaled target within 1e-6",
                "measured": f"max abs gap {max_truth_gap}",
                "scope": f"{block} {method} {seed}",
                "evidence": "y_true_phys versus parquet target_value",
                "resume": "stop this model before accepting the shard",
                "pending": "hotspot endpoints",
                "optional_fix": "A second standardization would change the endpoint scale.",
                "changes_protocol": True,
            }
        )
    return pd.DataFrame(rows, columns=PRED_COLUMNS)


def evaluate_against_accepted(block, method, seed, score_path, y_true, y_pred, groups, mu, np):
    accepted = read_json(ROOT / score_path)
    fresh = metric_bundle(y_true, y_pred, groups, mu, np)
    rows = []
    passed = True
    for name in METRIC_NAMES:
        old = float(accepted[name])
        new = float(fresh[name])
        ok = within_tolerance(new, old)
        passed = passed and ok
        rows.append(
            {
                "block": block,
                "method": method,
                "seed": int(seed),
                "metric": name,
                "old": repr(old),
                "new": repr(new),
                "diff": repr(new - old),
                "tolerance": repr(tolerance(old)),
                "pass": str(ok).lower(),
            }
        )
    return passed, rows, fresh


def cache_decision(parquet_path: Path, sidecar_path: Path, identity: dict, dataset) -> str:
    if not parquet_path.is_file() and not sidecar_path.is_file():
        return "missing"
    if not parquet_path.is_file() or not sidecar_path.is_file():
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "prediction shard and sidecar exist together",
                "measured": f"parquet {parquet_path.is_file()} sidecar {sidecar_path.is_file()}",
                "scope": identity["block"] + " " + identity["method"] + " " + str(identity["seed"]),
                "evidence": str(parquet_path),
                "resume": "stop without overwriting a partial shard",
                "pending": "later stages using this model",
                "optional_fix": "Deleting the partial file by hand is outside this command.",
                "changes_protocol": False,
            }
        )
    sidecar = read_json(sidecar_path)
    same_identity = sidecar.get("checkpoint_sha256") == identity["checkpoint_sha256"]
    if sidecar.get("reproduction_pass") and not same_identity:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "completed cache identity matches the checkpoint",
                "measured": f"stored {sidecar.get('checkpoint_sha256')} current {identity['checkpoint_sha256']}",
                "scope": f"{identity['block']} {identity['method']} {identity['seed']}",
                "evidence": str(sidecar_path),
                "resume": "stop without overwriting the completed shard",
                "pending": "a new inference of this model",
                "optional_fix": "Overwriting a conflicting cache would replace old evidence.",
                "changes_protocol": True,
            }
        )
    if not sidecar.get("reproduction_pass"):
        return "replace_failed"
    import pandas as pd

    frame = pd.read_parquet(parquet_path)
    if list(frame.columns) != PRED_COLUMNS:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "cached columns match the required prediction schema",
                "measured": str(list(frame.columns)),
                "scope": str(parquet_path),
                "evidence": "parquet columns",
                "resume": "stop without overwriting the completed shard",
                "pending": "reuse",
                "optional_fix": "Rewriting the schema in place would replace old evidence.",
                "changes_protocol": True,
            }
        )
    for split in ("validation", "test"):
        got = frame.loc[frame["split"] == split, "unit_id"].astype(str).tolist()
        want = expected_ids(dataset, split)
        if id_hash(got) != id_hash(want) or sidecar.get(f"{split}_id_hash") != id_hash(want):
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "cached unit ids equal the current validation and test ids",
                    "measured": f"{split} cached {len(got)} current {len(want)}",
                    "scope": str(parquet_path),
                    "evidence": "unit_id hash",
                    "resume": "stop without overwriting the completed shard",
                    "pending": "reuse",
                    "optional_fix": "Replacing the ids would change the scored set.",
                    "changes_protocol": True,
                }
            )
    if sidecar.get("mean_repr") != identity["mean_repr"] or sidecar.get("std_repr") != identity["std_repr"]:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "cached scale matches the current train scaler",
                "measured": f"stored {sidecar.get('mean_repr')} {sidecar.get('std_repr')}",
                "scope": str(parquet_path),
                "evidence": "sidecar scale",
                "resume": "stop without overwriting the completed shard",
                "pending": "reuse",
                "optional_fix": "Changing the stored scale would change the protocol.",
                "changes_protocol": True,
            }
        )
    return "reuse"


def verify_cached_metrics(block, method, seed, parquet_path, score_path, mu, encoding, np, pd):
    frame = pd.read_parquet(parquet_path)
    test = frame[frame["split"] == "test"].reset_index(drop=True)
    groups = np.asarray([encoding[str(value)] for value in test["target_group"].tolist()], dtype=int)
    return evaluate_against_accepted(
        block,
        method,
        seed,
        score_path,
        test["y_true_z"].to_numpy(dtype=np.float64),
        test["y_pred_z"].to_numpy(dtype=np.float64),
        groups,
        mu,
        np,
    )


def run_model(job, dataset, scaler, spatial, total_slots, raw_y, torch, np, pd, check_batch: bool):
    block = job["block"]
    method = job["method"]
    seed = int(job["seed"])
    parquet_path, sidecar_path = shard_paths(block, method, seed)
    checkpoint = ROOT / job["checkpoint_path"]
    identity = {
        "block": block,
        "method": method,
        "seed": seed,
        "checkpoint_sha256": sha256_file(checkpoint),
        "mean_repr": repr(scaler["scaler_mean"]),
        "std_repr": repr(scaler["scaler_std"]),
    }
    decision = cache_decision(parquet_path, sidecar_path, identity, dataset)
    encoding = {str(key): int(value) for key, value in job["h_encoding"].items()}
    if decision == "reuse":
        passed, rows, _fresh = verify_cached_metrics(
            block,
            method,
            seed,
            parquet_path,
            job["score_path"],
            job["mu"],
            encoding,
            np,
            pd,
        )
        store_reproduction(rows)
        if not passed:
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "cached predictions reproduce ACCEPTED within 1e-6 + 1e-5*|old|",
                    "measured": "at least one cached metric is outside tolerance",
                    "scope": f"{block} {method} seed{seed}",
                    "evidence": str(REPRO_PATH),
                    "resume": "stop this block; the completed shard was not overwritten",
                    "pending": "baselines and hotspot endpoints for this block",
                    "optional_fix": "Widening the tolerance would change the protocol.",
                    "changes_protocol": True,
                }
            )
        return {"passed": True, "reused": True, "batch_diff": None}
    model = load_checkpoint(checkpoint, dataset.num_spatial, torch)
    test_frame = dataset.atomic_df[dataset.atomic_df["split"] == "test"].reset_index(drop=True)
    val_frame = dataset.atomic_df[dataset.atomic_df["split"] == "validation"].reset_index(drop=True)
    test_ids, test_hours, test_indices = frame_arrays(test_frame, spatial, pd)
    batch_diff = None
    if check_batch:
        batch_diff = batch_agreement(
            model, test_ids, test_hours, test_indices, spatial, total_slots, torch, np
        )
        if batch_diff > 1e-5:
            raise ScientificStop(
                {
                    "stage": "H1",
                    "threshold": "single-row and batch-256 forwards agree within 1e-5",
                    "measured": f"max abs diff {batch_diff}",
                    "scope": f"{block} {method} seed{seed}",
                    "evidence": "first 8 test rows",
                    "resume": "stop this block before writing predictions",
                    "pending": "remaining models and hotspot endpoints",
                    "optional_fix": "Ignoring the batch gap would change the inference implementation.",
                    "changes_protocol": True,
                }
            )
    test_pred = predict_frame(model, test_frame, spatial, total_slots, torch, np)
    val_pred = predict_frame(model, val_frame, spatial, total_slots, torch, np)
    groups = np.asarray(
        [encoding[str(value)] for value in test_frame["target_group"].tolist()],
        dtype=int,
    )
    y_true = test_frame["target_value"].to_numpy(dtype=np.float64)
    passed, rows, _fresh = evaluate_against_accepted(
        block, method, seed, job["score_path"], y_true, test_pred, groups, job["mu"], np
    )
    table = build_prediction_table(
        block,
        method,
        seed,
        dataset,
        {"validation": val_pred, "test": test_pred},
        scaler,
        raw_y,
        np,
        pd,
    )
    table.to_parquet(parquet_path, index=False)
    sidecar = {
        **identity,
        "checkpoint_path": job["checkpoint_path"],
        "checkpoint_bytes": checkpoint.stat().st_size,
        "h_encoding": encoding,
        "splits": ["validation", "test"],
        "n_rows": int(len(table)),
        "validation_id_hash": id_hash(expected_ids(dataset, "validation")),
        "test_id_hash": id_hash(expected_ids(dataset, "test")),
        "reproduction_pass": bool(passed),
        "batch_check_max_abs_diff": batch_diff,
        "created_utc": utc_now(),
    }
    write_json(sidecar_path, sidecar)
    store_reproduction(rows)
    del model
    gc.collect()
    if not passed:
        raise ScientificStop(
            {
                "stage": "H1",
                "threshold": "each ACCEPTED metric within 1e-6 + 1e-5*|old|",
                "measured": "at least one metric is outside tolerance",
                "scope": f"{block} {method} seed{seed}",
                "evidence": str(REPRO_PATH),
                "resume": f"pause {block}; later models on this block were not started",
                "pending": "baselines, baseline selection, and test hotspot endpoints",
                "optional_fix": "Widening the tolerance or dropping the seed would change the protocol.",
                "changes_protocol": True,
            }
        )
    return {"passed": True, "reused": False, "batch_diff": batch_diff}


def asset_jobs(freeze: dict, block: str) -> list[dict]:
    spec = freeze["blocks"][block]
    rows = [
        row
        for row in read_csv(ASSET_PATH)
        if row["block"] == block and row["status"] == "ok"
    ]
    jobs = []
    for method in freeze["methods"]:
        for seed in spec["seeds"]:
            matches = [row for row in rows if row["method"] == method and int(row["seed"]) == int(seed)]
            if len(matches) != 1:
                raise ScientificStop(
                    {
                        "stage": "H1",
                        "threshold": "one ok asset row per method and seed",
                        "measured": f"{block} {method} {seed} rows {len(matches)}",
                        "scope": block,
                        "evidence": str(ASSET_PATH),
                        "resume": "pause this block",
                        "pending": "prediction",
                        "optional_fix": "Dropping the seed would change the protocol.",
                        "changes_protocol": True,
                    }
                )
            row = matches[0]
            jobs.append(
                {
                    "block": block,
                    "method": method,
                    "seed": int(seed),
                    "checkpoint_path": row["checkpoint_path"],
                    "score_path": row["score_path"],
                    "mu": spec["mu"],
                    "h_encoding": spec["h_encoding"],
                }
            )
    return jobs


def cmd_predict(canary: bool, block: str | None) -> int:
    require_start_memory()
    np, pd = import_scientific()
    torch = import_torch()
    require_file(AUDIT_PATH, "predict", "run audit --experiment hotspot")
    audit = read_json(AUDIT_PATH)
    if not audit.get("h0_ready"):
        raise ScientificStop(
            {
                "stage": "predict",
                "threshold": "audit status h0_ready",
                "measured": str(audit.get("problems")),
                "scope": "requested blocks",
                "evidence": str(AUDIT_PATH),
                "resume": "rerun audit after the H0 inputs are ready",
                "pending": "prediction",
                "optional_fix": "Skipping the audit would change the gate.",
                "changes_protocol": True,
            }
        )
    freeze = load_freeze()
    blocks = selected_blocks(freeze, block)
    if not canary:
        require_file(CANARY_PATH, "predict --remaining", "run predict --canary")
        canary_status = read_json(CANARY_PATH)
        for name in blocks:
            if not canary_status.get("blocks", {}).get(name, {}).get("passed"):
                raise ScientificStop(
                    {
                        "stage": "predict --remaining",
                        "threshold": "canary passed for the requested block",
                        "measured": str(canary_status.get("blocks", {}).get(name)),
                        "scope": name,
                        "evidence": str(CANARY_PATH),
                        "resume": "pause this block and continue only a block whose canary passed",
                        "pending": "remaining models on this block",
                        "optional_fix": "Starting the remaining models after a failed canary would skip the gate.",
                        "changes_protocol": True,
                    }
                )
    watch = ResourceWatch("inference", "predict --canary" if canary else "predict --remaining")
    failures = []
    reused = 0
    inferred = 0
    datasets = {}
    try:
        for name in blocks:
            jobs = asset_jobs(freeze, name)
            first_seed = freeze["blocks"][name]["seeds"][0]
            chosen = []
            for job in jobs:
                is_canary = job["method"] == "raven" and int(job["seed"]) == int(first_seed)
                if canary and is_canary:
                    chosen.append(job)
                if not canary and not is_canary:
                    chosen.append(job)
            block_ok = True
            for job in chosen:
                watch.raise_if_over_budget(
                    f"resume at {job['block']} {job['method']} seed{job['seed']}"
                )
                watch.raise_if_memory(
                    f"resume at {job['block']} {job['method']} seed{job['seed']}"
                )
                if name not in datasets:
                    load_cpu = process_cpu_seconds()
                    load_wall = time.perf_counter()
                    try:
                        datasets[name] = load_dataset(name, freeze["blocks"][name], np, pd)
                    except ScientificStop as exc:
                        spent = process_cpu_seconds() - load_cpu
                        watch.failure_cpu += spent
                        watch.charge(
                            spent,
                            time.perf_counter() - load_wall,
                            kind="dataset_load",
                            block=name,
                            failure_cpu_seconds=spent,
                            cache_reuse_models=0,
                        )
                        failures.append(exc.payload)
                        block_ok = False
                        break
                    watch.charge(
                        process_cpu_seconds() - load_cpu,
                        time.perf_counter() - load_wall,
                        kind="dataset_load",
                        block=name,
                        cache_reuse_models=0,
                    )
                dataset, scaler, spatial, total_slots, raw_y = datasets[name]
                model_cpu = process_cpu_seconds()
                model_wall = time.perf_counter()
                try:
                    result = run_model(
                        job,
                        dataset,
                        scaler,
                        spatial,
                        total_slots,
                        raw_y,
                        torch,
                        np,
                        pd,
                        check_batch=canary,
                    )
                except ScientificStop as exc:
                    spent = process_cpu_seconds() - model_cpu
                    watch.failure_cpu += spent
                    watch.charge(
                        spent,
                        time.perf_counter() - model_wall,
                        kind="model",
                        block=name,
                        method=job["method"],
                        seed=int(job["seed"]),
                        failure_cpu_seconds=spent,
                        cache_reuse_models=0,
                    )
                    failures.append(exc.payload)
                    block_ok = False
                    break
                inferred += 0 if result["reused"] else 1
                reused += 1 if result["reused"] else 0
                watch.charge(
                    process_cpu_seconds() - model_cpu,
                    time.perf_counter() - model_wall,
                    kind="model",
                    block=name,
                    method=job["method"],
                    seed=int(job["seed"]),
                    cache_reuse_models=1 if result["reused"] else 0,
                    batch_check_max_abs_diff=result["batch_diff"],
                )
                print(
                    f"{name} {job['method']} seed{job['seed']} "
                    f"{'reused' if result['reused'] else 'inferred'}",
                    flush=True,
                )
            if canary and block_ok:
                current = read_json(CANARY_PATH) if CANARY_PATH.is_file() else {"blocks": {}}
                current["blocks"][name] = {
                    "method": "raven",
                    "seed": int(first_seed),
                    "passed": True,
                }
                current["ended"] = utc_now()
                write_json(CANARY_PATH, current)
    finally:
        datasets.clear()
        gc.collect()
        watch.record(kind="overhead", models_inferred=inferred)
        write_resource_md()
    if failures:
        payload = dict(failures[0])
        payload["measured"] = " | ".join(str(item.get("measured")) for item in failures)
        payload["scope"] = " | ".join(str(item.get("scope")) for item in failures)
        write_failure(payload)
        return 2
    return 0


def parse_observed(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    text = str(value).strip()
    if not text or text == "[]":
        return []
    if text.startswith("["):
        return [str(item) for item in json.loads(text)]
    return [text]


def cmd_baselines(block: str | None) -> int:
    require_start_memory()
    np, pd = import_scientific()
    import pyarrow.parquet as pq

    require_file(REPRO_PATH, "baselines", "finish predict --remaining")
    freeze = load_freeze()
    blocks = selected_blocks(freeze, block)
    rows = reproduction_rows()
    for name in blocks:
        for method in freeze["methods"]:
            for seed in freeze["blocks"][name]["seeds"]:
                metrics = [
                    row
                    for row in rows
                    if row["block"] == name and row["method"] == method and int(row["seed"]) == int(seed)
                ]
                if len(metrics) != len(METRIC_NAMES) or any(row["pass"] != "true" for row in metrics):
                    raise ScientificStop(
                        {
                            "stage": "H2",
                            "threshold": "all five trained methods reproduce ACCEPTED on all 10 seeds",
                            "measured": f"{name} {method} seed{seed} metric rows {len(metrics)}",
                            "scope": name,
                            "evidence": str(REPRO_PATH),
                            "resume": "pause this block before baselines",
                            "pending": "baselines, selection, test endpoints",
                            "optional_fix": "Dropping the seed would change the protocol.",
                            "changes_protocol": True,
                        }
                    )
    watch = ResourceWatch("statistics", "baselines")
    status = {"blocks": {}}
    for name in blocks:
        watch.raise_if_over_budget(f"resume baselines at {name}")
        watch.raise_if_memory(f"resume baselines at {name}")
        spec = freeze["blocks"][name]
        scaler = read_json(PREDICTIONS / name / "scaler.json")
        atomic = pd.read_parquet(
            ROOT / spec["atomic_units"],
            columns=["unit_id", "spatial_id", "absolute_time", "split", "target_value", "target_group"],
        )
        atomic["unit_id"] = atomic["unit_id"].astype(str)
        atomic["spatial_id"] = atomic["spatial_id"].astype(str)
        atomic["target_group"] = atomic["target_group"].astype(str)
        region_by_spatial = atomic.groupby("spatial_id")["target_group"].nunique()
        if int((region_by_spatial > 1).sum()):
            raise ScientificStop(
                {
                    "stage": "H2",
                    "threshold": "each spatial id has one target group",
                    "measured": f"mixed grids {int((region_by_spatial > 1).sum())}",
                    "scope": name,
                    "evidence": spec["atomic_units"],
                    "resume": "stop baseline construction",
                    "pending": "selection and test endpoints",
                    "optional_fix": "Averaging mixed regions would invent a map.",
                    "changes_protocol": True,
                }
            )
        spatial_region = (
            atomic.drop_duplicates("spatial_id").set_index("spatial_id")["target_group"].to_dict()
        )
        stamps = pd.to_datetime(atomic["absolute_time"], utc=True)
        atomic = atomic.assign(
            absolute_time_utc=stamps.map(lambda stamp: pd.Timestamp(stamp).isoformat()),
            date_utc=stamps.dt.strftime("%Y-%m-%d"),
            hour_block=(stamps.dt.hour // 6).astype(int),
        )
        train_units = set(atomic.loc[atomic["split"] == "train", "unit_id"])
        unit_meta = atomic.set_index("unit_id")[
            ["spatial_id", "target_group", "hour_block", "split"]
        ].to_dict(orient="index")
        client = pd.read_parquet(
            ROOT / "data" / "processed" / spec["dataset"] / "client_measurements.parquet",
            columns=["client_id", "unit_id", "potential_measurement"],
        )
        measurement = {
            (str(client_id), str(unit_id)): float(value)
            for client_id, unit_id, value in zip(
                client["client_id"], client["unit_id"], client["potential_measurement"]
            )
            if value is not None and math.isfinite(float(value))
        }
        del client
        scored = atomic[atomic["split"].isin(["validation", "test"])].copy()
        mean = float(scaler["mean"])
        std = float(scaler["std"])
        scored["y_true_phys"] = scored["target_value"].astype(float)
        scored["y_true_z"] = (scored["y_true_phys"] - mean) / std
        seed_status = []
        for seed in spec["seeds"]:
            watch.raise_if_memory(f"resume baselines at {name} seed{seed}")
            event_path = (
                ROOT
                / spec["trace_root"]
                / f"seed{seed}"
                / "training_eventtrace"
                / "events.parquet"
            )
            available = event_path.is_file()
            info = {"seed": int(seed), "events_present": available}
            if not available:
                info["status"] = "unavailable"
                seed_status.append(info)
                continue
            table = pq.read_table(
                event_path, columns=["client_id", "observed_unit_ids", "U"]
            ).to_pandas()
            seen = set()
            per_unit: dict[str, list[float]] = {}
            missing_measurement = 0
            non_train = 0
            for client_id, observed, flag in zip(
                table["client_id"], table["observed_unit_ids"], table["U"]
            ):
                if int(flag) != 1:
                    continue
                for unit_id in parse_observed(observed):
                    if unit_id not in train_units:
                        non_train += 1
                        continue
                    key = (str(client_id), unit_id)
                    if key in seen:
                        continue
                    seen.add(key)
                    value = measurement.get(key)
                    if value is None:
                        missing_measurement += 1
                        continue
                    per_unit.setdefault(unit_id, []).append(value)
            del table
            unit_mean = {unit: float(np.mean(values)) for unit, values in per_unit.items()}
            if not unit_mean:
                info.update(
                    {
                        "status": "unavailable",
                        "missing_measurement": missing_measurement,
                        "non_train_ids": non_train,
                    }
                )
                seed_status.append(info)
                continue
            per_grid: dict[str, list[float]] = {}
            per_region: dict[str, list[float]] = {}
            buckets: dict[tuple[str, int], list[float]] = {}
            for unit, value in unit_mean.items():
                meta = unit_meta[unit]
                per_grid.setdefault(meta["spatial_id"], []).append(value)
                per_region.setdefault(meta["target_group"], []).append(value)
                buckets.setdefault((meta["spatial_id"], int(meta["hour_block"])), []).append(value)
            grid_mean = {key: float(np.mean(values)) for key, values in per_grid.items()}
            region_mean = {key: float(np.mean(values)) for key, values in per_region.items()}
            global_mean = float(np.mean(list(unit_mean.values())))
            enabled = {
                key: float(np.mean(values))
                for key, values in buckets.items()
                if len(values) >= 3
            }

            def spatial_value(spatial_id: str, region: str) -> float:
                if spatial_id in grid_mean:
                    return grid_mean[spatial_id]
                if region in region_mean:
                    return region_mean[region]
                return global_mean

            def cell_value(spatial_id: str, region: str, hour_block: int) -> float:
                bucket = enabled.get((spatial_id, int(hour_block)))
                if bucket is None:
                    return spatial_value(spatial_id, region)
                return bucket

            base = scored[
                [
                    "unit_id",
                    "spatial_id",
                    "absolute_time_utc",
                    "date_utc",
                    "target_group",
                    "split",
                    "hour_block",
                    "y_true_phys",
                    "y_true_z",
                ]
            ].copy()
            spatial_pred = [
                spatial_value(spatial_id, region)
                for spatial_id, region in zip(base["spatial_id"], base["target_group"])
            ]
            cell_pred = [
                cell_value(spatial_id, region, hour)
                for spatial_id, region, hour in zip(
                    base["spatial_id"], base["target_group"], base["hour_block"]
                )
            ]
            for method_name, physical in (
                ("Delivered-SpatialMean", spatial_pred),
                ("Delivered-CellBlockMean", cell_pred),
            ):
                physical_array = np.asarray(physical, dtype=np.float64)
                out = base.copy()
                out["block"] = name
                out["method"] = method_name
                out["seed"] = int(seed)
                out["y_pred_phys"] = physical_array
                out["y_pred_z"] = (physical_array - mean) / std
                path, sidecar = shard_paths(name, method_name, int(seed))
                out[PRED_COLUMNS].to_parquet(path, index=False)
                write_json(
                    sidecar,
                    {
                        "block": name,
                        "method": method_name,
                        "seed": int(seed),
                        "rule": "delivered-history-v1",
                        "events": str(event_path.relative_to(ROOT)).replace("\\", "/"),
                        "n_pairs": len(seen),
                        "n_units": len(unit_mean),
                        "n_grids": len(grid_mean),
                        "n_enabled_buckets": len(enabled),
                        "reproduction_pass": True,
                        "created_utc": utc_now(),
                    },
                )
            info.update(
                {
                    "status": "ready",
                    "n_pairs": len(seen),
                    "n_units": len(unit_mean),
                    "n_grids": len(grid_mean),
                    "n_enabled_buckets": len(enabled),
                    "missing_measurement": missing_measurement,
                    "non_train_ids": non_train,
                }
            )
            seed_status.append(info)
            print(f"{name} baselines seed{seed} units {len(unit_mean)}", flush=True)
        for seed in spec["seeds"]:
            fed_path, _fed_side = shard_paths(name, "fedavg_window", int(seed))
            two_path, _two_side = shard_paths(name, "twostage_hajek", int(seed))
            if not fed_path.is_file() or not two_path.is_file():
                for item in seed_status:
                    if int(item["seed"]) == int(seed):
                        item["ensemble"] = "unavailable"
                continue
            fed = pd.read_parquet(fed_path)
            two = pd.read_parquet(two_path)
            fed = fed.sort_values(["split", "unit_id"]).reset_index(drop=True)
            two = two.sort_values(["split", "unit_id"]).reset_index(drop=True)
            if fed["unit_id"].astype(str).tolist() != two["unit_id"].astype(str).tolist():
                raise ScientificStop(
                    {
                        "stage": "H2",
                        "threshold": "FedAvg and TwoStage-Hajek shards share unit ids",
                        "measured": f"{name} seed{seed}",
                        "scope": name,
                        "evidence": str(fed_path),
                        "resume": "stop ensemble construction",
                        "pending": "selection and test endpoints",
                        "optional_fix": "Dropping mismatched units would change the ensemble.",
                        "changes_protocol": True,
                    }
                )
            out = fed.copy()
            out["method"] = "Fixed-Ensemble"
            out["y_pred_z"] = 0.5 * (
                fed["y_pred_z"].to_numpy(dtype=np.float64) + two["y_pred_z"].to_numpy(dtype=np.float64)
            )
            out["y_pred_phys"] = 0.5 * (
                fed["y_pred_phys"].to_numpy(dtype=np.float64)
                + two["y_pred_phys"].to_numpy(dtype=np.float64)
            )
            path, sidecar = shard_paths(name, "Fixed-Ensemble", int(seed))
            out[PRED_COLUMNS].to_parquet(path, index=False)
            write_json(
                sidecar,
                {
                    "block": name,
                    "method": "Fixed-Ensemble",
                    "seed": int(seed),
                    "rule": "equal-average-v1",
                    "members": ["fedavg_window", "twostage_hajek"],
                    "weights": [0.5, 0.5],
                    "deployment_inferences": 2,
                    "fitted_mixture": False,
                    "reproduction_pass": True,
                    "created_utc": utc_now(),
                },
            )
        status["blocks"][name] = {"seeds": seed_status}
    status["ended"] = utc_now()
    write_json(BASELINE_STATUS, status)
    watch.record(cache_reuse_models=0)
    write_resource_md()
    print("baselines written")
    return 0


def self_check_scores(np) -> None:
    def select(score, spatial, k, higher: bool):
        order = sorted(
            range(len(score)),
            key=lambda index: ((-score[index] if higher else score[index]), spatial[index]),
        )
        return order[:k]

    def capture(y, selected, k):
        kth = np.partition(y, len(y) - k)[len(y) - k]
        n_strict = int(np.sum(y > kth))
        n_tie = int(np.sum(y == kth))
        tie_weight = (k - n_strict) / n_tie
        weights = np.where(y > kth, 1.0, np.where(y == kth, tie_weight, 0.0))
        return float(weights[selected].sum() / k)

    y = np.array([1.0, 3.0, 2.0, 0.0, 4.0])
    spatial = ["a", "b", "c", "d", "e"]
    chosen = select(y, spatial, 1, True)
    assert chosen == [4]
    assert capture(y, chosen, 1) == 1.0
    worst = select(-y, spatial, 1, True)
    assert abs((y[4] - y[worst[0]]) / 1.0 - 4.0) < 1e-12
    tied = select(np.zeros(3), ["b", "a", "c"], 1, True)
    assert tied == [1]
    labels = np.array([5.0, 5.0, 5.0, 1.0, 0.0])
    both = capture(labels, [0, 1], 2)
    mixed = capture(labels, [0, 3], 2)
    assert abs(both - (2.0 / 3.0)) < 1e-12
    assert abs(mixed - (1.0 / 3.0)) < 1e-12
    assert budget_k(11, 1, 5) == 3
    assert budget_k(10, 1, 5) == 2
    assert budget_k(11, 1, 10) == 2
    assert budget_k(10, 3, 10) == 3
    reference = (4.0 - float(np.mean(y))) / 1.0
    assert abs(reference - 2.0) < 1e-12


def score_method_split(block, method, seed, split, mu, scaler, pool_rows, np, pd):
    path, _sidecar = shard_paths(block, method, int(seed))
    if not path.is_file():
        return None
    frame = pd.read_parquet(path)
    part = frame[frame["split"] == split].copy()
    if not np.isfinite(part["y_pred_phys"]).all() or not np.isfinite(part["y_true_phys"]).all():
        raise ScientificStop(
            {
                "stage": "H3",
                "threshold": "predictions and labels are finite",
                "measured": f"{block} {method} seed{seed} {split}",
                "scope": block,
                "evidence": str(path),
                "resume": "stop scoring this method",
                "pending": "aggregation",
                "optional_fix": "Filling nonfinite predictions would change the endpoint.",
                "changes_protocol": True,
            }
        )
    sigma = float(scaler["std"])
    encoding = {str(key): int(value) for key, value in scaler["h_encoding"].items()}
    grouped = {key: value for key, value in part.groupby("absolute_time_utc", sort=False)}
    window_rows = []
    share_rows = []
    for pool_row in pool_rows:
        stamp = pool_row["absolute_time"]
        slot = grouped.get(stamp)
        if slot is None:
            raise ScientificStop(
                {
                    "stage": "H3",
                    "threshold": "every qualified pool time has predictions",
                    "measured": stamp,
                    "scope": f"{block} {method} seed{seed} {split}",
                    "evidence": str(path),
                    "resume": "stop scoring",
                    "pending": "aggregation",
                    "optional_fix": "Dropping the slot would change the protocol.",
                    "changes_protocol": True,
                }
            )
        n_grids = int(pool_row["n_grids"])
        if int(slot["spatial_id"].nunique()) != n_grids or len(slot) != n_grids:
            raise ScientificStop(
                {
                    "stage": "H3",
                    "threshold": "slot rows equal distinct spatial ids and the H0 N",
                    "measured": f"rows {len(slot)} unique {int(slot['spatial_id'].nunique())} pool {n_grids}",
                    "scope": f"{block} {stamp}",
                    "evidence": str(POOL_PATH),
                    "resume": "stop scoring",
                    "pending": "aggregation",
                    "optional_fix": "Collapsing or expanding the slot would change the protocol.",
                    "changes_protocol": True,
                }
            )
        y = slot["y_true_phys"].to_numpy(dtype=np.float64)
        pred = slot["y_pred_phys"].to_numpy(dtype=np.float64)
        spatial = slot["spatial_id"].astype(str).tolist()
        regions = slot["target_group"].astype(str).tolist()
        mean_y = float(np.mean(y))
        for budget in BUDGETS:
            k = budget_k(n_grids, budget["numerator"], budget["denominator"])
            truth_order = sorted(range(n_grids), key=lambda index: (-y[index], spatial[index]))
            pred_order = sorted(range(n_grids), key=lambda index: (-pred[index], spatial[index]))
            truth_set = truth_order[:k]
            pred_set = pred_order[:k]
            gap = float(y[truth_set].sum() - y[pred_set].sum())
            j_value = gap / (k * sigma)
            if j_value < -1e-9:
                raise ScientificStop(
                    {
                        "stage": "H3",
                        "threshold": "J is at least zero because T maximizes the label sum",
                        "measured": repr(j_value),
                        "scope": f"{block} {method} {stamp}",
                        "evidence": "slot score",
                        "resume": "stop before aggregating a negative J",
                        "pending": "decision",
                        "optional_fix": "Changing the sign of J would change the protocol.",
                        "changes_protocol": True,
                    }
                )
            kth = np.partition(y, n_grids - k)[n_grids - k]
            n_strict = int(np.sum(y > kth))
            n_tie = int(np.sum(y == kth))
            tie_weight = (k - n_strict) / n_tie
            weights = np.where(y > kth, 1.0, np.where(y == kth, tie_weight, 0.0))
            capture = float(weights[pred_set].sum() / k)
            window_rows.append(
                {
                    "block": block,
                    "split": split,
                    "seed": int(seed),
                    "method": method,
                    "budget": budget["name"],
                    "primary": str(budget["primary"]).lower(),
                    "time": stamp,
                    "date": pool_row["utc_date"],
                    "N": n_grids,
                    "k": k,
                    "J": j_value,
                    "J_phys": gap / k,
                    "H": capture,
                    "random_J": (float(y[truth_set].sum()) / k - mean_y) / sigma,
                }
            )
            counts = {region: 0 for region in encoding}
            for index in pred_set:
                counts[regions[index]] += 1
            for region, count in counts.items():
                share_rows.append(
                    {
                        "block": block,
                        "split": split,
                        "seed": int(seed),
                        "method": method,
                        "budget": budget["name"],
                        "date": pool_row["utc_date"],
                        "region": region,
                        "share": count / k,
                    }
                )
    test_metrics = None
    if split == "test":
        groups = np.asarray([encoding[str(value)] for value in part["target_group"].tolist()], dtype=int)
        test_metrics = metric_bundle(
            part["y_true_z"].to_numpy(dtype=np.float64),
            part["y_pred_z"].to_numpy(dtype=np.float64),
            groups,
            mu,
            np,
        )
        test_metrics.update({"block": block, "method": method, "seed": int(seed), "split": split})
    return window_rows, share_rows, test_metrics


def qualified_pool(block: str, split: str) -> list[dict]:
    return [
        row
        for row in read_csv(POOL_PATH)
        if row["block"] == block and row["split"] == split and row["included"] == "1"
    ]


def aggregate_windows(window_rows, pd):
    frame = pd.DataFrame(window_rows)
    daily = (
        frame.groupby(["block", "split", "seed", "method", "budget", "date"], as_index=False)
        .agg(
            n_slots=("J", "size"),
            J=("J", "mean"),
            J_phys=("J_phys", "mean"),
            H=("H", "mean"),
            random_J=("random_J", "mean"),
        )
        .sort_values(["block", "split", "method", "budget", "seed", "date"])
    )
    per_seed = daily.groupby(
        ["block", "split", "seed", "method", "budget"], as_index=False
    ).agg(J=("J", "mean"), J_phys=("J_phys", "mean"), H=("H", "mean"), random_J=("random_J", "mean"))
    summary = per_seed.groupby(["block", "split", "method", "budget"], as_index=False).agg(
        n_seeds=("seed", "nunique"),
        J=("J", "mean"),
        J_phys=("J_phys", "mean"),
        H=("H", "mean"),
        random_J=("random_J", "mean"),
    )
    return daily, per_seed, summary


def write_score_bundle(split: str, window_rows, share_rows, metric_rows, pd) -> None:
    daily, _per_seed, summary = aggregate_windows(window_rows, pd)
    prefix = "validation" if split == "validation" else "test"
    write_csv(
        HOTSPOT / f"window_scores_{prefix}.csv",
        window_rows,
        [
            "block",
            "split",
            "seed",
            "method",
            "budget",
            "primary",
            "time",
            "date",
            "N",
            "k",
            "J",
            "J_phys",
            "H",
            "random_J",
        ],
    )
    daily.to_csv(HOTSPOT / f"daily_scores_{prefix}.csv", index=False)
    summary.to_csv(HOTSPOT / f"summary_{prefix}.csv", index=False)
    if share_rows:
        share = pd.DataFrame(share_rows)
        daily_share = share.groupby(
            ["block", "split", "method", "budget", "region", "seed", "date"],
            as_index=False,
        )["share"].mean()
        seed_share = daily_share.groupby(
            ["block", "split", "method", "budget", "region", "seed"],
            as_index=False,
        )["share"].mean()
        collapsed = seed_share.groupby(
            ["block", "split", "method", "budget", "region"],
            as_index=False,
        )["share"].mean()
        collapsed.to_csv(HOTSPOT / f"region_shares_{prefix}.csv", index=False)
    if metric_rows:
        write_csv(
            HOTSPOT / "FULL_SPLIT_METRICS.csv",
            metric_rows,
            [
                "block",
                "split",
                "method",
                "seed",
                "RMSE_mu",
                "MAE_mu",
                "WorstGroupRMSE",
                "WorstGroupRMSE_R0",
                "WorstGroupRMSE_R1",
                "WorstGroupRMSE_R2",
                "WorstGroupRMSE_R3",
            ],
        )


def combine_score_files(pd) -> None:
    frames = []
    daily_frames = []
    summary_frames = []
    share_frames = []
    for prefix in ("validation", "test"):
        path = HOTSPOT / f"window_scores_{prefix}.csv"
        if path.is_file():
            frames.append(pd.read_csv(path))
        daily_path = HOTSPOT / f"daily_scores_{prefix}.csv"
        if daily_path.is_file():
            daily_frames.append(pd.read_csv(daily_path))
        summary_path = HOTSPOT / f"summary_{prefix}.csv"
        if summary_path.is_file():
            summary_frames.append(pd.read_csv(summary_path))
        share_path = HOTSPOT / f"region_shares_{prefix}.csv"
        if share_path.is_file():
            share_frames.append(pd.read_csv(share_path))
    if frames:
        pd.concat(frames, ignore_index=True).to_csv(HOTSPOT / "WINDOW_SCORES.csv", index=False)
    if daily_frames:
        pd.concat(daily_frames, ignore_index=True).to_csv(HOTSPOT / "DAILY_SCORES.csv", index=False)
    if summary_frames:
        pd.concat(summary_frames, ignore_index=True).to_csv(HOTSPOT / "SUMMARY.csv", index=False)
    if share_frames:
        pd.concat(share_frames, ignore_index=True).to_csv(HOTSPOT / "REGION_SHARES.csv", index=False)


def method_names(freeze: dict) -> list[str]:
    return list(freeze["methods"]) + list(SIMPLE_BASELINES)


def score_block(block, split, freeze, np, pd):
    scaler = read_json(PREDICTIONS / block / "scaler.json")
    pool_rows = qualified_pool(block, split)
    mu = freeze["blocks"][block]["mu"]
    windows = []
    shares = []
    metrics = []
    unavailable = []
    for method in method_names(freeze):
        ready_seeds = 0
        for seed in freeze["blocks"][block]["seeds"]:
            scored = score_method_split(
                block, method, int(seed), split, mu, scaler, pool_rows, np, pd
            )
            if scored is None:
                unavailable.append({"method": method, "seed": int(seed)})
                continue
            window_rows, share_rows, metric = scored
            windows.extend(window_rows)
            shares.extend(share_rows)
            if metric is not None:
                metrics.append(metric)
            ready_seeds += 1
        if method in freeze["methods"] and ready_seeds != len(freeze["blocks"][block]["seeds"]):
            raise ScientificStop(
                {
                    "stage": "H3",
                    "threshold": "trained methods have all 10 seeds",
                    "measured": f"{block} {method} ready {ready_seeds}",
                    "scope": block,
                    "evidence": str(PREDICTIONS / block),
                    "resume": "stop scoring",
                    "pending": "decision",
                    "optional_fix": "Scoring a subset of seeds would change the protocol.",
                    "changes_protocol": True,
                }
            )
    return windows, shares, metrics, unavailable


def cmd_select(block: str | None) -> int:
    require_start_memory()
    np, pd = import_scientific()
    self_check_scores(np)
    require_file(BASELINE_STATUS, "select-baseline", "run baselines")
    freeze = load_freeze()
    blocks = selected_blocks(freeze, block)
    watch = ResourceWatch("statistics", "select-baseline --experiment hotspot")
    existing = read_json(SELECTION_PATH) if SELECTION_PATH.is_file() else None
    selection = {"experiment": "hotspot", "selection_split": "validation", "budget": "0.2", "blocks": {}}
    if existing:
        selection = existing
    windows = []
    shares = []
    for name in blocks:
        watch.raise_if_over_budget(f"resume select-baseline at {name}")
        block_windows, block_shares, _metrics, unavailable = score_block(
            name, "validation", freeze, np, pd
        )
        windows.extend(block_windows)
        shares.extend(block_shares)
        _daily, _per_seed, summary = aggregate_windows(block_windows, pd)
        primary = summary[summary["budget"] == "0.2"]
        values = {str(row.method): float(row.J) for row in primary.itertuples(index=False)}
        candidates = [
            method
            for method in method_names(freeze)
            if method != "raven" and method in values
        ]
        missing = [
            method
            for method in method_names(freeze)
            if method != "raven" and method not in values
        ]
        if not candidates:
            raise ScientificStop(
                {
                    "stage": "H2",
                    "threshold": "at least one non-RAVEN validation score",
                    "measured": "no candidate",
                    "scope": name,
                    "evidence": str(BASELINE_STATUS),
                    "resume": "stop before test endpoints",
                    "pending": "hotspot --split test",
                    "optional_fix": "Selecting on the test split would change the protocol.",
                    "changes_protocol": True,
                }
            )
        best = min(values[method] for method in candidates)
        tied = [method for method in candidates if abs(values[method] - best) <= 1e-12]
        order = list(freeze["non_raven_tie_order_unicode"])
        tied.sort(key=lambda method: order.index(method))
        winner = tied[0]
        record = {
            "b_H": winner,
            "J": values[winner],
            "tie_break_applied": len(tied) > 1,
            "tied_methods": tied,
            "validation_J": values,
            "unavailable_non_raven": missing,
            "unavailable_rows": unavailable,
            "fixed_ensemble_deployment_inferences": 2,
        }
        if existing and name in existing.get("blocks", {}):
            old = existing["blocks"][name]
            if old.get("b_H") != winner or abs(float(old.get("J")) - values[winner]) > 1e-12:
                raise ScientificStop(
                    {
                        "stage": "H2",
                        "threshold": "existing baseline selection matches the recomputed validation J",
                        "measured": f"stored {old.get('b_H')} {old.get('J')} new {winner} {values[winner]}",
                        "scope": name,
                        "evidence": str(SELECTION_PATH),
                        "resume": "stop without overwriting the frozen selection",
                        "pending": "test endpoints",
                        "optional_fix": "Replacing b_H after seeing a conflict would change the protocol.",
                        "changes_protocol": True,
                    }
                )
        else:
            selection["blocks"][name] = record
    if not existing:
        selection["frozen_utc"] = utc_now()
        write_json(SELECTION_PATH, selection)
    write_score_bundle("validation", windows, shares, [], pd)
    combine_score_files(pd)
    watch.record(cache_reuse_models=0)
    write_resource_md()
    print("baseline selection frozen")
    return 0


def calendar_dates(block: str, pd) -> list[str]:
    rows = [
        row["utc_date"]
        for row in read_csv(POOL_PATH)
        if row["block"] == block and row["split"] == "test"
    ]
    unique = sorted(set(rows))
    start = datetime.fromisoformat(unique[0])
    end = datetime.fromisoformat(unique[-1])
    span = []
    cursor = start
    while cursor <= end:
        span.append(cursor.date().isoformat())
        cursor += timedelta(days=1)
    return span


def circular_indices(length: int, block: int, rng, np):
    chosen = []
    while len(chosen) < length:
        start = int(rng.integers(0, length))
        for offset in range(block):
            chosen.append((start + offset) % length)
            if len(chosen) == length:
                break
    return np.asarray(chosen, dtype=np.int64)


def bootstrap_d(j_base, j_raven, qualified, block_length: int, np):
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    draws = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    redraws = 0
    attempts = 0
    n_seeds, n_days = j_raven.shape
    completed = 0
    while completed < BOOTSTRAP_DRAWS:
        attempts += 1
        if attempts > BOOTSTRAP_DRAWS * 100:
            break
        day_index = circular_indices(n_days, block_length, rng, np)
        if not qualified[day_index].any():
            redraws += 1
            continue
        seed_index = rng.integers(0, n_seeds, size=n_seeds)
        base = _resample_mean(j_base, seed_index, day_index, np)
        raven = _resample_mean(j_raven, seed_index, day_index, np)
        if not np.isfinite(base) or not np.isfinite(raven):
            redraws += 1
            continue
        draws[completed] = base - raven
        completed += 1
    if completed != BOOTSTRAP_DRAWS:
        raise ScientificStop(
            {
                "stage": "H4",
                "threshold": "10000 finite bootstrap draws",
                "measured": f"completed {completed} redraws {redraws}",
                "scope": "bootstrap",
                "evidence": "circular moving block",
                "resume": "confidence judgment pauses",
                "pending": "decision",
                "optional_fix": "Shortening the bootstrap would change the protocol.",
                "changes_protocol": True,
            }
        )
    return draws, redraws, attempts


def _resample_mean(values, seed_index, day_index, np):
    sampled = values[seed_index][:, day_index]
    mask = np.isfinite(sampled)
    counts = mask.sum(axis=1)
    if np.any(counts == 0):
        return float("nan")
    sums = np.where(mask, sampled, 0.0).sum(axis=1)
    return float(np.mean(sums / counts))


def matrix_from_daily(daily, block, method, budget, calendar, np):
    part = daily[
        (daily["block"] == block) & (daily["method"] == method) & (daily["budget"] == budget)
    ]
    seeds = sorted(int(seed) for seed in part["seed"].unique())
    lookup = {
        (int(row.seed), str(row.date)): float(row.J)
        for row in part.itertuples(index=False)
    }
    matrix = np.full((len(seeds), len(calendar)), np.nan, dtype=np.float64)
    for seed_index, seed in enumerate(seeds):
        for day_index, day in enumerate(calendar):
            if (seed, day) in lookup:
                matrix[seed_index, day_index] = lookup[(seed, day)]
    return matrix


def judge_block(stats: dict) -> dict:
    gates = {
        "assets_and_support": bool(stats["assets_and_support"]),
        "practical_line": bool(stats["practical_line"]),
        "lower_bound": bool(stats["lower_bound_positive"] and not stats["confidence_paused"]),
        "capture": bool(stats["delta_h"] >= -0.02),
        "prediction_cost": bool(
            stats["rmse_cost"] is not None
            and stats["worst_cost"] is not None
            and stats["rmse_cost"] <= 0.05
            and stats["worst_cost"] <= 0.05
        ),
        "beats_all_six": bool(stats["beats_all_six"]),
        "seven_day_median": bool(stats["median_7"] > 0),
    }
    failed = [name for name, ok in gates.items() if not ok]
    if not failed:
        status = "PASS_SCREEN"
    elif not gates["practical_line"]:
        status = "FAIL_SCREEN"
    elif not gates["lower_bound"]:
        status = "INCONCLUSIVE"
    elif gates["practical_line"] and not gates["beats_all_six"] and stats["beats_selected"]:
        status = "BEATS_SELECTED_ONLY"
    else:
        status = "GATES_NOT_MET"
    kind = ""
    if status == "FAIL_SCREEN":
        if stats["relative_defined"] is False:
            kind = "no measurable room"
        elif stats["D"] <= 0:
            kind = "strong baseline has the lower test J"
        else:
            kind = "small gain"
        if not gates["prediction_cost"]:
            kind = kind + "; prediction cost is also outside the guard"
    return {"status": status, "failed_gates": failed, "gates": gates, "fail_kind": kind}


def cmd_hotspot(split: str, block: str | None) -> int:
    if split != "test":
        raise ScientificStop(
            {
                "stage": "H3",
                "threshold": "hotspot --split test",
                "measured": split,
                "scope": "hotspot",
                "evidence": "argument",
                "resume": "run hotspot --split test after baseline selection",
                "pending": "test endpoints",
                "optional_fix": "Scoring another split as the endpoint would change the protocol.",
                "changes_protocol": True,
            }
        )
    require_start_memory()
    np, pd = import_scientific()
    self_check_scores(np)
    require_file(SELECTION_PATH, "hotspot", "run select-baseline --experiment hotspot")
    freeze = load_freeze()
    selection = read_json(SELECTION_PATH)
    blocks = selected_blocks(freeze, block)
    watch = ResourceWatch("statistics", "hotspot --split test")
    windows = []
    shares = []
    metrics = []
    decisions = {"experiment": "hotspot", "blocks": {}, "P2_VS_PROJECTION_UNRESOLVED": True}
    paired_rows = []
    for name in blocks:
        watch.raise_if_over_budget(f"resume hotspot at {name}")
        if name not in selection["blocks"]:
            raise ScientificStop(
                {
                    "stage": "H3",
                    "threshold": "b_H is frozen for this block",
                    "measured": "selection entry absent",
                    "scope": name,
                    "evidence": str(SELECTION_PATH),
                    "resume": "run select-baseline for this block",
                    "pending": "test endpoints",
                    "optional_fix": "Choosing b_H from the test split would change the protocol.",
                    "changes_protocol": True,
                }
            )
        block_windows, block_shares, block_metrics, unavailable = score_block(
            name, "test", freeze, np, pd
        )
        windows.extend(block_windows)
        shares.extend(block_shares)
        metrics.extend(block_metrics)
        daily, per_seed, summary = aggregate_windows(block_windows, pd)
        primary = summary[summary["budget"] == "0.2"].set_index("method")
        b_h = selection["blocks"][name]["b_H"]
        j_r = float(primary.loc["raven", "J"])
        j_b = float(primary.loc[b_h, "J"])
        h_r = float(primary.loc["raven", "H"])
        h_b = float(primary.loc[b_h, "H"])
        d_value = j_b - j_r
        relative = None if j_b <= 1e-8 else d_value / j_b
        practical = relative is not None and relative >= 0.10 and d_value >= 0.01
        metric_frame = pd.DataFrame(block_metrics)
        def mean_metric(method, column):
            return float(metric_frame.loc[metric_frame["method"] == method, column].mean())

        rmse_r = mean_metric("raven", "RMSE_mu")
        rmse_b = mean_metric(b_h, "RMSE_mu")
        worst_r = mean_metric("raven", "WorstGroupRMSE")
        worst_b = mean_metric(b_h, "WorstGroupRMSE")
        rmse_cost = None if rmse_b == 0 else rmse_r / rmse_b - 1.0
        worst_cost = None if worst_b == 0 else worst_r / worst_b - 1.0
        others = [method for method in method_names(freeze) if method != "raven"]
        present = [method for method in others if method in primary.index]
        beats = {method: bool(j_r < float(primary.loc[method, "J"])) for method in present}
        calendar = calendar_dates(name, pd)
        qualified_dates = sorted(
            {
                row["utc_date"]
                for row in read_csv(POOL_PATH)
                if row["block"] == name and row["split"] == "test" and row["included"] == "1"
            }
        )
        qualified = np.asarray([day in set(qualified_dates) for day in calendar], dtype=bool)
        j_raven = matrix_from_daily(daily, name, "raven", "0.2", calendar, np)
        j_base = matrix_from_daily(daily, name, b_h, "0.2", calendar, np)
        if j_raven.shape != j_base.shape or j_raven.shape[0] != 10:
            raise ScientificStop(
                {
                    "stage": "H4",
                    "threshold": "primary comparison has 10 paired seeds",
                    "measured": f"raven {j_raven.shape} b_H {j_base.shape}",
                    "scope": name,
                    "evidence": "seed by date matrix",
                    "resume": "stop the confidence interval for this block",
                    "pending": "decision",
                    "optional_fix": "Dropping a seed would change the protocol.",
                    "changes_protocol": True,
                }
            )
        draws_3, redraw_3, attempts_3 = bootstrap_d(j_base, j_raven, qualified, 3, np)
        draws_7, redraw_7, attempts_7 = bootstrap_d(j_base, j_raven, qualified, 7, np)
        np.save(HOTSPOT / f"bootstrap_primary_{name}_block3.npy", draws_3)
        np.save(HOTSPOT / f"bootstrap_primary_{name}_block7.npy", draws_7)
        q3 = np.quantile(draws_3, [0.0125, 0.025, 0.5, 0.975])
        q7 = np.quantile(draws_7, [0.025, 0.5, 0.975])
        rate_3 = redraw_3 / attempts_3
        stats = {
            "b_H": b_h,
            "J_raven": j_r,
            "J_bH": j_b,
            "H_raven": h_r,
            "H_bH": h_b,
            "D": d_value,
            "G": relative,
            "relative_defined": relative is not None,
            "delta_h": h_r - h_b,
            "rmse_raven": rmse_r,
            "rmse_bH": rmse_b,
            "rmse_cost": rmse_cost,
            "worst_raven": worst_r,
            "worst_bH": worst_b,
            "worst_cost": worst_cost,
            "beats": beats,
            "beats_all_six": len(present) == len(others) and all(beats.values()),
            "beats_selected": bool(beats.get(b_h, False)),
            "unavailable": unavailable,
            "assets_and_support": len(present) == len(others)
            and not selection["blocks"][name]["unavailable_non_raven"]
            and not unavailable,
            "practical_line": practical,
            "lower_9875": float(q3[0]),
            "ci95": [float(q3[1]), float(q3[3])],
            "lower_bound_positive": bool(q3[0] > 0),
            "redraw_rate_3": rate_3,
            "redraws_3": int(redraw_3),
            "attempts_3": int(attempts_3),
            "confidence_paused": bool(rate_3 > 0.01),
            "median_7": float(q7[1]),
            "ci95_7": [float(q7[0]), float(q7[2])],
            "redraw_rate_7": redraw_7 / attempts_7,
            "calendar_days": len(calendar),
            "qualified_dates": len(qualified_dates),
            "random_J": float(primary.loc["raven", "random_J"]),
            "validation_J": selection["blocks"][name]["validation_J"],
        }
        judgment = judge_block(stats)
        stats["judgment"] = judgment
        decisions["blocks"][name] = stats
        paired_rows.append(
            {
                "block": name,
                "role": "primary",
                "method": b_h,
                "budget": "0.2",
                "J_raven": j_r,
                "J_method": j_b,
                "D": d_value,
                "G": "" if relative is None else relative,
                "delta_H": h_r - h_b,
                "rmse_cost": "" if rmse_cost is None else rmse_cost,
                "worst_cost": "" if worst_cost is None else worst_cost,
                "ci95_low": float(q3[1]),
                "ci95_high": float(q3[3]),
                "lower_9875": float(q3[0]),
                "median_7": float(q7[1]),
                "ci95_7_low": float(q7[0]),
                "ci95_7_high": float(q7[2]),
                "confidence_paused": str(rate_3 > 0.01).lower(),
                "screen_status": judgment["status"],
            }
        )
        for method in present:
            if method == b_h:
                continue
            j_m = float(primary.loc[method, "J"])
            h_m = float(primary.loc[method, "H"])
            d_m = j_m - j_r
            rmse_m = mean_metric(method, "RMSE_mu")
            worst_m = mean_metric(method, "WorstGroupRMSE")
            paired_rows.append(
                {
                    "block": name,
                    "role": "secondary",
                    "method": method,
                    "budget": "0.2",
                    "J_raven": j_r,
                    "J_method": j_m,
                    "D": d_m,
                    "G": "" if j_m <= 1e-8 else d_m / j_m,
                    "delta_H": h_r - h_m,
                    "rmse_cost": rmse_r / rmse_m - 1.0,
                    "worst_cost": worst_r / worst_m - 1.0,
                    "ci95_low": "",
                    "ci95_high": "",
                    "lower_9875": "",
                    "median_7": "",
                    "ci95_7_low": "",
                    "ci95_7_high": "",
                    "confidence_paused": "",
                    "screen_status": "",
                }
            )
    write_score_bundle("test", windows, shares, metrics, pd)
    test_daily = HOTSPOT / "daily_scores_test.csv"
    if test_daily.is_file():
        pd.read_csv(test_daily).to_csv(HOTSPOT / "SEED_DATE_JH.csv", index=False)
    combine_score_files(pd)
    write_csv(
        HOTSPOT / "PAIRED_COMPARISONS.csv",
        paired_rows,
        [
            "block",
            "role",
            "method",
            "budget",
            "J_raven",
            "J_method",
            "D",
            "G",
            "delta_H",
            "rmse_cost",
            "worst_cost",
            "ci95_low",
            "ci95_high",
            "lower_9875",
            "median_7",
            "ci95_7_low",
            "ci95_7_high",
            "confidence_paused",
            "screen_status",
        ],
    )
    passed = [
        name
        for name, stats in decisions["blocks"].items()
        if stats["judgment"]["status"] == "PASS_SCREEN"
    ]
    if len(decisions["blocks"]) == 2 and len(passed) == 2:
        decisions["protocol_status"] = "PASS_BOTH_PROTOCOLS"
    elif len(passed) == 1:
        decisions["protocol_status"] = "PASS_ONE_PROTOCOL"
        decisions["passed_block"] = passed[0]
    else:
        decisions["protocol_status"] = "NO_PROTOCOL_PASS"
    decisions["ended"] = utc_now()
    write_json(SCREEN_PATH, _json_ready(decisions))
    watch.record(cache_reuse_models=0)
    write_resource_md()
    print(decisions["protocol_status"])
    return 0


def _json_ready(value):
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if hasattr(value, "item"):
        return _json_ready(value.item())
    return value


def fmt(value, digits=6):
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def cmd_report() -> int:
    np, pd = import_scientific()
    freeze = load_freeze()
    lines = [
        "# City Scanner hotspot screen decision",
        "",
        f"- Written: {utc_now()}",
        "- Driver: `results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py`",
        "- Python: `.venv_new/Scripts/python.exe`",
        "- Experiment: hotspot. The target-shift scheme is outside this plan.",
        "",
        "## Commands",
        "",
        "From `C:/Cursor/raven.mcs`:",
        "",
        "1. `audit --experiment hotspot`",
        "2. `predict --canary`",
        "3. `predict --remaining`",
        "4. `baselines`",
        "5. `select-baseline --experiment hotspot`",
        "6. `hotspot --split test`",
        "7. `report --experiment hotspot`",
        "",
    ]
    if SCREEN_PATH.is_file():
        decision = read_json(SCREEN_PATH)
        lines.append(f"Protocol status: `{decision['protocol_status']}`.")
        lines.append("")
        lines.append("`P2_VS_PROJECTION_UNRESOLVED` remains in force.")
        lines.append("")
        lines.append("## Block results")
        lines.append("")
        for name, stats in decision["blocks"].items():
            judgment = stats["judgment"]
            better = [method for method, flag in stats["beats"].items() if flag]
            worse = [method for method, flag in stats["beats"].items() if not flag]
            lines.extend(
                [
                    f"### {name}",
                    "",
                    f"- Screen status: `{judgment['status']}`",
                    f"- Failed gates: {', '.join(judgment['failed_gates']) if judgment['failed_gates'] else 'none'}",
                    f"- Fail description: {judgment['fail_kind']}",
                    f"- Validation-selected b_H: `{stats['b_H']}`",
                    f"- Test J RAVEN: {fmt(stats['J_raven'])}",
                    f"- Test J b_H: {fmt(stats['J_bH'])}",
                    f"- D: {fmt(stats['D'])}",
                    f"- G: {fmt(stats['G'])}",
                    f"- Capture H RAVEN: {fmt(stats['H_raven'])}",
                    f"- Capture H b_H: {fmt(stats['H_bH'])}",
                    f"- Delta H: {fmt(stats['delta_h'])}",
                    f"- RMSE cost: {fmt(stats['rmse_cost'])}",
                    f"- WorstGroupRMSE cost: {fmt(stats['worst_cost'])}",
                    f"- 3-day 95% interval for D: {fmt(stats['ci95'][0])} to {fmt(stats['ci95'][1])}",
                    f"- 3-day one-sided 98.75% lower bound: {fmt(stats['lower_9875'])}",
                    f"- 7-day median D: {fmt(stats['median_7'])}",
                    f"- 7-day 95% interval: {fmt(stats['ci95_7'][0])} to {fmt(stats['ci95_7'][1])}",
                    f"- Calendar days: {stats['calendar_days']}; qualified dates: {stats['qualified_dates']}",
                    f"- Uniform-random reference J: {fmt(stats['random_J'])}",
                    f"- RAVEN has the smaller test J than: {', '.join(better) if better else 'none'}",
                    f"- These candidates have the smaller test J: {', '.join(worse) if worse else 'none'}",
                    "",
                ]
            )
        lines.extend(["## Five questions", ""])
        status_text = "; ".join(
            f"{name} is {stats['judgment']['status']}" for name, stats in decision["blocks"].items()
        )
        if decision["protocol_status"] == "PASS_BOTH_PROTOCOLS":
            lines.append(
                "Both blocks are `PASS_SCREEN`, so the frozen screen treats both as worth an independent data check."
            )
        elif decision["protocol_status"] == "PASS_ONE_PROTOCOL":
            lines.append(
                f"One block is worth an independent data check under this screen: `{decision.get('passed_block')}`. {status_text}."
            )
        else:
            lines.append(
                f"The gain does not enter an inspection decision. {status_text}. "
                "`PASS_SCREEN` is the status that would mark a block as worth an independent data check."
            )
        lines.append("")
        for name, stats in decision["blocks"].items():
            better = [method for method, flag in stats["beats"].items() if flag]
            worse = [method for method, flag in stats["beats"].items() if not flag]
            lines.append(
                f"On {name}, the validation-selected control is `{stats['b_H']}`. "
                f"Test D is {fmt(stats['D'])} training standard deviations and G is {fmt(stats['G'])}. "
                f"RAVEN has the smaller J than {', '.join(better) if better else 'no listed candidate'}. "
                f"The candidates with the smaller J are {', '.join(worse) if worse else 'none'}."
            )
        lines.extend(
            [
                "",
                "The prediction cost is the full-test RMSE_mu ratio minus one, and the same form for WorstGroupRMSE. "
                "The block results above give both costs against b_H. A negative cost means RAVEN has the smaller full-test error. "
                "The frozen guard is 5 percent on each cost.",
                "",
                "The 10 percent and 30 percent budgets are in `hotspot/SUMMARY.csv`. They do not replace the 20 percent decision.",
                "",
                "The scores use the existing City Scanner test splits. Those splits have already been used in this project, so this screen is an old-test exploration. The two blocks can share raw sampling.",
                "",
                "The same-protocol projection comparison remains open: `P2_VS_PROJECTION_UNRESOLVED`.",
                "",
                "This round does not write the result into the paper and does not start training.",
                "",
            ]
        )
        if decision["protocol_status"] != "PASS_BOTH_PROTOCOLS":
            failed = []
            for name, stats in decision["blocks"].items():
                if stats["judgment"]["status"] != "PASS_SCREEN":
                    failed.append(
                        f"{name}: {stats['judgment']['status']}; gates {stats['judgment']['failed_gates']}; "
                        f"D={stats['D']}; G={stats['G']}; lower={stats['lower_9875']}"
                    )
            write_failure(
                {
                    "stage": "H4",
                    "threshold": "all seven PASS_SCREEN conditions on a block",
                    "measured": " | ".join(failed),
                    "scope": ", ".join(decision["blocks"]),
                    "evidence": str(SCREEN_PATH),
                    "resume": "stop expansion; do not add seeds or retrain inside this protocol",
                    "pending": "independent confirmation only if a later protocol is authorized",
                    "optional_fix": "Relaxing 10%, 0.01 SD, the 98.75% bound, the capture guard, or the cost guard would change the protocol.",
                    "changes_protocol": True,
                }
            )
    else:
        lines.extend(
            [
                "Test endpoints are not in `hotspot/SCREEN_DECISION.json` yet.",
                "",
                "Completed stage files:",
                "",
            ]
        )
        for path in (AUDIT_PATH, CANARY_PATH, REPRO_PATH, BASELINE_STATUS, SELECTION_PATH):
            lines.append(f"- {path.name}: {'present' if path.is_file() else 'absent'}")
        lines.append("")
    if (HOTSPOT / "DAILY_SCORES.csv").is_file() and SCREEN_PATH.is_file():
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            decision = read_json(SCREEN_PATH)
            daily = pd.read_csv(HOTSPOT / "DAILY_SCORES.csv")
            test = daily[daily["split"] == "test"]
            figure, axes = plt.subplots(1, len(decision["blocks"]), figsize=(6 * len(decision["blocks"]), 4), squeeze=False)
            for axis, (name, stats) in zip(axes[0], decision["blocks"].items()):
                part = test[(test["block"] == name) & (test["budget"] == "0.2")]
                raven = part[part["method"] == "raven"].groupby("seed")["J"].mean()
                base = part[part["method"] == stats["b_H"]].groupby("seed")["J"].mean()
                seeds = sorted(set(raven.index) & set(base.index))
                delta = [float(base.loc[seed] - raven.loc[seed]) for seed in seeds]
                axis.bar([str(seed) for seed in seeds], delta)
                axis.axhline(0.0)
                axis.set_title(name)
                axis.set_xlabel("seed")
                axis.set_ylabel("J difference (training SD)")
            figure.tight_layout()
            figure.savefig(HOTSPOT / "fig_paired_j_diff.png", dpi=150)
            plt.close(figure)
            summary = pd.read_csv(HOTSPOT / "SUMMARY.csv")
            summary = summary[summary["split"] == "test"]
            figure, axes = plt.subplots(len(decision["blocks"]), 2, figsize=(10, 4 * len(decision["blocks"])), squeeze=False)
            for row_index, name in enumerate(decision["blocks"]):
                part = summary[summary["block"] == name]
                for method, group in part.groupby("method"):
                    ordered = group.sort_values("budget")
                    axes[row_index, 0].plot(ordered["budget"], ordered["J"], marker="o", label=method)
                    axes[row_index, 1].plot(ordered["budget"], ordered["H"], marker="o", label=method)
                axes[row_index, 0].set_ylabel("J (training SD)")
                axes[row_index, 1].set_ylabel("capture rate H")
                axes[row_index, 0].set_xlabel("budget fraction")
                axes[row_index, 1].set_xlabel("budget fraction")
                axes[row_index, 0].set_title(f"{name} J")
                axes[row_index, 1].set_title(f"{name} H")
                axes[row_index, 1].legend(fontsize=7)
            figure.tight_layout()
            figure.savefig(HOTSPOT / "fig_budget_jh.png", dpi=150)
            plt.close(figure)
            lines.extend(["## Figures", "", "- `hotspot/fig_paired_j_diff.png`", "- `hotspot/fig_budget_jh.png`", ""])
        except Exception as exc:
            lines.extend(["## Figures", "", f"Figure generation stopped: {type(exc).__name__}: {exc}", ""])
    ledger = ledger_rows()
    if ledger:
        lines.extend(["## Stage timing", ""])
        for row in ledger:
            if row.get("kind") == "model":
                continue
            lines.append(
                f"- {row.get('command')} ended {row.get('ended')} "
                f"cpu {fmt(float(row.get('cpu_seconds', 0.0)), 4)}s "
                f"wall {fmt(float(row.get('wall_seconds', 0.0)), 4)}s"
            )
        lines.append("")
    DECISION_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_resource_md()
    print(f"wrote {DECISION_PATH}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="City Scanner hotspot screen")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit")
    audit.add_argument("--experiment", required=True)
    audit.add_argument("--block", choices=["visit", "measured-O"])

    predict = sub.add_parser("predict")
    mode = predict.add_mutually_exclusive_group(required=True)
    mode.add_argument("--canary", action="store_true")
    mode.add_argument("--remaining", action="store_true")
    predict.add_argument("--block", choices=["visit", "measured-O"])

    baselines = sub.add_parser("baselines")
    baselines.add_argument("--block", choices=["visit", "measured-O"])

    select = sub.add_parser("select-baseline")
    select.add_argument("--experiment", required=True)
    select.add_argument("--block", choices=["visit", "measured-O"])

    hotspot = sub.add_parser("hotspot")
    hotspot.add_argument("--split", required=True)
    hotspot.add_argument("--block", choices=["visit", "measured-O"])

    report = sub.add_parser("report")
    report.add_argument("--experiment", required=True)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    experiment = getattr(args, "experiment", "hotspot")
    if experiment != "hotspot":
        print("This driver implements the hotspot plan. target_shift is not defined here.")
        return 2
    try:
        if args.command == "audit":
            return cmd_audit(args.block)
        if args.command == "predict":
            return cmd_predict(args.canary, args.block)
        if args.command == "baselines":
            return cmd_baselines(args.block)
        if args.command == "select-baseline":
            return cmd_select(args.block)
        if args.command == "hotspot":
            return cmd_hotspot(args.split, args.block)
        if args.command == "report":
            return cmd_report()
    except (ScientificStop, ResourceBlock) as exc:
        if isinstance(exc, ResourceBlock):
            payload = {
                "stage": args.command,
                "threshold": "memory and CPU/wall caps in the hotspot plan",
                "measured": exc.measured,
                "scope": getattr(args, "block", None) or "requested blocks",
                "evidence": "process memory and budget ledger",
                "resume": exc.resume,
                "pending": "the batch that had not started",
                "optional_fix": "Raising the cap would change the resource protocol.",
                "changes_protocol": True,
            }
            write_failure(payload)
            write_resource_md()
            print(exc.measured)
            return 3
        write_failure(exc.payload)
        write_resource_md()
        print(exc.payload.get("measured"))
        return 2
    except Exception:
        trace = traceback.format_exc()
        write_failure(
            {
                "stage": args.command,
                "threshold": "the command finishes without an unhandled exception",
                "measured": trace.splitlines()[-1],
                "scope": getattr(args, "block", None) or "requested blocks",
                "evidence": trace,
                "resume": "rerun the same command after the traceback is addressed",
                "pending": "later stages",
                "optional_fix": "The traceback is the observation. A cause beyond it is not stated.",
                "changes_protocol": False,
            }
        )
        print(trace)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
