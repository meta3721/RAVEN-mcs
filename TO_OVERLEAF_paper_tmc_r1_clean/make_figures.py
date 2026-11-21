"""IEEE TMC figures for paper_tmc_r1 from frozen specification-seal CSVs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOCAL = Path(__file__).resolve().parent / "figure_data"
SEAL = ROOT / "RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1"
SEAL_SRC = SEAL / "05_PROVENANCE" / "FINAL_FIGURE_SOURCES"
SRC = LOCAL if (LOCAL / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv").exists() else SEAL_SRC
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
            # Match the IEEEtran body font (Times) and math (Computer Modern).
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
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
        s.set_color("#595959")
        s.set_linewidth(1.2)
    ax.tick_params(direction="in", length=2.5, width=0.8)
    ax.grid(False)


def _frame_only(ax) -> None:
    """Show a clean border without ticks (used by the schematic Fig. 1)."""
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color("#595959")
        s.set_linewidth(1.2)


def _barplot(ax, data, labels, raven_last=True, headroom=0.30, compact=False):
    """Bar + error bar (mean +/- std) with muted hatched fill.

    Replaces the boxplots so the figures match the ``mean +/- std`` tables
    and the reviewer's bar-chart preference. ``headroom`` keeps empty space
    above the tallest bar so the figure does not look cramped.
    ``compact`` is for one-column multi-panel layouts.
    """
    means = np.array([np.mean(d) for d in data])
    stds = np.array([np.std(d, ddof=1) if len(d) > 1 else 0.0 for d in data])
    x = np.arange(len(labels))
    cap = 1.5 if compact else 2.5
    bars = ax.bar(
        x, means, yerr=stds, capsize=cap,
        width=0.64 if compact else 0.6, edgecolor="0.15",
        linewidth=0.6 if compact else 0.7,
        error_kw=dict(ecolor="0.25", lw=0.6, capthick=0.6),
    )
    for i, b in enumerate(bars):
        is_raven = raven_last and i == len(data) - 1
        b.set_facecolor(RAVEN_COLOR if is_raven else COLORS[i % (len(COLORS) - 1)])
        b.set_alpha(0.85)
        b.set_hatch(HATCHES[-1] if is_raven else HATCHES[i % (len(HATCHES) - 1)])
    lo = float(np.min(means - stds))
    hi = float(np.max(means + stds))
    span = hi - lo if hi > lo else max(abs(hi), 1.0)
    ax.set_ylim(lo - 0.12 * span, hi + headroom * span)
    ax.set_xticks(x)
    ax.set_xticklabels(
        labels,
        rotation=42 if compact else 16,
        ha="right",
        fontsize=5.6 if compact else 7.5,
    )
    if compact:
        ax.tick_params(axis="y", labelsize=6.0)
    return bars


def _panel_caption(ax, text: str, compact: bool = False) -> None:
    """Draw panel text separately, preserving the real horizontal-axis label."""
    ax.text(0.5, -0.30 if compact else -0.25, text, transform=ax.transAxes,
            ha="center", va="top", fontsize=7.5 if compact else 9, clip_on=False)


def fig1_framework(output_dir=None, poppler=None):
    """Render Fig. 1 only from its editable vector reconstruction.

    Other figure functions and frozen result inputs are intentionally untouched.
    Use fig1_framework_vector.py directly in a reportlab-only environment.
    """
    import importlib.util
    source = Path(__file__).with_name("fig1_framework_vector.py")
    spec = importlib.util.spec_from_file_location("raven_fig1_vector", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_fig1(OUT if output_dir is None else output_dir, poppler)


def _revised_data_figure(name):
    """Dispatch one deterministic data figure; no other figure is executed."""
    import importlib.util
    source = Path(__file__).with_name("data_figures_revision.py")
    spec = importlib.util.spec_from_file_location("raven_data_figure_revision", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    module.style()
    return module.FUNCTIONS[name]()


def fig2_e2() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig2_e2")


def fig3_structural() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig3_structural")


def fig4_prediction() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig4_prediction")


def fig5_ablation() -> None:
    df = pd.read_csv(SRC / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.45))
    metric_groups = [
        (0, "SensorScope", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"],
         r"(a) SensorScope, structural"),
        (1, "SensorScope", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"],
         r"(b) SensorScope, prediction"),
        (2, "U-Air", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"],
         r"(c) U-Air, structural"),
        (3, "U-Air", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"],
         r"(d) U-Air, prediction"),
    ]
    x = np.arange(len(COMPONENTS))
    w = 0.36

    def _vals_sig(ds, metric):
        vals, sigs = [], []
        for comp in COMPONENTS:
            hit = df[(df["dataset"] == ds) & (df["component"] == comp) & (df["metric"] == metric)]
            if len(hit):
                vals.append(float(hit.iloc[0]["relative_change_percent"]))
                sigs.append(bool(hit.iloc[0]["holm_significant"]))
            else:
                vals.append(0.0)
                sigs.append(False)
        return vals, sigs

    def _draw_bars(ax, series, xvals=None, width=w, annotate=True, fs=5.5):
        xs = x if xvals is None else xvals
        artists = []
        for j, (vals, lab, sigs) in enumerate(series):
            bars = ax.bar(xs + (j - 0.5) * width, vals, width=width, label=lab,
                          color=COLORS[j + 1], edgecolor="0.15", linewidth=0.6)
            for b in bars:
                b.set_hatch(HATCHES[j])
            artists.append((bars, vals, sigs))
        ax.axhline(0.0, color="0.25", lw=0.8)
        if annotate:
            flat = [v for vals, _, _ in series for v in vals]
            span = max(max(flat) - min(flat), 1e-3)
            for bars, vals, sigs in artists:
                for b, v, sig in zip(bars, vals, sigs):
                    if abs(v) < 0.002 and not sig:
                        continue
                    off = 0.055 * span
                    label = f"{v:+.2f}" + ("*" if sig else "")
                    ax.text(b.get_x() + b.get_width() / 2.0, v + (off if v >= 0 else -off),
                            label, ha="center", va="bottom" if v >= 0 else "top",
                            fontsize=fs, color="0.15",
                            bbox=dict(boxstyle="square,pad=0.10", fc="white", ec="none", alpha=0.85))
        return artists

    for c, ds, metrics, labs, cap in metric_groups:
        ax = axes.flat[c]
        series = []
        for metric, lab in zip(metrics, labs):
            v, s = _vals_sig(ds, metric)
            series.append((v, lab, s))
        _draw_bars(ax, series, annotate=(ds != "U-Air"), fs=5.0)
        if ds == "U-Air":
            for j, (vals, lab, sigs) in enumerate(series):
                label = f"{vals[0]:+.2f}" + ("*" if sigs[0] else "")
                ax.text(x[0] + (j - 0.5) * w, vals[0] + (0.28 if vals[0] >= 0 else -0.28),
                        label, ha="center", va="bottom" if vals[0] >= 0 else "top",
                        fontsize=5.0, color="0.15",
                        bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none", alpha=0.85))
        flat = [v for vals, _, _ in series for v in vals]
        ymin, ymax = min(flat), max(flat)
        pad = max(0.18 * (ymax - ymin + 1e-6), 0.08 * max(abs(ymin), abs(ymax), 0.02))
        ax.set_ylim(ymin - pad, ymax + 1.55 * pad)
        ax.set_xticks(x)
        ax.set_xticklabels(COMPONENTS, fontsize=6.0)
        ax.set_ylabel("rel. change (%)", fontsize=7)
        ax.tick_params(axis="y", labelsize=6.0)
        _box(ax)
        loc = "upper right" if ds == "U-Air" else "best"
        leg = ax.legend(frameon=True, fancybox=False, edgecolor="0.3", loc=loc,
                        borderpad=0.2, handlelength=1.2, fontsize=5.0)
        leg.get_frame().set_linewidth(0.6)
        _panel_caption(ax, cap, compact=True)
    fig.tight_layout(h_pad=0.4, w_pad=0.3)
    fig.savefig(OUT / "fig5_e4_component_ablation.pdf")
    fig.savefig(OUT / "fig5_e4_component_ablation.png")
    plt.close(fig)


def fig6_uair_excl_design() -> None:
    """U-Air E4 ablation excluding the Design layer (1x2 magnified view).

    Reproduces the user-made fig6_e4_uair_excl_design with the panel titles
    moved from the top of each panel to directly below the image (xlabel),
    matching the panel-caption convention of figs 2-5.
    """
    df = pd.read_csv(SRC / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    df = df[df["dataset"] == "U-Air"]
    comps = ["Obs", "Use", "Inst", "Debt"]
    xlabs = ["Obs", "Use", "Inst", "Debt"]
    x = np.arange(len(comps))
    w = 0.36
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.25))

    def _series(metric):
        vals, sigs = [], []
        for comp in comps:
            hit = df[(df["component"] == comp) & (df["metric"] == metric)]
            vals.append(float(hit.iloc[0]["relative_change_percent"]))
            sigs.append(bool(hit.iloc[0]["holm_significant"]))
        return vals, sigs

    def _draw(ax, metrics, labels, ylim, yticks):
        for j, (metric, lab) in enumerate(zip(metrics, labels)):
            vals, sigs = _series(metric)
            bars = ax.bar(x + (j - 0.5) * w, vals, width=w, label=lab,
                          color=COLORS[j + 1], edgecolor="0.15", linewidth=0.6)
            for b in bars:
                b.set_hatch(HATCHES[j])
            for b, v, sig in zip(bars, vals, sigs):
                off = 0.012 * (ylim[1] - ylim[0])
                txt = (f"{v:+.2f}" if abs(v) >= 0.05 else f"{v:+.3f}") + ("*" if sig else "")
                ax.text(b.get_x() + b.get_width() / 2.0, v + (off if v >= 0 else -off),
                        txt, ha="center", va="bottom" if v >= 0 else "top",
                        fontsize=5.0, color="0.15",
                        bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none", alpha=0.85))
        ax.axhline(0.0, color="0.25", lw=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(xlabs, fontsize=6)
        ax.set_ylabel("rel. change (%)", fontsize=7)
        ax.tick_params(axis="y", labelsize=6)
        ax.set_ylim(*ylim)
        ax.set_yticks(yticks)
        _box(ax)
        leg = ax.legend(frameon=True, fancybox=False, edgecolor="0.3",
                        fontsize=5.0, handlelength=1.1, loc="best", borderpad=0.2)
        leg.get_frame().set_linewidth(0.5)

    _draw(axes[0], ["Delta_group", "Delta_c_s"],
          [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"],
          (-0.25, 0.25), [-0.2, -0.1, 0.0, 0.1, 0.2])
    _panel_caption(axes[0], r"(a) Structural, excl.\ Design", compact=True)

    _draw(axes[1], ["RMSE_mu", "Tail_RMSE"],
          [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"],
          (-0.06, 0.24), [-0.05, 0.00, 0.05, 0.10, 0.15, 0.20])
    _panel_caption(axes[1], r"(b) Prediction, excl.\ Design", compact=True)
    fig.tight_layout(w_pad=0.4)
    fig.savefig(OUT / "fig6_e4_uair_excl_design.pdf")
    fig.savefig(OUT / "fig6_e4_uair_excl_design.png")
    plt.close(fig)


def fig_w1_design_gate() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig_w1_design_gate")


def fig_g3_tdrive() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig_g3_tdrive")


def fig_certificate() -> None:
    """Redraw this figure only from its original CSV rows."""
    _revised_data_figure("fig_certificate")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig1_framework()
    fig2_e2()
    fig3_structural()
    fig4_prediction()
    fig5_ablation()
    fig6_uair_excl_design()
    fig_w1_design_gate()
    fig_g3_tdrive()
    fig_certificate()
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
