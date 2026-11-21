# 正文主张一致性修订定向差异

以本轮开始时工作树为基准；保留已有核心主张、结果和评分修复。

## main.tex

```diff
--- task-start/main.tex
+++ current/main.tex
@@ -132,5 +132,5 @@
 usable-update weights can also use the registered sensing state before
 usability is known.  Combined with a lagged opportunity ratio, these corrections
-reconstruct the target mass represented by delivered updates.  The reference
+form an estimated, stabilized target-mass reference for delivered updates.  The reference
 is not yet an executable allocation.  The server calibrates it on available
 clients under weight caps and minimum effective support.  The aggregation
@@ -150,14 +150,15 @@
 \centering
 \includegraphics[width=\textwidth]{fig1_raven_problem_framework.pdf}
-\caption{RAVEN-MCS aligns asynchronous federated completion with a public
-deployment target.  (a)~Three selection layers induce an arrival law that
+\caption{RAVEN-MCS constructs a deployment-target reference and calibrates it
+on finite-window support.  (a)~Three selection layers induce an arrival law that
 need not match the deployment target.
 (b)~RAVEN-Design forms a selection-corrected target-mass reference and
-calibrates it in the current feasible support.  RAVEN-NoDesign uses
-$\widehat\zeta=1$ and is not target-mass reconstruction.
+calibrates it in the current feasible support.  RAVEN-NoDesign sets
+$\widehat\zeta=1$ to omit opportunity-to-target correction;
+observation/usability correction and calibration remain.
 The Design setting is fixed before the window opens and held throughout it;
 the coverage Gate is a separate diagnostic.
-(P2) is the per-window calibration program that maps this reference onto the
-feasible aggregation set; it is defined in Section~\ref{sec:calibration}.}
+The per-window program (P2) maps this reference onto the feasible aggregation
+set (Section~\ref{sec:calibration}).}
 \label{fig:raven_overview}
 \end{figure*}
@@ -368,6 +369,6 @@
 allocation.  The compatible client--atomic measure distributes the same target
 mass among clients, while its stratum marginal pools units for opportunity
-correction.  Consistency across these levels lets corrected client masses
-represent the deployment groups used for evaluation.
+correction.  Consistency across these levels specifies the deployment target
+for corrected client-mass estimates.
 The construction in Appendix~\ref{app:deferred_constructions} uses public
 client shares and conditional atomic target masses, all frozen before
@@ -496,6 +497,6 @@
 \label{sec:reconstruction}
 
-RAVEN connects sensing-unit correction to a window's client reference using
-sequential IPW and H\'ajek normalization.  Local weights determine training
+RAVEN constructs an estimated, stabilized window reference from sensing-unit
+correction using sequential IPW and H\'ajek normalization.  Local weights determine training
 within clients, while corrected masses determine their relative server reference.
 
@@ -622,6 +623,6 @@
  \label{eq:normalized_update}
 \end{equation}
-The displacement divides out the local learning rate and step count, preserving
-the server update scale.  Constant within-client correction cancels during
+This divides out the explicit local learning-rate and step-count factors;
+the training path still determines the displacement.  Constant within-client correction cancels during
 normalization.  Heterogeneous propensities supply different inputs, although
 clipping can still equalize realized weights.
@@ -655,5 +656,6 @@
 \end{equation}
 Local H\'ajek normalization removes the client's total scale from training.
-$m_{k,r}d_{k,r}$ restores relative corrected mass between usable clients.
+$m_{k,r}d_{k,r}$ includes that mass scale and usable-update correction in
+the relative server reference.
 The ideal untruncated factorization of $\beta^\star\overline a^\star$ is
 given in the supplemental material for ideal event weights. The implemented
@@ -663,6 +665,4 @@
 $\boldsymbol\mu$ when current support is incomplete.  Section~\ref{sec:calibration}
 maps the reference to executable aggregation weights.
-W1 compares direct-reference structural readouts, Uniform, projection, and
-RAVEN to assess this calibration step (Section~\ref{subsec:eval_rq3}).
 
 \subsection{Information Boundary and Stabilization}
@@ -775,6 +775,6 @@
 establishes uniqueness under its stated conditions, separately from numerical
 solver accuracy.
-W1 compares direct-reference structural readouts, Uniform, projection, and
-full RAVEN under their respective rules (Section~\ref{subsec:eval_rq3}).
+Same-support comparisons of direct-reference structural readouts, Uniform,
+projection, and full RAVEN assess this step (Section~\ref{subsec:eval_rq3}).
 
 \subsection{Global Update and Window Logic}
@@ -843,5 +843,5 @@
 \end{algorithm}
 
-\subsection{Finite-Sample Aggregate Coverage Certificate}
+\subsection{Aggregate Opportunity-Coverage Diagnostic}
 \label{subsec:agg_certificate_alg}
 \label{subsec:agg_coverage_object}
@@ -1095,5 +1095,5 @@
 \end{proposition}
 
-\subsection{Aggregate Coverage Guarantees}
+\subsection{Stable-Regime Aggregate Coverage Bound}
 \label{subsec:agg_coverage_theory}
 \label{subsec:pairwise_barrier}
@@ -1133,6 +1133,7 @@
 \label{sec:evaluation}
 
-We test the target--arrival distinction, attribute structural changes to
-aggregation mechanisms, and assess their prediction and deployment consequences.
+We evaluate application-level group alignment, attribute same-support structural
+changes to reference and calibration mechanisms, and examine prediction,
+runtime, and finite-support diagnostics.
 
 \subsection{Experimental Setup}
@@ -1180,15 +1181,15 @@
 \midrule
 SensorScope~\cite{ingelrest2010sensorscope} & 55 & 10285/3465/3410 & 4 &
-station $\times$ block $\times$ day & 440 & main comparison; ablation\\
+station $\times$ block $\times$ day & 440 & controlled mechanisms (Design, ablation)\\
 U-Air~\cite{zheng2013uair} & 36 & 5688/1908/1908 & 4 &
-spatial ID $\times$ block $\times$ day & 288 & main comparison; ablation\\
+spatial ID $\times$ block $\times$ day & 288 & controlled mechanisms (Design, ablation)\\
 NSW-Traffic~\cite{tfnsw2024traffic} & 43 & 18576/6192/6192 & 4 &
-region $\times$ block $\times$ day & 32 & risk interchangeability; four-region protocol\\
+region $\times$ block $\times$ day & 32 & risk semantics; four-region comparison\\
 T-Drive~\cite{yuan2010tdrive} & 9994 cells & 285659/--/74569 & 4 &
 cell $\times$ block $\times$ day & -- & hybrid (real $R$)\\
 City Scanner~\cite{wang2023cityscanner} & 446 cells & 9343/3290/2090 & 4 &
-region $\times$ block $\times$ day & 32 & hybrid (real $R$)\\
-City Scanner P2 & 416 cells & 10141/2835/1984 & 4 &
-region $\times$ block $\times$ day & 32 & hybrid (meas.\ $O$)\\
+region $\times$ block $\times$ day & 32 & application; real $R$, controlled $O/U$\\
+City Scanner Pilot 2 & 416 cells & 10141/2835/1984 & 4 &
+region $\times$ block $\times$ day & 32 & application; real $R$, measured $O$, controlled $U$\\
 \bottomrule
 \end{tabular*}
@@ -1209,7 +1210,9 @@
 Paired methods share EventTraces and within-stratum exchangeability
 $\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.
-Design-on/off arms fix their setting throughout each run.  Principal comparisons
-use 20 paired seeds; the balanced control uses five, and T-Drive plus three
-supplemental rankings use ten.  Learning diagnostics use three development
+Design-on/off arms fix their setting throughout each run.  Controlled station
+comparisons use 20 paired seeds; each City Scanner five-method block and
+T-Drive use ten, and the balanced control uses five.  The six-arm target-map
+comparison uses ten traces with three model seeds each.  Other counts are
+specified per table.  Learning diagnostics use three development
 seeds and one Uniform trajectory.  Seeds represent model/trace randomness,
 not independent cities; no test result selects parameters, groups, or strata.
@@ -1223,8 +1226,13 @@
 where evaluation group mass is normalized on supported test units and $n_g$ is
 the group count.  SensorScope/U-Air use uniform atomic evaluation mass, hence
-pooled RMSE.  U-Air/Traffic use training scales $17.363/575.776$; their main
-RMSE entries are dimensionless, while SensorScope retains physical units.
-WorstGroupRMSE is the maximum of four UTC-block scores after within-block
-renormalization; Tail RMSE uses frozen blocks 2 and 3, not error-selected groups.
+pooled RMSE.  In the controlled station protocols, SensorScope retains physical
+units, while U-Air/Traffic use training scales $17.363/575.776$ and report
+dimensionless RMSE.  City Scanner uses each block's own training-only
+$z$-score scale (Table~\ref{tab:cityscanner_real}).  WorstGroupRMSE is the maximum
+score across the protocol's frozen groups, with scoring weights renormalized
+within each group.  SensorScope/U-Air and T-Drive use four UTC blocks;
+City Scanner and the NSW-Traffic four-region protocol use spatial groups,
+as specified in their captions and appendices.  In the station protocols
+reporting Tail RMSE, it uses frozen UTC blocks 2 and 3.
 Only the risk-semantic test replaces target weights by
 \eqref{eq:arrival_distribution} for $\mathrm{RMSE}_{\rho}$.
@@ -1255,6 +1263,6 @@
 trained-rule contrasts within dataset/endpoint, and four 20-seed worst-group
 contrasts against FedAU/ObsUse.  Differences below $10^{-12}$ are numerical
-ties.  Tables give mean $\pm$ SD; intervals use 10000 seed-paired percentile
-bootstrap draws at seed 20261002.  The descriptive $+.5\%$ worst-group tolerance
+ties.  Tables give mean $\pm$ SD; controlled station intervals use 10000
+seed-paired percentile bootstrap draws at seed 20261002.  The descriptive $+.5\%$ worst-group tolerance
 uses mean paired relative differences on TEST seeds 30011--30020 for ranking
 prose; Holm tests use all 20.  It is not a non-inferiority proof.
@@ -1380,5 +1388,6 @@
 (mean $\pm$ std, 10 seeds, $178$ windows).  Lower is better.
 $O$ and $U$ are Complete-aligned controls.
-RAVEN-NoDesign ($\widehat\zeta=1$) is not target-mass reconstruction.
+RAVEN-NoDesign ($\widehat\zeta=1$) omits opportunity-to-target correction,
+retaining observation/usability correction and calibration.
 WorstGroupRMSE is the maximum over UTC H1--H4.
 RAVEN-NoDesign is outside the descriptive $+0.5\%$ worst-group tolerance versus
@@ -1458,5 +1467,5 @@
 (20 seeds; positive $=$ Design worse).  On SensorScope, Design slightly
 reduces $\Delta_{\mathrm{group}}$ ($-1.23\%$ estimated, $-1.03\%$
-oracle) with a flat RMSE.  On U-Air, estimated and oracle Design both
+oracle) with little change in mean RMSE.  On U-Air, estimated and oracle Design both
 worsen $\Delta_{\mathrm{group}}$ and $\mathrm{RMSE}_{\mu}$ by about
 $7.5\%$.  The U-Air Design-off arm runs
@@ -1771,6 +1780,7 @@
 
 \paragraph{Coverage diagnostic.}
-The coverage-controlled candidate ($\mathrm{Design}_t=\mathrm{Gate}_t$)
-has empirical pooled CERTIFIED validity $.959$, falling to $.750$ for U-Air
+The separate coverage-controlled candidate couples $\mathrm{Design}_t=\mathrm{Gate}_t$,
+unlike pre-window configured Design in the main method.  Empirical pooled
+CERTIFIED validity for this candidate is $.959$, falling to $.750$ for U-Air
 at $a=1$ (Appendix~\ref{app:certificate_audit}).
 
```

## appendix.tex

```diff
--- task-start/appendix.tex
+++ current/appendix.tex
@@ -1003,8 +1003,7 @@
 $^\dagger$; the main inferential family consists of the deployable methods.
 
-The same-backbone family below is evaluated with Design on, on both
-blocks, so the U-Air panels diagnose that arm rather than the setting the
-deployment uses there.  Table~\ref{tab:main_effectiveness} reports both settings on both blocks: Design
-on for SensorScope and Design off for U-Air.
+The same-backbone family below uses Design on for both station blocks.
+Table~\ref{tab:main_effectiveness} separately reports both fixed Design settings
+on each dataset.
 
 \subsection{Windowed adaptations of FedAU, ObsUse, and TimeAlign}
```
