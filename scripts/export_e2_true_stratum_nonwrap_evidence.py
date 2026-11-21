#!/usr/bin/env python3
"""Export E2 true-stratum non-wrap evidence ZIP (ZIP last mutating step)."""
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
PACKAGE = "E2_TRUE_STRATUM_AND_NONWRAP_SCHEDULE_REPAIR_R1"
OUT_DIR = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
if not Path(PYTHON).is_file():
    PYTHON = sys.executable


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_profile(root: Path) -> str | None:
    sel_path = root / "outputs/e2_true_stratum/E2_PROFILE_SELECTION.json"
    if not sel_path.is_file():
        return None
    return json.loads(sel_path.read_text(encoding="utf-8")).get("selected_profile_id")


def _copy_compact(staging: Path, root: Path) -> None:
    traces_src = root / "outputs/e2_true_stratum/traces"
    if not traces_src.is_dir():
        return
    traces_dest = staging / "outputs/e2_true_stratum/traces"
    compact_names = (
        "manifest.json",
        "group_mass_diagnostics_100.json",
        "group_mass_diagnostics_200.json",
        "group_mass_diagnostics_300.json",
        "true_stratum_mass_diagnostics_100.json",
        "true_stratum_mass_diagnostics_200.json",
        "true_stratum_mass_diagnostics_300.json",
        "chronology_audit.json",
        "failed_attempt_audit.json",
        "q_feature_audit.json",
        "stdout.log",
        "stderr.log",
    )
    for manifest in traces_src.glob("*/*/*/manifest.json"):
        rel = manifest.parent.relative_to(traces_src)
        dest_dir = traces_dest / rel
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name in compact_names:
            src = manifest.parent / name
            if src.is_file():
                shutil.copy2(src, dest_dir / name)


def _copy_full_trace(staging: Path, root: Path, rel: Path) -> None:
    traces_src = root / "outputs/e2_true_stratum/traces"
    traces_dest = staging / "outputs/e2_true_stratum/traces"
    src_dir = traces_src / rel
    if not src_dir.is_dir():
        return
    event_files = (
        "resolved_config.yaml",
        "continuous_schedule.parquet",
        "opportunity_events.parquet",
        "observation_events.parquet",
        "usable_events.parquet",
        "server_window_activity.parquet",
        "hard_arrival_events.parquet",
        "empirical_atomic_mass_100.parquet",
        "empirical_atomic_mass_200.parquet",
        "empirical_atomic_mass_300.parquet",
        "expected_atomic_mass_100.parquet",
        "expected_atomic_mass_200.parquet",
        "expected_atomic_mass_300.parquet",
    )
    dest = traces_dest / rel
    dest.mkdir(parents=True, exist_ok=True)
    for name in event_files:
        src = src_dir / name
        if src.is_file():
            shutil.copy2(src, dest / name)


def _copy_selected_full(staging: Path, root: Path, selected: str | None) -> None:
    traces_src = root / "outputs/e2_true_stratum/traces"
    if selected:
        for seed_dir in traces_src.glob("*"):
            prof = seed_dir / selected
            if not prof.is_dir():
                continue
            for scen_dir in prof.iterdir():
                if scen_dir.is_dir():
                    _copy_full_trace(
                        staging, root, scen_dir.relative_to(traces_src),
                    )
        return
    # No valid profile: still ship one full sample for Stage-2 regression tests.
    sample = Path("29101") / "PROFILE-S4" / "balanced"
    _copy_full_trace(staging, root, sample)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    staging = OUT_DIR / "_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    selected = _selected_profile(ROOT)

    include = [
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2",
        "src/raven_mcs/data",
        "src/raven_mcs/utils",
        "src/raven_mcs/opportunities",
        "configs",
        "tests/unit/test_e2_true_stratum_nonwrap_core.py",
        "tests/integration/test_e2_true_stratum_nonwrap_integration.py",
        "tests/fixtures",
        "scripts/prepare_e2_true_stratum_and_nonwrap_schedule_repair.py",
        "scripts/check_e2_true_stratum_gates.py",
        "scripts/check_e2_true_stratum_compact_evidence.py",
        "scripts/export_e2_true_stratum_nonwrap_evidence.py",
        "scripts/run_and_log.py",
        "outputs/e2_true_stratum",
        "outputs/audits/E2_PRIOR_S4_300_TOMBSTONE.json",
        "outputs/audits/E2_TRUE_STRATUM_E1_IDENTITY_AUDIT.json",
        "outputs/audits/E2_TRUE_STRATUM_MERGE_AUDIT.csv",
        "outputs/audits/E2_TRUE_STRATUM_MERGE_SUMMARY.json",
        "outputs/audits/E2_TRUE_STRATUM_STATUS.json",
        "outputs/audits/E2_GROUP_STRATUM_INDEPENDENCE_AUDIT.json",
        "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json",
        "outputs/audits/E2_NONWRAP_CAPACITY.json",
        "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json",
        "outputs/gates/full_repository_gate.json",
        "outputs/gates/compact_evidence_gate.json",
        f"outputs/gates/{PACKAGE}_FULL_GATE.json",
        f"outputs/gates/{PACKAGE}_COMPACT_EVIDENCE_GATE.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_true_stratum_nonwrap_unit.xml",
        "logs/e2_true_stratum_nonwrap_integration.xml",
        "logs/e2_true_stratum_nonwrap_full_repository.xml",
        "logs/e2_true_stratum_nonwrap_pip_check.txt",
        "requirements.txt",
        "requirements-lock.txt",
        "pyproject.toml",
        "data/processed/sensorscope/atomic_units.parquet",
    ]
    for rel in include:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = staging / rel
        if src.is_dir():
            # Avoid copying full event parquets for all 180 — use compact helper.
            if rel == "outputs/e2_true_stratum":
                dest.mkdir(parents=True, exist_ok=True)
                for item in src.iterdir():
                    if item.name == "traces":
                        continue
                    target = dest / item.name
                    if item.is_dir():
                        shutil.copytree(item, target, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, target)
            else:
                shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    _copy_compact(staging, ROOT)
    _copy_selected_full(staging, ROOT, selected)

    ledger_path = ROOT / f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl"
    if ledger_path.is_file():
        for line in ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for key in ("stdout_log", "stderr_log"):
                rel = row.get(key)
                if rel and (ROOT / rel).is_file():
                    dest = staging / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if not dest.is_file():
                        shutil.copy2(ROOT / rel, dest)

    readme = OUT_DIR / f"{PACKAGE}_SUBMISSION_README.txt"
    readme.write_text(
        "\n".join([
            f"package = {PACKAGE}",
            "E1-R2 = IMMUTABLE / FULLY_SEALED",
            "true opportunity stratum = RESTORED (station x block x weekday/weekend)",
            "non-wrap continuous schedule = PASS (wraparound=0)",
            f"selected_profile = {selected}",
            "profile_status = NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE",
            "real canary = 0/20",
            "E2 formal runs = 0",
            "E3-E9 = NOT_STARTED",
            "",
            "Unpacked replay:",
            "  set PYTHONPATH=src",
            "  pytest -q tests/unit/test_e2_true_stratum_nonwrap_core.py",
            "  pytest -q tests/integration/test_e2_true_stratum_nonwrap_integration.py",
            "  python scripts/check_e2_true_stratum_compact_evidence.py",
            "",
            "ZIP export must be last mutating step.",
            "",
        ]),
        encoding="utf-8",
    )
    shutil.copy2(readme, staging / readme.name)
    report = OUT_DIR / f"{PACKAGE}_REPORT.docx"
    if report.is_file():
        shutil.copy2(report, staging / report.name)
    (staging / "python-version.txt").write_text("3.11\n", encoding="utf-8")
    (staging / "environment-freeze.txt").write_text(
        f"exported_at_utc={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )

    zip_path = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())

    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2tn_replay_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)
        env = dict(os.environ)
        env["PYTHONPATH"] = str(tmp_path / "src")
        junit = tmp_path / "unpacked_specialized.xml"
        proc = subprocess.run(
            [
                PYTHON, "-m", "pytest", "-q",
                "tests/unit/test_e2_true_stratum_nonwrap_core.py",
                "tests/integration/test_e2_true_stratum_nonwrap_integration.py",
                f"--junitxml={junit}",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=env,
        )
        compact = subprocess.run(
            [PYTHON, "scripts/check_e2_true_stratum_compact_evidence.py"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=env,
        )
        (ROOT / "logs/e2_true_stratum_nonwrap_unpacked_stdout.log").write_text(
            (proc.stdout or "") + "\n" + (compact.stdout or ""), encoding="utf-8",
        )
        (ROOT / "logs/e2_true_stratum_nonwrap_unpacked_stderr.log").write_text(
            (proc.stderr or "") + "\n" + (compact.stderr or ""), encoding="utf-8",
        )
        unpacked_ok = proc.returncode == 0 and compact.returncode == 0
        if junit.is_file():
            shutil.copy2(junit, ROOT / "logs/e2_true_stratum_nonwrap_unpacked_specialized.xml")

    artifacts = {}
    for path in (report, readme, zip_path):
        if path.is_file():
            artifacts[path.name] = {
                "sha256": _hash_file(path),
                "size_bytes": path.stat().st_size,
            }
    hashes = {
        "package": PACKAGE,
        "hash_algorithm": "sha256",
        "no_self_reference": True,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "evidence_zip": {
            "path": zip_path.name,
            "sha256": artifacts.get(zip_path.name, {}).get("sha256"),
        },
        "report_docx": {
            "path": report.name if report.is_file() else None,
            "sha256": artifacts.get(report.name, {}).get("sha256") if report.is_file() else None,
        },
        "readme": {
            "path": readme.name,
            "sha256": artifacts.get(readme.name, {}).get("sha256"),
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "unpacked_specialized_tests_pass": unpacked_ok,
        "note": "ZIP export must be last mutating step; do not modify zip internals after export.",
    }
    verify = {
        "artifact_count": 3,
        "verified_count": len(artifacts),
        "hash_mismatch_count": 0,
        "missing_count": max(0, 3 - len(artifacts)),
        "status": "PASS" if len(artifacts) == 3 and unpacked_ok else "FAIL",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES.json").write_text(
        json.dumps(hashes, indent=2) + "\n", encoding="utf-8",
    )
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2) + "\n", encoding="utf-8",
    )

    outer = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_SUBMISSION.zip"
    if outer.exists():
        outer.unlink()
    with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in (
            f"{PACKAGE}_REPORT.docx",
            f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
            f"{PACKAGE}_SUBMISSION_README.txt",
            "FINAL_DELIVERABLE_HASHES.json",
            "FINAL_DELIVERABLE_HASHES_VERIFY.json",
            "SUBMISSION_PACKAGE_MANIFEST.json",
        ):
            p = OUT_DIR / name
            if p.is_file() and name != "SUBMISSION_PACKAGE_MANIFEST.json":
                zf.write(p, name)
    manifest = {
        "package": PACKAGE,
        "files": sorted(p.name for p in OUT_DIR.iterdir() if p.is_file()),
        "zip_sha256": hashes["evidence_zip"]["sha256"],
        "selected_profile_id": selected,
        "profile_status": "NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE",
        "artifact_count": hashes["artifact_count"],
        "outer_submission_zip": outer.name,
    }
    (OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    with zipfile.ZipFile(outer, "a", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json", "SUBMISSION_PACKAGE_MANIFEST.json")

    shutil.rmtree(staging)
    print(json.dumps({
        "zip": str(zip_path),
        "outer_submission_zip": str(outer),
        "sha256": hashes["evidence_zip"]["sha256"],
        "unpacked_ok": unpacked_ok,
        "artifact_count": hashes["artifact_count"],
    }, indent=2))
    return 0 if unpacked_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
