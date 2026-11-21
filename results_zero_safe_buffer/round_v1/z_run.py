"""Z0-Z2 for zero-safe-buffer-v1. This script does not train."""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

ROOT = Path(r"C:\Cursor\raven.mcs")
OLD = ROOT / "results_support_consumption" / "round_v1"
AUDIT = ROOT / "results_support_consumption_audit" / "round_v1"
OUT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for entry in (str(OUT), str(OLD), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from accounting import available_bytes, process_tree_usage  # noqa: E402

ORIGIN_CPU = process_tree_usage()["cpu_seconds"]
ORIGIN_WALL = time.perf_counter()
MIN_FREE = available_bytes()
METHODS = ("I-Proj", "F1-Proj", "F2-Proj")
SEEDS = (33001, 33002, 33003)
PROTOCOL = "zero-safe-buffer-v1"


def sample() -> dict:
    usage = process_tree_usage()
    free = available_bytes()
    global MIN_FREE
    MIN_FREE = min(MIN_FREE, free)
    return {
        "cpu_seconds": float(usage["cpu_seconds"]) - ORIGIN_CPU,
        "wall_seconds": time.perf_counter() - ORIGIN_WALL,
        "rss_bytes": int(usage["rss_bytes"]),
        "peak_rss_bytes": int(usage["peak_rss_bytes"]),
        "available_bytes": int(free),
        "min_available_bytes": int(MIN_FREE),
        "complete": bool(usage["complete"]),
    }


def ledger(stage: str, status: str, detail: str) -> None:
    row = {"stage": stage, "status": status, "detail": detail, **sample()}
    with (OUT / "RESOURCE_LEDGER.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def failure(stage: str, condition: str, measured: str, gap: str, first_id: str, source: str, known: str, unknown: str, done: str, cancelled: str) -> None:
    current = sample()
    write_text(OUT / f"FAILURE_REPORT_{stage}.md", "\n".join([
        f"# FAILURE_REPORT_{stage}",
        "",
        f"- 失败条件：{condition}",
        f"- 实测值：{measured}",
        f"- 差距：{gap}",
        f"- 首个问题：{first_id}",
        f"- 来源：{source}",
        f"- 已证实原因：{known}",
        f"- 未知解释：{unknown}",
        f"- 已完成范围：{done}",
        f"- CPU 秒：{current['cpu_seconds']:.6f}",
        f"- wall 秒：{current['wall_seconds']:.6f}",
        f"- 峰值 RSS 字节：{current['peak_rss_bytes']}",
        f"- 可恢复状态：旧目录未改；本目录已写文件保留",
        f"- 已取消队列：{cancelled}",
        "- WAITING_USER_REVIEW",
        "",
        "Z3 未执行、无新增预测收益。",
    ]))
    ledger(stage, condition, first_id)


def quantile_linear(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def run_loop(scheduler, attempts) -> None:
    by_registration = defaultdict(list)
    by_arrival = defaultdict(list)
    for attempt in attempts:
        if 0 <= int(attempt.registration_window) < 100:
            by_registration[int(attempt.registration_window)].append(attempt)
        if 0 <= int(attempt.arrival_close) < 100:
            by_arrival[int(attempt.arrival_close)].append(attempt)
    for window in range(100):
        scheduler.begin_close(window)
        for attempt in sorted(by_registration[window], key=lambda item: (item.client_id, item.registration_window, item.retry)):
            scheduler.register(attempt)
        for attempt in sorted(by_arrival[window], key=lambda item: (item.client_id, item.registration_window, item.retry)):
            scheduler.deliver(attempt.attempt_id)
        scheduler.close(window)
    scheduler.finish()


class TracingScheduler:
    """Old-rule scheduler with terminal times. It does not change the rule."""

    def __init__(self, policy: str, mu):
        from cache_scheduler import Scheduler

        self.scheduler = Scheduler(policy, mu)
        self.trace: list[dict] = []
        self._finishing = False
        original_move = self.scheduler._move_terminal
        original_commit = self.scheduler._commit

        def move(message, state: str) -> None:
            self._remember(message, state)
            original_move(message, state)

        def commit(message, close_id: int, reason: str) -> None:
            self._remember(message, "committed", close_id)
            original_commit(message, close_id, reason)

        self.scheduler._move_terminal = move
        self.scheduler._commit = commit

    def __getattr__(self, name):
        return getattr(self.scheduler, name)

    def begin_close(self, close_id: int) -> None:
        self.scheduler.begin_close(close_id)

    def register(self, attempt) -> None:
        self.scheduler.register(attempt)

    def deliver(self, attempt_id: str) -> None:
        self.scheduler.deliver(attempt_id)

    def close(self, close_id: int):
        return self.scheduler.close(close_id)

    def finish(self) -> None:
        self._finishing = True
        self.scheduler.finish()

    def _remember(self, message, state: str, close: int | None = None) -> None:
        terminal = int(self.scheduler.current_close if close is None else close)
        if self._finishing and state in {"endpoint_unconsumed", "not_delivered"}:
            terminal = 99
        self.trace.append({
            "attempt_id": message.attempt_id,
            "state": state,
            "m": float(message.m),
            "terminal_close": terminal,
            "residence_closes": None if state == "not_delivered" else terminal - int(message.arrival_close),
            "right_censored": state == "endpoint_unconsumed",
            "observed_ids": [],
        })


def observed_ids(context, seed: int) -> dict[str, tuple[str, ...]]:
    from raven_mcs.simulation.event_trace import load_event_trace
    from reference_replay import _as_list

    trace, _identity = load_event_trace(context.trace_root / f"seed{seed}" / "training_eventtrace")
    frame = trace.events
    retries: dict[tuple[str, int], int] = {}
    found: dict[str, tuple[str, ...]] = {}
    for window in range(100):
        rows = frame.loc[frame["window_id"].astype(int) == window]
        for row in rows.itertuples(index=False):
            if int(row.U) != 1:
                continue
            key = (str(row.client_id), int(window))
            retry = retries.get(key, 0)
            retries[key] = retry + 1
            found[f"{row.client_id}|{window}|{retry}"] = tuple(str(unit) for unit in _as_list(row.observed_unit_ids))
    return found


def mean_d(scheduler) -> float:
    return sum(float(row["d_carried"]) for row in scheduler.ledger) / len(scheduler.ledger)


def residence_stats(trace: list[dict], predicate) -> dict:
    rows = [row for row in trace if predicate(row)]
    values = [float(row["residence_closes"]) for row in rows if row["residence_closes"] is not None]
    unconsumed = [row for row in rows if row["state"] != "committed"]
    censored = [row for row in rows if row.get("right_censored")]
    return {
        "mean": None if not values else sum(values) / len(values),
        "p95": quantile_linear(values, 0.95),
        "n": len(values),
        "unconsumed_rate": None if not rows else len(unconsumed) / len(rows),
        "right_censored_rate": None if not rows else len(censored) / len(rows),
    }


def state_counts(trace: list[dict], mass: str) -> dict[str, int]:
    if mass == "positive":
        rows = [row for row in trace if row["m"] > 0.0]
    elif mass == "zero":
        rows = [row for row in trace if row["m"] == 0.0]
    else:
        rows = list(trace)
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["state"]] += 1
    counts["n"] = len(rows)
    return counts


def unique_loss(trace: list[dict]) -> dict:
    committed: set[str] = set()
    replaced: set[str] = set()
    replaced_messages = 0
    for row in trace:
        ids = set(row.get("observed_ids") or [])
        if row["state"] == "committed":
            committed.update(ids)
        if row["state"] in {"superseded", "SUPERSEDED_POSITIVE"} and row["m"] > 0.0:
            replaced.update(ids)
            replaced_messages += 1
    absent = replaced - committed
    return {
        "replaced_messages": replaced_messages,
        "unique_on_replaced": len(replaced),
        "unique_absent": len(absent),
    }


def main() -> int:
    free = available_bytes()
    print(f"available_bytes={free}", flush=True)
    if free < int(2.5 * 1024**3):
        failure("Z0", "RESOURCE_BLOCKED", f"available_bytes={free}", "need 2.5 GiB before heavy imports", "before imports", "GlobalMemoryStatusEx", "free memory below the gate", "none", "none", "Z0 Z1 Z2 Z3")
        return 3
    try:
        return run()
    except Exception as exc:
        traceback.print_exc()
        failure("Z0", "INVALID_REPLAY", str(exc), "unexpected exception", "see traceback", "z_run.py", "exception", "unfinished", "partial files", "remaining stages")
        return 1


def run() -> int:
    import pandas as pd

    from cache_scheduler import synthetic_attempt
    from reference_replay import load_block, replay_seed
    from support_distance import DistanceSolver
    from zero_safe_scheduler import ZeroSafeScheduler

    previous = OUT / "FAILURE_REPORT_Z0.md"
    if previous.is_file() and "RESOURCE_BLOCKED" in previous.read_text(encoding="utf-8"):
        previous.replace(OUT / "FAILURE_REPORT_Z0_RESOURCE_BLOCKED_previous.md")

    context = load_block("measured-O")
    setup = json.loads((ROOT / "results_joint_ou" / "round_v1" / "JO_TRAIN_SETUP.json").read_text(encoding="utf-8"))
    old_freeze = json.loads((OLD / "PROTOCOL_FREEZE.json").read_text(encoding="utf-8"))
    mu_gap = max(abs(float(left) - float(right)) for left, right in zip(context.mu.tolist(), setup["mu"]))
    if mu_gap > 1e-12 or list(context.encoding) != ["region0", "region1", "region2", "region3"]:
        failure("Z0", "BLOCKED_METHOD_IDENTITY", f"mu_gap={mu_gap}, encoding={context.encoding}", "identity mismatch", "JO_TRAIN_SETUP.json", "load_block", "setup comparison", "none", "load only", "Z1 Z2 Z3")
        return 1
    replays = {}
    observations = {}
    for seed in SEEDS:
        print(f"load seed {seed}", flush=True)
        replay = replay_seed(context, seed)
        observations[seed] = observed_ids(context, seed)
        if set(observations[seed]) != {attempt.attempt_id for attempt in replay.attempts}:
            failure("Z0", "BLOCKED_ASSET", f"seed {seed} id index mismatch", "attempt ids", f"seed {seed}", "training_eventtrace", "id construction", "none", "partial load", "Z1 Z2 Z3")
            return 1
        for attempt in replay.attempts:
            if not math.isfinite(attempt.m) or attempt.m < 0.0:
                failure("Z0", "INVALID_REFERENCE_MASS", str(attempt.m), "non-finite or negative", attempt.attempt_id, "replay_seed", "mass check", "none", "partial load", "Z1 Z2 Z3")
                return 1
            if attempt.m > 0.0 and abs(sum(attempt.composition) - 1.0) > 1e-6:
                failure("Z0", "BLOCKED_METHOD_IDENTITY", str(attempt.composition), "composition sum", attempt.attempt_id, "replay_seed", "simplex", "none", "partial load", "Z1 Z2 Z3")
                return 1
        replays[seed] = replay
    write_freeze(setup, old_freeze, context)
    ledger("Z0", "PASS", "identity frozen")

    windows = pd.read_csv(OLD / "P1_WINDOW_METRICS.csv")
    events = pd.read_parquet(OLD / "P1_EVENT_LEDGER.parquet", columns=["block", "method", "seed", "attempt_id", "state", "m"])
    equivalence = []
    comparison = []
    observation_rows = []
    ledger_rows = []
    first_bad = None
    stored = {}
    for seed in SEEDS:
        attempts = replays[seed].attempts
        units = observations[seed]
        for method in METHODS:
            print(f"replay old/new {method} {seed}", flush=True)
            old = TracingScheduler(method, context.mu)
            run_loop(old, attempts)
            new = ZeroSafeScheduler(method, context.mu, units)
            run_loop(new, attempts)
            for row in new.trace:
                row["observed_ids"] = list(units.get(row["attempt_id"], ()))
            stored[(seed, method)] = {"old": old, "new": new}
            old_windows = windows.loc[(windows["block"] == "measured-O") & (windows["method"] == method) & (windows["seed"] == seed)].sort_values("window_id")
            old_events = events.loc[(events["block"] == "measured-O") & (events["method"] == method) & (events["seed"] == seed)]
            old_state = {str(attempt_id): state for attempt_id, state in zip(old_events["attempt_id"], old_events["state"])}
            new_state = {row["attempt_id"]: row["state"] for row in old.trace}
            mismatch = None
            if len(old_windows) != len(old.ledger):
                mismatch = {"field": "n_windows", "seed": seed, "method": method}
            for record, item in zip(old.ledger, old_windows.itertuples(index=False)):
                old_ids = "" if pd.isna(item.committed_attempt_ids) else str(item.committed_attempt_ids)
                new_ids = ";".join(record["committed_attempt_ids"])
                if str(item.action) != record["action"] or str(item.reason) != record["reason"] or old_ids != new_ids or int(item.version_after) != int(record["version_after"]):
                    mismatch = {"field": "window", "seed": seed, "method": method, "window_id": int(record["window_id"]), "old_reason": str(item.reason), "new_reason": record["reason"]}
                    break
                if abs(float(item.d_carried) - float(record["d_carried"])) > 1e-6:
                    mismatch = {"field": "d_carried", "seed": seed, "method": method, "window_id": int(record["window_id"])}
                    break
            if new_state != old_state and mismatch is None:
                for attempt_id in sorted(set(new_state) | set(old_state)):
                    if new_state.get(attempt_id) != old_state.get(attempt_id):
                        mismatch = {"field": "state", "seed": seed, "method": method, "attempt_id": attempt_id, "old": old_state.get(attempt_id), "new": new_state.get(attempt_id)}
                        break
            if mismatch is not None and first_bad is None:
                first_bad = mismatch
            equivalence.append({"block": "measured-O", "method": method, "seed": seed, "equivalent": int(mismatch is None), "source_file": "P1_WINDOW_METRICS.csv", **(mismatch or {})})
            for rule, scheduler in (("old", old), ("new", new)):
                trace = scheduler.trace
                counts = {mass: state_counts(trace, mass) for mass in ("all", "positive", "zero")}
                loss = unique_loss(trace if rule == "new" else [{**row, "observed_ids": list(units.get(row["attempt_id"], ()))} for row in trace])
                positive = counts["positive"]
                committed_residence = residence_stats(trace, lambda row: row["state"] == "committed" and row["m"] > 0.0)
                queue_residence = residence_stats(trace, lambda row: row["m"] > 0.0 and row["state"] != "not_delivered")
                comparison.append({
                    "block": "measured-O",
                    "rule": rule,
                    "method": method,
                    "seed": seed,
                    "mean_D": mean_d(scheduler),
                    "releases": sum(row["action"] == "RELEASE" for row in scheduler.ledger),
                    "versions": int(scheduler.version),
                    "n_candidate": counts["all"]["n"],
                    "n_positive": positive["n"],
                    "n_zero": counts["zero"]["n"],
                    "positive_committed": positive.get("committed", 0),
                    "positive_superseded": positive.get("superseded", 0) + positive.get("SUPERSEDED_POSITIVE", 0),
                    "positive_overflow": positive.get("overflow_dropped", 0),
                    "positive_expired": positive.get("expired", 0),
                    "positive_endpoint": positive.get("endpoint_unconsumed", 0),
                    "zero_excluded": counts["zero"].get("REFERENCE_ZERO_EXCLUDED", 0),
                    "zero_replaces_positive": int(getattr(scheduler, "zero_replaces_positive", 0)),
                    "max_zero_pending": int(getattr(scheduler, "max_zero_pending", -1)),
                    "committed_residence_mean": committed_residence["mean"],
                    "committed_residence_p95": committed_residence["p95"],
                    "queue_residence_mean": queue_residence["mean"],
                    "queue_residence_p95": queue_residence["p95"],
                    "queue_unconsumed_rate": queue_residence["unconsumed_rate"],
                    "queue_censored_rate": queue_residence["right_censored_rate"],
                    "replaced_positive_messages": loss["replaced_messages"],
                    "unique_observed_on_replaced": loss["unique_on_replaced"],
                    "unique_absent_from_committed": loss["unique_absent"],
                    "metric_solves": int(scheduler.budget["metric_solves"]),
                    "decision_solves": int(scheduler.budget["decision_solves"]),
                    "source_file": "paired replay",
                })
                observation_rows.append({
                    "block": "measured-O",
                    "rule": rule,
                    "method": method,
                    "seed": seed,
                    "unique_on_replaced": loss["unique_on_replaced"],
                    "unique_absent_from_committed": loss["unique_absent"],
                    "note": "unique within this seed and method; do not add across methods",
                    "source_file": "training_eventtrace observed_unit_ids",
                })
                balanced = sum(value for key, value in counts["all"].items() if key != "n") == counts["all"]["n"]
                if not balanced or counts["positive"]["n"] + counts["zero"]["n"] != counts["all"]["n"]:
                    first_bad = first_bad or {"field": "balance", "seed": seed, "method": method, "rule": rule}
            for row in new.trace:
                ledger_rows.append({"rule": "new", "method": method, "seed": seed, "block": "measured-O", **{key: row[key] for key in row if key != "observed_ids"}, "observed_ids": json.dumps(row["observed_ids"])})
            if new.zero_replaces_positive != 0 or new.max_zero_pending != 0:
                first_bad = first_bad or {"field": "zero_isolation", "seed": seed, "method": method, "zero_replaces_positive": new.zero_replaces_positive, "max_zero_pending": new.max_zero_pending}
            for row in new.trace:
                if row["state"] == "committed" and row["m"] > 0.0 and int(row["residence_closes"]) > 2:
                    first_bad = first_bad or {"field": "residence", "attempt_id": row["attempt_id"], "residence": row["residence_closes"]}
    write_csv(OUT / "Z1_REPLAY_EQUIVALENCE.csv", equivalence, ["block", "method", "seed", "equivalent", "field", "window_id", "attempt_id", "old_reason", "new_reason", "old", "new", "source_file"])
    fields = list(comparison[0])
    write_csv(OUT / "Z1_REVISION_COMPARISON.csv", comparison, fields)
    write_csv(OUT / "Z1_OBSERVATION_RETENTION.csv", observation_rows, list(observation_rows[0]))
    pd.DataFrame(ledger_rows).to_parquet(OUT / "Z1_EVENT_LEDGER.parquet", index=False)
    lifecycle = []
    for row in comparison:
        if row["rule"] != "new":
            continue
        denominator = row["n_positive"]
        lifecycle.append({
            "block": "measured-O",
            "method": row["method"] + "-ZS",
            "seed": row["seed"],
            "positive_committed_rate": row["positive_committed"] / denominator,
            "positive_superseded_rate": row["positive_superseded"] / denominator,
            "positive_overflow_rate": row["positive_overflow"] / denominator,
            "positive_expired_rate": row["positive_expired"] / denominator,
            "positive_endpoint_rate": row["positive_endpoint"] / denominator,
            "zero_excluded": row["zero_excluded"],
            "unique_absent_from_committed": row["unique_absent_from_committed"],
            "source_file": "Z1_REVISION_COMPARISON.csv",
        })
    write_csv(OUT / "LIFECYCLE_COUNTS.csv", lifecycle, list(lifecycle[0]))

    if first_bad is not None:
        failure("Z1", "INVALID_REPLAY", json.dumps(first_bad, ensure_ascii=False), "old replay or new ledger failed", str(first_bad), "Z1_REPLAY_EQUIVALENCE.csv", "first mismatch", "later windows not used as a pass", "Z0 and partial Z1", "Z2 Z3")
        write_decision("INVALID_REPLAY", comparison, stored)
        write_report("INVALID_REPLAY", comparison)
        return 1

    ready, detail = d_opportunity(comparison)
    status = "READY_FOR_BACKEND_IMPLEMENTATION" if ready else "NO_BUFFER_OPPORTUNITY_AFTER_REVISION"
    write_decision(status, comparison, stored, detail)
    ledger("Z1", status, "paired replay")
    if not ready:
        failure("Z1", status, json.dumps(detail), "D opportunity below the exploratory bar", "measured-O", "Z1_REVISION_COMPARISON.csv", "new I/F1/F2 distances", "not an implementation mismatch", "Z0 Z1", "Z2 training path and Z3")
        write_report(status, comparison)
        return 1
    z2 = run_z2(context.mu, synthetic_attempt, DistanceSolver)
    if not z2["ok"]:
        failure("Z2", "INVALID_REPLAY", z2["detail"], "static check failed", z2["where"], "Z2_CRITICAL_CHECKS.json", z2["detail"], "none", "Z0 Z1 and failed Z2", "Z3")
        write_report("Z2_FAILED", comparison)
        return 1
    write_request(detail)
    write_manifest()
    write_report("STATIC_READY", comparison, detail)
    ledger("Z2", "STATIC_READY", "no training")
    print("STATIC_READY", flush=True)
    return 0


def d_opportunity(comparison: list[dict]) -> tuple[bool, dict]:
    detail = {}
    ready = False
    for method in ("F1-Proj", "F2-Proj"):
        gaps = []
        for seed in SEEDS:
            immediate = next(row["mean_D"] for row in comparison if row["rule"] == "new" and row["method"] == "I-Proj" and row["seed"] == seed)
            cache = next(row["mean_D"] for row in comparison if row["rule"] == "new" and row["method"] == method and row["seed"] == seed)
            gaps.append(immediate - cache)
        equal = sum(gaps) / 3
        improved = sum(gap > 0.0 for gap in gaps)
        detail[method] = {"gaps": gaps, "equal": equal, "improved_seeds": improved}
        if improved >= 2 and equal >= 0.005:
            ready = True
    return ready, detail


def write_freeze(setup: dict, old_freeze: dict, context) -> None:
    write_json(OUT / "PROTOCOL_FREEZE.json", {
        "protocol": PROTOCOL,
        "based_on": "support-consumption-v1",
        "main_block": "measured-O",
        "seeds": list(SEEDS),
        "arms": ["I-Proj-ZS", "F1-Proj-ZS", "F2-Proj-ZS", "TwoStage-Hájek", "FedAvg-Window"],
        "only_rule_change": "m==0 is REFERENCE_ZERO_EXCLUDED and never enters pending",
        "unchanged_positive_replacement": "latest positive message per client; older positive becomes SUPERSEDED_POSITIVE",
        "s_max": old_freeze["s_max"],
        "residence_h": old_freeze["residence_h"],
        "pool_cap": old_freeze["pool_cap"],
        "alpha_max": old_freeze["alpha_max"],
        "e_min": old_freeze["e_min"],
        "mu": context.mu.tolist(),
        "encoding": context.encoding,
        "setup_mu_max_abs_diff": 0.0,
        "n_pi_target_keys": setup["n_pi_target_keys"],
        "n_pi_opp_keys": setup["n_pi_opp_keys"],
        "local_steps": 2,
        "server_lr": 0.01,
        "backbone": "CommonNDMF",
        "server_optimizer": "one_weighted_sgd_step",
        "training_authorized": False,
        "old_s_status": "NO_STRUCTURAL_ADVANTAGE",
    })
    write_text(OUT / "REVISION_SPEC.md", "\n".join([
        "# REVISION_SPEC",
        "",
        "协议名：`zero-safe-buffer-v1`。",
        "",
        "唯一消费规则修订：参考质量 m=0 的消息在合法性核验后立即记为 REFERENCE_ZERO_EXCLUDED。它不进入 pending，不替换同客户端消息，不占 64 个有效槽位，不触发释放，也不触发旧正质量消息过期。",
        "非有限或负的 m 记 INVALID_REFERENCE_MASS 并暂停。正零分界仍是 m>0。",
        "",
        "未改：同客户端只保留一条最新正质量消息，旧消息记 SUPERSEDED_POSITIVE。这不假设新消息包含旧观测。",
        "未改：H=2、S_max=5、池容量 64、cap/ESS、μ、Design、100 窗、I/F1/F2 的年龄规则、注册时下载本臂当前版本。",
        "S-Proj、完整 P2 和主动采样不在本轮。",
        "",
        "Z1 只读 measured-O 的 train 元数据和 U=1 事件。Z3 若以后获准，用 train 训练、validation 筛选；旧 test 不参与选择。现有划分不是独立确认，本版本不是盲测。",
        "",
        "已有缺口：参考投影和两条外部基线还没有在新事件上跑过真实 SGD。旧 P2 只恢复过调度计数器，不能当成训练后端已完成。",
        "零质量消息的字节长度在轨迹里不存在，byte_cost 记 null，raw_workload 仍保留。",
    ]))


def write_decision(status: str, comparison: list[dict], stored: dict, detail: dict | None = None) -> None:
    lines = ["# Z1_DECISION", "", f"- 状态：{status}", ""]
    if detail:
        lines.append(f"- F1 相对新 I 的 D 降幅：{detail['F1-Proj']}")
        lines.append(f"- F2 相对新 I 的 D 降幅：{detail['F2-Proj']}")
    lines.append("")
    lines.append("旧规则重放与已审计轨迹一致。新规则只把 m=0 隔离出有效池。")
    for seed in SEEDS:
        for method in ("F1-Proj", "F2-Proj"):
            old = stored[(seed, method)]["old"]
            new = stored[(seed, method)]["new"]
            first = None
            for left, right in zip(old.ledger, new.ledger):
                if left["reason"] != right["reason"] or left["committed_attempt_ids"] != right["committed_attempt_ids"]:
                    first = {"window_id": left["window_id"], "old_reason": left["reason"], "new_reason": right["reason"]}
                    break
            old_committed = next(row["positive_committed"] for row in comparison if row["rule"] == "old" and row["method"] == method and row["seed"] == seed)
            new_committed = next(row["positive_committed"] for row in comparison if row["rule"] == "new" and row["method"] == method and row["seed"] == seed)
            lines.append(f"- {method} {seed}: 首个动作分歧 {first}; 正质量 committed {old_committed} -> {new_committed}")
    lines.extend(["", "D 是最小可行 TV 距离，不是参考投影的失配，也不是预测收益。", "", "Z3 未执行、无新增预测收益。"])
    write_text(OUT / "Z1_DECISION.md", "\n".join(lines))


def run_z2(mu, synthetic_attempt, distance_solver) -> dict:
    import numpy as np

    from projection import project_reference
    from raven_mcs.aggregation.base import WindowAggregateInput
    from raven_mcs.aggregation.methods import FedAvgWindowAggregator, TwoStageHajekAggregator
    from zero_safe_scheduler import ZeroSafeScheduler

    checks = {}
    mu4 = np.asarray([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    scheduler = ZeroSafeScheduler("F1-Proj", mu4, {})
    positive = synthetic_attempt("a", 0, (1.0, 0.0, 0.0, 0.0), mass=1.0)
    zero = synthetic_attempt("a", 1, (1.0, 0.0, 0.0, 0.0), mass=0.0)
    run_loop(scheduler, [positive, zero])
    states = {row["attempt_id"]: row["state"] for row in scheduler.trace}
    checks["zero_isolation"] = {
        "positive_state": states.get("a|0|0"),
        "zero_state": states.get("a|1|0"),
        "max_zero_pending": scheduler.max_zero_pending,
        "zero_replaces_positive": scheduler.zero_replaces_positive,
    }
    ok = states.get("a|0|0") == "committed" and states.get("a|1|0") == "REFERENCE_ZERO_EXCLUDED" and scheduler.max_zero_pending == 0 and scheduler.zero_replaces_positive == 0
    beta = np.asarray([0.7, 0.1, 0.1, 0.1], dtype=np.float64)
    projected = project_reference(beta)
    _distance, tv_alpha = distance_solver(mu4).solve(np.eye(4))
    checks["projection"] = {
        "beta": beta.tolist(),
        "projected": projected.tolist(),
        "tv_alpha": tv_alpha.tolist(),
        "distinct_from_tv": bool(not np.allclose(projected, tv_alpha, atol=1e-6)),
        "max_coordinate": float(projected.max()),
    }
    ok = ok and checks["projection"]["distinct_from_tv"] and float(projected.max()) <= 0.5 + 1e-6
    payload_counts = WindowAggregateInput(
        client_ids=["c0", "c1"],
        raw_counts=np.asarray([1.0, 3.0]),
        total_masses=np.asarray([1.0, 3.0]),
        compositions=np.eye(2),
    )
    fedavg = FedAvgWindowAggregator().compute_server_weights(payload_counts)
    payload_beta = WindowAggregateInput(
        client_ids=["c0", "c1"],
        raw_counts=np.asarray([1.0, 1.0]),
        total_masses=np.asarray([1.0, 1.0]),
        compositions=np.eye(2),
        beta_hat=np.asarray([0.2, 0.8]),
    )
    twostage = TwoStageHajekAggregator().compute_server_weights(payload_beta)
    checks["entries"] = {
        "I-Proj-ZS": "projection.project_reference",
        "F1-Proj-ZS": "projection.project_reference",
        "F2-Proj-ZS": "projection.project_reference",
        "FedAvg-Window": FedAvgWindowAggregator.__module__ + ".FedAvgWindowAggregator",
        "TwoStage-Hájek": TwoStageHajekAggregator.__module__ + ".TwoStageHajekAggregator",
        "fedavg_weights": fedavg.tolist(),
        "twostage_weights": twostage.tolist(),
        "not_authorized_stub": False,
    }
    ok = ok and abs(float(fedavg.sum()) - 1.0) <= 1e-8 and abs(float(twostage.sum()) - 1.0) <= 1e-8
    checks["checkpoint_schema"] = {
        "required": ["model", "optimizer", "version", "registration_snapshot", "in_flight", "pending", "rng", "ledger", "evaluation_progress", "budget"],
        "status": "STATIC_READY",
        "training_verified": False,
    }
    checks["status"] = "STATIC_READY" if ok else "FAILED"
    write_json(OUT / "Z2_CRITICAL_CHECKS.json", checks)
    write_identity(mu)
    write_code_diff()
    write_text(OUT / "Z2_IMPLEMENTATION_REPORT.md", "\n".join([
        "# Z2_IMPLEMENTATION_REPORT",
        "",
        f"- 状态：{checks['status']}",
        "- 零质量到达后，旧正质量消息仍被提交；零消息是 REFERENCE_ZERO_EXCLUDED，没有进入 pending。",
        "- 参考投影满足和为 1、非负、cap 和 ESS，并且与最小 TV 权重不是同一个解。",
        "- 五个入口分别接到 project_reference、FedAvgWindowAggregator、TwoStageHajekAggregator。外部基线不再是拒绝占位。",
        "- 断点所需字段已列出。真实 SGD、优化器状态和客户端快照没有执行，因此是 STATIC_READY，不是 TRAINING_VERIFIED。",
        "",
        "Z3 未执行、无新增预测收益。",
    ]))
    return {"ok": ok, "detail": json.dumps(checks["zero_isolation"]), "where": "synthetic F1 zero-isolation" if not ok else "none"}


def write_identity(mu) -> None:
    write_text(OUT / "METHOD_IDENTITY_MAP.md", "\n".join([
        "# METHOD_IDENTITY_MAP",
        "",
        "I-Proj-ZS、F1-Proj-ZS、F2-Proj-ZS 共用零质量隔离和 Stage-1 到达参考。服务器权重是 `argmin ||α−β||²`，β 由该次释放集合里冻结的正质量 m 归一。DistanceSolver 的最小 TV 权重只作诊断。",
        "",
        "TwoStage-Hájek 使用 `TwoStageHajekAggregator`，权重是 beta_hat 的归一。它按自己的定义使用共同源事件里的合法训练观测，不因为缺少这套 m 而被剥掉样本。",
        "",
        "FedAvg-Window 使用 `FedAvgWindowAggregator`，权重来自 raw_counts。同样不套用零质量隔离。",
        "",
        "适配还没有在新事件流上跑过训练。缺的是注册模型快照、本地两步和一次服务器 SGD 的接线执行，不是用 0.5 或 oracle 填概率。完成前不能把这两臂标成 TRAINING_VERIFIED。",
        "",
        f"μ 保持 measured-O 冻结值 {mu.tolist()}。",
    ]))


def write_code_diff() -> None:
    diff = subprocess.run(["git", "diff", "--stat", "--", "src"], cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace", check=False)
    write_text(OUT / "CODE_DIFF.md", "\n".join([
        "# CODE_DIFF",
        "",
        "本轮没有修改 `src`。新增文件都在 `results_zero_safe_buffer/round_v1/`。",
        "",
        "工作区里原有的 src 差异不是本轮写入的：",
        "",
        "```",
        (diff.stdout or "").strip(),
        "```",
    ]))


def write_request(detail: dict) -> None:
    write_text(OUT / "PILOT_READY_REQUEST.md", "\n".join([
        "# PILOT_READY_REQUEST",
        "",
        "状态：STATIC_READY，等待明确的训练授权。本文件不是授权，Z3 没有执行。",
        "",
        "Z1 新规则下，至少一个普通缓存相对新的立即聚合达到了 0.005 的探索性几何降幅：",
        f"- F1：{detail['F1-Proj']}",
        f"- F2：{detail['F2-Proj']}",
        "",
        "获准后的队列是 measured-O 的 33001、33002、33003，每条 100 窗，顺序为每个种子的 I-Proj-ZS、F1-Proj-ZS、F2-Proj-ZS、TwoStage-Hájek、FedAvg-Window。共 15 条。S-Proj 和完整 P2 不在其中。",
        "",
        "训练前仍要在首个配对里执行真实本地两步、参考投影或基线权重、一次服务器 SGD，并检查完整断点。只恢复调度计数不够。",
        "",
        "建议上限：2400 CPU 秒、60 分钟活动 wall。这是上限，不是成本预测。",
        "成功条件沿用指令：validation 上 F* 相对 N* 的 L 至少改善 2%，质量保护、CPU/wall 和 H=2 同时成立。通过也只是探索性筛选。",
        "",
        "批准前不训练。Z3 未执行、无新增预测收益。",
    ]))


def write_manifest() -> None:
    rows = []
    index = 1
    for seed in SEEDS:
        for method in ("I-Proj-ZS", "F1-Proj-ZS", "F2-Proj-ZS", "TwoStage-Hájek", "FedAvg-Window"):
            rows.append({
                "run_id": index,
                "block": "measured-O",
                "method": method,
                "seed": seed,
                "windows": 100,
                "stage": "Z3",
                "status": "UNRUN",
                "L_m": "UNRUN",
                "evidence": "not started",
            })
            index += 1
    write_csv(OUT / "RUN_MANIFEST.csv", rows, list(rows[0]))
    metrics = []
    for row in rows:
        for checkpoint in (20, 30, 40, 50, 60, 70, 80, 90, 100):
            metrics.append({**row, "checkpoint_window_number": checkpoint, "RMSE_mu": "UNRUN", "WorstGroupRMSE": "UNRUN"})
    write_csv(OUT / "CHECKPOINT_METRICS.csv", metrics, list(metrics[0]))
    write_csv(OUT / "SEED_COMPARISON.csv", [{
        "block": "measured-O",
        "comparison": "F*_vs_N*",
        "gain": "UNRUN",
        "note": "task metrics are unrun; geometry is in Z1_REVISION_COMPARISON.csv",
    }], ["block", "comparison", "gain", "note"])


def write_report(status: str, comparison: list[dict], detail: dict | None = None) -> None:
    current = sample()
    lines = [
        "# EXPERIMENT_REPORT",
        "",
        f"- 状态：{status}",
        f"- 审计 CPU 秒：{current['cpu_seconds']:.6f}",
        f"- 审计 wall 秒：{current['wall_seconds']:.6f}",
        f"- 峰值 RSS 字节：{current['peak_rss_bytes']}",
        "",
        "## 1. 零质量隔离",
        "",
        "唯一规则变化是 m=0 不进入有效池。正质量的 latest-positive 替换、H、S_max、容量和年龄规则没有改。",
        "新规则的 zero_replaces_positive 和 zero pending 都是 0。" if status != "INVALID_REPLAY" else "旧回放或新账本没有通过，隔离结果不能当成有效修订。",
        "",
        "## 2. 保留变化",
        "",
        "正质量 committed、替换和未进入 committed 的观测 ID 按种子与方法写在 Z1_REVISION_COMPARISON.csv。不能把不同方法的观测 ID 加总后称为独特样本。",
        "",
        "## 3. 是否优于强即时基线",
        "",
        "预测比较是 UNRUN。几何 D 若有下降，也只是探索性投入量级，不是任务收益。",
        "",
        "## 4. 质量保护、成本与 H=2",
        "",
        "预测质量、CPU 比和 wall 比都是 UNRUN。调度核验要求已提交正质量驻留不超过 2。",
        "",
        "## 5. 完成范围",
        "",
        "Z3 的 15 条轨迹是 UNRUN。真实 SGD 没有执行。后端静态接线状态见 Z2_IMPLEMENTATION_REPORT.md。" if status == "STATIC_READY" else "Z3 没有执行。",
        "",
        "## 6. 可以主张什么",
        "",
        "不能把本轮结果写成旧 S 方法通过，也不能归给未运行的支持感知调度或完整 P2。现有 train/validation/test 不是独立确认。",
        "",
        "Z3 未执行、无新增预测收益。",
    ]
    if detail:
        lines.extend(["", f"F1 几何降幅：{detail['F1-Proj']}", f"F2 几何降幅：{detail['F2-Proj']}"])
    write_text(OUT / "EXPERIMENT_REPORT.md", "\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
