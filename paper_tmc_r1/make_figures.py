"""IEEE TMC figures for paper_tmc_r1 from frozen specification-seal CSVs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1"
SRC = SEAL / "05_PROVENANCE" / "FINAL_FIGURE_SOURCES"
OUT = Path(__file__).resolve().parent / "figures"

E2_METHODS = ["FedAvg-Window", "FedAsync-Window", "TimeAlign-Agg", "TwoStage-Hajek", "RAVEN-MCS"]
E3_METHODS = ["FedAvg-Window", "FedAsync-Window", "TimeAlign-Agg", "Local-Hajek", "TwoStage-Hajek", "RAVEN-MCS"]
E3_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "Loc-Hajek", "2S-Hajek", "RAVEN"]
E2_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "2S-Hajek", "RAVEN"]
COMPONENTS = ["Design", "Obs", "Use", "Inst", "Debt"]
HATCHES = ["///", "\\\\\\", "xxx", "...", "+++", "ooo"]
# Muted, print-safe palette (not neon).
COLORS = ["#6B7B8C", "#7A8B6F", "#8C7A6B", "#6F7A8B", "#8B7A8C", "#3D5A73"]
RAVEN_COLOR = "#3D5A73"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 8,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
        }
    )


def _box(ax) -> None:
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color("0.25")
        s.set_linewidth(0.8)
    ax.tick_params(direction="in", length=2.5, width=0.6)
    ax.grid(False)


def _boxplot(ax, data, labels, raven_last=True):
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        showfliers=False,
        patch_artist=True,
        widths=0.62,
        medianprops={"color": "0.1", "linewidth": 1.1},
        whiskerprops={"color": "0.2", "linewidth": 0.7},
        capprops={"color": "0.2", "linewidth": 0.7},
        boxprops={"linewidth": 0.7, "edgecolor": "0.15"},
    )
    for i, box in enumerate(bp["boxes"]):
        is_raven = raven_last and i == len(data) - 1
        box.set_facecolor(RAVEN_COLOR if is_raven else COLORS[i % (len(COLORS) - 1)])
        box.set_alpha(0.85)
        box.set_hatch(HATCHES[-1] if is_raven else HATCHES[i % (len(HATCHES) - 1)])
        box.set_edgecolor("0.15")
    return bp


def _panel_caption(ax, text: str) -> None:
    ax.set_xlabel(text, fontsize=8, labelpad=3)


def fig1_framework() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.75))
    # (a) problem
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("")

    def node(ax, xy, w, h, text, fc="#E8EDF1"):
        x, y = xy
        p = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=fc, edgecolor="0.2", linewidth=0.9)
        ax.add_patch(p)
        ax.text(x, y, text, ha="center", va="center", fontsize=7, color="0.1")

    node(ax, (2.0, 7.6), 3.2, 1.5, "Public target\n$\\mu$ over $h(i)$", "#D9E2EC")
    node(ax, (1.5, 4.4), 2.4, 1.25, "Opportunity $R$", "#EEE6DC")
    node(ax, (4.2, 4.4), 2.4, 1.25, "Observation $O$", "#EEE6DC")
    node(ax, (7.0, 4.4), 2.6, 1.25, "Usable $U$", "#EEE6DC")
    node(ax, (7.6, 1.6), 3.4, 1.4, "Arrival mass\n$\\rho^{\\mathrm{arr}}\\neq\\mu$", "#E4DCD3")
    for a, b in [((2.7, 4.4), (3.0, 4.4)), ((5.4, 4.4), (5.7, 4.4))]:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(7.6, 2.35), xytext=(7.0, 3.75),
                arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(6.0, 1.6), xytext=(2.0, 6.8),
                arrowprops=dict(arrowstyle="-|>", color="#3D5A73", lw=1.0, ls="--"))
    ax.text(3.4, 6.15, "mismatch", fontsize=7, color="#3D5A73", style="italic")
    _panel_caption(ax, r"(a) Two-stage selection vs.\ deployment target")

    # (b) architecture: coupled pipeline, not five innovations
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    node(ax, (5.0, 8.35), 4.6, 1.35, "Design / Obs / Use layer correction", "#D9E2EC")
    node(ax, (5.0, 6.35), 4.2, 1.35, "Normalized reconstruction", "#D9E2EC")
    node(ax, (1.7, 3.85), 2.7, 1.45, "Inst.\ncalibration", "#E8EEE6")
    node(ax, (5.0, 3.85), 2.7, 1.45, "(P2) feasible\nadjustment", "#E8EEE6")
    node(ax, (8.3, 3.85), 2.7, 1.45, "Debt\nupdate", "#E8EEE6")
    node(ax, (8.3, 1.45), 2.7, 1.35, "Aggregation\n$\\theta_{r+1}$", "#E8EEE6")
    ax.annotate("", xy=(5.0, 7.10), xytext=(5.0, 7.65), arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(2.6, 4.60), xytext=(3.6, 5.65), arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(3.65, 3.85), xytext=(3.05, 3.85), arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(6.95, 3.85), xytext=(6.35, 3.85), arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.annotate("", xy=(8.3, 2.2), xytext=(8.3, 3.1), arrowprops=dict(arrowstyle="-|>", color="0.25", lw=0.9))
    ax.text(5.0, 9.55, "Coupled reconstruction + calibration", ha="center", fontsize=7.5, color="0.2")
    ax.text(5.0, 9.05, "not five independent modules", ha="center", fontsize=6.5, color="0.35")
    _panel_caption(ax, r"(b) RAVEN-MCS as one coordinated architecture")

    fig.tight_layout(w_pad=0.6, h_pad=0.2)
    fig.savefig(OUT / "fig1_raven_problem_framework.pdf")
    fig.savefig(OUT / "fig1_raven_problem_framework.png")
    plt.close(fig)


def fig2_e2() -> None:
    df = pd.read_csv(SRC / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.45), gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    data = [df.loc[df["method"] == m, "D_aligned"].astype(float).to_numpy() for m in E2_METHODS]
    _boxplot(ax, data, E2_SHORT)
    ax.axhline(0.0, color="0.35", ls="--", lw=0.8)
    ax.set_ylabel(r"$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$")
    _box(ax)
    _panel_caption(ax, r"(a) Seed-level $D_{\mathrm{aligned}}$ (20 paired seeds)")

    ax = axes[1]
    neg = [(df.loc[df["method"] == m, "D_aligned"].astype(float) < 0).sum() for m in E2_METHODS]
    x = np.arange(len(E2_METHODS))
    bars = ax.bar(x, neg, color=[RAVEN_COLOR if m == "RAVEN-MCS" else COLORS[i] for i, m in enumerate(E2_METHODS)],
                  edgecolor="0.15", linewidth=0.7, width=0.7)
    for i, b in enumerate(bars):
        b.set_hatch(HATCHES[-1] if E2_METHODS[i] == "RAVEN-MCS" else HATCHES[i])
    ax.set_xticks(x)
    ax.set_xticklabels(E2_SHORT, rotation=18, ha="right")
    ax.set_ylabel("Negative seeds / 20")
    ax.set_ylim(0, 22)
    ax.axhline(10, color="0.7", ls=":", lw=0.6)
    _box(ax)
    _panel_caption(ax, r"(b) Direction count (not a ranking)")
    fig.tight_layout(w_pad=0.7)
    fig.savefig(OUT / "fig2_e2_risk_noninterchangeability.pdf")
    fig.savefig(OUT / "fig2_e2_risk_noninterchangeability.png")
    plt.close(fig)


def fig3_structural() -> None:
    df = pd.read_csv(SRC / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.55))
    specs = [
        (0, 0, "SensorScope", "Delta_group", r"(a) SensorScope, $\Delta_{\mathrm{group}}$"),
        (0, 1, "SensorScope", "Delta_c_s", r"(b) SensorScope, $\Delta_{c,s}$"),
        (1, 0, "U-Air", "Delta_group", r"(c) U-Air, $\Delta_{\mathrm{group}}$"),
        (1, 1, "U-Air", "Delta_c_s", r"(d) U-Air, $\Delta_{c,s}$"),
    ]
    for r, c, ds, col, cap in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
        _boxplot(ax, data, E3_SHORT)
        ax.set_ylabel(r"lower is better")
        ax.tick_params(axis="x", rotation=22)
        _box(ax)
        _panel_caption(ax, cap)
    fig.tight_layout(h_pad=1.1, w_pad=0.6)
    fig.savefig(OUT / "fig3_e3_structural_mismatch.pdf")
    fig.savefig(OUT / "fig3_e3_structural_mismatch.png")
    plt.close(fig)


def fig4_prediction() -> None:
    df = pd.read_csv(SRC / "FIG_E3_E3_PREDICTION_RISK.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.55))
    specs = [
        (0, 0, "SensorScope", "RMSE_mu", r"(a) SensorScope, $\mathrm{RMSE}_{\mu}$"),
        (0, 1, "SensorScope", "Tail_RMSE", r"(b) SensorScope, Tail RMSE"),
        (1, 0, "U-Air", "RMSE_mu", r"(c) U-Air, $\mathrm{RMSE}_{\mu}$"),
        (1, 1, "U-Air", "Tail_RMSE", r"(d) U-Air, Tail RMSE"),
    ]
    for r, c, ds, col, cap in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
        _boxplot(ax, data, E3_SHORT)
        ax.set_ylabel("lower is better")
        ax.tick_params(axis="x", rotation=22)
        _box(ax)
        _panel_caption(ax, cap)
    fig.tight_layout(h_pad=1.1, w_pad=0.6)
    fig.savefig(OUT / "fig4_e3_prediction_risk.pdf")
    fig.savefig(OUT / "fig4_e3_prediction_risk.png")
    plt.close(fig)


def fig5_ablation() -> None:
    df = pd.read_csv(SRC / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.35))
    metric_groups = [
        (0, 0, "SensorScope", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"],
         r"(a) SensorScope, structural"),
        (0, 1, "SensorScope", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"],
         r"(b) SensorScope, prediction"),
        (1, 0, "U-Air", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"],
         r"(c) U-Air, structural"),
        (1, 1, "U-Air", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"],
         r"(d) U-Air, prediction"),
    ]
    x = np.arange(len(COMPONENTS))
    w = 0.36
    for r, c, ds, metrics, labs, cap in metric_groups:
        ax = axes[r, c]
        for j, (metric, lab) in enumerate(zip(metrics, labs)):
            vals = []
            for comp in COMPONENTS:
                hit = df[(df["dataset"] == ds) & (df["component"] == comp) & (df["metric"] == metric)]
                vals.append(float(hit.iloc[0]["relative_change_percent"]) if len(hit) else 0.0)
            bars = ax.bar(x + (j - 0.5) * w, vals, width=w, label=lab, color=COLORS[j + 1],
                          edgecolor="0.15", linewidth=0.6)
            for b in bars:
                b.set_hatch(HATCHES[j])
        ax.axhline(0.0, color="0.25", lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(COMPONENTS)
        ax.set_ylabel("rel. change (%)")
        _box(ax)
        leg = ax.legend(frameon=True, fancybox=False, edgecolor="0.3", loc="best", borderpad=0.25, handlelength=1.4)
        leg.get_frame().set_linewidth(0.6)
        _panel_caption(ax, cap)
    fig.tight_layout(h_pad=1.05, w_pad=0.55)
    fig.savefig(OUT / "fig5_e4_component_ablation.pdf")
    fig.savefig(OUT / "fig5_e4_component_ablation.png")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig1_framework()
    fig2_e2()
    fig3_structural()
    fig4_prediction()
    fig5_ablation()
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
