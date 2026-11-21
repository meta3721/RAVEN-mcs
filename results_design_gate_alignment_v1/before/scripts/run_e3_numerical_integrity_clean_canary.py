#!/usr/bin/env python3
"""Execute freeze-bound clean E3 numerical-integrity canary phases."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED, PHASE1, PHASE2  # noqa: E402
from raven_mcs.e3.canary.execute import run_logical  # noqa: E402
from raven_mcs.e3.canary.schedule import build_canary_matrix, logical_run_id  # noqa: E402
from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH, ROUND, SOURCE_FREEZE_FILE  # noqa: E402
from raven_mcs.e3.numerical.finite import metric_status, required_metrics_finite  # noqa: E402
from raven_mcs.e3.numerical.source_freeze import (  # noqa: E402
    load_freeze,
    verify_freeze_matches_workspace,
)
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
FIELDS = [
    "dataset",
    "method",
    "seed",
    "logical_run_id",
    "attempt_count",
    "source_revision",
    "completed_windows",
    "checkpoint_present",
    "all_required_metrics_finite",
    "model_state_finite",
    "prediction_finite",
    "rmse_mu_status",
    "rmse_rho_status",
    "delta_cs_status",
    "atomic_rho_status",
    "ledger_status",
    "accepted",
]


def _append_status(row: dict, freeze: dict) -> None:
    run_dir = ART / "runs" / row["dataset"] / row["method"] / f"seed{row['seed']}"
    metrics_path = run_dir / "final_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.is_file() else {}
    central = row["method"].startswith("central")
    required = ["RMSE_mu", "MAE_mu", "Head_RMSE", "Tail_RMSE", "RMSE_rho"]
    out = {
        "dataset": row.get("dataset"),
        "method": row.get("method"),
        "seed": row.get("seed"),
        "logical_run_id": row.get("logical_run_id"),
        "attempt_count": row.get("attempt_count"),
        "source_revision": freeze.get("git_commit"),
        "completed_windows": row.get("completed_windows"),
        "checkpoint_present": (run_dir / "checkpoints" / "final.pt").is_file(),
        "all_required_metrics_finite": required_metrics_finite(metrics, required + ([] if central else ["Delta_c_s"])),
        "model_state_finite": bool(row.get("accepted", False)),
        "prediction_finite": bool(row.get("accepted", False)),
        "rmse_mu_status": metric_status(metrics.get("RMSE_mu"), applicable=True),
        "rmse_rho_status": metric_status(metrics.get("RMSE_rho"), applicable=not central),
        "delta_cs_status": metric_status(metrics.get("Delta_c_s"), applicable=not central),
        "atomic_rho_status": "N_A" if central else ("OK" if (run_dir / "atomic_rho_summary.json").is_file() else "MISSING"),
        "ledger_status": "OK" if (run_dir / "ledger.jsonl").is_file() else "MISSING",
        "accepted": bool(row.get("accepted")),
    }
    journal = ART / "E3_CANARY_RUN_JOURNAL.jsonl"
    with journal.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(out, sort_keys=True) + "\n")
    latest = {
        r["logical_run_id"]: r
        for r in (json.loads(x) for x in journal.read_text(encoding="utf-8").splitlines() if x.strip())
    }
    for name in ("E3_CLEAN_CANARY_RUN_STATUS.csv", "E3_CANARY_RUN_STATUS.csv"):
        with (ART / name).open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(latest[key] for key in sorted(latest))


def _run_phase(phase: int, freeze: dict, force: bool) -> dict:
    rows = []
    for dataset, method in (PHASE1 if phase == 1 else PHASE2):
        row = run_logical(root=ROOT, art=ART, dataset=dataset, method=method, seed=CANARY_SEED, force=force)
        row.update({"phase": phase, "logical_run_id": logical_run_id(dataset, method)})
        dump_json(row, ART / "runs" / dataset / method / f"seed{CANARY_SEED}" / "canary_phase_row.json")
        _append_status(row, freeze)
        rows.append(row)
        if not row.get("accepted"):
            return {"phase": phase, "status": "PHASE_FAILED", "failed": row, "results": rows}
    return {"phase": phase, "status": "PHASE_PASS", "results": rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=(1, 2, 12), default=12)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    freeze = load_freeze(ART)
    if freeze is None or not (ART / SOURCE_FREEZE_FILE).is_file():
        print("Refusing Phase 1: E3_CLEAN_CANARY_SOURCE_FREEZE.json is required.")
        return 2
    drift = verify_freeze_matches_workspace(ROOT, freeze)
    if drift:
        print(json.dumps({"status": "SOURCE_FREEZE_DRIFT", "drift": drift}, indent=2))
        return 5
    if args.fresh:
        for path in (ART / "runs").rglob("CANARY_ACCEPTED.json") if (ART / "runs").is_dir() else []:
            path.unlink()
        for name in ("E3_CANARY_RUN_JOURNAL.jsonl", "E3_CANARY_RUN_STATUS.csv"):
            (ART / name).unlink(missing_ok=True)
    force = bool(args.fresh or freeze.get("force_clean_run"))
    dump_json(build_canary_matrix(), ART / "E3_CANARY_RUN_MATRIX.json")
    for phase in ((1, 2) if args.phase == 12 else (args.phase,)):
        dump_json({"round": ROUND, "status": f"PHASE{phase}_IN_PROGRESS", "canary_seed": CANARY_SEED,
                   "source_revision": freeze.get("git_commit"), "updated_utc": datetime.now(timezone.utc).isoformat()},
                  ART / "E3_CANARY_STOP_STATUS.json")
        summary = _run_phase(phase, freeze, force)
        dump_json(summary, ART / f"E3_CANARY_PHASE{phase}_SUMMARY.json")
        if summary["status"] != "PHASE_PASS":
            dump_json({"round": ROUND, "status": "E3_CANARY_BLOCKED_BY_SOFTWARE_FIX", "phase": phase,
                       "failed": summary["failed"], "formal_not_started": True}, ART / "E3_CANARY_STOP_STATUS.json")
            return 1
    dump_json({"round": ROUND, "status": "CANARY_EXECUTION_COMPLETE", "canary_seed": CANARY_SEED,
               "formal_not_started": True, "total_accepted": 28, "source_revision": freeze.get("git_commit")},
              ART / "E3_CANARY_STOP_STATUS.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
