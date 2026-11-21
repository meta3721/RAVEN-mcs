"""Icon-based redesign of Fig. 1 for the RAVEN-MCS paper (IEEE TMC).

This version borrows the "concrete icon" idiom from the reference system-model
figures (cloud = server, phones = mobile participants) to make the paper's
storyline easier to parse, while keeping the meaning identical to the original.

  (a) The problem.  Mobile participants (phones) feed the server (cloud)
      through the three non-random selection layers Opportunity R ->
      Observation O -> Usable U, so the arrival law rho_arr that reaches the
      cloud need not match the public deployment target mu (bullseye).  The
      dashed "wanted mu" arrow vs. the actual arrival shows the mismatch.

  (b) The architecture.  One coordinated server-side loop (reconstruction +
      calibration) closes through Aggregation theta_{r+1} and feeds the next
      round of mobile participants -- not five independent modules.

No data is read (schematic only).  Entities are limited to those that actually
exist in the paper: a server and mobile clients; no fog node / requester.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent / "figures"

EDGE = "#595959"
TXT = "#333333"
GRAY = "#7A7A7A"
BLUE = "#D9E2EC"    # target / reconstruction
BEIGE = "#EEE6DC"   # selection gates / participants
GREEN = "#E8EEE6"   # calibration
TAUPE = "#E4DCD3"   # arrival / mismatch
NAVY = "#3D5A73"    # RAVEN accent / aggregation
MISMATCH = "#8A4B4B"

FS = 8


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
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(EDGE)
        s.set_linewidth(1.2)


def _arrow(ax, p0, p1, color=EDGE, lw=1.1, ls="-", rad=0.0, style="-|>", ms=11) -> None:
    a = FancyArrowPatch(
        p0, p1, arrowstyle=style, mutation_scale=ms,
        color=color, lw=lw, linestyle=ls, zorder=4,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(a)


def _node(ax, xy, w, h, text, fc, fs=FS, lw=1.1) -> None:
    x, y = xy
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.05,rounding_size=0.12",
        facecolor=fc, edgecolor=EDGE, linewidth=lw, zorder=2,
    ))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=TXT, zorder=3)


def _cloud(ax, x, y, w, h, fc, lw=1.1, zorder=2) -> None:
    """A soft cloud (server) icon: rounded body + three puffs."""
    body = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h * 0.70,
        boxstyle="round,pad=0.03,rounding_size=0.24",
        facecolor=fc, edgecolor=EDGE, linewidth=lw, zorder=zorder,
    )
    ax.add_patch(body)
    for (px, py, pr) in [
        (x - w * 0.24, y + h * 0.08, h * 0.26),
        (x, y + h * 0.15, h * 0.30),
        (x + w * 0.24, y + h * 0.08, h * 0.26),
    ]:
        ax.add_patch(Circle((px, py), pr, facecolor=fc, edgecolor="none", zorder=zorder))


def _phone(ax, x, y, w=0.78, h=1.4, fc=BEIGE, lw=1.0) -> None:
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.20",
        facecolor=fc, edgecolor=EDGE, linewidth=lw, zorder=3,
    ))
    ax.add_patch(FancyBboxPatch(
        (x - w / 2 + 0.10, y - h / 2 + 0.16), w - 0.20, h - 0.44,
        boxstyle="round,pad=0.01,rounding_size=0.08",
        facecolor="white", edgecolor=GRAY, linewidth=0.5, zorder=4,
    ))
    ax.add_patch(Circle((x, y - h / 2 + 0.09), 0.045, facecolor=GRAY,
                        edgecolor="none", zorder=5))


def _target(ax, x, y, r=0.62) -> None:
    ax.add_patch(Circle((x, y), r, facecolor=BLUE, edgecolor=EDGE, linewidth=1.1, zorder=3))
    ax.add_patch(Circle((x, y), r * 0.60, facecolor="white", edgecolor=EDGE, linewidth=0.7, zorder=4))
    ax.add_patch(Circle((x, y), r * 0.24, facecolor=NAVY, edgecolor="none", zorder=5))


def panel_a(ax) -> None:
    _frame_only(ax)

    # ---- deployment target (bullseye) + label, top-left ---------------
    _target(ax, 2.0, 8.65)
    ax.text(2.0, 7.75, "deployment target", ha="center", va="top",
            fontsize=7.5, color=GRAY)
    _node(ax, (4.4, 8.65), 3.2, 1.15, "public target\n$\\mu$ over $h(i)$", BLUE, fs=8)

    # ---- participants (phones), left ----------------------------------
    for (px, py) in [(1.45, 7.0), (1.05, 5.7), (1.45, 4.4)]:
        _phone(ax, px, py)
    ax.text(1.35, 3.15, "mobile\nparticipants", ha="center", va="top",
            fontsize=7.5, color=GRAY)

    # ---- selection gates, middle --------------------------------------
    gy = 5.7
    gates = [(3.3, "Opportunity\n$R$"), (5.05, "Observation\n$O$"), (6.8, "Usable\n$U$")]
    for (gx, label) in gates:
        _node(ax, (gx, gy), 1.4, 1.15, label, BEIGE, fs=7.5)

    # ---- server cloud, right ------------------------------------------
    _cloud(ax, 8.75, gy, 2.2, 2.1, TAUPE)
    ax.text(8.75, gy + 0.18, "server", ha="center", va="center", fontsize=8, color=TXT, zorder=6)
    ax.text(8.75, gy - 0.42, "arrival\n$\\rho^{\\mathrm{arr}}$", ha="center", va="center",
            fontsize=7.5, color=TXT, zorder=6)

    # ---- flow arrows ---------------------------------------------------
    _arrow(ax, (1.85, 5.7), (2.55, 5.7))
    _arrow(ax, (4.05, 5.7), (4.3, 5.7))
    _arrow(ax, (5.8, 5.7), (6.05, 5.7))
    _arrow(ax, (7.55, 5.7), (7.78, 5.7))

    # ---- stage markers --------------------------------------------------
    ax.text(4.18, 6.55, "stage 1", ha="center", va="bottom", fontsize=7.5,
            color=GRAY, style="italic")
    ax.text(5.92, 6.55, "stage 2", ha="center", va="bottom", fontsize=7.5,
            color=GRAY, style="italic")

    # ---- non-random drop at each gate -----------------------------------
    for gx in (3.3, 5.05, 6.8):
        ax.plot([gx, gx], [5.125, 4.45], color=GRAY, lw=0.9, ls="--", zorder=3)
        ax.text(gx, 4.32, "$\\times$", ha="center", va="top", fontsize=8,
                color=MISMATCH, zorder=4)
    ax.text(5.05, 3.55, "non-random drop at each layer", ha="center", va="top",
            fontsize=7.5, color=GRAY, style="italic")

    # ---- wanted-mu vs actual arrival (mismatch) --------------------------
    _arrow(ax, (4.4, 8.05), (8.0, 6.85), color=GRAY, lw=1.0, ls="--", rad=0.25)
    ax.text(6.4, 7.75, "wanted: $\\mu$", ha="center", va="center", fontsize=7.5,
            color=GRAY, style="italic")
    _node(ax, (5.0, 2.6), 6.6, 1.0,
          "structural mismatch:  $\\rho^{\\mathrm{arr}}\\neq\\mu$", TAUPE, fs=8.5)


def panel_b(ax) -> None:
    _frame_only(ax)

    # ---- participants (phones) feed the server --------------------------
    for (px, py) in [(1.4, 7.3), (1.0, 5.6), (1.4, 3.9)]:
        _phone(ax, px, py)
    ax.text(1.35, 2.6, "mobile\nparticipants", ha="center", va="top",
            fontsize=7.5, color=GRAY)
    _arrow(ax, (1.85, 5.6), (3.9, 5.6))
    ax.text(2.9, 6.0, "observations", ha="center", va="bottom", fontsize=7.5,
            color=GRAY, style="italic")

    # ---- server cloud containing the coordinated loop --------------------
    _cloud(ax, 6.9, 5.6, 5.6, 5.9, BLUE)
    ax.text(5.05, 7.5, "server", ha="center", va="center", fontsize=8.5,
            color=TXT, zorder=6)

    cx, cy, R = 6.9, 5.5, 1.5
    pos = {
        "corr": (140.0, "Design/Obs/Use\ncorrection", BLUE),
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

    w, h = 2.3, 1.0
    for key, (_, text, fc) in pos.items():
        x, y = coords[key]
        _node(ax, (x, y), w, h, text, fc, fs=7)

    flow = [("corr", "norm"), ("norm", "inst"), ("inst", "p2"),
            ("p2", "debt"), ("debt", "agg")]
    for a, b in flow:
        (x0, y0), (x1, y1) = coords[a], coords[b]
        dx, dy = x1 - x0, y1 - y0
        L = np.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p0 = (x0 + ux * (w / 2), y0 + uy * (h / 2))
        p1 = (x1 - ux * (w / 2), y1 - uy * (h / 2))
        _arrow(ax, p0, p1, lw=1.0, ms=10)

    # feedback: aggregation -> next round of participants
    (x0, y0), (x1, y1) = coords["agg"], coords["corr"]
    _arrow(ax, (x0, y0 + h / 2), (x1, y1 + h / 2), color=GRAY, lw=1.0, ls="--", rad=0.35)
    ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.30, "next round $r{+}1$",
            ha="center", va="center", fontsize=7, color=GRAY, style="italic")

    ax.text(cx, cy + 0.30, "one coordinated\narchitecture", ha="center", va="center",
            fontsize=9, color=TXT, fontweight="bold")
    ax.text(cx, cy - 0.66, "reconstruction + calibration\n(not five independent modules)",
            ha="center", va="center", fontsize=7, color=GRAY)

    # legend
    for (lx, label, fc) in [(1.3, "reconstruction", BLUE), (4.5, "calibration", GREEN),
                            (7.1, "aggregation", NAVY)]:
        ax.add_patch(FancyBboxPatch((lx, 1.55), 0.34, 0.34,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=fc, edgecolor=EDGE, linewidth=0.7, zorder=3))
        ax.text(lx + 0.45, 1.72, label, ha="left", va="center", fontsize=6, color=TXT)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.1))
    panel_a(axes[0])
    panel_b(axes[1])
    fig.tight_layout(w_pad=0.9, h_pad=0.2)
    fig.savefig(OUT / "fig1_raven_problem_framework_v3.pdf")
    fig.savefig(OUT / "fig1_raven_problem_framework_v3.png")
    plt.close(fig)
    print("wrote fig1_raven_problem_framework_v3.pdf/.png")


if __name__ == "__main__":
    main()
