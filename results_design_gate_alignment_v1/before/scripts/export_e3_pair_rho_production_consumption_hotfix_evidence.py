#!/usr/bin/env python3
"""Hash finalize + package E3 pair/rho production consumption hotfix."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_pair_rho_production_consumption_hotfix_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_PAIR_RHO_PRODUCTION_CONSUMPTION_HOTFIX_R1"
PACKAGE = "TO_SUBMIT_E3_PAIR_RHO_PRODUCTION_CONSUMPTION_HOTFIX_R1"
SKIP = {
    "E3_HOTFIX_HASH_MANIFEST.json",
    "E3_HOTFIX_HASH_VERIFICATION.json",
    "gate_results.json",
    "gate_diagnostics.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_hash_manifest() -> dict:
    files = {}
    for path in sorted(ART.rglob("*")):
        if not path.is_file() or path.name in SKIP or path.suffix == ".pt":
            continue
        # skip bulky fixture/eventtrace internals from manifest? include for integrity
        if "tmp_pobs" in path.parts:
            continue
        if "runner_smoke" in path.parts and path.suffix in {".pt", ".parquet"}:
            continue
        if "eventtrace_nd" in path.parts and path.suffix in {".parquet", ".pt"}:
            continue
        if "fixture_nd" in path.parts and path.suffix == ".parquet":
            continue
        files[path.relative_to(ART).as_posix()] = _sha(path)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "artifact_count": len(files),
        "excluded_from_hash": sorted(SKIP | {"*.pt", "tmp_pobs/**", "heavy binary smoke/eventtrace"}),
    }
    dump_json(manifest, ART / "E3_HOTFIX_HASH_MANIFEST.json")
    mismatch = 0
    checked = {}
    for rel, digest in files.items():
        ok = _sha(ART / rel) == digest
        checked[rel] = ok
        mismatch += int(not ok)
    verify = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mismatch_count": mismatch,
        "status": "PASS" if mismatch == 0 else "FAIL",
        "checked": checked,
    }
    dump_json(verify, ART / "E3_HOTFIX_HASH_VERIFICATION.json")
    return verify


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1
    rc = subprocess.call(
        [
            sys.executable,
            str(ROOT / "scripts/check_e3_pair_rho_production_consumption_hotfix_gates.py"),
        ],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_PAIR_RHO_PRODUCTION_CONSUMPTION_HOTFIX_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT.parent / f"{PACKAGE}.zip"
    if zip_path.exists():
        zip_path.unlink()
    # Also place under OUT/
    zip_inner = OUT / f"{PACKAGE}.zip"
    if zip_inner.exists():
        zip_inner.unlink()

    include_names = [
        "E3_PAIR_METRIC_NAME_AND_DEFINITION_AUDIT.md",
        "E3_PAIR_METRIC_NAME_AND_DEFINITION_AUDIT.json",
        "E3_STRUCTURAL_PAIR_METRIC_FINAL_DEFINITION.md",
        "E3_STRUCTURAL_PAIR_METRIC_FINAL_DEFINITION.json",
        "E3_NONSYMMETRIC_PAIR_METRIC_ANALYTICAL_TEST.json",
        "E3_RHO_GROUP_TO_UNIT_MAPPING_FIX.md",
        "E3_RHO_GROUP_TO_UNIT_MAPPING_FIX.json",
        "E3_PRODUCTION_RHO_ANALYTICAL_TEST.json",
        "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.md",
        "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.json",
        "E3_POBS_FIELD_USAGE_AUDIT.json",
        "E3_PIOPP_SEMANTIC_IDENTITY.md",
        "E3_PIOPP_SEMANTIC_IDENTITY.json",
        "E3_PRODUCTION_JOINT_PIOPP_PERTURBATION_TEST.json",
        "E3_MECHANISM_METRIC_APPLICABILITY_R2.csv",
        "E3_MECHANISM_METRIC_APPLICABILITY_R2.json",
        "E3_PRODUCTION_APPLICABILITY_ENFORCEMENT_TEST.json",
        "E3_HOTFIX_NONPERFORMANCE_SMOKE_REPORT.md",
        "E3_HOTFIX_NONPERFORMANCE_SMOKE.json",
        "E3_REAL_METRIC_OUTPUT_SCHEMA_V5.json",
        "E3_METHOD_READINESS_R5.csv",
        "E3_METHOD_READINESS_R5.json",
        "E3_DATASET_READINESS_R5.csv",
        "E3_DATASET_READINESS_R5.json",
        "E3_MINIMUM_NEW_RUN_MATRIX_R5.csv",
        "E3_MINIMUM_NEW_RUN_MATRIX_R5.json",
        "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R5.md",
        "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R5.json",
        "E3_HOTFIX_SOURCE_HASHES.json",
        "E3_HOTFIX_HASH_MANIFEST.json",
        "E3_HOTFIX_HASH_VERIFICATION.json",
        "E3_HOTFIX_STOP_STATUS.json",
        "gate_results.json",
        "E3_PAIR_RHO_PRODUCTION_CONSUMPTION_HOTFIX_R1_REPORT.md",
    ]
    logs = [
        ROOT / "logs/e3_hotfix_unit.xml",
        ROOT / "logs/e3_hotfix_integration.xml",
        ROOT / "logs/e3_hotfix_pytest_full.xml",
        ROOT / "logs/e3_hotfix_pip_check.txt",
    ]

    with zipfile.ZipFile(zip_inner, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in include_names:
            path = ART / name
            if path.is_file():
                zf.write(path, arcname=f"{PACKAGE}/{name}")
        for log in logs:
            if log.is_file():
                zf.write(log, arcname=f"{PACKAGE}/logs/{log.name}")
    shutil.copy2(zip_inner, zip_path)
    stop = json.loads((ART / "E3_HOTFIX_STOP_STATUS.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "zip": str(zip_path),
                "status": stop.get("status"),
                "hash_verify": verify.get("status"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
