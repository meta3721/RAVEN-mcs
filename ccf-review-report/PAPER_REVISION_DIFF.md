# 本轮规范源文件差异记录

2026-10-16。基准为本轮开始时工作树文本，包含并保留用户原有未提交改动；不是对HEAD全部差异的归属认领。

## main.tex

```diff
--- before/main.tex
+++ current/main.tex
@@ -30,7 +30,7 @@
 %\usepackage{appendix}
 \usepackage{placeins}
 \usepackage{xr}
-\externaldocument{supplemental}
+\externaldocument[][nocite]{supplemental}
 \graphicspath{{./figures/}{./images/}}
 \hyphenation{op-tical net-works semi-conduc-tor IEEE-Xplore}
 
@@ -69,23 +69,26 @@
 
 
 \begin{abstract}
-Mobile crowdsensing completion learns from updates selected by opportunity,
-observation, and usable-update delivery.  These mechanisms shape an arrival law
-that can differ from the public deployment target.  RAVEN-MCS reconstructs a
-selection-corrected reference with a preconfigured opportunity Design factor
-from pre-outcome histories and calibrates it within
-the feasible aggregation set of each asynchronous window.  We distinguish
-deployment-target risk from arrival-weighted risk, establish ideal Design-on target-moment
-and group-mass recovery under support and identification conditions, and prove
-unique solvability and plug-in stability of the calibration program.  Paired
-component comparisons isolate the roles of correction and feasibility: on
-SensorScope, projecting the corrected reference improves group mismatch by
-$+0.768$ percentage points over uniform server weights, while the Design factor
-provides a further $+0.922$ points on the same active set.  Station-based protocol
-experiments and hybrid mobility replays characterize structural alignment and
-its relationship to deployment-weighted prediction error.  The resulting
-framework connects the population represented by usable observations to the
-client mixtures that a finite sensing window can realize.
+Mobile crowdsensing completion learns from data selected by opportunity,
+observation, and update delivery.  The resulting arrival distribution can differ
+from the deployment target, yet correcting that distribution does not make the
+target realizable by the clients in a finite window.  RAVEN-MCS connects these
+two problems: it reconstructs a selection-corrected reference over atomic sensing
+units from sequential pre-outcome histories, then calibrates the reference under
+window-specific support, client caps, and effective-support constraints.  The
+full criterion combines reference fidelity with group matching, uncertainty,
+staleness, and accumulated target debt.  We establish ideal target-moment recovery
+under support and identification assumptions and fixed-window calibration
+stability.  Paired experiments distinguish the gains already explained by uniform
+aggregation from the increment due to the corrected reference.  On SensorScope,
+reference projection reduces group mismatch by $0.768$ percentage points relative
+to Uniform; a separate same-support comparison of projected references with and
+without Design gives $0.922$ points.  These are distinct contrasts.  Joint
+structural, prediction, and runtime comparisons show that improved mass alignment
+does not consistently improve prediction, and that a simpler projection can
+outperform the full criterion on structure and cost.  The framework separates
+population reconstruction, finite-window realizability, and their measured
+consequences for completion.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -131,7 +134,9 @@
 partial, arbitrary, or biased client participation
 \cite{wang2022unified,jhunjhunwala2022fedvarp,wu2023anchor,wang2024lightweight,sun2025debiasing,mohri2019agnostic,chen2026fedcure,morishita2026who}.
 These directions establish that sparsity, asynchrony, and non-uniform
-participation matter, but they do not resolve the following MCS problem:
+participation matter.  Target-aware aggregation also studies population
+selection and target matching~\cite{morishita2026who,listozec2024overcoming}.
+The remaining MCS question is:
 \emph{how should one align asynchronous federated data completion with a
 deployment target when sensing-side availability and update-side usability
 jointly select the data that enter learning?}  Correcting only the final
@@ -174,80 +179,52 @@
 \label{fig:raven_overview}
 \end{figure*}
 
-Our main contributions are as follows.
+Our contributions follow the distinction between the population to be served,
+the population represented by selected data, and the mixtures available now.
 
 \begin{itemize}
-    \item \textbf{Deployment-target risk semantics under two-stage non-random
-    selection.}
-    We formulate asynchronous federated MCS completion as a
-    deployment-target alignment problem rather than an arrival-centered
-    learning problem.  The formulation distinguishes the atomic deployment law
-    from the law induced by mobile opportunity, observation, and usable-update
-    selection, and defines structural mismatch at both deployment-group and
-    client--opportunity-stratum levels.  We prove that when the deployment and
-    arrival laws differ, their induced risk functionals are not generally
-    interchangeable.  This distinction identifies the population risk represented
-    by selected observations and the deployment population the model serves.
-
-    \item \textbf{Selection-layer-aware target reconstruction.}
-    We develop an exposure-aware normalized reconstruction that keeps the
-    opportunity/design, observation, and usable-update mechanisms separate
-    instead of collapsing them into a single missingness probability, using only
-    legal pre-outcome information and local H\'ajek normalization to yield a
-    selection-corrected reference mass for aggregation.  Usable-update correction
-    supplies the third sequential factor.  Under
-    compatible target support, sequential pre-outcome
-    ignorability, and correct ideal selection ratios, the ideal pooled normalized
-    sequential estimator with the target-mass opportunity ratio recovers
-    compatible target moments or target-group mass.  Clipping controls the
-    finite-sample bias--variance trade-off of the practical estimator.  That
-    reconstruction is RAVEN-Design, the setting that turns the Design factor on;
-    with the factor off, RAVEN-NoDesign fixes the opportunity factor at one.
-    The factor is an explicit
-    configuration that the deployment fixes before the window opens and holds
-    throughout it.  Both settings are reported; \eqref{eq:design_gate}
-    describes a block-level target-support check.  A finite-sample coverage bound is audited as an
-    empirical diagnostic in the supplemental material.
-
-    \item \textbf{Feasibility-aware instantaneous and long-term target
-    calibration.}
-    We show that statistically reconstructed target mass and instantaneous
-    mobile realizability are different problems.  RAVEN-MCS therefore calibrates
-    the corrected reference inside the current feasible aggregation set while
-    accounting for target mismatch, reference fidelity, uncertainty, and
-    staleness, and carries unresolved group under-service through a long-term
-    target-debt process.  The program has a nonempty compact convex
-    feasible set and a unique global minimizer under the stated conditions, and
-    when the active set is held fixed with compatible target support the
-    implemented RAVEN-Design clipped plug-in is a Lipschitz perturbation of the
-    same-window ideal reference that the calibration program does not amplify in
-    $\boldsymbol\alpha$, per \eqref{eq:g4_alpha}.
-
-    \item \textbf{Component attribution relative to uniform aggregation.}
-    We separate the published FedAvg-to-RAVEN structural difference, per dataset
-    over 20 paired seeds, into the part that uniform server weights already close
-    and the part that the corrected reference closes: $68.96\%$ versus $31.04\%$
-    of a $2.09$ pp group gap on SensorScope, and $83.07\%$ versus $16.93\%$ of
-    $1.47$ pp on U-Air.  Structural improvements are therefore quoted relative to
-    uniform weights.  The projected reference
-    $\mathrm{Proj}_{\mathcal{C}_r}(\widehat{\boldsymbol\beta}_r)$ carries the
-    reference-side part.  On SensorScope, the Design factor additionally provides
-    a practically significant same-active-set improvement:
-    $\mathrm{B1}(\textsc{raven})-\mathrm{B1}(\text{no }\zeta)=+0.922$ pp
-    ($[0.721,1.141]$, stable across seed halves), outside the $\pm0.10$ band in
-    closable-gap units (Section~\ref{subsec:eval_rq2}).
+    \item \textbf{Sensing-unit target formulation and information interfaces.}
+    We distinguish a public atomic deployment measure, the arrival law induced
+    by sequential $R/O/U$ selection, and the current feasible composition.
+    Separate pre-outcome histories specify which information can identify each
+    selection layer.  The formulation connects deployment-group and
+    client--stratum masses and provides the risk and support objects used by
+    both reconstruction and evaluation.  Six controlled selection scenarios and
+    real-opportunity replays examine these distinctions.
+
+    \item \textbf{Selection-corrected reference with finite-window calibration.}
+    We connect local H\'ajek correction and usable-update mass reconstruction to
+    a server reference, then calibrate that reference on the available clients
+    under caps and effective-support constraints.  RAVEN retains its full (P2)
+    criterion and target-debt state.  Ideal pooled reconstruction identifies
+    target moments under A1--A3; the practical clipped reference carries a
+    stabilization error, and the calibration map is non-expansive in the
+    reference only at a fixed window state.  Long-run alignment additionally
+    requires sublinear debt.  The opportunity Design factor is configured before
+    window opening; the coverage Gate supplies a separate diagnostic.
+
+    \item \textbf{Attribution of structural alignment and prediction effects.}
+    Over 20 paired seeds, Uniform explains $68.96\%$ of the matched
+    FedAvg-to-RAVEN group-gap reduction on SensorScope and $83.07\%$ on U-Air.
+    We compare the remaining increment using direct references, feasible
+    projection, and full RAVEN, with prediction and runtime reported alongside
+    structure.  The SensorScope projection--Uniform contrast is $0.768$ pp;
+    the independent projected Design-on/off contrast is $0.922$ pp.
+    Concentrated-target, within-stratum selection, geometric, and learning
+    diagnostics explain which mechanisms are exercised and why structural
+    improvements need not yield prediction gains.
 \end{itemize}
 
-The empirical structural claim is the projected reference, together with the
-Design configuration.  Inverse-probability weighting, H\'ajek normalization, and
-a convex match to a known target composition are prior ingredients.  What this
-setting adds is deployment-target semantics over sensing units, legal
-pre-outcome histories for the three selection layers, and the finite-window
-feasible set.
+Inverse-probability weighting, H\'ajek normalization, target calibration, ESS,
+and strong-convexity arguments are established tools.  The specific connection
+studied here is between a sensing-unit reference reconstructed across sequential
+selection layers and a changing window's constrained client mixture.  The
+experiments distinguish the value of that connection from the contribution of
+each term in the full criterion.
 
 We evaluate these contributions with a no-harm control, a risk-semantic block,
 and a SensorScope/U-Air development table under always-on protocol $R$ on station
-traces (Table~\ref{tab:main_effectiveness}).  Independent hybrid ceilings, namely
+traces (Table~\ref{tab:main_effectiveness}).  Independent hybrid comparisons, namely
 a T-Drive taxi replay under real $R$ with controlled $O$ and $U$, an NSW-Traffic
 four-region protocol table, and the City Scanner {PM}$_{2.5}$ and Pilot~2 tables
 of the supplemental material, provide separate evaluations of their respective
@@ -297,18 +274,23 @@
 client mixture \cite{mohri2019agnostic}; and FedProx and SCAFFOLD address client
 drift \cite{li2020fedprox,karimireddy2020scaffold}.  These methods correct
 participation, while RAVEN-MCS additionally separates sensing-side opportunity
-and observation from update-side usability.  FedIPW~\cite{morishita2026who} is
-closest in the two-stage FL vocabulary, but its factorization of enrollment and
-round-level participation stays on the client roster: it does not factor MCS
-opportunity or observation of sensing units, and the aligned object is not a
-public deployment measure over $h(i)$.  It is cited as the nearest
-enrollment--participation IPW, not as an MCS completion baseline.
-FLOSS~\cite{goetze2025floss} reweights aggregation for client
-opt-out and stragglers.  FedPALS~\cite{listozec2024overcoming} aggregates toward
-a known target label distribution by a convex combination of client models.
-Projecting the corrected reference onto $\mathcal{C}_r$ is that same matching
-step applied to a deployment-group composition rather than to labels, and
-Section~\ref{subsec:eval_rq2} evaluates this deployment-group projection directly.
+and observation from update-side usability.
+FLOSS~\cite{goetze2025floss} reweights aggregation for client opt-out and stragglers.
+
+FedIPW~\cite{morishita2026who} factors client enrollment and round participation,
+and its limited-information extension calibrates enrolled clients to known
+population summaries.  Thus sequential IPW and population calibration are
+already available at the client level.  RAVEN instead links selections of atomic
+sensing units to a reference for the usable clients in each window, with distinct
+pre-observation and pre-delivery histories.
+FedPALS~\cite{listozec2024overcoming} matches a known target label distribution
+by convex aggregation and regularizes inverse sample-level ESS; it also treats
+targets outside the client convex hull.  RAVEN's reference projection acts in
+client-weight space, while its group term acts in composition space, with hard
+window-specific caps and client-level ESS constraints.  These operations are
+related calibration constructions, not identical projections.  Cross-window
+debt records residual group under-service.  The supplemental mechanism comparison
+distinguishes these information requirements and guarantee scopes.
 Classical survey estimators supply the H\'ajek building blocks
 \cite{horvitz1952generalization,hajek1971comment,shimodaira2000covariate,robins1994estimation},
 and importance weighting can lose effect in over-parameterized networks
@@ -639,9 +621,11 @@
 
 RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization) first forms a
 selection-corrected reference for the mass the usable data represent.
-Opportunity, observation, and usable-update selection are kept separate
-because they have different conditioning sets and therefore cannot be
-replaced by a single generic missingness probability.
+Opportunity, observation, and usable-update selection have different
+conditioning histories.  Their probabilities can be multiplied into a joint
+inclusion probability by the chain rule; retaining the factors specifies when
+their covariates and outcomes become available and permits layer-specific
+estimation and diagnosis.
 
 \subsection{Opportunity/Design Correction}
 \label{subsec:design_correction}
@@ -926,7 +910,9 @@
  \label{eq:debt_bound}
 \end{equation}
 The full derivation is in the target-debt accounting proof of the supplemental
-material.
+material.  Vanishing long-run mismatch follows if
+$\|\mathbf Q_R\|_1=o(S_R)$; the recursion alone does not establish that growth
+condition.
 
 \subsection{Feasibility-Aware Calibration Program}
 \label{subsec:P2}
@@ -950,21 +936,18 @@
 \end{align}
 The debt term prioritizes accumulated under-served groups; the group,
 reference, variance, and staleness terms are coordinated terms of one
-program.  Over the $3279$ active windows of these two datasets the range of
-$\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ over $\mathcal{C}_r$ has median
-$10^{-13}$, so the $\ell_1$ surface is flat, its minimizer over $\mathcal{C}_r$
-not unique, and the group term only selects among the solutions equivalent in
-$\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$.  The reason is support: a window's
-active clients reach only a few of the target's $220$ or $144$ groups, so the
-group objective is flat across the feasible set and on its own cannot move the
-window's group distribution toward $\boldsymbol\mu$.  The endpoint moves only
-through the tie-break among those equivalent points, and that is what the
-reference anchor supplies: the tie-broken per-window rule gains $0.0107$ pp of
-group mass over uniform weights ($1.05140$ against $1.06213$, per-seed maximum
-$0.0337$).  The constraint is thus the load-bearing part of (P2), and the group
-objective alone is not.  The flatness is measured on these two datasets, at the
-frozen configuration; where a window's active clients do cover the target's
-groups, the group term regains its effect.
+program.  The reference anchor penalizes departures from the reconstructed
+client mass, while the group term penalizes departures of the resulting
+composition from the deployment target.  These are different distances:
+projection of $\widehat{\boldsymbol\beta}_r$ in client-weight space minimizes
+$\|\boldsymbol\alpha-\widehat{\boldsymbol\beta}_r\|_2^2$, whereas group matching
+minimizes $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_2^2$.
+Over the $3279$ audited active windows, the feasible range of the evaluation
+quantity $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ has median $10^{-13}$.
+This describes the $\ell_1$ evaluation geometry, not constancy of the squared
+$\ell_2$ term in (P2).  Limited group support can restrict observable alignment
+even when feasible weights differ; the rule comparisons in
+Section~\ref{subsec:eval_rq3} measure the consequences of the separate terms.
 $\widehat{\boldsymbol\beta}_r$ is the selection-corrected reference;
 $\boldsymbol\alpha_r$ is the feasible aggregation decision.
 
@@ -1141,8 +1124,8 @@
 $1/p^{\mathrm{obs}}$: \eqref{eq:a_stabilized} already carries
 $\widehat\zeta^{o}$, so bounding $1/p^{\mathrm{obs}}$ alone leaves it
 unbounded.
-A6a is exactly what makes the map return the ideal untruncated ratios, and
-hence what makes \eqref{eq:eps_stab} vanish.
+A6a ensures that the map returns the ideal untruncated ratios and is sufficient
+for the stabilization error in \eqref{eq:eps_stab} to vanish.
 
 \noindent\textbf{A6b (Bounded interpolation error).}
 On A5's active support the pre-outcome estimates satisfy
@@ -1278,7 +1261,7 @@
 \bigl\|\boldsymbol\beta_r^{\mathcal T}-\boldsymbol\beta_r^\star\bigr\|_1 .
 \label{eq:eps_stab}
 \end{equation}
-It vanishes exactly when $\mathcal{T}$ reproduces the ideal ratios on the
+It vanishes when the stabilized and ideal normalized references coincide on the
 active support, and it depends only on the true margins, $\pi^{\mathrm{tar}}$
 and the frozen constants, so it is measurable on a released trace.  Let
 $n_r=\max_{k\in\mathcal{A}_r}\sum_i R_{k,r,i}O_{k,r,i}$ and
@@ -1318,7 +1301,7 @@
 $C_1=(2K_rn_r/B_{\min})(d_{\max}\max\{L_\pi,L_p\}+a_{\max}L_q)$; under Design
 off $\zeta\equiv1$, so $L_\pi=0$ and $L_p=1/p_{\min}^2$.  This stability bound
 compares references on shared target support with a fixed active set.
-It holds with or without A6a, which is exactly what drives
+It holds with or without A6a, which is sufficient to set
 $\varepsilon_{\mathrm{stab},r}$ to zero.
 \end{proposition}
 
@@ -1563,8 +1546,11 @@
 decision.  The support-compatible mixture-target diagnostic on SensorScope
 exceeds the no-harm threshold; the comparison table uses the specified
 deployment target.
-All experiments use 20 paired seeds except the balanced control (five) and four ten-seed tables (the T-Drive
-ranking here, three in the supplement).  Those seeds capture algorithmic and EventTrace randomness, not independent
+The principal comparison blocks use 20 paired seeds except the balanced control
+(five) and four ten-seed tables (the T-Drive ranking here, three in the
+supplement).  The separate learning diagnostics use three development seeds and
+one Uniform trajectory, as specified in Appendix~\ref{app:learning_capacity}.
+Those seeds capture algorithmic and EventTrace randomness, not independent
 cities.  No test result tunes the selection process, parameters, groups, or strata.
 
 \subsubsection{Metrics and statistical policy}
@@ -1669,6 +1655,16 @@
 here because the risk-semantic experiment reports the five methods used in that test.}
 \label{fig:risk_noninterchangeability}
 \end{figure}
+
+The six-scenario matrix separates the selection layers.  Relative to the
+balanced control, observation-only selection changes arrival RMSE for all five
+methods after the existing Holm correction, but changes target RMSE for none.
+Complete-aligned selection changes arrival RMSE for five methods and target
+RMSE for two.  Opportunity-only, usable-only, and complete-counteracting shifts
+have no Holm-significant target-RMSE contrast in this matrix.  The full ranges
+and counts in Appendix~\ref{app:e2_layer_matrix} show why the layers must be
+measured separately: compounding or cancellation is a property of a particular
+selection construction, not a universal direction of target-risk change.
 
 \noindent\textbf{Risk-interchangeability finding.}
 Under two-stage non-random selection, the arrival law need not be an
@@ -1772,7 +1768,8 @@
 $\Delta_{\mathrm{group}}$/$\Delta_{c\text{-}s}$ from FedAvg's $1.0558/1.2903$ to
 $1.0139/1.2644$ ($3.96\%/2.01\%$); the Design-off row gives $1.0265/1.2719$, so
 the two settings differ by $1.237\%$ and $0.597\%$ (paired, 20 seeds) while
-their $\mathrm{RMSE}_{\mu}$ is indistinguishable ($7.9380$ versus $7.9384$).
+their $\mathrm{RMSE}_{\mu}$ point estimates are $7.9380$ and $7.9384$, with
+no Holm-significant prediction contrast.
 Four-block worst-group RMSE stays within the descriptive $+0.5\%$ worst-group
 tolerance versus FedAU-Window and
 ObsUse-Window (TEST $-0.01\%$ and $+0.05\%$; ALL20 $+0.02\%$ and $+0.10\%$).
@@ -1802,13 +1799,13 @@
 
 Local-H\'ajek coincides with FedAvg-Window wherever the two keep the same active
 set, because the realized within-client H\'ajek weights are uniform on these
-traces; on U-Air the sealed-family RAVEN bars are Design-on, not the
+traces; on U-Air the corresponding RAVEN bars are Design-on, not the
 RAVEN-NoDesign rows of Table~\ref{tab:main_effectiveness}.
 
 \noindent\textbf{Where the structural gain comes from.}
-The RAVEN rows of Table~\ref{tab:main_effectiveness} sit next to count-weighted
-FedAvg-Window, and on a common ruler most of that difference is not the
-correction.  Writing the FedAvg group gap as
+The matched-support rule comparison in Table~\ref{tab:trained_rules} separates
+count weighting from selection correction.  On its common ruler, writing the
+count-weighted FedAvg group gap as
 $\Delta_{\mathrm{FedAvg}}-\Delta_{\mathrm{RAVEN}}
 =(\Delta_{\mathrm{FedAvg}}-\Delta_{\mathrm{unif}})
 +(\Delta_{\mathrm{unif}}-\Delta_{\mathrm{RAVEN}})$, it is $2.09$ pp of target
@@ -1820,15 +1817,15 @@
 SensorScope ($77.58\%$ and $74.58\%$ count-to-uniform), while their U-Air active
 sets differ from the reference ruler and admit no decomposition.
 
-The projected reference carries the reference-side part, and the design factor is
-the only further ingredient both necessary and practically significant.
+The projected reference accounts for the main reference-side increment in these
+comparisons.  The Design contrast is assessed separately on matched support.
 Replacing uniform weights by
 $\mathrm{Proj}_{\mathcal{C}_r}(\widehat{\boldsymbol\beta}_r)$ is worth $+0.768$ pp
 ($[0.563,0.970]$) on SensorScope, above the $0.5$ pp practical line and stable
 across the two seed halves, and $+0.286$ pp ($[0.098,0.471]$) on U-Air, below
 that line and unstable across the halves ($+0.170$ tune, $+0.402$ report).
-Imposing $\mathcal{C}_r$ and projecting onto it is what turns the reconstruction
-into alignment: against the uncorrected reference, which violates the recorded
+Imposing $\mathcal{C}_r$ changes how the reconstruction is realized: against the
+unprojected corrected reference, which violates the recorded
 feasibility constraints and is worse than uniform weights,
 the projection is worth $+1.188$ pp ($[0.956,1.409]$) on SensorScope and
 $+1.399$ pp ($[1.019,1.782]$) on U-Air.  Removing the design factor costs
@@ -1845,8 +1842,7 @@
 ($[+0.013,+0.063]$) in the closable-gap units of
 Section~\ref{subsec:equivalence_band}, is well inside the $\pm0.10$ band, and
 the variance and staleness terms move that group endpoint by at most $0.008$ in
-the same units.  They are retained as the
-definition of the criterion.  The reference anchor gives the unique minimizer,
+the same units.  The reference anchor gives the unique minimizer,
 and debt accounts for accumulated group under-service through the one-sided
 bound \eqref{eq:debt_bound}.  The anchor term is
 what makes the problem strictly convex, so the flat $\ell_1$ surface of
@@ -2069,8 +2065,8 @@
 $\Delta_{c\text{-}s}$ by $0.310\%$ (significant) while the group change is not
 significant after Holm correction, and on U-Air the structural changes are not
 significant while removing Inst worsens $\mathrm{RMSE}_{\mu}$ and tail RMSE by
-$0.143\%$ and $0.149\%$ (both $p_{\mathrm{Holm}}=0.0194$).  Debt has the
-narrowest but most consistent role: removing it significantly increases both
+$0.143\%$ and $0.149\%$ (both $p_{\mathrm{Holm}}=0.0194$).  Removing debt
+significantly increases both
 structural mismatches on both datasets, but only by $0.0141\%/0.0040\%$ on
 SensorScope and $0.0043\%/0.0024\%$ on U-Air, far below the descriptive
 $+0.5\%$ worst-group tolerance that governs the external comparisons of
@@ -2078,53 +2074,105 @@
 accounting of \eqref{eq:debt_bound}; its long-run alignment implication is
 conditional on $\|\mathbf Q_R\|_1=o(S_R)$.
 
-\noindent\textbf{Server-weight rules trained under the same policy.}
-Retraining the same window policy while changing only the server weights
-separates structural movement from prediction.  With 20 paired seeds per dataset
-the group endpoint orders the same way on both datasets, with the
-projection-with-debt rule lowest, then the projection alone, frozen RAVEN and
-instantaneous calibration, uniform weights, and count-weighted FedAvg: $0.98464$,
-$1.01158$, $1.01394$, $1.01409$, $1.02693$, and $1.05577$ on SensorScope, and
-$1.08001$, $1.09162$, $1.09236$, $1.09241$, $1.09734$, and $1.12176$ on U-Air.
-Paired within each dataset, the projection improves on uniform weights by
-$+0.768$ pp ($p_{\mathrm{Holm}}=2.7\times10^{-5}$) on SensorScope, the value
-Section~\ref{subsec:eval_rq2} also gives, and by $+0.286$ pp ($0.0166$) on U-Air.
-The projection-with-debt variant uses $\kappa=1000$, selected on tuning seeds.
-Its numerical approximation error and endpoint deltas are in
-Section~\ref{app:kappa_probe} of the supplemental material.
-Frozen RAVEN trails the projection by $0.118$ pp on SensorScope ($0.019$) and is
-indistinguishable from it on U-Air.  These projection rules are new rules of
-this study with their own specified objectives.  Their measured runtime is
-$18.5$--$20.0$~s against $27.1$~s on SensorScope.  No prediction-endpoint
-contrast survives Holm correction on either dataset (SensorScope
-$p_{\mathrm{Holm}}=1.000$ throughout; U-Air best raw $p=0.027$,
-$p_{\mathrm{Holm}}=0.133$), and the arm order on $\mathrm{RMSE}_{\mu}$ does not
-follow the structural order, which is what the ceiling measurement of
-Section~\ref{subsec:ceiling} anticipates.
+\noindent\textbf{Server-weight rules trained under matched support.}
+Table~\ref{tab:trained_rules} places structure, prediction, and cost on one
+comparison population.  All rules retain the Design-on correction pathway and
+the active clients of the full RAVEN arm.  Count weighting is proportional to
+observed counts on that matched support; Uniform uses $1/K_r$; projection uses
+$\arg\min_{\alpha\in\mathcal C_r}\|\alpha-\widehat\beta_r\|_2^2$.
+Projection with debt instead minimizes
+$-\kappa\mathbf Q_r^\top M_r\alpha+\tfrac12\|\alpha-\widehat\beta_r\|_2^2$
+with its own debt recursion and $\kappa=1000$, selected on tuning seeds.
+Inst-Cal removes debt from the full criterion.  Full RAVEN retains (P2).
+These rules retain their own names and objectives.
+
+\begin{table*}[t]
+\centering
+\caption{Trained server-weight rules on matched Design-on support (20 paired
+seeds per dataset; means; lower is better). Prediction uses the saved-parameter
+scores, including the existing terminal-window correction. Runtime is measured
+wall-clock seconds per run. The U-Air count row is restricted to the RAVEN-Design
+support and therefore differs from FedAvg in Table~\ref{tab:main_effectiveness}.
+The $\kappa=1000$ rule is a separate sensitivity variant.}
+\label{tab:trained_rules}
+\footnotesize
+\setlength{\tabcolsep}{5pt}
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrr}
+\toprule
+Dataset & Server-weight rule & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$ &
+$\mathrm{RMSE}_\mu$ & WorstGroupRMSE & Wall (s)\\
+\midrule
+SensorScope & Count / matched support & $1.05577$ & $1.29032$ & $7.93889$ & $8.67161$ & $20.5$\\
+SensorScope & Uniform & $1.02693$ & $1.27069$ & $7.93931$ & $8.67202$ & $20.0$\\
+SensorScope & Reference projection & $1.01158$ & $1.26903$ & $7.93725$ & $8.66989$ & $19.9$\\
+SensorScope & Projection with debt ($\kappa=1000$) & $0.98464$ & $1.26659$ & $7.93842$ & $8.67109$ & $18.5$\\
+SensorScope & Inst-Cal & $1.01409$ & $1.26443$ & $7.93799$ & $8.67066$ & $26.2$\\
+SensorScope & Full RAVEN-Design & $1.01394$ & $1.26438$ & $7.93799$ & $8.67066$ & $27.1$\\
+\midrule
+U-Air & Count / matched support & $1.12176$ & $1.26213$ & $1.19225$ & $1.25956$ & $12.0$\\
+U-Air & Uniform & $1.09734$ & $1.24065$ & $1.19349$ & $1.26094$ & $8.5$\\
+U-Air & Reference projection & $1.09162$ & $1.23265$ & $1.19691$ & $1.26474$ & $8.8$\\
+U-Air & Projection with debt ($\kappa=1000$) & $1.08001$ & $1.22623$ & $1.19470$ & $1.26231$ & $9.0$\\
+U-Air & Inst-Cal & $1.09241$ & $1.23342$ & $1.19537$ & $1.26304$ & $15.1$\\
+U-Air & Full RAVEN-Design & $1.09236$ & $1.23339$ & $1.19537$ & $1.26303$ & $15.3$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+Count-to-Uniform reduces group mismatch by $1.442$ pp on SensorScope and
+$1.221$ pp on U-Air.  Projection adds $0.768$ pp and $0.286$ pp, respectively.
+Full RAVEN then has $0.118$ pp more group mismatch than projection on SensorScope
+($p_{\mathrm{Holm}}=0.019$), while reducing client--stratum mismatch by $0.232$ pp.
+Its U-Air group contrast with projection is not significant.  Simple projection
+also takes less wall time: $19.9$ versus $27.1$ s on SensorScope and $8.8$ versus
+$15.3$ s on U-Air.  No registered prediction superiority contrast survives Holm
+correction (SensorScope $p_{\mathrm{Holm}}=1$; U-Air minimum $0.120$ under the
+corrected scores).  Better structural ordering therefore does not establish a
+prediction advantage for the full objective.
+
+The direct corrected reference $\alpha=\widehat\beta_r$ has a different evidence
+role.  The fixed-support structural readout gives group mismatch $1.03533$ on
+SensorScope and $1.11961$ on U-Air before projection; these allocations can
+violate caps or ESS.  The $1.188$ pp and $1.399$ pp projection improvements in
+Section~\ref{subsec:eval_rq2} describe that readout, without a trained prediction
+or runtime row for direct aggregation.  Design is a further independent
+contrast: the same-support projected on/off difference of $0.922$ pp on
+SensorScope is distinct from the $0.768$ pp projection--Uniform difference.
+The full end-to-end Design on/off comparison remains
+Table~\ref{tab:e4_ablation}; U-Air changes support and cannot supply a
+same-support Design attribution.
+
+The projection values describe numerical implementations of the stated rules,
+not exact optimizer certificates.  The existing independent projection audit
+finds a maximum endpoint discrepancy of $2.42\times10^{-5}$ in $\Delta$ units;
+its point-level optimality checks do not all pass.  Section~\ref{app:kappa_probe}
+reports this numerical scale separately from the measured rule effects.
 
 \subsection{Prediction Sensitivity within the Feasible Weight Class}
 \label{subsec:ceiling}
 
-The recoverable gain is bounded inside the class the method defines: weights in
-$\mathcal{C}_r$ of \eqref{eq:Cr}, selected by (P2), scored by the
-deployment-target criterion $\mathrm{RMSE}_{\mu}$.  Two measured quantities bound
-it.  The first is the headroom from the uncorrected member (FedAvg-Window) to the
-best member evaluated on true margins,
-$H=(\mathrm{RMSE}_{\mu}(\text{FedAvg})-\mathrm{RMSE}_{\mu}(\text{oracle}))/\mathrm{RMSE}_{\mu}(\text{FedAvg})$,
-over a stress grid varying the opportunity tilt, the tail observation scale, the
-model capacity, and the target.  The pre-specified continuation threshold is
-$H\ge0.5\%$ with a positive interval lower bound.  The measured headroom falls
-below this threshold.  SensorScope has a paired-difference minimum
-detectable effect of $0.17$--$0.36$ percentage points, with all six estimates
-inside $[-0.03\%,+0.08\%]$.  U-Air uses $20$ seeds, $270$ runs and $45$
-traces, with every estimate satisfying $|H|\le0.217\%$ and a $95\%$
-interval containing zero; its realized detectable effect of $0.70$--$0.80$ points
-excludes effects above about $0.7\%$ without resolving the $0.5\%$ bar on its
-own.  Hardening the observation propensity to vary within a stratum and correlate
-with the label raises the oracle gap by $15$--$21\times$, to $0.104\%$ on
-SensorScope and $0.251\%$ on U-Air, both inside the same bound.  The bound is
-this weight class at the server step of the grid.  NSW-Traffic, where that step
-is replaced, is reported in Section~\ref{subsec:limitations}.
+Two empirical comparisons assess prediction sensitivity of the evaluated
+server-weight configurations.  First, compare FedAvg-Window with the evaluated
+true-margin configuration using
+$H=(\mathrm{RMSE}_{\mu}(\text{FedAvg})-\mathrm{RMSE}_{\mu}(\text{oracle}))/
+\mathrm{RMSE}_{\mu}(\text{FedAvg})$.
+The grid varies opportunity tilt, tail observation scale, model capacity, and
+target, with a $0.5\%$ practical effect criterion.  SensorScope's six estimates
+lie in $[-0.03\%,+0.08\%]$, with paired minimum detectable effects of
+$0.17$--$0.36$ percentage points.  On U-Air, 270 runs and 45 traces over 20 seeds
+give $|H|\le0.217\%$ and intervals containing zero; the $0.70$--$0.80$ point
+detectable effects leave a $0.5\%$ improvement unresolved.  These are measured
+contrasts for specific oracle-margin configurations, not upper bounds over all
+weights in $\mathcal C_r$.
+
+The original block-constant observation model also leaves local H\'ajek
+weights uniform whenever the retained records share its correction factor.
+A separate within-stratum construction varies the observation propensity with
+the time-index tercile inside each stratum, while preserving the block mean.
+Mean distinct propensities per stratum rise from one to $2.76$ on SensorScope
+and $2.83$ on U-Air.  This is covariate-dependent constructed selection, rather
+than a direct dependence on an unobserved response.  The construction and
+information interface are detailed in Appendix~\ref{app:f1_mechanism}.
 
 The second quantity is the cost of estimating the margins, measured inside one
 calibrated member so that only the observation and usable-update margins change.
@@ -2140,16 +2188,16 @@
 composition at the same order for the members whose weights normalize that
 reference.  Accurate margin estimates are therefore not what holds the prediction
 endpoint flat, since three of the four members are insensitive to a large change
-in their own aggregation weights.  At the composition level the perturbation is
-already bounded, because \eqref{eq:g4_comp} limits the aggregate difference
+in their own aggregation weights.  At a fixed window state,
+\eqref{eq:g4_comp} bounds the aggregate difference
 induced by the margin estimates to $\|M_r\|_2$ times the reference perturbation
 controlled by Proposition~\ref{prop:practical_plugin}; a metric-level bound of
 the same form would require a transfer assumption between the training and the
-deployment distributions, which Proposition~2 does not make, so the metric-level
-ceiling above is measured, at the minimum detectable effects stated.
+deployment distributions, which Proposition~2 does not make, so prediction sensitivity remains an empirical measurement at the detection scales stated.
 
 \noindent\textbf{Active-set geometry and prediction sensitivity.}
-The active-client count determines the dimension of the feasible weight set.  With
+The active-client count bounds, but does not by itself determine, the dimension
+of the feasible weight set.  With
 the frozen $E_{\min}=3$, the bound in \eqref{eq:Cr} is
 $\overline E_r=\min(3,K_r)$, and since $\|\boldsymbol\alpha\|_2^2\ge1/K_r$ on
 the simplex with equality only at $\mathbf 1/K_r$, a window with $K_r\le3$
@@ -2166,6 +2214,86 @@
 window counts show, rather than on the weights inside a window.
 NSW-Traffic is the block on which most windows have $K_r>3$; its prediction
 measurement is in Section~\ref{subsec:limitations}.
+
+\paragraph{Does a concentrated target expose a larger prediction gain?}
+The NSW-Traffic target-concentration comparison keeps the original backbone,
+two local steps, and server update.  It multiplies the prior mass of a
+pre-specified coordinate region (region1) by $\kappa_{\mathrm{tar}}$ and
+renormalizes, with a single-region limit.  This concentration parameter differs
+from the debt-strength $\kappa$ in Table~\ref{tab:trained_rules}.
+Table~\ref{tab:target_concentration} compares Local-H\'ajek control with
+RAVEN-SimOracle, which uses the generator's observation probabilities and
+Monte Carlo usable-update probabilities with the full calibration pathway.
+The $\kappa_{\mathrm{tar}}=1$ pair reuses existing runs; the $5$ pair comes from
+the four-arm concentration experiment, and the $10$ and single-region pairs
+come from two further target conditions, each with 20 paired seeds.
+
+\begin{table}[t]
+\centering
+\caption{Traffic target concentration and the evaluated oracle-margin contrast.
+$D$ is control minus oracle test RMSE in the original standardized units;
+relative gain is $100\overline D/\overline{\mathrm{RMSE}}_{\mathrm{control}}$.
+Intervals and MDE retain the existing seed-paired analysis.}
+\label{tab:target_concentration}
+\scriptsize
+\setlength{\tabcolsep}{2.2pt}
+\begin{tabular}{lrrrr}
+\toprule
+$\kappa_{\mathrm{tar}}$ & Top region & $\overline D$ [95\% CI] & MDE$_{80}$ & Gain (\%)\\
+\midrule
+1 & $0.256$ & \shortstack{$0.000013$\\$[-0.000099,0.000148]$} & $0.000197$ & $0.0013$\\
+5 & $0.632$ & \shortstack{$0.000228$\\$[0.000055,0.000422]$} & $0.000289$ & $0.0225$\\
+10 & $0.775$ & \shortstack{$0.000462$\\$[0.000241,0.000708]$} & $0.000367$ & $0.0454$\\
+Single region & $1.000$ & \shortstack{$0.000994$\\$[0.000685,0.001337]$} & $0.000511$ & $0.0970$\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+The contrast grows with concentration, reaching $0.0970\%$ at the single-region
+target.  Its interval excludes zero and its mean exceeds the reported MDE at
+$\kappa_{\mathrm{tar}}=10$ and the limit.  At $5$, the interval excludes zero
+but the mean remains below its MDE.  All four effects remain below this
+experiment's pre-specified $2\%$ practical criterion.  Thus target dilution
+alone does not explain the small gain for this evaluated oracle and update
+rule; the measurement does not optimize over the entire feasible weight class.
+
+\paragraph{Weight freedom, composition freedom, and adjustable mass.}
+A separate three-seed development geometry audit reconstructs feasible sets
+without evaluating predictions.  Table~\ref{tab:development_geometry} retains
+its own window population, independently of the older percentages above.
+With $W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
+\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable target mass is the sum
+of $\mu_g$ over positive-target groups with $W_{r,g}\ge.01$.
+This distinguishes a non-singleton weight set from a direction that moves group
+composition and from the amount of target mass that can move.
+
+\begin{table}[t]
+\centering
+\caption{Natural-window geometry in the separate development protocol
+(seeds 41001--41003, cap .5 and ESS minimum 3). These are geometric measurements,
+not fixed-Design performance comparisons.}
+\label{tab:development_geometry}
+\scriptsize
+\setlength{\tabcolsep}{3pt}
+\begin{tabular}{lrrrr}
+\toprule
+Dataset & Windows & $K$ range & Singleton (\%) & Adj. mass (\%)\\
+\midrule
+SensorScope & 283 & 1--6 & 80.57 & 0.433\\
+U-Air & 228 & 1--6 & 82.46 & 0.515\\
+Traffic & 300 & 1--15 & 4.33 & 4.647\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+For Traffic's 183 sorted-client subsets with $K=8$, ESS minimum 4, and cap .25,
+all have a composition direction of rank at least one and at least two groups
+with $W_{r,g}\ge.01$, but mean adjustable target mass is only $4.651\%$.
+The reference violates the constraints in $59.02\%$ of these subsets and the
+mean projection distance is $0.067487$ in client-weight $\ell_2$ units.
+Appendix~\ref{app:development_geometry} gives the cap/ESS sensitivity.  Selecting
+subsets from natural windows is a geometry diagnostic, not a controlled
+participation intervention or evidence of a prediction gain.
 
 \subsection{Deployment Conditions and Evaluation Scope}
 \label{subsec:limitations}
@@ -2237,34 +2365,38 @@
 $0.967$ for window FedAvg and $0.973$ for the oracle-margin arm on average, in
 $[0.659,1.572]$ and $[0.795,1.459]$, against $1.007$ for the test-fitted constant on
 the same test weights, where the training-mean predictor takes the same value;
-both arms therefore sit below that reference.  Scored on the same runs after that
+both arm means therefore sit below that reference.  Scored on the same runs after that
 prediction contrast, the oracle-margin weights reduce $\Delta_{\mathrm{group}}$ by
 $0.0079$
 $[0.0051,0.0110]$ and $\Delta_{c\text{-}s}$ by $0.0099$ $[0.0067,0.0132]$.
-The original-step comparison and the Adam comparison quantify prediction
-headroom within this server-weight class at their respective detection scales.
+The original-step and Adam comparisons measure the evaluated oracle-margin
+configuration at their respective detection scales.  Separate longer-budget
+learning diagnostics in Appendix~\ref{app:learning_capacity} distinguish backbone
+capacity from aggregation effects, using development validation data and physical
+units rather than the test scores above.
 
 
 \section{Conclusion}
 \label{sec:conclusion}
 
-RAVEN-MCS connects deployment-target semantics with feasible aggregation in
-windowed-asynchronous sensing.  The sequential reconstruction represents the
-opportunity, observation, and usable-update layers explicitly, while calibration
-maps the corrected reference into the mixtures available at window closure.
-With Design configured on, the ideal correction under A1--A3 recovers compatible target moments and group
-mass.  The calibration program has a unique minimizer, and the clipped plug-in
-admits a stability bound on shared target support.
-
-The paired experiments attribute structural alignment to uniform aggregation,
-the corrected reference, and its feasible projection.  On SensorScope, the
-projection improves group mismatch by $+0.768$ percentage points over uniform
-weights, and the Design factor contributes $+0.922$ points on the same active
-set.  Separate mobility and observation protocols characterize how these
-structural effects relate to deployment-weighted prediction.  Together, the
-formulation and measurements distinguish statistical target reconstruction from
-finite-window realizability and provide a basis for choosing aggregation weights
-for a specified sensing population.
+RAVEN-MCS connects a selection-corrected sensing-unit reference to the
+constrained client mixtures available in an asynchronous window.  Its formulation
+separates the deployment target, sequential arrival law, and feasible composition;
+the ideal reconstruction and fixed-window stability results specify different
+parts of that connection.  Debt carries under-service across windows, with
+long-run alignment conditional on its growth rate.
+
+The experiments separate the changes due to Uniform, reference projection,
+Design, and the full criterion.  On SensorScope, projection improves group
+mismatch by $0.768$ pp relative to Uniform; the distinct same-support projected
+Design-on/off contrast is $0.922$ pp.  Projection is faster than full RAVEN and
+has lower group mismatch on SensorScope, while the full criterion improves the
+client--stratum endpoint.  These structural differences do not establish
+consistent prediction gains.  Concentrated-target and geometric diagnostics
+further distinguish target mass, feasible adjustment, and learning sensitivity.
+Population reconstruction and finite-window calibration are therefore separate
+requirements whose task value must be assessed under the actual learning and
+selection protocol.
 
 \section*{Data and Code Availability}
 SensorScope, U-Air, NSW-Traffic, and T-Drive are public and cited in
@@ -2298,16 +2430,20 @@
 
 The server-weight comparisons in Section~\ref{subsec:eval_rq3} use a shared
 driver and distinct objectives for RAVEN, projection, and projection with debt.
-The RAVEN replay reproduces its recorded endpoints, and all $120$ runs retain
-their recorded active sets.  Across $240$ rule runs, replayed server weights
-are bit-identical and endpoint agreement reaches $6.9\times10^{-15}$ percentage
-points.  Relative to the reference path's solver tolerance of $10^{-9}$, the
-projection rules differ by $2\times10^{-6}$ to $3.7\times10^{-5}$ percentage
-points; uniform weights and the reconstructed reference match.
-Section~\ref{app:kappa_probe} reports approximation relative to exact projection
+The W1 records retain each rule's weights, reference, and active clients.
+Numerical comparisons report structural endpoint discrepancies separately from
+optimizer certificates.
+Section~\ref{app:kappa_probe} reports discrepancy relative to an independent projection computation
 through $\varepsilon_{\mathrm{impl}}$ and specifies the debt weight selected
 on tuning seeds.
 
+The target-concentration table uses \texttt{results\_traffic\_e2/round\_v1/}.
+The separate learning and geometry diagnostics use the R2 validation summaries
+and curves in \texttt{results\_main\_rebuild\_r1/}.  Their development splits and
+budgets differ from the main test comparison.  The trained-rule prediction
+values use \texttt{round\_v5\_1/TRADEOFF\_V51.csv}; projection accuracy is
+reported from the subsequent numerical audit rather than asserted exact.
+
 \bibliographystyle{IEEEtran}
 \bibliography{reference}
 
```

## appendix.tex

```diff
--- before/appendix.tex
+++ current/appendix.tex
@@ -1277,11 +1277,8 @@
 \section{Complete Proofs for Aggregate Coverage Certification}
 \label{app:agg_coverage_proofs}
 
-This section records the complete proofs for
+This section gives the deferred coverage proofs for
 Section~\mbox {III-D}--\mbox {VI-F}.
-Existing reconstruction proofs are unchanged.  The coverage-certificate
-numbering is independent of Proposition~1 and
-Theorem~1.  All arguments below are complete.
 
 \begin{algorithm}[t]
 \caption{Aggregate coverage certificate (diagnostic Gate)}
@@ -1510,14 +1507,6 @@
 correct operational response.  The detector does not restore
 Theorem~2 on the undetected first-shift window.
 
-The optional bounded-TV robustness extension is omitted: it would require a
-legally frozen pre-test $\epsilon_g$ with $\alpha'+\epsilon_g\le\alpha$, not
-estimated post hoc from the test sequence, plus a complete proof.  Those
-conditions are not met, so the core paper relies only on
-Theorem~2, Corollary~\ref{cor:false-safe-gate}, and
-Proposition~\ref{prop:drift-boundary}.
-
-
 \section{Supplementary Risk-Semantic Evidence}
 \label{app:risk_semantic_evidence}
 
@@ -1588,6 +1577,39 @@
 \end{table}
 
 
+\subsection{Response to Each Selection Layer}
+\label{app:e2_layer_matrix}
+
+The six scenarios use five methods and 20 paired seeds each (600 existing
+runs).  Table~\ref{tab:e2_layer_matrix} summarizes the final numerical-tie-aware
+analysis.  Each range spans the five method-specific mean changes from balanced;
+the significant counts retain the existing within-method, within-metric Holm
+families over the five non-balanced scenarios.  Signed arrival--target gaps are
+not absolute mismatch scores.  Complete-counteracting does not establish the
+proposed directional event, and no corrected comparison establishes RAVEN
+prediction dominance across these scenarios.
+
+\begin{table*}[t]
+\centering
+\caption{Risk responses to controlled selection layers on NSW-Traffic.
+Changes use the original standardized RMSE units; $\times10^{-3}$ applies to
+both range columns. Counts are Holm-significant methods out of five.}
+\label{tab:e2_layer_matrix}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr}
+\toprule
+Scenario & Target change range & Arrival change range & Target significant & Arrival significant\\
+\midrule
+Balanced & 0 & 0 & -- & --\\
+Opportunity only & $[0.057,0.114]$ & $[5.699,5.990]$ & 0/5 & 0/5\\
+Observation only & $[0.108,0.157]$ & $[11.018,11.145]$ & 0/5 & 5/5\\
+Usable update only & $[0.193,0.245]$ & $[5.472,5.607]$ & 0/5 & 0/5\\
+Complete aligned & $[0.757,0.820]$ & $[21.660,22.130]$ & 2/5 & 5/5\\
+Complete counteracting & $[0.030,0.059]$ & $[12.447,12.639]$ & 0/5 & 0/5\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
 \section{Local-H\'ajek Degeneracy Analysis}
 \label{app:local_hajek}
 
@@ -1650,6 +1672,44 @@
 numerical equality without weakening the general role of H\'ajek normalization
 when within-window correction weights are heterogeneous.
 
+
+\subsection{Within-Stratum Observation Heterogeneity}
+\label{app:f1_mechanism}
+
+The F1 construction changes the observation probability to
+$p_i=\operatorname{clip}(\operatorname{sigmoid}(b_{0,b}+\theta_O z_i),.05,.95)$,
+where $z_i\in\{-1,0,1\}$ is the time-index tercile of a training unit within
+its opportunity stratum.  The block intercept $b_{0,b}$ preserves the original
+block mean, .35 or .1925.  It uses no current response value.  Thus the
+intervention introduces within-stratum covariate dependence, not general MNAR
+selection.  At $\theta_O=0$ the copied selection traces coincide with the
+original construction; at $\theta_O=1$ they are regenerated with the same
+opportunity, delivery process, seeds, splits, and target maps.
+
+\begin{table}[t]
+\centering
+\caption{Observation-probability diversity in F1. Distinct probabilities are
+counted per opportunity stratum; entries are stratum means. The block marginal
+is preserved by construction.}
+\label{tab:f1_mechanism}
+\footnotesize
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrr}
+\toprule
+Dataset & $\theta_O=0$ & $\theta_O=1$\\
+\midrule
+SensorScope & 1.00 & 2.76\\
+U-Air & 1.00 & 2.83\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The estimated-propensity arm retains the original covariates.  The true-$p$
+arm replaces only the atomic observation propensity, retaining estimated $q$
+and Design on on both datasets.  Its local inverse weights can therefore vary
+across observed time terciles, whereas a stratum-constant factor cancels under
+local H\'ajek normalization.  This separates a construction that supplies no
+within-stratum correction signal from one that supplies such a signal; it does
+not by itself establish a prediction benefit.
 
 \section{P2 Feasibility Diagnostics}
 \label{app:p2_diagnostics}
@@ -1719,7 +1779,7 @@
 target and selection protocols.  Prediction and oracle references carry
 $^\dagger$; the main inferential family consists of the deployable methods.
 
-The sealed same-backbone family below is evaluated with Design on, on both
+The same-backbone family below is evaluated with Design on, on both
 blocks, so the U-Air panels diagnose that arm rather than the setting the
 deployment uses there.  Table~III reports both settings on both blocks: Design
 on for SensorScope and Design off for U-Air.
@@ -1766,32 +1826,25 @@
 
 \begin{table*}[t]
 \centering
-\caption{Comparison of target semantics and selection correction.  RAVEN
-combines a public deployment target, sequential R/O/U pre-outcome
-histories, sensing-side correction, and finite-window calibration.
-FedIPW~\cite{morishita2026who} is the nearest two-stage FL IPW
-(enrollment then participation) for federated learning.
-FLOSS~\cite{goetze2025floss} is client-level opt-out/straggler IPW.
-FedAU-Window and ObsUse-Window used in Section~VII are
-adaptations to window-close aggregation.
-The table compares method specifications.}
+\caption{Closest mechanisms and their information requirements. Population
+calibration and target matching are established ingredients; the RAVEN column
+specifies their connection to sensing-unit selection and finite-window support.}
 \label{tab:nearest_neighbor}
-\setlength{\tabcolsep}{3.2pt}
-{\footnotesize
-\begin{tabular}{@{}p{2.30cm}p{2.10cm}p{2.05cm}p{1.85cm}p{2.30cm}@{}}
+\footnotesize
+\setlength{\tabcolsep}{3pt}
+\begin{tabular}{@{}p{1.8cm}p{4.2cm}p{4.2cm}p{6.0cm}@{}}
 \toprule
-Family & Target & Selection & Sensing-side & Finite-support cal.\\
-\midrule
-Covariate-shift FL & target/test domain & sample/client & no & no\\
-FedAU / participation debiasing & original FL objective & client participation & no & no\\
-FedIPW & pop.\ mean update & enroll then participate & no & no\\
-FLOSS & client roster & opt-out / straggler & no & no\\
-Correlated participation & long-run availability & client/update & no & limited\\
-Agnostic / targeted FL & client mixture & client distribution & no & not the issue\\
-Semi-async fairness/queue & participation fairness & client/update & no & queue \(\neq\) target debt\\
-\textbf{RAVEN-MCS} & public deployment \(\mu\) & R/O/U & yes & yes\\
+Dimension & FedIPW~\cite{morishita2026who} & FedPALS~\cite{listozec2024overcoming} & RAVEN-MCS\\
+\midrule
+Selection unit & Client enrollment and round participation & Client/source label distribution & Atomic sensing opportunity/observation, then registered update usability\\
+Available information & Pre-enrollment/pre-round covariates; population summaries in calibration extension & Known client and target label marginals, client sample sizes & Public atomic/group target; lagged opportunity, pre-$O$ covariates, pre-$U$ registration history\\
+Target object & Target-population mean update & Target-domain risk under label shift & Deployment measure over sensing units and compatible client--stratum mass\\
+Correction / reference & Product IPW; enrolled-sample calibration & Convex composition matching & Sequential normalized correction forms $\widehat\beta_r$ before feasible calibration\\
+Caps / ESS & Population-summary constraints; no corresponding window caps/ESS & Soft inverse sample-level ESS penalty & Hard client cap and client-level ESS ball on current $\mathcal A_r$\\
+Cross-window state & Propensity estimation & Recomputed target-aware weights & Lagged selection/variance histories and target debt\\
+Guarantee scope & Mean-update identification; residual-weight analysis under stated optimization assumptions & One-step unbiased update under label shift and convex-hull coverage & Ideal pooled moments; fixed-state calibration stability; conditional debt accounting\\
 \bottomrule
-\end{tabular}}
+\end{tabular}
 \end{table*}
 
 \begin{table}[t]
@@ -1818,7 +1871,7 @@
 \begin{figure}[t]
 \centering
 \includegraphics[width=\columnwidth]{fig3_e3_structural_mismatch.pdf}
-\caption{Sealed same-backbone structural alignment on SensorScope and
+\caption{Same-backbone structural alignment on SensorScope and
 U-Air (mean $\pm$ std over 20 paired seeds; lower is better).
 (a)(b)~SensorScope $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$;
 (c)(d)~U-Air $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$.
@@ -1831,7 +1884,7 @@
 \begin{figure}[t]
 \centering
 \includegraphics[width=\columnwidth]{fig4_e3_prediction_risk.pdf}
-\caption{Sealed same-backbone deployment-target prediction risk
+\caption{Same-backbone deployment-target prediction risk
 (mean $\pm$ std over 20 paired seeds; lower is better).
 (a)(b)~SensorScope $\mathrm{RMSE}_{\mu}$ and Tail RMSE;
 (c)(d)~U-Air $\mathrm{RMSE}_{\mu}$ and Tail RMSE.
@@ -2143,14 +2196,12 @@
 (iii)~SensorScope $\Delta_{\mathrm{group}}$ remains lower for
 RAVEN-Design than for FedAvg (paired $-1.04\%$).
 
-The structural effects vary with the opportunity process.
-SensorScope $\Delta_{c\text{-}s}$ versus FedAvg shrinks to
-$-0.05\%$ ($p>0.05$).
-Removing Design on SensorScope moves
-$\Delta_{\mathrm{group}}$ by $+0.05\%$ ($p>0.05$).  Absolute
-$\Delta_{\mathrm{group}}$ also sits higher for every method than in
-Table~III (about $1.33$ versus $1.01$ on
-SensorScope), consistent with the thinner protocol $R$.
+The thinner opportunity process changes the structural effects.  On
+SensorScope, the $\Delta_{c\text{-}s}$ contrast with FedAvg shrinks to
+$-0.05\%$, and removing Design changes $\Delta_{\mathrm{group}}$ by
+$+0.05\%$; neither contrast is significant ($p>0.05$).
+Every method also has higher absolute $\Delta_{\mathrm{group}}$ than in
+Table~III, about $1.33$ versus $1.01$ on SensorScope.
 
 \begin{table*}[t]
 \centering
@@ -2405,7 +2456,7 @@
 U-Air $25.5\%$ is EventTrace occurrence, not this statistic.}
 \label{tab:scd_phi_freeze}
 \scriptsize
-\setlength{\tabcolsep}{3pt}
+\setlength{\tabcolsep}{2.5pt}
 \begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
 \toprule
 Block & $n_{\mathrm{train}}$ & $n_{\mathrm{zero}}$ & coverage & Design (42)\\
@@ -2582,3 +2633,108 @@
 \end{table*}
 
 
+
+\section{Learning Capacity under a Separate Development Protocol}
+\label{app:learning_capacity}
+
+These measurements use chronological development validation splits and seeds
+41001--41003, rather than the test comparisons in the main paper.
+Central-delivered pools only delivered training observations.  Both backbones
+are evaluated over 200 effective data passes, with Adam learning rates
+$.0003,.001,.003$ and momentum-SGD rates $.001,.01,.03$, batch size 64, and a
+factor-.3 schedule after passes 50, 100, and 150.  Configurations and checkpoints
+are selected on validation.  HistoryResidual adds a 64/32 history network and a
+training-statistic residual reference to Common-NDMF.  The 108 central runs,
+one Traffic Uniform development run, and three U-Air Central-all diagnostics
+are separate learning measurements, not new RAVEN comparisons.
+
+\begin{table*}[t]
+\centering
+\caption{Common-NDMF Central-delivered validation after the longer training
+budget (three development seeds; physical units). Gains are mean seed-paired
+relative improvements over the strongest applicable simple baseline. These
+values are not the old protocol's test scores or RAVEN aggregation gains.}
+\label{tab:learning_capacity}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllrrr}
+\toprule
+Dataset & Unit & Optimizer / LR & Strongest simple baseline & Baseline RMSE & Model RMSE $\pm$ SD & Gain (\%)\\
+\midrule
+Traffic & vehicles/h & Adam / .003 & Weekly seasonal naive & 381.6185 & $202.0554\pm3.1556$ & $+47.01$\\
+SensorScope & $^\circ$C & Adam / .003 & Training mean & 2.9687 & $2.6675\pm.0987$ & $+10.16$\\
+U-Air & $\mu$g/m$^3$ & SGD / .03 & Spatial training mean & 20.3060 & $20.5015\pm.2311$ & $-0.96$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+\begin{figure*}[t]
+\centering
+\includegraphics[width=\textwidth]{fig_learning_capacity_r2.png}
+\caption{Longer-budget development learning curves, with physical training
+RMSE above and deployment-weighted validation RMSE below. Lines are means and
+shading spans the three seeds. Dashed lines show the strongest applicable simple
+baseline mean. Per-seed best validation scores in
+Table~\ref{tab:learning_capacity} differ from the minimum of a mean curve.}
+\label{fig:learning_capacity}
+\end{figure*}
+
+Training means, spatial means, seasonal means, persistence, and repeated-phase
+daily/weekly seasonal-naive predictors share the delivered-training information
+boundary.  Persistence uses the latest legal training observation; seasonal
+naive repeats the latest available phase without feeding validation labels back
+into history.  Weekly comparison requires at least two weeks of training
+observations.  Prediction is inverse-scaled and scored against float64 physical
+targets.  Traffic's target is traffic volume; the other two retain their
+controlled client-measurement definitions.
+
+Common-NDMF improves on the strongest simple reference for Traffic and
+SensorScope but not U-Air.  HistoryResidual gives $7.33\%$ on Traffic and
+$-0.34\%/-4.45\%$ on SensorScope/U-Air.  U-Air Central-all, with all training
+labels visible, averages $19.5427$ versus $18.4567$ for its spatial-mean
+reference.  This distinguishes backbone/generalization limits from delivery
+sparsity alone.  The single Traffic Uniform run reaches $253.1132$ vehicles/h
+($33.70\%$ improvement), but its best validation error still improves
+$0.914\%$ between passes 100 and 200.  The central runs plateau under the
+declared criterion, whereas this federated run does not.  Neither the pooled
+learning gain nor that single development trajectory establishes a RAVEN
+weighting benefit.
+
+\section{Constraint Sensitivity of the Development Geometry}
+\label{app:development_geometry}
+
+The geometry uses first-cycle payloads from the separate development traces,
+with their recorded correction settings.  It does not re-evaluate the main
+fixed-Design performance experiment.  For each natural window with at least
+eight distinct clients, the diagnostic takes the first eight in sorted client
+order and renormalizes their reference.  Rank is measured from the centered
+composition matrix; group ranges are extrema over the constrained feasible
+set.  Therefore $K-1$, composition rank, and mass with a group range of at least
+.01 describe different kinds of freedom.
+
+\begin{table}[t]
+\centering
+\caption{Traffic fixed-$K=8$ geometry on the same 183 subsets. $E$ is the
+minimum client ESS; cap bounds each weight. Repair is mean
+$\|\operatorname{Proj}_{\mathcal C}(\widehat\beta)-\widehat\beta\|_2$.
+Mean adjustable target mass is $4.651\%$ in every row.}
+\label{tab:geometry_sensitivity}
+\footnotesize
+\setlength{\tabcolsep}{4pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}rrrr}
+\toprule
+$E$ & Cap & Reference violates (\%) & Repair\\
+\midrule
+2.0 & .2500 & 59.02 & .067487\\
+4.0 & .2500 & 59.02 & .067487\\
+6.4 & .2500 & 68.85 & .074626\\
+4.0 & .1875 & 96.17 & .126015\\
+4.0 & .5000 & 12.02 & .010304\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The natural data contain no $K=16$ payload.  Tightening caps increases reference
+infeasibility and projection distance without changing the .01-threshold
+adjustable mass in these subsets.  This illustrates why a single count of active
+clients is insufficient to characterize the target adjustment available to a
+server.  No forecasts or label-dependent choices enter this geometry audit.
```

## supplemental.tex

```diff
--- before/supplemental.tex
+++ current/supplemental.tex
@@ -55,7 +55,7 @@
 
 
 \usepackage{xr}
-\externaldocument{main}
+\externaldocument[][nocite]{main}
 
 \begin{document}
 
@@ -70,11 +70,11 @@
 and must be uploaded as a separate PDF. It is not a standalone submission.}
 
 % Continue figure/table/equation numbers from the companion main paper.
-% Main now has 4 figures, 4 tables, 1 algorithm (window-close configured Design) and
+% Main has 4 figures, 7 tables, 1 algorithm (window-close configured Design) and
 % the support-gate / switch-point equations (42)-(43).
 % Numbered statements in main: Prop. 1--3, Thm. 1--2, Assumption 1.
 \setcounter{figure}{4}
-\setcounter{table}{4}
+\setcounter{table}{7}
 \setcounter{algorithm}{1}
 \setcounter{equation}{43}
 \setcounter{proposition}{4}
@@ -101,10 +101,10 @@
 frozen debt strength the same contrast is $+0.0073$ pp ($[0.0064,0.0083]$) on
 SensorScope, inside the equivalence band of
 Section~\ref{subsec:equivalence_band} in the main paper.  Numerical
-approximation relative to the exact projection is measured by
+approximation relative to an independent projection computation is measured by
 $\varepsilon_{\mathrm{impl}}$, the distance
-between a trained rule's server weights and the exact minimizer of its
-projection problem.  That distance is reported in the $\Delta$ units of
+between a trained rule's structural endpoints and those of the independently
+computed projection comparator.  That distance is reported in the $\Delta$ units of
 the structural endpoints and not as a relative tolerance: over all $240$ rule
 runs $\varepsilon_{\mathrm{impl}}$ is at most $2.42\times10^{-5}$ in those units,
 equivalently $1.21\times10^{-3}$ in the percentage-point convention of
@@ -118,15 +118,8 @@
 describe the $\kappa=1000$ sensitivity variant separately from the standard
 RAVEN configuration.
 
-% The appendix cites a small number of works. Carrying its own bibliography
-% keeps this file compilable on its own, without main.aux.
-% The main paper imports this document's .aux through xr, so re-writing the five
-% cite keys that appendix.tex also cites in the main paper would define them twice.
-% The .aux write is suppressed for the bibliography only; \citation is untouched,
-% so the numbering and the reference list are unchanged.
-\makeatletter\@fileswfalse\makeatother
+% Each PDF has its own bibliography. xr imports cross-references without bibcite.
 \bibliographystyle{IEEEtran}
 \bibliography{reference}
-\makeatletter\@fileswtrue\makeatother
 
 \end{document}
```

## reference.bib

```diff
--- before/reference.bib
+++ current/reference.bib
@@ -508,7 +508,8 @@
   author={Morishita, Gota},
   howpublished={arXiv preprint arXiv:2604.26604},
   year={2026},
-  month={Apr}
+  month={Apr},
+  url={https://arxiv.org/abs/2604.26604}
 }
 
 @inproceedings{goetze2025floss,
@@ -527,12 +528,13 @@
 }
 
 @misc{listozec2024overcoming,
-  title={Overcoming Label Shift in Target-Aware Federated Learning},
+  title={Overcoming Label Shift with Target-Aware Federated Learning},
   author={Listo Zec, Edvin and Breitholtz, Adam and Johansson, Fredrik D.},
   howpublished={arXiv preprint arXiv:2411.03799},
   year={2024},
   month={Nov},
-  note={TMLR submission (OpenReview: dQAsAmb1Xb); arXiv 2411.03799v2, 26 Aug 2025; no TMLR volume at close}
+  url={https://arxiv.org/abs/2411.03799},
+  note={Version 2, Aug. 26, 2025}
 }
 
 @inproceedings{byrd2019importance,
```

