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
E3_METHODS = ["FedAvg-Window", "FedAsync-Window", "TimeAlign-Agg", "Local-Hajek", "TwoStage-Hajek", "FedAU-Window", "ObsUse-Window", "RAVEN-MCS"]
E3_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "Local-Hajek", "TwoStage-Hajek", "FedAU", "ObsUse", "RAVEN-MCS"]
E2_SHORT = ["FedAvg", "FedAsync", "TimeAlign", "TwoStage-Hajek", "RAVEN-MCS"]
COMPONENTS = ["Design", "Obs", "Use", "Inst", "Debt"]
COMPONENT_LABELS = ["Design", "Observation", "Usable", "Instantaneous", "Debt"]
HATCHES = ["///", "\\\\\\", "xxx", "...", "+++", "ooo", "---"]
# Muted, print-safe palette (not neon).
COLORS = ["#6B7B8C", "#7A8B6F", "#8C7A6B", "#6F7A8B", "#8B7A8C", "#7A6F8B", "#3D5A73"]
RAVEN_COLOR = "#3D5A73"


def _ieee_rc() -> None:
    """Match IEEEtran body type: Times, 8 pt titles, 7 pt labels."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "legend.frameon": True,
        "savefig.bbox": "standard",
        "savefig.pad_inches": 0.0,
    })


def _style() -> None:
    _ieee_rc()
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
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


def _barplot(ax, data, labels, raven_last=True, headroom=0.30):
    """Bar + error bar (mean +/- std) with muted hatched fill.

    Replaces the boxplots so the figures match the ``mean +/- std`` tables
    and the reviewer's bar-chart preference. ``headroom`` keeps empty space
    above the tallest bar so the figure does not look cramped.
    """
    means = np.array([np.mean(d) for d in data])
    stds = np.array([np.std(d, ddof=1) if len(d) > 1 else 0.0 for d in data])
    x = np.arange(len(labels))
    bars = ax.bar(
        x, means, yerr=stds, capsize=2.5, tick_label=labels,
        width=0.6, edgecolor="0.15", linewidth=0.7,
        error_kw=dict(ecolor="0.25", lw=0.7, capthick=0.7),
    )
    for i, b in enumerate(bars):
        is_raven = raven_last and i == len(data) - 1
        b.set_facecolor(RAVEN_COLOR if is_raven else COLORS[i % (len(COLORS) - 1)])
        b.set_alpha(0.85)
        b.set_hatch(HATCHES[-1] if is_raven else HATCHES[i % (len(HATCHES) - 1)])
    lo = float(np.min(means - stds))
    hi = float(np.max(means + stds))
    span = hi - lo if hi > lo else max(abs(hi), 1.0)
    ax.set_ylim(lo - 0.15 * span, hi + headroom * span)
    return bars


def _panel_caption(ax, text: str) -> None:
    ax.set_xlabel(text, fontsize=9, labelpad=3)


def _value_labels(ax, xs, ys, texts, *, err=None, fs=6.5, color="#272727",
                  rotate=90, y_lock=None, lock_by_sign=False) -> None:
    """Place value labels in aligned rows.

    ``y_lock``: every label on one baseline (similar bar heights).
    ``lock_by_sign``: nonnegative labels share one top baseline; negative
    labels share one bottom baseline.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    e = np.zeros_like(ys) if err is None else np.asarray(err, dtype=float)
    span = max(float(np.nanmax(ys + e) - np.nanmin(ys - e)), 1e-6)
    pad = 0.04 * span
    y_top = float(np.nanmax(ys + e)) + pad
    y_bot = float(np.nanmin(ys - e)) - pad
    for x, y, ei, text in zip(xs, ys, e, texts):
        if y_lock is not None:
            y0, ha, va = y_lock, "left", "center"
        elif lock_by_sign:
            if y >= 0:
                y0, ha, va = y_top, "left", "center"
            else:
                y0, ha, va = y_bot, "right", "center"
        elif y >= 0:
            y0, ha, va = y + ei + pad, "left", "center"
        else:
            y0, ha, va = y - ei - pad, "right", "center"
        ax.text(
            x, y0, text, ha=ha, va=va, fontsize=fs, color=color,
            rotation=rotate, rotation_mode="anchor", zorder=4, clip_on=False,
        )


def _ylim_for_labels(ys, err=None, headroom=0.48, foot=0.12) -> tuple[float, float]:
    """Y-limits that clear error bars plus rotated value labels."""
    ys = np.asarray(ys, dtype=float)
    e = np.zeros_like(ys) if err is None else np.asarray(err, dtype=float)
    lo = float(np.min(ys - e))
    hi = float(np.max(ys + e))
    span = hi - lo if hi > lo else max(abs(hi), 1e-6)
    return lo - foot * span, hi + headroom * span


def fig1_framework() -> None:
    """Fig. 1 overview schematic.

    (a) Two-stage selection R→O→U can warp public target μ into a
    mismatched arrival mass ρ^arr.  (b) Reconstruction then calibration
    is one coupled loop, not five independent modules.  Decorative glyphs
    illustrate those relations; they are not extra scientific modules.
    """

    _ieee_rc()

    EDGE = "#4D4D4D"
    TXT = "#272727"
    MUTED = "#767676"
    BLUE = "#D7E4F0"
    BEIGE = "#EFE6DA"
    GREEN = "#E3EDE4"
    TAUPE = "#E8DDD4"
    ACCENT = "#A56B6B"
    WASH_B = "#EEF4F8"
    WASH_G = "#EEF3EE"
    RING = "#C5D0C8"

    fig, axes = plt.subplots(2, 1, figsize=(7.20, 6.70))
    fig.subplots_adjust(left=0.018, right=0.988, top=0.955, bottom=0.035, hspace=0.10)

    def frame(ax) -> None:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(True)
            s.set_color("#B0B0B0")
            s.set_linewidth(0.7)

    def panel_label(ax, letter: str, title: str) -> None:
        ax.set_xlabel(f"({letter}) {title}", fontsize=8, labelpad=2)

    def capsule(ax, xy, w, h, text, fc, fs=7.0, math=None, math_fs=8.5) -> None:
        x, y = xy
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.03,rounding_size=0.18",
            facecolor=fc, edgecolor=EDGE, linewidth=0.75, zorder=3,
        ))
        if math is None:
            ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                    color=TXT, zorder=4)
        else:
            ax.text(x, y + 0.18, text, ha="center", va="center", fontsize=fs,
                    color=TXT, zorder=4)
            ax.text(x, y - 0.26, math, ha="center", va="center", fontsize=math_fs,
                    color=TXT, zorder=4)

    def arrow(ax, p0, p1, color=EDGE, lw=0.95, rad=0.0, ms=9.0) -> None:
        ax.add_patch(FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=ms,
            color=color, lw=lw, zorder=5, shrinkA=0.2, shrinkB=0.2,
            connectionstyle=f"arc3,rad={rad}",
        ))

    def bullseye(ax, x, y, r=0.26) -> None:
        ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=EDGE,
                            lw=0.55, zorder=5))
        ax.add_patch(Circle((x, y), r * 0.64, facecolor=BLUE, edgecolor=EDGE,
                            lw=0.4, zorder=6))
        ax.add_patch(Circle((x, y), r * 0.26, facecolor=ACCENT, edgecolor="none",
                            zorder=7))

    def phone(ax, x, y, h=0.52) -> None:
        w = h * 0.52
        ax.add_patch(FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.07",
            facecolor=BEIGE, edgecolor=EDGE, linewidth=0.5, zorder=3,
        ))
        ax.add_patch(FancyBboxPatch(
            (x - w / 2 + 0.04, y - h / 2 + 0.08), w - 0.08, h - 0.18,
            boxstyle="round,pad=0.006,rounding_size=0.03",
            facecolor="white", edgecolor="#A8A8A8", linewidth=0.3, zorder=4,
        ))

    def bars(ax, x, y, heights, fc, w=0.30, gap=0.09) -> None:
        n = len(heights)
        total = n * w + (n - 1) * gap
        x0 = x - total / 2
        for i, hi in enumerate(heights):
            ax.add_patch(Rectangle(
                (x0 + i * (w + gap), y), w, hi,
                facecolor=fc, edgecolor=EDGE, linewidth=0.4, zorder=3,
            ))

    def funnel(ax, y_top, y_bot, w_top, w_bot, xc, fc, shift=0.0) -> None:
        xtl, xtr = xc - w_top / 2, xc + w_top / 2
        xbl, xbr = xc + shift - w_bot / 2, xc + shift + w_bot / 2
        ax.add_patch(Polygon(
            [(xtl, y_top), (xtr, y_top), (xbr, y_bot), (xbl, y_bot)],
            closed=True, facecolor=fc, edgecolor="none", zorder=0, alpha=0.95,
        ))

    def chain(ax, x, y) -> None:
        ax.add_patch(Circle((x - 0.12, y), 0.17, fill=False, edgecolor=EDGE,
                            lw=0.7, zorder=6))
        ax.add_patch(Circle((x + 0.12, y), 0.17, fill=False, edgecolor=EDGE,
                            lw=0.7, zorder=6))

    def feasible_set(ax, x, y, s=0.34) -> None:
        pts = np.array([
            (x, y + s), (x + 0.95 * s, y + 0.18 * s),
            (x + 0.59 * s, y - 0.81 * s), (x - 0.59 * s, y - 0.81 * s),
            (x - 0.95 * s, y + 0.18 * s),
        ])
        ax.add_patch(Polygon(pts, closed=True, facecolor="#F4F7F4",
                             edgecolor=EDGE, lw=0.6, zorder=6))

    # (a) funnel: public target is filtered by R → O → U into a mismatched arrival
    ax = axes[0]
    frame(ax)
    panel_label(ax, "a", "Selection warps the public target")

    ax.add_patch(FancyBboxPatch(
        (1.50, 7.58), 7.20, 1.56,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        facecolor=WASH_B, edgecolor="#C5D4E0", linewidth=0.55, zorder=0,
    ))
    bullseye(ax, 2.18, 8.36, r=0.28)
    bars(ax, 4.15, 7.80, (0.66, 0.66, 0.66), BLUE)
    ax.text(6.85, 8.52, "Public target", ha="center", va="center",
            fontsize=7, color=TXT, zorder=4)
    ax.text(6.85, 8.02, r"$\mu$ over $h(i)$", ha="center", va="center",
            fontsize=8.5, color=TXT, zorder=4)

    funnel(ax, 6.82, 2.18, 6.55, 3.85, 5.10, "#F3EBE0", shift=0.32)
    phone(ax, 4.40, 6.52)
    phone(ax, 5.10, 6.52)
    phone(ax, 5.80, 6.52)
    capsule(ax, (5.10, 5.82), 3.45, 0.70, r"Opportunity $R$", BEIGE)
    capsule(ax, (5.20, 4.18), 3.25, 0.70, r"Observation $O$", BEIGE)
    capsule(ax, (5.32, 2.68), 3.05, 0.70, r"Usable $U$", BEIGE)
    arrow(ax, (5.12, 5.44), (5.18, 4.56), ms=8.0)
    arrow(ax, (5.22, 3.80), (5.30, 3.06), ms=8.0)
    ax.text(8.48, 4.18, "two-stage\nselection", ha="center", va="center",
            fontsize=6.5, color=MUTED, zorder=4)

    ax.add_patch(FancyBboxPatch(
        (1.50, 0.22), 7.20, 1.82,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        facecolor="#F3EBE4", edgecolor="#D4C4B6", linewidth=0.55, zorder=0,
    ))
    bars(ax, 4.15, 0.48, (0.30, 0.58, 0.90), TAUPE)
    ax.text(6.85, 1.42, "Arrival mass", ha="center", va="center",
            fontsize=7, color=TXT, zorder=4)
    ax.text(6.85, 0.82, r"$\rho^{\mathrm{arr}}\neq\mu$", ha="center", va="center",
            fontsize=8.5, color=TXT, zorder=4)

    ax.plot([1.15, 1.15], [8.36, 1.13], color=ACCENT, lw=1.0,
            ls=(0, (2.0, 1.3)), zorder=2, solid_capstyle="butt")
    ax.plot([1.15, 1.48], [8.36, 8.36], color=ACCENT, lw=1.0, zorder=2)
    ax.plot([1.15, 1.48], [1.13, 1.13], color=ACCENT, lw=1.0, zorder=2)
    ax.add_patch(Circle((1.15, 4.75), 0.40, facecolor="white",
                        edgecolor=ACCENT, lw=0.8, zorder=6))
    ax.text(1.15, 4.75, r"$\neq$", ha="center", va="center", fontsize=9,
            color=ACCENT, zorder=7)

    # (b) orbit: reconstruction feeds a calibration loop on the feasible set
    ax = axes[1]
    frame(ax)
    panel_label(ax, "b", "One coupled reconstruction + calibration loop")

    ax.add_patch(FancyBboxPatch(
        (0.55, 7.58), 8.90, 1.52,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        facecolor=WASH_B, edgecolor="#C5D4E0", linewidth=0.55, zorder=0,
        linestyle=(0, (1.6, 1.2)),
    ))
    capsule(ax, (3.05, 8.34), 3.70, 1.00, "Design, observation\nand usable correction", BLUE, fs=6.5)
    capsule(ax, (7.20, 8.34), 3.30, 1.00, "Normalized\nreconstruction", BLUE)
    arrow(ax, (4.88, 8.34), (5.42, 8.34))

    cx, cy, rr = 5.05, 3.38, 2.38
    ax.add_patch(Circle((cx, cy), rr + 0.78, facecolor=WASH_G,
                        edgecolor="#C5D4C8", linewidth=0.55, zorder=0,
                        linestyle=(0, (1.6, 1.2))))
    ax.add_patch(Circle((cx, cy), rr, fill=False, edgecolor=RING,
                        linewidth=1.35, zorder=1))
    feasible_set(ax, cx, cy + 0.10, s=0.48)
    ax.text(cx, cy - 0.58, "feasible set", ha="center", va="center",
            fontsize=6.5, color=MUTED, zorder=6)

    nodes_b = [
        ((cx, cy + rr), 2.72, 0.95, "Instantaneous\ncalibration"),
        ((cx + rr, cy), 2.55, 0.95, "(P2) feasible\nadjustment"),
        ((cx, cy - rr), 2.28, 0.90, "Debt\nupdate"),
        ((cx - rr, cy), 2.38, 0.98, "Aggregation"),
    ]
    for (xy, w, h, text) in nodes_b:
        capsule(ax, xy, w, h, text, GREEN)
    ax.text(cx - rr, cy - 0.58, r"$\theta_{r+1}$", ha="center", va="top",
            fontsize=8.5, color=TXT, zorder=6)

    arrow(ax, (5.05, 7.58), (5.05, cy + rr + 0.50))
    chain(ax, 4.22, 6.72)
    ax.text(cx, 0.32, "not five independent modules", ha="center",
            va="center", fontsize=7, color=MUTED, style="italic", zorder=7)
    arrow(ax, (cx + 0.92, cy + rr - 0.52), (cx + rr - 0.52, cy + 0.92), rad=-0.22)
    arrow(ax, (cx + rr - 0.52, cy - 0.92), (cx + 0.92, cy - rr + 0.52), rad=-0.22)
    arrow(ax, (cx - 0.92, cy - rr + 0.52), (cx - rr + 0.52, cy - 0.92), rad=-0.22)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig1_raven_problem_framework"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig1_raven_problem_framework"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def fig2_e2() -> None:
    """Fig. 2: shared negative D_aligned across five methods.

    This is a risk-semantic test, not a ranking. All methods use the same
    muted encoding; seed-level points are drawn so the 20 paired replicates
    remain visible behind the mean ± s.d.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    _ieee_rc()

    TXT = "#272727"
    MUTED = "#767676"
    EDGE = "#4D4D4D"
    NEG = "#5B7FCA"   # D < 0 (the shared direction)
    POS = "#A56B6B"   # D ≥ 0 (the few opposite seeds)
    BAR = "#D5DCE4"
    MEAN = "#272727"

    df = pd.read_csv(SRC / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv")
    data = [df.loc[df["method"] == m, "D_aligned"].astype(float).to_numpy() for m in E2_METHODS]
    n_seed = 20
    if any(len(d) != n_seed for d in data):
        raise ValueError("Fig. 2 expects 20 paired seeds per method")

    fig, axes = plt.subplots(
        1, 2, figsize=(7.20, 3.15), gridspec_kw={"width_ratios": [1.45, 1.0]},
    )
    fig.subplots_adjust(left=0.11, right=0.985, top=0.70, bottom=0.22, wspace=0.34)
    TITLE_FS = 8

    def panel_title(ax, letter: str, title: str) -> None:
        ax.text(0.0, 1.04, letter, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        ax.text(0.08, 1.04, title, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")

    def clean(ax) -> None:
        ax.tick_params(direction="out", length=2.4, width=0.8, colors=TXT)
        ax.spines["left"].set_color(EDGE)
        ax.spines["bottom"].set_color(EDGE)

    # (a) every seed + mean ± std; color encodes sign, not method rank
    ax = axes[0]
    rng = np.random.default_rng(0)  # display jitter only; values unchanged
    ax.axhline(0.0, color=MUTED, ls=(0, (2.4, 1.6)), lw=0.7, zorder=1)
    for i, d in enumerate(data):
        xj = i + rng.uniform(-0.16, 0.16, size=len(d))
        neg_mask = d < 0
        ax.scatter(xj[neg_mask], d[neg_mask], s=11, c=NEG, edgecolors=EDGE,
                   linewidths=0.35, zorder=3, alpha=0.9)
        ax.scatter(xj[~neg_mask], d[~neg_mask], s=14, c=POS, edgecolors=EDGE,
                   linewidths=0.4, zorder=4)
        mu = float(np.mean(d))
        sd = float(np.std(d, ddof=1))
        ax.errorbar(i, mu, yerr=sd, fmt="o", color=MEAN, ecolor=MEAN,
                    ms=3.4, lw=0.85, capsize=2.2, capthick=0.8, zorder=5)
        ax.text(i, 0.040, f"{mu:.3f}", ha="center", va="bottom",
                fontsize=6.5, color=TXT, zorder=6, clip_on=False)
    ax.set_xticks(np.arange(len(E2_SHORT)))
    ax.set_xticklabels(E2_SHORT, rotation=18, ha="right", rotation_mode="anchor")
    ax.set_xlim(-0.55, len(E2_SHORT) - 0.45)
    ax.set_ylim(-0.094, 0.058)
    ax.set_ylabel(r"$D_{\mathrm{aligned}}$", fontsize=8)
    panel_title(ax, "a", r"Seed-level $D_{\mathrm{aligned}}$")
    clean(ax)

    # (b) sign count only; equal encoding so it cannot be read as a ranking
    ax = axes[1]
    neg = np.array([(d < 0).sum() for d in data], dtype=int)
    x = np.arange(len(E2_METHODS))
    ax.bar(x, neg, color=BAR, edgecolor=EDGE, linewidth=0.7, width=0.62, zorder=2)
    for i, v in enumerate(neg):
        ax.text(i, 20.2, f"{v}/20", ha="center", va="bottom",
                fontsize=7, color=TXT, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(E2_SHORT, rotation=18, ha="right", rotation_mode="anchor")
    ax.set_ylabel("Negative seeds / 20")
    ax.set_ylim(0, 23.5)
    ax.set_xlim(-0.55, len(E2_SHORT) - 0.45)
    panel_title(ax, "b", "Negative-seed count")
    clean(ax)

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=NEG,
               markeredgecolor=EDGE, markeredgewidth=0.35, markersize=5.0,
               linestyle="None", label=r"Seed, $D<0$"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=POS,
               markeredgecolor=EDGE, markeredgewidth=0.4, markersize=5.4,
               linestyle="None", label=r"Seed, $D\geq 0$"),
        Line2D([0], [0], marker="o", color=MEAN, markersize=3.6, lw=0.85,
               label=r"Mean $\pm$ std ($n=20$)"),
        Patch(facecolor=BAR, edgecolor=EDGE, linewidth=0.7,
              label="Negative-seed count"),
    ]
    fig.legend(
        handles=handles, loc="upper center", ncol=4, fontsize=7,
        frameon=True, fancybox=False, edgecolor="#B0B0B0", framealpha=1.0,
        borderpad=0.45, handlelength=1.3, columnspacing=1.25,
        bbox_to_anchor=(0.55, 0.995),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig2_e2_risk_noninterchangeability"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig2_e2_risk_noninterchangeability"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def fig3_structural() -> None:
    """Fig. 3: structural mismatch on SensorScope and U-Air.

    Mean ± std over 20 paired seeds. Panel titles use the same 8 pt bold
    Times as the panel letters. A shared legend identifies methods.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    _ieee_rc()

    TXT = "#272727"
    EDGE = "#4D4D4D"
    TITLE_FS = 8
    FACE = [
        "#9AA7B5", "#8A9B86", "#B09A86", "#8A96A8",
        "#9B8A9B", "#7A7390", "#6F8496", "#3D5A73",
    ]
    HATCH_I = ["///", "\\\\\\", "xxx", "...", "+++", "ooo", "---", ""]

    df = pd.read_csv(SRC / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    specs = [
        (0, 0, "SensorScope", "Delta_group", "a", r"SensorScope, $\Delta_{\mathrm{group}}$"),
        (0, 1, "SensorScope", "Delta_c_s", "b", r"SensorScope, $\Delta_{c\text{-}s}$"),
        (1, 0, "U-Air", "Delta_group", "c", r"U-Air, $\Delta_{\mathrm{group}}$"),
        (1, 1, "U-Air", "Delta_c_s", "d", r"U-Air, $\Delta_{c\text{-}s}$"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.20, 5.40))
    fig.subplots_adjust(left=0.10, right=0.985, top=0.80, bottom=0.16,
                        hspace=0.42, wspace=0.30)

    def clean(ax) -> None:
        ax.tick_params(direction="out", length=2.4, width=0.8, colors=TXT)
        ax.spines["left"].set_color(EDGE)
        ax.spines["bottom"].set_color(EDGE)

    for r, c, ds, col, letter, title in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).to_numpy() for m in E3_METHODS]
        if any(len(d) != 20 for d in data):
            raise ValueError(f"Fig. 3 expects 20 seeds: {ds} {col}")
        means = np.array([float(np.mean(d)) for d in data])
        stds = np.array([float(np.std(d, ddof=1)) for d in data])
        x = np.arange(len(E3_SHORT))
        bars = ax.bar(
            x, means, yerr=stds, capsize=2.2, width=0.68,
            edgecolor=EDGE, linewidth=0.65,
            error_kw=dict(ecolor=EDGE, lw=0.7, capthick=0.7),
            zorder=2,
        )
        for i, b in enumerate(bars):
            b.set_facecolor(FACE[i])
            b.set_hatch(HATCH_I[i])
            b.set_alpha(0.92)
        y_lock = float(np.max(means + stds))
        span = max(y_lock - float(np.min(means - stds)), 1e-6)
        _value_labels(
            ax, x, means, [f"{v:.3f}" for v in means],
            err=stds, fs=6.0, color=TXT, rotate=90,
            y_lock=y_lock + 0.06 * span,
        )
        ax.set_ylim(*_ylim_for_labels(means, stds, headroom=0.55, foot=0.12))
        ax.set_xticks(x)
        ax.set_xticklabels(E3_SHORT, rotation=28, ha="right",
                           rotation_mode="anchor")
        ylab = r"$\Delta_{\mathrm{group}}$" if col == "Delta_group" else r"$\Delta_{c\text{-}s}$"
        ax.set_ylabel(ylab, fontsize=8)
        ax.text(0.0, 1.04, letter, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        ax.text(0.08, 1.04, title, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        clean(ax)

    method_patches = [
        Patch(facecolor=FACE[i], edgecolor=EDGE, linewidth=0.65,
              hatch=HATCH_I[i], label=E3_SHORT[i])
        for i in range(len(E3_SHORT))
    ]
    stat_handle = Line2D([0], [0], color=EDGE, lw=0.85,
                         marker="o", markersize=3.2,
                         label=r"Mean $\pm$ std ($n=20$)")
    fig.legend(
        handles=method_patches + [stat_handle],
        loc="upper center", ncol=5, fontsize=8,
        frameon=True, fancybox=False, edgecolor="#B0B0B0", framealpha=1.0,
        borderpad=0.45, handlelength=1.35, columnspacing=1.15,
        bbox_to_anchor=(0.54, 0.995),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig3_e3_structural_mismatch"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig3_e3_structural_mismatch"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def fig4_prediction() -> None:
    """Fig. 4: deployment-target prediction risk on SensorScope and U-Air.

    Mean ± std over 20 paired seeds. Panel titles use the same 8 pt bold
    Times as the panel letters. A shared legend identifies methods.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    _ieee_rc()

    TXT = "#272727"
    EDGE = "#4D4D4D"
    TITLE_FS = 8
    FACE = [
        "#9AA7B5", "#8A9B86", "#B09A86", "#8A96A8",
        "#9B8A9B", "#7A7390", "#6F8496", "#3D5A73",
    ]
    HATCH_I = ["///", "\\\\\\", "xxx", "...", "+++", "ooo", "---", ""]

    df = pd.read_csv(SRC / "FIG_E3_E3_PREDICTION_RISK.csv")
    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
    specs = [
        (0, 0, "SensorScope", "RMSE_mu", "a", r"SensorScope, $\mathrm{RMSE}_{\mu}$"),
        (0, 1, "SensorScope", "Tail_RMSE", "b", "SensorScope, Tail RMSE"),
        (1, 0, "U-Air", "RMSE_mu", "c", r"U-Air, $\mathrm{RMSE}_{\mu}$"),
        (1, 1, "U-Air", "Tail_RMSE", "d", "U-Air, Tail RMSE"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.20, 5.40))
    fig.subplots_adjust(left=0.10, right=0.985, top=0.80, bottom=0.16,
                        hspace=0.42, wspace=0.30)

    def clean(ax) -> None:
        ax.tick_params(direction="out", length=2.4, width=0.8, colors=TXT)
        ax.spines["left"].set_color(EDGE)
        ax.spines["bottom"].set_color(EDGE)

    for r, c, ds, col, letter, title in specs:
        ax = axes[r, c]
        sub = df[df["dataset"] == ds]
        data = [sub.loc[sub["method"] == m, col].astype(float).to_numpy() for m in E3_METHODS]
        if any(len(d) != 20 for d in data):
            raise ValueError(f"Fig. 4 expects 20 seeds: {ds} {col}")
        means = np.array([float(np.mean(d)) for d in data])
        stds = np.array([float(np.std(d, ddof=1)) for d in data])
        x = np.arange(len(E3_SHORT))
        bars = ax.bar(
            x, means, yerr=stds, capsize=2.2, width=0.68,
            edgecolor=EDGE, linewidth=0.65,
            error_kw=dict(ecolor=EDGE, lw=0.7, capthick=0.7),
            zorder=2,
        )
        for i, b in enumerate(bars):
            b.set_facecolor(FACE[i])
            b.set_hatch(HATCH_I[i])
            b.set_alpha(0.92)
        y_lock = float(np.max(means + stds))
        span = max(y_lock - float(np.min(means - stds)), 1e-6)
        _value_labels(
            ax, x, means, [f"{v:.3f}" for v in means],
            err=stds, fs=6.0, color=TXT, rotate=90,
            y_lock=y_lock + 0.06 * span,
        )
        ax.set_ylim(*_ylim_for_labels(means, stds, headroom=0.55, foot=0.12))
        ax.set_xticks(x)
        ax.set_xticklabels(E3_SHORT, rotation=28, ha="right",
                           rotation_mode="anchor")
        ylab = r"$\mathrm{RMSE}_{\mu}$" if col == "RMSE_mu" else "Tail RMSE"
        ax.set_ylabel(ylab, fontsize=8)
        ax.text(0.0, 1.04, letter, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        ax.text(0.08, 1.04, title, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        clean(ax)

    method_patches = [
        Patch(facecolor=FACE[i], edgecolor=EDGE, linewidth=0.65,
              hatch=HATCH_I[i], label=E3_SHORT[i])
        for i in range(len(E3_SHORT))
    ]
    stat_handle = Line2D([0], [0], color=EDGE, lw=0.85,
                         marker="o", markersize=3.2,
                         label=r"Mean $\pm$ std ($n=20$)")
    fig.legend(
        handles=method_patches + [stat_handle],
        loc="upper center", ncol=5, fontsize=8,
        frameon=True, fancybox=False, edgecolor="#B0B0B0", framealpha=1.0,
        borderpad=0.45, handlelength=1.35, columnspacing=1.15,
        bbox_to_anchor=(0.54, 0.995),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig4_e3_prediction_risk"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig4_e3_prediction_risk"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def fig5_ablation() -> None:
    """Fig. 5: one-factor component removal vs full RAVEN.

    Positive relative change means removal worsens the metric. Panel titles
    use the same 8 pt bold sans-serif as the panel letters. A shared legend
    identifies metrics. U-Air Obs–Debt is shown at full scale in Fig. 6.
    """
    from matplotlib.patches import Patch

    _ieee_rc()

    TXT = "#272727"
    EDGE = "#4D4D4D"
    MUTED = "#767676"
    TITLE_FS = 8
    FACE_M = {
        "Delta_group": "#8A9B86",
        "Delta_c_s": "#B09A86",
        "RMSE_mu": "#8A96A8",
        "Tail_RMSE": "#3D5A73",
    }
    HATCH_M = {
        "Delta_group": "///",
        "Delta_c_s": "xxx",
        "RMSE_mu": "...",
        "Tail_RMSE": "---",
    }
    LAB_M = {
        "Delta_group": r"$\Delta_{\mathrm{group}}$",
        "Delta_c_s": r"$\Delta_{c\text{-}s}$",
        "RMSE_mu": r"$\mathrm{RMSE}_{\mu}$",
        "Tail_RMSE": "Tail RMSE",
    }

    df = pd.read_csv(SRC / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    expected = 2 * len(COMPONENTS) * 4
    if len(df) < expected:
        raise ValueError(f"Fig. 5 expected at least {expected} rows, got {len(df)}")
    x = np.arange(len(COMPONENTS))
    w = 0.36
    specs = [
        (0, 0, "SensorScope", ["Delta_group", "Delta_c_s"], "a", "SensorScope, structural mismatch"),
        (0, 1, "SensorScope", ["RMSE_mu", "Tail_RMSE"], "b", "SensorScope, prediction risk"),
        (1, 0, "U-Air", ["Delta_group", "Delta_c_s"], "c", "U-Air, structural mismatch"),
        (1, 1, "U-Air", ["RMSE_mu", "Tail_RMSE"], "d", "U-Air, prediction risk"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.20, 5.35))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.80, bottom=0.16,
                        hspace=0.48, wspace=0.28)

    def clean(ax, boxed=False) -> None:
        ax.tick_params(direction="out", length=2.4, width=0.8, colors=TXT)
        ax.spines["left"].set_color(EDGE)
        ax.spines["bottom"].set_color(EDGE)
        if boxed:
            ax.spines["right"].set_visible(True)
            ax.spines["top"].set_visible(True)
            ax.spines["right"].set_color(EDGE)
            ax.spines["top"].set_color(EDGE)

    def vals_sig(ds, metric):
        vals, sigs = [], []
        for comp in COMPONENTS:
            hit = df[(df["dataset"] == ds) & (df["component"] == comp) & (df["metric"] == metric)]
            if len(hit) != 1:
                raise ValueError(f"Fig. 5 missing unique row: {ds} {comp} {metric}")
            vals.append(float(hit.iloc[0]["relative_change_percent"]))
            sigs.append(bool(hit.iloc[0]["holm_significant"]))
        return vals, sigs

    def fmt_delta(v: float) -> str:
        return f"{v:+.2f}" if abs(v) >= 0.05 else f"{v:+.3f}"

    def draw_bars(ax, metrics, series, xvals, width, annotate, fs):
        artists = []
        for j, metric in enumerate(metrics):
            vals, sigs = series[j]
            bars = ax.bar(
                xvals + (j - 0.5) * width, vals, width=width,
                color=FACE_M[metric], edgecolor=EDGE, linewidth=0.65,
                hatch=HATCH_M[metric], zorder=2,
            )
            artists.append((bars, vals, sigs))
        ax.axhline(0.0, color=MUTED, ls=(0, (2.4, 1.6)), lw=0.7, zorder=1)
        if annotate:
            all_xs, all_ys, all_texts = [], [], []
            for bars, vals, sigs in artists:
                all_xs.extend(b.get_x() + b.get_width() / 2.0 for b in bars)
                all_ys.extend(vals)
                all_texts.extend(
                    fmt_delta(v) + ("*" if sig else "") for v, sig in zip(vals, sigs)
                )
            _value_labels(
                ax, all_xs, all_ys, all_texts, fs=fs, color=TXT, rotate=90,
                lock_by_sign=True,
            )
        return artists

    for r, c, ds, metrics, letter, title in specs:
        ax = axes[r, c]
        series = [vals_sig(ds, metric) for metric in metrics]
        draw_bars(ax, metrics, series, x, w, annotate=(ds != "U-Air"), fs=6.0)
        if ds == "U-Air":
            # Design dominates U-Air; Obs–Debt values are labeled in Fig. 6.
            d_xs, d_ys, d_texts = [], [], []
            for j, (vals, sigs) in enumerate(series):
                d_xs.append(x[0] + (j - 0.5) * w)
                d_ys.append(vals[0])
                d_texts.append(fmt_delta(vals[0]) + ("*" if sigs[0] else ""))
            _value_labels(
                ax, d_xs, d_ys, d_texts, fs=6.0, color=TXT, rotate=90,
                lock_by_sign=True,
            )
        flat = np.array([v for vals, _ in series for v in vals], dtype=float)
        ax.set_ylim(*_ylim_for_labels(flat, headroom=0.42, foot=0.42))
        ax.set_xticks(x)
        ax.set_xticklabels(COMPONENT_LABELS, rotation=18, ha="right",
                           rotation_mode="anchor")
        ax.set_ylabel("Relative change (%)", fontsize=8)
        ax.text(0.0, 1.04, letter, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        ax.text(0.08, 1.04, title, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        clean(ax)

    metric_order = ["Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"]
    handles = [
        Patch(facecolor=FACE_M[m], edgecolor=EDGE, linewidth=0.65,
              hatch=HATCH_M[m], label=LAB_M[m])
        for m in metric_order
    ]
    star_handle = Patch(facecolor="none", edgecolor="none",
                        label=r"* Holm-adjusted $p<0.05$")
    fig.legend(
        handles=handles + [star_handle],
        loc="upper center", ncol=5, fontsize=8,
        frameon=True, fancybox=False, edgecolor="#B0B0B0", framealpha=1.0,
        borderpad=0.45, handlelength=1.35, columnspacing=1.15,
        bbox_to_anchor=(0.54, 0.995),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig5_e4_component_ablation"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig5_e4_component_ablation"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def fig6_uair_excl_design() -> None:
    """Fig. 6: U-Air ablation zoom excluding Design.

    Same CSV and relative-change definition as Fig. 5. Design is omitted
    only because it dominates the U-Air axis and is already shown in Fig. 5.
    """
    from matplotlib.patches import Patch

    _ieee_rc()

    TXT = "#272727"
    EDGE = "#4D4D4D"
    MUTED = "#767676"
    TITLE_FS = 8
    FACE_M = {
        "Delta_group": "#8A9B86",
        "Delta_c_s": "#B09A86",
        "RMSE_mu": "#8A96A8",
        "Tail_RMSE": "#3D5A73",
    }
    HATCH_M = {
        "Delta_group": "///",
        "Delta_c_s": "xxx",
        "RMSE_mu": "...",
        "Tail_RMSE": "---",
    }
    LAB_M = {
        "Delta_group": r"$\Delta_{\mathrm{group}}$",
        "Delta_c_s": r"$\Delta_{c\text{-}s}$",
        "RMSE_mu": r"$\mathrm{RMSE}_{\mu}$",
        "Tail_RMSE": "Tail RMSE",
    }
    ZOOM = ["Obs", "Use", "Inst", "Debt"]

    df = pd.read_csv(SRC / "FIG_E4_E4_COMPONENT_ABLATION.csv")
    x = np.arange(len(ZOOM))
    w = 0.30
    specs = [
        (0, ["Delta_group", "Delta_c_s"], "a", "Structural mismatch, excluding Design"),
        (1, ["RMSE_mu", "Tail_RMSE"], "b", "Prediction risk, excluding Design"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(7.20, 3.20))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.68, bottom=0.20, wspace=0.32)

    def clean(ax) -> None:
        ax.tick_params(direction="out", length=2.4, width=0.8, colors=TXT)
        ax.spines["left"].set_color(EDGE)
        ax.spines["bottom"].set_color(EDGE)

    def vals_sig(metric):
        vals, sigs = [], []
        for comp in ZOOM:
            hit = df[(df["dataset"] == "U-Air") & (df["component"] == comp) & (df["metric"] == metric)]
            if len(hit) != 1:
                raise ValueError(f"Fig. 6 missing unique row: U-Air {comp} {metric}")
            vals.append(float(hit.iloc[0]["relative_change_percent"]))
            sigs.append(bool(hit.iloc[0]["holm_significant"]))
        return vals, sigs

    def fmt_delta(v: float) -> str:
        return f"{v:+.2f}" if abs(v) >= 0.05 else f"{v:+.3f}"

    for c, metrics, letter, title in specs:
        ax = axes[c]
        series = [vals_sig(metric) for metric in metrics]
        for j, metric in enumerate(metrics):
            vals, _sigs = series[j]
            ax.bar(
                x + (j - 0.5) * w, vals, width=w,
                color=FACE_M[metric], edgecolor=EDGE, linewidth=0.65,
                hatch=HATCH_M[metric], zorder=2,
            )
        ax.axhline(0.0, color=MUTED, ls=(0, (2.4, 1.6)), lw=0.7, zorder=1)
        all_xs, all_ys, all_texts = [], [], []
        for j, (vals, sigs) in enumerate(series):
            all_xs.extend(x + (j - 0.5) * w)
            all_ys.extend(vals)
            all_texts.extend(
                fmt_delta(v) + ("*" if sig else "") for v, sig in zip(vals, sigs)
            )
        _value_labels(
            ax, all_xs, all_ys, all_texts, fs=6.5, color=TXT, rotate=90,
            lock_by_sign=True,
        )
        flat = np.array([v for vals, _ in series for v in vals], dtype=float)
        ax.set_ylim(*_ylim_for_labels(flat, headroom=0.48, foot=0.48))
        ax.set_xticks(x)
        ax.set_xticklabels(COMPONENT_LABELS[1:], rotation=12, ha="right",
                           rotation_mode="anchor")
        ax.set_ylabel("Relative change (%)", fontsize=8)
        ax.text(0.0, 1.05, letter, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        ax.text(0.08, 1.05, title, transform=ax.transAxes, fontsize=TITLE_FS,
                fontweight="bold", color=TXT, ha="left", va="bottom")
        clean(ax)

    metric_order = ["Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"]
    handles = [
        Patch(facecolor=FACE_M[m], edgecolor=EDGE, linewidth=0.65,
              hatch=HATCH_M[m], label=LAB_M[m])
        for m in metric_order
    ]
    star_handle = Patch(facecolor="none", edgecolor="none",
                        label=r"* Holm-adjusted $p<0.05$")
    fig.legend(
        handles=handles + [star_handle],
        loc="upper center", ncol=5, fontsize=8,
        frameon=True, fancybox=False, edgecolor="#B0B0B0", framealpha=1.0,
        borderpad=0.45, handlelength=1.35, columnspacing=1.15,
        bbox_to_anchor=(0.54, 0.995),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig6_e4_uair_excl_design"
    fig.savefig(f"{stem}.svg", bbox_inches=None)
    fig.savefig(f"{stem}.pdf", bbox_inches=None)
    fig.savefig(f"{stem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{stem}.png", dpi=600, bbox_inches=None)
    nature_out = Path(__file__).resolve().parent / "figures_nature"
    nature_out.mkdir(parents=True, exist_ok=True)
    nstem = nature_out / "fig6_e4_uair_excl_design"
    fig.savefig(f"{nstem}.svg", bbox_inches=None)
    fig.savefig(f"{nstem}.pdf", bbox_inches=None)
    fig.savefig(f"{nstem}.tiff", dpi=600, bbox_inches=None)
    fig.savefig(f"{nstem}.png", dpi=600, bbox_inches=None)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig1_framework()
    fig2_e2()
    fig3_structural()
    fig4_prediction()
    fig5_ablation()
    fig6_uair_excl_design()
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
