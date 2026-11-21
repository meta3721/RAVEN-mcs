#!/usr/bin/env python3
"""Create the self-contained E3 numerical-integrity evidence archive."""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH  # noqa: E402

ART = ROOT / ART_RELATIVE_PATH
OUT = ROOT / "deliverables/TO_SUBMIT_E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1"
ZIP = ROOT / "deliverables/TO_SUBMIT_E3_NUMERICAL_INTEGRITY_AND_CLEAN_CANARY_FIX_R1.zip"


def main() -> int:
    if not ART.is_dir():
        print(f"Missing artifact directory: {ART}")
        return 2
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ART, OUT)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in OUT.rglob("*"):
            if path.is_file():
                archive.write(path, f"{OUT.name}/{path.relative_to(OUT).as_posix()}")
    print(ZIP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
