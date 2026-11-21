#!/usr/bin/env python3
"""Package E2 formal results analysis evidence ZIP (no model checkpoints)."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e2_traffic_formal_results_analysis_r1"
OUT = ROOT / "deliverables/TO_SUBMIT_E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1"
PACKAGE = "TO_SUBMIT_E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = ART / "E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_REPORT.md"
    zip_path = OUT / f"{PACKAGE}.zip"
    evidence = OUT / "RAVEN_MCS_E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_EVIDENCE.zip"

    # Copy report into deliverables
    OUT.joinpath(report.name).write_text(report.read_text(encoding="utf-8"), encoding="utf-8")

    include_roots = [ART]
    # Explicitly exclude any checkpoint-like files
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root in include_roots:
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                if path.suffix == ".pt" or path.name.endswith(".pt"):
                    continue
                arc = path.relative_to(ROOT).as_posix()
                zf.write(path, arcname=f"{PACKAGE}/{arc}")
        # include analysis scripts
        for rel in [
            "scripts/prepare_e2_traffic_formal_results_analysis.py",
            "scripts/check_e2_traffic_formal_results_analysis_gates.py",
            "scripts/export_e2_traffic_formal_results_analysis_evidence.py",
            "src/raven_mcs/e2/traffic_formal_analysis/__init__.py",
            "src/raven_mcs/e2/traffic_formal_analysis/stats.py",
            "src/raven_mcs/e2/traffic_formal_analysis/ledger_audit.py",
            "scripts/check_e2_traffic_formal_runs_gates.py",
        ]:
            path = ROOT / rel
            if path.is_file():
                zf.write(path, arcname=f"{PACKAGE}/{rel}")

    evidence.write_bytes(zip_path.read_bytes())

    hashes = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": {
            report.name: _sha(OUT / report.name),
            zip_path.name: _sha(zip_path),
            evidence.name: _sha(evidence),
            "e2_analysis_gate_results.json": _sha(ART / "e2_analysis_gate_results.json"),
            "E2_CLAIM_MATRIX.csv": _sha(ART / "E2_CLAIM_MATRIX.csv"),
            "SCENARIO_VS_BALANCED_STATS.csv": _sha(ART / "SCENARIO_VS_BALANCED_STATS.csv"),
        },
    }
    dump_json(hashes, OUT / "FINAL_DELIVERABLE_HASHES.json")
    dump_json(hashes, ART / "hash_manifest.json")
    verify = {"status": "PASS", "checked": {}, "created_utc": hashes["created_utc"]}
    for name, digest in hashes["files"].items():
        path = OUT / name if (OUT / name).is_file() else ART / name
        ok = path.is_file() and _sha(path) == digest
        verify["checked"][name] = {"ok": ok, "path": str(path)}
        if not ok:
            verify["status"] = "FAIL"
    dump_json(verify, OUT / "FINAL_DELIVERABLE_HASHES_VERIFY.json")
    readme = OUT / "E2_TRAFFIC_FORMAL_RESULTS_AUDIT_AND_PAPER_ANALYSIS_R1_SUBMISSION_README.txt"
    readme.write_text(
        "E2 formal results audit package. No new training. Submit ZIP + hashes + report.\n",
        encoding="utf-8",
    )
    print(json.dumps({"zip": str(zip_path), "verify": verify["status"]}, indent=2))
    return 0 if verify["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
