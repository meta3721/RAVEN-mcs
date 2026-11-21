# 本轮差异与图形前后对照

## 文字要点

- 原B节长名单→五项独立主方案说明、用途分组的辅助比较、按RQ分组的指标。
- 原公式29后简略on/off→保留公式，明确框架简称、固定配置名和计算因子；保留其余步骤及支持区别。
- 摘要未描述TwoStage→附机会/观测参考规则描述；仍八句、数字与结论范围不变。
- 原直接Table引用→五处Supplementary Table直接定位；原详细表保留。
- 减少重复设置与RQ标题之后重复导语，保留全部关键不利数字、阈值和统计家族。
- City Scanner候选完成核对但没有进入正式正文，详见报告的页数约束与未完成项。

## 七图前后对照

以下上方为修改前，下方为修改后。数据点、误差范围、计数和统计量保持；差异只涉及标签、纹理、透明度、留白与输出格式。

### fig2_e2_risk_noninterchangeability

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig2_e2_risk_noninterchangeability_comparison.png)

### fig_g3_tdrive_h_mass

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig_g3_tdrive_h_mass_comparison.png)

### fig_w1_design_gate

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig_w1_design_gate_comparison.png)

### fig3_e3_structural_mismatch

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig3_e3_structural_mismatch_comparison.png)

### fig4_e3_prediction_risk

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig4_e3_prediction_risk_comparison.png)

### fig_certificate_audit

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig_certificate_audit_comparison.png)

### fig_learning_capacity_r2

![修改前后对照](C:/Cursor/raven.mcs/tmp/baselines_visual_20261102/fig_learning_capacity_r2_comparison.png)

## City Scanner紧凑候选

![两协议组对齐与预测候选](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/baselines_visual_candidate/fig_cityscanner_core_candidate.png)

## 完整源码差异

### main.tex

```diff
--- main.tex before
+++ main.tex after
@@ -69,7 +69,7 @@
 
 
 \begin{abstract}
-Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints. Existing approaches address completion, participation bias, and target-aware aggregation, whereas this setting requires an explicit link between sensing-unit reference reconstruction and constrained window execution. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then applies usability correction to form the server reference and calibrates executable weights under caps and effective-support constraints, coordinating reference fidelity, group targets, and accumulated under-service. Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion for anchored convex calibration at a shared fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.
+Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints. Existing approaches address completion, participation bias, and target-aware aggregation, whereas this setting requires an explicit link between sensing-unit reference reconstruction and constrained window execution. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then applies usability correction to form the server reference and calibrates executable weights under caps and effective-support constraints, coordinating reference fidelity, group targets, and accumulated under-service. Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion for anchored convex calibration at a shared fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN-MCS reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek, an opportunity/observation-corrected reference rule, in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -721,8 +721,11 @@
 \end{cases}
 \label{eq:design_factor}
 \end{equation}
-RAVEN-Design uses the lagged ratio.  RAVEN-NoDesign retains the opportunity
-arrival law.  All other correction, calibration, and debt steps coincide.
+RAVEN abbreviates RAVEN-MCS. For fixed-configuration comparisons, the framework with Design enabled throughout
+the run is RAVEN-Design; with Design disabled it is RAVEN-NoDesign.
+The former applies the lagged ratio in \eqref{eq:design_factor}; the latter sets
+it to one, retaining the opportunity arrival law. All other correction,
+calibration, and debt-update steps coincide.
 On/off comparison arms fix the setting throughout a run.  The catalogue check
 \eqref{eq:design_gate} can inform configuration only when its catalogue and
 public lookup already exist before opening, independently of coverage.
@@ -1085,31 +1088,27 @@
 \subsection{Datasets and Selection Protocols}
 \label{subsec:eval_setup}
 
-Table~\ref{tab:datasets} gives chronological splits, groups, strata, and roles.
+Table~\ref{tab:datasets} lists chronological splits, clients, groups, and strata.
 SensorScope~\cite{ingelrest2010sensorscope,barrenetxea2019sensorscope} and
-U-Air~\cite{zheng2013uair} use station clients and spatial-unit $\times$ UTC-block
-deployment groups; their finer opportunity strata distinguish weekday/weekend.
-NSW-Traffic~\cite{tfnsw2024traffic} uses station clients and four coordinate
-regions.  These semi-synthetic blocks construct all three selection layers
-from frozen public/training information.  The main Complete-aligned condition
-tilts opportunity mass by $\exp(-1.25)$ against UTC blocks 2 and 3,
-observes with probability $.35$ versus $.1925$ there, and uses a device-tier
-compute/network process with $S_{\max}=5$ and at most four risk units per
-client-window.  Observation propensity is block-constant; usability is drawn
-once per client-window.  The compounding direction and always-on SensorScope/U-Air protocol $R$ are
-constructed rather than measured; Appendix~\ref{app:int_r} separately thins
-opportunity to intermittent occupancy.
-
-T-Drive~\cite{yuan2010tdrive} supplies real taxi opportunities from 5837 taxis
-on 9994 cells, with controlled Complete-aligned $O/U$ and four UTC target
-blocks.  City Scanner New York {PM}$_{2.5}$ uses occupied
-$500$\,m $\times$ $30$\,min cells as clients, not vehicles,
-with real visit-occupancy $R$ and controlled $O/U$.  Pilot~2 instead measures $O$
-from finite PM values in $[0,1000]$: 1931 of 14960 occupied cell-slots are
-unobserved.  Its risk set uses the union of retained PM and {NO}$_2$ GPS
-streams, with controlled $U$.  Thus no block measures real usable-update
-delivery. City Scanner and NSW use their own locally fixed region targets;
-protocol identities remain separate in all comparisons.
+U-Air~\cite{zheng2013uair} use station clients, spatial-unit $\times$ UTC-block
+groups, and weekday/weekend opportunity strata. NSW-Traffic~\cite{tfnsw2024traffic}
+uses stations and four coordinate regions. Their controlled selection uses
+frozen public/training information. Complete-aligned opportunity mass tilts
+by $\exp(-1.25)$ against UTC blocks 2/3; observation probability is
+$.35$ versus $.1925$ there. Device-tier compute/network usability uses
+$S_{\max}=5$ and at most four risk units/client-window. Observation propensity
+is block-constant; usability is drawn once/client-window. The compounding
+direction and always-on station $R$ are constructed; Appendix~\ref{app:int_r}
+separately tests intermittent occupancy.
+
+T-Drive~\cite{yuan2010tdrive} provides real opportunities from 5837 taxis on
+9994 cells, controlled Complete-aligned $O/U$, and four UTC target blocks.
+City Scanner NYC PM$_{2.5}$ uses occupied $500$\,m $\times$ $30$\,min cells,
+not vehicles, as clients: real visit-occupancy $R$, controlled $O/U$.
+Pilot~2 measures $O$ from finite PM in $[0,1000]$: 1931/14960 occupied
+cell-slots are unobserved. Its risk set unions retained PM/NO$_2$ GPS streams;
+$U$ remains controlled. No protocol measures usable-update delivery.
+City Scanner and NSW retain protocol-specific region targets.
 
 \begin{table*}[t]
 \centering
@@ -1141,85 +1140,111 @@
 \subsection{Baselines and Evaluation Measures}
 \label{subsec:eval_methods}
 
-Table~\ref{tab:nearest_neighbor} compares the selection objects, information
-requirements, and guarantee scopes of RAVEN, FedIPW, and FedPALS. This is a
-mechanism comparison, distinct from the evaluated baseline family below.
-The deployable same-backbone family comprises count-weighted
-FedAvg-Window~\cite{mcmahan2017communication},
-FedAsync-Window~\cite{xie2019asynchronous}, the windowed TimeAlign adaptation
-of~\cite{wang2026federated}, Local-H\'ajek record correction, and TwoStage-H\'ajek
-opportunity/observation correction.  FedAU-Window adapts participation
-debiasing~\cite{wang2024lightweight}; ObsUse-Window corrects observation and
-usability without Design, P2, or debt.  Appendix~\ref{app:adapted_baselines}
-specifies these windowed adaptations. Inst-Cal removes debt from full P2.
-Additional comparisons include Debt-Cal and the reference-only Central-All,
-Central-Delivered, and RAVEN-SimOracle.
-Full RAVEN uses Sections~\ref{sec:reconstruction}--\ref{sec:calibration} with
-run-fixed Design. Matched-support rules include Count, Uniform, projection,
-Inst-Cal, and full P2. Projection minimizes squared distance to $\widehat\beta_r$
-on $\mathcal C_r$; the separate tuning-selected $\kappa=1000$ rule adds
-$-\kappa\mathbf Q_r^\top M_r\alpha$ and its own debt recursion.
-Component removal changes only the specified component.
-
-On supported test units,
+The following five principal schemes share the task backbone and window-close
+protocol; their local weighting, reference masses, and aggregation rules differ.
+Each experiment retains its stated comparison set.
+
+\noindent\textit{FedAvg-Window.}
+Our windowed adaptation of FedAvg~\cite{mcmahan2017communication} aggregates
+usable client updates in proportion to their observed record counts at closure.
+It uses uniformly weighted local training and provides the count-weighted
+reference for assessing selection correction and constrained aggregation.
+
+\noindent\textit{TwoStage-H\'ajek.}
+This comparison rule uses opportunity/observation-corrected, locally normalized
+training and the resulting client masses. Usability correction then forms
+$b_{k,r}=m_{k,r}d_{k,r}$; the server directly normalizes these masses to
+$\widehat\beta_r$, without P2 or debt. It isolates reference-based aggregation
+from executable calibration.
+
+\noindent\textit{FedAU-Window.}
+Inspired by FedAU's participation debiasing~\cite{wang2024lightweight}, our
+window adaptation weights observed counts inversely by lagged usable-update
+participation rates estimated from earlier attempts. Local training remains
+uniform; opportunity and observation correction, P2, and debt are absent.
+Appendix~\ref{app:adapted_baselines} specifies smoothing and unseen-client handling.
+
+\noindent\textit{ObsUse-Window.}
+This comparison rule weights observed client counts inversely by frozen
+observation and lagged participation probabilities, retaining uniform local
+training. It examines joint observation/usability reweighting without the
+opportunity Design ratio, feasible calibration, or debt; its precise rates
+are defined in Appendix~\ref{app:adapted_baselines}.
+
+\noindent\textit{RAVEN-Design.}
+The complete comparison arm reconstructs a reference through opportunity,
+observation, and usability correction, then solves P2 under cap and
+effective-support constraints. It coordinates reference fidelity, deployment-group
+composition, and accumulated under-service, with Design fixed on as defined
+after \eqref{eq:design_factor}.
+
+\noindent\textit{Auxiliary comparisons.}
+FedAsync-Window~\cite{xie2019asynchronous}, TimeAlign-Agg~\cite{wang2026federated},
+and Local-H\'ajek test staleness, temporal coverage, and local correction.
+Matched-support Count, Uniform, reference projection, and P2 share support
+and constraints; projection minimizes $\|\alpha-\widehat\beta_r\|_2^2$ on
+$\mathcal C_r$. Inst-Cal removes debt; RAVEN-NoDesign fixes Design off.
+Central-All/Delivered and RAVEN-SimOracle are reference-only. Debt-Cal and
+the tuning-selected $\kappa=1000$ projection-plus-debt rule have separate
+recursions. FedIPW/FedPALS are mechanism comparators, not run baselines
+(Supplementary Table~\ref{tab:nearest_neighbor}). Labels may omit Window;
+2S-H\'ajek abbreviates TwoStage-H\'ajek.
+
+\noindent\textit{Deployment alignment.}
+Group mismatch measures the $L_1$ distance between aggregate group mass and
+the deployment target; client--stratum mismatch compares the finer client/stratum
+allocation with its target (\eqref{eq:omega_bar}--\eqref{eq:delta_cs}). Both lie
+in $[0,2]$, with smaller values indicating closer alignment. Group-TV
+percentage-point differences use $\mathrm{pp}=50\Delta$.
+
+\noindent\textit{Prediction and measured cost.}
+Target RMSE measures prediction error on supported deployment units; smaller
+values are better. On supported test units,
+
 \[
 \mathrm{RMSE}_{\mu}=\left[\sum_{i\in\mathcal I_{\mathrm{test}}}
 \frac{\mu^{\mathrm{eval}}_{h(i)}}{n_{h(i)}}(\widehat Y_i-Y_i)^2\right]^{1/2},
 \]
-where evaluation group mass is normalized on supported test units and $n_g$ is
-the group count.  SensorScope/U-Air use uniform atomic evaluation mass, hence
-pooled RMSE.  In the controlled station protocols, SensorScope retains physical
-units, while U-Air/Traffic use training scales $17.363/575.776$ and report
-dimensionless RMSE.  City Scanner uses each block's own training-only
-$z$-score scale (Table~\ref{tab:cityscanner_real}).  WorstGroupRMSE is the maximum
-score across the protocol's frozen groups, with scoring weights renormalized
-within each group.  SensorScope/U-Air and T-Drive use four UTC blocks;
-City Scanner and the NSW-Traffic four-region protocol use spatial groups,
-as specified in their captions and appendices.  In the station protocols
-reporting Tail RMSE, it uses frozen UTC blocks 2 and 3.
-Only the risk-semantic test replaces target weights by
-\eqref{eq:arrival_distribution} for $\mathrm{RMSE}_{\rho}$.
-Structural metrics are \eqref{eq:omega_bar}--\eqref{eq:delta_cs}.
-Group mismatch measures deployment alignment; client--stratum gaps, prediction
-errors, and wall-clock seconds describe composition, task performance, and cost.
+Here $n_g$ counts supported group-$g$ test units and evaluation mass sums to one.
+Uniform atomic mass gives pooled RMSE on SensorScope/U-Air. SensorScope uses
+physical units; U-Air/Traffic use training scales $17.363/575.776$.
+City Scanner uses protocol-specific training-only $z$-scores.
+WorstGroupRMSE maximizes within-group-renormalized RMSE over frozen groups:
+four UTC blocks for SensorScope/U-Air/T-Drive, spatial groups for City Scanner
+and four-region NSW-Traffic. Tail RMSE instead pools frozen UTC blocks 2 and 3.
+Only the risk-semantic test substitutes arrival weights
+\eqref{eq:arrival_distribution} for $\mathrm{RMSE}_\rho$.
+Lower prediction errors are better. Wall-clock seconds measure the stated
+workload/environment, not communication or energy; lower is faster.
 
 \subsection{Implementation and Statistical Settings}
 \label{subsec:eval_implementation}
 
-Paired methods share Common-NDMF, step sizes, and traces. Formal SensorScope/U-Air
-runs use two local steps and 100/80 windows, respectively; separate learning-capacity
-comparisons use their own budgets and physical scales
-(Appendix~\ref{app:learning_capacity}).
-
-Paired methods share EventTraces and within-stratum exchangeability
+Paired methods share Common-NDMF, step sizes, EventTraces, and within-stratum exchangeability
 $\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.
-Design-on/off arms fix their setting throughout each run.  Controlled station
+Formal SensorScope/U-Air runs use two local steps and 100/80 windows; development
+budgets/scales remain separate (Appendix~\ref{app:learning_capacity}). Controlled station
 comparisons use 20 paired seeds; each City Scanner five-method block and
 T-Drive use ten, and the balanced control uses five.  The six-arm target-map
 comparison uses ten traces with three model seeds each.  Other counts are
 specified per table.  Learning diagnostics use three development
 seeds and one Uniform trajectory.  Seeds represent model/trace randomness,
-not independent cities; no test result selects parameters, groups, or strata.
-
-\paragraph{Structural comparison convention.}
+not independent cities; TEST does not select parameters, groups, or strata.
+
+\noindent\textit{Structural comparison convention.}
 \label{subsec:equivalence_band}
-Uniform is the structural ruler. The hindsight minimum $\Delta^\star$ uses
-identical active sets, $M_r$, and $\mathcal C_r$, knowing all windows: an offline
-structural reference, not a prediction bound.  For each matched
-endpoint, normalize paired differences as
-$\langle\Delta_a-\Delta_b\rangle/
-\langle\Delta_{\mathrm{Uniform}}-\Delta^\star\rangle$, with both means over the
-same seeds, rather than averaging per-seed ratios. The existing paired 95\%
-intervals jointly resample numerator and denominator. An interval wholly within
-$[-.10,+.10]$ meets the registered practical band; for removed$-$full, an
-interval wholly above $+.10$ meets the protocol's component-necessity magnitude
-criterion. The independent group-TV practical-effect criterion requires a 95\% lower bound
-$\ge.5$ pp, using $\mathrm{pp}=50\Delta$. Parameter-free main contrasts use all
-20 seeds; tuning/report halves assess stability. These magnitude criteria are
-separate from the Wilcoxon/Holm tests below. Section~\ref{subsec:rq2_mechanisms}
-reports the corresponding effects.
-
-Tests are seed-paired Wilcoxon~\cite{wilcoxon1945individual}, with
+Uniform is the structural ruler. The offline hindsight minimum $\Delta^\star$
+shares active sets, $M_r$, and $\mathcal C_r$. Normalize paired structural
+effects by $\langle\Delta_a-\Delta_b\rangle/
+\langle\Delta_{\mathrm{Uniform}}-\Delta^\star\rangle$, using same-seed means;
+95\% intervals jointly resample numerator/denominator. Intervals within
+$[-.10,+.10]$ meet the practical band; removed$-$full intervals above $+.10$
+meet the component-necessity magnitude criterion. Group-TV practical effects
+require a 95\% lower bound $\ge.5$ pp. Parameter-free contrasts use all
+20 seeds; tuning/report halves assess stability. Magnitude and significance
+criteria remain distinct.
+
+Seed-paired Wilcoxon~\cite{wilcoxon1945individual} tests use
 Holm~\cite{holm1979simple} correction at $.05$ within registered families:
 four ablation endpoints per dataset, four prediction contrasts per dataset,
 trained-rule contrasts within dataset/endpoint, and four 20-seed worst-group
@@ -1228,25 +1253,19 @@
 seed-paired percentile bootstrap draws at seed 20261002.  The descriptive $+.5\%$ worst-group tolerance
 uses mean paired relative differences on TEST seeds 30011--30020 for ranking
 prose; Holm tests use all 20. Formal non-inferiority uses a separate $2\%$ margin in the six-arm City Scanner comparison.
-For matched-support trained-rule comparisons, all arms are scored directly from
-their saved parameter states on the same TEST target weights, including runs
-whose final recorded window has an empty active set. Balanced-control,
+Matched-support rules use saved parameters and common TEST weights, including
+empty-final-window runs. Balanced-control,
 oracle-sensitivity, and concentration criteria retain their distinct thresholds below.
 
 \subsection{Deployment-Target Alignment (RQ1)}
 \label{subsec:rq1_alignment}
 \label{subsec:eval_rq1}
 
-Complete-framework comparisons evaluate deployment alignment;
-risk-semantic controls distinguish target and arrival evaluation.
-
 \paragraph{City Scanner protocols.}
 \label{subsec:cityscanner_real}
 
-Table~\ref{tab:cityscanner_real} tests group alignment under real sensing
-opportunities in two protocols with distinct data and target maps.
-Design is fixed on and Gate is unused; their $R/O/U$ definitions and scales
-are given in the setup and table. Appendices~\ref{app:cityscanner_nyc}--
+Table~\ref{tab:cityscanner_real} compares two
+real-opportunity protocols with distinct target maps, fixed-on Design, and unused Gate. Appendices~\ref{app:cityscanner_nyc}--
 \ref{app:cityscanner_p2_measured_o} give construction, filtering, and splits.
 Group-mismatch reductions below use ratios of seed means; prediction gains use mean
 seed-paired relative differences.
@@ -1392,9 +1411,6 @@
 \label{subsec:rq2_mechanisms}
 \label{subsec:eval_rq2}
 \label{subsec:eval_rq3}
-
-Matched-support comparisons isolate weighting and calibration;
-Design and component interventions examine their endpoint effects.
 
 \paragraph{Matched-support rules.}
 Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
@@ -1541,7 +1557,7 @@
 \pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
 $.114/.172$.  The required improvement against both FedAU and ObsUse is
 $-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
-while meeting no-harm (Table~\ref{tab:underserved_block}).  INT-R preserves the direction of U-Air's Design trade-off, while
+while meeting no-harm (Supplementary Table~\ref{tab:underserved_block}).  INT-R preserves the direction of U-Air's Design trade-off, while
 the SensorScope client--stratum advantage approaches zero.
 
 \paragraph{Component removal.}
@@ -1595,7 +1611,7 @@
 Constant within-client weights cancel in local normalization in the original
 station blocks (Appendix~\ref{app:local_hajek}).
 The within-stratum heterogeneity experiment varies time-tercile covariates at fixed block observation means
-(Table~\ref{tab:f1_mechanism}; Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
+(Supplementary Table~\ref{tab:f1_mechanism}; Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
 inputs to the correction pathway.
 
 \paragraph{Numerical accuracy.}
@@ -1611,9 +1627,6 @@
 \subsection{Target Support and Feasible Adjustment (RQ3)}
 \label{subsec:rq3_adjustment}
 \label{subsec:ceiling}
-
-Target-map variants and feasible group-mass ranges reveal adjustment space;
-reference and learning sensitivity explain its relation to prediction.
 
 \paragraph{Target-support variants.}
 \label{subsec:cityscanner_target_support}
@@ -1666,7 +1679,7 @@
 floor changes group marginals as well as zero masses. The separate four-contrast
 secondary family has no Holm-significant member. Common-target alignment uses
 group mismatch; client--stratum gaps are arm-specific
-(Table~\ref{tab:cityscanner_sixarm_cs}).
+(Supplementary Table~\ref{tab:cityscanner_sixarm_cs}).
 
 Target-map effects also depend on which groups the support represents.
 In the retrospective comparison (Appendix~\ref{app:cityscanner_phi}), masking
@@ -1701,7 +1714,7 @@
 in $5.22\%/5.18\%$ and the inverse-usability ceiling in $24.22\%/23.75\%$.
 At true margins on active Design-on support, reference stabilization error
 has median zero and maximum $\ell_1$ values $.553/.680$
-(Table~\ref{tab:app_a5_a6_audit}). The perturbation bound retains this error;
+(Supplementary Table~\ref{tab:app_a5_a6_audit}). The perturbation bound retains this error;
 A6a is sufficient for it to vanish. Shared support/state and A6b remain
 comparison conditions because the saved states omit active-set lists and
 estimated margins. The worst-case Design-on constant $L_\pi\le2\times10^{13}$

```

### appendix.tex

逐字节/内容保持，无差异。

### supplemental.tex

逐字节/内容保持，无差异。

### data_figures_revision.py

```diff
--- data_figures_revision.py before
+++ data_figures_revision.py after
@@ -32,7 +32,7 @@
       'mathtext.fontset':'stix','font.size':8,'axes.labelsize':8,'xtick.labelsize':7.5,
       'ytick.labelsize':7.5,'legend.fontsize':7.5,'axes.linewidth':.65,
       'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':250,
-      'axes.unicode_minus':True})
+      'axes.unicode_minus':True,'hatch.linewidth':.35})
 
 
 def frame(ax):
@@ -50,7 +50,7 @@
 def save(fig,name,record):
     OUT.mkdir(parents=True,exist_ok=True)
     fig.canvas.draw()
-    for ext in ['pdf','png']:
+    for ext in ['pdf','svg','png']:
         fig.savefig(OUT/(name+'.'+ext),facecolor='white')
     record['size_inches']=list(fig.get_size_inches())
     record['axis_labels']=[{'x':a.get_xlabel(),'y':a.get_ylabel()} for a in fig.axes]
@@ -72,13 +72,13 @@
 def fig2_e2():
     source=DATA/'FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv';d=pd.read_csv(source)
     s=stats(d,E2,'D_aligned');x=np.arange(5)
-    fig,axes=plt.subplots(1,2,figsize=(3.5,1.95))
+    fig,axes=plt.subplots(1,2,figsize=(3.5,1.72))
     fig.subplots_adjust(left=.25,right=.98,bottom=.29,top=.96,wspace=.50)
-    labels=['FedAvg','FedAsync','TimeAlign','2S-Hájek','RAVEN-MCS']
+    labels=['FedAvg','FedAsync','TimeAlign','2S-Hájek','RAVEN-Design']
     for i,row in enumerate(s):
         ci=METHODS.index(row['method'])
-        axes[0].barh(i,row['mean'],xerr=row['sample_sd'],height=.63,color=COLORS[ci],edgecolor='#263747',linewidth=.5,
-         error_kw={'elinewidth':.7,'capsize':2,'capthick':.7},hatch='//' if ci==5 else None)
+        axes[0].barh(i,row['mean'],xerr=row['sample_sd'],height=.63,color=COLORS[ci],edgecolor='#263747',linewidth=.35,
+         error_kw={'elinewidth':.7,'capsize':2,'capthick':.7},hatch='/' if ci==5 else None)
     axes[0].axvline(0,color='#263747',ls='--',lw=.8)
     lo=min(v['mean']-v['sample_sd'] for v in s);hi=max(v['mean']+v['sample_sd'] for v in s);span=hi-lo
     axes[0].set_xlim(min(0,lo)-span*.10,max(0,hi)+span*.14)
@@ -88,10 +88,10 @@
     counts=[]
     for i,m in enumerate(E2):
         q=d.loc[d.method==m,'D_aligned'];n=int((q<0).sum());counts.append(n);ci=METHODS.index(m)
-        axes[1].barh(i,n,height=.63,color=COLORS[ci],edgecolor='#263747',linewidth=.5,hatch='//' if ci==5 else None)
+        axes[1].barh(i,n,height=.63,color=COLORS[ci],edgecolor='#263747',linewidth=.5,hatch='/' if ci==5 else None)
         axes[1].text(n+.6,i,f'{n}/{len(q)}',ha='left',va='center',fontsize=7.4)
     axes[1].axvline(10,color='#69737B',ls=':',lw=.8);axes[1].set_xlim(0,27)
-    axes[1].set_xticks([0,10,20]);axes[1].set_xlabel('Negative seeds',labelpad=2)
+    axes[1].set_xticks([0,10,20]);axes[1].set_xlabel(r'Seeds with $D<0$',labelpad=2)
     for i,ax in enumerate(axes):ax.set_yticks(x,labels if i==0 else ['']*5);ax.set_ylim(4.6,-.6);frame(ax);ax.grid(False)
     panel(axes[0],'(a) Risk difference',-.35);panel(axes[1],'(b) Direction count',-.35)
     save(fig,'fig2_e2_risk_noninterchangeability',{'source':str(source.relative_to(R)),'stats':s,'negative_counts':counts,'negative_denominator':20})
@@ -101,12 +101,12 @@
     mass=pd.read_csv(DATA/'FIG_G3_TDRIVE_H_MASS.csv');tv=pd.read_csv(DATA/'FIG_G3_TDRIVE_TV.csv')
     fig,axes=plt.subplots(1,2,figsize=(3.5,1.92));fig.subplots_adjust(left=.13,right=.98,bottom=.27,top=.80,wspace=.55)
     ax=axes[0];x=np.arange(4);w=.25
-    for j,(col,label,color,hatch) in enumerate([('mu_test_seal',r'Target $\mu$','#77818B','//'),('pi_opp_real_R',r'Real $R$','#365E83','xx'),('pi_opp_balanced_unit','Unit-balanced','#82947B','..')]):
+    for j,(col,label,color,hatch) in enumerate([('mu_test_seal',r'Target $\mu$','#77818B','//'),('pi_opp_real_R',r'Real $R$','#365E83','/'),('pi_opp_balanced_unit','Unit-balanced','#82947B','..')]):
         ax.bar(x+(j-1)*w,mass[col],w,label=label,color=color,hatch=hatch,edgecolor='#263747',linewidth=.45)
     ax.set_xticks(x,mass.h_id,fontsize=8);ax.set_ylim(0,.78);ax.set_yticks([0,.3,.6]);ax.set_ylabel('Group mass')
     ax.legend(loc='lower center',bbox_to_anchor=(.48,1.01),ncol=1,frameon=False,fontsize=7.5,labelspacing=.15,borderaxespad=0)
     ax=axes[1];vals=tv.tv_opp_vs_mu.to_numpy();bars=ax.bar(np.arange(3),vals,.56,color=['#365E83','#77818B','#82947B'],edgecolor='#263747',linewidth=.5)
-    for b,v,h in zip(bars,vals,['xx','//','..']):b.set_hatch(h);ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.3f}',ha='center',fontsize=7.5)
+    for b,v,h in zip(bars,vals,['/','\\','..']):b.set_hatch(h);ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.3f}',ha='center',fontsize=7.5)
     ax.axhline(.05,color='#69737B',ls=':',lw=.9)
     ax.set_xticks([0,1,2],['T-Drive','SS\nprot.','UA\nprot.'],fontsize=7.7);ax.set_ylim(0,.38);ax.set_ylabel(r'TV$(\pi^{\mathrm{opp}},\mu)$')
     for ax in axes:frame(ax);ax.grid(False)
@@ -115,14 +115,14 @@
 
 
 def fig_w1_design_gate():
-    d=pd.read_csv(DATA/'FIG_W1_DESIGN_GATE.csv');fig,axes=plt.subplots(1,2,figsize=(3.5,2.10))
+    d=pd.read_csv(DATA/'FIG_W1_DESIGN_GATE.csv');fig,axes=plt.subplots(1,2,figsize=(3.5,1.90))
     fig.subplots_adjust(left=.13,right=.98,bottom=.26,top=.84,wspace=.50)
     annotation_records=[]
     for ax,col,cap in zip(axes,['Delta_group_pct','RMSE_mu_pct'],['(a) Group mismatch','(b) Target RMSE']):
         values=[]
         for j,var in enumerate(['Estimated','Oracle']):
             vals=[float(d.loc[(d.dataset==ds)&(d.variant==var),col].iloc[0]) for ds in ['SensorScope','U-Air']]
-            bars=ax.bar(np.arange(2)+(j-.5)*.34,vals,.32,label=var,color=['#82947B','#365E83'][j],hatch=['//','..'][j],edgecolor='#263747',linewidth=.5)
+            bars=ax.bar(np.arange(2)+(j-.5)*.34,vals,.32,label=var,color=['#82947B','#365E83'][j],hatch=['/','..'][j],edgecolor='#263747',linewidth=.5)
             for b,v in zip(bars,vals):
                 # Two reserved annotation rows per sign, independent of tiny bar heights.
                 label_y=(.82+j*.12) if v>=0 else (.055+j*.095)
@@ -183,7 +183,7 @@
     fig,axes=plt.subplots(2,1,figsize=(3.5,3.00));fig.subplots_adjust(left=.18,right=.97,top=.97,bottom=.15,hspace=1.0)
     ax=axes[0]
     for ds,color,mark,label in [('sensorscope','#365E83','o','SensorScope'),('uair','#82947B','s','U-Air')]:
-        q=cert[cert.dataset==ds];ax.scatter(q.C_t,q.C_LCB,s=11,facecolors='none',edgecolors=color,marker=mark,lw=.65,label=label,zorder=3)
+        q=cert[cert.dataset==ds];ax.scatter(q.C_t,q.C_LCB,s=11,facecolors='none',edgecolors=color,marker=mark,lw=.65,label=label,zorder=3,alpha=.55)
     bad=cert[cert.C_LCB>cert.C_t+1e-12]
     ax.scatter(bad.C_t,bad.C_LCB,marker='x',s=24,color='#A65B4E',lw=.9,label='Miscoverage',zorder=5)
     hi=max(float(cert.C_t.max()),float(cert.C_LCB.max()),.2)*1.06
@@ -238,21 +238,20 @@
     files=[R/'results_c1_cityscanner/round_v1/tables/CS_E3.csv',R/'results_joint_ou/round_v1/tables/JO_E3.csv']
     methods=['fedavg_window','twostage_hajek','fedau_window','obsuse_window','raven'];labels=['FedAvg','TwoStage-Hájek','FedAU','ObsUse','RAVEN-Design']
     colors=['#77818B','#5C8F98','#B18A75','#9B88A0','#365E83'];marks=['o','v','s','D','P'];rows=[]
-    fig,axes=plt.subplots(2,3,figsize=(7.16,3.9));fig.subplots_adjust(left=.16,right=.98,top=.90,bottom=.18,wspace=.44,hspace=.85)
+    fig,axes=plt.subplots(2,2,figsize=(7.16,2.05));fig.subplots_adjust(left=.15,right=.98,top=.91,bottom=.17,wspace=.34,hspace=1.05)
     for row,(file,protocol) in enumerate(zip(files,['Visit occupancy: real R, controlled O/U','Pilot 2: union-GPS R, measured O, controlled U'])):
         d=pd.read_csv(file)
-        for j,(metric,title) in enumerate([('Delta_group',r'Group mismatch $\downarrow$'),('RMSE_mu',r'Target RMSE $\downarrow$'),('WorstGroupRMSE',r'Worst-group RMSE $\downarrow$')]):
+        for j,(metric,title) in enumerate([('Delta_group',r'Group mismatch $\downarrow$'),('RMSE_mu',r'Target RMSE $\downarrow$')]):
             ax=axes[row,j];ss=[]
             for i,m in enumerate(methods):
                 q=d.loc[d.method==m,metric];assert len(q)==10
                 mean=float(q.mean());sd=float(q.std(ddof=1));ss.append({'method':m,'mean':mean,'sample_sd':sd})
                 ax.errorbar(mean,i,xerr=sd,fmt=marks[i],color=colors[i],markersize=4,capsize=2,lw=.8)
             ax.set_yticks(range(5),labels if j==0 else ['']*5);ax.set_ylim(4.5,-.5);ax.xaxis.set_major_locator(MaxNLocator(3));frame(ax)
-            panel(ax,f'({"abcdef"[row*3+j]}) '+(['Group mismatch ↓','Target RMSE ↓\n(block-specific z-score)','Worst-group RMSE ↓\n(block-specific z-score)'][j]),-.25)
+            panel(ax,f'({"abcd"[row*2+j]}) '+(['Group mismatch ↓','Target RMSE ↓','Worst-group RMSE ↓\n(block-specific z-score)'][j]),-.25)
             rows.append({'protocol':protocol,'source':str(file.relative_to(R)),'metric':metric,'stats':ss})
         axes[row,0].text(0,1.15,protocol,transform=axes[row,0].transAxes,ha='left',fontsize=8.3,bbox={'fc':'white','ec':'none','pad':0})
-    fig.text(.56,.025,'Points: means; intervals: sample SD (10 seeds per protocol)',ha='center',fontsize=8)
-    save(fig,'fig_cityscanner_core_candidate',{'rows':rows,'uncertainty':'mean ± sample SD, 10 seeds per protocol','integration':'candidate only; Table II retained without duplicate figure'})
+    save(fig,'fig_cityscanner_core_candidate',{'rows':rows,'uncertainty':'mean ± sample SD, 10 seeds per protocol','integration':'candidate; main integration compiled to 15 pages; full endpoints remain in table'})
 
 
 FUNCTIONS={f.__name__:f for f in [fig2_e2,fig_g3_tdrive,fig_w1_design_gate,fig3_structural,fig4_prediction,fig_certificate,fig_learning_capacity,fig_cityscanner_candidate]}

```

