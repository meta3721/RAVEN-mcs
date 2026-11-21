#!/usr/bin/env python3
"""Export ledger-closure deliverable ZIP and hashes."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_LEDGER_CLOSURE_R1"
CANARY_PKG = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
OUT_DIR = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_path(staging: Path, relative: str) -> None:
    source = ROOT / relative
    if not source.exists():
        return
    destination = staging / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)


def write_report(stop: dict, gates: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    doc.add_heading("E2-TRAFFIC-REAL-RUNNER-LEDGER-CLOSURE-R1 Report", level=0)
    doc.add_heading("1. Executive Summary", level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Metric"
    table.rows[0].cells[1].text = "Value"
    front = {
        "status": stop.get("status"),
        "seed": 29001,
        "fresh_rerun": stop.get("fresh_rerun"),
        "reaudit_only": stop.get("reaudit_only"),
        "completed_runs": stop.get("completed_run_count"),
        "training_START/FINISH": "see G9 diagnostics",
        "G1-G10 all_pass": gates.get("all_pass"),
        "next": stop.get("next_authorized_round"),
        "runtime_commit": stop.get("runtime_commit"),
    }
    for k, v in front.items():
        row = table.add_row().cells
        row[0].text = str(k)
        row[1].text = str(v)
    sections = [
        ("2. Why previous G9 was insufficient",
         "Prior ledger recorded reaudit/replay of aggregated results, not 30 independent --run-one training commands with START/FINISH pairing and I/O hashes."),
        ("3. Frozen scope and unchanged hashes",
         {"profile": "PROFILE-S1", "registry_sha256": stop.get("registry_sha256")}),
        ("4. Code changes",
         "Limited to prepare CLI split, run_and_log START/FINISH+input hashes, ledger sequence, G9 evaluator, tests, export."),
        ("5. Fresh-run proof",
         {"fresh_rerun": stop.get("fresh_rerun"), "reaudit_only": stop.get("reaudit_only")}),
        ("6-11. Audits", gates.get("g9_diagnostics", {})),
        ("12. G1-G10", gates.get("gates")),
        ("13. Tests", "See JUnit XML in evidence"),
        ("14. Noninspection", {"validation": stop.get("validation_seed_reads"), "formal": stop.get("formal_seed_reads")}),
        ("15. Stop position", stop.get("status")),
        ("16. Next authorized round", stop.get("next_authorized_round")),
    ]
    for title, body in sections:
        doc.add_heading(title, level=1)
        doc.add_paragraph(json.dumps(body, indent=2, default=str)[:7000])
    doc.save(path)
    return path


def write_readme(stop: dict, gates: dict, g9: dict) -> Path:
    path = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    path.write_text(
        "\n".join([
            f"Round: {PACKAGE}",
            "Frozen profile: PROFILE-S1",
            "Seed: 29001 only",
            "Scenarios: 6",
            "Methods: 5",
            "Fresh real training runs: 30",
            f"Training Ledger START records: {g9.get('training_start_count')}",
            f"Training Ledger FINISH records: {g9.get('training_finish_count')}",
            f"Unique scenario-method pairs: {g9.get('unique_scenario_method_count')}",
            f"Retry count: {stop.get('retry_count')}",
            f"Seed replacement count: {stop.get('seed_replacement_count')}",
            f"Validation seed reads: {stop.get('validation_seed_reads')}",
            f"Formal seed reads: {stop.get('formal_seed_reads')}",
            f"Formal run count: {stop.get('formal_run_count')}",
            f"All G1-G10: {'PASS' if gates.get('all_pass') else 'FAIL'}",
            f"Status: {stop.get('status')}",
            f"Next authorized round: {stop.get('next_authorized_round')}",
            f"Runtime commit: {stop.get('runtime_commit')}",
        ]) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> int:
    python = str(PYTHON if PYTHON.is_file() else Path(sys.executable))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stop = json.loads(
        (ROOT / "outputs/e2_traffic_real_runner_canary/E2_TRAFFIC_REAL_RUNNER_CANARY_STOP_STATUS.json").read_text(
            encoding="utf-8",
        )
    )
    gates = json.loads((ROOT / f"outputs/gates/{CANARY_PKG}_GATES.json").read_text(encoding="utf-8"))
    g9 = gates.get("g9_diagnostics") or {}
    report = write_report(stop, gates)
    readme = write_readme(stop, gates, g9)

    staging = OUT_DIR / "_staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    # Checkpoint hash inventory (avoid huge pt copies if needed — include files + inventory).
    ckpt_inv = []
    for sid in ["balanced", "opportunity_only", "observation_only", "usable_only", "complete_aligned", "complete_counteracting"]:
        for method in ["fedavg_window", "fedasync_window", "flamf_timealign_adapted", "twostage_hajek", "raven"]:
            p = ROOT / f"outputs/e2_traffic_real_runner_canary/runs/{sid}/{method}/checkpoints/final.pt"
            if p.is_file():
                ckpt_inv.append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)})
    (staging / "checkpoint_hash_inventory.json").write_text(json.dumps(ckpt_inv, indent=2) + "\n", encoding="utf-8")

    include = (
        "src/raven_mcs/e2/traffic_real_runner",
        "scripts/prepare_e2_traffic_real_runner_canary.py",
        "scripts/run_and_log.py",
        "scripts/_run_e2rr_ledger_sequence.py",
        "scripts/check_e2_traffic_real_runner_canary_gates.py",
        "scripts/check_e2_traffic_real_runner_canary_compact_evidence.py",
        "scripts/export_e2_traffic_real_runner_ledger_closure_evidence.py",
        "tests/unit/test_e2_traffic_real_runner_ledger_g9.py",
        "tests/unit/test_e2_traffic_real_runner_canary_core.py",
        "tests/integration/test_e2_traffic_real_runner_canary_stop.py",
        "configs/frozen/e2_traffic_profiles_s1",
        "configs/frozen/e2_traffic_public_target",
        "outputs/e2_traffic_real_runner_canary",
        "outputs/audits/E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json",
        "outputs/audits/E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json",
        "outputs/audits/E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_METRIC_CONSISTENCY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_NUMERICAL_STABILITY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json",
        f"outputs/gates/{CANARY_PKG}_GATES.json",
        f"outputs/gates/{CANARY_PKG}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{CANARY_PKG}_EXACT_COMMANDS.jsonl",
        "logs/e2_traffic_real_runner_canary_unit.xml",
        "logs/e2_traffic_real_runner_canary_integration.xml",
        "logs/e2_traffic_real_runner_canary_full_repository.xml",
        "logs/e2_traffic_real_runner_ledger_g9_unit.xml",
        "logs/e2rr_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)
    # training logs
    for path in (ROOT / "logs").glob("e2rr_train_seed29001__*.*.log"):
        copy_path(staging, path.relative_to(ROOT).as_posix())
    for path in (ROOT / "logs").glob("e2rr_*.stdout.log"):
        copy_path(staging, path.relative_to(ROOT).as_posix())
    for path in (ROOT / "logs").glob("e2rr_*.stderr.log"):
        copy_path(staging, path.relative_to(ROOT).as_posix())

    # archive manifest pointer
    latest = ROOT / "outputs/archive/E2_TRAFFIC_REAL_RUNNER_CANARY_R1_PRE_LEDGER_CLOSURE_LATEST.txt"
    if latest.is_file():
        arch = Path(latest.read_text(encoding="utf-8").strip())
        man = arch / "archive_manifest.json"
        if man.is_file():
            dest = staging / "archive_manifest.json"
            shutil.copy2(man, dest)

    shutil.copy2(report, staging / report.name)
    shutil.copy2(readme, staging / readme.name)
    (staging / "python-version.txt").write_text(
        subprocess.check_output([python, "--version"], text=True), encoding="utf-8",
    )
    (staging / "git-HEAD.txt").write_text(
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True), encoding="utf-8",
    )
    if (ROOT / "requirements-lock.txt").is_file():
        shutil.copy2(ROOT / "requirements-lock.txt", staging / "requirements-lock.txt")
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True)
    (staging / "environment-freeze.txt").write_text(freeze.stdout or "", encoding="utf-8")

    evidence = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if evidence.is_file():
        evidence.unlink()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in staging.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())

    # Outer submission ZIP
    outer = OUT_DIR / f"TO_SUBMIT_{PACKAGE}.zip"
    hashes = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            f"{PACKAGE}_REPORT.docx": sha256(report),
            f"{PACKAGE}_SUBMISSION_README.txt": sha256(readme),
            f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip": sha256(evidence),
        },
    }
    hash_path = OUT_DIR / "FINAL_DELIVERABLE_HASHES.json"
    hash_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")

    verify = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verified_artifact_count": 0,
        "hash_mismatch_count": 0,
        "rows": [],
    }
    for name, digest in hashes["artifacts"].items():
        path = OUT_DIR / name
        actual = sha256(path)
        ok = actual == digest
        verify["rows"].append({"artifact": name, "expected": digest, "actual": actual, "match": ok})
        if ok:
            verify["verified_artifact_count"] += 1
        else:
            verify["hash_mismatch_count"] += 1
    verify["status"] = "PASS" if verify["hash_mismatch_count"] == 0 and verify["verified_artifact_count"] == 3 else "FAIL"
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2) + "\n", encoding="utf-8",
    )

    if outer.is_file():
        outer.unlink()
    with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in (
            f"{PACKAGE}_REPORT.docx",
            f"{PACKAGE}_SUBMISSION_README.txt",
            f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
            "FINAL_DELIVERABLE_HASHES.json",
            "FINAL_DELIVERABLE_HASHES_VERIFY.json",
        ):
            zf.write(OUT_DIR / name, name)

    shutil.rmtree(staging, ignore_errors=True)
    print(json.dumps({
        "submission_zip": outer.as_posix(),
        "verify": verify["status"],
        "stop": stop.get("status"),
    }, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
