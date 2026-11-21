"""Non-training checks for the runtime fixes.

The frozen-trace comparison imports pandas only after free memory is at least
2.5 GiB. Below 1 GiB it returns immediately and does not claim the mapping passed.
"""

from __future__ import annotations

import ast
import json
import shutil
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_DIR = HERE / "training_run_v1"


def main() -> int:
    started = time.perf_counter()
    from runtime_budget import (
        IMPLEMENTATION_CPU,
        IMPLEMENTATION_WALL,
        TRAINING_CPU,
        TRAINING_WALL,
        _accounting,
        add_cost,
        before_heavy,
        load_budget,
        peek_memory,
    )

    _, process_tree_usage = _accounting()
    origin_cpu = float(process_tree_usage()["cpu_seconds"])
    pure = _pure_checks()
    gate = before_heavy()
    identity = {
        "status": "UNRUN",
        "reason": gate["status"],
        "available_bytes": gate["available_bytes"],
        "waited_seconds": gate.get("waited_seconds", 0.0),
    }
    if gate["status"] == "OK":
        identity = _frozen_identity()
    heavy = sorted(name for name in ("torch", "numpy", "pandas", "cvxpy", "pyarrow") if name in __import__("sys").modules)
    if identity["status"] != "PASS":
        heavy_after = [name for name in heavy if name in ("torch", "cvxpy")]
        if heavy_after:
            identity = {"status": "INVALID_CHECK", "reason": "training libraries loaded", "modules": heavy_after}
    budget = load_budget()
    cpu_before = float(budget["implementation"]["cpu_seconds"])
    usage = process_tree_usage()
    add_cost(
        "implementation",
        max(0.0, float(usage["cpu_seconds"]) - origin_cpu),
        max(0.0, time.perf_counter() - started),
        "runtime_check",
    )
    budget = load_budget()
    status = "RUNTIME_FIXES_PRESENT_IDENTITY_UNRUN"
    if not pure["pass"]:
        status = "RUNTIME_CHECK_FAILED"
    elif gate["status"] != "OK":
        status = "RESOURCE_BLOCKED"
    elif identity["status"] == "PASS":
        status = "RUNTIME_READY_UNRUN"
    elif identity["status"] != "UNRUN":
        status = str(identity["status"])
    payload = {
        "status": status,
        "training_executed": False,
        "pure": pure,
        "memory_gate": gate,
        "frozen_identity": identity,
        "heavy_modules_loaded": heavy,
        "implementation_cpu_seconds": budget["implementation"]["cpu_seconds"],
        "implementation_wall_seconds": budget["implementation"]["wall_seconds"],
        "implementation_limit_cpu_seconds": IMPLEMENTATION_CPU,
        "implementation_limit_wall_seconds": IMPLEMENTATION_WALL,
        "training_cpu_seconds": budget["training"]["cpu_seconds"],
        "training_wall_seconds": budget["training"]["wall_seconds"],
        "training_limit_cpu_seconds": TRAINING_CPU,
        "training_limit_wall_seconds": TRAINING_WALL,
        "cpu_before_this_process": cpu_before,
        "budget_monotonic": float(budget["implementation"]["cpu_seconds"]) + 1e-12 >= cpu_before,
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "RUNTIME_CHECK.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(status, f"identity={identity['status']}", f"free={gate['available_bytes']}")
    return 0 if pure["pass"] and status != "RUNTIME_CHECK_FAILED" else 1


def _pure_checks() -> dict:
    from checkpoint_store import optimizer_state, save_checkpoint
    from event_driver import describe_resume
    from reference_logic import assign_attempt_id, compare_frozen, due_updates
    from runtime_budget import load_budget

    retries = {}
    zero_id, zero_retry = assign_attempt_id("c", 0, 0, retries)
    positive_id, positive_retry = assign_attempt_id("c", 0, 1, retries)
    retry_pass = zero_retry is None and positive_retry == 0 and positive_id == "c|0|0" and zero_id == "c|0|u0"
    mismatch = compare_frozen(
        [{"attempt_id": "a|0|0", "m": 1.0, "composition": [1.0], "group_mass": [1.0]}],
        [{"attempt_id": "a|0|0", "m": 1.0, "composition": [1.0, 0.0], "group_mass": [1.0]}],
    )
    same = compare_frozen(
        [{"attempt_id": "a|0|0", "m": 1.0, "composition": [1.0], "group_mass": [1.0]}],
        [{"attempt_id": "a|0|0", "m": 1.0, "composition": [1.0], "group_mass": [1.0]}],
    )
    ready, rejected = due_updates(
        [
            {"attempt_id": "late", "arrival_close": 2, "u": 1, "m": 1.0, "registration_version": 0},
            {"attempt_id": "stale", "arrival_close": 0, "u": 1, "m": 1.0, "registration_version": 0},
        ],
        0,
        6,
        5,
    )
    arrival_pass = [item["attempt_id"] for item in ready] == [] and [item["attempt_id"] for item in rejected] == ["stale"]
    before = float(load_budget()["implementation"]["cpu_seconds"])
    directory = Path(tempfile.mkdtemp(prefix="resume_probe_"))
    path = directory / "probe.pkl"
    save_checkpoint(path, _probe_payload(optimizer_state))
    cursor = describe_resume(path)
    after = float(load_budget()["implementation"]["cpu_seconds"])
    shutil.rmtree(directory)
    resume_pass = (
        cursor["seed"] == 33001
        and cursor["arm"] == "F1-Proj-ZS"
        and cursor["next_window"] == 4
        and cursor["registration_versions"] == [0, 3]
        and after == before
    )
    tree = ast.parse((HERE / "event_driver.py").read_text(encoding="utf-8"))
    restore = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "restore_branch")
    has_finally = any(isinstance(node, ast.Try) and node.finalbody for node in ast.walk(restore))
    execute = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "execute_arm")
    calls = [
        node for node in ast.walk(execute)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
    ]
    calls.sort(key=lambda node: (node.lineno, node.col_offset))
    order = [node.func.id if isinstance(node.func, ast.Name) else node.func.attr for node in calls]
    gate_before_load = "before_heavy" in order and "_load_training_stack" in order and order.index("before_heavy") < order.index("_load_training_stack")
    passed = all((
        retry_pass,
        mismatch["pass"] is False and mismatch["reason"] == "composition",
        same["pass"] is True,
        arrival_pass,
        resume_pass,
        has_finally,
        gate_before_load,
    ))
    return {
        "pass": passed,
        "retry_rule": retry_pass,
        "length_mismatch": mismatch,
        "equal_vectors": same["pass"],
        "arrival_rule": arrival_pass,
        "resume_cursor": cursor,
        "budget_unchanged_by_resume_read": after == before,
        "restore_finally": has_finally,
        "gate_before_training_stack": gate_before_load,
    }


def _probe_payload(optimizer_state) -> dict:
    return {
        "model_state": {"w": [1.0]},
        "optimizer_state": optimizer_state(local_lr=0.01, server_lr=0.01, local_steps=2, step_count=1),
        "version": 3,
        "registration_snapshots": {"0": {"w": [1.0]}, "3": {"w": [1.25]}},
        "client_state": {"seed": 33001, "arm": "F1-Proj-ZS"},
        "in_flight": {},
        "pending": {},
        "rng_state": {"torch": "probe"},
        "data_cursor": {"next_window": 4, "trace_hash": "probe"},
        "ledger": {"scores": [], "first_update": None, "first_hold": None},
        "eval_progress": {"completed_closes": 4, "score_points": 0},
        "budget": {"optimizer_steps": 1, "cumulative_audit": {"cpu_seconds": 0.0}, "audit_only": True},
    }


def _frozen_identity() -> dict:
    import sys

    repo = HERE.parents[2]
    support = repo / "results_support_consumption" / "round_v1"
    for entry in (support, repo / "src", repo):
        if str(entry) not in sys.path:
            sys.path.insert(0, str(entry))
    from reference_logic import assign_attempt_id, compare_frozen
    from reference_replay import load_block, replay_seed
    from raven_mcs.simulation.event_trace import load_event_trace

    context = load_block("measured-O")
    result = replay_seed(context, 33001)
    trace, _identity = load_event_trace(context.trace_root / "seed33001" / "training_eventtrace")
    retries = {}
    walked = []
    for window in range(100):
        rows = trace.events.loc[trace.events["window_id"].astype(int) == window]
        for row in rows.itertuples(index=False):
            attempt_id, _retry = assign_attempt_id(str(row.client_id), window, int(row.U), retries)
            if int(row.U) == 1:
                walked.append(attempt_id)
    frozen = {item.attempt_id: item for item in result.attempts}
    expected = [
        {
            "attempt_id": item.attempt_id,
            "m": float(item.m),
            "composition": [float(value) for value in item.composition],
            "group_mass": [float(value) for value in item.group_mass],
        }
        for item in result.attempts
    ]
    actual = []
    for attempt_id in walked:
        item = frozen.get(attempt_id)
        if item is None:
            return {"status": "REFERENCE_IDENTITY_MISMATCH", "reason": "missing", "attempt_id": attempt_id}
        actual.append({
            "attempt_id": item.attempt_id,
            "m": float(item.m),
            "composition": [float(value) for value in item.composition],
            "group_mass": [float(value) for value in item.group_mass],
        })
    compared = compare_frozen(expected, actual)
    if not compared["pass"]:
        compared["status"] = "REFERENCE_IDENTITY_MISMATCH"
        return compared
    path = RUN_DIR / "frozen_reference_seed33001.json"
    path.write_text(json.dumps({"seed": 33001, "trace_hash": result.trace_hash, "attempts": expected}), encoding="utf-8")
    return {"status": "PASS", "n": compared["n"], "trace_hash": result.trace_hash, "path": str(path)}


if __name__ == "__main__":
    raise SystemExit(main())
