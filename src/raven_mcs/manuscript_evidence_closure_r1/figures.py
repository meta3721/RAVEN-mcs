"""Publication figures from final R2 CSVs. Grayscale-readable, no significance stars."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json
from raven_mcs.manuscript_evidence_closure_r1.constants import (
    E2_FIG_METHODS,
    E3_FIG_METHODS,
    E4_COMPONENTS,
    METHOD_DISPLAY,
)


def _meta(path: Path, **kwargs: Any) -> None:
    write_json(Path(str(path) + ".meta.json"), {"csv_sha256": sha256_file(path) if path.is_file() else "", **kwargs})


def _boxplot(ax, data, labels, **kwargs):
    try:
        return ax.boxplot(data, tick_labels=labels, **kwargs)
    except TypeError:
        return ax.boxplot(data, labels=labels, **kwargs)


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.grid": False,
        }
    )


def fig1(r2: Path, out: Path) -> Path:
    src = r2 / "07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv"
    df = pd.read_csv(src)
    df = df[df["method"].isin(E2_FIG_METHODS)].copy()
    dest = out / "03_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.csv"
    write_csv(dest, df.to_dict(orient="records"))
    _meta(
        dest,
        source_files=["paper_ready_r2/07_figure_sources/FIG1_E2_RISK_NONINTERCHANGEABILITY.csv"],
        original_evidence="paper_ready_r2/01_core_data/e2/E2_D_ALIGNED_PER_SEED.csv",
        filters="complete_aligned; five formal E2 methods",
        visual_message="D_aligned has a stable nonzero (negative) direction; not a RAVEN-superiority figure",
        lower_is_not_better_note="D_aligned = Delta RMSE_mu - Delta RMSE_rho (aligned vs balanced). A stable negative sign supports risk non-interchangeability, not method ranking.",
        claim_ceiling="C1/C2 only",
    )
    _style()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    data = [df.loc[df["method"] == m, "D_aligned"].astype(float).to_numpy() for m in E2_FIG_METHODS]
    bp = _boxplot(ax, data, E2_FIG_METHODS, showfliers=True, patch_artist=True, widths=0.55)
    for i, box in enumerate(bp["boxes"]):
        gray = 0.85 - 0.12 * (i % 3)
        box.set_facecolor(str(gray))
        box.set_edgecolor("black")
    for med in bp["medians"]:
        med.set_color("black")
        med.set_linewidth(1.4)
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_ylabel(r"$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_\mu-\Delta\mathrm{RMSE}_\rho$")
    ax.set_title("E2 Traffic (complete-aligned): risk non-interchangeability")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    pdf = out / "04_figures/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.pdf"
    png = out / "04_figures/FIG1_E2_RISK_NONINTERCHANGEABILITY_FINAL.png"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    return dest


def fig2(r2: Path, out: Path) -> Path:
    src = r2 / "01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv"
    df = pd.read_csv(src)
    df = df[df["dataset"].isin(["SensorScope", "U-Air"])].copy()
    df = df[df["method"].isin(E3_FIG_METHODS)].copy()
    df = df[df["Delta_group"].notna() & df["Delta_c_s"].notna()].copy()
    dest = out / "03_figure_sources/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.csv"
    write_csv(dest, df.to_dict(orient="records"))
    _meta(
        dest,
        source_files=["paper_ready_r2/01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv"],
        filters="SensorScope/U-Air; five main baselines + RAVEN; drop missing structural fields",
        excluded_evidence="E3 Traffic; Central reference rows",
        claim_ceiling="C3 structural alignment; not universal RMSE",
        lower_is_better=True,
    )
    _style()
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.6), sharex=False)
    metrics = [("Delta_group", r"$\Delta_{\mathrm{group}}$"), ("Delta_c_s", r"$\Delta_{c,s}$")]
    datasets = ["SensorScope", "U-Air"]
    for i, ds in enumerate(datasets):
        for j, (col, ylab) in enumerate(metrics):
            ax = axes[i, j]
            sub = df[df["dataset"] == ds]
            data = [sub.loc[sub["method"] == m, col].astype(float).to_numpy() for m in E3_FIG_METHODS]
            bp = _boxplot(ax, data, E3_FIG_METHODS, showfliers=False, patch_artist=True, widths=0.6)
            for k, box in enumerate(bp["boxes"]):
                gray = 0.9 if E3_FIG_METHODS[k] != "RAVEN-MCS" else 0.45
                box.set_facecolor(str(gray))
                box.set_edgecolor("black")
            for med in bp["medians"]:
                med.set_color("black")
            ax.set_title(f"{ds}")
            ax.set_ylabel(ylab + " (lower better)")
            ax.tick_params(axis="x", rotation=28, labelsize=7)
    fig.suptitle("E3 structural target mismatch (paired seeds 30001–30020)")
    fig.tight_layout()
    pdf = out / "04_figures/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.pdf"
    png = out / "04_figures/FIG2_E3_STRUCTURAL_MISMATCH_FINAL.png"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    return dest


def fig3(r2: Path, out: Path) -> Path:
    src = r2 / "04_statistics/E4_FINAL_STATISTICS_R2.csv"
    df = pd.read_csv(src)
    dest = out / "03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv"
    keep = [
        "dataset",
        "component",
        "metric",
        "relative_change_percent",
        "paired_mean_difference",
        "Holm_p",
        "holm_significant",
        "direction",
        "final_component_label",
        "qualitative_magnitude",
        "evidence_generation",
    ]
    write_csv(dest, df[keep].to_dict(orient="records"))
    _meta(
        dest,
        source_files=["paper_ready_r2/04_statistics/E4_FINAL_STATISTICS_R2.csv"],
        formula="100*(Metric_w/oX - Metric_RAVEN)/Metric_RAVEN",
        positive="removing the component worsens a lower-is-better metric",
        negative="removing the component improves the metric",
        claim_ceiling="C5–C8 mechanism/trade-off; not universal component necessity",
        wo_inst_generation="2",
    )
    _style()
    metrics = ["Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"]
    metric_lab = {
        "Delta_group": r"$\Delta_{\mathrm{group}}$",
        "Delta_c_s": r"$\Delta_{c,s}$",
        "RMSE_mu": r"RMSE$_\mu$",
        "Tail_RMSE": "Tail RMSE",
    }
    fig, axes = plt.subplots(2, 4, figsize=(9.2, 5.2), sharey=False)
    x = np.arange(len(E4_COMPONENTS))
    for i, ds in enumerate(["SensorScope", "U-Air"]):
        for j, metric in enumerate(metrics):
            ax = axes[i, j]
            vals = []
            for comp in E4_COMPONENTS:
                hit = df[(df["dataset"] == ds) & (df["component"] == comp) & (df["metric"] == metric)]
                if hit.empty:
                    raise ValueError(f"missing E4 relative_change for {ds}/{comp}/{metric}")
                vals.append(float(hit.iloc[0]["relative_change_percent"]))
            colors = ["0.35" if v >= 0 else "0.75" for v in vals]
            ax.bar(x, vals, color=colors, edgecolor="black", linewidth=0.6)
            ax.axhline(0.0, color="black", linewidth=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(E4_COMPONENTS, rotation=45, ha="right", fontsize=7)
            if i == 0:
                ax.set_title(metric_lab[metric])
            if j == 0:
                ax.set_ylabel(f"{ds}\nrel. change (%)")
    fig.suptitle("E4: relative change when a component is removed (positive = worsens)")
    fig.tight_layout()
    pdf = out / "04_figures/FIG3_E4_COMPONENT_REMOVAL_FINAL.pdf"
    png = out / "04_figures/FIG3_E4_COMPONENT_REMOVAL_FINAL.png"
    pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf)
    fig.savefig(png)
    plt.close(fig)
    return dest
