#!/usr/bin/env python3
"""Package formal evidence to deliverables/TO_SUBMIT_E3_FORMAL_RUNS_R1.zip."""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.formal.constants import art_path  # noqa: E402

ART = art_path(ROOT)
OUT_DIR = ROOT / "deliverables" / "TO_SUBMIT_E3_FORMAL_RUNS_R1"
ZIP = ROOT / "deliverables" / "TO_SUBMIT_E3_FORMAL_RUNS_R1.zip"


def main() -> int:
    if not ART.is_dir():
        print(f"missing {ART}")
        return 2
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    # Copy key evidence; exclude huge intermediate attempt backups if needed
    shutil.copytree(
        ART,
        OUT_DIR,
        ignore=shutil.ignore_patterns("attempts", "__pycache__", "*.pt"),
    )
    # Keep checkpoint hashes via manifests; include a note that .pt omitted for size
    (OUT_DIR / "CHECKPOINT_OMISSION_NOTE.md").write_text(
        "Checkpoint .pt binaries omitted from zip for size; hashes remain in "
        "runtime manifests and raw-results seal.\n",
        encoding="utf-8",
    )
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in OUT_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, f"{OUT_DIR.name}/{path.relative_to(OUT_DIR).as_posix()}")
    print(ZIP)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
