#!/usr/bin/env python3
"""Export PROFILE-S1 final freeze evidence."""
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
PACKAGE = "E2_TRAFFIC_PROFILE_S1_FINAL_FREEZE_R1"
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
        "src/raven_mcs/e2/traffic_profiles",
        "src/raven_mcs/e2/traffic_balanced_canary",
        "src/raven_mcs/e2/empirical",
        "src/raven_mcs/e2/stage2",
        "src/raven_mcs/e2/distribution",
        "src/raven_mcs/utils",
        "scripts/prepare_e2_traffic_profile_s1_final_freeze.py",
        "scripts/check_e2_traffic_profile_s1_final_freeze_gates.py",
        "scripts/check_e2_traffic_profile_s1_final_freeze_compact_evidence.py",
        "scripts/export_e2_traffic_profile_s1_final_freeze_evidence.py",
        "scripts/_run_e2s1_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_traffic_profile_s1_final_freeze_core.py",
        "tests/integration/test_e2_traffic_profile_s1_final_freeze_stop.py",
        "outputs/e2_traffic_profile_s1",
        "outputs/audits/E2_TRAFFIC_PROFILE_S1_INPUT_IDENTITY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_PROFILE_S2_SUPPORT_TOMBSTONE.json",
        "outputs/audits/E2_TRAFFIC_PROFILE_S1_PARAMETER_CONSISTENCY_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_PROFILE_S1_EXACT_EXPECTED_MASS_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_PROFILE_S1_CLIP_AND_SUPPORT_AUDIT.json",
        "outputs/audits/E2_TRAFFIC_PROFILE_S1_DIRECTION_CERTIFICATE.json",
        "configs/frozen/e2_traffic_profiles_s1",
        "configs/frozen/e2_traffic_public_target",
        "configs/e2_numeric/scenario_direction_registry.yaml",
        "configs/e2_numeric/strength_profile_registry.yaml",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_traffic_profile_s1_final_freeze_unit.xml",
        "logs/e2_traffic_profile_s1_final_freeze_integration.xml",
        "logs/e2_traffic_profile_s1_final_freeze_full_repository.xml",
        "logs/e2s1_pip_check.txt",
    )
    for relative in include:
        copy_path(staging, relative)
    logs = ROOT / "logs"
    if logs.is_dir():
        for path in logs.glob("e2s1_*.log"):
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

    artifacts = {"report": report, "readme": readme, "evidence": evidence}
    hashes = {
        "package": PACKAGE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifacts": {
            name: {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for name, path in artifacts.items()
        },
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES.json").write_text(
        json.dumps(hashes, indent=2) + "\n", encoding="utf-8",
    )
    mismatches = []
    for name, meta in hashes["artifacts"].items():
        actual = sha256(ROOT / meta["path"])
        if actual != meta["sha256"]:
            mismatches.append({"name": name, "expected": meta["sha256"], "actual": actual})
    verify = {
        "status": "PASS" if not mismatches else "FAIL",
        "verified_count": 3 - len(mismatches),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2) + "\n", encoding="utf-8",
    )
    shutil.rmtree(staging, ignore_errors=True)
    print(json.dumps({"evidence": evidence.as_posix(), "verify": verify}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
