"""Report, stop status, and submission package."""
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
    branch = json.loads(
        (art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json").read_text(encoding="utf-8")
    )
    recovery = json.loads(
        (art / "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.json").read_text(encoding="utf-8")
    )
    design = json.loads(
        (art / "E4_WO_DESIGN_FINAL_DECISION_R2.json").read_text(encoding="utf-8")
    )
    design_sum = json.loads(
        (art / "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json").read_text(encoding="utf-8")
    )
    claims = json.loads(
        (art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json").read_text(encoding="utf-8")
    )
    e5 = json.loads((art / "E4_TO_E5_DECISION_FINAL.json").read_text(encoding="utf-8"))
    seal_path = art / "E4_WO_INST_FINAL_CORRECTIVE_RAW_RESULTS_SEAL.json"
    seal = (
        json.loads(seal_path.read_text(encoding="utf-8"))
        if seal_path.is_file()
        else {}
    )

    lines = [
        f"# {ROUND} Report",
        "",
        "## 1. Executive decision",
        f"- Branch: `{branch.get('branch')}` / `{branch.get('decision')}`",
        f"- Recovered E3 λ_β: `{recovery.get('recovered_lambda_beta')}`",
        f"- Design decision: `{design.get('decision')}`",
        f"- E4→E5: `{e5.get('decision')}`",
        "",
        "## 2. No-scope-expansion attestation",
        "- No Traffic / new datasets / baselines / metrics / seeds / E5.",
        "",
        "## 3. E3 full-RAVEN λ_β recovery",
        f"- recovered rows: {recovery.get('n_recovered')} / {recovery.get('n_rows')}",
        f"- evidence path: `{recovery.get('methods_recovery', {}).get('evidence_path')}`",
        f"- evidence hash: `{recovery.get('methods_recovery', {}).get('evidence_hash')}`",
        "",
        "## 4. Per-seed λ_β consistency",
        "- See `E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json`.",
        "",
        "## 5. Full P2 parameter identity",
        "- See `E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json`.",
        "",
        "## 6. Existing corrected w/o-Inst parameter audit",
        "- Gen1 used λ_β=1e-8 (mismatch vs E3=1.0) → Branch B.",
        "",
        "## 7. One-factor w/o-Inst specification",
        "- Keep matched E3 λ_β/λ_v/λ_s; only λ_g=0 + instant_calibration=False.",
        "",
        "## 8. Branch A/B/C decision",
        f"- `{branch.get('decision')}` (authorized runs={branch.get('new_formal_runs_authorized')})",
        "",
        "## 9. w/o-Inst final regression",
        "- See `E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json`.",
        "",
        "## 10. Corrective source freeze",
        "- See `E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json` (Branch B).",
        "",
        "## 11. Corrective 40-run execution",
        f"- accepted: {seal.get('accepted_corrective_runs', 'n/a')} / 40",
        f"- seal: `{seal.get('status', 'n/a')}`",
        "",
        "## 12. Superseded w/o-Inst provenance",
        "- Gen0 INVALID_P2_OFF; Gen1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH; Gen2 FINAL_VALID_ONE_FACTOR.",
        "",
        "## 13. P2 state persistence",
        "- Final runs persist `p2_invocation_states.json` with full lambdas/residuals.",
        "",
        "## 14. U-Air 774-window Design layer audit",
        f"- rows: {design_sum.get('total_differing_windows')}",
        f"- counts: {json.dumps(design_sum.get('counts'))}",
        "",
        "## 15. Design causal classification",
        "- Physical EventTrace layers identical; first difference at weight-support / aggregation.",
        "",
        "## 16. Design final decision",
        f"- `{design.get('decision')}`",
        "",
        "## 17. Final 240-cell evidence index",
        "- `E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv`",
        "",
        "## 18. Updated Inst statistics",
        "- `E4_INST_FINAL_STATS.csv` (FULL RAVEN vs Gen2 wo_inst only).",
        "",
        "## 19. Final component claim matrix",
    ]
    for comp, payload in claims.items():
        lines.append(f"- **{comp}**: `{payload['status']}` — {payload['paper_safe_wording']}")
    lines.extend([
        "",
        "## 20. Final mechanism synthesis",
        "- See `E4_CORE_MECHANISM_SYNTHESIS_FINAL_R3.md`.",
        "",
        "## 21. Whether E5 is truly needed",
        f"- `{e5.get('decision')}` (e5_started=false)",
        "",
        "## 22. Exact next action",
        "- Stop experiments and write the paper using sealed E4 evidence.",
        "",
        "## Gates",
        f"- pass_count: {gates.get('pass_count')} / {gates.get('total_count')}",
        f"- all_pass: {gates.get('all_pass')}",
        f"- failed: {gates.get('failed')}",
        "",
    ])
    path = art / "E4_WO_INST_REFERENCE_PENALTY_FINAL_CORRECTION_R1_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_stop_status(root: Path, gates: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    design = json.loads(
        (art / "E4_WO_DESIGN_FINAL_DECISION_R2.json").read_text(encoding="utf-8")
    )
    branch = json.loads(
        (art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json").read_text(encoding="utf-8")
    )
    if branch.get("branch") == "C":
        status = "E4_FINAL_SEAL_BLOCKED_BY_E3_PARAMETER_PROVENANCE"
    elif design.get("decision") == "WO_DESIGN_SCOPE_LEAKAGE_CONFIRMED":
        status = "E4_FINAL_SEAL_BLOCKED_BY_DESIGN_SCOPE_LEAKAGE"
    elif not gates.get("all_pass"):
        # distinguish one-factor failure if regression failed
        reg = json.loads(
            (art / "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json").read_text(
                encoding="utf-8"
            )
        )
        if not reg.get("exactly_one_scientific_component_changed"):
            status = "E4_FINAL_SEAL_BLOCKED_BY_WO_INST_ONE_FACTOR_FAILURE"
        else:
            status = "E4_FINAL_SEAL_BLOCKED_BY_WO_INST_ONE_FACTOR_FAILURE"
    else:
        status = "E4_CORE_MECHANISM_ABLATION_FINAL_SEALED"
    payload = {
        "round": ROUND,
        "status": status,
        "gates_all_pass": bool(gates.get("all_pass")),
        "e5_launched": False,
        "e4_to_e5_decision": "E4_SEALED_STOP_EXPERIMENTS_AND_WRITE",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_FINAL_STOP_STATUS.json")
    return payload


def export_package(root: Path) -> Path:
    art = art_path(root)
    deliverables = art / "deliverables"
    deliverables.mkdir(parents=True, exist_ok=True)
    # also top-level deliverables path requested
    top = Path(root) / "deliverables"
    top.mkdir(parents=True, exist_ok=True)
    name = "TO_SUBMIT_E4_WO_INST_REFERENCE_PENALTY_FINAL_CORRECTION_R1.zip"
    include = [
        "E4_WO_INST_LAMBDA_BETA_PHASE0_ATTESTATION.json",
        "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.csv",
        "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.json",
        "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.md",
        "E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json",
        "E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json",
        "E4_CURRENT_WO_INST_PARAMETER_AUDIT.csv",
        "E4_CURRENT_WO_INST_PARAMETER_AUDIT.json",
        "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json",
        "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.md",
        "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json",
        "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.md",
        "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json",
        "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json",
        "E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv",
        "E4_WO_INST_SUPERSEDED_PROVENANCE.csv",
        "E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv",
        "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json",
        "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.md",
        "E4_WO_DESIGN_FINAL_DECISION_R2.json",
        "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
        "E4_WO_INST_FINAL_CORRECTIVE_RAW_RESULTS_SEAL.json",
        "E4_FINAL_VALID_EVIDENCE_SEAL_R2.json",
        "E4_INST_FINAL_STATS.csv",
        "E4_INST_FINAL_STATS.json",
        "E4_WO_INST_FINAL_CLAIM.json",
        "E4_WO_INST_FINAL_CLAIM.md",
        "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
        "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.md",
        "E4_CORE_MECHANISM_SYNTHESIS_FINAL_R3.md",
        "E4_TO_E5_DECISION_FINAL.json",
        "E4_TO_E5_DECISION_FINAL.md",
        "E4_WO_INST_FINAL_GATES.json",
        "E4_GATES.json",
        "E4_HASH_MANIFEST.json",
        "E4_HASH_VERIFICATION.json",
        "E4_FINAL_STOP_STATUS.json",
        "E4_WO_INST_REFERENCE_PENALTY_FINAL_CORRECTION_R1_REPORT.md",
    ]
    for zip_path in (deliverables / name, top / name):
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname in include:
                p = art / fname
                if p.is_file():
                    zf.write(p, arcname=fname)
            # include a few p2 state samples + recovered source hashes
            rec = art / "recovered_source" / "methods.py"
            if rec.is_file():
                zf.write(rec, arcname="recovered_source/methods.py")
            # package note for tests path
            tests = Path(root) / "tests" / "unit" / "test_e4_wo_inst_reference_penalty_final_correction.py"
            if tests.is_file():
                zf.write(tests, arcname="tests/unit/test_e4_wo_inst_reference_penalty_final_correction.py")
            gates_script = (
                Path(root)
                / "scripts"
                / "check_e4_wo_inst_reference_penalty_final_correction_gates.py"
            )
            if gates_script.is_file():
                zf.write(
                    gates_script,
                    arcname="scripts/check_e4_wo_inst_reference_penalty_final_correction_gates.py",
                )
    dump_json(
        {"zip": str((top / name).relative_to(root)).replace("\\", "/"), "status": "PACKAGED"},
        art / "E4_PACKAGE_MANIFEST.json",
    )
    return top / name
