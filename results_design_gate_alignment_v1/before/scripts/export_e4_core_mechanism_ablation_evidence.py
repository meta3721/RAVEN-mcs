#!/usr/bin/env python3
"""Create the E4 submission archive after analysis."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1"
ZIP = ROOT / "deliverables" / "TO_SUBMIT_E4_CORE_MECHANISM_ABLATION_R1.zip"


def main() -> None:
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and "smoke_only" not in path.as_posix():
                archive.write(path, f"{ART.name}/{path.relative_to(ART).as_posix()}")
    print(ZIP)


if __name__ == "__main__":
    main()
