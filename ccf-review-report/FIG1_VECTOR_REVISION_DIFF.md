# 图一与图注局部差异

```diff
--- main.tex before figure caption
+++ main.tex after figure caption
@@ -130,17 +130,21 @@
 \begin{figure*}[t]
 \centering
 \includegraphics[width=\textwidth]{fig1_raven_problem_framework.pdf}
-\caption{RAVEN-MCS constructs a deployment-target reference and calibrates it
-on finite-window support.  (a)~Three selection layers induce an arrival law that
-need not match the deployment target.
-(b)~RAVEN-Design forms a selection-corrected target-mass reference and
-calibrates it in the current feasible support.  RAVEN-NoDesign sets
-$\widehat\zeta=1$ to omit opportunity-to-target correction;
-observation/usability correction and calibration remain.
-The Design setting is fixed before the window opens and held throughout it;
-the coverage Gate is a separate diagnostic.
-The per-window program (P2) maps this reference onto the feasible aggregation
-set (Section~\ref{sec:calibration}).}
+\caption{RAVEN-MCS in an active window. (a)~Opportunity/observation
+correction supplies both normalized local training weights and corrected mass
+$m_{k,r}$; raw records remain local. Usable updates finish computation and
+transmission before close and satisfy the staleness limit.
+(b)~Pre-$U$ correction reconstructs $\widehat{\boldsymbol\beta}_r$ from
+$m_{k,r}d_{k,r}$. P2 converts this reference to feasible weights
+$\boldsymbol\alpha_r^\star$ using current support, composition, target and
+state (Section~\ref{sec:calibration}); exact target matching need not be feasible.
+(c)~Weights and normalized updates meet at aggregation. Afterwards, debt uses
+$\boldsymbol\omega_r=M_r\boldsymbol\alpha_r^\star$, not model parameters;
+debt and history feedback have separate destinations. Solid lines show current
+inputs; dashed lines carry next-window state. Design is fixed before opening;
+Gate is a separate diagnostic. The carrier and vectors are schematic; City
+Scanner clients are occupied space--time grid cells. Empty active sets preserve
+model and debt and add no effective step mass.}
 \label{fig:raven_overview}
 \end{figure*}
 

--- make_figures.py before
+++ make_figures.py after
@@ -115,218 +115,18 @@
     ax.set_xlabel(text, fontsize=7.5 if compact else 9, labelpad=3 if compact else 4)
 
 
-def fig1_framework() -> None:
-    """Fig. 1 from ``_paper_work/figures_nature``: funnel + coupled loop.
-
-    Visual content matches the Nature-restyled schematic.  The paper wrapper
-    stays ``figure*`` + ``width=\\textwidth``; this function only redraws the
-    same two panels in the IEEE two-column 1x2 slot.
+def fig1_framework(output_dir=None, poppler=None):
+    """Render Fig. 1 only from its editable vector reconstruction.
+
+    Other figure functions and frozen result inputs are intentionally untouched.
+    Use fig1_framework_vector.py directly in a reportlab-only environment.
     """
-
-    EDGE = "#4D4D4D"
-    TXT = "#272727"
-    MUTED = "#767676"
-    BLUE = "#D7E4F0"
-    BEIGE = "#EFE6DA"
-    GREEN = "#E3EDE4"
-    TAUPE = "#E8DDD4"
-    ACCENT = "#A56B6B"
-    WASH_B = "#EEF4F8"
-    WASH_G = "#EEF3EE"
-    RING = "#C5D0C8"
-
-    # Same 1x2 IEEE slot as the previous Overleaf Fig. 1 (not the stacked
-    # Nature canvas).  Content, colours, and glyphs are those of figures_nature.
-    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.35))
-    fig.subplots_adjust(left=0.012, right=0.988, top=0.97, bottom=0.11, wspace=0.08)
-
-    def frame(ax) -> None:
-        ax.set_xlim(0, 10)
-        ax.set_ylim(0, 10)
-        ax.set_xticks([])
-        ax.set_yticks([])
-        for s in ax.spines.values():
-            s.set_visible(True)
-            s.set_color("#B0B0B0")
-            s.set_linewidth(0.7)
-
-    def panel_label(ax, letter: str, title: str) -> None:
-        ax.set_xlabel(f"({letter}) {title}", fontsize=8, labelpad=2)
-
-    def capsule(ax, xy, w, h, text, fc, fs=6.2, math=None, math_fs=7.5) -> None:
-        x, y = xy
-        ax.add_patch(FancyBboxPatch(
-            (x - w / 2, y - h / 2), w, h,
-            boxstyle="round,pad=0.03,rounding_size=0.18",
-            facecolor=fc, edgecolor=EDGE, linewidth=0.75, zorder=3,
-        ))
-        if math is None:
-            ax.text(x, y, text, ha="center", va="center", fontsize=fs,
-                    color=TXT, zorder=4)
-        else:
-            ax.text(x, y + 0.18, text, ha="center", va="center", fontsize=fs,
-                    color=TXT, zorder=4)
-            ax.text(x, y - 0.26, math, ha="center", va="center", fontsize=math_fs,
-                    color=TXT, zorder=4)
-
-    def arrow(ax, p0, p1, color=EDGE, lw=0.95, rad=0.0, ms=8.0) -> None:
-        ax.add_patch(FancyArrowPatch(
-            p0, p1, arrowstyle="-|>", mutation_scale=ms,
-            color=color, lw=lw, zorder=5, shrinkA=0.2, shrinkB=0.2,
-            connectionstyle=f"arc3,rad={rad}",
-        ))
-
-    def bullseye(ax, x, y, r=0.26) -> None:
-        ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=EDGE,
-                            lw=0.55, zorder=5))
-        ax.add_patch(Circle((x, y), r * 0.64, facecolor=BLUE, edgecolor=EDGE,
-                            lw=0.4, zorder=6))
-        ax.add_patch(Circle((x, y), r * 0.26, facecolor=ACCENT, edgecolor="none",
-                            zorder=7))
-
-    def phone(ax, x, y, h=0.52) -> None:
-        w = h * 0.52
-        ax.add_patch(FancyBboxPatch(
-            (x - w / 2, y - h / 2), w, h,
-            boxstyle="round,pad=0.012,rounding_size=0.07",
-            facecolor=BEIGE, edgecolor=EDGE, linewidth=0.5, zorder=3,
-        ))
-        ax.add_patch(FancyBboxPatch(
-            (x - w / 2 + 0.04, y - h / 2 + 0.08), w - 0.08, h - 0.18,
-            boxstyle="round,pad=0.006,rounding_size=0.03",
-            facecolor="white", edgecolor="#A8A8A8", linewidth=0.3, zorder=4,
-        ))
-
-    def bars(ax, x, y, heights, fc, w=0.30, gap=0.09) -> None:
-        n = len(heights)
-        total = n * w + (n - 1) * gap
-        x0 = x - total / 2
-        for i, hi in enumerate(heights):
-            ax.add_patch(Rectangle(
-                (x0 + i * (w + gap), y), w, hi,
-                facecolor=fc, edgecolor=EDGE, linewidth=0.4, zorder=3,
-            ))
-
-    def funnel(ax, y_top, y_bot, w_top, w_bot, xc, fc, shift=0.0) -> None:
-        xtl, xtr = xc - w_top / 2, xc + w_top / 2
-        xbl, xbr = xc + shift - w_bot / 2, xc + shift + w_bot / 2
-        ax.add_patch(Polygon(
-            [(xtl, y_top), (xtr, y_top), (xbr, y_bot), (xbl, y_bot)],
-            closed=True, facecolor=fc, edgecolor="none", zorder=0, alpha=0.95,
-        ))
-
-    def chain(ax, x, y) -> None:
-        ax.add_patch(Circle((x - 0.12, y), 0.17, fill=False, edgecolor=EDGE,
-                            lw=0.7, zorder=6))
-        ax.add_patch(Circle((x + 0.12, y), 0.17, fill=False, edgecolor=EDGE,
-                            lw=0.7, zorder=6))
-
-    def feasible_set(ax, x, y, s=0.34) -> None:
-        pts = np.array([
-            (x, y + s), (x + 0.95 * s, y + 0.18 * s),
-            (x + 0.59 * s, y - 0.81 * s), (x - 0.59 * s, y - 0.81 * s),
-            (x - 0.95 * s, y + 0.18 * s),
-        ])
-        ax.add_patch(Polygon(pts, closed=True, facecolor="#F4F7F4",
-                             edgecolor=EDGE, lw=0.6, zorder=6))
-
-    # (a) funnel: public target is filtered by R → O → U into a mismatched arrival
-    ax = axes[0]
-    frame(ax)
-    panel_label(ax, "a", "Selection warps the public target")
-
-    ax.add_patch(FancyBboxPatch(
-        (1.50, 7.58), 7.20, 1.56,
-        boxstyle="round,pad=0.03,rounding_size=0.12",
-        facecolor=WASH_B, edgecolor="#C5D4E0", linewidth=0.55, zorder=0,
-    ))
-    bullseye(ax, 2.18, 8.36, r=0.28)
-    bars(ax, 4.15, 7.80, (0.66, 0.66, 0.66), BLUE)
-    ax.text(6.85, 8.52, "Public target", ha="center", va="center",
-            fontsize=6.2, color=TXT, zorder=4)
-    ax.text(6.85, 8.02, r"$\mu$ over $h(i)$", ha="center", va="center",
-            fontsize=7.5, color=TXT, zorder=4)
-
-    funnel(ax, 6.82, 2.18, 6.55, 3.85, 5.10, "#F3EBE0", shift=0.32)
-    phone(ax, 4.40, 6.52)
-    phone(ax, 5.10, 6.52)
-    phone(ax, 5.80, 6.52)
-    capsule(ax, (5.10, 5.82), 3.45, 0.70, r"Opportunity $R$", BEIGE)
-    capsule(ax, (5.20, 4.18), 3.25, 0.70, r"Observation $O$", BEIGE)
-    capsule(ax, (5.32, 2.68), 3.05, 0.70, r"Usable $U$", BEIGE)
-    arrow(ax, (5.12, 5.44), (5.18, 4.56), ms=8.0)
-    arrow(ax, (5.22, 3.80), (5.30, 3.06), ms=8.0)
-    ax.text(8.48, 4.18, "two-stage\nselection", ha="center", va="center",
-            fontsize=5.8, color=MUTED, zorder=4)
-
-    ax.add_patch(FancyBboxPatch(
-        (1.50, 0.22), 7.20, 1.82,
-        boxstyle="round,pad=0.03,rounding_size=0.12",
-        facecolor="#F3EBE4", edgecolor="#D4C4B6", linewidth=0.55, zorder=0,
-    ))
-    bars(ax, 4.15, 0.48, (0.30, 0.58, 0.90), TAUPE)
-    ax.text(6.85, 1.42, "Arrival mass", ha="center", va="center",
-            fontsize=6.2, color=TXT, zorder=4)
-    ax.text(6.85, 0.82, r"$\rho^{\mathrm{arr}}\neq\mu$", ha="center", va="center",
-            fontsize=7.5, color=TXT, zorder=4)
-
-    ax.plot([1.15, 1.15], [8.36, 1.13], color=ACCENT, lw=1.0,
-            ls=(0, (2.0, 1.3)), zorder=2, solid_capstyle="butt")
-    ax.plot([1.15, 1.48], [8.36, 8.36], color=ACCENT, lw=1.0, zorder=2)
-    ax.plot([1.15, 1.48], [1.13, 1.13], color=ACCENT, lw=1.0, zorder=2)
-    ax.add_patch(Circle((1.15, 4.75), 0.40, facecolor="white",
-                        edgecolor=ACCENT, lw=0.8, zorder=6))
-    ax.text(1.15, 4.75, r"$\neq$", ha="center", va="center", fontsize=8,
-            color=ACCENT, zorder=7)
-
-    # (b) orbit: reconstruction feeds a calibration loop on the feasible set
-    ax = axes[1]
-    frame(ax)
-    panel_label(ax, "b", "One coupled reconstruction + calibration loop")
-
-    ax.add_patch(FancyBboxPatch(
-        (0.55, 7.58), 8.90, 1.52,
-        boxstyle="round,pad=0.03,rounding_size=0.14",
-        facecolor=WASH_B, edgecolor="#C5D4E0", linewidth=0.55, zorder=0,
-        linestyle=(0, (1.6, 1.2)),
-    ))
-    capsule(ax, (3.05, 8.34), 3.70, 1.00,
-            "Design, observation\nand usable correction", BLUE, fs=5.6)
-    capsule(ax, (7.20, 8.34), 3.30, 1.00, "Normalized\nreconstruction", BLUE, fs=6.0)
-    arrow(ax, (4.88, 8.34), (5.42, 8.34))
-
-    cx, cy, rr = 5.05, 3.38, 2.38
-    ax.add_patch(Circle((cx, cy), rr + 0.78, facecolor=WASH_G,
-                        edgecolor="#C5D4C8", linewidth=0.55, zorder=0,
-                        linestyle=(0, (1.6, 1.2))))
-    ax.add_patch(Circle((cx, cy), rr, fill=False, edgecolor=RING,
-                        linewidth=1.35, zorder=1))
-    feasible_set(ax, cx, cy + 0.10, s=0.48)
-    ax.text(cx, cy - 0.58, "feasible set", ha="center", va="center",
-            fontsize=5.8, color=MUTED, zorder=6)
-
-    nodes_b = [
-        ((cx, cy + rr), 2.72, 0.95, "Instantaneous\ncalibration"),
-        ((cx + rr, cy), 2.55, 0.95, "(P2) feasible\nadjustment"),
-        ((cx, cy - rr), 2.28, 0.90, "Debt\nupdate"),
-        ((cx - rr, cy), 2.38, 0.98, "Aggregation"),
-    ]
-    for (xy, w, h, text) in nodes_b:
-        capsule(ax, xy, w, h, text, GREEN, fs=6.0)
-    ax.text(cx - rr, cy - 0.58, r"$\theta_{r+1}$", ha="center", va="top",
-            fontsize=7.5, color=TXT, zorder=6)
-
-    arrow(ax, (5.05, 7.58), (5.05, cy + rr + 0.50))
-    chain(ax, 4.22, 6.72)
-    ax.text(cx, 0.32, "not five independent modules", ha="center",
-            va="center", fontsize=6.2, color=MUTED, style="italic", zorder=7)
-    arrow(ax, (cx + 0.92, cy + rr - 0.52), (cx + rr - 0.52, cy + 0.92), rad=-0.22)
-    arrow(ax, (cx + rr - 0.52, cy - 0.92), (cx + 0.92, cy - rr + 0.52), rad=-0.22)
-    arrow(ax, (cx - 0.92, cy - rr + 0.52), (cx - rr + 0.52, cy - 0.92), rad=-0.22)
-
-    fig.savefig(OUT / "fig1_raven_problem_framework.pdf")
-    fig.savefig(OUT / "fig1_raven_problem_framework.png")
-    plt.close(fig)
+    import importlib.util
+    source = Path(__file__).with_name("fig1_framework_vector.py")
+    spec = importlib.util.spec_from_file_location("raven_fig1_vector", source)
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    return module.render_fig1(OUT if output_dir is None else output_dir, poppler)
 
 
 def fig2_e2() -> None:

```
