#!/usr/bin/env python3
"""Finalize hashes and export E3 multidataset protocol closure package."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_multidataset_protocol_closure_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_MULTIDATASET_PROTOCOL_CLOSURE_R1"
PACKAGE = "TO_SUBMIT_E3_MULTIDATASET_PROTOCOL_CLOSURE_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SKIP_HASH_NAMES = {
    "E3_CLOSURE_HASH_MANIFEST.json",
    "E3_CLOSURE_HASH_VERIFICATION.json",
    # Gate outputs are written after scientific artifacts are frozen.
    "gate_results.json",
    "gate_diagnostics.json",
}


def build_hash_manifest() -> dict:
    files = {}
    for path in sorted(ART.rglob("*")):
        if not path.is_file():
            continue
        if path.name in SKIP_HASH_NAMES:
            continue
        if path.suffix == ".pt":
            raise SystemExit(f"Refusing to hash/package checkpoint: {path}")
        rel = path.relative_to(ART).as_posix()
        files[rel] = _sha(path)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_root": str(ART.as_posix()),
        "files": files,
        "artifact_count": len(files),
        "excluded_from_hash": sorted(SKIP_HASH_NAMES),
        "note": "Scientific artifacts frozen before gate JSON rewrite; mismatch_count must be 0",
    }
    dump_json(manifest, ART / "E3_CLOSURE_HASH_MANIFEST.json")
    mismatch = 0
    checked = {}
    for rel, digest in files.items():
        p = ART / rel
        ok = p.is_file() and _sha(p) == digest
        checked[rel] = ok
        if not ok:
            mismatch += 1
    verify = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "mismatch_count": mismatch,
        "status": "PASS" if mismatch == 0 else "FAIL",
        "checked": checked,
    }
    dump_json(verify, ART / "E3_CLOSURE_HASH_VERIFICATION.json")
    return verify


def main() -> int:
    import subprocess
    import sys

    OUT.mkdir(parents=True, exist_ok=True)

    # 1) Freeze scientific artifact hashes (report already final).
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    # 2) Re-run gates now that verification exists (may rewrite gate_*.json only).
    gate_rc = subprocess.call([sys.executable, str(ROOT / "scripts/check_e3_multidataset_protocol_closure_gates.py")], cwd=str(ROOT))
    if gate_rc != 0:
        return gate_rc

    # 3) Independent re-verify of frozen scientific artifacts (once).
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_MULTIDATASET_PROTOCOL_CLOSURE_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT / f"{PACKAGE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and path.suffix != ".pt":
                zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")
        for rel in [
            "scripts/prepare_e3_multidataset_protocol_closure.py",
            "scripts/check_e3_multidataset_protocol_closure_gates.py",
            "scripts/export_e3_multidataset_protocol_closure_evidence.py",
            "src/raven_mcs/e3/protocol_closure/__init__.py",
            "src/raven_mcs/e3/protocol_closure/constants.py",
            "src/raven_mcs/e3/protocol_closure/reuse_guard.py",
            "src/raven_mcs/e3/protocol_closure/pair_state.py",
            "src/raven_mcs/e3/protocol_closure/complete_aligned.py",
            "src/raven_mcs/e3/protocol_closure/central_reference.py",
            "src/raven_mcs/e3/protocol_closure/method_registry.py",
            "tests/unit/test_e3_multidataset_protocol_closure_core.py",
            "logs/e3_multidataset_protocol_closure_unit.xml",
            "logs/e3_multidataset_protocol_closure_pytest_full.xml",
            "logs/e3_multidataset_protocol_closure_pip_check.txt",
        ]:
            p = ROOT / rel
            if p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/{rel}")
        cfg = ROOT / "configs/frozen/e3_multidataset_protocol_closure"
        if cfg.is_dir():
            for path in sorted(cfg.rglob("*")):
                if path.is_file():
                    zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ROOT).as_posix()}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        if any(n.endswith(".pt") for n in zf.namelist()):
            raise SystemExit("Package contains checkpoints")

    pkg_hash = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "zip": str(zip_path),
        "sha256": _sha(zip_path),
        "inner_verification": verify,
    }
    dump_json(pkg_hash, OUT / "FINAL_DELIVERABLE_HASHES.json")
    print(
        json.dumps(
            {
                "zip": str(zip_path),
                "verify": verify["status"],
                "mismatch_count": verify["mismatch_count"],
                "zip_sha256": pkg_hash["sha256"],
            },
            indent=2,
        )
    )
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
