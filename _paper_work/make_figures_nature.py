"""Nature-figure restyle of RAVEN-MCS Fig 1-5.

Backend: Python/matplotlib (exclusive). Data comes unchanged from the frozen
figure_data CSVs. Scientific content, numbers, and claims are preserved; only
the publication style is restyled to the nature-figure standard:
  - sans-serif (Arial), editable SVG text, no top/right spines
  - one unified baseline family + one RAVEN hero accent across panels
  - mean +/- std error bars, 20 paired seeds
  - Fig 5 keeps the CSV's Holm significance asterisks and the U-Air inset
Output: SVG (primary) + PDF + PNG under figures_nature/.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "figure_data"
OUT = ROOT / "figures_nature"

E2_METHODS = ["FedAvg-Window", "FedAsync-Window", "TimeAlign-Agg", "TwoStage-Hajek", "RAVEN-MCS"]
E3_METHODS = ["FedAvg-Window", "FedAsync-Window", "TimeAlign-Agg", "Local-Hajek", "TwoStage-Hajek", "RAVEN-MCS"]
E2_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "2S-Hajek", "RAVEN"]
E3_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "Loc-Hajek", "2S-Hajek", "RAVEN"]
COMPONENTS = ["Design", "Obs", "Use", "Inst", "Debt"]

# Unified palette: neutral baseline family + one hero accent for RAVEN.
RAVEN = "#0F4D92"
BASELINE_GRAYS = ["#C9C9C9", "#ADADAD", "#8F8F8F", "#6E6E6E", "#4E4E4E"]
METHOD_COLORS = {
    "FedAvg-Window": "#CFCFCF",
    "FedAsync-Window": "#B4B4B4",
    "TimeAlign-Agg": "#969696",
    "Local-Hajek": "#D6D6D6",
    "TwoStage-Hajek": "#5A5A5A",
    "RAVEN-MCS": RAVEN,
}
METRIC_COLORS = ["#0F4D92", "#C08A3E"]  # metric series 1 / 2 (blue + amber)

EDGE = "#444444"
FS = 8


def _style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": FS,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "legend.frameon": False,
        "axes.titlesize": FS,
        "axes.labelsize": FS,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


def _save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=600)
    plt.close(fig)


def _panel_label(ax, label: str) -> None:
    ax.text(-0.08, 1.04, label, transform=ax.transAxes, fontsize=FS + 1,
            fontweight="bold", va="bottom", ha="left")


def _mean_std(vals: np.ndarray):
    vals = np.asarray(vals, dtype=float)
    m = float(np.mean(vals))
    s = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
    return m, s


def _barplot(ax, data, labels, raven_last=True, headroom=0.28):
    means = [np.mean(d) for d in data]
    stds = [np.std(d, ddof=1) if len(d) > 1 else 0.0 for d in data]
    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=stds, capsize=2.5, width=0.62,
                  edgecolor="black", linewidth=0.6,
                  error_kw=dict(ecolor="0.35", lw=0.7, capthick=0.7))
    for i, b in enumerate(bars):
        is_raven = raven_last and i == len(data) - 1
        b.set_facecolor(RAVEN if is_raven else BASELINE_GRAYS[i % len(BASELINE_GRAYS)])
        b.set_alpha(0.95)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    lo = float(np.min(np.asarray(means) - np.asarray(stds)))
    hi = float(np.max(np.asarray(means) + np.asarray(stds)))
    span = hi - lo if hi > lo else max(abs(hi), 1.0)
    ax.set_ylim(lo - 0.18 * span, hi + headroom * span)
    return bars


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(EDGE)
    ax.spines["bottom"].set_color(EDGE)


def fig1_framework() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7.16, 5.4))
    TXT = "#222222"
    BLUE = "#D9E2EC"
    BEIGE = "#EEE6DC"
    GREEN = "#E8EEE6"
    TAUPE = "#E4DCD3"
    NAVY = RAVEN

    def node(ax, xy, w, h, text, fc, fs=7.5):
        x, y = xy
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.06,rounding_size=0.12",
                                    facecolor=fc, edgecolor="#595959", linewidth=1.0, zorder=2))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=TXT, zorder=3)

    def arrow(ax, p0, p1, color="#595959", lw=1.1, ls="-"):
        ax.annotate("", xy=p1, xytext=p0,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, linestyle=ls))

    def target(ax, x, y, r=0.6):
        ax.add_patch(Circle((x, y), r, facecolor=BLUE, edgecolor="#595959", linewidth=1.0, zorder=3))
        ax.add_patch(Circle((x, y), r * 0.6, facecolor="white", edgecolor="#595959", linewidth=0.6, zorder=4))
        ax.add_patch(Circle((x, y), r * 0.24, facecolor=NAVY, edgecolor="none", zorder=5))

    def phone(ax, x, y, w=0.72, h=1.3):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.03,rounding_size=0.18",
                                    facecolor=BEIGE, edgecolor="#595959", linewidth=0.9, zorder=3))
        ax.add_patch(FancyBboxPatch((x - w / 2 + 0.09, y - h / 2 + 0.15), w - 0.18, h - 0.40,
                                    boxstyle="round,pad=0.01,rounding_size=0.08",
                                    facecolor="white", edgecolor="#888", linewidth=0.4, zorder=4))
        ax.add_patch(Circle((x, y - h / 2 + 0.08), 0.04, facecolor="#888", edgecolor="none", zorder=5))

    # ---- (a) problem -------------------------------------------------
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#595959"); s.set_linewidth(1.0)
    target(ax, 2.0, 8.6)
    ax.text(2.0, 7.7, "deployment target", ha="center", va="top", fontsize=7, color="#666")
    node(ax, (4.4, 8.6), 3.1, 1.1, "public target\n$\\mu$ over $h(i)$", BLUE, fs=7.5)
    for (px, py) in [(1.5, 7.0), (1.1, 5.7), (1.5, 4.4)]:
        phone(ax, px, py)
    ax.text(1.4, 3.15, "mobile\nparticipants", ha="center", va="top", fontsize=7, color="#666")
    gy = 5.7
    for (gx, lab) in [(3.3, "Opportunity\n$R$"), (5.05, "Observation\n$O$"), (6.8, "Usable\n$U$")]:
        node(ax, (gx, gy), 1.4, 1.1, lab, BEIGE, fs=7)
    # cloud
    cx, cy = 8.75, gy
    ax.add_patch(FancyBboxPatch((cx - 1.1, cy - 1.0), 2.2, 1.45,
                                boxstyle="round,pad=0.03,rounding_size=0.22",
                                facecolor=TAUPE, edgecolor="#595959", linewidth=1.0, zorder=2))
    for (px, py, pr) in [(cx - 0.5, cy + 0.18, 0.55), (cx, cy + 0.3, 0.62), (cx + 0.5, cy + 0.18, 0.55)]:
        ax.add_patch(Circle((px, py), pr, facecolor=TAUPE, edgecolor="none", zorder=2))
    ax.text(cx, cy + 0.15, "server", ha="center", va="center", fontsize=7.5, color=TXT, zorder=6)
    ax.text(cx, cy - 0.42, "arrival\n$\\rho^{\\mathrm{arr}}$", ha="center", va="center", fontsize=7.5, color=TXT, zorder=6)
    arrow(ax, (1.85, 5.7), (2.55, 5.7))
    arrow(ax, (4.05, 5.7), (4.3, 5.7))
    arrow(ax, (5.8, 5.7), (6.05, 5.7))
    arrow(ax, (7.55, 5.7), (7.62, 5.7))
    ax.text(4.18, 6.5, "stage 1", ha="center", va="bottom", fontsize=7, color="#666", style="italic")
    ax.text(5.92, 6.5, "stage 2", ha="center", va="bottom", fontsize=7, color="#666", style="italic")
    for gx in (3.3, 5.05, 6.8):
        ax.plot([gx, gx], [5.15, 4.45], color="#999", lw=0.8, ls="--", zorder=3)
        ax.text(gx, 4.33, "$\\times$", ha="center", va="top", fontsize=7.5, color="#8A4B4B", zorder=4)
    arrow(ax, (4.4, 8.05), (7.9, 6.85), color="#888", lw=0.9, ls="--")
    ax.text(6.3, 7.75, "wanted: $\\mu$", ha="center", va="center", fontsize=7, color="#666", style="italic")
    node(ax, (5.0, 2.4), 6.4, 0.95, "structural mismatch:  $\\rho^{\\mathrm{arr}}\\neq\\mu$", TAUPE, fs=8)
    ax.set_xlabel("(a) Two-stage selection vs. deployment target", fontsize=7.5)

    # ---- (b) architecture -------------------------------------------
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(1, 11.4)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color("#595959"); s.set_linewidth(1.0)
    node(ax, (3.8, 8.9), 4.6, 1.2, "Design / Obs / Use\ncorrection", BLUE)
    node(ax, (3.8, 7.05), 4.6, 1.2, "Normalized reconstruction", BLUE)
    node(ax, (3.8, 4.85), 2.5, 1.4, "Inst.\ncalibration", GREEN)
    node(ax, (7.4, 4.85), 2.5, 1.4, "(P2) feasible\nadjustment", GREEN)
    node(ax, (7.4, 2.6), 2.5, 1.4, "Debt\nupdate", GREEN)
    node(ax, (3.8, 2.6), 2.5, 1.4, "Aggregation\n$\\theta_{r+1}$", NAVY)
    arrow(ax, (3.8, 7.7), (3.8, 8.25))
    arrow(ax, (3.8, 5.6), (3.8, 6.4))
    arrow(ax, (6.15, 4.85), (5.05, 4.85))
    arrow(ax, (7.4, 3.35), (7.4, 4.1))
    arrow(ax, (5.05, 2.6), (6.15, 2.6))
    ax.text(5.0, 10.6, "Coupled reconstruction + calibration", ha="center", fontsize=9.5, color=TXT)
    ax.text(5.0, 10.0, "not five independent modules", ha="center", fontsize=8, color=TXT)
    ax.set_xlabel("(b) RAVEN-MCS as one coordinated architecture", fontsize=7.5)

    fig.tight_layout(h_pad=0.7)
    _save(fig, "fig1_raven_problem_framework")


def fig2_e2() -> None:
    df = pd.read_csv(DATA / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.4),
                             gridspec_kw={"width_ratios": [1.35, 1.0]})
    ax = axes[0]
    data = [df.loc[df["method"] == m, "D_aligned"].astype(float).to_numpy() for m in E2_METHODS]
    _barplot(ax, data, E2_SHORT)
    ax.axhline(0.0, color="0.4", ls="--", lw=0.8)
    ax.set_ylabel(r"$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$", fontsize=7.5)
    _clean(ax)
    _panel_label(ax, "a")
    ax.set_xlabel("Seed-level $D_{\\mathrm{aligned}}$ (20 paired seeds)", fontsize=7.5)

    ax = axes[1]
    neg = [(df.loc[df["method"] == m, "D_aligned"].astype(float) < 0).sum() for m in E2_METHODS]
    x = np.arange(len(E2_METHODS))
    bars = ax.bar(x, neg, width=0.66, edgecolor="black", linewidth=0.6,
                  color=[RAVEN if m == "RAVEN-MCS" else BASELINE_GRAYS[i] for i, m in enumerate(E2_METHODS)])
    ax.set_xticks(x)
    ax.set_xticklabels(E2_SHORT, rotation=18, ha="right")
    ax.set_ylabel("Negative seeds / 20", fontsize=7)
    ax.set_ylim(0, 22)
    ax.axhline(10, color="0.7", ls=":", lw=0.6)
    _clean(ax)
    _panel_label(ax, "b")
    ax.set_xlabel("Direction count (not a ranking)", fontsize=7)
    fig.tight_layout(w_pad=0.8)
    _save(fig, "fig2_e2_risk_noninterchangeability")


def fig3_structural() -> None:
    df = pd.read_csv(DATA / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.5))
    specs = [
        (0, 0, "SensorScope", "Delta_group", r"$\Delta_{\mathrm{group}}$"),
        (0, 1, "SensorScope", "Delta_c_s", r"$\Delta_{c,s}$"),
        (1, 0, "U-Air", "Delta_group", r"$\Delta_{\mathrm{group}}$"),
        (1, 1, "U-Air", "Delta_c_s", r"$\Delta_{c,s}$"),
    ]
    for (r, c, ds, col, ylab) in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
        _barplot(ax, data, E3_SHORT)
        ax.set_ylabel(ylab, fontsize=7.5)
        ax.tick_params(axis="x", rotation=20)
        _clean(ax)
        _panel_label(ax, "abcd"[r * 2 + c])
        ax.set_xlabel(f"{ds}", fontsize=7)
    fig.tight_layout(h_pad=1.0, w_pad=0.7)
    _save(fig, "fig3_e3_structural_mismatch")


def fig4_prediction() -> None:
    df = pd.read_csv(DATA / "FIG_E3_E3_PREDICTION_RISK.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.5))
    specs = [
        (0, 0, "SensorScope", "RMSE_mu", r"$\mathrm{RMSE}_{\mu}$"),
        (0, 1, "SensorScope", "Tail_RMSE", "Tail RMSE"),
        (1, 0, "U-Air", "RMSE_mu", r"$\mathrm{RMSE}_{\mu}$"),
        (1, 1, "U-Air", "Tail_RMSE", "Tail RMSE"),
    ]
    for (r, c, ds, col, ylab) in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
        _barplot(ax, data, E3_SHORT)
        ax.set_ylabel(ylab, fontsize=7.5)
        ax.tick_params(axis="x", rotation=20)
        _clean(ax)
        _panel_label(ax, "abcd"[r * 2 + c])
        ax.set_xlabel(f"{ds}", fontsize=7)
    fig.tight_layout(h_pad=1.0, w_pad=0.7)
    _save(fig, "fig4_e3_prediction_risk")


def fig5_ablation() -> None:
    df = pd.read_csv(DATA / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.6))
    groups = [
        (0, 0, "SensorScope", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"]),
        (0, 1, "SensorScope", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"]),
        (1, 0, "U-Air", ["Delta_group", "Delta_c_s"], [r"$\Delta_{\mathrm{group}}$", r"$\Delta_{c,s}$"]),
        (1, 1, "U-Air", ["RMSE_mu", "Tail_RMSE"], [r"$\mathrm{RMSE}_{\mu}$", "Tail RMSE"]),
    ]
    x = np.arange(len(COMPONENTS))
    w = 0.36

    def vals_sig(ds, metric):
        vals, sigs = [], []
        for comp in COMPONENTS:
            hit = df[(df["dataset"] == ds) & (df["component"] == comp) & (df["metric"] == metric)]
            if len(hit):
                vals.append(float(hit.iloc[0]["relative_change_percent"]))
                sigs.append(bool(hit.iloc[0]["holm_significant"]))
            else:
                vals.append(0.0); sigs.append(False)
        return vals, sigs

    def draw(ax, series, xvals=None, width=w, annotate=True, fs=5.5):
        xs = x if xvals is None else xvals
        artists = []
        for j, (vals, lab, sigs) in enumerate(series):
            bars = ax.bar(xs + (j - 0.5) * width, vals, width=width, label=lab,
                          color=METRIC_COLORS[j], edgecolor="black", linewidth=0.5)
            artists.append((bars, vals, sigs))
        ax.axhline(0.0, color="0.3", lw=0.7)
        if annotate:
            flat = [val for vals, _, _ in series for val in vals]
            span = max(max(flat) - min(flat), 1e-3)
            for bars, vals, sigs in artists:
                for b, v, sig in zip(bars, vals, sigs):
                    if abs(v) < 0.05 and not sig:
                        continue
                    off = 0.055 * span
                    ax.text(b.get_x() + b.get_width() / 2, v + (off if v >= 0 else -off),
                            f"{v:+.2f}" + ("*" if sig else ""), ha="center",
                            va="bottom" if v >= 0 else "top", fontsize=fs, color="0.15")
        return artists

    for (r, c, ds, metrics, labs) in groups:
        ax = axes[r, c]
        series = []
        for metric, lab in zip(metrics, labs):
            v, s = vals_sig(ds, metric)
            series.append((v, lab, s))
        draw(ax, series, annotate=(ds != "U-Air"))
        if ds == "U-Air":
            for j, (vals, lab, sigs) in enumerate(series):
                ax.text(x[0] + (j - 0.5) * w, vals[0] + (0.28 if vals[0] >= 0 else -0.28),
                        f"{vals[0]:+.2f}" + ("*" if sigs[0] else ""), ha="center",
                        va="bottom" if vals[0] >= 0 else "top", fontsize=5.5, color="0.15")
            ins = ax.inset_axes([0.40, 0.10, 0.57, 0.40])
            ins.set_facecolor("white")
            zoom = [(vals[1:], lab, sigs[1:]) for vals, lab, sigs in series]
            zx = np.arange(len(COMPONENTS) - 1)
            draw(ins, zoom, xvals=zx, width=0.34, annotate=True, fs=5)
            ins.set_xticks(zx)
            ins.set_xticklabels(COMPONENTS[1:], fontsize=6)
            ins.set_title("excl. Design", fontsize=6, pad=1, color="0.3")
            for s in ("top", "right"):
                ins.spines[s].set_visible(False)
            ins.tick_params(labelsize=6)
        flat = [v for vals, _, _ in series for v in vals]
        ymin, ymax = min(flat), max(flat)
        pad = max(0.18 * (ymax - ymin + 1e-6), 0.08 * max(abs(ymin), abs(ymax), 0.02))
        ax.set_ylim(ymin - pad, ymax + 1.55 * pad)
        ax.set_xticks(x)
        ax.set_xticklabels(COMPONENTS)
        ax.set_ylabel("rel. change (%)", fontsize=7)
        _clean(ax)
        _panel_label(ax, "abcd"[r * 2 + c])
        if ds == "U-Air":
            ax.legend(loc="upper right", fontsize=7.5, frameon=False, handlelength=1.2)
        else:
            ax.legend(loc="best", fontsize=7.5, frameon=False, handlelength=1.2)
    fig.tight_layout(h_pad=1.0, w_pad=0.6)
    _save(fig, "fig5_e4_component_ablation")


def main() -> None:
    _style()
    fig1_framework()
    fig2_e2()
    fig3_structural()
    fig4_prediction()
    fig5_ablation()
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
