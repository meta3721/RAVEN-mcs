"""Process-tree CPU, RSS, and free-memory accounting for one local process."""

from __future__ import annotations

import ctypes
import os
import time
from ctypes import wintypes

GiB = 1024**3
MIN_FREE_START = int(2.5 * GiB)
MIN_FREE_PAUSE = int(2.0 * GiB)
MIN_FREE_EXIT = int(1.0 * GiB)
MAX_RSS = int(1.5 * GiB)


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


class FileTime(ctypes.Structure):
    _fields_ = [("lo", wintypes.DWORD), ("hi", wintypes.DWORD)]


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


class ProcessEntry(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class AccountingError(RuntimeError):
    pass


def available_bytes() -> int:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    kernel.GlobalMemoryStatusEx.restype = wintypes.BOOL
    if not kernel.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise AccountingError(f"GlobalMemoryStatusEx failed: {ctypes.get_last_error()}")
    return int(status.ullAvailPhys)


def _filetime_seconds(stamp: FileTime) -> float:
    return ((int(stamp.hi) << 32) | int(stamp.lo)) / 10_000_000


def _cpu_of_handle(kernel, handle) -> float:
    created, exited, kernel_time, user_time = FileTime(), FileTime(), FileTime(), FileTime()
    kernel.GetProcessTimes.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
        ctypes.POINTER(FileTime),
    ]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    ok = kernel.GetProcessTimes(
        handle,
        ctypes.byref(created),
        ctypes.byref(exited),
        ctypes.byref(kernel_time),
        ctypes.byref(user_time),
    )
    if not ok:
        raise AccountingError(f"GetProcessTimes failed: {ctypes.get_last_error()}")
    return _filetime_seconds(kernel_time) + _filetime_seconds(user_time)


def _rss_of_handle(kernel, handle) -> tuple[int, int]:
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    if not ok:
        raise AccountingError(f"GetProcessMemoryInfo failed: {ctypes.get_last_error()}")
    return int(counters.PeakWorkingSetSize), int(counters.WorkingSetSize)


def _descendant_pids(root_pid: int) -> list[int]:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32FirstW.restype = wintypes.BOOL
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32NextW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    snapshot = kernel.CreateToolhelp32Snapshot(0x00000002, 0)
    if int(snapshot) == -1 or snapshot is None:
        raise AccountingError(f"process snapshot failed: {ctypes.get_last_error()}")
    children: dict[int, list[int]] = {}
    try:
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(ProcessEntry)
        ok = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        if not ok:
            raise AccountingError(f"Process32FirstW failed: {ctypes.get_last_error()}")
        while ok:
            parent = int(entry.th32ParentProcessID)
            pid = int(entry.th32ProcessID)
            children.setdefault(parent, []).append(pid)
            entry = ProcessEntry()
            entry.dwSize = ctypes.sizeof(ProcessEntry)
            ok = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    found: list[int] = []
    stack = list(children.get(int(root_pid), []))
    seen = {int(root_pid)}
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        found.append(pid)
        stack.extend(children.get(pid, []))
    return found


def process_tree_usage(root_pid: int | None = None) -> dict[str, float | int | bool]:
    """CPU and RSS for the root process plus descendants it can open."""
    root = int(os.getpid() if root_pid is None else root_pid)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    descendants = _descendant_pids(root)
    cpu = _cpu_of_handle(kernel, kernel.GetCurrentProcess())
    peak, rss = _rss_of_handle(kernel, kernel.GetCurrentProcess())
    unreadable: list[int] = []
    query = 0x1000
    for pid in descendants:
        handle = kernel.OpenProcess(query, False, pid)
        if not handle:
            unreadable.append(pid)
            continue
        try:
            cpu += _cpu_of_handle(kernel, handle)
            child_peak, child_rss = _rss_of_handle(kernel, handle)
            peak = max(peak, child_peak)
            rss += child_rss
        finally:
            kernel.CloseHandle(handle)
    return {
        "cpu_seconds": float(cpu),
        "rss_bytes": int(rss),
        "peak_rss_bytes": int(peak),
        "descendant_count": len(descendants),
        "unreadable_descendants": len(unreadable),
        "complete": len(unreadable) == 0,
    }


class StageWatch:
    def __init__(self, stage: str, cpu_budget: float, wall_budget: float):
        self.stage = stage
        self.cpu_budget = float(cpu_budget)
        self.wall_budget = float(wall_budget)
        usage = process_tree_usage()
        if not usage["complete"]:
            raise AccountingError("ACCOUNTING_INCOMPLETE: unreadable child process")
        self.origin_cpu = float(usage["cpu_seconds"])
        self.origin_wall = time.perf_counter()
        self.peak_rss = int(usage["peak_rss_bytes"])
        self.min_available = available_bytes()
        self.max_descendants = int(usage["descendant_count"])

    def sample(self) -> dict[str, float | int | bool]:
        usage = process_tree_usage()
        if not usage["complete"]:
            raise AccountingError("ACCOUNTING_INCOMPLETE: unreadable child process")
        now_free = available_bytes()
        self.peak_rss = max(self.peak_rss, int(usage["rss_bytes"]), int(usage["peak_rss_bytes"]))
        self.min_available = min(self.min_available, now_free)
        self.max_descendants = max(self.max_descendants, int(usage["descendant_count"]))
        cpu = float(usage["cpu_seconds"]) - self.origin_cpu
        wall = time.perf_counter() - self.origin_wall
        return {
            "cpu_seconds": cpu,
            "wall_seconds": wall,
            "remaining_cpu": self.cpu_budget - cpu,
            "remaining_wall": self.wall_budget - wall,
            "rss_bytes": int(usage["rss_bytes"]),
            "peak_rss_bytes": self.peak_rss,
            "available_bytes": now_free,
            "min_available_bytes": self.min_available,
            "descendant_count": int(usage["descendant_count"]),
            "complete": True,
        }

    def raise_for_limits(self) -> dict[str, float | int | bool]:
        sample = self.sample()
        if int(sample["available_bytes"]) < MIN_FREE_EXIT or int(sample["rss_bytes"]) > MAX_RSS:
            raise AccountingError(
                "RESOURCE_EXIT: "
                f"available={sample['available_bytes']} rss={sample['rss_bytes']}"
            )
        if int(sample["available_bytes"]) < MIN_FREE_PAUSE:
            raise AccountingError(
                "RESOURCE_PAUSE: "
                f"available={sample['available_bytes']} below {MIN_FREE_PAUSE}"
            )
        if float(sample["cpu_seconds"]) > self.cpu_budget or float(sample["wall_seconds"]) > self.wall_budget:
            raise AccountingError(
                "RESOURCE_BUDGET: "
                f"cpu={sample['cpu_seconds']:.3f}/{self.cpu_budget:.0f} "
                f"wall={sample['wall_seconds']:.3f}/{self.wall_budget:.0f}"
            )
        return sample


def require_start_memory() -> int:
    free = available_bytes()
    if free < MIN_FREE_EXIT:
        raise AccountingError(
            f"RESOURCE_EXIT: available memory {free} bytes is below {MIN_FREE_EXIT}"
        )
    if free < MIN_FREE_START:
        raise AccountingError(
            f"RESOURCE_PAUSE: available memory {free} bytes is below {MIN_FREE_START}"
        )
    return free
