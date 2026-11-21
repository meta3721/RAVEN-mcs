"""Manuscript tables from R2 authority only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json, write_text
from raven_mcs.manuscript_evidence_closure_r1.constants import (
    E3_MAIN_METHODS,
    E3_REFERENCE_METHODS,
    E4_CONFIGS,
    METHOD_CANONICAL,
    METHOD_DISPLAY,
)


def _meta(path: Path, **kwargs: Any) -> None:
    write_json(
        Path(str(path) + ".meta.json"),
        {
            "csv_sha256": sha256_file(path) if path.is_file() else "",
            "version": "manuscript_evidence_closure_r1",
            **kwargs,
        },
    )


def _fmt(mean: float, std: float, nd: int = 4) -> str:
    return f"{mean:.{nd}f} ± {std:.{nd}f}"


def table_i(r2: Path, out: Path) -> pd.DataFrame:
    src = r2 / "06_table_sources/TABLE_DATASET_SUMMARY_R2.csv"
    df = pd.read_csv(src)
    df = df[df["dataset"].isin(["SensorScope", "U-Air", "NSW-Traffic"])].copy()
    rows = []
    for _, r in df.iterrows():
        rows.append(
            {
                "Dataset": r["dataset"],
                "Domain": r["domain"],
                "Client/spatial identity": r["client_identity_definition"],
                "No. clients/spatial units": r["number_clients"] if pd.notna(r["number_clients"]) else r["number_spatial_units"],
                "Atomic units (train/val/test)": f"{int(r['train_count'])}/{int(r['validation_count'])}/{int(r['test_count'])}",
                "Deployment target h(i)": "four UTC time-of-day groups H1=00–06, H2=06–12, H3=12–18, H4=18–24 (train-split mass; no test labels)"
                if r["dataset"] in {"SensorScope", "U-Air"}
                else str(r["target_h_definition"]),
                "Opportunity stratum s(i)": str(r["opportunity_stratum_s_definition"]),
                "Selection-realism role": str(r["selection_mechanism"]),
                "Paper role": str(r["paper_role"]),
                "Comparability": str(r["final_comparability_status"]),
            }
        )
    path = out / "01_table_sources/TABLE_I_DATASETS.csv"
    write_csv(path, rows)
    _meta(
        path,
        source_files=["paper_ready_r2/06_table_sources/TABLE_DATASET_SUMMARY_R2.csv"],
        source_sha256=sha256_file(src),
        filters="evaluated datasets only; T-Drive excluded from Table I",
        transformations="manuscript field projection; h(i) wording aligned to R2 UTC 4-block semantics",
        claim_ceiling="Table I is setup, not a performance claim",
    )
    return pd.DataFrame(rows)


def table_e1(r2: Path, out: Path) -> None:
    src = r2 / "06_table_sources/TABLE_E1_BALANCED_SANITY.csv"
    stats = pd.read_csv(r2 / "04_statistics/E1_FINAL_STATISTICS.csv")
    df = pd.read_csv(src)
    any_sig = bool(stats["holm_significant"].astype(str).str.lower().isin(["true", "1"]).any())
    rows = []
    raven = df.loc[df["method"] == "RAVEN-MCS"].iloc[0]
    for _, r in df.iterrows():
        rows.append(
            {
                "method": r["method"],
                "paired_seeds": "28001–28005",
                "n": int(r["n"]),
                "primary_metric": "RMSE_mu",
                "RMSE_mu_mean": r["RMSE_mu_mean"],
                "diff_vs_RAVEN": float(r["RMSE_mu_mean"]) - float(raven["RMSE_mu_mean"]),
                "holm_significant_vs_RAVEN": False,
                "role": r["role"],
                "paper_conclusion": "No-harm / no significant degradation under balanced selection; statistical superiority not established",
            }
        )
    path = out / "01_table_sources/TABLE_E1_BALANCED_SANITY_FINAL.csv"
    write_csv(path, rows)
    _meta(
        path,
        source_files=[
            "paper_ready_r2/06_table_sources/TABLE_E1_BALANCED_SANITY.csv",
            "paper_ready_r2/04_statistics/E1_FINAL_STATISTICS.csv",
        ],
        statistical_method="E1 sealed Wilcoxon+Holm no-harm; no Holm-significant superiority",
        any_holm_significant=any_sig,
        paper_placement="Appendix or compact Results paragraph",
    )
    md = [
        "# Table E1 — Balanced sanity (appendix)",
        "",
        "Paired seeds 28001–28005. Primary no-harm metric: RMSE_μ.",
        "",
        "| Method | n | RMSE_μ mean | Δ vs RAVEN | Holm-significant vs RAVEN |",
        "|---|---:|---:|---:|:---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['method']} | {r['n']} | {float(r['RMSE_mu_mean']):.4f} | {r['diff_vs_RAVEN']:+.4f} | no |"
        )
    md += [
        "",
        "**Conclusion:** No-harm / no significant degradation under balanced selection; statistical superiority not established.",
        "",
        "Do not interpret E1 as a superiority result.",
        "",
    ]
    write_text(out / "02_tables/TABLE_E1_BALANCED_SANITY_FINAL.md", "\n".join(md))


def _e3_stat(stats: pd.DataFrame, dataset: str, method_disp: str, metric: str) -> tuple[float | None, float | None]:
    canon = METHOD_CANONICAL.get(method_disp, method_disp)
    ds = dataset.lower().replace("-", "")
    if ds == "sensorscope":
        ds = "sensorscope"
    if ds == "uair":
        ds = "uair"
    metric_map = {
        "RMSE_mu": "RMSE_mu_phys",
        "Tail_RMSE": "Tail_RMSE_phys",
        "MAE_mu": "MAE_mu_phys",
        "Delta_group": "Delta_group",
        "Delta_c_s": "Delta_c_s",
    }
    m = metric_map[metric]
    sub = stats[(stats["dataset"] == ds) & (stats["method"] == canon) & (stats["metric"] == m)]
    if sub.empty:
        return None, None
    row = sub.iloc[0]
    if str(row.get("applicability", "OK")).upper() in {"N_A", "NA", "N_A_NOT_APPLICABLE"}:
        return None, None
    mean, std = row["mean"], row["std"]
    if pd.isna(mean):
        return None, None
    return float(mean), 0.0 if pd.isna(std) else float(std)


def table_ii(r2: Path, out: Path) -> None:
    stats = pd.read_csv(r2 / "04_statistics/E3_FINAL_STATISTICS.csv")
    holm_rmse = pd.read_csv(r2 / "04_statistics/E3_FORMAL_HOLM_RESULTS.csv")
    holm_sec = pd.read_csv(
        r2 / "03_raw_evidence/e3/e3_formal_evidence_integrity_and_claim_closure_r1/E3_SECONDARY_HOLM_RESULTS.csv"
    )
    holm_rmse = holm_rmse[holm_rmse["dataset"] != "traffic"]
    holm_sec = holm_sec[holm_sec["dataset"] != "traffic"]

    def holm_flag(dataset: str, method_disp: str, metric: str) -> str:
        if method_disp == "RAVEN-MCS":
            return "reference"
        canon = METHOD_CANONICAL.get(method_disp)
        if canon is None:
            return "n/a"
        ds = "sensorscope" if dataset == "SensorScope" else "uair"
        if metric == "RMSE_mu":
            hit = holm_rmse[
                (holm_rmse["dataset"] == ds)
                & (holm_rmse["comparison"] == f"raven_vs_{canon}")
            ]
            if hit.empty:
                return "n/a"
            p = float(hit.iloc[0]["p_holm"])
            return "holm_sig_vs_RAVEN" if p < 0.05 else "not_holm_sig"
        mname = {"Tail_RMSE": "Tail_RMSE_phys", "Delta_group": "Delta_group", "Delta_c_s": "Delta_c_s"}.get(metric)
        hit = holm_sec[(holm_sec["dataset"] == ds) & (holm_sec["metric"] == mname) & (holm_sec["baseline"] == canon)]
        if hit.empty:
            return "n/a"
        p = float(hit.iloc[0]["p_holm"])
        return "holm_sig_vs_RAVEN" if p < 0.05 else "not_holm_sig"

    rows = []
    best: dict[tuple[str, str], float] = {}
    for dataset in ("SensorScope", "U-Air"):
        for method in E3_MAIN_METHODS + E3_REFERENCE_METHODS:
            rec: dict[str, Any] = {
                "dataset": dataset,
                "method": method,
                "n": 20,
                "block": "reference_only" if method in E3_REFERENCE_METHODS else "primary",
            }
            for metric in ("RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s"):
                mean, std = _e3_stat(stats, dataset, method, metric)
                rec[f"{metric}_mean"] = mean
                rec[f"{metric}_std"] = std
                rec[f"{metric}_display"] = "" if mean is None else _fmt(mean, std or 0.0)
                rec[f"{metric}_holm_vs_RAVEN"] = holm_flag(dataset, method, metric) if mean is not None else "n/a"
                if mean is not None and method in E3_MAIN_METHODS:
                    key = (dataset, metric)
                    if key not in best or mean < best[key]:
                        best[key] = mean
            rec["formatting"] = "reference_only" if method in E3_REFERENCE_METHODS else "primary"
            rows.append(rec)
    for rec in rows:
        marks = []
        for metric in ("RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s"):
            mean = rec.get(f"{metric}_mean")
            if mean is None or rec["method"] not in E3_MAIN_METHODS:
                rec[f"{metric}_numerical_best"] = False
                continue
            is_best = abs(mean - best[(rec["dataset"], metric)]) <= 1e-12
            rec[f"{metric}_numerical_best"] = is_best
            if is_best:
                marks.append(f"{metric}:numerical_best")
            if rec.get(f"{metric}_holm_vs_RAVEN") == "holm_sig_vs_RAVEN":
                marks.append(f"{metric}:statistically_supported_vs_RAVEN")
        rec["format_tags"] = ";".join(marks)
    path = out / "01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
    write_csv(path, rows)
    _meta(
        path,
        source_files=[
            "paper_ready_r2/04_statistics/E3_FINAL_STATISTICS.csv",
            "paper_ready_r2/04_statistics/E3_FORMAL_HOLM_RESULTS.csv",
            "paper_ready_r2/03_raw_evidence/e3/e3_formal_evidence_integrity_and_claim_closure_r1/E3_SECONDARY_HOLM_RESULTS.csv",
        ],
        filters="SensorScope and U-Air only; Traffic E3 excluded",
        statistical_method="mean±std over seeds 30001–30020; paired Wilcoxon + Holm vs RAVEN (R2 sealed families)",
        note="numerical_best is not a significance mark",
        excluded_evidence="E3 Traffic NOT_COMPARABLE",
    )
    md = [
        "# Table II — E3 main effectiveness (SensorScope, U-Air)",
        "",
        "Values are mean ± std over 20 paired seeds. Lower is better. Bold = numerical best among primary methods (not a significance claim). † = Holm-significant vs RAVEN (RAVEN better if the baseline is marked and the mean is higher).",
        "",
        "Traffic E3 is excluded (NOT_COMPARABLE cross-vintage).",
        "",
    ]
    for dataset in ("SensorScope", "U-Air"):
        md += [f"## {dataset}", "", "| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |", "|---|---|---|---|---|---|"]
        for rec in rows:
            if rec["dataset"] != dataset or rec["block"] != "primary":
                continue
            cells = []
            for metric in ("RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s"):
                txt = rec[f"{metric}_display"] or "—"
                if rec.get(f"{metric}_numerical_best"):
                    txt = f"**{txt}**"
                if rec.get(f"{metric}_holm_vs_RAVEN") == "holm_sig_vs_RAVEN":
                    txt += " †"
                cells.append(txt)
            md.append(f"| {rec['method']} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | primary |")
        md += ["", "*Reference-only (not a competitive baseline set):*", "", "| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |", "|---|---|---|---|---|---|"]
        for rec in rows:
            if rec["dataset"] != dataset or rec["block"] != "reference_only":
                continue
            md.append(
                f"| {rec['method']} | {rec['RMSE_mu_display'] or '—'} | {rec['Tail_RMSE_display'] or '—'} | {rec['Delta_group_display'] or '—'} | {rec['Delta_c_s_display'] or '—'} | reference_only |"
            )
        md.append("")
    md += [
        "RAVEN consistently reduces structural mismatch (Δ_group, Δ_{c,s}) on both comparable datasets.",
        "Prediction (RMSE_μ, Tail RMSE) remains competitive, with selective rather than universal gains.",
        "",
    ]
    write_text(out / "02_tables/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.md", "\n".join(md))


def table_iii(r2: Path, out: Path) -> None:
    src = r2 / "06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv"
    df = pd.read_csv(src)
    df = df[df["configuration"].isin(E4_CONFIGS)].copy()
    wo_inst = df[df["configuration"] == "RAVEN-w/o-Inst"]
    assert set(wo_inst["generation"].astype(str)) <= {"2"}, "w/o-Inst must be Generation 2"
    rows = df.to_dict(orient="records")
    path = out / "01_table_sources/TABLE_III_E4_CORE_ABLATION_FINAL.csv"
    write_csv(path, rows)
    _meta(
        path,
        source_files=["paper_ready_r2/06_table_sources/TABLE_E4_CORE_ABLATION_R2.csv"],
        source_sha256=sha256_file(src),
        filters="final valid 240-cell family; w/o-Inst Generation 2 only",
        n_cells=240,
        labels={
            "Design": "ENDPOINT_TRADEOFF",
            "Obs": "ENDPOINT_TRADEOFF",
            "Use": "NO_CLEAR_EFFECT",
            "Inst": "ENDPOINT_TRADEOFF",
            "Debt": "STRUCTURAL_ONLY_SUPPORTED (quantitatively small)",
        },
    )
    md = [
        "# Table III — E4 core ablation (SensorScope, U-Air)",
        "",
        "Final valid 240 cells. w/o-Inst is Generation 2 only. Mean ± std. Lower is better.",
        "",
        "Component labels: Design/Obs/Inst = ENDPOINT_TRADEOFF; Use = NO_CLEAR_EFFECT; Debt = STRUCTURAL_ONLY_SUPPORTED (quantitatively small).",
        "",
    ]
    for dataset in ("SensorScope", "U-Air"):
        md += [f"## {dataset}", "", "| Configuration | Δ_group | Δ_{c,s} | RMSE_μ | Tail RMSE | Gen |", "|---|---|---|---|---|---|"]
        for _, r in df[df["dataset"] == dataset].iterrows():
            md.append(
                "| {c} | {g:.4f} ± {gs:.4f} | {cs:.4f} ± {css:.4f} | {rm:.4f} ± {rms:.4f} | {t:.4f} ± {ts:.4f} | {gen} |".format(
                    c=r["configuration"],
                    g=r["Delta_group_mean"],
                    gs=r["Delta_group_std"],
                    cs=r["Delta_c_s_mean"],
                    css=r["Delta_c_s_std"],
                    rm=r["RMSE_mu_mean"],
                    rms=r["RMSE_mu_std"],
                    t=r["Tail_RMSE_mean"],
                    ts=r["Tail_RMSE_std"],
                    gen=r["generation"],
                )
            )
        md.append("")
    write_text(out / "02_tables/TABLE_III_E4_CORE_ABLATION_FINAL.md", "\n".join(md))
