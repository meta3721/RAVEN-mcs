# 核心优势主张修订差异

以本轮开始时的当前工作树为基准；保留已有City Scanner布局和一致性修复。

```diff
--- task-start/main.tex
+++ current/main.tex
@@ -70,23 +70,21 @@
 
 \begin{abstract}
-Mobile crowdsensing completion learns from observations selected by opportunity,
-observation, and update delivery.  Correcting the resulting arrival distribution
-can recover a deployment-target reference, but that reference may remain
-unrealizable by the clients available in a finite window.  RAVEN-MCS connects
-sequential reference reconstruction over atomic sensing units to feasible
-calibration on the current client support, with client weight caps and
-effective-support constraints.  Its aggregation program balances reference
-fidelity against target composition and accumulated under-service, using
-selection histories available before each outcome.  We establish ideal
-target-moment recovery under support and identification assumptions and
-calibration stability at a fixed window state.  Paired comparisons on shared
-client support distinguish
-structural gains explained by Uniform from the increment supplied by the
-corrected reference: on SensorScope, a feasible reference-projection comparator
-reduces group mismatch by $0.768$ percentage points relative to Uniform.
-City Scanner comparisons with real opportunities and, separately, measured
-observation show group-alignment advantages with protocol-dependent prediction
-leaders under controlled delivery. Projection can achieve lower group mismatch
-and runtime than full RAVEN on matched-support station comparisons.
+Mobile crowdsensing completion faces sequential selection through sensing
+opportunities, observation, and update delivery. A corrected reference may
+still be unrealizable within a finite window. RAVEN-MCS connects sequential deployment-target reference
+reconstruction over atomic sensing units to feasible calibration under client
+weight caps and effective-support constraints. Its aggregation program balances
+reference fidelity, target composition, and accumulated under-service using
+pre-outcome selection histories. We establish ideal target-moment recovery
+under support and identification assumptions and calibration stability at a
+fixed window state. In two City Scanner protocols, full RAVEN achieves the
+lowest mean group mismatch among reported methods, $25.8\%$ and $23.3\%$
+below TwoStage-H\'ajek, the best group comparator in each. Both use real
+opportunities and controlled delivery; one measures observation. Matched-support
+station comparisons quantify the distinct increments from reference correction
+and feasible projection. Prediction leaders vary by protocol, while projection
+can achieve lower group mismatch and runtime than full RAVEN. These comparisons
+locate the alignment benefits and practical trade-offs of finite-window
+calibration.
 \end{abstract}
 
@@ -168,36 +166,38 @@
 \begin{itemize}
     \item \textbf{Sensing-unit targets and information interfaces.}
-    We distinguish the public deployment target, the arrival law induced by
-    $R/O/U$, and the current feasible composition.  Separate pre-outcome
-    histories identify the information available for each correction.  Controlled
-    selection scenarios and real-opportunity replays examine the resulting
-    target--arrival distinction.
-
-    \item \textbf{Corrected references connected to feasible calibration.}
-    We link normalized sensing correction and usable-update mass reconstruction
-    to constrained aggregation on the available clients.  The analysis separates
-    ideal moment recovery, practical reference perturbation, and fixed-window
-    stability.  Geometry diagnostics distinguish weight freedom from adjustable
-    target composition.
-
-    \item \textbf{Attribution of structural and prediction effects.}
-    Matched-support comparisons separate count weighting, Uniform, feasible
-    reference projection, and full RAVEN.  Joint structure, prediction, and
-    runtime measurements identify the contributions of the reference and
-    aggregation rule.
+    We distinguish the deployment target, the arrival law induced by sequential
+    $R/O/U$, and the current feasible composition at atomic sensing units.
+    Separate pre-outcome histories specify each correction's information.
+    Risk-semantic experiments show that the same selection shift produces
+    different target-risk and arrival-risk responses.
+
+    \item \textbf{Reconstructed references linked to executable allocations.}
+    We connect normalized sensing correction and usable-update mass
+    reconstruction to constrained client weights. Same-support contrasts
+    quantify projection's effect on direct references and the increment of
+    the projected corrected reference over Uniform. The analysis establishes
+    ideal moment recovery and bounds practical reference perturbation and
+    fixed-window calibration sensitivity.
+
+    \item \textbf{Application-level group alignment and mechanism attribution.}
+    Full RAVEN attains the lowest mean group mismatch among reported methods
+    in both City Scanner protocols. Joint structure, prediction, and runtime
+    comparisons distinguish this application advantage from count-to-Uniform
+    effects and the reference-side increment. Geometry diagnostics separate
+    client count, composition directions, and adjustable target mass.
 \end{itemize}
 
-City Scanner provides real-opportunity and measured-observation evidence
-(Table~\ref{tab:cityscanner_real}), with different prediction leaders across
-protocols despite RAVEN's group-alignment advantage. Controlled station
-comparisons (Tables~\ref{tab:main_effectiveness} and~\ref{tab:trained_rules})
-identify the roles of reference reconstruction and feasible calibration.  On
-SensorScope, projection improves group mismatch by $0.768$ pp versus Uniform.
-A separate same-support projected Design-on/off comparison gives $0.922$ pp.
-These effects are not additive.  Six selection scenarios test risk semantics,
-target-concentration comparisons probe prediction sensitivity, and supplemental
-local-weight and geometry analyses explain which adjustments are available.
-Together, these comparisons link the available target adjustment to its
-measured prediction and runtime effects.
+City Scanner provides the principal application evidence: full RAVEN has the
+lowest mean group mismatch in both the visit-occupancy and measured-observation
+protocols (Table~\ref{tab:cityscanner_real}), with different prediction leaders.
+Controlled station comparisons (Tables~\ref{tab:main_effectiveness}
+and~\ref{tab:trained_rules}) identify the underlying reference and calibration
+effects. On SensorScope, reference projection improves group mismatch by
+$0.768$ pp versus Uniform; an independent same-support projected Design-on/off
+contrast gives $0.922$ pp. These effects are not additive. Uniform's share of
+the count-to-RAVEN gain separates the change in counting weights from the
+reference increment. Six selection scenarios establish the risk distinction,
+while geometry and positive-mass target variants examine how finite support
+shapes the observed group-alignment advantage.
 
 \section{Related Work}
@@ -1270,4 +1270,6 @@
 are given in the setup and table. Appendices~\ref{app:cityscanner_nyc}--
 \ref{app:cityscanner_p2_measured_o} give construction, filtering, and splits.
+Group-mismatch reductions below use ratios of seed means; prediction gains use mean
+seed-paired relative differences.
 
 \begin{table*}[t]
@@ -1304,17 +1306,22 @@
 \end{table*}
 
-In the visit-occupancy block, RAVEN minimizes group mismatch ($.0706$),
-while TwoStage-H\'ajek minimizes client--stratum mismatch. RAVEN's paired
-mean relative RMSE improves on FedAU/ObsUse by $1.71\%/1.34\%$, with
-worst-group reductions of $1.56\%/1.23\%$. FedAvg leads both prediction
-endpoints, with RAVEN's paired RMSE $5.59\%$ higher: the group-alignment
-benefit carries a measurable prediction cost against count weighting.
-
-In Pilot~2, RAVEN again minimizes group mismatch ($.0465$) and improves
-paired RMSE on FedAU/ObsUse/FedAvg by $.43\%/.45\%/.65\%$.
-TwoStage-H\'ajek leads both prediction endpoints and client--stratum alignment.
-The first two comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
-Thus the two protocols share a group-alignment advantage while yielding
-different prediction rankings.
+In the visit-occupancy block, full RAVEN gives the lowest mean group
+mismatch among the five methods: $.0706$ versus $.0952$ for TwoStage-H\'ajek,
+the best group comparator, a $25.8\%$ reduction by ratio of means. This
+improves alignment of the aggregated group composition with the deployment
+target. TwoStage-H\'ajek minimizes client--stratum mismatch. RAVEN's paired
+RMSE improves on FedAU/ObsUse by $1.71\%/1.34\%$, with worst-group
+reductions of $1.56\%/1.23\%$. FedAvg leads both prediction endpoints,
+with RAVEN's paired RMSE $5.59\%$ higher.
+
+Under Pilot~2's distinct data and target map, full RAVEN again gives the lowest
+mean group mismatch ($.0465$ versus TwoStage-H\'ajek's $.0607$), a
+$23.3\%$ ratio-of-means reduction. The group-alignment advantage thus also
+appears in the measured-observation protocol. Paired RMSE improves on
+FedAU/ObsUse/FedAvg by $.43\%/.45\%/.65\%$, while TwoStage-H\'ajek leads
+both prediction endpoints and client--stratum alignment. The first two
+comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
+The shared application advantage is group composition alignment, with
+protocol-dependent prediction rankings.
 
 \subsection{Risk Semantics and External Protocols}
@@ -1524,20 +1531,26 @@
 Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
 reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
-count-to-Uniform and $.65$ pp remaining.  U-Air gives $1.47$ pp
+count-to-Uniform and $.65$ pp remaining. U-Air gives $1.47$ pp
 ($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
-No analogous U-Air attribution is available for FedAU/ObsUse because their
-supports differ.
-
-Projection versus Uniform improves group mismatch by $.768$ pp
-($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$) on U-Air.
-The $.5$ pp practical line is cleared stably only on SensorScope, whereas
-U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.  Direct-reference structural
-readouts before projection are $1.03533/1.11961$, worse than Uniform and
-potentially infeasible under caps/ESS.  Projection improves those readouts by
-$1.188/1.399$ pp ($[.956,1.409]/[1.019,1.782]$); no trained prediction or
-runtime is attributed to direct aggregation.  Independently, same-support
-projected Design-on/off differs by $.922$ pp ($[.721,1.141]$) on SensorScope.
-This is not additive with projection--Uniform; U-Air changes active support
-and cannot identify that contrast.
+This isolates the effect of removing count weighting; the following contrasts
+measure the reference and calibration increments. U-Air FedAU/ObsUse use
+different supports and do not enter this attribution.
+
+Before feasible calibration, the direct corrected reference has group-mismatch
+readouts of $1.03533/1.11961$ on SensorScope/U-Air, above Uniform and
+potentially infeasible under caps/ESS. Projecting it improves these readouts by
+$1.188$ pp ($[.956,1.409]$) and $1.399$ pp ($[1.019,1.782]$), respectively.
+This fixed-support structural contrast quantifies the role of converting a
+reconstructed reference into a finite-window allocation; trained prediction
+and runtime are reported separately in Table~\ref{tab:trained_rules}.
+
+Relative to Uniform, corrected-reference projection improves group mismatch
+by $.768$ pp ($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$)
+on U-Air. The $.5$ pp practical line is cleared stably only on SensorScope;
+U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.
+SensorScope's independent same-support projected Design-on/off contrast gives
+$.922$ pp ($[.721,1.141]$). This opportunity-correction effect is not additive
+with projection--Uniform;
+U-Air changes active support and cannot identify that contrast.
 
 Full P2 has $.118$ pp more group mismatch than projection on SensorScope
@@ -1558,10 +1571,11 @@
 $100(M_{\mathrm{removed}}-M_{\mathrm{full}})/M_{\mathrm{full}}$.
 The Design row is the end-to-end trade-off above, not the same-support
-projection contrast.  Obs has endpoint-specific effects: U-Air group
-mismatch worsens $.123\%$ significantly, whereas SensorScope client--stratum
-mismatch improves $.070\%$ after removal.  Use has no adjusted-significant
-core endpoint.  Removing Inst worsens SensorScope client--stratum mismatch
-by $.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
+projection contrast. Inst contributes on specific structural and prediction
+endpoints: its removal worsens SensorScope client--stratum mismatch by
+$.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
 ($p_{\mathrm{Holm}}=.0194$), without significant U-Air structural changes.
+Obs has endpoint-specific effects: U-Air group mismatch worsens $.123\%$
+significantly, whereas SensorScope client--stratum mismatch improves $.070\%$
+after removal. Use has no adjusted-significant core endpoint.
 Debt's significant structural effects are
 $.0141\%/.0040\%$ on SensorScope and $.0043\%/.0024\%$ on U-Air.
@@ -1613,5 +1627,6 @@
 model seeds (Appendix~\ref{app:cityscanner_sixarm}). Replacing zero control-map
 masses with a positive floor retains $101.9\%$ of the FedAvg-to-control
-group-alignment gain. For the trace-level ratio
+group-alignment gain. The group advantage remains in this specific
+positive-mass target variant. For the trace-level ratio
 $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$,
 the Hodges--Lehmann estimate is $-.019\%$, with 95\% trace-cluster interval
@@ -1706,5 +1721,6 @@
 Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
 composition direction, but only $4.651\%$ mean adjustable target mass.
-References violate constraints in $59.02\%$, with mean projection distance
+These subsets distinguish the existence of an adjustment direction from the
+amount of target mass it can move. References violate constraints in $59.02\%$, with mean projection distance
 $.067487$.  Appendix~\ref{app:development_geometry} varies caps/ESS.
 
@@ -1762,14 +1778,15 @@
 \label{sec:conclusion}
 
-RAVEN-MCS connects a sensing-unit reference reconstructed across sequential
-selection to the constrained client mixtures available in an asynchronous
-window. Ideal moment recovery and fixed-window calibration stability address
-different parts of this connection, with long-run alignment conditional on
-debt growth. City Scanner yields the smallest group mismatch with
-protocol-dependent prediction leaders. Controlled station comparisons attribute
-most structural gain to Uniform and isolate reference-projection and Design
-increments. On SensorScope, projection has lower group mismatch and runtime,
-while full RAVEN has lower client--stratum mismatch. These findings support
-evaluating deployment-target alignment jointly with prediction and cost.
+RAVEN-MCS connects sequential sensing-unit reference reconstruction to
+executable client mixtures under finite-window constraints. The analysis
+separates ideal moment recovery and fixed-window stability from long-run
+alignment, which depends on sublinear debt growth. Full RAVEN attains the lowest
+mean group mismatch among reported methods in both City Scanner protocols.
+Same-support contrasts separate count-to-Uniform effects, reference correction,
+and feasible projection. The positive-mass
+target variant retains group-alignment gains, while geometry distinguishes
+available weight directions from adjustable target mass. Prediction leaders
+vary by protocol. On SensorScope, full RAVEN improves client--stratum alignment
+over projection at higher group mismatch and runtime.
 
 \section*{Data and Code Availability}
```
