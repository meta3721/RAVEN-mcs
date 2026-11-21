"""Non-training checks for the five-arm backend.

Heavy imports stay behind the 2.5 GiB gate. This script does not call
ClientTrainer.train_step and does not run a server optimizer step on model weights.
"""

from __future__ import annotations

import json
import os
import py_compile
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND = HERE.parent
REPO = ROUND.parents[1]
OLD = REPO / "results_support_consumption" / "round_v1"
SRC = REPO / "src"
for path in (HERE, ROUND, OLD, SRC, REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ.setdefault("PYTHONUTF8", "1")

Z2_CPU_ALREADY = 7.5 - 7.46875
Z2_WALL_ALREADY = 8.637049299984938 - 8.519495499989716
CPU_BUDGET = 600.0 - Z2_CPU_ALREADY
WALL_BUDGET = 20.0 * 60.0 - Z2_WALL_ALREADY
MU = [
    0.6496975806451613,
    0.1350806451612903,
    0.07258064516129033,
    0.14264112903225806,
]
GROUPS = ["region0", "region1", "region2", "region3"]


def pure_checks() -> dict:
    from checkpoint_store import CheckpointIncomplete, load_checkpoint, optimizer_state, save_checkpoint
    from five_arm_backend import ARMS, FiveArmBackend, TrainingNotAuthorized
    from update_semantics import apply_normalized_local_updates, rmse_mu_from_group_means, worst_group_rmse

    theta = apply_normalized_local_updates(
        [1.0, 1.0], [0.25, 0.75], [[0.5, 0.0], [0.0, 0.5]], 0.01,
    )
    server_ok = abs(theta[0] - 0.99875) < 1e-12 and abs(theta[1] - 0.99625) < 1e-12
    score = rmse_mu_from_group_means([0.0, 1.0], [0.5, 0.5])
    score_ok = abs(score - (0.5 ** 0.5)) < 1e-12
    worst_ok = worst_group_rmse([0.2, 0.5, 0.1]) == 0.5
    backend = FiveArmBackend()
    held = backend.apply_hold({"w": [1.0]}, backend.empty_optimizer(), 3)
    hold_ok = held[2] == 3 and held[0]["w"] == [1.0] and held[1]["step_count"] == 0
    denied = False
    try:
        backend.apply_release([1.0], [1.0], [[0.5]])
    except TrainingNotAuthorized:
        denied = True
    seed_a = backend.attempt_seed(33001, "client|0|0")
    seed_b = backend.attempt_seed(33001, "client|1|0")
    seed_ok = seed_a == backend.attempt_seed(33001, "client|0|0") and seed_a != seed_b
    rules_ok = (
        backend.arm_local_weight_rule("TwoStage-Hájek") == "stage1_hajek_a_bar_on_observed"
        and backend.server_weight_rule("FedAvg-Window") == "normalized_raw_counts"
        and all(arm in ARMS for arm in ("I-Proj-ZS", "F1-Proj-ZS", "F2-Proj-ZS"))
    )
    random.seed(7)
    state = random.getstate()
    payload = {
        "model_state": {"weight": [1.0, 2.0]},
        "optimizer_state": optimizer_state(local_lr=0.01, server_lr=0.01, local_steps=2, step_count=0),
        "version": 0,
        "registration_snapshots": {"a|0|0": {"weight": [1.0, 2.0]}},
        "client_state": {},
        "in_flight": {"a|0|0": {"m": 1.0}},
        "pending": {},
        "rng_state": {"python": state, "torch": None, "torch_status": "UNRUN"},
        "data_cursor": {"close": 0},
        "ledger": [],
        "eval_progress": {"completed_closes": 0},
        "budget": {"cpu_seconds": 0.0},
    }
    path = HERE / "_checkpoint_roundtrip.pkl"
    save_checkpoint(path, payload)
    loaded = load_checkpoint(path)
    roundtrip_ok = loaded["model_state"] == payload["model_state"] and loaded["rng_state"]["python"] == state
    rejected = False
    try:
        save_checkpoint(HERE / "_bad.pkl", {"optimizer_state": {"step_count": 1}})
    except CheckpointIncomplete:
        rejected = True
    path.unlink(missing_ok=True)
    path.with_suffix(path.suffix + ".index.json").unlink(missing_ok=True)
    compiled = []
    for name in ("update_semantics.py", "checkpoint_store.py", "five_arm_backend.py", "static_check.py"):
        py_compile.compile(str(HERE / name), doraise=True)
        compiled.append(name)
    py_compile.compile(str(ROUND / "zero_safe_scheduler.py"), doraise=True)
    ok = all([server_ok, score_ok, worst_ok, hold_ok, denied, seed_ok, rules_ok, roundtrip_ok, rejected])
    return {
        "pass": ok,
        "server_step": theta,
        "server_step_pass": server_ok,
        "rmse_formula": score,
        "rmse_formula_pass": score_ok,
        "worst_group_pass": worst_ok,
        "hold_pass": hold_ok,
        "training_call_denied": denied,
        "attempt_seed_stable": seed_ok,
        "weight_rules_pass": rules_ok,
        "checkpoint_roundtrip_pass": roundtrip_ok,
        "step_count_only_rejected": rejected,
        "compiled": compiled + ["zero_safe_scheduler.py"],
        "neural_training": "UNRUN",
    }


def validation_support() -> dict:
    import pyarrow.parquet as pq

    path = REPO / "data" / "processed" / "cityscanner_nyc_p2_measured_o" / "atomic_units.parquet"
    if not path.is_file():
        return {"status": "BLOCKED_ASSET", "missing": str(path)}
    schema_names = set(pq.read_schema(path).names)
    if not {"split", "target_group"} <= schema_names:
        return {"status": "BLOCKED_ASSET", "columns": sorted(schema_names)}
    table = pq.read_table(path, columns=["split", "target_group"], filters=[("split", "==", "validation")])
    groups = [str(value) for value in table.column("target_group").to_pylist()]
    counts: dict[str, int] = {}
    for group in groups:
        counts[group] = counts.get(group, 0) + 1
    missing = [group for group in GROUPS if counts.get(group, 0) <= 0]
    return {
        "status": "PASS" if not missing else "INSUFFICIENT_EVALUATION_SUPPORT",
        "validation_counts": {group: counts.get(group, 0) for group in GROUPS},
        "missing_groups": missing,
        "rows_read": len(groups),
        "target_value_read": False,
        "test_used_for_selection": False,
    }


def counter_check() -> dict:
    from cache_scheduler import synthetic_attempt
    from zero_safe_scheduler import ZeroSafeScheduler

    scheduler = ZeroSafeScheduler("F1-Proj", MU)
    scheduler.begin_close(0)
    positive = synthetic_attempt("a", 0, (1.0, 0.0, 0.0, 0.0), mass=1.0)
    scheduler.register(positive)
    scheduler.deliver(positive.attempt_id)
    first = scheduler.close(0)
    scheduler.begin_close(1)
    zero = synthetic_attempt("a", 1, (0.0, 0.0, 0.0, 0.0), mass=0.0)
    scheduler.register(zero)
    before = {message.attempt_id for message in scheduler.pending.values()}
    scheduler.deliver(zero.attempt_id)
    pending_after = sorted(message.attempt_id for message in scheduler.pending.values())
    zero_state = next(row["state"] for row in scheduler.trace if row["attempt_id"] == zero.attempt_id)
    second = scheduler.close(1)
    positive_state = next(row["state"] for row in scheduler.trace if row["attempt_id"] == positive.attempt_id)
    ok = (
        first["action"] == "HOLD"
        and zero.attempt_id not in before
        and pending_after == [positive.attempt_id]
        and zero_state == "REFERENCE_ZERO_EXCLUDED"
        and scheduler.zero_replaces_positive == 0
        and scheduler.zero_would_replace_positive == 1
        and scheduler.max_zero_pending == 0
        and second["action"] == "RELEASE"
        and positive_state == "committed"
        and scheduler.replacement_events[0]["incoming_m"] == 0.0
        and scheduler.replacement_events[0]["existing_m"] == 1.0
        and scheduler.replacement_events[0]["occurred"] is False
    )
    return {
        "pass": ok,
        "first_action": first["action"],
        "second_action": second["action"],
        "zero_state": zero_state,
        "positive_state": positive_state,
        "zero_replaces_positive": scheduler.zero_replaces_positive,
        "zero_would_replace_positive": scheduler.zero_would_replace_positive,
        "max_zero_pending": scheduler.max_zero_pending,
        "replacement_event": scheduler.replacement_events[0],
        "pending_after_zero": pending_after,
    }


def bind_check() -> dict:
    from raven_mcs.aggregation.methods import FedAvgWindowAggregator, TwoStageHajekAggregator
    from raven_mcs.correction.second_stage import beta_hat, d_weight, two_stage_mass
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf
    from raven_mcs.propensity.usable import UsablePropensity
    from raven_mcs.training.client import ClientTrainer

    from five_arm_backend import FiveArmBackend
    from projection import project_reference

    backend = FiveArmBackend()
    names = backend.resolve()
    identity = {
        "local_train": backend.calls["local_train"].function is ClientTrainer.train_step,
        "initial_model": backend.calls["initial_model"].function is deterministic_common_ndmf,
        "project": backend.calls["project"].function is project_reference,
        "fedavg_weights": backend.calls["fedavg_weights"].function is FedAvgWindowAggregator.compute_server_weights,
        "twostage_weights": (
            backend.calls["twostage_weights"].function is TwoStageHajekAggregator.compute_server_weights
        ),
        "d_weight": backend.calls["d_weight"].function is d_weight,
        "two_stage_mass": backend.calls["two_stage_mass"].function is two_stage_mass,
        "beta_hat": backend.calls["beta_hat"].function is beta_hat,
        "usable_propensity": backend.calls["usable_propensity"].function is UsablePropensity,
    }
    called = ClientTrainer.train_step is backend.calls["local_train"].function and backend.training_authorized is False
    return {
        "pass": all(identity.values()) and called,
        "bound": names,
        "identity": identity,
        "train_step_called": False,
    }


def git_diff_stat() -> str:
    completed = subprocess.run(
        ["git", "diff", "--stat", "--", "results_zero_safe_buffer/round_v1/zero_safe_scheduler.py"],
        cwd=REPO,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return (completed.stdout or "") + (completed.stderr or "")


def main() -> int:
    sys.path.insert(0, str(OLD))
    from accounting import StageWatch, available_bytes

    watch = StageWatch("B0-B1", CPU_BUDGET, WALL_BUDGET)
    result: dict = {
        "training_executed": False,
        "historical_z2_cpu_seconds": Z2_CPU_ALREADY,
        "historical_z2_wall_seconds": Z2_WALL_ALREADY,
        "historical_z2_note": "incremental snapshots from RESOURCE_LEDGER.jsonl; not re-run",
    }
    try:
        result["pure_checks"] = pure_checks()
    except Exception as exc:
        result["status"] = "BACKEND_IMPLEMENTATION_INCOMPLETE"
        result["pure_error"] = f"{type(exc).__name__}: {exc}"
        result["heavy"] = {"status": "UNRUN"}
        _finish(result, watch, 1)
        return 1
    free = available_bytes()
    result["available_bytes_at_gate"] = free
    if free < 1024**3:
        result["status"] = "RESOURCE_BLOCKED"
        result["heavy"] = {"status": "UNRUN", "reason": "available memory below 1 GiB"}
        _finish(result, watch, 2)
        return 2
    if free < int(2.5 * 1024**3):
        if free < int(2.0 * 1024**3):
            time.sleep(30)
            free = available_bytes()
            result["available_bytes_after_wait"] = free
        if free < int(2.5 * 1024**3):
            result["status"] = "RESOURCE_BLOCKED"
            result["heavy"] = {
                "status": "UNRUN",
                "reason": "available memory below 2.5 GiB before heavy imports",
                "available_bytes": free,
            }
            _finish(result, watch, 2)
            return 2
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    try:
        watch.raise_for_limits()
        result["counter_check"] = counter_check()
        watch.raise_for_limits()
        result["validation_support"] = validation_support()
        watch.raise_for_limits()
        result["bind_check"] = bind_check()
        watch.raise_for_limits()
    except Exception as exc:
        result["status"] = "RESOURCE_BLOCKED" if "RESOURCE_" in str(exc) else "BACKEND_IMPLEMENTATION_INCOMPLETE"
        result["heavy_error"] = f"{type(exc).__name__}: {exc}"
        result["git_diff_stat"] = git_diff_stat()
        _finish(result, watch, 1)
        return 1
    validation = result["validation_support"]["status"]
    if validation == "INSUFFICIENT_EVALUATION_SUPPORT":
        result["status"] = validation
    elif validation == "BLOCKED_ASSET":
        result["status"] = "BLOCKED_ASSET"
    elif not result["counter_check"]["pass"] or not result["bind_check"]["pass"] or not result["pure_checks"]["pass"]:
        result["status"] = "BACKEND_IMPLEMENTATION_INCOMPLETE"
    else:
        result["status"] = "BACKEND_STATIC_READY"
    result["git_diff_stat"] = git_diff_stat()
    code = 0 if result["status"] == "BACKEND_STATIC_READY" else 1
    _finish(result, watch, code)
    return code


def _finish(result: dict, watch, code: int) -> None:
    sample = watch.sample()
    result["resource"] = {
        "cpu_seconds": sample["cpu_seconds"],
        "wall_seconds": sample["wall_seconds"],
        "rss_bytes": sample["rss_bytes"],
        "peak_rss_bytes": sample["peak_rss_bytes"],
        "available_bytes": sample["available_bytes"],
        "min_available_bytes": sample["min_available_bytes"],
        "cpu_budget_seconds": CPU_BUDGET,
        "wall_budget_seconds": WALL_BUDGET,
        "cpu_with_historical_z2": float(sample["cpu_seconds"]) + Z2_CPU_ALREADY,
        "wall_with_historical_z2": float(sample["wall_seconds"]) + Z2_WALL_ALREADY,
    }
    result["exit_code"] = code
    (HERE / "STATIC_CHECK_RESULTS.json").write_text(
        json.dumps(result, indent=2, default=str), encoding="utf-8",
    )
    ledger = {
        "stage": "B0-B1",
        "status": result.get("status"),
        "cpu_seconds": sample["cpu_seconds"],
        "wall_seconds": sample["wall_seconds"],
        "rss_bytes": sample["rss_bytes"],
        "peak_rss_bytes": sample["peak_rss_bytes"],
        "available_bytes": sample["available_bytes"],
        "min_available_bytes": sample["min_available_bytes"],
        "historical_z2_cpu_seconds": Z2_CPU_ALREADY,
        "historical_z2_wall_seconds": Z2_WALL_ALREADY,
        "training_executed": False,
    }
    with (HERE / "RESOURCE_LEDGER.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ledger) + "\n")
    print(result.get("status"), f"cpu={sample['cpu_seconds']:.3f}", f"free={sample['available_bytes']}")


if __name__ == "__main__":
    raise SystemExit(main())
