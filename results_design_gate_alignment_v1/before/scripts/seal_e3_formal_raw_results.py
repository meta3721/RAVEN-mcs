#!/usr/bin/env python3
"""Seal immutable raw formal results after all 560 new runs are accepted."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e3.formal.constants import (  # noqa: E402
    FORMAL_SEEDS,
    N_NEW,
    N_REUSED,
    N_TOTAL,
    REUSED_TRAFFIC_METHODS,
    ROUND,
    art_path,
)
from raven_mcs.e3.formal.matrix import build_formal_matrix, logical_run_id  # noqa: E402
from raven_mcs.utils.hashing import sha256_file  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402

ART = art_path(ROOT)


def main() -> int:
    freeze = json.loads((ART / "E3_FORMAL_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    matrix = build_formal_matrix()
    new_ids = []
    missing = []
    for row in matrix["rows"]:
        if row["kind"] != "new":
            continue
        marker = ART / "runs" / row["dataset"] / row["method"] / f"seed{row['seed']}" / "FORMAL_ACCEPTED.json"
        if marker.is_file():
            new_ids.append(row["logical_run_id"])
        else:
            missing.append(row["logical_run_id"])
    if missing:
        print(json.dumps({"status": "REFUSE_SEAL", "missing": len(missing), "example": missing[:5]}, indent=2))
        return 2
    if len(new_ids) != N_NEW:
        print(f"refusing seal: {len(new_ids)}/{N_NEW}")
        return 3

    reused_index = ART / "reused_traffic" / "E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json"
    reused = json.loads(reused_index.read_text(encoding="utf-8")) if reused_index.is_file() else {"records": []}
    if len(reused.get("records", [])) != N_REUSED:
        print(f"reused index incomplete: {len(reused.get('records', []))}/{N_REUSED}")
        return 4

    # Prove sealed five never executed under formal art
    sealed_rerun = [
        logical_run_id("traffic", m, s)
        for s in FORMAL_SEEDS
        for m in REUSED_TRAFFIC_METHODS
        if (ART / "runs" / "traffic" / m / f"seed{s}" / "FORMAL_ACCEPTED.json").is_file()
    ]
    if sealed_rerun:
        print(json.dumps({"status": "SEALED_FIVE_RERUN_DETECTED", "ids": sealed_rerun[:5]}, indent=2))
        return 5

    records = []
    for rid in sorted(new_ids):
        # parse dataset/method/seed from id
        parts = rid.split("::")
        ds, method, seed_s = parts[1], parts[3], parts[4].replace("seed", "")
        run_dir = ART / "runs" / ds / method / f"seed{seed_s}"
        metrics = run_dir / "final_metrics.json"
        ckpt = run_dir / "checkpoints" / "final.pt"
        dual = run_dir / "final_metrics_dual_domain.json"
        records.append(
            {
                "logical_run_id": rid,
                "dataset": ds,
                "method": method,
                "seed": int(seed_s),
                "kind": "new",
                "metrics_hash": sha256_file(metrics) if metrics.is_file() else None,
                "checkpoint_hash": sha256_file(ckpt) if ckpt.is_file() else None,
                "dual_domain_hash": sha256_file(dual) if dual.is_file() else None,
            }
        )

    seal = {
        "round": ROUND,
        "status": "SEALED",
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "source_revision": freeze.get("git_commit"),
        "source_manifest_hash": freeze.get("source_manifest_hash"),
        "accepted_new": len(new_ids),
        "reused_traffic": N_REUSED,
        "merged_total": N_TOTAL,
        "new_run_ids": sorted(new_ids),
        "reused_run_ids": [
            logical_run_id("traffic", r["method"], int(r["seed"])) for r in reused["records"]
        ],
        "records": records,
        "no_model_rerun_after_seal": True,
        "no_performance_tuning": True,
    }
    dump_json(seal, ART / "E3_FORMAL_RAW_RESULTS_SEAL.json")
    files = {
        str(p.relative_to(ART)).replace("\\", "/"): sha256_file(p)
        for p in ART.rglob("*")
        if p.is_file() and "E3_FORMAL_RAW_RESULTS_HASH" not in p.name
    }
    dump_json(
        {"round": ROUND, "n_files": len(files), "files": files},
        ART / "E3_FORMAL_RAW_RESULTS_HASH_MANIFEST.json",
    )
    print(json.dumps({"status": "SEALED", "accepted_new": N_NEW, "reused": N_REUSED}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
