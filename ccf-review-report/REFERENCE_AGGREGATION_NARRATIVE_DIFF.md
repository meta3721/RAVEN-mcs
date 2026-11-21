# 摘要与引言局部差异

```diff
--- main.tex before this edit
+++ main.tex after this edit
@@ -69,23 +69,7 @@
 
 
 \begin{abstract}
-Mobile crowdsensing completion faces sequential selection through sensing
-opportunities, observation, and update delivery. A corrected reference may
-still be unrealizable within a finite window. RAVEN-MCS connects sequential deployment-target reference
-reconstruction over atomic sensing units to feasible calibration under client
-weight caps and effective-support constraints. Its aggregation program balances
-reference fidelity, target composition, and accumulated under-service using
-pre-outcome selection histories. We establish ideal target-moment recovery
-under support and identification assumptions and calibration stability at a
-fixed window state. In two primary City Scanner comparisons, full RAVEN achieves the
-lowest mean group mismatch among the five methods in each, $25.8\%$ and $23.3\%$
-below TwoStage-H\'ajek, the best group comparator in each. Both use real
-opportunities and controlled delivery; one measures observation. Matched-support
-station comparisons quantify the distinct increments from reference correction
-and feasible projection. Prediction leaders vary by protocol, while projection
-can achieve lower group mismatch and runtime than full RAVEN. These comparisons
-locate the alignment benefits and practical trade-offs of finite-window
-calibration.
+Mobile crowdsensing completion uses updates selected through sensing opportunities, observation, and delivery. A selection-corrected reference for the deployment target may still be infeasible under the available clients and aggregation constraints of a finite window. RAVEN-MCS addresses this gap by reconstructing reference mass over atomic sensing units and calibrating it into executable client weights. Under weight caps and effective-support constraints, its aggregation program controls departures from the reference while matching deployment-group composition and accounting for accumulated under-service. Correct ideal ratios yield pooled target-moment recovery under compatible support, sequential identification, and cluster regularity. Calibration stability applies to reference perturbations at a fixed window state. In two City Scanner comparisons with real opportunities and controlled delivery, full RAVEN achieves the lowest mean group mismatch among the five methods in each. Reductions relative to TwoStage-H\'ajek, the best group comparator, are $25.8\%$ and $23.3\%$ by ratios of seed means. One protocol controls observation; the other measures it. Matched-support comparisons separate reference-correction and feasible-projection effects, identifying how calibration improves group alignment on the evaluated support.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -99,52 +83,52 @@
 Mobile crowdsensing (MCS) observes sparse urban and environmental fields,
 making data completion necessary~\cite{ganti2011mobile,li2024robust}.
 Federated learning trains completion models without centralizing sensing
-records~\cite{mcmahan2017communication,wang2026federated}.  We study windowed
+records~\cite{mcmahan2017communication,wang2026federated}. We study windowed
 asynchronous learning: clients compute and deliver updates at different times,
-while the server performs one global update when each window closes.  The
-challenge is to determine which deployment population those updates represent
-and how closely their aggregation can serve it.
-
-For an atomic sensing unit, a client must have a mobile opportunity ($R$),
-actually observe the unit ($O$), and deliver a usable update before the deadline
-($U$).  These sequential selections induce an arrival distribution that can
-differ from the public deployment target.  Correcting client participation
-alone does not describe which sensing units entered each update.  A second
-disconnect persists after correction: clients available now may cover only
-part of the target, and aggregation constraints can prevent the reconstructed
-reference from being realized.  The deployment target, selected-data
-population, and feasible client mixture are therefore distinct objects.
-
-Existing target-aware FL already addresses population selection and composition
-matching.  FedIPW factors enrollment and participation and calibrates to
-population summaries~\cite{morishita2026who}.  FedPALS matches a target
-distribution with convex aggregation and effective-sample-size regularization,
-including targets outside the client convex hull~\cite{listozec2024overcoming}.
-The MCS question is how to connect a reference reconstructed across sensing-unit
-and update selections to a changing window's constrained client mixture.
-Inverse weighting and convex calibration supply building blocks, but the
-reference and the executable aggregation decision have different meanings.
+while the server updates the global model when each window closes. Serving a
+deployment target requires both identifying what these updates represent and
+allocating weight within the support available at that close.
+
+An atomic sensing unit enters an update through a mobile opportunity ($R$),
+an actual observation ($O$), and usable delivery before the deadline ($U$).
+These sequential selections alter the distribution of sensing units represented
+by arriving updates. Correcting client participation alone does not account for
+the opportunity and observation selections within each client's records.
+
+Even a correctly reconstructed statistical reference need not be executable.
+Available clients may cover only part of the deployment target, and weight
+caps and effective-support constraints further restrict their mixture.
+The deployment target specifies the desired composition, the corrected
+reference reconstructs relative mass, and feasible aggregation weights specify
+what the server can apply now. Existing target-aware FL addresses population
+selection and composition matching: FedIPW factors enrollment and participation
+and calibrates to population summaries~\cite{morishita2026who}; FedPALS uses
+convex aggregation and effective-sample-size regularization to match target
+distributions, including those outside the client convex
+hull~\cite{listozec2024overcoming}. The remaining MCS problem is to carry
+sensing-unit selection correction through to a changing window's constrained
+client mixture.
 
 We develop \textbf{RAVEN-MCS} (Reference Alignment Via Exposure-aware
-Normalization for Mobile CrowdSensing) around this distinction
-(Fig.~\ref{fig:raven_overview}).  Each selection layer has its own information
-boundary.  Observation weights use histories available before sensing, while
-usable-update weights can also use the registered sensing state before
-usability is known.  Combined with a lagged opportunity ratio, these corrections
-form an estimated, stabilized target-mass reference for delivered updates.  The reference
-is not yet an executable allocation.  The server calibrates it on available
-clients under weight caps and minimum effective support.  The aggregation
-program jointly balances reference fidelity, deployment-group matching,
-uncertainty, staleness, and accumulated target debt.  Debt records under-service
-across windows rather than creating support absent from the current one.
-Even when several weights are feasible, clients with similar group compositions
-can offer little freedom to adjust target mass.
-
-This connection separates statistical identification from operational
-realizability.  Ideal pooled reconstruction recovers target moments under
-support and identification assumptions, whereas the implemented clipped
-reference includes stabilization error.  Calibration stability holds at a fixed
-window state, while long-run alignment additionally requires sublinear debt growth.
+Normalization for Mobile CrowdSensing) to turn this reconstructed reference
+into an executable aggregation decision (Fig.~\ref{fig:raven_overview}).
+Lagged opportunity ratios and observation histories support normalized local
+correction. Usability correction then reconstructs client reference masses
+from information available before delivery outcomes. The server selects
+weights on the available clients, penalizing departures from the reference
+and deviations from deployment-group composition under weight caps and
+minimum effective support. Variance and staleness proxies regularize this
+choice, while target debt carries accumulated under-service into subsequent
+windows. Reweighting cannot create missing sensing support or ensure exact
+target matching when the available compositions cannot realize it.
+
+The analysis separates reference recovery from the behavior of this constrained
+decision. Correct ideal ratios recover pooled target moments under compatible
+support, sequential identification, and cluster regularity. Practical
+reference bounds account for estimation and stabilization error; calibration
+sensitivity is bounded with the support, compositions, constraints, and
+remaining window state fixed. Long-run alignment additionally requires debt
+to grow sublinearly relative to effective step mass.
 
 \begin{figure*}[t]
 \centering
@@ -163,45 +147,51 @@
 \label{fig:raven_overview}
 \end{figure*}
 
+City Scanner provides the principal application evidence
+(Table~\ref{tab:cityscanner_real}). Full RAVEN has the lowest mean group
+mismatch among five methods in each of two distinct protocols. Both use real
+opportunities and controlled delivery; visit occupancy controls observation,
+whereas Pilot~2 measures it. Their common benefit is deployment-group
+alignment, with different prediction leaders. On the controlled station
+protocols, simple reference projection can also achieve lower group mismatch
+and runtime than full RAVEN (Tables~\ref{tab:main_effectiveness}
+and~\ref{tab:trained_rules}).
+
+Matched-support comparisons locate the source of structural improvements.
+Uniform explains much of the gain from removing count weighting. On
+SensorScope, the independent reference-projection rule improves group mismatch
+by $0.768$ pp over Uniform; a separate same-support projected Design-on/off
+contrast yields $0.922$ pp. These contrasts isolate different mechanisms and
+are not additive. Six selection scenarios distinguish target and arrival
+risks. Target-support variants retain lower group mismatch than FedAvg on all
+ten paired traces (Table~\ref{tab:cityscanner_sixarm}). Geometry diagnostics
+distinguish freedom to change weights from freedom to change group mass;
+formal station traces quantify the latter from arrival logs
+(Appendix~\ref{app:arrival_support}).
+
 Our contributions are:
-\begin{itemize}
-    \item \textbf{Sensing-unit targets and information interfaces.}
-    We distinguish the deployment target, the arrival law induced by sequential
-    $R/O/U$, and the current feasible composition at atomic sensing units.
-    Separate pre-outcome histories specify each correction's information.
-    Risk-semantic experiments show that the same selection shift produces
-    different target-risk and arrival-risk responses.
-
-    \item \textbf{Reconstructed references linked to executable allocations.}
-    We connect normalized sensing correction and usable-update mass
-    reconstruction to constrained client weights. Same-support contrasts
-    quantify projection's effect on direct references and the increment of
-    the projected corrected reference over Uniform. The analysis establishes
-    ideal moment recovery and bounds practical reference perturbation and
-    fixed-window calibration sensitivity.
-
-    \item \textbf{Application-level group alignment and mechanism attribution.}
-    Full RAVEN attains the lowest mean group mismatch among the five methods
-    in each primary City Scanner comparison. Joint structure, prediction, and runtime
-    comparisons distinguish this application advantage from count-to-Uniform
-    effects and the reference-side increment. Geometry diagnostics separate
-    client count, composition directions, and adjustable target mass.
-\end{itemize}
-
-City Scanner provides the principal application evidence: full RAVEN has the
-lowest mean group mismatch within each five-method visit-occupancy and
-measured-observation comparison (Table~\ref{tab:cityscanner_real}), with different prediction leaders.
-Controlled station comparisons (Tables~\ref{tab:main_effectiveness}
-and~\ref{tab:trained_rules}) identify the underlying reference and calibration
-effects. On SensorScope, reference projection improves group mismatch by
-$0.768$ pp versus Uniform; an independent same-support projected Design-on/off
-contrast gives $0.922$ pp. These effects are not additive. Uniform's share of
-the count-to-RAVEN gain separates the change in counting weights from the
-reference increment. Six selection scenarios establish the risk distinction.
-Target-support variants also lower group mismatch versus FedAvg on all ten
-paired traces (Table~\ref{tab:cityscanner_sixarm}); geometry characterizes
-the finite support available for adjustment. On the formal station traces,
-that mass is read from arrival logs (Appendix~\ref{app:arrival_support}).
+\begin{enumerate}
+    \item \textbf{From reconstructed references to executable aggregation.}
+    RAVEN-MCS couples sequential target-reference reconstruction to constrained
+    aggregation on the current window's clients, addressing the gap between
+    corrected statistical mass and executable weights. Calibration analysis
+    bounds sensitivity to the reference, while matched-support comparisons
+    distinguish direct-reference, projection, and full-program behavior.
+
+    \item \textbf{Sensing-unit foundations for reconstruction and calibration.}
+    We formulate the deployment target and sequential $R/O/U$ arrival law over
+    atomic sensing units, with pre-outcome information boundaries for each
+    correction. This formulation supports ideal pooled moment recovery and
+    separates practical reference error from fixed-window calibration
+    sensitivity.
+
+    \item \textbf{Application evidence and attribution of group alignment.}
+    Two City Scanner protocols establish full RAVEN's lowest mean group
+    mismatch within their respective five-method comparisons. Matched-support
+    rules and geometry diagnostics explain the distinct roles of reference
+    correction, feasible projection, and available composition directions in
+    this reference-to-aggregation link.
+\end{enumerate}
 
 \section{Related Work}
 \label{sec:related_work}

```

## 首次编译后的局部精简

```diff
--- first narrative draft
+++ final local compression
@@ -82,27 +82,26 @@
 
 Mobile crowdsensing (MCS) observes sparse urban and environmental fields,
 making data completion necessary~\cite{ganti2011mobile,li2024robust}.
-Federated learning trains completion models without centralizing sensing
-records~\cite{mcmahan2017communication,wang2026federated}. We study windowed
-asynchronous learning: clients compute and deliver updates at different times,
-while the server updates the global model when each window closes. Serving a
-deployment target requires both identifying what these updates represent and
-allocating weight within the support available at that close.
+Federated learning keeps sensing records on clients~\cite{mcmahan2017communication,wang2026federated}.
+In windowed asynchronous learning, clients deliver updates at different times
+and the server aggregates at each window close. Serving a deployment target
+requires identifying what these updates represent and weighting them within
+the available support.
 
 An atomic sensing unit enters an update through a mobile opportunity ($R$),
 an actual observation ($O$), and usable delivery before the deadline ($U$).
-These sequential selections alter the distribution of sensing units represented
-by arriving updates. Correcting client participation alone does not account for
-the opportunity and observation selections within each client's records.
+These selections change the sensing-unit distribution represented by arriving
+updates. Client participation correction alone does not account for
+opportunity and observation selection within each client's records.
 
 Even a correctly reconstructed statistical reference need not be executable.
 Available clients may cover only part of the deployment target, and weight
 caps and effective-support constraints further restrict their mixture.
-The deployment target specifies the desired composition, the corrected
-reference reconstructs relative mass, and feasible aggregation weights specify
-what the server can apply now. Existing target-aware FL addresses population
-selection and composition matching: FedIPW factors enrollment and participation
-and calibrates to population summaries~\cite{morishita2026who}; FedPALS uses
+The deployment target specifies desired composition, the corrected reference
+reconstructs relative mass, and feasible weights specify the executable
+aggregation. Existing target-aware FL addresses selection and composition:
+FedIPW factors enrollment and participation and calibrates to population
+summaries~\cite{morishita2026who}; FedPALS uses
 convex aggregation and effective-sample-size regularization to match target
 distributions, including those outside the client convex
 hull~\cite{listozec2024overcoming}. The remaining MCS problem is to carry
@@ -114,21 +113,19 @@
 into an executable aggregation decision (Fig.~\ref{fig:raven_overview}).
 Lagged opportunity ratios and observation histories support normalized local
 correction. Usability correction then reconstructs client reference masses
-from information available before delivery outcomes. The server selects
-weights on the available clients, penalizing departures from the reference
-and deviations from deployment-group composition under weight caps and
-minimum effective support. Variance and staleness proxies regularize this
-choice, while target debt carries accumulated under-service into subsequent
-windows. Reweighting cannot create missing sensing support or ensure exact
-target matching when the available compositions cannot realize it.
-
-The analysis separates reference recovery from the behavior of this constrained
-decision. Correct ideal ratios recover pooled target moments under compatible
-support, sequential identification, and cluster regularity. Practical
-reference bounds account for estimation and stabilization error; calibration
-sensitivity is bounded with the support, compositions, constraints, and
-remaining window state fixed. Long-run alignment additionally requires debt
-to grow sublinearly relative to effective step mass.
+using pre-outcome information. Under weight caps and minimum effective support,
+the server penalizes weight departures from the reference and composition
+deviations from the deployment target. Variance and staleness proxies regularize
+this choice; debt records accumulated under-service for subsequent windows.
+Reweighting cannot supply missing sensing support or guarantee exact target
+matching within the available compositions.
+
+Our analysis separates statistical recovery from constrained calibration.
+Correct ideal ratios recover pooled target moments under compatible support,
+sequential identification, and cluster regularity. Practical bounds account
+for estimation and stabilization error, then bound calibration sensitivity
+with support, compositions, constraints, and other window state fixed.
+Long-run alignment additionally requires debt sublinear in effective step mass.
 
 \begin{figure*}[t]
 \centering
@@ -149,24 +146,21 @@
 
 City Scanner provides the principal application evidence
 (Table~\ref{tab:cityscanner_real}). Full RAVEN has the lowest mean group
-mismatch among five methods in each of two distinct protocols. Both use real
-opportunities and controlled delivery; visit occupancy controls observation,
-whereas Pilot~2 measures it. Their common benefit is deployment-group
-alignment, with different prediction leaders. On the controlled station
-protocols, simple reference projection can also achieve lower group mismatch
-and runtime than full RAVEN (Tables~\ref{tab:main_effectiveness}
+mismatch in each five-method comparison. Both protocols use real opportunities
+and controlled delivery: visit occupancy controls observation, whereas Pilot~2
+measures it. Prediction leaders differ. In controlled station comparisons,
+simple reference projection can achieve lower group mismatch and runtime than
+full RAVEN (Tables~\ref{tab:main_effectiveness}
 and~\ref{tab:trained_rules}).
 
-Matched-support comparisons locate the source of structural improvements.
-Uniform explains much of the gain from removing count weighting. On
-SensorScope, the independent reference-projection rule improves group mismatch
-by $0.768$ pp over Uniform; a separate same-support projected Design-on/off
-contrast yields $0.922$ pp. These contrasts isolate different mechanisms and
-are not additive. Six selection scenarios distinguish target and arrival
+Matched-support comparisons separate count-weighting effects, reference
+correction, and calibration. Uniform explains much of the count-to-RAVEN gain.
+SensorScope's independent reference projection improves group mismatch by
+$0.768$ pp over Uniform; a separate same-support projected Design-on/off
+contrast yields $0.922$ pp. These effects are not additive. Six selection scenarios distinguish target and arrival
 risks. Target-support variants retain lower group mismatch than FedAvg on all
-ten paired traces (Table~\ref{tab:cityscanner_sixarm}). Geometry diagnostics
-distinguish freedom to change weights from freedom to change group mass;
-formal station traces quantify the latter from arrival logs
+ten paired traces (Table~\ref{tab:cityscanner_sixarm}). Geometry distinguishes weight freedom from adjustable group mass,
+quantified on formal station traces from arrival logs
 (Appendix~\ref{app:arrival_support}).
 
 Our contributions are:
@@ -186,8 +180,8 @@
     sensitivity.
 
     \item \textbf{Application evidence and attribution of group alignment.}
-    Two City Scanner protocols establish full RAVEN's lowest mean group
-    mismatch within their respective five-method comparisons. Matched-support
+    Full RAVEN gives the lowest mean group mismatch in each of two
+    five-method City Scanner comparisons. Matched-support
     rules and geometry diagnostics explain the distinct roles of reference
     correction, feasible projection, and available composition directions in
     this reference-to-aggregation link.

```
