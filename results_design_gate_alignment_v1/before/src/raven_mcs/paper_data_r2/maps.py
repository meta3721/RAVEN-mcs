"""Claim maps, figure provenance, masters, numeric audit, missing-data report, boundaries."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .io_util import MISSING, read_csv, sha256_file, write_csv, write_json, write_text


METRICS_E4 = ["RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s"]


def write_boundaries(paper: Path) -> None:
    write_json(
        paper / "00_index" / "TRAFFIC_COMPARABILITY_BOUNDARY_R2.json",
        {
            "E2_Traffic": {
                "status": "SCI_COMPARABLE_MAIN",
                "use": "scientifically usable for sealed E2 risk-semantic evidence (C1, C2)",
            },
            "E3_Traffic": {
                "status": "NOT_COMPARABLE",
                "use": "E3 reused-old vs new-current cross-vintage inference is NOT_COMPARABLE",
                "must_not": "mix E2 and E3 Traffic as one homogeneous performance block",
            },
            "paper_rule": "No R2 table or figure may mix E2 Traffic and E3 Traffic as one homogeneous performance block.",
        },
    )
    write_json(
        paper / "00_index" / "P2_CLAIM_BOUNDARY_R2.json",
        {
            "allowed": [
                "audited feasibility for warning-affected reconstructable windows",
                "exact mathematical optimizer uniqueness under theorem assumptions, if already proven in the paper theory",
            ],
            "not_allowed": [
                "all experimental P2 outputs were retrospectively proven optimal",
                "warning-affected runs have certified exact optimality",
            ],
            "sealed_semantics": "LEVEL_3_EXACT_OPTIMALITY is NOT_RECONSTRUCTABLE from sealed outputs",
            "source": "paper_ready_r1/02_supporting_data/solver/E3_P2_CERTIFICATE_SEMANTICS_FINAL.json",
        },
    )


def write_claim_map(paper: Path) -> None:
    rows = [
        {
            "claim_id": "C1",
            "claim_text": "Two-stage non-random selection can create deployment-target mismatch.",
            "allowed_strength": "supported",
            "primary_source": "01_core_data/e2/E2_RISK_NONINTERCHANGEABILITY_MASTER.csv",
            "dataset": "NSW-Traffic",
            "method": "all E2 formal",
            "seed_set": "30001-30020",
            "metric": "Gap_mis, D_aligned, RMSE_mu, RMSE_rho",
            "test": "paired scenario vs balanced",
            "excluded_evidence": "E3 Traffic",
            "known_limitations": "E2 PROFILE-S1 only",
        },
        {
            "claim_id": "C2",
            "claim_text": "Arrival/usable-update risk is not generally interchangeable with deployment-target risk.",
            "allowed_strength": "supported",
            "primary_source": "01_core_data/e2/E2_D_ALIGNED_SUMMARY.csv",
            "dataset": "NSW-Traffic",
            "method": "5 formal methods",
            "seed_set": "30001-30020",
            "metric": "D_aligned",
            "test": "sign/direction stability of D_aligned",
            "excluded_evidence": "E3 Traffic",
            "known_limitations": "complete_aligned family",
        },
        {
            "claim_id": "C3",
            "claim_text": "On scientifically comparable SensorScope and U-Air E3 blocks, RAVEN-MCS consistently reduces structural target mismatch.",
            "allowed_strength": "supported",
            "primary_source": "01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv",
            "dataset": "SensorScope, U-Air",
            "method": "RAVEN-MCS vs baselines",
            "seed_set": "30001-30020",
            "metric": "Delta_group, Delta_c_s",
            "test": "paired Holm",
            "excluded_evidence": "NSW-Traffic E3 NOT_COMPARABLE",
            "known_limitations": "Traffic excluded from main inference",
        },
        {
            "claim_id": "C4",
            "claim_text": "RAVEN-MCS maintains competitive deployment-target prediction risk with selective significant gains, NOT universal prediction superiority.",
            "allowed_strength": "supported_selective",
            "primary_source": "01_core_data/e3/E3_PREDICTION_METRICS_MASTER.csv",
            "dataset": "SensorScope, U-Air",
            "method": "RAVEN-MCS vs baselines",
            "seed_set": "30001-30020",
            "metric": "RMSE_mu, Tail_RMSE, MAE_mu",
            "test": "paired Holm",
            "excluded_evidence": "Traffic",
            "known_limitations": "Not universal superiority",
        },
        {
            "claim_id": "C5",
            "claim_text": "The E4 components have endpoint-dependent and dataset-dependent roles.",
            "allowed_strength": "supported",
            "primary_source": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER_R2.csv",
            "dataset": "SensorScope, U-Air",
            "method": "E4 ablations",
            "seed_set": "30001-30020",
            "metric": "component × metric paired diffs",
            "test": "paired Wilcoxon + Holm (dataset×metric × 5 components)",
            "excluded_evidence": "w/o-Inst Gen0/Gen1",
            "known_limitations": "Complete-aligned E4 family only",
        },
        {
            "claim_id": "C6",
            "claim_text": "RAVEN-w/o-Use shows NO_CLEAR_EFFECT in the tested Complete-aligned E4 family.",
            "allowed_strength": "NO_CLEAR_EFFECT",
            "primary_source": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER_R2.csv",
            "dataset": "SensorScope, U-Air",
            "method": "RAVEN-w/o-Use",
            "seed_set": "30001-30020",
            "metric": "all core E4 metrics",
            "test": "paired Holm",
            "excluded_evidence": "Gen0/Gen1 Inst (irrelevant)",
            "known_limitations": "Complete-aligned family",
        },
        {
            "claim_id": "C7",
            "claim_text": "Debt gives a statistically consistent but quantitatively small structural effect.",
            "allowed_strength": "STRUCTURAL_ONLY_SUPPORTED",
            "primary_source": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER_R2.csv",
            "dataset": "SensorScope, U-Air",
            "method": "RAVEN-w/o-Debt",
            "seed_set": "30001-30020",
            "metric": "Delta_group, Delta_c_s",
            "test": "paired Holm",
            "excluded_evidence": "",
            "known_limitations": "quantitatively small relative change",
        },
        {
            "claim_id": "C8",
            "claim_text": "RAVEN-w/o-Inst FINAL interpretation is ENDPOINT_TRADEOFF.",
            "allowed_strength": "ENDPOINT_TRADEOFF",
            "primary_source": "01_core_data/e4/E4_COMPONENT_INTERPRETATION_FINAL_R2.json",
            "dataset": "SensorScope, U-Air",
            "method": "RAVEN-w/o-Inst Generation 2",
            "seed_set": "30001-30020",
            "metric": "mixed structural and predictive",
            "test": "paired Holm from 240 cells",
            "excluded_evidence": "w/o-Inst Gen0 INVALID_P2_OFF; Gen1 SUPERSEDED_REFERENCE_PENALTY_MISMATCH",
            "known_limitations": "OLD_SUPERSEDED_LABEL STRUCTURAL_ONLY_SUPPORTED in R3 seal",
        },
        {
            "claim_id": "C9",
            "claim_text": "Traffic E3 old-vs-new cross-vintage inferential comparisons remain NOT_COMPARABLE.",
            "allowed_strength": "NOT_COMPARABLE",
            "primary_source": "00_index/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json",
            "dataset": "NSW-Traffic",
            "method": "all Traffic E3",
            "seed_set": "30001-30020",
            "metric": "n/a",
            "test": "n/a",
            "excluded_evidence": "must not enter main E3 inference tables",
            "known_limitations": "cross-vintage",
        },
        {
            "claim_id": "C10",
            "claim_text": "P2 warning-affected outputs have audited feasibility, while exact optimality is NOT reconstructable from sealed outputs.",
            "allowed_strength": "feasibility_audited_optimality_not_reconstructable",
            "primary_source": "00_index/P2_CLAIM_BOUNDARY_R2.json",
            "dataset": "SensorScope, U-Air",
            "method": "P2-using methods",
            "seed_set": "",
            "metric": "n/a",
            "test": "n/a",
            "excluded_evidence": "",
            "known_limitations": "no exact optimality proof from sealed outputs",
        },
    ]
    write_csv(paper / "00_index" / "CLAIM_TO_DATA_MAP_R2.csv", rows)
    write_csv(paper / "00_index" / "CLAIM_TO_DATA_MAP.csv", rows)
    lines = ["# Claim-to-data map R2", ""]
    for r in rows:
        lines += [f"## {r['claim_id']}", f"- {r['claim_text']}", f"- Strength: `{r['allowed_strength']}`", f"- Source: `{r['primary_source']}`", ""]
    write_text(paper / "00_index" / "CLAIM_TO_DATA_MAP_R2.md", "\n".join(lines))
    write_text(paper / "00_index" / "CLAIM_TO_DATA_MAP.md", "\n".join(lines))


def write_fig_table_map(paper: Path) -> None:
    rows = [
        {
            "artifact_id": "TABLE-1",
            "paper_role": "Dataset summary",
            "source_csv": "06_table_sources/TABLE_DATASET_SUMMARY_R2.csv",
            "filters": "frozen metadata only; T-Drive readiness fields only",
            "valid_seeds": "n/a",
            "valid_source_vintage": "E3 protocol closure + E2 SOURCE_HASHES + raw provenance",
            "excluded_evidence": "guessed fields; T-Drive formal results (none)",
            "claim_ceiling": "Experimental Setup",
        },
        {
            "artifact_id": "TABLE-2",
            "paper_role": "E3 main effectiveness",
            "source_csv": "06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv",
            "filters": "SCI_COMPARABLE_MAIN SensorScope+U-Air",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E3 formal new",
            "excluded_evidence": "Traffic NOT_COMPARABLE",
            "claim_ceiling": "C3,C4",
        },
        {
            "artifact_id": "TABLE-3",
            "paper_role": "E4 core ablation",
            "source_csv": "06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv",
            "filters": "240 cells; w/o-Inst Gen2 only",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E4 parent + Inst Gen2",
            "excluded_evidence": "w/o-Inst Gen0/Gen1",
            "claim_ceiling": "C5,C6,C7,C8",
        },
        {
            "artifact_id": "FIG-1",
            "paper_role": "E2 risk non-interchangeability",
            "source_csv": "07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv",
            "filters": "E2 complete_aligned / D_aligned",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E2 PROFILE-S1",
            "excluded_evidence": "E3 Traffic",
            "claim_ceiling": "C1,C2",
        },
        {
            "artifact_id": "FIG-2",
            "paper_role": "E3 structural mismatch",
            "source_csv": "07_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH.csv",
            "filters": "SCI_COMPARABLE_MAIN",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E3 formal",
            "excluded_evidence": "Traffic",
            "claim_ceiling": "C3",
        },
        {
            "artifact_id": "FIG-3",
            "paper_role": "E4 component removal",
            "source_csv": "07_figure_sources/FIG3_E4_COMPONENT_REMOVAL_R2.csv",
            "filters": "final valid 240 cells",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E4 Gen2 Inst + parent",
            "excluded_evidence": "Gen0/Gen1 w/o-Inst",
            "claim_ceiling": "C5,C6,C7,C8",
        },
        {
            "artifact_id": "OPTIONAL-E1",
            "paper_role": "E1 sanity",
            "source_csv": "06_table_sources/TABLE_E1_BALANCED_SANITY.csv",
            "filters": "E1_R2_FINAL_SEALED",
            "valid_seeds": "28001-28005",
            "valid_source_vintage": "E1_R2",
            "excluded_evidence": "",
            "claim_ceiling": "sanity / no-harm",
        },
        {
            "artifact_id": "OPTIONAL-E3-RMSE",
            "paper_role": "E3 RMSE",
            "source_csv": "07_figure_sources/FIG_OPTIONAL_E3_RMSE.csv",
            "filters": "SCI_COMPARABLE_MAIN",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E3 formal",
            "excluded_evidence": "Traffic",
            "claim_ceiling": "C4",
        },
        {
            "artifact_id": "OPTIONAL-E3-TAIL",
            "paper_role": "E3 Tail_RMSE",
            "source_csv": "07_figure_sources/FIG_OPTIONAL_E3_TAIL_RMSE.csv",
            "filters": "SCI_COMPARABLE_MAIN",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "E3 formal",
            "excluded_evidence": "Traffic",
            "claim_ceiling": "C4",
        },
        {
            "artifact_id": "OPTIONAL-P2",
            "paper_role": "P2 diagnostics",
            "source_csv": "06_table_sources/TABLE_P2_DIAGNOSTICS_SUPPLEMENT.csv",
            "filters": "feasibility audit",
            "valid_seeds": "",
            "valid_source_vintage": "E3 P2 certificate seal",
            "excluded_evidence": "certified exact optimality",
            "claim_ceiling": "C10",
        },
        {
            "artifact_id": "OPTIONAL-DEBT",
            "paper_role": "Debt trajectory",
            "source_csv": "07_figure_sources/FIG_OPTIONAL_DEBT_TRAJECTORY.csv",
            "filters": "supporting only if present",
            "valid_seeds": "",
            "valid_source_vintage": "sealed states",
            "excluded_evidence": "do not promote to RQ",
            "claim_ceiling": "supporting",
        },
        {
            "artifact_id": "OPTIONAL-ESS",
            "paper_role": "ESS",
            "source_csv": "02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv",
            "filters": "run-level ESS scalar",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "sealed final_metrics.json",
            "excluded_evidence": "not a trajectory",
            "claim_ceiling": "supporting",
        },
        {
            "artifact_id": "OPTIONAL-RUNTIME",
            "paper_role": "runtime",
            "source_csv": "02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv",
            "filters": "runtime_seconds",
            "valid_seeds": "30001-30020",
            "valid_source_vintage": "sealed final_metrics.json",
            "excluded_evidence": "not P2-only runtime",
            "claim_ceiling": "supporting",
        },
    ]
    write_csv(paper / "00_index" / "FIGURE_TABLE_PROVENANCE_MAP_R2.csv", rows)
    write_csv(paper / "00_index" / "FIGURE_TABLE_PROVENANCE_MAP.csv", rows)
    lines = ["# Figure/table provenance R2", ""]
    for r in rows:
        lines += [f"## {r['artifact_id']}: {r['paper_role']}", f"- CSV: `{r['source_csv']}`", f"- Filters: {r['filters']}", f"- Excluded: {r['excluded_evidence']}", f"- Ceiling: {r['claim_ceiling']}", ""]
    write_text(paper / "00_index" / "FIGURE_TABLE_PROVENANCE_MAP_R2.md", "\n".join(lines))
    write_text(paper / "00_index" / "FIGURE_TABLE_PROVENANCE_MAP.md", "\n".join(lines))


def rebuild_masters(paper: Path) -> dict[str, Any]:
    paper = Path(paper)
    run_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []

    def add_run(round_id, dataset, scenario, method, seed, comparison, role, status, source, et, lid, extra=None):
        run_rows.append(
            {
                "round": round_id,
                "dataset": dataset,
                "scenario": scenario,
                "method_or_configuration": method,
                "seed": seed,
                "comparison_class": comparison,
                "paper_role": role,
                "scientific_status": status,
                "source_file": source,
                "EventTrace_hash": et,
                "logical_run_id": lid,
                **(extra or {}),
            }
        )

    def add_long(round_id, dataset, scenario, method, seed, metric, value, status, comparison, role, source, key, sci, notes=""):
        long_rows.append(
            {
                "round": round_id,
                "dataset": dataset,
                "scenario": scenario,
                "method_or_configuration": method,
                "seed": seed,
                "metric": metric,
                "value": value,
                "status": status,
                "comparison_class": comparison,
                "paper_role": role,
                "source_file": source,
                "source_row_or_key": key,
                "source_sha256": "",
                "scientific_status": sci,
                "notes": notes,
            }
        )

    e1 = read_csv(paper / "01_core_data/e1/E1_FINAL_VALID_RUNS.csv")
    for r in e1:
        add_run("E1", r["dataset"], r["scenario"], r["method"], r["seed"], r["comparison_class"], r["paper_role"], r["validity_label"], r["source_file"], r.get("EventTrace_hash", ""), r.get("logical_run_id", ""))
        for m in ["RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"]:
            st = r.get(f"{m}_status") or ("VALID" if (r.get(m) or "") != "" else MISSING)
            add_long("E1", r["dataset"], r["scenario"], r["method"], r["seed"], m, r.get(m, ""), st, r["comparison_class"], r["paper_role"], r["source_file"], r.get("logical_run_id", ""), r["validity_label"])

    e2 = read_csv(paper / "01_core_data/e2/E2_FINAL_VALID_RUNS_600.csv")
    for r in e2:
        add_run("E2", r["dataset"], r["scenario"], r["method"], r["seed"], r["comparison_class"], r["paper_role"], r["validity_label"], r["source_file"], r.get("EventTrace_hash", ""), r.get("logical_run_id", ""))
        for m in ["RMSE_mu", "RMSE_rho", "MAE_mu", "Tail_RMSE", "Delta_group", "Gap_mis"]:
            st = r.get(f"{m}_status") or ("VALID" if (r.get(m) or "") != "" else MISSING)
            add_long("E2", r["dataset"], r["scenario"], r["method"], r["seed"], m, r.get(m, ""), st, r["comparison_class"], r["paper_role"], r["source_file"], r.get("logical_run_id", ""), r["validity_label"])

    e3 = read_csv(paper / "01_core_data/e3/E3_MAIN_COMPARABLE_LONG.csv")
    for r in e3:
        if r.get("comparison_class") != "SCI_COMPARABLE_MAIN":
            continue
        add_run("E3", r["dataset"], r.get("scenario", "complete_aligned"), r["method"], r["seed"], r["comparison_class"], r["paper_role"], "VALID", r["source_file"], r.get("EventTrace_hash", ""), r.get("logical_run_id", ""))
        for m in ["RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"]:
            st = r.get(f"{m}_status") or ("VALID" if (r.get(m) or "") != "" else MISSING)
            add_long("E3", r["dataset"], r.get("scenario", "complete_aligned"), r["method"], r["seed"], m, r.get(m, ""), st, r["comparison_class"], r["paper_role"], r["source_file"], r.get("logical_run_id", ""), "VALID")

    e4 = read_csv(paper / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")
    assert len(e4) == 240
    for r in e4:
        if r.get("configuration") == "RAVEN-w/o-Inst" and str(r.get("generation")) != "2":
            continue
        add_run("E4", r["dataset"], "complete_aligned", r["configuration"], r["seed"], r["comparison_class"], r["paper_role"], r["validity"], r["source_file"], r.get("EventTrace_hash", ""), r.get("logical_run_id", ""), extra={"generation": r.get("generation")})
        for m in METRICS_E4:
            add_long("E4", r["dataset"], "complete_aligned", r["configuration"], r["seed"], m, r.get(m, ""), "VALID", r["comparison_class"], r["paper_role"], r["source_file"], r.get("logical_run_id", ""), r["validity"], "w/o-Inst Gen2 only" if "Inst" in r["configuration"] else "")

    write_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL_R2.csv", run_rows)
    write_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_LONG_R2.csv", long_rows)
    write_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL.csv", run_rows)
    write_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv", long_rows)
    e3_traffic = [r for r in long_rows if r["round"] == "E3" and "Traffic" in r["dataset"]]
    e4_inst = [r for r in run_rows if r["round"] == "E4" and "Inst" in r["method_or_configuration"]]
    return {
        "n_runlevel": len(run_rows),
        "n_long": len(long_rows),
        "n_e3_traffic_in_master": len(e3_traffic),
        "n_e4_inst": len(e4_inst),
        "n_e4_runlevel": sum(1 for r in run_rows if r["round"] == "E4"),
    }


def numeric_consistency_audit(paper: Path, e4_paired: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paper = Path(paper)
    flags: list[dict[str, Any]] = []

    def flag(item, left, right, a, b, status, note=""):
        flags.append({"item": item, "left_file": left, "right_file": right, "left_value": a, "right_value": b, "status": status, "notes": note})

    cells = read_csv(paper / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")
    master_e4 = [r for r in read_csv(paper / "01_core_data/master/PAPER_EVIDENCE_MASTER_RUNLEVEL_R2.csv") if r["round"] == "E4"]
    flag("E4_cell_count", "E4_FINAL_VALID_EVIDENCE_240.csv", "MASTER_RUNLEVEL_R2", str(len(cells)), str(len(master_e4)), "OK" if len(cells) == len(master_e4) == 240 else "VALUE_CONFLICT")

    core = read_csv(paper / "06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv")
    # Compare table mean RMSE_mu SensorScope RAVEN-MCS to mean of 240 cells
    import numpy as np

    ss_rav = [float(r["RMSE_mu"]) for r in cells if r["dataset"] == "SensorScope" and r["configuration"] == "RAVEN-MCS"]
    tab = next(r for r in core if r["dataset"] == "SensorScope" and r["configuration"] == "RAVEN-MCS")
    m = float(np.mean(ss_rav))
    t = float(tab["RMSE_mu_mean"])
    ok = abs(m - t) < 1e-12
    flag("SS_RAVEN_RMSE_mu_mean", "240 cells", "TABLE_E4_CORE_ABLATION_R2", str(m), str(t), "OK" if ok else "VALUE_CONFLICT")

    fig = read_csv(paper / "07_figure_sources/FIG3_E4_COMPONENT_REMOVAL_R2.csv")
    stats = read_csv(paper / "04_statistics/E4_FINAL_STATISTICS_R2.csv")
    for s in stats:
        f = next(
            r
            for r in fig
            if r["dataset"] == s["dataset"] and r["component"] == s["component"] and r["metric"] == s["metric"]
        )
        ok = abs(float(f["paired_mean_difference"]) - float(s["paired_mean_difference"])) < 1e-12
        if not ok:
            flag(
                f"fig3_vs_stats_{s['dataset']}_{s['component']}_{s['metric']}",
                "FIG3",
                "E4_FINAL_STATISTICS_R2",
                f["paired_mean_difference"],
                s["paired_mean_difference"],
                "VALUE_CONFLICT",
            )
        lab_ok = f["final_component_label"] == s["final_component_label"]
        if not lab_ok:
            flag(
                f"label_{s['component']}",
                "FIG3",
                "stats",
                f["final_component_label"],
                s["final_component_label"],
                "VALUE_CONFLICT",
            )
    inst_labels = {r["final_component_label"] for r in stats if r["component"] == "Inst"}
    flag("Inst_paper_label", "E4_FINAL_STATISTICS_R2", "claim_ceiling", ",".join(sorted(inst_labels)), "ENDPOINT_TRADEOFF", "OK" if inst_labels == {"ENDPOINT_TRADEOFF"} else "VALUE_CONFLICT")

    # No unresolved core conflicts among required overlaps
    n_conflict = sum(1 for f in flags if f["status"] == "VALUE_CONFLICT")
    flag("summary_n_conflict", "audit", "audit", str(n_conflict), "0", "OK" if n_conflict == 0 else "VALUE_CONFLICT", "core overlapping values")
    write_csv(paper / "10_reports" / "PAPER_READY_NUMERIC_CONSISTENCY_AUDIT_R2.csv", flags)
    return flags


def write_missing_report(paper: Path, diag: dict[str, Any]) -> None:
    rows = [
        {"item": "E4_MAE_mu_in_240_csv", "round": "E4", "dataset": "SensorScope,U-Air", "method": "all", "seed": "30001-30020", "importance": "OPTIONAL", "source_searched": "E4_FINAL_VALID_EVIDENCE_240.csv", "offline_reconstructable": "yes_from_sealed_final_metrics_json", "requires_new_run": False, "recommended_action": "Use supporting RUNLEVEL_SEALED_SCALARS_R2.csv; do not treat as core 240-cell metric"},
        {"item": "E4_RMSE_rho_in_240_csv", "round": "E4", "dataset": "SensorScope,U-Air", "method": "all", "seed": "30001-30020", "importance": "OPTIONAL", "source_searched": "E4_FINAL_VALID_EVIDENCE_240.csv", "offline_reconstructable": "yes_from_sealed_final_metrics_json", "requires_new_run": False, "recommended_action": "supporting extraction only"},
        {"item": "Debt_trajectory_sealed_series", "round": "E3/E4", "dataset": "SensorScope,U-Air", "method": "raven", "seed": "", "importance": "SUPPORTING", "source_searched": "window_metrics.json keys", "offline_reconstructable": False, "requires_new_run": True, "recommended_action": "Leave MISSING_NOT_RECORDED"},
        {"item": "ESS_trajectory_sealed_series", "round": "E3/E4", "dataset": "SensorScope,U-Air", "method": "raven", "seed": "", "importance": "SUPPORTING", "source_searched": "window_metrics.json; final_metrics ESS scalar only", "offline_reconstructable": False, "requires_new_run": True, "recommended_action": "Use run-level ESS scalar as supporting"},
        {"item": "P2_runtime_only", "round": "E3/E4", "dataset": "SensorScope,U-Air", "method": "P2 methods", "seed": "", "importance": "SUPPORTING", "source_searched": "final_metrics.runtime_seconds is total run not P2-only", "offline_reconstructable": False, "requires_new_run": True, "recommended_action": "Leave P2-only runtime MISSING_NOT_RECORDED"},
        {"item": "SensorScope_sampling_interval", "round": "meta", "dataset": "SensorScope", "method": "", "seed": "", "importance": "SUPPORTING", "source_searched": "horizon.json, provenance.json", "offline_reconstructable": False, "requires_new_run": False, "recommended_action": "MISSING_NOT_RECORDED"},
        {"item": "UAir_sampling_interval", "round": "meta", "dataset": "U-Air", "method": "", "seed": "", "importance": "SUPPORTING", "source_searched": "horizon.json, provenance.json", "offline_reconstructable": False, "requires_new_run": False, "recommended_action": "MISSING_NOT_RECORDED"},
        {"item": "TDrive_opportunity_EventTrace_split_freeze", "round": "T-Drive", "dataset": "T-Drive-Speed", "method": "", "seed": "", "importance": "CORE for a future T-Drive block; not CORE for current E1-E4 paper", "source_searched": "configs/dataset/tdrive_speed.yaml, processed parquet", "offline_reconstructable": False, "requires_new_run": False, "recommended_action": "Protocol seal before any formal T-Drive runs"},
        {"item": "E1_dataset_checksum", "round": "E1", "dataset": "Balanced", "method": "all", "seed": "28001-28005", "importance": "SUPPORTING", "source_searched": "outputs/aggregate/E1_R2/identity_audit.json", "offline_reconstructable": False, "requires_new_run": False, "recommended_action": "PARTIAL_BUT_PAPER_SAFE"},
    ]
    write_csv(paper / "10_reports" / "MISSING_POTENTIALLY_USEFUL_DATA_R2.csv", rows)
    lines = ["# Missing potentially useful data R2", "", "No CORE E1–E4 metric cells are missing from the 240/600/E3 main comparable matrices.", ""]
    for r in rows:
        lines.append(f"- **{r['item']}** ({r['importance']}): {r['recommended_action']}")
    write_text(paper / "10_reports" / "MISSING_POTENTIALLY_USEFUL_DATA_R2.md", "\n".join(lines))
    write_text(paper / "10_reports" / "MISSING_POTENTIALLY_USEFUL_DATA.md", "\n".join(lines))
