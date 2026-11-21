#!/usr/bin/env python3
"""Export submission zip for E4 semantic integrity repair."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.package import export_package  # noqa: E402


def main() -> int:
    path = export_package(ROOT)
    print(json.dumps({"package": str(path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
