"""Copy sealed sources into the freeze tree. Never mutate originals."""

from __future__ import annotations

import shutil
from pathlib import Path

from raven_mcs.paper_data_r1.io_util import copy_file, ensure_dir, write_json, write_text
from raven_mcs.final_paper_data_asset_freeze_r1.constants import E4_LABELS, NA, SUBDIRS

IGNORE = shutil.ignore_patterns("*.zip", "__pycache__", "*.pyc", ".DS_Store", "Thumbs.db", "_work")


def _copytree(src: Path, dst: Path) -> None:
    src, dst = Path(src), Path(dst)
    if not src.exists():
        return
    if src.is_file():
        copy_file(src, dst)
        return
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=IGNORE)


def prepare_dirs(out: Path) -> None:
    for rel in SUBDIRS:
        ensure_dir(out / rel)


def collect_all(root: Path, out: Path) -> dict:
    root, out = Path(root), Path(out)
    r2 = root / "paper_ready_r2"
    mec = root / "manuscript_evidence_closure_r1"
    td = root / "tdrive_protocol_seal_r1"
    prepare_dirs(out)

    _copytree(r2 / "01_core_data/e1", out / "01_PAPER_CORE/E1")
    _copytree(r2 / "01_core_data/e2", out / "01_PAPER_CORE/E2")
    _copytree(r2 / "01_core_data/e3", out / "01_PAPER_CORE/E3")
    _copytree(r2 / "01_core_data/e4", out / "01_PAPER_CORE/E4")
    _copytree(r2 / "01_core_data/master", out / "01_PAPER_CORE/master_r2")
    _copytree(r2 / "04_statistics", out / "01_PAPER_CORE/STATISTICS")
    _copytree(r2 / "00_index", out / "01_PAPER_CORE/CLAIM_MAPS")
    _copytree(r2 / "06_table_sources/TABLE_DATASET_SUMMARY_R2.csv", out / "01_PAPER_CORE/DATASET_METADATA/TABLE_DATASET_SUMMARY_R2.csv")
    _copytree(r2 / "01_core_data/master/DATASET_METADATA_MASTER_R2.csv", out / "01_PAPER_CORE/DATASET_METADATA/DATASET_METADATA_MASTER_R2.csv")

    _copytree(r2 / "02_supporting_data", out / "02_PAPER_SUPPORTING/r2_supporting")
    _copytree(r2 / "02_supporting_data/diagnostics_r2", out / "05_WINDOW_LEVEL/diagnostics_r2")
    _copytree(r2 / "02_supporting_data/e3/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv", out / "07_WEIGHTS/local_hajek_provenance/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv")
    _copytree(r2 / "02_supporting_data/e3/E3_LOCAL_HAJEK_PROVENANCE_REPORT.md", out / "07_WEIGHTS/local_hajek_provenance/E3_LOCAL_HAJEK_PROVENANCE_REPORT.md")
    _copytree(r2 / "02_supporting_data/solver", out / "09_P2_SOLVER/r2_solver")
    _copytree(r2 / "02_supporting_data/runtime", out / "11_RUNTIME_SYSTEM/r2_runtime")
    _copytree(r2 / "02_supporting_data/diagnostics", out / "10_ESS_VARIANCE/r2_theory_diagnostics")
    _copytree(r2 / "05_provenance", out / "14_SOURCE_PROVENANCE/r2_provenance")
    _copytree(r2 / "05_provenance/FINAL_CONFIG_REGISTRY_R2.csv", out / "13_CONFIGS/FINAL_CONFIG_REGISTRY_R2.csv")
    _copytree(r2 / "05_provenance/FINAL_CONFIG_REGISTRY_R2.json", out / "13_CONFIGS/FINAL_CONFIG_REGISTRY_R2.json")
    _copytree(r2 / "05_provenance/E2_EVENTTRACE_INDEX_120.csv", out / "12_EVENTTRACES/E2/E2_EVENTTRACE_INDEX_120.csv")
    _copytree(r2 / "03_raw_evidence/e3/e3_formal_runs_r1/E3_FORMAL_EVENTTRACE_MANIFEST.json", out / "12_EVENTTRACES/E3/E3_FORMAL_EVENTTRACE_MANIFEST.json")
    _copytree(r2 / "03_raw_evidence/e4/gen2/E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv", out / "12_EVENTTRACES/E4/E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv")

    _copytree(r2 / "07_figure_sources", out / "15_FIGURE_SOURCES/r2")
    _copytree(r2 / "06_table_sources", out / "16_TABLE_SOURCES/r2")
    if mec.is_dir():
        _copytree(mec / "03_figure_sources", out / "15_FIGURE_SOURCES/manuscript_closure_r1")
        _copytree(mec / "04_figures", out / "15_FIGURE_SOURCES/manuscript_closure_r1_rendered")
        _copytree(mec / "01_table_sources", out / "16_TABLE_SOURCES/manuscript_closure_r1")
        _copytree(mec / "02_tables", out / "16_TABLE_SOURCES/manuscript_closure_r1_md")
        _copytree(mec / "00_audit", out / "14_SOURCE_PROVENANCE/manuscript_closure_r1_audit")
        _copytree(mec / "09_tdrive_decision", out / "20_TDRIVE_RESERVE/manuscript_go_no_go")

    _copytree(r2 / "03_raw_evidence/e4/gen0", out / "18_INVALID_CANARY/e4_wo_inst_gen0")
    _copytree(r2 / "03_raw_evidence/e4/gen1", out / "17_SUPERSEDED/e4_wo_inst_gen1")
    _copytree(r2 / "03_raw_evidence/e4/gen2", out / "03_APPENDIX_CANDIDATES/e4_gen2_provenance")
    _copytree(r2 / "03_raw_evidence/e3", out / "03_APPENDIX_CANDIDATES/e3_raw_r2")
    _copytree(r2 / "03_raw_evidence/e2", out / "03_APPENDIX_CANDIDATES/e2_raw_r2")
    _copytree(r2 / "03_raw_evidence/e1", out / "03_APPENDIX_CANDIDATES/e1_raw_r2")
    _copytree(r2 / "03_raw_evidence/source_snapshots", out / "14_SOURCE_PROVENANCE/source_snapshots")
    _copytree(r2 / "02_supporting_data/e3/E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv", out / "19_NOT_COMPARABLE/E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv")
    _copytree(r2 / "02_supporting_data/e3/E3_TRAFFIC_REFERENCE_ONLY.csv", out / "19_NOT_COMPARABLE/E3_TRAFFIC_REFERENCE_ONLY.csv")
    _copytree(r2 / "00_index/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json", out / "19_NOT_COMPARABLE/TRAFFIC_COMPARABILITY_BOUNDARY_R2.json")
    _copytree(r2 / "04_statistics/E4_FINAL_STATISTICS.csv", out / "17_SUPERSEDED/E4_FINAL_STATISTICS_pre_R2.csv")
    _copytree(r2 / "06_table_sources/TABLE_E4_CORE_ABLATION.csv", out / "17_SUPERSEDED/TABLE_E4_CORE_ABLATION_pre_R2.csv")
    _copytree(r2 / "06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv", out / "16_TABLE_SOURCES/r2/TABLE_E3_MAIN_EFFECTIVENESS.csv")

    if td.is_dir():
        _copytree(td, out / "20_TDRIVE_RESERVE/protocol_seal_r1")
        _copytree(td / "06_eventtrace", out / "12_EVENTTRACES/TDRIVE_PROTOCOL_ONLY")

    write_json(out / "01_PAPER_CORE/E4/E4_FINAL_LABELS.json", {**E4_LABELS, "Debt_note": "quantitatively small"})
    write_json(
        out / "20_TDRIVE_RESERVE/TDRIVE_RESERVE_STATUS.json",
        {
            "formal_runs_completed": 0,
            "paper_result_status": "NOT_RUN",
            "protocol_status": "SEALED",
            "evidence_status": "PROVENANCE_ONLY",
            "paper_role": "REVIEWER_RESERVE",
            "default_action": "DO_NOT_RUN_BEFORE_SUBMISSION",
            "activation_condition": "MATERIAL_REVIEWER_REQUEST_OR_LATER_EXPLICIT_TEACHER_APPROVAL",
        },
    )
    write_text(
        out / "18_INVALID_CANARY/README.md",
        "E4 w/o-Inst Generation 0 is INVALID (P2-off). Canary/failed attempts are not paper evidence.\n",
    )
    write_text(
        out / "17_SUPERSEDED/README.md",
        "E4 w/o-Inst Generation 1 and pre-R2 statistical/table products are SUPERSEDED. Do not use as paper-facing.\n",
    )
    write_json(
        out / "22_REPORTS/NO_NEW_EXPERIMENT_ATTESTATION.json",
        {
            "round": "RAVEN-MCS-FINAL-PAPER-DATA-ASSET-FREEZE-R1",
            "training_started": False,
            "formal_run_started": False,
            "canary_started": False,
            "tdrive_run_started": False,
            "new_seed_added": False,
            "new_dataset_added": False,
            "new_baseline_added": False,
            "scientific_metric_changed": False,
            "scientific_config_changed": False,
            "EventTrace_regenerated_for_results": False,
            "original_evidence_unchanged": True,
            "r2_authority_preserved": True,
            "writes_only_under": [str(out.name) + "/", "deliverables/"],
        },
    )
    missing_window = out / "06_SELECTION_PROCESS/propensity/PROPENSITY_STATUS.json"
    write_json(
        missing_window,
        {
            "pi_opp": NA,
            "p_obs": NA,
            "q_use": NA,
            "status": NA,
            "note": "No new propensity estimation. Offline reconstructable distributions were not sealed as row-level files.",
        },
    )
    write_json(
        out / "08_CALIBRATION_DEBT/debt/DEBT_TRAJECTORY_STATUS.json",
        {"debt_trajectory": NA, "per_group_debt_series": NA, "note": "Do not rerun. Leave MISSING_NOT_RECORDED."},
    )
    write_json(
        out / "08_CALIBRATION_DEBT/calibration/TARGET_COMPOSITION_STATUS.json",
        {
            "pre_calibration_composition": NA,
            "post_calibration_composition": NA,
            "fig5_mechanism": "NOT_AVAILABLE_WITHOUT_NEW_RUN",
        },
    )
    return {"r2": str(r2), "mec": str(mec), "tdrive": str(td)}
