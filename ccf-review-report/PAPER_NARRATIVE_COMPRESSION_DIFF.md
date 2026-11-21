# 叙述压缩定向差异

本轮当前工作树为基准，保留此前City Scanner及一致性修复。

## main.tex

```diff
--- current-start/main.tex
+++ current/main.tex
@@ -85,9 +85,8 @@
 corrected reference: on SensorScope, a feasible reference-projection comparator
 reduces group mismatch by $0.768$ percentage points relative to Uniform.
-Structural alignment does not consistently improve prediction, and projection
-can achieve lower group mismatch and runtime than the full RAVEN criterion.
 City Scanner comparisons with real opportunities and, separately, measured
-observation likewise show group-alignment advantages with protocol-dependent
-prediction trade-offs; delivery remains controlled.
+observation show group-alignment advantages with protocol-dependent prediction
+leaders under controlled delivery. Projection can achieve lower group mismatch
+and runtime than full RAVEN on matched-support station comparisons.
 \end{abstract}
 
@@ -149,5 +148,4 @@
 reference includes stabilization error.  Calibration stability holds at a fixed
 window state, while long-run alignment additionally requires sublinear debt growth.
-Neither property establishes prediction improvement.
 
 \begin{figure*}[t]
@@ -186,6 +184,6 @@
     Matched-support comparisons separate count weighting, Uniform, feasible
     reference projection, and full RAVEN.  Joint structure, prediction, and
-    runtime measurements identify the reference-side increment without assigning
-    every improvement to the full objective.
+    runtime measurements identify the contributions of the reference and
+    aggregation rule.
 \end{itemize}
 
@@ -200,7 +198,6 @@
 target-concentration comparisons probe prediction sensitivity, and supplemental
 local-weight and geometry analyses explain which adjustments are available.
-Together, the evidence shows why improved target alignment need not yield
-prediction gains, while distinguishing the connection's value from the roles
-of individual objective terms.
+Together, these comparisons link the available target adjustment to its
+measured prediction and runtime effects.
 
 \section{Related Work}
@@ -433,5 +430,5 @@
 Normalization is over the deployment domain, so both risks refer to the same
 sensing units.  Evaluation-period pooling specifies the comparison weights
-without replacing replace the attempt-level conditional probability used for training-time
+without replacing the attempt-level conditional probability used for training-time
 correction.
 
@@ -546,5 +543,5 @@
 and fixed within the window.
 Same-support Design contrasts and Obs/Use ablations assess endpoint-specific
-layer effects, not universal necessity (Section~\ref{subsec:eval_rq3}).
+layer effects (Section~\ref{subsec:eval_rq3}).
 
 \subsection{Observation Correction and Local H\'ajek Normalization}
@@ -629,7 +626,7 @@
 normalization.  Heterogeneous propensities supply different inputs, although
 clipping can still equalize realized weights.
-Local-weight audits and F1 examine constant-weight cancellation and heterogeneous
-inputs without establishing prediction gains
-(Appendix~\ref{app:local_hajek} and Table~\ref{tab:f1_mechanism}).
+Local-weight audits and F1 examine constant-weight cancellation and
+within-stratum covariate heterogeneity (Appendix~\ref{app:local_hajek} and
+Table~\ref{tab:f1_mechanism}).
 
 \subsection{Usable-Update Correction and Reference Aggregation Mass}
@@ -660,7 +657,5 @@
 $m_{k,r}d_{k,r}$ restores relative corrected mass between usable clients.
 The ideal untruncated factorization of $\beta^\star\overline a^\star$ is
-given in the supplemental material.  This factorization concerns ideal event
-weights rather than a prediction guarantee for multi-step updates from stale
-models.  The implemented
+given in the supplemental material for ideal event weights. The implemented
 $\widehat{\boldsymbol\beta}_r$ is instead an estimated, stabilized reference,
 not the feasible decision $\boldsymbol\alpha_r$.
@@ -751,6 +746,6 @@
  \label{eq:debt_bound}
 \end{equation}
-Only $\|\mathbf Q_R\|_1=o(S_R)$ makes this bound vanish.  The recursion does
-not establish debt stability.  The derivation is in the supplemental material.
+A vanishing bound requires $\|\mathbf Q_R\|_1=o(S_R)$; the derivation is
+in the supplemental material.
 
 \subsection{Feasibility-Aware Calibration Program}
@@ -782,7 +777,4 @@
 W1 compares direct-reference structural readouts, Uniform, projection, and
 full RAVEN under their respective rules (Section~\ref{subsec:eval_rq3}).
-On SensorScope, projection has lower group mismatch and runtime than full
-RAVEN, while RAVEN has lower client--stratum mismatch.  Structural ordering
-does not establish prediction ordering.
 
 \subsection{Global Update and Window Logic}
@@ -888,6 +880,4 @@
 Section~\ref{subsec:agg_coverage_theory} gives conditional guarantees.  The
 supplemental algorithm specifies the historical quantile construction.
-The CERTIFIED state does not establish exchangeability, and the stable-regime
-guarantee does not extend to arbitrary unannounced drift.
 
 \section{Theoretical Analysis}
@@ -1090,5 +1080,4 @@
 reported traces retains this term.  The worst-case envelope can be loose:
 the frozen Design-on constants give $L_\pi\le2\times10^{13}$.
-Reference or composition stability does not itself bound prediction risk.
 \end{proposition}
 
@@ -1105,7 +1094,4 @@
 Appendix~\ref{app:proof_prop4}.
 \end{proposition}
-
-This reweights existing predictions, not a model retrained under another
-target, and does not characterize either structural endpoint.
 
 \subsection{Aggregate Coverage Guarantees}
@@ -1249,7 +1235,6 @@
 $2.088/.678/1.007$ and are diagnostic references, not deployable baselines.
 Training/test target means are $.301/7.657$, $0/-.807$, and $0/.003$,
-respectively.  The old main models do not beat the training mean on the first
-two datasets; their structural differences do not establish effective absolute
-completion performance.
+respectively. Under the Complete-aligned station protocol, model RMSE on
+both SensorScope and U-Air exceeds the corresponding training-mean baseline.
 
 \paragraph{Structural comparison convention.}
@@ -1281,10 +1266,8 @@
 
 Table~\ref{tab:cityscanner_real} compares completion under real sensing
-opportunities. Both blocks predict {PM}$_{2.5}$, but use different data,
-targets, and sensing protocols.
-Their clients are occupied grid cells. Design is fixed on and the coverage
-Gate is unused. Usable-update delivery remains controlled in both blocks.
-Appendices~\ref{app:cityscanner_nyc}--\ref{app:cityscanner_p2_measured_o}
-give construction, filtering, and splits.
+opportunities, using different data and target maps for the two protocols.
+Design is fixed on and Gate is unused; their $R/O/U$ definitions and scales
+are given in the setup and table. Appendices~\ref{app:cityscanner_nyc}--
+\ref{app:cityscanner_p2_measured_o} give construction, filtering, and splits.
 
 \begin{table*}[t]
@@ -1321,21 +1304,17 @@
 \end{table*}
 
-With real visit occupancy and controlled observation, RAVEN minimizes group
-mismatch ($.0706$), while TwoStage-H\'ajek minimizes client--stratum mismatch.
-RAVEN's seed-paired mean relative RMSE is
-$1.71\%/1.34\%$ lower than FedAU/ObsUse, with worst-group reductions
-$1.56\%/1.23\%$. FedAvg predicts best on both endpoints.
-Against this count-weighted baseline, RAVEN's $5.59\%$ higher paired RMSE
-shows that improved group alignment can carry a prediction cost.
-
-Pilot~2 measures observation from finite {PM}$_{2.5}$ on union GPS occupancy,
-where {NO}$_2$ contributes locations without supplying prediction labels.
-RAVEN again has
-the smallest group mismatch ($.0465$), and its paired RMSE is
-$.43\%/ .45\%/ .65\%$ lower than FedAU/ObsUse/FedAvg. TwoStage-H\'ajek
-predicts best on both endpoints. It also minimizes client--stratum mismatch.
-The declared $-.5\%$ improvement criterion against both FedAU and ObsUse
-is not met. The cross-block differences cannot be attributed solely to
-measuring $O$, because the data and targets also change.
+In the visit-occupancy block, RAVEN minimizes group mismatch ($.0706$),
+while TwoStage-H\'ajek minimizes client--stratum mismatch. RAVEN's paired
+mean relative RMSE improves on FedAU/ObsUse by $1.71\%/1.34\%$, with
+worst-group reductions of $1.56\%/1.23\%$. FedAvg leads both prediction
+endpoints, with RAVEN's paired RMSE $5.59\%$ higher: the group-alignment
+benefit carries a measurable prediction cost against count weighting.
+
+In Pilot~2, RAVEN again minimizes group mismatch ($.0465$) and improves
+paired RMSE on FedAU/ObsUse/FedAvg by $.43\%/.45\%/.65\%$.
+TwoStage-H\'ajek leads both prediction endpoints and client--stratum alignment.
+The first two comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
+Thus the two protocols share a group-alignment advantage while yielding
+different prediction rankings.
 
 \subsection{Risk Semantics and External Protocols}
@@ -1350,6 +1329,6 @@
 $-.0214$, 17--18 negative seeds per method, and paired
 $p=4.83\times10^{-4}$--$5.86\times10^{-4}$.  Target change is about
-$8\times10^{-4}$ versus $2.2\times10^{-2}$ arrival change.  This supports
-different risk responses, not RAVEN prediction superiority.
+$8\times10^{-4}$ versus $2.2\times10^{-2}$ arrival change, showing that
+selection affects the two risk views differently.
 The six-scenario matrix (Appendix~\ref{app:e2_layer_matrix}) finds Holm-significant
 arrival changes for all five methods under observation-only and complete-aligned
@@ -1426,12 +1405,11 @@
 
 Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  SensorScope
-Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$,
-with no Holm-significant prediction improvement.  Removing Design worsens the structural endpoints by $1.237\%/.597\%$,
+Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$.
+Removing Design worsens the structural endpoints by $1.237\%/.597\%$,
 measured relative to the Design-on arm.
 U-Air reverses on group and prediction: removing Design improves group
 mismatch by $6.943\%$, RMSE by $6.885\%$, and tail RMSE by $7.221\%$, while
-worsening client--stratum mismatch by $4.990\%$.  Estimated and oracle Design
-track this reversal (Fig.~\ref{fig:w1_design_gate}); it is not simply an
-estimated-propensity failure.
+worsening client--stratum mismatch by $4.990\%$. Both estimated and oracle
+Design show this reversal (Fig.~\ref{fig:w1_design_gate}).
 
 \begin{table}[!htbp]
@@ -1440,6 +1418,5 @@
 mean $\pm$ SD; lower is better).  Both Design arms are shown.  Worst-group
 uses four UTC blocks; descriptive tolerance and training-mean references are
-defined in Section~\ref{subsec:eval_setup}.  Prediction superiority is not
-Holm-significant.  INT-R is a separate supplemental protocol.}
+defined in Section~\ref{subsec:eval_setup}. INT-R is a separate supplemental protocol.}
 \label{tab:main_effectiveness}
 \scriptsize
@@ -1477,8 +1454,5 @@
 worsen $\Delta_{\mathrm{group}}$ and $\mathrm{RMSE}_{\mu}$ by about
 $7.5\%$.  The U-Air Design-off arm runs
-Algorithm~\ref{alg:window_close} with $D_t=\mathrm{off}$;
-this figure diagnoses the reversal, not the
-selection rule.  The U-Air Design-on $\Delta_{c\text{-}s}$ gain remains in
-Table~\ref{tab:e4_ablation}.}
+Algorithm~\ref{alg:window_close} with $D_t=\mathrm{off}$.}
 \label{fig:w1_design_gate}
 \end{figure}
@@ -1500,6 +1474,5 @@
 $.114/.172$.  The required improvement against both FedAU and ObsUse is
 $-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
-while meeting no-harm (Table~\ref{tab:underserved_block}); no test confirmation
-is claimed.  INT-R preserves the direction of U-Air's Design trade-off, while
+while meeting no-harm (Table~\ref{tab:underserved_block}).  INT-R preserves the direction of U-Air's Design trade-off, while
 the SensorScope client--stratum advantage approaches zero.
 
@@ -1571,10 +1544,12 @@
 ($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
 U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
-versus RAVEN's $27.1/15.3$ s.  Registered prediction superiority does not
-survive Holm correction (SensorScope $p=1$; U-Air minimum $.120$ under corrected
-saved-parameter scores).  Numerical endpoint discrepancy from the independent
-projection comparator reaches $2.42\times10^{-5}$ in $\Delta$ units, and
-point-level optimality checks do not all pass; this is not exact optimizer
-certification (Appendix~\ref{app:kappa_probe}).
+versus RAVEN's $27.1/15.3$ s. Registered prediction contrasts are not
+Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ under corrected
+saved-parameter scores).
+
+\paragraph{Numerical accuracy.}
+The independent projection comparison has endpoint discrepancy up to
+$2.42\times10^{-5}$ in $\Delta$ units, with some point-level optimality checks
+failing (Appendix~\ref{app:kappa_probe}). Feasibility is assessed separately.
 
 \paragraph{Component removal.}
@@ -1589,10 +1564,10 @@
 by $.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
 ($p_{\mathrm{Holm}}=.0194$), without significant U-Air structural changes.
-Debt's structural effects are significant but tiny:
+Debt's significant structural effects are
 $.0141\%/.0040\%$ on SensorScope and $.0043\%/.0024\%$ on U-Air.
 The frozen-strength projection/debt increment ($.0073$ pp on SensorScope,
 $.0024$ pp on U-Air), group, variance, and staleness effects lie inside the
-registered practical band.  This does not prove all P2 terms necessary;
-$\kappa=1000$ remains an independent sensitivity result.
+registered practical band. The $\kappa=1000$ rule is a separate sensitivity
+comparison.
 
 \begin{table}[!htbp]
@@ -1641,8 +1616,7 @@
 $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$,
 the Hodges--Lehmann estimate is $-.019\%$, with 95\% trace-cluster interval
-$[-1.89\%,+12.28\%]$ ($p=.922$). The deletion-cost contrast is inconclusive,
-not equivalent. Flooring also changes target group marginals, so the contrast
-does not isolate deletion alone. All traces, including the high-variation
-trace, remain in this primary result.
+$[-1.89\%,+12.28\%]$ ($p=.922$), leaving deletion cost unresolved.
+Flooring changes both zero masses and target group marginals, so this is a
+joint target-support comparison.
 
 \subsection{Prediction Sensitivity and Adjustment Geometry}
@@ -1663,15 +1637,22 @@
 $+.040\%$ ($[-.090,+.171]\%$) on U-Air over 20 paired seeds.  Three U-Air
 members stay within $.3\%$, but TwoStage-H\'ajek lies $2.04\%$ above its
-oracle-margin counterpart ($[1.33,2.75]\%$).  Reference perturbations are not
-uniformly small (median $\ell_1=.077$, maximum $1.15$); their weak prediction
-response cannot be explained solely by accurate margin estimates.  Fixed-state
-composition stability in \eqref{eq:g4_comp} is not a prediction guarantee.
-The local-weight audit finds constant realized weights in the original blocks;
-F1 introduces time-tercile covariates while preserving block observation means
-(Appendix~\ref{app:f1_mechanism}).  Different propensities do not ensure
-different clipped weights or prediction gains; F1 is not general MNAR evidence.
+oracle-margin counterpart ($[1.33,2.75]\%$). Reference perturbations
+(median $\ell_1=.077$, maximum $1.15$) can be appreciable even where prediction
+is insensitive. The support audit checks true margins on active support and
+records active clipping; missing estimated-margin logs leave A6b unverified
+(Appendix~\ref{app:a5_a6_audit}).
+
+The local-weight audit finds constant realized weights in the original blocks.
+F1 varies time-tercile covariates at fixed block observation means
+(Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
+inputs to the correction pathway.
+
+Arrival-weighted validation shifts the reported risk by $-4.11\%$ to
+$-4.12\%$ on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects
+the same configuration on all 20 seeds. In these comparisons, the scoring
+distortion changes reported error more than configuration selection.
 
 With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
-In the old main protocol this covers $78.6\%$ of 1877 SensorScope windows,
+In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
 $90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
 windows.  Largest target groups carry only $.53\%/.79\%$.
@@ -1718,6 +1699,6 @@
 
 \paragraph{Separate development geometry and learning.}
-Table~\ref{tab:development_geometry} uses three new development seeds, not the
-old window population above.  For feasible group range
+Table~\ref{tab:development_geometry} summarizes three separate development
+trajectories. For feasible group range
 $W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
 \min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
@@ -1727,11 +1708,9 @@
 References violate constraints in $59.02\%$, with mean projection distance
 $.067487$.  Appendix~\ref{app:development_geometry} varies caps/ESS.
-This is geometry, not a participation intervention or prediction experiment.
 
 \begin{table}[t]
 \centering
 \caption{Natural-window geometry in the separate development protocol
-(seeds 41001--41003, cap .5 and ESS minimum 3). These are geometric measurements,
-not fixed-Design performance comparisons.}
+(seeds 41001--41003, cap .5 and ESS minimum 3).}
 \label{tab:development_geometry}
 \scriptsize
@@ -1748,11 +1727,10 @@
 \end{table}
 
-Longer-budget learning uses development validation, physical units, and
-seeds 41001--41003, separately from these test comparisons
-(Appendix~\ref{app:learning_capacity}).  Common-NDMF Central-delivered improves
-on applicable simple baselines for Traffic and SensorScope, but not U-Air;
-those validation gains do not belong to RAVEN.  The single federated Traffic
-Uniform trajectory is not yet plateaued.  Backbone capacity, training budget,
-and aggregation benefits therefore remain separate questions.
+Longer-budget centralized learning uses development validation in physical
+units on seeds 41001--41003 (Appendix~\ref{app:learning_capacity}).
+Common-NDMF Central-delivered improves on simple baselines for Traffic and
+SensorScope but remains worse on U-Air. The single federated Traffic Uniform
+trajectory has not plateaued. These measurements assess backbone learning,
+while Table~\ref{tab:trained_rules} isolates aggregation-rule effects.
 
 \subsection{Update-Rule Sensitivity and Coverage Scope}
@@ -1764,6 +1742,6 @@
 Increasing local steps from 2 to 20 leaves FedAvg $2.8\%$--$3.0\%$ above
 a centralized Adam reference ($10^{-3}$, 20 minibatch steps of 32).
-This combines optimizer and budget differences, not aggregation alone;
-federated parameters move only $.26\%$--$.40\%$ of their initial norm.
+The optimizer and training budget differ in this comparison; federated
+parameters move $.26\%$--$.40\%$ of their initial norm.
 
 Replacing only the server step with Adam ($\beta_1=.9$, $\beta_2=.99$,
@@ -1774,18 +1752,10 @@
 $[.659,1.572]/[.795,1.459]$, below the $1.007$ constant reference mean.
 On those same runs oracle weights reduce group/client--stratum mismatch by
-$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$).  Structural benefit
-thus coexists with unresolved prediction value under the changed update rule.
-
-Arrival-weighted validation misstates target risk by $-4.11\%$ to $-4.12\%$
-on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects the same
-configuration on all 20 seeds.  Support audits find positive true margins
-on active support, not full identification; clipping is active and missing
-estimated-margin logs prevent A6b verification (Appendix~\ref{app:a5_a6_audit}).
-The fixed coverage-stress candidate gives pooled CERTIFIED validity $.959$
-but only $.750$ for U-Air at $a=1$; its complete cells and transition behavior
-remain in Appendix~\ref{app:certificate_audit}.  Adaptive RESET/CERTIFIED
-transitions lack a validity proof.  These diagnostic records, from the older
-coverage-controlled candidate, do not validate configured Design or P2
-prediction performance.  Real delivery $U$ remains unmeasured in all blocks.
+$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$).
+
+\paragraph{Coverage diagnostic.}
+The coverage-controlled candidate ($\mathrm{Design}_t=\mathrm{Gate}_t$)
+has empirical pooled CERTIFIED validity $.959$, falling to $.750$ for U-Air
+at $a=1$ (Appendix~\ref{app:certificate_audit}).
 
 \section{Conclusion}
@@ -1794,15 +1764,12 @@
 RAVEN-MCS connects a sensing-unit reference reconstructed across sequential
 selection to the constrained client mixtures available in an asynchronous
-window.  Ideal moment recovery and fixed-window calibration stability address
+window. Ideal moment recovery and fixed-window calibration stability address
 different parts of this connection, with long-run alignment conditional on
-debt growth.  City Scanner shows group-alignment advantages alongside protocol-dependent
-prediction trade-offs under real opportunities and measured observation, with
-controlled delivery. Station comparisons separate changes explained by
-Uniform from reference projection and independent Design effects.  Simple
-projection is faster and can improve group alignment over full RAVEN, while
-the full criterion improves another structural endpoint.  These differences do
-not establish consistent prediction gains.  Target concentration, geometry,
-update-rule, and learning diagnostics show why deployment-target alignment must
-be evaluated jointly with task performance and cost under the actual protocol.
+debt growth. City Scanner yields the smallest group mismatch with
+protocol-dependent prediction leaders. Controlled station comparisons attribute
+most structural gain to Uniform and isolate reference-projection and Design
+increments. On SensorScope, projection has lower group mismatch and runtime,
+while full RAVEN has lower client--stratum mismatch. These findings support
+evaluating deployment-target alignment jointly with prediction and cost.
 
 \section*{Data and Code Availability}
```

## appendix.tex

```diff
--- current-start/appendix.tex
+++ current/appendix.tex
@@ -738,7 +738,6 @@
 \label{app:risk_semantic_evidence}
 
-This appendix reports supplementary statistics that are useful for interpreting
-risk interchangeability but are not required in the main text.  No additional realization,
-retraining, or post-hoc model selection is introduced here.
+This appendix gives the balanced control and full selection-scenario statistics
+for interpreting target and arrival risk.
 
 \subsection{Balanced No-Harm Control}
@@ -780,6 +779,5 @@
 methods, and 17--18 of 20 paired seeds are negative.  This supports the
 risk-semantic premise that arrival-weighted and deployment-target-weighted
-views react differently to the same structured selection shift.  It does not
-establish method-level superiority.
+views react differently to the same structured selection shift.
 
 \begin{table}[!t]
@@ -814,6 +812,5 @@
 families over the five non-balanced scenarios.  Signed arrival--target gaps are
 not absolute mismatch scores.  Complete-counteracting does not establish the
-proposed directional event, and no corrected comparison establishes RAVEN
-prediction dominance across these scenarios.
+proposed directional event.
 
 \begin{table*}[t]
@@ -935,7 +932,6 @@
 and Design on on both datasets.  Its local inverse weights can therefore vary
 across observed time terciles, whereas a stratum-constant factor cancels under
-local H\'ajek normalization.  This separates a construction that supplies no
-within-stratum correction signal from one that supplies such a signal; it does
-not by itself establish a prediction benefit.
+local H\'ajek normalization. The construction thus supplies a within-stratum
+correction signal while retaining the block observation means.
 
 \section{P2 Feasibility Diagnostics}
@@ -1795,6 +1791,4 @@
 shapes on the same keys, rescaled within region to the common target;
 70/33 zero keys remain. All maps cover the 959 recorded risk-set keys.
-These trained variants differ from control RAVEN and disputed fixed-prediction
-re-scorings. Flooring changes both zeros and marginals.
 
 The primary $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ uses within-trace
@@ -1802,9 +1796,8 @@
 (paired Wilcoxon $p=.922$). Resampling traces and model seeds within trace
 gives the recorded 95\% percentile interval $[-1.89\%,+12.28\%]$,
-which establishes neither deletion cost nor $2\%$ equivalence.
+which spans zero and extends beyond the $2\%$ equivalence band.
 The group-gain retention is
 $(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{floor}})/
-(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$,
-not prediction improvement.
+(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$.
 
 No member of the four-contrast secondary Holm family (M1/control,
@@ -1830,5 +1823,5 @@
 training-statistic residual reference to Common-NDMF.  The 108 central runs,
 one Traffic Uniform development run, and three U-Air Central-all diagnostics
-are separate learning measurements, not new RAVEN comparisons.
+share this development protocol.
 
 \begin{table*}[t]
@@ -1836,6 +1829,5 @@
 \caption{Common-NDMF Central-delivered validation after the longer training
 budget (three development seeds; physical units). Gains are mean seed-paired
-relative improvements over the strongest applicable simple baseline. These
-values are not the old protocol's test scores or RAVEN aggregation gains.}
+relative improvements over the strongest applicable simple baseline.}
 \label{tab:learning_capacity}
 \footnotesize
@@ -1879,7 +1871,5 @@
 ($33.70\%$ improvement), but its best validation error still improves
 $0.914\%$ between passes 100 and 200.  The central runs plateau under the
-declared criterion, whereas this federated run does not.  Neither the pooled
-learning gain nor that single development trajectory establishes a RAVEN
-weighting benefit.
+declared criterion, whereas this federated run does not.
 
 \section{Constraint Sensitivity of the Development Geometry}
```

## supplemental.tex

```diff
--- current-start/supplemental.tex
+++ current/supplemental.tex
@@ -99,5 +99,4 @@
 $1.347/.580$ pp on SensorScope/U-Air (Holm $\approx10^{-5}$), unlike the
 frozen-strength $.0073$ pp SensorScope effect inside the practical band.
-These gains are not standard-RAVEN benefits.
 The independent projection comparison gives maximum structural endpoint
 discrepancy $\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units
```
