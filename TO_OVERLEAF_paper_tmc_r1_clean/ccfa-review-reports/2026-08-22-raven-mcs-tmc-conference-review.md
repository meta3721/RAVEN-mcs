# CCFA 论文评审报告 — RAVEN-MCS（TMC 投稿清洁稿）

## 1. Report Metadata

```text
Review date: 2026-08-22
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A 期刊, regular paper
Paper title: RAVEN-MCS: Target-Risk-Calibrated Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed: TO_OVERLEAF_paper_tmc_r1_clean/main.tex (3204 行; 正文至 Conclusion 约 1935 行, 附录约 1269 行), reference.bib (43 条), figure_data/*.csv (4), make_figures.py; 未提供编译 PDF; figures/ 下 6 个 includegraphics 目标 PDF 均不在本目录
Search basis: 公开检索 Shimodaira 2000 (JSPI), Byrd & Lipton 2019 (ICML/PMLR 97), FedAU Wang & Ji ICLR 2024 / OpenReview / IBM 官方仓库, Robins–Rotnitzky–Zhao 1994 (JASA); IEEE Computer Society Author Guidelines (2026 抓取); TMC 专页页限转述来自 Computer Society 通用政策与第三方摘录, 未核到独立 TMC Author Information HTML
Report file: ccfa-review-reports/2026-08-22-raven-mcs-tmc-conference-review.md
Reviewer mode: full（scientific + writing + format + revision-action synthesis）
```

```text
Mode: full / standard
Venue and assumptions: IEEE TMC regular paper, CCF-A, 默认单盲 (IEEE CS 允许申请双盲; TMC 不在“不提供双盲”名单中, 但默认仍是 reviewer-anonymous / author-visible)。发表后常规 Transactions 正文 12 页, 超出收 MOPC; 附录须作为 supplemental 单独提交。第三方摘录称 TMC 投稿可至 18 页, 未核到本刊独立 HTML。
Paper summary: 见第 3 节。
Likely stance and calibrated score: Weak reject / borderline-negative, 5/10, confidence 4/5。
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: uncertain
Evidence: IEEEtran journal 单文件含 \appendices; 正文+附录体量很大。IEEE CS 政策写明期刊附录视为 supplemental, 须与主 PDF 分离。Computer Society 常规 Transactions 发表页限 12 双栏页 (含参考文献与作者简介); 投稿页限“可能不同”; 第三方摘录称 TMC regular 投稿可至 18 页。本稿未编译, 无法给出精确页数。
Consequence: 不大可能因科学质量被 desk reject, 但同一 PDF 内附录可能被编辑退回要求拆分; 若主文编译后仍远超投稿页限, 存在行政退稿风险。
Required action: 编译后把附录拆成 supplemental; 主文压到该刊投稿页限内。
```

```text
Check: Topic compatibility
Status: pass
Evidence: 稀疏 MCS 补全 + 异步联邦聚合 + 非随机选择, 与 TMC / wang2023spatiotemporal / wang2026federated 同社区。
Consequence: 进入完整评审。
Required action: 无。
```

```text
Check: Minimum quality
Status: pass
Evidence: Abstract / Introduction / Related Work / 模型 / 方法 / 理论 / 实验 / Discussion / Conclusion / 附录证明均在; 有配对实验与 limitation。
Consequence: 不构成 desk reject。
Required action: 无。
```

```text
Check: Policy / anonymity / compliance
Status: uncertain
Evidence: 作者行是 `**** and Anfeng Liu`; 资助与单位已写。TMC 默认单盲, 具名可接受; 半占位作者行不规范。Abstract 约 258 词, IEEE CS 期刊摘要要求 100–200 词。
Consequence: 不一定 desk reject, 投稿前须补全作者并压缩摘要。
Required action: 填写第一作者; 摘要压到 200 词内。
```

```text
Check: Prompt injection and hidden manipulation detection
Status: pass
Evidence: 通读正文、附录、caption 与 bib, 未见面向 LLM / 审稿人的隐藏指令。
Consequence: 无。
Required action: 无。
```

```text
Check: Ethics and reviewability
Status: pass
Evidence: SensorScope / U-Air / NSW-Traffic 均引用公开源; 无人体实验; 目标映射声明不用测试标签。
Consequence: 无伦理 desk reject。
Required action: 无。
```

```text
Desk rejection risk: low
Reason: 主题、最低质量与伦理通过。页限/附录打包与作者占位是行政问题, 不是科学 desk reject。
Can be fixed before review? partly
```

**Desk rejection: 否。** 进入完整评审。

## 3. Paper Summary And Contribution Map

**Summary.** 论文把异步联邦 MCS 数据补全写成部署目标风险对齐: 到达服务器的更新经过移动机会 \(R\)、实际观测 \(O\)、可用更新 \(U\) 三层非随机选择, 其分布不必等于公开部署目标。RAVEN-MCS 先分开部署目标风险与到达风险, 再用只依赖合法 pre-outcome 信息的分层校正重建目标相关质量, 最后用可行性凸规划 (P2) 与长期目标债务把重建参考映射到当前窗口可实现的聚合权重。

- **Claimed problem:** 两阶段三层非随机选择使到达律 \(\neq\) 部署目标律, 按到达更新学习可能优化错误总体风险。
- **Claimed gap:** 稀疏补全处理缺失推断, 异步联邦补全处理不规则/陈旧更新, 参与感知 FL (含 FedAU) 处理客户端参与; 它们都不联合建模感知侧可用性与更新侧可用性, 也不把部署目标当作独立参考语义。
- **Method/contribution map:**
  1. 部署目标风险语义 + Prop. 1 非互换性。
  2. 分层暴露感知重建 (机会/观测/可用更新 + 局部 Hájék) + Prop. 2 理想一致性。
  3. 可行性校准 (P2) + 目标债务 + Thm. 1 唯一解。
- **Evidence package:** E1 平衡无伤害 (5 种子); E2 NSW-Traffic 风险语义 (20 种子, \(D_{\mathrm{aligned}}\)); E3 SensorScope / U-Air 主有效性 (20 配对种子, \(\Delta_{\mathrm{group}}\), \(\Delta_{c\text{-}s}\), \(\mathrm{RMSE}_\mu\), Tail RMSE); E4 单因子消融; 附录证明、Local-Hájék 退化审计 (9666 窗口)、P2 可行性审计、E2 运行时诊断。
- **Stated limitations:** 不支持任意隐藏混杂与支持外质量; 裁剪后不声称精确无偏; Use 无孤立效应; Debt 效应小; Local-Hájék 在正式块退化为 FedAvg; P2 后验最优性不可重构; NSW-Traffic 不做方法推断; 无独立真实轨迹验证; TimeAlign-Agg 非官方复现。

## 4. Search And Related-Work Basis

```text
Queries used:
  Shimodaira 2000 improving predictive inference covariate shift importance weighting JSPI
  Byrd Lipton 2019 what is the effect of importance weighting in deep learning ICML
  FedAU Wang Ji ICLR 2024 lightweight unknown participation statistics federated averaging
  Robins Rotnitzky Zhao 1994 estimation of regression coefficients sequential missing data inverse probability
  IEEE Transactions on Mobile Computing author information page length supplemental material
Sources searched:
  IEEE CS Author Guidelines; Computer Society TMC CSDL; ICLR proceedings / OpenReview / arXiv:2306.03401; IBM/fedau; PMLR 97:872-881; JASA 89:846-866; JSPI 90:227-244 bibliographic records
Closest works found:
  FedAU (Wang & Ji, ICLR 2024): 未知参与统计下自适应聚合重加权, 官方代码 IBM/fedau。论文 §II 称为 particularly relevant, 评价中未作基线。
  Shimodaira (2000, JSPI 90:227-244): 协变量分布 ≠ 目标总体时的加权似然。未引。
  Robins, Rotnitzky, Zhao (1994, JASA 89:846-866): 缺失数据逆概率加权估计方程, 顺序 MAR 校正的标准来源。未引。
  Byrd & Lipton (2019, ICML/PMLR 97:872-881): 过参数化网络中 importance weighting 随训练消失。未引。机制与本稿有限容量补全模型不完全相同, 但可解释“结构对齐不必降低 RMSE”。
  Horvitz–Thompson 1952 / Hájek 1971: 已引, 并作为 Local-Hájek / TwoStage-Hájek 基线。
  wang2026federated: 最近的联邦 MCS 补全。TimeAlign-Agg 自承 not an official reproduction。
Unverified related-work risks:
  未逐条核对 43 条 bib 的 PDF; 未检索 2024–2026 全部“target-aware FL / sequential IPW for MCS”新作; TMC 18 页投稿上限来自第三方摘录。
Source-quality screening status:
  FedAU、Shimodaira、Byrd、Robins 均核到正式会议/期刊出处; 未使用 MDPI。wang2026federated 与若干 2026 条目仅核 bib, 未核 PDF。
```

## 5. Expected Review Outcome

```text
Expected outcome: Weak reject（borderline-negative）
Main accept signal: MCS 问题切分清楚; 实验协议公平 (共享 selection trace, 20 配对种子, Wilcoxon+Holm); limitation 与负结果 (Use 无效, Debt 极小, Local-Hájek 退化) 写得诚实; 附录证明完整。
Main reject signal: 主表增益是 2–4% 的结构 L1, 部署目标 RMSE 无普遍优势 (U-Air 上略差于 FedAvg); 核心 Design 层在 U-Air 消融中使 RMSE 改善 6.55%; 文中称为 particularly relevant 的 FedAU 未进入 Table II; 理论三件套分别是测度不等的直接推论、标准顺序 IPW/Hájek、强凸 QP 唯一解。
Confidence: 4/5
```

不给出接受概率。本稿科学完成度高于“未写完的草稿”, 但还达不到 TMC 弱收所需的部署后果或不可替代基线优势。

## 6. Strengths And Weaknesses

**Strengths**

- 把“到达更新分布 ≠ 部署目标”写成 MCS 特有的 \(R\to O\to U\) 顺序选择, 比只谈稀疏或缺席客户端更贴 TMC。
- E2 用同一选择位移下 \(D_{\mathrm{aligned}}\approx -0.021\) (17–18/20 种子为负) 把风险语义做成可检验命题, 而不是口号。
- 统计政策规范: 共享 trace、配对 Wilcoxon、预声明 Holm 族、\(\alpha=0.05\)。
- 负结果纪律好: Use 无孤立效应、Debt \(0.004\%\)–\(0.014\%\)、Local-Hájek 9666 窗口权重极差为 0、P2 778 条 solver warning 且不声称后验最优。
- 写作术语稳定 (`deployment-target`, `usable-update`, `client--stratum`), Abstract / Introduction / Conclusion 主张上限大体一致。

**Weaknesses**

```text
Weakness: 主主张的可部署后果落在结构代理指标上, 预测风险没有跟上。
Evidence basis: Table II. SensorScope \(\Delta_{\mathrm{group}}\) 1.0558→1.0139 (3.96%), \(\Delta_{c\text{-}s}\) 2.01%; U-Air 2.62%/2.28%。SensorScope RMSE 最佳是 TwoStage-Hájek 7.9309, RAVEN 7.9380; U-Air RMSE 最佳是 FedAvg/Local-Hájek 1.1882, RAVEN 1.1911。对 TwoStage-Hájek 的 2.04% U-Air RMSE 优势是选择性的。
Reviewer deduction: TMC 审稿人会问“对齐了又怎样”。2–4% 的 L1 质量差, 在补全 RMSE 上没有对应收益, 不足以支撑三层校正 + 凸规划 + 债务的系统复杂度。
Required fix: 增加覆盖阈值消不掉的下游指标 (最差组 RMSE、任务级补全/调度误差), 或证明更长时域上对齐的累积后果; 否则把贡献明确降为问题表述 + 负结果分析。
```

```text
Weakness: 称为 particularly relevant 的 FedAU 没有进入主比较族。
Evidence basis: §II 第 3 小节用一段介绍 FedAU, 并写 participation can change the effective FL objective。Table II 基线是 FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hájek, TwoStage-Hájek。没有 FedAU-Window, 也没有 sun2025debiasing。
Reviewer deduction: 最接近的“参与重加权 ≠ 目标对齐”对照缺失。Novelty 审稿人可以把 RAVEN 读成 FedAU 的 MCS 包装 + 标准 IPW。TimeAlign-Agg 还自承不是 wang2026federated 官方复现。
Required fix: 加入窗口化 FedAU (官方代码存在) 和/或 sun2025, 在同一 trace 上报告结构与 RMSE; 或给出不能运行的具体协议障碍。
```

```text
Weakness: 理论贡献偏薄, 与经验主张的距离被 Discussion 自己拉开。
Evidence basis: Prop. 1 是“两个不同的有限支撑概率向量存在不同加权期望”, 即测度不等的定义。Prop. 2 是顺序 IPW/Hájek 在 A1–A3 下的弱大数律。Thm. 1 是非空紧凸集上 \(\lambda_\beta>0\) 强凸目标的唯一极小点。E3 明确“不应读成 Prop. 2 或 Thm. 1 的经验证明”。
Reviewer deduction: 同情的审稿人会把价值放在 MCS 形式化, 而不是定理。苛刻审稿人会说三贡献里有两块是教材结果, 第三块是带约束的加权平均。
Required fix: 在 §II 相对 Shimodaira 单次密度比与 Robins 顺序 IPW 写清信息集与可行集校准的差异; 不要把 Prop. 1 写成独立科学发现。
```

```text
Weakness: 消融显示核心 Design 层可以伤害论文声称要保持的部署目标预测。
Evidence basis: Table III U-Air 去掉 Design: \(\Delta_{\mathrm{group}}\) \(-6.943\%^\ast\), \(\mathrm{RMSE}_\mu\) \(-6.553\%^\ast\), 同时 \(\Delta_{c\text{-}s}\) \(+4.990\%^\ast\)。正文称为 endpoint trade-off。附录 774 窗口 provenance 排除了 trace 泄漏。
Reviewer deduction: 这不是小负结果。它说明被保护的细粒度对齐可以与 \(\mathrm{RMSE}_\mu\) 反向。若审稿人把 RMSE 当部署后果, Design 层在 U-Air 上是有害组件。
Required fix: 解释何时应关闭 Design; 或证明该 RMSE 下降来自错误总体。仅称 trade-off 不够。
```

```text
Weakness: 选择过程是协议合成的, 不是被验证的移动机会过程。
Evidence basis: Complete-aligned 让三层选择“同方向非随机”; SensorScope/U-Air 是站点/网格环境数据。§VII-D 承认无独立真实轨迹验证, 不声称 mobility-model universality。
Reviewer deduction: TMC 领域审稿人会把这读成在静态传感器数据上注入合成缺失, 再证明加权能靠近自己定义的时间块目标。
Required fix: 用真实轨迹/机会日志驱动 \(R\); 或把贡献明确限制为 controlled selection protocol 下的统计校正。
```

## 7. Potentially Missing Related Work

```text
Work: Shimodaira, H. (2000). Improving predictive inference under covariate shift by weighting the log-likelihood function. JSPI 90:227–244.
Status: searched
Why relevant: 训练协变量分布 ≠ 目标总体时的密度比加权, 是本稿重建层的直接祖先。
Overlap: 单次密度比 vs 三层顺序信息集; 无可行集校准。
Needed comparison: §II 写清差异, 停止把“目标加权”写成 MCS 独有发明。
```

```text
Work: Robins, J. M., Rotnitzky, A., & Zhao, L. P. (1994). Estimation of regression coefficients when some regressors are not always observed. JASA 89:846–866.
Status: searched
Why relevant: 顺序缺失下的 IPW 估计方程是 Prop. 2 的标准来源; 论文只引到 Horvitz–Thompson / Hájek。
Overlap: 顺序逆概率校正; 本稿加上 MCS 窗口与 (P2)。
Needed comparison: 引用并限定“新”的部分是部署目标语义 + 可行校准, 不是 IPW 本身。
```

```text
Work: Wang, S., & Ji, M. (2024). A lightweight method for tackling unknown participation statistics in federated averaging. ICLR 2024. Official code: IBM/fedau.
Status: searched
Why relevant: 论文自己把它标成 particularly relevant; 参与重加权会替换 FL 目标。
Overlap: 聚合权重适应未知参与; 不建模 \(R/O\) 感知层, 也不对准公开部署目标 \(h(i)\)。
Needed comparison: 必须作为 Table II 基线, 而不只是文字对照。
```

```text
Work: Byrd, J., & Lipton, Z. C. (2019). What is the effect of importance weighting in deep learning? ICML 2019, PMLR 97:872–881.
Status: searched
Why relevant: 解释 IW 不必改变最终预测; 与 “alignment ≠ RMSE” 叙事相容。
Overlap: 机制针对过参数化可分网络, 与本稿补全模型不完全相同。
Needed comparison: 引用时限定模型类, 避免暗示同一失效定理适用于 RAVEN。
```

```text
Work: 2024–2026 target-aware / distributionally robust FL 与 MCS 机会过程轨迹模型的更新工作
Status: unverified
Why relevant: 若已有把部署目标与到达律分开并对齐的联邦 MCS 论文, 新颖性需要收缩。
Overlap: 未知。
Needed comparison: 投稿前用独立文献检索补一轮, 不在本报告中发明条目。
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| 到达律不必匹配部署目标, 优化到达更新可能优化错误总体风险 | Abstract; Intro para 2; Prop. 1 | Prop. 1 + E2 \(D_{\mathrm{aligned}}\approx-0.021\), 20 种子 | adequate | 问题成立; Prop. 1 本身几乎是定义 | 把 Prop. 1 降为引理/remark, 让 E2 承担经验重量 |
| 三层校正在理想条件下恢复兼容目标律 | Contrib. 2; Prop. 2 | 附录证明; A1–A3; 明确排除有限窗口与裁剪 | adequate for the ideal claim | 不覆盖实现版 RAVEN | 保持现有限定; 不要在 Intro 读成有限窗口保证 |
| (P2) 有唯一全局极小 | Contrib. 3; Thm. 1 | 强凸 + 紧凸可行集; 附录 Hessian | adequate for the program | 778 条 warning, 后验最优不可重构 | 正文已限定; 保持 |
| 结构错配相对 FedAvg 降 3.96%/2.01% 与 2.62%/2.28% | Abstract; Intro; Table II | 20 种子, Holm 对五条同骨干基线显著 | strong for the L1 metric | 效应小; 指标是自己定义的 \(\omega\) vs \(\mu\) | 报告绝对 L1 与效应量, 不只百分比 |
| 保持 competitive 部署目标预测, 有选择性显著增益 | Abstract; RQ2 | U-Air vs TwoStage-Hájek 2.04%; 对 FedAvg 不显著且均值略差 | weak-to-adequate | Abstract 的 “selective significant gains” 比主表更亮 | 摘要改为 “no universal RMSE gain; one Holm-significant comparison on U-Air” |
| RAVEN 是耦合系统, Use 无孤立效应, Debt 很小 | RQ3; Discussion | Table III | strong | 诚实, 但削弱“三层都必要” | 已披露; 考虑把 Use 从贡献句中降级 |
| 去掉 Design 是 endpoint trade-off 而非审计失败 | RQ3; App. design provenance | 774 窗口 hash 一致 | adequate for leakage | 未解释为何 RMSE 变好应被视为可接受 | 增加错误总体 vs 有限样本噪声分析 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines:** 同骨干五条 + Inst-Cal / Debt-Cal。缺 FedAU、sun2025、官方 wang2026federated。Local-Hájek 因协议退化与 FedAvg 数值相同, 实际有效基线更少。Central-* 标成 reference-only, 处理得当。
- **Ablations:** 五组件单因子, 方向不单调, 这是优点。U-Air Design 与 RMSE 反向是未消化的决策点。Use 四指标均不显著。
- **Datasets:** E3/E4 只有 SensorScope (55) 与 U-Air (36)。NSW-Traffic 仅 E2。目标 \(h(i)\) 是四个 UTC 时段, 不是空间覆盖或任务优先级。Complete-aligned 选择是同方向合成协议。
- **Metrics:** \(\mathrm{RMSE}_\mu\) 与 Tail RMSE 合理; \(\Delta_{\mathrm{group}}\) / \(\Delta_{c\text{-}s}\) 是训练质量的 L1, 不是下游 MCS 任务。无通信、能量、延迟、成功率。附录 runtime 只是 E2 墙钟, 且 RAVEN 与 FedAvg 几乎相同 (~72s vs ~71s), 不能当系统开销证据。
- **Statistical rigor:** 20 配对种子 + Wilcoxon + Holm, 对 TMC 经验论文是加分。E1 只有 5 种子, 且只作 no-harm。未报告效应量 (Cliff \(\delta\) / 配对中位数差)。
- **Robustness/failure:** 有 Design 反向、Hájek 退化、P2 warning。无漂移主表、无真实轨迹、无超参敏感性扫描。
- **Implementation:** 无 `\begin{algorithm}` (却导入了 `algorithm`/`algorithmic`)。选择模型、EMA、裁剪阈、P2 权重 \(\lambda\) 的可复现清单不完整。
- **Artifacts:** 数据有 DOI/URL。代码、配置、种子列表、selection-trace 生成器均未提供, 也无 camera-ready 承诺。
- **Limitations:** §VII 比多数 TMC 稿诚实。它不能替代缺失的 FedAU 与下游指标。

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-Justified
Expertise: MCS / TMC sympathetic reader
Likely score: 6/10 (borderline positive)
Confidence: 4
Main positive signal: 问题是 TMC 的; E2 把“到达 ≠ 目标”做成跨方法稳定的负 \(D_{\mathrm{aligned}}\); 协议公平。
Main negative signal: 2–4% L1 与无 RMSE 优势限制兴奋度。
Evidence basis: §I gap; Fig. 2; Table II.
Fatal concern if any: none
Score-change condition: 任一不可被覆盖阈值消去的下游指标为正, 可到 7。
```

```text
Reviewer: Critical
Expertise: reject-case hunter
Likely score: 4/10 (weak reject)
Confidence: 4
Main positive signal: 负结果没有藏。
Main negative signal: FedAU 被写成 closest work 却不比; Prop. 1 空洞; Design 消融伤害 RMSE; 选择是合成的。
Evidence basis: §II FedAU 段; Prop. 1; Table II–III; §VII-D。
Fatal concern if any: 无单一政策/造假问题。最接近 fatal 的是“中心经验主张不被部署指标支持”。
Score-change condition: 加入 FedAU 且 RAVEN 在结构上显著更好、RMSE 不显著更差, 可到 5; 若 FedAU 同时更好, 降到 3。
```

```text
Reviewer: Method / Soundness
Expertise: statistical correction / convex aggregation
Likely score: 6/10
Confidence: 4
Main positive signal: 信息集边界写得清楚; 裁剪与 A3 的缺口没有粉饰; Thm. 1 对所陈述规划是对的。
Main negative signal: 识别依赖正确倾向与 positivity; 实现是裁剪 plug-in; Prop. 1 不应作为定理贡献。
Evidence basis: A1–A4; Prop. 2 声明; §VII-C。
Fatal concern if any: none, given the written boundaries
Score-change condition: 相对顺序 IPW 文献划界, Novelty 升; 理论分不必升。
```

```text
Reviewer: Evidence / Experiment
Expertise: empirical FL / MCS
Likely score: 4/10
Confidence: 4
Main positive signal: 共享 trace 与 Holm 使小差异可审。
Main negative signal: 有效基线因 Hájek 退化而变窄; 缺 FedAU; RMSE 无优势; U-Air Design 反向 6.55%。
Evidence basis: Table II–III; App. Local-Hájek; App. P2。
Fatal concern if any: none
Score-change condition: FedAU + 第三个可比数据集或下游任务。
```

```text
Reviewer: Novelty / Positioning
Expertise: FL participation bias / covariate shift
Likely score: 4/10
Confidence: 4
Main positive signal: 部署目标 \(h(i)\) 对机会层 \(s(i)\) + 可行集, 相对 FedAU 有真实对象差异。
Main negative signal: 未引 Shimodaira / Robins; 未跑 FedAU; 机制是 IPW + 小 QP。
Evidence basis: §II; searched sources above。
Fatal concern if any: 不是 novelty collapse, 是 under-positioned incrementalism。
Score-change condition: 补文献篱笆 + FedAU 表, Novelty 可到 4/5。
```

```text
Reviewer: Writing / Clarity
Expertise: reviewability
Likely score: 7/10 on writing; 5/10 overall unchanged
Confidence: 4
Main positive signal: 主张上限、术语、RQ 对齐都好。
Main negative signal: 无算法框图; 方法符号密; 摘要 258 词且偏亮。
Evidence basis: Abstract; §§IV–V; missing algorithm env。
Fatal concern if any: none
Score-change condition: 算法环境 + 摘要收束, Clarity 可到 5。
```

```text
Reviewer: Ethics / Reproducibility
Expertise: artifacts / responsible claims
Likely score: 5/10
Confidence: 4
Main positive signal: 公开数据; 不用测试标签; limitation 具体。
Main negative signal: 无代码、无超参见清单、无 artifact 承诺; 作者占位; 图 PDF 不在本目录。
Evidence basis: §VII-D; package file list; no code sentence。
Fatal concern if any: none
Score-change condition: 发布可运行仓库 (trace 生成器、种子、P2 求解器)。
```

```text
Reviewer: Domain Application (MCS)
Expertise: mobile crowdsensing practice
Likely score: 4/10
Confidence: 4
Main positive signal: 机会/观测/上报失败确实是 MCS 运行问题。
Main negative signal: 评价在站点温度/空气网格上注入 Complete-aligned 缺失; \(h(i)\) 是一天四段; 无工人、轨迹、通信或激励。
Evidence basis: Table I; §VII-D; runtime table。
Fatal concern if any: none; venue mismatch 是部分的, 不是错刊。
Score-change condition: 真实机会过程或 MCS 任务级效用。
```

```text
Reviewer: Evidence/Ablation (extra)
Expertise: component isolation
Likely score: 4/10
Confidence: 4
Main positive signal: 单因子、同种子、不假装五模块单调。
Main negative signal: Use 无效应仍留在故事里; Design 与 RMSE 反向未变成决策规则。
Evidence basis: Table III; RQ3 答句。
Fatal concern if any: none
Score-change condition: 把 Use 从默认流水线移到条件组件, 并给出 Design 开关准则。
```

```text
Reviewer: Reproducibility (extra)
Expertise: independent reimplementation
Likely score: 3/10
Confidence: 4
Main positive signal: 数据集划分数字与审计计数可核。
Main negative signal: 缺算法、代码、\(\lambda\) 与裁剪默认值、倾向模型细节; 图文件缺失。
Evidence basis: no algorithm; empty figures/; §V 叙述。
Fatal concern if any: none
Score-change condition: 代码 + 配置 + 生成图。
```

```text
Reviewer: Novice Advocate
Expertise: first-time TMC reader
Likely score: 6/10
Confidence: 3
Main positive signal: Intro 三问 (serve / represent / realize) 清楚; RQ 与理论链对齐。
Main negative signal: \(\pi,\nu,\zeta,\beta,\alpha,Q\) 同时出现且无伪代码; Fig. 1 源文件不在包内。
Evidence basis: Intro; §§III–V; missing fig PDFs。
Fatal concern if any: none
Score-change condition: 一页算法 + 符号表。
```

```text
Agreement: 问题对 TMC 合法; 协议公平; 结构 L1 有小而显著的改善; RMSE 不是卖点; 理论是正确但浅的。
Disagreement: 同情读者给 6, 认为形式化本身可发表; 批判读者给 4, 认为缺 FedAU 且无部署后果。无人给 8+ 或 desk-reject 1–2。
Decisive positive axis: 诚实的 MCS 选择偏置形式化 + 可审计实验协议。
Decisive negative axis: 经验主张停在小 L1; 最近参与重加权基线缺失; 核心层可伤害 RMSE。
Unresolved evidence: 官方 FedAU 在同一 trace 上的数字; 真实轨迹机会过程; 编译后页数。
AC stance: Weak reject / 5.0。讨论可能变成“major revision 后可再投”, 但按当前稿不是弱收。不把同情分与批判分平均成 6。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | major | 结构 2–4% 改善未翻译成部署 RMSE / 任务效用 | Table II; Abstract; §VII-A | Significance, Evidence | experiment | 增加覆盖消不掉的下游指标, 或收缩贡献 | ccf-experiment-designer | 正的下游结果: Significance 3→4, overall +0.5~+1; 再失败: 维持 5 或降至 4 |
| M2 | major | FedAU 称为 closest 却不比 | §II; Table II; ICLR 2024 + IBM/fedau | Originality, Evidence | experiment | 窗口化 FedAU (及可选 sun2025) 同 trace 对比 | ccf-experiment-designer | 比较支持分层对齐独特作用: Originality 3→4; 若 FedAU 全面更好: overall −1 |
| M3 | major | 理论增量浅且未相对 Shimodaira/Robins 划界 | Prop. 1–2; Thm. 1; searched JSPI/JASA | Originality, Positioning | related-work | 引用并写差异; Prop. 1 降级 | ccf-paper-writer | Originality 3→4, overall +0.5, 抬不到弱收 |
| M4 | major | U-Air 去 Design 使 RMSE 降 6.55% | Table III; App. design provenance | Evidence, Soundness | analysis-fixable / experiment | 给出开关规则或错误总体解释 | ccf-paper-writer / ccf-experiment-designer | 解释成立则 Evidence 不降; 无解释则苛刻读者把 overall 压到 4 |
| M5 | moderate | Local-Hájek 退化, 有效基线变窄 | Table II 注; App. 9666 窗口 | Evidence | experiment | 换使层内权重非均匀的协议, 或去掉该基线的独立地位 | ccf-experiment-designer | 恢复可区分的 Hájek 对照: Evidence +0.5 |
| M6 | moderate | 选择过程合成, 无真实机会轨迹 | Table I; §VII-D | Significance, domain | experiment / accepted-limitation | 轨迹驱动 \(R\), 或把主张限为 controlled protocol | ccf-experiment-designer | 真实机会验证: Significance +0.5 |
| M7 | moderate | 无代码/算法/超参, 图 PDF 不在包内 | 无 algorithm; figures 缺失; 无 artifact 句 | Reproducibility | reproducibility / LaTeX | 补算法、发代码、生成并纳入 6 图 | ccf-paper-writer | Reproducibility 3→4 |
| m1 | minor | 摘要 258 词且增益措辞偏亮 | Abstract vs Table II; IEEE CS 100–200 词 | Clarity, format | writing / claim-qualification | 压到 200 词; 与 Table II 对齐 | ccf-paper-writer | Clarity 局部 |
| m2 | minor | 作者占位、附录在主文件 | `\author{**** and Anfeng Liu}`; `\appendices` | format / policy | LaTeX/format | 补作者; 附录改 supplemental | ccf-paper-writer | 行政合规, 不改科学分 |
| m3 | minor | TimeAlign 非官方复现 | §VII setup | Evidence | experiment / writing | 列差异或换官方代码 | ccf-experiment-designer | 次要 |
| m4 | minor | Byrd 类 IW 失效文献未引 | searched ICML 2019 | Positioning | citation/positioning | 限定模型类后引用 | ccf-paper-writer | 只巩固 M3 |
| m5 | minor | 无通信/能量/延迟 | App. runtime 仅墙钟 | domain / Significance | experiment | 报聚合开销或明确非系统论文 | ccf-experiment-designer | 对 TMC 系统向读者有用, 单独不够弱收 |

## 12. AC / Meta-Review

审稿人同意: 这是一篇写完的、可审的 TMC 范围稿, 不是 desk reject。协议与 limitation 诚实。分歧在意义: 同情者看到干净的问题切分, 批判者看到小 L1、缺 FedAU、Design 与 RMSE 反向。

决定性接受轴是 MCS 选择偏置的形式化加可重复的结构校正证据。决定性拒绝轴是部署后果不足, 加上论文自己标出的最近基线没有跑。

AC 立场: **Weak reject, 5/10。** 现稿更像一次认真的 major-revision 起点, 而不是可接受的 CCF-A 期刊论文。讨论风险: AE 可能因写作质量给一次大修, 但若审稿人抓住 FedAU 与 RMSE, 大修必须包含新实验, 不能只改句子。

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 3 | 4 | §II; Prop. 1–2; Thm. 1; 未引 Shimodaira/Robins; FedAU 只引不比 | MCS 对象切分真实, 机制是顺序 IPW + 凸校准。补篱笆与 FedAU 表可到 4。 |
| Soundness | 4 | 4 | A1–A4; 附录证明; 裁剪/solver 边界已写 | 不是错误; 也不是深定理。Prop. 1 过卖会在答辩中被点名, 暂不降到 3。 |
| Evidence | 3 | 4 | Table II–III; E2; 缺 FedAU; RMSE 无普遍优势 | 协议 4, 主张匹配度 3。FedAU + 下游指标可到 4; Design 无解释可到 2。 |
| Significance | 3 | 4 | Abstract 2–4% L1; U-Air RMSE 1.1911 vs 1.1882; 合成选择 | TMC 关心运行后果。下游或真实轨迹可到 4; 否则锁 3。 |
| Clarity | 4 | 4 | 三贡献/RQ 对齐; 无算法; 摘要偏长 | 可读。算法 + 摘要收束可到 5。 |
| Reproducibility | 3 | 4 | 公开数据与审计数字; 无代码/图文件/超参见 | 独立复现需猜测。代码与图可到 4。 |
| Ethics / Limitations | 4 | 4 | §VII 具体; 公开数据; 作者占位 | 主张纪律是 5 的方向; 缺代码承诺与作者信息, 定为 4。 |

**Overall:** 5 / 10  | **Scholarly Confidence:** 4 / 5

**Recommendation:** weak-reject / borderline-negative
**Verdict:** 单独补句子或补 Shimodaira 不够 +1。需要 FedAU 比较或不可消去的下游指标之一为正向, 才可能到 6。若官方参与重加权在 RMSE 与结构上同时更好, 降到 4。

```text
Quality: 3
Clarity: 4
Significance: 3
Originality: 3
Soundness: 4
Evidence: 3
Reproducibility: 3
Ethics / Limitations: 4
Overall: 5
Confidence: 4
Score-change conditions: 见上表与第 15 节
```

### Writing scorecard (full mode)

| Dimension | Weight | Score (1-5) | Confidence (1-5) | Evidence basis | Concrete repair |
| --- | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | Intro 问题→缺口→三问 | 早一句点明 RMSE 不是主卖点 |
| Contribution display | 12 | 4 | 4 | 三条贡献非空, Prop. 1 过重 | Prop. 1 改为 supporting lemma |
| Paragraph logic | 10 | 4 | 4 | 多数段落单任务 | Method 若干段同时定义符号与声称识别 |
| Claim-evidence alignment | 14 | 4 | 4 | Discussion 诚实, Abstract 偏亮 | 摘要与 Table II 对齐 |
| Method readability | 10 | 3 | 4 | 无算法; 符号密 | 加 Algorithm 1 覆盖重建+(P2)+债务 |
| Experiment narration | 10 | 4 | 4 | RQ 先结论后数字 | Fig. 3/4 无 Holm 星, 靠表 |
| Related-work positioning | 8 | 3 | 4 | FedAU 段强, 缺密度比/顺序 IPW | 加 Shimodaira/Robins 对照轴 |
| Terminology and notation consistency | 8 | 5 | 4 | h(i)/s(i), 目标/到达 稳定 | 保持 |
| LaTeX and format discipline | 8 | 3 | 4 | 附录在主文件; 图缺失; 摘要超词; 空 algorithm 包 | 拆附录、生成图、压摘要 |
| Reviewer-facing risk | 8 | 3 | 4 | “selective gains” + 缺 FedAU | 先改摘要与基线表 |

**Writing score:** 3.74 / 5. **Writing risk band:** moderate.

## 14. Questions For Authors

1. 为什么 Table II 没有 FedAU, 尽管 §II 把它写成 particularly relevant, 且官方实现公开?
2. 部署系统应该最大化 \(\Delta_{c\text{-}s}\) 还是最小化 \(\mathrm{RMSE}_\mu\)? 在 U-Air 上去掉 Design 时二者冲突, 默认流水线如何选?
3. 四个 UTC 时段作为 \(h(i)\), 对应哪一个具体 MCS 部署目标 (覆盖公平、高峰误差、还是监管报告窗口)?
4. Complete-aligned 的同方向非随机选择, 有没有真实轨迹或参与日志作为依据, 还是纯协议设计?
5. 发表时代码、selection-trace 生成器与 P2 求解配置是否会公开?

## 15. Score Revision Criteria

```text
Raising the score would require:
  1) 同一 shared trace 上的 FedAU (或书面说明不可比的协议冲突) , 且 RAVEN 的结构优势不能被参与重加权复制; 或
  2) 一个覆盖打平后仍存在的下游/最差组/任务指标对 RAVEN 有利。
  满足 1 或 2 之一, overall 可到 6 (borderline positive)。两者都正且 RMSE 不显著退化, 才讨论 7。
  只补 Shimodaira/Robins/算法/代码: Originality 或 Reproducibility +1, overall 仍 5, 最多 +0.5。
Lowering the score would be triggered by:
  FedAU 同协议下结构与 RMSE 均更好; 或发现目标/选择用了测试标签; 或 Prop. 1 被当作唯一理论卖点且无 E2。overall 4 或更低。
Concerns unlikely to change before submission:
  Prop. 1 的数学深度; 12 页发表页限下的系统开销评价; 无新数据时的真实轨迹缺口。
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | FedAU 同 trace 比较支持分层对齐 | Originality, Evidence | +0.5 overall, 可能到 6 |
| Raise score | 覆盖消不掉的下游指标为正 | Significance, Evidence | +0.5 to +1 overall |
| Raise score | Shimodaira/Robins 划界 + 算法 + 代码 | Originality, Clarity, Reproducibility | 维度 +1, overall 0 to +0.5 |
| Lower score | 参与重加权同时赢结构和 RMSE | Evidence, Originality | −1 overall |
| No quick change | 合成机会过程; Prop. 1 浅 | Significance, Originality | 投稿前难动 |

## 16. Action Plan And CCFA Handoffs

```text
Priority: 1
Action: 在共享 selection trace 上加入窗口化 FedAU, 报告 \(\Delta\) 与 \(\mathrm{RMSE}_\mu\)。
Owner skill: ccf-experiment-designer
Input needed: 现有 E3 协议、IBM/fedau 权重更新规则、窗口语义。
Expected output: 新表行 + 是否“参与重加权 ≠ 层对齐”的判定。
Handoff required: yes (需用户授权新实验; 本技能不发明数字)
```

```text
Priority: 1
Action: 选定一个覆盖打平后仍存在的部署指标 (最差组 RMSE、任务误差、或预声明空间组), 跑完并按结果改主张。
Owner skill: ccf-experiment-designer
Input needed: 预声明分组与冻结检查点。
Expected output: 正结果进主文, 负结果进 §VII (不可藏)。
Handoff required: yes
```

```text
Priority: 2
Action: §II 加入 Shimodaira 2000 与 Robins et al. 1994, 把差异写成“顺序三层信息集 + 可行集校准”, 并把 Prop. 1 降为 lemma。
Owner skill: ccf-paper-writer
Input needed: 本报告第 7 节条目。
Expected output: 修订 Related Work / Theory 措辞, 不新增实验数字。
Handoff required: yes (改稿)
```

```text
Priority: 2
Action: 为 U-Air Design 反向写决策规则; 将 Use 从“必要层”降为“本协议无孤立效应的层”。
Owner skill: ccf-paper-writer
Input needed: Table III 与 App. design provenance。
Expected output: RQ3/Discussion 改写。
Handoff required: yes
```

```text
Priority: 3
Action: 生成并纳入 6 张图; 增加 Algorithm 1; 摘要压到 200 词并与 Table II 对齐; 附录改 supplemental; 填写作者; 准备代码仓库。
Owner skill: ccf-paper-writer
Input needed: make_figures.py, figure_data, 作者信息, 代码许可。
Expected output: 可编译 Overleaf 包。
Handoff required: yes
```

```text
Recommended next CCFA owner: ccf-experiment-designer (先做 M1/M2), 然后 ccf-paper-writer。不要把本评审直接交给 ccf-rebuttal-writer。
```

### Writing-review panel (compact)

```text
Role: Storyline reviewer
Writing score tendency: 4
Confidence: 4
Main readability gain: serve / represent / realize 三问。
Main reviewer-confusion risk: 读完 Intro 会期待 RMSE 胜利。
Evidence basis: Intro 末与 Abstract。
Concrete edit: 在贡献后立刻写 “primary endpoint is structural mismatch”。
Expected score movement: 降低 M1 的写作放大, 不改 Significance。
```

```text
Role: Claim-evidence reviewer
Writing score tendency: 3.5
Confidence: 4
Main readability gain: RQ2 答句承认非普遍最优。
Main reviewer-confusion risk: Abstract “selective significant gains”。
Evidence basis: Abstract vs Table II U-Air FedAvg 1.1882 vs RAVEN 1.1911。
Concrete edit: 摘要只保留 Holm 显著的那一处, 并报 FedAvg 对照。
Expected score movement: Clarity 4 维持或微升。
```

```text
Role: LaTeX/format reviewer
Writing score tendency: 3
Confidence: 5
Main readability gain: IEEEtran journal 模板正确。
Main reviewer-confusion risk: 缺图、附录绑定、摘要超词、空 algorithm 包、作者 ****。
Evidence basis: 目录无 pdf 图; `\appendices`; 258 词; `\usepackage{algorithm}` 未使用。
Concrete edit: 见 Priority 3。
Expected score movement: 行政/格式, 非科学 overall。
```

### High-impact paragraph IDs

| ID | Current role | Reviewer takeaway | Main problem | Concrete edit | Severity |
| --- | --- | --- | --- | --- | --- |
| Abstract-P1 | claim + evidence | 三层选择 + 2–4% 结构收益 + 选择性 RMSE | 258 词; RMSE 措辞亮于表 | 删机制细节; 对齐 Table II | high |
| Intro-P2 | problem | 到达数据不是部署总体 | 无 | keep | low |
| Intro-P3 | gap | 稀疏/异步/参与三条线都不够 | FedAU 在缺口段被并列, 后文不比 | 缺口段预告将作参与重加权对照, 或删“particularly” | high |
| Contrib-1 | claim | 风险语义 + 非互换 | 把定义性命题当贡献 | 改为 formulation contribution, 定理降级 | medium |
| Related-FedAU | contrast | FedAU 改目标, RAVEN 对齐部署目标 | 只有文字, 无表 | 指向新的 FedAU 行 | high |
| Eval-RQ2 | evidence | 结构赢, RMSE 竞争 | “Yes” 开答, 数字是小 L1 | 先报绝对 \(\Delta\) 与 RMSE 符号 | medium |
| Eval-Design | limitation | Design 保护 \(c\text{-}s\), 可伤害 RMSE | 称为 trade-off 后仍默认开 Design | 加决策句 | high |
| Disc-RMSE | limitation | 对齐不必降 RMSE | 好 | keep | low |
| Conc-P2 | summary | 与理论同构的实验支持 | 未提 FedAU 缺失与 Design 反向 | 结论加一句未测参与重加权与 U-Air 权衡 | medium |

```text
Format verdict: 模板对, 投稿包不完整。
Blocking compliance issues: 6 张 includegraphics PDF 不在本目录, 现包不能稳定编译; 附录在主 tex 中, 违反 IEEE CS “appendices are supplemental” 政策。
LaTeX/source issues: 未使用的 algorithm 包; `\def\red`/`\def\blue` 遗留; 作者 ****; 未编译 (not compiled)。
Figure/table/caption issues: 表 caption 自我完备; 图文件缺失。Fig. 3/4 不标 Holm。
Citation/reference issues: 43 条均在 tex 中使用的抽查范围内; 缺 Shimodaira/Robins/Byrd。
Notation/equation issues: 符号先定义后使用, 总体一致; 缺总表与算法。
Suggested checks or build command: 先 `python make_figures.py` 生成 fig2–fig6, 补 fig1, 再 pdflatex+bibtex; 测主文页数 (附录分离后)。
```

```text
Venue: IEEE Transactions on Mobile Computing
Venue family: mobile computing / networking systems
Primary scoring dimensions: 真实 MCS 问题, 设计可实现性, 评价现实性, 端到端后果, 运行边界
Evidence package expected: 真实或轨迹驱动负荷, 最近 MCS/FL 基线, 开销, 任务级效用
Likely reviewer taste: “这能让部署中的 MCS 补全更好吗?”
Likely AC concern: 小代理指标 + 标准 IW/QP
Biggest mismatch risk: 把合成选择下的结构 L1 当成系统贡献
Writing moves that improve fit: 算法, 附录外置, 基线补全, 把 RMSE/任务后果放进摘要
```

```text
Checks run: desk, contribution, evidence, adversarial, related-work public search (4 条 closest work), claim-evidence table, experiment audit, 11-role panel, writing scorecard, paragraph IDs, LaTeX/format scan, IEEE CS policy fetch, score consistency
Checks skipped: 全文 PDF 编译; 43 条 bib PDF 逐条核对; TMC 专页 18 页上限的官方 HTML; 代码执行; 真实轨迹数据审计
Unresolved risks: 编译页数; FedAU 同协议数字; 2024–2026 未检索全的 target-aware FL; fig1 源文件下落
```

```text
Output self-check:
1. 16 节顺序与技能模板一致。
2. 表列数对齐。
3. overall 5 与最强未解问题 (Significance 3 + 缺 FedAU) 一致, 未用写作分抬到弱收。
4. 未给接受概率, 未发明实验数字, 未把 sibling 目录的 FedAU 表抄进本稿证据。
5. 每个 ≤3 分维度都有扣分理由与修复条件。
```
