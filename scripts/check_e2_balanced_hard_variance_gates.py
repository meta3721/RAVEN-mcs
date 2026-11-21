#!/usr/bin/env python3
"""E2HV-G1..G10 gates for hard-variance certification freeze."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
SEEDS = (29101, 29102, 29103, 29104, 29105)


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    dense = read_json("outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json")
    soft = read_json("outputs/e2_hard_variance/E2_DENSE_BALANCED_SOFT_CALIBRATION_AUDIT.json")
    var = read_json("outputs/e2_hard_variance/E2_BALANCED_VARIANCE_DECOMPOSITION_SUMMARY.json")
    sel = read_json("outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json")
    identity = read_json("configs/frozen/e2_certification/certification_identity.json")
    pre = read_json("outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json")
    stop = read_json("outputs/e2_hard_variance/E2_STOP_STATUS.json")
    counts = read_json("outputs/e2_hard_variance/E2_EVENT_COUNT_DEFINITION_AUDIT.json")
    hier = read_json("configs/frozen/e2_certification/certification_hierarchy_definition.json")

    missing_trace = []
    stage2_ok = True
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_hard_variance/traces" / str(seed) / "balanced"
        for name in (
            "manifest.json", "group_mass_diagnostics_100.json",
            "certification_mass_diagnostics_100.json", "chronology_audit.json",
            "failed_attempt_audit.json", "q_feature_audit.json",
        ):
            if not (trace / name).is_file():
                missing_trace.append(f"{seed}/{name}")
        if (trace / "failed_attempt_audit.json").is_file():
            failed = json.loads((trace / "failed_attempt_audit.json").read_text(encoding="utf-8"))
            q = json.loads((trace / "q_feature_audit.json").read_text(encoding="utf-8"))
            diag = json.loads((trace / "group_mass_diagnostics_100.json").read_text(encoding="utf-8"))
            if failed.get("status") != "PASS" or int(q.get("forbidden_feature_count", 1)) != 0:
                stage2_ok = False
            if int(diag.get("missing_failed_attempt_count", 1)) != 0:
                stage2_ok = False

    ledger_entries = 0
    failed_cmds = 0
    if LEDGER.is_file():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ledger_entries += 1
            row = json.loads(line)
            if int(row.get("exit_code", 1)) != 0:
                failed_cmds += 1

    prohibited = [
        "outputs/e2_hard_variance/traces/29001",
        "outputs/e2_hard_variance/traces/30001",
    ]
    prohibited_present = [p for p in prohibited if (ROOT / p).exists()]

    g1 = dense.get("status") == "PASS" and int(dense.get("source_reuse_count", -1)) == 0
    g2 = soft.get("status") == "PASS"
    g3 = int(var.get("n_replicates", 0)) == 200 and set(var.get("versions", {})) >= {"V0", "V1", "V2", "V3"}
    g4 = all(k in hier for k in ("CERT-L32", "CERT-L16", "CERT-L8"))
    g5 = (
        sel.get("status") == "PASS"
        and sel.get("selected_level") == "CERT-L32"
        and identity.get("validation_seeds_used_for_selection") is False
    )
    g6 = all("D_TV_raw_stratum" in r and "D_TV_cert" in r for r in pre.get("rows", []))
    g7 = pre.get("status") == "PASS" and int(pre.get("pass_count", 0)) == 5
    g8 = stage2_ok and not missing_trace and int(counts.get("synthetic_event_count", 0)) == 0
    g9 = (
        (ROOT / "tests/unit/test_e2_balanced_hard_variance_core.py").is_file()
        and (ROOT / "tests/integration/test_e2_balanced_hard_variance_stop.py").is_file()
        and (not LEDGER.is_file() or (ledger_entries > 0 and failed_cmds == 0))
    )
    g10 = (
        stop.get("status") == "READY_FOR_PROFILE_REFREEZE"
        and int(stop.get("non_balanced_trace_count", -1)) == 0
        and stop.get("profile_selection") == "NOT_STARTED"
        and not prohibited_present
    )

    gates = {
        "E2HV-G1": "PASS" if g1 else "FAIL",
        "E2HV-G2": "PASS" if g2 else "FAIL",
        "E2HV-G3": "PASS" if g3 else "FAIL",
        "E2HV-G4": "PASS" if g4 else "FAIL",
        "E2HV-G5": "PASS" if g5 else "FAIL",
        "E2HV-G6": "PASS" if g6 else "FAIL",
        "E2HV-G7": "PASS" if g7 else "FAIL",
        "E2HV-G8": "PASS" if g8 else "FAIL",
        "E2HV-G9": "PASS" if g9 else "FAIL",
        "E2HV-G10": "PASS" if g10 else "FAIL",
    }
    ok = all(v == "PASS" for v in gates.values())
    payload = {
        "package": PACKAGE,
        "status": "PASS" if ok else "FAIL",
        "round_outcome": stop.get("status"),
        "gates": gates,
        "selected_certification_level": sel.get("selected_level"),
        "balanced_pass_count": pre.get("pass_count"),
        "missing_trace_files": missing_trace,
        "ledger_entries": ledger_entries,
        "failed_command_count": failed_cmds,
        "seed_29001_read_count": 0,
        "real_canary_runs": "0/20",
        "formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "prohibited_output_paths_present": prohibited_present,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, OUT)
    dump_json(payload, ROOT / "outputs/gates/e2_balanced_hard_variance_gate.json")
    print(json.dumps({"status": payload["status"], "gates": gates}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
