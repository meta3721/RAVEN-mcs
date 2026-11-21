# 最终叙事修改前后对照

日期：2026-10-31。以本轮修改前归档为基准，未回退用户已有修改。仅规范main.tex与appendix.tex发生文本变化；两份PDF及编译派生文件随之更新。摘要169→169词，引言481→481词，正文/补充14/14→14/14页。

以下为代表性差异，完整局部unified diff保存在`C:/Cursor/raven.mcs/tmp/final_narrative_20261031/main.tex.diff`和`appendix.tex.diff`；逐项证据与未闭合事项见FINAL_NARRATIVE_POLISHING_REPORT.md。实验数据、表格数值单元、数学程序与正式证明不变。

## 第10项 · main.tex

修改前：

```latex
Mobile crowdsensing completion learns from updates selected through sensing opportunities, observation, and delivery. Selection correction can reconstruct a deployment-target reference, yet that reference may remain infeasible for the clients and aggregation constraints of a finite window. RAVEN-MCS bridges this gap in two steps: it reconstructs reference mass over atomic sensing units, then calibrates executable client weights under weight caps and effective-support constraints. The calibration program coordinates reference fidelity with deployment-group composition and accumulated under-service. Our analysis establishes ideal pooled target-moment recovery under compatible support, sequential identification, and cluster regularity, and bounds reference-induced calibration perturbations at a fixed window state. In two City Scanner protocols with real opportunities and controlled delivery, full RAVEN achieves the lowest mean group mismatch among five methods. Relative to TwoStage-H\'ajek, the best group comparator, reductions are 25.8\% and 23.3\% by ratios of seed means. Observation is controlled in one protocol and measured in the other. Matched-support comparisons distinguish reference correction from feasible projection, supporting group-alignment gains within the evaluated support and constraints.
```

修改后：

```latex
Mobile crowdsensing completion reconstructs sparse urban fields from distributed sensor observations. Sequential selection changes their represented population, while finite windows can make a corrected deployment reference infeasible for available clients. Participation correction and target-aware aggregation address population composition but leave sensing-unit reconstruction disconnected from constrained window execution. We propose RAVEN-MCS to convert reconstructed target references into executable client mixtures. Opportunity and observation correction jointly supply normalized local training weights and client masses, which usability correction rescales into a server reference. Calibration coordinates reference fidelity, deployment-group composition, and accumulated under-service under weight caps and effective-support constraints. Analysis establishes ideal pooled moment recovery under correct ratios, compatible support, sequential identification and cluster regularity, and calibration stability at a fixed window state under strong convexity conditions. Across two City Scanner protocols with real opportunities, controlled delivery, and controlled or measured observation, RAVEN achieves the lowest mean group mismatch among five methods, reducing it by 25.8\% and 23.3\% relative to TwoStage-H\'ajek, the best group comparator, by ratios of seed means.
```

## 第11项 · main.tex

修改前：

```latex
Although asynchronous learning accommodates irregular updates~\cite{xie2019asynchronous}, participation correction
```

修改后：

```latex
Asynchronous learning accommodates irregular updates~\cite{xie2019asynchronous}, and participation correction
```

## 第8项 · main.tex

修改前：

```latex
Reweighting cannot create missing sensing support or ensure exact target matching.
```

修改后：

```latex
Calibration operates within the group compositions achievable on current sensing support.
```

## 第1项 · appendix.tex

修改前：

```latex
$q_{\min}$ floor inactive
```

修改后：

```latex
$q_{\min}$ floor activation
```

## 第1项 · appendix.tex

修改前：

```latex
$d_{\max}$ ceiling inactive
```

修改后：

```latex
$d_{\max}$ ceiling activation
```

## 第2项 · appendix.tex

修改前：

```latex
$\min_r \mathbf{1}^{\top}b>0$
```

修改后：

```latex
Obs./use mass minimum
```

## 第2项 · appendix.tex

修改前：

```latex
\noindent\textbf{A5 holds.}  The opportunity and observation margins are
strictly positive everywhere in the traces, and the usable-update margin is
strictly positive on every client-window that actually enters the estimator.
The smallest observed usable margin is $5.5\times10^{-3}$, no observed
client-window has a vanishing usable margin, and the smallest window-level
H\'ajek mass is $5.521$ on SensorScope and $16.89$ on U-Air.  The positivity
and normalization steps of Proposition~2 and the denominator in
\eqref{eq:beta_ref} are therefore not degenerate on these traces.
```

修改后：

```latex
\noindent\textbf{Positive margins and recorded mass.} Opportunity and observation
margins are positive throughout the traces; the smallest observed usable margin
is $5.5\times10^{-3}$. The recorded observation/usability-weighted window mass
has minima $5.521$ on SensorScope and $16.89$ on U-Air. This statistic precedes
opportunity correction and therefore describes a different normalization mass
from the full Design-on reference in \eqref{eq:beta_ref}.
```

## 第3项 · appendix.tex

修改前：

```latex
there; $\varepsilon_{\mathrm{stab},r}=0$ also needs A6a. The readings below
use recorded margins on the released traces.
```

修改后：

```latex
there. A6a is sufficient for $\varepsilon_{\mathrm{stab},r}=0$, but is not
necessary when normalization cancels distortions. The statistics below use
recorded margins on the selection traces.
```

## 第4项 · appendix.tex

修改前：

```latex
$d_{\max}=10$. Those are the \texttt{build\_full\_runner} defaults;
\texttt{run\_e3\_real} does not override them. $a_{\max}=40$ belongs to the
E1-R2 weight-safety calibration and the E2 traffic runner, not these blocks.
Each entry is the decisive cell, because one violation settles a bound.
```

修改后：

```latex
$d_{\max}=10$. These constants define the station-trace comparison analyzed here.
```

## 第5项 · appendix.tex

修改前：

```latex
Local-Hajek provenance audit.
```

修改后：

```latex
Within-client weight constancy.
```

## 第6项 · appendix.tex

修改前：

```latex
evaluate the historical coverage-controlled candidate
$\mathrm{Design}_t=\mathrm{Gate}_t$, separately from configured Design.
Pooled CERTIFIED validity is $0.959$ with zero false-safe openings;
these empirical rates do not establish validity of adaptive RESET/CERTIFIED switching.
```

修改后：

```latex
evaluate a coverage-controlled Design variant with
$\mathrm{Design}_t=\mathrm{Gate}_t$, rather than the main method's pre-window
Design configuration and diagnostic-only Gate. Pooled CERTIFIED validity is
$0.959$ with zero false-safe openings. The stable-block guarantee in
Section~\ref{subsec:agg_coverage_theory} assumes score exchangeability.
```

## 第7项 · appendix.tex

修改前：

```latex
allocation and does not move the main-comparison or worst-group headlines.
```

修改后：

```latex
allocation.
```

## 第7项 · appendix.tex

修改前：

```latex
contrasts. Point-level optimality checks do not all pass; endpoint agreement
is not certification.
```

修改后：

```latex
contrasts. Primal residuals reach $6.66\times10^{-16}$ against tolerance
$10^{-13}$, while stationarity residuals reach $.667$ against $10^{-12}$.
Comparator objective gaps exceed $10^{-12}$ in 7 of 200 sampled windows,
with maximum $9.64\times10^{-12}$. These diagnostics separate numerical
feasibility and endpoint agreement from exact optimality.
```

## 第7项 · appendix.tex

修改前：

```latex
The Design ablation in Section~\ref{subsec:eval_rq3} exhibits an endpoint
trade-off on U-Air.  A paired-window provenance audit covers
774 windows.  Opportunity, observation, usable-update, and
registration hashes are identical between full RAVEN and w/o-Design throughout
the audited set.  Differences first arise from the positive design-weight/P2
support induced after the Design ratio is removed.  This confirms that the
ablation effect is a weight-support consequence of the intended intervention,
not selection-trace leakage.
```

修改后：

```latex
The Design ablation in Section~\ref{subsec:eval_rq3} exhibits an endpoint
trade-off on U-Air. Across 774 paired windows, full RAVEN and w/o-Design share
opportunity, observation, usable-update, and registration events. Removing the
Design ratio changes positive-mass P2 support, so the end-to-end contrast
includes support changes as well as weight changes.
```

## 第9项 · main.tex

修改前：

```latex
Prediction scores use saved model parameters with the terminal-window correction.
```

修改后：

```latex
Prediction uses the common saved-parameter scoring rule defined above.
```

## 第12项 · main.tex

修改前：

```latex
CC BY 4.0. A local reproduction bundle is maintained; its contents have not been
verified as a complete package of code, scoring inputs, and summaries for all
reported protocols. No public access link is currently provided.
```

修改后：

```latex
CC BY 4.0. Author-held materials include selection configurations, target maps,
event traces, City Scanner result summaries, and matched-support scoring inputs.
These materials are retained locally and are not publicly released.
```

## 第13项 · main.tex

修改前：

```latex
within it, as specified in Section~\ref{subsec:agg_certificate_alg}.
```

修改后：

```latex
within it, as specified in Section~\ref{subsec:global_update}.
```

## 第13项 · appendix.tex

修改前：

```latex
under the balanced
Balanced control.
```

修改后：

```latex
under the balanced
control.
```

## 第13项 · appendix.tex

修改前：

```latex
The fixed reference $c_{\mathrm{ref}}=.9168365859958755$ uses the $t=20$
release's $\ell=.9069767441860466$ and $a=.4929920904914447$.
```

修改后：

```latex
The fixed reference $c_{\mathrm{ref}}\approx.916837$ uses the $t=20$
release's $\ell\approx.906977$ and $a\approx.492992$.
```

## 访问状态的最终用语

复现材料段落最后一句为：`These materials are retained locally; no public access link is provided.` 不凭本地未见链接推断全球没有公开版本，也不承诺公开完整复现包。

## 恢复入口

`C:/Cursor/raven.mcs/ccf-review-report/backups/final_narrative_20261031_090533.zip`。无后续改动时，仅恢复本轮改动的main.tex和appendix.tex，以及需要回退的两份PDF；有后续改动时，对照上述diff逐块逆向合并。保留旧实验、原停止报告和其他AI修改。
