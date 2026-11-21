"""Finalize report, stop status, and submission zip."""
from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.utils.serialization import dump_json

from .constants import ROUND, art_path


def write_report(root: Path, gates: dict[str, Any]) -> Path:
    art = art_path(root)
    task_a = json.loads((art / "E4_TASK_A_DECISION.json").read_text(encoding="utf-8"))
    task_b = json.loads((art / "E4_TASK_B_DECISION.json").read_text(encoding="utf-8"))
    task_c = json.loads((art / "E4_TASK_C_DECISION.json").read_text(encoding="utf-8"))
    claims = json.loads((art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json").read_text(encoding="utf-8"))
    seal = json.loads((art / "E4_CORRECTIVE_RAW_RESULTS_SEAL.json").read_text(encoding="utf-8"))
    nxt = json.loads((art / "E4_NEXT_STEP_DECISION.json").read_text(encoding="utf-8"))

    lines = [
        f"# {ROUND} Report",
        "",
        "## Decisions",
        f"- Task A: `{task_a.get('decision')}`",
        f"- Task B: `{task_b.get('decision')}` (corrective reruns={task_b.get('authorized_corrective_reruns')})",
        f"- Task C: `{task_c.get('decision')}`",
        f"- Next step: `{nxt.get('decision')}`",
        "",
        "## Corrective reruns",
        f"- accepted: {seal.get('accepted_corrective_runs')} / 40",
        f"- seal: `{seal.get('status')}`",
        "",
        "## Claim summary (R2)",
    ]
    for comp, payload in claims.items():
        lines.append(f"- **{comp}**: `{payload['status']}` — {payload['paper_safe_wording']}")
    lines.extend([
        "",
        "## Gates",
        f"- pass_count: {gates.get('pass_count')} / {gates.get('total_count')}",
        f"- all_pass: {gates.get('all_pass')}",
        f"- failed: {gates.get('failed')}",
        "",
        "## Notes",
        "- Parent E4 raw runs were not deleted or overwritten.",
        "- Only raven_wo_inst (40 cells) was correctively rerun.",
        "- E5 was not launched.",
        "",
    ])
    path = art / "E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_stop_status(root: Path, gates: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    payload = {
        "round": ROUND,
        "status": "COMPLETE" if gates.get("all_pass") else "BLOCKED",
        "gates_all_pass": bool(gates.get("all_pass")),
        "e5_launched": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_FINAL_STOP_STATUS.json")
    return payload


def export_package(root: Path) -> Path:
    art = art_path(root)
    deliverables = art / "deliverables"
    deliverables.mkdir(parents=True, exist_ok=True)
    zip_path = deliverables / "TO_SUBMIT_E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1.zip"
    include_names = [
        "E4_SEMANTIC_REPAIR_PHASE0_ATTESTATION.json",
        "E4_SOURCE_DIFF_CLASSIFICATION.json",
        "E4_SOURCE_DIFF_CLASSIFICATION.md",
        "E4_ABLATION_SWITCH_REGRESSION.json",
        "E4_TASK_A_DECISION.json",
        "E4_WO_INST_SEMANTIC_FIX.json",
        "E4_WO_INST_SEMANTIC_FIX.md",
        "E4_WO_INST_CONTROL_FLOW_AUDIT.json",
        "E4_WO_INST_ONE_FACTOR_REGRESSION.json",
        "E4_WO_INST_PARENT_P2_AUDIT.json",
        "E4_TASK_B_DECISION.json",
        "E4_ACTIVE_SET_SUMMARY.csv",
        "E4_ACTIVE_SET_DIFF_VS_RAVEN.csv",
        "E4_ACTIVE_SET_AUDIT.json",
        "E4_ACTIVE_SET_AUDIT.md",
        "E4_TASK_C_DECISION.json",
        "E4_MINIMAL_CORRECTIVE_RERUN_MATRIX.json",
        "E4_CORRECTIVE_SOURCE_FREEZE.json",
        "E4_SMOKE_RESULTS.json",
        "E4_CORRECTIVE_RUN_STATUS.json",
        "E4_CORRECTIVE_RAW_RESULTS_SEAL.json",
        "E4_PROVENANCE_SUPERSESSION.csv",
        "E4_FINAL_VALID_EVIDENCE_INDEX.csv",
        "E4_ABLATION_PAIRED_TESTS_R2.csv",
        "E4_ABLATION_PAIRED_TESTS_R2.json",
        "E4_INST_CORRECTED_STATS.csv",
        "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json",
        "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.md",
        "E4_COMPONENT_CONTRIBUTION_MATRIX_R2.csv",
        "E4_INTERPRETATION_R2.json",
        "E4_INTERPRETATION_R2.md",
        "E4_NEXT_STEP_DECISION.json",
        "E4_SEMANTIC_REPAIR_GATES.json",
        "E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1_REPORT.md",
        "E4_FINAL_STOP_STATUS.json",
    ]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in include_names:
            path = art / name
            if path.is_file():
                zf.write(path, arcname=name)
        # include a thin corrective acceptance manifest, not full tensors
        corr = art / "corrective_runs"
        for marker in corr.glob("*/*/seed*/FORMAL_ACCEPTED.json"):
            zf.write(marker, arcname=str(marker.relative_to(art)).replace("\\", "/"))
            audit = marker.parent / "method_smoke_audit.json"
            metrics = marker.parent / "final_metrics.json"
            if audit.is_file():
                zf.write(audit, arcname=str(audit.relative_to(art)).replace("\\", "/"))
            if metrics.is_file():
                zf.write(metrics, arcname=str(metrics.relative_to(art)).replace("\\", "/"))
    dump_json(
        {"zip": str(zip_path), "created_utc": datetime.now(timezone.utc).isoformat()},
        art / "E4_PACKAGE_MANIFEST.json",
    )
    return zip_path
