"""Execute one Canary logical run (resumable, attempt-aware)."""

from __future__ import annotations

import json
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.e3.canary.constants import (
    CANARY_SEED,
    FROZEN_DATASET_HASHES,
    M_MC,
    SCENARIO,
)
from raven_mcs.e3.canary.dataset_load import (
    load_horizon,
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.canary.schedule import logical_run_id
from raven_mcs.e3.canary.traffic_reuse_guard import assert_canary_schedulable
from raven_mcs.e3.numerical.source_freeze import load_freeze
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.utils.serialization import dump_json


def eventtrace_dir(art: Path, dataset: str, seed: int = CANARY_SEED) -> Path:
    return art / "eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"


def ensure_eventtrace(root: Path, art: Path, dataset: str, seed: int = CANARY_SEED) -> dict[str, Any]:
    out = art / "eventtraces" / dataset / f"seed{seed}"
    identity_path = out / "training_eventtrace" / "trace_identity.json"
    if identity_path.is_file():
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
        return {"status": "REUSED", "identity": identity, "path": str(out)}
    # Incomplete prior attempt — wipe before regenerate (Windows/OneDrive safe)
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    ds = load_paper_dataset(root, dataset)
    mapping = load_spatial_to_client(root, dataset)
    atomic, stratum_meta = apply_sealed_opportunity_stratum(
        ds.atomic_df, dataset=dataset, root=root
    )
    horizon = load_horizon(root, dataset)
    n_windows = int(horizon["chosen_E3_formal_windows"])
    mat = materialize_r3_trace(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=mapping,
        out_dir=out,
        seed=int(seed),
        num_windows=n_windows,
        m_mc=M_MC,
        delivery_mode="nominal",
    )
    dump_json(
        {"stratum_meta": stratum_meta, "num_windows": n_windows, "m_mc": M_MC},
        out / "generation_meta.json",
    )
    return {"status": "CREATED", **mat, "num_windows": n_windows, "path": str(out)}


def _next_attempt(run_dir: Path, run_id: str) -> int:
    ledger = run_dir / "ledger.jsonl"
    n = 0
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("run_id") == run_id and rec.get("event") == "START":
                n = max(n, int(str(rec.get("attempt_id", "")).rsplit("attempt", 1)[-1] or 0))
    return n + 1


def run_logical(
    *,
    root: Path,
    art: Path,
    dataset: str,
    method: str,
    seed: int = CANARY_SEED,
    local_steps: int = 2,
    force: bool = False,
    accepted_marker_name: str = "CANARY_ACCEPTED.json",
    source_identity_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assert_canary_schedulable(dataset=dataset, method=method, seed=seed)
    run_id = logical_run_id(dataset, method, seed)
    run_dir = art / "runs" / dataset / method / f"seed{seed}"
    accepted_marker = run_dir / accepted_marker_name
    if accepted_marker.is_file() and not force:
        prev = json.loads(accepted_marker.read_text(encoding="utf-8"))
        return {"status": "ALREADY_ACCEPTED", "logical_run_id": run_id, **prev}

    ensure_eventtrace(root, art, dataset, seed)
    et = eventtrace_dir(art, dataset, seed)
    ds = load_paper_dataset(root, dataset)
    mapping = load_spatial_to_client(root, dataset)
    attempt = _next_attempt(run_dir, run_id)
    attempt_id = f"{run_id}__attempt{attempt}"

    # Preserve prior attempt artifacts under attempts/
    if run_dir.exists() and any(run_dir.iterdir()) and attempt > 1:
        bak = run_dir / "attempts" / f"attempt{attempt - 1}"
        bak.mkdir(parents=True, exist_ok=True)
        for p in list(run_dir.iterdir()):
            if p.name in {"attempts", "ledger.jsonl"}:
                continue
            dest = bak / p.name
            if p.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(p, dest)
            else:
                shutil.copy2(p, dest)

    freeze = load_freeze(art) or {}
    source_identity = source_identity_override or {
        "git_commit": freeze.get("git_commit"),
        "source_manifest_hash": freeze.get("source_manifest_hash"),
        "method_source_hash": freeze.get("method_source_hash"),
        "runner_source_hash": freeze.get("runner_source_hash"),
        "dataset_hash": FROZEN_DATASET_HASHES.get(str(dataset).lower()),
    }
    try:
        result = run_e3_real(
            root=root,
            run_dir=run_dir,
            dataset=ds,
            method=method,
            seed=int(seed),
            eventtrace_dir=et,
            spatial_to_client=mapping,
            dataset_name=dataset,
            local_steps=local_steps,
            attempt_id=attempt_id,
            ledger_path=run_dir / "ledger.jsonl",
            source_identity=source_identity,
        )
        from raven_mcs.e3.numerical.finite import is_finite_number, metric_status

        metrics = result.get("metrics") or {}
        ckpt = (run_dir / "checkpoints" / "final.pt").is_file()
        required = ["RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho"]
        finite_ok = True
        for key in required:
            app = str(metrics.get(f"{key}_applicability", "APPLICABLE"))
            if app in {"NOT_APPLICABLE", "N_A", "N/A"}:
                continue
            if not is_finite_number(metrics.get(key)):
                finite_ok = False
                break
        # Delta_c_s required for non-central methods
        if method not in {"central_all", "central_delivered"}:
            if not is_finite_number(metrics.get("Delta_c_s")):
                finite_ok = False
        accepted = (
            result.get("status") == "REAL_PATH_EXECUTED"
            and ckpt
            and finite_ok
        )
        row = {
            "logical_run_id": run_id,
            "attempt_id": attempt_id,
            "attempt_count": attempt,
            "dataset": dataset,
            "method": method,
            "seed": seed,
            "scenario": SCENARIO,
            "execution_status": result.get("status"),
            "accepted": bool(accepted),
            "checkpoint_present": ckpt,
            "completed_windows": result.get("completed_windows"),
            "RMSE_mu": metrics.get("RMSE_mu"),
            "RMSE_rho": metrics.get("RMSE_rho"),
            "Delta_c_s": metrics.get("Delta_c_s"),
            "error": None,
            "finished_utc": datetime.now(timezone.utc).isoformat(),
        }
        if accepted:
            dump_json(row, accepted_marker)
        dump_json(row, run_dir / "canary_attempt_result.json")
        return row
    except Exception as exc:  # noqa: BLE001
        # Preserve failed attempt FINISH in Ledger (attempt-aware integrity)
        with (run_dir / "ledger.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "event": "FINISH",
                        "run_id": run_id,
                        "attempt_id": attempt_id,
                        "exit_code": 1,
                        "status": "FAILED",
                        "error": f"{type(exc).__name__}: {exc}",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        row = {
            "logical_run_id": run_id,
            "attempt_id": attempt_id,
            "attempt_count": attempt,
            "dataset": dataset,
            "method": method,
            "seed": seed,
            "execution_status": "FAILED",
            "accepted": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "finished_utc": datetime.now(timezone.utc).isoformat(),
        }
        dump_json(row, run_dir / "canary_attempt_result.json")
        return row
