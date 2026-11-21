#!/usr/bin/env python3
"""Seal E4 raw results only when all 200 accepted markers exist."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.constants import ABLATIONS, DATASETS, FORMAL_SEEDS, art_path  # noqa: E402
from raven_mcs.e4.matrix import build_matrix, logical_run_id  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def main() -> int:
    art = art_path(ROOT)
    freeze = json.loads((art / "E4_FORMAL_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    rows = build_matrix()["rows"]
    new_ids = []
    missing = []
    for r in rows:
        marker = art / "runs" / r["dataset"] / r["method"] / f"seed{r['seed']}" / "FORMAL_ACCEPTED.json"
        if marker.is_file():
            new_ids.append(r["logical_run_id"])
        else:
            missing.append(r["logical_run_id"])
    ref_ids = [
        f"e3::{ds}::complete_aligned::raven::seed{seed}"
        for ds in DATASETS
        for seed in FORMAL_SEEDS
    ]
    status_rows = []
    for r in rows:
        run_dir = art / "runs" / r["dataset"] / r["method"] / f"seed{r['seed']}"
        metrics = {}
        if (run_dir / "final_metrics.json").is_file():
            metrics = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
        et = ROOT / "artifacts/e3_formal_runs_r1/eventtraces" / r["dataset"] / f"seed{r['seed']}" / "training_eventtrace" / "trace_identity.json"
        et_hash = json.loads(et.read_text(encoding="utf-8")).get("trace_hash") if et.is_file() else None
        status_rows.append(
            {
                "dataset": r["dataset"],
                "seed": r["seed"],
                "ablation": r["method"],
                "logical_run_id": r["logical_run_id"],
                "attempt_count": 1,
                "eventtrace_hash": et_hash,
                "source_revision": freeze.get("source_manifest_hash"),
                "completed_windows": bool(
                    (run_dir / "FORMAL_ACCEPTED.json").is_file()
                    and json.loads((run_dir / "FORMAL_ACCEPTED.json").read_text(encoding="utf-8")).get("completed_windows")
                ),
                "checkpoint_present": (run_dir / "checkpoints" / "final.pt").is_file(),
                "rmse_mu_status": "FINITE" if np_finite(metrics.get("RMSE_mu")) else "MISSING",
                "tail_rmse_status": "FINITE" if np_finite(metrics.get("Tail_RMSE")) else "MISSING",
                "delta_group_status": "FINITE" if np_finite(metrics.get("Delta_group")) else "MISSING",
                "delta_cs_status": "FINITE" if np_finite(metrics.get("Delta_c_s")) else "MISSING",
                "p2_status": "PRESENT" if (run_dir / "p2_invocation_states.json").is_file() or r["method"] == "raven_wo_inst" else "MISSING",
                "ledger_status": "PRESENT" if (run_dir / "ledger.jsonl").is_file() else "MISSING",
                "accepted": marker_exists(run_dir),
            }
        )
    import csv

    with (art / "E4_FORMAL_RUN_STATUS.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(status_rows[0].keys()) if status_rows else ["dataset"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(status_rows)

    # per-seed completeness
    complete_rows = []
    for ds in DATASETS:
        for seed in FORMAL_SEEDS:
            ok = all(
                (art / "runs" / ds / method / f"seed{seed}" / "FORMAL_ACCEPTED.json").is_file()
                for method in ABLATIONS
            ) and (
                ROOT / "artifacts/e3_formal_runs_r1/runs" / ds / "raven" / f"seed{seed}" / "FORMAL_ACCEPTED.json"
            ).is_file()
            complete_rows.append({"dataset": ds, "seed": seed, "complete": ok})
    with (art / "E4_PER_SEED_COMPLETENESS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dataset", "seed", "complete"])
        writer.writeheader()
        writer.writerows(complete_rows)

    sealed = len(missing) == 0 and all(r["complete"] for r in complete_rows)
    dump_json(
        {
            "status": "SEALED" if sealed else "BLOCKED",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "accepted_new_runs": len(new_ids),
            "expected_new_runs": 200,
            "missing_new_runs": missing,
            "new_run_ids": new_ids,
            "reused_raven_reference_ids": ref_ids,
            "source_manifest_hash": freeze.get("source_manifest_hash"),
            "ablation_counts": {m: 40 for m in ABLATIONS} if sealed else None,
            "dataset_counts": {"sensorscope": 100, "uair": 100} if sealed else None,
            "seed_counts": {str(s): 10 for s in FORMAL_SEEDS} if sealed else None,
        },
        art / "E4_RAW_RESULTS_SEAL.json",
    )
    return 0 if sealed else 1


def np_finite(v) -> bool:
    try:
        import math

        return v is not None and math.isfinite(float(v))
    except Exception:
        return False


def marker_exists(run_dir: Path) -> bool:
    return (run_dir / "FORMAL_ACCEPTED.json").is_file()


if __name__ == "__main__":
    raise SystemExit(main())
