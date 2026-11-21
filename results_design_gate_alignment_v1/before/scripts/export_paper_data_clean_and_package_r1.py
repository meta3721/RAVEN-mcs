"""Export / run PAPER-DATA-CLEAN-AND-PACKAGE-R1 packaging pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from raven_mcs.paper_data_r1.pipeline import run_pipeline


def main() -> int:
    root = Path.cwd()
    summary = run_pipeline(root)
    print(json.dumps(
        {
            "final_status": summary.get("final_status"),
            "core_zip": summary.get("pack", {}).get("core_zip"),
            "full_zip": summary.get("pack", {}).get("full_zip"),
            "e2_runs": summary.get("statuses", {}).get("E2", {}).get("n_valid_runs"),
            "e2_eventtraces": summary.get("statuses", {}).get("E2", {}).get("n_eventtraces"),
            "e4_cells": summary.get("statuses", {}).get("E4", {}).get("n_core_cells"),
            "tdrive": summary.get("tdrive", {}).get("status"),
            "gates": summary.get("gates"),
            "core_missing": summary.get("core_missing"),
        },
        indent=2,
        default=str,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
