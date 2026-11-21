#!/usr/bin/env python3
"""E4SR-G1..G26 gate runner."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.gates import run_gates  # noqa: E402


def main() -> int:
    result = run_gates(ROOT)
    print(json.dumps(result, indent=2))
    return 0 if result.get("all_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
