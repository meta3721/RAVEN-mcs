#!/usr/bin/env python3
"""Hash finalize + package E3 Delta_c_s + atomic rho final hotfix."""
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
ART = ROOT / "artifacts/e3_delta_cs_atomic_rho_final_hotfix_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_DELTA_CS_AND_ATOMIC_RHO_FINAL_HOTFIX_R1"
PACKAGE = "TO_SUBMIT_E3_DELTA_CS_AND_ATOMIC_RHO_FINAL_HOTFIX_R1"
SKIP = {
    "E3_DELTA_CS_ATOMIC_RHO_HASH_MANIFEST.json",
    "E3_DELTA_CS_ATOMIC_RHO_HASH_VERIFICATION.json",
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
        if any(x in path.parts for x in ("tmp_pobs", "runner_smoke", "eventtrace_nd", "fixture_nd", "fixture_probe")):
            if path.suffix in {".parquet", ".pt"} or "training_eventtrace" in path.parts:
                continue
        files[path.relative_to(ART).as_posix()] = _sha(path)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "artifact_count": len(files),
    }
    dump_json(manifest, ART / "E3_DELTA_CS_ATOMIC_RHO_HASH_MANIFEST.json")
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
    dump_json(verify, ART / "E3_DELTA_CS_ATOMIC_RHO_HASH_VERIFICATION.json")
    return verify


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts/check_e3_delta_cs_atomic_rho_final_hotfix_gates.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_DELTA_CS_AND_ATOMIC_RHO_FINAL_HOTFIX_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_inner = OUT / f"{PACKAGE}.zip"
    zip_path = OUT.parent / f"{PACKAGE}.zip"
    for z in (zip_inner, zip_path):
        if z.exists():
            z.unlink()

    include_names = [
        "E3_OPPORTUNITY_STRATUM_FINAL_DEFINITION.md",
        "E3_OPPORTUNITY_STRATUM_FINAL_DEFINITION.json",
        "E3_DELTA_CS_EXACT_DEFINITION.md",
        "E3_DELTA_CS_EXACT_DEFINITION.json",
        "E3_DELTA_CS_TARGET_MASS_AUDIT.md",
        "E3_DELTA_CS_TARGET_MASS_AUDIT.json",
        "E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.csv",
        "E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.json",
        "E3_DELTA_CS_STATE_SCHEMA_V6.json",
        "E3_DELTA_CS_NONSYMMETRIC_ANALYTICAL_TEST.json",
        "E3_DELTA_CS_FIELD_USAGE_AUDIT.json",
        "E3_ATOMIC_RHO_FACTOR_REGISTRY.json",
        "E3_ATOMIC_RHO_SCHEMA_V2.json",
        "E3_ATOMIC_RHO_WITHIN_GROUP_HETEROGENEITY_TEST.json",
        "E3_ATOMIC_RMSE_RHO_ANALYTICAL_TEST.json",
        "E3_RHO_FIELD_USAGE_AUDIT.json",
        "E3_TRAFFIC_ATOMIC_RHO_REUSE_AUDIT.md",
        "E3_TRAFFIC_ATOMIC_RHO_REUSE_AUDIT.json",
        "E3_PRODUCTION_METRIC_OBJECT_SEPARATION_AUDIT.json",
        "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE_REPORT.md",
        "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE.json",
        "E3_REAL_METRIC_OUTPUT_SCHEMA_V6.json",
        "E3_METHOD_READINESS_R6.csv",
        "E3_METHOD_READINESS_R6.json",
        "E3_DATASET_READINESS_R6.csv",
        "E3_DATASET_READINESS_R6.json",
        "E3_MINIMUM_NEW_RUN_MATRIX_R6.csv",
        "E3_MINIMUM_NEW_RUN_MATRIX_R6.json",
        "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R6.md",
        "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R6.json",
        "E3_DELTA_CS_ATOMIC_RHO_SOURCE_HASHES.json",
        "E3_DELTA_CS_ATOMIC_RHO_HASH_MANIFEST.json",
        "E3_DELTA_CS_ATOMIC_RHO_HASH_VERIFICATION.json",
        "E3_DELTA_CS_ATOMIC_RHO_STOP_STATUS.json",
        "gate_results.json",
        "E3_DELTA_CS_AND_ATOMIC_RHO_FINAL_HOTFIX_R1_REPORT.md",
    ]
    logs = [
        ROOT / "logs/e3_delta_cs_rho_unit.xml",
        ROOT / "logs/e3_delta_cs_rho_integration.xml",
        ROOT / "logs/e3_delta_cs_rho_pytest_full.xml",
        ROOT / "logs/e3_delta_cs_rho_pip_check.txt",
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
    stop = json.loads((ART / "E3_DELTA_CS_ATOMIC_RHO_STOP_STATUS.json").read_text(encoding="utf-8"))
    print(json.dumps({"zip": str(zip_path), "status": stop.get("status"), "hash_verify": verify.get("status")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
