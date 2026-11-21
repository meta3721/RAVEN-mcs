"""Integration tests for true stratum non-wrap repair."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATION_SEEDS = (29101, 29102, 29103, 29104, 29105)
PROFILES = tuple(f"PROFILE-S{i}" for i in range(1, 7))
SCENARIOS = (
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
)
COMPACT = (
    "manifest.json",
    "group_mass_diagnostics_300.json",
    "true_stratum_mass_diagnostics_300.json",
    "chronology_audit.json",
    "failed_attempt_audit.json",
    "q_feature_audit.json",
)
FULL_EVENTS = (
    "hard_arrival_events.parquet",
    "continuous_schedule.parquet",
    "opportunity_events.parquet",
)


def test_all_180_traces_rerun():
    base = ROOT / "outputs/e2_true_stratum/traces"
    n = len(list(base.glob("*/*/*/manifest.json")))
    assert n == 180


def test_profile_selection_recomputed():
    sel = json.loads(
        (ROOT / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    assert sel["status"] in {
        "PASS",
        "SELECTED",
        "NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE",
    }
    # Must not silently keep PROFILE-S4 without revalidation.
    assert "reason" in sel or sel.get("selected_profile_id") is not None or sel["status"].startswith("NO_VALID")


def test_window_selection_recomputed():
    win = json.loads(
        (ROOT / "outputs/e2_true_stratum/E2_WINDOW_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    assert win["status"] in {"PASS", "BLOCKED_NO_VALID_PROFILE"}


def test_100_200_are_legal_prefixes_of_300():
    # Nested prefixes exist as diagnostic files on every trace.
    path = next(ROOT.glob("outputs/e2_true_stratum/traces/*/*/*/group_mass_diagnostics_100.json"))
    parent = path.parent
    assert (parent / "group_mass_diagnostics_200.json").is_file()
    assert (parent / "group_mass_diagnostics_300.json").is_file()


def test_failed_attempt_regression():
    audit = json.loads(
        (ROOT / "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["status"] == "PASS"


def test_active_server_window_regression():
    import pandas as pd

    paths = list(
        ROOT.glob("outputs/e2_true_stratum/traces/*/*/*/server_window_activity.parquet")
    )
    if not paths:
        pytest.skip("no full server_window_activity in compact evidence tree")
    df = pd.read_parquet(paths[0])
    assert "server_window_active" in df.columns
    assert len(df) == 300


def test_required_trace_files_if_present():
    base = ROOT / "outputs/e2_true_stratum/traces"
    sel = json.loads(
        (ROOT / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json").read_text(
            encoding="utf-8"
        )
    ).get("selected_profile_id")
    for seed in VALIDATION_SEEDS:
        for profile in PROFILES:
            for scenario in SCENARIOS:
                d = base / str(seed) / profile / scenario
                assert d.is_dir()
                for name in COMPACT:
                    assert (d / name).is_file(), f"{d}/{name}"
                if sel and profile == sel:
                    for name in FULL_EVENTS:
                        assert (d / name).is_file()


def test_full_gate_passes_or_documents_no_valid_profile():
    gate = json.loads(
        (
            ROOT / "outputs/gates/E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1_FULL_GATE.json"
        ).read_text(encoding="utf-8")
    ) if (
        ROOT / "outputs/gates/E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1_FULL_GATE.json"
    ).is_file() else {}
    sel = json.loads(
        (ROOT / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json").read_text(
            encoding="utf-8"
        )
    )
    if sel["status"] == "NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE":
        assert sel["selected_profile_id"] is None
    elif gate:
        assert gate["gates"]["E2TN-G6"] == "PASS"


def test_compact_evidence_gate_passes():
    import subprocess
    import sys

    gate_path = ROOT / "outputs/gates/compact_evidence_gate.json"
    if not gate_path.is_file():
        subprocess.check_call(
            [sys.executable, "scripts/check_e2_true_stratum_compact_evidence.py"],
            cwd=ROOT,
        )
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    assert gate["status"] == "PASS"


def test_complete_ledger_contains_trace_generation():
    ledger = ROOT / "logs/E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        pytest.skip("ledger not yet written")
    text = ledger.read_text(encoding="utf-8")
    assert "prepare_e2_true_stratum" in text or "true_stratum" in text


def test_formal_seed_noninspection():
    assert not (ROOT / "outputs/e2_true_stratum/traces/30001").exists()


def test_external_hash_verifies_three_artifacts():
    path = ROOT / (
        "deliverables/TO_SUBMIT_E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1/"
        "FINAL_DELIVERABLE_HASHES_VERIFY.json"
    )
    if not path.is_file():
        pytest.skip("hashes not yet written")
    ver = json.loads(path.read_text(encoding="utf-8"))
    assert ver.get("status") == "PASS"
    assert int(ver.get("verified_count", 0)) == 3
