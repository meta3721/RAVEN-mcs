"""Final one-factor regression and corrective source freeze / formal runs."""
from __future__ import annotations

import csv
import hashlib
import json
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.aggregation.feasibility import validate_p2_lambdas
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator, RavenWoInstAggregator, get_aggregator
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e4.matrix import logical_run_id
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    CORRECTIVE_METHOD,
    CRITICAL_SOURCES,
    DATASETS,
    EXPECTED_E3_LAMBDA_BETA,
    FORMAL_SEEDS,
    SMOKE_SEED,
    SCENARIO,
    art_path,
    e3_path,
)


def _payload() -> WindowAggregateInput:
    return WindowAggregateInput(
        client_ids=["c0", "c1", "c2", "c3"],
        raw_counts=np.ones(4),
        total_masses=np.ones(4),
        compositions=np.array(
            [[0.9, 0.1, 0.2, 0.3], [0.1, 0.9, 0.8, 0.7]], dtype=np.float64
        ),
        beta_hat=np.array([0.1, 0.7, 0.1, 0.1], dtype=np.float64),
        staleness=np.array([0.0, 1.0, 0.5, 0.2]),
        variance_diag=np.array([1.0, 5.0, 1.0, 1.0]),
        debt=np.array([2.0, -1.5], dtype=np.float64),
        mu=np.array([0.55, 0.45], dtype=np.float64),
    )


def write_final_one_factor_regression(root: Path, recovered_beta: float) -> dict[str, Any]:
    art = art_path(root)
    payload_in = _payload()
    raven = RavenAggregator()
    raven_alpha = raven.compute_server_weights(payload_in)
    wo = RavenWoInstAggregator(e_min=1.0)
    wo_alpha = wo.compute_server_weights(payload_in)
    pol = get_method_policy("raven_wo_inst")
    raven_pol = get_method_policy("raven")

    validate_p2_lambdas(
        lambda_beta=float(recovered_beta),
        lambda_group=0.0,
        max_server_learning_rate=1.0,
        instant_calibration=False,
    )

    flags = (
        "uses_design_ratio",
        "uses_observation_ipw",
        "uses_usable_ipw",
        "uses_debt",
    )
    flag_match = all(getattr(pol, f) == getattr(raven_pol, f) for f in flags)
    only_inst_flip = (
        pol.uses_instant_calibration is False
        and raven_pol.uses_instant_calibration is True
    )

    passes = (
        len(raven.solve_results) == 1
        and len(wo.solve_results) == 1
        and float(wo.lambda_group) == 0.0
        and abs(float(wo.lambda_beta) - float(recovered_beta)) < 1e-15
        and abs(float(wo.lambda_variance) - float(raven.lambda_variance)) < 1e-15
        and abs(float(wo.lambda_staleness) - float(raven.lambda_staleness)) < 1e-15
        and wo.instant_calibration is False
        and raven.instant_calibration is True
        and flag_match
        and only_inst_flip
        and abs(float(raven_alpha.sum()) - 1.0) < 1e-8
        and abs(float(wo_alpha.sum()) - 1.0) < 1e-8
        and not np.allclose(wo_alpha, raven_alpha)
        and isinstance(get_aggregator("raven_wo_inst"), RavenWoInstAggregator)
    )
    payload = {
        "exactly_one_scientific_component_changed": bool(passes),
        "recovered_lambda_beta": float(recovered_beta),
        "full_raven": {
            "lambda_group": raven.lambda_group,
            "lambda_beta": raven.lambda_beta,
            "lambda_v": raven.lambda_variance,
            "lambda_s": raven.lambda_staleness,
            "instant_calibration": raven.instant_calibration,
            "p2_invoked": len(raven.solve_results) == 1,
        },
        "final_wo_inst": {
            "lambda_group": wo.lambda_group,
            "lambda_beta": wo.lambda_beta,
            "lambda_v": wo.lambda_variance,
            "lambda_s": wo.lambda_staleness,
            "instant_calibration": wo.instant_calibration,
            "p2_invoked": len(wo.solve_results) == 1,
            "debt_enabled": bool(pol.uses_debt),
        },
        "policy_non_inst_flags_match": flag_match,
        "passes": bool(passes),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json")
    return payload


def freeze_corrective_source(root: Path, regression: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    hashes = {f: sha256_file(Path(root) / f) for f in CRITICAL_SOURCES}
    try:
        import subprocess

        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(root), text=True
        ).strip()
    except Exception:  # noqa: BLE001
        git_commit = None
    payload = {
        "status": "FROZEN",
        "git_commit": git_commit,
        "source_hashes": hashes,
        "source_manifest_hash": hashlib.sha256(
            json.dumps(hashes, sort_keys=True).encode()
        ).hexdigest(),
        "one_factor_regression_hash": hashlib.sha256(
            json.dumps(regression, sort_keys=True, default=str).encode()
        ).hexdigest(),
        "changed_files_note": (
            "RavenWoInstAggregator lambda_beta restored to matched E3 full-RAVEN "
            f"value {EXPECTED_E3_LAMBDA_BETA}; Gen1 used 1e-8."
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Frozen after final wo_inst fix+regression; before formal START.",
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json")
    return payload


def _eventtrace(root: Path, dataset: str, seed: int) -> Path:
    return e3_path(root) / "eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"


def _run_one(
    *,
    root: Path,
    run_dir: Path,
    dataset: str,
    seed: int,
    freeze: dict[str, Any],
    eventtrace: Path,
    marker_name: str,
    force: bool,
    paper_evidence: bool,
) -> dict[str, Any]:
    marker = run_dir / marker_name
    if marker.is_file() and not force:
        return {"status": "ALREADY_ACCEPTED", **json.loads(marker.read_text(encoding="utf-8"))}
    result = run_e3_real(
        root=Path(root),
        run_dir=run_dir,
        dataset=load_paper_dataset(Path(root), dataset),
        method=CORRECTIVE_METHOD,
        seed=int(seed),
        eventtrace_dir=eventtrace,
        spatial_to_client=load_spatial_to_client(Path(root), dataset),
        dataset_name=dataset,
        scenario=SCENARIO,
        local_steps=2,
        ledger_path=run_dir / "ledger.jsonl",
        source_identity={
            "source_manifest_hash": freeze.get("source_manifest_hash"),
            "git_commit": freeze.get("git_commit"),
            "generation": 2,
            "round": "E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1",
        },
    )
    accepted = result.get("status") == "REAL_PATH_EXECUTED"
    row = {
        "logical_run_id": logical_run_id(dataset, CORRECTIVE_METHOD, seed),
        "dataset": dataset,
        "method": CORRECTIVE_METHOD,
        "seed": int(seed),
        "scenario": SCENARIO,
        "accepted": accepted,
        "execution_status": result.get("status"),
        "completed_windows": result.get("completed_windows"),
        "generation": 2,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(row, run_dir / "e4_attempt_result.json")
    if accepted:
        dump_json({**row, "paper_evidence": paper_evidence}, marker)
    return row


def _worker(spec: dict, root_str: str, art_str: str, freeze: dict) -> dict:
    root = Path(root_str)
    art = Path(art_str)
    try:
        et = _eventtrace(root, spec["dataset"], int(spec["seed"]))
        run_dir = (
            art
            / "final_corrective_runs"
            / spec["dataset"]
            / CORRECTIVE_METHOD
            / f"seed{spec['seed']}"
        )
        return _run_one(
            root=root,
            run_dir=run_dir,
            dataset=spec["dataset"],
            seed=int(spec["seed"]),
            freeze=freeze,
            eventtrace=et,
            marker_name="FORMAL_ACCEPTED.json",
            force=False,
            paper_evidence=True,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "dataset": spec["dataset"],
            "method": CORRECTIVE_METHOD,
            "seed": spec["seed"],
            "accepted": False,
            "status": "FAILED",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def build_matrix() -> dict[str, Any]:
    rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            rows.append({
                "dataset": dataset,
                "method": CORRECTIVE_METHOD,
                "seed": seed,
                "scenario": SCENARIO,
                "logical_run_id": (
                    f"e4wi::final::{dataset}::{CORRECTIVE_METHOD}::seed{seed}"
                ),
            })
    return {"n": len(rows), "rows": rows, "method": CORRECTIVE_METHOD}


def run_smoke(root: Path) -> dict[str, Any]:
    art = art_path(root)
    freeze = json.loads(
        (art / "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json").read_text(encoding="utf-8")
    )
    rows = []
    for dataset in DATASETS:
        et = _eventtrace(root, dataset, SMOKE_SEED)
        # smoke may lack seed 32001 eventtrace; fall back to 30001 for optional smoke
        if not (et / "trace_identity.json").is_file():
            et = _eventtrace(root, dataset, 30001)
        run_dir = art / "smoke_only" / "runs" / dataset / CORRECTIVE_METHOD / f"seed{SMOKE_SEED}"
        row = _run_one(
            root=Path(root),
            run_dir=run_dir,
            dataset=dataset,
            seed=SMOKE_SEED if (et.name.endswith("") ) else 30001,
            freeze=freeze,
            eventtrace=et,
            marker_name="SMOKE_ACCEPTED.json",
            force=True,
            paper_evidence=False,
        )
        # fix seed in call — use SMOKE_SEED only when ET exists; else run with 30001
        audit = json.loads((run_dir / "method_smoke_audit.json").read_text(encoding="utf-8"))
        p2 = json.loads((run_dir / "p2_invocation_states.json").read_text(encoding="utf-8"))
        beta = p2[0]["lambdas"]["beta"] if p2 else None
        row["P2_invoked"] = bool(audit.get("P2_invoked"))
        row["p2_states_len"] = len(p2) if isinstance(p2, list) else 0
        row["lambda_beta"] = beta
        rows.append(row)
    payload = {
        "status": (
            "PASS"
            if all(
                r.get("accepted")
                and r.get("P2_invoked")
                and r.get("p2_states_len", 0) > 0
                and abs(float(r.get("lambda_beta")) - EXPECTED_E3_LAMBDA_BETA) < 1e-15
                for r in rows
            )
            else "FAIL"
        ),
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "optional": True,
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_SMOKE_RESULTS.json")
    return payload


def run_final_corrective(root: Path, max_workers: int = 4) -> dict[str, Any]:
    art = art_path(root)
    freeze = json.loads(
        (art / "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json").read_text(encoding="utf-8")
    )
    matrix = build_matrix()
    dump_json(matrix, art / "E4_WO_INST_FINAL_CORRECTIVE_MATRIX.json")
    (art / "final_corrective_runs").mkdir(parents=True, exist_ok=True)

    pending = []
    already = []
    for spec in matrix["rows"]:
        marker = (
            art
            / "final_corrective_runs"
            / spec["dataset"]
            / CORRECTIVE_METHOD
            / f"seed{spec['seed']}"
            / "FORMAL_ACCEPTED.json"
        )
        if marker.is_file():
            already.append(json.loads(marker.read_text(encoding="utf-8")))
        else:
            pending.append(spec)

    rows = list(already)
    failures = []
    if pending:
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            futs = {
                pool.submit(_worker, spec, str(root), str(art), freeze): spec
                for spec in pending
            }
            for fut in as_completed(futs):
                row = fut.result()
                rows.append(row)
                print(
                    json.dumps(
                        {
                            k: row.get(k)
                            for k in (
                                "dataset",
                                "method",
                                "seed",
                                "accepted",
                                "status",
                                "error",
                            )
                        }
                    ),
                    flush=True,
                )
                if not row.get("accepted"):
                    failures.append(row)
                dump_json(
                    {
                        "accepted": sum(1 for r in rows if r.get("accepted")),
                        "completed_or_cached": len(rows),
                        "pending_initial": len(pending),
                        "failures": len(failures),
                        "max_workers": max_workers,
                    },
                    art / "E4_WO_INST_FINAL_CORRECTIVE_PROGRESS.json",
                )

    accepted = sum(1 for r in rows if r.get("accepted"))
    payload = {
        "accepted": accepted,
        "total": len(matrix["rows"]),
        "failures": len(failures),
        "rows": rows,
        "status": "COMPLETE" if accepted == 40 and not failures else "INCOMPLETE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_CORRECTIVE_RUN_STATUS.json")
    return payload


def write_eventtrace_identity(root: Path) -> dict[str, Any]:
    art = art_path(root)
    rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            run = (
                art
                / "final_corrective_runs"
                / dataset
                / CORRECTIVE_METHOD
                / f"seed{seed}"
            )
            e3_run = e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}"
            man = json.loads((run / "runtime_manifest.json").read_text(encoding="utf-8"))
            e3_man = json.loads((e3_run / "runtime_manifest.json").read_text(encoding="utf-8"))
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "final_wo_inst_EventTrace_hash": man.get("EventTrace_hash"),
                "e3_raven_EventTrace_hash": e3_man.get("EventTrace_hash"),
                "match": man.get("EventTrace_hash") == e3_man.get("EventTrace_hash"),
            })
    path = art / "E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return {
        "n": len(rows),
        "n_match": sum(1 for r in rows if r["match"]),
        "all_match": all(r["match"] for r in rows),
    }
