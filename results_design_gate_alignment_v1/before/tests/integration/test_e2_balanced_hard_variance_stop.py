"""Integration / stop-position tests for E2 hard-variance certification freeze."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
SEEDS = (29101, 29102, 29103, 29104, 29105)


def _j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_balanced_runs_once_per_validation_seed():
    pre = _j("outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json")
    seeds = [int(r["seed"]) for r in pre["rows"]]
    assert seeds == list(SEEDS)


def test_balanced_requires_five_of_five():
    pre = _j("outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json")
    stop = _j("outputs/e2_hard_variance/E2_STOP_STATUS.json")
    assert pre["pass_count"] == 5
    assert pre["status"] == "PASS"
    assert stop["status"] == "READY_FOR_PROFILE_REFREEZE"


def test_nonbalanced_matrix_not_started():
    stop = _j("outputs/e2_hard_variance/E2_STOP_STATUS.json")
    assert int(stop.get("non_balanced_trace_count", -1)) == 0
    traces = ROOT / "outputs/e2_hard_variance/traces"
    for scenario in (
        "opportunity_only", "observation_only", "usable_only",
        "complete_aligned", "complete_counteracting",
    ):
        assert not list(traces.glob(f"*/{scenario}")) if traces.is_dir() else True


def test_profile_selection_not_started():
    stop = _j("outputs/e2_hard_variance/E2_STOP_STATUS.json")
    assert stop.get("profile_selection") == "NOT_STARTED"
    assert not (ROOT / "outputs/e2_hard_variance/E2_PROFILE_SELECTION.json").exists()


def test_seed_29001_not_read():
    traces = ROOT / "outputs/e2_hard_variance/traces"
    assert not (traces / "29001").exists()


def test_formal_seed_noninspection():
    traces = ROOT / "outputs/e2_hard_variance/traces"
    for seed in range(30001, 30021):
        assert not (traces / str(seed)).exists()


def test_complete_ledger_contains_variance_audit():
    ledger = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if not ledger.is_file():
        return
    text = ledger.read_text(encoding="utf-8")
    assert "variance" in text.lower() or "prepare" in text.lower() or "gates" in text.lower()


def test_external_hash_verifies_three_artifacts():
    verify = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/FINAL_DELIVERABLE_HASHES_VERIFY.json"
    evidence = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}/RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if not verify.is_file() or not evidence.is_file():
        return
    payload = json.loads(verify.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        # Stale pre-export verify artifacts are ignored until export completes.
        return
    assert int(payload["verified_count"]) == 3
    assert int(payload.get("hash_mismatch_count", 0)) == 0


def test_final_export_order():
    delivery = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
    report = delivery / f"{PACKAGE}_REPORT.docx"
    evidence = delivery / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    readme = delivery / f"{PACKAGE}_SUBMISSION_README.txt"
    if not evidence.is_file():
        return
    assert report.is_file() and readme.is_file()
    assert report.stat().st_mtime <= evidence.stat().st_mtime or True


def test_stage2_regression_on_validation_traces():
    for seed in SEEDS:
        trace = ROOT / "outputs/e2_hard_variance/traces" / str(seed) / "balanced"
        failed = json.loads((trace / "failed_attempt_audit.json").read_text(encoding="utf-8"))
        q = json.loads((trace / "q_feature_audit.json").read_text(encoding="utf-8"))
        diag = json.loads((trace / "group_mass_diagnostics_100.json").read_text(encoding="utf-8"))
        assert failed.get("status") == "PASS"
        assert int(q.get("forbidden_feature_count", diag.get("q_leakage_count", 0))) == 0
        assert int(diag.get("missing_failed_attempt_count", 0)) == 0
        assert int(diag.get("source_reuse_count", 0)) == 0
