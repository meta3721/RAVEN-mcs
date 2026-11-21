"""P0 redo: relink public reference rows and freeze the evaluation panel.

No model is fit. No RMSE, ContrastMAE, gain, or interval is written.
P1 is not implemented and is not run.
"""
import csv
import hashlib
import io
import json
import os
import shutil
import statistics
import sys
import time
import traceback
import zipfile
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import ctypes
from ctypes import wintypes

ROOT = Path(__file__).resolve().parent
SOURCE_ZIP = Path(r"C:\Users\szr\Desktop\record\1\dataset_dense_reference_evidence\epa_purpleair_2021.zip")
CACHE = Path(r"C:\Cursor\raven.mcs\results_targeted_reference_calibration\source_cache_20261022")
EPA_88101 = CACHE / "daily_88101_2019.zip"
EPA_88502 = CACHE / "daily_88502_2019.zip"
SITE_MAP_SRC = Path(
    r"C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration"
    r"\p0_p1_20261022_161223\site_map.csv"
)
EXPECTED_HASH = {
    EPA_88101.name: "88B9B0B1BBD0C7545FFC07959A5ECBD4C6FBE951C67EA648CEF70CAFE956AF53",
    EPA_88502.name: "1DCC4D3AEB71C1DD62C315CA846915B75F685F07B5BADBAA21FA77C0F28C2C4D",
}
LIMIT_BYTES = int(1.5 * 2**30)
WINDOW = ("2019-01-26", "2019-06-28")
SPLITS = (
    ("D_fit", "2019-01-26", "2019-02-22", "D"),
    ("D_tune", "2019-02-23", "2019-03-08", "D"),
    ("V", "2019-03-09", "2019-04-05", "V"),
    ("A", "2019-04-06", "2019-05-03", "A"),
    ("T", "2019-05-04", "2019-06-28", "T"),
)
SPLIT_BOUNDS = {name: (lo, hi) for name, lo, hi, _period in SPLITS}
VALUE_SPLITS = {"D_fit", "D_tune", "V"}
SUPPORT = {"D": 20, "V": 10, "A": 10, "T": 20, "D_fit": 1, "D_tune": 1}
MISSING = {"", "NA"}
INSPECTION_CPU = (
    {"stage": "P0_redo_inspect_header", "cpu_s": 0.125, "wall_s": 0.127276},
    {"stage": "P0_redo_inspect_methods", "cpu_s": 0.125, "wall_s": 0.122552},
)
PRIOR_LEDGER_LINES = [
    '{"stage": "P0", "script": "inspect_source.py", "log": "P0_1_inspect_source.log", "cpu_s": 2.0, "worker_cpu_s": 1.75, "wall_s": 8.281000000002678, "peak_rss_bytes": 175185920, "exit_code": 0, "pause_reason": null, "timestamp": "2026-10-22T16:19:52", "meter": "50ms tree sampling + worker exit CPU + Windows peak working set; monitor CPU included"}',
    '{"stage": "P0", "script": "prepare_data.py", "log": "P0_2_prepare_data.log", "cpu_s": 0.9375, "worker_cpu_s": 0.875, "wall_s": 1.1559999999881256, "peak_rss_bytes": 100204544, "exit_code": 0, "pause_reason": null, "timestamp": "2026-10-22T16:20:08", "meter": "50ms tree sampling + worker exit CPU + Windows peak working set; monitor CPU included"}',
    '{"stage": "P0", "script": "explain_p0_failure.py", "log": "P0_3_explain_p0_failure.log", "cpu_s": 0.46875, "worker_cpu_s": 0.453125, "wall_s": 0.7339999999967404, "peak_rss_bytes": 112095232, "exit_code": 0, "pause_reason": null, "timestamp": "2026-10-22T16:22:15", "meter": "50ms tree sampling + worker exit CPU + Windows peak working set; monitor CPU included"}',
    '{"stage":"P0_prior_inherited","cpu_s":3.40625,"note":"Metered CPU from p0_p1_20261022_161223. Not remeasured and not zeroed. This line repeats the sum of the three lines above and is not added again.","download":false}',
    '{"stage":"P0_identity_extract_and_match","cpu_s":3.96875,"wall_s":4.218,"min_available_bytes_during_epa_scan":1629421568,"epa_rows_scanned":891974,"epa_rows_kept":13461,"note":"process_time of extract_and_match_dfit.py. Peak RSS was not instrumented."}',
    '{"stage":"P0_identity_linkage_table","cpu_s":0.15625,"wall_s":0.156,"available_bytes_end":1960374272,"note":"process_time of build_linkage.py."}',
    '{"stage":"download_not_cpu","cpu_s":0,"wall_s":16.702,"note":"Single download of daily_88101_2019.zip and daily_88502_2019.zip. Not counted as model CPU."}',
]


class ResourcePause(RuntimeError):
    pass


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_uint64),
        ("ullAvailPhys", ctypes.c_uint64),
        ("ullTotalPageFile", ctypes.c_uint64),
        ("ullAvailPageFile", ctypes.c_uint64),
        ("ullTotalVirtual", ctypes.c_uint64),
        ("ullAvailVirtual", ctypes.c_uint64),
        ("ullAvailExtendedVirtual", ctypes.c_uint64),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
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


_KERNEL = ctypes.WinDLL("kernel32", use_last_error=True)
_MEM_STATUS = _KERNEL.GlobalMemoryStatusEx
_MEM_STATUS.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
_MEM_STATUS.restype = wintypes.BOOL
_RSS = _KERNEL.K32GetProcessMemoryInfo
_RSS.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD]
_RSS.restype = wintypes.BOOL
_PROCESS = _KERNEL.GetCurrentProcess()


def available_bytes():
    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(status)
    if not _MEM_STATUS(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(status.ullAvailPhys)


def rss_bytes():
    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    if not _RSS(_PROCESS, ctypes.byref(counters), counters.cb):
        raise OSError("K32GetProcessMemoryInfo failed: " + str(ctypes.get_last_error()))
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


class Guard:
    def __init__(self):
        self.low_since = None
        self.peak_rss = 0
        self.min_available = None

    def check(self):
        avail = available_bytes()
        working, peak = rss_bytes()
        self.peak_rss = max(self.peak_rss, working, peak)
        if self.min_available is None or avail < self.min_available:
            self.min_available = avail
        if self.peak_rss > LIMIT_BYTES:
            raise ResourcePause("process RSS " + str(self.peak_rss) + " exceeds 1.5 GiB")
        now = time.monotonic()
        if avail < LIMIT_BYTES:
            if self.low_since is None:
                self.low_since = now
            elif now - self.low_since >= 30:
                raise ResourcePause("available memory below 1.5 GiB for 30 seconds")
        else:
            self.low_since = None
        return avail


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: "" if row.get(name) is None else row.get(name) for name in fieldnames})


def locate(day):
    for name, lo, hi, period in SPLITS:
        if lo <= day <= hi:
            return name, period
    return None, None


def date_span(lo, hi):
    cursor = date.fromisoformat(lo)
    end = date.fromisoformat(hi)
    out = []
    while cursor <= end:
        out.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return out


def quorum(n_sites):
    return max(3, (n_sites * 3 + 3) // 4)


def native_duration(method_name):
    if "R & P Model 2025" in method_name:
        return "24 HOUR"
    if "BAM-1020" in method_name or "BAM-1022" in method_name or "T640" in method_name:
        return "1 HOUR"
    return None


def parse_decimal(text):
    if text in MISSING:
        return None
    try:
        return Decimal(text.strip())
    except Exception:
        return "INVALID"


def event_id(site, day, poc, method_code, event_type, duration):
    return "|".join(("88101", site, day, poc, method_code, event_type, duration))


EXPECTED_NOT_SINGLE = [
    4551, 6209, 6869, 7578, 7818, 7833, 8342, 8402,
    8717, 8738, 8747, 8781, 8842, 11956, 11990, 12004, 12375,
]
USABLE_ROW = {"UNIQUE", "SAME_VALUE_MULTI_MONITOR"}


def ordered_event_ids(ids):
    def sort_key(value):
        bits = value.split("|")
        return (bits[3], bits[4], bits[5], bits[6], value)

    return sorted(set(ids), key=sort_key)


def billing_text(ids):
    return " || ".join(ordered_event_ids(ids))


def new_bucket():
    return {
        "means": set(),
        "names": set(),
        "standards": set(),
        "observations": set(),
        "units": set(),
        "n": 0,
    }


def aqs_site(state, county, site):
    return f"{int(state):02d}-{int(county):03d}-{int(site):04d}"


def stream_epa(zip_path, parameter, sites, guard, cpu_start):
    index = defaultdict(dict)
    scanned = 0
    kept = 0
    parameter_skipped = 0
    multi_member = []
    with zipfile.ZipFile(zip_path) as archive:
        members = archive.namelist()
        multi_member = members
        member = members[0]
        with archive.open(member) as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
            for row in reader:
                scanned += 1
                if scanned % 200000 == 0:
                    guard.check()
                    if time.process_time() - cpu_start > 300:
                        raise ResourcePause("this round CPU exceeded 300 seconds during EPA scan")
                day = row["Date Local"]
                if day < WINDOW[0] or day > WINDOW[1]:
                    continue
                if row["Parameter Code"] != parameter:
                    parameter_skipped += 1
                    continue
                site = aqs_site(row["State Code"], row["County Code"], row["Site Num"])
                if site not in sites:
                    continue
                key = (row["POC"], row["Method Code"], row["Event Type"], row["Sample Duration"])
                bucket = index[(site, day)].get(key)
                if bucket is None:
                    bucket = new_bucket()
                    index[(site, day)][key] = bucket
                mean_text = row["Arithmetic Mean"].strip()
                if mean_text not in MISSING:
                    bucket["means"].add(Decimal(mean_text))
                bucket["names"].add(row["Method Name"])
                bucket["standards"].add(row["Pollutant Standard"])
                bucket["observations"].add(row["Observation Count"])
                bucket["units"].add(row["Units of Measure"])
                bucket["n"] += 1
                kept += 1
    return {
        "index": index,
        "scanned": scanned,
        "kept": kept,
        "parameter_skipped_in_window": parameter_skipped,
        "member": multi_member[0],
        "member_count": len(multi_member),
    }


def load_source():
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        member = next(name for name in archive.namelist() if name.endswith("Full24hrdataset.csv"))
        raw_rows = list(csv.DictReader(io.TextIOWrapper(archive.open(member), encoding="utf-8-sig", newline="")))
    fields = [name for name in raw_rows[0] if name and not name.startswith("Unnamed")]
    missing_counts = {name: 0 for name in ("PM25cf1", "RH", "TempC", "PM25FM")}
    ids = set()
    id_dates = set()
    for row in raw_rows:
        ids.add(row["ID"])
        id_dates.add((row["ID"], row["Date"]))
        for name in missing_counts:
            if row[name] in MISSING:
                missing_counts[name] += 1
    seen = set()
    kept = []
    duplicates = 0
    for line_number, row in enumerate(raw_rows, start=2):
        key = tuple(row[name] for name in fields)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        item = {name: row[name] for name in fields}
        item["source_row"] = line_number
        kept.append(item)
    return {
        "member": member,
        "raw_rows": len(raw_rows),
        "ids": len(ids),
        "id_dates": len(id_dates),
        "missing": missing_counts,
        "duplicates": duplicates,
        "kept": kept,
        "fields": fields,
    }


def load_site_map():
    shutil.copy2(SITE_MAP_SRC, ROOT / "site_map.csv")
    rows = {}
    with SITE_MAP_SRC.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows[row["device_id"]] = row
    return rows


def match_identities(index, site, day, method_name, duration, target):
    found = []
    for key, bucket in index.get((site, day), {}).items():
        poc, method_code, event_type, sample_duration = key
        if sample_duration != duration or method_name not in bucket["names"]:
            continue
        if len(bucket["means"]) != 1 or target not in bucket["means"]:
            continue
        found.append((key, bucket))
    return found


def count_88502(index, site, day, method_name, duration, target):
    return len(match_identities(index, site, day, method_name, duration, target))


def screen(device_days, guard):
    valid_dates = defaultdict(set)
    for item in device_days:
        if item["status"] == "VALID":
            valid_dates[(item["site_id"], item["reference_type"])].add(item["date"])
    ranking = []
    for (site, reference_type), days in valid_dates.items():
        periods = sorted({locate(day)[1] for day in days})
        ranking.append({
            "site_id": site,
            "group": next(item["group"] for item in device_days if item["site_id"] == site),
            "reference_type": reference_type,
            "periods_covered": len(periods),
            "valid_reference_dates": len(days),
            "periods": "|".join(periods),
            "selected": "false",
        })
    by_site = defaultdict(list)
    for row in ranking:
        by_site[row["site_id"]].append(row)
    winners = {}
    for site, rows in by_site.items():
        rows.sort(key=lambda row: (-row["periods_covered"], -row["valid_reference_dates"], row["reference_type"]))
        rows[0]["selected"] = "true"
        winners[site] = rows[0]
    representatives = []
    for site, winner in sorted(winners.items()):
        reference_type = winner["reference_type"]
        paired_by_device = defaultdict(set)
        devices = set()
        for item in device_days:
            if item["site_id"] != site or item["reference_type"] != reference_type:
                continue
            devices.add(item["device_id"])
            if item["paired"]:
                paired_by_device[item["device_id"]].add(item["date"])
        ordered = sorted(devices, key=lambda device: (-len(paired_by_device[device]), device))
        device_id = ordered[0]
        counts = {name: 0 for name, _lo, _hi, _period in SPLITS}
        chosen_days = []
        for item in device_days:
            if item["device_id"] == device_id and item["reference_type"] == reference_type:
                chosen_days.append(item)
                if item["paired"]:
                    counts[item["split"]] += 1
        counts["D"] = counts["D_fit"] + counts["D_tune"]
        failed = [f"{name}={counts[name]}<{threshold}" for name, threshold in SUPPORT.items() if counts[name] < threshold]
        representatives.append({
            "site_id": site,
            "device_id": device_id,
            "group": winner["group"],
            "reference_type": reference_type,
            "periods_covered": winner["periods_covered"],
            "valid_reference_dates": winner["valid_reference_dates"],
            "paired_days_154": len(paired_by_device[device_id]),
            "D_fit": counts["D_fit"],
            "D_tune": counts["D_tune"],
            "D": counts["D"],
            "V": counts["V"],
            "A": counts["A"],
            "T": counts["T"],
            "included": "false" if failed else "true",
            "reason": ";".join(failed),
            "days": chosen_days,
        })
    guard.check()
    return ranking, representatives


def build_panel(representatives):
    included = [row for row in representatives if row["included"] == "true"]
    group_sites = {
        group: [row["site_id"] for row in included if row["group"] == group]
        for group in ("West", "North")
    }
    required = {group: quorum(len(sites)) for group, sites in group_sites.items()}
    paired = defaultdict(set)
    for row in included:
        for item in row["days"]:
            if item["paired"]:
                paired[item["date"]].add(row["site_id"])
    panel = []
    evaluable = {"V": [], "T": []}
    for split in ("V", "T"):
        for day in date_span(*SPLIT_BOUNDS[split]):
            available = paired.get(day, set())
            counts = {group: sum(site in available for site in sites) for group, sites in group_sites.items()}
            day_ok = all(counts[group] >= required[group] for group in ("West", "North"))
            if day_ok:
                evaluable[split].append(day)
            for row in included:
                has_pair = row["site_id"] in available
                eligible = day_ok and has_pair
                if not has_pair:
                    reason = "missing_pair"
                elif not day_ok:
                    reason = "group_day_support"
                else:
                    reason = ""
                weight = "0"
                if eligible:
                    weight = "1/" + str(counts[row["group"]])
                panel.append({
                    "date": day,
                    "site_id": row["site_id"],
                    "group": row["group"],
                    "eligible": "true" if eligible else "false",
                    "weight": weight,
                    "ineligible_reason": reason,
                    "split": split,
                    "day_evaluable": "true" if day_ok else "false",
                    "west_available": counts["West"],
                    "north_available": counts["North"],
                    "west_required": required["West"],
                    "north_required": required["North"],
                })
    t0 = date(2019, 5, 4)
    blocks = sorted({(date.fromisoformat(day) - t0).days // 7 for day in evaluable["T"]})
    stats = {
        "candidate_sites_with_a_valid_type": len(representatives),
        "fixed_sites": len(included),
        "West_sites": len(group_sites["West"]),
        "North_sites": len(group_sites["North"]),
        "V_evaluable_days": len(evaluable["V"]),
        "T_evaluable_days": len(evaluable["T"]),
        "T_blocks": len(blocks),
        "T_block_indices": blocks,
        "quorum": required,
        "included_site_ids": [row["site_id"] for row in included],
    }
    failures = []
    if stats["fixed_sites"] < 10:
        failures.append(f"fixed_sites={stats['fixed_sites']} < 10")
    if stats["West_sites"] < 4:
        failures.append(f"West_sites={stats['West_sites']} < 4")
    if stats["North_sites"] < 4:
        failures.append(f"North_sites={stats['North_sites']} < 4")
    if stats["V_evaluable_days"] < 20:
        failures.append(f"V_evaluable_days={stats['V_evaluable_days']} < 20")
    if stats["T_evaluable_days"] < 40:
        failures.append(f"T_evaluable_days={stats['T_evaluable_days']} < 40")
    if stats["T_blocks"] < 7:
        failures.append(f"T_blocks={stats['T_blocks']} < 7")
    return panel, stats, failures


def decimal_text(value):
    return format(value, "f")


def build_outputs(representatives, device_days, links):
    included_ids = {(row["site_id"], row["device_id"], row["reference_type"]) for row in representatives if row["included"] == "true"}
    manifest = []
    features = []
    labels = {"D_fit": [], "D_tune": [], "V": []}
    for row in representatives:
        included = row["included"] == "true"
        for item in sorted(row["days"], key=lambda day: day["date"]):
            manifest.append({
                "site_id": row["site_id"],
                "device_id": row["device_id"],
                "group": row["group"],
                "date": item["date"],
                "split": item["split"],
                "reference_type": row["reference_type"],
                "reference_linked": "true" if item["status"] == "VALID" else "false",
                "paired_valid": "true" if item["paired"] else "false",
                "included_in_panel": "true" if included else "false",
                "billing_key": item["billing_key"] if item["status"] == "VALID" else "",
            })
            if not included:
                continue
            features.append({
                "row_id": row["site_id"] + "|" + item["date"],
                "date": item["date"],
                "site_id": row["site_id"],
                "device_id": row["device_id"],
                "group": row["group"],
                "split": item["split"],
                "paired_valid": "true" if item["paired"] else "false",
                "PM25cf1": item["pm25cf1"],
                "RH": item["rh"],
                "TempC": item["tempc"],
            })
            if item["paired"] and item["split"] in labels:
                members = item["billing_key"].split(" || ") if item["billing_key"] else []
                if item["reference_decimal"] is None or len(members) != item["n_event_keys"] or item["n_event_keys"] < 1:
                    raise RuntimeError("label construction did not retain every matched monitor")
                labels[item["split"]].append({
                    "row_id": row["site_id"] + "|" + item["date"],
                    "date": item["date"],
                    "site_id": row["site_id"],
                    "device_id": row["device_id"],
                    "group": row["group"],
                    "split": item["split"],
                    "billing_key": item["billing_key"],
                    "n_monitors": item["n_event_keys"],
                    "reference": decimal_text(item["reference_decimal"]),
                })
    for split, rows in labels.items():
        for row in rows:
            lo, hi = SPLIT_BOUNDS[split]
            if not (lo <= row["date"] <= hi):
                raise RuntimeError("label date escaped its split")
            if row["device_id"] == "IA3" and row["date"] == "2019-01-27":
                raise RuntimeError("IA3 2019-01-27 was labeled after the unresolved FRM day")
            if int(row["n_monitors"]) > 1 and row["billing_key"].count(" || ") + 1 != int(row["n_monitors"]):
                raise RuntimeError("multi-monitor label collapsed to one key")
    events = {}
    for item in device_days:
        if item["status"] != "VALID" or not item["billing_key"]:
            continue
        slot = events.get(item["billing_key"])
        if slot is None:
            slot = {
                "billing_key": item["billing_key"],
                "site_id": item["site_id"],
                "date": item["date"],
                "split": item["split"],
                "group": item["group"],
                "parameter_code": "88101",
                "ordered_event_keys": item["billing_key"],
                "n_keys": item["n_event_keys"],
                "method_name": item["reference_type"],
                "devices": set(),
                "source_rows": set(),
                "means": set(),
            }
            events[item["billing_key"]] = slot
        slot["devices"].add(item["device_id"])
        slot["source_rows"].update(item["source_rows"])
        slot["means"].add(item["reference_decimal"])
    event_rows = []
    collisions = []
    for key, slot in events.items():
        if len(slot["means"]) != 1:
            collisions.append({"billing_key": key, "split": slot["split"], "n_reference_values": len(slot["means"])})
        value = ""
        withheld = "true"
        if slot["split"] in VALUE_SPLITS and len(slot["means"]) == 1:
            value = decimal_text(next(iter(slot["means"])))
            withheld = "false"
        event_rows.append({
            "billing_key": key,
            "site_id": slot["site_id"],
            "date": slot["date"],
            "split": slot["split"],
            "group": slot["group"],
            "parameter_code": "88101",
            "ordered_event_keys": slot["ordered_event_keys"],
            "n_keys": slot["n_keys"],
            "method_name": slot["method_name"],
            "devices": "|".join(sorted(slot["devices"])),
            "source_rows": "|".join(str(number) for number in sorted(slot["source_rows"])),
            "n_devices": len(slot["devices"]),
            "billing_count": 1,
            "reference_value": value,
            "value_withheld": withheld,
        })
    excluded = []
    for item in device_days:
        if not item["status"].startswith("EXCLUDED_"):
            continue
        excluded.append({
            "date": item["date"],
            "site_id": item["site_id"],
            "device_id": item["device_id"],
            "reference_type": item["reference_type"],
            "exclusion_reason": item["status"],
            "source_rows": "|".join(str(number) for number in item["source_rows"]),
            "split": item["split"],
            "group": item["group"],
            "n_event_keys": item["n_event_keys"],
        })
    return manifest, features, labels, event_rows, excluded, collisions, included_ids


def preprocessing(features):
    paired = [row for row in features if row["split"] == "D_fit" and row["paired_valid"] == "true"]
    out = {"fit_split": "D_fit", "n_paired_rows": len(paired), "applied_to_exported_features": False}
    for name in ("RH", "TempC"):
        values = []
        missing = 0
        for row in paired:
            parsed = parse_decimal(row[name])
            if parsed is None:
                missing += 1
            elif parsed == "INVALID":
                raise RuntimeError("undocumented " + name + " token in D_fit")
            else:
                values.append(parsed)
        median = statistics.median(values) if values else None
        out[name] = {
            "missing": missing,
            "non_missing": len(values),
            "median": None if median is None else decimal_text(median),
        }
    out["note"] = "Medians are stored for a later authorized fit. This run does not impute and does not fit."
    return out


def protocol_document():
    return {
        "version": "targeted-reference-calibration-P0-same-value-screen-20261022",
        "fitted": False,
        "P1": "NOT_RUN",
        "thresholds_computed": False,
        "source": str(SOURCE_ZIP).replace("\\", "/"),
        "epa_cache": str(CACHE).replace("\\", "/"),
        "splits": {name: [lo, hi] for name, lo, hi, _period in SPLITS},
        "period_D": ["2019-01-26", "2019-03-08"],
        "groups": ["West", "North"],
        "features": ["PM25cf1", "RH", "TempC"],
        "target": "PM25FM",
        "units": "ug/m3",
        "missing_tokens": ["NA", ""],
        "negative_reference": "retain",
        "event_key": "AQS site + date + parameter 88101 + POC + method code + event type + native sample duration",
        "link_requirements": [
            "parameter 88101 only; 88502 cannot replace FRM/FEM",
            "EPA Method Name exactly equals FEMorFRMtype",
            "EPA Arithmetic Mean exactly equals PM25FM as a decimal; no tolerance; 1st Max Value is not used",
        ],
        "native_duration": {
            "R & P Model 2025": "24 HOUR",
            "BAM-1020": "1 HOUR",
            "BAM-1022": "1 HOUR",
            "T640_including_T640X": "1 HOUR",
        },
        "pollutant_standard_merge": "same POC, method, event type, native duration, and mean only",
        "device_day": {
            "one_event_key": "UNIQUE; reference is that key's mean",
            "same_value_multi_monitor": "two or more keys whose means all equal the same source value; reference is that shared value; all keys are retained in POC, method code, event type order",
            "different_reference_values": "EXCLUDED_AMBIGUOUS_MONITOR",
            "any_unresolved_row": "EXCLUDED_UNRESOLVED_ROW; linked siblings are not kept",
            "billing_key": "ordered set of all matched keys on the valid device-day; identical sets bill once",
        },
        "same_value_waiver_rows": EXPECTED_NOT_SINGLE,
        "named_unresolved_row": 8402,
        "do_not_replace_8402_pm25fm": ["13.3", "14"],
        "reference_type_order": ["four_periods_covered_desc", "unique_valid_dates_desc", "FEMorFRMtype_lexical"],
        "representative_order": ["paired_dates_154_desc", "ID_lexical"],
        "no_replacement_after_support_failure": True,
        "no_min_poc_no_first_row_no_average": True,
        "site_support": SUPPORT,
        "panel_support": {
            "sites": 10,
            "each_group": 4,
            "V_days": 20,
            "T_days": 40,
            "T_blocks": 7,
            "day_group_required": "max(3, ceil(0.75 * fixed sites in that group))",
            "T_block_definition": "floor((date - 2019-05-04).days / 7); a block counts if it contains at least one evaluable day",
        },
        "A_T": "linkage metadata only; reference numbers are not written; training reads are refused",
        "models_defined_not_fit": {
            "M0": "raw PM25cf1",
            "M1": "intercept + beta x",
            "M2": "M1 + b_site",
            "M3": "M2 + d_site x1",
            "M4": {
                "n_estimators": 100,
                "max_depth": 6,
                "min_samples_leaf": 5,
                "max_features": 1.0,
                "bootstrap": False,
                "criterion": "squared_error",
                "n_jobs": 1,
                "random_state": 20261022,
            },
        },
        "lambda": [0.1, 1, 10],
        "thresholds": {"G_R": 0.05, "H_C": 0.02, "near_zero": 1e-08},
        "budgets": {
            "inherited_cpu_s": 12.765625,
            "inherited_not_deducted_from_cap": True,
            "this_round_cpu_s": 300,
            "this_round_wall_s": 900,
            "rss_gib": 1.5,
            "low_available_gib": 1.5,
            "low_available_seconds": 30,
        },
        "threads": 1,
        "no_gpu": True,
    }


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[name]) for name in headers) + " |")
    return "\n".join(lines)


def write_audit(state):
    counts = state["source_counts"]
    link = state["link_counts"]
    lines = [
        "# P0 重算审计",
        "",
        "状态：`" + state["status"] + "`。P1：`NOT_RUN`。评价面板：`" + state["panel"] + "`。",
        "",
        "本轮没有拟合模型，没有计算 RMSE、ContrastMAE、5% 收益或 2% 组差。这些门槛只写在冻结配置里。",
        "",
        "## 来源",
        "",
        "- 主表：`" + counts["member"] + "`，解析 " + str(counts["raw_rows"]) + " 行、" + str(counts["ids"]) + " 个 ID、" + str(counts["id_dates"]) + " 个 ID×日期。",
        "- 完全重复折叠 " + str(counts["duplicates"]) + " 行。之后的联结使用折叠后的行，源行号仍是 CSV 行号。",
        "- 全表缺失：PM25cf1 " + str(counts["missing"]["PM25cf1"]) + "，RH " + str(counts["missing"]["RH"]) + "，TempC " + str(counts["missing"]["TempC"]) + "，PM25FM " + str(counts["missing"]["PM25FM"]) + "。缺失记号只认 `NA` 和空字符串。",
        "- 字典说明 `PM25FM` 与 `PM25cf1` 的单位是 µg/m³。负参考值保留。",
        "- EPA 日文件来自只读缓存，没有重新下载。88101 扫描 " + str(state["epa"]["88101"]["scanned"]) + " 行，窗口内目标站点保留 " + str(state["epa"]["88101"]["kept"]) + " 行。88502 扫描 " + str(state["epa"]["88502"]["scanned"]) + " 行，保留 " + str(state["epa"]["88502"]["kept"]) + " 行。88502 只用来核对未联结行，没有替补 88101。",
        "- 站点映射沿用已核对的 `site_map.csv` 字节副本。West/North 以源表 `region` 为准。",
        "",
        "## 旧键复算",
        "",
        "旧键“站点 + 日期 + 参考型号”在 West/North、2019-01-26—2019-06-28 内有 " + str(link["old_conflict_keys"]) + " 个多值键，涉及 " + str(link["old_conflict_sites"]) + " 个站、" + str(link["old_conflict_dates"]) + " 日、" + str(link["old_conflict_rows"]) + " 行。这只是对照已关闭的失败记录，不把该记录改成通过。",
        "",
        "## 新事件键联结",
        "",
        "一行在参数为 88101、方法名完全相同、算术平均与 `PM25FM` 十进制精确相等、并且采样时长按仪器固定时，才算命中一个监测键。恰好一个键为 `UNIQUE`。两个或更多键且每个键的平均都等于该源值时为 `SAME_VALUE_MULTI_MONITOR`，全部键按 POC、方法代码、事件类型排序保留，不填写单一 POC。零个键，或命中键的平均并不都等于该源值，该行不可用。重力法 `R & P Model 2025` 用 `24 HOUR`。BAM-1020、BAM-1022、T640 用 `1 HOUR`。`T640X` 名称包含 `T640`，按同一连续 FEM 规则使用 `1 HOUR`，没有改用别的时长去促成联结。`24-HR BLK AVG` 不并入，也不与 `1 HOUR` 平均。同一键只因污染物标准重复且均值已经相同才合并。",
        "",
        "| 对象 | 数量 |",
        "| --- | ---: |",
        "| 窗口内 West/North 且有参考值的源行 | " + str(link["rows_in_scope"]) + " |",
        "| 恰好一个事件键 | " + str(link["rows_single"]) + " |",
        "| 同值多监测键 | " + str(link["rows_same_value"]) + " |",
        "| 零个事件键 | " + str(link["rows_zero"]) + " |",
        "| 不是恰好一个键的源行 | " + ", ".join(str(number) for number in link["not_single_source_rows"]) + " |",
        "| 第3节复核 | " + ("一致" if link["review_ok"] else "不一致") + " |",
        "| 同一新事件键的不同参考值 | " + str(link["event_value_collisions"]) + " |",
        "| EPA 键内多个算术平均 | " + str(link["epa_multi_mean_keys"]) + " |",
        "",
        "源行 8402 的核对：" + state["row_8402_text"],
        "",
        "88502 对未联结行的精确方法、时长和均值命中数：" + str(link["unresolved_88502_hits"]) + "。这些命中没有用来替补。",
        "",
        "IA3 在 2019-01-27 的设备日：" + state["ia3_text"],
        "",
    ]
    if state["screened"]:
        lines.extend([
            "## 排除的设备日",
            "",
            "第3节复核一致后，才使用同值多键规则。两个或更多键的算术平均都等于同一个源值时，参考值就是这个共同浓度，全部键按 POC、方法代码、事件类型排序保留，不指定其中一个 POC。同一设备日出现两个不同参考值时标为 `EXCLUDED_AMBIGUOUS_MONITOR`。任一源行没有可用监测键时，整个设备日为 `EXCLUDED_UNRESOLVED_ROW`。没有取最小 POC，没有保留第一条，没有平均，也没有按与传感器的距离挑选。",
            "",
            "| 排除原因 | 设备日 |",
            "| --- | ---: |",
            "| EXCLUDED_AMBIGUOUS_MONITOR | " + str(state["exclusion_counts"].get("EXCLUDED_AMBIGUOUS_MONITOR", 0)) + " |",
            "| EXCLUDED_UNRESOLVED_ROW | " + str(state["exclusion_counts"].get("EXCLUDED_UNRESOLVED_ROW", 0)) + " |",
            "",
            "有效参考日只统计上述规则下的有效设备日。代表设备的有效配对日还要求 `PM25cf1` 不是缺失；RH 和 TempC 缺失不取消配对，留待以后用 D_fit 中位数填充。本轮不填充、不拟合。",
            "",
            "## 站点筛选",
            "",
            "候选站点 " + str(state["candidate_sites"]) + " 个，其中至少有一个有效参考设备日的站点 " + str(state["stats"]["candidate_sites_with_a_valid_type"]) + " 个。没有有效参考日的站点：" + state["sites_without_valid"] + "。",
            "",
            "型号先比 D、V、A、T 四个时段的覆盖数，再比 154 天内唯一有效参考日，平局按型号名称字典序。代表设备按 154 天有效配对日数，平局按 ID 字典序。支持不足则剔除该站点，不换设备，也不换型号。",
            "",
            md_table(
                ["site_id", "group", "device_id", "reference_type", "paired_days_154", "D_fit", "D_tune", "D", "V", "A", "T", "included", "reason"],
                state["representative_rows"],
            ),
            "",
            "## 评价面板",
            "",
            "固定站点 " + str(state["stats"]["fixed_sites"]) + " 个，West " + str(state["stats"]["West_sites"]) + " 个，North " + str(state["stats"]["North_sites"]) + " 个。",
            "组内当日门槛：West " + str(state["stats"]["quorum"]["West"]) + "，North " + str(state["stats"]["quorum"]["North"]) + "。",
            "V 可评价日 " + str(state["stats"]["V_evaluable_days"]) + "。T 可评价日 " + str(state["stats"]["T_evaluable_days"]) + "。T 七天块 " + str(state["stats"]["T_blocks"]) + " 个，块号 " + str(state["stats"]["T_block_indices"]) + "。块从 2019-05-04 起每 7 天一块，块内至少一天可评价即计入。",
            "",
            "未通过的面板条件：" + ("无" if not state["failures"] else "；".join(state["failures"])) + "。",
            "",
        ])
    else:
        lines.extend([
            "## 筛选",
            "",
            "未进入站点筛选和评价面板。排除名单没有扩大。固定站点数、V/T 可评价日和七天块数未确定。",
            "",
            "停止原因：" + state["stop_reason"],
            "",
        ])
    lines.extend([
        "## 接口",
        "",
        state["isolation_text"],
        "",
        "没有训练模型，因此不声称预测不变性已经验证。",
        "",
    ])
    (ROOT / "P0_DATA_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_failure(state):
    if state["status"] == "PASS_P0":
        return
    lines = [
        "# P0 失败或阻塞记录",
        "",
        "状态：`" + state["status"] + "`。P1：`NOT_RUN`。",
        "",
        state["stop_reason"] if state["stop_reason"] else "面板支持条件没有全部达到。",
        "",
        "实测与门槛：",
        "",
    ]
    if state["screened"]:
        stats = state["stats"]
        lines.append(
            "固定站点 "
            + str(stats["fixed_sites"])
            + "（门槛 10），West "
            + str(stats["West_sites"])
            + "（门槛 4），North "
            + str(stats["North_sites"])
            + "（门槛 4），V 可评价日 "
            + str(stats["V_evaluable_days"])
            + "（门槛 20），T 可评价日 "
            + str(stats["T_evaluable_days"])
            + "（门槛 40），T 七天块 "
            + str(stats["T_blocks"])
            + "（门槛 7）。"
        )
        lines.append("")
        lines.append("未达到的条件：" + "；".join(state["failures"]) + "。")
    else:
        lines.append("筛选未进行。固定站点数和可评价日未确定。")
    lines.extend([
        "",
        "原因类别：见状态。这不是把缺的数值写成 0，也不是模型效果失败。",
        "",
        "已完成范围：公开数据的身份重算和本文件列出的检查。P1 没有运行。",
        "",
        "当前还能支持的结论：只限于上面写出的计数和状态。不能据此说校准有效或无效。",
        "",
        "本轮不改日期、区域、支持门槛，也不换设备或型号。后续若要改变这些规则，需要单独授权。",
        "",
    ])
    (ROOT / "FAILURE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def write_next_stage(state):
    text = "\n".join([
        "# 下一阶段申请",
        "",
        "P0 状态：`" + state["status"] + "`。",
        "",
        "P1 尚未授权。`P0_SAME_VALUE_SCREEN_INSTRUCTIONS_20261022.md` 只授权完成 P0 筛选。本轮没有实现 M0–M4，没有运行 P1，也没有计算收益或区间。",
        "",
        "在获得单独的 P1 授权之前，不读取 A/T 参考数值，不训练 M0–M4。",
        "",
    ])
    (ROOT / "NEXT_STAGE_REQUEST.md").write_text(text, encoding="utf-8")


def write_readme():
    command = (
        '$env:OMP_NUM_THREADS = "1"\n'
        '$env:MKL_NUM_THREADS = "1"\n'
        '$env:OPENBLAS_NUM_THREADS = "1"\n'
        '$env:NUMEXPR_NUM_THREADS = "1"\n'
        '& "C:\\Cursor\\raven.mcs\\.venv_new\\Scripts\\python.exe" '
        '"C:\\Cursor\\raven.mcs\\results_targeted_reference_calibration\\p0_same_value_screen_20261022_210125\\prepare_data.py"\n'
    )
    text = "\n".join([
        "# P0 补做",
        "",
        "实际使用的 PowerShell 命令：",
        "",
        "```powershell",
        command.rstrip(),
        "```",
        "",
        "Python 是 `C:\\Cursor\\raven.mcs\\.venv_new\\Scripts\\python.exe`。没有升级这个环境，也没有新建包装依赖。内存用 Windows 工作集接口计量。",
        "",
        "EPA 日文件和补充 PDF、数据字典只从 `source_cache_20261022` 读取。主表从原始数据包读取。没有重新下载。",
        "",
    ])
    (ROOT / "README.md").write_text(text, encoding="utf-8")


def write_isolation_md(isolation):
    lines = [
        "# 接口隔离检查",
        "",
        "通过：" + ("是" if isolation["passed"] else "否") + "。要求标签文件：" + ("是" if isolation["require_labels"] else "否") + "。",
        "",
        "已检查的内容：",
        "",
    ]
    for item in isolation["checks"]:
        detail = ""
        extras = [f"{key}={value}" for key, value in item.items() if key not in ("check", "ok")]
        if extras:
            detail = "（" + "，".join(extras) + "）"
        lines.append("- " + item["check"] + "：" + ("通过" if item["ok"] else "未通过") + detail)
    lines.extend([
        "",
        "训练入口只接受 D_fit 与 D_tune，二者合并为 D。V、A、T 的训练读取会拒绝。A/T 标签文件不存在。",
        "",
        "未检查：没有训练模型，没有改写 A/T 标签副本后比较预测。预测不变性：" + isolation["prediction_invariance"] + "。",
        "",
    ])
    (ROOT / "ISOLATION_CHECK.md").write_text("\n".join(lines), encoding="utf-8")


def empty_tables():
    write_csv(
        ROOT / "reference_events_metadata.csv",
        ["billing_key", "site_id", "date", "split", "group", "parameter_code", "ordered_event_keys", "n_keys", "method_name", "devices", "source_rows", "n_devices", "billing_count", "reference_value", "value_withheld"],
        [],
    )
    write_csv(
        ROOT / "representative_devices.csv",
        ["site_id", "device_id", "group", "reference_type", "periods_covered", "valid_reference_dates", "paired_days_154", "D_fit", "D_tune", "D", "V", "A", "T", "included", "reason"],
        [],
    )
    write_csv(
        ROOT / "excluded_device_days.csv",
        ["date", "site_id", "device_id", "reference_type", "exclusion_reason", "source_rows", "split", "group", "n_event_keys"],
        [],
    )
    write_csv(
        ROOT / "split_manifest.csv",
        ["site_id", "device_id", "group", "date", "split", "reference_type", "reference_linked", "paired_valid", "included_in_panel", "billing_key"],
        [],
    )
    write_csv(
        ROOT / "evaluation_panel.csv",
        ["date", "site_id", "group", "eligible", "weight", "ineligible_reason", "split", "day_evaluable", "west_available", "north_available", "west_required", "north_required"],
        [],
    )


def run(state, guard, cpu_start):
    guard.check()
    if guard.min_available < LIMIT_BYTES:
        started = time.monotonic()
        while available_bytes() < LIMIT_BYTES:
            guard.check()
            if time.monotonic() - started >= 30:
                raise ResourcePause("available memory below 1.5 GiB for 30 seconds before linkage")
            time.sleep(1)
    for path in (EPA_88101, EPA_88502):
        digest = sha256_file(path)
        if digest != EXPECTED_HASH[path.name]:
            raise RuntimeError("cache hash mismatch for " + path.name)
    state["cache_hashes_ok"] = True
    site_map = load_site_map()
    state["site_map_sha256"] = sha256_file(ROOT / "site_map.csv")
    source = load_source()
    state["source_counts"] = {
        "member": source["member"],
        "raw_rows": source["raw_rows"],
        "ids": source["ids"],
        "id_dates": source["id_dates"],
        "missing": source["missing"],
        "duplicates": source["duplicates"],
    }
    if [len(date_span(*SPLIT_BOUNDS[name])) for name in ("D_fit", "D_tune", "V", "A", "T")] != [28, 14, 28, 28, 56]:
        raise RuntimeError("split lengths drifted")
    scope = []
    unmapped = []
    group_mismatch = []
    invalid_numbers = []
    for row in source["kept"]:
        if row["region"] not in ("West", "North"):
            continue
        if not (WINDOW[0] <= row["Date"] <= WINDOW[1]):
            continue
        meta = site_map.get(row["ID"])
        if meta is None or not meta["site_id"]:
            unmapped.append(row["ID"])
            continue
        if meta["group"] != row["region"]:
            group_mismatch.append({"device_id": row["ID"], "source_region": row["region"], "map_group": meta["group"]})
        parsed = parse_decimal(row["PM25FM"])
        if parsed == "INVALID":
            invalid_numbers.append(row["source_row"])
        scope.append({
            "source_row": row["source_row"],
            "date": row["Date"],
            "device_id": row["ID"],
            "site_id": meta["site_id"],
            "group": row["region"],
            "frm": row["FEMorFRM"],
            "reference_type": row["FEMorFRMtype"],
            "pm_text": row["PM25FM"],
            "pm_decimal": parsed,
            "pm25cf1": row["PM25cf1"],
            "rh": row["RH"],
            "tempc": row["TempC"],
        })
    epa_sites = {row["site_id"] for row in site_map.values() if row["group"] in ("West", "North") and row["site_id"]}
    epa_sites.update(row["site_id"] for row in scope)
    state["epa"] = {}
    scanned = {}
    for parameter, path in (("88101", EPA_88101), ("88502", EPA_88502)):
        scanned[parameter] = stream_epa(path, parameter, epa_sites, guard, cpu_start)
        state["epa"][parameter] = {
            "scanned": scanned[parameter]["scanned"],
            "kept": scanned[parameter]["kept"],
            "member": scanned[parameter]["member"],
            "parameter_skipped_in_window": scanned[parameter]["parameter_skipped_in_window"],
        }
    guard.check()
    epa_conflicts = []
    units = set()
    for (site, day), buckets in scanned["88101"]["index"].items():
        split_name, _period = locate(day)
        for key, bucket in buckets.items():
            units.update(bucket["units"])
            if len(bucket["means"]) > 1:
                poc, method_code, event_type, duration = key
                epa_conflicts.append({
                    "site_id": site,
                    "date": day,
                    "split": split_name,
                    "poc": poc,
                    "method_code": method_code,
                    "event_type": event_type,
                    "sample_duration": duration,
                    "n_distinct_means": len(bucket["means"]),
                    "n_epa_rows": bucket["n"],
                })
    old_groups = defaultdict(list)
    links = []
    for row in scope:
        if row["pm_decimal"] in (None, "INVALID"):
            continue
        old_groups[(row["site_id"], row["date"], row["reference_type"])].append(row)
        split_name, _period = locate(row["date"])
        duration = native_duration(row["reference_type"])
        record = {
            "source_row": row["source_row"],
            "date": row["date"],
            "split": split_name,
            "device_id": row["device_id"],
            "site_id": row["site_id"],
            "group": row["group"],
            "reference_type": row["reference_type"],
            "pm_decimal": row["pm_decimal"],
            "pm_text": row["pm_text"],
            "link_status": "UNRESOLVED_NO_EXACT_MONITOR",
            "n_identities": 0,
            "event_id": "",
            "event_keys": [],
            "means_all_equal_source": False,
            "poc": "",
            "method_code": "",
            "method_name": "",
            "event_type": "",
            "sample_duration": duration or "",
            "pollutant_standards": "",
            "observation_count": "",
            "units": "",
            "n_88502": "",
        }
        if duration is None:
            record["link_status"] = "UNRESOLVED_NO_DOCUMENTED_DURATION"
        else:
            identities = match_identities(
                scanned["88101"]["index"], row["site_id"], row["date"], row["reference_type"], duration, row["pm_decimal"]
            )
            ordered = sorted(identities, key=lambda item: item[0])
            ids = []
            means = []
            means_ok = True
            for key, bucket in ordered:
                poc, method_code, event_type, sample_duration = key
                ids.append(event_id(row["site_id"], row["date"], poc, method_code, event_type, sample_duration))
                if len(bucket["means"]) != 1:
                    means_ok = False
                    continue
                means.append(next(iter(bucket["means"])))
            record["n_identities"] = len(ordered)
            record["event_keys"] = ids
            record["means_all_equal_source"] = bool(ordered) and means_ok and all(mean == row["pm_decimal"] for mean in means) and len(set(means)) == 1
            if len(ordered) == 1 and record["means_all_equal_source"]:
                key, bucket = ordered[0]
                poc, method_code, event_type, sample_duration = key
                record.update({
                    "link_status": "UNIQUE",
                    "event_id": ids[0],
                    "poc": poc,
                    "method_code": method_code,
                    "method_name": row["reference_type"],
                    "event_type": event_type,
                    "sample_duration": sample_duration,
                    "pollutant_standards": " | ".join(sorted(bucket["standards"])) if any(bucket["standards"]) else "(blank)",
                    "observation_count": "|".join(sorted(bucket["observations"])),
                    "units": "|".join(sorted(bucket["units"])),
                })
            elif len(ordered) >= 2 and record["means_all_equal_source"]:
                record["link_status"] = "SAME_VALUE_MULTI_MONITOR"
                record["method_name"] = row["reference_type"]
                record["sample_duration"] = duration
        if record["link_status"] not in USABLE_ROW and duration is not None:
            record["n_88502"] = count_88502(
                scanned["88502"]["index"], row["site_id"], row["date"], row["reference_type"], duration, row["pm_decimal"]
            )
        links.append(record)
    not_single = sorted(record["source_row"] for record in links if record["n_identities"] != 1)
    same_rows = [record for record in links if record["link_status"] == "SAME_VALUE_MULTI_MONITOR"]
    zero_rows = [record for record in links if record["n_identities"] == 0]
    unusable = sorted(record["source_row"] for record in links if record["link_status"] not in USABLE_ROW)
    expected_same = [number for number in EXPECTED_NOT_SINGLE if number != 8402]
    review_ok = (
        not_single == EXPECTED_NOT_SINGLE
        and sorted(record["source_row"] for record in zero_rows) == [8402]
        and sorted(record["source_row"] for record in same_rows) == expected_same
        and all(record["n_identities"] == 2 and record["means_all_equal_source"] and len(record["event_keys"]) == 2 for record in same_rows)
    )
    designated = sorted(
        record["source_row"]
        for record in links
        if record["link_status"] == "SAME_VALUE_MULTI_MONITOR" and (record["poc"] or record["event_id"] or record["method_code"])
    )
    old_conflict_keys = []
    old_conflict_rows = 0
    for key, rows in old_groups.items():
        if len({row["pm_text"] for row in rows}) > 1:
            old_conflict_keys.append(key)
            old_conflict_rows += len(rows)
    by_event_means = defaultdict(set)
    for record in links:
        if record["link_status"] in USABLE_ROW:
            for key in record["event_keys"]:
                by_event_means[key].add(record["pm_decimal"])
    source_collisions = [
        {"event_id": key, "n_reference_values": len(values)}
        for key, values in by_event_means.items()
        if len(values) > 1
    ]
    sensor_groups = defaultdict(list)
    for row in scope:
        sensor_groups[(row["device_id"], row["date"])].append(row)
    sensor_conflicts = []
    for (device_id, day), rows in sensor_groups.items():
        fields = []
        for field, label in (("pm25cf1", "PM25cf1"), ("rh", "RH"), ("tempc", "TempC")):
            tokens = {None if row[field] in MISSING else row[field] for row in rows}
            if len(tokens) > 1:
                fields.append(label)
        if fields:
            sensor_conflicts.append({
                "device_id": device_id,
                "date": day,
                "split": locate(day)[0],
                "fields": "|".join(fields),
                "source_rows": "|".join(str(row["source_row"]) for row in sorted(rows, key=lambda item: item["source_row"])),
            })
    row_8402 = next((record for record in links if record["source_row"] == 8402), None)
    if row_8402 is None:
        row_8402_text = "源行 8402 没有出现在 West/North 窗口联结里。"
    else:
        row_8402_text = (
            "设备 " + row_8402["device_id"]
            + "，站点 " + row_8402["site_id"]
            + "，日期 " + row_8402["date"]
            + "，段 " + str(row_8402["split"])
            + "，联结状态 " + row_8402["link_status"]
            + "，身份数 " + str(row_8402["n_identities"])
            + "，88502 命中 " + str(row_8402["n_88502"])
            + "。D_fit 参考文字是 " + row_8402["pm_text"] + "。"
        )
    link_counts = {
        "rows_in_scope": len(links),
        "rows_unique": sum(record["link_status"] == "UNIQUE" for record in links),
        "rows_single": sum(record["n_identities"] == 1 for record in links),
        "rows_same_value": len(same_rows),
        "rows_zero": len(zero_rows),
        "rows_unresolved": len(unusable),
        "unresolved_source_rows": unusable,
        "not_single_source_rows": not_single,
        "zero_identity_rows": sorted(record["source_row"] for record in zero_rows),
        "review_ok": review_ok,
        "event_value_collisions": len(source_collisions),
        "epa_multi_mean_keys": len(epa_conflicts),
        "old_conflict_keys": len(old_conflict_keys),
        "old_conflict_sites": len({key[0] for key in old_conflict_keys}),
        "old_conflict_dates": len({key[1] for key in old_conflict_keys}),
        "old_conflict_rows": old_conflict_rows,
        "unresolved_88502_hits": sum(int(record["n_88502"]) for record in links if record["n_88502"] != ""),
        "units": sorted(units),
        "unmapped_devices": sorted(set(unmapped)),
        "group_mismatches": group_mismatch,
        "invalid_reference_rows": invalid_numbers,
        "sensor_conflicts": len(sensor_conflicts),
    }
    state["link_counts"] = link_counts
    state["row_8402_text"] = row_8402_text
    grouped_days = defaultdict(list)
    for record in links:
        grouped_days[(record["device_id"], record["date"], record["reference_type"])].append(record)
    device_days = []
    for (device_id, day, reference_type), records in grouped_days.items():
        statuses = {record["link_status"] for record in records}
        values = {record["pm_decimal"] for record in records}
        member_ids = ordered_event_ids(key for record in records for key in record["event_keys"])
        if not statuses <= USABLE_ROW:
            status_name = "EXCLUDED_UNRESOLVED_ROW"
            bill = ""
            reference_decimal = None
        elif len(values) != 1:
            status_name = "EXCLUDED_AMBIGUOUS_MONITOR"
            bill = ""
            reference_decimal = None
        else:
            status_name = "VALID"
            bill = " || ".join(member_ids)
            reference_decimal = next(iter(values))
            if not member_ids or bill != billing_text(member_ids):
                raise RuntimeError("valid device-day did not retain its ordered monitor set")
        source_rows_for_day = [row for row in scope if row["device_id"] == device_id and row["date"] == day and row["reference_type"] == reference_type and row["pm_decimal"] not in (None, "INVALID")]
        cf1 = {None if row["pm25cf1"] in MISSING else row["pm25cf1"] for row in source_rows_for_day}
        paired = status_name == "VALID" and cf1 == {next(iter(cf1))} and next(iter(cf1)) is not None and len(cf1) == 1
        first = source_rows_for_day[0]
        device_days.append({
            "device_id": device_id,
            "date": day,
            "reference_type": reference_type,
            "site_id": first["site_id"],
            "group": first["group"],
            "split": locate(day)[0],
            "status": status_name,
            "billing_key": bill,
            "n_event_keys": len(member_ids),
            "source_rows": sorted(record["source_row"] for record in records),
            "reference_decimal": reference_decimal,
            "paired": paired,
            "pm25cf1": "" if None in cf1 or len(cf1) != 1 else next(iter(cf1)),
            "rh": first["rh"],
            "tempc": first["tempc"],
        })
    ia3 = [item for item in device_days if item["device_id"] == "IA3" and item["date"] == "2019-01-27"]
    ia3_bits = []
    for item in sorted(ia3, key=lambda row: row["reference_type"]):
        ia3_bits.append(item["reference_type"] + " → " + item["status"] + "，源行 " + "|".join(str(number) for number in item["source_rows"]))
    state["ia3_text"] = "；".join(ia3_bits) if ia3_bits else "没有找到 IA3 在 2019-01-27 的设备日。"
    stop_status = None
    stop_reason = ""
    if invalid_numbers or unmapped or group_mismatch:
        stop_status = "BLOCKED_METADATA"
        stop_reason = "站点映射或参考数值记号不能按冻结规则解释。未映射设备 " + str(sorted(set(unmapped))) + "；组别不一致 " + str(len(group_mismatch)) + "；无法解析的参考行 " + str(invalid_numbers) + "。"
    elif epa_conflicts or source_collisions:
        stop_status = "INVALID_RUN"
        stop_reason = "同一新事件键出现不同参考值。EPA 多均值键 " + str(len(epa_conflicts)) + " 个，源行撞到同一键的不同数值 " + str(len(source_collisions)) + " 个。没有平均，也没有挑选其中一个。"
    elif not review_ok:
        stop_status = "BLOCKED_METADATA"
        stop_reason = "第3节复核不一致。不是恰好一个键的源行是 " + str(not_single) + "。没有扩大同值豁免，也没有改用最小 POC、第一条、平均值或距离。"
    elif designated:
        stop_status = "INVALID_RUN"
        stop_reason = "同值多键行被指定了单一 POC 或单一事件键：" + str(designated) + "。"
    elif sensor_conflicts:
        stop_status = "INVALID_RUN"
        stop_reason = "同一设备日的 PM25cf1、RH 或 TempC 不一致，共 " + str(len(sensor_conflicts)) + " 个设备日。没有挑选其中一行。"
    linkage_rows = []
    for record in links:
        exported = record["pm_text"] if record["split"] in VALUE_SPLITS else ""
        linkage_rows.append({
            "source_row": record["source_row"],
            "date": record["date"],
            "split": record["split"],
            "device_id": record["device_id"],
            "site_id": record["site_id"],
            "group": record["group"],
            "reference_type": record["reference_type"],
            "link_status": record["link_status"],
            "n_identities": record["n_identities"],
            "event_id": record["event_id"],
            "ordered_event_keys": " || ".join(record["event_keys"]),
            "poc": record["poc"],
            "method_code": record["method_code"],
            "event_type": record["event_type"],
            "sample_duration": record["sample_duration"],
            "n_88502_exact_not_used": record["n_88502"],
            "pm25fm_exported": exported,
            "value_withheld": "false" if record["split"] in VALUE_SPLITS else "true",
        })
    write_csv(
        ROOT / "row_linkage.csv",
        ["source_row", "date", "split", "device_id", "site_id", "group", "reference_type", "link_status", "n_identities", "event_id", "ordered_event_keys", "poc", "method_code", "event_type", "sample_duration", "n_88502_exact_not_used", "pm25fm_exported", "value_withheld"],
        linkage_rows,
    )
    same_value_rows = []
    for record in same_rows:
        same_value_rows.append({
            "source_row": record["source_row"],
            "date": record["date"],
            "split": record["split"],
            "device_id": record["device_id"],
            "site_id": record["site_id"],
            "ordered_event_keys": " || ".join(record["event_keys"]),
            "pm25fm_exported": record["pm_text"] if record["split"] in VALUE_SPLITS else "",
            "value_withheld": "false" if record["split"] in VALUE_SPLITS else "true",
        })
    write_csv(
        ROOT / "same_value_multimonitor_rows.csv",
        ["source_row", "date", "split", "device_id", "site_id", "ordered_event_keys", "pm25fm_exported", "value_withheld"],
        same_value_rows,
    )
    if epa_conflicts:
        write_csv(
            ROOT / "event_key_mean_conflicts.csv",
            ["site_id", "date", "split", "poc", "method_code", "event_type", "sample_duration", "n_distinct_means", "n_epa_rows"],
            epa_conflicts,
        )
    if sensor_conflicts:
        write_csv(
            ROOT / "sensor_input_conflicts.csv",
            ["device_id", "date", "split", "fields", "source_rows"],
            sensor_conflicts,
        )
    state["screened"] = stop_status is None
    state["stop_reason"] = stop_reason
    state["failures"] = []
    state["stats"] = None
    state["representative_rows"] = []
    state["exclusion_counts"] = {}
    state["candidate_sites"] = len({row["site_id"] for row in scope})
    state["sites_without_valid"] = ""
    if stop_status is not None:
        empty_tables()
        state["status"] = stop_status
        state["panel"] = "NOT_RUN"
    else:
        unresolved_days = [item for item in device_days if item["status"] == "EXCLUDED_UNRESOLVED_ROW"]
        if len(unresolved_days) != 1 or 8402 not in unresolved_days[0]["source_rows"] or 8465 not in unresolved_days[0]["source_rows"]:
            raise RuntimeError("named unresolved device-day did not keep its sibling rows")
        ranking, representatives = screen(device_days, guard)
        panel, stats, failures = build_panel(representatives)
        manifest, features, labels, event_rows, excluded, collisions, _included = build_outputs(representatives, device_days, links)
        if collisions:
            state["status"] = "INVALID_RUN"
            state["panel"] = "NOT_RUN"
            state["stop_reason"] = "写出元数据时发现同一计费键对应多个参考值。没有平均，也没有改用最小 POC。"
            state["screened"] = False
            empty_tables()
        else:
            for row in excluded:
                if row["exclusion_reason"] == "EXCLUDED_UNRESOLVED_ROW" and "8402" not in row["source_rows"].split("|"):
                    raise RuntimeError("unresolved exclusion expanded beyond row 8402")
            write_csv(
                ROOT / "reference_type_ranking.csv",
                ["site_id", "group", "reference_type", "periods_covered", "valid_reference_dates", "periods", "selected"],
                ranking,
            )
            representative_rows = []
            for row in representatives:
                representative_rows.append({key: value for key, value in row.items() if key != "days"})
            write_csv(
                ROOT / "representative_devices.csv",
                ["site_id", "device_id", "group", "reference_type", "periods_covered", "valid_reference_dates", "paired_days_154", "D_fit", "D_tune", "D", "V", "A", "T", "included", "reason"],
                representative_rows,
            )
            write_csv(
                ROOT / "excluded_device_days.csv",
                ["date", "site_id", "device_id", "reference_type", "exclusion_reason", "source_rows", "split", "group", "n_event_keys"],
                sorted(excluded, key=lambda row: (row["date"], row["site_id"], row["device_id"], row["reference_type"])),
            )
            write_csv(
                ROOT / "split_manifest.csv",
                ["site_id", "device_id", "group", "date", "split", "reference_type", "reference_linked", "paired_valid", "included_in_panel", "billing_key"],
                manifest,
            )
            write_csv(
                ROOT / "evaluation_panel.csv",
                ["date", "site_id", "group", "eligible", "weight", "ineligible_reason", "split", "day_evaluable", "west_available", "north_available", "west_required", "north_required"],
                panel,
            )
            write_csv(
                ROOT / "reference_events_metadata.csv",
                ["billing_key", "site_id", "date", "split", "group", "parameter_code", "ordered_event_keys", "n_keys", "method_name", "devices", "source_rows", "n_devices", "billing_count", "reference_value", "value_withheld"],
                sorted(event_rows, key=lambda row: (row["date"], row["site_id"], row["billing_key"])),
            )
            data_dir = ROOT / "data"
            data_dir.mkdir(exist_ok=True)
            write_csv(
                data_dir / "features.csv",
                ["row_id", "date", "site_id", "device_id", "group", "split", "paired_valid", "PM25cf1", "RH", "TempC"],
                features,
            )
            for split, rows in labels.items():
                write_csv(
                    data_dir / f"labels_{split}.csv",
                    ["row_id", "date", "site_id", "device_id", "group", "split", "billing_key", "n_monitors", "reference"],
                    rows,
                )
            write_json(ROOT / "preprocessing_D_fit.json", preprocessing(features))
            state["representative_rows"] = representative_rows
            state["stats"] = stats
            state["failures"] = failures
            state["exclusion_counts"] = {
                "EXCLUDED_AMBIGUOUS_MONITOR": sum(row["exclusion_reason"] == "EXCLUDED_AMBIGUOUS_MONITOR" for row in excluded),
                "EXCLUDED_UNRESOLVED_ROW": sum(row["exclusion_reason"] == "EXCLUDED_UNRESOLVED_ROW" for row in excluded),
            }
            ranked_sites = {row["site_id"] for row in representatives}
            missing_sites = sorted({row["site_id"] for row in scope} - ranked_sites)
            state["sites_without_valid"] = "、".join(missing_sites) if missing_sites else "无"
            state["panel"] = "WRITTEN"
            state["event_rows"] = len(event_rows)
            state["event_device_reuses"] = sum(int(row["n_devices"]) - 1 for row in event_rows)
            state["label_counts"] = {split: len(rows) for split, rows in labels.items()}
    assert_published_boundaries()
    from isolation_check import check as isolation_check
    isolation = isolation_check(ROOT, require_labels=state["screened"] and state.get("panel") == "WRITTEN")
    state["isolation"] = isolation
    write_isolation_md(isolation)
    if state["screened"] and state.get("panel") == "WRITTEN":
        if not isolation["passed"]:
            state["status"] = "INVALID_RUN"
            state["stop_reason"] = "接口隔离检查未通过。"
        elif state["failures"]:
            state["status"] = "INSUFFICIENT_DATA"
            state["stop_reason"] = "身份联结完成，但站点或可评价日没有达到冻结门槛。"
        else:
            state["status"] = "PASS_P0"
            state["stop_reason"] = ""
    refused = [item for item in isolation["checks"] if item["check"].startswith("training_refuses_") and item["ok"]]
    state["isolation_text"] = "训练读取拒绝检查通过 " + str(len(refused)) + " 项。完整接口结果见 ISOLATION_CHECK.md。预测不变性未运行。"
    write_json(ROOT / "protocol_freeze.json", protocol_document())
    write_json(ROOT / "linkage_summary.json", {
        "old_conflict_keys": link_counts["old_conflict_keys"],
        "old_conflict_sites": link_counts["old_conflict_sites"],
        "old_conflict_dates": link_counts["old_conflict_dates"],
        "old_conflict_rows": link_counts["old_conflict_rows"],
        "rows_in_scope": link_counts["rows_in_scope"],
        "rows_unique": link_counts["rows_unique"],
        "rows_same_value": link_counts["rows_same_value"],
        "rows_zero": link_counts["rows_zero"],
        "not_single_source_rows": link_counts["not_single_source_rows"],
        "review_matches_section_3": link_counts["review_ok"],
        "rows_unresolved": link_counts["rows_unresolved"],
        "unresolved_source_rows": link_counts["unresolved_source_rows"],
        "epa_multi_mean_keys": link_counts["epa_multi_mean_keys"],
        "event_value_collisions": link_counts["event_value_collisions"],
        "sensor_conflicts": link_counts["sensor_conflicts"],
        "units": link_counts["units"],
        "epa_kept": {"88101": state["epa"]["88101"]["kept"], "88502": state["epa"]["88502"]["kept"]},
    })
    write_audit(state)
    write_failure(state)
    write_next_stage(state)
    write_readme()
    versions = {"python": sys.version, "GPU": False, "threads": 1, "memory_meter": "kernel32 K32GetProcessMemoryInfo working set"}
    for module_name in ("numpy", "pandas", "sklearn", "psutil"):
        try:
            module = __import__(module_name)
            versions[module_name] = getattr(module, "__version__", "present")
        except Exception:
            versions[module_name] = "not_imported"
    write_json(ROOT / "environment.json", versions)
    status_doc = {
        "status": state["status"],
        "P1": "NOT_RUN",
        "panel": state["panel"],
        "training": False,
        "prediction_invariance": "NOT_RUN",
        "unresolved_source_rows": link_counts["unresolved_source_rows"],
        "review_matches_section_3": link_counts["review_ok"],
        "same_value_multi_monitor_rows": link_counts["rows_same_value"],
        "zero_identity_rows": link_counts["zero_identity_rows"],
        "excluded_ambiguous_monitor_days": state["exclusion_counts"].get("EXCLUDED_AMBIGUOUS_MONITOR") if state.get("panel") == "WRITTEN" else None,
        "excluded_unresolved_days": state["exclusion_counts"].get("EXCLUDED_UNRESOLVED_ROW") if state.get("panel") == "WRITTEN" else None,
        "named_unresolved_row_only": link_counts["unresolved_source_rows"] == [8402],
        "screened": state["screened"] and state.get("panel") == "WRITTEN",
        "failures": state["failures"],
        "fixed_sites": None if state["stats"] is None else state["stats"]["fixed_sites"],
        "West_sites": None if state["stats"] is None else state["stats"]["West_sites"],
        "North_sites": None if state["stats"] is None else state["stats"]["North_sites"],
        "V_evaluable_days": None if state["stats"] is None else state["stats"]["V_evaluable_days"],
        "T_evaluable_days": None if state["stats"] is None else state["stats"]["T_evaluable_days"],
        "T_blocks": None if state["stats"] is None else state["stats"]["T_blocks"],
        "T_block_indices": None if state["stats"] is None else state["stats"]["T_block_indices"],
        "isolation_passed": isolation["passed"],
    }
    write_json(ROOT / "P0_status.json", status_doc)
    state["status_doc"] = status_doc


def assert_published_boundaries():
    with (ROOT / "row_linkage.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["split"] in ("A", "T") and row["pm25fm_exported"] != "":
                raise RuntimeError("A/T concentration written to row_linkage")
            if row["link_status"] == "SAME_VALUE_MULTI_MONITOR" and (row["poc"] or row["event_id"] or row["method_code"]):
                raise RuntimeError("same-value row designated one monitor")
    with (ROOT / "same_value_multimonitor_rows.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["split"] in ("A", "T") and row["pm25fm_exported"] != "":
                raise RuntimeError("A/T concentration written to same-value table")
            if " || " not in row["ordered_event_keys"]:
                raise RuntimeError("same-value row does not retain multiple keys")
    with (ROOT / "reference_events_metadata.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("split") in ("A", "T") and row.get("reference_value", "") != "":
                raise RuntimeError("A/T concentration written to metadata")
            if row.get("n_keys") and int(row["n_keys"]) > 1:
                if row["ordered_event_keys"].count(" || ") + 1 != int(row["n_keys"]):
                    raise RuntimeError("billing metadata collapsed monitors")
                if row["billing_key"] != row["ordered_event_keys"]:
                    raise RuntimeError("billing key is not the full ordered set")
    for path, forbidden in (
        (ROOT / "evaluation_panel.csv", ("pm25", "reference")),
        (ROOT / "excluded_device_days.csv", ("pm25", "reference_value")),
    ):
        header = path.read_text(encoding="utf-8").splitlines()[0].lower()
        for token in forbidden:
            if token in header:
                raise RuntimeError(path.name + " header contains " + token)


def write_resource(state, cpu_seconds, wall_seconds, guard):
    inherited = 12.765625
    lines = [json.dumps({
        "stage": "inherited_cpu_total",
        "cpu_s": inherited,
        "components_cpu_s": [7.53125, 5.234375],
        "component_notes": [
            "7.53125 = p0_p1 metered 3.40625 + identity extract 3.96875 + linkage 0.15625",
            "5.234375 = p0_redo_20261022_193538 metered total, including its header and method inspections",
        ],
        "download_wall_s": 16.702,
        "download_is_cpu": False,
        "deducted_from_this_round_budget": False,
    }, ensure_ascii=False)]
    lines.append(json.dumps({
        "stage": "P0_same_value_screen_prepare_data",
        "cpu_s": cpu_seconds,
        "wall_s": wall_seconds,
        "peak_rss_bytes": guard.peak_rss,
        "min_available_bytes": guard.min_available,
        "status": state.get("status"),
        "meter": "process_time plus Windows working set; single process",
    }, ensure_ascii=False))
    lines.append(json.dumps({
        "stage": "P0_same_value_screen_this_round_total",
        "cpu_s": cpu_seconds,
        "wall_s": wall_seconds,
        "includes_inherited_cpu": False,
        "cap_cpu_s": 300,
        "cap_wall_s": 900,
    }, ensure_ascii=False))
    (ROOT / "resource_ledger.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    paused = state.get("status") == "RESOURCE_PAUSE"
    text = "\n".join([
        "# 资源与预算",
        "",
        "继承 CPU 写在账本开头，不从本轮 300 秒里扣除。",
        "",
        "| 项目 | CPU 秒 | 墙钟秒 | 内存 |",
        "| --- | ---: | ---: | --- |",
        "| 继承：p0_p1 计量部分 | 7.53125 | 下载 16.702 不计 CPU | 见原账本 |",
        "| 继承：p0_redo_20261022_193538 | 5.234375 | 6.032518 | 峰值 RSS 227020800 字节 |",
        "| 继承合计 | 12.765625 | 不计入本轮上限 | 不从 300 秒扣除 |",
        "| 本轮 prepare_data | " + format(cpu_seconds, ".6f") + " | " + format(wall_seconds, ".6f") + " | 峰值 RSS " + str(guard.peak_rss) + " 字节；最低可用 " + str(guard.min_available) + " 字节 |",
        "| 本轮合计 | " + format(cpu_seconds, ".6f") + " | " + format(wall_seconds, ".6f") + " | 同上 |",
        "",
        "本轮上限是新增 300 CPU 秒、900 计算墙钟秒。进程 RSS 上限 1.5 GiB，可用内存连续 30 秒低于 1.5 GiB 则暂停。"
        + ("本轮触发了资源暂停。" if paused else "本轮没有触发这些上限。"),
        "",
        "没有使用 GPU，没有开多进程。EPA 文件按行读取，只保留目标站点窗口内的记录。",
        "",
    ])
    (ROOT / "RESOURCE_AND_BUDGET.md").write_text(text, encoding="utf-8")
    if "status_doc" in state:
        state["status_doc"]["this_round_cpu_s"] = cpu_seconds
        state["status_doc"]["this_round_wall_s"] = wall_seconds
        state["status_doc"]["inherited_cpu_s"] = inherited
        state["status_doc"]["peak_rss_bytes"] = guard.peak_rss
        state["status_doc"]["min_available_bytes"] = guard.min_available
        write_json(ROOT / "P0_status.json", state["status_doc"])


def main():
    cpu_start = time.process_time()
    wall_start = time.perf_counter()
    guard = Guard()
    state = {"status": None, "panel": "NOT_RUN", "screened": False, "stop_reason": "", "failures": []}
    try:
        run(state, guard, cpu_start)
    except ResourcePause as exc:
        state["status"] = "RESOURCE_PAUSE"
        state["panel"] = "NOT_RUN"
        state["stop_reason"] = str(exc)
        write_json(ROOT / "P0_status.json", {"status": "RESOURCE_PAUSE", "P1": "NOT_RUN", "panel": "NOT_RUN", "reason": str(exc)})
        (ROOT / "FAILURE_REPORT.md").write_text("# 资源暂停\n\n" + str(exc) + "\n\nP1：`NOT_RUN`。\n", encoding="utf-8")
    except Exception:
        (ROOT / "implementation_error.txt").write_text(traceback.format_exc(), encoding="utf-8")
        state["status"] = "IMPLEMENTATION_ERROR"
        raise
    finally:
        guard.check()
        write_resource(state, time.process_time() - cpu_start, time.perf_counter() - wall_start, guard)
    print(json.dumps({"status": state.get("status"), "panel": state.get("panel"), "screened": state.get("screened")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
