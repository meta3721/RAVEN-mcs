"""Steps 2-5 of the reachability attribution. Stops when a registered check fails."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from m1_distance import distance

ROOT = Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_m1_attribution" / "round_v1"
TRACE = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
MU_PATH = OUT / "M1_MU.json"
P0_WINDOWS = ROOT / "results_xw_pool" / "round_v1" / "P0_WINDOWS.csv"
MASS_TOL = 1e-8
DIST_TOL = 1e-6
ADJ_THRESHOLD = 0.01
RNG_SEED = 20261019
N_BOOT = 10000

BLOCKS = ("NSW-Traffic", "SensorScope", "U-Air")
FOLDERS = {
    "NSW-Traffic": TRACE / "traffic",
    "SensorScope": TRACE / "sensorscope",
    "U-Air": TRACE / "uair",
}
BLOCKED = {
    "City Scanner 访问占用": (
        "opportunity_features 没有组字段（没有 stratum、hour_block 或 target_group）。"
        "s_max=5 在 generation_meta 里。没有使用冻结 mu 文件"
    ),
    "City Scanner Pilot 2": (
        "存在 target_group_by_unit，元数据里有 s_max=5，但没有 region0-3 的冻结 mu。"
        "没有假定均匀 0.25"
    ),
    "T-Drive": "opportunity_features 没有组字段。没有使用微型夹具。没有套用冻结 mu 文件",
}
WINDOW_FIELDS = [
    "block",
    "seed",
    "window",
    "K",
    "n_groups",
    "row_type",
    "off_target_clients",
    "mu_miss",
    "mu_pin",
    "mu_adj",
    "mu_positive",
    "d_simplex",
    "d_cap",
    "d_ess",
    "d_C",
    "inc_cap",
    "inc_ess",
    "inc_joint",
]
MEAN_FIELDS = [
    "mu_miss",
    "mu_pin",
    "mu_adj",
    "d_simplex",
    "d_cap",
    "d_ess",
    "d_C",
    "inc_cap",
    "inc_ess",
    "inc_joint",
    "n_groups",
    "onehot",
]


def group_from_features(text: str, mu: dict[str, float]) -> str:
    payload = json.loads(text)
    if "hour_block" in payload:
        key = str(int(payload["hour_block"]))
        if key in mu:
            return key
    for key_name in ("processed_target_group", "target_group_h", "h_id", "target_group"):
        if key_name in payload and str(payload[key_name]) in mu:
            return str(payload[key_name])
    stratum = str(payload.get("opportunity_stratum", ""))
    parts = [p for p in stratum.split("::") if p]
    block = None
    spatial = None
    for part in parts:
        if part.startswith("block"):
            block = part.replace("block", "")
        elif part not in {"weekend", "weekday"}:
            spatial = part
    candidates = []
    if spatial is not None and block is not None:
        candidates.append(f"{spatial}::block{block}")
    if block is not None:
        candidates.append(block)
    for cand in candidates:
        if cand in mu:
            return cand
    if "target_group_by_unit" in payload:
        labels = {str(v) for v in payload["target_group_by_unit"].values()}
        if len(labels) == 1 and next(iter(labels)) in mu:
            return next(iter(labels))
        raise KeyError("attempt group is not a single frozen mu key")
    raise KeyError(stratum or "no group field")


def feasible_interval(n_in: int, n_out: int) -> tuple[float, float]:
    if n_in < 0 or n_out < 0 or n_in + n_out <= 0:
        raise ValueError("empty client set")
    if n_out == 0:
        return 1.0, 1.0
    if n_in == 0:
        return 0.0, 0.0
    box_lo = max(0.0, 1.0 - 0.5 * n_out)
    box_hi = min(1.0, 0.5 * n_in)
    a_coef = 1.0 / n_in + 1.0 / n_out
    b_coef = -2.0 / n_out
    c_coef = 1.0 / n_out - 1.0 / 3.0
    disc = b_coef * b_coef - 4.0 * a_coef * c_coef
    if disc < 0 or box_lo > box_hi:
        return 0.0, 0.0
    root = disc ** 0.5
    r1 = (-b_coef - root) / (2.0 * a_coef)
    r2 = (-b_coef + root) / (2.0 * a_coef)
    lo = max(box_lo, min(r1, r2))
    hi = min(box_hi, max(r1, r2))
    if lo > hi + 1e-12:
        return 0.0, 0.0
    return lo, hi


def normalized_mu() -> dict[str, dict[str, float]]:
    raw = json.loads(MU_PATH.read_text(encoding="utf-8"))
    out = {}
    for name in BLOCKS:
        entry = raw[name]
        total = float(entry["sum"])
        if total <= 0:
            raise RuntimeError(f"{name} sum is not positive")
        out[name] = {str(k): float(v) / total for k, v in entry["mu"].items()}
    return out


def split_mass(groups: list[str], mu: dict[str, float]) -> dict[str, float]:
    k = len(groups)
    counts: dict[str, int] = defaultdict(int)
    off = 0
    for group in groups:
        if group not in mu or mu[group] <= 0.0:
            off += 1
            continue
        counts[group] += 1
    miss = pin = adj = positive = 0.0
    for group, mass in mu.items():
        if mass <= 0.0:
            continue
        positive += mass
        n_in = counts.get(group, 0)
        if n_in == 0:
            miss += mass
            continue
        if k <= 3:
            pin += mass
            continue
        lo, hi = feasible_interval(n_in, k - n_in)
        if hi - lo >= ADJ_THRESHOLD:
            adj += mass
        else:
            pin += mass
    return {
        "mu_miss": miss,
        "mu_pin": pin,
        "mu_adj": adj,
        "mu_positive": positive,
        "off_target_clients": off,
    }


def deviations(row: dict) -> list[str]:
    found = []
    mass_gap = row["mu_miss"] + row["mu_pin"] + row["mu_adj"] - row["mu_positive"]
    if abs(mass_gap) > MASS_TOL:
        found.append(f"mass gap {mass_gap}")
    if row["K"] <= 3 and row["mu_adj"] != 0.0:
        found.append(f"K<=3 mu_adj {row['mu_adj']}")
    if row["row_type"] != "mixed":
        ident = row["d_simplex"] - 2.0 * row["mu_miss"]
        if abs(ident) > DIST_TOL:
            found.append(f"one-hot gap {ident}")
    order = (
        ("d_cap", "d_simplex"),
        ("d_C", "d_cap"),
        ("d_ess", "d_simplex"),
        ("d_C", "d_ess"),
    )
    for left, right in order:
        gap = row[right] - row[left]
        if gap > DIST_TOL:
            found.append(f"{left} < {right} by {gap}")
    return found


def evaluate_window(groups: list[str], mu: dict[str, float], window: int) -> dict:
    k = len(groups)
    alpha_bar = min(1.0, max(0.5, 1.0 / k))
    e_bar = min(3.0, float(k))
    masses = split_mass(groups, mu)
    d_simplex = distance(groups, mu, alpha_bar, e_bar, "simplex")
    d_cap = distance(groups, mu, alpha_bar, e_bar, "cap")
    d_ess = distance(groups, mu, alpha_bar, e_bar, "ess")
    d_c = distance(groups, mu, alpha_bar, e_bar, "C")
    row = {
        "window": window,
        "K": k,
        "n_groups": len(set(groups)),
        "row_type": "onehot",
        **masses,
        "d_simplex": d_simplex,
        "d_cap": d_cap,
        "d_ess": d_ess,
        "d_C": d_c,
        "inc_cap": d_cap - d_simplex,
        "inc_ess": d_ess - d_simplex,
        "inc_joint": d_c - max(d_cap, d_ess),
    }
    return row


def load_seed(path: Path, mu: dict[str, float], first_only: bool = False) -> list[dict]:
    table = pq.read_table(
        path,
        columns=["window_id", "client_id", "downloaded_version", "U", "opportunity_features"],
    )
    rows = table.to_pydict()
    seen = set()
    by_window: dict[int, list[dict]] = defaultdict(list)
    for i, flag in enumerate(rows["U"]):
        if int(flag) != 1:
            continue
        client = str(rows["client_id"][i])
        sigma = int(rows["downloaded_version"][i])
        arrived = int(rows["window_id"][i])
        ident = (client, sigma, arrived)
        if ident in seen:
            raise RuntimeError(f"duplicate attempt identity {ident}")
        seen.add(ident)
        group = group_from_features(rows["opportunity_features"][i], mu)
        by_window[arrived].append({"client": client, "sigma": sigma, "group": group})
    out = []
    for arrived in sorted(by_window):
        best: dict[str, dict] = {}
        for attempt in by_window[arrived]:
            current = best.get(attempt["client"])
            if current is None or attempt["sigma"] > current["sigma"]:
                best[attempt["client"]] = attempt
        groups = [item["group"] for item in best.values()]
        if not groups:
            continue
        out.append(evaluate_window(groups, mu, arrived))
        if first_only:
            break
    return out


def write_status(payload: dict) -> None:
    (OUT / "M1_STATUS.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def base_status() -> dict:
    payload = {
        "void_windows": 0,
        "estimate": "blocked",
        "estimate_reason": "",
    }
    for name, reason in BLOCKED.items():
        payload[name] = {"status": "blocked", "geometry": "blocked", "estimate": "blocked", "void_windows": 0, "reason": reason}
    return payload


def smoke(mu: dict[str, float]) -> tuple[bool, str]:
    path = TRACE / "traffic" / "seed30001" / "training_eventtrace" / "events.parquet"
    try:
        windows = load_seed(path, mu, first_only=True)
    except Exception as exc:
        return False, f"窗口未能计算。{type(exc).__name__}: {exc}\n没有进入第 3 步。没有计算 RMSE。\n"
    if not windows:
        return False, "NSW-Traffic seed30001 produced no K>=1 close."
    row = windows[0]
    found = deviations(row)
    if found:
        text = (
            f"窗口 {row['window']}。冒烟失败。\n"
            + "\n".join(found)
            + "\n没有进入第 3 步。没有计算 RMSE。\n"
        )
        return False, text
    text = (
        f"窗口 {row['window']}。\n"
        "成立：质量三项之和与该窗正目标质量之差不超过 1e-8；"
        "d_C 不小于 d_simplex；"
        "K<=3 时 mu_adj 为 0；"
        "独热恒等式；"
        "距离单调性。\n"
        "没有写下该窗的质量或距离。没有计算 RMSE。\n"
        "通过只说明脚本读进了 NSW-Traffic seed30001 的这条轨迹。\n"
    )
    return True, text


def bootstrap_interval(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    n = len(values)
    draws = values[rng.integers(0, n, size=(N_BOOT, n))].mean(axis=1)
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def summarize(rows: list[dict]) -> list[dict]:
    rng = np.random.default_rng(RNG_SEED)
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        layer = "K<=3" if int(row["K"]) <= 3 else "K>3"
        grouped[(row["block"], layer, row["seed"])].append(row)
    summary = []
    for block in BLOCKS:
        for layer in ("K<=3", "K>3"):
            seed_names = sorted({seed for (name, lay, seed) in grouped if name == block and lay == layer})
            record: dict[str, object] = {
                "block": block,
                "layer": layer,
                "n_seeds": len(seed_names),
                "n_windows": sum(len(grouped[(block, layer, seed)]) for seed in seed_names),
            }
            if not seed_names:
                for field in MEAN_FIELDS:
                    record[field] = ""
                for field in ("mu_miss", "mu_pin", "mu_adj", "d_simplex", "d_cap", "d_ess", "d_C"):
                    record[f"{field}_lo"] = ""
                    record[f"{field}_hi"] = ""
                summary.append(record)
                continue
            seed_means = {field: [] for field in MEAN_FIELDS}
            for seed in seed_names:
                items = grouped[(block, layer, seed)]
                for field in MEAN_FIELDS:
                    if field == "onehot":
                        seed_means[field].append(
                            sum(1.0 for item in items if item["row_type"] == "onehot") / len(items)
                        )
                    else:
                        seed_means[field].append(float(np.mean([item[field] for item in items])))
            for field in MEAN_FIELDS:
                record[field] = float(np.mean(seed_means[field]))
            for field in ("mu_miss", "mu_pin", "mu_adj", "d_simplex", "d_cap", "d_ess", "d_C"):
                lo, hi = bootstrap_interval(np.array(seed_means[field], dtype=float), rng)
                record[f"{field}_lo"] = lo
                record[f"{field}_hi"] = hi
            summary.append(record)
    return summary


def align_p0(rows: list[dict]) -> tuple[bool, str, float]:
    p0: dict[tuple[str, str, int], float] = {}
    with P0_WINDOWS.open(encoding="utf-8", newline="") as handle:
        for item in csv.DictReader(handle):
            if item["block"] not in BLOCKS:
                continue
            key = (item["block"], item["seed"], int(float(item["window"])))
            p0[key] = float(item["adj_A"])
    ours = {(row["block"], row["seed"], int(row["window"])): float(row["mu_adj"]) for row in rows}
    missing_here = sorted(set(p0) - set(ours))
    missing_there = sorted(set(ours) - set(p0))
    if missing_here or missing_there:
        return False, f"window set mismatch missing_in_m1={len(missing_here)} missing_in_p0={len(missing_there)}", float("nan")
    gaps = [abs(p0[key] - ours[key]) for key in p0]
    worst = max(gaps) if gaps else 0.0
    if worst > MASS_TOL:
        return False, f"mu_adj differs from adj_A by {worst}", worst
    return True, "aligned", worst


def estimate_available(paths: list[Path]) -> str:
    reasons = []
    for path in paths:
        schema = pq.read_schema(path)
        vector_columns = []
        for field in schema:
            type_name = str(field.type)
            if type_name.startswith(("list", "large_list", "struct", "map")):
                vector_columns.append(field.name)
        seed_dir = path.parents[1]
        trace_dir = path.parent
        sidecars = {
            "metadata": trace_dir / "metadata.json",
            "trace_identity": trace_dir / "trace_identity.json",
            "provenance": seed_dir / "e2_reuse_provenance.json",
        }
        for label, sidecar in sidecars.items():
            if not sidecar.is_file():
                reasons.append(f"{seed_dir.name} missing {label}")
                continue
            obj = json.loads(sidecar.read_text(encoding="utf-8"))
            if _contains_aligned_vector(obj):
                return f"found a candidate vector in {sidecar}"
        if vector_columns:
            return f"{seed_dir.name} has non-scalar columns {vector_columns}"
    return ""


def _contains_aligned_vector(obj: object) -> bool:
    if isinstance(obj, dict):
        numeric_keys = 0
        for key, value in obj.items():
            if key in {"source", "mode"}:
                continue
            if isinstance(value, list) and len(value) > 1 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value):
                return True
            if _contains_aligned_vector(value):
                return True
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_keys += 1
        return False
    if isinstance(obj, list):
        return any(_contains_aligned_vector(item) for item in obj)
    return False


def write_rows(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    mu = normalized_mu()
    status = base_status()
    ok, smoke_text = smoke(mu["NSW-Traffic"])
    (OUT / "M1_SMOKE.md").write_text(smoke_text, encoding="utf-8")
    if not ok:
        for name in BLOCKS:
            status[name] = {"status": "stopped", "geometry": "stopped", "estimate": "blocked", "void_windows": 0, "reason": "smoke failed"}
        status["round"] = "stopped"
        write_status(status)
        return

    window_rows: list[dict] = []
    for name in BLOCKS:
        folder = FOLDERS[name]
        paths = sorted(folder.glob("seed*/training_eventtrace/events.parquet"))
        if not paths:
            status[name] = {"status": "blocked", "geometry": "blocked", "estimate": "blocked", "void_windows": 0, "reason": f"no events.parquet under {folder}"}
            continue
        block_rows: list[dict] = []
        try:
            for path in paths:
                seed = path.parents[1].name
                seed_count = 0
                for row in load_seed(path, mu[name]):
                    found = deviations(row)
                    if found:
                        status[name] = {
                            "status": "stopped",
                            "geometry": "stopped",
                            "estimate": "blocked",
                            "void_windows": 1,
                            "reason": f"{seed} window {row['window']}: " + "; ".join(found),
                        }
                        status["void_windows"] = 1
                        status["round"] = "stopped"
                        write_status(status)
                        print("STOP", name, seed, row["window"])
                        return
                    block_rows.append({"block": name, "seed": seed, **row})
                    seed_count += 1
                print("seed", name, seed, "windows", seed_count)
        except Exception as exc:
            kind = "blocked" if isinstance(exc, KeyError) else "stopped"
            status[name] = {
                "status": kind,
                "geometry": kind,
                "estimate": "blocked",
                "void_windows": 0 if kind == "blocked" else 1,
                "reason": f"{type(exc).__name__}: {exc}",
            }
            if kind == "stopped":
                status["void_windows"] = 1
                status["round"] = "stopped"
                write_status(status)
                print("STOP", name, exc)
                return
            print("BLOCKED", name, exc)
            continue
        window_rows.extend(block_rows)
        status[name] = {"status": "pending_align", "geometry": "pending_align", "estimate": "blocked", "void_windows": 0}

    write_rows(OUT / "M1_WINDOWS.csv", window_rows, WINDOW_FIELDS)
    matched, message, worst = align_p0(window_rows)
    if not matched:
        for name in BLOCKS:
            if status.get(name, {}).get("status") == "pending_align":
                status[name] = {"status": "stopped", "geometry": "stopped", "estimate": "blocked", "void_windows": 0, "reason": message}
        status["round"] = "stopped"
        status["align"] = message
        write_status(status)
        print("STOP align", message)
        return

    summary = summarize(window_rows)
    summary_fields = [
        "block",
        "layer",
        "n_seeds",
        "n_windows",
        *MEAN_FIELDS,
        "mu_miss_lo",
        "mu_miss_hi",
        "mu_pin_lo",
        "mu_pin_hi",
        "mu_adj_lo",
        "mu_adj_hi",
        "d_simplex_lo",
        "d_simplex_hi",
        "d_cap_lo",
        "d_cap_hi",
        "d_ess_lo",
        "d_ess_hi",
        "d_C_lo",
        "d_C_hi",
    ]
    write_rows(OUT / "M1_SUMMARY.csv", summary, summary_fields)
    used_paths = []
    for name in BLOCKS:
        if status.get(name, {}).get("status") != "pending_align":
            continue
        used_paths.extend(sorted(FOLDERS[name].glob("seed*/training_eventtrace/events.parquet")))
    found_vector = estimate_available(used_paths)
    estimate_reason = (
        found_vector
        if found_vector
        else "列名和三份侧车文件里没有与窗口客户端行对齐的组向量。oracle_p 与 oracle_q 是标量，没有当作参考。没有打开 provenance 指向的源目录，没有拟合 q。"
    )
    write_rows(
        OUT / "M1_ESTIMATE.csv",
        [],
        ["block", "seed", "window", "delta_ref", "delta_dec"],
    )
    for name in BLOCKS:
        if status.get(name, {}).get("status") == "pending_align":
            status[name] = {
                "status": "complete",
                "geometry": "complete",
                "estimate": "blocked",
                "void_windows": 0,
                "reason": estimate_reason,
            }
    status["estimate"] = "blocked"
    status["estimate_reason"] = estimate_reason
    status["align_max_abs"] = worst
    status["round"] = "complete"
    status["void_windows"] = 0
    write_status(status)
    print("DONE", "windows", len(window_rows), "align", worst)


if __name__ == "__main__":
    main()
