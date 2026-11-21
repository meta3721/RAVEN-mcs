#!/usr/bin/env python3
"""Export only the E3 closure audit artifacts, never raw training outputs."""
from __future__ import annotations
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.evidence_closure.constants import ART_RELATIVE_PATH  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
OUT = ROOT / "deliverables" / "TO_SUBMIT_E3_FORMAL_EVIDENCE_INTEGRITY_AND_CLAIM_CLOSURE_R1"
ZIP = ROOT / "deliverables" / "TO_SUBMIT_E3_FORMAL_EVIDENCE_INTEGRITY_AND_CLAIM_CLOSURE_R1.zip"

def main() -> int:
    if not (ART / "STOP_STATUS.json").is_file(): return 2
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(ART, OUT, ignore=shutil.ignore_patterns("*.pt", "attempts", "__pycache__"))
    shutil.copy2(
        ROOT / "tests" / "unit" / "test_e3_evidence_integrity_claim_closure_core.py",
        OUT / "E3_TARGETED_AUDIT_TESTS.py",
    )
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in OUT.rglob("*"):
            if path.is_file(): zf.write(path, f"{OUT.name}/{path.relative_to(OUT).as_posix()}")
    print(ZIP); return 0
if __name__ == "__main__": raise SystemExit(main())
