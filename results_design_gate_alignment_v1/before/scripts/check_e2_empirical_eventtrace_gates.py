#!/usr/bin/env python3
"""Evaluate E2EE-G1..G10 for empirical EventTrace and profile refreeze round."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from raven_mcs.e2.empirical.gates import PROFILES, SCENARIOS, VALIDATION_SEEDS
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
GATES_OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"

REQUIRED_TRACE_FILES = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
    "hard_arrival_events.parquet",
    "empirical_atomic_mass_100.parquet",
    "empirical_atomic_mass_200.parquet",
    "empirical_atomic_mass_300.parquet",
    "expected_atomic_mass_100.parquet",
    "expected_atomic_mass_200.parquet",
    "expected_atomic_mass_300.parquet",
    "group_mass_diagnostics_100.json",
    "group_mass_diagnostics_200.json",
    "group_mass_diagnostics_300.json",
    "stratum_mass_diagnostics_100.json",
    "stratum_mass_diagnostics_200.json",
    "stratum_mass_diagnostics_300.json",
    "stdout.log",
    "stderr.log",
)


def _pass(cond: bool) -> str:
    return "PASS" if cond else "FAIL"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _junit_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return 'failures="0"' in text and 'errors="0"' in text


def _audit_ledger(root: Path) -> dict:
    rows: list[dict] = []
    if LEDGER.is_file():
        rows = [
            json.loads(line)
            for line in LEDGER.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    failed_exit = sum(1 for row in rows if int(row.get("exit_code", 1)) != 0)
    placeholders = sum(1 for row in rows if row.get("placeholder"))
    missing_logs = 0
    for row in rows:
        for key in ("stdout_log", "stderr_log"):
            rel = row.get(key)
            if not rel or not (root / rel).is_file():
                missing_logs += 1
    zero_duration = sum(1 for row in rows if float(row.get("duration_sec") or 0) <= 0)
    return {
        "ledger_entries": len(rows),
        "failed_exit_code_count": failed_exit,
        "placeholder_command_count": placeholders,
        "missing_stdout_stderr_count": missing_logs,
        "zero_duration_command_count": zero_duration,
        "ledger_strict_pass": (
            bool(rows)
            and failed_exit == 0
            and placeholders == 0
            and missing_logs == 0
            and zero_duration == 0
        ),
    }


def _trace_dirs(root: Path) -> list[Path]:
    base = root / "outputs/e2_empirical/traces"
    if not base.is_dir():
        return []
    return sorted(
        p for p in base.glob("*/*/*")
        if p.is_dir() and p.parent.parent.parent == base
    )


def _check_trace_files(root: Path) -> tuple[int, int, int]:
    """Return (expected_count, complete_count, missing_file_count)."""
    dirs = _trace_dirs(root)
    expected = len(VALIDATION_SEEDS) * len(PROFILES) * len(SCENARIOS)
    complete = 0
    missing_total = 0
    for trace_dir in dirs:
        missing = [f for f in REQUIRED_TRACE_FILES if not (trace_dir / f).is_file()]
        if not missing:
            complete += 1
        missing_total += len(missing)
    return expected, complete, missing_total


def _manifest_checks(root: Path) -> dict[str, bool]:
    """Pipeline semantic checks across all generated manifests."""
    expected = len(VALIDATION_SEEDS) * len(PROFILES) * len(SCENARIOS)
    ok_g3 = True
    ok_g4 = True
    ok_g5 = True
    manifests_found = 0
    for trace_dir in _trace_dirs(root):
        manifest_path = trace_dir / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifests_found += 1
        manifest = _load_json(manifest_path)
        obs = manifest.get("obs_audit") or {}
        use = manifest.get("use_audit") or {}
        arr = manifest.get("arr_audit") or {}
        if int(obs.get("exposure_event_count") or 0) <= 0:
            ok_g3 = False
        if int(obs.get("actual_O_events_saved") or 0) <= 0:
            ok_g3 = False
        if int(use.get("failed_attempt_omission_count", 1)) != 0:
            ok_g4 = False
        if int(use.get("actual_U_events_saved", 0)) <= 0:
            ok_g4 = False
        if not bool(arr.get("empirical_from_A_O_U")):
            ok_g5 = False
        if bool(arr.get("expected_alias_used")):
            ok_g5 = False
        if float(arr.get("total_hard_arrival_mass") or 0) <= 0:
            ok_g5 = False
        for length in (100, 200, 300):
            diag_path = trace_dir / f"group_mass_diagnostics_{length}.json"
            if diag_path.is_file():
                diag = _load_json(diag_path)
                if diag.get("hashes_equal_warning"):
                    ok_g5 = False
    if manifests_found != expected:
        return {
            "g3": False,
            "g4": False,
            "g5": False,
            "manifest_count": manifests_found,
            "expected_manifest_count": expected,
        }
    return {
        "g3": ok_g3,
        "g4": ok_g4,
        "g5": ok_g5,
        "manifest_count": manifests_found,
        "expected_manifest_count": expected,
    }


def evaluate(
    root: Path,
    *,
    unit_ok: bool,
    integ_ok: bool,
    full_ok: bool,
    unpacked_ok: bool,
) -> dict:
    schedule_audit = _load_json(
        root / "outputs/audits/E2_300_WINDOW_SCHEDULE_NONREPETITION_AUDIT.json"
    )
    opp_riskset = _load_json(
        root / "outputs/audits/E2_OPPORTUNITY_RISKSET_DIFFERENCE_AUDIT.json"
    )
    matrix = _load_json(
        root / "outputs/e2_empirical/E2_EMPIRICAL_TRACE_MATRIX_SUMMARY.json"
    )
    selection = _load_json(
        root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
    )
    window = _load_json(
        root / "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_LENGTH_SELECTION.json"
    )
    tombstone = _load_json(
        root / "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json"
    )
    selected = selection.get("selected_profile_id")
    ledger = _audit_ledger(root)
    manifest_checks = _manifest_checks(root)
    expected_traces, complete_traces, missing_files = _check_trace_files(root)

    g1 = (
        schedule_audit.get("status") == "PASS"
        and schedule_audit.get("chronological_order_status") == "PASS"
        and bool(schedule_audit.get("schedule_uniforms_used_all"))
        and not bool(schedule_audit.get("block_hashes_all_equal_any"))
        and float(schedule_audit.get("min_unique_window_payload_ratio") or 0) >= 0.80
    )

    g2 = False
    if selected and opp_riskset:
        # Keys are "{seed}/{profile_id}".
        diffs = [
            opp_riskset[k]
            for k in opp_riskset
            if k.split("/")[-1] == selected
        ]
        g2 = (
            len(diffs) == len(VALIDATION_SEEDS)
            and all(
                int(d.get("balanced_vs_opportunity_event_difference_count") or 0) > 0
                for d in diffs
            )
            and all(d.get("status") == "PASS" for d in diffs)
        )
        if matrix.get("manifests"):
            opp_uniform_ok = all(
                int(m.get("opportunity_uniforms_used_count") or 0) > 0
                for m in matrix["manifests"].values()
            )
            g2 = g2 and opp_uniform_ok

    g3 = manifest_checks["g3"]
    g4 = manifest_checks["g4"]
    g5 = manifest_checks["g5"]

    g6 = (
        int(matrix.get("trace_count") or 0) == 180
        and int(matrix.get("trace_failure_count") or 0) == 0
        and int(matrix.get("missing_required_file_count") or 0) == 0
        and complete_traces == expected_traces == 180
        and missing_files == 0
    )

    g7 = False
    if selection.get("status") == "SELECTED" and selected:
        gate_csv = root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_GATE_SUMMARY.csv"
        if gate_csv.is_file():
            gate_df = pd.read_csv(gate_csv)
            row = gate_df.loc[gate_df["profile_id"] == selected]
            g7 = not row.empty and bool(row.iloc[0]["profile_valid"])
        gate_by_seed = root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_GATE_BY_SEED.csv"
        if gate_by_seed.is_file():
            gdf = pd.read_csv(gate_by_seed)
            sel = gdf[gdf["profile_id"] == selected]
            g7 = g7 and bool((sel.groupby("seed")["profile_valid_seed"].all()).all())

    frozen_prof = root / "configs/frozen/e2_empirical/selected_strength_profile.yaml"
    frozen_prof_id = root / "configs/frozen/e2_empirical/selected_strength_profile_identity.json"
    frozen_win = root / "configs/frozen/e2_empirical/selected_window_length.yaml"
    frozen_win_id = root / "configs/frozen/e2_empirical/selected_window_length_identity.json"
    g8 = (
        selection.get("status") == "SELECTED"
        and selected is not None
        and frozen_prof.is_file()
        and frozen_prof_id.is_file()
        and frozen_win.is_file()
        and frozen_win_id.is_file()
        and window.get("selected_windows") in (100, 200, 300)
        and yaml.safe_load(frozen_prof.read_text(encoding="utf-8")).get("selected_profile_id") == selected
        and int(yaml.safe_load(frozen_win.read_text(encoding="utf-8")).get("selected_windows")) == int(
            window.get("selected_windows")
        )
    )

    tests_ok = bool(unit_ok and integ_ok and full_ok and unpacked_ok)
    g9 = tests_ok and ledger["ledger_strict_pass"]
    # Strict: never upgrade G9 from junit when ledger or tests fail.

    seed_blob = ""
    for path in [
        root / "outputs/e2_empirical/E2_EMPIRICAL_CONTEXT.json",
        root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json",
        root / "configs/frozen/e2_empirical/selected_strength_profile_identity.json",
    ]:
        if path.is_file():
            seed_blob += path.read_text(encoding="utf-8")
    seed_29001_reads = seed_blob.count("29001")
    formal_reads = sum(seed_blob.count(str(s)) for s in range(30001, 30021))
    g10 = (
        seed_29001_reads == 0
        and formal_reads == 0
        and tombstone.get("not_reused_without_revalidation") is True
        and tombstone.get("prior_profile_id") == "PROFILE-S2"
    )

    gates = {
        "E2EE-G1": _pass(g1),
        "E2EE-G2": _pass(g2),
        "E2EE-G3": _pass(g3),
        "E2EE-G4": _pass(g4),
        "E2EE-G5": _pass(g5),
        "E2EE-G6": _pass(g6),
        "E2EE-G7": _pass(g7),
        "E2EE-G8": _pass(g8),
        "E2EE-G9": _pass(g9),
        "E2EE-G10": _pass(g10),
    }
    all_pass = all(v == "PASS" for v in gates.values())
    return {
        "status": "PASS" if all_pass else "FAIL",
        "all_pass": all_pass,
        "gates": gates,
        "selected_profile_id": selected,
        "selected_windows": window.get("selected_windows"),
        "trace_count": matrix.get("trace_count"),
        "trace_failure_count": matrix.get("trace_failure_count"),
        "complete_trace_dirs": complete_traces,
        "expected_trace_dirs": expected_traces,
        "missing_required_file_count": missing_files,
        "manifest_count": manifest_checks["manifest_count"],
        "schedule_audit_status": schedule_audit.get("status"),
        "ledger_entries": ledger["ledger_entries"],
        "failed_command_count": ledger["failed_exit_code_count"],
        "missing_log_count": ledger["missing_stdout_stderr_count"],
        "placeholder_command_count": ledger["placeholder_command_count"],
        "zero_duration_command_count": ledger["zero_duration_command_count"],
        "unit_tests_pass": unit_ok,
        "integration_tests_pass": integ_ok,
        "full_repository_tests_pass": full_ok,
        "unpacked_specialized_tests_pass": unpacked_ok,
        "real_canary_runs": "0/20",
        "seed_29001_read_count": seed_29001_reads,
        "formal_seed_read_count": formal_reads,
        "e2_formal_runs": 0,
        "e3_e9_status": "NOT_STARTED",
        "e2_status": "READY_FOR_REAL_RUNNER_CANARY" if all_pass else "NOT_READY",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "prior_tombstone_hash": sha256_file(
            root / "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json"
        ) if (root / "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json").is_file() else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-ok", action="store_true")
    parser.add_argument("--integration-ok", action="store_true")
    parser.add_argument("--full-ok", action="store_true")
    parser.add_argument("--unpacked-ok", action="store_true")
    args = parser.parse_args()

    unit_ok = args.unit_ok or _junit_ok(ROOT / "logs/e2_empirical_eventtrace_unit.xml")
    integ_ok = args.integration_ok or _junit_ok(
        ROOT / "logs/e2_empirical_eventtrace_integration.xml"
    )
    full_ok = args.full_ok or _junit_ok(
        ROOT / "logs/e2_empirical_eventtrace_full_repository.xml"
    )
    unpacked_ok = args.unpacked_ok or _junit_ok(
        ROOT / "logs/e2_empirical_eventtrace_unpacked_specialized.xml"
    )

    result = evaluate(
        ROOT,
        unit_ok=unit_ok,
        integ_ok=integ_ok,
        full_ok=full_ok,
        unpacked_ok=unpacked_ok,
    )
    GATES_OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_json(result, GATES_OUT)
    print(json.dumps(result, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
