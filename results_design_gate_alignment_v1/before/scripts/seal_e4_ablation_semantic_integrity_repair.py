#!/usr/bin/env python3
"""Seal corrective raw results and write provenance/evidence index."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.corrective import (  # noqa: E402
    seal_corrective,
    write_provenance_and_index,
)


def main() -> int:
    seal = seal_corrective(ROOT)
    if seal.get("status") != "SEALED":
        print(json.dumps(seal, indent=2))
        return 1
    idx = write_provenance_and_index(ROOT)
    print(json.dumps({"seal": seal["status"], **idx}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
