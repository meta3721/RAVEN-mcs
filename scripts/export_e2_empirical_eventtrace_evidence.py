#!/usr/bin/env python3
"""Export self-contained E2 empirical EventTrace evidence ZIP (ZIP must be last step)."""
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
PACKAGE = "E2_EMPIRICAL_EVENTTRACE_AND_PROFILE_REFREEZE_R1"
OUT_DIR = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
if not Path(PYTHON).is_file():
    PYTHON = sys.executable


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_profile(root: Path) -> str | None:
    sel_path = root / "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json"
    if not sel_path.is_file():
        return None
    return json.loads(sel_path.read_text(encoding="utf-8")).get("selected_profile_id")


def _copy_selected_traces(staging: Path, root: Path, selected: str | None) -> None:
    """Copy selected-profile manifests, events, and compact diagnostics."""
    traces_src = root / "outputs/e2_empirical/traces"
    if not traces_src.is_dir() or not selected:
        return
    traces_dest = staging / "outputs/e2_empirical/traces"
    event_files = (
        "manifest.json",
        "resolved_config.yaml",
        "continuous_schedule.parquet",
        "opportunity_events.parquet",
        "observation_events.parquet",
        "usable_events.parquet",
        "hard_arrival_events.parquet",
    )
    compact_files = (
        "group_mass_diagnostics_100.json",
        "group_mass_diagnostics_200.json",
        "group_mass_diagnostics_300.json",
        "stratum_mass_diagnostics_100.json",
        "stratum_mass_diagnostics_200.json",
        "stratum_mass_diagnostics_300.json",
        "stdout.log",
        "stderr.log",
    )
    for seed_dir in traces_src.glob("*"):
        prof_dir = seed_dir / selected
        if not prof_dir.is_dir():
            continue
        for scen_dir in prof_dir.iterdir():
            if not scen_dir.is_dir():
                continue
            rel = scen_dir.relative_to(traces_src)
            dest = traces_dest / rel
            dest.mkdir(parents=True, exist_ok=True)
            for name in (*event_files, *compact_files):
                src = scen_dir / name
                if src.is_file():
                    shutil.copy2(src, dest / name)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    staging = OUT_DIR / "_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    selected = _selected_profile(ROOT)
    gates_path = ROOT / f"outputs/gates/{PACKAGE}_GATES.json"
    gates = json.loads(gates_path.read_text(encoding="utf-8")) if gates_path.is_file() else {}

    include = [
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2",
        "src/raven_mcs/data",
        "src/raven_mcs/utils",
        "configs/frozen/e2_empirical",
        "configs/frozen/e2_numeric",
        "configs/frozen/e1_sensorscope_clients.yaml",
        "configs/e2_numeric",
        "configs/e2_entry/seed_registry_candidate.yaml",
        "schemas/e2_scenario_mass_diagnostics.schema.json",
        "tests/unit/test_e2_empirical_eventtrace_core.py",
        "tests/integration/test_e2_empirical_eventtrace_integration.py",
        "tests/fixtures",
        "scripts/prepare_e2_empirical_eventtrace_and_profile_refreeze.py",
        "scripts/check_e2_empirical_eventtrace_gates.py",
        "scripts/export_e2_empirical_eventtrace_evidence.py",
        "scripts/run_and_log.py",
        "outputs/e2_empirical/E2_EMPIRICAL_TRACE_MATRIX_SUMMARY.json",
        "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_SELECTION.json",
        "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_GATE_BY_SEED.csv",
        "outputs/e2_empirical/E2_EMPIRICAL_PROFILE_GATE_SUMMARY.csv",
        "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_LENGTH_SELECTION.json",
        "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_STABILITY_BY_SEED.csv",
        "outputs/e2_empirical/E2_EMPIRICAL_WINDOW_STABILITY_SUMMARY.csv",
        "outputs/e2_empirical/E2_EMPIRICAL_CONTEXT.json",
        "outputs/e2_empirical/E2_EXPECTED_HARD_EMPIRICAL_MASS_AUDIT.csv",
        "outputs/e2_empirical/E2_RISK_VISIBILITY_AUDIT.csv",
        "outputs/audits/E2_300_WINDOW_SCHEDULE_NONREPETITION_AUDIT.json",
        "outputs/audits/E2_OPPORTUNITY_RISKSET_DIFFERENCE_AUDIT.json",
        "outputs/audits/E2_INVALID_PRIOR_SELECTION_TOMBSTONE.json",
        "outputs/audits/E2_STRENGTH_PROFILE_REGISTRY_AUDIT.json",
        "outputs/audits/E2_SCENARIO_DIRECTION_REGISTRY_AUDIT.json",
        "outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.json",
        "outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.md",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_empirical_eventtrace_unit.xml",
        "logs/e2_empirical_eventtrace_integration.xml",
        "logs/e2_empirical_eventtrace_full_repository.xml",
        "logs/e2_empirical_eventtrace_pip_check.txt",
        "requirements.txt",
        "requirements-lock.txt",
        "pyproject.toml",
    ]
    # Minimal processed data needed for unpacked pytest replay.
    data_paths = [
        "data/processed/sensorscope/atomic_units.parquet",
        "configs/frozen/e1_pi_target_manifest.json",
    ]
    include.extend(data_paths)

    for rel in include:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = staging / rel
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    _copy_selected_traces(staging, ROOT, selected)

    # Include ledger stdout/stderr artifacts.
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
            "E2 hard EventTrace generator = PASS (when gates PASS)",
            f"selected_profile = {selected}",
            f"E2EE gates = {gates.get('status', 'UNKNOWN')}",
            "real canary = 0/20",
            "E2 formal runs = 0",
            "E3-E9 = NOT_STARTED",
            "",
            "Unpacked replay:",
            "  set PYTHONPATH=src",
            "  pytest -q tests/unit/test_e2_empirical_eventtrace_core.py",
            "  pytest -q tests/integration/test_e2_empirical_eventtrace_integration.py",
            "  pip check",
            "",
            "ZIP export must be last mutating step; do not modify zip internals after export.",
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
        "\n".join([
            f"exported_at_utc={datetime.now(timezone.utc).isoformat()}",
            f"python={PYTHON}",
            "note=ZIP export must be last mutating step",
        ]) + "\n",
        encoding="utf-8",
    )
    if (ROOT / "requirements-lock.txt").is_file():
        shutil.copy2(ROOT / "requirements-lock.txt", staging / "requirements-lock.txt")

    # ZIP creation is the last mutating step before external hash files only.
    zip_path = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())

    # Independent unpack replay of specialized tests.
    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2ee_replay_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)
        env = dict(**dict(**__import__("os").environ), PYTHONPATH=str(tmp_path / "src"))
        junit = tmp_path / "unpacked_specialized.xml"
        proc = subprocess.run(
            [
                PYTHON, "-m", "pytest", "-q",
                "tests/unit/test_e2_empirical_eventtrace_core.py",
                "tests/integration/test_e2_empirical_eventtrace_integration.py",
                f"--junitxml={junit}",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=env,
        )
        (ROOT / "logs/e2_empirical_eventtrace_unpacked_stdout.log").write_text(
            proc.stdout or "", encoding="utf-8",
        )
        (ROOT / "logs/e2_empirical_eventtrace_unpacked_stderr.log").write_text(
            proc.stderr or "", encoding="utf-8",
        )
        unpacked_ok = proc.returncode == 0
        if junit.is_file():
            shutil.copy2(junit, ROOT / "logs/e2_empirical_eventtrace_unpacked_specialized.xml")
            with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(
                    junit,
                    "logs/e2_empirical_eventtrace_unpacked_specialized.xml",
                )

    hashes = {
        "evidence_zip": {
            "path": zip_path.name,
            "sha256": _hash_file(zip_path),
        },
        "report_docx": {
            "path": report.name if report.is_file() else None,
            "sha256": _hash_file(report) if report.is_file() else None,
        },
        "readme": {
            "path": readme.name,
            "sha256": _hash_file(readme),
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "unpacked_specialized_tests_pass": unpacked_ok,
        "note": "ZIP export must be last mutating step; do not modify zip internals after export.",
    }
    hash_json = OUT_DIR / "FINAL_DELIVERABLE_HASHES.json"
    hash_json.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    verify = {
        "evidence_zip_sha256_matches": _hash_file(zip_path) == hashes["evidence_zip"]["sha256"],
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2) + "\n", encoding="utf-8",
    )
    (OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json").write_text(
        json.dumps({
            "package": PACKAGE,
            "files": sorted(p.name for p in OUT_DIR.iterdir() if p.is_file()),
            "zip_sha256": hashes["evidence_zip"]["sha256"],
            "selected_profile_id": selected,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.rmtree(staging)
    print(json.dumps({
        "zip": str(zip_path),
        "sha256": hashes["evidence_zip"]["sha256"],
        "unpacked_ok": unpacked_ok,
    }, indent=2))
    return 0 if unpacked_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
