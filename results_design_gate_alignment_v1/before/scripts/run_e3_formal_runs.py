#!/usr/bin/env python3
"""Execute E3 formal stages A/B/C (new runs only; sealed Traffic five never scheduled)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.formal.constants import ROUND, art_path  # noqa: E402
from raven_mcs.e3.formal.execute import run_logical  # noqa: E402
from raven_mcs.e3.formal.scheduler import stage_rows, update_progress  # noqa: E402
from raven_mcs.e3.formal.source_freeze import verify  # noqa: E402
from raven_mcs.e3.numerical.finite import metric_status  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = art_path(ROOT)
FIELDS = [
    "dataset",
    "method",
    "seed",
    "source_revision",
    "logical_run_id",
    "attempt_count",
    "scenario",
    "eventtrace_hash",
    "dataset_hash",
    "target_hash",
    "stratum_hash",
    "config_hash",
    "completed_windows",
    "checkpoint_present",
    "all_required_metrics_finite",
    "rmse_mu_status",
    "rmse_rho_status",
    "delta_group_status",
    "delta_cs_status",
    "head_tail_status",
    "ledger_status",
    "reused_or_new",
    "accepted",
]


def _status_row(result: dict, freeze: dict) -> dict:
    run_dir = ART / "runs" / result["dataset"] / result["method"] / f"seed{result['seed']}"
    metrics = {}
    if (run_dir / "final_metrics.json").is_file():
        metrics = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
    manifest = {}
    if (run_dir / "runtime_manifest.json").is_file():
        manifest = json.loads((run_dir / "runtime_manifest.json").read_text(encoding="utf-8"))
    central = str(result["method"]).startswith("central")
    et_id = (
        ART
        / "eventtraces"
        / result["dataset"]
        / f"seed{result['seed']}"
        / "training_eventtrace"
        / "trace_identity.json"
    )
    et_hash = None
    if et_id.is_file():
        et_hash = json.loads(et_id.read_text(encoding="utf-8")).get("trace_hash")
    target = {}
    if (run_dir / "target_wiring.json").is_file():
        target = json.loads((run_dir / "target_wiring.json").read_text(encoding="utf-8"))
    stratum = {}
    if (run_dir / "opportunity_stratum_identity.json").is_file():
        stratum = json.loads((run_dir / "opportunity_stratum_identity.json").read_text(encoding="utf-8"))
    return {
        "dataset": result.get("dataset"),
        "method": result.get("method"),
        "seed": result.get("seed"),
        "source_revision": freeze.get("git_commit"),
        "logical_run_id": result.get("logical_run_id"),
        "attempt_count": result.get("attempt_count"),
        "scenario": "complete_aligned",
        "eventtrace_hash": et_hash or manifest.get("EventTrace_hash"),
        "dataset_hash": json.loads(
            (ART / "E3_FORMAL_DATASET_HASH_AUDIT.json").read_text(encoding="utf-8")
        )
        .get(result["dataset"], {})
        .get("got"),
        "target_hash": target.get("artifact_sha256"),
        "stratum_hash": stratum.get("mapping_hash") or stratum.get("stratum_hash"),
        "config_hash": manifest.get("config_hash"),
        "completed_windows": result.get("completed_windows"),
        "checkpoint_present": (run_dir / "checkpoints" / "final.pt").is_file(),
        "all_required_metrics_finite": bool(result.get("accepted")),
        "rmse_mu_status": metric_status(metrics.get("RMSE_mu"), applicable=True),
        "rmse_rho_status": metric_status(metrics.get("RMSE_rho"), applicable=not central),
        "delta_group_status": metric_status(metrics.get("Delta_group"), applicable=not central),
        "delta_cs_status": metric_status(metrics.get("Delta_c_s"), applicable=not central),
        "head_tail_status": (
            "OK"
            if metric_status(metrics.get("Head_RMSE"), applicable=True) == "OK"
            and metric_status(metrics.get("Tail_RMSE"), applicable=True) == "OK"
            else "MISSING"
        ),
        "ledger_status": "OK" if (run_dir / "ledger.jsonl").is_file() else "MISSING",
        "reused_or_new": "new",
        "accepted": bool(result.get("accepted")),
    }


def _write_status(row: dict) -> None:
    path = ART / "E3_FORMAL_RUN_STATUS.csv"
    journal = ART / "E3_FORMAL_RUN_JOURNAL.jsonl"
    with journal.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    latest = {
        json.loads(x)["logical_run_id"]: json.loads(x)
        for x in journal.read_text(encoding="utf-8").splitlines()
        if x.strip()
    }
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for key in sorted(latest):
            w.writerow({k: latest[key].get(k) for k in FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("A", "B", "C", "all"), default="all")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()
    if args.max_workers != 1:
        print("NOTE: max_workers>1 reserved; executing serially for scientific isolation.")

    freeze_path = ART / "E3_FORMAL_SOURCE_FREEZE.json"
    if not freeze_path.is_file():
        print("missing E3_FORMAL_SOURCE_FREEZE.json — run freeze_e3_formal_source.py")
        return 2
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    drift = verify(ROOT, freeze)
    if drift:
        print(json.dumps({"status": "SOURCE_FREEZE_DRIFT", "drift": drift}, indent=2))
        return 5

    rows = stage_rows(args.stage, args.seed)
    dump_json(
        {
            "round": ROUND,
            "status": f"STAGE_{args.stage}_IN_PROGRESS",
            "n_scheduled": len(rows),
            "source_revision": freeze.get("git_commit"),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "formal_execution_started": True,
        },
        ART / "E3_FORMAL_RUNS_STOP_STATUS.json",
    )

    accepted = 0
    for i, spec in enumerate(rows, 1):
        print(
            f"[E3-FORMAL] {i}/{len(rows)} stage={spec['stage']} "
            f"{spec['dataset']} {spec['method']} seed={spec['seed']}",
            flush=True,
        )
        result = run_logical(
            root=ROOT,
            art=ART,
            dataset=spec["dataset"],
            method=spec["method"],
            seed=int(spec["seed"]),
            freeze=freeze,
        )
        update_progress(ART, result)
        status = _status_row(result, freeze)
        _write_status(status)
        print(
            json.dumps(
                {
                    "logical_run_id": result.get("logical_run_id"),
                    "accepted": result.get("accepted"),
                    "status": result.get("status") or result.get("execution_status"),
                    "error": result.get("error"),
                    "RMSE_mu_phys": result.get("RMSE_mu_phys"),
                }
            ),
            flush=True,
        )
        if not result.get("accepted"):
            dump_json(
                {
                    "round": ROUND,
                    "status": "E3_FORMAL_RUNS_BLOCKED_BY_SOFTWARE_FAILURE",
                    "failed": result,
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                },
                ART / "E3_FORMAL_RUNS_STOP_STATUS.json",
            )
            return 1
        accepted += 1

    dump_json(
        {
            "round": ROUND,
            "status": f"STAGE_{args.stage}_COMPLETE",
            "accepted_in_invocation": accepted,
            "source_revision": freeze.get("git_commit"),
            "updated_utc": datetime.now(timezone.utc).isoformat(),
        },
        ART / "E3_FORMAL_RUNS_STOP_STATUS.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
