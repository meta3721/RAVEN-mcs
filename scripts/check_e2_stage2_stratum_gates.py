#!/usr/bin/env python3
"""Evaluate E2SR-G1..G10 for Stage-2 eligibility and true-stratum refreeze round."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from raven_mcs.e2.stage2.gates import PROFILES, SCENARIOS, VALIDATION_SEEDS
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1"
LEDGER = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
GATES_OUT = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"

REQUIRED_TRACE_FILES = (
    "manifest.json",
    "resolved_config.yaml",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
    "observation_events.parquet",
    "usable_events.parquet",
    "server_window_activity.parquet",
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
    "failed_attempt_audit.json",
    "q_feature_audit.json",
    "stdout.log",
    "stderr.log",
)
FORBIDDEN_STRATA = {"head", "neutral", "tail"}


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
    base = root / "outputs/e2_stage2_stratum/traces"
    if not base.is_dir():
        return []
    return sorted(
        p for p in base.glob("*/*/*")
        if p.is_dir() and p.parent.parent.parent == base
    )


def _check_trace_files(root: Path) -> tuple[int, int, int]:
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


def _manifest_semantics(root: Path) -> dict[str, bool | int]:
    expected = len(VALIDATION_SEEDS) * len(PROFILES) * len(SCENARIOS)
    ok_g1 = True
    ok_g2 = True
    ok_g3 = True
    manifests_found = 0
    for trace_dir in _trace_dirs(root):
        manifest_path = trace_dir / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifests_found += 1
        manifest = _load_json(manifest_path)
        use = manifest.get("use_audit") or {}
        activity = manifest.get("activity_audit") or {}

        if manifest.get("stage2_eligibility_rule") != "observed_count > 0":
            ok_g1 = False
        if use.get("eligibility_rule") != "observed_count > 0":
            ok_g1 = False
        if int(use.get("not_eligible_count", 0)) < 0:
            ok_g1 = False

        fail_path = trace_dir / "failed_attempt_audit.json"
        if fail_path.is_file():
            fa = _load_json(fail_path)
            if int(fa.get("missing_failed_attempt_count", 1)) != 0:
                ok_g2 = False
            if int(fa.get("extra_failed_attempt_count", 1)) != 0:
                ok_g2 = False
            if fa.get("failed_attempt_payload_hash_match") is not True:
                ok_g2 = False
        else:
            ok_g2 = False

        if activity.get("active_window_equals_usable_rate_identically") is not False:
            ok_g3 = False
        if activity.get("definition_alias_forbidden") is not True:
            ok_g3 = False

    if manifests_found != expected:
        return {
            "g1": False,
            "g2": False,
            "g3": False,
            "manifest_count": manifests_found,
            "expected_manifest_count": expected,
        }
    return {
        "g1": ok_g1,
        "g2": ok_g2,
        "g3": ok_g3,
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
    failed_attempt = _load_json(root / "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json")
    chrono = _load_json(root / "outputs/audits/E2_CHRONOLOGICAL_ORDER_AUDIT.json")
    stratum_status = _load_json(root / "outputs/audits/E2_TRUE_STRATUM_STATUS.json")
    stratum_identity = _load_json(
        root / "configs/frozen/e2_stratum/opportunity_stratum_identity.json"
    )
    matrix = _load_json(root / "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json")
    selection = _load_json(root / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json")
    window = _load_json(root / "outputs/e2_stage2_stratum/E2_WINDOW_SELECTION.json")
    tombstone = _load_json(
        root / "outputs/audits/E2_PRIOR_EMPIRICAL_SELECTION_TOMBSTONE.json"
    )
    q_manifest = _load_json(root / "configs/frozen/e2_stage2/q_feature_manifest.json")

    selected = selection.get("selected_profile_id")
    ledger = _audit_ledger(root)
    manifest_checks = _manifest_semantics(root)
    expected_traces, complete_traces, missing_files = _check_trace_files(root)

    g1 = manifest_checks.get("g1", False) and bool(
        stratum_status.get("role_substitution") is False or stratum_status.get("status") == "PASS"
    )

    g2 = (
        failed_attempt.get("status") == "PASS"
        and int(failed_attempt.get("missing_failed_attempt_count", 1)) == 0
        and int(failed_attempt.get("extra_failed_attempt_count", 1)) == 0
        and failed_attempt.get("failed_attempt_payload_hash_match") is True
        and manifest_checks.get("g2", False)
    )

    g3 = manifest_checks.get("g3", False)
    if matrix.get("manifests"):
        for key, manifest in matrix["manifests"].items():
            act = (manifest.get("activity_audit") or {})
            if act.get("active_window_equals_usable_rate_identically") is not False:
                g3 = False

    strata_ids = list(stratum_identity.get("stratum_ids") or [])
    g4 = (
        stratum_status.get("status") == "PASS"
        and stratum_identity.get("role_substitution") is False
        and not any(s in FORBIDDEN_STRATA for s in strata_ids)
        and int(stratum_identity.get("stratum_count_merged") or 0) >= 4
        and abs(float(stratum_identity.get("target_mass_sum") or 0) - 1.0) < 1e-9
        and bool(stratum_identity.get("mapping_hash"))
    )

    g5 = (
        int(matrix.get("trace_count") or 0) == 180
        and int(matrix.get("trace_failure_count") or 0) == 0
        and complete_traces == expected_traces == 180
        and missing_files == 0
    )

    g6 = False
    if selection.get("status") == "SELECTED" and selected:
        gate_csv = root / "outputs/e2_stage2_stratum/E2_PROFILE_GATE_SUMMARY.csv"
        if gate_csv.is_file():
            gate_df = pd.read_csv(gate_csv)
            row = gate_df.loc[gate_df["profile_id"] == selected]
            g6 = not row.empty and bool(row.iloc[0]["profile_valid"])
        gate_by_seed = root / "outputs/e2_stage2_stratum/E2_PROFILE_GATE_BY_SEED.csv"
        if gate_by_seed.is_file():
            gdf = pd.read_csv(gate_by_seed)
            sel = gdf[gdf["profile_id"] == selected]
            g6 = g6 and bool((sel.groupby("seed")["profile_valid_seed"].all()).all())
        g6 = g6 and selection.get("revalidated_on_stage2_and_true_stratum") is True
        g6 = g6 and selection.get("prior_PROFILE_S2_not_special_cased") is True

    frozen_prof = root / "configs/frozen/e2_stage2_stratum/selected_strength_profile.yaml"
    frozen_prof_id = root / "configs/frozen/e2_stage2_stratum/selected_strength_profile_identity.json"
    frozen_win = root / "configs/frozen/e2_stage2_stratum/selected_window_length.yaml"
    frozen_win_id = root / "configs/frozen/e2_stage2_stratum/selected_window_length_identity.json"
    g7 = (
        selection.get("status") == "SELECTED"
        and selected is not None
        and frozen_prof.is_file()
        and frozen_prof_id.is_file()
        and frozen_win.is_file()
        and frozen_win_id.is_file()
        and window.get("selected_windows") in (100, 200, 300)
        and window.get("prior_300_not_preferred") is True
        and yaml.safe_load(frozen_prof.read_text(encoding="utf-8")).get("selected_profile_id") == selected
        and int(yaml.safe_load(frozen_win.read_text(encoding="utf-8")).get("selected_windows")) == int(
            window.get("selected_windows")
        )
    )

    g8 = (
        chrono.get("chronological_order_status") == "PASS"
        and int(chrono.get("per_client_violation_count") or 0) == 0
        and q_manifest.get("protocol") == "E2-STAGE2-ELIGIBILITY-AND-TRUE-STRATUM-REFREEZE-R1"
        and bool(q_manifest.get("allowed_features"))
        and bool(q_manifest.get("forbidden_features"))
    )
    if matrix.get("manifests"):
        for manifest in matrix["manifests"].values():
            q_audit = manifest.get("q_feature_audit") or {}
            if q_audit.get("leakage_status") != "PASS":
                g8 = False
            if int(q_audit.get("forbidden_feature_count", 1)) != 0:
                g8 = False

    tests_ok = bool(unit_ok and integ_ok and full_ok and unpacked_ok)
    g9 = tests_ok and ledger["ledger_strict_pass"]
    # Strict: never upgrade G9 from junit when ledger or tests fail.

    seed_blob = ""
    for path in [
        root / "outputs/e2_stage2_stratum/E2_STAGE2_STRATUM_CONTEXT.json",
        root / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json",
        root / "configs/frozen/e2_stage2_stratum/selected_strength_profile_identity.json",
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
        and tombstone.get("must_revalidate_all_profiles") is True
    )

    gates = {
        "E2SR-G1": _pass(g1),
        "E2SR-G2": _pass(g2),
        "E2SR-G3": _pass(g3),
        "E2SR-G4": _pass(g4),
        "E2SR-G5": _pass(g5),
        "E2SR-G6": _pass(g6),
        "E2SR-G7": _pass(g7),
        "E2SR-G8": _pass(g8),
        "E2SR-G9": _pass(g9),
        "E2SR-G10": _pass(g10),
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
        "manifest_count": manifest_checks.get("manifest_count"),
        "failed_attempt_audit_status": failed_attempt.get("status"),
        "chronological_order_status": chrono.get("chronological_order_status"),
        "stratum_count_merged": stratum_identity.get("stratum_count_merged"),
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
            root / "outputs/audits/E2_PRIOR_EMPIRICAL_SELECTION_TOMBSTONE.json"
        ) if (root / "outputs/audits/E2_PRIOR_EMPIRICAL_SELECTION_TOMBSTONE.json").is_file() else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-ok", action="store_true")
    parser.add_argument("--integration-ok", action="store_true")
    parser.add_argument("--full-ok", action="store_true")
    parser.add_argument("--unpacked-ok", action="store_true")
    args = parser.parse_args()

    unit_ok = args.unit_ok or _junit_ok(ROOT / "logs/e2_stage2_stratum_unit.xml")
    integ_ok = args.integration_ok or _junit_ok(
        ROOT / "logs/e2_stage2_stratum_integration.xml"
    )
    full_ok = args.full_ok or _junit_ok(
        ROOT / "logs/e2_stage2_stratum_full_repository.xml"
    )
    unpacked_ok = args.unpacked_ok or _junit_ok(
        ROOT / "logs/e2_stage2_stratum_unpacked_specialized.xml"
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
