#!/usr/bin/env python3
"""Package only the derived E3 final evidence seal."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_final_evidence_provenance_and_wording_seal_r1"
ZIP = ROOT / "deliverables/TO_SUBMIT_E3_FINAL_EVIDENCE_PROVENANCE_AND_WORDING_SEAL_R1.zip"


def main() -> None:
    ZIP.parent.mkdir(exist_ok=True)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ART.rglob("*")):
            if path.is_file():
                archive.write(path, f"{ART.name}/{path.relative_to(ART).as_posix()}")
    print(ZIP)


if __name__ == "__main__":
    main()
