# 本轮局部语言润色完整差异

相对于2026-11-05执行前的实际文件，不是相对于Git HEAD。用户已有未提交改动保留。

## main.tex

```diff
--- before/main.tex
+++ after/main.tex
@@ -71,7 +71,7 @@
 
 
 \begin{abstract}
-Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints. Existing approaches address completion, participation bias, and target-aware aggregation, whereas this setting requires an explicit link between sensing-unit reference reconstruction and constrained window execution. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then applies usability correction to form the server reference and calibrates executable weights under caps and effective-support constraints, coordinating reference fidelity, group targets, and accumulated under-service. Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion for anchored convex calibration at a shared fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN-MCS reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek, an opportunity/observation-corrected reference rule, in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.
+Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints. Existing approaches address completion, participation bias, and target-aware aggregation, but a corrected sensing-unit reference still needs to be converted into weights that the current window can execute. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then corrects for update usability to form the server reference and calibrates client weights under caps and effective-support constraints, accounting for reference fidelity, group targets, and accumulated under-service. Rigorous theoretical analysis establishes ideal pooled moment recovery under the stated ratio, support, identification, and cluster conditions, and reference non-expansion when anchored convex calibration uses shared support and otherwise fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN-MCS reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek, an opportunity/observation-corrected reference rule, in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -93,19 +93,18 @@
 Completion representations exploit cross-task and non-aligned sensing structure~\cite{wang2024fewshot,liu2025nonaligned}, and asynchronous learning accommodates irregular updates~\cite{xie2019asynchronous}.
 Participation correction adjusts unequal client contributions~\cite{wang2024lightweight,sun2025debiasing}; FedIPW additionally calibrates enrollment and participation using population summaries~\cite{morishita2026who}.
 However, normalizing each client's training weights removes the total mass scale that the server needs to represent relative client contributions after sequential selection.
-The challenge is to reconstruct local training weights and server reference mass for the same sensing-unit target, using only the information available before each selection outcome.
+Local training weights and server reference mass must therefore represent the same sensing-unit target using information available before each selection outcome.
 
 Beyond statistical reconstruction, a finite window can aggregate only the client updates that are usable at closure, so a corrected reference need not itself be an executable allocation.
 Available group compositions, per-client weight caps, and effective-support constraints jointly delimit the mixtures that can be formed, even with accurate selection ratios.
 Participation analyses and semi-asynchronous bias correction address unequal or irregular update contributions~\cite{wang2022unified,chen2026fedcure}; estimating participation weights provides a correction for these contribution imbalances~\cite{wang2024lightweight}.
 FedIPW calibrates population summaries under limited information~\cite{morishita2026who}, while FedPALS uses convex target-label matching and sample-ESS regularization, including targets outside the client convex hull~\cite{listozec2024overcoming}.
-The task here is to connect a sequentially reconstructed sensing-unit reference to the constrained mixture available in the current window.
 Group under-service can also accumulate across windows, motivating a state that records service deficits alongside instantaneous reference matching.
-The challenge is to coordinate fidelity to the reconstructed reference with feasible deployment-group service and cumulative deficits, while characterizing how reference errors propagate through this allocation.
+Calibration must coordinate reference fidelity with feasible deployment-group service and cumulative deficits, while accounting for how reference errors propagate into the allocation.
 
 To address the above challenges, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), a framework linking sensing-unit target-reference reconstruction to executable aggregation for windowed federated completion.
-Specifically, opportunity and observation correction generate weights shared by normalized local training and client-mass estimation, and pre-outcome usability correction then rescales those masses to form the server reference for constrained calibration at window close.
-Furthermore, the calibration program coordinates fidelity to the reference in client-weight space with deployment-group alignment and accumulated under-service, under weight caps and client-level effective-support constraints on current clients.
+Specifically, shared opportunity and observation weights determine normalized local training and client-mass estimates, which pre-outcome usability correction rescales into the server reference.
+Furthermore, calibration at window close coordinates reference fidelity in client-weight space with deployment-group alignment and accumulated under-service, subject to weight caps and client-level effective-support constraints.
 In this way, RAVEN-MCS turns the reconstructed reference into a feasible client mixture that targets deployment-group alignment within the available sensing support.
 The major contributions of this work are summarized as follows:
 \begin{enumerate}
@@ -117,29 +116,31 @@
 \section{Related Work}
 \label{sec:related_work}
 
-Sparse MCS studies evolutionary inference and sensing utility
-\cite{wang2025evolutionary,xu2025rethinking}, few-shot and cold-start transfer
-\cite{wang2024fewshot,zhang2026mapt}, and uncertainty-based pricing
-\cite{liu2026pricing}. Multi-scale methods use pyramids~\cite{liu2026pyramid}
-or integrate non-aligned observations~\cite{liu2025nonaligned}; StrucFormer
-combines low-rank priors with Transformers~\cite{kang2025strucformer},
-addressing representation rather than deployment mass.
-
-Federated completion~\cite{wang2026federated} and FedAsync~\cite{xie2019asynchronous}
-address distributed records and irregular updates. Staleness-aware methods
-\cite{sun2024staleness,islam2025seafl,li2026stdfl} improve timing and efficiency.
-DeFedAvg analyzes heterogeneous asynchronous training~\cite{wang2025defedavg};
-MasFL controls staleness through historical momentum, with adaptive gradient
-normalization in AdaMasFL~\cite{yan2025momentum}.
-
-FL bias includes demographic, performance-related, and contribution-related
-effects~\cite{benarba2025bias}; arbitrary participation has dedicated analyses
-\cite{wang2022unified}. FedAU estimates participation weights
-\cite{wang2024lightweight}; other methods handle correlated participation,
-semi-asynchronous bias, and opt-out stragglers
-\cite{sun2025debiasing,chen2026fedcure,goetze2025floss}.
-FAST permits arbitrary participation between snapshots but requires uniform
-client participation at snapshots
+Sparse MCS research addresses evolutionary inference and sensing
+utility~\cite{wang2025evolutionary,xu2025rethinking}, few-shot and cold-start
+transfer~\cite{wang2024fewshot,zhang2026mapt}, and uncertainty-based
+pricing~\cite{liu2026pricing}. Representation methods use
+pyramids~\cite{liu2026pyramid}, integrate non-aligned
+observations~\cite{liu2025nonaligned}, or combine low-rank priors with
+Transformers, as in StrucFormer~\cite{kang2025strucformer}. These methods
+address representation rather than deployment mass.
+
+Distributed records and update timing motivate federated
+completion~\cite{wang2026federated} and FedAsync~\cite{xie2019asynchronous}.
+Staleness-aware methods improve timing and
+efficiency~\cite{sun2024staleness,islam2025seafl,li2026stdfl}.
+Heterogeneity is analyzed in DeFedAvg~\cite{wang2025defedavg}, while MasFL
+controls staleness through historical momentum and AdaMasFL adds adaptive
+gradient normalization~\cite{yan2025momentum}.
+
+Participation mechanisms are another source of FL bias, alongside demographic
+and performance-related effects~\cite{benarba2025bias}. Arbitrary participation
+has dedicated analyses~\cite{wang2022unified}, while FedAU estimates
+participation weights~\cite{wang2024lightweight}. Other methods address
+correlated participation, semi-asynchronous bias, and opt-out
+stragglers~\cite{sun2025debiasing,chen2026fedcure,goetze2025floss}.
+Participation assumptions differ: FAST permits arbitrary participation between
+snapshots but requires uniform client participation at snapshots
 \cite{li2025fast}. FOCUS uses time-varying graphs and push--pull updates, with
 linear rates under strong convexity or a Polyak--\L{}ojasiewicz condition and positive participation
 probabilities~\cite{ying2025focus}. PHP-FL targets performance fairness with
@@ -236,8 +237,8 @@
 \end{equation}
 Here $\pi^{\mathrm{opp}}_{k,s,r}$ is client--stratum opportunity mass and
 $\nu^{\mathrm{opp}}_{k,r}(i\mid s)$ is its conditional atomic law.  The
-realized $R_{k,r,i}$ record events from this process, not mutually independent
-Bernoulli draws.  Subsequent selection probabilities are
+realized indicators $R_{k,r,i}$ record events from this process; they are not
+mutually independent Bernoulli draws.  Subsequent selection probabilities are
 \begin{align}
  p^{\mathrm{obs}}_{k,r,i}
  &\triangleq
@@ -413,7 +414,7 @@
 \end{equation}
 Normalization gives $\sum_{k,s}\widehat\Pi_{k,s}(R)=1$.  Both structural
 distances lie in $[0,2]$ and convert to target-mass percentage points by
-$\mathrm{pp}=50\Delta$.  The Uniform ruler, same-support hindsight comparison,
+$\mathrm{pp}=50\Delta$.  The Uniform benchmark, same-support hindsight comparison,
 and practical equivalence convention are specified in
 Section~\ref{subsec:equivalence_band}.
 
@@ -667,9 +668,9 @@
  \label{eq:debt_bound}
 \end{equation}
 \begin{proof}
-Coordinatewise summation bounds cumulative under-service's positive part by
-$\mathbf Q_R$. Zero total mass makes its $\ell_1$ norm twice its positive
-mass (\appref{app:proof_debt_bound}).
+Coordinatewise summation bounds the positive part of cumulative signed
+under-service by $\mathbf Q_R$. The signed under-service vector sums to zero,
+so its $\ell_1$ norm equals twice its positive mass (\appref{app:proof_debt_bound}).
 \end{proof}
 A vanishing bound requires $\|\mathbf Q_R\|_1=o(S_R)$.
 
@@ -1113,7 +1114,7 @@
 by $\exp(-1.25)$ against UTC blocks 2/3; observation probability is
 $.35$ versus $.1925$ there. Device-tier compute/network usability uses
 $S_{\max}=5$ and at most four risk units/client-window. Observation propensity
-is block-constant; usability is drawn once/client-window. The compounding
+is constant within each block; usability is sampled once per client in each window. The compounding
 direction and always-on station $R$ are constructed; \appref{app:int_r}
 separately tests intermittent occupancy.
 
@@ -1254,13 +1255,13 @@
 
 \noindent\textit{Structural comparison convention.}
 \label{subsec:equivalence_band}
-Uniform is the structural ruler. The offline hindsight minimum $\Delta^\star$
-shares active sets, $M_r$, and $\mathcal C_r$. Normalize paired structural
+Uniform is the structural benchmark. The offline hindsight minimum $\Delta^\star$
+uses the same active sets, $M_r$, and $\mathcal C_r$. Normalize paired structural
 effects by $\langle\Delta_a-\Delta_b\rangle/
 \langle\Delta_{\mathrm{Uniform}}-\Delta^\star\rangle$, using same-seed means;
 95\% intervals jointly resample numerator/denominator. Intervals within
 $[-.10,+.10]$ meet the practical band; removed$-$full intervals above $+.10$
-meet the component-necessity magnitude criterion. Group-TV practical effects
+meet the magnitude criterion for component necessity. Group-TV practical effects
 require a 95\% lower bound $\ge.5$ pp. Parameter-free contrasts use all
 20 seeds; tuning/report halves assess stability. Magnitude and significance
 criteria remain distinct.
@@ -1271,9 +1272,10 @@
 trained-rule contrasts within dataset/endpoint, and four 20-seed worst-group
 contrasts against FedAU/ObsUse.  Differences below $10^{-12}$ are numerical
 ties.  Tables give mean $\pm$ SD; controlled station intervals use 10000
-seed-paired percentile bootstrap draws at seed 20261002.  The descriptive $+.5\%$ worst-group tolerance
-uses mean paired relative differences on TEST seeds 30011--30020 for ranking
-prose; Holm tests use all 20. Formal non-inferiority uses a separate $2\%$ margin in the six-arm City Scanner comparison.
+seed-paired percentile bootstrap draws at seed 20261002.  Ranking statements use a descriptive $+.5\%$ worst-group tolerance based on
+mean paired relative differences on TEST seeds 30011--30020; Holm tests use
+all 20 seeds. The six-arm City Scanner comparison instead tests formal
+non-inferiority with a $2\%$ margin.
 Matched-support rules use saved parameters and common TEST weights, including
 empty-final-window runs. Balanced-control,
 oracle-sensitivity, and concentration criteria retain their distinct thresholds below.
@@ -1326,27 +1328,27 @@
 mismatch among the five methods: $.0706$ versus $.0952$ for TwoStage-H\'ajek,
 the best group comparator, a $25.8\%$ reduction by ratio of means. This
 improves alignment of the aggregated group composition with the deployment
-target. TwoStage-H\'ajek minimizes client--stratum mismatch. RAVEN's paired
-RMSE improves on FedAU/ObsUse by $1.71\%/1.34\%$, with worst-group
-reductions of $1.56\%/1.23\%$. FedAvg leads both prediction endpoints,
+target. TwoStage-H\'ajek minimizes client--stratum mismatch. RAVEN reduces paired RMSE by $1.71\%$ relative to FedAU and $1.34\%$ relative
+to ObsUse; the corresponding worst-group RMSE reductions are $1.56\%$ and
+$1.23\%$, respectively. FedAvg leads both prediction endpoints,
 with RAVEN's paired RMSE $5.59\%$ higher.
 
 Under Pilot~2's distinct data and target map, full RAVEN again gives the lowest
 mean group mismatch ($.0465$ versus TwoStage-H\'ajek's $.0607$), a
 $23.3\%$ ratio-of-means reduction. The group-alignment advantage thus also
-appears in the measured-observation protocol. Paired RMSE improves on
-FedAU/ObsUse/FedAvg by $.43\%/.45\%/.65\%$, while TwoStage-H\'ajek leads
-both prediction endpoints and client--stratum alignment. The first two
-comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
+appears in the measured-observation protocol. RAVEN reduces paired RMSE by $.43\%$ relative to FedAU, $.45\%$ relative to
+ObsUse, and $.65\%$ relative to FedAvg. TwoStage-H\'ajek leads both prediction
+endpoints and client--stratum alignment. The FedAU and ObsUse comparisons
+miss the declared $\le-.5\%$ paired relative-error criterion.
 
 
 \paragraph{Controlled station comparisons}
 
 
-Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  SensorScope
-Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$.
-Removing Design worsens the structural endpoints by $1.237\%/.597\%$,
-measured relative to the Design-on arm.
+Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  On SensorScope,
+Design reduces group mismatch by $3.96\%$ and client--stratum mismatch by
+$2.01\%$ relative to FedAvg. Removing Design worsens these endpoints by
+$1.237\%$ and $.597\%$, respectively, relative to Design on.
 U-Air reverses on group and prediction: removing Design improves group
 mismatch by $6.943\%$, RMSE by $6.885\%$, and tail RMSE by $7.221\%$, while
 worsening client--stratum mismatch by $4.990\%$. Both estimated and oracle
@@ -1398,14 +1400,15 @@
 \label{fig:w1_design_gate}
 \end{figure}
 
-SensorScope Design and U-Air NoDesign meet the descriptive worst-group
-tolerance against FedAU/ObsUse on TEST means ($-.01\%/+.05\%$ and
-$+.48\%/+.44\%$); corresponding all-20 means are $+.02\%/+.10\%$ and
-$+.002\%/+.075\%$.  U-Air Design instead exceeds it by $7.9\%/8.0\%$.
-The 20-seed Holm contrasts do not establish prediction superiority.
-Within its Design-on family, U-Air RAVEN improves worst-group RMSE versus
-TwoStage-H\'ajek by $2.46\%$ on TEST seeds, but its absolute $1.2630$ remains
-above FedAvg's $1.1690$.
+Against FedAU and ObsUse, respectively, SensorScope Design has TEST
+worst-group RMSE changes of $-.01\%$ and $+.05\%$; U-Air NoDesign has
+$+.48\%$ and $+.44\%$. Both meet the descriptive tolerance. The corresponding
+all-20-seed changes are $+.02\%$ and $+.10\%$ on SensorScope, and $+.002\%$
+and $+.075\%$ on U-Air. U-Air Design exceeds the tolerance, with changes of
+$7.9\%$ and $8.0\%$ against the same comparators. The 20-seed Holm tests do
+not establish prediction superiority. U-Air RAVEN improves worst-group RMSE
+by $2.46\%$ over TwoStage-H\'ajek on TEST seeds within the Design-on family,
+but its absolute RMSE of $1.2630$ remains above FedAvg's $1.1690$.
 
 
 Under-served-block validation meets no-harm but misses the required improvement
@@ -1416,12 +1419,12 @@
 
 \paragraph{Additional sensing protocols}
 Real T-Drive opportunity is intermittent: active fraction $.425$, burstiness
-$+.38$, and cell coverage $.547$.  Four-block opportunity--target TV is $.142$
-versus $.192/ .278$ in protocol SensorScope/U-Air, all above $.05$
+$+.38$, and cell coverage $.547$.  Four-block opportunity--target TV is $.142$, compared with $.192$ on
+SensorScope and $.278$ on U-Air under their respective protocols, all above $.05$
 (Fig.~\ref{fig:g3_tdrive}; Table~\ref{tab:tdrive_hybrid}).
 With controlled $O/U$, RAVEN-NoDesign fails the
-$+.5\%$ worst-group tolerance against FedAU/ObsUse: paired relative
-$+2.39\%/+2.43\%$ (versus FedAvg $+.32\%$).  Its group gap equals FedAvg's;
+$+.5\%$ worst-group tolerance: paired worst-group RMSE increases are $+2.39\%$ relative
+to FedAU and $+2.43\%$ relative to ObsUse (versus FedAvg, $+.32\%$).  Its group gap equals FedAvg's;
 Design on worsens prediction, worst-group risk, and group mismatch.  Delivery remains controlled.
 
 \begin{figure}[t]
@@ -1546,18 +1549,20 @@
 \end{table*}
 
 \paragraph{Reference reconstruction and feasible calibration}
-Before feasible calibration, the direct corrected reference has group-mismatch
-readouts of $1.03533/1.11961$ on SensorScope/U-Air, above Uniform and
-potentially infeasible under caps/ESS. Projecting it improves these readouts by
-$1.188$ pp ($[.956,1.409]$) and $1.399$ pp ($[1.019,1.782]$), respectively.
+Before feasible calibration, the direct corrected reference has group mismatch
+$1.03533$ on SensorScope and $1.11961$ on U-Air, above Uniform; the reference
+may also violate caps or ESS constraints. Projection reduces group mismatch
+relative to this reference by $1.188$ pp ($[.956,1.409]$) on SensorScope and
+$1.399$ pp ($[1.019,1.782]$) on U-Air.
 This fixed-support structural contrast quantifies the role of converting a
 reconstructed reference into a finite-window allocation; trained prediction
 and runtime are reported separately in Table~\ref{tab:trained_rules}.
 
 Relative to Uniform, corrected-reference projection improves group mismatch
 by $.768$ pp ($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$)
-on U-Air. The $.5$ pp practical line is cleared stably only on SensorScope;
-U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.
+on U-Air. Only SensorScope consistently meets the pre-specified $.5$ pp practical
+threshold; U-Air's improvement is $.170$ pp on tuning seeds and $.402$ pp
+on report seeds.
 SensorScope's independent same-support projected Design-on/off contrast gives
 $.922$ pp ($[.721,1.141]$). This opportunity-correction effect is not additive
 with projection--Uniform;
@@ -1565,8 +1570,8 @@
 
 Full P2 has $.118$ pp more group mismatch than projection on SensorScope
 ($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
-U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
-versus RAVEN's $27.1/15.3$ s. The prediction contrasts are not
+U-Air's group contrast is not significant. Projection takes $19.9$ s versus
+RAVEN's $27.1$ s on SensorScope, and $8.8$ s versus $15.3$ s on U-Air. The prediction contrasts are not
 Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ using the saved model parameters).
 
 Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
@@ -1575,8 +1580,8 @@
 ($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
 These mean-difference shares describe this shared pathway, not causal
 component contributions or additive gains across the following comparisons.
-The hindsight structural ruler has a group-TV gap from Uniform of
-$3.44/1.32$ pp on SensorScope/U-Air over 20 always-on seeds. U-Air FedAU/ObsUse use
+The hindsight structural reference has a group-TV gap from Uniform of
+$3.44$ pp on SensorScope and $1.32$ pp on U-Air over 20 always-on seeds. U-Air FedAU/ObsUse use
 different supports and do not enter this attribution.
 
 \paragraph{Component contributions}
@@ -1586,17 +1591,18 @@
 $100(M_{\mathrm{removed}}-M_{\mathrm{full}})/M_{\mathrm{full}}$.
 The Design row includes the support changes described in
 Section~\ref{subsec:rq1_alignment}, not the fixed-support projection intervention.
-Inst removes instantaneous calibration, whereas Inst-Cal removes debt. Inst contributes on specific structural and prediction
-endpoints: its removal worsens SensorScope client--stratum mismatch by
-$.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
-($p_{\mathrm{Holm}}=.0194$), without significant U-Air structural changes.
-Obs has endpoint-specific effects: U-Air group mismatch worsens $.123\%$
-significantly, whereas SensorScope client--stratum mismatch improves $.070\%$
-after removal. Use has no adjusted-significant core endpoint.
-Debt's significant structural effects are
-$.0141\%/.0040\%$ on SensorScope and $.0043\%/.0024\%$ on U-Air.
-The frozen-strength projection/debt increment ($.0073$ pp on SensorScope,
-$.0024$ pp on U-Air), group, variance, and staleness effects lie inside the
+The Inst ablation removes instantaneous calibration, whereas Inst-Cal removes
+debt. Removing instantaneous calibration worsens SensorScope client--stratum mismatch by $.310\%$.
+On U-Air it worsens RMSE by $.143\%$ and tail RMSE by $.149\%$
+($p_{\mathrm{Holm}}=.0194$), without significant structural changes.
+Removing Obs significantly worsens U-Air group mismatch by $.123\%$ but
+improves SensorScope client--stratum mismatch by $.070\%$. Removing Use has
+no significant core effect after adjustment. Removing Debt significantly
+increases group and client--stratum mismatch by $.0141\%$ and $.0040\%$ on
+SensorScope, and by $.0043\%$ and $.0024\%$ on U-Air, respectively.
+With the pre-specified debt coefficient, adding debt to projection changes
+group-TV by $.0073$ pp on SensorScope and $.0024$ pp on U-Air. These
+increments and the group, variance, and staleness effects lie inside the
 registered practical band. The $\kappa=1000$ rule is a separate sensitivity
 comparison.
 
@@ -1651,7 +1657,7 @@
 With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
 In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
 $90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
-windows.  Largest target groups carry only $.53\%/.79\%$.
+windows.  The largest target groups carry only $.53\%$ on SensorScope and $.79\%$ on U-Air.
 Across 3279 evaluated active windows the feasible L1 group-distance range has
 median $10^{-13}$; this does not make the squared L2 term in P2 constant.
 
@@ -1726,8 +1732,9 @@
 group gain. The gains therefore remain observable in these support/shape
 variants; NoDesign also has lower group mismatch than M1$\mu$/M2$\mu$.
 
-For floor/M1$\mu$/M2$\mu$ versus FedAvg, one-sided 95\% prediction upper bounds
-of $3.83/4.14/8.15\%$ exceed the $2\%$ non-inferiority margin;
+Relative to FedAvg, the one-sided 95\% prediction upper bounds are $3.83\%$
+for floor, $4.14\%$ for M1$\mu$, and $8.15\%$ for M2$\mu$. All exceed the
+$2\%$ non-inferiority margin;
 the gated superiority tests therefore remain untested. The control/floor paired prediction ratio remains inconclusive;
 floor changes group marginals as well as zero masses. The graphical primary
 chains and secondary Holm family retain separate identities
@@ -1735,9 +1742,8 @@
 (Supplementary Table~\ref{tab:cityscanner_sixarm_cs}).
 
 \paragraph{Reference sensitivity}
-Stabilization contributes reference error in the conditional perturbation
-analysis: its median is zero but maxima reach $.553/.680$ in $\ell_1$ on
-SensorScope/U-Air (\appref{app:a5_a6_audit}). Replacing estimated margins
+In the conditional perturbation analysis, stabilization error has median zero
+but reaches $\ell_1$ maxima of $.553$ on SensorScope and $.680$ on U-Air (\appref{app:a5_a6_audit}). Replacing estimated margins
 can change reference mass appreciably while prediction remains insensitive
 (\appref{app:reference_sensitivity}).
 Evaluated oracle configurations are sensitivity references, not predictive
@@ -1751,21 +1757,23 @@
 Learning and update-rule budgets remain distinct
 (\apprefs{app:learning_capacity}{app:update_rule_sensitivity}).
 
-Support determines represented group mass; cap and ESS bound its adjustment.
-Weight freedom, composition freedom, and prediction sensitivity remain distinct.
+Support determines which group mass is represented, while caps and ESS limit
+how far that mass can be adjusted. Feasible changes in client weights need
+not change group composition or prediction error.
 
 \section{Conclusion}
 \label{sec:conclusion}
 
-RAVEN-MCS connects sequential sensing-unit reference reconstruction to
-executable client mixtures under finite-window constraints. Ideal moment
-recovery and fixed-window stability support different parts of this connection;
-long-run alignment additionally requires sublinear debt growth.
-Matched-support comparisons distinguish count-weighting, reference correction,
-and calibration, while geometry identifies adjustable target mass.
-Full RAVEN attains the lowest mean group mismatch among five methods in each
-of two City Scanner protocols. These results support deployment-group alignment
-on the evaluated support and constraints.
+RAVEN-MCS reconstructs a reference through sequential sensing-unit correction
+and converts it into executable client mixtures under finite-window
+constraints. Full RAVEN attains the lowest mean group mismatch among five
+methods in each of two City Scanner protocols. Matched-support comparisons
+identify the roles of count-weighting, reference correction, and calibration;
+geometry shows where group mass can actually be adjusted. Ideal moment
+recovery and fixed-window stability support reconstruction and calibration,
+respectively, while long-run alignment additionally requires sublinear debt
+growth. The evidence supports deployment-group alignment within the evaluated
+support and constraints.
 
 \section*{Data and Code Availability}
 The public sources are cited in Table~\ref{tab:datasets}.  T-Drive follows
```

## appendix.tex

```diff
--- before/appendix.tex
+++ after/appendix.tex
@@ -1219,7 +1219,7 @@
 $0.20$, so the block matches the published T-Drive active fraction, not
 T-Drive burstiness, and it is not a taxi process.
 
-Table~\ref{tab:int_r_occ} audits seeds $30001$, $30010$, and $30020$. Seed
+Table~\ref{tab:int_r_occ} covers seeds $30001$, $30010$, and $30020$. Seed
 $30001$ has mean active fraction in $[0.35,0.50]$ on both datasets.
 Four-block $\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$ stays above the
 pre-registered $0.05$ threshold ($0.309$ SensorScope, $0.225$ U-Air), so
@@ -1299,10 +1299,10 @@
 
 
 The equality between Local-Hajek and FedAvg in the formal SensorScope/U-Air
-blocks is protocol-specific and should not be interpreted as a general
-equivalence.  Table~\ref{tab:app_local_hajek} covers
+blocks is protocol-specific and does not imply general
+equivalence. Table~\ref{tab:app_local_hajek} covers
 9666 effective client-windows: 6070 on SensorScope and
-3596 on U-Air.  In every audited effective client-window, the realized
+3596 on U-Air. In every effective client-window, the realized
 within-client correction-weight range is 0.
 
 
@@ -1391,9 +1391,9 @@
 \subsection{Numerical Feasibility of P2}
 \AppNavLabel{app:p2_diagnostics}
 
-Theorem~1 concerns the mathematical program.  Separately, the
-experimental audit reconstructs whether logged allocations satisfy the P2
-constraints whenever the necessary state is available.  Table~\ref{tab:app_p2_coverage}
+Theorem~1 concerns the mathematical program. Numerical checks test stored
+allocations against P2 constraints where the required state is logged.
+Table~\ref{tab:app_p2_coverage}
 summarizes the dataset-level certificate coverage.
 
 \begin{table}[!t]
@@ -1446,13 +1446,14 @@
 \AppNavLabel{app:trained_rule_probe}
 \AppNavLabel{app:kappa_probe}
 
-At tuned $\kappa=1000$, projection-with-debt gains $1.347/.580$ pp on
-SensorScope/U-Air over projection (Holm $\approx10^{-5}$), versus the
-frozen-strength $.0073$ pp SensorScope gain inside the practical band.
+At tuned $\kappa=1000$, projection-with-debt reduces group-TV versus projection
+by $1.347$ pp on SensorScope and $.580$ pp on U-Air (Holm $\approx10^{-5}$).
+SensorScope's gain at the pre-specified debt coefficient is $.0073$ pp,
+within the practical band.
 Projection's maximum endpoint discrepancy across 240 runs is
 $\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units ($.00121$ pp):
-17\% of the frozen-strength debt effect, $.13\%/.16\%$ of Design/projection
-contrasts. Primal residuals reach $6.66\times10^{-16}$ against tolerance
+17\% of the debt effect at the pre-specified coefficient, $.13\%$ of the
+Design contrast, and $.16\%$ of the projection contrast. Primal residuals reach $6.66\times10^{-16}$ against tolerance
 $10^{-13}$, while stationarity residuals reach $.667$ against $10^{-12}$.
 Comparator objective gaps exceed $10^{-12}$ in 7 of 200 sampled windows,
 with maximum $9.64\times10^{-12}$. These diagnostics separate numerical
@@ -1943,7 +1944,7 @@
 
 Table~\ref{tab:development_geometry} reports natural-window geometry;
 Table~\ref{tab:geometry_sensitivity} varies caps and ESS on fixed-client subsets.
-First-cycle development payloads retain their correction settings. Windows
+Initial development updates retain their correction settings. Windows
 with at least eight clients use the first eight in sorted order and a
 renormalized reference. Feasible ranges separate weight freedom from mass
 adjustable by at least .01, without prediction re-evaluation.
```

