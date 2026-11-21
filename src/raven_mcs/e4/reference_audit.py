"""Audit immutable E3 RAVEN references and EventTrace identities."""
from __future__ import annotations
import json
from pathlib import Path
from .constants import DATASETS, FORMAL_SEEDS
from raven_mcs.utils.hashing import sha256_file

def audit(root: Path, *, seeds=FORMAL_SEEDS) -> dict:
    root = Path(root)
    rows, missing = [], []
    for dataset in DATASETS:
        for seed in seeds:
            ref = root / "artifacts/e3_formal_runs_r1/runs" / dataset / "raven" / f"seed{seed}"
            trace = root / "artifacts/e3_formal_runs_r1/eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"
            metrics, manifest, identity = ref / "final_metrics.json", ref / "runtime_manifest.json", trace / "trace_identity.json"
            present = all(p.is_file() for p in (metrics, manifest, identity))
            if not present:
                missing.append({"dataset": dataset, "seed": seed})
            trace_id = json.loads(identity.read_text(encoding="utf-8")) if identity.is_file() else {}
            rows.append({
                "dataset": dataset, "seed": seed, "reference_run": str(ref),
                "eventtrace": str(trace), "reference_metrics_sha256": sha256_file(metrics) if metrics.is_file() else None,
                "reference_manifest_sha256": sha256_file(manifest) if manifest.is_file() else None,
                "eventtrace_identity_sha256": sha256_file(identity) if identity.is_file() else None,
                "eventtrace_hash": trace_id.get("trace_hash"), "present": present,
            })
    return {"n_expected": len(DATASETS) * len(seeds), "n_present": len(rows) - len(missing),
            "rows": rows, "missing": missing, "status": "PASS" if not missing else "BLOCKED_MISSING_E3_INPUTS"}
