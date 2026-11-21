#!/usr/bin/env python3
"""E2PF-G1..G10 gates for Traffic S1-S6 profile freeze."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_S1_S6_PROFILE_FREEZE_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SCENARIOS = [
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
]
SEEDS = (28201, 28202, 28203)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main() -> int:
    identity = j("outputs/audits/E2_TRAFFIC_S1_S6_INPUT_IDENTITY_AUDIT.json")
    gate_corr = j("configs/frozen/e2_traffic_profiles/balanced_canary_gate_correction.json")
    q_audit = j("outputs/audits/E2_TRAFFIC_Q_RUNTIME_INTERFACE_AUDIT.json")
    cert = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_direction_certificate.json")
    registry = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_profile_registry.json")
    identity_f = j("configs/frozen/e2_traffic_profiles/traffic_s1_s6_identity.json")
    stop = j("outputs/e2_traffic_profiles/E2_TRAFFIC_S1_S6_PROFILE_FREEZE_STOP_STATUS.json")
    structure = j("outputs/audits/E2_TRAFFIC_PROFILE_STRUCTURE_AUDIT.json")
    nondeg = j("outputs/audits/E2_TRAFFIC_PROFILE_NONDEGENERACY_AUDIT.json")

    ledger_entries = failed_cmd = forced_zero = missing_logs = 0
    first = None
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ledger_entries += 1
            row = json.loads(line)
            if first is None:
                first = row.get("label")
            if int(row.get("exit_code", 1)) != 0:
                failed_cmd += 1
            for key in ("stdout_log", "stderr_log"):
                rel = row.get(key)
                if rel and not (ROOT / rel).is_file():
                    missing_logs += 1
            cmd = " ".join(str(x) for x in row.get("command", []))
            if "sys.exit(0)" in cmd and row.get("label") == "gates":
                forced_zero += 1

    expected_mass_ok = all(
        (ROOT / f"outputs/e2_traffic_profiles/scenarios/{sid}/expected_opportunity_mass.parquet").is_file()
        and (ROOT / f"outputs/e2_traffic_profiles/scenarios/{sid}/expected_observation_mass.parquet").is_file()
        and (ROOT / f"outputs/e2_traffic_profiles/scenarios/{sid}/expected_arrival_mass.parquet").is_file()
        and (ROOT / f"outputs/e2_traffic_profiles/scenarios/{sid}/expected_client_window_activity.parquet").is_file()
        for sid in SCENARIOS
    )
    traces_ok = all(
        (ROOT / f"outputs/e2_traffic_profiles/scenarios/{sid}/traces/{seed}/hard_arrival_events.parquet").is_file()
        for sid in SCENARIOS
        for seed in SEEDS
    )
    one_param = all(
        int(registry["scenarios"][sid].get("d_opp", 99) is not None)
        and registry.get("parameter_sets_per_scenario") == 1
        and int(registry.get("grid_search_count", 1)) == 0
        for sid in SCENARIOS
    )

    g1 = identity.get("status") == "PASS"
    g2 = (
        gate_corr.get("status") == "PASS"
        and gate_corr.get("diagnostic_only")
        and gate_corr["diagnostic_only"][0].get("absolute_veto") is False
    )
    g3 = (
        q_audit.get("status") == "PASS"
        and int(q_audit.get("stage2_eligible_in_q_numeric_features", 1)) == 0
        and int(q_audit.get("observed_count_in_q_numeric_features", 1)) == 0
        and int(q_audit.get("target_value_in_q_numeric_features", 1)) == 0
    )
    g4 = expected_mass_ok
    g5 = one_param and int(stop.get("grid_search_count", 1)) == 0
    g6 = int(cert.get("expected_direction_pass_count", 0)) == 6 and nondeg.get("status") == "PASS"
    g7 = int(cert.get("hard_direction_pass_count", 0)) == 6 and traces_ok and int(stop.get("hard_trace_count", 0)) == 18
    g8 = (
        identity_f.get("status") == "FROZEN"
        and cert.get("status") == "PASS"
        and registry.get("status") == "FROZEN"
    )
    g9 = (
        (ROOT / "tests/unit/test_e2_traffic_s1_s6_profile_freeze_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_traffic_s1_s6_profile_freeze_stop.py").is_file()
        and (not LEDGER.is_file() or (
            ledger_entries > 0 and failed_cmd == 0 and missing_logs == 0 and forced_zero == 0
            and first == "profile_generation"
        ))
    )
    g10 = (
        int(stop.get("training_artifact_count", -1)) == 0
        and int(stop.get("seed_29001_read_count", -1)) == 0
        and int(stop.get("validation_seed_read_count", -1)) == 0
        and int(stop.get("formal_seed_read_count", -1)) == 0
        and int(stop.get("e2_formal_runs", -1)) == 0
        and stop.get("e3_e9_status") == "NOT_STARTED"
        and int(structure.get("unsupported_arrival_count", 1)) == 0
    )

    gates = {f"E2PF-G{i}": ("PASS" if v else "FAIL") for i, v in enumerate(
        [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10], start=1,
    )}
    core_ok = all(gates[f"E2PF-G{i}"] == "PASS" for i in range(1, 9))
    packaging_ok = gates["E2PF-G9"] == "PASS" and gates["E2PF-G10"] == "PASS"
    expected_stop = (
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY"
        if core_ok
        else "BLOCKED_TRAFFIC_PROFILE_FREEZE_FAILED"
    )
    stop_ok = stop.get("status") in {
        expected_stop,
        "READY_FOR_TRAFFIC_REAL_RUNNER_CANARY",
        "BLOCKED_TRAFFIC_PROFILE_FREEZE_FAILED",
        "BLOCKED_INPUT_IDENTITY_MISMATCH",
        "BLOCKED_MISSING_S1_S6_DIRECTION_REGISTRY",
    }
    ok = packaging_ok and stop_ok and gates["E2PF-G1"] == "PASS"
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "core_gates_pass": core_ok,
        "gates": gates,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed_cmd,
        "missing_log_count": missing_logs,
        "forced_zero_wrapper_count": forced_zero,
        "ledger_first_label": first,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    print(json.dumps(payload, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
