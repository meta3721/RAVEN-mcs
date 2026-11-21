#!/usr/bin/env python3
"""Freeze source identity after clean-canary prechecks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.numerical.constants import ART_RELATIVE_PATH  # noqa: E402
from raven_mcs.e3.numerical.source_freeze import write_source_freeze  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-clean-run", action="store_true")
    args = parser.parse_args()
    art = ROOT / ART_RELATIVE_PATH
    pre = art / "E3_PRE_CLEAN_REGRESSION.json"
    if not pre.is_file():
        print("Run prepare/prechecks before freezing source.")
        return 2
    pre_payload = json.loads(pre.read_text(encoding="utf-8"))
    if pre_payload.get("status") != "PASS":
        print(f"Refusing freeze: precheck status={pre_payload.get('status')}")
        return 3
    payload = write_source_freeze(ROOT, art, force=args.force_clean_run)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
