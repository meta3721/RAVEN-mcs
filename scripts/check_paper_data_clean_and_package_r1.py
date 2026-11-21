"""Check G1–G30 for PAPER-DATA-CLEAN-AND-PACKAGE-R1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from raven_mcs.paper_data_r1.gates import run_gates


def main() -> int:
    root = Path.cwd()
    paper = root / "paper_ready_r1"
    if not paper.exists():
        print("paper_ready_r1 missing; run export first", file=sys.stderr)
        return 2
    gates = run_gates(root, paper, {"e5_started": False, "new_seed_dataset_baseline_metric": False})
    print(json.dumps(gates, indent=2, default=str))
    return 0 if gates.get("all_pass") else 1


if __name__ == "__main__":
    sys.exit(main())
