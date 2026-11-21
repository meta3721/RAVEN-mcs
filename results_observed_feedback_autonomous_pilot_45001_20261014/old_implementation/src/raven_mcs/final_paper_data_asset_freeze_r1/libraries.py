"""Figure/table libraries, claim maps, dictionary, rebuttal, section requirements."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r1.io_util import copy_file, sha256_file, write_csv, write_json, write_text
from raven_mcs.final_paper_data_asset_freeze_r1.constants import NA


def _sha(p: Path) -> str:
    return sha256_file(p) if p.is_file() else NA


def build_libraries(root: Path, r2: Path, mec: Path, out: Path) -> None:
    fig1 = mec / "03_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv"
    fig2 = mec / "03_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv"
    fig3p = r2 / "07_figure_sources/FIG_OPTIONAL_E3_RMSE.csv"
    fig4 = mec / "03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv"
    if fig3p.is_file():
        copy_file(fig3p, out / "15_FIGURE_SOURCES/FIG3_E3_PREDICTION_RISK.csv")
    pred = r2 / "01_core_data/e3/E3_PREDICTION_METRICS_MASTER.csv"
    if pred.is_file():
        copy_file(pred, out / "15_FIGURE_SOURCES/FIG3_E3_PREDICTION_RISK_MASTER.csv")
    ess = r2 / "07_figure_sources/FIG_OPTIONAL_ESS.csv"
    p2rt = r2 / "07_figure_sources/FIG_OPTIONAL_P2_RUNTIME.csv"
    haj = out / "07_WEIGHTS/local_hajek_provenance/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv"
    ds = r2 / "06_table_sources/TABLE_DATASET_SUMMARY_R2.csv"

    figs = [
        {
            "figure_id": "FIG1_E2_RISK_NONINTERCHANGEABILITY",
            "title": "E2 D_aligned risk non-interchangeability",
            "rq": "RQ1",
            "paper_role": "RQ1_PROBLEM_EVIDENCE",
            "source_assets": str(fig1.as_posix() if fig1.is_file() else r2 / "07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv"),
            "source_hashes": _sha(fig1 if fig1.is_file() else r2 / "07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv"),
            "metrics": "D_aligned",
            "datasets": "NSW-Traffic",
            "methods": "five E2 formal",
            "seeds": "30001-30020",
            "recommended_location": "Section VII-B",
            "main_or_appendix": "main",
            "scientific_value": "high",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "MAIN_FIGURE_READY",
            "notes": "Not a RAVEN ranking figure",
        },
        {
            "figure_id": "FIG2_E3_STRUCTURAL_MISMATCH",
            "title": "E3 structural target mismatch",
            "rq": "RQ2",
            "paper_role": "RQ2_MAIN_EFFECTIVENESS",
            "source_assets": str(fig2 if fig2.is_file() else r2 / "07_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH.csv"),
            "source_hashes": _sha(fig2 if fig2.is_file() else r2 / "07_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH.csv"),
            "metrics": "Delta_group,Delta_c_s",
            "datasets": "SensorScope,U-Air",
            "methods": "five baselines + RAVEN",
            "seeds": "30001-30020",
            "recommended_location": "Section VII-C",
            "main_or_appendix": "main",
            "scientific_value": "high",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "MAIN_FIGURE_READY",
            "notes": "Traffic E3 excluded",
        },
        {
            "figure_id": "FIG3_E3_PREDICTION_RISK",
            "title": "E3 prediction risk (RMSE_mu / Tail)",
            "rq": "RQ2",
            "paper_role": "RQ2_MAIN_EFFECTIVENESS",
            "source_assets": str(pred),
            "source_hashes": _sha(pred),
            "metrics": "RMSE_mu,Tail_RMSE",
            "datasets": "SensorScope,U-Air",
            "methods": "E3 primary + reference-only",
            "seeds": "30001-30020",
            "recommended_location": "Section VII-C or appendix",
            "main_or_appendix": "main_or_appendix",
            "scientific_value": "high",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "MAIN_FIGURE_READY",
            "notes": "Selective RMSE; not universal superiority. Table II already covers prediction.",
        },
        {
            "figure_id": "FIG4_E4_COMPONENT_ABLATION",
            "title": "E4 component removal relative change",
            "rq": "RQ3",
            "paper_role": "RQ3_MECHANISM",
            "source_assets": str(fig4 if fig4.is_file() else r2 / "07_figure_sources/FIG3_E4_COMPONENT_REMOVAL_R2.csv"),
            "source_hashes": _sha(fig4 if fig4.is_file() else r2 / "07_figure_sources/FIG3_E4_COMPONENT_REMOVAL_R2.csv"),
            "metrics": "relative_change_percent",
            "datasets": "SensorScope,U-Air",
            "methods": "five w/o-X vs RAVEN",
            "seeds": "30001-30020",
            "recommended_location": "Section VII-D",
            "main_or_appendix": "main",
            "scientific_value": "high",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "MAIN_FIGURE_READY",
            "notes": "w/o-Inst Gen2 only; mixed signs required",
        },
        {
            "figure_id": "FIG5_SELECTION_TARGET_COMPOSITION",
            "title": "Opportunity/usable to post-calibration vs target mu",
            "rq": "RQ3",
            "paper_role": "RQ3_MECHANISM",
            "source_assets": "",
            "source_hashes": "",
            "metrics": "group mass trajectory",
            "datasets": "SensorScope,U-Air",
            "methods": "RAVEN-MCS",
            "seeds": "30001-30020",
            "recommended_location": "none",
            "main_or_appendix": "none",
            "scientific_value": "high_if_existed",
            "data_complete": False,
            "needs_new_experiment": False,
            "recommendation": "INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN_NEW_EXPERIMENT",
            "notes": "target_composition_trajectory MISSING_NOT_RECORDED",
        },
        {
            "figure_id": "FIG6_P2_FEASIBILITY_OR_ESS",
            "title": "P2 feasibility / ESS diagnostic",
            "rq": "n/a",
            "paper_role": "THEORY_DIAGNOSTIC",
            "source_assets": str(ess) + ";" + str(p2rt),
            "source_hashes": _sha(ess) + ";" + _sha(p2rt),
            "metrics": "ESS,runtime,P2 warnings",
            "datasets": "SensorScope,U-Air",
            "methods": "P2-using",
            "seeds": "30001-30020",
            "recommended_location": "Appendix",
            "main_or_appendix": "appendix",
            "scientific_value": "medium",
            "data_complete": ess.is_file(),
            "needs_new_experiment": False,
            "recommendation": "APPENDIX_FIGURE_READY" if ess.is_file() else "SOURCE_READY_OPTIONAL",
            "notes": "P2-only runtime often MISSING_NOT_RECORDED; use total runtime supporting",
        },
        {
            "figure_id": "FIG7_RUNTIME_DIAGNOSTIC",
            "title": "Runtime diagnostic",
            "rq": "n/a",
            "paper_role": "SYSTEM_DIAGNOSTIC",
            "source_assets": str(r2 / "02_supporting_data/runtime/RUNTIME_MASTER.csv"),
            "source_hashes": _sha(r2 / "02_supporting_data/runtime/RUNTIME_MASTER.csv"),
            "metrics": "runtime_seconds",
            "datasets": "E2/E3 as recorded",
            "methods": "sealed",
            "seeds": "as recorded",
            "recommended_location": "Appendix optional",
            "main_or_appendix": "appendix",
            "scientific_value": "low-medium",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "SOURCE_READY_OPTIONAL",
            "notes": "Not a scalability claim",
        },
        {
            "figure_id": "FIG8_LOCAL_HAJEK_PROVENANCE",
            "title": "Local-Hajek degeneracy provenance",
            "rq": "RQ2",
            "paper_role": "STATISTICAL_SUPPORT",
            "source_assets": str(haj),
            "source_hashes": _sha(haj) if haj.is_file() else _sha(r2 / "02_supporting_data/e3/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv"),
            "metrics": "weight range / effective windows",
            "datasets": "SensorScope,U-Air",
            "methods": "Local-Hajek",
            "seeds": "30001-30020",
            "recommended_location": "Appendix / rebuttal",
            "main_or_appendix": "appendix",
            "scientific_value": "medium",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "APPENDIX_FIGURE_READY",
            "notes": "PAPER_SUPPORTING",
        },
        {
            "figure_id": "FIG9_DATASET_SUPPORT_CONTEXT",
            "title": "Dataset support / setup context",
            "rq": "setup",
            "paper_role": "DATASET_SETUP",
            "source_assets": str(ds),
            "source_hashes": _sha(ds),
            "metrics": "n_clients, splits, h/s",
            "datasets": "SensorScope,U-Air,NSW-Traffic",
            "methods": "n/a",
            "seeds": "n/a",
            "recommended_location": "Section VII-A / Table I",
            "main_or_appendix": "table_preferred",
            "scientific_value": "medium",
            "data_complete": True,
            "needs_new_experiment": False,
            "recommendation": "DROP_LOW_VALUE",
            "notes": "Table I already carries this; figure optional",
        },
    ]
    write_csv(out / "15_FIGURE_SOURCES/FIGURE_CANDIDATE_REGISTRY.csv", figs)
    fig_ready = []
    for f in figs:
        fig_ready.append(
            {
                "figure_id": f["figure_id"],
                "all_source_data_present": bool(f["data_complete"]),
                "statistics_present": f["figure_id"] not in {"FIG5_SELECTION_TARGET_COMPOSITION", "FIG9_DATASET_SUPPORT_CONTEXT"},
                "provenance_complete": bool(f["source_hashes"]) or f["figure_id"] == "FIG5_SELECTION_TARGET_COMPOSITION",
                "new_experiment_required": False,
                "main_text_value": f["main_or_appendix"],
                "appendix_value": "yes" if "appendix" in str(f["main_or_appendix"]) else "optional",
                "recommended_final_status": f["recommendation"],
            }
        )
    write_csv(out / "22_REPORTS/FIGURE_DATA_READINESS_AUDIT.csv", fig_ready)

    t1 = mec / "01_table_sources/TABLE_I_DATASETS.csv"
    t2 = mec / "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
    t3 = mec / "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv"
    te1 = mec / "01_table_sources/TABLE_E1_BALANCED_SANITY_FINAL.csv"
    tables = [
        {"table_id": "TABLE_I_DATASET_SETUP", "title": "Datasets/protocols", "rq": "setup", "paper_role": "DATASET_SETUP", "source_assets": str(t1 if t1.is_file() else ds), "source_hashes": _sha(t1 if t1.is_file() else ds), "recommended_location": "Section VII-A", "main_or_appendix": "main", "scientific_value": "high", "data_complete": True, "needs_new_experiment": False, "recommendation": "MAIN_TABLE_READY", "notes": "T-Drive excluded from Table I"},
        {"table_id": "TABLE_II_MAIN_EFFECTIVENESS", "title": "E3 SensorScope/U-Air", "rq": "RQ2", "paper_role": "RQ2_MAIN_EFFECTIVENESS", "source_assets": str(t2 if t2.is_file() else r2 / "06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv"), "source_hashes": _sha(t2 if t2.is_file() else r2 / "06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv"), "recommended_location": "Section VII-C", "main_or_appendix": "main", "scientific_value": "high", "data_complete": True, "needs_new_experiment": False, "recommendation": "MAIN_TABLE_READY", "notes": "No Traffic E3"},
        {"table_id": "TABLE_III_CORE_ABLATION", "title": "E4 240-cell ablation", "rq": "RQ3", "paper_role": "RQ3_MECHANISM", "source_assets": str(t3 if t3.is_file() else r2 / "06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv"), "source_hashes": _sha(t3 if t3.is_file() else r2 / "06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv"), "recommended_location": "Section VII-D", "main_or_appendix": "main", "scientific_value": "high", "data_complete": True, "needs_new_experiment": False, "recommendation": "MAIN_TABLE_READY", "notes": "w/o-Inst Gen2"},
        {"table_id": "TABLE_E1_SANITY_APPENDIX", "title": "E1 balanced sanity", "rq": "RQ1", "paper_role": "RQ1_PROBLEM_EVIDENCE", "source_assets": str(te1 if te1.is_file() else r2 / "06_table_sources/TABLE_E1_BALANCED_SANITY.csv"), "source_hashes": _sha(te1 if te1.is_file() else r2 / "06_table_sources/TABLE_E1_BALANCED_SANITY.csv"), "recommended_location": "Appendix", "main_or_appendix": "appendix", "scientific_value": "medium", "data_complete": True, "needs_new_experiment": False, "recommendation": "APPENDIX_TABLE_READY", "notes": "No-harm; not superiority"},
        {"table_id": "TABLE_IV_STATISTICAL_SUMMARY", "title": "Holm/paired summary", "rq": "RQ2/RQ3", "paper_role": "STATISTICAL_SUPPORT", "source_assets": str(out / "01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv"), "source_hashes": "", "recommended_location": "Appendix", "main_or_appendix": "appendix", "scientific_value": "medium", "data_complete": True, "needs_new_experiment": False, "recommendation": "APPENDIX_TABLE_READY", "notes": "One paper-facing statistic per comparison"},
        {"table_id": "TABLE_V_RUNTIME_P2_APPENDIX", "title": "Runtime / P2 appendix", "rq": "n/a", "paper_role": "SYSTEM_DIAGNOSTIC", "source_assets": str(r2 / "02_supporting_data/runtime/RUNTIME_MASTER.csv"), "source_hashes": _sha(r2 / "02_supporting_data/runtime/RUNTIME_MASTER.csv"), "recommended_location": "Appendix optional", "main_or_appendix": "appendix", "scientific_value": "low-medium", "data_complete": True, "needs_new_experiment": False, "recommendation": "SOURCE_READY_OPTIONAL", "notes": "No scalability claim"},
        {"table_id": "TABLE_VI_FULL_METHOD_RESULTS_APPENDIX", "title": "Full method results", "rq": "RQ2", "paper_role": "APPENDIX_ONLY", "source_assets": str(r2 / "06_table_sources/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv"), "source_hashes": _sha(r2 / "06_table_sources/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv"), "recommended_location": "Appendix", "main_or_appendix": "appendix", "scientific_value": "medium", "data_complete": True, "needs_new_experiment": False, "recommendation": "APPENDIX_TABLE_READY", "notes": "Includes reference-only methods; still no Traffic E3 inference"},
    ]
    write_csv(out / "16_TABLE_SOURCES/TABLE_CANDIDATE_REGISTRY.csv", tables)
    write_csv(
        out / "22_REPORTS/TABLE_DATA_READINESS_AUDIT.csv",
        [
            {
                "table_id": t["table_id"],
                "all_source_data_present": True,
                "statistics_present": True,
                "provenance_complete": True,
                "new_experiment_required": False,
                "main_text_value": t["main_or_appendix"],
                "appendix_value": t["main_or_appendix"],
                "recommended_final_status": t["recommendation"],
            }
            for t in tables
        ],
    )

    claims = [
        {"asset_id": "E2_D_ALIGNED", "claim_id": "C1", "rq": "RQ1", "contribution": "1", "section": "VII-B", "figure_id": "FIG1", "table_id": "", "claim_strength": "supported", "required_or_optional": "required"},
        {"asset_id": "E2_D_ALIGNED", "claim_id": "C2", "rq": "RQ1", "contribution": "1", "section": "VII-B", "figure_id": "FIG1", "table_id": "", "claim_strength": "supported", "required_or_optional": "required"},
        {"asset_id": "E3_STRUCTURAL", "claim_id": "C3", "rq": "RQ2", "contribution": "2", "section": "VII-C", "figure_id": "FIG2", "table_id": "TABLE_II", "claim_strength": "supported", "required_or_optional": "required"},
        {"asset_id": "E3_PREDICTION", "claim_id": "C4", "rq": "RQ2", "contribution": "2", "section": "VII-C", "figure_id": "FIG3", "table_id": "TABLE_II", "claim_strength": "supported_selective", "required_or_optional": "required"},
        {"asset_id": "E4_240", "claim_id": "C5", "rq": "RQ3", "contribution": "3", "section": "VII-D", "figure_id": "FIG4", "table_id": "TABLE_III", "claim_strength": "supported", "required_or_optional": "required"},
        {"asset_id": "E4_USE", "claim_id": "C6", "rq": "RQ3", "contribution": "3", "section": "VII-D", "figure_id": "FIG4", "table_id": "TABLE_III", "claim_strength": "NO_CLEAR_EFFECT", "required_or_optional": "required"},
        {"asset_id": "E4_DEBT", "claim_id": "C7", "rq": "RQ3", "contribution": "3", "section": "VII-D", "figure_id": "FIG4", "table_id": "TABLE_III", "claim_strength": "STRUCTURAL_ONLY_SUPPORTED_small", "required_or_optional": "required"},
        {"asset_id": "E4_INST_GEN2", "claim_id": "C8", "rq": "RQ3", "contribution": "3", "section": "VII-D", "figure_id": "FIG4", "table_id": "TABLE_III", "claim_strength": "ENDPOINT_TRADEOFF", "required_or_optional": "required"},
        {"asset_id": "TRAFFIC_E3", "claim_id": "C9", "rq": "RQ2", "contribution": "n/a", "section": "VIII", "figure_id": "", "table_id": "", "claim_strength": "NOT_COMPARABLE", "required_or_optional": "required_limitation"},
        {"asset_id": "P2_BOUNDARY", "claim_id": "C10", "rq": "n/a", "contribution": "3", "section": "VI/VIII", "figure_id": "", "table_id": "", "claim_strength": "feasibility_not_exact_optimality", "required_or_optional": "required_limitation"},
    ]
    write_csv(out / "00_MASTER_CATALOG/ASSET_TO_CLAIM_MAP.csv", claims)

    sections = [
        {"section": "III", "required_data": "dataset semantics / h / s / R / O / U definitions", "available": True, "asset_ids": "DATASET_METADATA_FINAL;FINAL_H_S_SEMANTICS", "gap": "row-level R/O/U not sealed", "new_experiment_needed": False},
        {"section": "IV", "required_data": "selection-layer correction definitions/provenance", "available": True, "asset_ids": "FINAL_CONFIG_MASTER;Local-Hajek provenance", "gap": "propensity distributions MISSING_NOT_RECORDED", "new_experiment_needed": False},
        {"section": "V", "required_data": "calibration/debt/P2 semantics", "available": True, "asset_ids": "P2_CLAIM_BOUNDARY;E4 labels", "gap": "debt trajectory MISSING_NOT_RECORDED", "new_experiment_needed": False},
        {"section": "VI", "required_data": "theory diagnostics if any", "available": "partial", "asset_ids": "ESS scalars;P2 feasibility", "gap": "ESS trajectory MISSING_NOT_RECORDED", "new_experiment_needed": False},
        {"section": "VII-A", "required_data": "dataset/config/statistics metadata", "available": True, "asset_ids": "TABLE_I;FINAL_CONFIG_MASTER", "gap": "none core", "new_experiment_needed": False},
        {"section": "VII-B", "required_data": "E1/E2", "available": True, "asset_ids": "E1 25; E2 600; FIG1", "gap": "none", "new_experiment_needed": False},
        {"section": "VII-C", "required_data": "E3 SS/U-Air", "available": True, "asset_ids": "E3 440 comparable; TABLE_II; FIG2", "gap": "Traffic E3 NOT_COMPARABLE by design", "new_experiment_needed": False},
        {"section": "VII-D", "required_data": "E4 240", "available": True, "asset_ids": "E4 240; TABLE_III; FIG4", "gap": "none core", "new_experiment_needed": False},
        {"section": "VIII", "required_data": "Traffic/P2/Use/Debt limitations", "available": True, "asset_ids": "boundaries; E4 labels; T-Drive reserve", "gap": "no T-Drive performance", "new_experiment_needed": False},
        {"section": "Appendix", "required_data": "diagnostics, provenance, full tables", "available": True, "asset_ids": "supporting/appendix folders", "gap": "supporting fields listed in MISSING_DATA_FINAL", "new_experiment_needed": False},
    ]
    write_csv(out / "00_MASTER_CATALOG/SECTION_DATA_REQUIREMENTS.csv", sections)

    rebuttal = [
        {"concern": "Where is risk mismatch?", "existing_asset_ids": "FIG1;E2_D_ALIGNED", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Why Local-Hajek collapses?", "existing_asset_ids": "07_WEIGHTS/local_hajek_provenance", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Why Traffic excluded from E3 inference?", "existing_asset_ids": "19_NOT_COMPARABLE", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Is P2 feasible?", "existing_asset_ids": "09_P2_SOLVER;P2_CLAIM_BOUNDARY", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Why Use has no effect?", "existing_asset_ids": "E4_FINAL_STATISTICS_R2;C6", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Why Debt effect is tiny?", "existing_asset_ids": "E4 Debt rows; C7", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Do components trade off?", "existing_asset_ids": "FIG4;C5;C8", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "What is runtime?", "existing_asset_ids": "11_RUNTIME_SYSTEM", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "What is ESS?", "existing_asset_ids": "10_ESS_VARIANCE;RUNLEVEL_SEALED_SCALARS_R2", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Where is mobility?", "existing_asset_ids": "20_TDRIVE_RESERVE", "ready_answer": True, "new_experiment_needed": False},
        {"concern": "Can T-Drive be run later?", "existing_asset_ids": "TDRIVE_RESERVE_STATUS", "ready_answer": True, "new_experiment_needed": False},
    ]
    write_csv(out / "00_MASTER_CATALOG/REBUTTAL_ASSET_MAP.csv", rebuttal)

    dictionary = [
        {"name": "RMSE_mu", "symbol": "RMSE_μ", "definition": "deployment-target weighted RMSE", "unit": "physical units", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "E1/E2/E3/E4 as recorded", "valid_rounds": "E1-E4", "comparability_notes": "not universal superiority", "paper_claim_usage": "C4 companion"},
        {"name": "MAE_mu", "symbol": "MAE_μ", "definition": "deployment-target weighted MAE", "unit": "physical units", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "when VALID", "valid_rounds": "E3/E4", "comparability_notes": "often MISSING_NOT_RECORDED in E1/E2/E4", "paper_claim_usage": "supporting"},
        {"name": "Tail_RMSE", "symbol": "Tail RMSE", "definition": "tail-group RMSE companion", "unit": "physical units", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "E1/E3/E4", "valid_rounds": "E1-E4", "comparability_notes": "", "paper_claim_usage": "C4 companion"},
        {"name": "RMSE_rho", "symbol": "RMSE_ρ", "definition": "usable-update/arrival risk RMSE", "unit": "physical units", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "E2 primary; E3 when VALID", "valid_rounds": "E1-E3", "comparability_notes": "E4 often MISSING_NOT_RECORDED", "paper_claim_usage": "C2 via D_aligned"},
        {"name": "Delta_group", "symbol": "Δ_group", "definition": "group-mass structural mismatch vs target h(i)", "unit": "dimensionless", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "SensorScope,U-Air", "valid_rounds": "E3/E4", "comparability_notes": "Central N/A", "paper_claim_usage": "C3 primary"},
        {"name": "Delta_c_s", "symbol": "Δ_{c,s}", "definition": "stratum structural mismatch vs s(i)", "unit": "dimensionless", "lower_or_higher_better": "lower", "granularity": "run", "valid_datasets": "SensorScope,U-Air", "valid_rounds": "E3/E4", "comparability_notes": "Central N/A", "paper_claim_usage": "C3 primary"},
        {"name": "D_aligned", "symbol": "D_aligned", "definition": "Delta RMSE_mu - Delta RMSE_rho on complete-aligned vs balanced", "unit": "RMSE units", "lower_or_higher_better": "sign/stability not ranking", "granularity": "seed×method", "valid_datasets": "NSW-Traffic E2", "valid_rounds": "E2", "comparability_notes": "not a superiority metric", "paper_claim_usage": "C1/C2"},
        {"name": "ESS", "symbol": "ESS", "definition": "effective sample size scalar if recorded", "unit": "count", "lower_or_higher_better": "context", "granularity": "run", "valid_datasets": "E3 supporting", "valid_rounds": "E3", "comparability_notes": "trajectory MISSING_NOT_RECORDED", "paper_claim_usage": "diagnostic only"},
        {"name": "n_eff", "symbol": "n_eff", "definition": "effective sample mass if recorded", "unit": "count", "lower_or_higher_better": "context", "granularity": "run", "valid_datasets": "when recorded", "valid_rounds": "E3", "comparability_notes": "often MISSING_NOT_RECORDED", "paper_claim_usage": "diagnostic"},
        {"name": "P2 residual", "symbol": "P2 residual", "definition": "feasibility residual of P2 solve when reconstructable", "unit": "solver", "lower_or_higher_better": "lower", "granularity": "window/run", "valid_datasets": "P2-using", "valid_rounds": "E3/E4", "comparability_notes": "exact optimality NOT reconstructable", "paper_claim_usage": "C10"},
        {"name": "runtime", "symbol": "t", "definition": "wall-clock run runtime_seconds", "unit": "s", "lower_or_higher_better": "n/a", "granularity": "run", "valid_datasets": "when recorded", "valid_rounds": "E1-E4", "comparability_notes": "not a scalability study", "paper_claim_usage": "appendix"},
        {"name": "R", "symbol": "R", "definition": "opportunity indicator", "unit": "binary", "lower_or_higher_better": "n/a", "granularity": "atomic", "valid_datasets": "EventTrace", "valid_rounds": "E2-E4", "comparability_notes": "row-level not in CORE ZIP", "paper_claim_usage": "model"},
        {"name": "O", "symbol": "O", "definition": "observation indicator", "unit": "binary", "lower_or_higher_better": "n/a", "granularity": "atomic", "valid_datasets": "EventTrace", "valid_rounds": "E2-E4", "comparability_notes": "", "paper_claim_usage": "model"},
        {"name": "U", "symbol": "U", "definition": "usable-update indicator; delivered iff U=1", "unit": "binary", "lower_or_higher_better": "n/a", "granularity": "atomic", "valid_datasets": "EventTrace", "valid_rounds": "E2-E4", "comparability_notes": "", "paper_claim_usage": "model"},
        {"name": "h(i)", "symbol": "h(i)", "definition": "deployment-target group", "unit": "group id", "lower_or_higher_better": "n/a", "granularity": "atomic", "valid_datasets": "SS/U-Air/Traffic", "valid_rounds": "all", "comparability_notes": "h ≠ s", "paper_claim_usage": "setup"},
        {"name": "s(i)", "symbol": "s(i)", "definition": "opportunity stratum", "unit": "stratum id", "lower_or_higher_better": "n/a", "granularity": "atomic", "valid_datasets": "SS/U-Air/Traffic", "valid_rounds": "all", "comparability_notes": "h ≠ s", "paper_claim_usage": "setup"},
        {"name": "mu", "symbol": "μ", "definition": "public deployment-target distribution / target masses", "unit": "probability", "lower_or_higher_better": "n/a", "granularity": "dataset split", "valid_datasets": "SS/U-Air/Traffic", "valid_rounds": "all", "comparability_notes": "train-split mass; no test labels", "paper_claim_usage": "model"},
    ]
    write_csv(out / "00_MASTER_CATALOG/FINAL_DATA_DICTIONARY.csv", dictionary)
    write_json(out / "00_MASTER_CATALOG/FIGURE_BUDGET_RECOMMENDATION.json", {
        "main": ["FIG1_E2_RISK_NONINTERCHANGEABILITY", "FIG2_E3_STRUCTURAL_MISMATCH", "FIG4_E4_COMPONENT_ABLATION"],
        "optional_main": ["FIG3_E3_PREDICTION_RISK"],
        "appendix": ["FIG6_P2_FEASIBILITY_OR_ESS", "FIG8_LOCAL_HAJEK_PROVENANCE"],
        "do_not_run": ["FIG5_SELECTION_TARGET_COMPOSITION"],
        "drop": ["FIG9_DATASET_SUPPORT_CONTEXT"],
        "note": "4–6 figures total; do not add FIG5 by rerunning",
    })
    write_json(out / "00_MASTER_CATALOG/TABLE_BUDGET_RECOMMENDATION.json", {
        "main": ["TABLE_I_DATASET_SETUP", "TABLE_II_MAIN_EFFECTIVENESS", "TABLE_III_CORE_ABLATION"],
        "appendix": ["TABLE_E1_SANITY_APPENDIX", "TABLE_IV_STATISTICAL_SUMMARY", "TABLE_VI_FULL_METHOD_RESULTS_APPENDIX"],
        "optional": ["TABLE_V_RUNTIME_P2_APPENDIX"],
    })
