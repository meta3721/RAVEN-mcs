#!/usr/bin/env python3
"""Export E2 global-window / finite-sample gate evidence package."""
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
PACKAGE = "E2_GLOBAL_WINDOW_AND_FINITE_SAMPLE_GATE_REPAIR_R1"
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


def main() -> int:
    python = str(PYTHON if PYTHON.is_file() else Path(sys.executable))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    staging = OUT_DIR / "_staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)

    include = (
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2/__init__.py",
        "src/raven_mcs/e2/global_window",
        "src/raven_mcs/e2/legal_horizon",
        "src/raven_mcs/e2/identity.py",
        "src/raven_mcs/utils",
        "configs/frozen/e2_global_windows",
        "configs/frozen/e2_spatial_identity",
        "configs/frozen/e2_finite_sample_gate",
        "scripts/prepare_e2_global_window_and_finite_sample_gate.py",
        "scripts/check_e2_global_window_finite_gate_gates.py",
        "scripts/check_e2_global_window_finite_gate_compact_evidence.py",
        "scripts/export_e2_global_window_finite_gate_evidence.py",
        "scripts/_run_e2gw_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_global_window_finite_gate_core.py",
        "tests/integration/test_e2_global_window_finite_gate_stop.py",
        "outputs/audits/E2_PRIOR_LOCAL_WINDOW_AND_GATE_TOMBSTONE.json",
        "outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json",
        "outputs/audits/E2_ATOMIC_UNIQUE_WINDOW_ASSIGNMENT_AUDIT.json",
        "outputs/audits/E2_TRUE_SPATIAL_IDENTITY_AUDIT.json",
        "outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json",
        "outputs/audits/E2_FINITE_SAMPLE_GATE_JUSTIFICATION.json",
        "outputs/e2_global_window",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_global_window_finite_gate_unit.xml",
        "logs/e2_global_window_finite_gate_integration.xml",
        "logs/e2_global_window_finite_gate_full_repository.xml",
        "logs/e2gw_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)

    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    if not report.is_file():
        raise SystemExit(f"missing report: {report}")
    stop = json.loads((ROOT / "outputs/e2_global_window/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    win = json.loads((ROOT / "outputs/audits/E2_GLOBAL_SERVER_WINDOW_AUDIT.json").read_text(encoding="utf-8"))
    cap = win.get("capacity") or stop.get("capacity") or {}
    readme.write_text("\n".join((
        f"package={PACKAGE}",
        f"round_outcome={stop.get('status')}",
        f"max_legal_global_windows={cap.get('max_legal_global_windows')}",
        f"window_hours={cap.get('window_hours')}",
        f"supported_span_hours={cap.get('supported_span_hours')}",
        f"spatial_status={stop.get('spatial_status')}",
        "validation_traces=0",
        "design_seeds=28101-28120",
        "validation_seeds=29101-29105 NOT_RUN",
        "profile_selection=NOT_STARTED",
        "seed_29001_read_count=0; real_canary=0/20; formal_runs=0; E3-E9=NOT_STARTED",
        "",
        "Replay:",
        "  set PYTHONPATH=src",
        "  pytest -q tests/unit/test_e2_global_window_finite_gate_*.py",
        "  pytest -q tests/integration/test_e2_global_window_finite_gate_*.py",
        "  python scripts/check_e2_global_window_finite_gate_compact_evidence.py",
        "",
    )), encoding="utf-8")
    shutil.copy2(report, staging / report.name)
    shutil.copy2(readme, staging / readme.name)
    (staging / "python-version.txt").write_text(
        subprocess.check_output([python, "--version"], text=True), encoding="utf-8",
    )
    if (ROOT / "requirements-lock.txt").is_file():
        shutil.copy2(ROOT / "requirements-lock.txt", staging / "requirements-lock.txt")
    freeze = subprocess.run([python, "-m", "pip", "freeze"], capture_output=True, text=True)
    (staging / "environment-freeze.txt").write_text(freeze.stdout or "", encoding="utf-8")

    evidence = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if evidence.exists():
        evidence.unlink()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())

    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2gw_unpack_") as temporary:
        unpacked = Path(temporary)
        with zipfile.ZipFile(evidence) as archive:
            archive.extractall(unpacked)
        env = dict(os.environ, PYTHONPATH=str(unpacked / "src"))
        unit = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/unit/test_e2_global_window_finite_gate_core.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        integ = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/integration/test_e2_global_window_finite_gate_stop.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        compact = subprocess.run(
            [python, "scripts/check_e2_global_window_finite_gate_compact_evidence.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        (ROOT / "logs/e2gw_unpacked_stdout.log").write_text(
            (unit.stdout or "") + (integ.stdout or "") + (compact.stdout or ""), encoding="utf-8",
        )
        (ROOT / "logs/e2gw_unpacked_stderr.log").write_text(
            (unit.stderr or "") + (integ.stderr or "") + (compact.stderr or ""), encoding="utf-8",
        )
        unpacked_ok = unit.returncode == integ.returncode == compact.returncode == 0

    artifacts = {
        path.name: {"sha256": sha256(path), "size_bytes": path.stat().st_size}
        for path in (report, evidence, readme)
    }
    hashes = {
        "package": PACKAGE,
        "hash_algorithm": "sha256",
        "no_self_reference": True,
        "artifact_count": 3,
        "artifacts": artifacts,
        "unpacked_replay_pass": unpacked_ok,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    verified = mismatches = missing = 0
    for name, expected in artifacts.items():
        path = OUT_DIR / name
        if not path.is_file():
            missing += 1
        elif sha256(path) == expected["sha256"]:
            verified += 1
        else:
            mismatches += 1
    verify = {
        "status": "PASS" if verified == 3 and not mismatches and not missing and unpacked_ok else "FAIL",
        "verified_count": verified,
        "expected_count": 3,
        "hash_mismatch_count": mismatches,
        "missing_count": missing,
        "unpacked_replay_pass": unpacked_ok,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(staging, ignore_errors=True)
    print(json.dumps({"status": verify["status"], "evidence": str(evidence), "unpacked_ok": unpacked_ok}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
