# PAPER_POLISHING_DIFF

回退基线：C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/stepwise_polish_20261029_212935。只还原本轮改动；若已有后续编辑，应按diff合并，不能整篇覆盖。

## 摘要

修改前：

```latex
\begin{abstract}
Mobile crowdsensing completion uses updates selected through sensing opportunities, observation, and delivery. A selection-corrected reference for the deployment target may still be infeasible under the available clients and aggregation constraints of a finite window. RAVEN-MCS addresses this gap by reconstructing reference mass over atomic sensing units and calibrating it into executable client weights. Under weight caps and effective-support constraints, its aggregation program controls departures from the reference while matching deployment-group composition and accounting for accumulated under-service. Correct ideal ratios yield pooled target-moment recovery under compatible support, sequential identification, and cluster regularity. Calibration stability applies to reference perturbations at a fixed window state. In two City Scanner comparisons with real opportunities and controlled delivery, full RAVEN achieves the lowest mean group mismatch among the five methods in each. Reductions relative to TwoStage-H\'ajek, the best group comparator, are $25.8\%$ and $23.3\%$ by ratios of seed means. One protocol controls observation; the other measures it. Matched-support comparisons separate reference-correction and feasible-projection effects, identifying how calibration improves group alignment on the evaluated support.
```

修改后：

```latex
\begin{abstract}
Mobile crowdsensing completion learns from updates selected through sensing opportunities, observation, and delivery. Selection correction can reconstruct a deployment-target reference, yet that reference may remain infeasible for the clients and aggregation constraints of a finite window. RAVEN-MCS bridges this gap in two steps: it reconstructs reference mass over atomic sensing units, then calibrates executable client weights under weight caps and effective-support constraints. The calibration program coordinates reference fidelity with deployment-group composition and accumulated under-service. Our analysis establishes ideal pooled target-moment recovery under compatible support, sequential identification, and cluster regularity, and bounds reference-induced calibration perturbations at a fixed window state. In two City Scanner protocols with real opportunities and controlled delivery, full RAVEN achieves the lowest mean group mismatch among five methods. Relative to TwoStage-H\'ajek, the best group comparator, reductions are 25.8\% and 23.3\% by ratios of seed means. Observation is controlled in one protocol and measured in the other. Matched-support comparisons distinguish reference correction from feasible projection, supporting group-alignment gains within the evaluated support and constraints.
```

## 引言应用与机制概述

修改前：

```latex
City Scanner provides the principal application evidence
(Table~\ref{tab:cityscanner_real}). Full RAVEN has the lowest mean group
mismatch in each five-method comparison. Both protocols use real opportunities
and controlled delivery: visit occupancy controls observation, whereas Pilot~2
measures it. Prediction leaders differ. In controlled station comparisons,
simple reference projection can achieve lower group mismatch and runtime than
full RAVEN (Tables~\ref{tab:main_effectiveness}
and~\ref{tab:trained_rules}).

Matched-support comparisons separate count-weighting effects, reference
correction, and calibration. Uniform explains much of the count-to-RAVEN gain.
SensorScope's independent reference projection improves group mismatch by
$0.768$ pp over Uniform; a separate same-support projected Design-on/off
contrast yields $0.922$ pp. These effects are not additive. Six selection scenarios distinguish target and arrival
risks. Target-support variants retain lower group mismatch than FedAvg on all
ten paired traces (Table~\ref{tab:cityscanner_sixarm}). Geometry distinguishes weight freedom from adjustable group mass,
quantified on formal station traces from arrival logs
(Appendix~\ref{app:arrival_support}).
```

修改后：

```latex
City Scanner provides the principal application evidence
(Table~\ref{tab:cityscanner_real}). Full RAVEN has the lowest mean group
mismatch in each five-method comparison. Both protocols use real opportunities
and controlled delivery; observation is controlled for visit occupancy and
measured for Pilot~2. Prediction leaders differ by protocol.
Matched-support comparisons distinguish count weighting, reference correction,
and feasible projection (Table~\ref{tab:trained_rules}), while selection and
geometry diagnostics explain arrival-risk distortion and available composition
directions (Appendices~\ref{app:e2_layer_matrix} and~\ref{app:arrival_support}).
Target-support variants test whether group alignment persists when target maps
change (Table~\ref{tab:cityscanner_sixarm}).
```

## 三项贡献

修改前：

```latex
Our contributions are:
\begin{enumerate}
    \item \textbf{From reconstructed references to executable aggregation.}
    RAVEN-MCS couples sequential target-reference reconstruction to constrained
    aggregation on the current window's clients, addressing the gap between
    corrected statistical mass and executable weights. Calibration analysis
    bounds sensitivity to the reference, while matched-support comparisons
    distinguish direct-reference, projection, and full-program behavior.

    \item \textbf{Sensing-unit foundations for reconstruction and calibration.}
    We formulate the deployment target and sequential $R/O/U$ arrival law over
    atomic sensing units, with pre-outcome information boundaries for each
    correction. This formulation supports ideal pooled moment recovery and
    separates practical reference error from fixed-window calibration
    sensitivity.

    \item \textbf{Application evidence and attribution of group alignment.}
    Full RAVEN gives the lowest mean group mismatch in each of two
    five-method City Scanner comparisons. Matched-support
    rules and geometry diagnostics explain the distinct roles of reference
    correction, feasible projection, and available composition directions in
    this reference-to-aggregation link.
\end{enumerate}
```

修改后：

```latex
Our contributions are:
\begin{enumerate}
    \item \textbf{Sensing-unit targets and sequential reconstruction.}
    We formulate deployment mass and the $R/O/U$ arrival law over atomic
    sensing units, with pre-outcome information boundaries for each correction.
    This captures within-client selection beyond participation alone and
    supports ideal pooled target-moment recovery (Proposition~\ref{prop:reconstruction}).

    \item \textbf{From reconstructed references to executable aggregation.}
    RAVEN-MCS calibrates the reference on current window support under client
    caps and effective-support constraints, using debt to record under-service.
    The analysis establishes a unique minimizer and fixed-state perturbation
    bounds; long-run alignment requires sublinear debt growth
    (Theorem~\ref{thm:calibration}, Proposition~\ref{prop:practical_plugin}).

    \item \textbf{Application evidence and mechanism attribution.}
    Full RAVEN gives the lowest mean group mismatch in two five-method
    City Scanner comparisons. Matched-support rules separate count-to-Uniform,
    reference-projection, and full-program effects, while geometry identifies
    which composition directions the window can adjust
    (Tables~\ref{tab:cityscanner_real} and~\ref{tab:trained_rules}).
\end{enumerate}
```

## 结论与可用性

修改前：

```latex
\section{Conclusion}
\label{sec:conclusion}

RAVEN-MCS connects sequential sensing-unit reference reconstruction to
executable client mixtures under finite-window constraints. The analysis
separates ideal moment recovery and fixed-window stability from long-run
alignment, which depends on sublinear debt growth. Full RAVEN attains the lowest
mean group mismatch among the five methods in each primary City Scanner
comparison.
Same-support contrasts separate count-to-Uniform effects, reference correction,
and feasible projection. The tested target-support variants also improve group alignment over count
weighting, while geometry distinguishes available weight directions from
adjustable target mass. Prediction leaders
vary by protocol. On SensorScope, full RAVEN improves client--stratum alignment
over projection at higher group mismatch and runtime.

\section*{Data and Code Availability}
The public sources are cited in Table~\ref{tab:datasets}.  T-Drive follows
Microsoft Research terms~\cite{yuan2010tdrive}.  City Scanner
{PM}$_{2.5}$~\cite{wang2023cityscanner} is Zenodo 10.5281/zenodo.7961851,
CC BY 4.0. The locally held reproduction archive contains frozen targets,
selection configurations, EventTraces, paired results, figure/table inputs,
and scoring identities. It includes both five-method City Scanner protocols,
corrected saved-parameter scores for the matched-support weight rules,
target-concentration results, and Adam sensitivity records. For the separate
six-arm target-map comparison, run records, maps, and registered tests are
archived; aggregate summaries and analysis provenance remain outside the
archive, as do the independent learning and geometry records.
```

修改后：

```latex
\section{Conclusion}
\label{sec:conclusion}

RAVEN-MCS connects sequential sensing-unit reference reconstruction to
executable client mixtures under finite-window constraints. Ideal moment
recovery and fixed-window stability support different parts of this connection;
long-run alignment additionally requires sublinear debt growth.
Matched-support comparisons distinguish count-weighting, reference correction,
and calibration, while geometry identifies adjustable target mass.
Full RAVEN attains the lowest mean group mismatch among five methods in each
of two City Scanner protocols. These results support deployment-group alignment
on the evaluated support; prediction rankings remain protocol-dependent.

\section*{Data and Code Availability}
The public sources are cited in Table~\ref{tab:datasets}.  T-Drive follows
Microsoft Research terms~\cite{yuan2010tdrive}.  City Scanner
{PM}$_{2.5}$~\cite{wang2023cityscanner} is Zenodo 10.5281/zenodo.7961851,
CC BY 4.0. A local reproduction bundle is maintained; its contents have not been
verified as a complete package of code, scoring inputs, and summaries for all
reported protocols. No public access link is currently provided.
```

## 证明及版式关键变化

- 四处`proof[Proof sketch]`→正式`proof`，保留论证，延后推导增加带label的完整证明指向。
- 附录原“Proof of …”标题后直接进入推导→先加不计数的完整条件/对象/结论重述，再进入proof，以一个空心框结束。原编号公式用eqref重用；不新编号。
- 覆盖完整证明去掉反复解释无效推断方向的段落，保留“随机秩→事件包含→截断界”的完整链条；非负性和时间边界仍明示。没有把证明改成单句“见附录”。
- 引言.768/.922和SensorScope具体开销去重，原数值/区间仍在原结果节，没有把不同对比相加。
- F1及G5_SOLVER_DIVERGE→层内观测异质性、具体求解差异阈值；10^-4/10^-3不变。
- Table IV/V中的Window后缀改由caption统一定义；数值、行序、方法身份均保持。
- 图一仅缩短caption，素材不变；补充首页移出上传操作指令。没有数据或公式迁移到新增附录。

- 完整逐行差异：[main.tex.diff](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/stepwise_polish_20261029_212935/main.tex.diff)。
- 完整逐行差异：[appendix.tex.diff](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/stepwise_polish_20261029_212935/appendix.tex.diff)。
- 完整逐行差异：[supplemental.tex.diff](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/stepwise_polish_20261029_212935/supplemental.tex.diff)。
