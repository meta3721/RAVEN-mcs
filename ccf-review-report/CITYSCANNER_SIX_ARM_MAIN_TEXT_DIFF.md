# City Scanner六臂正文提升差异

当前工作树为本轮基准，未恢复旧稿。

## main.tex

```diff
--- task-start/main.tex
+++ current/main.tex
@@ -78,6 +78,6 @@
 pre-outcome selection histories. We establish ideal target-moment recovery
 under support and identification assumptions and calibration stability at a
-fixed window state. In two City Scanner protocols, full RAVEN achieves the
-lowest mean group mismatch among reported methods, $25.8\%$ and $23.3\%$
+fixed window state. In two primary City Scanner comparisons, full RAVEN achieves the
+lowest mean group mismatch among the five methods in each, $25.8\%$ and $23.3\%$
 below TwoStage-H\'ajek, the best group comparator in each. Both use real
 opportunities and controlled delivery; one measures observation. Matched-support
@@ -182,6 +182,6 @@
 
     \item \textbf{Application-level group alignment and mechanism attribution.}
-    Full RAVEN attains the lowest mean group mismatch among reported methods
-    in both City Scanner protocols. Joint structure, prediction, and runtime
+    Full RAVEN attains the lowest mean group mismatch among the five methods
+    in each primary City Scanner comparison. Joint structure, prediction, and runtime
     comparisons distinguish this application advantage from count-to-Uniform
     effects and the reference-side increment. Geometry diagnostics separate
@@ -190,6 +190,6 @@
 
 City Scanner provides the principal application evidence: full RAVEN has the
-lowest mean group mismatch in both the visit-occupancy and measured-observation
-protocols (Table~\ref{tab:cityscanner_real}), with different prediction leaders.
+lowest mean group mismatch within each five-method visit-occupancy and
+measured-observation comparison (Table~\ref{tab:cityscanner_real}), with different prediction leaders.
 Controlled station comparisons (Tables~\ref{tab:main_effectiveness}
 and~\ref{tab:trained_rules}) identify the underlying reference and calibration
@@ -198,7 +198,8 @@
 contrast gives $0.922$ pp. These effects are not additive. Uniform's share of
 the count-to-RAVEN gain separates the change in counting weights from the
-reference increment. Six selection scenarios establish the risk distinction,
-while geometry and positive-mass target variants examine how finite support
-shapes the observed group-alignment advantage.
+reference increment. Six selection scenarios establish the risk distinction.
+Target-support variants also lower group mismatch versus FedAvg on all ten
+paired traces (Table~\ref{tab:cityscanner_sixarm}); geometry characterizes
+the finite support available for adjustment.
 
 \section{Related Work}
@@ -1332,4 +1333,56 @@
 The shared application advantage is group composition alignment, with
 protocol-dependent prediction rankings.
+
+\paragraph{Target-support variants.}
+\label{subsec:cityscanner_target_support}
+Table~\ref{tab:cityscanner_sixarm} tests whether group-alignment gains persist
+across target support and client--stratum shapes on ten shared visit-occupancy
+traces, each with three model seeds. Floor fills the control map's zero masses
+and renormalizes. M1$\mu$/M2$\mu$ use ACS population/NYC~311 shapes on the
+same control keys, rescaled within region to the public $\boldsymbol\mu$.
+These are trained target-map variants; Appendix~\ref{app:cityscanner_sixarm}
+gives their construction and statistical details.
+
+\begin{table*}[t]
+\centering
+\caption{City Scanner visit-occupancy target-map variants (mean $\pm$ SD
+over ten trace means, three model seeds per trace; a different aggregation
+level from Table~\ref{tab:cityscanner_real}). Predictions use common region
+weights and the training-standardized scale. $\rho$ is the percentage of
+non-test delivered units assigned zero mass (zero for Design off). Group gaps
+share the public region target; bold marks each endpoint minimum.}
+\label{tab:cityscanner_sixarm}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}
+\toprule
+Method / target map & $\rho$ (\%) & $\Delta_{\mathrm{group}}\downarrow$ &
+$\mathrm{RMSE}_{\mu}\downarrow$ & WorstGroupRMSE $\downarrow$\\
+\midrule
+FedAvg / count & 0.00 & $0.1953{\pm}0.0342$ & $\mathbf{0.2409}{\pm}0.0832$ & $\mathbf{0.2529}{\pm}0.0903$\\
+RAVEN-NoDesign & 0.00 & $0.0736{\pm}0.0264$ & $0.2439{\pm}0.0835$ & $0.2575{\pm}0.0905$\\
+RAVEN-control & 14.35 & $0.0706{\pm}0.0266$ & $0.2561{\pm}0.1031$ & $0.2695{\pm}0.1095$\\
+RAVEN-floor & 0.00 & $\mathbf{0.0682}{\pm}0.0313$ & $0.2442{\pm}0.0842$ & $0.2576{\pm}0.0908$\\
+RAVEN-M1$\mu$ & 1.01 & $0.0771{\pm}0.0338$ & $0.2467{\pm}0.0889$ & $0.2609{\pm}0.0971$\\
+RAVEN-M2$\mu$ & 0.98 & $0.0813{\pm}0.0301$ & $0.2508{\pm}0.0907$ & $0.2661{\pm}0.1003$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+Floor, M1$\mu$, and M2$\mu$ each reduce group mismatch versus FedAvg on
+all ten paired traces and pass the three registered structural comparisons
+under the graphical multiplicity allocation (one-sided paired Wilcoxon,
+each $p=9.77\times10^{-4}$). Floor retains $101.9\%$ of the FedAvg-to-control
+group gain. The gains therefore remain observable in these support/shape
+variants; NoDesign also has lower group mismatch than M1$\mu$/M2$\mu$.
+
+Prediction non-inferiority at $2\%$ is not established for floor/M1$\mu$/M2$\mu$
+versus FedAvg: one-sided 95\% upper bounds are $3.83/4.14/8.15\%$,
+so prediction superiority is not tested. Separately, the primary trace-level
+ratio $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$
+has Hodges--Lehmann estimate $-.019\%$, 95\% percentile trace-cluster interval
+$[-1.89\%,+12.28\%]$, and $p=.922$. Deletion cost remains unresolved;
+floor changes group marginals as well as zero masses. The separate four-contrast
+secondary family has no Holm-significant member. Arm-specific client--stratum
+gaps are reported in Table~\ref{tab:cityscanner_sixarm_cs}.
 
 \subsection{Risk Semantics and External Protocols}
@@ -1632,16 +1685,4 @@
 U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
 
-\paragraph{City Scanner target support.}
-A separate six-arm experiment uses ten visit-occupancy traces, each with three
-model seeds (Appendix~\ref{app:cityscanner_sixarm}). Replacing zero control-map
-masses with a positive floor retains $101.9\%$ of the FedAvg-to-control
-group-alignment gain. The group advantage remains in this specific
-positive-mass target variant. For the trace-level ratio
-$\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$,
-the Hodges--Lehmann estimate is $-.019\%$, with 95\% trace-cluster interval
-$[-1.89\%,+12.28\%]$ ($p=.922$), leaving deletion cost unresolved.
-Flooring changes both zero masses and target group marginals, so this is a
-joint target-support comparison.
-
 \subsection{Prediction Sensitivity and Adjustment Geometry}
 \label{subsec:ceiling}
@@ -1792,9 +1833,10 @@
 separates ideal moment recovery and fixed-window stability from long-run
 alignment, which depends on sublinear debt growth. Full RAVEN attains the lowest
-mean group mismatch among reported methods in both City Scanner protocols.
+mean group mismatch among the five methods in each primary City Scanner
+comparison.
 Same-support contrasts separate count-to-Uniform effects, reference correction,
-and feasible projection. The positive-mass
-target variant retains group-alignment gains, while geometry distinguishes
-available weight directions from adjustable target mass. Prediction leaders
+and feasible projection. The tested target-support variants also improve group alignment over count
+weighting, while geometry distinguishes available weight directions from
+adjustable target mass. Prediction leaders
 vary by protocol. On SensorScope, full RAVEN improves client--stratum alignment
 over projection at higher group mismatch and runtime.
```

## appendix.tex

```diff
--- task-start/appendix.tex
+++ current/appendix.tex
@@ -1758,27 +1758,25 @@
 reports mean and SD over ten within-trace model-seed means.
 
-\begin{table*}[t]
-\centering
-\caption{Six-arm City Scanner comparison (ten traces, three model seeds per
-trace; mean $\pm$ SD across trace means). Prediction uses common region weights
-and the training-standardized scale. $\rho$: percentage of non-test delivered
-units assigned zero mass (zero for Design off). Group gaps share a region
-target; client--stratum gaps use arm-specific maps and cannot rank alignment
-to a common target. Lower errors are better.}
-\label{tab:cityscanner_sixarm}
+\begin{table}[t]
+\centering
+\caption{Supplementary client--stratum gaps for the six trained target-map
+variants in Table~\ref{tab:cityscanner_sixarm} (mean $\pm$ SD over ten trace
+means of three model seeds). Each gap uses its arm's own target map;
+these values do not rank alignment to a common client--stratum target.}
+\label{tab:cityscanner_sixarm_cs}
 \footnotesize
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lccccc@{}}
-\toprule
-Arm & $\rho$ (\%) & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
-\midrule
-\texttt{fedavg\_window} & 0.00 & $0.2409{\pm}0.0832$ & $0.2529{\pm}0.0903$ & $0.1953{\pm}0.0342$ & $0.8123{\pm}0.0191$\\
-\texttt{raven\_wo\_design} & 0.00 & $0.2439{\pm}0.0835$ & $0.2575{\pm}0.0905$ & $0.0736{\pm}0.0264$ & $0.7880{\pm}0.0254$\\
-\texttt{raven\_ctrl} & 14.35 & $0.2561{\pm}0.1031$ & $0.2695{\pm}0.1095$ & $0.0706{\pm}0.0266$ & $0.5676{\pm}0.0311$\\
-\texttt{raven\_ctrl\_floor} & 0.00 & $0.2442{\pm}0.0842$ & $0.2576{\pm}0.0908$ & $0.0682{\pm}0.0313$ & $0.7892{\pm}0.0235$\\
-\texttt{raven\_M1mu} & 1.01 & $0.2467{\pm}0.0889$ & $0.2609{\pm}0.0971$ & $0.0771{\pm}0.0338$ & $1.4060{\pm}0.0168$\\
-\texttt{raven\_M2mu} & 0.98 & $0.2508{\pm}0.0907$ & $0.2661{\pm}0.1003$ & $0.0813{\pm}0.0301$ & $1.4348{\pm}0.0147$\\
-\bottomrule
-\end{tabular*}
-\end{table*}
+\begin{tabular}{lr}
+\toprule
+Method / target map & $\Delta_{c\text{-}s}$\\
+\midrule
+FedAvg / count & $0.8123{\pm}0.0191$\\
+RAVEN-NoDesign & $0.7880{\pm}0.0254$\\
+RAVEN-control & $0.5676{\pm}0.0311$\\
+RAVEN-floor & $0.7892{\pm}0.0235$\\
+RAVEN-M1$\mu$ & $1.4060{\pm}0.0168$\\
+RAVEN-M2$\mu$ & $1.4348{\pm}0.0147$\\
+\bottomrule
+\end{tabular}
+\end{table}
 
 \texttt{fedavg\_window} uses count weights and \texttt{raven\_wo\_design}
@@ -1800,9 +1798,17 @@
 (\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$.
 
-No member of the four-contrast secondary Holm family (M1/control,
-M2/control, floor/NoDesign, six-arm dose-response slope) is significant.
-The separate floor/M1/M2 versus FedAvg non-inferiority chains miss the
-$2\%$ margin: one-sided 95\% upper bounds are $3.83/4.14/8.15\%$,
-so superiority is not tested. All traces enter the primary analysis.
+The three registered chains compare floor, M1$\mu$, and M2$\mu$ with FedAvg.
+Their structure node H1 applies a one-sided paired Wilcoxon test to
+within-trace three-seed mean group differences. Each arm has lower mismatch
+on all ten traces ($p=.0009765625$), and all three H1 nodes reject under the
+graphical allocation at family level $.05$: equal initial chain weights $1/3$ and Holm
+redistribution $1/2$ across the other chains. These are the individual
+one-sided p-values, not Holm-adjusted p-values.
+The prediction non-inferiority node H2 requires its one-sided
+Wilcoxon-inverted upper bound to be below $2\%$. The bounds
+$3.83/4.14/8.15\%$ do not meet that rule, so the gated superiority node H3
+is not tested. Separately, no member of the four-contrast secondary Holm
+family (M1/control, M2/control, floor/NoDesign, six-arm dose-response slope)
+is significant. All traces enter the primary analysis.
 Trace 32005's control/NoDesign cost recurs across five model seeds.
 Its registered exclusion is sensitivity only: the primary-contrast interval
```

## supplemental.tex

```diff
--- task-start/supplemental.tex
+++ current/supplemental.tex
@@ -71,9 +71,9 @@
 
 % Continue figure/table/equation numbers from the companion main paper.
-% Main has 4 figures, 8 tables, 1 algorithm and 41 numbered equations.
+% Main has 4 figures, 9 tables, 1 algorithm and 41 numbered equations.
 % Offline support and retrospective switch equations are in Appendix J.
 % Numbered statements in main: four propositions, two theorems, one assumption.
 \setcounter{figure}{4}
-\setcounter{table}{8}
+\setcounter{table}{9}
 \setcounter{algorithm}{1}
 \setcounter{equation}{41}
```
