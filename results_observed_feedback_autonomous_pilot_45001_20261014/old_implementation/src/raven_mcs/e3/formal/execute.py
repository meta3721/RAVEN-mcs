"""Formal marker wrapper around the stable canary real-execution path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raven_mcs.e3.canary.constants import FROZEN_DATASET_HASHES
from raven_mcs.e3.canary.dataset_load import load_paper_dataset
from raven_mcs.e3.canary.execute import run_logical as _run_canary
from raven_mcs.e3.formal.eventtrace import ensure_eventtrace
from raven_mcs.e3.formal.matrix import logical_run_id
from raven_mcs.e3.formal.metric_scale import convert_metrics, policy
from raven_mcs.e3.formal.source_freeze import verify
from raven_mcs.utils.serialization import dump_json


def run_logical(
    *,
    root: Path,
    art: Path,
    dataset: str,
    method: str,
    seed: int,
    freeze: dict,
    force: bool = False,
) -> dict[str, Any]:
    if int(seed) == 31001:
        raise ValueError("canary seed 31001 is forbidden in formal stats")
    run_dir = art / "runs" / dataset / method / f"seed{seed}"
    marker = run_dir / "FORMAL_ACCEPTED.json"
    if marker.is_file() and not force:
        prior = json.loads(marker.read_text(encoding="utf-8"))
        if prior.get("source_manifest_hash") == freeze.get("source_manifest_hash"):
            return {"status": "ALREADY_ACCEPTED", **prior}

    drift = verify(root, freeze)
    if drift:
        raise RuntimeError(f"SOURCE_FREEZE_DRIFT: {drift}")

    # Provision EventTrace first so canary ensure reuses Traffic E2 copy / SS-UA cache.
    ensure_eventtrace(root, art, dataset, seed)

    source_identity = {
        "git_commit": freeze.get("git_commit"),
        "source_manifest_hash": freeze.get("source_manifest_hash"),
        "runner_source_hash": (freeze.get("source_hashes") or {}).get(
            "src/raven_mcs/e3/real_runner/runner.py"
        ),
        "method_source_hash": (freeze.get("source_hashes") or {}).get(
            "src/raven_mcs/training/window_runner.py"
        )
        or freeze.get("source_manifest_hash"),
        "dataset_hash": FROZEN_DATASET_HASHES.get(str(dataset).lower()),
    }
    row = _run_canary(
        root=root,
        art=art,
        dataset=dataset,
        method=method,
        seed=seed,
        force=force,
        accepted_marker_name="FORMAL_ACCEPTED.json",
        source_identity_override=source_identity,
    )
    row["logical_run_id"] = logical_run_id(dataset, method, seed)
    row["source_manifest_hash"] = freeze.get("source_manifest_hash")
    row["source_revision"] = freeze.get("git_commit")
    row["reused_or_new"] = "new"

    if row.get("accepted"):
        ds = load_paper_dataset(root, dataset)
        sigma = float(getattr(ds, "_scaler_std", 1.0)) if getattr(ds, "_standardized", False) else None
        scale = policy(dataset, reused=False, sigma=sigma)
        metrics_path = run_dir / "final_metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.is_file() else {}
        dual = convert_metrics(metrics, scale)
        dump_json(dual, run_dir / "final_metrics_dual_domain.json")
        dump_json(scale, run_dir / "metric_scale_policy.json")
        row["RMSE_mu_std"] = dual.get("RMSE_mu_std")
        row["RMSE_mu_phys"] = dual.get("RMSE_mu_phys")
        row["metric_scale_status"] = scale.get("status")
        dump_json(row, marker)
    return row
