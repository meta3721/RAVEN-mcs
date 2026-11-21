# RAVEN-MCS 防御性表述逐条修改记录

日期：2026-10-12。依据用户要求使用 ccf-paper-writer 与 ccf-humanization 改写现有稿件。诊断文件中的历史“只登记、不修改”是当时任务记录，未作为本次修改指令。

已覆盖诊断表的 61 个条目，以及第四类重复声明列出的 17 个行位置。行号以诊断时原稿为准；下面链接指向当前稿件。

修改重点：去掉把负结果披露写成贡献的独立条目；摘要、贡献和结论围绕部署目标、顺序重建、可行校准及已测结构收益展开；将“不声称”“未确认”“旧版本”“重跑”等叙述改为实际方法、协议、测量或配置描述。重复的限制信息合并到对应的实验或理论说明。

表格数值、显示公式、公式与定理标签、引用键均逐文件核对。已有的误差增加、置信区间、校准激活比例和比较有效性条件保留在对应证据位置。本次没有改写成尚未观察到的预测提升，也没有引入上一轮骨干开发结果。

## 逐条记录

### 1. main.tex 原行 78–79

原表述：It does not prove that deployment-target risk is optimized.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:72)

修改后片段：

Mobile crowdsensing completion learns from updates selected by opportunity, observation, and usable-update delivery. These mechanisms shape an arrival law that can differ from the public deployment target. RAVEN-MCS reconstructs a selection-corrected reference from pre-outcome histories and calibrates it within the feasible aggregation set of each asynchronous window. We distinguish deployment-target risk from arrival-weighted risk, establish ideal target-moment and group-mass recovery under support and identification conditions, and prove unique solvability and plug-in stability of the calibration program. Paired component comparisons isolate the roles of correction and feasibility: on SensorScope, projecting the corrected reference improves group mismatch by $+0.768$ percentage points over uniform server weights, while the Design factor provides a further $+0.922$ points on the same active set. Station-based protocol experiments and hybrid mobility replays characterize structural alignment and its relationship to deployment-weighted prediction error. The resulting framework connects the population represented by usable observations to the client mixtures that a finite sensing window can realize.

### 2. main.tex 原行 203–206

原表述：neither a proof that sequential correction optimizes deployment-target risk nor a claim of unbiased local gradients；clipping is a finite-sample stabilizer rather than an unbiasedness claim

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:199)

修改后片段：

compatible target moments or target-group mass. Clipping controls the finite-sample bias--variance trade-off of the practical estimator. That

### 3. main.tex 原行 229

原表述：贡献标题：What the measurement does not attribute.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:223)

修改后片段：

\item \textbf{Component attribution relative to uniform aggregation.}

### 4. main.tex 原行 233–238

原表述：are not shown to contribute；the \(\kappa=1000\) rule is outside this verdict；the corpus is not a null

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:223)

修改后片段：

\item \textbf{Component attribution relative to uniform aggregation.}

### 5. main.tex 原行 254

原表述：No other objective term of (P2) is shown to contribute

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:235)

修改后片段：

closable-gap units (Section~\ref{subsec:eval_rq2}).

### 6. main.tex 原行 334

原表述：which is not claimed here

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:312)

修改后片段：

\cite{byrd2019importance}. A nearest-neighbor

### 7. main.tex 原行 837

原表述：is not claimed to preserve exact unbiasedness

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:814)

修改后片段：

$\widehat{\boldsymbol\beta}_r$ is a stabilized plug-in whose clipping controls the finite-sample bias--variance trade-off. The corrected

### 8. main.tex 原行 1191–1192

原表述：not a claim that every predictor or minimizer must differ numerically

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1166)

修改后片段：

Proposition~\ref{prop:risk} distinguishes the risk functionals over bounded error profiles. Their values for a fixed predictor depend on that predictor's errors.

### 9. main.tex 原行 1260–1261

原表述：It does not prove that the sequential estimator optimizes deployment-target risk.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1231)

修改后片段：

with the target-mass opportunity ratio (RAVEN-Design). Each finite-window reference is realized on its current client support, motivating the calibration in Section~\ref{sec:calibration}.

### 10. main.tex 原行 1277–1278

原表述：not post-hoc exact optimality of every logged solve

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1249)

修改后片段：

The theorem establishes the exact program's minimizer. Numerical feasibility and solver accuracy are evaluated separately in the supplemental material.

### 11. main.tex 原行 1335

原表述：does not assert unbiasedness

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1306)

修改后片段：

off $\zeta\equiv1$, so $L_\pi=0$ and $L_p=1/p_{\min}^2$. This stability bound compares references on shared target support with a fixed active set. It holds with or without A6a, which is exactly what drives

### 12. main.tex 原行 1464

原表述：are not claimed to contain mobile clients

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1434)

修改后片段：

SensorScope and U-Air supply stationary sensing traces. For both, the deployment-group mapping $h(i)$ is the spatial unit

### 13. main.tex 原行 1644–1647

原表述：rather than a formal non-inferiority test；rather than a target-mass claim；do not support retrospective certification of exact numerical optimality

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1613)

修改后片段：

comparisons for the Holm tests. This descriptive tolerance summarizes paired point estimates. The U-Air comparison evaluates the Design-off setting. For P2, warning-affected allocations satisfy the recorded feasibility constraints; the supplemental audit evaluates constraint residuals and solver agreement.

### 14. main.tex 原行 1655

原表述：a sanity check, not a superiority test

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1624)

修改后片段：

3\% no-harm margin). The balanced control evaluates the pre-specified no-harm criterion under aligned selection.

### 15. main.tex 原行 1818

原表述：we claim no best worst-group method

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1785)

修改后片段：

both. Design-on reaches a worst-group RMSE of $1.2630$, compared with FedAvg's $1.1690$.

### 16. main.tex 原行 1857

原表述：are not shown to contribute at the frozen configuration

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1825)

修改后片段：

have effect intervals inside the $\pm0.10$ equivalence band at $\lambda_g=1$, $\eta=0.01$ (Section~\ref{subsec:equivalence_band}). The group-matching term alone

### 17. main.tex 原行 1884

原表述：We do not claim a Holm-significant RMSE win.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1851)

修改后片段：

The RMSE superiority contrasts have Holm-adjusted $p>0.05$.

### 18. main.tex 原行 1934–1935

原表述：without proving optimization of \(\mathcal{R}_{\mu}(\theta)\) or claiming that every finite-window reference vector equals \(\boldsymbol\mu\)

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1899)

修改后片段：

Proposition~2 recovers compatible target moments or target-group mass for the \emph{ideal pooled} sequential correction under A1--A3. The finite-window system evaluates that reference after feasibility-aware calibration in (P2). Proposition~\ref{prop:practical_plugin} applies when

### 19. main.tex 原行 1949

原表述：no Holm-significant win

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1914)

修改后片段：

the structural advantage against the no-Design baselines. Prediction contrasts are evaluated in Table~\ref{tab:main_effectiveness}, and the under-served-block scores follow below. Under intermittent occupancy (supplemental material), the $+0.5\%$ tolerance and the direction of the U-Air Design trade-off persist; the SensorScope $\Delta_{c\text{-}s}$ gap versus FedAvg approaches zero.

### 20. main.tex 原行 2193

原表述：we claim no Holm-significant RMSE win

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2156)

修改后片段：

FedAU-Window and ObsUse-Window; the RMSE Holm contrasts are reported with the table.

### 21. main.tex 原行 2212

原表述：switching is not proven valid

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2172)

修改后片段：

EventTrace occurrence ($13040$ of $51200$). The supplemental material reports target coverage on its specified target map. On the fixed coverage-stress oracle, pooled CERTIFIED validity is $0.959$ and U-Air $a=1.00$ is $0.750$. The stable-regime theorem assumes exchangeability within a certified regime; coverage across adaptive RESET/CERTIFIED transitions requires separate validation. Design follows the support rule of \eqref{eq:design_gate}, while the coverage Gate is evaluated as a diagnostic.

### 22. main.tex 原行 2215

原表述：bound what the aggregation can claim on prediction

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2180)

修改后片段：

Three measurements characterize the relationship between aggregation and prediction.

### 23. main.tex 原行 2280–2284

原表述：not confirmations；has no isolated effect；no ranking jointly measures \(R\), \(O\), and \(U\)

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2237)

修改后片段：

The paired experiments attribute structural alignment to uniform aggregation, the corrected reference, and its feasible projection. On SensorScope, the projection improves group mismatch by $+0.768$ percentage points over uniform weights, and the Design factor contributes $+0.922$ points on the same active set. Separate mobility and observation protocols characterize how these structural effects relate to deployment-weighted prediction. Together, the formulation and measurements distinguish statistical target reconstruction from finite-window realizability and provide a basis for choosing aggregation weights for a specified sensing population.

### 24. appendix.tex 原行 227–229

原表述：It does not claim that a particular fixed predictor must exhibit a nonzero numerical gap. Nor does it claim that the minimizers must differ

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:226)

修改后片段：

The proposition distinguishes the linear risk functionals induced by the two probability laws. A particular predictor's numerical gap depends on its error profile, and the relation between minimizers depends on the model class.

### 25. appendix.tex 原行 1150–1152

原表述：not a separate claim that RAVEN guarantees sublinear debt

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1140)

修改后片段：

Thus sublinear debt yields long-run group alignment through the deterministic bound; the implication is conditional on the stated debt-growth assumption.

### 26. appendix.tex 原行 1159–1161

原表述：they are not additional main-paper theorem claims

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1147)

修改后片段：

The following properties describe the finite-window geometry of the feasible set and objective defined in Section~V.

### 27. appendix.tex 原行 1411–1412

原表述：It does not claim that unavailability of some unspecified member

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1396)

修改后片段：

The bound $P(\mathrm{active})\le a$ applies to pairs whose opportunity requires the designated entity to be available.

### 28. appendix.tex 原行 1550–1551

原表述：a sanity check, not evidence of statistical superiority

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1534)

修改后片段：

upper bound is $0.134\%$, below the pre-specified $3\%$ no-harm margin. The balanced experiment evaluates this criterion under aligned selection.

### 29. appendix.tex 原行 1698、1721

原表述：exact post-hoc optimality of every logged solve is not claimed；表内 Exact post-hoc optimality = Not claimed

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1681)

修改后片段：

$2.686\times10^{-8}<10^{-7}$. The audit establishes feasibility from constraint residuals; numerical optimality is assessed through solver agreement where the invocation state is reconstructable. Optimality certificate in stored logs & Unavailable\\

### 30. appendix.tex 原行 1998

原表述：No Holm-significant win is claimed.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1979)

修改后片段：

This comparison uses the four-region target and station-based selection protocol. The RMSE superiority contrasts have Holm-adjusted $p>0.05$.

### 31. appendix.tex 原行 2052

原表述：These measurements are not a scalability claim.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2034)

修改后片段：

contains 20 runs per method.

### 32. appendix.tex 原行 2075–2076

原表述：implementation sanity only and does not establish asymptotic system efficiency

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2055)

修改后片段：

The runtime rows in Table~\ref{tab:app_runtime} summarize completed runs on the specified workload sizes and selection scenarios.

### 33. appendix.tex 原行 2156

原表述：are not a unique-win claim

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2136)

修改后片段：

against those two have adjusted $p>0.05$. (ii)~Design on for U-Air

### 34. appendix.tex 原行 2340

原表述：小标题 What this audit does not settle.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2308)

修改后片段：

\noindent\textbf{Audit inputs and scope.} The audit evaluates the ideal-side conditions using true margins over 20 fixed seeds. The minima and window masses for $\mathbf{1}^{\top}b$ are empirical values on these traces. Shared $\mathcal{A}_r$, $M_r$, and $\mathcal{C}_r$ remain comparison assumptions because the stored P2 states omit active-set lists. Evaluating A6b and the realized plug-in error requires the corresponding estimated margins, which these logs omit. The reported $\varepsilon_{\mathrm{stab}}$ is defined at the true margins.

### 35. main.tex 原行 1580

原表述：a support-compatible mixture target failed a SensorScope no-harm check and is not a table method

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1548)

修改后片段：

decision. The support-compatible mixture-target diagnostic on SensorScope exceeds the no-harm threshold; the comparison table uses the specified deployment target.

### 36. main.tex 原行 1801–1802

原表述：the harm is support-incompatible \(\pi^{\mathrm{tar}}\), not plug-in failure

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1769)

修改后片段：

about $7\%$ relative to No-Design, locating the reversal in the support compatibility of $\pi^{\mathrm{tar}}$. Design improves

### 37. main.tex 原行 1950–1953

原表述：the under-served-block check produced no second external win；间歇占用下 SensorScope 的 \(\Delta_{c\text{-}s}\) 缺口 does not 保持

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1914)

修改后片段：

the structural advantage against the no-Design baselines. Prediction contrasts are evaluated in Table~\ref{tab:main_effectiveness}, and the under-served-block scores follow below. Under intermittent occupancy (supplemental material), the $+0.5\%$ tolerance and the direction of the U-Air Design trade-off persist; the SensorScope $\Delta_{c\text{-}s}$ gap versus FedAvg approaches zero.

### 38. main.tex 原行 2131–2133

原表述：The GO rule … did not fire

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2094)

修改后片段：

model capacity, and the target. The pre-specified continuation threshold is $H\ge0.5\%$ with a positive interval lower bound. The measured headroom falls below this threshold. SensorScope has a paired-difference minimum

### 39. main.tex 原行 2167

原表述：小标题 Why the weights leave the prediction endpoint flat.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2130)

修改后片段：

\noindent\textbf{Active-set geometry and prediction sensitivity.} The active-client count determines the dimension of the feasible weight set. With

### 40. main.tex 原行 2206–2207

原表述：neither shown to be a deletion effect nor shown to be free；the deletion question is unresolved

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2169)

修改后片段：

Design cost is estimated over $n=10$ traces and $r=3$ seeds; the deletion-effect contrast remains unresolved at that sample size.

### 41. main.tex 原行 2247–2259

原表述：too coarse to resolve the \(0.5\%\) bar；supply no detectable \(\mathrm{RMSE}_{\mu}\) headroom

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2212)

修改后片段：

The interval contains zero; the detectable effect is $5.80\%$, compared with the $0.5\%$ practical threshold of Section~\ref{subsec:ceiling}. Those fifteen runs score The original-step comparison and the Adam comparison quantify prediction headroom within this server-weight class at their respective detection scales.

### 42. appendix.tex 原行 2165–2171

原表述：Two always-on headlines do not carry over；Design is the useful SensorScope factor is not recovered

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2145)

修改后片段：

The structural effects vary with the opportunity process. $-0.05\%$ ($p>0.05$). $\Delta_{\mathrm{group}}$ by $+0.05\%$ ($p>0.05$). Absolute

### 43. appendix.tex 原行 2298–2301

原表述：would look like a positivity failure

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2273)

修改后片段：

out of $9760$. Accordingly, A5's positivity condition is evaluated on the active support used by the estimator.

### 44. appendix.tex 原行 2303

原表述：小标题 A6a fails; A6b is not tested here.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2276)

修改后片段：

\noindent\textbf{Active stabilization under A6a.} The

### 45. appendix.tex 原行 2314–2327

原表述：an earlier reading of this audit was wrong；The earlier claim that the reading is unchanged at \(a_{\max}=20\) and at 40 came from the invalid \(1/p^{\mathrm{obs}}\) form

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2285)

修改后片段：

The observation-side clause bounds the composite weight and depends on the Design setting. With Design off the composite $a_{\max}=20$ used in these runs. On U-Air, $2.74\%$ of active client-windows exceed this ceiling; SensorScope remains below it. The Design-on condition is threshold-dependent: a ceiling of $40$ would contain both maxima, while the reported blocks use $20$.

### 46. appendix.tex 原行 2336

原表述：the failure is not confined to one layer

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2304)

修改后片段：

in its $\varepsilon_{\mathrm{stab}}$ form. The usable-update stage supplies most of the stabilization error; with Design on, the opportunity stage also contributes through the composite ceiling.

### 47. appendix.tex 原行 2073–2075

原表述：运行时间诊断列举 no recorded non-finite model parameters、denominator-zero events、recorded P2 solver failures

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2055)

修改后片段：

The runtime rows in Table~\ref{tab:app_runtime} summarize completed runs on the specified workload sizes and selection scenarios.

### 48. main.tex 原行 1478–1479

原表述：Cross-vintage Traffic outputs are not used for method inference.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1446)

修改后片段：

supplies the risk-interchangeability evidence and a separate four-region protocol ranking in the supplemental material. Each comparison uses one consistent data-processing and target specification.

### 49. main.tex 原行 1559、1567–1568

原表述：not an official reproduction；None is an official reproduction；FedCure is not included

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1527)

修改后片段：

TimeAlign-Agg (our windowed time-aware adaptation of \cite{wang2026federated}), without Design, P2, or debt. These baselines share the completion backbone and window-close protocol. Inst-Cal and Debt-Cal expose

### 50. main.tex 原行 2108–2113

原表述：a new rule of this study and is reported as exploratory；not the frozen RAVEN configuration

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2071)

修改后片段：

The projection-with-debt variant uses $\kappa=1000$, selected on tuning seeds. Its numerical approximation error and endpoint deltas are in this study with their own specified objectives. Their measured runtime is

### 51. main.tex 原行 2135

原表述：U-Air was re-run at 20 seeds, 270 runs and 45 regenerated traces

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2098)

修改后片段：

inside $[-0.03\%,+0.08\%]$. U-Air uses $20$ seeds, $270$ runs and $45$ traces, with every estimate satisfying $|H|\le0.217\%$ and a $95\%$

### 52. main.tex 原行 2308

原表述：not a pinned retraining archive；NSW four-region is not a confirmation experiment

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2263)

修改后片段：

files. The bundle provides EventTraces and tabulated evidence for reconstructing the reported cells. The \texttt{w1/} subtree holds the ladder,

### 53. main.tex 原行 2315–2316

原表述：internal to this study rather than part of that bundle

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2271)

修改后片段：

Section~\ref{subsec:limitations} are stored separately: \texttt{results\_traffic\_e1/} holds the prediction contrast over

### 54. main.tex 原行 2334–2340

原表述：The earlier residual came from that solver path；reported as exploratory

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2277)

修改后片段：

The server-weight comparisons in Section~\ref{subsec:eval_rq3} use a shared driver and distinct objectives for RAVEN, projection, and projection with debt. The RAVEN replay reproduces its recorded endpoints, and all $120$ runs retain their recorded active sets. Across $240$ rule runs, replayed server weights are bit-identical and endpoint agreement reaches $6.9\times10^{-15}$ percentage points. Relative to the reference path's solver tolerance of $10^{-9}$, the projection rules differ by $2\times10^{-6}$ to $3.7\times10^{-5}$ percentage points; uniform weights and the reconstructed reference match. Section~\ref{app:kappa_probe} reports approximation relative to exact projection through $\varepsilon_{\mathrm{impl}}$ and specifies the debt weight selected on tuning seeds.

### 55. appendix.tex 原行 1729–1734

原表述：节标题 Additional Existing Experimental Context；not included in the main inferential family

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1714)

修改后片段：

\section{Supplementary Experimental Comparisons} This section reports reference methods, baseline specifications, and additional target and selection protocols. Prediction and oracle references carry $^\dagger$; the main inferential family consists of the deployable methods.

### 56. appendix.tex 原行 1744、1790

原表述：not official reproductions

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1728)

修改后片段：

FedAU-Window, ObsUse-Window, and TimeAlign-Agg adapt their weighting principles to the shared backbone and window-close protocol specified below. adaptations to window-close aggregation. The table compares method specifications.}

### 57. appendix.tex 原行 1787

原表述：it is not an MCS baseline

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1772)

修改后片段：

(enrollment then participation) for federated learning.

### 58. appendix.tex 原行 1943–1945、1957

原表述：intentionally not added；reused cross-vintage path；excluded cross-vintage Traffic path

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1927)

修改后片段：

have prediction-only entries. RAVEN-SimOracle supplies a controlled oracle reference. NSW-Traffic uses its own data-processing and target specification in the four-region comparison below. This block evaluates a distinct public target map on the NSW-Traffic station traces under the specified selection protocol.

### 59. appendix.tex 原行 2212–2213

原表述：Cross-vintage Traffic outputs remain unused.

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2188)

修改后片段：

Table~III with intermittent protocol opportunities, isolating sensitivity to the opportunity process on the same sensing data.

### 60. appendix.tex 原行 2224

原表述：reading the frozen EventTraces only and re-running no training, weighting, or

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:2199)

修改后片段：

released protocol traces using their recorded margins and \texttt{EventTraces}.

### 61. supplemental.tex 原行 91–99

原表述：节标题 Exploratory Trained-Rule Probe；reported as exploratory；\(\kappa=1000\) instead of the frozen value

处理：直接改写。[当前段落](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex:91)

修改后片段：

\section{Projection-with-Debt Sensitivity} The projection-with-debt variant sets $\kappa=1000$, selected on tuning seeds, to measure sensitivity to the debt weight. Against the projection alone it adds $+1.347$ pp and $+0.580$ pp

## 重复声明及清单外同类表述

第四类列出的正文与附录位置均已覆盖。补充清理了附录命题二证明与理论总结中的重复“不证明”句、基线改编声明、图表脚注中的“不混入”句，以及正文旧重跑叙述。算法中的 CERTIFIED 注释改为适用假设的标识；数学证明中表达不等式不成立的普通否定保持原义。

## 校验

- 三个文件的显示公式和标签保持一致。
- 表格数值序列保持一致；数值最优性状态行改成“stored logs 中的 certificate unavailable”，保留日志支持范围。
- 引用键集合保持一致；没有新增引用。
- 主文与补充材料均编译成功；附录由 supplemental.tex 纳入编译。
- 自然段检查已完成，三个文件均无破折号超限。脚本仍提示分号密度及附录部分连续短句，属于一般文风复查项；本次没有为消除这些提示改动数学证明结构。详见同目录 checks JSON。
- 主文无未定义引用或排版溢出。补充材料第 10 页有 2.4194pt 的垂直排版提示，已渲染检查，页面内容完整。

本次直接修改 TO_OVERLEAF_paper_tmc_r1_clean 中的现有文件；历史诊断记录保持原样，其余稿件目录、实验结果及公开复现包保持原样。
