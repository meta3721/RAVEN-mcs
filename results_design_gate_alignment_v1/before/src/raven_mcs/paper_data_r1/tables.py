"""Build main table and figure source CSVs with meta JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import read_csv, write_csv, write_meta_json, write_text


def _mean(vals: list[float]) -> float | None:
    return sum(vals) / len(vals) if vals else None


def build_tables_and_figures(paper: Path) -> dict[str, Any]:
    paper = Path(paper)
    tables = paper / "06_table_sources"
    figs = paper / "07_figure_sources"
    idx = paper / "00_index"
    tables.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    # TABLE E1
    e1_src = paper / "01_core_data" / "e1" / "E1_FINAL_VALID_RUNS.csv"
    e1_rows = read_csv(e1_src) if e1_src.is_file() else []
    e1_table = []
    by_m: dict[str, list[dict[str, str]]] = {}
    for r in e1_rows:
        by_m.setdefault(r.get("method", ""), []).append(r)
    for method, rs in sorted(by_m.items()):
        def col(name: str) -> str:
            vals = []
            for x in rs:
                try:
                    vals.append(float(x[name]))
                except (KeyError, TypeError, ValueError):
                    pass
            m = _mean(vals)
            return "" if m is None else f"{m:.6g}"

        e1_table.append(
            {
                "method": method,
                "n": len(rs),
                "RMSE_mu_mean": col("RMSE_mu"),
                "Tail_RMSE_mean": col("Tail_RMSE"),
                "Delta_group_mean": col("Delta_group"),
                "Delta_c_s_mean": col("Delta_c_s"),
                "role": "balanced_no_harm_sanity",
            }
        )
    p = write_csv(tables / "TABLE_E1_BALANCED_SANITY.csv", e1_table)
    write_meta_json(
        p,
        source_files=["01_core_data/e1/E1_FINAL_VALID_RUNS.csv"],
        filters="E1 accepted sealed runs",
        transformations="mean over seeds",
        metric_definitions={"RMSE_mu": "target RMSE"},
        included_seeds=sorted({r.get("seed") for r in e1_rows}),
        statistical_method="descriptive means; no-harm tests in E1_FINAL_STATISTICS",
    )

    # TABLE E2
    e2_src = paper / "01_core_data" / "e2" / "E2_D_ALIGNED_PER_SEED.csv"
    e2_rows = read_csv(e2_src) if e2_src.is_file() else []
    e2_table = []
    by_m2: dict[str, list[dict[str, str]]] = {}
    for r in e2_rows:
        by_m2.setdefault(r.get("method", ""), []).append(r)
    for method, rs in sorted(by_m2.items()):
        signs = [int(float(x["sign_D"])) for x in rs if x.get("sign_D") not in ("", None)]
        dvals = []
        for x in rs:
            try:
                dvals.append(float(x["D_aligned"]))
            except (TypeError, ValueError):
                pass
        e2_table.append(
            {
                "method": method,
                "n": len(rs),
                "D_aligned_mean": "" if not dvals else f"{_mean(dvals):.6g}",
                "n_negative_sign": sum(1 for s in signs if s < 0),
                "n_positive_sign": sum(1 for s in signs if s > 0),
                "scenario": "complete_aligned",
            }
        )
    p = write_csv(tables / "TABLE_E2_RISK_SEMANTICS.csv", e2_table)
    write_meta_json(
        p,
        source_files=["01_core_data/e2/E2_D_ALIGNED_PER_SEED.csv"],
        filters="complete_aligned only",
        transformations="per-method mean D_aligned and sign counts",
        metric_definitions={"D_aligned": "Delta RMSE_mu - Delta RMSE_rho"},
        included_seeds=sorted({r.get("seed") for r in e2_rows}),
        statistical_method="direction stability summary",
    )

    # TABLE E3 main
    e3_src = paper / "01_core_data" / "e3" / "E3_MAIN_COMPARABLE_LONG.csv"
    e3_rows = read_csv(e3_src) if e3_src.is_file() else []
    e3_table = []
    keyset: dict[tuple[str, str], list[dict[str, str]]] = {}
    for r in e3_rows:
        keyset.setdefault((r.get("dataset", ""), r.get("method", "")), []).append(r)
    for (ds, method), rs in sorted(keyset.items()):
        def mcol(name: str) -> str:
            vals = []
            for x in rs:
                try:
                    if x.get(f"{name}_status") == "NOT_COMPARABLE":
                        continue
                    vals.append(float(x[name]))
                except (KeyError, TypeError, ValueError):
                    pass
            m = _mean(vals)
            return "" if m is None else f"{m:.6g}"

        e3_table.append(
            {
                "dataset": ds,
                "method": method,
                "n": len(rs),
                "RMSE_mu_mean": mcol("RMSE_mu"),
                "MAE_mu_mean": mcol("MAE_mu"),
                "Tail_RMSE_mean": mcol("Tail_RMSE"),
                "Delta_group_mean": mcol("Delta_group"),
                "Delta_c_s_mean": mcol("Delta_c_s"),
                "comparison_class": "SCI_COMPARABLE_MAIN",
            }
        )
    p = write_csv(tables / "TABLE_E3_MAIN_EFFECTIVENESS.csv", e3_table)
    write_meta_json(
        p,
        source_files=["01_core_data/e3/E3_MAIN_COMPARABLE_LONG.csv"],
        filters="comparison_class=SCI_COMPARABLE_MAIN (SensorScope+U-Air only)",
        transformations="mean over seeds; Traffic excluded",
        excluded_rows="all NSW-Traffic / NOT_COMPARABLE",
        included_seeds=sorted({r.get("seed") for r in e3_rows}),
        statistical_method="descriptive means; inferential tests in E3 Holms",
    )

    # TABLE E3 full methods supplement (includes traffic as reference rows flagged)
    e3_all = paper / "01_core_data" / "e3" / "E3_FINAL_VALID_EVIDENCE_INDEX.csv"
    all_rows = read_csv(e3_all) if e3_all.is_file() else []
    supp = [
        {
            "dataset": r.get("dataset"),
            "method": r.get("method"),
            "seed": r.get("seed"),
            "comparison_class": r.get("comparison_class"),
            "RMSE_mu": r.get("RMSE_mu"),
            "Delta_group": r.get("Delta_group"),
            "Delta_c_s": r.get("Delta_c_s"),
            "paper_use": "main" if r.get("comparison_class") == "SCI_COMPARABLE_MAIN" else "reference_only",
        }
        for r in all_rows
    ]
    p = write_csv(tables / "TABLE_E3_FULL_METHODS_SUPPLEMENT.csv", supp)
    write_meta_json(
        p,
        source_files=["01_core_data/e3/E3_FINAL_VALID_EVIDENCE_INDEX.csv"],
        filters="all E3 index rows",
        transformations="none",
        excluded_rows="",
        statistical_method="supplement; Traffic not for main inference",
    )

    # TABLE E4
    e4_src = paper / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    e4_rows = read_csv(e4_src) if e4_src.is_file() else []
    e4_table = []
    key4: dict[tuple[str, str], list[dict[str, str]]] = {}
    for r in e4_rows:
        key4.setdefault((r.get("dataset", ""), r.get("configuration", "")), []).append(r)
    for (ds, conf), rs in sorted(key4.items()):
        def mcol4(name: str) -> str:
            vals = []
            for x in rs:
                try:
                    vals.append(float(x[name]))
                except (KeyError, TypeError, ValueError):
                    pass
            m = _mean(vals)
            return "" if m is None else f"{m:.6g}"

        e4_table.append(
            {
                "dataset": ds,
                "configuration": conf,
                "n": len(rs),
                "generation": rs[0].get("generation", "") if rs else "",
                "RMSE_mu_mean": mcol4("RMSE_mu"),
                "Tail_RMSE_mean": mcol4("Tail_RMSE"),
                "Delta_group_mean": mcol4("Delta_group"),
                "Delta_c_s_mean": mcol4("Delta_c_s"),
            }
        )
    p = write_csv(tables / "TABLE_E4_CORE_ABLATION.csv", e4_table)
    write_meta_json(
        p,
        source_files=["01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv"],
        filters="final 240 cells; wo_inst Gen2 only",
        transformations="mean over seeds",
        excluded_rows="wo_inst Gen0/Gen1",
        included_seeds=sorted({r.get("seed") for r in e4_rows}),
        statistical_method="descriptive means; effects in COMPONENT_EFFECT_MASTER",
    )

    e4_eff = paper / "01_core_data" / "e4" / "E4_COMPONENT_EFFECT_MASTER.csv"
    eff_rows = read_csv(e4_eff) if e4_eff.is_file() else []
    p = write_csv(tables / "TABLE_E4_COMPONENT_EFFECTS.csv", eff_rows)
    write_meta_json(
        p,
        source_files=["01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv"],
        filters="all components",
        transformations="copy of sealed R3 numerical cells + means",
        statistical_method="paired Holm from sealed claim matrix",
    )

    p2 = paper / "02_supporting_data" / "solver" / "P2_FEASIBILITY_SUMMARY.csv"
    p2_rows = read_csv(p2) if p2.is_file() else []
    p = write_csv(tables / "TABLE_P2_DIAGNOSTICS_SUPPLEMENT.csv", p2_rows)
    write_meta_json(
        p,
        source_files=["02_supporting_data/solver/P2_FEASIBILITY_SUMMARY.csv"],
        filters="supplement only",
        transformations="none",
        statistical_method="feasibility audit boundary",
    )

    dataset_summary = [
        {
            "dataset": "SensorScope",
            "domain": "environmental sensing",
            "paper_role": "E3/E4 main",
            "number_clients": "",
            "data_source_checksum": "",
            "status_note": "MISSING_NOT_RECORDED for fields not in sealed summaries",
        },
        {
            "dataset": "U-Air",
            "domain": "urban air quality",
            "paper_role": "E3/E4 main",
            "number_clients": "",
            "data_source_checksum": "",
            "status_note": "MISSING_NOT_RECORDED for fields not in sealed summaries",
        },
        {
            "dataset": "NSW-Traffic",
            "domain": "traffic",
            "paper_role": "E2 main; E3 reference-only / NOT_COMPARABLE",
            "number_clients": "",
            "data_source_checksum": "",
            "status_note": "MISSING_NOT_RECORDED",
        },
        {
            "dataset": "Balanced",
            "domain": "synthetic/semi-synthetic sanity",
            "paper_role": "E1 no-harm",
            "number_clients": "",
            "data_source_checksum": "",
            "status_note": "MISSING_NOT_RECORDED",
        },
        {
            "dataset": "T-Drive-Speed",
            "domain": "mobility",
            "paper_role": "future external validation only",
            "number_clients": "",
            "data_source_checksum": "",
            "status_note": "readiness only; no formal runs this round",
        },
    ]
    p = write_csv(tables / "TABLE_DATASET_SUMMARY.csv", dataset_summary)
    write_meta_json(
        p,
        source_files=["08_tdrive_readiness", "E3/E2 seals"],
        filters="dataset-level",
        transformations="missing fields left empty (not zero-filled)",
        statistical_method="n/a",
    )

    # Figures
    fig1 = [
        {
            "method": r.get("method"),
            "seed": r.get("seed"),
            "D_aligned": r.get("D_aligned"),
            "sign_D": r.get("sign_D"),
            "Delta_mu_aligned": r.get("Delta_mu_aligned"),
            "Delta_rho_aligned": r.get("Delta_rho_aligned"),
        }
        for r in e2_rows
    ]
    p = write_csv(figs / "FIG1_E2_RISK_NONINTERCHANGEABILITY.csv", fig1)
    write_meta_json(
        p,
        source_files=["01_core_data/e2/E2_D_ALIGNED_PER_SEED.csv"],
        filters="complete_aligned",
        transformations="none",
    )

    fig2 = [
        {
            "dataset": r.get("dataset"),
            "method": r.get("method"),
            "seed": r.get("seed"),
            "Delta_group": r.get("Delta_group"),
            "Delta_c_s": r.get("Delta_c_s"),
        }
        for r in e3_rows
    ]
    p = write_csv(figs / "FIG2_E3_STRUCTURAL_MISMATCH.csv", fig2)
    write_meta_json(
        p,
        source_files=["01_core_data/e3/E3_MAIN_COMPARABLE_LONG.csv"],
        filters="SCI_COMPARABLE_MAIN",
        transformations="none",
        excluded_rows="Traffic",
    )

    fig3 = [
        {
            "dataset": r.get("dataset"),
            "component": r.get("component"),
            "metric": r.get("metric"),
            "paired_seed_mean_difference": r.get("paired_seed_mean_difference"),
            "Holm_p": r.get("Holm_p"),
            "direction": r.get("direction"),
            "qualitative_status": r.get("qualitative_status"),
        }
        for r in eff_rows
    ]
    p = write_csv(figs / "FIG3_E4_COMPONENT_REMOVAL.csv", fig3)
    write_meta_json(
        p,
        source_files=["01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv"],
        filters="all components",
        transformations="none",
    )

    # Optional figures
    opt_rmse = [
        {"dataset": r.get("dataset"), "method": r.get("method"), "seed": r.get("seed"), "RMSE_mu": r.get("RMSE_mu")}
        for r in e3_rows
    ]
    for name, rows, src in (
        ("FIG_OPTIONAL_E3_RMSE.csv", opt_rmse, "E3_MAIN_COMPARABLE_LONG"),
        (
            "FIG_OPTIONAL_E3_TAIL_RMSE.csv",
            [
                {
                    "dataset": r.get("dataset"),
                    "method": r.get("method"),
                    "seed": r.get("seed"),
                    "Tail_RMSE": r.get("Tail_RMSE"),
                }
                for r in e3_rows
            ],
            "E3_MAIN_COMPARABLE_LONG",
        ),
        ("FIG_OPTIONAL_E4_HEATMAP.csv", fig3, "E4_COMPONENT_EFFECT_MASTER"),
    ):
        p = write_csv(figs / name, rows)
        write_meta_json(p, source_files=[src], filters="optional", transformations="none")

    # Empty optional placeholders with status
    for name in ("FIG_OPTIONAL_DEBT_TRAJECTORY.csv", "FIG_OPTIONAL_ESS.csv", "FIG_OPTIONAL_P2_RUNTIME.csv"):
        p = write_csv(
            figs / name,
            [{"status": "MISSING_NOT_RECORDED", "notes": "trajectory not packaged as sealed CSV this round"}],
        )
        write_meta_json(p, source_files=[], filters="optional missing", transformations="none")

    # Provenance map
    prov_map = [
        {
            "artifact_id": "Main Table 1",
            "paper_role": "E3 overall main results",
            "source_csv": "06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv",
            "original_evidence_files": "E3_FORMAL_RUN_STATUS.csv;final_metrics.json",
            "datasets": "SensorScope,U-Air",
            "methods": "all main comparable",
            "seeds": "30001-30020",
            "metrics": "RMSE_mu,MAE_mu,Tail_RMSE,Delta_group,Delta_c_s",
            "filter": "SCI_COMPARABLE_MAIN",
            "aggregation": "mean over seeds",
            "statistical_test": "Holm paired (separate stats files)",
            "excluded_evidence": "Traffic NOT_COMPARABLE",
            "claim_ceiling": "C3,C4",
        },
        {
            "artifact_id": "Main Table 2",
            "paper_role": "E4 core ablation",
            "source_csv": "06_table_sources/TABLE_E4_CORE_ABLATION.csv",
            "original_evidence_files": "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
            "datasets": "SensorScope,U-Air",
            "methods": "6 configurations",
            "seeds": "30001-30020",
            "metrics": "RMSE_mu,Tail_RMSE,Delta_group,Delta_c_s",
            "filter": "240 cells; Gen2 wo_inst",
            "aggregation": "mean over seeds",
            "statistical_test": "component effects via claim matrix",
            "excluded_evidence": "wo_inst Gen0/Gen1",
            "claim_ceiling": "C5,C6,C7",
        },
        {
            "artifact_id": "Fig. 1",
            "paper_role": "E2 risk non-interchangeability",
            "source_csv": "07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv",
            "original_evidence_files": "COMPLETE_ALIGNED_DOD.csv",
            "datasets": "NSW-Traffic",
            "methods": "5",
            "seeds": "30001-30020",
            "metrics": "D_aligned",
            "filter": "complete_aligned",
            "aggregation": "per-seed",
            "statistical_test": "direction stability",
            "excluded_evidence": "",
            "claim_ceiling": "C1,C2",
        },
        {
            "artifact_id": "Fig. 2",
            "paper_role": "E3 structural mismatch reduction",
            "source_csv": "07_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH.csv",
            "original_evidence_files": "E3 main comparable",
            "datasets": "SensorScope,U-Air",
            "methods": "all main",
            "seeds": "30001-30020",
            "metrics": "Delta_group,Delta_c_s",
            "filter": "SCI_COMPARABLE_MAIN",
            "aggregation": "per-seed",
            "statistical_test": "Holm",
            "excluded_evidence": "Traffic",
            "claim_ceiling": "C3",
        },
        {
            "artifact_id": "Fig. 3",
            "paper_role": "E4 component removal effect",
            "source_csv": "07_figure_sources/FIG3_E4_COMPONENT_REMOVAL.csv",
            "original_evidence_files": "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
            "datasets": "SensorScope,U-Air",
            "methods": "ablations",
            "seeds": "30001-30020",
            "metrics": "component effects",
            "filter": "final valid",
            "aggregation": "paired mean diff",
            "statistical_test": "Holm",
            "excluded_evidence": "Gen0/Gen1 wo_inst",
            "claim_ceiling": "C5,C6,C7",
        },
    ]
    write_csv(idx / "FIGURE_TABLE_PROVENANCE_MAP.csv", prov_map)
    write_text(
        idx / "FIGURE_TABLE_PROVENANCE_MAP.md",
        "\n".join(
            ["# Figure/Table provenance map", ""]
            + [f"- **{r['artifact_id']}**: `{r['source_csv']}` ({r['paper_role']})" for r in prov_map]
            + [""]
        ),
    )

    return {"n_tables": 8, "n_main_figures": 3}
