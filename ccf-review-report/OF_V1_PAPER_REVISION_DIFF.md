# OF-v1论文整合：当前工作树差异

基线为本轮编辑前的规范源码，不是Git HEAD。保留了其他AI的现有修复。

仅编辑main.tex、appendix.tex、supplemental.tex；未修改算法、参数、原始结果、协议、书目或图像。正文新增约60词单段，附录新增约310词（含公式的空格分词粗计，不含表体）与单栏五臂表。为满足14页，去重附近开发学习/几何、City Scanner协议说明、图表标题，合并重复诊断标题。全部旧数学环境及数值表体保持。

原Projection-with-Debt Sensitivity归入P2诊断E-A，保留app:trained_rule_probe/app:kappa_probe；这项迁移不计为净节省。开发学习曲线采用标准浮动位置[!tbp]，宽度、图像、模板、字号及间距参数不变。

## main.tex

```diff
--- main.tex (before this task)
+++ main.tex (canonical)
@@ -1788,16 +1788,13 @@
 practical criterion.  Target dilution alone therefore does not explain the
 small gain of this oracle/update configuration.
 
-\paragraph{Separate development geometry and learning.}
-Table~\ref{tab:development_geometry} summarizes three separate development
-trajectories. For feasible group range
+Table~\ref{tab:development_geometry} covers three development trajectories. For group range
 $W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
 \min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
 where $W_{r,g}\ge.01$.
 Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
 composition direction, but only $4.651\%$ mean adjustable target mass.
-These subsets distinguish the existence of an adjustment direction from the
-amount of target mass it can move. References violate constraints in $59.02\%$, with mean projection distance
+References violate constraints in $59.02\%$, with mean projection distance
 $.067487$.  Appendix~\ref{app:development_geometry} varies caps/ESS.
 
 \begin{table}[t]
@@ -1818,38 +1815,41 @@
 \end{tabular}
 \end{table}
 
-Longer-budget centralized learning uses development validation in physical
-units on seeds 41001--41003 (Appendix~\ref{app:learning_capacity}).
-Common-NDMF Central-delivered improves on simple baselines for Traffic and
-SensorScope but remains worse on U-Air. The single federated Traffic Uniform
-trajectory has not plateaued. These measurements assess backbone learning,
-while Table~\ref{tab:trained_rules} isolates aggregation-rule effects.
+Central-delivered Common-NDMF outperforms simple baselines on Traffic/SensorScope,
+not U-Air (development seeds 41001--41003; physical units;
+Appendix~\ref{app:learning_capacity}). Traffic Uniform has not plateaued.
+Table~\ref{tab:trained_rules} isolates aggregation effects.
 
 \subsection{Update-Rule Sensitivity and Coverage Scope}
 \label{subsec:limitations}
 
-NSW-Traffic has mean $K=12.1$; only $15.1\%$ of active windows in a separate
-15-seed comparison force Uniform.  Under the original server step four
-federated members, including oracle margins, agree in RMSE within $.002\%$.
-Increasing local steps from 2 to 20 leaves FedAvg $2.8\%$--$3.0\%$ above
-a centralized Adam reference ($10^{-3}$, 20 minibatch steps of 32).
-The optimizer and training budget differ in this comparison; federated
-parameters move $.26\%$--$.40\%$ of their initial norm.
-
-Replacing only the server step with Adam ($\beta_1=.9$, $\beta_2=.99$,
-$\tau=10^{-3}$, rate $.003$, one update per window) on 15 seeds unused for
-rate selection yields oracle-margin headroom versus FedAvg of $-1.49\%$
-($[-5.42,+1.76]\%$), with 80\% MDE $5.80\%$.  This wide interval does not
-establish equivalence at $.5\%$.  Mean RMSE is $.967/.973$, ranges
-$[.659,1.572]/[.795,1.459]$, below the $1.007$ constant reference mean.
-On those same runs oracle weights reduce group/client--stratum mismatch by
-$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$).
-
-\paragraph{Coverage diagnostic.}
-The separate coverage-controlled candidate couples $\mathrm{Design}_t=\mathrm{Gate}_t$,
-unlike pre-window configured Design in the main method.  Empirical pooled
-CERTIFIED validity for this candidate is $.959$, falling to $.750$ for U-Air
-at $a=1$ (Appendix~\ref{app:certificate_audit}).
+On NSW-Traffic (mean $K=12.1$, $15.1\%$ forced-Uniform active windows,
+15 seeds), four federated rules including oracle margins agree within
+$.002\%$ RMSE with the original server step. At 2/20 local steps, FedAvg
+remains $2.8\%$--$3.0\%$ above centralized Adam ($10^{-3}$, 20 minibatches
+of 32), with different optimizers and budgets; federated parameter movement is
+$.26\%$--$.40\%$ of initial norm.
+
+Server-only Adam ($\beta_1=.9$, $\beta_2=.99$, $\tau=10^{-3}$, rate $.003$,
+one update/window) on 15 seeds unused for rate selection gives oracle-margin
+RMSE headroom over FedAvg of $-1.49\%$ ($[-5.42,+1.76]\%$; 80\% MDE
+$5.80\%$), without establishing $.5\%$ equivalence. Mean RMSE is
+$.967/.973$, ranges $[.659,1.572]/[.795,1.459]$, versus the $1.007$ constant
+reference. Oracle weights reduce group/client--stratum mismatch by
+$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$) on these runs.
+
+Window closure determines when messages are aggregated, whereas mixture
+calibration chooses how available client updates are weighted.
+On one previously used Traffic development seed, fixing the rolling release-quality reference
+after warm-up changed 129 of 799 original-trajectory decisions.
+In autonomous runs, the rolling reference
+shortened mean windows by $30.08\%$ while increasing time-averaged composition
+mismatch by $.02584$ (Appendix~\ref{app:release_timing}).
+
+The coverage-controlled candidate uses $\mathrm{Design}_t=\mathrm{Gate}_t$,
+unlike the main method's pre-window configuration. Pooled CERTIFIED
+validity is $.959$; U-Air has $.750$ at $a=1$
+(Appendix~\ref{app:certificate_audit}).
 
 \section{Conclusion}
 \label{sec:conclusion}
```

## appendix.tex

```diff
--- appendix.tex (before this task)
+++ appendix.tex (canonical)
@@ -992,6 +992,19 @@
 \end{tabular*}
 \end{table}
 
+
+\subsection{Projection-with-Debt Sensitivity}
+\label{app:trained_rule_probe}
+\label{app:kappa_probe}
+
+At tuned $\kappa=1000$, projection-with-debt gains $1.347/.580$ pp on
+SensorScope/U-Air over projection (Holm $\approx10^{-5}$), versus the
+frozen-strength $.0073$ pp SensorScope gain inside the practical band.
+Projection's maximum endpoint discrepancy across 240 runs is
+$\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units ($.00121$ pp):
+17\% of the frozen-strength debt effect, $.13\%/.16\%$ of Design/projection
+contrasts. Point-level optimality checks do not all pass; endpoint agreement
+is not certification.
 
 \FloatBarrier
 
@@ -1670,15 +1683,11 @@
 
 \begin{table}[t]
 \centering
-\caption{Offline target-support statistic per block, and the Design
-setting returned by the support rule \eqref{eq:design_gate}.
-Zero test: frozen $\pi^{\mathrm{tar}}(k(i),s(i))$ for the occupancy-attached
-client; a missing key is $0$.
-The support rule sets Design on exactly when this statistic is zero, and it does not
-verify positivity on target-positive pairs.
-The rule outputs coincide with the settings displayed in the rankings;
-the counts alone do not establish when their inputs became available.
-U-Air $25.5\%$ is EventTrace occurrence, not this statistic.}
+\caption{Offline zero-target counts for occupancy-attached clients using
+frozen $\pi^{\mathrm{tar}}(k(i),s(i))$ (missing keys: $0$).
+Rule~\eqref{eq:design_gate} returns the reported Design settings.
+These counts establish neither target-positive support nor pre-window input
+availability; U-Air's $25.5\%$ EventTrace occurrence is a different statistic.}
 \label{tab:scd_phi_freeze}
 \scriptsize
 \setlength{\tabcolsep}{2.5pt}
@@ -1696,73 +1705,65 @@
 \end{tabular*}
 \end{table}
 
-SensorScope and U-Air look up test-split client--stratum mass
-$\pi^{\mathrm{tar}}_{k,s}$.  T-Drive looks up test-split stratum
-frequency.  City Scanner blocks assign the test-group share $\mu_{h(i)}$
-to training atoms, with all four regions positive.  NSW-Traffic uses a
-four-region freeze.  These are distinct lookup objects.  The same
-coverage statistic on one map does not mean that the SensorScope/U-Air
-support statistic transferred.  The City Scanner value follows from
-positive regional $\mu$, not from checking target-positive pairs.
+Lookup objects differ: test-split client--stratum mass
+$\pi^{\mathrm{tar}}_{k,s}$ on SensorScope/U-Air, test-stratum frequency on
+T-Drive, and a four-region freeze on NSW-Traffic. City Scanner assigns
+positive test-group shares $\mu_{h(i)}$ to training atoms, rather than
+checking target-positive pairs; its zero count is not the SensorScope/U-Air
+support check.
 
 \subsection{City Scanner New York {PM}$_{2.5}$}
 \label{app:cityscanner_nyc}
 
-The visit-occupancy block uses New York Pilot~1/2 {PM} CSVs from
-Zenodo 10.5281/zenodo.7961851 ({CC BY} 4.0)~\cite{wang2023cityscanner},
-excluding Boston, Beirut, and {NO}$_2$. Non-finite GPS, time, or {PM}$_{2.5}$
-and concentrations outside $[0,1000]$\,$\mu$g/m$^3$ are removed.
-$Y$ averages the remaining calibrated measurements in occupied
-$500$\,m $\times$ $30$\,min cells; empty slots are absent, not imputed.
-Clients are cells, with GPS determining real occupancy $R$.
-The four-quadrant target uses median cell indices without $Y$;
-$\boldsymbol\mu$ is the test-region share. Strata are
+New York Pilot~1/2 {PM} CSVs (Zenodo 10.5281/zenodo.7961851,
+{CC BY} 4.0)~\cite{wang2023cityscanner} exclude Boston, Beirut and {NO}$_2$.
+Filtering removes non-finite GPS/time/{PM}$_{2.5}$ and values outside
+$[0,1000]$\,$\mu$g/m$^3$. Occupied $500$\,m $\times$ $30$\,min cells average
+calibrated measurements into $Y$; empty slots are absent. Cells are clients;
+GPS supplies $R$. Median cell indices define four quadrants without $Y$;
+$\boldsymbol\mu$ is their test share. Strata are
 $\mathrm{region}{::}\mathrm{block}{::}\mathrm{weekday}$ (at most 32).
-$O/U$ are Complete-aligned controls ($p_{\mathrm{obs}}=.35$, $S_{\max}=5$).
-
-There are 14723 units, 446 cells and 2776 slots; chronological
-train/validation/test counts are $9343/3290/2090$, with test-region counts
-$496/992/148/454$. Seeds $32001$--$32010$ share 100 windows formed by
-equal-count bins of the 1666 training slots. Design is on and Gate unused
-(Table~\ref{tab:scd_phi_freeze}). Table~\ref{tab:cityscanner_real}(a)
-reports training-standardized errors. The driver clips tiny negative solver
-weights and renormalizes; one seed-32006 window required this correction.
+Complete-aligned $O/U$ use $p_{\mathrm{obs}}=.35$, $S_{\max}=5$.
+
+The 14723 units, 446 cells and 2776 slots split chronologically into
+$9343/3290/2090$ train/validation/test units (test regions:
+$496/992/148/454$). Seeds $32001$--$32010$ share 100 equal-count windows
+of 1666 training slots. Design is on; Gate unused
+(Table~\ref{tab:scd_phi_freeze}). Table~\ref{tab:cityscanner_real}(a) uses
+training-standardized errors. One seed-32006 window required the driver's
+clipping and renormalization of tiny negative solver weights.
 
 \subsection{City Scanner Pilot~2 with Measured Observation}
 \label{app:cityscanner_p2_measured_o}
 
-This block uses New York Pilot~2 {PM} and {NO}$_2$ CSVs from the same
-licensed source, excluding Pilot~1, Boston and Beirut. Clients and $Y$ use
-the same grid-cell definitions. Union GPS defines $R$; finite {PM}$_{2.5}$
-in $[0,1000]$ defines $O=1$. {NO}$_2$ contributes locations only.
-$U$ remains Complete-aligned ($S_{\max}=5$). The frozen region target,
-Design-on setting and unused Gate are unchanged in role, not in numerical
-target values.
-
-Occupancy comprises 14960 cell-slots, 416 cells and 2402 slots:
-$10141/2835/1984$ train/validation/test. There are 1931 unobserved units
-($12.9\%$) and 13029 labeled units; test-region occupancy is
-$1289/268/144/283$. Seeds $33001$--$33010$ use 100 windows from 1441
-training slots. Table~\ref{tab:cityscanner_real}(b) reports errors in this
-block's own training-standardized scale. Section~\ref{subsec:cityscanner_real}
-gives both rankings, paired comparisons and the missed improvement criterion.
+Pilot~2 uses {PM}/{NO}$_2$ CSVs from the same source, excluding Pilot~1,
+Boston and Beirut, with the same client/$Y$ grid. Union GPS supplies $R$;
+finite {PM}$_{2.5}$ in $[0,1000]$ supplies $O=1$. {NO}$_2$ contributes
+locations only. $U$ remains Complete-aligned ($S_{\max}=5$). The frozen regional
+target, Design-on and unused Gate retain their roles, with different target values.
+
+The 14960 cell-slots, 416 cells and 2402 slots split into
+$10141/2835/1984$ train/validation/test units: 1931 unobserved ($12.9\%$),
+13029 labeled; test-region occupancy $1289/268/144/283$.
+Seeds $33001$--$33010$ use 100 windows from 1441 training slots.
+Table~\ref{tab:cityscanner_real}(b) uses this block's training standardization;
+Section~\ref{subsec:cityscanner_real} gives rankings, paired comparisons and
+the missed improvement criterion.
 
 \subsection{City Scanner Target Maps and Zero-Mass Handling}
 \label{app:cityscanner_sixarm}
 
-This trained six-arm comparison uses the visit-occupancy protocol with
-controlled $O/U$: ten traces, each with model seeds $s,s+100000,s+200000$.
-The 180 cells comprise 150 newly trained and 30 reused cells. Maps are fixed
-before training from public locations, calendar strata and test-region shares,
-without responses or model errors. Table~\ref{tab:cityscanner_sixarm}
-reports mean and SD over ten within-trace model-seed means.
+The six-arm visit-occupancy comparison uses controlled $O/U$ and ten traces
+with model seeds $s,s+100000,s+200000$: 150 newly trained and 30 reused runs.
+Maps use public locations, calendar strata and test-region shares before
+training, without responses/errors. Table~\ref{tab:cityscanner_sixarm}
+summarizes ten within-trace model-seed means.
 
 \begin{table}[t]
 \centering
-\caption{Supplementary client--stratum gaps for the six trained target-map
-variants in Table~\ref{tab:cityscanner_sixarm} (mean $\pm$ SD over ten trace
-means of three model seeds). Each gap uses its arm's own target map;
-these values do not rank alignment to a common client--stratum target.}
+\caption{Client--stratum gaps for Table~\ref{tab:cityscanner_sixarm}
+(mean $\pm$ SD, ten trace means of three model seeds).
+These arm-specific gaps do not rank alignment to a common target.}
 \label{tab:cityscanner_sixarm_cs}
 \footnotesize
 \begin{tabular}{lr}
@@ -1779,61 +1780,54 @@
 \end{tabular}
 \end{table}
 
-\texttt{fedavg\_window} uses count weights and \texttt{raven\_wo\_design}
-fixes Design off, so neither applies the target ratio.
-\texttt{raven\_ctrl} uses the test-location control map (1164 keys,
-812 zeros). \texttt{raven\_ctrl\_floor} fills these zeros with the smallest
-positive mass ($4.78469\times10^{-4}$) and renormalizes, changing group
-marginals. \texttt{raven\_M1mu}/\texttt{raven\_M2mu} use ACS population/NYC~311
-shapes on the same keys, rescaled within region to the common target;
-70/33 zero keys remain. All maps cover the 959 recorded risk-set keys.
-
-The primary $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ uses within-trace
-model-seed mean RMSE, giving a Hodges--Lehmann estimate of $-.019\%$
-(paired Wilcoxon $p=.922$). Resampling traces and model seeds within trace
-gives the recorded 95\% percentile interval $[-1.89\%,+12.28\%]$,
-which spans zero and extends beyond the $2\%$ equivalence band.
-The group-gain retention is
+Count-weighted \texttt{fedavg\_window} and Design-off
+\texttt{raven\_wo\_design} omit the target ratio.
+\texttt{raven\_ctrl} has 1164 keys, 812 zero; \texttt{raven\_ctrl\_floor}
+replaces zeros with $4.78469\times10^{-4}$, the smallest positive mass,
+and renormalizes, changing group marginals.
+\texttt{raven\_M1mu}/\texttt{raven\_M2mu} use ACS population/NYC~311 shapes
+on these keys, rescaled within region to the common target (70/33 zeros).
+All maps cover the 959 risk-set keys.
+
+For $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ on within-trace mean RMSE,
+Hodges--Lehmann gives $-.019\%$ (paired Wilcoxon $p=.922$).
+Hierarchical resampling of traces and their model seeds gives the 95\%
+percentile interval $[-1.89\%,+12.28\%]$, including zero but extending above
+the $2\%$ equivalence band. Group-gain retention is
 $(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{floor}})/
 (\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$.
 
-The three registered chains compare floor, M1$\mu$, and M2$\mu$ with FedAvg.
-Their structure node H1 applies a one-sided paired Wilcoxon test to
-within-trace three-seed mean group differences. Each arm has lower mismatch
-on all ten traces ($p=.0009765625$), and all three H1 nodes reject under the
-graphical allocation at family level $.05$: equal initial chain weights $1/3$ and Holm
-redistribution $1/2$ across the other chains. These are the individual
-one-sided p-values, not Holm-adjusted p-values.
-The prediction non-inferiority node H2 requires its one-sided
-Wilcoxon-inverted upper bound to be below $2\%$. The bounds
-$3.83/4.14/8.15\%$ do not meet that rule, so the gated superiority node H3
-is not tested. Separately, no member of the four-contrast secondary Holm
-family (M1/control, M2/control, floor/NoDesign, six-arm dose-response slope)
-is significant. All traces enter the primary analysis.
-Trace 32005's control/NoDesign cost recurs across five model seeds.
-Its registered exclusion is sensitivity only: the primary-contrast interval
-narrows to $[-2.32\%,+3.53\%]$ and remains inconclusive.
-Recorded diagnostic power at the $2\%$ margin is $.151$ with all traces.
+Registered floor/M1$\mu$/M2$\mu$ versus FedAvg chains use one-sided paired
+Wilcoxon tests of within-trace three-seed mean group differences (H1).
+All improve on all ten traces (individual $p=.0009765625$) and reject under
+family-level $.05$ graphical allocation (initial weights $1/3$, Holm
+redistribution $1/2$ to other chains). Prediction non-inferiority (H2)
+requires a Wilcoxon-inverted one-sided upper bound below $2\%$;
+$3.83/4.14/8.15\%$ fail, leaving superiority (H3) untested.
+The secondary Holm family (M1/control, M2/control, floor/NoDesign, six-arm
+dose-response slope) has no significant member.
+All traces enter the primary analysis. Trace 32005's control/NoDesign cost
+recurs across five model seeds; its sensitivity-only exclusion gives
+$[-2.32\%,+3.53\%]$, still inconclusive. All-trace diagnostic power at
+$2\%$ is $.151$.
 
 \section{Learning Capacity under a Separate Development Protocol}
 \label{app:learning_capacity}
 
-These measurements use chronological development validation splits and seeds
-41001--41003, rather than the test comparisons in the main paper.
-Central-delivered pools only delivered training observations.  Both backbones
-are evaluated over 200 effective data passes, with Adam learning rates
-$.0003,.001,.003$ and momentum-SGD rates $.001,.01,.03$, batch size 64, and a
-factor-.3 schedule after passes 50, 100, and 150.  Configurations and checkpoints
-are selected on validation.  HistoryResidual adds a 64/32 history network and a
-training-statistic residual reference to Common-NDMF.  The 108 central runs,
-one Traffic Uniform development run, and three U-Air Central-all diagnostics
-share this development protocol.
+Chronological development validation uses seeds 41001--41003, separately from
+the main test comparisons. Central-delivered pools delivered training observations.
+Both backbones run 200 effective passes with Adam rates $.0003,.001,.003$ or
+momentum-SGD rates $.001,.01,.03$, batch size 64, and factor-.3 decay after
+passes 50, 100, and 150; validation selects configurations/checkpoints.
+HistoryResidual adds a 64/32 history network and a training-statistic residual
+reference to Common-NDMF. This covers 108 central runs, one Traffic Uniform
+run, and three U-Air Central-all diagnostics.
 
 \begin{table*}[t]
 \centering
-\caption{Common-NDMF Central-delivered validation after the longer training
-budget (three development seeds; physical units). Gains are mean seed-paired
-relative improvements over the strongest applicable simple baseline.}
+\caption{Common-NDMF Central-delivered validation (three development seeds;
+physical units). Gains are mean seed-paired relative improvements over the
+strongest applicable simple baseline.}
 \label{tab:learning_capacity}
 \footnotesize
 \begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllrrr}
@@ -1847,52 +1841,45 @@
 \end{tabular*}
 \end{table*}
 
-\begin{figure*}[!b]
+\begin{figure*}[!tbp]
 \centering
 \includegraphics[width=\textwidth]{fig_learning_capacity_r2.png}
-\caption{Longer-budget development learning curves, with physical training
-RMSE above and deployment-weighted validation RMSE below. Lines are means and
-shading spans the three seeds. Dashed lines show the strongest applicable simple
-baseline mean. Per-seed best validation scores in
-Table~\ref{tab:learning_capacity} differ from the minimum of a mean curve.}
+\caption{Development learning curves: physical training RMSE (top) and
+deployment-weighted validation RMSE (bottom). Lines/shading give means/seed
+ranges ($n=3$); dashes give strongest-baseline means.
+Table~\ref{tab:learning_capacity} uses per-seed best checkpoints.}
 \label{fig:learning_capacity}
 \end{figure*}
 
-Training means, spatial means, seasonal means, persistence, and repeated-phase
-daily/weekly seasonal-naive predictors share the delivered-training information
-boundary.  Persistence uses the latest legal training observation; seasonal
-naive repeats the latest available phase without feeding validation labels back
-into history.  Weekly comparison requires at least two weeks of training
-observations.  Prediction is inverse-scaled and scored against float64 physical
-targets.  Traffic's target is traffic volume; the other two retain their
-controlled client-measurement definitions.
-
-Common-NDMF improves on the strongest simple reference for Traffic and
-SensorScope but not U-Air.  HistoryResidual gives $7.33\%$ on Traffic and
-$-0.34\%/-4.45\%$ on SensorScope/U-Air.  U-Air Central-all, with all training
-labels visible, averages $19.5427$ versus $18.4567$ for its spatial-mean
-reference.  This distinguishes backbone/generalization limits from delivery
-sparsity alone.  The single Traffic Uniform run reaches $253.1132$ vehicles/h
-($33.70\%$ improvement), but its best validation error still improves
-$0.914\%$ between passes 100 and 200.  The central runs plateau under the
-declared criterion, whereas this federated run does not.
-
-\section{Constraint Sensitivity of the Development Geometry}
+Training/spatial/seasonal means, persistence, and daily/weekly seasonal-naive
+predictors share delivered-training information. Persistence uses the latest
+legal observation; seasonal naive repeats the latest available phase, with
+weekly comparison requiring two training weeks. Validation labels never enter
+history. Predictions are inverse-scaled against float64 physical targets:
+Traffic volume and the other datasets' controlled client measurements.
+
+HistoryResidual gains are $7.33\%$ on Traffic and $-0.34\%/-4.45\%$ on
+SensorScope/U-Air. U-Air Central-all exposes all training labels yet averages
+$19.5427$ versus the spatial reference's $18.4567$, indicating limits beyond
+delivery sparsity. Traffic Uniform reaches $253.1132$
+vehicles/h ($33.70\%$ improvement), still improving $0.914\%$ from passes
+100 to 200; unlike the central runs, it has not plateaued under the stated criterion.
+
+\section{Development Geometry and Release Timing}
 \label{app:development_geometry}
 
-This separate development diagnostic uses first-cycle payloads and their
-recorded correction settings. For each natural window with at least eight
-clients, it takes the first eight in sorted order and renormalizes their
-reference. Centered composition rank and feasible group ranges distinguish
-weight freedom from mass adjustable by at least .01; they do not re-evaluate
-fixed-Design prediction performance.
+First-cycle development payloads retain their correction settings. Windows
+with at least eight clients use the first eight in sorted order and a
+renormalized reference. Centered composition rank and feasible group ranges
+separate weight freedom from mass adjustable by at least .01, without
+prediction re-evaluation.
 
 \begin{table}[t]
 \centering
-\caption{Traffic fixed-$K=8$ geometry on the same 183 subsets. $E$ is the
-minimum client ESS; cap bounds each weight. Repair is mean
+\caption{Traffic geometry on 183 fixed-$K=8$ subsets. $E$: minimum ESS;
+cap: maximum weight; repair: mean
 $\|\operatorname{Proj}_{\mathcal C}(\widehat\beta)-\widehat\beta\|_2$.
-Mean adjustable target mass is $4.651\%$ in every row.}
+Mean adjustable mass is $4.651\%$ throughout.}
 \label{tab:geometry_sensitivity}
 \footnotesize
 \setlength{\tabcolsep}{4pt}
@@ -1909,7 +1896,74 @@
 \end{tabular*}
 \end{table}
 
-No natural payload has $K=16$. Tighter caps increase infeasibility and
-projection distance while leaving .01-threshold adjustable mass unchanged.
-Client count alone therefore does not characterize adjustment capacity.
-No forecasts or label-dependent choices enter this audit.
+No natural payload has $K=16$; tighter caps increase infeasibility/projection
+distance, not .01-threshold adjustable mass. No forecasts or label-dependent
+choices enter this diagnostic.
+
+\subsection{Release-Timing Reference Study}
+\label{app:release_timing}
+
+This exploratory comparison uses Traffic TRAIN, one reused development seed
+(45001), and Common-NDMF with ClientTrainer. All policies share
+$T=100$, a $.1$ grid, fixed-time-1 warm-up through $t=20$, maximum window 4,
+version-age limit 5, and three clients for non-forced closure.
+Design is on and Gate is diagnostic. GAP20-fixed-reference (GAP20) branches
+from the common $t=20$ model, message pool and random streams for autonomous
+training and consumption. Local H\'ajek-SGD (one step) and server rates are $.01$.
+P2 uses group/reference coefficients $1/1$, variance/staleness coefficients
+$.1/.1$, cap $\max(.5,1/K)$, ESS minimum $\min(3,K)$,
+$d_{\max}=10$, $q_{\min}=.05$, variance floor $10^{-4}$, and maximum server
+rate 1. Observation stabilization uses $a_{\max}=20$, $p_{\min}=.05$, and
+$\pi_{\min}=10^{-6}$. Here $q=.5$ is a diagnostic prior, not a fitted
+consumption probability. Predictive accuracy is not evaluated.
+
+With actual P2 weights, $\ell_t=\tfrac12\|M_t\boldsymbol\alpha_t-\boldsymbol\mu\|_1$,
+$a_t$ is weighted version age divided by 5, and $c_t=\ell_t+.02a_t$.
+With opening time $o_t$ and $u_t=\operatorname{clip}((t-o_t)/4,0,1)$,
+\[
+\begin{aligned}
+B_t^{\mathrm{roll}}&=c_{L_t}-c_t+\kappa_{\mathrm{stop}}b_t+.20u_t,\\
+B_t^{\mathrm{fix}}&=c_{\mathrm{ref}}-c_t+.20u_t,
+\end{aligned}
+\]
+$b_t=\mathbf Q_t^\top(M_t\boldsymbol\alpha_t-\boldsymbol\mu)/
+(1+\|\mathbf Q_t\|_1)$. The rolling reference $c_{L_t}$ uses the last nonempty release's
+quality and age. The fixed reference $c_{\mathrm{ref}}=.9168365859958755$
+uses the $t=20$ release's $\ell=.9069767441860466$ and
+$a=.4929920904914447$. Saved releases do not re-age.
+Both rules close when $B_t\ge.02+10^{-7}$, subject to terminal, warm-up,
+deadline, and minimum-client priorities in that order.
+OF-no-Q-stop and GAP20 use $\kappa_{\mathrm{stop}}=0$; OF-v1 uses $.1$.
+All retain P2's $\mathbf Q$ and its updates.
+
+\begin{table}[t]
+\centering
+\caption{Traffic release-control diagnostics on one development seed
+($G$, $W$, and $J$: lower is better).}
+\label{tab:release_timing}
+\footnotesize
+\setlength{\tabcolsep}{3pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrr}
+\toprule
+Policy & $G$ & $W$ & $J$\\
+\midrule
+OF-v1 & .945218 & .601504 & .989880\\
+OF-no-Q-stop & .945218 & .601504 & .989880\\
+GAP20-fixed-reference & .919375 & .860215 & .974163\\
+Fixed time 0.5 & .958859 & .506329 & .997309\\
+Fixed time 2 & .843083 & 2.000000 & .949308\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+Table~\ref{tab:release_timing} gives $G$, the last nonempty release's
+$\ell$ averaged over 800 grids (20.1--100). $W$ is mean positive post-20 window
+duration including empty/terminal closures. Auxiliary $J$ averages
+$\ell+.02a+.20\,\mathrm{duration}/4$ over nonempty post-20 releases.
+$W$ is logical window time, not wall or registration-to-consumption time.
+Fixed-reference shadows change 129/799 original-trajectory actions
+(16.1452\%), all rolling CLOSE to fixed WAIT: 129/582 free states (22.1649\%).
+Rolling minus fixed reference averages $.0395584$ (median $.0405236$),
+usually relaxing release. Autonomous OF-no-Q-stop reduces
+$W$ by $30.0752\%$ but raises $G$ by $.0258430$ versus GAP20. Neither
+dominates both metrics. OF-v1 and OF-no-Q-stop share metrics and closure sequences on this seed.
```

## supplemental.tex

```diff
--- supplemental.tex (before this task)
+++ supplemental.tex (canonical)
@@ -84,27 +84,6 @@
 
 \input{appendix}
 
-% Trained-rule probe deferred from the results section of the main paper.  It is
-% placed after \input{appendix} so that the appendix keeps its own section
-% numbering, and it adds no numbered statement, so the counters set above stay
-% valid for the appendix.
-\section{Projection-with-Debt Sensitivity}
-\label{app:trained_rule_probe}
-
-\subsection{The $\kappa=1000$ projection-with-debt rule}
-\label{app:kappa_probe}
-
-The independent projection-with-debt rule uses $\kappa=1000$, selected on
-tuning seeds.  Relative to projection, it improves group alignment by
-$1.347/.580$ pp on SensorScope/U-Air (Holm $\approx10^{-5}$), unlike the
-frozen-strength $.0073$ pp SensorScope effect inside the practical band.
-The independent projection comparison gives maximum structural endpoint
-discrepancy $\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units
-across 240 runs, or $.00121$ pp.  It is 17\% of the small frozen-strength
-debt effect and $.13\%/ .16\%$ of the independent Design/projection contrasts.
-This endpoint discrepancy is not an optimizer certificate; the existing
-point-level optimality checks do not all pass.
-
 % Each PDF has its own bibliography. xr imports cross-references without bibcite.
 \bibliographystyle{IEEEtran}
 \bibliography{reference}
```
