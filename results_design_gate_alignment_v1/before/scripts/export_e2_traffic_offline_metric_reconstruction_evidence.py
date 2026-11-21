#!/usr/bin/env python3
"""Export offline reconstruction package ZIP."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_offline_metric_reconstruction_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1"
PACKAGE = "TO_SUBMIT_E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = ART / "E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1_REPORT.md"
    OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
    zip_path = OUT / f"{PACKAGE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if not path.is_file() or path.suffix == ".pt":
                continue
            zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        for rel in [
            "scripts/prepare_e2_traffic_offline_metric_reconstruction.py",
            "scripts/validate_e2_claim_matrix.py",
            "scripts/check_e2_traffic_offline_metric_reconstruction_and_claim_correction_gates.py",
            "scripts/export_e2_traffic_offline_metric_reconstruction_evidence.py",
            "src/raven_mcs/e2/traffic_offline_recon/__init__.py",
            "src/raven_mcs/e2/traffic_offline_recon/reconstruct.py",
        ]:
            p = ROOT / rel
            if p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/{rel}")
    evidence = OUT / "RAVEN_MCS_E2_TRAFFIC_OFFLINE_METRIC_RECONSTRUCTION_AND_CLAIM_CORRECTION_R1_EVIDENCE.zip"
    evidence.write_bytes(zip_path.read_bytes())
    hashes = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verify_status": "PASS",
        "files": {
            report.name: _sha(OUT / report.name),
            zip_path.name: _sha(zip_path),
            "gate_results.json": _sha(ART / "gate_results.json"),
            "E2_CLAIM_MATRIX.csv": _sha(ART / "E2_CLAIM_MATRIX.csv"),
            "CLAIM_EVIDENCE_VALIDATION.json": _sha(ART / "CLAIM_EVIDENCE_VALIDATION.json"),
        },
    }
    dump_json(hashes, OUT / "FINAL_DELIVERABLE_HASHES.json")
    dump_json(hashes, ART / "hash_manifest.json")
    verify = {"status": "PASS", "checked": {}}
    for name, digest in hashes["files"].items():
        path = OUT / name if (OUT / name).is_file() else ART / name
        ok = path.is_file() and _sha(path) == digest
        verify["checked"][name] = {"ok": ok, "path": str(path)}
        if not ok:
            verify["status"] = "FAIL"
            hashes["verify_status"] = "FAIL"
    dump_json(verify, OUT / "FINAL_DELIVERABLE_HASHES_VERIFY.json")
    dump_json(hashes, ART / "hash_manifest.json")
    print(json.dumps({"zip": str(zip_path), "verify": verify["status"]}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
