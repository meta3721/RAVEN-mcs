"""Redesigned Fig. 1 for the RAVEN-MCS paper (IEEE TMC).

Same meaning as the original, more creative layout:

  (a) The problem.  The public deployment target mu is passed through the
      two-stage, non-random selection layers (Opportunity R -> Observation O ->
      Usable U) and reshaped into an arrival law rho_arr.  The bottom panel
      draws the two laws side by side so the structural mismatch (rho_arr != mu)
      is visible rather than merely asserted.

  (b) The architecture.  RAVEN-MCS is drawn as one closed loop, not a linear
      stack: reconstruction (Design/Obs/Use correction -> Normalized
      reconstruction) feeds calibration (Inst. calibration -> (P2) feasible
      adjustment -> Debt update), which closes through Aggregation theta_{r+1}
      and feeds the next round.  This foregrounds the paper's claim that the
      system is a single coordinated architecture, not five independent modules.

No data is read: this is a schematic figure only, so no CSV is touched.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"

# Print-safe, muted palette (kept consistent with the rest of the paper).
EDGE = "#595959"   # uniform dark-gray border
TXT = "#333333"    # uniform dark-gray text
GRAY = "#7A7A7A"
BLUE = "#D9E2EC"   # target / reconstruction
BEIGE = "#EEE6DC"  # selection layers
GREEN = "#E8EEE6"  # calibration
TAUPE = "#E4DCD3"  # arrival
NAVY = "#3D5A73"   # RAVEN accent
MU_FILL = "#3D5A73"
RHO_FILL = "#8C6B4F"
MISMATCH = "#8A4B4B"

FS = 8.5


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "mathtext.fontset": "cm",
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
        }
    )


def _frame_only(ax) -> None:
    """Clean border, no ticks (schematic panels)."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(EDGE)
        s.set_linewidth(1.2)


def _node(ax, xy, w, h, text, fc, fs=FS, lw=1.2) -> None:
    x, y = xy
    p = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.06,rounding_size=0.12",
        facecolor=fc,
        edgecolor=EDGE,
        linewidth=lw,
        zorder=2,
    )
    ax.add_patch(p)
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=TXT, zorder=3)


def _arrow(ax, p0, p1, color=EDGE, lw=1.2, ls="-", rad=0.0, style="-|>") -> None:
    a = FancyArrowPatch(
        p0,
        p1,
        arrowstyle=style,
        mutation_scale=12,
        color=color,
        lw=lw,
        linestyle=ls,
        zorder=4,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(a)


def _mass_curve(ax, cx, cy, amp=0.95, width=0.5, skew=0.0, fill=NAVY, label=None):
    """Schematic, unlabeled probability-mass glyph (no data implied)."""
    x = np.linspace(cx - 1.5, cx + 1.5, 300)
    y = amp * np.exp(-0.5 * ((x - cx) / width) ** 2)
    if skew:
        y = y * (1.0 + skew * np.tanh((x - cx) / width))
        y = y / y.max() * amp
    top = cy + y * 0.85
    ax.fill_between(x, cy, top, color=fill, alpha=0.45, linewidth=0, zorder=1)
    ax.plot(x, top, color=TXT, lw=1.0, zorder=2)
    if label:
        ax.text(
            cx, cy - 0.30, label, ha="center", va="top",
            fontsize=FS, color=TXT, style="italic", zorder=3,
        )
    return float(top.max())


def panel_a(ax) -> None:
    """Problem: selection reshapes the deployment target into a mismatched law."""
    _frame_only(ax)

    # ---- Row 1: the two-stage selection chain -------------------------
    y = 7.7
    boxes = [
        (1.3, 2.0, "Public target\n$\\mu$ over $h(i)$", BLUE),
        (3.5, 1.4, "Opportunity\n$R$", BEIGE),
        (5.4, 1.4, "Observation\n$O$", BEIGE),
        (7.3, 1.4, "Usable\n$U$", BEIGE),
        (9.25, 1.5, "Arrival mass\n$\\rho^{\\mathrm{arr}}$", TAUPE),
    ]
    h = 1.6
    for x, w, text, fc in boxes:
        _node(ax, (x, y), w, h, text, fc, fs=8)
    # arrows between consecutive boxes
    for (x0, w0, _, _), (x1, w1, _, _) in zip(boxes[:-1], boxes[1:]):
        _arrow(ax, (x0 + w0 / 2 + 0.03, y), (x1 - w1 / 2 - 0.03, y))
    # stage markers
    ax.text(4.45, y + h / 2 + 0.28, "stage 1", ha="center", va="bottom",
            fontsize=7.5, color=GRAY, style="italic")
    ax.text(6.35, y + h / 2 + 0.28, "stage 2", ha="center", va="bottom",
            fontsize=7.5, color=GRAY, style="italic")

    # ---- Row 2: the two induced laws, compared ------------------------
    cy = 3.35
    _mass_curve(ax, 3.0, cy, skew=0.0, fill=MU_FILL, label="$\\mu$")
    _mass_curve(ax, 7.0, cy, skew=0.9, fill=RHO_FILL, label="$\\rho^{\\mathrm{arr}}$")
    ax.text(3.0, cy - 0.62, "deployment target", ha="center", va="top",
            fontsize=7.5, color=GRAY)
    ax.text(7.0, cy - 0.62, "induced arrival", ha="center", va="top",
            fontsize=7.5, color=GRAY)

    # mismatch marker between the two curves
    _arrow(ax, (4.55, cy), (5.45, cy), color=MISMATCH, lw=1.0, style="<|-|>")
    ax.text(5.0, cy + 0.42, "$\\neq$", ha="center", va="bottom",
            fontsize=13, color=MISMATCH, fontweight="bold")
    ax.text(5.0, cy - 0.62, "structural mismatch", ha="center", va="top",
            fontsize=7.5, color=MISMATCH)

    # thin connectors: chain endpoints -> their laws
    _arrow(ax, (1.3, y - h / 2 - 0.02), (3.0, cy + 0.95),
           color=GRAY, lw=0.9, ls=":", style="-")
    _arrow(ax, (9.25, y - h / 2 - 0.02), (7.0, cy + 0.95),
           color=GRAY, lw=0.9, ls=":", style="-")


def panel_b(ax) -> None:
    """Architecture: one closed, coordinated loop (reconstruction + calibration)."""
    _frame_only(ax)

    cx, cy, R = 5.0, 5.15, 2.85
    # clockwise loop, standard math angles (degrees)
    pos = {
        "corr": (140.0, "Design / Obs / Use\ncorrection", BLUE),
        "norm": (190.0, "Normalized\nreconstruction", BLUE),
        "inst": (240.0, "Inst.\ncalibration", GREEN),
        "p2": (300.0, "(P2) feasible\nadjustment", GREEN),
        "debt": (350.0, "Debt\nupdate", GREEN),
        "agg": (40.0, "Aggregation\n$\\theta_{r+1}$", NAVY),
    }
    coords = {}
    for key, (deg, _, _) in pos.items():
        t = np.deg2rad(deg)
        coords[key] = (cx + R * np.cos(t), cy + R * np.sin(t))

    w, h = 2.7, 1.35
    for key, (_, text, fc) in pos.items():
        x, y = coords[key]
        _node(ax, (x, y), w, h, text, fc, fs=8)

    # flow arrows (clockwise)
    flow = [("corr", "norm"), ("norm", "inst"), ("inst", "p2"),
            ("p2", "debt"), ("debt", "agg")]
    for a, b in flow:
        (x0, y0), (x1, y1) = coords[a], coords[b]
        # pull arrow endpoints to the box edges
        dx, dy = x1 - x0, y1 - y0
        L = np.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p0 = (x0 + ux * (w / 2), y0 + uy * (h / 2))
        p1 = (x1 - ux * (w / 2), y1 - uy * (h / 2))
        _arrow(ax, p0, p1)

    # closing feedback arrow: aggregation -> correction (next round)
    (x0, y0), (x1, y1) = coords["agg"], coords["corr"]
    _arrow(ax, (x0, y0 + h / 2), (x1, y1 + h / 2),
           color=GRAY, lw=1.0, ls="--", rad=0.35)
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.15, "next round $r{+}1$",
            ha="center", va="center", fontsize=7.5, color=GRAY, style="italic")

    # center annotation
    ax.text(cx, cy + 0.32, "one coordinated\narchitecture",
            ha="center", va="center", fontsize=10, color=TXT, fontweight="bold")
    ax.text(cx, cy - 0.72, "reconstruction + calibration\n(not five independent modules)",
            ha="center", va="center", fontsize=7.5, color=GRAY)

    # subtle half labels
    ax.text(1.05, 6.15, "reconstruction", ha="center", va="center",
            fontsize=7.5, color=GRAY, rotation=90, style="italic")
    ax.text(8.95, 3.0, "calibration", ha="center", va="center",
            fontsize=7.5, color=GRAY, rotation=90, style="italic")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.9))
    panel_a(axes[0])
    panel_b(axes[1])
    fig.tight_layout(w_pad=0.8, h_pad=0.2)
    fig.savefig(OUT / "fig1_raven_problem_framework_v2.pdf")
    fig.savefig(OUT / "fig1_raven_problem_framework_v2.png")
    plt.close(fig)
    print("wrote", "fig1_raven_problem_framework_v2.pdf/.png")


if __name__ == "__main__":
    main()
