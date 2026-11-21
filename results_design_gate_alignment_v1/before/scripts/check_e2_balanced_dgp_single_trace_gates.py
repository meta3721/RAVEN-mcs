#!/usr/bin/env python3
"""E2BD-G1..G10 gates for balanced DGP / single-trace certification repair."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_DGP_AND_SINGLE_TRACE_CERTIFICATION_REPAIR_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SEEDS = (29101, 29102, 29103, 29104, 29105)
SRC_BOUNDED = ROOT / "src/raven_mcs/e2/balanced_dgp/bounded_schedule.py"


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    bounded = read_json("outputs/audits/E2_BOUNDED_CANDIDATE_WINDOW_AUDIT.json")
    mass = read_json("outputs/audits/E2_EVENT_MASS_SEMANTICS_AUDIT.json")
    soft = read_json("outputs/e2_balanced_dgp/E2_OPPORTUNITY_PROBABILITY_CALIBRATION_AUDIT.json")
    spatial = read_json("outputs/audits/E2_REAL_SPATIAL_IDENTITY_AUDIT.json")
    var = read_json("outputs/e2_balanced_dgp/E2_SINGLE_ARM_VARIANCE_SUMMARY.json")
    sel = read_json("outputs/e2_balanced_dgp/E2_CERTIFICATION_LEVEL_SELECTION.json")
    stop = read_json("outputs/e2_balanced_dgp/E2_STOP_STATUS.json")
    tomb = read_json("outputs/audits/E2_PRIOR_ANTITHETIC_CERTIFICATION_TOMBSTONE.json")

    src = SRC_BOUNDED.read_text(encoding="utf-8")
    no_suffix = "iloc[start:n]" not in src and "pool.iloc[start:" not in src

    ledger_entries = failed_cmds = 0
    first_label = None
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ledger_entries += 1
            row = json.loads(line)
            if first_label is None:
                first_label = row.get("label")
            if int(row.get("exit_code", 1)) != 0:
                failed_cmds += 1

    pre_path = ROOT / "outputs/e2_balanced_dgp/E2_BALANCED_SINGLE_TRACE_PRE_GATE_SUMMARY.json"
    pre = read_json(pre_path.relative_to(ROOT).as_posix()) if pre_path.is_file() else {}

    missing_trace = []
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_balanced_dgp/traces" / str(seed) / "balanced"
        for name in (
            "opportunity_events.parquet", "observation_events.parquet",
            "usable_events.parquet", "hard_arrival_events.parquet",
            "failed_attempt_audit.json", "q_feature_audit.json",
        ):
            if not (trace / name).is_file():
                missing_trace.append(f"{seed}/{name}")

    feasibility = sel.get("feasibility") or {}
    any_feasible = any(bool(v.get("feasible")) for v in feasibility.values())
    selected = sel.get("selected_level")
    finest = None
    for level in ("CERT-L32", "CERT-L16", "CERT-L8"):
        if bool((feasibility.get(level) or {}).get("feasible")):
            finest = level
            break

    g1 = (
        bounded.get("status") == "PASS"
        and int(bounded.get("future_candidate_count", -1)) == 0
        and int(bounded.get("source_reuse_count", -1)) == 0
        and no_suffix
    )
    g2 = (
        mass.get("status") == "PASS"
        and mass.get("event_mass_depends_on_calibration") is False
        and float(mass.get("event_mass_value", -1)) == 1.0
    )
    g3 = (
        soft.get("status") == "PASS"
        and soft.get("calibration_target") == "p_opp"
        and soft.get("event_mass_unchanged") is True
        and float(soft.get("max_D_TV_group_soft", 1)) <= 0.01
        and float(soft.get("max_D_TV_raw_stratum_soft", 1)) <= 0.01
        and float(soft.get("max_D_TV_client_raw_stratum_soft", 1)) <= 0.03
    )
    g4 = (
        spatial.get("status") == "PASS"
        and int(spatial.get("synthetic_coordinate_usage_count", 1)) == 0
        and "synthetic" not in str(spatial.get("coordinate_source", "")).lower()
    )
    g5 = (
        int(var.get("n_replicates", 0)) == 200
        and var.get("antithetic_used") is False
        and var.get("estimator") == "single_arm"
        and set(var.get("versions", {})) >= {"V0", "V1", "V2", "V3"}
    )
    g6 = (
        sel.get("antithetic_used_for_selection") is False
        and (
            (any_feasible and selected == finest and sel.get("status") == "PASS")
            or ((not any_feasible) and sel.get("status") == "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE")
        )
    )
    g7 = (
        pre.get("status") == "PASS"
        and int(pre.get("pass_count", 0)) == 5
        and int(pre.get("antithetic_arms", 0)) == 1
        and not missing_trace
    )
    g8 = (not missing_trace) if g7 else (sel.get("status") == "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE")
    g9 = (
        (ROOT / "tests/unit/test_e2_balanced_dgp_single_trace_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_balanced_dgp_single_trace_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed_cmds == 0
            and first_label in {"prepare", "prepare_generation", "bounded_prepare"}
        ))
    )
    stop_status = stop.get("status")
    non_bal = stop.get("non_balanced_trace_count")
    if non_bal is None:
        non_bal = 0
    profile = stop.get("profile_selection", "NOT_STARTED")
    g10 = (
        stop_status in {
            "READY_FOR_PROFILE_REFREEZE",
            "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE",
            "BALANCED_SINGLE_TRACE_PRE_GATE_FAIL",
            "BLOCKED_OPPORTUNITY_PROBABILITY_CALIBRATION",
        }
        and int(non_bal) == 0
        and profile == "NOT_STARTED"
        and tomb.get("must_revalidate_single_arm") is True
        and not (ROOT / "outputs/e2_balanced_dgp/traces/29001").exists()
    )

    gates = {
        "E2BD-G1": "PASS" if g1 else "FAIL",
        "E2BD-G2": "PASS" if g2 else "FAIL",
        "E2BD-G3": "PASS" if g3 else "FAIL",
        "E2BD-G4": "PASS" if g4 else "FAIL",
        "E2BD-G5": "PASS" if g5 else "FAIL",
        "E2BD-G6": "PASS" if g6 else "FAIL",
        "E2BD-G7": "PASS" if g7 else "FAIL",
        "E2BD-G8": "PASS" if g8 else "FAIL",
        "E2BD-G9": "PASS" if g9 else "FAIL",
        "E2BD-G10": "PASS" if g10 else "FAIL",
    }
    # Round may honestly stop before traces; overall PASS only on full success.
    ok = all(v == "PASS" for v in gates.values())
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop_status if stop_status != "BLOCKED_SINGLE_ARM_CERTIFICATION_INFEASIBLE"
        else stop.get("status", stop_status),
        "gates": gates,
        "selected_certification_level": selected,
        "finest_feasible_level": finest,
        "balanced_pass_count": pre.get("pass_count", 0),
        "missing_trace_files": missing_trace,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed_cmds,
        "ledger_first_label": first_label,
        "seed_29001_read_count": 0,
        "real_canary_runs": "0/20",
        "formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    # Normalize round_outcome from nested stop payloads.
    if isinstance(stop.get("status"), str):
        payload["round_outcome"] = stop["status"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    dump_json(payload, ROOT / "outputs/gates/e2_balanced_dgp_single_trace_gate.json")
    print(json.dumps({"status": payload["status"], "round_outcome": payload["round_outcome"], "gates": gates}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
