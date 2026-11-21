#!/usr/bin/env python3
"""Smoke raven_wo_inst on seed 32001 for SS+UA after semantic fix."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.corrective import freeze_corrective_source, run_smoke  # noqa: E402
from raven_mcs.e4.semantic_repair.constants import art_path  # noqa: E402


def main() -> int:
    art = art_path(ROOT)
    if not (art / "E4_CORRECTIVE_SOURCE_FREEZE.json").is_file():
        freeze_corrective_source(ROOT)
    payload = run_smoke(ROOT)
    print(json.dumps({"status": payload["status"], "rows": [
        {k: r.get(k) for k in ("dataset", "accepted", "P2_invoked", "p2_states_len")}
        for r in payload["rows"]
    ]}, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
