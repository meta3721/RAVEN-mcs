"""Active-participation P0 audit. No model, no training, no val/test labels."""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from ctypes import wintypes
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

ROOT = Path("C:/Cursor/raven.mcs")
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data/processed/cityscanner_nyc_p2_measured_o"
REGIONS = ("region0", "region1", "region2", "region3")
MU = {region: 0.25 for region in REGIONS}
TOL = 1e-10
CPU_BUDGET = 120.0
WALL_BUDGET = 300.0
RSS_CAP = 1 << 30
FREE_FLOOR = 2 << 30
DATE_START = date(2021, 9, 23)
DATE_END = date(2021, 11, 4)
WARMUP_BOUND = pd.Timestamp("2021-09-22 23:00:00", tz="UTC")

CPU0 = time.process_time()
WALL0 = time.perf_counter()
LOW_FREE_SINCE: float | None = None


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


class ProcessMemory(ctypes.Structure):
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


def free_bytes() -> int:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(status.ullAvailPhys)


def rss_pair() -> tuple[int, int]:
    counters = ProcessMemory()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.K32GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemory),
        wintypes.DWORD,
    ]
    kernel.K32GetProcessMemoryInfo.restype = wintypes.BOOL
    ok = kernel.K32GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    )
    if not ok:
        raise OSError(f"K32GetProcessMemoryInfo failed: {ctypes.get_last_error()}")
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def guard(stage: str) -> None:
    global LOW_FREE_SINCE
    now = time.perf_counter()
    cpu = time.process_time() - CPU0
    wall = now - WALL0
    rss, peak = rss_pair()
    avail = free_bytes()
    if cpu > CPU_BUDGET or wall > WALL_BUDGET or peak > RSS_CAP:
        raise SystemExit(
            f"INTERRUPTED_P0_RESOURCE stage={stage} cpu={cpu} wall={wall} peak_rss={peak}"
        )
    if avail < FREE_FLOOR:
        if LOW_FREE_SINCE is None:
            LOW_FREE_SINCE = now
        elif now - LOW_FREE_SINCE >= 10.0:
            raise SystemExit(
                f"INTERRUPTED_P0_RESOURCE stage={stage} free={avail} for 10s"
            )
    else:
        LOW_FREE_SINCE = None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frozen_dates() -> list[date]:
    days = []
    cursor = DATE_START
    while cursor <= DATE_END:
        days.append(cursor)
        cursor += timedelta(days=1)
    if len(days) != 43:
        raise RuntimeError(f"frozen denominator is {len(days)}, expected 43")
    return days


def allocate_quota(counts: dict[str, int], k: int) -> tuple[dict[str, int], str]:
    present = [region for region in REGIONS if counts.get(region, 0) > 0]
    allocation = {region: 0 for region in REGIONS}
    if k <= 0 or not present:
        return allocation, "skip"
    if k < len(present):
        return allocation, "fallback_global_quality_pps"
    for region in present:
        allocation[region] = 1
    left = k - len(present)
    present_mu = sum(MU[region] for region in present)
    while left > 0:
        choice = None
        choice_score = None
        for region in present:
            if allocation[region] >= counts[region]:
                continue
            score = k * MU[region] / present_mu - allocation[region]
            better = choice is None or score > choice_score + 1e-15
            tie = (
                choice is not None
                and abs(score - choice_score) <= 1e-15
                and REGIONS.index(region) < REGIONS.index(choice)
            )
            if better or tie:
                choice = region
                choice_score = score
        if choice is None:
            raise RuntimeError("quota allocation exceeded group capacity")
        allocation[choice] += 1
        left -= 1
    return allocation, "group_quota"


def capped_inclusion(weights: np.ndarray, k: int) -> np.ndarray:
    weights = np.asarray(weights, dtype=np.float64)
    size = int(weights.shape[0])
    inclusion = np.zeros(size, dtype=np.float64)
    if k <= 0 or size == 0:
        return inclusion
    if k >= size:
        return np.ones(size, dtype=np.float64)
    free = np.ones(size, dtype=bool)
    left = float(k)
    for _ in range(size):
        active = weights[free]
        scale = float(active.sum())
        if scale <= 0.0:
            inclusion[free] = left / float(free.sum())
            break
        trial = np.zeros(size, dtype=np.float64)
        trial[free] = left / scale * weights[free]
        saturated = free & (trial >= 1.0 - 1e-15)
        if not bool(np.any(saturated)):
            inclusion[free] = trial[free]
            break
        inclusion[saturated] = 1.0
        free[saturated] = False
        left = float(k) - float(inclusion.sum())
        if not bool(np.any(free)):
            break
    return inclusion


def explored_inclusion(weights: np.ndarray, k: int) -> np.ndarray:
    size = int(len(weights))
    if k <= 0 or size == 0:
        return np.zeros(size, dtype=np.float64)
    if k >= size:
        return np.ones(size, dtype=np.float64)
    tilde = capped_inclusion(weights, k)
    return 0.2 * float(k) / float(size) + 0.8 * tilde


def systematic_selected(inclusion: np.ndarray, start: float) -> tuple[int, ...]:
    inclusion = np.asarray(inclusion, dtype=np.float64)
    k = int(round(float(inclusion.sum())))
    if k == 0:
        return ()
    cumulative = np.cumsum(inclusion)
    chosen = []
    for step in range(k):
        target = float(start) + float(step)
        index = int(np.searchsorted(cumulative, target, side="right"))
        chosen.append(index)
    return tuple(chosen)


def design_atoms(inclusion: np.ndarray) -> list[tuple[float, tuple[int, ...]]]:
    inclusion = np.asarray(inclusion, dtype=np.float64)
    k = int(round(float(inclusion.sum())))
    if k == 0:
        return [(1.0, ())]
    cumulative = np.cumsum(inclusion)
    cuts = {0.0}
    for boundary in cumulative:
        for step in range(k):
            cuts.add(float(boundary - step) % 1.0)
    ordered = sorted(cuts)
    unique = [ordered[0]]
    for value in ordered[1:]:
        if value - unique[-1] > 1e-14:
            unique.append(value)
    bounds = unique + [1.0]
    atoms = []
    for left, right in zip(bounds[:-1], bounds[1:]):
        width = right - left
        if width <= 1e-15:
            continue
        probes = (
            left + width * 0.5,
            min(left + 1e-12, right - 1e-15),
            max(right - 1e-12, left + 1e-15),
        )
        selections = {systematic_selected(inclusion, probe) for probe in probes}
        if len(selections) != 1:
            raise RuntimeError(f"systematic atom is not constant on [{left}, {right})")
        atoms.append((width, selections.pop()))
    return atoms


def inclusion_from_atoms(
    atoms: list[tuple[float, tuple[int, ...]]], size: int
) -> np.ndarray:
    estimated = np.zeros(size, dtype=np.float64)
    for width, chosen in atoms:
        for index in chosen:
            estimated[index] += width
    return estimated


def ht_expectation(
    atoms: list[tuple[float, tuple[int, ...]]],
    coefficient: np.ndarray,
    delta: np.ndarray,
    inclusion: np.ndarray,
) -> np.ndarray:
    accumulated = np.zeros(delta.shape[1], dtype=np.float64)
    for width, chosen in atoms:
        term = np.zeros(delta.shape[1], dtype=np.float64)
        for index in chosen:
            if inclusion[index] <= 0.0:
                raise RuntimeError("inverse probability used at a nonpositive inclusion")
            term += coefficient[index] * delta[index] / inclusion[index]
        accumulated += width * term
    return accumulated


def parameter_count(num_spatial: int) -> int:
    embedding = num_spatial * 32
    time_mlp = (5 * 64 + 64) + (64 * 32 + 32)
    head = (128 * 128 + 128) + (128 * 64 + 64) + (64 * 32 + 32) + (32 + 1)
    return embedding + time_mlp + head


def json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(type(value))


def write_json(name: str, payload: dict) -> None:
    (OUT / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=json_default) + "\n",
        encoding="utf-8",
    )


def run_sampling() -> dict:
    guard("sampling")
    tests = []

    def product_atoms(blocks: list[np.ndarray]) -> list[tuple[float, tuple[int, ...]]]:
        pieces = [design_atoms(block) for block in blocks]
        combined = [(1.0, ())]
        offset = 0
        for block, piece in zip(blocks, pieces):
            nxt = []
            for width, chosen in combined:
                for block_width, block_chosen in piece:
                    nxt.append(
                        (
                            width * block_width,
                            chosen + tuple(index + offset for index in block_chosen),
                        )
                    )
            combined = nxt
            offset += len(block)
        return combined

    def finish(name: str, inclusion: np.ndarray, coefficient: np.ndarray, delta: np.ndarray, *, inverse: bool, groups=None, expected_groups=None, blocks=None) -> None:
        atoms = product_atoms(blocks) if blocks is not None else design_atoms(inclusion)
        sizes = [len(chosen) for _, chosen in atoms]
        duplicates = [len(chosen) != len(set(chosen)) for _, chosen in atoms]
        measure = float(sum(width for width, _ in atoms))
        estimated = inclusion_from_atoms(atoms, len(inclusion))
        inclusion_gap = float(np.max(np.abs(estimated - inclusion))) if len(inclusion) else 0.0
        record = {
            "name": name,
            "sample_sizes": sorted(set(sizes)),
            "duplicate_selection": bool(any(duplicates)),
            "design_measure": measure,
            "inclusion": [float(value) for value in inclusion],
            "inclusion_sum": float(inclusion.sum()),
            "inclusion_gap": inclusion_gap,
            "probability_bounds_ok": bool(np.all((inclusion > 0.0) & (inclusion <= 1.0 + 1e-15))) if inverse else bool(np.all(inclusion == 0.0)),
            "inverse_probability_evaluated": inverse,
        }
        if inverse:
            expected = coefficient @ delta
            observed = ht_expectation(atoms, coefficient, delta, inclusion)
            record["ht_gap"] = float(np.max(np.abs(observed - expected)))
        else:
            record["ht_gap"] = None
        if groups is not None:
            mismatches = []
            for _, chosen in atoms:
                counts = {region: 0 for region in REGIONS}
                for index in chosen:
                    counts[groups[index]] += 1
                if counts != expected_groups:
                    mismatches.append(counts)
            record["group_count_mismatch_atoms"] = len(mismatches)
        record["pass"] = (
            record["duplicate_selection"] is False
            and abs(measure - 1.0) <= TOL
            and inclusion_gap <= TOL
            and record["probability_bounds_ok"]
            and (record["ht_gap"] is None or record["ht_gap"] <= TOL)
            and record.get("group_count_mismatch_atoms", 0) == 0
            and (0 not in sizes if inverse else sizes == [0])
        )
        tests.append(record)

    # Select all.
    inclusion = np.ones(4, dtype=np.float64)
    coefficient = np.full(4, 0.25, dtype=np.float64)
    delta = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, -1.0], [-2.0, 0.5]], dtype=np.float64)
    finish("select_all", inclusion, coefficient, delta, inverse=True)

    # Zero budget. No inverse-probability term is formed.
    finish(
        "zero_budget",
        np.zeros(3, dtype=np.float64),
        np.ones(3, dtype=np.float64),
        np.ones((3, 2), dtype=np.float64),
        inverse=False,
    )

    # K=1 is the select-all special case.
    finish(
        "k1_select_all",
        np.ones(1, dtype=np.float64),
        np.array([0.25], dtype=np.float64),
        np.array([[4.0, -3.0]], dtype=np.float64),
        inverse=True,
    )

    # Nonuniform saturated capped PPS plus exploration.
    weights = np.array([1.0, 2.0, 3.0, 100.0], dtype=np.float64)
    inclusion = explored_inclusion(weights, 2)
    coefficient = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float64)
    delta = np.arange(8, dtype=np.float64).reshape(4, 2)
    finish("saturated_nonuniform", inclusion, coefficient, delta, inverse=True)

    # Group quota with a saturated group, then within-group probabilities.
    counts = {"region0": 1, "region1": 1, "region2": 3, "region3": 0}
    allocation, mode = allocate_quota(counts, 4)
    group_of = ["region0", "region1", "region2", "region2", "region2"]
    within = {
        "region0": explored_inclusion(np.array([1.0]), 1),
        "region1": explored_inclusion(np.array([2.0]), 1),
        "region2": explored_inclusion(np.array([1.0, 1.0, 10.0]), allocation["region2"]),
    }
    inclusion = np.concatenate([within["region0"], within["region1"], within["region2"]])
    coefficient = np.array([0.25, 0.25, 0.25 / 12.0, 0.25 / 12.0, 2.5 / 12.0], dtype=np.float64)
    delta = np.array(
        [[1.0, 1.0], [2.0, -1.0], [0.0, 1.0], [1.0, 0.0], [-1.0, 2.0]],
        dtype=np.float64,
    )
    finish(
        "group_quota_redistribution",
        inclusion,
        coefficient,
        delta,
        inverse=True,
        groups=group_of,
        expected_groups=allocation,
        blocks=[within["region0"], within["region1"], within["region2"]],
    )

    # Missing region and k < G_present fallback. Budget stays k=1.
    counts = {"region0": 1, "region1": 1, "region2": 1, "region3": 0}
    allocation, mode = allocate_quota(counts, 1)
    weights = np.array([0.25, 0.25, 0.25], dtype=np.float64)
    inclusion = explored_inclusion(weights, 1)
    finish(
        "missing_group_fallback",
        inclusion,
        weights,
        np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 1.0]], dtype=np.float64),
        inverse=True,
    )
    tests[-1]["quota_mode"] = mode
    tests[-1]["allocation"] = allocation
    tests[-1]["missing_target_mass"] = 0.25
    tests[-1]["pass"] = bool(tests[-1]["pass"] and mode == "fallback_global_quality_pps" and sum(allocation.values()) == 0)

    worst = max(record["inclusion_gap"] for record in tests)
    ht_values = [record["ht_gap"] for record in tests if record["ht_gap"] is not None]
    return {
        "tolerance": TOL,
        "enumeration_clients_max": 5,
        "method": "fixed-size systematic sampling; inclusion checked by exact piecewise measure, not by draw frequency",
        "tests": tests,
        "max_inclusion_gap": worst,
        "max_ht_gap": max(ht_values),
        "pass": all(record["pass"] for record in tests),
    }


def main() -> None:
    guard("start")
    facts: dict = {
        "free_bytes_start": free_bytes(),
        "prediction_results_opened": False,
        "validation_test_target_values_used": False,
    }
    identity = json.loads((DATA / "identity.json").read_text(encoding="utf-8"))
    ingest = json.loads((ROOT / "results_joint_ou/round_v1/INGEST_REPORT.json").read_text(encoding="utf-8"))
    occupancy_hash = sha256_file(DATA / "occupancy_units.parquet")
    facts["identity"] = {
        "identity_data_hash": identity["data_hash"],
        "ingest_data_hash": ingest["data_hash"],
        "identity_occupancy_sha256": identity["occupancy_sha256"],
        "ingest_occupancy_sha256": ingest["occupancy_sha256"],
        "recomputed_occupancy_sha256": occupancy_hash,
        "hash_match": (
            identity["data_hash"] == ingest["data_hash"]
            and identity["occupancy_sha256"] == ingest["occupancy_sha256"] == occupancy_hash
        ),
    }
    guard("loaded-hashes")

    occupancy = pd.read_parquet(
        DATA / "occupancy_units.parquet",
        columns=[
            "unit_id",
            "spatial_id",
            "client_id",
            "absolute_time",
            "time_index",
            "split",
            "target_group",
            "o_observed",
        ],
    )
    atomic = pd.read_parquet(
        DATA / "atomic_units.parquet",
        columns=[
            "unit_id",
            "spatial_id",
            "absolute_time",
            "time_index",
            "split",
            "target_group",
            "target_value",
            "is_warmup",
        ],
    )
    clients = pd.read_parquet(
        DATA / "client_measurements.parquet",
        columns=["client_id", "unit_id", "potential_measurement", "split"],
    )
    guard("loaded-tables")

    occupancy["absolute_time"] = pd.to_datetime(occupancy["absolute_time"], utc=True)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    for frame in (occupancy, atomic, clients):
        for column in frame.columns:
            if str(frame[column].dtype) == "string" or frame[column].dtype == object:
                frame[column] = frame[column].astype(str)

    train_atomic = atomic.loc[atomic["split"].eq("train")].copy()
    warmup = train_atomic.loc[train_atomic["is_warmup"].map(lambda value: bool(value))]
    cutoff = warmup["absolute_time"].max()
    train_end = occupancy.loc[occupancy["split"].eq("train"), "absolute_time"].max()
    facts["time"] = {
        "warmup_rows": int(len(warmup)),
        "warmup_max_utc": str(cutoff),
        "frozen_warmup_bound_utc": str(WARMUP_BOUND),
        "warmup_bound_match": bool(cutoff == WARMUP_BOUND),
        "train_min_utc": str(occupancy.loc[occupancy["split"].eq("train"), "absolute_time"].min()),
        "train_max_utc": str(train_end),
        "validation_min_utc": str(occupancy.loc[occupancy["split"].eq("validation"), "absolute_time"].min()),
        "validation_max_utc": str(occupancy.loc[occupancy["split"].eq("validation"), "absolute_time"].max()),
        "test_min_utc": str(occupancy.loc[occupancy["split"].eq("test"), "absolute_time"].min()),
        "test_max_utc": str(occupancy.loc[occupancy["split"].eq("test"), "absolute_time"].max()),
        "warmup_outside_train": int((atomic["is_warmup"].map(lambda value: bool(value)) & ~atomic["split"].eq("train")).sum()),
    }
    split_times = {
        split: set(occupancy.loc[occupancy["split"].eq(split), "absolute_time"])
        for split in ("train", "validation", "test")
    }
    facts["time"]["split_time_overlap"] = {
        "train_validation": len(split_times["train"] & split_times["validation"]),
        "train_test": len(split_times["train"] & split_times["test"]),
        "validation_test": len(split_times["validation"] & split_times["test"]),
    }

    o0_ids = set(occupancy.loc[occupancy["o_observed"].astype(int).eq(0), "unit_id"])
    atomic_ids = set(atomic["unit_id"])
    client_ids = set(clients["unit_id"])
    train_values = train_atomic["target_value"].to_numpy(dtype=np.float64)
    train_client = clients.loc[clients["split"].eq("train"), "potential_measurement"].to_numpy(dtype=np.float64)
    warmup_values = warmup["target_value"].to_numpy(dtype=np.float64)
    facts["o_and_ids"] = {
        "occupancy_rows": int(len(occupancy)),
        "o1_rows": int(occupancy["o_observed"].astype(int).eq(1).sum()),
        "o0_rows": int(len(o0_ids)),
        "o0_unit_ids_in_atomic": int(len(o0_ids & atomic_ids)),
        "o0_unit_ids_in_client_measurements": int(len(o0_ids & client_ids)),
        "atomic_rows": int(len(atomic)),
        "atomic_unit_duplicates": int(atomic["unit_id"].duplicated().sum()),
        "occupancy_unit_duplicates": int(occupancy["unit_id"].duplicated().sum()),
        "client_pair_duplicates": int(clients.duplicated(["client_id", "unit_id"]).sum()),
        "atomic_not_in_occupancy": int(len(atomic_ids - set(occupancy["unit_id"]))),
        "client_units_not_in_atomic": int(len(client_ids - atomic_ids)),
        "occupancy_client_equals_spatial": bool((occupancy["client_id"] == occupancy["spatial_id"]).all()),
        "client_id_startswith_NYCP": int(clients["client_id"].str.startswith("NYCP").sum()),
        "spatial_id_startswith_NYCP": int(occupancy["spatial_id"].str.startswith("NYCP").sum()),
        "train_atomic_nonfinite": int((~np.isfinite(train_values)).sum()),
        "train_client_nonfinite": int((~np.isfinite(train_client)).sum()),
        "groups": sorted(occupancy["target_group"].unique()),
    }
    facts["scaler_warmup_only"] = {
        "n": int(warmup_values.size),
        "all_finite": bool(np.isfinite(warmup_values).all()),
        "mean": float(np.mean(warmup_values)),
        "std_population": float(np.std(warmup_values)),
        "executed_training": False,
    }
    warmup_spatial = set(warmup["spatial_id"])
    facts["vocabulary"] = {
        "warmup_spatial_ids": len(warmup_spatial),
        "all_atomic_spatial_ids": int(atomic["spatial_id"].nunique()),
        "parameter_count_warmup_vocab": parameter_count(len(warmup_spatial)),
        "parameter_count_all_atomic_vocab": parameter_count(int(atomic["spatial_id"].nunique())),
        "existing_processed_dataset_uses": "all atomic spatial ids, including validation and test",
        "p0_contract_uses": "warmup train spatial ids only",
    }

    atomic_by_unit = atomic.set_index("unit_id", drop=False)
    client_by_unit = clients.set_index("unit_id", drop=False)
    occupancy["utc_day"] = occupancy["absolute_time"].dt.floor("D")
    days = frozen_dates()
    candidate_rows = []
    daily_rows = []
    exclusion_totals: dict[str, int] = defaultdict(int)

    for day in days:
        stamp = pd.Timestamp(datetime(day.year, day.month, day.day, tzinfo=timezone.utc))
        block = occupancy.loc[occupancy["utc_day"].eq(stamp)]
        observed = block.loc[block["o_observed"].astype(int).eq(1)]
        reason_counts: dict[str, int] = defaultdict(int)
        eligible_counts = {region: 0 for region in REGIONS}
        eligible_mass = {region: 0 for region in REGIONS}
        inventory_clients = 0
        for client_id, group in observed.groupby("client_id", sort=True):
            inventory_clients += 1
            reasons = []
            legal_units = []
            times = []
            groups = set()
            if not bool((group["split"] == "train").all()):
                reasons.append("split_not_all_train")
            if bool((group["absolute_time"] <= WARMUP_BOUND).any()):
                reasons.append("at_or_before_warmup_bound")
            if str(client_id).startswith("NYCP"):
                reasons.append("sensor_id_used_as_client")
            if client_id not in warmup_spatial:
                reasons.append("spatial_absent_from_warmup_vocabulary")
            for record in group.itertuples(index=False):
                times.append(record.absolute_time)
                unit_id = str(record.unit_id)
                unit_reasons = []
                if str(record.split) != "train":
                    unit_reasons.append("not_train")
                if record.absolute_time <= WARMUP_BOUND:
                    unit_reasons.append("warmup_time")
                if str(record.target_group) not in MU:
                    unit_reasons.append("unknown_group")
                if unit_id not in atomic_by_unit.index:
                    unit_reasons.append("missing_atomic")
                else:
                    atomic_row = atomic_by_unit.loc[unit_id]
                    if str(atomic_row["spatial_id"]) != str(record.spatial_id):
                        unit_reasons.append("spatial_mismatch")
                    if str(atomic_row["split"]) != "train":
                        unit_reasons.append("atomic_split_mismatch")
                    if str(atomic_row["target_group"]) != str(record.target_group):
                        unit_reasons.append("group_mismatch")
                    if int(atomic_row["time_index"]) != int(record.time_index):
                        unit_reasons.append("time_index_mismatch")
                    if bool(atomic_row["is_warmup"]):
                        unit_reasons.append("atomic_warmup_flag")
                    target = float(atomic_row["target_value"])
                    if not math.isfinite(target):
                        unit_reasons.append("nonfinite_train_target")
                if unit_id not in client_by_unit.index:
                    unit_reasons.append("missing_client_measurement")
                else:
                    measured = client_by_unit.loc[unit_id]
                    if str(measured["client_id"]) != str(record.client_id):
                        unit_reasons.append("client_id_mismatch")
                    if str(measured["split"]) != "train":
                        unit_reasons.append("client_split_mismatch")
                    if str(measured["split"]) == "train":
                        label = float(measured["potential_measurement"])
                        if not math.isfinite(label):
                            unit_reasons.append("nonfinite_train_label")
                if unit_reasons:
                    for reason in unit_reasons:
                        if reason not in reasons:
                            reasons.append(reason)
                else:
                    legal_units.append(unit_id)
                    groups.add(str(record.target_group))
            unique_units = int(group["unit_id"].nunique())
            if len(groups) > 1:
                reasons.append("client_spans_multiple_groups")
                legal_units = []
            eligible = len(legal_units) >= 1 and "spatial_absent_from_warmup_vocabulary" not in reasons
            if not eligible and not reasons:
                reasons.append("no_legal_batch")
            group_name = str(group["target_group"].mode().iloc[0])
            if eligible:
                eligible_counts[group_name] += 1
                eligible_mass[group_name] += len(legal_units)
            for reason in reasons:
                reason_counts[reason] += 1
                exclusion_totals[reason] += 1
            candidate_rows.append(
                {
                    "date": day.isoformat(),
                    "client_id": str(client_id),
                    "group": group_name,
                    "n_inventory_o1": int(len(group)),
                    "n_unique_units": unique_units,
                    "n_eligible_units": int(len(legal_units)) if eligible else 0,
                    "eligible": bool(eligible),
                    "exclusion_reason": "" if eligible else "|".join(reasons),
                    "earliest_time": str(min(times)),
                    "latest_time": str(max(times)),
                    "eligibility_source": "train_o1_unique_cellslot_after_warmup_bound_full_batch",
                }
            )
        k_eligible = int(sum(eligible_counts.values()))
        k = 0 if k_eligible == 0 else int(math.ceil(k_eligible / 4.0))
        g_present = int(sum(value > 0 for value in eligible_counts.values()))
        if k_eligible == 1:
            allocation = {region: (1 if eligible_counts[region] else 0) for region in REGIONS}
            quota_mode = "k1_select_all"
        else:
            allocation, quota_mode = allocate_quota(eligible_counts, k)
        missing_mass = float(sum(MU[region] for region in REGIONS if eligible_mass[region] == 0))
        passed = bool(k_eligible >= 8 and k < k_eligible and k >= g_present)
        discrepancy = []
        if inventory_clients != k_eligible:
            discrepancy.append(f"inventory_minus_eligible={inventory_clients - k_eligible}")
        if quota_mode == "fallback_global_quality_pps":
            discrepancy.append("k_lt_G_present_fallback_global_quality_pps")
        if quota_mode == "skip":
            discrepancy.append("zero_candidate_day")
        if k_eligible == 1:
            discrepancy.append("k1_select_all_fails_k_lt_K")
        for reason, count in sorted(reason_counts.items()):
            discrepancy.append(f"{reason}={count}")
        daily_rows.append(
            {
                "date": day.isoformat(),
                "K_inventory": int(inventory_clients),
                "K_eligible": k_eligible,
                "k": int(k if k_eligible != 1 else 1),
                "G_present": g_present,
                "K_g": json.dumps(eligible_counts, sort_keys=True),
                "k_g": json.dumps(allocation, sort_keys=True),
                "missing_target_mass": missing_mass,
                "selection_condition_pass": passed,
                "discrepancy_reason": "|".join(discrepancy),
            }
        )
        guard(f"day-{day.isoformat()}")

    candidates = pd.DataFrame(candidate_rows)
    daily = pd.DataFrame(daily_rows)
    candidates.to_csv(OUT / "ELIGIBLE_CANDIDATES.csv", index=False)
    daily.to_csv(OUT / "DAILY_FEASIBILITY.csv", index=False)

    eligible = candidates.loc[candidates["eligible"].astype(bool)]
    appearances: dict[str, list[date]] = defaultdict(list)
    for record in eligible.itertuples(index=False):
        appearances[str(record.client_id)].append(date.fromisoformat(record.date))
    prior = 0
    prior_7 = 0
    gaps = []
    for record in eligible.itertuples(index=False):
        current = date.fromisoformat(record.date)
        earlier = [item for item in appearances[str(record.client_id)] if item < current]
        if earlier:
            prior += 1
            gap = (current - max(earlier)).days
            gaps.append(gap)
            if gap <= 7:
                prior_7 += 1
    n_eligible_rows = int(len(eligible))
    facts["eligibility"] = {
        "frozen_days": 43,
        "days_present_in_occupancy": int((daily["K_inventory"] > 0).sum()),
        "days_pass_gate": int(daily["selection_condition_pass"].sum()),
        "days_required": 35,
        "K_eligible_min": int(daily["K_eligible"].min()),
        "K_eligible_median": float(daily["K_eligible"].median()),
        "K_eligible_max": int(daily["K_eligible"].max()),
        "K_inventory_min": int(daily["K_inventory"].min()),
        "K_inventory_median": float(daily["K_inventory"].median()),
        "K_inventory_max": int(daily["K_inventory"].max()),
        "days_four_eligible_groups": int((daily["G_present"] == 4).sum()),
        "exclusion_client_day_counts": dict(exclusion_totals),
        "candidate_rows": int(len(candidates)),
        "eligible_client_days": n_eligible_rows,
    }
    facts["history_upper_bound"] = {
        "eligible_client_days": n_eligible_rows,
        "with_any_earlier_eligible_appearance": prior,
        "fraction_any_earlier": float(prior / n_eligible_rows) if n_eligible_rows else None,
        "with_earlier_eligible_appearance_within_7_days": prior_7,
        "fraction_within_7_days": float(prior_7 / n_eligible_rows) if n_eligible_rows else None,
        "median_gap_days_among_repeats": float(np.median(gaps)) if gaps else None,
        "meaning": "upper bound on history availability; a prior appearance is not a received update",
    }
    facts["sampling"] = run_sampling()
    rss, peak = rss_pair()
    facts["resource"] = {
        "cpu_seconds": time.process_time() - CPU0,
        "wall_seconds": time.perf_counter() - WALL0,
        "rss_bytes": rss,
        "peak_rss_bytes": peak,
        "free_bytes_end": free_bytes(),
        "cpu_budget_seconds": CPU_BUDGET,
        "wall_budget_seconds": WALL_BUDGET,
        "rss_cap_bytes": RSS_CAP,
    }
    write_json("AUDIT_FACTS.json", facts)
    write_json("SAMPLING_CHECKS.json", facts["sampling"])
    print(json.dumps({
        "days_pass_gate": facts["eligibility"]["days_pass_gate"],
        "sampling_pass": facts["sampling"]["pass"],
        "warmup_bound_match": facts["time"]["warmup_bound_match"],
        "hash_match": facts["identity"]["hash_match"],
        "cpu_seconds": facts["resource"]["cpu_seconds"],
        "peak_rss_bytes": peak,
    }, default=json_default))


if __name__ == "__main__":
    main()
