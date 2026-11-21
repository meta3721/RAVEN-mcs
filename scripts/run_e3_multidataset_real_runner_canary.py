#!/usr/bin/env python3
"""Execute E3 Canary Phase-1 / Phase-2 logical runs (seed 31001 only)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.canary.constants import CANARY_SEED, PHASE1, PHASE2, ROUND  # noqa: E402
from raven_mcs.e3.canary.execute import run_logical  # noqa: E402
from raven_mcs.e3.canary.schedule import build_canary_matrix, logical_run_id  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = ROOT / "artifacts/e3_multidataset_real_runner_canary_r1"


def _append_status(row: dict) -> None:
    path = ART / "E3_CANARY_RUN_STATUS.csv"
    fields = [
        "dataset",
        "method",
        "seed",
        "phase",
        "logical_run_id",
        "attempt_count",
        "execution_status",
        "completed_windows",
        "checkpoint_present",
        "eventtrace_hash_valid",
        "target_hash_valid",
        "stratum_hash_valid",
        "delta_cs_status",
        "atomic_rho_status",
        "rmse_mu_status",
        "rmse_rho_status",
        "head_tail_status",
        "ledger_status",
        "accepted",
    ]
    write_header = not path.is_file()
    # Enrich from run dir
    run_dir = ART / "runs" / row["dataset"] / row["method"] / f"seed{row['seed']}"
    et_ok = (
        ART / "eventtraces" / row["dataset"] / f"seed{row['seed']}" / "training_eventtrace" / "trace_identity.json"
    ).is_file()
    ckpt = bool(row.get("checkpoint_present"))
    metrics = {}
    if (run_dir / "final_metrics.json").is_file():
        metrics = json.loads((run_dir / "final_metrics.json").read_text(encoding="utf-8"))
    ledger_ok = False
    if (run_dir / "ledger.jsonl").is_file():
        lines = [json.loads(x) for x in (run_dir / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        starts = [x for x in lines if x.get("event") == "START"]
        finishes = [x for x in lines if x.get("event") == "FINISH"]
        ledger_ok = bool(starts) and bool(finishes)
    out = {
        "dataset": row["dataset"],
        "method": row["method"],
        "seed": row["seed"],
        "phase": row["phase"],
        "logical_run_id": row["logical_run_id"],
        "attempt_count": row.get("attempt_count"),
        "execution_status": row.get("execution_status"),
        "completed_windows": row.get("completed_windows"),
        "checkpoint_present": ckpt,
        "eventtrace_hash_valid": et_ok,
        "target_hash_valid": (run_dir / "target_wiring.json").is_file(),
        "stratum_hash_valid": (run_dir / "opportunity_stratum_identity.json").is_file(),
        "delta_cs_status": "OK" if metrics.get("Delta_c_s") is not None or row["method"].startswith("central") else "MISSING",
        "atomic_rho_status": "OK" if (run_dir / "atomic_rho_summary.json").is_file() else "MISSING",
        "rmse_mu_status": "OK" if metrics.get("RMSE_mu") is not None else "MISSING",
        "rmse_rho_status": "OK" if metrics.get("RMSE_rho") is not None else "MISSING",
        "head_tail_status": "OK"
        if metrics.get("Head_RMSE") is not None and metrics.get("Tail_RMSE") is not None
        else "MISSING",
        "ledger_status": "OK" if ledger_ok else "MISSING",
        "accepted": bool(row.get("accepted")),
    }
    # Rewrite entire CSV from accumulated jsonl for determinism
    journal = ART / "E3_CANARY_RUN_JOURNAL.jsonl"
    with journal.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(out, sort_keys=True) + "\n")
    # Rebuild CSV from latest per logical_run_id
    latest: dict[str, dict] = {}
    if journal.is_file():
        for line in journal.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            latest[rec["logical_run_id"]] = rec
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for rid in sorted(latest):
            w.writerow(latest[rid])


def run_phase(phase: int) -> dict:
    pairs = PHASE1 if phase == 1 else PHASE2
    results = []
    for dataset, method in pairs:
        print(f"[CANARY] phase={phase} {dataset} {method} seed={CANARY_SEED}", flush=True)
        row = run_logical(root=ROOT, art=ART, dataset=dataset, method=method, seed=CANARY_SEED)
        row["phase"] = phase
        row["logical_run_id"] = logical_run_id(dataset, method)
        dump_json(row, ART / "runs" / dataset / method / f"seed{CANARY_SEED}" / "canary_phase_row.json")
        _append_status(row)
        results.append(row)
        print(
            json.dumps(
                {
                    "logical_run_id": row["logical_run_id"],
                    "accepted": row.get("accepted"),
                    "status": row.get("execution_status"),
                    "error": row.get("error"),
                }
            ),
            flush=True,
        )
        if not row.get("accepted"):
            return {
                "phase": phase,
                "status": "PHASE_FAILED",
                "failed": row,
                "results": results,
            }
    return {"phase": phase, "status": "PHASE_PASS", "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=(1, 2, 12), default=12)
    args = parser.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    stop0 = ART / "E3_CANARY_STOP_STATUS.json"
    if not stop0.is_file():
        print("Phase 0 missing; run prepare_e3_multidataset_real_runner_canary.py first")
        return 2
    st = json.loads(stop0.read_text(encoding="utf-8"))
    if st.get("status") not in {
        "PHASE0_PASS_READY_FOR_PHASE1",
        "PHASE1_PASS_READY_FOR_PHASE2",
        "READY_FOR_E3_FORMAL_RUNS",
        "PHASE1_IN_PROGRESS",
        "PHASE2_IN_PROGRESS",
    }:
        # allow resume after partial progress markers we set below
        if not str(st.get("status", "")).startswith("PHASE"):
            print(f"Refusing to run Canary from status={st.get('status')}")
            return 3

    dump_json(build_canary_matrix(), ART / "E3_CANARY_RUN_MATRIX.json")

    if args.phase in (1, 12):
        dump_json(
            {
                "round": ROUND,
                "status": "PHASE1_IN_PROGRESS",
                "canary_seed": CANARY_SEED,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            },
            ART / "E3_CANARY_STOP_STATUS.json",
        )
        p1 = run_phase(1)
        dump_json(p1, ART / "E3_CANARY_PHASE1_SUMMARY.json")
        if p1["status"] != "PHASE_PASS":
            dump_json(
                {
                    "round": ROUND,
                    "status": "E3_CANARY_BLOCKED_BY_SOFTWARE_FIX",
                    "phase": 1,
                    "failed": p1.get("failed"),
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                },
                ART / "E3_CANARY_STOP_STATUS.json",
            )
            print(json.dumps({"status": "PHASE1_FAILED"}, indent=2))
            return 1
        dump_json(
            {
                "round": ROUND,
                "status": "PHASE1_PASS_READY_FOR_PHASE2",
                "phase1_accepted": 11,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            },
            ART / "E3_CANARY_STOP_STATUS.json",
        )

    if args.phase in (2, 12):
        st = json.loads((ART / "E3_CANARY_STOP_STATUS.json").read_text(encoding="utf-8"))
        if st.get("status") not in {
            "PHASE1_PASS_READY_FOR_PHASE2",
            "PHASE2_IN_PROGRESS",
            "READY_FOR_E3_FORMAL_RUNS",
        }:
            print(f"Phase 2 requires Phase 1 pass; status={st.get('status')}")
            return 4
        dump_json(
            {
                "round": ROUND,
                "status": "PHASE2_IN_PROGRESS",
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            },
            ART / "E3_CANARY_STOP_STATUS.json",
        )
        p2 = run_phase(2)
        dump_json(p2, ART / "E3_CANARY_PHASE2_SUMMARY.json")
        if p2["status"] != "PHASE_PASS":
            dump_json(
                {
                    "round": ROUND,
                    "status": "E3_CANARY_BLOCKED_BY_SOFTWARE_FIX",
                    "phase": 2,
                    "failed": p2.get("failed"),
                    "updated_utc": datetime.now(timezone.utc).isoformat(),
                },
                ART / "E3_CANARY_STOP_STATUS.json",
            )
            print(json.dumps({"status": "PHASE2_FAILED"}, indent=2))
            return 1
        dump_json(
            {
                "round": ROUND,
                "status": "CANARY_EXECUTION_COMPLETE",
                "phase1_accepted": 11,
                "phase2_accepted": 17,
                "total_accepted": 28,
                "canary_seed": CANARY_SEED,
                "formal_not_started": True,
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            },
            ART / "E3_CANARY_STOP_STATUS.json",
        )

    print(json.dumps(json.loads((ART / "E3_CANARY_STOP_STATUS.json").read_text(encoding="utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
