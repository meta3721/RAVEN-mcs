#!/usr/bin/env python3
"""Gate checker for E4-WO-INST-REFERENCE-PENALTY-FINAL-CORRECTION-R1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.wo_inst_final.gates import run_gates, write_hash_manifest  # noqa: E402


def main() -> int:
    write_hash_manifest(ROOT)
    gates = run_gates(ROOT)
    print(json.dumps({
        "all_pass": gates.get("all_pass"),
        "pass_count": gates.get("pass_count"),
        "total_count": gates.get("total_count"),
        "failed": gates.get("failed"),
    }, indent=2))
    return 0 if gates.get("all_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
