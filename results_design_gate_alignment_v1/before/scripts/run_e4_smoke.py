#!/usr/bin/env python3
"""Run the disjoint E4 smoke matrix (not paper evidence)."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from raven_mcs.e4.constants import art_path
from raven_mcs.e4.smoke import run
from raven_mcs.utils.serialization import dump_json
if __name__ == "__main__":
    art=art_path(ROOT)
    try:
        result=run(ROOT,art); dump_json(result,art/"E4_SMOKE_RESULTS.json")
        raise SystemExit(0 if result["accepted"] == result["n"] else 1)
    except Exception as exc:
        dump_json({"status":"BLOCKED","error":f"{type(exc).__name__}: {exc}"},art/"E4_SMOKE_RESULTS.json"); raise
