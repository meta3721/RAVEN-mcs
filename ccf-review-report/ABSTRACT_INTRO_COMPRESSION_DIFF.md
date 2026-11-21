# 摘要与引言本轮差异

基准为本轮开始的当前工作树，不回退前轮修改。仅修改摘要与引言正文，框架图保持。

```diff
--- this-round-start/main.tex
+++ current/main.tex
@@ -69,26 +69,25 @@
 
 
 \begin{abstract}
-Mobile crowdsensing completion learns from data selected by opportunity,
-observation, and update delivery.  The resulting arrival distribution can differ
-from the deployment target, yet correcting that distribution does not make the
-target realizable by the clients in a finite window.  RAVEN-MCS connects these
-two problems: it reconstructs a selection-corrected reference over atomic sensing
-units from sequential pre-outcome histories, then calibrates the reference under
-window-specific support, client caps, and effective-support constraints.  The
-full criterion combines reference fidelity with group matching, uncertainty,
-staleness, and accumulated target debt.  We establish ideal target-moment recovery
-under support and identification assumptions and fixed-window calibration
-stability.  Paired experiments distinguish the gains already explained by uniform
-aggregation from the increment due to the corrected reference.  On SensorScope,
-reference projection reduces group mismatch by $0.768$ percentage points relative
-to Uniform; a separate same-support comparison of projected references with and
-without Design gives $0.922$ points.  These are distinct contrasts.  Joint
-structural, prediction, and runtime comparisons show that improved mass alignment
-does not consistently improve prediction, and that a simpler projection can
-outperform the full criterion on structure and cost.  The framework separates
-population reconstruction, finite-window realizability, and their measured
-consequences for completion.
+Mobile crowdsensing completion learns from observations selected by opportunity,
+observation, and update delivery.  Correcting the resulting arrival distribution
+can recover a deployment-target reference, but that reference may remain
+unrealizable by the clients available in a finite window.  RAVEN-MCS connects
+sequential reference reconstruction over atomic sensing units to feasible
+calibration on the current client support, with client weight caps and
+effective-support constraints.  Its aggregation program balances reference
+fidelity against target composition and accumulated under-service, using
+selection histories available before each outcome.  We establish ideal
+target-moment recovery under support and identification assumptions and
+calibration stability at a fixed window state.  Paired comparisons on shared
+client support distinguish
+structural gains explained by Uniform from the increment supplied by the
+corrected reference: on SensorScope, a feasible reference-projection comparator
+reduces group mismatch by $0.768$ percentage points relative to Uniform.
+Structural alignment does not consistently improve prediction, and projection
+can achieve lower group mismatch and runtime than the full RAVEN criterion.
+These findings separate the roles of population reconstruction and finite-window
+calibration in federated completion.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -99,69 +98,56 @@
 \section{Introduction}
 \label{sec:introduction}
 
-Mobile crowdsensing (MCS) collects urban and environmental data from mobile
-devices without a dense dedicated infrastructure
-\cite{ganti2011mobile,guo2015mobile,ma2014opportunities}.
-Continuous sensing is costly and participation is intermittent, so practical
-systems observe only a sparse field and rely on completion
-\cite{wang2023outlier,li2024robust,wang2023transformer,wang2024fewshot,wang2025evolutionary,xu2025rethinking,liu2026pyramid,zhang2026mapt}.
-Federated learning trains those models without centralizing raw records
-\cite{mcmahan2017communication,yang2019federated,kairouz2021advances,li2020federated},
-including asynchronous aggregation for irregular or stale updates
-\cite{wang2026federated,xie2019asynchronous,liu2023adaptive,sun2024staleness}.
-The system studied here is \emph{windowed asynchronous}: one global update per
-window at close, not immediate-update FedAsync.
-
-A less visible issue arises before aggregation: \emph{the data that reach the
-server are not necessarily sampled from the distribution that the deployed
-predictor is intended to serve}.  For an atomic sensing target $i$, a mobile
-client must first have an opportunity to cover $i$, the target must then actually
-be observed, and finally the client's local update must complete computation and
-communication before the server's usable-update deadline.  The two-stage MCS
-process therefore contains three distinct selection layers, mobile opportunity
-$R$, observation $O$, and usable update $U$, whose probabilities depend on
-mobility, sensing conditions, resource state, network quality, deadlines, and
-staleness.  Even when each layer is operationally reasonable, their composition
-can make the distribution of observed and successfully delivered data differ
-from the public deployment target, so optimizing the distribution induced by
-arriving updates can optimize the \emph{wrong population risk}.
-
-Sparse MCS completion
-primarily asks how to infer missing values from the available observations
-\cite{wang2023spatiotemporal,li2024robust}; asynchronous federated completion
-asks how to learn effectively from irregular or stale client updates
-\cite{wang2026federated,sun2024staleness}; and participation-aware FL studies
-partial, arbitrary, or biased client participation
-\cite{wang2022unified,jhunjhunwala2022fedvarp,wu2023anchor,wang2024lightweight,sun2025debiasing,mohri2019agnostic,chen2026fedcure,morishita2026who}.
-These directions establish that sparsity, asynchrony, and non-uniform
-participation matter.  Target-aware aggregation also studies population
-selection and target matching~\cite{morishita2026who,listozec2024overcoming}.
-The remaining MCS question is:
-\emph{how should one align asynchronous federated data completion with a
-deployment target when sensing-side availability and update-side usability
-jointly select the data that enter learning?}  Correcting only the final
-client-participation distribution does not identify whether the distortion arose
-from mobile opportunity, actual observation, or usable-update censoring, and
-reconstructing a statistically correct target mass does not imply that this mass
-is realizable by the clients available in a finite mobile window.
-
-We develop \textbf{RAVEN-MCS}, short for \textbf{Reference Alignment Via
-Exposure-aware Normalization for Mobile CrowdSensing}.  RAVEN-MCS treats
-deployment-target mass alignment, rather than raw update frequency, as the
-reference semantics of asynchronous federated data completion.  As illustrated in
-Fig.~\ref{fig:raven_overview}, the method separates the public deployment target
-from the arrival/usable-update law, then factors the opportunity, observation,
-and usable-update layers under their legal pre-outcome information boundaries
-(selection-time covariates, not outcome or test labels).  RAVEN-Design uses the
-lagged target-mass opportunity ratio with Design configured on before the
-window opens; RAVEN-NoDesign configures that factor at one, retaining the arrival
-opportunity law.  The resulting statistical reference may still be unattainable in a
-particular mobile window, so RAVEN-MCS maps the corrected reference to a feasible
-aggregation decision through instantaneous target calibration, a strongly convex
-calibration program, and long-term target debt.  This separation yields three
-distinct questions: \emph{what target should be served}, \emph{what target mass
-the selected data represent}, and \emph{what target composition can be feasibly
-realized now}.
+Mobile crowdsensing (MCS) observes sparse urban and environmental fields,
+making data completion necessary~\cite{ganti2011mobile,li2024robust}.
+Federated learning trains completion models without centralizing sensing
+records~\cite{mcmahan2017communication,wang2026federated}.  We study windowed
+asynchronous learning: clients compute and deliver updates at different times,
+while the server performs one global update when each window closes.  The
+challenge is to determine which deployment population those updates represent
+and how closely their aggregation can serve it.
+
+For an atomic sensing unit, a client must have a mobile opportunity ($R$),
+actually observe the unit ($O$), and deliver a usable update before the deadline
+($U$).  These sequential selections induce an arrival distribution that can
+differ from the public deployment target.  Correcting client participation
+alone does not describe which sensing units entered each update.  A second
+disconnect persists after correction: clients available now may cover only
+part of the target, and aggregation constraints can prevent the reconstructed
+reference from being realized.  The deployment target, selected-data
+population, and feasible client mixture are therefore distinct objects.
+
+Existing target-aware FL already addresses population selection and composition
+matching.  FedIPW factors enrollment and participation and calibrates to
+population summaries~\cite{morishita2026who}.  FedPALS matches a target
+distribution with convex aggregation and effective-sample-size regularization,
+including targets outside the client convex hull~\cite{listozec2024overcoming}.
+The MCS question is how to connect a reference reconstructed across sensing-unit
+and update selections to a changing window's constrained client mixture.
+Inverse weighting and convex calibration supply building blocks, but the
+reference and the executable aggregation decision have different meanings.
+
+We develop \textbf{RAVEN-MCS} (Reference Alignment Via Exposure-aware
+Normalization for Mobile CrowdSensing) around this distinction
+(Fig.~\ref{fig:raven_overview}).  Each selection layer has its own information
+boundary.  Observation weights use histories available before sensing, while
+usable-update weights can also use the registered sensing state before
+usability is known.  Combined with a lagged opportunity ratio, these corrections
+reconstruct the target mass represented by delivered updates.  The reference
+is not yet an executable allocation.  The server calibrates it on available
+clients under weight caps and minimum effective support.  The aggregation
+program jointly balances reference fidelity, deployment-group matching,
+uncertainty, staleness, and accumulated target debt.  Debt records under-service
+across windows rather than creating support absent from the current one.
+Even when several weights are feasible, clients with similar group compositions
+can offer little freedom to adjust target mass.
+
+This connection separates statistical identification from operational
+realizability.  Ideal pooled reconstruction recovers target moments under
+support and identification assumptions, whereas the implemented clipped
+reference includes stabilization error.  Calibration stability holds at a fixed
+window state, while long-run alignment additionally requires sublinear debt growth.
+Neither property establishes prediction improvement.
 
 \begin{figure*}[t]
 \centering
@@ -179,63 +165,39 @@
 \label{fig:raven_overview}
 \end{figure*}
 
-Our contributions follow the distinction between the population to be served,
-the population represented by selected data, and the mixtures available now.
-
+Our contributions are:
 \begin{itemize}
-    \item \textbf{Sensing-unit target formulation and information interfaces.}
-    We distinguish a public atomic deployment measure, the arrival law induced
-    by sequential $R/O/U$ selection, and the current feasible composition.
-    Separate pre-outcome histories specify which information can identify each
-    selection layer.  The formulation connects deployment-group and
-    client--stratum masses and provides the risk and support objects used by
-    both reconstruction and evaluation.  Six controlled selection scenarios and
-    real-opportunity replays examine these distinctions.
-
-    \item \textbf{Selection-corrected reference with finite-window calibration.}
-    We connect local H\'ajek correction and usable-update mass reconstruction to
-    a server reference, then calibrate that reference on the available clients
-    under caps and effective-support constraints.  RAVEN retains its full (P2)
-    criterion and target-debt state.  Ideal pooled reconstruction identifies
-    target moments under A1--A3; the practical clipped reference carries a
-    stabilization error, and the calibration map is non-expansive in the
-    reference only at a fixed window state.  Long-run alignment additionally
-    requires sublinear debt.  The opportunity Design factor is configured before
-    window opening; the coverage Gate supplies a separate diagnostic.
-
-    \item \textbf{Attribution of structural alignment and prediction effects.}
-    Over 20 paired seeds, Uniform explains $68.96\%$ of the matched
-    FedAvg-to-RAVEN group-gap reduction on SensorScope and $83.07\%$ on U-Air.
-    We compare the remaining increment using direct references, feasible
-    projection, and full RAVEN, with prediction and runtime reported alongside
-    structure.  The SensorScope projection--Uniform contrast is $0.768$ pp;
-    the independent projected Design-on/off contrast is $0.922$ pp.
-    Concentrated-target, within-stratum selection, geometric, and learning
-    diagnostics explain which mechanisms are exercised and why structural
-    improvements need not yield prediction gains.
+    \item \textbf{Sensing-unit targets and information interfaces.}
+    We distinguish the public deployment target, the arrival law induced by
+    $R/O/U$, and the current feasible composition.  Separate pre-outcome
+    histories identify the information available for each correction.  Controlled
+    selection scenarios and real-opportunity replays examine the resulting
+    target--arrival distinction.
+
+    \item \textbf{Corrected references connected to feasible calibration.}
+    We link normalized sensing correction and usable-update mass reconstruction
+    to constrained aggregation on the available clients.  The analysis separates
+    ideal moment recovery, practical reference perturbation, and fixed-window
+    stability.  Geometry diagnostics distinguish weight freedom from adjustable
+    target composition.
+
+    \item \textbf{Attribution of structural and prediction effects.}
+    Matched-support comparisons separate count weighting, Uniform, feasible
+    reference projection, and full RAVEN.  Joint structure, prediction, and
+    runtime measurements identify the reference-side increment without assigning
+    every improvement to the full objective.
 \end{itemize}
 
-Inverse-probability weighting, H\'ajek normalization, target calibration, ESS,
-and strong-convexity arguments are established tools.  The specific connection
-studied here is between a sensing-unit reference reconstructed across sequential
-selection layers and a changing window's constrained client mixture.  The
-experiments distinguish the value of that connection from the contribution of
-each term in the full criterion.
-
-We evaluate these contributions with a no-harm control, a risk-semantic block,
-and a SensorScope/U-Air development table under always-on protocol $R$ on station
-traces (Table~\ref{tab:main_effectiveness}).  Independent hybrid comparisons, namely
-a T-Drive taxi replay under real $R$ with controlled $O$ and $U$, an NSW-Traffic
-four-region protocol table, and the City Scanner {PM}$_{2.5}$ and Pilot~2 tables
-of the supplemental material, provide separate evaluations of their respective
-targets and selection protocols.  The
-Design factor is set explicitly on each block, and both settings are reported
-where the trade-off is material.  NSW-Traffic and City Scanner use locally
-constructed target maps rather than a transferred SensorScope/U-Air lookup
-object.  A supplemental occupancy-robustness block thins protocol $R$ on the same
-station clients, and a coverage Gate is audited only as a diagnostic that does not
-switch Design.
-
+The main comparison (Table~\ref{tab:main_effectiveness}) and matched-support
+rules (Table~\ref{tab:trained_rules}) address different contrasts.  On
+SensorScope, projection improves group mismatch by $0.768$ pp versus Uniform.
+A separate same-support projected Design-on/off comparison gives $0.922$ pp.
+These effects are not additive.  Six selection scenarios test risk semantics,
+target-concentration comparisons probe prediction sensitivity, and supplemental
+local-weight and geometry analyses explain which adjustments are available.
+Together, the evidence shows why improved target alignment need not yield
+prediction gains, while distinguishing the connection's value from the roles
+of individual objective terms.
 
 \section{Related Work}
 \label{sec:related_work}
```
