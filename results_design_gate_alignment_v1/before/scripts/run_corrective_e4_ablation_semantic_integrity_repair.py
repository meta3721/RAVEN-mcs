#!/usr/bin/env python3
"""Formal 40 corrective raven_wo_inst runs (resume-by-accepted, max_workers=4)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.corrective import run_corrective  # noqa: E402
from raven_mcs.e4.semantic_repair.constants import art_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    prep = json.loads((art_path(ROOT) / "E4_PREPARE_STATUS.json").read_text(encoding="utf-8"))
    if not prep.get("authorize_40_corrective_reruns"):
        raise SystemExit("corrective reruns not authorized by prepare status")
    smoke = json.loads((art_path(ROOT) / "E4_SMOKE_RESULTS.json").read_text(encoding="utf-8"))
    if smoke.get("status") != "PASS":
        raise SystemExit("smoke must PASS before formal corrective runs")
    payload = run_corrective(ROOT, max_workers=args.max_workers)
    print(json.dumps({k: payload.get(k) for k in ("status", "accepted", "total", "failures")}, indent=2))
    return 0 if payload.get("status") == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
