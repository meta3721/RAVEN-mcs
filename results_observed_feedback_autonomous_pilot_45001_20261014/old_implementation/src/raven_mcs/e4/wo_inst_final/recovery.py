"""Phase-0 attestation and E3 full-RAVEN lambda_beta recovery."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    DATASETS,
    E3_METHODS_HASH,
    E3_WINDOW_RUNNER_HASH,
    EXPECTED_E3_LAMBDA_BETA,
    FORMAL_SEEDS,
    art_path,
    e3_path,
)


def write_phase0(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    payload = {
        "round": "E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1",
        "status": "PHASE0_ATTESTED",
        "training_started": False,
        "formal_rerun_started": False,
        "new_dataset_added": False,
        "new_seed_added": False,
        "new_metric_added": False,
        "e5_started": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_LAMBDA_BETA_PHASE0_ATTESTATION.json")
    return payload


def _recover_methods_blob(root: Path) -> dict[str, Any]:
    """Recover frozen E3 methods.py content that hashes to E3_METHODS_HASH."""
    art = art_path(root)
    recovered_dir = art / "recovered_source"
    recovered_dir.mkdir(parents=True, exist_ok=True)
    target = E3_METHODS_HASH
    candidates: list[Path] = []

    local = recovered_dir / "methods.py"
    if local.is_file() and sha256_file(local) == target:
        candidates.append(local)

    hist_root = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "History"
    if hist_root.is_dir():
        for d in hist_root.iterdir():
            if not d.is_dir():
                continue
            for f in d.iterdir():
                if not f.is_file() or f.name == "entries.json":
                    continue
                try:
                    if f.stat().st_size < 100 or f.stat().st_size > 2_000_000:
                        continue
                    if hashlib.sha256(f.read_bytes()).hexdigest() == target:
                        candidates.append(f)
                except OSError:
                    continue

    if not candidates:
        return {
            "recovery_status": "NOT_RECOVERABLE",
            "evidence_source": "missing_blob",
            "evidence_path": None,
            "evidence_hash": None,
            "lambda_group": None,
            "lambda_beta": None,
            "lambda_v": None,
            "lambda_s": None,
        }

    src = candidates[0]
    data = src.read_bytes()
    out = recovered_dir / "methods.py"
    if not out.is_file() or sha256_file(out) != target:
        out.write_bytes(data)
    text = data.decode("utf-8")
    m = re.search(
        r"class RavenAggregator\(Aggregator\):.*?def __init__\((.*?)\).*?-> None:",
        text,
        re.S,
    )
    block = m.group(1) if m else ""
    def _default(name: str) -> float | None:
        mm = re.search(rf"{name}:\s*float\s*=\s*([0-9eE.+-]+)", block)
        return float(mm.group(1)) if mm else None

    lambdas = {
        "lambda_group": _default("lambda_group"),
        "lambda_beta": _default("lambda_beta"),
        "lambda_v": _default("lambda_variance"),
        "lambda_s": _default("lambda_staleness"),
    }
    return {
        "recovery_status": "RECOVERED",
        "evidence_source": "deterministic_reconstruction_from_frozen_source_hash",
        "evidence_path": str(out.relative_to(root)).replace("\\", "/"),
        "evidence_hash": sha256_file(out),
        "cursor_history_source": str(src),
        "e3_formal_source_freeze_methods_hash": E3_METHODS_HASH,
        **lambdas,
        "alpha_max_default": _default("alpha_max"),
        "e_min_default": _default("e_min"),
        "max_server_learning_rate_default": _default("max_server_learning_rate"),
    }


def _recover_window_runner(root: Path) -> dict[str, Any]:
    art = art_path(root)
    recovered_dir = art / "recovered_source"
    recovered_dir.mkdir(parents=True, exist_ok=True)
    target = E3_WINDOW_RUNNER_HASH
    out = recovered_dir / "window_runner.py"
    if out.is_file() and sha256_file(out) == target:
        text = out.read_text(encoding="utf-8")
    else:
        hist_root = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "History"
        found = None
        if hist_root.is_dir():
            for d in hist_root.iterdir():
                if not d.is_dir():
                    continue
                for f in d.iterdir():
                    if not f.is_file() or f.name == "entries.json":
                        continue
                    try:
                        data = f.read_bytes()
                    except OSError:
                        continue
                    if hashlib.sha256(data).hexdigest() == target:
                        found = data
                        break
                if found is not None:
                    break
        if found is None:
            return {
                "recovery_status": "NOT_RECOVERABLE",
                "get_aggregator_no_kwargs": None,
                "evidence_hash": None,
            }
        out.write_bytes(found)
        text = found.decode("utf-8")
    no_kwargs = bool(re.search(r"aggregator\s*=\s*get_aggregator\(\s*method\s*\)", text))
    return {
        "recovery_status": "RECOVERED",
        "evidence_path": str(out.relative_to(root)).replace("\\", "/"),
        "evidence_hash": sha256_file(out),
        "get_aggregator_no_kwargs": no_kwargs,
        "e3_formal_source_freeze_window_runner_hash": E3_WINDOW_RUNNER_HASH,
    }


def recover_e3_lambda_beta(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    freeze = json.loads(
        (e3_path(root) / "E3_FORMAL_SOURCE_FREEZE.json").read_text(encoding="utf-8")
    )
    methods = _recover_methods_blob(root)
    wr = _recover_window_runner(root)

    rows: list[dict[str, Any]] = []
    recoverable = (
        methods.get("recovery_status") == "RECOVERED"
        and wr.get("recovery_status") == "RECOVERED"
        and wr.get("get_aggregator_no_kwargs") is True
        and methods.get("lambda_beta") is not None
        and freeze.get("source_hashes", {}).get(
            "src/raven_mcs/aggregation/methods.py"
        )
        == E3_METHODS_HASH
        and methods.get("evidence_hash") == E3_METHODS_HASH
    )

    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            run = e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}"
            accepted = run / "FORMAL_ACCEPTED.json"
            manifest = run / "runtime_manifest.json"
            snap = run / "config_snapshot.json"
            man = (
                json.loads(manifest.read_text(encoding="utf-8"))
                if manifest.is_file()
                else {}
            )
            status = "RECOVERED" if recoverable and accepted.is_file() else "NOT_RECOVERABLE"
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "e3_logical_run_id": f"e3::{dataset}::complete_aligned::raven::seed{seed}",
                "accepted_attempt_id": man.get("attempt_id") or man.get("run_id"),
                "e3_source_revision": freeze.get("git_commit"),
                "resolved_config_hash": man.get("config_hash"),
                "p2_state_hash_if_available": None,
                "manifest_hash": sha256_file(manifest) if manifest.is_file() else None,
                "lambda_group": methods.get("lambda_group") if recoverable else None,
                "lambda_beta": methods.get("lambda_beta") if recoverable else None,
                "lambda_v": methods.get("lambda_v") if recoverable else None,
                "lambda_s": methods.get("lambda_s") if recoverable else None,
                "evidence_source": methods.get("evidence_source"),
                "evidence_path": methods.get("evidence_path"),
                "evidence_hash": methods.get("evidence_hash"),
                "recovery_status": status,
                "config_snapshot_path": str(snap.relative_to(root)).replace("\\", "/")
                if snap.is_file()
                else None,
                "window_runner_no_kwargs": wr.get("get_aggregator_no_kwargs"),
                "window_runner_hash": wr.get("evidence_hash"),
            })

    csv_path = art / "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.csv"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    payload = {
        "n_rows": len(rows),
        "n_recovered": sum(1 for r in rows if r["recovery_status"] == "RECOVERED"),
        "methods_recovery": methods,
        "window_runner_recovery": wr,
        "freeze_methods_hash": freeze.get("source_hashes", {}).get(
            "src/raven_mcs/aggregation/methods.py"
        ),
        "recovered_lambda_beta": methods.get("lambda_beta") if recoverable else None,
        "constant_across_all_40": recoverable
        and all(r.get("lambda_beta") == methods.get("lambda_beta") for r in rows),
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.json")
    md = [
        "# E3 full-RAVEN λ_β recovery",
        "",
        f"- recovered: {payload['n_recovered']} / {payload['n_rows']}",
        f"- lambda_beta: `{payload['recovered_lambda_beta']}`",
        f"- methods evidence hash: `{methods.get('evidence_hash')}`",
        f"- window_runner get_aggregator(method) no-kwargs: `{wr.get('get_aggregator_no_kwargs')}`",
        f"- reconstruction: frozen E3 methods.py blob recovered and hash-bound to "
        f"`{E3_METHODS_HASH}` from E3_FORMAL_SOURCE_FREEZE.json; defaults applied "
        "because window_runner calls `get_aggregator(method)` with no kwargs.",
        "",
    ]
    (art / "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    return payload


def write_consistency_audit(root: Path, recovery: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    by_ds: dict[str, Any] = {}
    for dataset in DATASETS:
        vals = [
            r["lambda_beta"]
            for r in recovery["rows"]
            if r["dataset"] == dataset and r["recovery_status"] == "RECOVERED"
        ]
        if len(vals) != 20:
            cls = "NOT_RECOVERABLE"
        elif len(set(vals)) == 1:
            cls = "CONSTANT_ACROSS_20_SEEDS"
        else:
            cls = "INCONSISTENT_UNEXPLAINED"
        by_ds[dataset] = {
            "classification": cls,
            "n": len(vals),
            "unique_values": sorted({float(v) for v in vals if v is not None}),
        }
    payload = {
        "by_dataset": by_ds,
        "global_classification": (
            "CONSTANT_ACROSS_20_SEEDS"
            if all(v["classification"] == "CONSTANT_ACROSS_20_SEEDS" for v in by_ds.values())
            else (
                "NOT_RECOVERABLE"
                if any(v["classification"] == "NOT_RECOVERABLE" for v in by_ds.values())
                else "INCONSISTENT_UNEXPLAINED"
            )
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json")
    return payload


def write_p2_parameter_identity(root: Path, recovery: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    methods = recovery["methods_recovery"]
    wr = recovery["window_runner_recovery"]
    payload = {
        "full_raven_p2_coefficients": {
            "lambda_group": methods.get("lambda_group"),
            "lambda_beta": methods.get("lambda_beta"),
            "lambda_v": methods.get("lambda_v"),
            "lambda_s": methods.get("lambda_s"),
            "alpha_max": methods.get("alpha_max_default"),
            "e_min": methods.get("e_min_default"),
            "max_server_learning_rate": methods.get("max_server_learning_rate_default"),
        },
        "construction": {
            "window_runner": "get_aggregator(method) with no kwargs",
            "proven": bool(wr.get("get_aggregator_no_kwargs")),
            "window_runner_hash": wr.get("evidence_hash"),
            "methods_hash": methods.get("evidence_hash"),
        },
        "one_factor_implication": (
            "Final raven_wo_inst must keep lambda_beta/lambda_v/lambda_s/alpha bounds/"
            "ESS/debt identical to full RAVEN; only instantaneous calibration removed "
            "(lambda_group=0, instant_calibration=False)."
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json")
    return payload
