"""Prepare directories for PAPER-DATA-CLEAN-AND-PACKAGE-R1."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    paper = root / "paper_ready_r1"
    for rel in (
        "00_index",
        "01_core_data/e1",
        "01_core_data/e2",
        "01_core_data/e3",
        "01_core_data/e4",
        "01_core_data/master",
        "02_supporting_data/e0_correctness",
        "02_supporting_data/e1",
        "02_supporting_data/e2",
        "02_supporting_data/e3",
        "02_supporting_data/e4",
        "02_supporting_data/solver",
        "02_supporting_data/runtime",
        "02_supporting_data/diagnostics",
        "03_raw_evidence/e1",
        "03_raw_evidence/e2",
        "03_raw_evidence/e3",
        "03_raw_evidence/e4",
        "03_raw_evidence/source_snapshots",
        "04_statistics",
        "05_provenance",
        "06_table_sources",
        "07_figure_sources",
        "08_tdrive_readiness",
        "09_archive_manifest",
        "10_reports/previews",
    ):
        (paper / rel).mkdir(parents=True, exist_ok=True)
    (root / "deliverables").mkdir(parents=True, exist_ok=True)
    print(f"Prepared {paper}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
