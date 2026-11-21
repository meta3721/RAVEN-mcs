#!/usr/bin/env python3
"""After Stage A completes, run Stage B then Stage C serially."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_formal_runs_r1"


def _stop() -> dict:
    p = ART / "E3_FORMAL_RUNS_STOP_STATUS.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _run_stage(stage: str) -> int:
    log = ART / "logs" / f"stage_{stage}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        proc = subprocess.run(
            [sys.executable, "scripts/run_e3_formal_runs.py", "--stage", stage],
            cwd=ROOT,
            stdout=fh,
            stderr=subprocess.STDOUT,
            env={**dict(**__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
        )
    return proc.returncode


def main() -> int:
    # Wait until Stage A is no longer IN_PROGRESS (or already complete)
    while True:
        st = _stop().get("status", "")
        if st in {"STAGE_A_COMPLETE", "STAGE_B_IN_PROGRESS", "STAGE_B_COMPLETE", "STAGE_C_IN_PROGRESS", "STAGE_C_COMPLETE"}:
            break
        if "BLOCKED" in st:
            print(st)
            return 1
        if st == "STAGE_A_IN_PROGRESS":
            time.sleep(60)
            continue
        # If somehow still PHASE0, do not start
        if st and "IN_PROGRESS" not in st and "COMPLETE" not in st:
            time.sleep(60)
            continue
        break

    for stage in ("B", "C"):
        st = _stop().get("status", "")
        if st == f"STAGE_{stage}_COMPLETE":
            continue
        print(f"starting stage {stage}", flush=True)
        rc = _run_stage(stage)
        if rc != 0:
            print(f"stage {stage} failed rc={rc}")
            return rc
    print("stages B+C complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
