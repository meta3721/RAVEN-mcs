#!/usr/bin/env python3
"""Hash finalize + package E3 semantic alignment closure."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_SEMANTIC_ALIGNMENT_AND_RUNNER_INTEGRATION_CLOSURE_R1"
PACKAGE = "TO_SUBMIT_E3_SEMANTIC_ALIGNMENT_AND_RUNNER_INTEGRATION_CLOSURE_R1"
SKIP = {
    "E3_SEMANTIC_CLOSURE_HASH_MANIFEST.json",
    "E3_SEMANTIC_CLOSURE_HASH_VERIFICATION.json",
    "gate_results.json",
    "gate_diagnostics.json",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_hash_manifest() -> dict:
    # Ensure no checkpoints remain
    for pt in ART.rglob("*.pt"):
        pt.unlink()
    files = {}
    for path in sorted(ART.rglob("*")):
        if not path.is_file() or path.name in SKIP or path.suffix == ".pt":
            continue
        files[path.relative_to(ART).as_posix()] = _sha(path)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "artifact_count": len(files),
        "excluded_from_hash": sorted(SKIP),
    }
    dump_json(manifest, ART / "E3_SEMANTIC_CLOSURE_HASH_MANIFEST.json")
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
    dump_json(verify, ART / "E3_SEMANTIC_CLOSURE_HASH_VERIFICATION.json")
    return verify


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts/check_e3_semantic_alignment_and_runner_integration_closure_gates.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_SEMANTIC_ALIGNMENT_AND_RUNNER_INTEGRATION_CLOSURE_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT / f"{PACKAGE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and path.suffix != ".pt":
                zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        for rel in [
            "scripts/prepare_e3_semantic_alignment_and_runner_integration_closure.py",
            "scripts/check_e3_semantic_alignment_and_runner_integration_closure_gates.py",
            "scripts/export_e3_semantic_alignment_and_runner_integration_closure_evidence.py",
            "tests/unit/test_e3_semantic_alignment_core.py",
            "tests/integration/test_e3_semantic_runner_integration.py",
            "logs/e3_semantic_alignment_unit.xml",
            "logs/e3_semantic_alignment_pytest_full.xml",
            "logs/e3_semantic_alignment_pip_check.txt",
        ]:
            p = ROOT / rel
            if p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/{rel}")
        for path in sorted((ROOT / "src/raven_mcs/e3/semantic_alignment").rglob("*.py")):
            zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        cfg = ROOT / "configs/frozen/e3_semantic_alignment_r2"
        if cfg.is_dir():
            for path in sorted(cfg.rglob("*")):
                if path.is_file():
                    zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        if any(n.endswith(".pt") for n in zf.namelist()):
            raise SystemExit("package contains checkpoints")

    dump_json(
        {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "zip": str(zip_path),
            "sha256": _sha(zip_path),
            "inner_verification": verify,
        },
        OUT / "FINAL_DELIVERABLE_HASHES.json",
    )
    print(json.dumps({"zip": str(zip_path), "verify": verify["status"], "mismatch_count": verify["mismatch_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
