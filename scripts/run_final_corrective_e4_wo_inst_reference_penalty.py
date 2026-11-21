#!/usr/bin/env python3
"""Formal 40 final corrective raven_wo_inst runs (resume-by-accepted)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.wo_inst_final.constants import art_path  # noqa: E402
from raven_mcs.e4.wo_inst_final.corrective import run_final_corrective  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    prep = json.loads((art_path(ROOT) / "E4_PREPARE_STATUS.json").read_text(encoding="utf-8"))
    if not prep.get("authorize_40_final_reruns"):
        raise SystemExit("final corrective reruns not authorized by prepare status")
    branch = json.loads(
        (art_path(ROOT) / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json").read_text(
            encoding="utf-8"
        )
    )
    if branch.get("branch") != "B":
        raise SystemExit("formal runs only authorized under Branch B")
    freeze = art_path(ROOT) / "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json"
    if not freeze.is_file():
        raise SystemExit("corrective source freeze missing")
    reg = json.loads(
        (art_path(ROOT) / "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json").read_text(
            encoding="utf-8"
        )
    )
    if not reg.get("exactly_one_scientific_component_changed"):
        raise SystemExit("one-factor regression must pass before formal START")
    payload = run_final_corrective(ROOT, max_workers=args.max_workers)
    print(
        json.dumps(
            {k: payload.get(k) for k in ("status", "accepted", "total", "failures")},
            indent=2,
        )
    )
    return 0 if payload.get("status") == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
