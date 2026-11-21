#!/usr/bin/env python3
"""Export E2 data recovery evidence (manifests/audits only; no giant raw dumps)."""
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
PACKAGE = "E2_DATA_HORIZON_AND_SPATIAL_METADATA_RECOVERY_R1"
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
        "src/raven_mcs/e2/identity.py",
        "src/raven_mcs/utils",
        "scripts/prepare_e2_data_horizon_and_spatial_recovery.py",
        "scripts/check_e2_data_horizon_spatial_recovery_gates.py",
        "scripts/check_e2_data_horizon_spatial_recovery_compact_evidence.py",
        "scripts/export_e2_data_horizon_spatial_recovery_evidence.py",
        "scripts/_run_e2dr_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_data_horizon_spatial_recovery_core.py",
        "tests/integration/test_e2_data_horizon_spatial_recovery_stop.py",
        "outputs/data_recovery",
        "outputs/audits/E2_CURRENT_SENSOR_SUBSET_TOMBSTONE.json",
        "outputs/audits/E2_DATA_RECOVERY_NONLEAKAGE_AUDIT.json",
        "configs/frozen/e2_data_recovery",
        "configs/dataset/sensorscope.yaml",
        "configs/dataset/traffic.yaml",
        "configs/dataset/uair.yaml",
        "configs/dataset/tdrive_speed.yaml",
        "data/manifests",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_data_horizon_spatial_recovery_unit.xml",
        "logs/e2_data_horizon_spatial_recovery_integration.xml",
        "logs/e2_data_horizon_spatial_recovery_full_repository.xml",
        "logs/e2dr_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)

    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    if not report.is_file():
        raise SystemExit(f"missing report: {report}")
    stop = json.loads((ROOT / "outputs/data_recovery/E2_STOP_STATUS.json").read_text(encoding="utf-8"))
    decision = json.loads((ROOT / "outputs/data_recovery/E2_PROTOCOL_ROUTE_DECISION.json").read_text(encoding="utf-8"))
    ranking = json.loads((ROOT / "outputs/data_recovery/E2_REPLACEMENT_DATASET_RANKING.json").read_text(encoding="utf-8"))
    readme.write_text("\n".join((
        f"package={PACKAGE}",
        f"round_outcome={stop.get('status')}",
        f"route={decision.get('selected_route')}",
        f"replacement={ranking.get('selected_dataset')}",
        f"next={decision.get('next_authorized_round')}",
        "experimental_traces=0",
        "validation_reads=0",
        "Profile selection=NOT_STARTED",
        "",
        "Replay:",
        "  set PYTHONPATH=src",
        "  pytest -q tests/unit/test_e2_data_horizon_spatial_recovery_*.py",
        "  pytest -q tests/integration/test_e2_data_horizon_spatial_recovery_*.py",
        "  python scripts/check_e2_data_horizon_spatial_recovery_compact_evidence.py",
        "",
        "Note: large raw Sensorscope.zip is NOT bundled; see manifests + checksums.",
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
    with tempfile.TemporaryDirectory(prefix="e2dr_unpack_") as temporary:
        unpacked = Path(temporary)
        with zipfile.ZipFile(evidence) as archive:
            archive.extractall(unpacked)
        env = dict(os.environ, PYTHONPATH=str(unpacked / "src"))
        unit = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/unit/test_e2_data_horizon_spatial_recovery_core.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        integ = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/integration/test_e2_data_horizon_spatial_recovery_stop.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        compact = subprocess.run(
            [python, "scripts/check_e2_data_horizon_spatial_recovery_compact_evidence.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        (ROOT / "logs/e2dr_unpacked_stdout.log").write_text(
            (unit.stdout or "") + (integ.stdout or "") + (compact.stdout or ""), encoding="utf-8",
        )
        (ROOT / "logs/e2dr_unpacked_stderr.log").write_text(
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
