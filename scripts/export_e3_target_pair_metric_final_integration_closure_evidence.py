#!/usr/bin/env python3
"""Hash finalize + package E3 final integration closure."""
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
ART = ROOT / "artifacts/e3_target_pair_metric_final_integration_closure_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E3_TARGET_PAIR_METRIC_FINAL_INTEGRATION_CLOSURE_R1"
PACKAGE = "TO_SUBMIT_E3_TARGET_PAIR_METRIC_FINAL_INTEGRATION_CLOSURE_R1"
SKIP = {
    "E3_FINAL_INTEGRATION_HASH_MANIFEST.json",
    "E3_FINAL_INTEGRATION_HASH_VERIFICATION.json",
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
        files[path.relative_to(ART).as_posix()] = _sha(path)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "artifact_count": len(files),
        "excluded_from_hash": sorted(SKIP | {"*.pt"}),
    }
    dump_json(manifest, ART / "E3_FINAL_INTEGRATION_HASH_MANIFEST.json")
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
    dump_json(verify, ART / "E3_FINAL_INTEGRATION_HASH_VERIFICATION.json")
    return verify


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1
    rc = subprocess.call(
        [sys.executable, str(ROOT / "scripts/check_e3_target_pair_metric_final_integration_closure_gates.py")],
        cwd=str(ROOT),
    )
    if rc != 0:
        return rc
    verify = build_hash_manifest()
    if verify["mismatch_count"] != 0:
        return 1

    report = ART / "E3_TARGET_PAIR_METRIC_FINAL_INTEGRATION_CLOSURE_R1_REPORT.md"
    if report.is_file():
        OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    zip_path = OUT / f"{PACKAGE}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ART.rglob("*")):
            if not path.is_file() or path.suffix == ".pt":
                continue
            zf.write(path, arcname=f"{PACKAGE}/{path.relative_to(ART).as_posix()}")
        for rel in [
            "src/raven_mcs/e3/target_pair",
            "src/raven_mcs/e3/real_runner/runner.py",
            "src/raven_mcs/e3/real_runner/fixture_nd.py",
            "src/raven_mcs/e3/real_runner/generator_r3.py",
            "scripts/prepare_e3_target_pair_metric_final_integration_closure.py",
            "scripts/check_e3_target_pair_metric_final_integration_closure_gates.py",
            "tests/unit/test_e3_target_pair_metric_final_integration_core.py",
            "tests/integration/test_e3_target_pair_metric_final_integration.py",
        ]:
            p = ROOT / rel
            if p.is_dir():
                for f in p.rglob("*.py"):
                    zf.write(f, arcname=f"{PACKAGE}/code/{f.relative_to(ROOT).as_posix()}")
            elif p.is_file():
                zf.write(p, arcname=f"{PACKAGE}/code/{p.relative_to(ROOT).as_posix()}")
        for log in [
            "logs/e3_final_integration_unit.xml",
            "logs/e3_final_integration_pytest_full.xml",
            "logs/e3_final_integration_pip_check.txt",
        ]:
            lp = ROOT / log
            if lp.is_file():
                zf.write(lp, arcname=f"{PACKAGE}/{log}")

    meta = {
        "package": PACKAGE,
        "zip": str(zip_path),
        "zip_sha256": _sha(zip_path),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "gate_status": json.loads((ART / "gate_results.json").read_text(encoding="utf-8")).get("status"),
        "stop_status": json.loads((ART / "E3_FINAL_INTEGRATION_STOP_STATUS.json").read_text(encoding="utf-8")).get(
            "status"
        ),
    }
    dump_json(meta, OUT / "PACKAGE_META.json")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
