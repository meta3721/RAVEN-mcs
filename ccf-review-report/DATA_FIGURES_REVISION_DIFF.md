# 本轮最终源码差异（相对备份）

```diff
--- main.tex before
+++ main.tex final
@@ -1422,12 +1422,12 @@
 \begin{figure}[t]
 \raggedright
 \includegraphics[width=\columnwidth]{fig2_e2_risk_noninterchangeability.pdf}
-\caption{Risk interchangeability on complete-aligned NSW-Traffic.  (a)~Seed-level
-$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$
-over 20 paired seeds.  (b)~Count of negative risk differences across seeds.
-A negative value means that the arrival-weighted risk changes more than the
-deployment-target risk under the same selection shift.  Local-H\'ajek is omitted
-here because the risk-semantic experiment reports the five methods used in that test.}
+\caption{Complete-aligned NSW-Traffic risk differences.
+(a)~Mean $\pm$ sample SD over 20 paired seeds of
+$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$;
+zero denotes equal changes. (b)~Negative counts; the dotted line marks 10/20.
+Negative differences mean greater arrival-risk change under the same shift.
+Counts describe direction, not significance or performance ranking.}
 \label{fig:risk_noninterchangeability}
 \end{figure}
 
@@ -1442,11 +1442,11 @@
 \begin{figure}[t]
 \raggedright
 \includegraphics[width=\columnwidth]{fig_g3_tdrive_h_mass.pdf}
-\caption{T-Drive real-mobility opportunity.  (a)~Public $\boldsymbol\mu$,
-taxi opportunity, and a unit-balanced reference; real $R$ under-serves
-H3 and over-serves H4.  (b)~Four-block
-$\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$.
-Design is off; the RAVEN-NoDesign ranking is in
+\caption{T-Drive opportunity. (a)~Target $\boldsymbol\mu$, real taxi $R$,
+and unit-balanced reference. (b)~Four-block
+$\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$; SS/UA prot. denote
+Complete-aligned SensorScope/U-Air. The dotted $0.05$ line is the pre-specified
+mismatch-diagnostic threshold. Design-off performance is in
 Table~\ref{tab:tdrive_hybrid}.}
 \label{fig:g3_tdrive}
 \end{figure}
@@ -1531,13 +1531,11 @@
 \begin{figure}[t]
 \raggedright
 \includegraphics[width=\columnwidth]{fig_w1_design_gate.pdf}
-\caption{Design versus No-Design, estimated and oracle propensities
-(20 seeds; positive $=$ Design worse).  On SensorScope, Design slightly
-reduces $\Delta_{\mathrm{group}}$ ($-1.23\%$ estimated, $-1.03\%$
-oracle) with little change in mean RMSE.  On U-Air, estimated and oracle Design both
-worsen $\Delta_{\mathrm{group}}$ and $\mathrm{RMSE}_{\mu}$ by about
-$7.5\%$.  The U-Air Design-off arm runs
-Algorithm~\ref{alg:window_close} with $D_t=\mathrm{off}$.}
+\caption{Design versus No-Design with estimated/oracle propensities
+(20 seeds): $100(M_{\mathrm{Design}}-M_{\mathrm{NoDesign}})/M_{\mathrm{NoDesign}}$;
+positive means Design is worse. SensorScope improves group alignment with
+little RMSE change; U-Air worsens both endpoints by about $7.5\%$.
+The off arm uses Algorithm~\ref{alg:window_close} with $D_t=\mathrm{off}$.}
 \label{fig:w1_design_gate}
 \end{figure}
 

```

```diff
--- appendix.tex before
+++ appendix.tex final
@@ -1089,28 +1089,22 @@
 \begin{figure}[t]
 \centering
 \includegraphics[width=\columnwidth]{fig3_e3_structural_mismatch.pdf}
-\caption{Same-backbone structural alignment on SensorScope and
-U-Air (mean $\pm$ std over 20 paired seeds; lower is better).
-(a)(b)~SensorScope $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$;
-(c)(d)~U-Air $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$.
-SensorScope RAVEN-MCS is RAVEN-Design.  U-Air RAVEN-MCS in this
-figure uses Design on, not the Design-off rows of
-Table~\ref{tab:main_effectiveness}.  These rows are the frozen run set, and
-some of their active sets differ from the Table~\ref{tab:app_e3_uair} rows,
-so the figure supports no same-support claim of its own.}
+\caption{Frozen same-backbone structural results: means $\pm$ sample SD,
+20 paired seeds, lower is better. (a)(b)~SensorScope group/client--stratum
+mismatch; (c)(d)~U-Air counterparts. RAVEN-Design is on in both datasets;
+Table~\ref{tab:main_effectiveness} also reports U-Air off. Active sets differ
+from some Table~\ref{tab:app_e3_uair} rows, so these figures establish no
+same-support comparison.}
 \label{fig:e3_structural}
 \end{figure}
 
 \begin{figure}[t]
 \centering
 \includegraphics[width=\columnwidth]{fig4_e3_prediction_risk.pdf}
-\caption{Same-backbone deployment-target prediction risk
-(mean $\pm$ std over 20 paired seeds; lower is better).
-(a)(b)~SensorScope $\mathrm{RMSE}_{\mu}$ and Tail RMSE;
-(c)(d)~U-Air $\mathrm{RMSE}_{\mu}$ and Tail RMSE.
-U-Air RAVEN-MCS here uses Design on.  The Design-off U-Air row
-($\mathrm{RMSE}_{\mu}=1.1131$) is in
-Table~\ref{tab:main_effectiveness}.  Row identities are those stated in
+\caption{Frozen prediction results: means $\pm$ sample SD, 20 paired
+seeds, lower is better. (a)(b)~SensorScope target/Tail RMSE; (c)(d)~U-Air
+counterparts. RAVEN-Design is on; U-Air off ($\mathrm{RMSE}_{\mu}=1.1131$)
+is in Table~\ref{tab:main_effectiveness}. Support identities follow
 Fig.~\ref{fig:e3_structural}.}
 \label{fig:e3_prediction}
 \end{figure}
@@ -1599,13 +1593,13 @@
 \begin{figure}[t]
 \raggedright
 \includegraphics[width=\columnwidth]{fig_certificate_audit.pdf}
-\caption{Finite-sample audit of the aggregate coverage certificate.
-(a)~CERTIFIED windows: realized coverage $C_t$ versus
-$C^{\mathrm{LCB}}_t$.  The dashed line is $y=x$; dotted lines mark
-$\tau_{\mathrm{cov}}=0.05$.
-(b)~SensorScope $a=0.40$ timeline.  Gray bands are WARMUP; the red mark
-is a retained CERTIFIED miscoverage that triggers RESET on the next
-window.  The LCB stays below $0.05$, so Gate remains off.}
+\caption{Coverage-diagnostic audit of the historical candidate
+(separate from configured Design). (a)~CERTIFIED windows: $C_t$ versus
+$C_t^{\mathrm{LCB}}$; crosses retain actual miscoverage, dashes show $y=x$,
+and dotted lines mark $\tau_{\mathrm{cov}}=0.05$.
+(b)~SensorScope $a=0.40$: gray bands are WARMUP, the warm band is RESET,
+and the cross is the retained miscoverage triggering next-window RESET.
+The LCB stays below $0.05$, so diagnostic Gate stays off.}
 \label{fig:certificate_audit}
 \end{figure}
 
@@ -1799,10 +1793,12 @@
 
 \begin{figure*}[!tbp]
 \centering
-\includegraphics[width=0.74\textwidth]{fig_learning_capacity_r2.png}
-\caption{Development learning curves: physical training RMSE (top) and
-deployment-weighted validation RMSE (bottom). Lines/shading give means/seed
-ranges ($n=3$); dashes give strongest-baseline means.
+\includegraphics[width=\textwidth]{fig_learning_capacity_r2.pdf}
+\caption{Central-delivered development curves (seeds 41001--41003):
+training/validation RMSE by row, physical units by column. Lines/shading show
+means/seed min--max; dotted validation baselines are seed means. The log axis
+counts effective passes. Common-NDMF: Adam $.003$ on Traffic/SensorScope,
+SGD $.03$ on U-Air. HistoryResidual: Adam $.003/.001/.003$ respectively.
 Table~\ref{tab:learning_capacity} uses per-seed best checkpoints.}
 \label{fig:learning_capacity}
 \end{figure*}

```

```diff
--- make_figures.py before
+++ make_figures.py final
@@ -112,7 +112,9 @@
 
 
 def _panel_caption(ax, text: str, compact: bool = False) -> None:
-    ax.set_xlabel(text, fontsize=7.5 if compact else 9, labelpad=3 if compact else 4)
+    """Draw panel text separately, preserving the real horizontal-axis label."""
+    ax.text(0.5, -0.30 if compact else -0.25, text, transform=ax.transAxes,
+            ha="center", va="top", fontsize=7.5 if compact else 9, clip_on=False)
 
 
 def fig1_framework(output_dir=None, poppler=None):
@@ -129,84 +131,31 @@
     return module.render_fig1(OUT if output_dir is None else output_dir, poppler)
 
 
+def _revised_data_figure(name):
+    """Dispatch one deterministic data figure; no other figure is executed."""
+    import importlib.util
+    source = Path(__file__).with_name("data_figures_revision.py")
+    spec = importlib.util.spec_from_file_location("raven_data_figure_revision", source)
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    module.OUT = OUT
+    module.style()
+    return module.FUNCTIONS[name]()
+
+
 def fig2_e2() -> None:
-    df = pd.read_csv(SRC / "FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv")
-    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.15))
-    ax = axes[0]
-    data = [df.loc[df["method"] == m, "D_aligned"].astype(float).to_numpy() for m in E2_METHODS]
-    _barplot(ax, data, E2_SHORT, compact=True, headroom=0.38)
-    ax.axhline(0.0, color="0.35", ls="--", lw=0.8)
-    ax.set_ylabel(r"$D_{\mathrm{aligned}}$", fontsize=7)
-    _box(ax)
-    _panel_caption(ax, r"(a) Seed-level $D_{\mathrm{aligned}}$", compact=True)
-
-    ax = axes[1]
-    neg = [(df.loc[df["method"] == m, "D_aligned"].astype(float) < 0).sum() for m in E2_METHODS]
-    x = np.arange(len(E2_METHODS))
-    bars = ax.bar(x, neg, color=[RAVEN_COLOR if m == "RAVEN-MCS" else COLORS[i] for i, m in enumerate(E2_METHODS)],
-                  edgecolor="0.15", linewidth=0.6, width=0.7)
-    for i, b in enumerate(bars):
-        b.set_hatch(HATCHES[-1] if E2_METHODS[i] == "RAVEN-MCS" else HATCHES[i])
-    ax.set_xticks(x)
-    ax.set_xticklabels(E2_SHORT, rotation=42, ha="right", fontsize=5.6)
-    ax.set_ylabel("Negative seeds / 20", fontsize=7)
-    ax.tick_params(axis="y", labelsize=6.0)
-    ax.set_ylim(0, 24)
-    ax.axhline(10, color="0.7", ls=":", lw=0.6)
-    _box(ax)
-    _panel_caption(ax, r"(b) Direction count (not a ranking)", compact=True)
-    fig.tight_layout(w_pad=0.45)
-    fig.savefig(OUT / "fig2_e2_risk_noninterchangeability.pdf")
-    fig.savefig(OUT / "fig2_e2_risk_noninterchangeability.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig2_e2")
 
 
 def fig3_structural() -> None:
-    df = pd.read_csv(SRC / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv")
-    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
-    fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.35))
-    specs = [
-        (0, "SensorScope", "Delta_group", r"(a) SensorScope, $\Delta_{\mathrm{group}}$"),
-        (1, "SensorScope", "Delta_c_s", r"(b) SensorScope, $\Delta_{c,s}$"),
-        (2, "U-Air", "Delta_group", r"(c) U-Air, $\Delta_{\mathrm{group}}$"),
-        (3, "U-Air", "Delta_c_s", r"(d) U-Air, $\Delta_{c,s}$"),
-    ]
-    for c, ds, col, cap in specs:
-        ax = axes.flat[c]
-        sub = df[df["dataset"] == ds]
-        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
-        _barplot(ax, data, E3_SHORT, compact=True, headroom=0.42)
-        ax.set_ylabel(r"$\Delta_{\mathrm{group}}$" if col == "Delta_group" else r"$\Delta_{c,s}$", fontsize=7)
-        _box(ax)
-        _panel_caption(ax, cap, compact=True)
-    fig.tight_layout(h_pad=0.45, w_pad=0.35)
-    fig.savefig(OUT / "fig3_e3_structural_mismatch.pdf")
-    fig.savefig(OUT / "fig3_e3_structural_mismatch.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig3_structural")
 
 
 def fig4_prediction() -> None:
-    df = pd.read_csv(SRC / "FIG_E3_E3_PREDICTION_RISK.csv")
-    df = df[df["method"].isin(E3_METHODS) & df["dataset"].isin(["SensorScope", "U-Air"])]
-    fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.35))
-    specs = [
-        (0, "SensorScope", "RMSE_mu", r"(a) SensorScope, $\mathrm{RMSE}_{\mu}$"),
-        (1, "SensorScope", "Tail_RMSE", r"(b) SensorScope, Tail RMSE"),
-        (2, "U-Air", "RMSE_mu", r"(c) U-Air, $\mathrm{RMSE}_{\mu}$"),
-        (3, "U-Air", "Tail_RMSE", r"(d) U-Air, Tail RMSE"),
-    ]
-    for c, ds, col, cap in specs:
-        ax = axes.flat[c]
-        sub = df[df["dataset"] == ds]
-        data = [sub.loc[sub["method"] == m, col].astype(float).dropna().to_numpy() for m in E3_METHODS]
-        _barplot(ax, data, E3_SHORT, compact=True, headroom=0.42)
-        ax.set_ylabel(r"$\mathrm{RMSE}_{\mu}$" if col == "RMSE_mu" else "Tail RMSE", fontsize=7)
-        _box(ax)
-        _panel_caption(ax, cap, compact=True)
-    fig.tight_layout(h_pad=0.45, w_pad=0.35)
-    fig.savefig(OUT / "fig4_e3_prediction_risk.pdf")
-    fig.savefig(OUT / "fig4_e3_prediction_risk.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig4_prediction")
 
 
 def fig5_ablation() -> None:
@@ -361,188 +310,18 @@
 
 
 def fig_w1_design_gate() -> None:
-    df = pd.read_csv(SRC / "FIG_W1_DESIGN_GATE.csv")
-    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.15))
-    metrics = [
-        (0, "Delta_group_pct", r"(a) $\Delta_{\mathrm{group}}$ vs No-Design"),
-        (1, "RMSE_mu_pct", r"(b) $\mathrm{RMSE}_{\mu}$ vs No-Design"),
-    ]
-    datasets = ["SensorScope", "U-Air"]
-    variants = ["Estimated", "Oracle"]
-    x = np.arange(len(datasets))
-    w = 0.36
-    for c, col, cap in metrics:
-        ax = axes[c]
-        for j, var in enumerate(variants):
-            vals = [
-                float(df[(df["dataset"] == ds) & (df["variant"] == var)][col].iloc[0])
-                for ds in datasets
-            ]
-            bars = ax.bar(
-                x + (j - 0.5) * w, vals, width=w, label=var + " Design",
-                color=COLORS[j + 1] if j == 0 else RAVEN_COLOR,
-                edgecolor="0.15", linewidth=0.7,
-            )
-            for b in bars:
-                b.set_hatch(HATCHES[j])
-            for b, v in zip(bars, vals):
-                ax.text(
-                    b.get_x() + b.get_width() / 2.0,
-                    v + (0.22 if v >= 0 else -0.22),
-                    f"{v:+.2f}%", ha="center",
-                    va="bottom" if v >= 0 else "top", fontsize=5.5, color="0.15",
-                )
-        ax.axhline(0.0, color="0.35", ls="--", lw=0.8)
-        ax.set_xticks(x)
-        ax.set_xticklabels(datasets, fontsize=6.5)
-        ax.set_ylabel("rel. change (%)", fontsize=7)
-        ax.tick_params(axis="y", labelsize=6)
-        _box(ax)
-        if c == 0:
-            ax.legend(frameon=True, fancybox=False, edgecolor="0.3",
-                      fontsize=5.5, handlelength=1.1, loc="upper left", borderpad=0.2)
-        _panel_caption(ax, cap, compact=True)
-    fig.tight_layout(w_pad=0.4)
-    fig.savefig(OUT / "fig_w1_design_gate.pdf")
-    fig.savefig(OUT / "fig_w1_design_gate.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig_w1_design_gate")
 
 
 def fig_g3_tdrive() -> None:
-    mass = pd.read_csv(SRC / "FIG_G3_TDRIVE_H_MASS.csv")
-    tv = pd.read_csv(SRC / "FIG_G3_TDRIVE_TV.csv")
-    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.20))
-
-    ax = axes[0]
-    labels = mass["h_id"].tolist()
-    x = np.arange(len(labels))
-    w = 0.26
-    series = [
-        ("mu_test_seal", r"target $\mu$", COLORS[0], HATCHES[0]),
-        ("pi_opp_real_R", r"real $R$", RAVEN_COLOR, HATCHES[-1]),
-        ("pi_opp_balanced_unit", "unit-balanced", COLORS[1], HATCHES[1]),
-    ]
-    for j, (col, lab, fc, hatch) in enumerate(series):
-        bars = ax.bar(
-            x + (j - 1) * w, mass[col].to_numpy(), width=w, label=lab,
-            color=fc, edgecolor="0.15", linewidth=0.7,
-        )
-        for b in bars:
-            b.set_hatch(hatch)
-    ax.set_xticks(x)
-    ax.set_xticklabels(labels, fontsize=6.5)
-    ax.set_ylabel("group mass", fontsize=7)
-    ax.tick_params(axis="y", labelsize=6)
-    ax.set_ylim(0, 0.78)
-    ax.legend(frameon=True, fancybox=False, edgecolor="0.3",
-              fontsize=5.2, handlelength=1.0, ncol=1, loc="upper left", borderpad=0.2)
-    _box(ax)
-    _panel_caption(ax, r"(a) Four-block masses on T-Drive", compact=True)
-
-    ax = axes[1]
-    names = tv["source"].tolist()
-    vals = tv["tv_opp_vs_mu"].to_numpy()
-    x = np.arange(len(names))
-    bars = ax.bar(x, vals, width=0.55, color=[RAVEN_COLOR, COLORS[0], COLORS[1]],
-                  edgecolor="0.15", linewidth=0.7)
-    for i, b in enumerate(bars):
-        b.set_hatch(HATCHES[-1] if i == 0 else HATCHES[i])
-        ax.text(b.get_x() + b.get_width() / 2.0, vals[i] + 0.008,
-                f"{vals[i]:.3f}", ha="center", va="bottom", fontsize=6, color="0.15")
-    ax.axhline(0.05, color="0.45", ls=":", lw=0.8)
-    ax.set_xticks(x)
-    ax.set_xticklabels(["T-Drive", "SS prot.", "UA prot."], fontsize=6)
-    ax.set_ylabel(r"TV$(\pi^{\mathrm{opp}},\mu)$", fontsize=7)
-    ax.tick_params(axis="y", labelsize=6)
-    ax.set_ylim(0, 0.38)
-    _box(ax)
-    _panel_caption(ax, r"(b) Four-block opportunity--target TV", compact=True)
-
-    fig.tight_layout(w_pad=0.4)
-    fig.savefig(OUT / "fig_g3_tdrive_h_mass.pdf")
-    fig.savefig(OUT / "fig_g3_tdrive_h_mass.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig_g3_tdrive")
 
 
 def fig_certificate() -> None:
-    """Coverage-stress audit of Design_t := Gate_t (CERTIFIED windows + primary track)."""
-    win = pd.read_csv(LOCAL / "FIG_CERTIFICATE_WINDOWS.csv")
-    cert = win[win["state_before_decision"] == "CERTIFIED"].copy()
-    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.55))
-
-    ax = axes[0]
-    ss = cert[cert["dataset"] == "sensorscope"]
-    ua = cert[cert["dataset"] == "uair"]
-    ax.scatter(
-        ss["C_t"], ss["C_LCB"], s=14, marker="o", facecolors="none",
-        edgecolors=RAVEN_COLOR, linewidths=0.7, label="SensorScope",
-        zorder=3,
-    )
-    ax.scatter(
-        ua["C_t"], ua["C_LCB"], s=16, marker="s", facecolors="none",
-        edgecolors=COLORS[0], linewidths=0.7, label="U-Air",
-        zorder=3,
-    )
-    lo = 0.0
-    hi = max(float(cert["C_t"].max()), float(cert["C_LCB"].max()), 0.20)
-    ax.plot([lo, hi], [lo, hi], color="0.55", lw=0.7, ls="--", zorder=1)
-    ax.axhline(0.05, color="0.25", ls=":", lw=0.8, zorder=2)
-    ax.axvline(0.05, color="0.25", ls=":", lw=0.8, zorder=2)
-    ax.set_xlim(lo, hi)
-    ax.set_ylim(lo, hi)
-    ax.set_aspect("equal", adjustable="box")
-    ax.set_xlabel(r"$C_t$", fontsize=8)
-    ax.set_ylabel(r"$C^{\mathrm{LCB}}_t$", fontsize=8)
-    ax.legend(frameon=False, loc="upper left", fontsize=7, handletextpad=0.3)
-    _box(ax)
-    _panel_caption(ax, r"(a) CERTIFIED windows", compact=True)
-
-    ax = axes[1]
-    tr = win[
-        (win["dataset"] == "sensorscope") & (win["availability_level"] == 0.4)
-    ].sort_values("window_id")
-    x = tr["window_id"].to_numpy()
-    warmup = tr["state_before_decision"].eq("WARMUP").to_numpy()
-    reset = tr["state_before_decision"].eq("RESET").to_numpy()
-    in_band = False
-    start = 0
-    for i, flag in enumerate(warmup):
-        if flag and not in_band:
-            start = i
-            in_band = True
-        elif not flag and in_band:
-            ax.axvspan(x[start] - 0.5, x[i - 1] + 0.5, color="0.88", lw=0, zorder=0)
-            in_band = False
-    if in_band:
-        ax.axvspan(x[start] - 0.5, x[-1] + 0.5, color="0.88", lw=0, zorder=0)
-    rst_idx = np.flatnonzero(reset)
-    if len(rst_idx):
-        ax.axvspan(
-            x[rst_idx[0]] - 0.5, x[rst_idx[-1]] + 0.5,
-            color="#E8D4D4", lw=0, zorder=0,
-        )
-    ax.plot(x, tr["C_t"], color=RAVEN_COLOR, lw=1.1, label=r"$C_t$")
-    ax.plot(x, tr["C_hat"], color=COLORS[0], lw=0.9, ls="--", label=r"$\widehat C_t$")
-    ax.plot(x, tr["C_LCB"], color=COLORS[1], lw=1.1, label=r"$C^{\mathrm{LCB}}_t$")
-    ax.axhline(0.05, color="0.25", ls=":", lw=0.8)
-    trig = tr[tr["reset_trigger_after_window"].astype(int) == 1]
-    if len(trig):
-        ax.scatter(
-            trig["window_id"], trig["C_LCB"], marker="x", s=28,
-            color="#8C3A3A", linewidths=0.9, zorder=4, label="RESET trigger",
-        )
-    ax.set_xlim(-1, float(x.max()) + 1)
-    ax.set_ylim(0.0, 0.10)
-    ax.set_xlabel("window", fontsize=8)
-    ax.set_ylabel("coverage", fontsize=8)
-    ax.legend(frameon=False, loc="upper right", fontsize=6.5, ncol=2, columnspacing=0.6)
-    _box(ax)
-    _panel_caption(ax, r"(b) SensorScope, $a=0.40$", compact=True)
-
-    fig.tight_layout(w_pad=0.55)
-    fig.savefig(OUT / "fig_certificate_audit.pdf")
-    fig.savefig(OUT / "fig_certificate_audit.png")
-    plt.close(fig)
+    """Redraw this figure only from its original CSV rows."""
+    _revised_data_figure("fig_certificate")
 
 
 def main() -> None:

```
