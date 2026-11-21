#!/usr/bin/env python3
"""Export final numerical-tolerance claim-seal package."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1"
PACKAGE = "TO_SUBMIT_E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = ART / "E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_REPORT.md"
    OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    zip_path = OUT / f"{PACKAGE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and path.suffix != ".pt":
                zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        for rel in [
            "scripts/prepare_e2_traffic_numerical_tolerance_and_final_claim_seal.py",
            "scripts/validate_e2_claim_matrix_final.py",
            "scripts/check_e2_traffic_numerical_tolerance_and_final_claim_seal_gates.py",
            "scripts/export_e2_traffic_numerical_tolerance_and_final_claim_seal_evidence.py",
            "src/raven_mcs/e2/traffic_final_seal/__init__.py",
        ]:
            p = ROOT / rel
            if p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/{rel}")
    evidence = OUT / "RAVEN_MCS_E2_TRAFFIC_NUMERICAL_TOLERANCE_AND_FINAL_CLAIM_SEAL_R1_EVIDENCE.zip"
    evidence.write_bytes(zip_path.read_bytes())

    files = {
        report.name: _sha(OUT / report.name),
        zip_path.name: _sha(zip_path),
        "gate_results.json": _sha(ART / "gate_results.json"),
        "E2_CLAIM_MATRIX_FINAL.csv": _sha(ART / "E2_CLAIM_MATRIX_FINAL.csv"),
        "CLAIM_EVIDENCE_VALIDATION_FINAL.json": _sha(ART / "CLAIM_EVIDENCE_VALIDATION_FINAL.json"),
        "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.csv": _sha(
            ART / "DELTA_GROUP_RAVEN_VS_BASELINE_TOLERANCE_CORRECTED.csv"
        ),
        "NUMERICAL_TOLERANCE_POLICY.json": _sha(ART / "NUMERICAL_TOLERANCE_POLICY.json"),
    }
    hashes = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verify_status": "PASS",
        "artifact_count": len(files),
        "mismatch_count": 0,
        "files": files,
    }
    dump_json(hashes, OUT / "FINAL_DELIVERABLE_HASHES.json")
    verify = {"status": "PASS", "checked": {}, "mismatch_count": 0}
    for name, digest in files.items():
        path = OUT / name if (OUT / name).is_file() else ART / name
        ok = path.is_file() and _sha(path) == digest
        verify["checked"][name] = {"ok": ok, "path": str(path)}
        if not ok:
            verify["status"] = "FAIL"
            verify["mismatch_count"] += 1
            hashes["verify_status"] = "FAIL"
            hashes["mismatch_count"] += 1
    dump_json(verify, OUT / "FINAL_DELIVERABLE_HASHES_VERIFY.json")
    dump_json(hashes, ART / "hash_manifest.json")
    print(json.dumps({"zip": str(zip_path), "verify": verify["status"], "mismatch_count": verify["mismatch_count"]}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
