#!/usr/bin/env python3
"""Compact evidence replay from Ledger + manifests (not gate booleans alone)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from raven_mcs.e2.traffic_real_runner.ledger_g9 import evaluate_g9
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
CANARY = ROOT / "outputs/e2_traffic_real_runner_canary"


def main() -> int:
    stop = json.loads((CANARY / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json").read_text(encoding="utf-8"))
    main_df = pd.read_csv(CANARY / "main_results_seed29001.csv")
    noninsp = json.loads(
        (ROOT / "outputs/audits/E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json").read_text(
            encoding="utf-8",
        )
    )
    g9 = evaluate_g9(
        root=ROOT,
        ledger_path=LEDGER,
        canary_out=CANARY,
        noninsp=noninsp,
        require_junit=True,
    )
    training_finish = 0
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("run_kind") == "training" and row.get("record_type") == "FINISH":
                training_finish += 1
    checks = {
        "stop_ready": stop.get("status") == "READY_FOR_TRAFFIC_E2_FORMAL_RUNS",
        "seed_29001": int(stop.get("seed", 0)) == 29001,
        "fresh_rerun": stop.get("fresh_rerun") is True,
        "reaudit_only_false": stop.get("reaudit_only") is False,
        "ledger_training_finish_30": training_finish == 30,
        "g9_pass_from_ledger": g9.get("pass") is True,
        "main_rows_30": len(main_df) == 30,
        "windows_100": int(main_df["completed_windows"].min()) == 100 and int(main_df["completed_windows"].max()) == 100,
        "gap_identity": bool((
            (main_df["Gap_mis"] - (main_df["RMSE_mu"] - main_df["RMSE_rho"])).abs() < 1e-9
        ).all()),
        "no_retry": int(main_df["retry_count"].sum()) == 0,
        "checkpoints_30": int(stop.get("checkpoint_count", 0)) == 30,
    }
    payload = {
        "protocol": PACKAGE,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "g9_diagnostics": {
            "training_finish_count": g9.get("training_finish_count"),
            "unique_scenario_method_count": g9.get("unique_scenario_method_count"),
            "status": g9.get("status"),
        },
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
