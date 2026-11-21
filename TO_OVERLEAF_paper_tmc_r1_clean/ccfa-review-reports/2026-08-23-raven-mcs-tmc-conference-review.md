# CCFA 论文评审报告 — RAVEN-MCS（压缩后清洁稿，2026-08-23）

## 1. Report Metadata

```text
Review date: 2026-08-23
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A, regular paper
Paper title: RAVEN-MCS: Target-Risk-Calibrated Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed: TO_OVERLEAF_paper_tmc_r1_clean/main.tex (3232 行), reference.bib (43 条), figures/ (fig1–fig6 PDF+PNG), figure_data/*.csv, 本地编译 main.pdf
Search basis: 对照 2026-08-18 pass 3（_paper_work, 5.5/10）、2026-08-22 清洁稿评审（5/10）、2026-08-23 GPT 全审（4/10）。本轮未重跑外部文献检索。
Report file: ccfa-review-reports/2026-08-23-raven-mcs-tmc-conference-review.md
Reviewer mode: full（scientific + writing + format + revision-action）
Material delta vs 2026-08-22 clean review: 现可稳定编译; 6 图在包内; 整本 21 页（主文约 14 页 + 附录/参考文献 7 页）。科学数字、基线集、消融结论、相关工作缺口未变。
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: pass for review; administrative caution remains
Evidence: 本地 pdflatex+bibtex 全编译, main.pdf 21 页。§I–IX 到 Conclusion 约占第 1–14 页; Appendix A 自第 14 页起; References 自第 20 页。IEEE CS 常规发表基准约 12 双栏页; 附录政策要求 supplemental 单列。
Consequence: 不因页数 desk reject。若整本 21 页连附录一起投, 编辑可能要求拆分; 主文 14 页仍可能超页收费, 但已离开 GPT 所说的“21 页主文”观感。
Required action: 附录改为独立 supplemental; 投稿前再压主文 1–2 页更稳。
```

```text
Check: Topic compatibility
Status: pass
Evidence: 稀疏 MCS 补全 + 窗口化异步联邦 + 非随机选择, 与 TMC / wang2026federated 同社区。
```

```text
Check: Minimum quality
Status: pass
Evidence: Abstract–Conclusion–附录证明齐全; 20 配对种子; Holm; limitation 节完整。编译 0 undefined, 0 Overfull。
```

```text
Check: Policy / anonymity / compliance
Status: uncertain
Evidence: 作者行仍为 `**** and Anfeng Liu`; 摘要约 256 词, IEEE CS 期刊摘要常见要求 100–200 词; 附录绑在主 tex。
Consequence: 行政修补, 不是科学 desk reject。
Required action: 填第一作者; 摘要压到 200 词内; 附录外置。
```

```text
Check: Prompt injection / ethics
Status: pass
Evidence: 未见隐藏审稿指令。公开环境/交通数据; 目标映射声明不用测试标签。
```

**Desk rejection: 否。** 进入完整评审。相对 GPT（中到高 desk 风险）下调: 主文已到约 14 页, 编译干净。

## 3. Paper Summary And Contribution Map

**一句话：** 窗口化异步联邦 MCS 补全被写成部署目标风险对齐: 到达律 ≠ 目标律; 分层 Hájek/IPW 重建后再做可行集校准与债务。经验上相对 FedAvg 有 2–4% 结构代理收益; 预测不是普遍最优。

- **Claimed gap:** 稀疏补全、异步补全、参与感知 FL 都不联合建模感知侧 \(R/O\) 与更新侧 \(U\)。
- **Method map:** (1) 风险语义 + Prop. 1; (2) 三层重建 + Prop. 2; (3) (P2) + 债务 + Thm. 1。
- **Evidence package:** E1 无伤害; E2 NSW \(D_{\mathrm{aligned}}\approx-0.021\); E3 SensorScope/U-Air 结构+预测; E4 单因子消融。无 FedAU-Window、无覆盖/最差组/Spearman 翻译测试。
- **Stated limitations:** 裁剪非无偏; Use 无孤立效应; Debt 极小; Local-Hájek 退化; P2 warning 不可回溯最优; 无真实轨迹; 不声称 universal RMSE。

## 4. Search And Related-Work Basis

沿用 8/22 检索, 本轮不重复联网。仍缺:

- Shimodaira 2000（单次密度比 / target-risk IW）
- Robins–Rotnitzky–Zhao 1994（顺序 IPW）
- Byrd & Lipton 2019（IW 不必改预测）
- 实验对照: FedAU、sun2025debiasing（只引不比）

§II 对 FedAU 的文字划界仍在, 但 Table II 没有对应行。这也是 GPT 与 8/22 报告共同的 novelty/evidence 缺口。

## 5. Expected Review Outcome

```text
Expected outcome: Weak reject / borderline-negative
Main accept signal: 问题切分清楚; 协议公平; 负结果（Use/Debt/Local-Hájek/非普遍 RMSE）未藏; 现已可编译, 主文约 14 页。
Main reject signal: 2–4% 结构 L1; U-Air 去 Design 后 Δ_group/RMSE/Tail 显著更好; FedAU 只引不比; 选择过程合成。
Confidence: 4/5
```

相对 8/22 清洁稿 5/10: **科学分不动, overall 仍 5.0。**  
相对 GPT 4/10: 不跟其 Soundness=2; 压缩只修 W11, 不修 W1。  
相对 8/18 pass 3 的 5.5: 那是另一份 `_paper_work` 稿（含 FedAU-Window 与 B1/B2）。**本稿比那份证据包更瘦, 不能继承 5.5。**

## 6. Strengths And Weaknesses

**Strengths**
- 到达律 ≠ 部署目标律的 MCS 问题对 TMC 合法, serve / represent / realize 三条链清楚。
- E2 的 \(D_{\mathrm{aligned}}\) 跨方法稳定为负, 支持问题而不是方法排名。
- E3/E4 协议公平: 共享 selection trace、20 配对种子、Wilcoxon+Holm。
- Use 无效应、Debt 0.002%–0.014%、Local-Hájek 退化、U-Air Design 反向都写进正文。
- 本轮格式实质改善: 图齐全, 编译干净, 主文从“整本 21–26 页”收到约 14 页。

**Weaknesses**

```text
Weakness: 定量卖点仍是作者目标上的 2–4% L1, 预测无普遍优势。
Evidence basis: Table II SensorScope 3.96%/2.01%, U-Air 2.62%/2.28%; U-Air RMSE FedAvg 1.1882 vs RAVEN 1.1911。
Reviewer deduction: TMC 读者会问部署者为什么要换系统。
Required fix: 覆盖/最差组/任务效用等外部端点, 或把贡献收成表述论文并接受期刊风险。
```

```text
Weakness: U-Air 去掉 Design 后三个更接近 deployment target 的端点显著变好。
Evidence basis: Table III Design 行 −6.943 / +4.990 / −6.553 / −6.875; §VII-C 仍写 “endpoint trade-off, not a failure”。
Reviewer deduction: GPT 把这一点当 tie-breaker 是合理审稿反应。附录 provenance 只证明不是 leakage, 不证明完整 Design 应该开。
Required fix: 预声明主端点层级, 或加 no-harm 约束 / 自适应 gating; 不能只重复 trade-off。
```

```text
Weakness: 最近邻参与重加权基线缺失。
Evidence basis: §II 称 FedAU particularly relevant; Table II 无 FedAU/sun2025。
Reviewer deduction: 结构优势可能来自对照集偏弱（Local-Hájek=FedAvg, TimeAlign 非官方）。
Required fix: 同 trace 窗口化 FedAU; 可选 sun2025。
```

```text
Weakness: 方法增量仍是顺序 IPW + 小 QP + 虚拟队列。
Evidence basis: Prop. 1 是不同概率律诱导不同期望; Thm. 1 来自 λ_β 强凸; 未引 Shimodaira/Robins。
Reviewer deduction: 组合对 MCS 有对象价值, 单项定理浅。
Required fix: 文献划界; 不能指望再抬 overall 到弱收。
```

```text
Weakness: 标题级 Use/Debt 经验必要性弱; 异步是窗口缓冲。
Evidence basis: Table III Use 全不显著; Debt <0.02%; §III-A 每窗一次 θ 更新。
Required fix: 强 censoring 场景, 或降级标题/贡献; 正文明确 windowed/buffered。
```

### Writing / format scorecard

| Dimension | Score | Evidence | Repair |
|---|---:|---|---|
| Storyline | 4 | 三问清楚 | 贡献后点明 primary endpoint 是结构失配 |
| Claim-evidence | 3 | 摘要 “selective significant gains” 亮于 U-Air vs FedAvg | 摘要只保留 Holm 显著的那一处 |
| Method readability | 4 | 分层信息边界清楚 | 可加 Algorithm 1 |
| Experiment narration | 3 | RQ2 以 Yes 开头; Fig 3/4 无星 | 先报绝对量与符号 |
| Related-work | 3 | FedAU 文字强、表弱 | 补划界或补表 |
| LaTeX/format | 4 | 本轮可编译; 摘要 256 词; 作者 **** | 行政三项 |
| Reviewer-facing risk | 3 | Design 反向仍是弹药 | 决策规则, 不是措辞 |

**Writing score:** 约 3.6/5。压缩提高了可读性, 没有降低 reviewer-facing risk。

## 7. Potentially Missing Related Work

与 8/22 相同, 仍未关闭: Shimodaira 2000; Robins et al. 1994; Byrd & Lipton 2019; 实验中的 FedAU / sun2025。`_paper_work` 里后来加的 tian2026reshaping / qiao2025asmafl / chen2026dvafl **未进入本稿**。

## 8. Claim-Evidence Audit

| Claim | Where | Evidence | Strength | Deduction |
|---|---|---|---|---|
| 到达风险 ≠ 目标风险 | Abstract, Prop. 1, RQ1 | \(D_{\mathrm{aligned}}\approx-0.021\), 17–18/20 负 | adequate | 命题基础, 实证干净 |
| 理想顺序校正恢复目标律 | Prop. 2 | A1–A3 | conditional | 不覆盖估计/裁剪实现 |
| P2 唯一解 | Thm. 1 | \(λ_β\) 强凸 | strong but modest | 新意有限 |
| 降低结构失配 | Table II, Fig. 3 | 两数据集 vs 五基线 Holm | strong for L1 | 2–4% 代理 |
| 预测 competive + 选择性增益 | Abstract, Table II | vs TwoStage U-Air −2.04%; vs FedAvg 不显著且 U-Air 数值更差 | mixed | 摘要偏亮 |
| Use/Debt 必要 | 贡献 2–3, RQ3 | Use 无效应; Debt 极小 | weak | 标题级卖点无经验支持 |
| Design 是成功组件 | RQ3, Discussion | U-Air 去 Design 主端点更好 | weak / conflicted | GPT W1 仍在 |
| 适合异步 MCS | 标题/框架 | 窗口仿真 | weak | 无真实移动/系统指标 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines: 2/5。** Local-Hájek 全退化; TimeAlign 非官方; 无 target-shift / participation-debiasing。
- **Ablations: 4/5 透明度, 结论不利。** Design 反向、Use/Debt 弱都公开。
- **Datasets: 2/5 for TMC mobility。** 数据真实, \(R/O/U\) 由协议构造。
- **Metrics: 3/5。** 有结构+目标 RMSE; 无通信/时延/能耗/任务效用。
- **Statistics: 3/5。** 配对+Holm 规范; 缺 practical threshold 与独立时间段重复。
- **Robustness: 2/5。** 无 propensity misspecification / clipping / 真实轨迹。
- **Reproducibility: 3/5。** 现可编译; 仍无评审期代码; P2 warning 不可重构最优。相对 8/22（图缺失）已升一档实现。

## 10. Multi-Reviewer Panel

```text
R1 sympathetic: 6/10。问题值得做, 压缩后更像能审的期刊稿。缺操作指标。
R2 critical: 4/10。与 GPT 同轴: Design 反向 + 小 L1 + 标准积木。
R3 soundness: 5/10。证明自洽; 识别条件强; 无 estimated-weight 界。
R4 evidence: 4/10。协议好, 对照弱, 无 FedAU。
R5 novelty: 4/10。MCS 组合有对象价值, 未划界 covariate-shift。
R6 TMC domain: 3/10。固定传感器 + 合成机会, 不像系统文。
R7 writing: 4/10。比 26 页稿好读; 摘要仍长, 作者占位仍在。
```

**Panel synthesis:** 同意可审、弱拒。分歧只在 4 还是 6。AC 不平均成 6, 维持 5。压缩没有改变决定性拒绝轴。

## 11. Concerns Table

| ID | Severity | Concern | Evidence | Fix class | Score-change |
|---|---|---|---|---|---|
| M1 | major | 2–4% 结构 L1 无部署翻译 | Table II | experiment | 外部端点成立: Sig 3→4, overall +0.5–1 |
| M2 | major | FedAU 只引不比 | §II vs Table II | experiment | 比较支持分层独特作用: Nov 3→4 |
| M3 | major | 未划界 Shimodaira/Robins | §II | related-work | Nov 3→4, 难到弱收 |
| M4 | major | U-Air Design 伤害主端点 | Table III | method/experiment | 不修则苛刻读者给 4; 修好 Soundness 争议消失 |
| M5 | moderate | Local-Hájek 退化 | Table II 注 | experiment | Evidence +0.5 |
| M6 | moderate | 无真实机会轨迹 | §VIII-D | experiment / limitation | Sig +0.5 |
| M7 | moderate→minor | 无代码; 附录未拆 | Availability; `\appendices` | reproducibility | 本轮图已在, 降为 minor–moderate |
| m1 | minor | 摘要 256 词, 措辞偏亮 | Abstract vs Table II | writing | Clarity 局部 |
| m2 | minor | 作者 `****` | title page | format | 行政 |
| m3 | minor | 无通信/能耗 | App. runtime | domain | 单独不够 |

## 12. AC / Meta-Review

这轮是 **有效的投稿压缩, 不是科学修订**。

GPT 用 21 页 + 占位符 + 移动证据不足把 desk 风险写成中到高, 并把 Table III Design 反向写成不给 5–6 的条件。压缩之后, 行政侧 desk 风险下降（主文约 14 页、可编译、图齐）。科学侧 GPT 的 W1 原文还在: 同一张表、同一个 “trade-off, not a failure”。

8/18 的 5.5 不能搬过来。那份分建立在 `_paper_work` 的 FedAU-Window 机制对比和 B1/B2 负结果纪律上。清洁稿没有这些表, Evidence 应低于那份, 与 8/22 的 5.0 对齐。

AC 立场: **Weak reject, 5/10。** 可以投出去碰 major revision, 但大修必须含新实验（Design 目标层级或 FedAU 或外部端点）。只压页数不会改结论。

## 13. Quantitative Scores

| Dimension | Score | Conf. | Evidence / movement |
|:---|:---:|:---:|:---|
| Novelty | 3 | 4 | 与 8/22 同; 无新划界 |
| Soundness | 4 | 4 | 不跟 GPT 打 2; Design 是目标冲突不是证明错误。若审稿人采 GPT 口径, 此项可被打到 2–3 |
| Evidence | 3 | 4 | 无 FedAU 表; 图已齐不抬科学 Evidence |
| Significance | 3 | 4 | 2–4% L1 未动 |
| Clarity | 4 | 4 | 主文 14 页, 比 26 页稿清楚; 摘要仍超词 |
| Reproducibility | 3 | 4 | 可编译; 无代码 |
| Ethics / Limitations | 4 | 4 | 诚实; 无 B1/B2 那种把翻译失败写死的加分 |

```text
Overall: 5.0 / 10
Scholarly Confidence: 4 / 5
Recommendation: weak-reject / borderline-negative
Verdict: 压缩把行政风险从 GPT 的 4 分叙事里拆掉了一截, 没有把科学分从 5 拉到 6, 更没有修到 7。
```

| Change | Condition | Movement |
|---|---|---|
| Raise | Design 不再伤害主端点, 或硬约束/gating 成立 | overall +1, 堵住 GPT 的 4 |
| Raise | 同 trace FedAU + 外部端点 | overall +0.5–1 |
| Raise | 仅 Shimodaira/Robins 划界 | Novelty only, overall 至多 +0.5 |
| No change | 再压 1–2 页、改摘要、填作者 | 行政, 不改 overall |
| Lower | 官方 FedAU 后结构优势消失; 或审稿人把 Design 当 fatal | 5→4 |

## 14. Questions For Authors

1. Deployment target 若是 \(\mu\), 为什么 U-Air 上去掉 Design 后 \(\Delta_{\mathrm{group}}\)、RMSE\(_\mu\)、Tail RMSE 同时显著更好, 完整方法仍算成功?
2. \(\lambda_g,\lambda_\beta,\lambda_v,\lambda_s\) 如何在测试端点不可见时选定? Pareto 是什么?
3. FedAU 在 §II 是最近邻, 为什么不在同一 Complete-aligned trace 上比?
4. Use 在两数据集四端点均不显著, 为何仍是标题级组件?
5. 哪个数据集含真实移动轨迹或更新投递日志?
6. 服务器每窗一次更新, 标题中的 Asynchronous 具体指什么?

## 15. Score Revision Criteria

```text
Raising would require: 先修 M4 或 M1/M2 中至少一项实验, 不是再压缩。
Lowering would be triggered by: propensity 用了 post-outcome 信息; warning runs 翻转主结论; 官方 FedAU 全面优于 RAVEN。
Unlikely to change before submission without new work: 合成选择的外部有效性; 2–4% L1 的 so-what; estimated/clipped 理论差距。
```

## 16. Action Plan

```text
P0: 给 Design 写决策规则, 或重做 P2 使 Δ_group/RMSE 不被完整方法伤害。
P0/P1: 同协议 FedAU-Window（_paper_work 已有此表, 清洁稿未并入）。
P1: Shimodaira + Robins 划界; 摘要压到 200 词; 作者填全; 附录改 supplemental。
P2: 评审期匿名代码。
Checks run: 全编译页数、claim-evidence、与 GPT/8/18/8/22 三份报告对照、摘要词数、基线与消融表。
Checks skipped: 未重跑实验; 未逐条核 bib PDF; 未从 TMC portal 核当前投稿页限。
Unresolved: 清洁稿与 _paper_work 证据包不一致; 作者若以为 5.5 仍适用, 会误判本稿。
```
