#!/usr/bin/env python3
"""Resume-by-accepted, seed-major E4 formal ablation executor with conservative parallelism."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.constants import art_path  # noqa: E402
from raven_mcs.e4.execute import run_logical  # noqa: E402
from raven_mcs.e4.matrix import build_matrix  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def _worker(spec: dict, freeze: dict) -> dict:
    try:
        return run_logical(
            root=ROOT,
            art=art_path(ROOT),
            freeze=freeze,
            dataset=spec["dataset"],
            method=spec["method"],
            seed=int(spec["seed"]),
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "dataset": spec["dataset"],
            "method": spec["method"],
            "seed": spec["seed"],
            "accepted": False,
            "status": "FAILED",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=0)
    args = parser.parse_args()
    art = art_path(ROOT)
    freeze = json.loads((art / "E4_FORMAL_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    matrix = build_matrix()["rows"]
    pending = []
    already = []
    for spec in matrix:
        marker = art / "runs" / spec["dataset"] / spec["method"] / f"seed{spec['seed']}" / "FORMAL_ACCEPTED.json"
        if marker.is_file():
            already.append(json.loads(marker.read_text(encoding="utf-8")))
        else:
            pending.append(spec)

    cpus = os.cpu_count() or 4
    workers = args.max_workers or max(1, min(4, max(1, cpus // 2)))
    print(
        json.dumps(
            {
                "total": len(matrix),
                "already_accepted": len(already),
                "pending": len(pending),
                "max_workers": workers,
            }
        ),
        flush=True,
    )

    rows = list(already)
    failures = []
    if pending:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_worker, spec, freeze): spec for spec in pending}
            for fut in as_completed(futures):
                row = fut.result()
                rows.append(row)
                print(json.dumps({k: row.get(k) for k in ("dataset", "method", "seed", "accepted", "status", "error")}), flush=True)
                if not row.get("accepted"):
                    failures.append(row)
                accepted = sum(1 for r in rows if r.get("accepted"))
                dump_json(
                    {
                        "accepted": accepted,
                        "completed_or_cached": len(rows),
                        "pending_initial": len(pending),
                        "failures": len(failures),
                        "max_workers": workers,
                    },
                    art / "E4_FORMAL_PROGRESS.json",
                )

    accepted = sum(1 for r in rows if r.get("accepted"))
    dump_json(
        {
            "rows": rows,
            "accepted": accepted,
            "total": len(matrix),
            "failures": failures,
            "status": "COMPLETE" if accepted == len(matrix) and not failures else "IN_PROGRESS_OR_FAILED",
        },
        art / "E4_FORMAL_PROGRESS.json",
    )
    return 0 if accepted == len(matrix) and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
