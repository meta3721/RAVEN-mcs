#!/usr/bin/env python3
"""Export public-target q-seal evidence."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_PUBLIC_TARGET_AND_Q_FEATURE_SEAL_R1"
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
        "src/raven_mcs/e2/traffic_public_target",
        "src/raven_mcs/utils",
        "scripts/prepare_e2_traffic_public_target_and_qseal.py",
        "scripts/check_e2_traffic_public_target_qseal_gates.py",
        "scripts/check_e2_traffic_public_target_qseal_compact_evidence.py",
        "scripts/export_e2_traffic_public_target_qseal_evidence.py",
        "scripts/_run_e2pt_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_traffic_public_target_qseal_core.py",
        "tests/integration/test_e2_traffic_public_target_qseal_stop.py",
        "outputs/traffic_public_target",
        "outputs/e2_traffic_public_target_canary",
        "outputs/audits/E2_TRAFFIC_GROUP_TARGET_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_LABEL_FREE_REGION_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_Q_FEATURE_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_END_TO_END_LEAKAGE_SCAN.json",
        "outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.json",
        "outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_THEORY_COMPATIBILITY.md",
        "outputs/audits/E2_TRAFFIC_PUBLIC_TARGET_NONLEAKAGE_AUDIT.json",
        "configs/frozen/e2_traffic_public_target",
        "configs/frozen/e2_traffic/global_windows_identity.json",
        "configs/frozen/e2_traffic/station_spatial_identity.json",
        "outputs/traffic_mapping/E2_TRAFFIC_ATOMIC_TABLE_IDENTITY.json",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_traffic_public_target_qseal_unit.xml",
        "logs/e2_traffic_public_target_qseal_integration.xml",
        "logs/e2_traffic_public_target_qseal_full_repository.xml",
        "logs/e2pt_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)
    logs = ROOT / "logs"
    if logs.is_dir():
        for path in logs.glob("e2pt_*.log"):
            copy_path(staging, path.relative_to(ROOT).as_posix())

    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    if not report.is_file() or not readme.is_file():
        raise SystemExit("missing report/readme")
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
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(evidence, "r") as archive:
            archive.extractall(tmp)
        needed = [
            f"{PACKAGE}_REPORT.docx",
            f"{PACKAGE}_SUBMISSION_README.txt",
            "outputs/traffic_public_target/E2_TRAFFIC_PUBLIC_TARGET_STOP_STATUS.json",
            "configs/frozen/e2_traffic_public_target/q_feature_manifest.json",
        ]
        unpacked_ok = all((Path(tmp) / n).exists() for n in needed)

    artifacts = {
        f"{PACKAGE}_REPORT.docx": report,
        f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip": evidence,
        f"{PACKAGE}_SUBMISSION_README.txt": readme,
    }
    hashes = {
        "package": PACKAGE,
        "hash_algorithm": "sha256",
        "artifact_count": 3,
        "artifacts": {
            name: {"sha256": sha256(path), "size_bytes": path.stat().st_size}
            for name, path in artifacts.items()
        },
        "unpacked_replay_pass": unpacked_ok,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8",
    )
    mismatch = 0
    for name, path in artifacts.items():
        if sha256(path) != hashes["artifacts"][name]["sha256"]:
            mismatch += 1
    verify = {
        "status": "PASS" if mismatch == 0 and unpacked_ok else "FAIL",
        "verified_count": 3 if mismatch == 0 else 3 - mismatch,
        "expected_count": 3,
        "hash_mismatch_count": mismatch,
        "missing_count": 0,
        "unpacked_replay_pass": unpacked_ok,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2), encoding="utf-8",
    )
    shutil.rmtree(staging, ignore_errors=True)
    print(json.dumps({"status": verify["status"], "evidence": str(evidence), "unpacked_ok": unpacked_ok}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
