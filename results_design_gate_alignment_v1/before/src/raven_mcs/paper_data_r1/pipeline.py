"""End-to-end paper-data clean-and-package pipeline."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import STATUS_A, STATUS_B, STATUS_C, STATUS_D, ROUND
from .collect_e1 import collect_e1
from .collect_e2 import collect_e2
from .collect_e3 import collect_e3
from .collect_e4 import collect_e4
from .discover import discover_sources
from .gates import run_gates
from .io_util import ensure_dir, read_csv, write_csv, write_json, write_text
from .masters import build_masters
from .package_zips import package_all
from .tables import build_tables_and_figures
from .tdrive_readiness import audit_tdrive


def _git_rev(root: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(root), text=True)
            .strip()
        )
    except Exception:  # noqa: BLE001
        return "UNKNOWN"


def _ensure_tree(paper: Path) -> None:
    for rel in (
        "00_index",
        "01_core_data/e1",
        "01_core_data/e2",
        "01_core_data/e3",
        "01_core_data/e4",
        "01_core_data/master",
        "02_supporting_data/e0_correctness",
        "02_supporting_data/e1",
        "02_supporting_data/e2",
        "02_supporting_data/e3",
        "02_supporting_data/e4",
        "02_supporting_data/solver",
        "02_supporting_data/runtime",
        "02_supporting_data/diagnostics",
        "03_raw_evidence/e1",
        "03_raw_evidence/e2",
        "03_raw_evidence/e3",
        "03_raw_evidence/e4",
        "03_raw_evidence/source_snapshots",
        "04_statistics",
        "05_provenance",
        "06_table_sources",
        "07_figure_sources",
        "08_tdrive_readiness",
        "09_archive_manifest",
        "10_reports/previews",
    ):
        ensure_dir(paper / rel)


def _supporting_diagnostics(root: Path, paper: Path, missing: list[dict[str, Any]]) -> None:
    # Theory diagnostic availability (no reconstruction unless unambiguous)
    rows = []
    quantities = [
        "debt_bound",
        "epsilon_reach_B",
        "variance_proxy",
        "calibration_residual",
        "ESS_trajectory",
        "target_composition_trajectory",
        "debt_trajectory",
        "P2_objective_components",
    ]
    for q in quantities:
        rows.append(
            {
                "quantity": q,
                "E1_available": "PARTIAL" if q in {"ESS_trajectory", "calibration_residual"} else "MISSING_NOT_RECORDED",
                "E2_available": "PARTIAL" if q in {"ESS_trajectory"} else "MISSING_NOT_RECORDED",
                "E3_available": "PARTIAL",
                "E4_available": "PARTIAL",
                "raw_inputs_available": "UNKNOWN",
                "offline_reconstruction_possible": "false",
                "scientific_definition_frozen": "UNKNOWN",
                "paper_use_recommendation": "SUPPORTING_ONLY_IF_SEALED",
                "notes": "No unambiguous offline reconstruction performed this round",
            }
        )
    write_csv(paper / "02_supporting_data" / "diagnostics" / "THEORY_DIAGNOSTIC_AVAILABILITY.csv", rows)

    # Runtime
    runtime_rows = []
    e2_rt = root / "artifacts/e2_traffic_formal_runs_r1/formal_runtime_metrics.csv"
    if e2_rt.is_file():
        for r in read_csv(e2_rt):
            rr = dict(r)
            rr["round"] = "E2"
            runtime_rows.append(rr)
    write_csv(paper / "02_supporting_data" / "runtime" / "RUNTIME_MASTER.csv", runtime_rows)
    write_csv(
        paper / "02_supporting_data" / "runtime" / "SYSTEM_DIAGNOSTIC_AVAILABILITY.csv",
        [
            {
                "quantity": "total_runtime",
                "available": bool(runtime_rows),
                "notes": "from sealed E2 formal_runtime_metrics where present",
            },
            {
                "quantity": "memory",
                "available": False,
                "notes": "MISSING_NOT_RECORDED",
            },
            {
                "quantity": "communication_bytes",
                "available": False,
                "notes": "MISSING_NOT_RECORDED for most rounds",
            },
        ],
    )

    # E0 placeholder
    write_text(
        paper / "02_supporting_data" / "e0_correctness" / "README.md",
        "# E0 correctness\n\nNo dedicated E0 sealed package collected beyond discovery index references.\n",
    )


def _dictionary_and_index(paper: Path) -> None:
    idx = paper / "00_index"
    dict_rows = [
        {
            "term": "RMSE_mu",
            "definition": "Deployment-target RMSE under target measure mu",
            "unit": "target units",
            "lower_better": "True",
            "datasets": "all",
            "rounds": "E1-E4",
            "formula_source": "sealed metric definitions",
            "na_semantics": "empty value + status",
        },
        {
            "term": "RMSE_rho",
            "definition": "Arrival/usable-update risk under sampling measure rho",
            "unit": "target units",
            "lower_better": "True",
            "datasets": "where defined",
            "rounds": "E1-E3",
            "formula_source": "sealed",
            "na_semantics": "NOT_COMPARABLE on Traffic E3 cross-vintage",
        },
        {
            "term": "MAE_mu",
            "definition": "Mean absolute error under target measure",
            "unit": "target units",
            "lower_better": "True",
            "datasets": "where recorded",
            "rounds": "E3 primarily",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED if absent",
        },
        {
            "term": "Tail_RMSE",
            "definition": "Tail-group RMSE",
            "unit": "target units",
            "lower_better": "True",
            "datasets": "where recorded",
            "rounds": "E1-E4",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED if absent",
        },
        {
            "term": "Delta_group",
            "definition": "Structural group disparity / mismatch",
            "unit": "ratio/gap as sealed",
            "lower_better": "True",
            "datasets": "SensorScope,U-Air,E1",
            "rounds": "E1,E3,E4",
            "formula_source": "sealed",
            "na_semantics": "empty+status",
        },
        {
            "term": "Delta_c_s",
            "definition": "Structural stratum mismatch",
            "unit": "as sealed",
            "lower_better": "True",
            "datasets": "SensorScope,U-Air",
            "rounds": "E3,E4",
            "formula_source": "sealed",
            "na_semantics": "empty+status",
        },
        {
            "term": "Delta_pair",
            "definition": "Paired target metric delta",
            "unit": "as sealed",
            "lower_better": "context",
            "datasets": "where recorded",
            "rounds": "E3",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "D_aligned",
            "definition": "Delta RMSE_mu - Delta RMSE_rho on Complete-aligned",
            "unit": "risk units",
            "lower_better": "context (sign/direction evidence)",
            "datasets": "NSW-Traffic",
            "rounds": "E2",
            "formula_source": "COMPLETE_ALIGNED_DOD",
            "na_semantics": "n/a",
        },
        {
            "term": "ESS",
            "definition": "Effective sample size",
            "unit": "count",
            "lower_better": "False",
            "datasets": "where recorded",
            "rounds": "E3+",
            "formula_source": "sealed metrics",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "n_eff",
            "definition": "Effective update count / ESS proxy",
            "unit": "count",
            "lower_better": "False",
            "datasets": "where recorded",
            "rounds": "E3+",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "debt_norm",
            "definition": "Debt norm / normalized debt",
            "unit": "as sealed",
            "lower_better": "context",
            "datasets": "where recorded",
            "rounds": "E1/E4 supporting",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "calibration_residual",
            "definition": "Instant calibration residual",
            "unit": "as sealed",
            "lower_better": "True",
            "datasets": "where recorded",
            "rounds": "supporting",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "runtime",
            "definition": "Wall-clock runtime",
            "unit": "seconds",
            "lower_better": "True",
            "datasets": "where recorded",
            "rounds": "E1-E4",
            "formula_source": "sealed",
            "na_semantics": "MISSING_NOT_RECORDED",
        },
        {
            "term": "P2_residual",
            "definition": "P2 feasibility residual",
            "unit": "as sealed",
            "lower_better": "True",
            "datasets": "P2 methods",
            "rounds": "E3/E4 supporting",
            "formula_source": "solver audits",
            "na_semantics": "optimality not reconstructable",
        },
    ]
    write_csv(idx / "PAPER_DATA_DICTIONARY.csv", dict_rows)
    write_text(
        idx / "PAPER_DATA_DICTIONARY.md",
        "\n".join(
            ["# Paper data dictionary", ""]
            + [f"- **{r['term']}**: {r['definition']} ({r['na_semantics']})" for r in dict_rows]
            + [""]
        ),
    )
    write_text(
        idx / "PAPER_DATA_PACKAGE_INDEX.md",
        "\n".join(
            [
                f"# {ROUND} package index",
                "",
                "## Layers",
                "- PAPER_CORE: `01_core_data/`, `06_table_sources/`, `07_figure_sources/`",
                "- PAPER_SUPPORTING: `02_supporting_data/`",
                "- FULL_ARCHIVE: `03_raw_evidence/` + supporting + provenance",
                "",
                "## Source of truth for paper numbers",
                "- `01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv`",
                "- `01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv`",
                "",
                "## Packages",
                "- `RAVEN_MCS_PAPER_DATA_CORE_R1.zip`",
                "- `RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R1.zip`",
                "",
            ]
        ),
    )


def _write_reports(
    root: Path,
    paper: Path,
    deliverables: Path,
    *,
    statuses: dict[str, Any],
    tdrive: dict[str, Any],
    pack: dict[str, Any],
    gates: dict[str, Any],
    missing: list[dict[str, Any]],
    final_status: str,
) -> None:
    reports = paper / "10_reports"
    write_csv(reports / "MISSING_POTENTIALLY_USEFUL_DATA.csv", missing)
    write_text(
        reports / "MISSING_POTENTIALLY_USEFUL_DATA.md",
        "\n".join(
            ["# Missing potentially useful data", ""]
            + (
                [
                    f"- **{m['item']}** ({m['importance']}): expected `{m['expected_source']}` — {m['recommended_action']}"
                    for m in missing
                ]
                if missing
                else ["- None recorded beyond optional trajectory fields."]
            )
            + [""]
        ),
    )
    write_text(
        reports / "EXTRA_DATA_COLLECTED.md",
        "\n".join(
            [
                "# Extra data collected (may not enter main paper tables)",
                "",
                "- E2 scenario summaries, counteracting evidence, ledger audits",
                "- E3 Local-Hajek provenance proofs and P2 solver audits",
                "- E4 Gen0/Gen1 superseded wo_inst archives",
                "- E4 Design 774-window layer audit",
                "- Runtime metrics from E2 formal_runtime_metrics",
                "- Theory-diagnostic availability inventory",
                "- Source snapshots of critical sealed CSVs/JSONs",
                "- Full claim matrices and gate/report copies under 03_raw_evidence",
                "",
            ]
        ),
    )

    lines = [
        f"# {ROUND} Report",
        "",
        "## 1. Executive summary",
        f"- Final status: `{final_status}`",
        f"- E2 runs: {statuses.get('E2', {}).get('n_valid_runs')}; EventTraces: {statuses.get('E2', {}).get('n_eventtraces')}",
        f"- E3 index rows: {statuses.get('E3', {}).get('n_index_rows')} (formal+reused)",
        f"- E4 core cells: {statuses.get('E4', {}).get('n_core_cells')} (wo_inst Gen2 only in core)",
        f"- Gates: {gates.get('n_pass')}/{gates.get('n_gates')} pass",
        "",
        "## 2. No-training/no-rerun attestation",
        "- training_started=false",
        "- formal_runs_started=false",
        "- No E1/E2/E3/E4 reruns; no T-Drive formal runs; no E5+.",
        "",
        "## 3. Source roots discovered",
        "- See `00_index/ALL_RELEVANT_SOURCE_PATHS.csv`",
        "",
        "## 4. E1 collection status",
        f"- {statuses.get('E1')}",
        "",
        "## 5. E2 collection status",
        f"- {statuses.get('E2')}",
        "",
        "## 6. E3 collection status",
        f"- {statuses.get('E3')}",
        "",
        "## 7. E4 collection status",
        f"- {statuses.get('E4')}",
        "",
        "## 8. w/o-Inst generation handling",
        "- Gen0 INVALID_P2_OFF → FULL_ARCHIVE only",
        "- Gen1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH → FULL_ARCHIVE only",
        "- Gen2 FINAL_VALID_ONE_FACTOR → PAPER_CORE (40 cells)",
        "",
        "## 9. Traffic comparability handling",
        "- E2 Traffic: paper-core for risk non-interchangeability",
        "- E3 Traffic: NOT_COMPARABLE_CROSS_VINTAGE; supporting/reference only",
        "",
        "## 10. Local-Hajek provenance",
        "- Collected under `02_supporting_data/e3/` and `03_raw_evidence/e3/local_hajek/`",
        "",
        "## 11. P2 solver evidence",
        "- Collected under `02_supporting_data/solver/`",
        "",
        "## 12. Theory-diagnostic availability",
        "- See `02_supporting_data/diagnostics/THEORY_DIAGNOSTIC_AVAILABILITY.csv`",
        "",
        "## 13. Runtime/system data availability",
        "- See `02_supporting_data/runtime/`",
        "",
        "## 14. T-Drive readiness",
        f"- status=`{tdrive.get('status')}`",
        f"- blockers={tdrive.get('blockers')}",
        "",
        "## 15. Master evidence table status",
        "- `01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv`",
        "- `01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv`",
        "",
        "## 16. Main table-source files",
        "- `06_table_sources/TABLE_E*.csv` (+ meta JSON)",
        "",
        "## 17. Main figure-source files",
        "- `07_figure_sources/FIG1_*.csv`, `FIG2_*.csv`, `FIG3_*.csv`",
        "",
        "## 18. Extra optional data collected",
        "- See `EXTRA_DATA_COLLECTED.md`",
        "",
        "## 19. Missing potentially useful data",
        "- See `MISSING_POTENTIALLY_USEFUL_DATA.md`",
        "",
        "## 20. Package contents",
        f"- CORE: `{pack.get('core_zip')}` members={pack.get('n_core_members')}",
        f"- FULL: `{pack.get('full_zip')}` members={pack.get('n_full_members')}",
        "",
        "## 21. Hash verification",
        f"- CORE pass={pack.get('core_verification', {}).get('pass')}",
        f"- FULL pass={pack.get('full_verification', {}).get('pass')}",
        "",
        "## 22. Recommended next step",
        "- Use CORE zip for paper drafting; consult FULL for audits/appendix.",
        "- T-Drive formal block only after separate authorization if readiness reaches READY.",
        "",
    ]
    report_text = "\n".join(lines)
    write_text(reports / "RAVEN_MCS_PAPER_DATA_CLEAN_AND_PACKAGE_R1_REPORT.md", report_text)
    write_text(deliverables / "RAVEN_MCS_PAPER_DATA_CLEAN_AND_PACKAGE_R1_REPORT.md", report_text)

    handoff = "\n".join(
        [
            f"ROUND={ROUND}",
            f"FINAL_STATUS={final_status}",
            f"CORE_ZIP={pack.get('core_zip')}",
            f"FULL_ZIP={pack.get('full_zip')}",
            "PAPER_PRIORITY_ZIP=RAVEN_MCS_PAPER_DATA_CORE_R1.zip",
            "MASTER_LONG=paper_ready_r1/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv",
            "MASTER_RUNLEVEL=paper_ready_r1/01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv",
            "TRAFFIC_E3=NOT_COMPARABLE for cross-method main inference",
            "WO_INST_VALID_GENERATION=2 (FINAL_VALID_ONE_FACTOR)",
            "RAW_EVIDENCE=paper_ready_r1/03_raw_evidence/",
            f"TDRIVE_STATUS={tdrive.get('status')}",
            f"GATES_PASS={gates.get('n_pass')}/{gates.get('n_gates')}",
            f"CORE_MISSING_ITEMS={len([m for m in missing if m.get('importance')=='CORE'])}",
            "",
        ]
    )
    write_text(deliverables / "RAVEN_MCS_PAPER_DATA_R1_HANDOFF.txt", handoff)
    write_text(paper / "RAVEN_MCS_PAPER_DATA_R1_HANDOFF.txt", handoff)


def run_pipeline(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or Path.cwd())
    paper = root / "paper_ready_r1"
    deliverables = root / "deliverables"
    _ensure_tree(paper)

    missing: list[dict[str, Any]] = []

    # Discovery
    discover_sources(root, paper / "00_index")

    # Immutability attestation
    write_json(
        paper / "05_provenance" / "SOURCE_IMMUTABILITY_ATTESTATION.json",
        {
            "original_files_modified": False,
            "original_files_deleted": False,
            "training_started": False,
            "formal_runs_started": False,
            "scientific_parameters_changed": False,
            "preprocessing_changed": False,
            "workspace_revision": _git_rev(root),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "round": ROUND,
        },
    )

    statuses = {
        "E1": collect_e1(root, paper, missing),
        "E2": collect_e2(root, paper, missing),
        "E3": collect_e3(root, paper, missing),
        "E4": collect_e4(root, paper, missing),
    }
    _supporting_diagnostics(root, paper, missing)
    build_masters(root, paper)
    build_tables_and_figures(paper)
    tdrive = audit_tdrive(root, paper)
    _dictionary_and_index(paper)

    # Always list a few optional missing items explicitly
    for item, importance in (
        ("E4_MAE_mu_per_cell", "OPTIONAL"),
        ("E2_MAE_mu_in_formal_results", "OPTIONAL"),
        ("Debt_trajectory_sealed_csv", "SUPPORTING"),
        ("ESS_trajectory_sealed_csv", "SUPPORTING"),
        ("P2_runtime_trajectory_sealed_csv", "SUPPORTING"),
        ("Dataset_summary_client_counts", "SUPPORTING"),
    ):
        if not any(m.get("item") == item for m in missing):
            missing.append(
                {
                    "item": item,
                    "round": "",
                    "dataset": "",
                    "method": "",
                    "seed": "",
                    "expected_source": "sealed outputs",
                    "importance": importance,
                    "can_be_reconstructed_offline": "false",
                    "requires_new_experiment": "false",
                    "recommended_action": "Leave MISSING_NOT_RECORDED; do not invent",
                }
            )

    # Missing/extra reports must exist before G29/G30
    reports = paper / "10_reports"
    write_csv(reports / "MISSING_POTENTIALLY_USEFUL_DATA.csv", missing)
    write_text(
        reports / "MISSING_POTENTIALLY_USEFUL_DATA.md",
        "\n".join(
            ["# Missing potentially useful data", ""]
            + (
                [
                    f"- **{m['item']}** ({m['importance']}): expected `{m['expected_source']}` — {m['recommended_action']}"
                    for m in missing
                ]
                if missing
                else ["- None recorded beyond optional trajectory fields."]
            )
            + [""]
        ),
    )
    write_text(
        reports / "EXTRA_DATA_COLLECTED.md",
        "\n".join(
            [
                "# Extra data collected (may not enter main paper tables)",
                "",
                "- E2 scenario summaries, counteracting evidence, ledger audits",
                "- E3 Local-Hajek provenance proofs and P2 solver audits",
                "- E4 Gen0/Gen1 superseded wo_inst archives",
                "- E4 Design 774-window layer audit",
                "- Runtime metrics from E2 formal_runtime_metrics",
                "- Theory-diagnostic availability inventory",
                "- Source snapshots of critical sealed CSVs/JSONs",
                "- Full claim matrices and gate/report copies under 03_raw_evidence",
                "",
            ]
        ),
    )

    # Pre-package to enable zip verification gates, then finalize reports and re-package once
    pack = package_all(paper, deliverables)
    ctx = {"e5_started": False, "new_seed_dataset_baseline_metric": False}
    gates = run_gates(root, paper, ctx)

    core_ok = all(
        [
            statuses["E2"].get("core_complete"),
            statuses["E3"].get("core_complete"),
            statuses["E4"].get("core_complete"),
            statuses["E1"].get("core_complete"),
        ]
    )
    if (
        core_ok
        and gates.get("all_pass")
        and pack.get("core_verification", {}).get("pass")
        and pack.get("full_verification", {}).get("pass")
    ):
        final_status = (
            STATUS_A
            if tdrive.get("status") == "READY_FOR_SEPARATE_50_RUN_AUTHORIZATION"
            else STATUS_B
        )
    elif not pack.get("core_verification", {}).get("pass") or not pack.get("full_verification", {}).get("pass"):
        final_status = STATUS_D
    elif not core_ok:
        final_status = STATUS_C
    else:
        final_status = STATUS_C if gates.get("n_fail", 0) > 0 else STATUS_B

    _write_reports(
        root,
        paper,
        deliverables,
        statuses=statuses,
        tdrive=tdrive,
        pack=pack,
        gates=gates,
        missing=missing,
        final_status=final_status,
    )

    # Final package includes reports/handoff; re-verify gates
    pack = package_all(paper, deliverables)
    gates = run_gates(root, paper, ctx)
    if (
        core_ok
        and gates.get("all_pass")
        and pack.get("core_verification", {}).get("pass")
        and pack.get("full_verification", {}).get("pass")
    ):
        final_status = (
            STATUS_A
            if tdrive.get("status") == "READY_FOR_SEPARATE_50_RUN_AUTHORIZATION"
            else STATUS_B
        )

    # Refresh handoff/status only (avoid mutating packaged report body after final zip)
    handoff = "\n".join(
        [
            f"ROUND={ROUND}",
            f"FINAL_STATUS={final_status}",
            f"CORE_ZIP={pack.get('core_zip')}",
            f"FULL_ZIP={pack.get('full_zip')}",
            "PAPER_PRIORITY_ZIP=RAVEN_MCS_PAPER_DATA_CORE_R1.zip",
            "MASTER_LONG=paper_ready_r1/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv",
            "MASTER_RUNLEVEL=paper_ready_r1/01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv",
            "TRAFFIC_E3=NOT_COMPARABLE for cross-method main inference",
            "WO_INST_VALID_GENERATION=2 (FINAL_VALID_ONE_FACTOR)",
            "RAW_EVIDENCE=paper_ready_r1/03_raw_evidence/",
            f"TDRIVE_STATUS={tdrive.get('status')}",
            f"GATES_PASS={gates.get('n_pass')}/{gates.get('n_gates')}",
            f"CORE_MISSING_ITEMS={len([m for m in missing if m.get('importance')=='CORE'])}",
            "",
        ]
    )
    write_text(deliverables / "RAVEN_MCS_PAPER_DATA_R1_HANDOFF.txt", handoff)
    write_text(paper / "RAVEN_MCS_PAPER_DATA_R1_HANDOFF.txt", handoff)

    summary = {
        "final_status": final_status,
        "statuses": statuses,
        "tdrive": tdrive,
        "pack": pack,
        "gates": {"n_pass": gates.get("n_pass"), "n_gates": gates.get("n_gates"), "all_pass": gates.get("all_pass")},
        "core_missing": [m for m in missing if m.get("importance") == "CORE"],
    }
    write_json(paper / "10_reports" / "PIPELINE_SUMMARY.json", summary)
    return summary
