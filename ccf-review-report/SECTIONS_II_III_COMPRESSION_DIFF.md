# II与III局部压缩差异

以本轮开始时当前工作树为基准；保留摘要与引言。

## main.tex

```diff
--- this-round-start/main.tex
+++ current/main.tex
@@ -202,64 +202,47 @@
 \section{Related Work}
 \label{sec:related_work}
 
-Sparse MCS completion infers unsensed cells from a partial spatiotemporal
-field
-\cite{ganti2011mobile,guo2015mobile,ma2014opportunities,wang2023spatiotemporal,wang2023outlier,wang2023transformer,wang2024fewshot,li2024robust,wang2025evolutionary,xu2025rethinking,liu2026pyramid,zhang2026mapt,liu2026pricing}.
-Recruitment, incentives, and privacy
-\cite{liu2026multidimensional,zhang2025incentive,lu2025piece,zhang2026locally}
-are orthogonal and do not formulate deployment-target risk under sequential
-selection.
-
-Federated completion keeps sensing records on clients
-\cite{mcmahan2017communication,yang2019federated,kairouz2021advances,li2020federated}.
-Wang \emph{et al.}~\cite{wang2026federated} combine local completion with a
-time-aware architecture and asynchronous aggregation for sparse MCS, in whose
-spirit we study windowed rather than immediate-update asynchrony.
-FedAsync and staleness-aware variants update as models arrive
-\cite{xie2019asynchronous,liu2023adaptive,sun2024staleness,islam2025seafl,li2026stdfl};
-those works ask how to learn from the updates that participate, whereas
-RAVEN-MCS models which target mass those updates represent.  Federated conformal
-prediction builds label-set coverage under heterogeneity or label shift
-\cite{lu2023federated,plassier2023conformal}; the diagnostic Gate in
-Section~\ref{subsec:agg_certificate_alg} is a window-level lower bound on
-realized aggregate opportunity coverage $C_t$, not a prediction set and not the
-Design rule.
-
-Non-uniform participation is the complementary FL object.  Unified convergence
-under arbitrary participation, FedVARP, and anchor sampling address partial
-client presence \cite{wang2022unified,jhunjhunwala2022fedvarp,wu2023anchor}, and
-FedAU estimates aggregation weights from participation history so that unknown
-participation does not replace the original FL objective
-\cite{wang2024lightweight}.  Correlated availability and semi-asynchronous
-bias have likewise been debiased
-\cite{sun2025debiasing,chen2026fedcure}; agnostic FL optimizes a worst-case
-client mixture \cite{mohri2019agnostic}; and FedProx and SCAFFOLD address client
-drift \cite{li2020fedprox,karimireddy2020scaffold}.  These methods correct
-participation, while RAVEN-MCS additionally separates sensing-side opportunity
-and observation from update-side usability.
-FLOSS~\cite{goetze2025floss} reweights aggregation for client opt-out and stragglers.
-
-FedIPW~\cite{morishita2026who} factors client enrollment and round participation,
-and its limited-information extension calibrates enrolled clients to known
-population summaries.  Thus sequential IPW and population calibration are
-already available at the client level.  RAVEN instead links selections of atomic
-sensing units to a reference for the usable clients in each window, with distinct
-pre-observation and pre-delivery histories.
-FedPALS~\cite{listozec2024overcoming} matches a known target label distribution
-by convex aggregation and regularizes inverse sample-level ESS; it also treats
-targets outside the client convex hull.  RAVEN's reference projection acts in
-client-weight space, while its group term acts in composition space, with hard
-window-specific caps and client-level ESS constraints.  These operations are
-related calibration constructions, not identical projections.  Cross-window
-debt records residual group under-service.  The supplemental mechanism comparison
-distinguishes these information requirements and guarantee scopes.
-Classical survey estimators supply the H\'ajek building blocks
-\cite{horvitz1952generalization,hajek1971comment,shimodaira2000covariate,robins1994estimation},
-and importance weighting can lose effect in over-parameterized networks
-\cite{byrd2019importance}.  A nearest-neighbor
-comparison on target, selection, sensing-side correction, and finite-window
-calibration is in the supplemental material.
-
+Sparse MCS completion infers missing spatiotemporal values from partial
+observations~\cite{ganti2011mobile,guo2015mobile,ma2014opportunities,wang2023spatiotemporal,wang2023outlier,wang2023transformer,wang2024fewshot,li2024robust,wang2025evolutionary,xu2025rethinking,liu2026pyramid,zhang2026mapt,liu2026pricing}.
+Federated completion keeps records on clients, while asynchronous and
+staleness-aware methods address irregular update arrival
+\cite{mcmahan2017communication,yang2019federated,kairouz2021advances,li2020federated,wang2026federated,xie2019asynchronous,liu2023adaptive,sun2024staleness,islam2025seafl,li2026stdfl}.
+Their learning and timing mechanisms complement the question studied here:
+which deployment mass the participating updates represent.
+Windowed aggregation fixes the server decision boundary while allowing different
+client start times and model versions, so update content remains distinct from
+arrival time.
+
+Participation-aware FL addresses partial client presence through convergence
+analysis, update-memory correction, and sampling
+\cite{wang2022unified,jhunjhunwala2022fedvarp,wu2023anchor}.
+FedAU estimates participation-based aggregation weights
+\cite{wang2024lightweight}.  Related methods address correlated availability,
+semi-asynchronous bias, opt-out, and stragglers
+\cite{sun2025debiasing,chen2026fedcure,goetze2025floss}.
+These client-level treatments motivate separating participation from the
+opportunity and observation selections that determine each update's sensing-unit
+content.  RAVEN models all three layers with distinct information histories.
+
+FedIPW~\cite{morishita2026who} is a closer reference: it factors client enrollment
+and round participation, and its limited-information extension calibrates to
+population summaries.  Sequential weighting and population calibration are thus
+established at the client level.  FedPALS~\cite{listozec2024overcoming} matches a
+known target label distribution through convex aggregation, treats targets
+outside the client convex hull, and trades composition error against inverse
+sample-level ESS.  RAVEN connects an atomic sensing-unit reference reconstructed
+across sequential selections to the usable clients in each window, under
+pre-observation and pre-delivery information boundaries.  It imposes hard
+client caps and client-level ESS constraints on that support and tracks residual
+under-service through target debt.  Reference projection in client-weight space
+and target matching in composition space are related but distinct operations.
+The supplemental comparison details the information and guarantee scopes.
+A soft sample-size penalty and a hard client-support constraint control
+different sources of weight concentration.
+Classical IPW and H\'ajek estimators supply the statistical tools
+\cite{horvitz1952generalization,hajek1971comment,shimodaira2000covariate,robins1994estimation}.
+Their weighting need not improve prediction in over-parameterized networks
+\cite{byrd2019importance}.
 
 \section{System Model and Target-Mass Formulation}
 \label{sec:system_model}
@@ -267,68 +250,49 @@
 \subsection{Windowed Asynchronous Mobile Crowdsensing}
 \label{subsec:windowed_mcs}
 
-We consider a mobile crowdsensing (MCS) system with a server and clients
-$\mathcal{K}=\{1,\ldots,K\}$.  The prediction domain is partitioned into atomic
-units $i=(n,t)\in\mathcal{I}$, where $n$ is a spatial unit and $t$ an absolute
-time index; each unit carries a target value
-$Y_i\in\mathcal{Y}\subseteq\mathbb{R}$, revealed only if observed, and a
-label-free deployment context $C_i^{\mathrm{dep}}$.  All clients contribute to
-one completion predictor $f_{\theta}$ with parameters
-$\theta\in\Theta\subseteq\mathbb{R}^{d}$, returning
-$\widehat Y_i=f_{\theta}(i;C_i^{\mathrm{dep}})\in\mathcal{Y}$ and updated by
-local training and aggregation.  A client-side observation of unit $i$ is
-denoted by $Z_{k,r,i}$ when available to client $k$ in server window $r$.
-
-Server time is divided into aggregation windows
-$\mathcal{W}_r=[T_r,T_{r+1})$, during which the server keeps $\theta_r$ fixed.
-Client $k$ may start local training from a previously downloaded model
-$\theta_{\sigma_{k,r}}$ with $\sigma_{k,r}\le r$, and
-$\tau_{k,r}\triangleq r-\sigma_{k,r}$ is the model-version staleness of that
-attempt.  Updates may arrive at different times, but individual arrivals do not
-modify the global model: the server closes the window, determines which
-registered attempts are usable, computes one aggregation vector, and performs the
-single transition $\theta_r\rightarrow\theta_{r+1}$.  This
-\emph{windowed-asynchronous} semantics is distinct from immediate-update
-FedAsync and keeps exogenous mobile/update events independent of the
-method-specific aggregation weights.
+A server coordinates clients $\mathcal K=\{1,\ldots,K\}$ over atomic units
+$i=(n,t)\in\mathcal I$, with spatial index $n$, absolute time $t$, target
+$Y_i\in\mathcal Y\subseteq\mathbb R$, and label-free deployment context
+$C_i^{\mathrm{dep}}$.  The target is revealed only if observed, with client
+measurement $Z_{k,r,i}$ in window $r$.  Clients train one completion predictor
+$f_\theta$, $\theta\in\Theta\subseteq\mathbb R^d$, producing
+$\widehat Y_i=f_\theta(i;C_i^{\mathrm{dep}})\in\mathcal Y$.
+
+The server holds $\theta_r$ fixed throughout
+$\mathcal W_r=[T_r,T_{r+1})$.  Client $k$ may start from an older model
+$\theta_{\sigma_{k,r}}$, $\sigma_{k,r}\le r$, with model-version staleness
+$\tau_{k,r}=r-\sigma_{k,r}$.  At close, the server determines usable attempts
+and performs one aggregation transition $\theta_r\to\theta_{r+1}$.
+Individual arrivals do not trigger updates as in immediate-update FedAsync.
+For comparison, the protocol freezes exogenous mobile/update events across
+methods without assuming general statistical independence.
+Local training and delivery remain asynchronous, while the server decides
+aggregation weights jointly over the window's usable clients.
 
 \subsection{Two-Stage, Three-Layer Non-Random Selection}
 \label{subsec:selection_process}
 
-Two-stage selection consists of a sensing-side stage with two
-layers, mobile opportunity and actual observation, and an update-side stage that
-determines whether a registered client attempt becomes usable before window
-closure.
-
-For client $k$, window $r$, and unit $i$, let
-$R_{k,r,i}\in\{0,1\}$ be the realized mobile opportunity indicator, which states
-whether $(k,i)$ belongs to the opportunity/risk set in window $r$ before the
-current sensing outcome is revealed.  Conditional on $R_{k,r,i}=1$,
-$O_{k,r,i}\in\{0,1\}$ indicates whether unit $i$ is actually observed.  A client
-with a nonempty observed buffer registers an update attempt, and the set of
-registered clients is $\mathcal{E}_r$.  For $k\in\mathcal{E}_r$ the attempted
-update is usable ($U_{k,r}=1$) only if computation and transmission succeed, the
-update arrives by $T_{r+1}$, and its staleness satisfies
-$\tau_{k,r}\le S_{\max}$, the block's frozen maximum admissible model-version
-staleness; otherwise $U_{k,r}=0$.  We first define the usable set
-$\mathcal{U}_r\triangleq\{k\in\mathcal{E}_r:U_{k,r}=1\}$;
-Section~\ref{sec:reconstruction} then removes zero-mass clients and forms the
-actual aggregation set $\mathcal{A}_r\subseteq\mathcal{U}_r$.  Failures, timeouts, network
-interruptions, and stale arrivals remain recorded as $U_{k,r}=0$ rather than
-disappearing from the selection log.
-
-We distinguish two structural mappings from units to finite label-free index
-sets: the \emph{deployment-target group} $h:\mathcal{I}\to\mathcal{G}$ and the
-\emph{opportunity stratum} $s:\mathcal{I}\to\mathcal{S}$, with $\mathcal{G}$ and
-$\mathcal{S}$ the finite sets of deployment groups and opportunity strata.  The
-group mapping specifies which deployment mass the predictor should serve, whereas
-the stratum mapping pools repeatable mobile exposure patterns for selection
-modeling, so the two are different scientific objects and $h(i)\neq s(i)$ in
-general.  Both are frozen from public/training-side information and do not use
-test-label values.
-
-For theoretical bookkeeping, let the normalized opportunity-event law in
-window $r$ be
+The sensing stage comprises opportunity $R$ and observation $O$, followed by
+update usability $U$.  The indicator $R_{k,r,i}\in\{0,1\}$ places $(k,i)$ in
+the opportunity/risk set before sensing.  Conditional on $R_{k,r,i}=1$,
+$O_{k,r,i}\in\{0,1\}$ records observation.  A nonempty observed buffer
+registers a client in $\mathcal E_r$.  Its attempt has $U_{k,r}=1$ only if
+computation and transmission succeed by $T_{r+1}$ with
+$\tau_{k,r}\le S_{\max}$, the frozen admissible staleness.  Failed attempts
+remain logged as $U_{k,r}=0$.  The usable set is
+$\mathcal U_r=\{k\in\mathcal E_r:U_{k,r}=1\}$.  Removing zero-mass clients in
+Section~\ref{sec:reconstruction} yields the aggregation set
+$\mathcal A_r\subseteq\mathcal U_r$.
+Usability is shared by the sensing records in a registered attempt, whereas
+opportunity and observation are indexed by unit.  The registered, usable, and
+positive-mass sets consequently have different roles in selection modeling,
+reference normalization, and aggregation.
+
+The label-free maps $h:\mathcal I\to\mathcal G$ and
+$s:\mathcal I\to\mathcal S$ specify deployment groups and opportunity strata.
+The former defines the mass to be served, whereas the latter pools mobile exposure for
+selection modeling.  They need not coincide and are frozen from public or
+training-side information without test labels.  The normalized opportunity law is
 \begin{equation}
  P_r^{\mathrm{opp}}(k,i)
  =
@@ -338,14 +302,10 @@
  \sum_{k,i}P_r^{\mathrm{opp}}(k,i)=1,
  \label{eq:opp_event_law}
 \end{equation}
-where $\pi^{\mathrm{opp}}_{k,s,r}$ is the client--stratum opportunity mass and
-$\nu^{\mathrm{opp}}_{k,r}(i\mid s)$ is the conditional atomic opportunity law.
-The realized risk-set indicators $R_{k,r,i}$ are the implementation-level
-bookkeeping of the opportunity events induced by this mobile exposure process;
-they are not assumed to be mutually independent Bernoulli draws.
-
-The subsequent selection probabilities are conditional on the same process, with
-$\Pr\{\cdot\}$ that probability.
+Here $\pi^{\mathrm{opp}}_{k,s,r}$ is client--stratum opportunity mass and
+$\nu^{\mathrm{opp}}_{k,r}(i\mid s)$ is its conditional atomic law.  The
+realized $R_{k,r,i}$ record events from this process, not mutually independent
+Bernoulli draws.  Subsequent selection probabilities are
 \begin{align}
  p^{\mathrm{obs}}_{k,r,i}
  &\triangleq
@@ -364,20 +324,22 @@
  \right).
  \label{eq:quse_def}
 \end{align}
-The observation history $\mathcal{H}^{\mathrm{obs}}_{k,r,i}$ contains
-only information available before $O_{k,r,i}$ is realized.  The
-usable-update history $\mathcal{H}^{\mathrm{use}}_{k,r}$ is measured
-after the sensing-side stage but before $U_{k,r}$ is realized.  It may
-therefore contain the already observed registration state, but not the
-realized computation/transmission outcomes, future events, or the
-current update vector used for aggregation.  This sequential
-information boundary is part of the statistical model.
+The history $\mathcal H^{\mathrm{obs}}_{k,r,i}$ contains only information
+available before $O_{k,r,i}$.  The pre-$U$ history
+$\mathcal H^{\mathrm{use}}_{k,r}$ may include the already realized sensing-side
+registration state, but excludes the realized computation/transmission outcome,
+future events, and the current update vector to be weighted.  Separate histories
+preserve the sequential information boundary without assuming independent
+selection layers.
+The opportunity law describes how sensing units enter risk sets, not which
+responses are subsequently observed.  A target group can span several
+opportunity strata, so its desired mass cannot be substituted for a stratum's
+selection probability.
 
 \subsection{Public Deployment Target and Compatible Target Measures}
 \label{subsec:target_measures}
 
-We begin with a public, label-independent atomic deployment target over the
-deployment domain $\mathcal{I}_{\mathrm{dep}}\subseteq\mathcal{I}$,
+The public atomic target on $\mathcal I_{\mathrm{dep}}\subseteq\mathcal I$ is
 \begin{equation}
     \varpi_i^{\mathrm{tar}}\ge0,
     \qquad
@@ -386,13 +348,12 @@
     \label{eq:atomic_target}
 \end{equation}
 Its deployment-group marginal is
-$\mu_g=\sum_{i:h(i)=g}\varpi_i^{\mathrm{tar}}$, so
-$\boldsymbol{\mu}\in\Delta^{|\mathcal{G}|-1}$.
-These define the application-level target served by the deployed
-predictor.  Opportunity correction uses a compatible client--stratum target
-$\pi^{\mathrm{tar}}_{k,i}$ built from the stratum mass of $s(i)$, a frozen
-public client share, and the conditional atomic law on $s(i)$
-(supplemental material).  Compatibility requires
+$\mu_g=\sum_{i:h(i)=g}\varpi_i^{\mathrm{tar}}$, with
+$\boldsymbol\mu\in\Delta^{|\mathcal G|-1}$.  Opportunity correction uses a
+compatible client--atomic target $\pi^{\mathrm{tar}}_{k,i}$, whose
+client--stratum marginal is
+$\pi^{\mathrm{tar}}_{k,s}=\sum_{i:s(i)=s}\pi^{\mathrm{tar}}_{k,i}$.
+Compatibility requires
 \begin{equation}
     \sum_k\pi^{\mathrm{tar}}_{k,i}
     =
@@ -401,39 +362,21 @@
     \sum_{k,s}\pi^{\mathrm{tar}}_{k,s}=1.
     \label{eq:target_compatibility}
 \end{equation}
-Equation~\eqref{eq:target_compatibility} is the bridge between the
-deployment-risk target and the client--stratum target used for Design
-and coverage.  Define $I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$.
-The unit lookup used by the target-coverage statistic, and the pair opportunity
-mass used by $C_t$, are constructed in the supplemental material.
-All target quantities are frozen before test-label evaluation.
-The window configuration $D_t\in\{\mathrm{on},\mathrm{off}\}$ is recorded
-before window $t$ opens and remains fixed during local training and
-window-close aggregation.  The reported on/off arms keep the same setting
-across all windows of a run.
-
-\subsection{Aggregate Coverage Certification Object}
-\label{subsec:agg_coverage_object}
-
-Realized aggregate coverage is
-\begin{equation}
- C_t
- =
- \sum_{(k,s)\in I_{\mathrm{tar}}}
- \pi^{\mathrm{tar}}_{k,s}
- \,
- \mathbf{1}\!\left\{\pi^{\mathrm{opp}}_{k,s,t}\ge\pi_{\mathrm{safe}}\right\},
- \label{eq:agg_Ct}
-\end{equation}
-where $\pi^{\mathrm{opp}}_{k,s,t}$ is the lagged opportunity mass of
-that pair, $\pi_{\mathrm{safe}}$ is a frozen threshold, and
-$\mathbf{1}\{\cdot\}$ is the indicator of the event in braces.
+This connects the deployment-risk target to the correction reference.
+The atomic measure assigns importance to sensing units independently of client
+allocation.  The compatible client--atomic measure distributes the same target
+mass among clients, while its stratum marginal pools units for opportunity
+correction.  Consistency across these levels lets corrected client masses
+represent the deployment groups used for evaluation.
+The construction in Appendix~\ref{app:deferred_constructions} uses public
+client shares and conditional atomic target masses, all frozen before
+test-label evaluation.  Design is configured before each window and fixed
+within it, as specified in Section~\ref{subsec:agg_certificate_alg}.
 
 \subsection{Deployment-Target Risk Versus Arrival Risk}
 \label{subsec:target_risk}
 
-For the squared loss
-$\ell(\widehat Y,Y)=\tfrac{1}{2}(\widehat Y-Y)^2$, the deployment-target risk is
+For squared loss $\ell(\widehat Y,Y)=\tfrac12(\widehat Y-Y)^2$, define
 \begin{equation}
  \mathcal{R}_{\mu}(\theta)
  =
@@ -444,16 +387,10 @@
  \right).
  \label{eq:target_risk}
 \end{equation}
-The data reaching learning, by contrast, follow the
-opportunity, observation, and usable-update mechanisms.
-
-For evaluation, quantities without a window index denote the frozen
-evaluation-period marginals of their corresponding pre-outcome mechanisms.
-Under \eqref{eq:opp_event_law}--\eqref{eq:quse_def}, the joint sequential
-probability that client $k$ contributes unit $i$ to learning is
-$P^{\mathrm{opp}}(k,i)\,p^{\mathrm{obs}}_{k,i}\,q^{\mathrm{use}}_{k}$, and the
-label-free atomic arrival intensity is the corresponding sum, evaluated by the
-plug-in
+Quantities without a window index below denote frozen evaluation-period
+marginals of the corresponding pre-outcome mechanisms.  The sequential
+inclusion law is $P^{\mathrm{opp}}(k,i)p^{\mathrm{obs}}_{k,i}q^{\mathrm{use}}_k$.
+The label-free arrival intensity is estimated by
 \begin{equation}
  \widehat r_i^{\mathrm{arr}}
  =
@@ -464,9 +401,9 @@
  \widehat q^{\mathrm{use}}_{k,s(i)},
  \label{eq:arrival_intensity}
 \end{equation}
-where $\widehat q^{\mathrm{use}}_{k,s}$ is the evaluation-period marginal of the
-legal pre-$U$ usable-update model over registered attempts associated with
-stratum $s$.  Normalize
+Here $\widehat q^{\mathrm{use}}_{k,s}$ is the evaluation-period marginal of
+the legal pre-$U$ model over registered attempts associated with stratum $s$,
+not a probability conditioned on the realized delivery outcome.  Normalize
 \begin{equation}
  \widetilde\rho_i^{\mathrm{arr}}
  =
@@ -485,37 +422,34 @@
  \right).
  \label{eq:arrival_risk}
 \end{equation}
-The deployment-target risk
-$\mathcal{R}_{\mu}$ measures how accurately the predictor serves the deployment
-population it is intended for, and the arrival risk $\mathcal{R}_{\rho}$ measures
-how accurately it fits the updates that actually reach training; the loss and the
-predictor are the same in both, and only the weighting law differs.  Since
-opportunity, observation, and usable-update selection are non-random, those two
-populations need not coincide, so accuracy on the arriving updates need not
-transfer to the deployment population and RAVEN-MCS treats deployment-target mass
-alignment, rather than usable-update frequency, as the reference semantics of the
-learning problem.
+The two risks differ in their weighting laws.  Sequential selection makes them
+non-interchangeable in general, although the same predictor and loss may yield
+equal values under both.  The arrival law above is a plug-in estimate of the
+population law.
+Normalization is over the deployment domain, so both risks refer to the same
+sensing units.  Evaluation-period pooling specifies the comparison weights
+without replacing replace the attempt-level conditional probability used for training-time
+correction.
 
 \subsection{Structural Alignment Objective}
 \label{subsec:design_objective}
-\label{subsec:equivalence_band}
-
-Section~\ref{sec:reconstruction} will construct two corrected within-client
-compositions: a deployment-group composition
-$\mathbf{c}^{g}_{k,r}\in\Delta^{|\mathcal{G}|-1}$ and an opportunity-stratum
-composition $\mathbf{c}^{s}_{k,r}\in\Delta^{|\mathcal{S}|-1}$.  For the final
-aggregation set $\mathcal{A}_r$, define
-$M_r=[\mathbf{c}^{g}_{k,r}]_{k\in\mathcal{A}_r}$.  Given feasible aggregation
-weights $\boldsymbol\alpha_r\in\mathcal{C}_r$, the effective deployment-group
-composition in an active window is $\boldsymbol\omega_r=M_r\boldsymbol\alpha_r$;
-the feasible set $\mathcal{C}_r$ is \eqref{eq:Cr}, and $\boldsymbol\alpha_r$ is
-determined by the calibration program (P2) of Section~\ref{subsec:P2} rather than
-supplied as an input.
-
-Let $\eta_r>0$ denote the server step size and define
-$I_r=\mathbf{1}\{|\mathcal{A}_r|>0\}$ and
-$S_R=\sum_{r=0}^{R-1}\eta_r I_r$.
-For $S_R>0$,
+
+Section~\ref{sec:reconstruction} constructs normalized within-client group and
+stratum compositions $\mathbf c^g_{k,r}\in\Delta^{|\mathcal G|-1}$ and
+$\mathbf c^s_{k,r}\in\Delta^{|\mathcal S|-1}$.  Set
+$M_r=[\mathbf c^g_{k,r}]_{k\in\mathcal A_r}$.  Feasible weights
+$\boldsymbol\alpha_r\in\mathcal C_r$ produce group composition
+$\boldsymbol\omega_r=M_r\boldsymbol\alpha_r$.  (P2) determines the weights
+on the support constrained by \eqref{eq:Cr}.  This separates what the corrected
+updates represent from the mixtures that aggregation can execute.
+Each column of $M_r$ is a corrected group composition, not a raw record count.
+Client weights change aggregate mass only along directions supplied by these
+columns and permitted by the feasible set.  Several clients need not offer
+distinct group compositions.
+
+For server step size $\eta_r>0$, let
+$I_r=\mathbf1\{|\mathcal A_r|>0\}$ and
+$S_R=\sum_{r=0}^{R-1}\eta_r I_r$.  All prefix averages below require $S_R>0$:
 \begin{equation}
     \overline{\boldsymbol\omega}_R
     =
@@ -524,33 +458,11 @@
     \eta_r I_r\boldsymbol\omega_r.
     \label{eq:omega_bar}
 \end{equation}
-We measure the group-level structural mismatch
-$\Delta_{\mathrm{group}}(R)=\left\|
-\overline{\boldsymbol\omega}_R-\boldsymbol\mu
-\right\|_1$,
-the $\ell_1$ distance between the time-averaged effective deployment-group
-composition and the deployment target.  Both sides are probability vectors
-over $\mathcal{G}$, so $0\le\Delta_{\mathrm{group}}\le2$.  Both structural
-endpoints are quoted in percentage points of target mass,
-$\mathrm{pp}=\Delta/2\times100$.  Structural contrasts are reported relative to
-uniform server weights $\alpha_{k,r}=1/|\mathcal{A}_r|$ and, where they turn on
-the reference, in units of the closable gap between uniform weighting and the
-same-support hindsight optimum, at the same active set, the same $M_r$, the same
-$\mathcal{C}_r$, and with all windows known in advance.  That gap is $3.44$ pp of
-target mass on SensorScope and $1.32$ pp on U-Air (protocol~$R$ always-on) over
-the $20$ seeds.  The pre-registered equivalence band is $\pm0.10$ in those
-units, and a contrast is read as inside the band when its paired interval lies
-within $\pm0.10$; a component removal is read as necessary only when that
-interval lies entirely beyond the band in the worsening direction, and the band
-itself is a practical-significance convention rather than a hypothesis test.
-The band and this reading rule were fixed before the ladder runs, and
-\texttt{w1/ladder\_v3/PREREG.md} in the released bundle states both.
-Read-only ladder contrasts instead use the report-half subset, whose
-same-support optimum differs slightly, so band verdicts are not convertible
-between the two.
-
-For client--stratum structure, extend $\alpha_{k,r}=0$ to
-$k\notin\mathcal{A}_r$ and define
+The group mismatch is
+$\Delta_{\mathrm{group}}(R)=\|\overline{\boldsymbol\omega}_R-\boldsymbol\mu\|_1$.
+The average weights active windows by server step size rather than elapsed wall
+time, keeping the structural readout on the same update scale as target debt.
+Extend $\alpha_{k,r}=0$ to inactive clients $k\notin\mathcal A_r$ and define
 \begin{equation}
  \widehat\Pi_{k,s}(R)
  =
@@ -561,9 +473,6 @@
  c^{s}_{k,r,s}.
  \label{eq:Pi_hat_ks}
 \end{equation}
-Because each active-window $\boldsymbol\alpha_r$ and each
-$\mathbf{c}^{s}_{k,r}$ are probability vectors,
-$\sum_{k,s}\widehat\Pi_{k,s}(R)=1$.  We therefore measure
 \begin{equation}
  \Delta_{c\text{-}s}(R)
  =
@@ -573,10 +482,14 @@
  \right|.
  \label{eq:delta_cs}
 \end{equation}
-The overall design goal is to keep $\mathcal{R}_{\mu}$ low while
-reducing $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$ under
-time-varying mobile feasibility and legal pre-outcome information.
-
+Normalization gives $\sum_{k,s}\widehat\Pi_{k,s}(R)=1$.  Both structural
+distances lie in $[0,2]$ and convert to target-mass percentage points by
+$\mathrm{pp}=50\Delta$.  The Uniform ruler, same-support hindsight comparison,
+and practical equivalence convention are specified in
+Section~\ref{subsec:equivalence_band}.
+The objective is to improve structural alignment under time-varying feasibility
+and legal information boundaries while evaluating deployment-target prediction
+risk.
 
 \section{Selection-Layer-Aware Target Reconstruction}
 \label{sec:reconstruction}
@@ -939,6 +852,24 @@
 
 \subsection{Finite-Sample Aggregate Coverage Certificate}
 \label{subsec:agg_certificate_alg}
+\label{subsec:agg_coverage_object}
+
+The auxiliary coverage diagnostic uses target-positive pairs
+$I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$ and realized coverage
+\begin{equation}
+ C_t
+ =
+ \sum_{(k,s)\in I_{\mathrm{tar}}}
+ \pi^{\mathrm{tar}}_{k,s}
+ \,
+ \mathbf{1}\!\left\{\pi^{\mathrm{opp}}_{k,s,t}\ge\pi_{\mathrm{safe}}\right\},
+ \label{eq:agg_Ct}
+\end{equation}
+Here $\pi^{\mathrm{opp}}_{k,s,t}$ is lagged opportunity mass and
+$\pi_{\mathrm{safe}}$ is a frozen threshold.  The pair masses and unit lookup
+are specified in Appendix~\ref{app:itar_lookup}.  Unlike federated conformal
+prediction sets~\cite{lu2023federated,plassier2023conformal}, this diagnostic
+assesses aggregate opportunity coverage.
 
 The Design factor $\eqref{eq:design_factor}$ is configured on or off.  A
 diagnostic Gate, detailed as the aggregate coverage certificate algorithm of the
@@ -1557,6 +1488,22 @@
 Structural alignment is
 $\Delta_{\mathrm{group}}(R)=\left\|\overline{\boldsymbol\omega}_R-\boldsymbol\mu\right\|_1$
 and $\Delta_{c\text{-}s}$ in \eqref{eq:delta_cs}; smaller is better.
+
+\paragraph{Structural comparison convention.}
+\label{subsec:equivalence_band}
+Structural contrasts use Uniform weights $\alpha_{k,r}=1/|\mathcal A_r|$
+as a ruler.  Reference-side effects also use the closable gap from Uniform to
+the hindsight optimum with the same active sets, $M_r$, and $\mathcal C_r$,
+knowing all windows in advance.  Across all 20 seeds this gap is $3.44$ pp
+on SensorScope and $1.32$ pp on U-Air under always-on protocol $R$.
+In closable-gap units, the pre-registered practical band is $\pm0.10$:
+a contrast is inside only if its paired interval lies entirely within the band;
+a removed component is necessary only if the interval is entirely beyond it in
+the worsening direction.  This is a practical-significance convention, not a
+hypothesis test.  Both rules were fixed before the ladder runs in the released
+\texttt{w1/ladder\_v3/PREREG.md}.  Read-only report-half contrasts use a slightly
+different same-support optimum and cannot inherit all-seed trained-comparison
+band verdicts.
 
 All formal method comparisons are paired by seed, using the paired Wilcoxon
 protocol~\cite{wilcoxon1945individual} with Holm
```

## appendix.tex

```diff
--- this-round-start/appendix.tex
+++ current/appendix.tex
@@ -59,7 +59,7 @@
 \subsubsection{Target-Positive Pairs, Coverage, and the Heuristic Lookup}
 \label{app:itar_lookup}
 The set $I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$ and the
-coverage $C_t$ in (6) use $\pi^{\mathrm{tar}}_{k,s}$ from
+coverage $C_t$ in \eqref{eq:agg_Ct} use $\pi^{\mathrm{tar}}_{k,s}$ from
 \eqref{eq:target_ks_mass}.  For unit $i$, $k(i)$ is the unique FL client
 attached to $i$ on the frozen occupancy map: the spatial identity of $i$
 under the same client map that builds \eqref{eq:target_ks_mass}.
@@ -76,7 +76,7 @@
 window opens; both fixed on/off settings are reported.
 The pair opportunity mass $\pi^{\mathrm{opp}}_{k,s,t}$ is
 $F_{t-}$-measurable on the same client--stratum key.
-Because $\sum_{k,s}\pi^{\mathrm{tar}}_{k,s}=1$, (6) equals
+Because $\sum_{k,s}\pi^{\mathrm{tar}}_{k,s}=1$, \eqref{eq:agg_Ct} equals
 the ratio of certified mass to total positive target mass.
 Per-block lookup constructions and the published coverage statistic are in
 Table~\ref{tab:scd_phi_freeze}.
@@ -93,7 +93,7 @@
  =1.
  \label{eq:A2_use_mean_ignorability}
 \end{equation}
-The coordinate cap and $\ell_2$ support bound in (25) are
+The coordinate cap and $\ell_2$ support bound in \eqref{eq:Cr} are
 \begin{equation}
 \begin{aligned}
  \overline\alpha_r
@@ -772,7 +772,7 @@
 \noindent\emph{Proof.}
 Fix an active window $r$ and the common set $\mathcal{A}_r$.  Write
 $\widehat a$ and $\widehat d$ for the implemented plug-in ratios
-(16) and (23) evaluated at the estimates, and
+\eqref{eq:a_stabilized} and \eqref{eq:d_use} evaluated at the estimates, and
 $a^{\mathcal T}$ and $d^{\mathcal T}$ for the same two maps evaluated at the
 true margins,
 \[
@@ -817,7 +817,7 @@
 $L_p=1/p_{\min}^2$.  A6b bounds the right-hand sides by
 $L_\pi\varepsilon_\pi+L_p\varepsilon_p$ and $L_q\varepsilon_q$.
 
-\emph{Step 2 (mass error).}  Each sum in (17) has at most $n_r$
+\emph{Step 2 (mass error).}  Each sum in \eqref{eq:m_total} has at most $n_r$
 terms, so
 $\lvert m_k-m^{\mathcal T}_{k}\rvert
 \le n_r\max_i\lvert a_{k,r,i}-a^{\mathcal T}_{k,r,i}\rvert$, and with
@@ -946,7 +946,7 @@
 mass $S_R$ to obtain the stated bound.
 
 We now prove the deterministic relation in
-(27).  Recall
+\eqref{eq:debt_bound}.  Recall
 \begin{equation}
     S_R
     =
@@ -1122,7 +1122,7 @@
     \label{eq:app_debt_bound_final}
 \end{equation}
 This is exactly the accounting relation stated in
-(27). \hfill$\square$
+\eqref{eq:debt_bound}. \hfill$\square$
 
 \paragraph{Consequence.}
 If the cumulative debt is sublinear in active step mass, that is,
@@ -2315,7 +2315,7 @@
 client-window has a vanishing usable margin, and the smallest window-level
 H\'ajek mass is $5.521$ on SensorScope and $16.89$ on U-Air.  The positivity
 and normalization steps of Proposition~2 and the denominator in
-(24) are therefore not degenerate on these traces.
+\eqref{eq:beta_ref} are therefore not degenerate on these traces.
 
 The one qualification is structural rather than numerical.  A usable-update
 margin of exactly zero occurs for $22.84\%$ of SensorScope and $23.75\%$ of
```

