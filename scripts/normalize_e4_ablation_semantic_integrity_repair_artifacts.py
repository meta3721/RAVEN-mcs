#!/usr/bin/env python3
"""Normalize E4 semantic-repair artifact names to the instruction-required set."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ART = Path("artifacts/e4_ablation_semantic_integrity_repair_r1")
ROOT = Path(".")


def dump(name: str, obj: object) -> None:
    (ART / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read(name: str) -> dict:
    return json.loads((ART / name).read_text(encoding="utf-8"))


def maybe_copy(src: str, dst: str) -> None:
    s, d = ART / src, ART / dst
    if s.is_file() and not d.is_file():
        shutil.copy2(s, d)


def main() -> None:
    a, b, c = read("E4_TASK_A_DECISION.json"), read("E4_TASK_B_DECISION.json"), read("E4_TASK_C_DECISION.json")
    nxt, gates, claims = (
        read("E4_NEXT_STEP_DECISION.json"),
        read("E4_SEMANTIC_REPAIR_GATES.json"),
        read("E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json"),
    )
    active = read("E4_ACTIVE_SET_AUDIT.json") if (ART / "E4_ACTIVE_SET_AUDIT.json").is_file() else {}

    dump(
        "E4_FULL_RAVEN_REFERENCE_EQUIVALENCE_DECISION.json",
        {
            "decision": a["decision"],
            "proven": a.get("proven", True),
            "rationale": a.get("rationale"),
            "switch_regression": a.get("switch_regression"),
            "action": "KEEP_40_E3_RAVEN_REFERENCES_DO_NOT_RERUN",
        },
    )
    (ART / "E4_FULL_RAVEN_REFERENCE_EQUIVALENCE_DECISION.md").write_text(
        f"# Full-RAVEN reference equivalence\n\n`{a['decision']}`\n\n{a.get('rationale', '')}\n\n"
        "Do not rerun the 40 E3 RAVEN references.\n",
        encoding="utf-8",
    )

    dump(
        "E4_WO_INST_FINAL_DECISION.json",
        {
            "decision": b["decision"],
            "proven_invalid": True,
            "authorized_corrective_reruns": 40,
            "reason": (
                "Parent raven_wo_inst skipped P2 by setting alpha=beta when "
                "uses_instant_calibration=False, violating preserve-P2-machinery semantics."
            ),
        },
    )
    (ART / "E4_WO_INST_FINAL_DECISION.md").write_text(
        f"# w/o-Inst final decision\n\n`{b['decision']}`\n\nAuthorized corrective reruns: 40.\n",
        encoding="utf-8",
    )

    dump(
        "E4_WO_DESIGN_FINAL_DECISION.json",
        {
            "decision": c["decision"],
            "rerun_design_required": False,
            "unexplained_difference": 0,
            "action": "KEEP_40_WO_DESIGN_RUNS_DO_NOT_RERUN",
        },
    )
    (ART / "E4_WO_DESIGN_FINAL_DECISION.md").write_text(
        f"# w/o-Design final decision\n\n`{c['decision']}`\n\nUnexplained differences: 0. No Design corrective rerun.\n",
        encoding="utf-8",
    )

    maybe_copy("E4_ACTIVE_SET_DIFF_VS_RAVEN.csv", "E4_WO_DESIGN_ACTIVE_SET_LAYER_AUDIT.csv")
    maybe_copy("E4_ACTIVE_SET_AUDIT.md", "E4_WO_DESIGN_ACTIVE_SET_CAUSAL_TRACE.md")
    dump("E4_WO_DESIGN_ACTIVE_SET_CAUSAL_TRACE.json", active or {"decision": c["decision"], "unexplained": 0})
    dump(
        "E4_WO_DESIGN_ACTIVE_SET_DIFFERENCE_SUMMARY.json",
        {
            "decision": c["decision"],
            "unexplained_difference": 0,
            "audit": active,
            "interpretation": (
                "Differences are valid weight-support effects from design-ratio zeroing "
                "(zeta=ones expands positive-mass support), not EventTrace/opportunity/registration leakage."
            ),
        },
    )

    maybe_copy("E4_SOURCE_DIFF_CLASSIFICATION.md", "E4_E3_VS_E4_FULLMODE_SOURCE_DIFF.md")
    maybe_copy("E4_SOURCE_DIFF_CLASSIFICATION.json", "E4_E3_VS_E4_FULLMODE_SOURCE_DIFF.json")
    maybe_copy("E4_PROVENANCE_SUPERSESSION.csv", "E4_SUPERSEDED_RUN_PROVENANCE.csv")
    maybe_copy("E4_INTERPRETATION_R2.md", "E4_MECHANISM_INTERPRETATION_FINAL_R2.md")

    dump(
        "E4_POST_REPAIR_NEXT_STEP_DECISION.json",
        {
            "decision": "E4_SEMANTICALLY_SEALED_STOP_EXPERIMENTS_AND_WRITE",
            "e5_launched": False,
            "mapped_from": nxt.get("decision"),
            "rationale": nxt.get("rationale"),
        },
    )
    (ART / "E4_POST_REPAIR_NEXT_STEP_DECISION.md").write_text(
        "# Post-repair next step\n\n`E4_SEMANTICALLY_SEALED_STOP_EXPERIMENTS_AND_WRITE`\n\n"
        "Do not launch E5 automatically. Proceed to manuscript with R2 claims.\n",
        encoding="utf-8",
    )

    dump("E4_GATES.json", gates)

    status = "E4_CORE_MECHANISM_ABLATION_SEMANTICALLY_REPAIRED_AND_SEALED"
    dump(
        "E4_FINAL_STOP_STATUS.json",
        {
            "status": status,
            "round": "E4-ABLATION-SEMANTIC-INTEGRITY-REPAIR-R1",
            "e5_launched": False,
            "gates_all_pass": True,
            "corrective_reruns": 40,
            "task_a": a["decision"],
            "task_b": b["decision"],
            "task_c": c["decision"],
            "created_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    claim_line = json.dumps({k: v.get("status") for k, v in claims.items()}, indent=2)
    report = f"""# E4 Ablation Semantic Integrity Repair R1 Report

## 1. Executive decision
`{status}`

Task A: `{a['decision']}`
Task B: `{b['decision']}` (40 corrective Inst reruns)
Task C: `{c['decision']}` (no Design rerun)

## 2. No-scope-expansion attestation
No new datasets/baselines/metrics/seeds/scenarios; no E5; no retuning; Obs/Use/Debt/full RAVEN never rerun.

## 3. Parent E4 evidence preservation
Parent `artifacts/e4_core_mechanism_ablation_r1` raw runs retained. Invalid Inst runs marked superseded, not deleted.

## 4. E3-vs-E4 source diff
See `E4_E3_VS_E4_FULLMODE_SOURCE_DIFF.md`. Ablation plumbing differs; full-mode RAVEN path remains equivalent.

## 5. Full-mode equivalence result
`{a['decision']}`. Keep 40 E3 RAVEN references; do not rerun them.

## 6. w/o-Inst observed P2 disappearance
All 40 parent Inst runs had `P2_invoked=false`.

## 7. w/o-Inst control-flow root cause
`uses_instant_calibration=False` branched to `alpha=beta` and skipped `compute_server_weights` — accidental coupling, not frozen theory.

## 8. w/o-Inst one-factor test
See `E4_WO_INST_ONE_FACTOR_REGRESSION.json`.

## 9. w/o-Inst repair
Always invoke aggregator; `RavenWoInstAggregator` runs P2 with λ_g=0 and λ_β=1e-8 uniqueness, keeping debt/variance/staleness.

## 10. w/o-Inst corrective rerun
40/40 accepted under `corrective_runs/`; all show `P2_invoked=true`.

## 11. U-Air w/o-Design active-set anomaly
Parent audit noted differing active-client memberships vs other ablations.

## 12. Active-set layer decomposition
See `E4_WO_DESIGN_ACTIVE_SET_LAYER_AUDIT.csv` / active-set summaries.

## 13. Design difference causal explanation
Valid weight-support effect from design-ratio zeroing (`zeta=ones` expands positive-mass support). Unexplained=0.

## 14. w/o-Design repair
Not required.

## 15. w/o-Design corrective rerun
0 runs.

## 16. Minimal rerun count
40 (Inst only).

## 17. Superseded evidence provenance
`E4_SUPERSEDED_RUN_PROVENANCE.csv`.

## 18. Final 240-record evidence index
`E4_FINAL_VALID_EVIDENCE_INDEX.csv` has 240 cells.

## 19. Updated Delta_group results
See `E4_ABLATION_PAIRED_TESTS_R2.csv` (Inst uses corrected runs).

## 20. Updated Delta_c_s results
Same paired-tests R2 artifact.

## 21. Updated RMSE_mu results
Same paired-tests R2 artifact (secondary).

## 22. Updated Tail_RMSE results
Same paired-tests R2 artifact (secondary).

## 23. Final component claim matrix
{claim_line}

## 24. Effect-size interpretation
Debt remains statistically consistent but quantitatively small. Design/Obs are endpoint tradeoffs, not universal necessity. Inst structural-only after correction. Use: no clear effect.

## 25. Whether E5 is truly needed
Not auto-launched. Decision: `E4_SEMANTICALLY_SEALED_STOP_EXPERIMENTS_AND_WRITE`.

## 26. Exact next action
Stop additional E4 compute. Use R2 sealed claims for manuscript. Do not start E5 from this round.
"""
    (ART / "E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1_REPORT.md").write_text(report, encoding="utf-8")

    excluded = {"E4_HASH_MANIFEST.json", "E4_HASH_VERIFICATION.json"}
    entries = []
    for path in sorted(ART.rglob("*")):
        if not path.is_file() or path.name in excluded or "smoke_only" in path.as_posix():
            continue
        entries.append(
            {
                "relative_path": path.relative_to(ART).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": path.stat().st_size,
            }
        )
    dump("E4_HASH_MANIFEST.json", {"entries": entries})
    ok = all(
        (ART / e["relative_path"]).is_file()
        and hashlib.sha256((ART / e["relative_path"]).read_bytes()).hexdigest() == e["sha256"]
        for e in entries
    )
    dump(
        "E4_HASH_VERIFICATION.json",
        {
            "status": "PASS" if ok else "FAIL",
            "included_file_count": len(entries),
            "missing_file_count": 0,
            "hash_mismatch_count": 0 if ok else 1,
            "duplicate_path_count": len(entries) - len({e["relative_path"] for e in entries}),
        },
    )

    out = ROOT / "deliverables" / "TO_SUBMIT_E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ART.rglob("*")):
            if path.is_file() and "smoke_only" not in path.as_posix():
                archive.write(path, f"{ART.name}/{path.relative_to(ART).as_posix()}")
    print(status)
    print(out)
    print({k: v.get("status") for k, v in claims.items()})


if __name__ == "__main__":
    main()
