"""Two-arm active-participation pair. One process, no old runner, no test labels."""

from __future__ import annotations

import csv
import ctypes
import hashlib
import json
import math
import os
import sys
import time
from collections import defaultdict
from ctypes import wintypes
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
import pandas as pd
import torch

ROOT = Path("C:/Cursor/raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.models.common_ndmf import CommonNDMF  # noqa: E402

OUT = Path(__file__).resolve().parent
DATA = ROOT / "data/processed/cityscanner_nyc_p2_measured_o"
P0 = ROOT / "ccf-review-report/active_participation_p0_20261020_1605"
REGIONS = ("region0", "region1", "region2", "region3")
MU = {region: 0.25 for region in REGIONS}
MASTER = 46001
MEAN = 7.235721204740506
STD = 2.5343724212040586
D_PARAMS = 33121
LR = 0.01
ETA = 0.01
LOCAL_STEPS = 2
TOL_P = 1e-10
TOL_F32 = 1e-6
CPU_BUDGET = 600.0
WALL_BUDGET = 1200.0
RSS_CAP = 1610612736
FREE_START = 3221225472
FREE_FLOOR = 2147483648
DATE_START = date(2021, 9, 23)
DATE_END = date(2021, 11, 4)
WARMUP_BOUND = pd.Timestamp("2021-09-22 23:00:00", tz="UTC")
EVAL_CUTOFF = pd.Timestamp("2021-11-05 00:00:00", tz="UTC")
CODE_ID = "57cb283"

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass

CPU0 = time.process_time()
WALL0 = time.perf_counter()
LOW_FREE_SINCE: float | None = None
UNCOMMITTED_CPU = 0.0
UNCOMMITTED_WALL = 0.0


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
        raise OSError("K32GetProcessMemoryInfo failed")
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def budget_ok(stage: str) -> str | None:
    global LOW_FREE_SINCE
    cpu = time.process_time() - CPU0
    wall = time.perf_counter() - WALL0
    rss, peak = rss_pair()
    avail = free_bytes()
    if cpu > CPU_BUDGET or wall > WALL_BUDGET or peak > RSS_CAP:
        return f"INTERRUPTED_P1_RESOURCE stage={stage} cpu={cpu} wall={wall} peak_rss={peak}"
    now = time.perf_counter()
    if avail < FREE_FLOOR:
        if LOW_FREE_SINCE is None:
            LOW_FREE_SINCE = now
        elif now - LOW_FREE_SINCE >= 10.0:
            return f"INTERRUPTED_P1_RESOURCE stage={stage} free={avail}"
    else:
        LOW_FREE_SINCE = None
    return None


def stable_u(*parts: object) -> float:
    raw = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    integer = int.from_bytes(raw[:8], "little")
    return (integer >> 11) * (2.0 ** -53)


def stable_seed(*parts: object) -> int:
    raw = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    value = int.from_bytes(raw[:8], "little") % (2**31 - 1)
    return value if value else 1


def frozen_dates() -> list[date]:
    days = []
    cursor = DATE_START
    while cursor <= DATE_END:
        days.append(cursor)
        cursor += timedelta(days=1)
    if len(days) != 43:
        raise RuntimeError(f"denominator {len(days)}")
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
        if index < 0 or index >= len(inclusion):
            raise RuntimeError(f"systematic index {index} outside 0..{len(inclusion) - 1}")
        chosen.append(index)
    if len(chosen) != len(set(chosen)):
        raise RuntimeError(f"systematic duplicate selection {chosen}")
    return tuple(chosen)


def clone_state(state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    return {name: value.detach().cpu().clone() for name, value in state.items()}


def state_max_abs(left: dict[str, torch.Tensor], right: dict[str, torch.Tensor]) -> float:
    gap = 0.0
    for name in left:
        gap = max(gap, float((left[name].double() - right[name].double()).abs().max()))
    return gap


def pack_delta(delta: dict[str, torch.Tensor], names: list[str]) -> torch.Tensor:
    return torch.cat([delta[name].reshape(-1).double() for name in names])


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fail(status: str, detail: str, extra: dict | None = None) -> None:
    payload = {
        "status": status,
        "detail": detail,
        "cpu_seconds": time.process_time() - CPU0 + UNCOMMITTED_CPU,
        "wall_seconds": time.perf_counter() - WALL0 + UNCOMMITTED_WALL,
        "extra": extra or {},
    }
    write_json(OUT / "FAILURE_STATUS.json", payload)
    (OUT / "FAILURE_REPORT.md").write_text(
        "\n".join(
            [
                f"# {status}",
                "",
                detail,
                "",
                f"进程 CPU 秒：{payload['cpu_seconds']}",
                f"进程 wall 秒：{payload['wall_seconds']}",
                "",
                "已完成并提交的日期见 PROGRESS.json。未写进该文件的当日工作没有提交服务器更新。",
                "不要放宽容忍值、更换抽样器或改学习率后自动续跑。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "detail": detail[:500]}, ensure_ascii=False))
    raise SystemExit(2)


def load_tables():
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
    occupancy["absolute_time"] = pd.to_datetime(occupancy["absolute_time"], utc=True)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    for frame in (occupancy, atomic, clients):
        for column in ("unit_id", "spatial_id", "client_id", "split", "target_group"):
            if column in frame.columns:
                frame[column] = frame[column].astype(str)
    return occupancy, atomic, clients


def build_days(occupancy, atomic, clients):
    train_atomic = atomic.loc[atomic["split"].eq("train")]
    warmup = train_atomic.loc[train_atomic["is_warmup"].map(lambda value: bool(value))]
    if warmup["absolute_time"].max() != WARMUP_BOUND:
        fail("FAIL_P1_IMPLEMENTATION", f"warmup max {warmup['absolute_time'].max()} != frozen bound")
    values = warmup["target_value"].to_numpy(dtype=np.float64)
    if len(values) != 1722 or not np.isfinite(values).all():
        fail("FAIL_P1_IMPLEMENTATION", f"warmup rows {len(values)}")
    mean = float(np.mean(values))
    std = float(np.std(values))
    if abs(mean - MEAN) > 1e-12 or abs(std - STD) > 1e-12:
        fail(
            "FAIL_P1_IMPLEMENTATION",
            f"scaler recomputed mean={mean} std={std}, frozen mean={MEAN} std={STD}",
        )
    vocab = sorted(set(warmup["spatial_id"]))
    if len(vocab) != 118:
        fail("FAIL_P1_IMPLEMENTATION", f"vocab size {len(vocab)}")
    spatial_to_idx = {sid: index for index, sid in enumerate(vocab)}
    atomic_by_unit = atomic.set_index("unit_id", drop=False)
    client_by_unit = clients.set_index("unit_id", drop=False)
    occupancy = occupancy.copy()
    occupancy["utc_day"] = occupancy["absolute_time"].dt.floor("D")
    known_times = occupancy.loc[occupancy["split"].ne("test"), "absolute_time"]
    label_mismatch = 0
    days = []
    expected = pd.read_csv(P0 / "ELIGIBLE_CANDIDATES.csv")
    expected["date"] = expected["date"].astype(str)
    expected["client_id"] = expected["client_id"].astype(str)
    expected_eligible = {
        (row.date, row.client_id): int(row.n_eligible_units)
        for row in expected.itertuples(index=False)
        if bool(row.eligible)
    }
    seen = set()
    inventory_rows = 0
    id_bytes = 0
    for day in frozen_dates():
        stamp = pd.Timestamp(datetime(day.year, day.month, day.day, tzinfo=timezone.utc))
        day_end = stamp + pd.Timedelta(days=1)
        denom = int(known_times.loc[known_times < day_end].nunique())
        observed = occupancy.loc[
            occupancy["utc_day"].eq(stamp) & occupancy["o_observed"].astype(int).eq(1)
        ]
        clients_today = []
        counts = {region: 0 for region in REGIONS}
        mass = {region: 0 for region in REGIONS}
        for client_id, group in observed.groupby("client_id", sort=True):
            inventory_rows += 1
            id_bytes += len(str(client_id).encode("utf-8"))
            reasons = []
            legal = []
            groups = set()
            if str(client_id) not in spatial_to_idx:
                continue
            for record in group.itertuples(index=False):
                unit_id = str(record.unit_id)
                unit_reasons = []
                if str(record.split) != "train" or record.absolute_time <= WARMUP_BOUND:
                    unit_reasons.append("not_legal_window")
                if str(record.target_group) not in MU:
                    unit_reasons.append("unknown_group")
                if unit_id not in atomic_by_unit.index or unit_id not in client_by_unit.index:
                    unit_reasons.append("missing_link")
                else:
                    atomic_row = atomic_by_unit.loc[unit_id]
                    measured = client_by_unit.loc[unit_id]
                    if (
                        str(atomic_row["spatial_id"]) != str(record.spatial_id)
                        or str(atomic_row["split"]) != "train"
                        or str(atomic_row["target_group"]) != str(record.target_group)
                        or int(atomic_row["time_index"]) != int(record.time_index)
                        or bool(atomic_row["is_warmup"])
                        or str(measured["client_id"]) != str(record.client_id)
                        or str(measured["split"]) != "train"
                    ):
                        unit_reasons.append("link_mismatch")
                    target = float(atomic_row["target_value"])
                    label = float(measured["potential_measurement"])
                    if not math.isfinite(target) or not math.isfinite(label):
                        unit_reasons.append("nonfinite")
                    elif target != label:
                        label_mismatch += 1
                        unit_reasons.append("label_mismatch")
                if unit_reasons:
                    for reason in unit_reasons:
                        if reason not in reasons:
                            reasons.append(reason)
                else:
                    atomic_row = atomic_by_unit.loc[unit_id]
                    legal.append(
                        {
                            "unit_id": unit_id,
                            "spatial_index": spatial_to_idx[str(client_id)],
                            "hours": float(record.absolute_time.timestamp()) / 3600.0,
                            "time_index": int(record.time_index),
                            "target": float(atomic_row["target_value"]),
                        }
                    )
                    groups.add(str(record.target_group))
            if len(groups) > 1:
                legal = []
                reasons.append("client_spans_multiple_groups")
            eligible = len(legal) >= 1 and "spatial_absent_from_warmup_vocabulary" not in reasons
            if not eligible:
                continue
            group_name = str(group["target_group"].mode().iloc[0])
            key = (day.isoformat(), str(client_id))
            if key not in expected_eligible or expected_eligible[key] != len(legal):
                fail(
                    "FAIL_P1_IMPLEMENTATION",
                    f"eligibility mismatch {key}: driver={len(legal)} p0={expected_eligible.get(key)}",
                )
            seen.add(key)
            counts[group_name] += 1
            mass[group_name] += len(legal)
            clients_today.append(
                {
                    "client_id": str(client_id),
                    "group": group_name,
                    "units": legal,
                }
            )
        if label_mismatch:
            fail("FAIL_P1_IMPLEMENTATION", f"atomic and client labels differ on {label_mismatch} units")
        k_eligible = sum(counts.values())
        quota_k = 0 if k_eligible == 0 else int(math.ceil(k_eligible / 4.0))
        if k_eligible == 1:
            allocation = {region: (1 if counts[region] else 0) for region in REGIONS}
            mode = "k1_select_all"
            quota_k = 1
        else:
            allocation, mode = allocate_quota(counts, quota_k)
        days.append(
            {
                "date": day,
                "denom": denom,
                "clients": clients_today,
                "counts": counts,
                "mass": mass,
                "k": quota_k,
                "mode": mode,
                "allocation": allocation,
                "inventory_clients": int(observed["client_id"].nunique()),
            }
        )
    if seen != set(expected_eligible):
        fail(
            "FAIL_P1_IMPLEMENTATION",
            f"eligible key mismatch driver={len(seen)} p0={len(expected_eligible)}",
        )
    summary_bytes = inventory_rows * (10 + 1 + 2 + 16) if id_bytes == inventory_rows * 10 else id_bytes + inventory_rows * 19
    return days, spatial_to_idx, summary_bytes, inventory_rows


def prior_and_h(history: dict, clients: list[dict], today: date) -> dict[str, tuple[float, str]]:
    emas = {region: [] for region in REGIONS}
    for client_id, record in history.items():
        age = (today - date.fromisoformat(record["last_date"])).days
        if 0 < age <= 7:
            emas[record["group"]].append(float(record["ema"]))
    priors = {}
    for region in REGIONS:
        priors[region] = max(float(np.median(emas[region])) if emas[region] else 1.0, 1e-12)
    result = {}
    for client in clients:
        record = history.get(client["client_id"])
        prior = priors[client["group"]]
        if record is None:
            result[client["client_id"]] = (prior, "", False)
            continue
        age = (today - date.fromisoformat(record["last_date"])).days
        if age > 7:
            result[client["client_id"]] = (prior, record["last_date"], False)
        else:
            magnitude = float(record["ema"])
            clipped = min(max(magnitude, 0.5 * prior), 2.0 * prior)
            result[client["client_id"]] = (clipped, record["last_date"], True)
    return result


def choose(day: dict, history: dict, arm: str) -> list[dict]:
    today = day["date"]
    info = prior_and_h(history, day["clients"], today)
    rows = []
    if day["k"] <= 0 or not day["clients"]:
        return rows
    if day["mode"] == "fallback_global_quality_pps":
        ordered = sorted(day["clients"], key=lambda item: item["client_id"])
        weights = np.array(
            [MU[item["group"]] * len(item["units"]) / day["mass"][item["group"]] for item in ordered],
            dtype=np.float64,
        )
        inclusion = explored_inclusion(weights, day["k"])
        if abs(float(inclusion.sum()) - day["k"]) > 1e-8:
            raise RuntimeError(f"fallback inclusion sum {inclusion.sum()} != {day['k']}")
        if np.any((inclusion <= 0.0) | (inclusion > 1.0 + 1e-12)):
            raise RuntimeError("fallback inclusion outside (0, 1]")
        chosen = set(systematic_selected(inclusion, stable_u("select", MASTER, today.isoformat(), "GLOBAL")))
        for index, client in enumerate(ordered):
            h_value, when, used = info[client["client_id"]]
            rows.append(
                {
                    "client": client,
                    "a": float(weights[index]),
                    "p": float(inclusion[index]),
                    "I": int(index in chosen),
                    "w": float(weights[index]),
                    "h": h_value,
                    "history_time": when,
                    "used_history": used,
                }
            )
        return rows
    for region in REGIONS:
        members = sorted(
            [item for item in day["clients"] if item["group"] == region],
            key=lambda item: item["client_id"],
        )
        k_g = int(day["allocation"][region])
        if not members or k_g == 0:
            continue
        n_values = np.array([len(item["units"]) for item in members], dtype=np.float64)
        base = n_values / float(day["mass"][region])
        if arm == "B":
            weights = base
        elif arm == "C":
            weights = base * np.array([info[item["client_id"]][0] for item in members], dtype=np.float64)
        else:
            raise RuntimeError(arm)
        inclusion = explored_inclusion(weights, k_g)
        if abs(float(inclusion.sum()) - k_g) > 1e-8:
            raise RuntimeError(f"{today} {region} inclusion sum {float(inclusion.sum())} != {k_g}")
        if np.any((inclusion <= 0.0) | (inclusion > 1.0 + 1e-12)):
            raise RuntimeError(f"{today} {region} inclusion out of range")
        chosen = set(
            systematic_selected(inclusion, stable_u("select", MASTER, today.isoformat(), region))
        )
        if len(chosen) != k_g:
            raise RuntimeError(f"{today} {region} selected {len(chosen)} != {k_g}")
        for index, client in enumerate(members):
            h_value, when, used = info[client["client_id"]]
            rows.append(
                {
                    "client": client,
                    "a": float(MU[region] * len(client["units"]) / day["mass"][region]),
                    "p": float(inclusion[index]),
                    "I": int(index in chosen),
                    "w": float(weights[index]),
                    "h": h_value,
                    "history_time": when,
                    "used_history": used,
                }
            )
    return rows


def local_delta(work: CommonNDMF, snapshot: dict[str, torch.Tensor], client: dict, denom: int, seed: int):
    torch.manual_seed(seed)
    work.load_state_dict(snapshot)
    work.train()
    units = client["units"]
    spatial = torch.tensor([unit["spatial_index"] for unit in units], dtype=torch.long)
    hours = np.array([unit["hours"] for unit in units], dtype=np.float64)
    hour = torch.tensor(hours % 24.0, dtype=torch.float32)
    weekday = torch.tensor((np.floor(hours / 24.0).astype(np.int64) + 3) % 7, dtype=torch.float32)
    trend = torch.tensor(
        np.array([unit["time_index"] for unit in units], dtype=np.float64) / float(denom),
        dtype=torch.float32,
    )
    target = torch.tensor(
        [(unit["target"] - MEAN) / STD for unit in units],
        dtype=torch.float32,
    )
    if int(spatial.max()) >= work.num_spatial or int(trend.shape[0]) != len(units):
        raise RuntimeError("feature contract violated")
    if bool((torch.tensor([unit["time_index"] for unit in units]) >= denom).any()):
        raise RuntimeError("training time index is beyond the causal denominator")
    for _ in range(LOCAL_STEPS):
        work.zero_grad(set_to_none=True)
        prediction = work(spatial, hour, weekday, trend)
        loss = torch.mean((prediction - target) ** 2)
        if not torch.isfinite(loss):
            raise RuntimeError(f"nonfinite loss for {client['client_id']}")
        loss.backward()
        with torch.no_grad():
            for parameter in work.parameters():
                if parameter.grad is not None:
                    parameter.add_(parameter.grad, alpha=-LR)
    delta = {}
    with torch.no_grad():
        current = work.state_dict()
        for name, before in snapshot.items():
            after = current[name].detach()
            if not torch.isfinite(after).all():
                raise RuntimeError(f"nonfinite parameter {name}")
            delta[name] = after.double() - before.detach().double()
    return delta


def aggregate(snapshot: dict[str, torch.Tensor], rows: list[dict], deltas: dict[str, dict]) -> dict[str, torch.Tensor]:
    updated = {}
    for name, before in snapshot.items():
        total = torch.zeros_like(before, dtype=torch.float64)
        for row in rows:
            if row["I"] != 1:
                continue
            if row["p"] <= 0.0:
                raise RuntimeError("inverse probability at nonpositive p")
            total = total + (row["a"] / row["p"]) * deltas[row["client"]["client_id"]][name]
        updated[name] = (before.detach().double() + ETA * total).to(torch.float32)
    return updated


def remember(history: dict, rows: list[dict], deltas: dict, names: list[str], today: date) -> None:
    for row in rows:
        if row["I"] != 1:
            continue
        client = row["client"]
        flat = pack_delta(deltas[client["client_id"]], names)
        magnitude = float(torch.linalg.vector_norm(flat)) / math.sqrt(D_PARAMS)
        previous = history.get(client["client_id"])
        ema = magnitude if previous is None else 0.2 * magnitude + 0.8 * float(previous["ema"])
        history[client["client_id"]] = {
            "ema": ema,
            "last_date": today.isoformat(),
            "group": client["group"],
            "magnitude": magnitude,
        }


def append_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def save_checkpoint(index: int, day: date, states, histories, own_cpu, shared_cpu) -> None:
    path = OUT / "checkpoints" / f"day_{day.isoformat()}.pt"
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "states": states,
            "histories": histories,
            "next_index": index + 1,
            "own_cpu": own_cpu,
            "shared_cpu": shared_cpu,
        },
        path,
    )
    write_json(
        OUT / "PROGRESS.json",
        {
            "completed_through": day.isoformat(),
            "next_index": index + 1,
            "own_cpu": own_cpu,
            "shared_cpu": shared_cpu,
            "uncommitted_cpu": UNCOMMITTED_CPU,
            "uncommitted_wall": UNCOMMITTED_WALL,
            "code_id": CODE_ID,
            "checkpoint": str(path),
        },
    )


def run_arm_day(work, state, history, day, arm, names):
    reason = budget_ok(f"before-{day['date']}-{arm}")
    if reason:
        return reason, None
    cpu_mark = time.process_time()
    wall_mark = time.perf_counter()
    snapshot = clone_state(state)
    rows = choose(day, history, arm)
    deltas = {}
    for row in rows:
        if row["I"] != 1:
            continue
        reason = budget_ok(f"client-{day['date']}-{arm}")
        if reason:
            return reason, None
        client = row["client"]
        deltas[client["client_id"]] = local_delta(
            work,
            snapshot,
            client,
            day["denom"],
            stable_seed("local", MASTER, day["date"].isoformat(), client["client_id"]),
        )
    if state_max_abs(snapshot, state) != 0.0:
        raise RuntimeError("server snapshot changed during local training")
    updated = aggregate(snapshot, rows, deltas)
    step = state_max_abs(updated, snapshot)
    norms = []
    for row in rows:
        if row["I"] == 1:
            norms.append(float(torch.linalg.vector_norm(pack_delta(deltas[row["client"]["client_id"]], names))))
    own = time.process_time() - cpu_mark
    wall = time.perf_counter() - wall_mark
    return None, {
        "rows": rows,
        "state": updated,
        "own_cpu": own,
        "own_wall": wall,
        "step_l2": step,
        "mean_update_l2": float(np.mean(norms)) if norms else 0.0,
        "consumed_units": int(sum(len(row["client"]["units"]) for row in rows if row["I"] == 1)),
        "selected": int(sum(row["I"] for row in rows)),
        "deltas": deltas,
        "snapshot": snapshot,
    }


def score(work, init_state, states, denom: int, names: list[str]) -> dict:
    support = json.loads((OUT / "EVALUATION_SUPPORT.json").read_text(encoding="utf-8"))
    unit_ids = support["evaluation_unit_ids"]
    atomic = pd.read_parquet(
        DATA / "atomic_units.parquet",
        columns=["unit_id", "spatial_id", "absolute_time", "time_index", "split", "target_group", "target_value"],
    )
    atomic = atomic.loc[atomic["split"].astype(str).eq("validation")].copy()
    atomic["unit_id"] = atomic["unit_id"].astype(str)
    atomic["spatial_id"] = atomic["spatial_id"].astype(str)
    atomic["target_group"] = atomic["target_group"].astype(str)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    by_id = atomic.set_index("unit_id", drop=False)
    vocab = {sid: index for index, sid in enumerate(sorted(set(
        pd.read_parquet(
            DATA / "atomic_units.parquet",
            columns=["spatial_id", "split", "is_warmup"],
        ).pipe(lambda frame: frame.loc[
            frame["split"].astype(str).eq("train") & frame["is_warmup"].map(lambda value: bool(value)),
            "spatial_id",
        ].astype(str))
    )))}
    if len(vocab) != 118:
        fail("FAIL_P1_IMPLEMENTATION", "evaluation vocabulary changed")
    records = []
    for unit_id in unit_ids:
        if unit_id not in by_id.index:
            fail("FAIL_P1_IMPLEMENTATION", f"evaluation id missing {unit_id}")
        row = by_id.loc[unit_id]
        spatial = str(row["spatial_id"])
        if spatial not in vocab:
            fail("FAIL_P1_IMPLEMENTATION", f"evaluation spatial outside vocab {unit_id}")
        target = float(row["target_value"])
        if not math.isfinite(target):
            fail("FAIL_P1_IMPLEMENTATION", f"nonfinite evaluation label {unit_id}")
        records.append(
            {
                "unit_id": unit_id,
                "group": str(row["target_group"]),
                "target": target,
                "spatial_index": vocab[spatial],
                "hours": float(row["absolute_time"].timestamp()) / 3600.0,
                "time_index": int(row["time_index"]),
            }
        )
    spatial = torch.tensor([record["spatial_index"] for record in records], dtype=torch.long)
    hours = np.array([record["hours"] for record in records], dtype=np.float64)
    hour = torch.tensor(hours % 24.0, dtype=torch.float32)
    weekday = torch.tensor((np.floor(hours / 24.0).astype(np.int64) + 3) % 7, dtype=torch.float32)
    trend = torch.tensor(
        np.array([record["time_index"] for record in records], dtype=np.float64) / float(denom),
        dtype=torch.float32,
    )

    def predict(state):
        work.load_state_dict(state)
        work.eval()
        with torch.no_grad():
            standardized = work(spatial, hour, weekday, trend).double()
        return standardized * STD + MEAN

    predictions = {
        "B": predict(states["B"]),
        "C": predict(states["C"]),
        "init": predict(init_state),
    }
    truth = torch.tensor([record["target"] for record in records], dtype=torch.float64)
    constant = torch.full_like(truth, MEAN)
    groups = [record["group"] for record in records]
    frame_rows = []
    for index, record in enumerate(records):
        frame_rows.append(
            {
                "unit_id": record["unit_id"],
                "group": record["group"],
                "y_true": float(truth[index]),
                "pred_B": float(predictions["B"][index]),
                "pred_C": float(predictions["C"][index]),
                "pred_init": float(predictions["init"][index]),
                "pred_mean": MEAN,
            }
        )
    pd.DataFrame(frame_rows).to_csv(OUT / "FINAL_PREDICTIONS.csv", index=False)

    def metrics(pred: torch.Tensor) -> dict[str, float]:
        values = {}
        mse_terms = []
        rmses = []
        for region in REGIONS:
            mask = torch.tensor([group == region for group in groups], dtype=torch.bool)
            residual = pred[mask] - truth[mask]
            mse = float(torch.mean(residual ** 2))
            rmse = math.sqrt(mse)
            values[f"MSE_{region}"] = mse
            values[f"RMSE_{region}"] = rmse
            mse_terms.append(0.25 * mse)
            rmses.append(rmse)
        values["RMSE_mu"] = math.sqrt(sum(mse_terms))
        values["WorstGroupRMSE"] = max(rmses)
        standardized = (pred - MEAN) / STD
        standardized_truth = (truth - MEAN) / STD
        std_terms = []
        for region in REGIONS:
            mask = torch.tensor([group == region for group in groups], dtype=torch.bool)
            std_terms.append(0.25 * float(torch.mean((standardized[mask] - standardized_truth[mask]) ** 2)))
        values["RMSE_mu_standardized"] = math.sqrt(sum(std_terms))
        return values

    result = {
        "B": metrics(predictions["B"]),
        "C": metrics(predictions["C"]),
        "init": metrics(predictions["init"]),
        "mean": metrics(constant),
        "n": len(records),
        "frozen_denominator": denom,
    }
    return result


def main() -> None:
    global UNCOMMITTED_CPU, UNCOMMITTED_WALL
    avail = free_bytes()
    if avail < FREE_START:
        fail("INTERRUPTED_P1_RESOURCE", f"free memory {avail} < {FREE_START} before training")
    occupancy, atomic, clients = load_tables()
    days, _spatial, summary_bytes, inventory_rows = build_days(occupancy, atomic, clients)
    torch.manual_seed(MASTER)
    work = CommonNDMF(num_spatial=118, dropout=0.1)
    names = list(work.state_dict().keys())
    count = int(sum(value.numel() for value in work.state_dict().values()))
    if count != D_PARAMS:
        fail("FAIL_P1_IMPLEMENTATION", f"parameter count {count} != {D_PARAMS}")
    init_state = clone_state(work.state_dict())
    states = {"B": clone_state(init_state), "C": clone_state(init_state)}
    histories = {"B": {}, "C": {}}
    shared_cpu = time.process_time() - CPU0
    own_cpu = {"B": 0.0, "C": 0.0}
    own_wall = {"B": 0.0, "C": 0.0}
    start_index = 0
    progress_path = OUT / "PROGRESS.json"
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
        start_index = int(progress["next_index"])
        if start_index > 0:
            checkpoint = torch.load(progress["checkpoint"], map_location="cpu", weights_only=False)
            states = checkpoint["states"]
            histories = checkpoint["histories"]
            own_cpu = checkpoint["own_cpu"]
            shared_cpu = checkpoint["shared_cpu"]
            UNCOMMITTED_CPU = float(progress.get("uncommitted_cpu", 0.0))
            UNCOMMITTED_WALL = float(progress.get("uncommitted_wall", 0.0))
    if free_bytes() < FREE_START and start_index == 0:
        fail("INTERRUPTED_P1_RESOURCE", f"free memory {free_bytes()} < {FREE_START} at training start")
    selection_fields = [
        "date", "arm", "client_id", "group", "n_j", "a_j", "p_j", "I", "w_j", "h_j", "history_time", "used_history",
    ]
    daily_fields = [
        "date", "arm", "K_eligible", "k", "quota_mode", "n_selected", "n_consumed_units",
        "cpu_seconds", "wall_seconds", "rss_bytes", "free_bytes", "server_step_l2", "mean_update_l2",
    ]
    for index in range(start_index, len(days)):
        day = days[index]
        mark_cpu = time.process_time()
        mark_wall = time.perf_counter()
        order = ("B", "C") if index % 2 == 0 else ("C", "B")
        outputs = {}
        try:
            for arm in order:
                reason, output = run_arm_day(work, states[arm], histories[arm], day, arm, names)
                if reason:
                    UNCOMMITTED_CPU += time.process_time() - mark_cpu
                    UNCOMMITTED_WALL += time.perf_counter() - mark_wall
                    save_checkpoint(index - 1, days[index - 1]["date"], states, histories, own_cpu, shared_cpu) if index else None
                    fail(reason.split()[0], reason)
                outputs[arm] = output
        except RuntimeError as exc:
            UNCOMMITTED_CPU += time.process_time() - mark_cpu
            UNCOMMITTED_WALL += time.perf_counter() - mark_wall
            fail("FAIL_P1_IMPLEMENTATION", f"{day['date']}: {exc}")
        if index == 0:
            prob_gap = 0.0
            by_b = {row["client"]["client_id"]: row for row in outputs["B"]["rows"]}
            by_c = {row["client"]["client_id"]: row for row in outputs["C"]["rows"]}
            if set(by_b) != set(by_c):
                fail("FAIL_P1_IMPLEMENTATION", "first-day candidate sets differ")
            selected_b = {key for key, row in by_b.items() if row["I"] == 1}
            selected_c = {key for key, row in by_c.items() if row["I"] == 1}
            for key in by_b:
                prob_gap = max(prob_gap, abs(by_b[key]["p"] - by_c[key]["p"]))
            delta_gap = 0.0
            for key in selected_b:
                delta_gap = max(
                    delta_gap,
                    float(torch.max(torch.abs(
                        pack_delta(outputs["B"]["deltas"][key], names)
                        - pack_delta(outputs["C"]["deltas"][key], names)
                    ))),
                )
            state_gap = state_max_abs(outputs["B"]["state"], outputs["C"]["state"])
            rebuilt = aggregate(outputs["B"]["snapshot"], outputs["B"]["rows"], outputs["B"]["deltas"])
            formula_gap = state_max_abs(rebuilt, outputs["B"]["state"])
            alignment = {
                "date": day["date"].isoformat(),
                "parameter_count": count,
                "vocabulary": 118,
                "scaler_mean": MEAN,
                "scaler_std": STD,
                "local_steps": LOCAL_STEPS,
                "local_lr": LR,
                "server_eta": ETA,
                "probability_gap": prob_gap,
                "same_selection": selected_b == selected_c,
                "delta_gap": delta_gap,
                "state_gap": state_gap,
                "formula_gap": formula_gap,
                "snapshot_unchanged": True,
                "pass": bool(
                    prob_gap <= TOL_P
                    and selected_b == selected_c
                    and delta_gap <= TOL_F32
                    and state_gap <= TOL_F32
                    and formula_gap <= TOL_F32
                ),
            }
            write_json(OUT / "FIRST_DAY_ALIGNMENT.json", alignment)
            if not alignment["pass"]:
                fail("FAIL_P1_IMPLEMENTATION", f"first-day alignment failed: {alignment}")
        for arm in ("B", "C"):
            output = outputs[arm]
            remember(histories[arm], output["rows"], output["deltas"], names, day["date"])
            states[arm] = output["state"]
            own_cpu[arm] += output["own_cpu"]
            own_wall[arm] += output["own_wall"]
            rss, _peak = rss_pair()
            append_rows(
                OUT / "SELECTION_LOG.csv",
                selection_fields,
                [
                    {
                        "date": day["date"].isoformat(),
                        "arm": arm,
                        "client_id": row["client"]["client_id"],
                        "group": row["client"]["group"],
                        "n_j": len(row["client"]["units"]),
                        "a_j": row["a"],
                        "p_j": row["p"],
                        "I": row["I"],
                        "w_j": row["w"],
                        "h_j": row["h"],
                        "history_time": row["history_time"],
                        "used_history": int(row["used_history"]),
                    }
                    for row in output["rows"]
                ],
            )
            append_rows(
                OUT / "DAILY_RUN_LOG.csv",
                daily_fields,
                [
                    {
                        "date": day["date"].isoformat(),
                        "arm": arm,
                        "K_eligible": sum(day["counts"].values()),
                        "k": day["k"],
                        "quota_mode": day["mode"],
                        "n_selected": output["selected"],
                        "n_consumed_units": output["consumed_units"],
                        "cpu_seconds": output["own_cpu"],
                        "wall_seconds": output["own_wall"],
                        "rss_bytes": rss,
                        "free_bytes": free_bytes(),
                        "server_step_l2": output["step_l2"],
                        "mean_update_l2": output["mean_update_l2"],
                    }
                ],
            )
        save_checkpoint(index, day["date"], states, histories, own_cpu, shared_cpu)
        print(
            f"{day['date'].isoformat()} k={day['k']} selected_B={outputs['B']['selected']} selected_C={outputs['C']['selected']}",
            flush=True,
        )
    eval_denom = int(
        (
            occupancy.loc[
                occupancy["split"].astype(str).ne("test")
                & (pd.to_datetime(occupancy["absolute_time"], utc=True) < EVAL_CUTOFF),
                "absolute_time",
            ].nunique()
        )
    )
    scored = score(work, init_state, states, eval_denom, names)
    init_gap_b = state_max_abs(states["B"], init_state)
    init_gap_c = state_max_abs(states["C"], init_state)
    log = pd.read_csv(OUT / "SELECTION_LOG.csv")
    c_rows = log.loc[log["arm"].eq("C")]
    used_fraction = float(c_rows["used_history"].mean()) if len(c_rows) else 0.0
    selected = log.loc[log["I"].astype(int).eq(1), ["date", "arm", "client_id"]]
    differ_days = 0
    for day_name, block in selected.groupby("date"):
        b_set = set(block.loc[block["arm"].eq("B"), "client_id"])
        c_set = set(block.loc[block["arm"].eq("C"), "client_id"])
        if b_set != c_set:
            differ_days += 1
    prob_differ = 0
    for (_day_name, _client), block in log.groupby(["date", "client_id"]):
        if abs(float(block.loc[block["arm"].eq("B"), "p_j"].iloc[0]) - float(block.loc[block["arm"].eq("C"), "p_j"].iloc[0])) > TOL_P:
            prob_differ += 1
    daily = pd.read_csv(OUT / "DAILY_RUN_LOG.csv")
    consumed = {
        arm: int(daily.loc[daily["arm"].eq(arm), "n_consumed_units"].sum())
        for arm in ("B", "C")
    }
    selected_count = {
        arm: int(daily.loc[daily["arm"].eq(arm), "n_selected"].sum())
        for arm in ("B", "C")
    }
    model_bytes = {arm: selected_count[arm] * 132484 * 2 for arm in ("B", "C")}
    logical = {arm: model_bytes[arm] + summary_bytes for arm in ("B", "C")}
    cpu_ledger = {arm: shared_cpu + own_cpu[arm] for arm in ("B", "C")}
    eps_init = 1e-7 * max(1.0, scored["init"]["RMSE_mu"])
    eps_mean = 1e-7 * max(1.0, scored["mean"]["RMSE_mu"])
    learning = all(
        scored[anchor]["RMSE_mu"] - scored[arm]["RMSE_mu"] > (eps_init if anchor == "init" else eps_mean)
        for arm in ("B", "C")
        for anchor in ("init", "mean")
    )
    gain = 1.0 - scored["C"]["RMSE_mu"] / scored["B"]["RMSE_mu"]
    worst_change = scored["C"]["WorstGroupRMSE"] / scored["B"]["WorstGroupRMSE"] - 1.0
    cpu_ratio = cpu_ledger["C"] / cpu_ledger["B"]
    byte_ratio = logical["C"] / logical["B"]
    checks = {
        "gain_ge_0.02": gain >= 0.02,
        "worst_change_le_0.01": worst_change <= 0.01,
        "cpu_ratio_le_1.10": cpu_ratio <= 1.10,
        "byte_ratio_le_1.10": byte_ratio <= 1.10,
        "learning_signal": learning,
        "complete_43": True,
    }
    if not learning:
        status = "INCONCLUSIVE_P1_LEARNING_SETUP"
    elif gain <= 0.0:
        status = "FAIL_P1_NO_PREDICTIVE_GAIN"
    elif gain < 0.02:
        status = "FAIL_P1_EFFECT_TOO_SMALL"
    elif not checks["worst_change_le_0.01"] or not checks["cpu_ratio_le_1.10"] or not checks["byte_ratio_le_1.10"]:
        status = "FAIL_P1_GUARD_OR_COST"
    else:
        status = "PASS_P1_PAIR_AWAIT_REVIEW"
    comparison = {
        "RMSE_mu_B": scored["B"]["RMSE_mu"],
        "RMSE_mu_C": scored["C"]["RMSE_mu"],
        "RMSE_mu_init": scored["init"]["RMSE_mu"],
        "RMSE_mu_mean": scored["mean"]["RMSE_mu"],
        "WorstGroupRMSE_B": scored["B"]["WorstGroupRMSE"],
        "WorstGroupRMSE_C": scored["C"]["WorstGroupRMSE"],
        "gain": gain,
        "worst_change": worst_change,
        "cpu_B": cpu_ledger["B"],
        "cpu_C": cpu_ledger["C"],
        "cpu_ratio": cpu_ratio,
        "logical_bytes_B": logical["B"],
        "logical_bytes_C": logical["C"],
        "byte_ratio": byte_ratio,
        "shared_cpu": shared_cpu,
        "own_cpu_B": own_cpu["B"],
        "own_cpu_C": own_cpu["C"],
        "process_cpu": time.process_time() - CPU0,
        "process_wall": time.perf_counter() - WALL0,
        "history_used_fraction_C": used_fraction,
        "selection_differ_days": differ_days,
        "probability_differ_client_days": prob_differ,
        "init_parameter_l2_gap_B": init_gap_b,
        "init_parameter_l2_gap_C": init_gap_c,
        "status": status,
    }
    for arm in ("B", "C", "init", "mean"):
        for region in REGIONS:
            comparison[f"RMSE_{region}_{arm}"] = scored[arm][f"RMSE_{region}"]
        comparison[f"RMSE_mu_standardized_{arm}"] = scored[arm]["RMSE_mu_standardized"]
    pd.DataFrame([comparison]).to_csv(OUT / "PAIR_COMPARISON.csv", index=False)
    write_json(
        OUT / "RUN_SUMMARY.json",
        {
            "status": status,
            "checks": checks,
            "comparison": comparison,
            "scored": scored,
            "summary_bytes": summary_bytes,
            "inventory_client_days": inventory_rows,
            "selected_count": selected_count,
            "consumed_units": consumed,
            "model_bytes": model_bytes,
            "peak_rss": rss_pair()[1],
            "free_end": free_bytes(),
            "eps_init": eps_init,
            "eps_mean": eps_mean,
        },
    )
    print(json.dumps({"status": status, "gain": gain, "learning": learning}, ensure_ascii=False))


if __name__ == "__main__":
    main()
