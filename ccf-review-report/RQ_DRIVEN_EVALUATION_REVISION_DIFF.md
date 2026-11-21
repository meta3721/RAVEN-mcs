# RQ驱动Evaluation：修改前后对照与完整差异

正式交付与核验结论见 [修改报告](C:/Cursor/raven.mcs/ccf-review-report/RQ_DRIVEN_EVALUATION_REVISION_REPORT.md)。本文件记录本轮相对于修改前备份的差异，不是相对于仓库历史提交，因而保留此前用户及其他AI已完成的修改。

## 1. 结构前后对照

修改前依次为 Experimental Setup、Real Sensing Opportunities and Measured Observation、Risk Semantics and External Protocols、Design Effects in Controlled Station Protocols、Attributing Structural Gains and Component Trade-offs、Prediction Sensitivity and Adjustment Geometry、Update-Rule Sensitivity and Coverage Scope。

修改后先列三个RQ，再依次为：

1. Datasets and Selection Protocols。
2. Baselines and Evaluation Measures。
3. Implementation and Statistical Settings。
4. Deployment-Target Alignment (RQ1)。
5. Mechanism Contributions (RQ2)。
6. Target Support and Feasible Adjustment (RQ3)。

原来按实验来源交错的应用结果、权重归因与几何解释，改为按问题聚合；没有增加第四个成本或条件核验问题。

## 2. 代表性实质修改

- **Evaluation开篇：**以部署对齐、参考/校准作用、支持及约束空间三个层次开篇，紧接完整RQ列表，不提前堆放结果数字、限制或数据集名。
- **设置与结果分开：**原设置中的离线差距效果移入RQ2；训练配置与统计家族集中到C。补充现有正式记录可核对的2局部步与100/80窗口预算，没有引入新参数。
- **应用与支持分开：**City Scanner两套五方法结果保留在RQ1；六臂目标图整表及其解释迁入RQ3。保留25.8%/23.3%的计算口径和预测真实排名。
- **机制按隔离比较展开：**将Count→Uniform、参考→投影、Uniform→投影和投影→完整P2放在同一段落链条；投影相对Uniform的0.768/0.286 pp与独立Design的0.922 pp继续分开。
- **支持变化紧随对应比较：**U-Air的774窗口、51.6%重合解释移至Design对照旁，避免用固定R/O/U替代同活跃支持条件。
- **成本与结构端点相邻：**简单投影的组端点及时间优势、完整P2在客户端—分层端点的差异与预测检验一起呈现，未隐藏不利结果。
- **几何先于辅助诊断：**RQ3先目标图及支持，再formal/arrival/development几何，后稳定化、参考与学习敏感性。L1评价与P2平方L2目标仍明确区分。
- **独立诊断归位：**训练均值、测试拟合常数和完整优化器敏感性原文迁入附录K；独立释放与coverage-controlled变体保留既有附录，删去正文重复摘要。

三个结果小节的结尾分别直接回答组对齐范围、可识别机制增量、多目标取舍及可调空间，未使用内部“PASS/中等匹配”等标签。全部表图数据块、公式与证明未改；新顺序仅改变自动编号和分页位置。

## 3. 词数、分页与回退

同口径Evaluation近似英文词数3430→3491（+61）；正文14→14页，补充14→14页。没有调整模板、字体、页边距或行距。新增问题与连接说明抵消了文字删减，不把内容迁移当成全文净节省。

[修改前归档](C:/Cursor/raven.mcs/ccf-review-report/backups/rq_evaluation_20261101_234754.zip)包含回退源文件及两份PDF。仅恢复本轮源文件改动；有后续修改时按以下差异反向合并，不能整体覆盖新main.tex。恢复后重新顺序编译两份文档。

## 4. 完整源码差异

以下差异由本轮修改前后文件直接生成；未改动的supplemental.tex、reference.bib、图片和实验文件不列差异。

### main.tex

```diff
--- main.tex before
+++ main.tex after
@@ -1071,14 +1071,20 @@
 \section{Evaluation}
 \label{sec:evaluation}
 
-We evaluate application-level group alignment, attribute same-support structural
-changes to reference and calibration mechanisms, and examine prediction,
-runtime, and finite-support diagnostics.
-
-\subsection{Experimental Setup}
+We study deployment-target alignment, the roles of reference reconstruction and
+feasible calibration, and the adjustment space set by support and constraints.
+\begin{itemize}
+\item \textbf{RQ1:} How effectively does RAVEN-MCS align aggregated client
+contributions with deployment targets under sequential sensing and update selection?
+\item \textbf{RQ2:} How do reference reconstruction and feasible calibration
+contribute to deployment-group alignment on matched client support?
+\item \textbf{RQ3:} How do target support and aggregation constraints shape
+the feasible adjustment of deployment-group mass?
+\end{itemize}
+
+\subsection{Datasets and Selection Protocols}
 \label{subsec:eval_setup}
 
-\subsubsection{Data, targets, and selection}
 Table~\ref{tab:datasets} gives chronological splits, groups, strata, and roles.
 SensorScope~\cite{ingelrest2010sensorscope,barrenetxea2019sensorscope} and
 U-Air~\cite{zheng2013uair} use station clients and spatial-unit $\times$ UTC-block
@@ -1132,7 +1138,9 @@
 \end{tabular*}
 \end{table*}
 
-\subsubsection{Methods and pairing}
+\subsection{Baselines and Evaluation Measures}
+\label{subsec:eval_methods}
+
 Table~\ref{tab:nearest_neighbor} compares the selection objects, information
 requirements, and guarantee scopes of RAVEN, FedIPW, and FedPALS. This is a
 mechanism comparison, distinct from the evaluated baseline family below.
@@ -1143,21 +1151,16 @@
 opportunity/observation correction.  FedAU-Window adapts participation
 debiasing~\cite{wang2024lightweight}; ObsUse-Window corrects observation and
 usability without Design, P2, or debt.  Appendix~\ref{app:adapted_baselines}
-specifies these windowed adaptations.  Inst-Cal removes debt from full P2;
-Debt-Cal and reference-only Central-All, Central-Delivered, and RAVEN-SimOracle
-provide additional context, not deployable performance guarantees.
-
-Paired methods share EventTraces and within-stratum exchangeability
-$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.
-Design-on/off arms fix their setting throughout each run.  Controlled station
-comparisons use 20 paired seeds; each City Scanner five-method block and
-T-Drive use ten, and the balanced control uses five.  The six-arm target-map
-comparison uses ten traces with three model seeds each.  Other counts are
-specified per table.  Learning diagnostics use three development
-seeds and one Uniform trajectory.  Seeds represent model/trace randomness,
-not independent cities; no test result selects parameters, groups, or strata.
-
-\subsubsection{Metrics and statistical policy}
+specifies these windowed adaptations. Inst-Cal removes debt from full P2.
+Additional comparisons include Debt-Cal and the reference-only Central-All,
+Central-Delivered, and RAVEN-SimOracle.
+Full RAVEN uses Sections~\ref{sec:reconstruction}--\ref{sec:calibration} with
+run-fixed Design. Matched-support rules include Count, Uniform, projection,
+Inst-Cal, and full P2. Projection minimizes squared distance to $\widehat\beta_r$
+on $\mathcal C_r$; the separate tuning-selected $\kappa=1000$ rule adds
+$-\kappa\mathbf Q_r^\top M_r\alpha$ and its own debt recursion.
+Component removal changes only the specified component.
+
 On supported test units,
 \[
 \mathrm{RMSE}_{\mu}=\left[\sum_{i\in\mathcal I_{\mathrm{test}}}
@@ -1177,20 +1180,32 @@
 Only the risk-semantic test replaces target weights by
 \eqref{eq:arrival_distribution} for $\mathrm{RMSE}_{\rho}$.
 Structural metrics are \eqref{eq:omega_bar}--\eqref{eq:delta_cs}.
-
-The training-mean predictors score $7.647/1.054/1.007$ on
-SensorScope/U-Air/Traffic.  Constants fitted to the scored test labels score
-$2.088/.678/1.007$ and are diagnostic references, not deployable baselines.
-Training/test target means are $.301/7.657$, $0/-.807$, and $0/.003$,
-respectively. Under the Complete-aligned station protocol, model RMSE on
-both SensorScope and U-Air exceeds the corresponding training-mean baseline.
+Group mismatch measures deployment alignment; client--stratum gaps, prediction
+errors, and wall-clock seconds describe composition, task performance, and cost.
+
+\subsection{Implementation and Statistical Settings}
+\label{subsec:eval_implementation}
+
+Paired methods share Common-NDMF, step sizes, and traces. Formal SensorScope/U-Air
+runs use two local steps and 100/80 windows, respectively; separate learning-capacity
+comparisons use their own budgets and physical scales
+(Appendix~\ref{app:learning_capacity}).
+
+Paired methods share EventTraces and within-stratum exchangeability
+$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$.
+Design-on/off arms fix their setting throughout each run.  Controlled station
+comparisons use 20 paired seeds; each City Scanner five-method block and
+T-Drive use ten, and the balanced control uses five.  The six-arm target-map
+comparison uses ten traces with three model seeds each.  Other counts are
+specified per table.  Learning diagnostics use three development
+seeds and one Uniform trajectory.  Seeds represent model/trace randomness,
+not independent cities; no test result selects parameters, groups, or strata.
 
 \paragraph{Structural comparison convention.}
 \label{subsec:equivalence_band}
 Uniform is the structural ruler. The hindsight minimum $\Delta^\star$ uses
 identical active sets, $M_r$, and $\mathcal C_r$, knowing all windows: an offline
-structural reference, not a prediction bound. Its group-TV gap from Uniform is
-$3.44/1.32$ pp on SensorScope/U-Air over 20 always-on seeds. For each matched
+structural reference, not a prediction bound.  For each matched
 endpoint, normalize paired differences as
 $\langle\Delta_a-\Delta_b\rangle/
 \langle\Delta_{\mathrm{Uniform}}-\Delta^\star\rangle$, with both means over the
@@ -1201,7 +1216,7 @@
 criterion. The independent group-TV practical-effect criterion requires a 95\% lower bound
 $\ge.5$ pp, using $\mathrm{pp}=50\Delta$. Parameter-free main contrasts use all
 20 seeds; tuning/report halves assess stability. These magnitude criteria are
-separate from the Wilcoxon/Holm tests below. Section~\ref{subsec:eval_rq3}
+separate from the Wilcoxon/Holm tests below. Section~\ref{subsec:rq2_mechanisms}
 reports the corresponding effects.
 
 Tests are seed-paired Wilcoxon~\cite{wilcoxon1945individual}, with
@@ -1218,7 +1233,14 @@
 whose final recorded window has an empty active set. Balanced-control,
 oracle-sensitivity, and concentration criteria retain their distinct thresholds below.
 
-\subsection{Real Sensing Opportunities and Measured Observation}
+\subsection{Deployment-Target Alignment (RQ1)}
+\label{subsec:rq1_alignment}
+\label{subsec:eval_rq1}
+
+Complete-framework comparisons evaluate deployment alignment;
+risk-semantic controls distinguish target and arrival evaluation.
+
+\paragraph{City Scanner protocols.}
 \label{subsec:cityscanner_real}
 
 Table~\ref{tab:cityscanner_real} tests group alignment under real sensing
@@ -1277,63 +1299,9 @@
 FedAU/ObsUse/FedAvg by $.43\%/.45\%/.65\%$, while TwoStage-H\'ajek leads
 both prediction endpoints and client--stratum alignment. The first two
 comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
-The shared application advantage is group composition alignment, with
-protocol-dependent prediction rankings.
-
-\paragraph{Target-support variants.}
-\label{subsec:cityscanner_target_support}
-Table~\ref{tab:cityscanner_sixarm} tests whether group-alignment gains persist
-across target support and client--stratum shapes on ten shared visit-occupancy
-traces, each with three model seeds. Floor fills the control map's zero masses
-and renormalizes. M1$\mu$/M2$\mu$ use ACS population/NYC~311 shapes on the
-same control keys, rescaled within region to the public $\boldsymbol\mu$.
-These are trained target-map variants; Appendix~\ref{app:cityscanner_sixarm}
-gives their construction and statistical details.
-
-\begin{table*}[t]
-\centering
-\caption{City Scanner visit-occupancy target-map variants.
-Mean $\pm$ SD over ten trace means, each averaging three model seeds.
-Predictions share region weights and a training-standardized scale.
-$\rho$ is the percentage of non-test delivered units assigned zero mass
-(zero with Design off). Group gaps use the common public region target;
-bold marks endpoint minima.}
-\label{tab:cityscanner_sixarm}
-\footnotesize
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}
-\toprule
-Method / target map & $\rho$ (\%) & $\Delta_{\mathrm{group}}\downarrow$ &
-$\mathrm{RMSE}_{\mu}\downarrow$ & WorstGroupRMSE $\downarrow$\\
-\midrule
-FedAvg / count & 0.00 & $0.1953{\pm}0.0342$ & $\mathbf{0.2409}{\pm}0.0832$ & $\mathbf{0.2529}{\pm}0.0903$\\
-RAVEN-NoDesign & 0.00 & $0.0736{\pm}0.0264$ & $0.2439{\pm}0.0835$ & $0.2575{\pm}0.0905$\\
-RAVEN-control & 14.35 & $0.0706{\pm}0.0266$ & $0.2561{\pm}0.1031$ & $0.2695{\pm}0.1095$\\
-RAVEN-floor & 0.00 & $\mathbf{0.0682}{\pm}0.0313$ & $0.2442{\pm}0.0842$ & $0.2576{\pm}0.0908$\\
-RAVEN-M1$\mu$ & 1.01 & $0.0771{\pm}0.0338$ & $0.2467{\pm}0.0889$ & $0.2609{\pm}0.0971$\\
-RAVEN-M2$\mu$ & 0.98 & $0.0813{\pm}0.0301$ & $0.2508{\pm}0.0907$ & $0.2661{\pm}0.1003$\\
-\bottomrule
-\end{tabular*}
-\end{table*}
-
-Floor, M1$\mu$, and M2$\mu$ each reduce group mismatch versus FedAvg on
-all ten paired traces and pass the three pre-specified structural comparisons
-under the graphical multiplicity allocation (one-sided paired Wilcoxon,
-each $p=9.77\times10^{-4}$). Floor retains $101.9\%$ of the FedAvg-to-control
-group gain. The gains therefore remain observable in these support/shape
-variants; NoDesign also has lower group mismatch than M1$\mu$/M2$\mu$.
-
-For floor/M1$\mu$/M2$\mu$ versus FedAvg, one-sided 95\% prediction upper bounds
-of $3.83/4.14/8.15\%$ exceed the $2\%$ non-inferiority margin;
-the gated superiority tests therefore remain untested. Separately, the primary trace-level
-ratio $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$
-has Hodges--Lehmann estimate $-.019\%$, 95\% percentile trace-cluster interval
-$[-1.89\%,+12.28\%]$, and $p=.922$. Deletion cost remains unresolved;
-floor changes group marginals as well as zero masses. The separate four-contrast
-secondary family has no Holm-significant member. Arm-specific client--stratum
-gaps are reported in Table~\ref{tab:cityscanner_sixarm_cs}.
-
-\subsection{Risk Semantics and External Protocols}
-\label{subsec:eval_rq1}
+
+
+\paragraph{Risk semantics and external protocols.}
 
 The five-seed balanced control meets its $3\%$ no-harm margin: RAVEN versus
 TimeAlign degrades by $.0599\%$, with one-sided 95\% upper bound $.134\%$.
@@ -1412,8 +1380,95 @@
 $.1048$); RAVEN stays within the descriptive worst-group tolerance against
 FedAU/ObsUse under its local four-region target.
 
-\subsection{Design Effects in Controlled Station Protocols}
+Arrival-weighted validation shifts the reported risk by $-4.11\%$ to
+$-4.12\%$ on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects
+the same configuration on all 20 seeds. In these comparisons, the scoring
+distortion changes reported error more than configuration selection.
+
+Both City Scanner protocols show group-alignment gains under real opportunities
+and controlled delivery; prediction and external-protocol rankings differ.
+
+\subsection{Mechanism Contributions (RQ2)}
+\label{subsec:rq2_mechanisms}
 \label{subsec:eval_rq2}
+\label{subsec:eval_rq3}
+
+Matched-support comparisons isolate weighting and calibration;
+Design and component interventions examine their endpoint effects.
+
+\paragraph{Matched-support rules.}
+Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
+RAVEN's active support across count weighting, Uniform, reference projection,
+Inst-Cal, and full P2.  Its U-Air count row is not the unrestricted FedAvg row
+of Table~\ref{tab:main_effectiveness}.  All paired rules use the same target and cap/ESS definitions;
+prediction follows the common saved-parameter scoring rule above.
+
+\begin{table*}[t]
+\centering
+\caption{Trained aggregation rules on matched Design-on support.
+Means over 20 paired seeds per dataset; lower is better.
+Wall is wall-clock seconds per run. U-Air Count uses RAVEN-Design support,
+unlike unrestricted FedAvg in Table~\ref{tab:main_effectiveness}.
+}
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
+Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
+reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
+count-to-Uniform and $.65$ pp remaining. U-Air gives $1.47$ pp
+($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
+This isolates the effect of removing count weighting; the following contrasts
+measure the reference and calibration increments.
+The hindsight structural ruler has a group-TV gap from Uniform of
+$3.44/1.32$ pp on SensorScope/U-Air over 20 always-on seeds. U-Air FedAU/ObsUse use
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
+
+Full P2 has $.118$ pp more group mismatch than projection on SensorScope
+($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
+U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
+versus RAVEN's $27.1/15.3$ s. The prediction contrasts are not
+Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ using the saved model parameters).
+
+\paragraph{Fixed-configuration Design effects.}
 
 Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  SensorScope
 Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$.
@@ -1423,6 +1478,10 @@
 mismatch by $6.943\%$, RMSE by $6.885\%$, and tail RMSE by $7.221\%$, while
 worsening client--stratum mismatch by $4.990\%$. Both estimated and oracle
 Design show this reversal (Fig.~\ref{fig:w1_design_gate}).
+Across 774 paired U-Air windows, R/O/U and registration are shared, but
+Design changes positive-mass support (active-set overlap $51.6\%$).
+This end-to-end contrast includes support changes;
+the projected SensorScope comparison holds support fixed.
 
 \begin{table}[!htbp]
 \centering
@@ -1485,88 +1544,6 @@
 while meeting no-harm (Table~\ref{tab:underserved_block}).  INT-R preserves the direction of U-Air's Design trade-off, while
 the SensorScope client--stratum advantage approaches zero.
 
-\subsection{Attributing Structural Gains and Component Trade-offs}
-\label{subsec:eval_rq3}
-
-\paragraph{Matched-support rules.}
-Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
-RAVEN's active support across count weighting, Uniform, reference projection,
-Inst-Cal, and full P2.  Its U-Air count row is not the unrestricted FedAvg row
-of Table~\ref{tab:main_effectiveness}.  Projection minimizes squared distance
-to $\widehat\beta_r$ on $\mathcal C_r$; the separate $\kappa=1000$ sensitivity
-rule adds $-\kappa\mathbf Q_r^\top M_r\alpha$ and its own debt recursion,
-with strength selected on tuning seeds.
-Prediction uses the common saved-parameter scoring rule defined above.
-
-\begin{table*}[t]
-\centering
-\caption{Trained aggregation rules on matched Design-on support.
-Means over 20 paired seeds per dataset; lower is better.
-Wall is wall-clock seconds per run. U-Air Count uses RAVEN-Design support,
-unlike unrestricted FedAvg in Table~\ref{tab:main_effectiveness}.
-}
-\label{tab:trained_rules}
-\footnotesize
-\setlength{\tabcolsep}{5pt}
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrr}
-\toprule
-Dataset & Server-weight rule & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$ &
-$\mathrm{RMSE}_\mu$ & WorstGroupRMSE & Wall (s)\\
-\midrule
-SensorScope & Count / matched support & $1.05577$ & $1.29032$ & $7.93889$ & $8.67161$ & $20.5$\\
-SensorScope & Uniform & $1.02693$ & $1.27069$ & $7.93931$ & $8.67202$ & $20.0$\\
-SensorScope & Reference projection & $1.01158$ & $1.26903$ & $7.93725$ & $8.66989$ & $19.9$\\
-SensorScope & Projection with debt ($\kappa=1000$) & $0.98464$ & $1.26659$ & $7.93842$ & $8.67109$ & $18.5$\\
-SensorScope & Inst-Cal & $1.01409$ & $1.26443$ & $7.93799$ & $8.67066$ & $26.2$\\
-SensorScope & Full RAVEN-Design & $1.01394$ & $1.26438$ & $7.93799$ & $8.67066$ & $27.1$\\
-\midrule
-U-Air & Count / matched support & $1.12176$ & $1.26213$ & $1.19225$ & $1.25956$ & $12.0$\\
-U-Air & Uniform & $1.09734$ & $1.24065$ & $1.19349$ & $1.26094$ & $8.5$\\
-U-Air & Reference projection & $1.09162$ & $1.23265$ & $1.19691$ & $1.26474$ & $8.8$\\
-U-Air & Projection with debt ($\kappa=1000$) & $1.08001$ & $1.22623$ & $1.19470$ & $1.26231$ & $9.0$\\
-U-Air & Inst-Cal & $1.09241$ & $1.23342$ & $1.19537$ & $1.26304$ & $15.1$\\
-U-Air & Full RAVEN-Design & $1.09236$ & $1.23339$ & $1.19537$ & $1.26303$ & $15.3$\\
-\bottomrule
-\end{tabular*}
-\end{table*}
-
-Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
-reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
-count-to-Uniform and $.65$ pp remaining. U-Air gives $1.47$ pp
-($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
-This isolates the effect of removing count weighting; the following contrasts
-measure the reference and calibration increments. U-Air FedAU/ObsUse use
-different supports and do not enter this attribution.
-
-Before feasible calibration, the direct corrected reference has group-mismatch
-readouts of $1.03533/1.11961$ on SensorScope/U-Air, above Uniform and
-potentially infeasible under caps/ESS. Projecting it improves these readouts by
-$1.188$ pp ($[.956,1.409]$) and $1.399$ pp ($[1.019,1.782]$), respectively.
-This fixed-support structural contrast quantifies the role of converting a
-reconstructed reference into a finite-window allocation; trained prediction
-and runtime are reported separately in Table~\ref{tab:trained_rules}.
-
-Relative to Uniform, corrected-reference projection improves group mismatch
-by $.768$ pp ($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$)
-on U-Air. The $.5$ pp practical line is cleared stably only on SensorScope;
-U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.
-SensorScope's independent same-support projected Design-on/off contrast gives
-$.922$ pp ($[.721,1.141]$). This opportunity-correction effect is not additive
-with projection--Uniform;
-U-Air changes active support and cannot identify that contrast.
-
-Full P2 has $.118$ pp more group mismatch than projection on SensorScope
-($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
-U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
-versus RAVEN's $27.1/15.3$ s. The prediction contrasts are not
-Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ using the saved model parameters).
-
-\paragraph{Numerical accuracy.}
-The independent projection comparison has endpoint discrepancy up to
-$2.42\times10^{-5}$ in $\Delta$ units
-(Appendix~\ref{app:kappa_probe}, including residual and objective-gap diagnostics). Appendix~\ref{app:p2_diagnostics} assesses numerical feasibility and solver
-discrepancies separately from mathematical optimality.
-
 \paragraph{Component removal.}
 Table~\ref{tab:e4_ablation} removes one component from Design-on under paired
 Complete-aligned traces, reporting
@@ -1615,18 +1592,131 @@
 \end{tabular}
 \end{table}
 
-\paragraph{Configuration and support.}
-The offline support rule and retrospective cost chart are in
-Appendix~\ref{app:cityscanner_phi}. Their catalogue and target lookup must
-exist before window opening; the coverage Gate does not select Design.
-The 774-window U-Air paired analysis holds R/O/U fixed, but Design changes positive-mass
-support (active-set overlap $51.6\%$). Zero-target share is not a cost predictor:
-masking SensorScope keys gives at most $.175\%$ cost at share $.388$, whereas
-U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
-
-\subsection{Prediction Sensitivity and Adjustment Geometry}
+Constant within-client weights cancel in local normalization in the original
+station blocks (Appendix~\ref{app:local_hajek}).
+The within-stratum heterogeneity experiment varies time-tercile covariates at fixed block observation means
+(Table~\ref{tab:f1_mechanism}; Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
+inputs to the correction pathway.
+
+\paragraph{Numerical accuracy.}
+The independent projection comparison has endpoint discrepancy up to
+$2.42\times10^{-5}$ in $\Delta$ units
+(Appendix~\ref{app:kappa_probe}, including residual and objective-gap diagnostics). Appendix~\ref{app:p2_diagnostics} assesses numerical feasibility and solver
+discrepancies separately from mathematical optimality.
+
+Count-to-Uniform and reference-projection increments are distinct; full P2
+coordinates endpoint and runtime trade-offs. Component effects are endpoint-specific,
+with a small standard-strength debt contribution.
+
+\subsection{Target Support and Feasible Adjustment (RQ3)}
+\label{subsec:rq3_adjustment}
 \label{subsec:ceiling}
 
+Target-map variants and feasible group-mass ranges reveal adjustment space;
+reference and learning sensitivity explain its relation to prediction.
+
+\paragraph{Target-support variants.}
+\label{subsec:cityscanner_target_support}
+Table~\ref{tab:cityscanner_sixarm} tests whether group-alignment gains persist
+across target support and client--stratum shapes on ten shared visit-occupancy
+traces, each with three model seeds. Floor fills the control map's zero masses
+and renormalizes. M1$\mu$/M2$\mu$ use ACS population/NYC~311 shapes on the
+same control keys, rescaled within region to the public $\boldsymbol\mu$.
+These are trained target-map variants; Appendix~\ref{app:cityscanner_sixarm}
+gives their construction and statistical details.
+
+\begin{table*}[t]
+\centering
+\caption{City Scanner visit-occupancy target-map variants.
+Mean $\pm$ SD over ten trace means, each averaging three model seeds.
+Predictions share region weights and a training-standardized scale.
+$\rho$ is the percentage of non-test delivered units assigned zero mass
+(zero with Design off). Group gaps use the common public region target;
+bold marks endpoint minima.}
+\label{tab:cityscanner_sixarm}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr@{}}
+\toprule
+Method / target map & $\rho$ (\%) & $\Delta_{\mathrm{group}}\downarrow$ &
+$\mathrm{RMSE}_{\mu}\downarrow$ & WorstGroupRMSE $\downarrow$\\
+\midrule
+FedAvg / count & 0.00 & $0.1953{\pm}0.0342$ & $\mathbf{0.2409}{\pm}0.0832$ & $\mathbf{0.2529}{\pm}0.0903$\\
+RAVEN-NoDesign & 0.00 & $0.0736{\pm}0.0264$ & $0.2439{\pm}0.0835$ & $0.2575{\pm}0.0905$\\
+RAVEN-control & 14.35 & $0.0706{\pm}0.0266$ & $0.2561{\pm}0.1031$ & $0.2695{\pm}0.1095$\\
+RAVEN-floor & 0.00 & $\mathbf{0.0682}{\pm}0.0313$ & $0.2442{\pm}0.0842$ & $0.2576{\pm}0.0908$\\
+RAVEN-M1$\mu$ & 1.01 & $0.0771{\pm}0.0338$ & $0.2467{\pm}0.0889$ & $0.2609{\pm}0.0971$\\
+RAVEN-M2$\mu$ & 0.98 & $0.0813{\pm}0.0301$ & $0.2508{\pm}0.0907$ & $0.2661{\pm}0.1003$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+Floor, M1$\mu$, and M2$\mu$ each reduce group mismatch versus FedAvg on
+all ten paired traces and pass the three pre-specified structural comparisons
+under the graphical multiplicity allocation (one-sided paired Wilcoxon,
+each $p=9.77\times10^{-4}$). Floor retains $101.9\%$ of the FedAvg-to-control
+group gain. The gains therefore remain observable in these support/shape
+variants; NoDesign also has lower group mismatch than M1$\mu$/M2$\mu$.
+
+For floor/M1$\mu$/M2$\mu$ versus FedAvg, one-sided 95\% prediction upper bounds
+of $3.83/4.14/8.15\%$ exceed the $2\%$ non-inferiority margin;
+the gated superiority tests therefore remain untested. Separately, the primary trace-level
+ratio $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$
+has Hodges--Lehmann estimate $-.019\%$, 95\% percentile trace-cluster interval
+$[-1.89\%,+12.28\%]$, and $p=.922$. Deletion cost remains unresolved;
+floor changes group marginals as well as zero masses. The separate four-contrast
+secondary family has no Holm-significant member. Common-target alignment uses
+group mismatch; client--stratum gaps are arm-specific
+(Table~\ref{tab:cityscanner_sixarm_cs}).
+
+Target-map effects also depend on which groups the support represents.
+In the retrospective comparison (Appendix~\ref{app:cityscanner_phi}), masking
+SensorScope keys gives at most $.175\%$ cost at zero-target share $.388$,
+whereas U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
+The zero-target share alone therefore does not predict cost.
+
+\paragraph{Support and constraint geometry.}
+With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
+In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
+$90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
+windows.  Largest target groups carry only $.53\%/.79\%$.
+Across 3279 evaluated active windows the feasible L1 group-distance range has
+median $10^{-13}$; this does not make the squared L2 term in P2 constant.
+Appendix~\ref{app:arrival_support} separates missing, narrow-range, and
+adjustable target mass on nonempty arrival logs from these formal traces.
+
+Appendix~\ref{app:development_geometry} records three development trajectories
+(seeds 41001--41003, cap $.5$, ESS minimum 3). Their targets and client
+subsets differ from the formal arrival logs in
+Appendix~\ref{app:arrival_support}. For group range
+$W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
+\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
+where $W_{r,g}\ge.01$.
+Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
+composition direction, but only $4.651\%$ mean adjustable target mass.
+References violate constraints in $59.02\%$, with mean projection distance
+$.067487$. The same appendix varies caps and ESS.
+
+\paragraph{Stabilization and reference sensitivity.}
+On observed SensorScope/U-Air client-windows, the $q_{\min}$ floor activates
+in $5.22\%/5.18\%$ and the inverse-usability ceiling in $24.22\%/23.75\%$.
+At true margins on active Design-on support, reference stabilization error
+has median zero and maximum $\ell_1$ values $.553/.680$
+(Table~\ref{tab:app_a5_a6_audit}). The perturbation bound retains this error;
+A6a is sufficient for it to vanish. Shared support/state and A6b remain
+comparison conditions because the saved states omit active-set lists and
+estimated margins. The worst-case Design-on constant $L_\pi\le2\times10^{13}$
+is a loose envelope, rather than a tight numerical prediction of observed error
+(Proposition~\ref{prop:practical_plugin}; Appendix~\ref{app:a5_a6_audit}).
+
+Inside one calibrated member, replacing estimated observation/usability margins
+by truth changes RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and
+$+.040\%$ ($[-.090,+.171]\%$) on U-Air over 20 paired seeds.  Three U-Air
+members stay within $.3\%$, but TwoStage-H\'ajek lies $2.04\%$ above its
+oracle-margin counterpart ($[1.33,2.75]\%$). Reference perturbations
+(median $\ell_1=.077$, maximum $1.15$) can be appreciable even where prediction
+is insensitive.
+
+\paragraph{Prediction sensitivity.}
 For evaluated true-margin configurations, define
 $H=(\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})-\mathrm{RMSE}_{\mu}(\mathrm{oracle}))/
 \mathrm{RMSE}_{\mu}(\mathrm{FedAvg})$.
@@ -1636,36 +1726,6 @@
 $|H|\le.217\%$ with intervals containing zero; $.70$--$.80$ point detection
 leaves the $.5\%$ practical improvement unresolved.  These configurations
 are not optimal upper bounds over all feasible weights.
-
-Inside one calibrated member, replacing estimated observation/usability margins
-by truth changes RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and
-$+.040\%$ ($[-.090,+.171]\%$) on U-Air over 20 paired seeds.  Three U-Air
-members stay within $.3\%$, but TwoStage-H\'ajek lies $2.04\%$ above its
-oracle-margin counterpart ($[1.33,2.75]\%$). Reference perturbations
-(median $\ell_1=.077$, maximum $1.15$) can be appreciable even where prediction
-is insensitive. The support analysis checks true margins on active support and
-records active clipping; missing estimated-margin logs leave A6b unverified
-(Appendix~\ref{app:a5_a6_audit}).
-
-The local-weight analysis finds constant realized weights in the original blocks.
-The within-stratum heterogeneity experiment varies time-tercile covariates at fixed block observation means
-(Table~\ref{tab:f1_mechanism}; Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
-inputs to the correction pathway.
-
-Arrival-weighted validation shifts the reported risk by $-4.11\%$ to
-$-4.12\%$ on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects
-the same configuration on all 20 seeds. In these comparisons, the scoring
-distortion changes reported error more than configuration selection.
-
-With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
-In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
-$90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
-windows.  Largest target groups carry only $.53\%/.79\%$.
-Across 3279 evaluated active windows the feasible L1 group-distance range has
-median $10^{-13}$; this does not make the squared L2 term in P2 constant.
-Weight freedom, composition freedom, and prediction sensitivity are distinct.
-Appendix~\ref{app:arrival_support} separates missing, narrow-range, and
-adjustable target mass on nonempty arrival logs from these formal traces.
 
 \paragraph{Target concentration.}
 Table~\ref{tab:target_concentration} multiplies region1's prior mass by
@@ -1704,54 +1764,13 @@
 practical criterion.  Target dilution alone therefore does not explain the
 small gain of this oracle/update configuration.
 
-Appendix~\ref{app:development_geometry} records three development trajectories
-(seeds 41001--41003, cap $.5$, ESS minimum 3). Their targets and client
-subsets differ from the formal arrival logs in
-Appendix~\ref{app:arrival_support}. For group range
-$W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
-\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
-where $W_{r,g}\ge.01$.
-Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
-composition direction, but only $4.651\%$ mean adjustable target mass.
-References violate constraints in $59.02\%$, with mean projection distance
-$.067487$. The same appendix varies caps and ESS.
-
-Central-delivered Common-NDMF outperforms simple baselines on Traffic/SensorScope,
-not U-Air (development seeds 41001--41003; physical units;
-Appendix~\ref{app:learning_capacity}). Traffic Uniform has not plateaued.
-Table~\ref{tab:trained_rules} isolates aggregation effects.
-
-\subsection{Update-Rule Sensitivity and Coverage Scope}
-\label{subsec:limitations}
-
-On NSW-Traffic (mean $K=12.1$, $15.1\%$ forced-Uniform active windows,
-15 seeds), four federated rules including oracle margins agree within
-$.002\%$ RMSE with the original server step. At 2/20 local steps, FedAvg
-remains $2.8\%$--$3.0\%$ above centralized Adam ($10^{-3}$, 20 minibatches
-of 32), with different optimizers and budgets; federated parameter movement is
-$.26\%$--$.40\%$ of initial norm.
-
-Server-only Adam ($\beta_1=.9$, $\beta_2=.99$, $\tau=10^{-3}$, rate $.003$,
-one update/window) on 15 seeds unused for rate selection gives oracle-margin
-RMSE headroom over FedAvg of $-1.49\%$ ($[-5.42,+1.76]\%$; 80\% MDE
-$5.80\%$), without establishing $.5\%$ equivalence. Mean RMSE is
-$.967/.973$, ranges $[.659,1.572]/[.795,1.459]$, versus the $1.007$ constant
-reference. Oracle weights reduce group/client--stratum mismatch by
-$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$) on these runs.
-
-Window closure determines when messages are aggregated, whereas mixture
-calibration chooses how available client updates are weighted.
-On one previously used Traffic development seed, fixing the rolling release-quality reference
-after warm-up changed 129 of 799 original-trajectory decisions.
-In autonomous runs, the rolling reference
-shortened mean windows by $30.08\%$ while increasing time-averaged composition
-mismatch by $.02584$ (Appendix~\ref{app:release_timing}).
-
-The stress levels lie in the pairwise-LCB barrier region established in
-Appendix~\ref{app:proof_pairwise_lcb}. The coverage-controlled Design variant uses $\mathrm{Design}_t=\mathrm{Gate}_t$,
-unlike the main method's pre-window configuration. Pooled CERTIFIED
-validity is $.959$; U-Air has $.750$ at $a=1$
-(Appendix~\ref{app:certificate_audit}).
+Appendix~\ref{app:learning_capacity} separates learning capacity from aggregation:
+formal station RMSE exceeds training-mean references, while independent development
+validation improves on simple baselines on Traffic/SensorScope, not U-Air.
+Update-rule sensitivities retain separate budgets (Appendix~\ref{app:update_rule_sensitivity}).
+
+Support determines represented group mass; cap and ESS bound its adjustment.
+Weight freedom, composition freedom, and prediction sensitivity remain distinct.
 
 \section{Conclusion}
 \label{sec:conclusion}

```

### appendix.tex

```diff
--- appendix.tex before
+++ appendix.tex after
@@ -1534,6 +1534,7 @@
 
 \section{Coverage Diagnostics under Availability Stress}
 \label{app:certificate_audit}
+\label{subsec:limitations}
 
 Table~\ref{tab:certificate_stress} and Fig.~\ref{fig:certificate_audit}
 evaluate a coverage-controlled Design variant with
@@ -1743,7 +1744,7 @@
 seeds; dropping it only in a sensitivity pass gives $[-2.32\%,+3.53\%]$,
 still inconclusive. All-trace diagnostic power at $2\%$ is $.151$.
 
-\section{Learning Capacity under a Separate Development Protocol}
+\section{Learning Capacity and Update-Rule Sensitivity}
 \label{app:learning_capacity}
 
 Development validation uses seeds 41001--41003, separate from the main test
@@ -1797,6 +1798,35 @@
 SensorScope/U-Air. U-Air Central-all averages $19.5427$ against the spatial
 reference $18.4567$. Traffic Uniform reaches $253.1132$ vehicles/h ($33.70\%$
 improvement) and is still improving $0.914\%$ from passes 100 to 200.
+
+
+\subsection{Formal-Protocol Prediction References}
+\label{app:formal_prediction_references}
+
+The training-mean predictors score $7.647/1.054/1.007$ on
+SensorScope/U-Air/Traffic.  Constants fitted to the scored test labels score
+$2.088/.678/1.007$ and are diagnostic references, not deployable baselines.
+Training/test target means are $.301/7.657$, $0/-.807$, and $0/.003$,
+respectively. Under the Complete-aligned station protocol, model RMSE on
+both SensorScope and U-Air exceeds the corresponding training-mean baseline.
+
+\subsection{Update-Rule Sensitivity}
+\label{app:update_rule_sensitivity}
+
+On NSW-Traffic (mean $K=12.1$, $15.1\%$ forced-Uniform active windows,
+15 seeds), four federated rules including oracle margins agree within
+$.002\%$ RMSE with the original server step. At 2/20 local steps, FedAvg
+remains $2.8\%$--$3.0\%$ above centralized Adam ($10^{-3}$, 20 minibatches
+of 32), with different optimizers and budgets; federated parameter movement is
+$.26\%$--$.40\%$ of initial norm.
+
+Server-only Adam ($\beta_1=.9$, $\beta_2=.99$, $\tau=10^{-3}$, rate $.003$,
+one update/window) on 15 seeds unused for rate selection gives oracle-margin
+RMSE headroom over FedAvg of $-1.49\%$ ($[-5.42,+1.76]\%$; 80\% MDE
+$5.80\%$), without establishing $.5\%$ equivalence. Mean RMSE is
+$.967/.973$, ranges $[.659,1.572]/[.795,1.459]$, versus the $1.007$ constant
+reference. Oracle weights reduce group/client--stratum mismatch by
+$.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$) on these runs.
 
 \section{Instantaneous Arrival-Support Geometry}
 \label{app:arrival_support}

```
