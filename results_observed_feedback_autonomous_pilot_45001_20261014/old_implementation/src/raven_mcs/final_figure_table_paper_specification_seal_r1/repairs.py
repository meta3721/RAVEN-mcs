"""Copy frozen sources, FIG6 repair, G52 audit, relative-path log."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from raven_mcs.paper_data_r1.io_util import copy_file, sha256_file, write_csv, write_json, write_text
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import FREEZE


def _rel(root: Path, p: Path) -> str:
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.name


def _meta(path: Path, **kwargs) -> None:
    write_json(Path(str(path) + ".meta.json"), {"output_hash": sha256_file(path) if path.is_file() else "", **kwargs})


def copy_and_repair(root: Path, out: Path) -> dict:
    freeze = root / FREEZE
    mec = root / "manuscript_evidence_closure_r1"
    fig_dir = out / "05_PROVENANCE/FINAL_FIGURE_SOURCES"
    tab_dir = out / "05_PROVENANCE/FINAL_TABLE_SOURCES"
    repairs = []

    pairs = [
        (
            "FIG_E1",
            freeze / "15_FIGURE_SOURCES/manuscript_closure_r1/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv",
            mec / "03_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv",
            fig_dir / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv",
        ),
        (
            "FIG_E2",
            freeze / "15_FIGURE_SOURCES/manuscript_closure_r1/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv",
            mec / "03_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv",
            fig_dir / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv",
        ),
        (
            "FIG_E3",
            freeze / "01_PAPER_CORE/E3/E3_PREDICTION_METRICS_MASTER.csv",
            root / "paper_ready_r2/01_core_data/e3/E3_PREDICTION_METRICS_MASTER.csv",
            fig_dir / "FIG_E3_E3_PREDICTION_RISK.csv",
        ),
        (
            "FIG_E4",
            freeze / "15_FIGURE_SOURCES/manuscript_closure_r1/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv",
            mec / "03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv",
            fig_dir / "FIG_E4_E4_COMPONENT_ABLATION.csv",
        ),
        (
            "TABLE_I",
            freeze / "16_TABLE_SOURCES/manuscript_closure_r1/TABLE_I_DATASETS.csv",
            mec / "01_table_sources/TABLE_I_DATASETS.csv",
            tab_dir / "TABLE_I_DATASET_PROTOCOL.csv",
        ),
        (
            "TABLE_II",
            freeze / "16_TABLE_SOURCES/manuscript_closure_r1/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv",
            mec / "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv",
            tab_dir / "TABLE_II_MAIN_EFFECTIVENESS.csv",
        ),
        (
            "TABLE_III",
            freeze / "16_TABLE_SOURCES/manuscript_closure_r1/TABLE_III_E4_CORE_ABLATION_FINAL.csv",
            mec / "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv",
            tab_dir / "TABLE_III_CORE_ABLATION.csv",
        ),
        (
            "APP_T1",
            freeze / "16_TABLE_SOURCES/manuscript_closure_r1/TABLE_E1_BALANCED_SANITY_FINAL.csv",
            mec / "01_table_sources/TABLE_E1_BALANCED_SANITY_FINAL.csv",
            tab_dir / "APP_T1_E1_BALANCED_SANITY.csv",
        ),
        (
            "APP_F1",
            freeze / "07_WEIGHTS/local_hajek_provenance/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv",
            root / "paper_ready_r2/02_supporting_data/e3/E3_LOCAL_HAJEK_PROVENANCE_SUMMARY.csv",
            fig_dir / "APP_F1_LOCAL_HAJEK_PROVENANCE.csv",
        ),
        (
            "APP_T3",
            freeze / "16_TABLE_SOURCES/r2/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv",
            root / "paper_ready_r2/06_table_sources/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv",
            tab_dir / "APP_T3_E3_FULL_METHODS.csv",
        ),
        (
            "APP_T5",
            freeze / "11_RUNTIME_SYSTEM/RUNTIME_SUMMARY_EXISTING.csv",
            freeze / "11_RUNTIME_SYSTEM/RUNTIME_SUMMARY_EXISTING.csv",
            tab_dir / "APP_T5_RUNTIME_SUMMARY_EXISTING.csv",
        ),
    ]
    hashes = {}
    for key, preferred, fallback, dest in pairs:
        src = preferred if preferred.is_file() else fallback
        before = sha256_file(src)
        copy_file(src, dest)
        after = sha256_file(dest)
        hashes[key] = {"src": _rel(root, src), "dest": dest.relative_to(out).as_posix(), "sha256": after}
        rel_old = src.as_posix()
        new_rel = dest.relative_to(out).as_posix()
        repairs.append(
            {
                "asset": key,
                "old_path": rel_old,
                "new_relative_path": new_rel,
                "file_exists": True,
                "sha256_before": before,
                "sha256_after": after,
                "scientific_content_changed": False,
            }
        )
        _meta(
            dest,
            input_assets=[_rel(root, src)],
            input_hashes=[before],
            filters="copy only; SensorScope/U-Air already applied in source where required",
            aggregation="none",
            statistical_protocol="unchanged sealed protocol",
            scientific_semantics_changed=False,
        )

    stats = freeze / "01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv"
    if stats.is_file():
        hashes["APP_T2"] = {
            "src": _rel(root, stats),
            "dest": "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv",
            "sha256": sha256_file(stats),
            "copied": False,
            "note": "not copied into this seal; freeze file contains historical machine paths in source_file column",
        }

    # FIG6: placeholder ESS/runtime CSVs are NOT figure-ready. Build appendix source from real P2 certificate summary.
    cert = freeze / "09_P2_SOLVER/r2_solver/E3_P2_CERTIFICATE_SUMMARY.csv"
    fig6_decision = "DROP_LOW_VALUE"
    fig6_note = "placeholder ESS/P2_RUNTIME CSVs are MISSING_NOT_RECORDED"
    if cert.is_file():
        df = pd.read_csv(cert)
        df = df[~df["dataset"].astype(str).str.lower().isin(["traffic", "nsw-traffic", "nsw_traffic"])].copy()
        dest = fig_dir / "APP_F2_P2_FEASIBILITY_SUMMARY.csv"
        rows = df.to_dict(orient="records")
        write_csv(dest, rows)
        agg = (
            df.groupby(["dataset", "certificate_status"], dropna=False)
            .agg(n_runs=("seed", "count"), mean_n_windows=("n_windows", "mean"), min_n_windows=("n_windows", "min"), max_n_windows=("n_windows", "max"))
            .reset_index()
        )
        dest2 = fig_dir / "APP_F2_P2_FEASIBILITY_BY_STATUS.csv"
        write_csv(dest2, agg.to_dict(orient="records"))
        _meta(
            dest,
            input_assets=["RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/09_P2_SOLVER/r2_solver/E3_P2_CERTIFICATE_SUMMARY.csv"],
            input_hashes=[sha256_file(cert)],
            filters="drop Traffic rows if any; no metric recompute",
            aggregation="identity copy of sealed certificate summary",
            statistical_protocol="none; diagnostic counts only",
            scientific_semantics_changed=False,
        )
        _meta(
            dest2,
            input_assets=["RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/09_P2_SOLVER/r2_solver/E3_P2_CERTIFICATE_SUMMARY.csv"],
            input_hashes=[sha256_file(cert)],
            filters="Traffic excluded",
            aggregation="groupby dataset×certificate_status count/mean/min/max n_windows",
            statistical_protocol="deterministic summary",
            scientific_semantics_changed=False,
        )
        hashes["APP_F2"] = {"src": _rel(root, cert), "dest": dest.relative_to(out).as_posix(), "sha256": sha256_file(dest)}
        hashes["APP_F2_AGG"] = {"dest": dest2.relative_to(out).as_posix(), "sha256": sha256_file(dest2)}
        fig6_decision = "APPENDIX_READY"
        fig6_note = "OPTION A: sealed E3_P2_CERTIFICATE_SUMMARY (Traffic excluded). Placeholder FIG_OPTIONAL_ESS/P2_RUNTIME are not figure sources."
        repairs.append(
            {
                "asset": "APP_F2",
                "old_path": str(cert),
                "new_relative_path": dest.relative_to(out).as_posix(),
                "file_exists": True,
                "sha256_before": sha256_file(cert),
                "sha256_after": sha256_file(dest),
                "scientific_content_changed": False,
            }
        )

    write_csv(out / "02_PACKAGING_REPAIR/ABSOLUTE_TO_RELATIVE_PATH_REPAIR.csv", repairs)
    write_json(
        out / "02_PACKAGING_REPAIR/FIG6_READINESS_REPAIR_R1.json",
        {
            "previous_recommendation": "APPENDIX_FIGURE_READY",
            "previous_sources": [
                "paper_ready_r2/07_figure_sources/FIG_OPTIONAL_ESS.csv",
                "paper_ready_r2/07_figure_sources/FIG_OPTIONAL_P2_RUNTIME.csv",
            ],
            "previous_source_content": "MISSING_NOT_RECORDED placeholders; identical SHA256",
            "option_a_used": fig6_decision == "APPENDIX_READY",
            "option_b": "SOURCE_READY_OPTIONAL or DROP_LOW_VALUE if no clean numeric source",
            "final_status": fig6_decision,
            "new_experiment": False,
            "scientific_data_changed": False,
            "note": fig6_note,
        },
    )
    write_text(
        out / "02_PACKAGING_REPAIR/FIG6_READINESS_REPAIR_R1.md",
        "\n".join(
            [
                "# FIG6 readiness repair",
                "",
                "Previous freeze marked `FIG6_P2_FEASIBILITY_OR_ESS` as `APPENDIX_FIGURE_READY`.",
                "The cited CSVs `FIG_OPTIONAL_ESS.csv` and `FIG_OPTIONAL_P2_RUNTIME.csv` contain only `MISSING_NOT_RECORDED` and share one SHA256. That is not a numeric figure source.",
                "",
                f"**Decision: {fig6_decision}.** {fig6_note}",
                "",
                "No experiment was run. Exact post-hoc P2 optimality remains not reconstructable.",
                "",
            ]
        ),
    )
    write_json(
        out / "02_PACKAGING_REPAIR/FDAF_G52_REPAIR_AUDIT.json",
        {
            "old_gate_status": "FAIL (transient): substring `**yes**` did not match report text `**YES.**`",
            "report_statement": "Section 41: manuscript-critical data available — YES. RQ1/RQ2/RQ3 core fields are present.",
            "final_status_statement": "B. RAVEN_MCS_FINAL_DATA_R1_FROZEN_CORE_READY_SUPPORTING_GAPS_REMAIN; manuscript_critical_complete=true",
            "cause": "gate bookkeeping / markdown punctuation, not missing core data",
            "repair": "document only; freeze report already stated completeness; subsequent freeze checker 52/52 PASS",
            "scientific_data_changed": False,
        },
    )
    write_text(
        out / "02_PACKAGING_REPAIR/FDAF_G52_REPAIR_AUDIT.md",
        "# FDAF-G52 repair\n\nThe expected scientific state is that manuscript-critical data are complete. The freeze report already said so. G52 failed once because `**yes**` is not a substring of `**YES.**`. Bookkeeping was repaired in the freeze round; this seal does not change scientific data.\n",
    )
    return {"hashes": hashes, "fig6": fig6_decision}
