#!/usr/bin/env python3
"""Export E3 protocol reuse/readiness submission package (no checkpoints)."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_protocol_reuse_and_readiness_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_PROTOCOL_REUSE_AND_READINESS_R1"
PACKAGE = "TO_SUBMIT_E3_PROTOCOL_REUSE_AND_READINESS_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = ART / "E3_PROTOCOL_REUSE_AND_READINESS_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT / f"{PACKAGE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and path.suffix != ".pt":
                zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        for rel in [
            "scripts/prepare_e3_protocol_reuse_and_readiness.py",
            "scripts/check_e3_protocol_reuse_and_readiness_gates.py",
            "scripts/export_e3_protocol_reuse_and_readiness_evidence.py",
            "src/raven_mcs/e3/__init__.py",
            "src/raven_mcs/e3/protocol_readiness/__init__.py",
            "tests/unit/test_e3_protocol_reuse_and_readiness_core.py",
            "logs/e3_protocol_reuse_unit.xml",
            "logs/e3_protocol_reuse_pytest_full.xml",
            "logs/e3_protocol_reuse_pip_check.txt",
        ]:
            p = ROOT / rel
            if p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/{rel}")

    # Reject any trained checkpoint accidentally packaged
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad = [n for n in zf.namelist() if n.endswith(".pt")]
        if bad:
            raise SystemExit(f"Package contains checkpoints: {bad}")

    key_names = [
        "E3_SCIENTIFIC_PROTOCOL.json",
        "E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json",
        "E3_DATASET_READINESS.csv",
        "E3_TRAFFIC_METHOD_COVERAGE.csv",
        "E3_METHOD_REGISTRY_AUDIT.csv",
        "E3_PRIMARY_COMPARISON_FREEZE.json",
        "E3_METRIC_AVAILABILITY.csv",
        "E3_PAIR_METRIC_READINESS.json",
        "E3_ORACLE_READINESS.csv",
        "E3_STATISTICAL_PROTOCOL.json",
        "E3_MINIMUM_NEW_RUN_MATRIX.json",
        "E3_CANARY_PLAN.json",
        "gate_results.json",
        "E3_PROTOCOL_REUSE_AND_READINESS_R1_REPORT.md",
        "E3_PROTOCOL_REUSE_AND_READINESS_STOP_STATUS.json",
        "hash_manifest_sources.json",
    ]
    files = {zip_path.name: _sha(zip_path)}
    if (OUT / report.name).is_file():
        files[report.name] = _sha(OUT / report.name)
    for name in key_names:
        p = ART / name
        if p.is_file():
            files[name] = _sha(p)

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
