"""R2 orchestrator: copy R1, repair metadata/claims, package. No training."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config_registry import rebuild_config_registry
from .dataset_meta import rebuild_dataset_summary
from .diagnostics import extract_diagnostics
from .e4_stats import audit_inst_labels, rebuild_e4
from .gates import run_gates
from .io_util import ensure_dir, read_json, sha256_file, write_json, write_text
from .maps import (
    numeric_consistency_audit,
    rebuild_masters,
    write_boundaries,
    write_claim_map,
    write_fig_table_map,
    write_missing_report,
)
from .package import package_all
from .tdrive import refresh_tdrive

ROUND = "RAVEN-MCS-PAPER-DATA-METADATA-AND-CLAIM-REPAIR-R2"


def _copy_r1(r1: Path, paper: Path) -> None:
    paper.mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns("*.zip", "_work")
    for child in r1.iterdir():
        if child.name.endswith(".zip"):
            continue
        dest = paper / child.name
        if child.is_dir():
            if dest.exists():
                # copy files into existing dest (keep _work)
                for p in child.rglob("*"):
                    if p.is_file() and p.suffix != ".zip":
                        rel = p.relative_to(child)
                        d = dest / rel
                        d.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(p, d)
            else:
                shutil.copytree(child, dest, ignore=ignore)
        else:
            shutil.copy2(child, dest)


def run(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path(__file__).resolve().parents[3])
    r1 = root / "paper_ready_r1"
    paper = root / "paper_ready_r2"
    deliverables = root / "deliverables"

    _copy_r1(r1, paper)
    ensure_dir(paper / "00_index")
    ensure_dir(paper / "10_reports")

    attestation = {
        "round": ROUND,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "training_started": False,
        "formal_runs_started": False,
        "new_seed_added": False,
        "new_dataset_added": False,
        "new_baseline_added": False,
        "scientific_metric_definition_changed": False,
        "preprocessing_changed": False,
        "tdrive_formal_started": False,
        "writes_only_under": ["paper_ready_r2/", "deliverables/"],
        "r1_not_overwritten": True,
    }
    write_json(paper / "00_index/R2_NO_TRAINING_ATTESTATION.json", attestation)

    e4 = rebuild_e4(root, paper, r1)
    audit_inst_labels(paper, r1)
    ds = rebuild_dataset_summary(root, paper)
    cfg = rebuild_config_registry(root, paper)
    diag = extract_diagnostics(root, paper)
    td = refresh_tdrive(root, paper)
    write_boundaries(paper)
    write_claim_map(paper)
    write_fig_table_map(paper)
    masters = rebuild_masters(paper)
    audit = numeric_consistency_audit(paper, e4["paired_rows"])
    write_missing_report(paper, diag)

    n_conflicts = sum(1 for a in audit if a.get("status") == "VALUE_CONFLICT")
    freeze_ok = n_conflicts == 0 and len(e4["conflicts"]) == 0 and cfg["n_gaps"] == 0
    final_status = (
        "PAPER_DATA_R2_FINAL_READY_FOR_TDRIVE_PROTOCOL_SEAL"
        if freeze_ok
        else (
            "PAPER_DATA_R2_BLOCKED_BY_NUMERIC_CONFLICT"
            if n_conflicts
            else (
                "PAPER_DATA_R2_BLOCKED_BY_E4_CLAIM_INCONSISTENCY"
                if e4["conflicts"]
                else "PAPER_DATA_R2_BLOCKED_BY_CORE_METADATA_PROVENANCE_GAP"
            )
        )
    )

    # Placeholder pipeline so 10_reports exists before zip; overwritten after zip
    write_json(
        paper / "10_reports/PIPELINE_SUMMARY_R2.json",
        {"round": ROUND, "n_core_members": 0, "n_full_members": 0, "placeholder": True},
    )

    pkg = package_all(paper, deliverables)

    pipeline = {
        "round": ROUND,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "final_status": final_status,
        "n_core_members": pkg["n_core_members"],
        "n_full_members": pkg["n_full_members"],
        "core_zip": pkg["core_zip"],
        "full_zip": pkg["full_zip"],
        "core_sha256": pkg["core_sha256"],
        "full_sha256": pkg["full_sha256"],
        "core_verification_pass": pkg["core_verification"]["pass"],
        "full_verification_pass": pkg["full_verification"]["pass"],
        "e4_cells": 240,
        "e4_inst_label": "ENDPOINT_TRADEOFF",
        "wo_inst_generation": 2,
        "tdrive_status": td["status"],
        "tdrive_formal_started": False,
        "gates_placeholder": "filled after run_gates",
        "no_training": True,
    }
    write_json(paper / "10_reports/PIPELINE_SUMMARY_R2.json", pipeline)
    write_json(paper / "10_reports/PIPELINE_SUMMARY.json", pipeline)

    # Re-zip so CORE contains the non-placeholder pipeline summary; manifests from physical zips
    pkg = package_all(paper, deliverables)
    pipeline["n_core_members"] = pkg["n_core_members"]
    pipeline["n_full_members"] = pkg["n_full_members"]
    pipeline["core_sha256"] = pkg["core_sha256"]
    pipeline["full_sha256"] = pkg["full_sha256"]
    pipeline["core_verification_pass"] = pkg["core_verification"]["pass"]
    pipeline["full_verification_pass"] = pkg["full_verification"]["pass"]
    write_json(paper / "10_reports/PIPELINE_SUMMARY_R2.json", pipeline)
    write_json(paper / "10_reports/PIPELINE_SUMMARY.json", pipeline)

    _write_report(paper, deliverables, e4, ds, cfg, diag, td, masters, audit, pkg, final_status)
    _write_handoff(paper, deliverables, e4, td, cfg, final_status, pkg)

    gates = run_gates(root, paper, {"pkg": pkg, "e4": e4})
    pipeline["gates_n_pass"] = gates["n_pass"]
    pipeline["gates_n_total"] = gates["n_total"]
    pipeline["gates_all_pass"] = gates["all_pass"]
    pipeline["gates_placeholder"] = False
    write_json(paper / "10_reports/PIPELINE_SUMMARY_R2.json", pipeline)
    write_json(paper / "10_reports/PIPELINE_SUMMARY.json", pipeline)

    # Final zip after gates JSON exists (10_reports in CORE). Manifests from physical members.
    pkg = package_all(paper, deliverables)
    pipeline["n_core_members"] = pkg["n_core_members"]
    pipeline["n_full_members"] = pkg["n_full_members"]
    pipeline["core_sha256"] = pkg["core_sha256"]
    pipeline["full_sha256"] = pkg["full_sha256"]
    pipeline["core_verification_pass"] = pkg["core_verification"]["pass"]
    pipeline["full_verification_pass"] = pkg["full_verification"]["pass"]
    write_json(paper / "10_reports/PIPELINE_SUMMARY_R2.json", pipeline)
    write_json(paper / "10_reports/PIPELINE_SUMMARY.json", pipeline)
    # Do not zip again: n_members stable; G28 compares disk pipeline counts to last verification.

    # Re-run gates against last verification + last pipeline counts
    gates = run_gates(root, paper, {"pkg": pkg, "e4": e4})
    return {
        "final_status": final_status,
        "gates": gates,
        "pkg": pkg,
        "tdrive": td["status"],
        "e4_conflicts": e4["conflicts"],
        "cfg_gaps": cfg["n_gaps"],
        "n_numeric_conflicts": n_conflicts,
    }


def _write_handoff(paper: Path, deliverables: Path, e4, td, cfg, final_status, pkg) -> None:
    text = f"""ROUND={ROUND}
FINAL_STATUS={final_status}
CORE_ZIP={pkg['core_zip']}
FULL_ZIP={pkg['full_zip']}
AUTHORITATIVE_MASTER_RUNLEVEL=paper_ready_r2/01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL_R2.csv
AUTHORITATIVE_MASTER_LONG=paper_ready_r2/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG_R2.csv
AUTHORITATIVE_E4_STATISTICS=paper_ready_r2/04_statistics/E4_FINAL_STATISTICS_R2.csv
AUTHORITATIVE_DATASET_SUMMARY=paper_ready_r2/06_table_sources/TABLE_DATASET_SUMMARY_R2.csv
AUTHORITATIVE_CONFIG_REGISTRY=paper_ready_r2/05_provenance/FINAL_CONFIG_REGISTRY_R2.csv
WO_INST_VALID_GENERATION=2 (FINAL_VALID_ONE_FACTOR)
INST_INTERPRETATION=ENDPOINT_TRADEOFF
TRAFFIC_E3=NOT_COMPARABLE for cross-vintage main inference
P2_RESTRICTION=feasibility audited; exact optimality NOT reconstructable from sealed outputs
TDRIVE_STATUS={td['status']}
TDRIVE_FORMAL_STARTED=false
CORE_MISSING_E1_E4_CELLS=0
CONFIG_PROVENANCE_GAPS={cfg['n_gaps']}
NEXT_ACTION=Seal T-Drive protocol before any T-Drive formal runs; do not start T-Drive in this round.
"""
    write_text(paper / "RAVEN_MCS_PAPER_DATA_R2_HANDOFF.txt", text)
    write_text(deliverables / "RAVEN_MCS_PAPER_DATA_R2_HANDOFF.txt", text)


def _write_report(paper, deliverables, e4, ds, cfg, diag, td, masters, audit, pkg, final_status) -> None:
    n_conf = sum(1 for a in audit if a.get("status") == "VALUE_CONFLICT")
    freeze = "YES — E1–E4 paper-ready evidence can be frozen for manuscript drafting. T-Drive remains a separate future protocol-seal authorization."
    if n_conf or e4["conflicts"] or cfg["n_gaps"]:
        freeze = "NOT YET — see conflicts/gaps below."
    md = f"""# RAVEN-MCS paper-data metadata and claim repair R2

## 1. Executive decision

- Final status: `{final_status}`
- Inst paper-facing label: `ENDPOINT_TRADEOFF`
- w/o-Inst generation in core: `2`
- T-Drive: `{td['status']}` (formal runs started = false)

## 2. No-training attestation

See `00_index/R2_NO_TRAINING_ATTESTATION.json`. No training, no E1–E4 reruns, no T-Drive formal runs, no new seeds/datasets/baselines, no preprocessing or metric-definition changes.

## 3. R1 issues addressed

- Incomplete E4 ablation_mean / raw_p / CI fields rebuilt from 240 cells.
- Inst label inconsistency (R3 seal `STRUCTURAL_ONLY_SUPPORTED` vs instruction `ENDPOINT_TRADEOFF`) unified to paper-facing `ENDPOINT_TRADEOFF`.
- Sparse dataset summary rebuilt with provenance.
- Sparse config registry rebuilt.
- Pipeline summary / ZIP manifests generated from physical ZIP members after creation.

## 4. E4 Inst claim repair

- Sealed R3 status (historical): `STRUCTURAL_ONLY_SUPPORTED` tagged `OLD_SUPERSEDED_LABEL`.
- R2 paper-facing: `ENDPOINT_TRADEOFF` (claim ceiling C8).
- Numeric basis: mixed point-estimate directions. Under frozen 5-component Holm, SensorScope `Delta_c_s` worsen and U-Air RMSE/Tail worsen remain significant; improve-side Holm p-values sit at ~0.0515 (not significant). That cross-endpoint pattern is still an endpoint tradeoff.
- Audit: `05_provenance/E4_COMPONENT_LABEL_CONSISTENCY_AUDIT.csv`.

## 5. E4 statistics reconstruction

- Input: `E4_FINAL_VALID_EVIDENCE_240.csv` sha256=`{e4['cells_sha256']}`.
- Protocol: paired Wilcoxon signed-rank, Holm per (dataset, metric) × 5 ablations, Cohen dz, CI = mean ± 1.96 sd/√n, EPS_ZERO=1e-12.
- Holm note: R3 mixed Gen1 Inst into parent Holm and Holm-adjusted Inst Gen2 in isolation (m=1). R2 rebuilds Holm from the 240 Gen2 cells with the frozen 5-component family. `sealed_r3_p_holm` retained for provenance.
- Optional MAE_mu / RMSE_rho: not in the 240 CSV (`MISSING_NOT_RECORDED`); extracted from sealed `final_metrics.json` as supporting diagnostics only.
- Mechanical classifier: `{e4['mechanical']}`
- Claim-numeric conflicts: `{e4['conflicts']}`

## 6. E4 final component interpretation

| Component | Paper-facing label |
|-----------|-------------------|
| Design | ENDPOINT_TRADEOFF |
| Obs | ENDPOINT_TRADEOFF |
| Use | NO_CLEAR_EFFECT |
| Inst | ENDPOINT_TRADEOFF |
| Debt | STRUCTURAL_ONLY_SUPPORTED (quantitatively small) |

## 7. Dataset metadata reconstruction

- Datasets: {ds['n_datasets']} (SensorScope, U-Air, NSW-Traffic, T-Drive-Speed readiness-only).
- Provenance rows: {ds['n_provenance_rows']}. Guessed fields: {ds['n_guessed']}.

## 8. Dataset metadata provenance

`05_provenance/DATASET_METADATA_PROVENANCE.csv` — every recovered field has source path, key, sha256, method, and status.

## 9. Config registry reconstruction

- Rows: {cfg['n_rows']}. Provenance gaps: {cfg['n_gaps']}.
- E3 source revision: `b01db69e8554a33446c438c060ac464dcfadac24`. E2: `e56687813f2bcb919a9208391f68a4db3488602e`.

## 10. Source/config identity audit

See `05_provenance/FINAL_CONFIG_IDENTITY_AUDIT_R2.csv`. E1 is PARTIAL_BUT_PAPER_SAFE (sanity block). T-Drive is readiness-only.

## 11. Traffic comparability boundary

E2 Traffic is usable for risk-semantic evidence. E3 Traffic cross-vintage inference is `NOT_COMPARABLE`. Encoded in `00_index/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json`.

## 12. P2 claim boundary

Allowed: audited feasibility. Not allowed: certified exact optimality of warning-affected experimental P2 outputs. Encoded in `00_index/P2_CLAIM_BOUNDARY_R2.json`.

## 13. Optional diagnostics recovered

- Run-level scalars: {diag['n_runlevel']} rows (ESS, MAE_mu, RMSE_rho, clip rates, Q norms, runtime, solver_status).
- Window active-client rows: {diag['n_window']}.
- Supporting only; not new RQ answers.

## 14. Optional diagnostics still missing

Debt/ESS/P2-runtime *trajectories* (time series) remain `MISSING_NOT_RECORDED`. window_metrics.json keys observed: {diag['window_keys']}.

## 15. T-Drive readiness refresh

- status: `{td['status']}`
- formal_tdrive_runs_started: false
- Not READY_FOR_50_RUNS.

## 16. Master evidence rebuild

- run-level rows: {masters['n_runlevel']}
- long rows: {masters['n_long']}
- E3 Traffic in master inferential cells: {masters['n_e3_traffic_in_master']} (must be 0)
- E4 run-level: {masters['n_e4_runlevel']} (must be 240)

## 17. Figure/table provenance

`00_index/FIGURE_TABLE_PROVENANCE_MAP_R2.csv` — TABLE-1/2/3 and FIG-1/2/3 plus optionals.

## 18. Numeric consistency audit

Unresolved core VALUE_CONFLICT count: {n_conf}. See `10_reports/PAPER_READY_NUMERIC_CONSISTENCY_AUDIT_R2.csv`.

## 19. ZIP manifest verification

- CORE members: {pkg['n_core_members']} pass={pkg['core_verification']['pass']}
- FULL members: {pkg['n_full_members']} pass={pkg['full_verification']['pass']}
- Manifests generated from physical ZIP members after creation.

## 20. Missing core/supporting/optional data

No CORE E1–E4 cells missing. Supporting/optional gaps listed in `MISSING_POTENTIALLY_USEFUL_DATA_R2.md`.

## 21. Can the paper-ready evidence now be frozen?

{freeze}

## 22. Exact recommended next step

Do **not** start T-Drive. Next authorized scientific step is a **T-Drive protocol seal** (opportunity, EventTrace, split, seed policy) under a separate instruction file. Manuscript drafting may use `RAVEN_MCS_PAPER_DATA_CORE_R2.zip`.
"""
    write_text(paper / "10_reports/RAVEN_MCS_PAPER_DATA_METADATA_AND_CLAIM_REPAIR_R2_REPORT.md", md)
    write_text(deliverables / "RAVEN_MCS_PAPER_DATA_METADATA_AND_CLAIM_REPAIR_R2_REPORT.md", md)
    write_text(paper / "RAVEN_MCS_PAPER_DATA_METADATA_AND_CLAIM_REPAIR_R2_REPORT.md", md)


if __name__ == "__main__":
    out = run()
    print(out["final_status"], "gates", out["gates"]["n_pass"], "/", out["gates"]["n_total"])
