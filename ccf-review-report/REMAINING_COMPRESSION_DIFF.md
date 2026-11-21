# 本轮剩余章节与附录压缩差异

基准为编辑前重新编译确认的当前工作树，不回退用户改动。

## main.tex

```diff
--- this-round-start/main.tex
+++ current/main.tex
@@ -889,13 +889,10 @@
 \section{Theoretical Analysis}
 \label{sec:theory}
 
-Proposition~\ref{prop:reconstruction}
-recovers compatible target moments or group mass under A1--A3 for the ideal
-Design-on sequential estimator.  The calibration results then establish
-existence, uniqueness, and stability on the current feasible client support.
-These statements condition on the configured Design setting.  The
-block-level zero-target check of \eqref{eq:design_gate} does not establish
-the positivity and identification assumptions below.
+We distinguish ideal population reconstruction from calibration on current
+support.  All proofs are in Appendix~\ref{app:complete_proofs} and
+Appendix~\ref{app:agg_coverage_proofs}.  The catalogue check
+\eqref{eq:design_gate} does not establish the assumptions below.
 
 \subsection{Assumptions}
 \label{subsec:assumptions}
@@ -914,8 +911,8 @@
 (display in the supplemental material).
 
 \noindent\textbf{A3 (Correct ideal ratios and cluster-level regularity).}
-Ideal ratios equal their population counterparts, or stabilizing bounds are
-inactive on relevant support.  As $N_R^{\mathrm{opp}}\rightarrow\infty$,
+The ideal estimator uses correct population ratios without clipping.
+Inactive stabilization alone does not establish correct ratios.  As $N_R^{\mathrm{opp}}\rightarrow\infty$,
 weighted cluster sums obey a weak law and the H\'ajek denominator stays
 strictly positive.
 
@@ -925,10 +922,8 @@
 $\lambda_g,\lambda_v,\lambda_s\ge0$.  The feasible set is \eqref{eq:Cr}.
 
 \noindent\textbf{A5 (Positivity and shared support).}
-Every event that enters the estimator, i.e.\ each target-supported event of
-A1 that belongs to the realized active set $\mathcal{A}_r$, has strictly
-positive opportunity, observation, and usable-update margins, so that the
-three inversions in \eqref{eq:chi_event} are well defined there.  The ideal and
+All target-supported events entering the estimator on $\mathcal A_r$ have
+positive opportunity, observation, and usable-update margins.  The ideal and
 the practical reference share $\mathcal{A}_r$, $M_r$, and $\mathcal{C}_r$,
 and the unnormalized H\'ajek mass obeys
 $\mathbf{1}^{\top}b\ge B_{\min}>0$.  To retain this shared support under
@@ -943,10 +938,6 @@
 Design on and $1/p^{\mathrm{obs}}\le a_{\max}$ with Design off, and
 $1/q^{\mathrm{use}}\le d_{\max}$; when $d_{\max}\le1/q_{\min}$, as for the
 frozen constants, the last clause also gives $q^{\mathrm{use}}\ge q_{\min}$.
-The ceiling clause is stated on the composite weight rather than on
-$1/p^{\mathrm{obs}}$: \eqref{eq:a_stabilized} already carries
-$\widehat\zeta^{o}$, so bounding $1/p^{\mathrm{obs}}$ alone leaves it
-unbounded.
 A6a ensures that the map returns the ideal untruncated ratios and is sufficient
 for the stabilization error in \eqref{eq:eps_stab} to vanish.
 
@@ -961,12 +952,9 @@
 
 \begin{proposition}[Target-vs-arrival risk distinction]
 \label{prop:risk}
-Let $\boldsymbol\varpi^{\mathrm{tar}}$ and
-$\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$ be two normalized laws on the same
-finite supported atomic domain.  If
-$\boldsymbol\varpi^{\mathrm{tar}}\neq\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$,
-then the two risk functionals are not interchangeable in general: there exists
-a bounded nonnegative error profile $e_i$ such that
+Distinct normalized laws $\boldsymbol\varpi^{\mathrm{tar}}$ and
+$\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$ on the same finite supported
+domain admit a bounded nonnegative error profile $e_i$ with
 \begin{equation}
  \sum_i
  \varpi_i^{\mathrm{tar}}e_i
@@ -975,25 +963,16 @@
  \widetilde\rho_i^{\mathrm{arr}}e_i.
  \label{eq:prop1_nonidentity}
 \end{equation}
-Conversely, equality of the two weighted expectations for every bounded error
-profile implies equality of the two underlying laws.
+Equality for every bounded profile implies equal laws.
 \end{proposition}
 
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
-Proposition~\ref{prop:risk} distinguishes the risk functionals over bounded error
-profiles.  Their values for a fixed predictor depend on that predictor's errors.
+A fixed predictor may nevertheless have equal risks.
 
 \subsection{Normalized Sequential Target Reconstruction}
 \label{subsec:prop_reconstruction}
 
-For the ideal analysis, let $\mathcal{O}_r$ denote the multiset of realized
-opportunity events in window $r$.  Each event $e\in\mathcal{O}_r$ carries a
-mark $(k_e,i_e)$ with marginal opportunity law
-$P_r^{\mathrm{opp}}(k_e,i_e)$ in \eqref{eq:opp_event_law}.  Observation and
-usable-update selection then occur sequentially according to
-\eqref{eq:pobs_def}--\eqref{eq:quse_def}.  Define
+Let $\mathcal O_r$ be the multiset of opportunity events, with marks
+$(k_e,i_e)$ distributed by \eqref{eq:opp_event_law}.  Sequential selection gives
 \begin{equation}
  \chi_e
  =
@@ -1036,20 +1015,11 @@
  \pi^{\mathrm{tar}}_{k,i}\psi(k,i).
  \label{eq:target_phi}
 \end{equation}
-Therefore, client--stratum indicators recover
-$\pi^{\mathrm{tar}}_{k,s}$.  By the compatibility identity
-\eqref{eq:target_compatibility}, choosing
-$\psi(k,i)=\mathbf{1}\{h(i)=g\}$ then recovers the deployment-group mass
-$\mu_g$.  The result establishes moment and group-mass recovery under A1--A3.
+Client--stratum indicators recover $\pi^{\mathrm{tar}}_{k,s}$; compatibility
+\eqref{eq:target_compatibility} makes group indicators recover $\mu_g$.
 \end{proposition}
 
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
-Proposition~\ref{prop:reconstruction} identifies the ideal pooled correction
-with the target-mass opportunity ratio (RAVEN-Design).  Each finite-window
-reference is realized on its current client support, motivating the calibration
-in Section~\ref{sec:calibration}.
+This pooled result does not make the target realizable in each finite window.
 
 \subsection{Existence and Uniqueness of Feasible Calibration}
 \label{subsec:theorem_calibration}
@@ -1062,9 +1032,6 @@
 has a unique global minimizer $\boldsymbol\alpha_r^\star$.
 \end{theorem}
 
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
 The theorem establishes the exact program's minimizer.  Numerical feasibility
 and solver accuracy are evaluated separately in the supplemental material.
 
@@ -1084,22 +1051,18 @@
 \bigl\|\boldsymbol\beta_r^{\mathcal T}-\boldsymbol\beta_r^\star\bigr\|_1 .
 \label{eq:eps_stab}
 \end{equation}
-It vanishes when the stabilized and ideal normalized references coincide on the
-active support, and it depends only on the true margins, $\pi^{\mathrm{tar}}$
-and the frozen constants, so it is measurable on a released trace.  Let
-$n_r=\max_{k\in\mathcal{A}_r}\sum_i R_{k,r,i}O_{k,r,i}$ and
-$K_r=|\mathcal{A}_r|$.
+It is zero when normalized references coincide.  Write
+$n_r=\max_{k\in\mathcal A_r}\sum_iR_{k,r,i}O_{k,r,i}$ and $K_r=|\mathcal A_r|$.
 
 \begin{proposition}[Practical plug-in perturbation]
 \label{prop:practical_plugin}
 Assume A1, A4, A5, and A6b.  Let the stabilized window mass obey
 $\mathbf{1}^{\top}b_r^{\mathcal T}\ge B_{\min}>0$ at the true margins, and let
 the ideal and the implemented reference share $\mathcal{A}_r$, $M_r$, and
-$\mathcal{C}_r$.  Let $\boldsymbol\beta_r^\star$ be the
-same-window ideal untruncated reference and
-$\widehat{\boldsymbol\beta}_r$ the implemented clipped plug-in.  Let
-$\boldsymbol\alpha^\star(\boldsymbol\beta)$ denote the unique P2 minimizer
-at that fixed window state.  Then
+$\mathcal{C}_r$.  Write $\boldsymbol\beta_r^\star$ for the same-window ideal reference,
+$\widehat{\boldsymbol\beta}_r$ for the implemented clipped plug-in, and
+$\boldsymbol\alpha^\star(\boldsymbol\beta)$ for the unique P2 minimizer
+at the fixed state.  Then
 \begin{align}
 \bigl\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\bigr\|_1
 &\le
@@ -1116,33 +1079,14 @@
 \bigl\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\bigr\|_2,
 \label{eq:g4_comp}
 \end{align}
-where $C_1$ is the explicit Lipschitz envelope of the stabilized H\'ajek map
-(supplemental material), with
-$L_\pi=\pi^{\mathrm{tar}}_{\max}/(\pi_{\min}^2p_{\min})$,
-$L_p=\pi^{\mathrm{tar}}_{\max}/(\pi_{\min}p_{\min}^2)$,
-$L_q=\min\{q_{\min}^{-2},d_{\max}^2\}$, and
-$C_1=(2K_rn_r/B_{\min})(d_{\max}\max\{L_\pi,L_p\}+a_{\max}L_q)$; under Design
-off $\zeta\equiv1$, so $L_\pi=0$ and $L_p=1/p_{\min}^2$.  This stability bound
-compares references on shared target support with a fixed active set.
-It holds with or without A6a, which is sufficient to set
-$\varepsilon_{\mathrm{stab},r}$ to zero.
+Here $C_1$ and its Design-on/off constants are defined in
+\eqref{eq:g4_c1}.  On the shared fixed state, the bounds hold without A6a, which is sufficient
+for $\varepsilon_{\mathrm{stab},r}=0$ but not necessary when normalization
+cancels distortions.  Active clipping in the
+reported traces retains this term.  The worst-case envelope can be loose:
+the frozen Design-on constants give $L_\pi\le2\times10^{13}$.
+Reference or composition stability does not itself bound prediction risk.
 \end{proposition}
-
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
-Two corollaries fix how the bound is read.  (a) If A6a holds,
-$\boldsymbol\beta_r^{\mathcal T}=\boldsymbol\beta_r^\star$ and
-$\varepsilon_{\mathrm{stab},r}=0$, so \eqref{eq:g4_beta} returns to the sharp
-form $C_1(\varepsilon_\pi+\varepsilon_p+\varepsilon_q)$.  (b) Under Design off
-the observation side contributes nothing to $\varepsilon_{\mathrm{stab},r}$
-exactly when $p^{\mathrm{obs}}\ge p_{\min}$ and
-$1/p^{\mathrm{obs}}\le a_{\max}$, leaving the usable-update stage as the only
-source.  On the main comparison blocks, active stabilization retains the
-$\varepsilon_{\mathrm{stab},r}$ term.  $C_1$ is a worst-case envelope:
-at $\pi_{\min}=10^{-6}$ and $p_{\min}=0.05$ the Design-on
-$L_\pi\le2\times10^{13}$, so the informative part of \eqref{eq:g4_beta} is
-$\varepsilon_{\mathrm{stab},r}$.
 
 \begin{proposition}[Group decomposition of the deployment-target criterion]
 \label{prop:group_decomposition}
@@ -1152,47 +1096,21 @@
 $\mathrm{RMSE}_g=[n_g^{-1}\sum_{i:h(i)=g}(\widehat Y_i-Y_i)^2]^{1/2}$ for the
 equal-weight score of group $g$.  Then
 $\mathrm{RMSE}_{\mu}^2=\sum_{g\in\mathcal G}\mu^{\mathrm{eval}}_g\,\mathrm{RMSE}_g^2$.
-Along a feasible direction $d$ of the simplex, $\sum_g d_g=0$, and when
-$\mathrm{RMSE}_{\mu}>0$, the directional derivative is
-$\sum_g d_g\,\mathrm{RMSE}_g^2/(2\,\mathrm{RMSE}_{\mu})$.
-Two methods exchange order between evaluation weight vectors
-$\boldsymbol\mu^{\mathrm{eval}}$ and $\boldsymbol\mu'^{\mathrm{eval}}$ only when
-$\sum_g\mu^{\mathrm{eval}}_g(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)$
-and
-$\sum_g\mu'^{\mathrm{eval}}_g(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)$
-have opposite signs.
+The identity holds for fixed predictions and fixed within-group weights.
+Directional sensitivity and ranking changes are derived in
+Appendix~\ref{app:proof_prop4}.
 \end{proposition}
 
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
-\noindent The decomposition rests on three stated conditions: the groups
-partition the supported test units, the within-group weights do not depend on
-the other groups' masses, and $\boldsymbol\mu^{\mathrm{eval}}$ is a probability
-vector.  It re-weights one fixed set of predictions, so it constrains how a
-reported value moves with the target map and not how a method would perform
-under a different map, and the group scores remain measured.  For the two
-Design settings scored under one map it decides the prediction endpoint: the
-sign of $\sum_g\mu^{\mathrm{eval}}_g[\mathrm{RMSE}_g^2(\mathrm{on})-
-\mathrm{RMSE}_g^2(\mathrm{off})]$ is the sign of the
-$\mathrm{RMSE}_{\mu}$ difference, and it says nothing about the structural
-endpoints $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$.
+This reweights existing predictions, not a model retrained under another
+target, and does not characterize either structural endpoint.
 
 \subsection{Aggregate Coverage Guarantees}
 \label{subsec:agg_coverage_theory}
 \label{subsec:pairwise_barrier}
 
-The reconstruction results above do not by themselves yield a finite-sample
-coverage certificate.  Deterministic pre-window pairwise LCBs are vacuous
-under hidden zero-opportunity events, and the frozen stress levels
-$a\in\{0.80,0.60,0.40,0.20\}$ fall in that region
-by the availability-induced barrier corollary in the supplemental material.  In a certified regime the
-false-safe probability of an empirical diagnostic Gate is bounded by
-$\alpha$, by the false-safe Gate corollary in the supplemental material; and
-no method can simultaneously provide nontrivial per-window certification and
-universal protection against arbitrary unannounced regime shifts, by the
-arbitrary-drift applicability boundary proposition in the supplemental
-material.
+Positive pairwise LCBs are vacuous under hidden zero-opportunity events
+(Appendix~\ref{app:proof_pairwise_lcb}); the frozen stress levels are in this
+region.  Aggregate coverage instead requires a stable regime.
 
 \begin{assumption}[Local score exchangeability within a certified stable regime]
 \label{ass:score-exchangeability}
@@ -1214,75 +1132,48 @@
  P\bigl(C^{\mathrm{LCB}}_t\le C_t\mid g\bigr)\ge 1-\alpha.
  \label{eq:agg_thm1}
 \end{equation}
-For $\alpha=0.05$ the right-hand side is $0.95$.  The theorem remains
-conditional on Assumption~\ref{ass:score-exchangeability} even when the
-algorithmic state is CERTIFIED.
+CERTIFIED is an operational state, not evidence for exchangeability.
 \end{theorem}
 
-\noindent\emph{Proof.}
-See the supplemental material.\hfill$\square$
-
-If Assumption~\ref{ass:score-exchangeability} holds, Theorem~\ref{thm:agg-lcb}
-bounds the Gate in that certified regime.
+The false-safe Gate consequence and arbitrary-drift impossibility boundary
+are proved in Appendix~\ref{app:agg_coverage_proofs}.  The stable-regime bound
+does not validate adaptive regime transitions.
 
 \section{Evaluation}
 \label{sec:evaluation}
 
-We evaluate RAVEN-MCS on risk interchangeability, RAVEN-Design versus
-the RAVEN-NoDesign setting, and component roles.
-
-\begin{itemize}
-    \item \textbf{Risk interchangeability:} does two-stage non-random selection
-    create a deployment-target mismatch, including under real taxi opportunity?
-    \item \textbf{RAVEN-Design and RAVEN-NoDesign:} does RAVEN-Design reduce
-    structural mismatch on the protocol-$R$ development table, and how do the
-    two settings trade off against each other and against prediction?
-    \item \textbf{Component roles:} which terms move structural diagnostics
-    versus prediction, and when is Design useful as a reconstruction factor?
-\end{itemize}
+We test the target--arrival distinction, attribute structural changes to
+aggregation mechanisms, and assess their prediction and deployment consequences.
 
 \subsection{Experimental Setup}
 \label{subsec:eval_setup}
 
-\subsubsection{Datasets and target semantics}
-
-Table~\ref{tab:datasets} summarizes the evaluated datasets.  SensorScope
-\cite{ingelrest2010sensorscope,barrenetxea2019sensorscope}\footnote{\url{https://doi.org/10.5281/zenodo.2654726}}
-and U-Air
-\cite{zheng2013uair}\footnote{\url{http://urban-computing.com/data}}
-provide the main comparison and ablation evidence and the coverage-stress audit.
-SensorScope and U-Air supply stationary sensing traces.  For both, the
-deployment-group mapping $h(i)$ is the spatial unit
-crossed with the four UTC time blocks (00--06, 06--12, 12--18, and 18--24),
-giving $220$ groups on SensorScope and $144$ on U-Air, with label-free
-masses.  Their opportunity strata $s(i)$ are finer: spatial identity
-$\times$ four time blocks $\times$ weekday/weekend.
-Accordingly, $h(i)$ and $s(i)$ retain the distinct semantics required by
-Section~\ref{subsec:selection_process}.
-
-NSW-Traffic
-\cite{tfnsw2024traffic}\footnote{\url{https://opendata.transport.nsw.gov.au/data/dataset/nsw-roads-traffic-volume-counts-api}}
-has 43 stations, four coordinate regions, and at most 32 strata.  It
-supplies the risk-interchangeability evidence and a separate four-region
-protocol ranking in the supplemental material.  Each comparison uses one
-consistent data-processing and target specification.
-
-T-Drive
-\cite{yuan2010tdrive}\footnote{\url{https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/}}
-is the public Microsoft Research taxi-trajectory sample; use follows that
-source's published terms.  Processed trajectories yield $R$ on $9994$
-cells and $5837$ taxis, with Complete-aligned $O$ and $U$ controls and
-the same four UTC groups $h(i)$.  The ranking uses the Design-off setting
-there; Design-on is also reported.
-
-City Scanner New York {PM}$_{2.5}$ and its Pilot~2 subset supply two further
-hybrid rankings in the supplemental material.  Occupied cells are the
-federated clients in both, $R$ is visit occupancy with RAVEN-Design used ($0$
-of $9343$ and $0$ of $10141$ train units), $O$/$U$ are controlled in the first,
-and in the second $O$ is measured from finite {PM}$_{2.5}$ in $[0,1000]$
-($1931$ of $14960$ occupied cell-slots unobserved), $R$ is visit occupancy on
-the union of kept-{PM} and {NO}$_2$ GPS streams, and $U$ is Complete-aligned
-($S_{\max}=5$).
+\subsubsection{Data, targets, and selection}
+Table~\ref{tab:datasets} gives chronological splits, groups, strata, and roles.
+SensorScope~\cite{ingelrest2010sensorscope,barrenetxea2019sensorscope} and
+U-Air~\cite{zheng2013uair} use station clients and spatial-unit $\times$ UTC-block
+deployment groups; their finer opportunity strata distinguish weekday/weekend.
+NSW-Traffic~\cite{tfnsw2024traffic} uses station clients and four coordinate
+regions.  These semi-synthetic blocks construct all three selection layers
+from frozen public/training information.  The main Complete-aligned condition
+tilts opportunity mass by $\exp(-1.25)$ against UTC blocks 2 and 3,
+observes with probability $.35$ versus $.1925$ there, and uses a device-tier
+compute/network process with $S_{\max}=5$ and at most four risk units per
+client-window.  Observation propensity is block-constant; usability is drawn
+once per client-window.  The compounding direction and always-on SensorScope/U-Air protocol $R$ are
+constructed rather than measured; Appendix~\ref{app:int_r} separately thins
+opportunity to intermittent occupancy.
+
+T-Drive~\cite{yuan2010tdrive} supplies real taxi opportunities from 5837 taxis
+on 9994 cells, with controlled Complete-aligned $O/U$ and four UTC target
+blocks.  City Scanner New York {PM}$_{2.5}$ uses occupied cells as clients,
+real visit-occupancy $R$, and controlled $O/U$.  Pilot~2 instead measures $O$
+from finite PM values in $[0,1000]$: 1931 of 14960 occupied cell-slots are
+unobserved.  Its risk set uses the union of retained PM and {NO}$_2$ GPS
+streams, with controlled $U$.  Thus no block measures real usable-update
+delivery.  The City Scanner and NSW targets are locally frozen region maps,
+not transferred station client--stratum lookups.  Protocol identities remain
+separate in all comparisons.
 
 \begin{table*}[t]
 \centering
@@ -1313,176 +1204,92 @@
 \end{tabular*}
 \end{table*}
 
-\subsubsection{Selection protocol and compared methods}
-
-The main comparison and ablation condition is \emph{Complete-aligned}: protocol $R$, $O$,
-and $U$ are all active and non-random in the same direction.  On
-SensorScope and U-Air, protocol $R$ is always-on.  A supplemental ranking
-thins that $R$ to the published T-Drive active fraction $0.425$.
-
-These layers are not measured in every block: opportunity is real on T-Drive and
-on the two City Scanner blocks, observation is measured on City Scanner Pilot~2
-only, and usable-update delivery is measured in no block.  The SensorScope,
-U-Air, and NSW-Traffic protocol blocks are semi-synthetic, with strata and target
-maps from the frozen public data while all three selection layers are constructed
-and labeled as controls.  There, opportunity is always-on with equal client mass
-and a factor $\exp(-1.25)$ against UTC blocks 2 and 3; observation is Bernoulli at
-rate $0.35$, reduced to $0.1925$ on the same two blocks; and the usable-update
-decision is a device-tier compute and network process that disadvantages those
-blocks, with $S_{\max}=5$ and at most four risk units per client-window.  Both
-parameters are constant within a stratum: the observation rate depends only on
-the UTC block, and the usable-update rate is drawn once per client-window for all
-its risk units.  The reported predictive gains describe this construction rather
-than the range attainable when selection varies at the unit level, and the
-compounding direction is therefore part of the construction rather than a
-measured property of these traces, and the structural-alignment results of
-Table~\ref{tab:main_effectiveness} are conditional on it.
-
-The main blocks assume within-stratum exchangeability,
-$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.  Paired methods
-share the same recorded selection trace.
-The five principal same-backbone baselines are
+\subsubsection{Methods and pairing}
+The deployable same-backbone family comprises count-weighted
 FedAvg-Window~\cite{mcmahan2017communication},
-FedAsync-Window~\cite{xie2019asynchronous},
-TimeAlign-Agg (our windowed time-aware adaptation of
-\cite{wang2026federated}),
-Local-H\'ajek (within-client inverse-probability / H\'ajek
-normalization~\cite{horvitz1952generalization,hajek1971comment}), and
-TwoStage-H\'ajek (sequential H\'ajek on opportunity and observation).  The main
-table additionally reports FedAU-Window, which adapts participation debiasing
-\cite{wang2024lightweight} to window-close aggregation (the
-windowed-adaptation specifications in the supplemental material), and
-ObsUse-Window, which applies the observation and usable-update corrections
-without Design, P2, or debt.  These baselines share the completion backbone
-and window-close protocol.  Inst-Cal and Debt-Cal expose
-the transition from reconstruction to calibration in the appendix.
-Central-All, Central-Delivered, and RAVEN-SimOracle are reference-only methods.
-The Design-on/off comparisons use a fixed setting throughout each run;
-the coverage-certificate audit is reported separately in the supplemental material.
-
-Design is
-worth $1.237\%$ of
-$\Delta_{\mathrm{group}}$ and $0.597\%$ of $\Delta_{c\text{-}s}$ on SensorScope at
-unchanged prediction, and costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$, $6.943\%$ of
-$\Delta_{\mathrm{group}}$, and $7.221\%$ of tail RMSE on U-Air while improving
-$\Delta_{c\text{-}s}$ by $4.990\%$, over the same 20 paired seeds
-(Section~\ref{subsec:eval_rq2}).  The choice is an endpoint-dependent deployment
-decision.  The support-compatible mixture-target diagnostic on SensorScope
-exceeds the no-harm threshold; the comparison table uses the specified
-deployment target.
-The principal comparison blocks use 20 paired seeds except the balanced control
-(five) and four ten-seed tables (the T-Drive ranking here, three in the
-supplement).  The separate learning diagnostics use three development seeds and
-one Uniform trajectory, as specified in Appendix~\ref{app:learning_capacity}.
-Those seeds capture algorithmic and EventTrace randomness, not independent
-cities.  No test result tunes the selection process, parameters, groups, or strata.
+FedAsync-Window~\cite{xie2019asynchronous}, the windowed TimeAlign adaptation
+of~\cite{wang2026federated}, Local-H\'ajek record correction, and TwoStage-H\'ajek
+opportunity/observation correction.  FedAU-Window adapts participation
+debiasing~\cite{wang2024lightweight}; ObsUse-Window corrects observation and
+usability without Design, P2, or debt.  Appendix~\ref{app:adapted_baselines}
+specifies these windowed adaptations.  Inst-Cal removes debt from full P2;
+Debt-Cal and reference-only Central-All, Central-Delivered, and RAVEN-SimOracle
+provide additional context, not deployable performance guarantees.
+
+Paired methods share EventTraces and within-stratum exchangeability
+$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.
+Design-on/off arms fix their setting throughout each run.  Principal comparisons
+use 20 paired seeds; the balanced control uses five, and T-Drive plus three
+supplemental rankings use ten.  Learning diagnostics use three development
+seeds and one Uniform trajectory.  Seeds represent model/trace randomness,
+not independent cities; no test result selects parameters, groups, or strata.
 
 \subsubsection{Metrics and statistical policy}
-
-Prediction is measured on the supported test units by
+On supported test units,
 \[
- \mathrm{RMSE}_{\mu}
- =
- \Bigl[\sum_{i\in\mathcal{I}_{\mathrm{test}}}
- \frac{\mu^{\mathrm{eval}}_{h(i)}}{n_{h(i)}}
- \bigl(\widehat Y_i-Y_i\bigr)^2\Bigr]^{1/2},
+\mathrm{RMSE}_{\mu}=\left[\sum_{i\in\mathcal I_{\mathrm{test}}}
+\frac{\mu^{\mathrm{eval}}_{h(i)}}{n_{h(i)}}(\widehat Y_i-Y_i)^2\right]^{1/2},
 \]
-where $n_g$ is the test-unit count in group $g$, $\boldsymbol\mu$ is the
-deployment-target marginal $\mu_g=\sum_{i:h(i)=g}\varpi_i^{\mathrm{tar}}$,
-$\boldsymbol\mu^{\mathrm{eval}}$ is the evaluation group mass normalized on
-the supported test units, and $\boldsymbol\mu^{\mathrm{blk}}$ aggregates
-$\boldsymbol\mu$ to the four UTC blocks.  On SensorScope and U-Air
-$\boldsymbol\mu^{\mathrm{eval}}$ is uniform on the supported test units, so
-$\mathrm{RMSE}_{\mu}$ is the unweighted pooled RMSE.
-The U-Air and NSW-Traffic targets are standardized by their training-split
-scales ($\sigma=17.363$ and $575.776$), so those $\mathrm{RMSE}_{\mu}$ entries
-are dimensionless while SensorScope is reported in physical units; ratios of two
-runs, such as $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$, are invariant
-to this standardization.  The test-split target means are $7.657$, $-0.807$ and
-$0.003$ on SensorScope, U-Air and NSW-Traffic, against training-split means of
-$0.301$, $0$, and $0$.  Fitted on the scored test labels, the test-fitted constant
-attains $\mathrm{RMSE}_{\mu}$ of $2.088$, $0.678$ and $1.007$; the training-mean
-predictor, which uses only the training split, attains $7.647$, $1.054$ and $1.007$.
-On SensorScope and U-Air the two differ by about $3.7\times$ and $1.6\times$, because
-their training and test target levels differ, so an absolute $\mathrm{RMSE}_{\mu}$
-there is read against the training-mean predictor; the relative quantities are
-invariant to that difference.  $\mathrm{WorstGroupRMSE}$ is the largest of the four
-UTC-block scores, each restricting the same weights to its own test units and
-renormalizing them inside the block (per-group table in the supplemental
-material), and the under-served-block score uses the block whose
-$\mu^{\mathrm{blk}}_b$ most exceeds opportunity mass
-(Section~\ref{subsec:eval_underserved}).  $\mathrm{Tail\_RMSE}$ applies that
-block functional to the frozen late-day blocks $2$ and $3$ ($12$--$24$~UTC),
-fixed before the runs rather than ranked by error or arrival ratio.  For the
-risk-interchangeability test only, $\mathrm{RMSE}_{\rho}$ replaces the evaluation
-weights by the atomic arrival weights of \eqref{eq:arrival_distribution}.
-Structural alignment is
-$\Delta_{\mathrm{group}}(R)=\left\|\overline{\boldsymbol\omega}_R-\boldsymbol\mu\right\|_1$
-and $\Delta_{c\text{-}s}$ in \eqref{eq:delta_cs}; smaller is better.
+where evaluation group mass is normalized on supported test units and $n_g$ is
+the group count.  SensorScope/U-Air use uniform atomic evaluation mass, hence
+pooled RMSE.  U-Air/Traffic use training scales $17.363/575.776$; their main
+RMSE entries are dimensionless, while SensorScope retains physical units.
+WorstGroupRMSE is the maximum of four UTC-block scores after within-block
+renormalization; Tail RMSE uses frozen blocks 2 and 3, not error-selected groups.
+Only the risk-semantic test replaces target weights by
+\eqref{eq:arrival_distribution} for $\mathrm{RMSE}_{\rho}$.
+Structural metrics are \eqref{eq:omega_bar}--\eqref{eq:delta_cs}.
+
+The training-mean predictors score $7.647/1.054/1.007$ on
+SensorScope/U-Air/Traffic.  Constants fitted to the scored test labels score
+$2.088/.678/1.007$ and are diagnostic references, not deployable baselines.
+Training/test target means are $.301/7.657$, $0/-.807$, and $0/.003$,
+respectively.  The old main models do not beat the training mean on the first
+two datasets; their structural differences do not establish effective absolute
+completion performance.
 
 \paragraph{Structural comparison convention.}
 \label{subsec:equivalence_band}
-Structural contrasts use Uniform weights $\alpha_{k,r}=1/|\mathcal A_r|$
-as a ruler.  Reference-side effects also use the closable gap from Uniform to
-the hindsight optimum with the same active sets, $M_r$, and $\mathcal C_r$,
-knowing all windows in advance.  Across all 20 seeds this gap is $3.44$ pp
-on SensorScope and $1.32$ pp on U-Air under always-on protocol $R$.
-In closable-gap units, the pre-registered practical band is $\pm0.10$:
-a contrast is inside only if its paired interval lies entirely within the band;
-a removed component is necessary only if the interval is entirely beyond it in
-the worsening direction.  This is a practical-significance convention, not a
-hypothesis test.  Both rules were fixed before the ladder runs in the released
-\texttt{w1/ladder\_v3/PREREG.md}.  Read-only report-half contrasts use a slightly
-different same-support optimum and cannot inherit all-seed trained-comparison
-band verdicts.
-
-All formal method comparisons are paired by seed, using the paired Wilcoxon
-protocol~\cite{wilcoxon1945individual} with Holm
-correction~\cite{holm1979simple} within the predeclared comparison families at
-$\alpha=0.05$; absolute differences below $10^{-12}$ are numerical ties, and
-tables report mean $\pm$ standard deviation.  Reported intervals are
-$10\,000$-draw seed-level paired percentile bootstrap intervals at seed
-$20261002$.  The Holm families used are the four ablation endpoints per dataset,
-the four registered prediction contrasts per dataset, the trained-rule contrasts
-within dataset and endpoint against the registered contrast list, and the
-$20$-seed $\mathrm{WorstGroupRMSE}$ family versus FedAU-Window and ObsUse-Window
-of the availability statement.  On four-block
-$\mathrm{WorstGroupRMSE}$, RAVEN-Design (SensorScope) and RAVEN-NoDesign (U-Air)
-are each compared with FedAU-Window and ObsUse-Window by a pre-specified $+0.5\%$
-mean-relative point-estimate tolerance on the paired relative differences, using
-TEST seeds $30011$--$30020$ for the ranking prose and the four 20-seed
-comparisons for the Holm tests.  This descriptive tolerance summarizes paired
-point estimates.  The U-Air comparison evaluates the Design-off setting.
-For P2, warning-affected allocations satisfy the recorded feasibility constraints;
-the supplemental audit evaluates constraint residuals and solver agreement.
-
-\subsection{Risk Interchangeability under Two-Stage Selection}
+Uniform is the structural ruler.  The closable gap to hindsight uses identical
+active sets, $M_r$, and $\mathcal C_r$ with all windows known: $3.44$ pp on
+SensorScope and $1.32$ pp on U-Air over all 20 always-on seeds.  In these
+normalized gap units, an interval wholly inside $\pm.10$ is within the
+pre-registered practical band; component necessity requires the interval wholly
+beyond it in the worsening direction.  This convention is not a hypothesis
+test.  The released \texttt{w1/ladder\_v3/PREREG.md} fixes both rules.
+Read-only report-half optima differ, so their verdicts are not interchangeable
+with all-seed trained comparisons.
+
+Tests are seed-paired Wilcoxon~\cite{wilcoxon1945individual}, with
+Holm~\cite{holm1979simple} correction at $.05$ within registered families:
+four ablation endpoints per dataset, four prediction contrasts per dataset,
+trained-rule contrasts within dataset/endpoint, and four 20-seed worst-group
+contrasts against FedAU/ObsUse.  Differences below $10^{-12}$ are numerical
+ties.  Tables give mean $\pm$ SD; intervals use 10000 seed-paired percentile
+bootstrap draws at seed 20261002.  The descriptive $+.5\%$ worst-group tolerance
+uses mean paired relative differences on TEST seeds 30011--30020 for ranking
+prose; Holm tests use all 20.  It is not a non-inferiority proof.
+Balanced-control, oracle-sensitivity, and concentration criteria retain their
+distinct thresholds below.
+
+\subsection{Risk Semantics and External Protocols}
 \label{subsec:eval_rq1}
 
-Under the balanced control, TimeAlign obtains mean deployment-target
-RMSE $7.7108\pm0.0272$ and RAVEN $7.7154\pm0.0337$ (mean relative
-degradation $0.0599\%$; one-sided 95\% upper bound $0.134\%$, below the
-3\% no-harm margin).  The balanced control evaluates the pre-specified no-harm
-criterion under aligned selection.
-
-We then test the premise of Proposition~1 on the NSW-Traffic
-risk-interchangeability experiment.  For each method and seed, write
-$\Delta_{\mu}=\mathrm{RMSE}_{\mu}^{\mathrm{aligned}}
--\mathrm{RMSE}_{\mu}^{\mathrm{balanced}}$ and
-$\Delta_{\rho}=\mathrm{RMSE}_{\rho}^{\mathrm{aligned}}
--\mathrm{RMSE}_{\rho}^{\mathrm{balanced}}$, with the pre-specified
-difference-of-differences $D_{\mathrm{aligned}}=\Delta_{\mu}-\Delta_{\rho}$,
-which would concentrate around zero if the two risk views reacted
-interchangeably to the same selection shift.  Instead,
-Fig.~\ref{fig:risk_noninterchangeability} shows a stable negative shift for all
-five methods: mean $D_{\mathrm{aligned}}$ ranges from $-0.0209$ to $-0.0214$,
-17--18 of the 20 paired seeds are negative for each method, and the paired
-Wilcoxon tests against zero give $p=4.83\times10^{-4}$--$5.86\times10^{-4}$.  The
-mean target-risk change is only about $8\times10^{-4}$ against a mean arrival-risk
-change of about $2.2\times10^{-2}$, so the same two-stage selection shift changes
-the arrival-weighted and deployment-target-weighted views by materially different
-amounts.  Complete method-level statistics are in the risk-semantic appendix of
-the supplemental material.
+The five-seed balanced control meets its $3\%$ no-harm margin: RAVEN versus
+TimeAlign degrades by $.0599\%$, with one-sided 95\% upper bound $.134\%$.
+Under complete-aligned NSW-Traffic, define target and arrival changes from
+balanced as $\Delta_\mu,\Delta_\rho$ and
+$D_{\mathrm{aligned}}=\Delta_\mu-\Delta_\rho$.
+Figure~\ref{fig:risk_noninterchangeability} gives mean $D$ from $-.0209$ to
+$-.0214$, 17--18 negative seeds per method, and paired
+$p=4.83\times10^{-4}$--$5.86\times10^{-4}$.  Target change is about
+$8\times10^{-4}$ versus $2.2\times10^{-2}$ arrival change.  This supports
+different risk responses, not RAVEN prediction superiority.
+The six-scenario matrix (Appendix~\ref{app:e2_layer_matrix}) finds Holm-significant
+arrival changes for all five methods under observation-only and complete-aligned
+selection, but target changes for zero and two methods respectively.  The other
+three non-balanced scenarios have no significant target contrast.  Compounding
+and cancellation depend on the construction.
 
 \begin{figure}[t]
 \raggedright
@@ -1496,29 +1303,13 @@
 \label{fig:risk_noninterchangeability}
 \end{figure}
 
-The six-scenario matrix separates the selection layers.  Relative to the
-balanced control, observation-only selection changes arrival RMSE for all five
-methods after the existing Holm correction, but changes target RMSE for none.
-Complete-aligned selection changes arrival RMSE for five methods and target
-RMSE for two.  Opportunity-only, usable-only, and complete-counteracting shifts
-have no Holm-significant target-RMSE contrast in this matrix.  The full ranges
-and counts in Appendix~\ref{app:e2_layer_matrix} show why the layers must be
-measured separately: compounding or cancellation is a property of a particular
-selection construction, not a universal direction of target-risk change.
-
-\noindent\textbf{Risk-interchangeability finding.}
-Under two-stage non-random selection, the arrival law need not be an
-interchangeable proxy for the deployment target, which supports Proposition~1.
-This test evaluates risk interchangeability for a fixed predictor.
-
-The same mismatch appears under real taxi opportunity.
-Fig.~\ref{fig:g3_tdrive} compares the public H1--H4 masses with the
-mass induced by processed T-Drive trajectories.  Real $R$ is intermittent (mean client active fraction $0.425$,
-burstiness $+0.38$, cell coverage $0.547$).  Four-block
-$\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$ is $0.142$ on T-Drive,
-$0.192$ on protocol SensorScope, and $0.278$ on protocol U-Air, all above
-$0.05$.  $O$ and $U$ remain Complete-aligned controls.
-Design is off on this block.
+Real T-Drive opportunity is intermittent: active fraction $.425$, burstiness
+$+.38$, and cell coverage $.547$.  Four-block opportunity--target TV is $.142$
+versus $.192/ .278$ in protocol SensorScope/U-Air, all above $.05$
+(Fig.~\ref{fig:g3_tdrive}).  With controlled $O/U$, RAVEN-NoDesign fails the
+$+.5\%$ worst-group tolerance against FedAU/ObsUse: paired relative
+$+2.39\%/+2.43\%$ (versus FedAvg $+.32\%$).  Its group gap equals FedAvg's;
+Design on worsens prediction, worst-group risk, and group mismatch.  Delivery remains controlled.
 
 \begin{figure}[t]
 \raggedright
@@ -1531,18 +1322,6 @@
 Table~\ref{tab:tdrive_hybrid}.}
 \label{fig:g3_tdrive}
 \end{figure}
-
-\noindent\textbf{Hybrid ranking under real taxi opportunity.}
-Table~\ref{tab:tdrive_hybrid} ranks the same windowed family under
-real taxi $R$ with Complete-aligned $O/U$ controls.
-FedAU-Window and ObsUse-Window remain strongest.
-RAVEN-NoDesign does not meet the $+0.5\%$ mean-relative
-tolerance versus those two (paired relative $+2.39\%$ and $+2.43\%$;
-versus FedAvg $+0.32\%$).  Design on raises
-$\mathrm{RMSE}_{\mu}$, worst-group RMSE, and $\Delta_{\mathrm{group}}$,
-as on U-Air.  RAVEN-NoDesign leaves the four-block
-structural gap unchanged relative to FedAvg; Section~\ref{subsec:eval_rq2}
-carries the paired Design-on/off contrasts.
 \begin{table}[!htbp]
 \centering
 \caption{T-Drive hybrid ranking under real taxi $R$
@@ -1570,141 +1349,47 @@
 \end{tabular}
 \end{table}
 
-\noindent\textbf{Independent four-region ranking on NSW-Traffic.}
-The heuristic is applied to a locally frozen four-region map
-with Design on, the ranking uses RAVEN-Design.
-That map is not the SensorScope/U-Air client--stratum lookup, so
-the NSW-Traffic four-region ranking table in the supplemental material is a
-protocol ranking, not a
-confirmation of that table or of a transferred support object.
-TwoStage-H\'ajek is lowest on $\mathrm{RMSE}_{\mu}$ and WorstGroupRMSE.
-FedAU-Window is lowest on $\Delta_{\mathrm{group}}$ ($0.0606$ versus
-$0.1048$ for RAVEN-Design).  RAVEN-Design
-stays within the descriptive $+0.5\%$ worst-group tolerance versus
-FedAU-Window and ObsUse-Window.
-
-\noindent\textbf{Hybrid rankings under City Scanner occupancy.}
-The City Scanner visit-occupancy ranking of the supplemental material ranks the
-same windowed family on occupied New York {PM}$_{2.5}$ cells, with real visit
-occupancy $R$, Complete-aligned $O/U$ controls, and RAVEN-Design on; its target
-map uses test-group shares $\mu_{h(i)}$ on training atoms with all four regions
-positive, not the station client--stratum lookup.  Paired mean relative error
-versus FedAU-Window and ObsUse-Window is $-1.71\%$ and $-1.34\%$ on
-$\mathrm{RMSE}_{\mu}$, and $-1.56\%$ and $-1.23\%$ on worst-group RMSE, while
-FedAvg-Window remains lowest on both prediction endpoints ($0.2379$ and
-$0.2489$) and RAVEN-Design is smallest on $\Delta_{\mathrm{group}}$ ($0.0706$).
-The Pilot~2 measured-$O$ ranking ranks the same family with measured $O$ and
-controlled $U$; TwoStage-H\'ajek is lowest on $\mathrm{RMSE}_{\mu}$ and
-WorstGroupRMSE, and RAVEN-Design is smallest on $\Delta_{\mathrm{group}}$ and
-lower than FedAU-Window, ObsUse-Window, and FedAvg-Window on both prediction
-endpoints (paired mean relative $-0.43\%$, $-0.45\%$, and $-0.65\%$ on
-$\mathrm{RMSE}_{\mu}$).  Clients are occupied cells rather than vehicles in both,
-and each comparison uses its specified occupancy and observation protocol.
-
-\subsection{Structural Alignment, Target RMSE, and Worst-Group Risk}
+The separate NSW four-region protocol ranking
+(Appendix~\ref{app:traffic_four_region}) favors TwoStage-H\'ajek on prediction
+and worst-group RMSE and FedAU on group mismatch ($.0606$ versus RAVEN's
+$.1048$); RAVEN stays within the descriptive worst-group tolerance against
+FedAU/ObsUse.  It does not validate a transferred station lookup.
+
+City Scanner visit occupancy (Appendix~\ref{app:cityscanner_nyc}) gives RAVEN
+relative RMSE gains of $1.71\%/1.34\%$ and worst-group gains of
+$1.56\%/1.23\%$ against FedAU/ObsUse, yet FedAvg is best on both prediction
+endpoints ($.2379/.2489$).  RAVEN has lowest group mismatch ($.0706$).
+With measured $O$ in Pilot~2 (Appendix~\ref{app:cityscanner_p2_measured_o}),
+TwoStage-H\'ajek remains best on both prediction endpoints; RAVEN has lowest
+group mismatch and beats FedAU/ObsUse/FedAvg in RMSE by
+$.43\%/.45\%/.65\%$.  These cell-client protocols are distinct from taxi-client
+T-Drive and from each other.  A trace dominating City Scanner's paired spread
+is retained: its recurrence over five model seeds identifies trace variability,
+not a model-training failure.  Power at the declared margin is only about $.15$
+over ten traces; the no-trace calculation is sensitivity only.
+The separate Design-cost analysis uses ten traces and three model seeds; its
+deletion-effect contrast remains unresolved.
+
+\subsection{Design and Main-Comparison Outcomes}
 \label{subsec:eval_rq2}
 
-On SensorScope, Design reduces
-$\Delta_{\mathrm{group}}$/$\Delta_{c\text{-}s}$ from FedAvg's $1.0558/1.2903$ to
-$1.0139/1.2644$ ($3.96\%/2.01\%$); the Design-off row gives $1.0265/1.2719$, so
-the two settings differ by $1.237\%$ and $0.597\%$ (paired, 20 seeds) while
-their $\mathrm{RMSE}_{\mu}$ point estimates are $7.9380$ and $7.9384$, with
-no Holm-significant prediction contrast.
-Four-block worst-group RMSE stays within the descriptive $+0.5\%$ worst-group
-tolerance versus FedAU-Window and
-ObsUse-Window (TEST $-0.01\%$ and $+0.05\%$; ALL20 $+0.02\%$ and $+0.10\%$).
-
-On U-Air the two settings separate: Design-off obtains
-$\Delta_{\mathrm{group}}=1.0165$ and $\mathrm{RMSE}_{\mu}=1.1131$ against
-$1.0924$ and $1.1954$ with Design on.  Fig.~\ref{fig:w1_design_gate} diagnoses
-the reversal, since estimated and oracle Design both worsen the primaries by
-about $7\%$ relative to No-Design, locating the reversal in the support
-compatibility of $\pi^{\mathrm{tar}}$.  Design improves
-$\Delta_{c\text{-}s}$ ($1.2334$ versus $1.2949$, $4.990\%$, $17.1\sigma$), so the
-U-Air choice is an endpoint-dependent trade rather than a dominated setting.  On
-the four-block worst-group endpoint the TEST mean relative differences versus
-FedAU-Window and ObsUse-Window are $+0.48\%$ and $+0.44\%$ (seeds
-$30011$--$30020$), and $+0.002\%$ and $+0.075\%$ over all $20$ table seeds; both
-slices stay within the descriptive $+0.5\%$ tolerance, the Holm tests on the
-$20$-seed family are not significant, and the comparison is a fallback
-evaluation.  Within the Design-on family,
-RAVEN-Design lowers worst-group RMSE by $2.46\%$ against TwoStage-H\'ajek on the
-TEST seeds ($10/10$), a family-internal comparison since both settings
-reconstruct target mass, and against the no-Design baselines RAVEN-NoDesign ties
-all six on prediction and worst-group RMSE, lowers $\Delta_{\mathrm{group}}$ by
-$2.4\%$ to $3.7\%$ and $\Delta_{c\text{-}s}$ by $1.4\%$ to $2.6\%$ against
-FedAvg, FedAsync, TimeAlign, FedAU and ObsUse, all $20/20$, and ties Debt-Cal on
-both.  Design-on reaches a worst-group RMSE of $1.2630$, compared with
-FedAvg's $1.1690$.
-
-Local-H\'ajek coincides with FedAvg-Window wherever the two keep the same active
-set, because the realized within-client H\'ajek weights are uniform on these
-traces; on U-Air the corresponding RAVEN bars are Design-on, not the
-RAVEN-NoDesign rows of Table~\ref{tab:main_effectiveness}.
-
-\noindent\textbf{Where the structural gain comes from.}
-The matched-support rule comparison in Table~\ref{tab:trained_rules} separates
-count weighting from selection correction.  On its common ruler, writing the
-count-weighted FedAvg group gap as
-$\Delta_{\mathrm{FedAvg}}-\Delta_{\mathrm{RAVEN}}
-=(\Delta_{\mathrm{FedAvg}}-\Delta_{\mathrm{unif}})
-+(\Delta_{\mathrm{unif}}-\Delta_{\mathrm{RAVEN}})$, it is $2.09$ pp of target
-mass on SensorScope ($95\%$ CI $[1.87,2.31]$), of which $1.44$ pp
-($68.96\%$, $[1.22,1.65]$) is already closed by uniform server weights
-alone and $0.65$ pp ($31.04\%$) requires the corrected reference; on U-Air the
-split is $1.47$ pp ($[1.18,1.75]$) $=1.22$ pp ($83.07\%$) $+0.25$ pp
-($16.93\%$).  FedAU-Window and ObsUse-Window decompose the same way on
-SensorScope ($77.58\%$ and $74.58\%$ count-to-uniform), while their U-Air active
-sets differ from the reference ruler and admit no decomposition.
-
-The projected reference accounts for the main reference-side increment in these
-comparisons.  The Design contrast is assessed separately on matched support.
-Replacing uniform weights by
-$\mathrm{Proj}_{\mathcal{C}_r}(\widehat{\boldsymbol\beta}_r)$ is worth $+0.768$ pp
-($[0.563,0.970]$) on SensorScope, above the $0.5$ pp practical line and stable
-across the two seed halves, and $+0.286$ pp ($[0.098,0.471]$) on U-Air, below
-that line and unstable across the halves ($+0.170$ tune, $+0.402$ report).
-Imposing $\mathcal{C}_r$ changes how the reconstruction is realized: against the
-unprojected corrected reference, which violates the recorded
-feasibility constraints and is worse than uniform weights,
-the projection is worth $+1.188$ pp ($[0.956,1.409]$) on SensorScope and
-$+1.399$ pp ($[1.019,1.782]$) on U-Air.  Removing the design factor costs
-$+0.922$ pp ($[0.721,1.141]$), outside the $\pm0.10$ band in the same units
-($-0.268$, $[-0.320,-0.214]$).  On U-Air the design-free variant does not keep
-the same active set and no value is reported for it.  The group-matching,
-variance, and staleness terms and the debt recursion
-($+0.0073$ pp, $[0.0064,0.0083]$, on SensorScope and $+0.0024$ pp on U-Air)
-have effect intervals inside the $\pm0.10$ equivalence band at
-$\lambda_g=1$, $\eta=0.01$
-(Section~\ref{subsec:equivalence_band}).  The group-matching term alone
-moves the client--stratum mismatch by $0.135$ pp on the wrong side on
-SensorScope.  Its effect on the group endpoint, $+0.039$
-($[+0.013,+0.063]$) in the closable-gap units of
-Section~\ref{subsec:equivalence_band}, is well inside the $\pm0.10$ band, and
-the variance and staleness terms move that group endpoint by at most $0.008$ in
-the same units.  The reference anchor gives the unique minimizer,
-and debt accounts for accumulated group under-service through the one-sided
-bound \eqref{eq:debt_bound}.  The anchor term is
-what makes the problem strictly convex, so the flat $\ell_1$ surface of
-Section~\ref{subsec:ceiling} does not make the solved point arbitrary.
+Table~\ref{tab:main_effectiveness} keeps both Design settings.  SensorScope
+Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$,
+with no Holm-significant prediction improvement.  Removing Design worsens the structural endpoints by $1.237\%/.597\%$,
+measured relative to the Design-on arm.
+U-Air reverses on group and prediction: removing Design improves group
+mismatch by $6.943\%$, RMSE by $6.885\%$, and tail RMSE by $7.221\%$, while
+worsening client--stratum mismatch by $4.990\%$.  Estimated and oracle Design
+track this reversal (Fig.~\ref{fig:w1_design_gate}); it is not simply an
+estimated-propensity failure.
 
 \begin{table}[!htbp]
 \centering
-\caption{Development table for the main comparison under always-on protocol $R$
-(mean $\pm$ std, 20 seeds; lower is better).
-The station traces use protocol-constructed $O$ and $U$ layers.
-Both Design settings are reported on both blocks, so the table is a
-within-dataset factor.
-WorstGroupRMSE is the maximum over the four UTC groups.
-On SensorScope both RAVEN settings, and on U-Air RAVEN-NoDesign, stay
-within the descriptive $+0.5\%$ worst-group tolerance versus those two
-(TEST seeds $30011$--$30020$); U-Air RAVEN-Design is outside it at $+7.9\%$ and $+8.0\%$.
-The RMSE superiority contrasts have Holm-adjusted $p>0.05$.
-Fitted on the scored test labels, the test-fitted constant attains
-$\mathrm{RMSE}_{\mu}$ of $2.088$ on SensorScope and $0.678$ on U-Air, while the
-training-mean predictor attains $7.647$ and $1.054$; the absolute column on both
-blocks is read against the training-mean predictor.
-A supplemental protocol table uses intermittent occupancy.}
+\caption{Always-on station protocol $R$, constructed $O/U$ (20 seeds,
+mean $\pm$ SD; lower is better).  Both Design arms are shown.  Worst-group
+uses four UTC blocks; descriptive tolerance and training-mean references are
+defined in Section~\ref{subsec:eval_setup}.  Prediction superiority is not
+Holm-significant.  INT-R is a separate supplemental protocol.}
 \label{tab:main_effectiveness}
 \scriptsize
 \setlength{\tabcolsep}{1pt}
@@ -1731,7 +1416,6 @@
 \bottomrule
 \end{tabular}
 \end{table}
-
 \begin{figure}[t]
 \raggedright
 \includegraphics[width=\columnwidth]{fig_w1_design_gate.pdf}
@@ -1748,183 +1432,37 @@
 \label{fig:w1_design_gate}
 \end{figure}
 
-Proposition~2 recovers compatible target moments or target-group mass for the
-\emph{ideal pooled} sequential correction under A1--A3.  The finite-window
-system evaluates that reference after feasibility-aware calibration in (P2).
-Proposition~\ref{prop:practical_plugin} applies when
-A5 and A6b hold and $\mathcal{A}_r$ is fixed, with the stabilization error
-\eqref{eq:eps_stab} carried explicitly, and A6a is the condition that makes that
-error vanish; the support-hypothesis audit in the supplemental material reports
-positive margins on the active support and active stabilization on both
-datasets.  The perturbation analysis therefore retains
-$\varepsilon_{\mathrm{stab}}$; A6b requires estimated-margin logs beyond this
-audit.  The main comparison evaluates the finite-window system after (P2).
-
-\noindent\textbf{Development-table findings.}
-On SensorScope, RAVEN-Design reduces structural mismatch relative to FedAvg and
-stays within the $+0.5\%$ worst-group tolerance.  On U-Air, RAVEN-NoDesign keeps
-the structural advantage against the no-Design baselines.  Prediction contrasts
-are evaluated in Table~\ref{tab:main_effectiveness}, and the under-served-block
-scores follow below.  Under intermittent occupancy (supplemental material),
-the $+0.5\%$ tolerance and the direction of the U-Air Design trade-off persist;
-the SensorScope $\Delta_{c\text{-}s}$ gap versus FedAvg approaches zero.
-
-\subsection{A Pre-Registered Under-Served-Block Check}
+SensorScope Design and U-Air NoDesign meet the descriptive worst-group
+tolerance against FedAU/ObsUse on TEST means ($-.01\%/+.05\%$ and
+$+.48\%/+.44\%$); corresponding all-20 means are $+.02\%/+.10\%$ and
+$+.002\%/+.075\%$.  U-Air Design instead exceeds it by $7.9\%/8.0\%$.
+The 20-seed Holm contrasts do not establish prediction superiority.
+Within its Design-on family, U-Air RAVEN improves worst-group RMSE versus
+TwoStage-H\'ajek by $2.46\%$ on TEST seeds, but its absolute $1.2630$ remains
+above FedAvg's $1.1690$.
+
+\paragraph{Under-served-block validation.}
 \label{subsec:eval_underserved}
-
-A validation-only endpoint also targets the under-served block rather than the
-intrinsically hardest one: after freezing the heuristic assignment we scored
-$g^{\star}=\arg\max_b(\mu^{\mathrm{blk}}_b-\pi^{\mathrm{opp},4}_b)$
-(SensorScope $g^{\star}=2$, gap $+0.114$; U-Air $g^{\star}=3$, gap $+0.172$),
-where a win requires mean paired relative RMSE versus FedAU-Window \emph{and}
-versus ObsUse-Window of at most $-0.5\%$.  The validation scores are
-$+0.05\%/+0.15\%$ and $-0.44\%/-0.27\%$, respectively, above the improvement
-threshold and within the no-harm threshold.  Evaluation stops at validation,
-and the descriptive $+0.5\%$ worst-group tolerance remains
-the only external endpoint statement.
-
-\subsection{What the Correction and Calibration Components Do}
+On validation only, aggregate target and opportunity mass to four UTC blocks
+and freeze $g^\star=\arg\max_b(\mu_b^{\mathrm{blk}}-
+\pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
+$.114/.172$.  The required improvement against both FedAU and ObsUse is
+$-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
+while meeting no-harm (Table~\ref{tab:underserved_block}); no test confirmation
+is claimed.  INT-R preserves the direction of U-Air's Design trade-off, while
+the SensorScope client--stratum advantage approaches zero.
+
+\subsection{Attributing Structural Gains and Component Trade-offs}
 \label{subsec:eval_rq3}
 
-The component-removal ablation starts from the fixed Design-on arm on both
-datasets and drops Design, Obs, Use, Inst, or Debt under the
-same Complete-aligned selection trace and paired seeds.
-Table~\ref{tab:e4_ablation} reports the relative change
-$\delta_{\mathrm{remove}}(M)
-=(M_{\mathrm{ablated}}-M_{\mathrm{full}})/M_{\mathrm{full}}\times100\%$,
-so a positive number means that removing the component worsens the metric; the
-magnified component-removal figure in the supplemental material visualizes the
-same one-factor removals, and all significance statements below use the
-pre-specified Holm families.
-
-\begin{table}[!htbp]
-\centering
-\caption{Component-removal ablation: relative change (\%) after removing one RAVEN component.
-Positive means the ablation worsens the metric; negative means it improves the
-metric.  $^\ast$ denotes Holm-adjusted $p<0.05$.}
-\label{tab:e4_ablation}
-\setlength{\tabcolsep}{3.5pt}
-\begin{tabular}{llrrrr}
-\toprule
-Dataset & Removed & $\Delta_{\mathrm{group}}$ &
-$\Delta_{c\text{-}s}$ & $\mathrm{RMSE}_{\mu}$ & Tail RMSE\\
-\midrule
-\multirow{5}{*}{SensorScope}
-& Design & $+1.237^\ast$ & $+0.597^\ast$ & $+0.005$ & $+0.005$\\
-& Obs    & $+0.096$       & $-0.070^\ast$ & $+0.012$ & $+0.011$\\
-& Use    & $+0.026$       & $+0.026$       & $+0.012$ & $+0.012$\\
-& Inst   & $-0.260$       & $+0.310^\ast$ & $-0.002$ & $-0.002$\\
-& Debt   & $+0.014^\ast$ & $+0.004^\ast$ & $<0.001$ & $<0.001$\\
-\midrule
-\multirow{5}{*}{U-Air}
-& Design & $-6.943^\ast$ & $+4.990^\ast$ & $-6.885^\ast$ & $-7.221^\ast$\\
-& Obs    & $+0.123^\ast$ & $+0.022$       & $-0.010$       & $-0.010$\\
-& Use    & $+0.014$       & $-0.014$       & $+0.025$       & $+0.026$\\
-& Inst   & $-0.089$       & $-0.143$       & $+0.143^\ast$ & $+0.149^\ast$\\
-& Debt   & $+0.004^\ast$ & $+0.002^\ast$ & $<0.001$ & $<0.001$\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-\paragraph{Design correction.}
-Removing Design worsens $\Delta_{c\text{-}s}$ by $0.597\%$ on SensorScope and
-$4.990\%$ on U-Air, both Holm-significant.  On U-Air the same ablation
-improves $\Delta_{\mathrm{group}}$ by $6.943\%$ and
-$\mathrm{RMSE}_{\mu}$ by $6.885\%$.  The U-Air ranking reports the fixed Design-off
-setting alongside Design on, with this endpoint trade-off
-(Fig.~\ref{fig:w1_design_gate}).  The $25.5\%$ figure is the realized always-on
-EventTrace occurrence share ($13040$ of $51200$ appearances), not an
-input of Algorithm~\ref{alg:window_close}, and is reported with the $\mathcal{A}_r$ overlap
-$51.6\%$.  Oracle Design tracks estimated
-Design.  SensorScope keeps Design on.  A 774-window check found identical
-R/O/U and registration events, with differences beginning only at the
-positive-weight/P2-support layer
-(supplemental material).
-
-\paragraph{Setting the Design factor.}
-The target-support gate is a block-level configuration rule evaluated on a
-specified training-unit catalogue.  Here $r$ indexes the experimental block,
-not the arriving window.  Write $n^{\mathrm{zero}}_r$ for catalogue units
-whose attached client--stratum carries zero public target mass and $n_r$ for
-all catalogue units.  The rule is
-\begin{equation}
-\rho_r=\frac{n^{\mathrm{zero}}_r}{n_r},
-\qquad
-D_r=\mathrm{on}\iff\rho_r=0 .
-\label{eq:design_gate}
-\end{equation}
-The rule returns on exactly when no catalogue unit sits on a stratum that the
-public target map declares empty.  Applying it before a window opens requires
-the catalogue and lookup to have been frozen and made available by then;
-current-window delivered units become available only after delivery.
-For the offline counts reported here, SensorScope, U-Air, and T-Drive use the
-client--stratum or stratum lookup.  The rule returns on for SensorScope and
-off for U-Air ($35.4\%$) and T-Drive ($47.4\%$), the settings those rankings use.
-NSW-Traffic and both City Scanner rankings are on because their public targets
-are four-region shares with every region positive.  That is a different lookup
-from the client--stratum statistic, and a zero on one map is not a zero on the
-other (supplemental material).  These offline rule outputs coincide with the
-settings displayed in the rankings.  The U-Air ablation measures $6.943\%$ of
-$\Delta_{\mathrm{group}}$ and $6.885\%$ of $\mathrm{RMSE}_{\mu}$ that Design costs
-on U-Air (Section~\ref{subsec:eval_rq2}).  Separately, an endpoint trade-off
-chart summarizes the measured on/off contrasts.
-Writing $M_{e,r}(D)$ for endpoint
-$e\in\mathcal{E}=\{\Delta_{\mathrm{group}},\Delta_{c\text{-}s},
-\mathrm{RMSE}_{\mu},\mathrm{Tail}\}$ under setting $D$, and weighting the four
-endpoints relative to their Design-on values,
-\begin{equation}
-\begin{aligned}
-\widehat J_r(D)&=\sum_{e\in\mathcal{E}}w_e\,\frac{M_{e,r}(D)}{M_{e,r}(\mathrm{on})},\\
-D_r^{\star}&=\arg\min_{D\in\{\mathrm{on},\mathrm{off}\}}\widehat J_r(D),
-\end{aligned}
-\label{eq:design_switch}
-\end{equation}
-In this measured trade-off chart, the two settings are indifferent when
-$w_c\,4.990=w_g\,6.943+w_\mu\,6.885+w_t\,7.221$, so a deployment that reads
-structure only keeps Design on if and only if $w_c/w_g>1.39$, one that reads
-$\mathrm{RMSE}_{\mu}$ alone keeps it off, and on SensorScope all four terms move
-the same way, so Design on is optimal for every weight vector.  The switch point
-is a retrospective decision chart for this U-Air ablation row, not a step
-that sets $D_t$ during the reported runs.  Table~\ref{tab:e4_ablation}
-records the Design-off trade-off on U-Air, the $4.990\%$
-$\Delta_{c\text{-}s}$ gain.  Proposition~\ref{prop:group_decomposition} supplies
-the block decomposition behind the $\mathrm{RMSE}_{\mu}$ entries of this
-trade-off, so a deployment can read the prediction side of the switch from the
-per-group scores it already reports, though that decomposition covers neither
-$\Delta_{\mathrm{group}}$ nor $\Delta_{c\text{-}s}$.
-
-\paragraph{Observation and usable-update correction.}
-Observation correction has a smaller, endpoint-specific effect: removing Obs
-worsens $\Delta_{\mathrm{group}}$ by $0.123\%$ on U-Air (Holm-significant) while
-its $\Delta_{c\text{-}s}$ and prediction effects are not significant, and on
-SensorScope no group change is significant while $\Delta_{c\text{-}s}$ improves
-by $0.070\%$.  In this Complete-aligned family, the Use ablation's core-endpoint
-contrasts have adjusted $p>0.05$ on both datasets.
-\paragraph{Instantaneous calibration and debt.}
-Inst also trades endpoints: on SensorScope removing it worsens
-$\Delta_{c\text{-}s}$ by $0.310\%$ (significant) while the group change is not
-significant after Holm correction, and on U-Air the structural changes are not
-significant while removing Inst worsens $\mathrm{RMSE}_{\mu}$ and tail RMSE by
-$0.143\%$ and $0.149\%$ (both $p_{\mathrm{Holm}}=0.0194$).  Removing debt
-significantly increases both
-structural mismatches on both datasets, but only by $0.0141\%/0.0040\%$ on
-SensorScope and $0.0043\%/0.0024\%$ on U-Air, far below the descriptive
-$+0.5\%$ worst-group tolerance that governs the external comparisons of
-Section~\ref{subsec:eval_rq2} on a different endpoint.  That matches the
-accounting of \eqref{eq:debt_bound}; its long-run alignment implication is
-conditional on $\|\mathbf Q_R\|_1=o(S_R)$.
-
-\noindent\textbf{Server-weight rules trained under matched support.}
-Table~\ref{tab:trained_rules} places structure, prediction, and cost on one
-comparison population.  All rules retain the Design-on correction pathway and
-the active clients of the full RAVEN arm.  Count weighting is proportional to
-observed counts on that matched support; Uniform uses $1/K_r$; projection uses
-$\arg\min_{\alpha\in\mathcal C_r}\|\alpha-\widehat\beta_r\|_2^2$.
-Projection with debt instead minimizes
-$-\kappa\mathbf Q_r^\top M_r\alpha+\tfrac12\|\alpha-\widehat\beta_r\|_2^2$
-with its own debt recursion and $\kappa=1000$, selected on tuning seeds.
-Inst-Cal removes debt from the full criterion.  Full RAVEN retains (P2).
-These rules retain their own names and objectives.
+\paragraph{Matched-support rules.}
+Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
+RAVEN's active support across count weighting, Uniform, reference projection,
+Inst-Cal, and full P2.  Its U-Air count row is not the unrestricted FedAvg row
+of Table~\ref{tab:main_effectiveness}.  Projection minimizes squared distance
+to $\widehat\beta_r$ on $\mathcal C_r$; the separate $\kappa=1000$ sensitivity
+rule adds $-\kappa\mathbf Q_r^\top M_r\alpha$ and its own debt recursion,
+with strength selected on tuning seeds.
 
 \begin{table*}[t]
 \centering
@@ -1959,120 +1497,159 @@
 \end{tabular*}
 \end{table*}
 
-Count-to-Uniform reduces group mismatch by $1.442$ pp on SensorScope and
-$1.221$ pp on U-Air.  Projection adds $0.768$ pp and $0.286$ pp, respectively.
-Full RAVEN then has $0.118$ pp more group mismatch than projection on SensorScope
-($p_{\mathrm{Holm}}=0.019$), while reducing client--stratum mismatch by $0.232$ pp.
-Its U-Air group contrast with projection is not significant.  Simple projection
-also takes less wall time: $19.9$ versus $27.1$ s on SensorScope and $8.8$ versus
-$15.3$ s on U-Air.  No registered prediction superiority contrast survives Holm
-correction (SensorScope $p_{\mathrm{Holm}}=1$; U-Air minimum $0.120$ under the
-corrected scores).  Better structural ordering therefore does not establish a
-prediction advantage for the full objective.
-
-The direct corrected reference $\alpha=\widehat\beta_r$ has a different evidence
-role.  The fixed-support structural readout gives group mismatch $1.03533$ on
-SensorScope and $1.11961$ on U-Air before projection; these allocations can
-violate caps or ESS.  The $1.188$ pp and $1.399$ pp projection improvements in
-Section~\ref{subsec:eval_rq2} describe that readout, without a trained prediction
-or runtime row for direct aggregation.  Design is a further independent
-contrast: the same-support projected on/off difference of $0.922$ pp on
-SensorScope is distinct from the $0.768$ pp projection--Uniform difference.
-The full end-to-end Design on/off comparison remains
-Table~\ref{tab:e4_ablation}; U-Air changes support and cannot supply a
-same-support Design attribution.
-
-The projection values describe numerical implementations of the stated rules,
-not exact optimizer certificates.  The existing independent projection audit
-finds a maximum endpoint discrepancy of $2.42\times10^{-5}$ in $\Delta$ units;
-its point-level optimality checks do not all pass.  Section~\ref{app:kappa_probe}
-reports this numerical scale separately from the measured rule effects.
-
-\subsection{Prediction Sensitivity within the Feasible Weight Class}
+Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
+reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
+count-to-Uniform and $.65$ pp remaining.  U-Air gives $1.47$ pp
+($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
+No analogous U-Air attribution is available for FedAU/ObsUse because their
+supports differ.
+
+Projection versus Uniform improves group mismatch by $.768$ pp
+($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$) on U-Air.
+The $.5$ pp practical line is cleared stably only on SensorScope, whereas
+U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.  Direct-reference structural
+readouts before projection are $1.03533/1.11961$, worse than Uniform and
+potentially infeasible under caps/ESS.  Projection improves those readouts by
+$1.188/1.399$ pp ($[.956,1.409]/[1.019,1.782]$); no trained prediction or
+runtime is attributed to direct aggregation.  Independently, same-support
+projected Design-on/off differs by $.922$ pp ($[.721,1.141]$) on SensorScope.
+This is not additive with projection--Uniform; U-Air changes active support
+and cannot identify that contrast.
+
+Full P2 has $.118$ pp more group mismatch than projection on SensorScope
+($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
+U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
+versus RAVEN's $27.1/15.3$ s.  Registered prediction superiority does not
+survive Holm correction (SensorScope $p=1$; U-Air minimum $.120$ under corrected
+saved-parameter scores).  Numerical endpoint discrepancy from the independent
+projection comparator reaches $2.42\times10^{-5}$ in $\Delta$ units, and
+point-level optimality checks do not all pass; this is not exact optimizer
+certification (Appendix~\ref{app:kappa_probe}).
+
+\paragraph{Component removal.}
+Table~\ref{tab:e4_ablation} removes one component from Design-on under paired
+Complete-aligned traces, reporting
+$100(M_{\mathrm{removed}}-M_{\mathrm{full}})/M_{\mathrm{full}}$.
+The Design row is the end-to-end trade-off above, not the same-support
+projection contrast.  Obs has endpoint-specific effects: U-Air group
+mismatch worsens $.123\%$ significantly, whereas SensorScope client--stratum
+mismatch improves $.070\%$ after removal.  Use has no adjusted-significant
+core endpoint.  Removing Inst worsens SensorScope client--stratum mismatch
+by $.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
+($p_{\mathrm{Holm}}=.0194$), without significant U-Air structural changes.
+Debt's structural effects are significant but tiny:
+$.0141\%/.0040\%$ on SensorScope and $.0043\%/.0024\%$ on U-Air.
+The frozen-strength projection/debt increment ($.0073$ pp on SensorScope,
+$.0024$ pp on U-Air), group, variance, and staleness effects lie inside the
+registered practical band.  This does not prove all P2 terms necessary;
+$\kappa=1000$ remains an independent sensitivity result.
+
+\begin{table}[!htbp]
+\centering
+\caption{Component-removal ablation: relative change (\%) after removing one RAVEN component.
+Positive means the ablation worsens the metric; negative means it improves the
+metric.  $^\ast$ denotes Holm-adjusted $p<0.05$.}
+\label{tab:e4_ablation}
+\setlength{\tabcolsep}{3.5pt}
+\begin{tabular}{llrrrr}
+\toprule
+Dataset & Removed & $\Delta_{\mathrm{group}}$ &
+$\Delta_{c\text{-}s}$ & $\mathrm{RMSE}_{\mu}$ & Tail RMSE\\
+\midrule
+\multirow{5}{*}{SensorScope}
+& Design & $+1.237^\ast$ & $+0.597^\ast$ & $+0.005$ & $+0.005$\\
+& Obs    & $+0.096$       & $-0.070^\ast$ & $+0.012$ & $+0.011$\\
+& Use    & $+0.026$       & $+0.026$       & $+0.012$ & $+0.012$\\
+& Inst   & $-0.260$       & $+0.310^\ast$ & $-0.002$ & $-0.002$\\
+& Debt   & $+0.014^\ast$ & $+0.004^\ast$ & $<0.001$ & $<0.001$\\
+\midrule
+\multirow{5}{*}{U-Air}
+& Design & $-6.943^\ast$ & $+4.990^\ast$ & $-6.885^\ast$ & $-7.221^\ast$\\
+& Obs    & $+0.123^\ast$ & $+0.022$       & $-0.010$       & $-0.010$\\
+& Use    & $+0.014$       & $-0.014$       & $+0.025$       & $+0.026$\\
+& Inst   & $-0.089$       & $-0.143$       & $+0.143^\ast$ & $+0.149^\ast$\\
+& Debt   & $+0.004^\ast$ & $+0.002^\ast$ & $<0.001$ & $<0.001$\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+\paragraph{Configuration and support.}
+For a specified training-unit catalogue, $r$ indexes the experimental block,
+$n_r$ counts units and $n_r^{\mathrm{zero}}$ counts those with an attached
+zero-target client--stratum.  The offline check is
+\begin{equation}
+\rho_r=\frac{n^{\mathrm{zero}}_r}{n_r},
+\qquad
+D_r=\mathrm{on}\iff\rho_r=0 .
+\label{eq:design_gate}
+\end{equation}
+It returns on for SensorScope and off for U-Air/T-Drive (zero shares
+$35.4\%/47.4\%$).  NSW and City Scanner's all-positive region lookups return
+on, but are different objects.  Because configuration is frozen before opening, its catalogue and public lookup
+must already exist; neither current outcomes nor the coverage Gate switches it.  The 774-window
+audit holds R/O/U and registration fixed; differences begin at positive-mass
+support.  U-Air's $25.5\%$ occurrence share and $51.6\%$ active-set overlap
+describe that trace, not a configuration input.
+For measured endpoint values $M_{e,r}(D)$,
+$e\in\mathcal E=\{\Delta_{\mathrm{group}},\Delta_{c\text{-}s},
+\mathrm{RMSE}_{\mu},\mathrm{Tail}\}$, and nonnegative weights $w_e$, the
+retrospective chart
+\begin{equation}
+\begin{aligned}
+\widehat J_r(D)&=\sum_{e\in\mathcal{E}}w_e\,\frac{M_{e,r}(D)}{M_{e,r}(\mathrm{on})},\\
+D_r^{\star}&=\arg\min_{D\in\{\mathrm{on},\mathrm{off}\}}\widehat J_r(D),
+\end{aligned}
+\label{eq:design_switch}
+\end{equation}
+has U-Air structural indifference at $w_c/w_g=1.39$ when only structural terms
+are weighted.  It is not the online rule used in the experiments.
+Zero-target share is not a Design-cost predictor: masking SensorScope target
+keys raises it to $.388$ with cost at most $.175\%$, while U-Air costs
+$6.6\%$--$7.5\%$ over shares $.354$--$.466$.
+
+\subsection{Prediction Sensitivity and Adjustment Geometry}
 \label{subsec:ceiling}
 
-Two empirical comparisons assess prediction sensitivity of the evaluated
-server-weight configurations.  First, compare FedAvg-Window with the evaluated
-true-margin configuration using
-$H=(\mathrm{RMSE}_{\mu}(\text{FedAvg})-\mathrm{RMSE}_{\mu}(\text{oracle}))/
-\mathrm{RMSE}_{\mu}(\text{FedAvg})$.
-The grid varies opportunity tilt, tail observation scale, model capacity, and
-target, with a $0.5\%$ practical effect criterion.  SensorScope's six estimates
-lie in $[-0.03\%,+0.08\%]$, with paired minimum detectable effects of
-$0.17$--$0.36$ percentage points.  On U-Air, 270 runs and 45 traces over 20 seeds
-give $|H|\le0.217\%$ and intervals containing zero; the $0.70$--$0.80$ point
-detectable effects leave a $0.5\%$ improvement unresolved.  These are measured
-contrasts for specific oracle-margin configurations, not upper bounds over all
-weights in $\mathcal C_r$.
-
-The original block-constant observation model also leaves local H\'ajek
-weights uniform whenever the retained records share its correction factor.
-A separate within-stratum construction varies the observation propensity with
-the time-index tercile inside each stratum, while preserving the block mean.
-Mean distinct propensities per stratum rise from one to $2.76$ on SensorScope
-and $2.83$ on U-Air.  This is covariate-dependent constructed selection, rather
-than a direct dependence on an unobserved response.  The construction and
-information interface are detailed in Appendix~\ref{app:f1_mechanism}.
-
-The second quantity is the cost of estimating the margins, measured inside one
-calibrated member so that only the observation and usable-update margins change.
-Replacing those two margins with their true values moves $\mathrm{RMSE}_{\mu}$ by
-$-0.008\%$ on SensorScope (oracle minus calibrated,
-$95\%$ interval $[-0.041\%,+0.025\%]$) and by $+0.040\%$ on U-Air
-($[-0.090\%,+0.171\%]$), paired over $20$ seeds.  Every member we evaluate stays
-inside $0.08\%$ on SensorScope under the same substitution, and on U-Air three of
-the four stay inside $0.3\%$ while TwoStage-H\'ajek sits $2.04\%$ above the
-oracle-margin member ($[1.33\%,2.75\%]$).  The substitution is not small before
-aggregation: the estimated reference differs from the true-margin reference by a
-median of $0.077$ in $\ell_1$ and by up to $1.15$, and it reaches the aggregate
-composition at the same order for the members whose weights normalize that
-reference.  Accurate margin estimates are therefore not what holds the prediction
-endpoint flat, since three of the four members are insensitive to a large change
-in their own aggregation weights.  At a fixed window state,
-\eqref{eq:g4_comp} bounds the aggregate difference
-induced by the margin estimates to $\|M_r\|_2$ times the reference perturbation
-controlled by Proposition~\ref{prop:practical_plugin}; a metric-level bound of
-the same form would require a transfer assumption between the training and the
-deployment distributions, which Proposition~2 does not make, so prediction sensitivity remains an empirical measurement at the detection scales stated.
-
-\noindent\textbf{Active-set geometry and prediction sensitivity.}
-The active-client count bounds, but does not by itself determine, the dimension
-of the feasible weight set.  With
-the frozen $E_{\min}=3$, the bound in \eqref{eq:Cr} is
-$\overline E_r=\min(3,K_r)$, and since $\|\boldsymbol\alpha\|_2^2\ge1/K_r$ on
-the simplex with equality only at $\mathbf 1/K_r$, a window with $K_r\le3$
-admits the uniform weights alone.  Over the $20$ frozen seeds, $78.6\%$ of the
-$1877$ active windows on SensorScope have $K_r\le3$; on U-Air the share is
-$90.2\%$ of $1402$ windows with Design on and $79.0\%$ of $1515$ with Design
-off.  In those windows (P2) returns uniform weights whatever its objective.  The
-projection over uniform server weights is worth $+0.768$ and $+0.286$~pp at the
-group endpoint.  The target
-leaves little room at the criterion level as well: its largest group carries
-$0.53\%$ of the mass on SensorScope ($220$ groups) and $0.79\%$ on U-Air
-($144$ groups).  The factor that moves $\mathrm{RMSE}_{\mu}$ by several points
-on U-Air is Design, and it acts on which client windows are active, as the two
-window counts show, rather than on the weights inside a window.
-Over the $3279$ audited active windows, the feasible range of
-$\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ has median $10^{-13}$.
-This is the $\ell_1$ evaluation geometry, not constancy of the squared
-$\ell_2$ term in P2.  Limited group support can restrict observable alignment
-even when feasible weights differ.  This main-comparison audit is separate
-from the development geometry below.
-NSW-Traffic is the block on which most windows have $K_r>3$; its prediction
-measurement is in Section~\ref{subsec:limitations}.
-
-\paragraph{Does a concentrated target expose a larger prediction gain?}
-The NSW-Traffic target-concentration comparison keeps the original backbone,
-two local steps, and server update.  It multiplies the prior mass of a
-pre-specified coordinate region (region1) by $\kappa_{\mathrm{tar}}$ and
-renormalizes, with a single-region limit.  This concentration parameter differs
-from the debt-strength $\kappa$ in Table~\ref{tab:trained_rules}.
-Table~\ref{tab:target_concentration} compares Local-H\'ajek control with
-RAVEN-SimOracle, which uses the generator's observation probabilities and
-Monte Carlo usable-update probabilities with the full calibration pathway.
-The $\kappa_{\mathrm{tar}}=1$ pair reuses existing runs; the $5$ pair comes from
-the four-arm concentration experiment, and the $10$ and single-region pairs
-come from two further target conditions, each with 20 paired seeds.
+For evaluated true-margin configurations, define
+$H=(\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})-\mathrm{RMSE}_{\mu}(\mathrm{oracle}))/
+\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})$.
+Varying opportunity tilt, tail observation, capacity, and target gives
+SensorScope estimates in $[-.03\%,+.08\%]$ with detectable effects
+$.17$--$.36$ percentage points.  U-Air's 270 runs/45 traces give
+$|H|\le.217\%$ with intervals containing zero; $.70$--$.80$ point detection
+leaves the $.5\%$ practical improvement unresolved.  These configurations
+are not optimal upper bounds over all feasible weights.
+
+Inside one calibrated member, replacing estimated observation/usability margins
+by truth changes RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and
+$+.040\%$ ($[-.090,+.171]\%$) on U-Air over 20 paired seeds.  Three U-Air
+members stay within $.3\%$, but TwoStage-H\'ajek lies $2.04\%$ above its
+oracle-margin counterpart ($[1.33,2.75]\%$).  Reference perturbations are not
+uniformly small (median $\ell_1=.077$, maximum $1.15$); their weak prediction
+response cannot be explained solely by accurate margin estimates.  Fixed-state
+composition stability in \eqref{eq:g4_comp} is not a prediction guarantee.
+The local-weight audit finds constant realized weights in the original blocks;
+F1 introduces time-tercile covariates while preserving block observation means
+(Appendix~\ref{app:f1_mechanism}).  Different propensities do not ensure
+different clipped weights or prediction gains; F1 is not general MNAR evidence.
+
+With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
+In the old main protocol this covers $78.6\%$ of 1877 SensorScope windows,
+$90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
+windows.  Largest target groups carry only $.53\%/.79\%$.
+Across 3279 audited active windows the feasible L1 group-distance range has
+median $10^{-13}$; this does not make the squared L2 term in P2 constant.
+Weight freedom, composition freedom, and prediction sensitivity are distinct.
+
+\paragraph{Target concentration.}
+Table~\ref{tab:target_concentration} multiplies region1's prior mass by
+$\kappa_{\mathrm{tar}}$ and renormalizes, keeping the original backbone, two
+local steps, and server rule.  Local-H\'ajek is compared with RAVEN-SimOracle
+using generator observation probabilities and Monte Carlo usability
+probabilities through the full calibration path.  The baseline pair is reused;
+$5$ comes from the four-arm experiment; $10$ and the single-region limit are
+two further conditions, each with 20 paired seeds.  This target multiplier
+is unrelated to debt strength $\kappa$.
 
 \begin{table}[t]
 \centering
@@ -2095,23 +1672,23 @@
 \end{tabular}
 \end{table}
 
-The contrast grows with concentration, reaching $0.0970\%$ at the single-region
-target.  Its interval excludes zero and its mean exceeds the reported MDE at
-$\kappa_{\mathrm{tar}}=10$ and the limit.  At $5$, the interval excludes zero
-but the mean remains below its MDE.  All four effects remain below this
-experiment's pre-specified $2\%$ practical criterion.  Thus target dilution
-alone does not explain the small gain for this evaluated oracle and update
-rule; the measurement does not optimize over the entire feasible weight class.
-
-\paragraph{Weight freedom, composition freedom, and adjustable mass.}
-A separate three-seed development geometry audit reconstructs feasible sets
-without evaluating predictions.  Table~\ref{tab:development_geometry} retains
-its own window population, independently of the older percentages above.
-With $W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
-\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable target mass is the sum
-of $\mu_g$ over positive-target groups with $W_{r,g}\ge.01$.
-This distinguishes a non-singleton weight set from a direction that moves group
-composition and from the amount of target mass that can move.
+The oracle contrast increases to $.0970\%$ at the limit.  At $10$ and the
+limit its interval excludes zero and its mean exceeds MDE; at $5$ only the
+former holds.  All four effects remain below this experiment's $2\%$
+practical criterion.  Target dilution alone therefore does not explain the
+small gain of this oracle/update configuration.
+
+\paragraph{Separate development geometry and learning.}
+Table~\ref{tab:development_geometry} uses three new development seeds, not the
+old window population above.  For feasible group range
+$W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
+\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
+where $W_{r,g}\ge.01$.
+Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
+composition direction, but only $4.651\%$ mean adjustable target mass.
+References violate constraints in $59.02\%$, with mean projection distance
+$.067487$.  Appendix~\ref{app:development_geometry} varies caps/ESS.
+This is geometry, not a participation intervention or prediction experiment.
 
 \begin{table}[t]
 \centering
@@ -2132,165 +1709,72 @@
 \end{tabular}
 \end{table}
 
-For Traffic's 183 sorted-client subsets with $K=8$, ESS minimum 4, and cap .25,
-all have a composition direction of rank at least one and at least two groups
-with $W_{r,g}\ge.01$, but mean adjustable target mass is only $4.651\%$.
-The reference violates the constraints in $59.02\%$ of these subsets and the
-mean projection distance is $0.067487$ in client-weight $\ell_2$ units.
-Appendix~\ref{app:development_geometry} gives the cap/ESS sensitivity.  Selecting
-subsets from natural windows is a geometry diagnostic, not a controlled
-participation intervention or evidence of a prediction gain.
-
-\subsection{Deployment Conditions and Evaluation Scope}
+Longer-budget learning uses development validation, physical units, and
+seeds 41001--41003, separately from these test comparisons
+(Appendix~\ref{app:learning_capacity}).  Common-NDMF Central-delivered improves
+on applicable simple baselines for Traffic and SensorScope, but not U-Air;
+those validation gains do not belong to RAVEN.  The single federated Traffic
+Uniform trajectory is not yet plateaued.  Backbone capacity, training budget,
+and aggregation benefits therefore remain separate questions.
+
+\subsection{Update-Rule Sensitivity and Coverage Scope}
 \label{subsec:limitations}
 
-RAVEN-Design and the City Scanner blocks report Design on, and RAVEN-NoDesign
-reports Design off on U-Air and T-Drive ($\widehat\zeta^{o}=1$).  On
-Table~\ref{tab:main_effectiveness}, SensorScope RAVEN-Design and U-Air
-RAVEN-NoDesign stay within the descriptive $+0.5\%$ TEST tolerance versus
-FedAU-Window and ObsUse-Window; the RMSE Holm contrasts are reported with the table.
-Table~\ref{tab:tdrive_hybrid} is outside the tolerance.  The
-NSW-Traffic four-region, City Scanner visit-occupancy, and Pilot~2 measured-$O$
-rankings of the supplemental material use their respective targets and
-selection protocols.  A1--A2 specify support and confounding
-boundaries.  Stabilization is active on the released traces, so
-Proposition~\ref{prop:practical_plugin} is used in its
-$\varepsilon_{\mathrm{stab}}$ form \eqref{eq:eps_stab}.  The City Scanner
-non-inferiority comparison has power about $0.15$ at the declared margin over
-ten traces.  The single City
-Scanner trace that dominates the paired spread is a trace-level outlier
-reproduced across five model seeds rather than a training instability, so it is
-retained; the no-trace recomputation is a sensitivity only.  The reported
-Design cost is estimated over $n=10$ traces and $r=3$ seeds; the deletion-effect
-contrast remains unresolved at that sample size.
-The $25.5\%$ figure is
-EventTrace occurrence ($13040$ of $51200$).  The supplemental material reports
-target coverage on its specified target map.  On the fixed coverage-stress
-oracle, pooled CERTIFIED validity is $0.959$ and U-Air $a=1.00$ is $0.750$.
-The stable-regime theorem assumes exchangeability within a certified regime;
-coverage across adaptive RESET/CERTIFIED transitions requires separate
-validation.  Design is fixed by configuration, while the coverage Gate is
-evaluated as a diagnostic.  Equation~\eqref{eq:design_gate} reports the
-separate offline target-support rule.
-
-Three measurements characterize the relationship between aggregation and prediction.
-Arrival-weighted validation misstates deployment risk, by $-4.11\%$ to
-$-4.12\%$ on SensorScope across the nine federated configurations we score,
-RAVEN with and without Design included, and by $+0.27\%$ to $+0.62\%$ on U-Air.
-It nevertheless selects the same configuration as the deployment target on all
-$20$ seeds of both datasets, so on these blocks the misstatement does not change
-a selection.
-Masking up to $40\%$ of the positive target keys on SensorScope, and with them
-the deployment target, raises $\rho_r$ of \eqref{eq:design_gate} from $0$ to
-$0.388$ without a prediction cost of Design above $0.175\%$, while on U-Air the
-cost stays at $6.6\%$--$7.5\%$ for $\rho_r$ between $0.354$ and $0.466$.  The
-statistic is therefore a zero-target support check for the rule, not a predictor of the
-size of its cost.
-
-On NSW-Traffic a window carries $12.1$ active clients on
-average.  In the fifteen-seed comparison below, $15.1\%$ of active windows have
-$K_r\le 3$, so the feasible set does not force uniform weights.  Under the
-original server step the four frozen federated members, the oracle-margin member
-included, agree on $\mathrm{RMSE}_{\mu}$ within $0.002\%$.  That step applies
-$\eta$ times the step-normalized client update once per window, one gradient
-step at any local budget, and raising the budget from $2$ to $20$ leaves window
-FedAvg $2.8\%$--$3.0\%$ above a centralized reference that is itself Adam at
-$10^{-3}$ over the pooled training units for $20$ minibatch steps of $32$, so the
-gap compares two update rules and step budgets rather than two aggregators alone.
-The federated parameters move $0.26\%$--$0.40\%$ of their initial norm over those
-runs.
-
-Replacing only this server step by Adam ($\beta_1=0.9$,
-$\beta_2=0.99$, $\tau=10^{-3}$) with step size $0.003$, one update per window,
-on fifteen seeds not used to choose that step size, puts the paired headroom of
-the oracle-margin weights relative to window FedAvg at $-1.49\%$, with bootstrap
-interval $[-5.42\%,+1.76\%]$ and an $80\%$ minimum detectable effect of $5.80\%$.
-The interval contains zero; the detectable effect is $5.80\%$, compared with
-the $0.5\%$ practical threshold of Section~\ref{subsec:ceiling}.  Those fifteen runs score
-$\mathrm{RMSE}_{\mu}$ at
-$0.967$ for window FedAvg and $0.973$ for the oracle-margin arm on average, in
-$[0.659,1.572]$ and $[0.795,1.459]$, against $1.007$ for the test-fitted constant on
-the same test weights, where the training-mean predictor takes the same value;
-both arm means therefore sit below that reference.  Scored on the same runs after that
-prediction contrast, the oracle-margin weights reduce $\Delta_{\mathrm{group}}$ by
-$0.0079$
-$[0.0051,0.0110]$ and $\Delta_{c\text{-}s}$ by $0.0099$ $[0.0067,0.0132]$.
-The original-step and Adam comparisons measure the evaluated oracle-margin
-configuration at their respective detection scales.  Separate longer-budget
-learning diagnostics in Appendix~\ref{app:learning_capacity} distinguish backbone
-capacity from aggregation effects, using development validation data and physical
-units rather than the test scores above.
-
+NSW-Traffic has mean $K=12.1$; only $15.1\%$ of active windows in a separate
+15-seed comparison force Uniform.  Under the original server step four
+federated members, including oracle margins, agree in RMSE within $.002\%$.
+Increasing local steps from 2 to 20 leaves FedAvg $2.8\%$--$3.0\%$ above
+a centralized Adam reference ($10^{-3}$, 20 minibatch steps of 32).
+This combines optimizer and budget differences, not aggregation alone;
+federated parameters move only $.26\%$--$.40\%$ of their initial norm.
+
+Replacing only the server step with Adam ($\beta_1=.9$, $\beta_2=.99$,
+$\tau=10^{-3}$, rate $.003$, one update per window) on 15 seeds unused for
+rate selection yields oracle-margin headroom versus FedAvg of $-1.49\%$
+($[-5.42,+1.76]\%$), with 80\% MDE $5.80\%$.  This wide interval does not
+establish equivalence at $.5\%$.  Mean RMSE is $.967/.973$, ranges
+$[.659,1.572]/[.795,1.459]$, below the $1.007$ constant reference mean.
+On those same runs oracle weights reduce group/client--stratum mismatch by
+$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$).  Structural benefit
+thus coexists with unresolved prediction value under the changed update rule.
+
+Arrival-weighted validation misstates target risk by $-4.11\%$ to $-4.12\%$
+on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects the same
+configuration on all 20 seeds.  Support audits find positive true margins
+on active support, not full identification; clipping is active and missing
+estimated-margin logs prevent A6b verification (Appendix~\ref{app:a5_a6_audit}).
+The fixed coverage-stress candidate gives pooled CERTIFIED validity $.959$
+but only $.750$ for U-Air at $a=1$; its complete cells and transition behavior
+remain in Appendix~\ref{app:certificate_audit}.  Adaptive RESET/CERTIFIED
+transitions lack a validity proof.  These diagnostic records, from the older
+coverage-controlled candidate, do not validate configured Design or P2
+prediction performance.  Real delivery $U$ remains unmeasured in all blocks.
 
 \section{Conclusion}
 \label{sec:conclusion}
 
-RAVEN-MCS connects a selection-corrected sensing-unit reference to the
-constrained client mixtures available in an asynchronous window.  Its formulation
-separates the deployment target, sequential arrival law, and feasible composition;
-the ideal reconstruction and fixed-window stability results specify different
-parts of that connection.  Debt carries under-service across windows, with
-long-run alignment conditional on its growth rate.
-
-The experiments separate the changes due to Uniform, reference projection,
-Design, and the full criterion.  On SensorScope, projection improves group
-mismatch by $0.768$ pp relative to Uniform; the distinct same-support projected
-Design-on/off contrast is $0.922$ pp.  Projection is faster than full RAVEN and
-has lower group mismatch on SensorScope, while the full criterion improves the
-client--stratum endpoint.  These structural differences do not establish
-consistent prediction gains.  Concentrated-target and geometric diagnostics
-further distinguish target mass, feasible adjustment, and learning sensitivity.
-Population reconstruction and finite-window calibration are therefore separate
-requirements whose task value must be assessed under the actual learning and
-selection protocol.
+RAVEN-MCS connects a sensing-unit reference reconstructed across sequential
+selection to the constrained client mixtures available in an asynchronous
+window.  Ideal moment recovery and fixed-window calibration stability address
+different parts of this connection, with long-run alignment conditional on
+debt growth.  The experiments separate structural changes already explained by
+Uniform from reference projection and independent Design effects.  Simple
+projection is faster and can improve group alignment over full RAVEN, while
+the full criterion improves another structural endpoint.  These differences do
+not establish consistent prediction gains.  Target concentration, geometry,
+update-rule, and learning diagnostics show why deployment-target alignment must
+be evaluated jointly with task performance and cost under the actual protocol.
 
 \section*{Data and Code Availability}
-SensorScope, U-Air, NSW-Traffic, and T-Drive are public and cited in
-Section~\ref{subsec:eval_setup}.  T-Drive use follows the published
-Microsoft Research terms~\cite{yuan2010tdrive}.
-City Scanner New York {PM}$_{2.5}$~\cite{wang2023cityscanner}
-(Zenodo 10.5281/zenodo.7961851, CC BY 4.0) is ranked in
-the City Scanner visit-occupancy and Pilot~2 measured-$O$ ranking tables of the
-supplemental material.
-The bundle \texttt{RAVEN\_MCS\_PUBLIC\_REPRO\_R1} contains paired seeds,
-frozen targets, EventTraces, tabulated figure and table sources,
-\texttt{SCD\_PHI.csv}, canonical Table~II
-(\texttt{TABLE\_II\_MAIN\_EFFECTIVENESS.csv}),
-the $20$-seed $\mathrm{WorstGroupRMSE}$ Holm family versus FedAU-Window and
-ObsUse-Window, ALL20/TEST10 slice relatives, the T-Drive hybrid ranking CSVs,
-and the NSW four-region, City Scanner visit-occupancy
-(\texttt{cityscanner/}), and Pilot~2 measured-$O$ (\texttt{cityscanner\_p2/})
-files.  The bundle provides EventTraces and tabulated evidence for reconstructing
-the reported cells.  The \texttt{w1/} subtree holds the ladder,
-frontier, trade-off, and audit artifacts behind the structural, band, and
-$\varepsilon_{\mathrm{impl}}$ numbers, with \texttt{w1/PAPER\_NUMBERS.csv}
-indexing the printed values and \texttt{verify.py} re-checking the payload
-against the manifest.
-
-The Adam step replacement and its structural readout of
-Section~\ref{subsec:limitations} are stored separately:
-\texttt{results\_traffic\_e1/} holds the prediction contrast over
-seeds $30006$--$30020$ and \texttt{results\_traffic\_struct/} the structural
-readout, with the test-fitted constant and the training-mean predictor tabulated
-in \texttt{TWO\_CONSTANTS.json}.
-
-The server-weight comparisons in Section~\ref{subsec:eval_rq3} use a shared
-driver and distinct objectives for RAVEN, projection, and projection with debt.
-The W1 records retain each rule's weights, reference, and active clients.
-Numerical comparisons report structural endpoint discrepancies separately from
-optimizer certificates.
-Section~\ref{app:kappa_probe} reports discrepancy relative to an independent projection computation
-through $\varepsilon_{\mathrm{impl}}$ and specifies the debt weight selected
-on tuning seeds.
-
-The target-concentration table uses \texttt{results\_traffic\_e2/round\_v1/}.
-The separate learning and geometry diagnostics use the R2 validation summaries
-and curves in \texttt{results\_main\_rebuild\_r1/}.  Their development splits and
-budgets differ from the main test comparison.  The trained-rule prediction
-values use \texttt{round\_v5\_1/TRADEOFF\_V51.csv}; projection accuracy is
-reported from the subsequent numerical audit rather than asserted exact.
+The public sources are cited in Table~\ref{tab:datasets}.  T-Drive follows
+Microsoft Research terms~\cite{yuan2010tdrive}.  City Scanner
+{PM}$_{2.5}$~\cite{wang2023cityscanner} is Zenodo 10.5281/zenodo.7961851,
+CC BY 4.0.  \texttt{RAVEN\_MCS\_PUBLIC\_REPRO\_R1} contains EventTraces,
+frozen targets, paired results, and figure/table sources for its indexed
+comparisons.  Later corrected W1 scores, concentration, Adam, learning, and
+geometry diagnostics remain in their separate result directories.  Their
+locations and scoring identities are indexed in the revision evidence record.
 
 \bibliographystyle{IEEEtran}
 \bibliography{reference}
-
 \end{document}
```

## appendix.tex

```diff
--- this-round-start/appendix.tex
+++ current/appendix.tex
@@ -71,7 +71,7 @@
 Table~\ref{tab:scd_phi_freeze} is the train-unit
 fraction of those zeros, not $\#\{i:\varpi_i^{\mathrm{tar}}=0\}$, and
 not a positivity check on target-positive pairs.  It is the input of the
-block-level support rule (42).  This catalogue statistic can inform the
+block-level support rule \eqref{eq:design_gate}.  This catalogue statistic can inform the
 Design configuration of \eqref{eq:design_factor} only if its inputs are available before the
 window opens; both fixed on/off settings are reported.
 The pair opportunity mass $\pi^{\mathrm{opp}}_{k,s,t}$ is
@@ -111,7 +111,7 @@
 \end{aligned}
  \label{eq:cap_ess}
 \end{equation}
-The Lipschitz constant in (38) is
+The Lipschitz constant in \eqref{eq:g4_beta} is
 \begin{multline}
 C_1
 =
@@ -144,630 +144,82 @@
 $\beta^\star_{k,r}=U_{k,r}m^\star_{k,r}d^\star_{k,r}/
 \sum_j U_{j,r}m^\star_{j,r}d^\star_{j,r}$.
 
-\subsection{Proof of Proposition~1}
+\subsection{Proof of Proposition~\ref{prop:risk}}
 \label{app:proof_prop1}
-
-\begin{proposition*}[Target-vs-arrival risk distinction]
-Let $\boldsymbol\varpi^{\mathrm{tar}}$ and
-$\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$ be two normalized laws on the same
-finite supported atomic domain.  If
-$\boldsymbol\varpi^{\mathrm{tar}}\neq
-\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$, then there exists a bounded
-nonnegative error profile $e_i$ such that
-\begin{equation}
-    \sum_i \varpi_i^{\mathrm{tar}}e_i
-    \neq
-    \sum_i \widetilde\rho_i^{\mathrm{arr}}e_i.
-    \label{eq:app_prop1_claim}
-\end{equation}
-Conversely, equality of the two weighted expectations for every bounded error
-profile implies equality of the two underlying laws.
-\end{proposition*}
-
-\noindent\emph{Proof.}
-Define $d_i\triangleq\varpi_i^{\mathrm{tar}}-\widetilde\rho_i^{\mathrm{arr}}$.
-Because both vectors are probability laws,
-\begin{equation}
-    \sum_i d_i=0.
-    \label{eq:app_prop1_zero_sum}
-\end{equation}
-The assumption
-$\boldsymbol\varpi^{\mathrm{tar}}\neq
-\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$
-implies that $d_i\neq0$ for at least one atomic unit.  Hence the set
-$B_+\triangleq\{i:d_i>0\}$
-is nonempty.  Indeed, if $d_i\le0$ for every $i$, then
-\eqref{eq:app_prop1_zero_sum} would force $d_i=0$ for every $i$, contradicting
-the assumed inequality of the two laws.
-
-Choose the bounded nonnegative profile
-$e_i=\mathbf{1}\{i\in B_+\}$, where $\mathbf{1}\{\cdot\}$ is the indicator of
-the event in braces.
-Then
+Set $d_i=\varpi_i^{\mathrm{tar}}-\widetilde\rho_i^{\mathrm{arr}}$.
+Both laws sum to one, so $\sum_i d_i=0$.  If they differ, the positive set
+$B_+=\{i:d_i>0\}$ is nonempty and the bounded nonnegative profile
+$e_i=\mathbf1\{i\in B_+\}$ gives $\sum_i d_i e_i>0$.
+Conversely, equality for every profile includes each coordinate indicator,
+forcing $d_i=0$ for every $i$.  A particular predictor may still have zero
+risk difference.\qed
+
+\subsection{Proof of Proposition~\ref{prop:reconstruction}}
+\label{app:proof_prop2}
+The target construction gives $\sum_{i:s(i)=s}\nu^{\mathrm{tar}}_{i\mid s}=1$
+on positive strata and
+$\sum_k\pi^{\mathrm{tar}}_{k,i}=\Lambda^{\mathrm{tar}}_{s(i)}
+\nu^{\mathrm{tar}}_{i\mid s(i)}\sum_k\lambda^{\mathrm{tar}}_{k\mid s(i)}
+=\varpi_i^{\mathrm{tar}}$.  On zero-mass strata both sides are zero.
+Consequently $\sum_{k,i}\pi^{\mathrm{tar}}_{k,i}=1$.
+
+For opportunity event $e$ with mark $(k,i)$, write $p_e=p^{\mathrm{obs}}_{k,r,i}$
+and $q_{k,r}=q^{\mathrm{use}}_{k,r}$.  Positivity makes both inversions legal.
+An observed event implies registration.  Apply
+\eqref{eq:A2_use_mean_ignorability} on that branch, then the observation
+conditional expectation, in temporal order:
 \begin{align}
- &
- \sum_i
- \varpi_i^{\mathrm{tar}}e_i
- -
- \sum_i
- \widetilde\rho_i^{\mathrm{arr}}e_i
- \nonumber\\
- &\qquad=
- \sum_{i\in B_+}
- \left(
- \varpi_i^{\mathrm{tar}}
- -
- \widetilde\rho_i^{\mathrm{arr}}
- \right)
- =
- \sum_{i\in B_+}d_i
- >0.
- \label{eq:app_prop1_difference}
+&\mathbb E\!\left[\left.\frac{O_eU_{k,r}}{p_eq_{k,r}}
+\right|k_e=k,i_e=i,\mathcal H_e^{\mathrm{obs}}\right]\nonumber\\
+&\quad=\mathbb E\!\left[\left.\frac{O_e}{p_e}
+\right|k_e=k,i_e=i,\mathcal H_e^{\mathrm{obs}}\right]=1.
+\label{eq:app_sequential_identity}
 \end{align}
-Therefore, the two weighted expectations differ for the bounded nonnegative
-profile $e_i=\mathbf{1}\{i\in B_+\}$.  This proves the forward direction.
-
-For the converse, suppose
-\begin{equation}
-    \sum_i \varpi_i^{\mathrm{tar}}e_i
-    =
-    \sum_i \widetilde\rho_i^{\mathrm{arr}}e_i
-    \label{eq:app_prop1_all_equal}
-\end{equation}
-for every bounded error profile $e$.  Fix an arbitrary atomic unit $j$ and set
-$e_i^{(j)}=\mathbf{1}\{i=j\}$.
-Substituting $e_i^{(j)}$ into
-\eqref{eq:app_prop1_all_equal} gives
-$\varpi_j^{\mathrm{tar}}=\widetilde\rho_j^{\mathrm{arr}}$.
-Since $j$ was arbitrary, the equality holds for every coordinate.  Hence
-$\boldsymbol\varpi^{\mathrm{tar}}=\widetilde{\boldsymbol\rho}^{\mathrm{arr}}$.
-This proves the converse. \hfill$\square$
-
-\paragraph{Interpretation.}
-The proposition distinguishes the linear risk functionals induced by the two
-probability laws.  A particular predictor's numerical gap depends on its error
-profile, and the relation between minimizers depends on the model class.
-
-
-\subsection{Proof of Proposition~2}
-\label{app:proof_prop2}
-
-\begin{proposition*}[Normalized target reconstruction]
-Under A1--A3, for any bounded test function $\psi(k,i)$, distinct from
-the Design factor of \eqref{eq:design_factor}, the H\'ajek ratio in
-(35) converges in probability to
-\begin{equation}
-    \Phi^{\mathrm{tar}}
-    =
-    \sum_{k,i}
-    \pi^{\mathrm{tar}}_{k,i}\psi(k,i).
-    \label{eq:app_target_phi}
-\end{equation}
-\end{proposition*}
-
-\noindent\emph{Proof.}
-We first record two identities used by the proof.
-
-\subsubsection{Target-Measure Compatibility}
-
-For every stratum $s$ with $\Lambda_s^{\mathrm{tar}}>0$,
-\eqref{eq:target_conditional_atomic} gives
-\begin{equation}
-    \sum_{i:s(i)=s}
-    \nu^{\mathrm{tar}}_{i\mid s}
-    =
-    \frac{
-    \sum_{i:s(i)=s}\varpi_i^{\mathrm{tar}}
-    }{
-    \Lambda_s^{\mathrm{tar}}
-    }
-    =1.
-    \label{eq:app_nu_normalization}
-\end{equation}
-For an atomic unit $i$ whose stratum has positive target mass, using
-$\pi^{\mathrm{tar}}_{k,s}
-=\Lambda_s^{\mathrm{tar}}
-\lambda^{\mathrm{tar}}_{k\mid s}$ and
-$\sum_k\lambda^{\mathrm{tar}}_{k\mid s}=1$ gives
-\begin{align}
- \sum_k\pi^{\mathrm{tar}}_{k,i}
- &=
- \sum_k
- \pi^{\mathrm{tar}}_{k,s(i)}
- \nu^{\mathrm{tar}}_{i\mid s(i)}
- \nonumber\\
- &=
- \Lambda_{s(i)}^{\mathrm{tar}}
- \nu^{\mathrm{tar}}_{i\mid s(i)}
- \sum_k
- \lambda^{\mathrm{tar}}_{k\mid s(i)}
- \nonumber\\
- &=
- \Lambda_{s(i)}^{\mathrm{tar}}
- \frac{\varpi_i^{\mathrm{tar}}}
- {\Lambda_{s(i)}^{\mathrm{tar}}}
- =
- \varpi_i^{\mathrm{tar}}.
- \label{eq:app_target_compatibility_positive}
-\end{align}
-If instead $\Lambda_{s(i)}^{\mathrm{tar}}=0$, then nonnegativity and
-\eqref{eq:target_stratum_mass} imply $\varpi_i^{\mathrm{tar}}=0$.  The
-zero-stratum convention in
-\eqref{eq:target_ks_mass}--\eqref{eq:target_ki_mass}
-gives $\pi^{\mathrm{tar}}_{k,i}=0$ for every $k$.  Hence, in both cases,
-\begin{equation}
- \sum_k\pi^{\mathrm{tar}}_{k,i}
- =\varpi_i^{\mathrm{tar}}.
- \label{eq:app_target_compatibility}
-\end{equation}
-Summing over $i$ also yields
-\begin{equation}
-    \sum_{k,i}\pi^{\mathrm{tar}}_{k,i}
-    =
-    \sum_i\varpi_i^{\mathrm{tar}}
-    =1.
-    \label{eq:app_pi_normalized}
-\end{equation}
-
-\subsubsection{Sequential Inverse-Selection Identity}
-
-Consider an opportunity event $e\in\mathcal{O}_r$ with mark
-$(k_e,i_e)=(k,i)$.  For compactness, write
-$p_e\triangleq p^{\mathrm{obs}}_{k,r,i}$ and
-$q_{k,r}\triangleq q^{\mathrm{use}}_{k,r}$.
-Under A1, both denominators are strictly positive on the target-supported event.
-
-Let $\mathcal{H}^{\mathrm{obs}}_e$ denote the legal history immediately before
-the observation outcome.  By the definition of $p_e$ and A2,
-\begin{equation}
-    \mathbb{E}
-    \left[
-    \left.
-    \frac{O_e}{p_e}
-    \right|
-    k_e=k,\,
-    i_e=i,\,
-    \mathcal{H}^{\mathrm{obs}}_e
-    \right]
-    =1.
-    \label{eq:app_obs_ipw}
-\end{equation}
-If $O_e=1$, client $k$ has at least one observed item and is therefore in the
-registered-attempt set $\mathcal{E}_r$.  Conditional on the legal pre-$U$
-history $\mathcal{H}^{\mathrm{use}}_{k,r}$, the definition of $q_{k,r}$ and A2
-give
-\begin{equation}
-    \mathbb{E}
-    \left[
-    \left.
-    \frac{U_{k,r}}{q_{k,r}}
-    \right|
-    k\in\mathcal{E}_r,\,
-    \mathcal{H}^{\mathrm{use}}_{k,r}
-    \right]
-    =1.
-    \label{eq:app_use_ipw}
-\end{equation}
-The usable-update indicator may be shared by several observed opportunity
-events of the same client-window.  This induces within-window dependence, but
-it does not invalidate the conditional identity
-\eqref{eq:app_use_ipw}.  A3 handles such dependence at the
-cluster/window level.
-
-Applying the tower property in the temporal order
-opportunity $\rightarrow$ observation $\rightarrow$ registration/use, and using
-\eqref{eq:A2_use_mean_ignorability} on the $O_e=1$ branch, gives
-\begin{align}
- &\mathbb{E}\!\left[
- \left.
- \frac{O_eU_{k,r}}{p_eq_{k,r}}
- \right|
- k_e=k,\,i_e=i,\,\mathcal{H}^{\mathrm{obs}}_e
- \right]
- \nonumber\\
- &\qquad=
- \mathbb{E}\!\left[
- \left.
- \frac{O_e}{p_e}
- \right|
- k_e=k,\,i_e=i,\,\mathcal{H}^{\mathrm{obs}}_e
- \right]
- =1.
- \label{eq:app_sequential_identity}
-\end{align}
-The inner conditional expectation is evaluated only on the $O_e=1$ branch,
-where client $k$ is registered.  It equals one by the strengthened
-mean-ignorability condition \eqref{eq:A2_use_mean_ignorability}.  The outer
-expectation is then \eqref{eq:app_obs_ipw}.
-
-With these two identities in hand, we prove the proposition.
-For event $e\in\mathcal{O}_r$, recall
-\begin{equation}
- \chi_e
- =
- O_eU_{k_e,r}
- \frac{
- \pi^{\mathrm{tar}}_{k_e,i_e}
- }{
- P_r^{\mathrm{opp}}(k_e,i_e)
- p^{\mathrm{obs}}_{k_e,r,i_e}
- q^{\mathrm{use}}_{k_e,r}
- }.
- \label{eq:app_chi}
-\end{equation}
-Condition first on the opportunity mark $(k_e,i_e)=(k,i)$.  Using
-\eqref{eq:app_sequential_identity},
-\begin{align}
- &\mathbb{E}
- \left[
- \left.
- \chi_e\psi(k_e,i_e)
- \right|
- k_e=k,\,
- i_e=i
- \right]
- \nonumber\\
- &=
- \frac{
- \pi^{\mathrm{tar}}_{k,i}
- }{
- P_r^{\mathrm{opp}}(k,i)
- }
- \psi(k,i)
- \,
- \mathbb{E}
- \left[
- \left.
- \frac{
- O_eU_{k,r}
- }{
- p^{\mathrm{obs}}_{k,r,i}
- q^{\mathrm{use}}_{k,r}
- }
- \right|
- k_e=k,\,
- i_e=i
- \right]
- \nonumber\\
- &=
- \frac{
- \pi^{\mathrm{tar}}_{k,i}
- }{
- P_r^{\mathrm{opp}}(k,i)
- }
- \psi(k,i).
- \label{eq:app_conditional_weighted_moment}
-\end{align}
-By (1), the mark itself has opportunity law
-$P_r^{\mathrm{opp}}(k,i)$.  Averaging
-\eqref{eq:app_conditional_weighted_moment} over this law therefore yields
-\begin{align}
- \mathbb{E}
- \left[
- \chi_e\psi(k_e,i_e)
- \right]
- &=
- \sum_{k,i}
- P_r^{\mathrm{opp}}(k,i)
- \frac{
- \pi^{\mathrm{tar}}_{k,i}
- }{
- P_r^{\mathrm{opp}}(k,i)
- }
- \psi(k,i)
- \nonumber\\
- &=
- \sum_{k,i}
- \pi^{\mathrm{tar}}_{k,i}\psi(k,i)
- =
- \Phi^{\mathrm{tar}}.
- \label{eq:app_expected_numerator_event}
-\end{align}
-Likewise, taking $\psi\equiv1$ and using
-\eqref{eq:app_pi_normalized},
-\begin{equation}
-    \mathbb{E}[\chi_e]
-    =
-    \sum_{k,i}\pi^{\mathrm{tar}}_{k,i}
-    =1.
-    \label{eq:app_expected_denominator_event}
-\end{equation}
-
-Let
-\begin{equation}
-    N_R^{\mathrm{opp}}
-    \triangleq
-    \sum_{r=0}^{R-1}|\mathcal{O}_r|
-    \label{eq:app_total_opp_events}
-\end{equation}
-be the total number of opportunity events in the first $R$ windows.  Define
-\begin{align}
- A_R(\psi)
- &\triangleq
- \sum_{r<R}
- \sum_{e\in\mathcal{O}_r}
- \chi_e\psi(k_e,i_e),
- \label{eq:app_AR}\\
- B_R
- &\triangleq
- \sum_{r<R}
- \sum_{e\in\mathcal{O}_r}
- \chi_e.
- \label{eq:app_BR}
-\end{align}
-A3 explicitly requires the asymptotic regime
-$N_R^{\mathrm{opp}}\rightarrow\infty$.  It is precisely the regularity
-condition needed to pass from the eventwise identities above to the possibly
-dependent client-window process.  Along this growing sequence, it gives
-\begin{align}
- \frac{A_R(\psi)}{N_R^{\mathrm{opp}}}
- &\xrightarrow{p}
- \Phi^{\mathrm{tar}},
- \label{eq:app_AR_lln}\\
- \frac{B_R}{N_R^{\mathrm{opp}}}
- &\xrightarrow{p}
- 1.
- \label{eq:app_BR_lln}
-\end{align}
-The second limit is strictly positive.  Therefore, by the continuous mapping
-theorem (equivalently, Slutsky's theorem),
-\begin{align}
- \widehat\Phi_R
- &=
- \frac{A_R(\psi)}{B_R}
- =
- \frac{
- A_R(\psi)/N_R^{\mathrm{opp}}
- }{
- B_R/N_R^{\mathrm{opp}}
- }
- \xrightarrow{p}
- \Phi^{\mathrm{tar}}.
- \label{eq:app_hajek_limit}
-\end{align}
-This proves the main convergence statement.
-
-It remains to verify the two stated marginals.
-
-For the client--stratum marginal, fix $(k_0,s_0)$ and choose
-\begin{equation}
-    \psi_{k_0,s_0}(k,i)
-    =
-    \mathbf{1}\{k=k_0,\ s(i)=s_0\}.
-    \label{eq:app_phi_client_stratum}
-\end{equation}
-If $\Lambda_{s_0}^{\mathrm{tar}}>0$, then
-\begin{align}
- \Phi^{\mathrm{tar}}
- &=
- \sum_{i:s(i)=s_0}
- \pi^{\mathrm{tar}}_{k_0,i}
- \nonumber\\
- &=
- \pi^{\mathrm{tar}}_{k_0,s_0}
- \sum_{i:s(i)=s_0}
- \nu^{\mathrm{tar}}_{i\mid s_0}
- =
- \pi^{\mathrm{tar}}_{k_0,s_0},
- \label{eq:app_recover_client_stratum_positive}
-\end{align}
-where the last equality follows from
-\eqref{eq:app_nu_normalization}.  If
-$\Lambda_{s_0}^{\mathrm{tar}}=0$, the zero-stratum convention gives both
-$\pi^{\mathrm{tar}}_{k_0,s_0}=0$ and
-$\pi^{\mathrm{tar}}_{k_0,i}=0$ for every $i$ in that stratum.  The same
-conclusion then holds.  Thus, in all cases,
-$\Phi^{\mathrm{tar}}=\pi^{\mathrm{tar}}_{k_0,s_0}$.
-
-Second, fix a deployment group $g$ and choose
-$\psi_g(k,i)=\mathbf{1}\{h(i)=g\}$.
-Using target compatibility
-\eqref{eq:app_target_compatibility},
-\begin{align}
- \Phi^{\mathrm{tar}}
- &=
- \sum_{k,i}
- \pi^{\mathrm{tar}}_{k,i}
- \mathbf{1}\{h(i)=g\}
- \nonumber\\
- &=
- \sum_{i:h(i)=g}
- \sum_k
- \pi^{\mathrm{tar}}_{k,i}
- \nonumber\\
- &=
- \sum_{i:h(i)=g}
- \varpi_i^{\mathrm{tar}}
- =
- \mu_g.
- \label{eq:app_recover_group}
-\end{align}
-Hence, the ideal normalized sequential correction recovers both the
-client--stratum target moments and, through the compatibility bridge, the
-deployment-group mass. \hfill$\square$
-
-\paragraph{Scope of Proposition~2.}
-The result establishes identification and consistency of compatible target
-moments or group mass for the ideal pooled sequential ratios under A1--A3.
-Finite-window realization depends on the current client support and is handled
-by the calibration in Section~V.  Active stabilization bounds control weight
-concentration through a finite-sample bias--variance trade-off in the practical
-plug-in estimator.
-
-
-\subsection{Proof of Theorem~1}
+This is a tower-property argument, not independence of observation and
+usability.  Shared client-window usability induces dependence, handled by A3's
+cluster-level weak law.
+For $\chi_e$ from \eqref{eq:chi_event}, integrating the mark with law
+$P_r^{\mathrm{opp}}(k,i)$ cancels its opportunity denominator:
+\begin{equation}
+\mathbb E[\chi_e\psi(k_e,i_e)]
+=\sum_{k,i}\pi^{\mathrm{tar}}_{k,i}\psi(k,i)=\Phi^{\mathrm{tar}},
+\qquad \mathbb E[\chi_e]=1.
+\label{eq:app_expected_numerator_event}
+\end{equation}
+Let $A_R=\sum_{r<R}\sum_{e\in\mathcal O_r}\chi_e\psi(k_e,i_e)$,
+$B_R=\sum_{r<R}\sum_{e\in\mathcal O_r}\chi_e$, and
+$N_R=\sum_{r<R}|\mathcal O_r|$.  Under A3, $N_R\to\infty$ and
+\begin{equation}
+A_R/N_R\xrightarrow{p}\Phi^{\mathrm{tar}},\qquad
+B_R/N_R\xrightarrow{p}1,\qquad A_R/B_R\xrightarrow{p}\Phi^{\mathrm{tar}}.
+\label{eq:app_hajek_limit}
+\end{equation}
+The positive denominator limit justifies the ratio by continuous mapping,
+even with within-window dependence.  Choosing a client--stratum indicator
+recovers $\pi^{\mathrm{tar}}_{k,s}$ by conditional normalization (including
+the zero-stratum convention); choosing a group indicator recovers $\mu_g$
+by target compatibility.  These are ideal pooled moments, not finite-window
+realizability or unbiasedness of clipped multi-step updates.\qed
+
+\subsection{Proof of Theorem~\ref{thm:calibration}}
 \label{app:proof_theorem1}
-
-\noindent\textbf{Theorem~1.}
-Under A4, every active window has a nonempty compact convex feasible set
-$\mathcal{C}_r$, and the calibration program
-$\min_{\boldsymbol\alpha\in\mathcal{C}_r}J_r(\boldsymbol\alpha)$
-has a unique global minimizer $\boldsymbol\alpha_r^\star$.
-
-\noindent\emph{Proof.}
-Fix an active window $r$.  Then
-\begin{equation}
-    K_r=|\mathcal{A}_r|\ge1.
-    \label{eq:app_K_positive}
-\end{equation}
-Consider the uniform vector
-\begin{equation}
-    \boldsymbol\alpha_r^{u}
-    =
-    \frac{1}{K_r}\mathbf{1}.
-    \label{eq:app_uniform_alpha}
-\end{equation}
-It satisfies
-\begin{equation}
-    \mathbf{1}^{\top}\boldsymbol\alpha_r^{u}=1
-    \quad\text{and}\quad
-    \alpha_{k,r}^{u}=\frac{1}{K_r}\ge0.
-    \label{eq:app_uniform_simplex}
-\end{equation}
-From \eqref{eq:cap_ess},
-\begin{equation}
-    \overline\alpha_r
-    =
-    \min\left\{
-    1,
-    \max\left\{
-    \alpha_{\max},
-    \frac{1}{K_r}
-    \right\}
-    \right\}.
-    \label{eq:app_alpha_bar}
-\end{equation}
-Since $K_r\ge1$ and $0<\alpha_{\max}\le1$,
-\begin{equation}
-    \frac{1}{K_r}\le\overline\alpha_r\le1.
-    \label{eq:app_uniform_box}
-\end{equation}
-Thus the box constraints are satisfied by
-$\boldsymbol\alpha_r^{u}$.
-
-Next,
-\begin{equation}
-    \left\|
-    \boldsymbol\alpha_r^{u}
-    \right\|_2^2
-    =
-    K_r\left(\frac{1}{K_r}\right)^2
-    =
-    \frac{1}{K_r}.
-    \label{eq:app_uniform_l2}
-\end{equation}
-Because
-\begin{equation}
-    \overline E_r
-    =
-    \min\{E_{\min},K_r\}
-    \le K_r,
-    \label{eq:app_Ebar_leq_K}
-\end{equation}
-we have
-\begin{equation}
-    \frac{1}{K_r}
-    \le
-    \frac{1}{\overline E_r}.
-    \label{eq:app_uniform_ess}
-\end{equation}
-Therefore
-\begin{equation}
-    \boldsymbol\alpha_r^{u}
-    \in
-    \mathcal{C}_r,
-    \label{eq:app_C_nonempty}
-\end{equation}
-so $\mathcal{C}_r$ is nonempty.
-
-The equality constraint
-$\mathbf{1}^{\top}\boldsymbol\alpha=1$ defines an affine set.  The coordinate
-constraints
-$0\le\alpha_k\le\overline\alpha_r$ define a closed convex box, and
-\begin{equation}
-    \left\{
-    \boldsymbol\alpha:
-    \|\boldsymbol\alpha\|_2^2
-    \le
-    1/\overline E_r
-    \right\}
-    \label{eq:app_l2_ball}
-\end{equation}
-is a closed convex Euclidean ball.  Their intersection is therefore closed and
-convex.  Moreover, the simplex and box constraints imply
-$0\le\alpha_k\le1$ for every coordinate, so the set is bounded.  Hence
-$\mathcal{C}_r$ is compact.
-
-We now analyze the objective.  Expanding only the terms that are quadratic in
-$\boldsymbol\alpha$, the Hessian of $J_r$ is
-\begin{equation}
- \nabla^2J_r
- =
- \lambda_gM_r^{\top}M_r
- +
- \lambda_{\beta}I
- +
- \lambda_vV_r.
- \label{eq:app_P2_hessian}
-\end{equation}
-The debt term
-$-\mathbf{Q}_r^{\top}M_r\boldsymbol\alpha$ and the staleness term
-$\lambda_s\overline{\boldsymbol\tau}_r^{\top}\boldsymbol\alpha$ are linear.
-They therefore contribute zero Hessian.  Under A4,
-\begin{equation}
-    M_r^{\top}M_r\succeq0,
-    \qquad
-    V_r\succeq0,
-    \qquad
-    \lambda_g,\lambda_v\ge0,
-    \qquad
-    \lambda_{\beta}>0.
-    \label{eq:app_psd_terms}
-\end{equation}
-Consequently, for every nonzero vector $\mathbf{x}\in\mathbb{R}^{K_r}$,
-\begin{align}
- \mathbf{x}^{\top}\nabla^2J_r\mathbf{x}
- &=
- \lambda_g\|M_r\mathbf{x}\|_2^2
- +
- \lambda_{\beta}\|\mathbf{x}\|_2^2
- +
- \lambda_v\mathbf{x}^{\top}V_r\mathbf{x}
- \nonumber\\
- &\ge
- \lambda_{\beta}\|\mathbf{x}\|_2^2
- >0.
- \label{eq:app_strong_convex}
-\end{align}
-Thus $J_r$ is $\lambda_{\beta}$-strongly convex on
-$\mathbb{R}^{K_r}$ and hence strictly convex on $\mathcal{C}_r$.
-
-Because $J_r$ is continuous and $\mathcal{C}_r$ is nonempty and compact, the
-Weierstrass theorem guarantees the existence of at least one minimizer.
-Strict convexity on the convex feasible set guarantees that two distinct
-minimizers cannot exist.  Therefore, (P2) has exactly one global minimizer,
-denoted by $\boldsymbol\alpha_r^\star$.  This completes the proof.
-\hfill$\square$
-
-\paragraph{Scope of Theorem~1.}
-The theorem proves existence and uniqueness of the mathematical optimizer of
-(P2).  It does not, by itself, certify that a finite-precision solver log
-reconstructs that optimizer exactly.  Numerical feasibility and post-hoc
-solver audit are separate empirical/provenance questions.
-
+For $K_r\ge1$, the cap/ESS definitions give
+$1/K_r\le\overline\alpha_r$ and $\overline E_r\le K_r$.
+Thus $\mathbf1/K_r$ satisfies the simplex, box, and squared-norm constraints.
+Their intersection is nonempty, closed, convex, and bounded, hence compact.
+The objective is continuous and
+\begin{equation}
+\nabla^2J_r=\lambda_gM_r^\top M_r+\lambda_\beta I+\lambda_vV_r
+\succeq\lambda_\beta I\succ0.
+\label{eq:app_P2_hessian}
+\end{equation}
+The debt and staleness terms are linear.  A4 therefore gives strong convexity;
+compactness gives existence and strict convexity gives uniqueness on
+$\mathcal C_r$.  This certifies the mathematical minimizer, not a stored
+finite-precision solution.\qed
 
 \subsection{Proof of Proposition~3}
 \label{app:proof_prop3}
-
-\noindent\textbf{Proposition~3.}
-Assume A1, A4, A5, and A6b, let
-$\mathbf{1}^{\top}b_r^{\mathcal T}\ge B_{\min}>0$ hold at the true margins,
-and let the ideal and the implemented reference share $\mathcal{A}_r$,
-$M_r$, and $\mathcal{C}_r$.  Then the implemented clipped plug-in
-$\widehat{\boldsymbol\beta}_r$ is a Lipschitz perturbation of the
-same-window ideal reference $\boldsymbol\beta_r^\star$ up to the stabilization
-error $\varepsilon_{\mathrm{stab},r}$, and the P2 map does not amplify that
-$\ell_2$ error on a fixed feasible set.
 
 \noindent\emph{Proof.}
 Fix an active window $r$ and the common set $\mathcal{A}_r$.  Write
@@ -855,12 +307,12 @@
 \Bigr).
 \]
 
-\emph{Step 4 (triangle inequality).}  By (37),
+\emph{Step 4 (triangle inequality).}  By \eqref{eq:eps_stab},
 $\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^\star\|_1
 \le\|\widehat{\boldsymbol\beta}_r-\boldsymbol\beta_r^{\mathcal T}\|_1
 +\varepsilon_{\mathrm{stab},r}$, and Steps 1--3 bound the first term by
 $C_1(\varepsilon_\pi+\varepsilon_p+\varepsilon_q)$ with the $C_1$ of
-\eqref{eq:g4_c1}: that is (38).
+\eqref{eq:g4_c1}: that is \eqref{eq:g4_beta}.
 
 \emph{Support lemma.}  Under Design on,
 $a>0\iff\pi^{\mathrm{tar}}>0\iff a^\star>0$ on A5's active support; under
@@ -868,10 +320,10 @@
 $b^{\mathcal T}$, $m^\star$ and $b^\star$ share a support, which is the
 shared-support clause of A5.
 
-The P2 bound (39) is the reference
+The P2 bound \eqref{eq:g4_alpha} is the reference
 non-expansion \eqref{eq:app_reference_nonexpansive}, proved later in this supplement, on the common
 convex set $\mathcal{C}_r$.  The composition bound
-(40) is the operator $2$-norm.
+\eqref{eq:g4_comp} is the operator $2$-norm.
 \hfill$\square$
 
 The constant $C_1$ is a worst-case envelope, not a numerical certificate: at
@@ -882,20 +334,11 @@
 \subsection{Proof of Proposition~4}
 \label{app:proof_prop4}
 
-\noindent\textbf{Proposition~4.}  Partition the supported test units into groups
-$\mathcal G$, let $\mu^{\mathrm{eval}}_g$ and $n_g$ be the evaluation mass and
-the unit count of group $g$, and write
-$\mathrm{RMSE}_g=[n_g^{-1}\sum_{i:h(i)=g}(\widehat Y_i-Y_i)^2]^{1/2}$.  Then
-$\mathrm{RMSE}_{\mu}^2=\sum_{g\in\mathcal G}\mu^{\mathrm{eval}}_g\mathrm{RMSE}_g^2$.
-Along a feasible direction $d$ of the simplex, $\sum_g d_g=0$, and when
-$\mathrm{RMSE}_{\mu}>0$, the directional derivative is
-$\sum_g d_g\mathrm{RMSE}_g^2/(2\mathrm{RMSE}_{\mu})$.
-Two methods exchange order between $\boldsymbol\mu^{\mathrm{eval}}$ and
-$\boldsymbol\mu'^{\mathrm{eval}}$ only when
-$\sum_g\mu^{\mathrm{eval}}_g(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)$
-and
-$\sum_g\mu'^{\mathrm{eval}}_g(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)$
-have opposite signs.
+For fixed predictions, the derivative along $\sum_gd_g=0$ is
+$\sum_gd_g\mathrm{RMSE}_g^2/(2\mathrm{RMSE}_{\mu})$ when
+$\mathrm{RMSE}_{\mu}>0$.  A ranking reversal requires opposite signs of
+$\sum_g\mu_g^{\mathrm{eval}}(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2)$
+under the two evaluation measures.
 
 \emph{Proof.}  Let $w_i=\mu^{\mathrm{eval}}_{h(i)}/n_{h(i)}$ and
 $e_i^2=(\widehat Y_i-Y_i)^2$.  Substituting the definition of
@@ -930,217 +373,26 @@
 
 \subsection{Proof of the Target-Debt Accounting Bound}
 \label{app:proof_debt_bound}
-
-The bound states that the prefix-averaged deployment composition
-$\overline{\boldsymbol\omega}_R$ cannot drift farther from the target
-$\boldsymbol\mu$ than twice the accumulated target debt per unit of active
-step mass.  Intuitively, the debt vector records, for each deployment group,
-how much service the group has cumulatively missed across windows.  The
-relation therefore turns that accounting into a deterministic control on
-structural mismatch: the group-average distance to the target is bounded by
-how much the process has fallen behind, normalized by how much it has run.
-The proof proceeds in three steps.  It first shows that the coordinate-wise
-debt dominates the cumulative signed discrepancy.  It then combines this
-domination with the zero-sum property of the discrepancy to bound its
-$\ell_1$ norm by twice the debt.  Finally, it divides by the active step
-mass $S_R$ to obtain the stated bound.
-
-We now prove the deterministic relation in
-\eqref{eq:debt_bound}.  Recall
-\begin{equation}
-    S_R
-    =
-    \sum_{r=0}^{R-1}\eta_rI_r,
-    \qquad
-    \overline{\boldsymbol\omega}_R
-    =
-    \frac{
-    \sum_{r=0}^{R-1}
-    \eta_rI_r\boldsymbol\omega_r
-    }{S_R},
-    \label{eq:app_debt_prefix_defs}
-\end{equation}
-for $S_R>0$.  In every active window,
-$\boldsymbol\alpha_r$ is a probability vector and each column
-$\mathbf{c}_{k,r}^{g}$ of $M_r$ is a deployment-group probability vector.
-Therefore
-\begin{equation}
-    \boldsymbol\omega_r
-    =
-    M_r\boldsymbol\alpha_r
-    \in
-    \Delta^{|\mathcal G|-1},
-    \label{eq:app_omega_simplex}
-\end{equation}
-and hence
-\begin{equation}
-    \mathbf{1}^{\top}\boldsymbol\omega_r
-    =
-    \mathbf{1}^{\top}\boldsymbol\mu
-    =1.
-    \label{eq:app_equal_mass}
-\end{equation}
-
-Define the cumulative signed target discrepancy
-\begin{equation}
-    \mathbf{D}_R
-    \triangleq
-    \sum_{r=0}^{R-1}
-    \eta_rI_r
-    \left(
-    \boldsymbol\mu-\boldsymbol\omega_r
-    \right).
-    \label{eq:app_DR}
-\end{equation}
-By \eqref{eq:app_debt_prefix_defs},
-\begin{equation}
-    \mathbf{D}_R
-    =
-    S_R
-    \left(
-    \boldsymbol\mu-\overline{\boldsymbol\omega}_R
-    \right).
-    \label{eq:app_DR_baromega}
-\end{equation}
-
-Fix a target-group coordinate $g$.  In an active window, the debt recursion is
-\begin{equation}
-    Q_{r+1,g}
-    =
-    \left[
-    Q_{r,g}
-    +
-    \eta_r
-    \left(
-    \mu_g-\omega_{r,g}
-    \right)
-    \right]_+.
-    \label{eq:app_debt_coordinate}
-\end{equation}
-Since $[x]_+\ge x$ for every scalar $x$,
-\begin{equation}
-    Q_{r+1,g}
-    \ge
-    Q_{r,g}
-    +
-    \eta_r
-    \left(
-    \mu_g-\omega_{r,g}
-    \right)
-    \label{eq:app_debt_one_step}
-\end{equation}
-holds for active windows.  In inactive windows,
-$Q_{r+1,g}=Q_{r,g}$ and $I_r=0$.  The same inequality can therefore be written
-uniformly as
-\begin{equation}
-    Q_{r+1,g}
-    \ge
-    Q_{r,g}
-    +
-    \eta_rI_r
-    \left(
-    \mu_g-\omega_{r,g}
-    \right).
-    \label{eq:app_debt_one_step_all}
-\end{equation}
-Telescoping from $r=0$ to $R-1$ and using $Q_{0,g}=0$ gives
-\begin{equation}
-    Q_{R,g}
-    \ge
-    D_{R,g}.
-    \label{eq:app_Q_dominates_D}
-\end{equation}
-Because $Q_{R,g}\ge0$, it follows that
-\begin{equation}
-    (D_{R,g})_+
-    \le
-    Q_{R,g}.
-    \label{eq:app_positive_part_domination}
-\end{equation}
-Summing over $g$,
-\begin{equation}
-    \|(\mathbf{D}_R)_+\|_1
-    \le
-    \|\mathbf{Q}_R\|_1.
-    \label{eq:app_positive_part_l1}
-\end{equation}
-
-Next, by \eqref{eq:app_equal_mass},
-\begin{align}
-    \mathbf{1}^{\top}\mathbf{D}_R
-    &=
-    \sum_{r=0}^{R-1}
-    \eta_rI_r
-    \mathbf{1}^{\top}
-    \left(
-    \boldsymbol\mu-\boldsymbol\omega_r
-    \right)
-    \nonumber\\
-    &=
-    \sum_{r=0}^{R-1}
-    \eta_rI_r(1-1)
-    =0.
-    \label{eq:app_DR_zero_sum}
-\end{align}
-For any finite-dimensional vector with zero coordinate sum, the positive and
-negative parts have equal $\ell_1$ mass:
-\begin{equation}
-    \|(\mathbf{D}_R)_+\|_1
-    =
-    \|(\mathbf{D}_R)_-\|_1,
-    \label{eq:app_pos_neg_equal}
-\end{equation}
-where $(\mathbf{x})_-=[-\mathbf{x}]_+$.  Therefore
-\begin{equation}
-\begin{aligned}
-    \|\mathbf{D}_R\|_1
-    &=
-    \|(\mathbf{D}_R)_+\|_1
-    +
-    \|(\mathbf{D}_R)_-\|_1\\
-    &=2\|(\mathbf{D}_R)_+\|_1
-    \le
-    2\|\mathbf{Q}_R\|_1.
-\end{aligned}
-    \label{eq:app_DR_l1_bound}
-\end{equation}
-Finally, substituting
-\eqref{eq:app_DR_baromega} into
-\eqref{eq:app_DR_l1_bound} and dividing by $S_R>0$ yields
-\begin{equation}
-    \left\|
-    \overline{\boldsymbol\omega}_R
-    -
-    \boldsymbol\mu
-    \right\|_1
-    \le
-    \frac{
-    2\|\mathbf{Q}_R\|_1
-    }{
-    S_R
-    }.
-    \label{eq:app_debt_bound_final}
-\end{equation}
-This is exactly the accounting relation stated in
-\eqref{eq:debt_bound}. \hfill$\square$
-
-\paragraph{Consequence.}
-If the cumulative debt is sublinear in active step mass, that is,
-$\|\mathbf{Q}_R\|_1=o(S_R)$, then
-\begin{equation}
-    \Delta_{\mathrm{group}}(R)
-    =
-    \left\|
-    \overline{\boldsymbol\omega}_R
-    -
-    \boldsymbol\mu
-    \right\|_1
-    \longrightarrow0.
-    \label{eq:app_debt_sublinear_consequence}
-\end{equation}
-Thus sublinear debt yields long-run group alignment through the deterministic
-bound; the implication is conditional on the stated debt-growth assumption.
-
+Let $D_R=\sum_{r<R}\eta_rI_r(\boldsymbol\mu-\boldsymbol\omega_r)
+=S_R(\boldsymbol\mu-\overline{\boldsymbol\omega}_R)$.
+Projection onto the nonnegative orthant gives, coordinatewise,
+\begin{equation}
+Q_{r+1,g}\ge Q_{r,g}+\eta_rI_r(\mu_g-\omega_{r,g}),
+\qquad (D_{R,g})_+\le Q_{R,g}.
+\label{eq:app_Q_dominates_D}
+\end{equation}
+The second inequality follows by telescoping from $Q_{0,g}=0$;
+inactive windows contribute zero and leave debt unchanged.
+Both target and active-window composition have unit mass, so
+$\mathbf1^\top D_R=0$.  Equal positive and negative mass then gives
+\begin{equation}
+S_R\|\overline{\boldsymbol\omega}_R-\boldsymbol\mu\|_1
+=\|D_R\|_1=2\|(D_R)_+\|_1\le2\|\mathbf Q_R\|_1.
+\label{eq:app_debt_bound_final}
+\end{equation}
+Divide by $S_R>0$ to obtain \eqref{eq:debt_bound}.  Vanishing mismatch follows
+if $\|\mathbf Q_R\|_1=o(S_R)$; the recursion alone does not prove that
+growth condition.\qed
 
 \subsection{Supplementary Consequences of the Calibration Geometry}
 \label{app:supp_calibration_geometry}
@@ -1244,41 +496,16 @@
 robustness guarantee to changes in the underlying mobile opportunity or
 selection process.
 
-\subsection{Summary of Theoretical Results}
 \label{app:proof_summary}
-
-The theoretical results connect target semantics, sequential reconstruction,
-and feasible calibration:
-
-\begin{enumerate}
-    \item Proposition~1 proves that unequal deployment and arrival laws define
-    different risk functionals in general.
-    \item Proposition~2 proves consistency of the ideal normalized sequential
-    opportunity--observation--usable correction under A1--A3 for compatible
-    target moments or target-group mass.
-    \item Proposition~3 proves that, under A1, A4, A5, and A6b, the implemented
-    clipped plug-in is a Lipschitz perturbation of the same-window ideal
-    reference up to the measurable stabilization error
-    $\varepsilon_{\mathrm{stab},r}$, and that P2 does not amplify that error on
-    a fixed $\mathcal{A}_r$.  A6a is the additional clause that drives
-    $\varepsilon_{\mathrm{stab},r}$ to zero.
-    \item Theorem~1 proves existence and uniqueness of the solution to (P2)
-    under A4.
-    \item The debt recursion gives a deterministic long-term accounting bound.
-    Vanishing structural mismatch follows whenever debt grows sublinearly in
-    active step mass.
-\end{enumerate}
-
-None of these results asserts identification outside target support, robustness
-to arbitrary hidden confounding, exact unbiasedness under active clipping, or
-universal predictive superiority.
-
+The reconstruction proof is population-level; reference non-expansion fixes
+the entire window state.  Neither result supplies a prediction guarantee or
+unconditional long-run alignment.
 
 \section{Complete Proofs for Aggregate Coverage Certification}
 \label{app:agg_coverage_proofs}
 
 This section gives the deferred coverage proofs for
-Section~\mbox {III-D}--\mbox {VI-F}.
+Sections~\ref{subsec:agg_certificate_alg} and~\ref{subsec:agg_coverage_theory}.
 
 \begin{algorithm}[t]
 \caption{Aggregate coverage certificate (diagnostic Gate)}
@@ -1781,7 +1008,7 @@
 
 The same-backbone family below is evaluated with Design on, on both
 blocks, so the U-Air panels diagnose that arm rather than the setting the
-deployment uses there.  Table~III reports both settings on both blocks: Design
+deployment uses there.  Table~\ref{tab:main_effectiveness} reports both settings on both blocks: Design
 on for SensorScope and Design off for U-Air.
 
 \subsection{Windowed adaptations of FedAU, ObsUse, and TimeAlign}
@@ -1849,7 +1076,7 @@
 
 \begin{table}[t]
 \centering
-\caption{Validation-only under-served-block RMSE of the Table~III
+\caption{Validation-only under-served-block RMSE of the Table~\ref{tab:main_effectiveness}
 RAVEN configuration relative
 to FedAU-Window and ObsUse-Window (ten paired seeds; negative means
 the RAVEN row is better).  The reported settings are Design on for SensorScope and Design off for U-Air.
@@ -1868,6 +1095,8 @@
 \end{tabular}
 \end{table}
 
+
+
 \begin{figure}[t]
 \centering
 \includegraphics[width=\columnwidth]{fig3_e3_structural_mismatch.pdf}
@@ -1877,7 +1106,7 @@
 (c)(d)~U-Air $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$.
 SensorScope RAVEN-MCS is RAVEN-Design.  U-Air RAVEN-MCS in this
 figure uses Design on, not the Design-off rows of
-Table~III.}
+Table~\ref{tab:main_effectiveness}.}
 \label{fig:e3_structural}
 \end{figure}
 
@@ -1890,33 +1119,13 @@
 (c)(d)~U-Air $\mathrm{RMSE}_{\mu}$ and Tail RMSE.
 U-Air RAVEN-MCS here uses Design on.  The Design-off U-Air row
 ($\mathrm{RMSE}_{\mu}=1.1131$) is in
-Table~III.}
+Table~\ref{tab:main_effectiveness}.}
 \label{fig:e3_prediction}
 \end{figure}
 
-\begin{figure}[t]
-\centering
-\includegraphics[width=\columnwidth]{fig5_e4_component_ablation.pdf}
-\caption{One-factor component removal.  Positive bars mean that removing the
-component worsens the metric; $^\ast$ marks Holm-adjusted $p<0.05$.
-(a)(b)~SensorScope structural and prediction endpoints;
-(c)(d)~U-Air structural and prediction endpoints.
-Values with $|\delta|<0.05\%$ and no significance mark are left unlabeled.
-Sign reversals show endpoint- and dataset-dependent roles rather than
-uniformly additive benefits.  The corresponding numeric table remains
-Table~IV in the main paper.}
-\label{fig:e4_ablation}
-\end{figure}
-
-\begin{figure}[t]
-\raggedright
-\includegraphics[width=\columnwidth]{fig6_e4_uair_excl_design.pdf}
-\caption{U-Air component ablation excluding Design, magnified from
-Fig.~\ref{fig:e4_ablation}.  (a)~Structural mismatch;
-(b)~prediction risk.  Positive means removing the component worsens
-the metric; $^\ast$ marks Holm-adjusted $p<0.05$.}
-\label{fig:uair_excl_design}
-\end{figure}
+
+
+
 
 \subsection{Full Method Context on the Comparable Datasets}
 \label{app:e3_full_context}
@@ -1925,7 +1134,7 @@
 \centering
 \caption{SensorScope full method context (mean $\pm$ std over 20 seeds).
 Lower is better.  $^\dagger$ denotes reference-only context.
-RAVEN-Design is the Table~III method.}
+RAVEN-Design is the Table~\ref{tab:main_effectiveness} method.}
 \label{tab:app_e3_sensorscope}
 \scriptsize
 \setlength{\tabcolsep}{3pt}
@@ -1987,7 +1196,7 @@
 
 Table~\ref{tab:traffic_four_region} ranks the same windowed family on
 NSW-Traffic under a new public target map: four pre-specified coordinate
-regions, not the UTC H1--H4 groups of Table~III.
+regions, not the UTC H1--H4 groups of Table~\ref{tab:main_effectiveness}.
 Design is configured on for this block.
 $R$, $O$, and $U$ remain Complete-aligned protocol layers.
 This block evaluates a distinct public target map on the NSW-Traffic station
@@ -2040,7 +1249,7 @@
 
 Table~\ref{tab:app_block_rmse} reports the four UTC-block scores whose
 maximum is $\mathrm{WorstGroupRMSE}$ in
-Table~III.  The blocks are the public
+Table~\ref{tab:main_effectiveness}.  The blocks are the public
 deployment groups $00$--$06$, $06$--$12$, $12$--$18$, and $18$--$24$~UTC.
 The table decomposes the existing prediction endpoint by group.  On both datasets the
 worst block is $g=2$ ($12$--$18$~UTC).  The pre-registered under-served
@@ -2112,7 +1321,7 @@
 \subsection{Provenance of the w/o-Design Endpoint Trade-off}
 \label{app:design_provenance}
 
-The Design ablation in Section~\mbox {VII-E} exhibits an endpoint
+The Design ablation in Section~\ref{subsec:eval_rq3} exhibits an endpoint
 trade-off on U-Air.  A paired-window provenance audit covers
 774 windows.  Opportunity, observation, usable-update, and
 registration hashes are identical between full RAVEN and w/o-Design throughout
@@ -2124,7 +1333,7 @@
 \section{Intermittent Protocol Opportunity (INT-R)}
 \label{app:int_r}
 
-The main comparison and ablation ranking in Table~III uses
+The main comparison and ablation ranking in Table~\ref{tab:main_effectiveness} uses
 Complete-aligned protocol opportunity that is always-on: every mapped
 client receives an opportunity event in every window.  That setting does
 not contain mobile clients, and it does not use T-Drive trajectories.
@@ -2136,12 +1345,12 @@
 $A_{k,t}=1$, the existing Complete-aligned $O$/$U$ path is unchanged.
 Occupancy is a two-state Markov process, independent across the $K=8$
 logical clients, with mean active-fraction target $0.425$ taken from the
-already-published T-Drive scalar in Section~\mbox {VII-B}.  The
+already-published T-Drive scalar in Section~\ref{subsec:eval_rq1}.  The
 same $(\alpha,\beta)$ pair is used on both datasets.  T-Drive GPS is not
 overlaid on the stations.  The Design settings are not retuned from
 these RMSE values: they are configurations, and both are reported, so
-SensorScope and U-Air are shown with the settings recorded in Table~III.
-The coverage Gate audited in Section~\mbox {VII-F} is not used.
+SensorScope and U-Air are shown with the settings recorded in Table~\ref{tab:main_effectiveness}.
+The coverage Gate audited in Section~\ref{subsec:limitations} is not used.
 
 A Goh--Barab\'asi burstiness target of $+0.38$ was also declared.  The
 stability screen required to keep single-seed active fractions inside
@@ -2157,7 +1366,7 @@
 $\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$ remains above the
 pre-registered $0.05$ threshold ($0.309$ on SensorScope and $0.225$ on
 U-Air at seed $30001$), so intermittent occupancy does not erase the
-mismatch that Table~III is about.
+mismatch that Table~\ref{tab:main_effectiveness} is about.
 
 \begin{table}[!htbp]
 \centering
@@ -2181,7 +1390,7 @@
 \end{table}
 
 Table~\ref{tab:int_r_e3} ranks the same methods as
-Table~III on those traces ($20$ paired seeds).
+Table~\ref{tab:main_effectiveness} on those traces ($20$ paired seeds).
 Three always-on conclusions survive.  (i)~Four-block
 $\mathrm{WorstGroupRMSE}$ remains within the descriptive $+0.5\%$
 tolerance versus FedAU-Window
@@ -2201,13 +1410,13 @@
 $-0.05\%$, and removing Design changes $\Delta_{\mathrm{group}}$ by
 $+0.05\%$; neither contrast is significant ($p>0.05$).
 Every method also has higher absolute $\Delta_{\mathrm{group}}$ than in
-Table~III, about $1.33$ versus $1.01$ on SensorScope.
+Table~\ref{tab:main_effectiveness}, about $1.33$ versus $1.01$ on SensorScope.
 
 \begin{table*}[t]
 \centering
 \caption{INT-R robustness ranking under intermittent protocol $R$
 (mean $\pm$ std over 20 seeds).  Lower is better.  The Design
-settings are the same as in Table~III.  Design on for U-Air is also reported.
+settings are the same as in Table~\ref{tab:main_effectiveness}.  Design on for U-Air is also reported.
 The comparison uses intermittent protocol occupancy on station clients.}
 \label{tab:int_r_e3}
 \scriptsize
@@ -2237,7 +1446,7 @@
 
 \paragraph{Scope of the supplementary evidence.}
 The INT-R block uses the same two station datasets as
-Table~III with intermittent protocol opportunities, isolating sensitivity to
+Table~\ref{tab:main_effectiveness} with intermittent protocol opportunities, isolating sensitivity to
 the opportunity process on the same sensing data.
 
 \section{Support-Hypothesis Audit for A5, A6a, and A6b}
@@ -2348,7 +1557,7 @@
 both maxima, while the reported blocks use $20$.
 
 The consequence for the theory is the one recorded in the main text.  The
-stabilization error $\varepsilon_{\mathrm{stab}}$ of (37) does not vanish on
+stabilization error $\varepsilon_{\mathrm{stab}}$ of \eqref{eq:eps_stab} does not vanish on
 these traces: its median is $0$, because most windows leave every stabilizer
 inactive at the true margins, but it is strictly positive on $10.7\%$
 (SensorScope) and $11.1\%$ (U-Air) of active windows and reaches $0.553$ and
@@ -2431,7 +1640,7 @@
 
 Table~\ref{tab:scd_phi_freeze} collects the offline train-unit zero-target
 fraction of each block, together with the setting returned by the support
-rule (42).  The SensorScope/U-Air counts enumerate unique units in the full
+rule \eqref{eq:design_gate}.  The SensorScope/U-Air counts enumerate unique units in the full
 training split, not the current window's delivered updates.  The rule outputs
 coincide with the settings displayed in the rankings.  Use as a pre-window
 configuration requires this catalogue and the frozen target lookup to be
@@ -2446,7 +1655,7 @@
 \begin{table}[t]
 \centering
 \caption{Offline target-support statistic per block, and the Design
-setting returned by the support rule (42).
+setting returned by the support rule \eqref{eq:design_gate}.
 Zero test: frozen $\pi^{\mathrm{tar}}(k(i),s(i))$ for the occupancy-attached
 client; a missing key is $0$.
 The gate sets Design on exactly when this statistic is zero, and it does not
@@ -2459,11 +1668,11 @@
 \setlength{\tabcolsep}{2.5pt}
 \begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
 \toprule
-Block & $n_{\mathrm{train}}$ & $n_{\mathrm{zero}}$ & coverage & Design (42)\\
-\midrule
-SensorScope (Table~III) & $10285$ & $0$ & $0$ & on\\
-U-Air (Table~III) & $5688$ & $2016$ & $35.4\%$ & off\\
-T-Drive hybrid (Table~II) & $285659$ & $135268$ & $47.4\%$ & off\\
+Block & $n_{\mathrm{train}}$ & $n_{\mathrm{zero}}$ & coverage & Design \eqref{eq:design_gate}\\
+\midrule
+SensorScope (Table~\ref{tab:main_effectiveness}) & $10285$ & $0$ & $0$ & on\\
+U-Air (Table~\ref{tab:main_effectiveness}) & $5688$ & $2016$ & $35.4\%$ & off\\
+T-Drive hybrid (Table~\ref{tab:tdrive_hybrid}) & $285659$ & $135268$ & $47.4\%$ & off\\
 NSW-Traffic four-region (Table~\ref{tab:traffic_four_region}) & $18576$ & $0$ & $0$ & on\\
 City Scanner NYC {PM}$_{2.5}$ (Table~\ref{tab:cityscanner_hybrid}) & $9343$ & $0$ & $0$ & on\\
 City Scanner P2 meas.\ $O$ (Table~\ref{tab:cityscanner_p2_measured_o}) & $10141$ & $0$ & $0$ & on\\
```

## supplemental.tex

```diff
--- this-round-start/supplemental.tex
+++ current/supplemental.tex
@@ -72,7 +72,7 @@
 % Continue figure/table/equation numbers from the companion main paper.
 % Main has 4 figures, 7 tables, 1 algorithm (window-close configured Design) and
 % the support-gate / switch-point equations (42)-(43).
-% Numbered statements in main: Prop. 1--3, Thm. 1--2, Assumption 1.
+% Numbered statements in main: four propositions, two theorems, one assumption.
 \setcounter{figure}{4}
 \setcounter{table}{7}
 \setcounter{algorithm}{1}
@@ -94,29 +94,17 @@
 \subsection{The $\kappa=1000$ projection-with-debt rule}
 \label{app:kappa_probe}
 
-The projection-with-debt variant sets $\kappa=1000$, selected on tuning seeds,
-to measure sensitivity to the debt weight.  Against the projection alone it
-adds $+1.347$ pp and $+0.580$ pp
-(Holm $\approx10^{-5}$ on both), on SensorScope and U-Air respectively; at the
-frozen debt strength the same contrast is $+0.0073$ pp ($[0.0064,0.0083]$) on
-SensorScope, inside the equivalence band of
-Section~\ref{subsec:equivalence_band} in the main paper.  Numerical
-approximation relative to an independent projection computation is measured by
-$\varepsilon_{\mathrm{impl}}$, the distance
-between a trained rule's structural endpoints and those of the independently
-computed projection comparator.  That distance is reported in the $\Delta$ units of
-the structural endpoints and not as a relative tolerance: over all $240$ rule
-runs $\varepsilon_{\mathrm{impl}}$ is at most $2.42\times10^{-5}$ in those units,
-equivalently $1.21\times10^{-3}$ in the percentage-point convention of
-Section~\ref{subsec:equivalence_band}.  Against the smallest structural reading
-it accompanies, the frozen-strength debt contrast of $+0.0073$ pp
-($1.46\times10^{-4}$ in the same units), that is $17\%$; against the two headline
-structural contrasts, the design factor at $0.922$ pp and the projection against
-uniform weights at $0.768$ pp ($1.84\times10^{-2}$ and $1.54\times10^{-2}$), it is
-$0.13\%$ and $0.16\%$.  These ratios compare numerical approximation error
-with structural endpoint effects in the same units.  The reported effects
-describe the $\kappa=1000$ sensitivity variant separately from the standard
-RAVEN configuration.
+The independent projection-with-debt rule uses $\kappa=1000$, selected on
+tuning seeds.  Relative to projection, it improves group alignment by
+$1.347/.580$ pp on SensorScope/U-Air (Holm $\approx10^{-5}$), unlike the
+frozen-strength $.0073$ pp SensorScope effect inside the practical band.
+These gains are not standard-RAVEN benefits.
+The independent projection comparison gives maximum structural endpoint
+discrepancy $\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units
+across 240 runs, or $.00121$ pp.  It is 17\% of the small frozen-strength
+debt effect and $.13\%/ .16\%$ of the independent Design/projection contrasts.
+This endpoint discrepancy is not an optimizer certificate; the existing
+point-level optimality checks do not all pass.
 
 % Each PDF has its own bibliography. xr imports cross-references without bibcite.
 \bibliographystyle{IEEEtran}
```

