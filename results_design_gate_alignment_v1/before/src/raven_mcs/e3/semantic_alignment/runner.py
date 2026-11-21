"""Unified E3 real-runner path used by future Canary (semantic dry allowed)."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run
from raven_mcs.e3.semantic_alignment.central_runner import run_central_e3
from raven_mcs.e3.semantic_alignment.constants import (
    PAIR_STATE_SCHEMA_VERSION,
    SCENARIO,
)
from raven_mcs.e3.semantic_alignment.pair_state_v2 import (
    emit_pair_state_from_trace,
    pair_state_schema_v2,
)
from raven_mcs.metrics.distribution import delta_group, delta_pair
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json


REQUIRED_METRIC_FIELDS = [
    "RMSE_mu",
    "MAE_mu",
    "Tail_RMSE",
    "Head_RMSE",
    "Delta_group",
    "Delta_pair",
    "delta_ref",
    "Q_norm1_over_S",
    "Q_norm2_over_S",
    "RMSE_rho",
    "ESS",
    "clip_rate_stage1",
    "clip_rate_stage2",
    "solver_status",
    "runtime_seconds",
]


def metric_schema_v2() -> dict[str, Any]:
    return {
        "schema_version": "E3_REAL_RUNNER_METRIC_SCHEMA_V2",
        "required_fields": REQUIRED_METRIC_FIELDS,
        "primary": [
            "RMSE_mu",
            "MAE_mu",
            "Tail_RMSE",
            "Delta_group",
            "Delta_pair",
            "delta_ref",
            "Q_norm1_over_S",
            "Q_norm2_over_S",
        ],
        "secondary": [
            "Head_RMSE",
            "RMSE_rho",
            "ESS",
            "clip_rate_stage1",
            "clip_rate_stage2",
            "solver_status",
            "runtime_seconds",
        ],
    }


def _append_ledger(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def run_e3_unified(
    *,
    root: Path,
    run_dir: Path,
    dataset: str,
    seed: int,
    method: str,
    scenario: str = SCENARIO,
    eventtrace_dir: Path,
    target_mu: dict[str, float],
    unit_to_group: dict[str, str],
    mode: str = "semantic_dry",
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    """Canonical E3 runner entry used by Canary/formal.

    mode=semantic_dry: emits scientific state without performance claims.
    """
    assert_schedulable_e3_run(dataset=dataset, scenario=scenario, seed=seed, method=method)
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = f"e3::{dataset}::{scenario}::{method}::seed{seed}"
    attempt_id = f"{run_id}__attempt1"
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    ledger_path = Path(ledger_path or (run_dir / "ledger.jsonl"))

    config = {
        "dataset": dataset,
        "seed": int(seed),
        "method": method,
        "scenario": scenario,
        "mode": mode,
        "pair_state_schema_version": PAIR_STATE_SCHEMA_VERSION,
        "metric_schema_version": "E3_REAL_RUNNER_METRIC_SCHEMA_V2",
    }
    dump_json(config, run_dir / "config_snapshot.json")
    config_hash = sha256_file(run_dir / "config_snapshot.json")

    et_identity = {}
    et_hash = None
    if (Path(eventtrace_dir) / "trace_identity.json").is_file():
        et_identity = json.loads((Path(eventtrace_dir) / "trace_identity.json").read_text(encoding="utf-8"))
        et_hash = et_identity.get("trace_hash")

    _append_ledger(
        ledger_path,
        {
            "event": "START",
            "run_id": run_id,
            "attempt_id": attempt_id,
            "dataset": dataset,
            "seed": int(seed),
            "scenario": scenario,
            "canonical_method": method,
            "config_hash": config_hash,
            "EventTrace_hash": et_hash,
            "metric_schema_version": config["metric_schema_version"],
            "pair_state_schema_version": PAIR_STATE_SCHEMA_VERSION,
            "timestamp": started,
        },
    )

    # Load events
    events = pd.read_parquet(Path(eventtrace_dir) / "events.parquet")
    for column in ("risk_set_unit_ids", "opportunity_features", "observed_unit_ids", "O"):
        if events[column].dtype == object:
            events[column] = events[column].map(lambda v: json.loads(v) if isinstance(v, str) else v)

    pair_frame, pair_summary = emit_pair_state_from_trace(
        events=events,
        dataset=dataset,
        seed=seed,
        scenario=scenario,
        method=method,
        target_mu=target_mu,
        unit_to_group=unit_to_group,
        eventtrace_hash=et_hash,
        config_hash=config_hash,
    )
    pair_path = run_dir / "pair_state.parquet"
    pair_frame.to_parquet(pair_path, index=False)
    dump_json(pair_summary, run_dir / "pair_metric_summary.json")

    metrics: dict[str, Any] = {k: None for k in REQUIRED_METRIC_FIELDS}
    metrics["Delta_pair"] = float(pair_summary["Delta_pair"])
    # Delta_group from group marginal of Pi_hat vs mu
    group_ids = sorted(target_mu)
    mu_vec = np.asarray([target_mu[g] for g in group_ids], dtype=np.float64)
    # Aggregate estimated pair mass to groups when pair_id == group
    if not pair_frame.empty:
        est = pair_frame.groupby("pair_id")["estimated_pair_mass"].sum()
        est = est / max(float(est.sum()), 1e-12)
        omega = np.asarray([float(est.get(g, 0.0)) for g in group_ids], dtype=np.float64)
        metrics["Delta_group"] = float(delta_group(omega, mu_vec))
    else:
        metrics["Delta_group"] = None

    checkpoint_hash = None
    if method in {"central_all", "central_delivered"}:
        central_out = run_central_e3(
            run_dir=run_dir,
            method=method,
            events=events,
            seed=seed,
        )
        metrics["RMSE_mu"] = central_out.get("train_mse_proxy")
        metrics["MAE_mu"] = central_out.get("train_mae_proxy")
        ckpt = run_dir / "checkpoints" / "final.pt"
        if ckpt.is_file():
            checkpoint_hash = sha256_file(ckpt)
    else:
        # Semantic dry federated path: no performance training; placeholders for accuracy fields
        metrics["RMSE_mu"] = None
        metrics["MAE_mu"] = None
        metrics["Tail_RMSE"] = None
        metrics["Head_RMSE"] = None
        metrics["delta_ref"] = 0.0
        metrics["Q_norm1_over_S"] = 0.0
        metrics["Q_norm2_over_S"] = 0.0
        metrics["RMSE_rho"] = None
        metrics["ESS"] = None
        metrics["clip_rate_stage1"] = 0.0
        metrics["clip_rate_stage2"] = 0.0
        metrics["solver_status"] = "SEMANTIC_DRY_NO_P2"

    runtime = float(time.perf_counter() - t0)
    metrics["runtime_seconds"] = runtime
    dump_json(metrics, run_dir / "final_metrics.json")
    metric_hash = sha256_file(run_dir / "final_metrics.json")
    pair_hash = sha256_file(pair_path)

    manifest = {
        "run_id": run_id,
        "attempt_id": attempt_id,
        "dataset": dataset,
        "seed": int(seed),
        "scenario": scenario,
        "method": method,
        "mode": mode,
        "status": "OK",
        "config_hash": config_hash,
        "EventTrace_hash": et_hash,
        "pair_state_hash": pair_hash,
        "metric_hash": metric_hash,
        "checkpoint_hash": checkpoint_hash,
        "pair_state_schema_version": PAIR_STATE_SCHEMA_VERSION,
        "no_performance_claim": mode == "semantic_dry",
    }
    dump_json(manifest, run_dir / "runtime_manifest.json")
    manifest_hash = sha256_file(run_dir / "runtime_manifest.json")

    _append_ledger(
        ledger_path,
        {
            "event": "FINISH",
            "run_id": run_id,
            "attempt_id": attempt_id,
            "exit_code": 0,
            "completed_windows": int(events["window_id"].nunique()) if len(events) else 0,
            "runtime": runtime,
            "checkpoint_hash": checkpoint_hash,
            "metric_output_hashes": {"final_metrics": metric_hash},
            "pair_state_output_hash": pair_hash,
            "manifest_hash": manifest_hash,
            "status": "OK",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {
        "run_id": run_id,
        "metrics": metrics,
        "pair_summary": pair_summary,
        "manifest": manifest,
        "status": "PAIR_STATE_RUNNER_INTEGRATED",
        "pair_state_path": str(pair_path),
    }
