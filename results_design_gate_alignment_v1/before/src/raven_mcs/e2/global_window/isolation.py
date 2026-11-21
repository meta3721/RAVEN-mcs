"""Design vs validation seed isolation audit."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from raven_mcs.e2.global_window.windows import DESIGN_SEEDS, VALIDATION_SEEDS
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def _count_validation_reads(root: Path) -> dict[str, int]:
    """Count on-disk validation artifacts under this round's output tree only."""
    out = root / "outputs/e2_global_window"
    counts = {
        "validation_config_read_count": 0,
        "validation_trace_read_count": 0,
        "validation_schedule_read_count": 0,
        "validation_output_read_count": 0,
    }
    if not out.exists():
        return counts
    for seed in VALIDATION_SEEDS:
        if (out / "traces" / str(seed)).exists():
            counts["validation_trace_read_count"] += 1
        if (out / "schedules" / f"{seed}.json").exists():
            counts["validation_schedule_read_count"] += 1
        if list(out.glob(f"**/*{seed}*")):
            counts["validation_output_read_count"] += 1
    return counts


def _source_refs_to_validation(root: Path) -> list[str]:
    """Static scan: global_window package must not execute validation seeds."""
    pkg = root / "src/raven_mcs/e2/global_window"
    refs: list[str] = []
    if not pkg.is_dir():
        return refs
    # Split tokens so this scanner file does not self-match.
    forbidden_a = "build_base_random_streams(" + "291"
    forbidden_b = "run_single_trace_" + "validation_seed"
    for path in pkg.rglob("*.py"):
        if path.name == "isolation.py":
            continue
        text = path.read_text(encoding="utf-8")
        if forbidden_a in text or forbidden_b in text:
            refs.append(str(path.relative_to(root)).replace("\\", "/"))
    return refs


def write_design_registry_and_isolation(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = root / "configs/frozen/e2_finite_sample_gate"
    out.mkdir(parents=True, exist_ok=True)
    design = {
        "design_seeds": list(DESIGN_SEEDS),
        "purpose": [
            "global_window_legality_audit",
            "balanced_dgp_design_audit",
            "single_arm_variance_estimation",
            "finite_sample_gate_freeze",
            "certification_level_selection",
        ],
        "forbidden_uses": ["method_performance", "validation_confirmation", "formal_results"],
        "registry_hash": sha256_json({"design_seeds": list(DESIGN_SEEDS)}),
    }
    dump_json(design, out / "design_seed_registry.json")
    dump_json({
        "validation_seeds": list(VALIDATION_SEEDS),
        "status": "RESERVED_NOT_RUN_THIS_ROUND",
    }, out / "validation_seed_registry.json")

    inter = sorted(set(DESIGN_SEEDS) & set(VALIDATION_SEEDS))
    reads = _count_validation_reads(root)
    refs = _source_refs_to_validation(root)
    total_reads = sum(reads.values())
    audit = {
        "design_seed_registry": list(DESIGN_SEEDS),
        "validation_seed_registry": list(VALIDATION_SEEDS),
        "intersection_count": int(len(inter)),
        "intersection": inter,
        **reads,
        "source_code_forbidden_execution_references": refs,
        "validation_read_count": int(total_reads),
        "status": "PASS" if len(inter) == 0 and total_reads == 0 and not refs else "FAIL",
    }
    dump_json(audit, root / "outputs/audits/E2_DESIGN_VALIDATION_ISOLATION_AUDIT.json")
    return {"design": design, "audit": audit}
