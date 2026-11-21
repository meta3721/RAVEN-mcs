# 诊断记录：Significance 读法，以及正文里的负面表述

日期：2026-10-11。稿件 `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`、`appendix.tex`、`supplemental.tex`。行号是当天读到的位置。本记录只登记，不改正文，不改审稿分数。

用户要求先看 Significance，并明确不把“预测零结果”再写成一条贡献。随后要求把 “we don't claim”、失败实验、旧版本这一类负面表述全部找出来。定理里用来界定公式的普通否定（例如“当前窗口可以不等于目标”）没有收入。

## Significance

审稿 `ccfa-review-reports/raven-mcs-tmc-review.md`（2026-10-10）给 Significance 2。决定轴之一是这一分。Originality 是另一条轴，当时是 3。审稿写明补一条引用不改变 Originality。FedPALS 那句已经写明匹配步骤相同、对象换成部署组组成。

引言要求读者接受的问题是：到达更新的分布和部署目标不同，按到达律训练会优化错的人群风险。测量交出来的正结果是组质量失配。

1. 方法特有的结构余量。FedAvg 到 RAVEN 的组缺口在 SensorScope 是 2.09 个百分点，其中 1.44 个百分点（68.96%）由均匀服务器权重单独补上，校正后的参考占 0.65 个百分点（31.04%）。投影相对均匀权重是 +0.768 个百分点，区间 [0.563, 0.970]，过了正文自己的 0.5 个百分点实用线。U-Air 同一投影是 +0.286 个百分点，区间 [0.098, 0.471]，低于这条线，两个种子半段是 +0.170 和 +0.402。债务、组匹配、方差、陈旧项落在 ±0.10 等价带里。
2. 部署目标误差。SensorScope 可恢复余量落在 [−0.03%, +0.08%]，最小可检出效应 0.17–0.36 个百分点，预先登记的 \(H\ge 0.5\%\) 没有触发。U-Air 上 \(|H|\le 0.217\%\)。NSW-Traffic 换成 Adam 之后，oracle-margin 相对窗口 FedAvg 是 −1.49%，区间 [−5.42%, +1.76%] 含 0，80% 最小可检出效应 5.80%。\(\Delta_{\mathrm{group}}\) 降 0.0079、\(\Delta_{c\text{-}s}\) 降 0.0099 是预测对比之后才计的。U-Air 打开 Design 使客户–层失配改善 4.990%，同时 \(\mathrm{RMSE}_{\mu}\) 付出 6.885%，最差组相对 FedAU-Window / ObsUse-Window 是 +7.9% 和 +8.0%。T-Drive 上 FedAU-Window 和 ObsUse-Window 排在前面。服务器权重重训后，组失配排序和 \(\mathrm{RMSE}_{\mu}\) 排序不一致，预测对比没有 Holm 显著项。
3. 贡献范围。贡献列表前三条仍是部署目标风险、三层重建和窗口内校准。摘要和后两条贡献把可用结论收成投影。审稿的 2→3 条件是：引言要求读者带走的范围等于测量能支撑的范围。用户 2026-10-11 拒绝再写一条预测零结果。

抬这一分的两条已关闭路线：不为 Significance 启动集中目标的正式重训；不加种子去打 0.5%。NSW 四段目标是均匀的。T-Drive 四段目标 top-1 是 51.4%，那里不是 RAVEN 的 RMSE 胜利。

## 检索范围

在三个 tex 里检索 claim、fail、previous、earlier、exploratory、sanity、not mixed、not a confirmation、cross-vintage、official reproduction。下面按三类列出。同一事实在摘要、贡献、实验、局限、结论里重复出现的，每处都保留。

## 一、明确的“不声称”

| 位置 | 原文 |
|---|---|
| `main.tex` 78–79 | It does not prove that deployment-target risk is optimized. |
| `main.tex` 203–206 | neither a proof that sequential correction optimizes deployment-target risk nor a claim of unbiased local gradients；clipping is a finite-sample stabilizer rather than an unbiasedness claim |
| `main.tex` 229 | 贡献标题：What the measurement does not attribute. |
| `main.tex` 233–238 | are not shown to contribute；the \(\kappa=1000\) rule is outside this verdict；the corpus is not a null |
| `main.tex` 254 | No other objective term of (P2) is shown to contribute |
| `main.tex` 334 | which is not claimed here |
| `main.tex` 837 | is not claimed to preserve exact unbiasedness |
| `main.tex` 1191–1192 | not a claim that every predictor or minimizer must differ numerically |
| `main.tex` 1260–1261 | It does not prove that the sequential estimator optimizes deployment-target risk. |
| `main.tex` 1277–1278 | not post-hoc exact optimality of every logged solve |
| `main.tex` 1335 | does not assert unbiasedness |
| `main.tex` 1464 | are not claimed to contain mobile clients |
| `main.tex` 1644–1647 | rather than a formal non-inferiority test；rather than a target-mass claim；do not support retrospective certification of exact numerical optimality |
| `main.tex` 1655 | a sanity check, not a superiority test |
| `main.tex` 1818 | we claim no best worst-group method |
| `main.tex` 1857 | are not shown to contribute at the frozen configuration |
| `main.tex` 1884 | We do not claim a Holm-significant RMSE win. |
| `main.tex` 1934–1935 | without proving optimization of \(\mathcal{R}_{\mu}(\theta)\) or claiming that every finite-window reference vector equals \(\boldsymbol\mu\) |
| `main.tex` 1949 | no Holm-significant win |
| `main.tex` 2193 | we claim no Holm-significant RMSE win |
| `main.tex` 2212 | switching is not proven valid |
| `main.tex` 2215 | bound what the aggregation can claim on prediction |
| `main.tex` 2280–2284 | not confirmations；has no isolated effect；no ranking jointly measures \(R\), \(O\), and \(U\) |
| `appendix.tex` 227–229 | It does not claim that a particular fixed predictor must exhibit a nonzero numerical gap. Nor does it claim that the minimizers must differ |
| `appendix.tex` 1150–1152 | not a separate claim that RAVEN guarantees sublinear debt |
| `appendix.tex` 1159–1161 | they are not additional main-paper theorem claims |
| `appendix.tex` 1411–1412 | It does not claim that unavailability of some unspecified member |
| `appendix.tex` 1550–1551 | a sanity check, not evidence of statistical superiority |
| `appendix.tex` 1698、1721 | exact post-hoc optimality of every logged solve is not claimed；表内 Exact post-hoc optimality = Not claimed |
| `appendix.tex` 1998 | No Holm-significant win is claimed. |
| `appendix.tex` 2052 | These measurements are not a scalability claim. |
| `appendix.tex` 2075–2076 | implementation sanity only and does not establish asymptotic system efficiency |
| `appendix.tex` 2156 | are not a unique-win claim |
| `appendix.tex` 2340 | 小标题 What this audit does not settle. |

“不证明优化了部署风险”在摘要、贡献 2、命题 2 之后、实验解读、结论各出现一次。

## 二、失败实验、未触发、被否定的旧读法

| 位置 | 原文 |
|---|---|
| `main.tex` 1580 | a support-compatible mixture target failed a SensorScope no-harm check and is not a table method |
| `main.tex` 1801–1802 | the harm is support-incompatible \(\pi^{\mathrm{tar}}\), not plug-in failure |
| `main.tex` 1950–1953 | the under-served-block check produced no second external win；间歇占用下 SensorScope 的 \(\Delta_{c\text{-}s}\) 缺口 does not 保持 |
| `main.tex` 2131–2133 | The GO rule … did not fire |
| `main.tex` 2167 | 小标题 Why the weights leave the prediction endpoint flat. |
| `main.tex` 2206–2207 | neither shown to be a deletion effect nor shown to be free；the deletion question is unresolved |
| `main.tex` 2247–2259 | too coarse to resolve the \(0.5\%\) bar；supply no detectable \(\mathrm{RMSE}_{\mu}\) headroom |
| `appendix.tex` 2165–2171 | Two always-on headlines do not carry over；Design is the useful SensorScope factor is not recovered |
| `appendix.tex` 2298–2301 | would look like a positivity failure |
| `appendix.tex` 2303 | 小标题 A6a fails; A6b is not tested here. |
| `appendix.tex` 2314–2327 | an earlier reading of this audit was wrong；The earlier claim that the reading is unchanged at \(a_{\max}=20\) and at 40 came from the invalid \(1/p^{\mathrm{obs}}\) form |
| `appendix.tex` 2336 | the failure is not confined to one layer |
| `appendix.tex` 2073–2075 | 运行时间诊断列举 no recorded non-finite model parameters、denominator-zero events、recorded P2 solver failures |

## 三、旧版本、重跑、探索性、过程状态

| 位置 | 原文 |
|---|---|
| `main.tex` 1478–1479 | Cross-vintage Traffic outputs are not used for method inference. |
| `main.tex` 1559、1567–1568 | not an official reproduction；None is an official reproduction；FedCure is not included |
| `main.tex` 2108–2113 | a new rule of this study and is reported as exploratory；not the frozen RAVEN configuration |
| `main.tex` 2135 | U-Air was re-run at 20 seeds, 270 runs and 45 regenerated traces |
| `main.tex` 2308 | not a pinned retraining archive；NSW four-region is not a confirmation experiment |
| `main.tex` 2315–2316 | internal to this study rather than part of that bundle |
| `main.tex` 2334–2340 | The earlier residual came from that solver path；reported as exploratory |
| `appendix.tex` 1729–1734 | 节标题 Additional Existing Experimental Context；not included in the main inferential family |
| `appendix.tex` 1744、1790 | not official reproductions |
| `appendix.tex` 1787 | it is not an MCS baseline |
| `appendix.tex` 1943–1945、1957 | intentionally not added；reused cross-vintage path；excluded cross-vintage Traffic path |
| `appendix.tex` 2212–2213 | Cross-vintage Traffic outputs remain unused. |
| `appendix.tex` 2224 | reading the frozen EventTraces only and re-running no training, weighting, or |
| `supplemental.tex` 91–99 | 节标题 Exploratory Trained-Rule Probe；reported as exploratory；\(\kappa=1000\) instead of the frozen value |

## 四、反复出现的“不混入、不是确认”

同一套否定各写一次：

- `main.tex` 272、1477–1478、2196、2280
- `appendix.tex` 1791、1956、1996–1997、2174–2175、2508–2510、2580–2582

措辞是 not mixed into Table III、not a confirmation of that table、not an end-to-end MCS ranking。

## 本记录不做的事

- 不把上述句子删掉或改写。用户尚未点名要改哪一句。
- 不把“预测零结果”追加进摘要或引言。用户 2026-10-11 已拒绝。
- 不把 Originality 从 3 改到更高，也不把 Significance 从 2 改分。
