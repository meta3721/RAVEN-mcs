"""E4 smoke matrix; smoke evidence is never formal paper evidence."""
from __future__ import annotations

import json
from pathlib import Path

from raven_mcs.e3.canary.execute import ensure_eventtrace
from raven_mcs.utils.serialization import dump_json

from .constants import ABLATIONS, DATASETS, SMOKE_SEED
from .execute import run_logical


def run(root: Path, art: Path) -> dict:
    """Generate smoke-only EventTraces under ART, then run all five ablations."""
    smoke_art = Path(art) / "smoke_only"
    smoke_art.mkdir(parents=True, exist_ok=True)
    rows = []
    et_meta = {}
    for dataset in DATASETS:
        created = ensure_eventtrace(Path(root), smoke_art, dataset, SMOKE_SEED)
        et_dir = smoke_art / "eventtraces" / dataset / f"seed{SMOKE_SEED}" / "training_eventtrace"
        et_meta[dataset] = {
            "status": created.get("status"),
            "path": str(et_dir),
            "paper_evidence": False,
            "note": "SMOKE_ONLY EventTrace generated for software precheck; not formal E3/E4 evidence.",
        }
        for method in ABLATIONS:
            rows.append(
                run_logical(
                    root=Path(root),
                    art=smoke_art,
                    dataset=dataset,
                    method=method,
                    seed=SMOKE_SEED,
                    eventtrace_dir=et_dir,
                    accepted_marker_name="SMOKE_ACCEPTED.json",
                    allow_nonformal_seed=True,
                )
            )
    summary = {
        "seed": SMOKE_SEED,
        "n": len(rows),
        "accepted": sum(bool(r.get("accepted")) for r in rows),
        "paper_evidence": False,
        "eventtraces": et_meta,
        "rows": rows,
        "status": "PASS" if rows and all(bool(r.get("accepted")) for r in rows) else "FAIL",
    }
    dump_json(summary, Path(art) / "E4_SMOKE_RESULTS.json")
    return summary
