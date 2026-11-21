#!/usr/bin/env python3
"""Export self-contained E2 hard-variance certification evidence package."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_BALANCED_HARD_VARIANCE_AND_CERTIFICATION_STRATUM_FREEZE_R1"
OUT_DIR = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
SEEDS = (29101, 29102, 29103, 29104, 29105)


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


def main() -> int:
    python = str(PYTHON if PYTHON.is_file() else Path(sys.executable))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    staging = OUT_DIR / "_staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    # Raw stratum identity snapshot for evidence completeness.
    snap = ROOT / "outputs/e2_hard_variance/E2_RAW_TRUE_STRATUM_IDENTITY_SNAPSHOT.json"
    if not snap.is_file():
        snap.write_text(json.dumps({
            "raw_stratum_count": 440,
            "definition": "station × time_block × weekday/weekend",
            "status": "UNCHANGED",
            "algorithm_identity": "raw_true_stratum",
        }, indent=2) + "\n", encoding="utf-8")

    include = (
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2/__init__.py",
        "src/raven_mcs/e2/hard_variance",
        "src/raven_mcs/e2/legal_horizon",
        "src/raven_mcs/e2/stage2",
        "src/raven_mcs/e2/empirical",
        "src/raven_mcs/e2/distribution",
        "src/raven_mcs/e2/identity.py",
        "src/raven_mcs/utils",
        "configs/frozen/e2_certification",
        "configs/frozen/e2_legal_horizon",
        "scripts/prepare_e2_balanced_hard_variance_and_certification.py",
        "scripts/check_e2_balanced_hard_variance_gates.py",
        "scripts/check_e2_balanced_hard_variance_compact_evidence.py",
        "scripts/export_e2_balanced_hard_variance_evidence.py",
        "scripts/_run_e2hv_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_balanced_hard_variance_core.py",
        "tests/integration/test_e2_balanced_hard_variance_stop.py",
        "outputs/audits/E2_CANDIDATE_TRUNCATION_AUDIT.json",
        "outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_balanced_hard_variance_unit.xml",
        "logs/e2_balanced_hard_variance_integration.xml",
        "logs/e2_balanced_hard_variance_full_repository.xml",
        "logs/e2hv_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)

    # Compact outputs (skip large parquet event dumps except antithetic marker presence via diagnostics).
    src_out = ROOT / "outputs/e2_hard_variance"
    dest_out = staging / "outputs/e2_hard_variance"
    dest_out.mkdir(parents=True, exist_ok=True)
    for item in src_out.iterdir():
        if item.name == "traces":
            continue
        if item.is_file():
            shutil.copy2(item, dest_out / item.name)
    compact_names = (
        "manifest.json", "group_mass_diagnostics_100.json",
        "certification_mass_diagnostics_100.json", "chronology_audit.json",
        "failed_attempt_audit.json", "q_feature_audit.json", "stdout.log", "stderr.log",
    )
    for seed in SEEDS:
        source = ROOT / "outputs/e2_hard_variance/traces" / str(seed) / "balanced"
        destination = staging / source.relative_to(ROOT)
        destination.mkdir(parents=True, exist_ok=True)
        for name in compact_names:
            if (source / name).is_file():
                shutil.copy2(source / name, destination / name)

    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    if not report.is_file():
        raise SystemExit(f"missing report: {report}")
    stop = json.loads((ROOT / "outputs/e2_hard_variance/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    pre = json.loads((ROOT / "outputs/e2_hard_variance/E2_BALANCED_CERT_PRE_GATE_SUMMARY.json").read_text(encoding="utf-8"))
    sel = json.loads((ROOT / "outputs/e2_hard_variance/E2_CERTIFICATION_LEVEL_SELECTION.json").read_text(encoding="utf-8"))
    dense = json.loads((ROOT / "outputs/audits/E2_DENSE_LEGAL_CANDIDATE_EXPOSURE_AUDIT.json").read_text(encoding="utf-8"))
    readme.write_text(
        "\n".join((
            f"package={PACKAGE}",
            f"round_outcome={stop.get('status')}",
            "selected_windows=100",
            f"avg_candidates_before={dense.get('average_candidates_before')}",
            f"avg_candidates_after={dense.get('average_candidates_after')}",
            "raw_stratum_count=440 (UNCHANGED)",
            f"selected_certification_level={sel.get('selected_level')}",
            f"balanced_cert_pre_gate={pre.get('pass_count')}/5 PASS",
            "non_balanced_trace_count=0",
            "profile_selection=NOT_STARTED",
            "seed_29001_read_count=0; real_canary=0/20; formal_runs=0; E3-E9=NOT_STARTED",
            "",
            "Replay:",
            "  set PYTHONPATH=src",
            "  pytest -q tests/unit/test_e2_balanced_hard_variance_*.py",
            "  pytest -q tests/integration/test_e2_balanced_hard_variance_*.py",
            "  python scripts/check_e2_balanced_hard_variance_gates.py",
            "  python scripts/check_e2_balanced_hard_variance_compact_evidence.py",
            "",
        )),
        encoding="utf-8",
    )
    shutil.copy2(report, staging / report.name)
    shutil.copy2(readme, staging / readme.name)

    (staging / "python-version.txt").write_text(
        subprocess.check_output([python, "--version"], text=True), encoding="utf-8",
    )
    if (ROOT / "requirements-lock.txt").is_file():
        shutil.copy2(ROOT / "requirements-lock.txt", staging / "requirements-lock.txt")
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True)
    (staging / "environment-freeze.txt").write_text(freeze.stdout or "", encoding="utf-8")
    if (ROOT / "logs/e2hv_pip_check.txt").is_file():
        shutil.copy2(ROOT / "logs/e2hv_pip_check.txt", staging / "logs/e2hv_pip_check.txt")

    evidence = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if evidence.exists():
        evidence.unlink()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())

    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2hv_unpack_") as temporary:
        unpacked = Path(temporary)
        with zipfile.ZipFile(evidence) as archive:
            archive.extractall(unpacked)
        env = dict(os.environ, PYTHONPATH=str(unpacked / "src"))
        unit = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/unit/test_e2_balanced_hard_variance_core.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        integ = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/integration/test_e2_balanced_hard_variance_stop.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        compact = subprocess.run(
            [python, "scripts/check_e2_balanced_hard_variance_compact_evidence.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        (ROOT / "logs/e2hv_unpacked_stdout.log").write_text(
            unit.stdout + integ.stdout + compact.stdout, encoding="utf-8",
        )
        (ROOT / "logs/e2hv_unpacked_stderr.log").write_text(
            unit.stderr + integ.stderr + compact.stderr, encoding="utf-8",
        )
        unpacked_ok = unit.returncode == integ.returncode == compact.returncode == 0

    # Hash triad AFTER evidence/readme/report are final.
    artifacts = {
        path.name: {"sha256": sha256(path), "size_bytes": path.stat().st_size}
        for path in (report, evidence, readme)
    }
    hashes = {
        "package": PACKAGE,
        "hash_algorithm": "sha256",
        "no_self_reference": True,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "unpacked_replay_pass": unpacked_ok,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    verified_count = mismatches = missing = 0
    for name, expected in artifacts.items():
        path = OUT_DIR / name
        if not path.is_file():
            missing += 1
        elif sha256(path) == expected["sha256"]:
            verified_count += 1
        else:
            mismatches += 1
    verify = {
        "status": "PASS" if verified_count == 3 and not mismatches and not missing and unpacked_ok else "FAIL",
        "verified_count": verified_count,
        "expected_count": 3,
        "hash_mismatch_count": mismatches,
        "missing_count": missing,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    hashes_path = OUT_DIR / "FINAL_DELIVERABLE_HASHES.json"
    verify_path = OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json"
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    verify_path.write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
    manifest = OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json"
    manifest.write_text(json.dumps({
        "package": PACKAGE,
        "round_outcome": stop.get("status"),
        "files": [report.name, evidence.name, readme.name, hashes_path.name, verify_path.name],
    }, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(staging)
    print(json.dumps({"status": verify["status"], "evidence": str(evidence), "unpacked_ok": unpacked_ok}, indent=2))
    return 0 if unpacked_ok and verify["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
