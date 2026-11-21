#!/usr/bin/env python3
"""Export a self-contained E2 legal-horizon Balanced evidence package."""
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
PACKAGE = "E2_LEGAL_HORIZON_AND_BALANCED_OPPORTUNITY_CALIBRATION_R1"
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
    include = (
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2/__init__.py",
        "src/raven_mcs/e2/legal_horizon",
        "src/raven_mcs/e2/stage2",
        "src/raven_mcs/e2/distribution",
        "src/raven_mcs/utils",
        "configs/frozen/e2_legal_horizon",
        "configs/frozen/e2_balanced_calibration",
        "scripts/prepare_e2_legal_horizon_and_balanced_calibration.py",
        "scripts/check_e2_legal_horizon_balanced_gates.py",
        "scripts/check_e2_legal_horizon_compact_evidence.py",
        "scripts/export_e2_legal_horizon_balanced_evidence.py",
        "scripts/_run_e2lb_ledger_sequence.py",
        "scripts/run_and_log.py",
        "tests/test_e2_legal_horizon_balanced_calibration.py",
        "outputs/e2_balanced_calibration",
        "outputs/audits/E2_ILLEGAL_300_AND_UNCALIBRATED_BALANCED_TOMBSTONE.json",
        "outputs/audits/E2_LEGAL_HORIZON_AUDIT.json",
        "outputs/audits/E2_100_WINDOW_SOURCE_UNIQUENESS_AUDIT.json",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
    )
    for relative in include:
        # The five trace directories are copied compactly below.
        if relative == "outputs/e2_balanced_calibration":
            src = ROOT / relative
            dest = staging / relative
            dest.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                if item.name != "traces":
                    copy_path(staging, str(Path(relative) / item.name))
            continue
        copy_path(staging, relative)
    compact_names = (
        "manifest.json", "resolved_config.yaml", "group_mass_diagnostics_100.json",
        "true_stratum_mass_diagnostics_100.json", "chronology_audit.json",
        "failed_attempt_audit.json", "q_feature_audit.json", "stdout.log", "stderr.log",
    )
    for seed in SEEDS:
        source = ROOT / "outputs/e2_balanced_calibration/traces" / str(seed) / "SHARED_BALANCED" / "balanced"
        destination = staging / source.relative_to(ROOT)
        destination.mkdir(parents=True, exist_ok=True)
        for name in compact_names:
            if (source / name).is_file():
                shutil.copy2(source / name, destination / name)

    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    if not report.is_file():
        raise SystemExit(f"missing report: {report}")
    readme.write_text(
        "\n".join((
            f"package={PACKAGE}",
            "round_outcome=BALANCED_PRE_GATE_FAIL",
            "legal_horizon=100 (maximum continuous horizon=105)",
            "source_reuse_count=0",
            "soft_calibration=PASS",
            "hard_balanced_pre_gate=FAIL (0/5), recorded as expected stop",
            "matrix=BLOCKED; selected_profile=None",
            "seed_29001_read_count=0; real_canary=0/20; formal_runs=0; E3-E9=NOT_STARTED",
            "",
            "Replay:",
            "  set PYTHONPATH=src",
            "  python scripts/check_e2_legal_horizon_balanced_gates.py",
            "  python scripts/check_e2_legal_horizon_compact_evidence.py",
            "  python -m pytest -q tests/test_e2_legal_horizon_balanced_calibration.py",
            "",
        )),
        encoding="utf-8",
    )
    shutil.copy2(report, staging / report.name)
    shutil.copy2(readme, staging / readme.name)

    evidence = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if evidence.exists():
        evidence.unlink()
    with zipfile.ZipFile(evidence, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())

    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2lb_unpack_") as temporary:
        unpacked = Path(temporary)
        with zipfile.ZipFile(evidence) as archive:
            archive.extractall(unpacked)
        env = dict(os.environ, PYTHONPATH=str(unpacked / "src"))
        gates = subprocess.run(
            [python, "scripts/check_e2_legal_horizon_balanced_gates.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        compact = subprocess.run(
            [python, "scripts/check_e2_legal_horizon_compact_evidence.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        tests = subprocess.run(
            [python, "-m", "pytest", "-q", "tests/test_e2_legal_horizon_balanced_calibration.py"],
            cwd=unpacked, env=env, capture_output=True, text=True,
        )
        (ROOT / "logs/e2lb_unpacked_stdout.log").write_text(
            gates.stdout + compact.stdout + tests.stdout, encoding="utf-8",
        )
        (ROOT / "logs/e2lb_unpacked_stderr.log").write_text(
            gates.stderr + compact.stderr + tests.stderr, encoding="utf-8",
        )
        unpacked_ok = gates.returncode == compact.returncode == tests.returncode == 0

    artifacts = {path.name: {"sha256": sha256(path), "size_bytes": path.stat().st_size}
                 for path in (report, evidence, readme)}
    hashes = {
        "package": PACKAGE, "hash_algorithm": "sha256", "no_self_reference": True,
        "artifact_count": len(artifacts), "artifacts": artifacts,
        "unpacked_replay_pass": unpacked_ok,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    verified_count = 0
    mismatches = 0
    missing = 0
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
        "verified_count": verified_count, "expected_count": 3,
        "hash_mismatch_count": mismatches, "missing_count": missing,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    hashes_path = OUT_DIR / "FINAL_DELIVERABLE_HASHES.json"
    verify_path = OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json"
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    verify_path.write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
    manifest = OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json"
    manifest.write_text(json.dumps({
        "package": PACKAGE,
        "round_outcome": "BALANCED_PRE_GATE_FAIL",
        "files": [report.name, evidence.name, readme.name, hashes_path.name, verify_path.name],
    }, indent=2) + "\n", encoding="utf-8")
    outer = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_SUBMISSION.zip"
    if outer.exists():
        outer.unlink()
    with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in (report, evidence, readme, hashes_path, verify_path, manifest):
            archive.write(path, path.name)
    shutil.rmtree(staging)
    print(json.dumps({"status": verify["status"], "evidence": str(evidence), "outer": str(outer)}, indent=2))
    return 0 if unpacked_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
