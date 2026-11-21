#!/usr/bin/env python3
"""Analyze sealed corrective evidence → R2 claims."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.analyze_r2 import run_analysis_r2  # noqa: E402


def main() -> int:
    out = run_analysis_r2(ROOT)
    summary = {k: v["status"] for k, v in out["claims"].items()}
    print(json.dumps({"n_paired": out["n_paired"], "claims": summary, "next": out["interpretation"]["next_step_decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
