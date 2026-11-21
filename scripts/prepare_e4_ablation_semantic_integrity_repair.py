#!/usr/bin/env python3
"""Phase 0 + Task A/B/C for E4 semantic integrity repair (no formal reruns)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.phase0 import write_phase0  # noqa: E402
from raven_mcs.e4.semantic_repair.task_a import run_task_a  # noqa: E402
from raven_mcs.e4.semantic_repair.task_b import run_task_b  # noqa: E402
from raven_mcs.e4.semantic_repair.task_c import run_task_c  # noqa: E402
from raven_mcs.e4.semantic_repair.corrective import (  # noqa: E402
    build_corrective_matrix,
    freeze_corrective_source,
)
from raven_mcs.e4.semantic_repair.constants import art_path  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def main() -> int:
    art = art_path(ROOT)
    art.mkdir(parents=True, exist_ok=True)
    phase0 = write_phase0(ROOT)
    a = run_task_a(ROOT)
    b = run_task_b(ROOT)
    c = run_task_c(ROOT)
    matrix = build_corrective_matrix()
    dump_json(matrix, art / "E4_MINIMAL_CORRECTIVE_RERUN_MATRIX.json")
    # Freeze after fix is already in tree; prepare records the post-fix freeze.
    freeze = freeze_corrective_source(ROOT)
    authorize = (
        a["decision"]["decision"] == "E4_FULLMODE_EQUIVALENT_TO_E3_RAVEN"
        and b["decision"]["decision"] == "WO_INST_EXISTING_40_RUNS_INVALID_TARGETED_RERUN_REQUIRED"
        and c["decision"]["decision"] == "WO_DESIGN_ACTIVE_SET_DIFFERENCE_IS_VALID_WEIGHT_SUPPORT_EFFECT"
        and b["decision"].get("proven_invalid")
    )
    dump_json(
        {
            "phase0": phase0["status"],
            "task_a": a["decision"]["decision"],
            "task_b": b["decision"]["decision"],
            "task_c": c["decision"]["decision"],
            "authorize_40_corrective_reruns": authorize,
            "freeze_status": freeze["status"],
        },
        art / "E4_PREPARE_STATUS.json",
    )
    print(json.dumps({"authorize_40_corrective_reruns": authorize, "art": str(art)}, indent=2))
    return 0 if authorize else 2


if __name__ == "__main__":
    raise SystemExit(main())
