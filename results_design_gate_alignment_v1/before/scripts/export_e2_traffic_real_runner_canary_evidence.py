#!/usr/bin/env python3
"""Export real-runner canary evidence ZIP and final hashes."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "E2_TRAFFIC_REAL_RUNNER_CANARY_R1"
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
        "src/raven_mcs/e2/traffic_real_runner",
        "src/raven_mcs/e2/traffic_profiles",
        "src/raven_mcs/e2/traffic_balanced_canary",
        "src/raven_mcs/training",
        "src/raven_mcs/aggregation",
        "src/raven_mcs/simulation",
        "src/raven_mcs/utils",
        "scripts/prepare_e2_traffic_real_runner_canary.py",
        "scripts/check_e2_traffic_real_runner_canary_gates.py",
        "scripts/check_e2_traffic_real_runner_canary_compact_evidence.py",
        "scripts/export_e2_traffic_real_runner_canary_evidence.py",
        "scripts/_run_e2rr_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_traffic_real_runner_canary_core.py",
        "tests/integration/test_e2_traffic_real_runner_canary_stop.py",
        "outputs/e2_traffic_real_runner_canary",
        "outputs/audits/E2_TRAFFIC_REAL_RUNNER_CANARY_INPUT_IDENTITY.json",
        "outputs/audits/E2_TRAFFIC_CANARY_CROSS_METHOD_TRACE_IDENTITY.json",
        "outputs/audits/E2_TRAFFIC_CANARY_RAVEN_RUNTIME_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_BASELINE_RUNTIME_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_METRIC_CONSISTENCY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_NUMERICAL_STABILITY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_CANARY_VALIDATION_FORMAL_NONINSPECTION_AUDIT.json",
        "configs/frozen/e2_traffic_profiles_s1",
        "configs/frozen/e2_traffic_public_target",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_traffic_real_runner_canary_unit.xml",
        "logs/e2_traffic_real_runner_canary_integration.xml",
        "logs/e2_traffic_real_runner_canary_full_repository.xml",
        "logs/e2rr_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)
    logs = ROOT / "logs"
    if logs.is_dir():
        for path in logs.glob("e2rr_*.log"):
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
    if evidence.is_file():
        evidence.unlink()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in staging.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())

    # Final hash order: Word, README, Evidence — then verify only those three.
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
    shutil.rmtree(staging, ignore_errors=True)
    print(json.dumps({"evidence": evidence.as_posix(), "verify": verify["status"]}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
