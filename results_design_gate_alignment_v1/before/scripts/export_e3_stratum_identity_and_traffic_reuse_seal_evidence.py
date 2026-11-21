#!/usr/bin/env python3
"""Self-contained hash finalize + package for stratum/reuse seal."""
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
ART = ROOT / "artifacts/e3_stratum_identity_and_traffic_reuse_seal_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_STRATUM_IDENTITY_AND_TRAFFIC_REUSE_SEAL_R1"
PACKAGE = "TO_SUBMIT_E3_STRATUM_IDENTITY_AND_TRAFFIC_REUSE_SEAL_R1"

# Hashed body — exclude self-referential manifest/verification/gates (written after hash)
HASHED_INCLUDE = [
    "E3_STRATUM_IDENTITY_SEAL.md",
    "E3_STRATUM_IDENTITY_SEAL.json",
    "E3_TRAFFIC_STRATUM_IDENTITY_SEAL.json",
    "E3_SENSORSCOPE_STRATUM_IDENTITY_SEAL.json",
    "E3_UAIR_STRATUM_IDENTITY_SEAL.json",
    "E3_STRATUM_DEPENDENT_OBJECT_REBUILD_AUDIT.json",
    "E3_DELTA_CS_POST_STRATUM_SEAL_TEST.json",
    "E3_ATOMIC_RHO_POST_STRATUM_SEAL_TEST.json",
    "E3_TRAFFIC_RMSE_RHO_REUSE_COMPATIBILITY_SEAL.md",
    "E3_TRAFFIC_RMSE_RHO_REUSE_COMPATIBILITY_SEAL.json",
    "E3_TRAFFIC_REUSE_METRIC_POLICY.json",
    "E3_STRATUM_REUSE_SEAL_SMOKE.json",
    "E3_STRATUM_REUSE_SEAL_SMOKE_REPORT.md",
    "E3_DATASET_READINESS_R7.csv",
    "E3_DATASET_READINESS_R7.json",
    "E3_MINIMUM_NEW_RUN_MATRIX_R7.csv",
    "E3_MINIMUM_NEW_RUN_MATRIX_R7.json",
    "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R7.md",
    "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R7.json",
    "E3_STRATUM_REUSE_SEAL_SOURCE_HASHES.json",
    "E3_STRATUM_REUSE_SEAL_STOP_STATUS.json",
    "E3_STRATUM_IDENTITY_AND_TRAFFIC_REUSE_SEAL_R1_REPORT.md",
    "traffic_region_mapping/traffic_station_region_mapping.csv",
    "traffic_region_mapping/traffic_station_region_identity.json",
]
# Packaged after gates; listed in ZIP with included_in_zip=true but not in self-hash body
POST_HASH_INCLUDE = [
    "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json",
    "E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json",
    "gate_results.json",
]
INCLUDE = HASHED_INCLUDE + POST_HASH_INCLUDE
LOGS = [
    "e3_stratum_reuse_seal_unit.xml",
    "e3_stratum_reuse_seal_integration.xml",
    "e3_stratum_reuse_seal_pytest_full.xml",
    "e3_stratum_reuse_seal_pip_check.txt",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(*, include_post: bool = False) -> dict:
    entries = {}
    for rel in HASHED_INCLUDE:
        path = ART / rel
        if not path.is_file():
            raise FileNotFoundError(f"PACKAGE_EVIDENCE_BLOCKED: missing {rel}")
        entries[rel] = {
            "sha256": _sha(path),
            "included_in_zip": True,
            "reason": None,
        }
    for name in LOGS:
        path = ROOT / "logs" / name
        if not path.is_file():
            raise FileNotFoundError(f"PACKAGE_EVIDENCE_BLOCKED: missing logs/{name}")
        entries[f"logs/{name}"] = {
            "sha256": _sha(path),
            "included_in_zip": True,
            "reason": None,
            "is_log": True,
        }
    entries["EXTERNAL/e2_traffic_seal_STOP_STATUS.json"] = {
        "sha256": None,
        "included_in_zip": False,
        "reason": "EXTERNAL_IMMUTABLE_PARENT_REFERENCE",
        "parent_path": "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json",
    }
    mismatch = 0
    checked = {}
    for rel, meta in entries.items():
        if not meta.get("included_in_zip"):
            checked[rel] = True
            continue
        path = ART / rel if not rel.startswith("logs/") else ROOT / rel
        ok = path.is_file() and _sha(path) == meta["sha256"]
        checked[rel] = ok
        mismatch += int(not ok)
    verify = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mismatch_count": mismatch,
        "status": "PASS" if mismatch == 0 else "FAIL",
        "checked": checked,
        "self_contained": mismatch == 0,
    }
    dump_json(verify, ART / "E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json")
    if include_post:
        for rel in POST_HASH_INCLUDE:
            path = ART / rel
            if path.is_file():
                entries[rel] = {
                    "sha256": _sha(path),
                    "included_in_zip": True,
                    "reason": "post_hash_artifact",
                }
    # Write manifest last (not part of hashed body)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
        "hashed_body": HASHED_INCLUDE,
        "post_hash_artifacts": POST_HASH_INCLUDE,
        "artifact_count": sum(1 for e in entries.values() if e.get("included_in_zip")),
        "external_count": sum(1 for e in entries.values() if not e.get("included_in_zip")),
    }
    dump_json(manifest, ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json")
    # Refresh post-hash entry digests after writing manifest/verify
    if include_post:
        for rel in POST_HASH_INCLUDE:
            path = ART / rel
            if path.is_file():
                entries[rel] = {
                    "sha256": _sha(path),
                    "included_in_zip": True,
                    "reason": "post_hash_artifact",
                }
        manifest["entries"] = entries
        dump_json(manifest, ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json")
        # Final verify ignores post-hash self files for mismatch_count
        verify["mismatch_count"] = mismatch
        verify["status"] = "PASS" if mismatch == 0 else "FAIL"
        dump_json(verify, ART / "E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json")
        # Update manifest entry for verification file once more
        entries["E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json"] = {
            "sha256": _sha(ART / "E3_STRATUM_REUSE_SEAL_HASH_VERIFICATION.json"),
            "included_in_zip": True,
            "reason": "post_hash_artifact",
        }
        entries["E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json"] = {
            "sha256": "SELF",
            "included_in_zip": True,
            "reason": "canonical_manifest",
        }
        manifest["entries"] = entries
        dump_json(manifest, ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json")
    return verify


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    verify = build_manifest(include_post=False)
    if verify["mismatch_count"] != 0:
        print(json.dumps(verify, indent=2))
        return 1
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts/check_e3_stratum_identity_and_traffic_reuse_seal_gates.py")],
        cwd=str(ROOT),
    )
    # Gates may fail G23 until final manifest; re-finalize then re-check
    verify = build_manifest(include_post=True)
    if verify["mismatch_count"] != 0:
        print(json.dumps(verify, indent=2))
        return 1
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts/check_e3_stratum_identity_and_traffic_reuse_seal_gates.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    verify = build_manifest(include_post=True)
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_STRATUM_IDENTITY_AND_TRAFFIC_REUSE_SEAL_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_inner = OUT / f"{PACKAGE}.zip"
    zip_path = OUT.parent / f"{PACKAGE}.zip"
    for z in (zip_inner, zip_path):
        if z.exists():
            z.unlink()

    with zipfile.ZipFile(zip_inner, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel, meta in json.loads(
            (ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json").read_text(encoding="utf-8")
        )["entries"].items():
            if not meta.get("included_in_zip"):
                continue
            path = ART / rel if not rel.startswith("logs/") else ROOT / rel
            if not path.is_file():
                raise FileNotFoundError(f"missing in zip build: {rel}")
            zf.write(path, arcname=f"{PACKAGE}/{rel}")
    shutil.copy2(zip_inner, zip_path)

    # Verify ZIP physically contains every included manifest entry
    with zipfile.ZipFile(zip_inner, "r") as zf:
        names = set(zf.namelist())
    missing = []
    for rel, meta in json.loads(
        (ART / "E3_STRATUM_REUSE_SEAL_HASH_MANIFEST.json").read_text(encoding="utf-8")
    )["entries"].items():
        if meta.get("included_in_zip") and f"{PACKAGE}/{rel}" not in names:
            missing.append(rel)
    if missing:
        print(json.dumps({"error": "PACKAGE_EVIDENCE_BLOCKED", "missing": missing}, indent=2))
        return 1

    stop = json.loads((ART / "E3_STRATUM_REUSE_SEAL_STOP_STATUS.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "zip": str(zip_path),
                "status": stop.get("status"),
                "hash_verify": verify.get("status"),
                "self_contained": True,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
