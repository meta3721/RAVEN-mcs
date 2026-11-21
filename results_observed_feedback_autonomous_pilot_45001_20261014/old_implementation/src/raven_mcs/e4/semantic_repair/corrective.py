"""Corrective wo_inst reruns, provenance supersession, and evidence index."""
from __future__ import annotations

import csv
import hashlib
import json
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.e4.matrix import logical_run_id
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    ABLATIONS,
    CORRECTIVE_METHOD,
    CRITICAL_SOURCES,
    DATASETS,
    FORMAL_SEEDS,
    SCENARIO,
    SMOKE_SEED,
    art_path,
    e3_path,
    parent_path,
)


def build_corrective_matrix() -> dict[str, Any]:
    rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            rows.append({
                "dataset": dataset,
                "method": CORRECTIVE_METHOD,
                "seed": seed,
                "scenario": SCENARIO,
                "logical_run_id": f"e4sr::corrective::{dataset}::{CORRECTIVE_METHOD}::seed{seed}",
            })
    return {"n": len(rows), "rows": rows, "method": CORRECTIVE_METHOD}


def freeze_corrective_source(root: Path) -> dict[str, Any]:
    art = art_path(root)
    hashes = {f: sha256_file(Path(root) / f) for f in CRITICAL_SOURCES}
    payload = {
        "status": "FROZEN",
        "source_hashes": hashes,
        "source_manifest_hash": hashlib.sha256(
            json.dumps(hashes, sort_keys=True).encode()
        ).hexdigest(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Frozen after wo_inst semantic fix; before formal corrective reruns.",
    }
    dump_json(payload, art / "E4_CORRECTIVE_SOURCE_FREEZE.json")
    return payload


def _eventtrace(root: Path, dataset: str, seed: int, *, smoke: bool = False) -> Path:
    if smoke:
        parent_et = (
            parent_path(root)
            / "smoke_only"
            / "eventtraces"
            / dataset
            / f"seed{seed}"
            / "training_eventtrace"
        )
        if (parent_et / "trace_identity.json").is_file():
            return parent_et
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
        "finished_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(row, run_dir / "e4_attempt_result.json")
    if accepted:
        dump_json({**row, "paper_evidence": paper_evidence}, marker)
    return row


def run_smoke(root: Path) -> dict[str, Any]:
    art = art_path(root)
    freeze = json.loads((art / "E4_CORRECTIVE_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    rows = []
    for dataset in DATASETS:
        et = _eventtrace(root, dataset, SMOKE_SEED, smoke=True)
        run_dir = art / "smoke_only" / "runs" / dataset / CORRECTIVE_METHOD / f"seed{SMOKE_SEED}"
        row = _run_one(
            root=Path(root),
            run_dir=run_dir,
            dataset=dataset,
            seed=SMOKE_SEED,
            freeze=freeze,
            eventtrace=et,
            marker_name="SMOKE_ACCEPTED.json",
            force=True,
            paper_evidence=False,
        )
        audit = json.loads((run_dir / "method_smoke_audit.json").read_text(encoding="utf-8"))
        p2 = json.loads((run_dir / "p2_invocation_states.json").read_text(encoding="utf-8"))
        row["P2_invoked"] = bool(audit.get("P2_invoked"))
        row["p2_states_len"] = len(p2) if isinstance(p2, list) else 0
        rows.append(row)
    payload = {
        "status": "PASS" if all(r.get("accepted") and r.get("P2_invoked") and r.get("p2_states_len", 0) > 0 for r in rows) else "FAIL",
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_SMOKE_RESULTS.json")
    return payload


def _worker(spec: dict, root_str: str, art_str: str, freeze: dict) -> dict:
    root = Path(root_str)
    art = Path(art_str)
    try:
        et = _eventtrace(root, spec["dataset"], int(spec["seed"]), smoke=False)
        run_dir = art / "corrective_runs" / spec["dataset"] / CORRECTIVE_METHOD / f"seed{spec['seed']}"
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


def run_corrective(root: Path, max_workers: int = 4) -> dict[str, Any]:
    art = art_path(root)
    freeze = json.loads((art / "E4_CORRECTIVE_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    matrix = build_corrective_matrix()
    dump_json(matrix, art / "E4_MINIMAL_CORRECTIVE_RERUN_MATRIX.json")
    (art / "corrective_runs").mkdir(parents=True, exist_ok=True)

    pending = []
    already = []
    for spec in matrix["rows"]:
        marker = (
            art / "corrective_runs" / spec["dataset"] / CORRECTIVE_METHOD / f"seed{spec['seed']}" / "FORMAL_ACCEPTED.json"
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
                        {k: row.get(k) for k in ("dataset", "method", "seed", "accepted", "status", "error")}
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
                    art / "E4_CORRECTIVE_PROGRESS.json",
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
    dump_json(payload, art / "E4_CORRECTIVE_RUN_STATUS.json")
    return payload


def seal_corrective(root: Path) -> dict[str, Any]:
    art = art_path(root)
    corr = art / "corrective_runs"
    rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            run = corr / dataset / CORRECTIVE_METHOD / f"seed{seed}"
            accepted = (run / "FORMAL_ACCEPTED.json").is_file()
            audit = (
                json.loads((run / "method_smoke_audit.json").read_text(encoding="utf-8"))
                if accepted else {}
            )
            p2 = (
                json.loads((run / "p2_invocation_states.json").read_text(encoding="utf-8"))
                if accepted else []
            )
            metrics = (
                json.loads((run / "final_metrics.json").read_text(encoding="utf-8"))
                if accepted else {}
            )
            rows.append({
                "dataset": dataset,
                "method": CORRECTIVE_METHOD,
                "seed": seed,
                "accepted": accepted,
                "P2_invoked": bool(audit.get("P2_invoked")),
                "p2_states_len": len(p2) if isinstance(p2, list) else 0,
                "RMSE_mu": metrics.get("RMSE_mu"),
                "Delta_group": metrics.get("Delta_group"),
                "Delta_c_s": metrics.get("Delta_c_s"),
            })
    ok = len(rows) == 40 and all(
        r["accepted"] and r["P2_invoked"] and r["p2_states_len"] > 0 for r in rows
    )
    payload = {
        "status": "SEALED" if ok else "BLOCKED",
        "accepted_corrective_runs": sum(1 for r in rows if r["accepted"]),
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_CORRECTIVE_RAW_RESULTS_SEAL.json")
    return payload


def write_provenance_and_index(root: Path) -> dict[str, Any]:
    art = art_path(root)
    parent = parent_path(root)
    corr = art / "corrective_runs"
    prov_rows: list[dict[str, Any]] = []
    index_rows: list[dict[str, Any]] = []

    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            index_rows.append({
                "dataset": dataset,
                "method": "raven",
                "seed": seed,
                "evidence_root": str(e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}"),
                "status": "VALID_REFERENCE",
                "source_round": "E3",
            })
        for method in ABLATIONS:
            for seed in FORMAL_SEEDS:
                parent_run = parent / "runs" / dataset / method / f"seed{seed}"
                if method == CORRECTIVE_METHOD:
                    corr_run = corr / dataset / method / f"seed{seed}"
                    prov_rows.append({
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "parent_path": str(parent_run),
                        "status": "SUPERSEDED_INVALID_P2_SKIP",
                        "replacement_path": str(corr_run),
                        "parent_deleted": False,
                    })
                    index_rows.append({
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "evidence_root": str(corr_run),
                        "status": "VALID_CORRECTIVE",
                        "source_round": "E4SR-R1",
                    })
                else:
                    prov_rows.append({
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "parent_path": str(parent_run),
                        "status": "RETAINED_VALID",
                        "replacement_path": "",
                        "parent_deleted": False,
                    })
                    index_rows.append({
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "evidence_root": str(parent_run),
                        "status": "VALID_PARENT",
                        "source_round": "E4",
                    })

    def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with path.open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    _csv(art / "E4_PROVENANCE_SUPERSESSION.csv", prov_rows)
    _csv(art / "E4_FINAL_VALID_EVIDENCE_INDEX.csv", index_rows)
    if len(index_rows) != 240:
        raise RuntimeError(f"expected 240 evidence cells, got {len(index_rows)}")
    dump_json(
        {
            "n_index": len(index_rows),
            "n_superseded": sum(1 for r in prov_rows if str(r["status"]).startswith("SUPERSEDED")),
        },
        art / "E4_EVIDENCE_INDEX_SUMMARY.json",
    )
    return {"n_index": len(index_rows), "n_prov": len(prov_rows)}
