#!/usr/bin/env python3
"""E2RR-G1..G10 gates with strict ledger-closure G9."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.e2.traffic_real_runner.ledger_g9 import evaluate_g9
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
CANARY = ROOT / "outputs/e2_traffic_real_runner_canary"
STOP = CANARY / "E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json"
SCENARIOS = [
    "balanced", "opportunity_only", "observation_only",
    "usable_only", "complete_aligned", "complete_counteracting",
]
METHODS = [
    "fedavg_window", "fedasync_window", "flamf_timealign_adapted",
    "twostage_hajek", "raven",
]


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    identity = j("outputs/audits/E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json")
    cross = j("outputs/audits/E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json")
    raven = j("outputs/audits/E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json")
    base = j("outputs/audits/E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json")
    metric = j("outputs/audits/E2_TRAFFIC_CANARY_METRIC_CONSISTENCY_AUDIT.json")
    num = j("outputs/audits/E2_TRAFFIC_CANARY_NUMERICAL_STABILITY_AUDIT.json")
    noninsp = j("outputs/audits/E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json")
    stop = j("outputs/e2_traffic_real_runner_canary/E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json")
    summary = j("outputs/e2_traffic_real_runner_canary/canary_summary_seed29001.json")
    registry = j("configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json")

    artifacts_ok = all(
        (CANARY / "runs" / sid / method / "checkpoints" / "final.pt").is_file()
        and (CANARY / "runs" / sid / method / "runtime_manifest.json").is_file()
        for sid in SCENARIOS for method in METHODS
    )
    result_files = all(
        (CANARY / name).is_file()
        for name in (
            "main_results_seed29001.csv",
            "main_results_seed29001.parquet",
            "group_metrics_seed29001.csv",
            "runtime_metrics_seed29001.csv",
            "communication_metrics_seed29001.csv",
            "stage_metrics_seed29001.csv",
            "clip_metrics_seed29001.csv",
            "p2_metrics_seed29001.csv",
            "run_manifest_seed29001.json",
            "canary_summary_seed29001.json",
        )
    )

    g1 = identity.get("status") == "PASS" and registry.get("selected_strength") == "PROFILE-S1"
    g2 = cross.get("status") == "PASS" and int(cross.get("eventtrace_count", 0)) == 6
    g3 = all(
        int(j(f"outputs/e2_traffic_real_runner_canary/runs/{sid}/{method}/config_snapshot.json")["local_steps"]) == 2
        and float(j(f"outputs/e2_traffic_real_runner_canary/runs/{sid}/{method}/config_snapshot.json")["a_max"]) == 40.0
        and float(j(f"outputs/e2_traffic_real_runner_canary/runs/{sid}/{method}/config_snapshot.json")["learning_rate"]) == 0.01
        and j(f"outputs/e2_traffic_real_runner_canary/runs/{sid}/{method}/config_snapshot.json").get("standardization") == "train_split_zscore"
        for sid in SCENARIOS for method in METHODS
    )
    g4 = (
        int(summary.get("completed_runs", 0)) == 30
        and int(summary.get("completed_windows_min", 0)) == 100
        and int(summary.get("completed_windows_max", 0)) == 100
        and int(summary.get("retry_count", 1)) == 0
        and int(summary.get("seed_replacement_count", 1)) == 0
        and stop.get("reaudit_only") is False
        and stop.get("fresh_rerun") is True
    )
    g5 = num.get("status") == "PASS"
    g6 = raven.get("status") == "PASS" and base.get("status") == "PASS"
    g7 = metric.get("status") == "PASS" and int(metric.get("result_rows", 0)) == 30
    g8 = artifacts_ok and result_files and int(summary.get("checkpoint_count", 0)) == 30

    g9_diag = evaluate_g9(
        root=ROOT,
        ledger_path=LEDGER,
        canary_out=CANARY,
        noninsp=noninsp,
        require_junit=True,
    )
    g9 = bool(g9_diag.get("pass"))

    g10 = (
        noninsp.get("status") == "PASS"
        and int(noninsp.get("validation_seed_reads", 1)) == 0
        and int(noninsp.get("formal_seed_reads", 1)) == 0
        and int(noninsp.get("formal_run_count", 1)) == 0
        and int(noninsp.get("formal_figures_count", 1)) == 0
        and registry.get("selected_strength") == "PROFILE-S1"
        and stop.get("e3_e9_status") == "NOT_STARTED"
    )

    gates = {
        "E2RR-G1": bool(g1),
        "E2RR-G2": bool(g2),
        "E2RR-G3": bool(g3),
        "E2RR-G4": bool(g4),
        "E2RR-G5": bool(g5),
        "E2RR-G6": bool(g6),
        "E2RR-G7": bool(g7),
        "E2RR-G8": bool(g8),
        "E2RR-G9": bool(g9),
        "E2RR-G10": bool(g10),
    }
    all_pass = all(gates.values())
    core = all(gates[k] for k in (
        "E2RR-G1", "E2RR-G2", "E2RR-G3", "E2RR-G4",
        "E2RR-G5", "E2RR-G6", "E2RR-G7", "E2RR-G8",
    ))

    # Stop status must reflect full G1–G10, never READY when G9 fails.
    if all_pass:
        final_status = "READY_FOR_TRAFFIC_E2_FORMAL_RUNS"
        next_round = "E2-TRAFFIC-FORMAL-RUNS-R1"
    elif not g9:
        final_status = "BLOCKED_TRAFFIC_REAL_RUNNER_LEDGER_NOT_CLOSED"
        next_round = None
    else:
        final_status = "BLOCKED_TRAFFIC_REAL_RUNNER_CANARY_FAILED"
        next_round = None
    stop["status"] = final_status
    stop["next_authorized_round"] = next_round
    stop["gates_all_pass"] = all_pass
    stop["g9_status"] = g9_diag.get("status")
    stop["reaudit_only"] = False
    dump_json(stop, STOP)

    payload = {
        "protocol": PACKAGE,
        "ledger_closure_round": "E2-TRAFFIC-REAL-RUNNER-LEDGER-CLOSURE-R1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "gates": gates,
        "core_pass": core,
        "all_pass": all_pass,
        "stop_status": final_status,
        "next_authorized_round": next_round,
        "g9_diagnostics": g9_diag,
    }
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2, default=str))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
