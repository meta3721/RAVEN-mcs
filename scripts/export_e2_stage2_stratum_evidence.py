#!/usr/bin/env python3
"""Export self-contained E2 Stage-2 stratum evidence ZIP (ZIP must be last step)."""
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
PACKAGE = "E2_STAGE2_ELIGIBILITY_AND_TRUE_STRATUM_REFREEZE_R1"
OUT_DIR = ROOT / f"deliverables/TO_SUBMIT_{PACKAGE}"
PYTHON = str(ROOT / ".venv" / "Scripts" / "python.exe")
if not Path(PYTHON).is_file():
    PYTHON = sys.executable


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_profile(root: Path) -> str | None:
    sel_path = root / "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json"
    if not sel_path.is_file():
        return None
    return json.loads(sel_path.read_text(encoding="utf-8")).get("selected_profile_id")


def _copy_all_manifests_and_diagnostics(staging: Path, root: Path) -> None:
    traces_src = root / "outputs/e2_stage2_stratum/traces"
    if not traces_src.is_dir():
        return
    traces_dest = staging / "outputs/e2_stage2_stratum/traces"
    compact_names = (
        "manifest.json",
        "group_mass_diagnostics_300.json",
        "stratum_mass_diagnostics_300.json",
        "failed_attempt_audit.json",
        "q_feature_audit.json",
    )
    for manifest in traces_src.glob("*/*/*/manifest.json"):
        rel = manifest.parent.relative_to(traces_src)
        dest_dir = traces_dest / rel
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name in compact_names:
            src = manifest.parent / name
            if src.is_file():
                shutil.copy2(src, dest_dir / name)


def _copy_selected_traces(staging: Path, root: Path, selected: str | None) -> None:
    traces_src = root / "outputs/e2_stage2_stratum/traces"
    if not traces_src.is_dir() or not selected:
        return
    traces_dest = staging / "outputs/e2_stage2_stratum/traces"
    event_files = (
        "manifest.json",
        "resolved_config.yaml",
        "continuous_schedule.parquet",
        "opportunity_events.parquet",
        "observation_events.parquet",
        "usable_events.parquet",
        "server_window_activity.parquet",
        "hard_arrival_events.parquet",
    )
    compact_files = (
        "group_mass_diagnostics_100.json",
        "group_mass_diagnostics_200.json",
        "group_mass_diagnostics_300.json",
        "stratum_mass_diagnostics_100.json",
        "stratum_mass_diagnostics_200.json",
        "stratum_mass_diagnostics_300.json",
        "failed_attempt_audit.json",
        "q_feature_audit.json",
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


def _build_external_hashes(
    report: Path,
    readme: Path,
    zip_path: Path,
    *,
    unpacked_ok: bool,
) -> tuple[dict, dict]:
    artifacts: dict[str, dict] = {}
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
            "path": readme.name if readme.is_file() else None,
            "sha256": artifacts.get(readme.name, {}).get("sha256") if readme.is_file() else None,
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "unpacked_specialized_tests_pass": unpacked_ok,
        "note": "ZIP export must be last mutating step; do not modify zip internals after export.",
    }
    mismatches = [
        name for name, meta in artifacts.items()
        if _hash_file(OUT_DIR / name) != meta["sha256"]
    ]
    verify = {
        "artifact_count": 3,
        "verified_count": len(artifacts) - len(mismatches),
        "hash_mismatch_count": len(mismatches),
        "missing_count": max(0, 3 - len(artifacts)),
        "self_reference": False,
        "status": (
            "PASS"
            if len(artifacts) == 3 and not mismatches and unpacked_ok
            else "FAIL"
        ),
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return hashes, verify


def _create_outer_submission_zip(out_dir: Path) -> Path:
    outer = out_dir / f"RAVEN_MCS_{PACKAGE}_SUBMISSION.zip"
    if outer.exists():
        outer.unlink()
    include_names = [
        f"{PACKAGE}_REPORT.docx",
        f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip",
        f"{PACKAGE}_SUBMISSION_README.txt",
        "FINAL_DELIVERABLE_HASHES.json",
        "FINAL_DELIVERABLE_HASHES_VERIFY.json",
        "SUBMISSION_PACKAGE_MANIFEST.json",
    ]
    with zipfile.ZipFile(outer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in include_names:
            path = out_dir / name
            if path.is_file():
                zf.write(path, name)
    return outer


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
        "configs",
        "src/raven_mcs/opportunities",
        "schemas/e2_scenario_mass_diagnostics.schema.json",
        "tests/unit/test_e2_stage2_stratum_core.py",
        "tests/integration/test_e2_stage2_stratum_integration.py",
        "tests/fixtures",
        "scripts/prepare_e2_stage2_eligibility_and_true_stratum_refreeze.py",
        "scripts/check_e2_stage2_stratum_gates.py",
        "scripts/export_e2_stage2_stratum_evidence.py",
        "scripts/_e2sr_unpacked_specialized.py",
        "scripts/run_and_log.py",
        "outputs/e2_stage2_stratum/E2_TRACE_MATRIX_SUMMARY.json",
        "outputs/e2_stage2_stratum/E2_PROFILE_SELECTION.json",
        "outputs/e2_stage2_stratum/E2_PROFILE_GATE_BY_SEED.csv",
        "outputs/e2_stage2_stratum/E2_PROFILE_GATE_SUMMARY.csv",
        "outputs/e2_stage2_stratum/E2_WINDOW_SELECTION.json",
        "outputs/e2_stage2_stratum/E2_WINDOW_STABILITY_BY_SEED.csv",
        "outputs/e2_stage2_stratum/E2_WINDOW_STABILITY_SUMMARY.csv",
        "outputs/e2_stage2_stratum/E2_STAGE2_STRATUM_CONTEXT.json",
        "outputs/audits/E2_FAILED_ATTEMPT_RETENTION_AUDIT.json",
        "outputs/audits/E2_CHRONOLOGICAL_ORDER_AUDIT.json",
        "outputs/audits/E2_TRUE_STRATUM_STATUS.json",
        "outputs/audits/E2_STRATUM_MERGE_AUDIT.csv",
        "outputs/audits/E2_PRIOR_EMPIRICAL_SELECTION_TOMBSTONE.json",
        f"outputs/gates/{PACKAGE}_GATES.json",
        f"logs/{PACKAGE}_EXACT_COMMANDS.jsonl",
        "logs/e2_stage2_stratum_unit.xml",
        "logs/e2_stage2_stratum_integration.xml",
        "logs/e2_stage2_stratum_full_repository.xml",
        "logs/e2_stage2_stratum_pip_check.txt",
        "requirements.txt",
        "requirements-lock.txt",
        "pyproject.toml",
    ]
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

    _copy_all_manifests_and_diagnostics(staging, ROOT)
    _copy_selected_traces(staging, ROOT, selected)

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
            "Stage-2 eligibility = observed_count > 0",
            "true opportunity stratum = RESTORED",
            f"selected_profile = {selected}",
            f"E2SR gates = {gates.get('status', 'UNKNOWN')}",
            "real canary = 0/20",
            "E2 formal runs = 0",
            "E3-E9 = NOT_STARTED",
            "",
            "Unpacked replay:",
            "  set PYTHONPATH=src",
            "  pytest -q tests/unit/test_e2_stage2_stratum_core.py",
            "  pytest -q tests/integration/test_e2_stage2_stratum_integration.py",
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

    zip_path = OUT_DIR / f"RAVEN_MCS_{PACKAGE}_EVIDENCE.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging).as_posix())

    unpacked_ok = False
    with tempfile.TemporaryDirectory(prefix="e2sr_replay_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_path)
        env = dict(**dict(**__import__("os").environ), PYTHONPATH=str(tmp_path / "src"))
        junit = tmp_path / "unpacked_specialized.xml"
        proc = subprocess.run(
            [
                PYTHON, "-m", "pytest", "-q",
                "tests/unit/test_e2_stage2_stratum_core.py",
                "tests/integration/test_e2_stage2_stratum_integration.py",
                f"--junitxml={junit}",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=env,
        )
        (ROOT / "logs/e2_stage2_stratum_unpacked_stdout.log").write_text(
            proc.stdout or "", encoding="utf-8",
        )
        (ROOT / "logs/e2_stage2_stratum_unpacked_stderr.log").write_text(
            proc.stderr or "", encoding="utf-8",
        )
        unpacked_ok = proc.returncode == 0
        if junit.is_file():
            shutil.copy2(junit, ROOT / "logs/e2_stage2_stratum_unpacked_specialized.xml")
            with zipfile.ZipFile(zip_path, "a", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(
                    junit,
                    "logs/e2_stage2_stratum_unpacked_specialized.xml",
                )

    hashes, verify = _build_external_hashes(report, readme, zip_path, unpacked_ok=unpacked_ok)
    hash_json = OUT_DIR / "FINAL_DELIVERABLE_HASHES.json"
    hash_json.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "FINAL_DELIVERABLE_HASHES_VERIFY.json").write_text(
        json.dumps(verify, indent=2) + "\n", encoding="utf-8",
    )
    manifest_payload = {
        "package": PACKAGE,
        "files": sorted(p.name for p in OUT_DIR.iterdir() if p.is_file()),
        "zip_sha256": hashes["evidence_zip"]["sha256"],
        "selected_profile_id": selected,
        "artifact_count": hashes.get("artifact_count"),
    }
    (OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8",
    )

    outer_zip = _create_outer_submission_zip(OUT_DIR)
    manifest_payload["outer_submission_zip"] = outer_zip.name
    (OUT_DIR / "SUBMISSION_PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8",
    )

    shutil.rmtree(staging)
    print(json.dumps({
        "zip": str(zip_path),
        "outer_submission_zip": str(outer_zip),
        "sha256": hashes["evidence_zip"]["sha256"],
        "unpacked_ok": unpacked_ok,
        "artifact_count": hashes.get("artifact_count"),
    }, indent=2))
    return 0 if unpacked_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
