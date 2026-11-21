# IEEE TMC 论文评审报告：RAVEN-MCS

## 1. Report Metadata

```text
Review date: 2026-08-22
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A 期刊
Paper title: RAVEN-MCS: Target-Risk-Calibrated Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed: main.tex (3204 行), reference.bib (43 条), figures/ (6 图), figure_data/ (4 CSV), make_figures.py
Search basis: 本地文献库交叉验证（43 条引用全部存在且被引用）；未做外部联网检索（网络受限）
Report file: 2026-08-22-raven-mcs-tmc-full-review.md
Reviewer mode: full（scientific + writing + format + revision-action synthesis）
```

## 2. Desk Rejection Assessment

- **Paper length**: 通过。IEEEtran 双栏 22 页（正文 + 附录），期刊篇幅合理。
- **Topic compatibility**: 通过。移动群智感知 + 联邦学习 + 非随机选择偏差，完全符合 TMC 范围。
- **Minimum quality**: 通过。结构完整、公式严谨、实验充分、语言已达期刊水准。
- **Policy/anonymity/compliance**: 通过（作者信息完整；无匿名要求）。注：第一作者仍为 `****` 占位符，投稿前需填写。
- **Prompt injection / hidden manipulation**: 未发现。
- **Ethics and reviewability**: 通过。数据均来自公开来源并引用；无人类受试者；无私隐/偏见风险。

**Desk rejection: 否（通过所有检查）**

## 3. Paper Summary And Contribution Map

**Summary**：论文研究移动群智感知（MCS）中的异步联邦数据补全问题。核心洞察是：到达服务器的数据经过"移动机会 R → 实际观测 O → 可用更新 U"三层非随机选择，其分布不一定代表部署目标分布。论文提出 RAVEN-MCS 框架，将补全问题形式化为部署目标风险对齐问题：先分离部署目标风险与到达风险，再通过暴露感知归一化重建目标相关质量，最后通过可行性感知校准（含长期目标债务）将重建参考映射到可行的聚合决策。

**Claimed problem**：异步联邦 MCS 补全中，训练数据分布与部署目标分布因两层三阶段非随机选择而错位。

**Claimed gap**：现有稀疏补全、异步联邦补全、参与感知 FL 各自处理 sparsity/asynchrony/participation，但都未联合建模"感知侧可用性 + 更新侧可用性"如何共同选择进入学习的数据，也未将部署目标作为参考语义。

**Method/contribution map**：
1. 部署目标风险语义（两层三阶段非随机选择的形式化 + Prop 1 非互换性定理）
2. 选择层感知的目标重建（暴露感知归一化，含 Hájék 归一化 + 可用更新校正，Prop 2 一致性定理）
3. 可行性感知的即时与长期目标校准（P2 凸规划 + 目标债务，Thm 1 唯一解存在性）

**Evidence package**：E1 平衡无伤害控制（5 种子）；E2 风险语义实验（NSW-Traffic，20 种子，D_aligned）；E3 主有效性（SensorScope/U-Air，20 种子，结构错配 + 预测风险）；E4 单因子消融（5 组件 × 2 数据集）；774 窗口溯源审计；9666 客户端窗口 Hájék 退化审计；附录完整证明（Prop 1/2、Thm 1、债务界、校准几何）。

**Stated limitations**：显式支持与顺序可忽略性假设；不支持任意隐藏混杂；裁剪是有偏的有限样本稳定器；Use 组件无可测独立效应；Debt 效应小；Local-Hajek 在实验窗口退化为 FedAvg；P2 后验最优性不可重构；不声称移动模型普适性。

## 4. Search And Related-Work Basis

```text
Queries used: 本地引用交叉验证（无外部联网检索，网络受限）
Sources searched: reference.bib（43 条）、正文 \cite 使用
Closest works found: FedAvg [mcmahan2017communication]、FedAsync [xie2019asynchronous]、FedAU [wang2024lightweight]、Sun et al. debiasing [sun2025debiasing]、FedCure [chen2026fedcure]、FedProx/SCAFFOLD [li2020fedprox, karimireddy2020scaffold]、Wang et al. federated MCS completion [wang2026federated]
Unverified related-work risks: 无法联网核实 2024-2026 最新文献是否有更接近的工作（如目标分布对齐的新近研究）；建议投稿前用 ccf-literature-searcher 做一次独立检索
Source-quality screening status: 引用均为 IEEE/ACM/会议正式出版物；部分 2026 条目为 in-press/arXiv 预印本（note 字段标注）
```

## 5. Expected Review Outcome

```text
Expected outcome: 弱接受（Weak Accept）~ 边界正（Borderline Positive）
Main accept signal: 问题定义清晰、三贡献有理论支撑（非互换性 + 一致性 + 唯一解）、实验协议公平（共享 trace、配对种子、Holm 校正）、边界披露诚实
Main reject signal: 经验增益规模小（结构错配 2-4% 改进、预测风险无普遍优势）；"对齐 vs 预测"叙事可能被质疑为"目标被选得太容易"；数据集仅 2 个正式可比块 + 1 个风险实验
Confidence: 3/5（本地全文+附录可审；缺外部联网检索与真实部署验证）
```

## 6. Strengths And Weaknesses

### Strengths

1. **问题形式化清晰**：三层选择（R/O/U）与部署目标/机会层的区分（h(i) vs s(i)）是干净的概念贡献；Prop 1 的非互换性定理为"训练分布 ≠ 部署分布"提供了严格基础。
2. **理论-实验对齐**：每个贡献都有对应证据（Prop 1→E2、Prop 2→E3 结构、Thm 1→附录 + E4）。
3. **实验协议公平**：所有方法共享同一选择 trace、20 配对种子、Holm 校正、预声明比较族；诚实披露基线实现方式（如 TimeAlign-Agg "not an official reproduction"）。
4. **边界披露诚实**：主动承认 Use 无独立效应、Debt 效应小、Local-Hajek 退化、P2 后验不可重构——这在审稿中显著提升可信度。
5. **写作质量高**：术语一致（deployment-target/usable-update/client--stratum）、无 em dash、句子 10-30 词、段落单中心；经润色后已达期刊水准。

### Weaknesses

```text
Weakness 1: 经验增益规模有限
Evidence basis: E3 结构错配改进 3.96%/2.01%（SensorScope）与 2.62%/2.28%（U-Air）；预测风险无普遍优势（仅对 TwoStage-Hajek 的 2.04% 选择性显著）
Reviewer deduction: TMC 审稿人可能质疑"对齐收益是否足以支撑系统复杂度"；核心叙事"主要改善对齐、预测竞争力保持"是诚实的，但也弱化了工程价值主张
Required fix: 增加一个端到端下游任务指标（如补全质量、任务成功率），或展示对齐改进在更长时域/更多窗口的累积效应
```

```text
Weakness 2: 数据集规模与多样性有限
Evidence basis: 仅 2 个正式可比数据集（SensorScope 55 站点、U-Air 36 站点）+ 1 个 E2 风险实验（NSW-Traffic）；无真实部署、无跨时段验证
Reviewer deduction: 审稿人可能要求第三个数据集或真实轨迹验证机会过程；附录已诚实声明"无独立真实轨迹外部验证"
Required fix: 若能获取第三个数据集（如 Pollution、Air Quality 类）做 E3 复制；否则在 limitations 中已充分披露，风险可控
```

```text
Weakness 3: TimeAlign-Agg 基线为自实现
Evidence basis: "implemented in the spirit of [wang2026federated], not an official reproduction"
Reviewer deduction: 审稿人可能质疑该基线的代表性；但论文已诚实披露，且该基线在 E1 中表现最佳（无伤害控制通过），缓解了此担忧
Required fix: 明确列出 TimeAlign 的关键超参数与 wang2026federated 原实现的差异；或联系作者获取官方代码做对齐
```

```text
Weakness 4: 新颖性定位依赖对"部署目标对齐"的再框架化
Evidence basis: Related Work 中 FedAU（参与可改变 FL 目标）、Sun et al.（相关参与偏差）、agnostic FL（对抗混合分布）均部分触及"目标 vs 参与分布"问题
Reviewer deduction: 审稿人可能问：与 FedAU 的"参与改变目标"相比，RAVEN 的增量是否主要是"选择层细化 + 可行性校准"而非全新范式？
Required fix: 在 Related Work 末段更明确地对比 FedAU/agnostic FL 与 RAVEN 的目标定义差异（参考已做，可强化）；可在 rebuttal 中强调"感知侧选择（R/O）在 FedAU 等参与层方法中不可见"
```

## 7. Potentially Missing Related Work

```text
Work: 近 3 年（2024-2026）的部署目标分布对齐 / 目标感知联邦学习 / 因果选择校正新作
Status: unverified（网络受限，未检索）
Why relevant: 论文声称"联合建模感知侧+更新侧选择 + 部署目标参考语义"为新贡献；若有更近的工作提出类似框架，新颖性定位需调整
Overlap: 未知
Needed comparison: 独立联网检索（ccf-literature-searcher），关键词：deployment-target alignment, target-aware federated learning, selection bias crowdsensing, exposure-aware normalization
```

```text
Work: 移动群智感知中的真实机会过程建模（trajectory/opportunity model）
Status: unverified
Why relevant: 论文的机会过程为合成/半合成；真实机会过程文献（如活动识别、时空机会模型）可能提供更强的对照或验证途径
Overlap: 低（论文聚焦统计校正而非过程建模）
Needed comparison: 可选；若时间允许，可增加真实机会数据的外部验证
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| 到达分布不必匹配部署目标 | Abstract, Sec II, Prop 1 | E2: D_aligned 稳定负值（-0.0209~-0.0214），17-18/20 种子负，Wilcoxon p<6e-4 | Strong | 无 | 无 |
| 理想归一化顺序校正恢复兼容目标 | Sec V, Prop 2 | 附录完整证明；E3 结构错配降低 | Strong（理论） | 理论成立，但有限窗口未必精确恢复（已披露） | 无 |
| 校准程序唯一全局最小解 | Sec VI, Thm 1 | 附录证明（A4 凸性） | Strong（理论） | 无 | 无 |
| RAVEN 降低结构错配 | Abstract, Sec VII | E3: 3.96/2.01%（S）、2.62/2.28%（U），Holm 显著 | Strong | 无 | 无 |
| 预测风险保持竞争力且有选择性显著增益 | Abstract, Sec VII | E3: 对 TwoStage-Hajek 的 2.04% 显著改进；其余不显著 | Adequate | "竞争力"是弱断言；审稿人可问为何不普遍更好 | 保持诚实表述即可；可增加 RMSE 分布图 |
| 校正与校准组件有端点/数据集依赖角色 | Abstract, Sec VII | E4 消融：Design 强、Obs 端点特定、Use 无独立效应、Debt 小但一致 | Strong | 无 | 无 |
| Use 校正无清晰孤立效应 | Sec VII, E4 | E4: Use 移除后四端点无显著变化 | Strong（负面结果诚实披露） | 负面结果处理得当 | 无 |
| 无伤害控制通过 | Sec VII, E1 | E1: 相对退化 0.0599%，上界 0.134% < 3% | Strong | 无 | 无 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines**: FedAvg-Window、FedAsync-Window、TimeAlign-Agg、Local-Hájék、TwoStage-Hájék（5 个同骨干基线）+ Inst-Cal/Debt-Cal（过渡）+ 3 个 reference-only。覆盖合理。
- **Ablations**: E4 单因子消融（Design/Obs/Use/Inst/Debt × 2 数据集 × 4 端点），隔离组件贡献。充分。
- **Datasets/benchmarks**: SensorScope、U-Air（E3/E4）、NSW-Traffic（E2）。3 数据集，2 个正式可比块。规模中等。
- **Metrics**: RMSE_μ、Tail RMSE、Δ_group、Δ_c-s、D_aligned。定义清晰、方向标注（lower is better）。
- **Statistical rigor**: 20 配对种子、配对 Wilcoxon、Holm 校正、预声明比较族、数值并列阈值（<1e-12）、负面结果诚实披露。优秀。
- **Robustness/failure cases**: 774 窗口溯源审计、9666 窗口 Hájék 退化审计、P2 可行性认证。超出常规。
- **Implementation details**: 种子、窗口、超参数、裁剪常数、审计流程均有记录。良好。
- **Artifacts and reproducibility**: figure_data CSV 已提供（数据可复现）；make_figures.py 提供（图可复现）；无代码仓库（未声明）。CSV 数据存在，代码缺失是主要可复现性缺口。
- **Limitations**: 充分披露（见 Summary）。

## 10. Multi-Reviewer Panel

```text
Reviewer 1 (Method / Soundness):
Expertise: 统计推断、因果校正、优化理论
Likely score: 7/10（weak accept）
Confidence: 4/5
Main positive signal: A1-A4 假设明确，Prop 1/2 与 Thm 1 证明完整，信息边界（pre-outcome）定义严谨
Main negative signal: 有限窗口下精确恢复的保证弱（已披露）；裁剪的偏差-方差权衡缺少量化
Evidence basis: Sec IV-VI 定义与证明、附录完整证明
Score-change condition: 若补充裁剪活性窗口占比的敏感性分析，+0.5
```

```text
Reviewer 2 (Evidence / Experiment):
Expertise: 移动感知实验、基准评估
Likely score: 6/10（borderline positive）
Confidence: 4/5
Main positive signal: 实验协议公平（共享 trace、配对种子、Holm），负面结果诚实披露，审计充分
Main negative signal: 增益规模小（2-4%）、数据集仅 2 个可比块、TimeAlign 为自实现基线
Evidence basis: Sec VII 全部实验 + 附录表
Score-change condition: 第三个数据集或端到端下游指标，+0.5~+1
```

```text
Reviewer 3 (Novelty / Positioning):
Expertise: 联邦学习、分布对齐
Likely score: 6/10（borderline）
Confidence: 3/5
Main positive signal: 三层选择形式化 + 部署目标参考语义的联合是清晰增量；与非互换性定理结合有理论深度
Main negative signal: FedAU/agnostic FL 部分触及"目标 vs 参与分布"；新颖性增量需在 rebuttal 中强调感知侧选择层（R/O）不可见性
Evidence basis: Sec II related work、Sec I 贡献
Score-change condition: 独立联网检索确认无更近重叠工作后，+0.5
```

```text
Reviewer 4 (Writing / Clarity):
Expertise: 学术写作
Likely score: 8/10（accept）
Confidence: 4/5
Main positive signal: 术语一致、结构清晰、figure/table 有明确 takeaway、无 em dash、句子 10-30 词
Main negative signal: 个别长段（Discussion 2.1）信息密度高；附录标记列举略长
Evidence basis: 全文检查
Score-change condition: 无实质扣分项
```

```text
Reviewer 5 (Ethics / Reproducibility):
Expertise: 可复现性、数据伦理
Likely score: 7/10（weak accept）
Confidence: 4/5
Main positive signal: 数据来源公开且引用、无隐私/人类受试者风险、限制披露充分、figure_data 可复现
Main negative signal: 无代码仓库；P2 求解器实现细节不完整（求解器类型、容差设置未明示）
Evidence basis: Sec VII、附录、文件清单
Score-change condition: 提供代码仓库或求解器实现细节，+0.5
```

```text
AC / Meta-Reviewer:
Agreement: 4/5 评审认为无致命缺陷；2 位 borderline（6/10），2 位 weak accept（7/10），1 位 accept（8/10）
Disagreement: 主要分歧在"增益规模是否足以支撑贡献"（Reviewer 2）vs "理论深度+诚实边界是否足够"（Reviewer 1/5）
Decisive positive axis: 问题定义 + 理论严谨 + 实验公平 + 边界诚实
Decisive negative axis: 经验增益小 + 数据集有限 + 部分新颖性增量需辩护
Unresolved evidence: 无外部联网检索确认最新相关文献；无真实部署验证
AC stance: 弱接受（Weak Accept）。论文理论扎实、实验诚实、写作优秀；但经验增益规模与数据集多样性不足以支持强接受。建议 major revision 补充第三个数据集或端到端指标，并在 rebuttal 中强化与 FedAU/agnostic FL 的区分。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | moderate | 经验增益规模小（2-4% 结构错配、预测无普遍优势） | Sec VII E3 | Significance | experiment | 增加端到端下游指标或长时域累积效应分析 | ccf-experiment-designer | +0.5~+1 overall |
| C2 | moderate | 数据集仅 2 个正式可比块 | Sec VII | Evidence | experiment | 补充第三数据集 E3 复制或真实轨迹验证 | ccf-experiment-designer | +0.5~+1 |
| C3 | minor | TimeAlign-Agg 为自实现基线 | Sec VII 1394-1406 | Evidence | experiment | 明确超参数差异；或联系原作者代码对齐 | ccf-experiment-designer | +0.5 |
| C4 | minor | 新颖性增量需强化与 FedAU/agnostic FL 的区分 | Sec II | Positioning | related-work | 强化感知侧选择层（R/O）的独特性论述 | ccf-paper-writer | +0.5 |
| C5 | minor | 无代码仓库、P2 求解器细节不完整 | Sec VII/附录 | Reproducibility | reproducibility | 提供代码仓库或求解器实现细节 | ccf-submission-checker | +0.5 |
| C6 | minor | 第一作者为 **** 占位符 | Title page | Compliance | writing | 填写作者姓名 | ccf-submission-checker | 无分数影响 |
| C7 | minor | 无法联网确认 2024-2026 最新相关文献 | Sec II | Positioning | related-work | 投稿前独立检索 | ccf-literature-searcher | +0.5（若无重叠） |

## 12. AC / Meta-Review

- **Reviewer consensus**: 无致命缺陷共识；2 borderline、2 weak accept、1 accept。
- **Reviewer disagreement**: 增益规模 vs 理论深度的权重分歧。
- **Decisive acceptance axis**: 问题形式化 + 理论严谨 + 实验公平 + 边界诚实。
- **Decisive rejection axis**: 无单一致命项；若经验增益被视为"工程增量不足"，可降至 reject，但理论贡献支撑其不落至此。
- **AC stance**: 弱接受，建议 major revision（补充证据 + 强化定位）。
- **Discussion risks**: 审稿人可能围绕"对齐收益的现实意义"展开辩论；诚实边界披露是主要防线。

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 4 | 3 | Sec I-II：三层选择形式化 + 部署目标参考语义 + 非互换性定理 | 与 FedAU/agnostic FL 的增量需在 rebuttal 强化（C4）；联网确认无更近工作可 +0.5 |
| Soundness | 4 | 4 | Sec IV-VI：A1-A4、Prop 1/2、Thm 1、附录完整证明 | 有限窗口精确恢复弱（已披露）；裁剪偏差-方差权衡缺量化 |
| Evidence | 4 | 4 | Sec VII：E1-E4、20 配对种子、Holm、审计 | 数据集 2 块 + 增益小（C1/C2）；第三数据集可 +0.5 |
| Significance | 3 | 3 | 问题重要但增益规模小、数据集有限 | 端到端指标或长时域分析可 +0.5（C1） |
| Clarity | 5 | 4 | 全文：术语一致、无 em dash、结构清晰、figure/table takeaway 明确 | 无 |
| Reproducibility | 4 | 4 | figure_data CSV + make_figures.py 可复现图表；20 种子、超参数、审计记录 | 无代码仓库、P2 求解器细节缺失（C5），补齐可 +0.5 |
| Ethics / Limitations | 5 | 4 | 数据公开引用、无私隐风险、限制披露充分、负面结果诚实 | 无 |

**Overall:** 7/10  | **Scholarly Confidence:** 3/5

**Recommendation:** weak-accept（major revision 后可能升至 accept）
**Verdict:** 补第三数据集/端到端指标 + 强化新颖性定位 + 提供代码/求解器细节，可 +1~1.5 至 8/10。

## 14. Questions For Authors

1. 结构错配 2-4% 的改进在真实 MCS 部署中对应什么下游收益？（C1）
2. 若 TimeAlign-Agg 超参数与原实现不同，结果对超参数选择的敏感性如何？（C3）
3. 裁剪常数 a_max/d_max/p_min 在实验中的实际活跃窗口占比？（Soundness）
4. P2 求解器类型与容差设置？（C5）
5. 是否考虑真实机会过程数据的验证？（C2）

## 15. Score Revision Criteria

```text
Raising the score would require: 第三数据集 E3 复制（+0.5）；端到端下游指标（+0.5）；代码仓库 + 求解器细节（+0.5）；联网确认无更近重叠文献（+0.5）
Lowering the score would be triggered by: 审稿人认定增益规模为"工程增量"且理论贡献不足以支撑（-1~-2）；发现未引用的高度重叠近作（fatal 风险）
Concerns unlikely to change before submission: 数据集多样性（需新数据采集，短期难补）；真实轨迹验证（需外部数据）
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: 高
Action: 补充第三数据集 E3 复制或端到端下游指标
Owner skill: ccf-experiment-designer
Input needed: 现有 figure_data、数据集获取渠道
Expected output: 新增实验块 + 结果表
Handoff required: yes
```

```text
Priority: 中
Action: 强化 Related Work 中与 FedAU/agnostic FL 的区分；润色新颖性论述
Owner skill: ccf-paper-writer
Input needed: 当前 Sec II 文本
Expected output: 修改后的相关段落
Handoff required: no
```

```text
Priority: 中
Action: 独立联网检索 2024-2026 相关文献，确认新颖性定位
Owner skill: ccf-literature-searcher
Input needed: 论文主题关键词
Expected output: 检索报告 + 潜在重叠文献
Handoff required: yes
```

```text
Priority: 中
Action: 提供代码仓库或 P2 求解器实现细节
Owner skill: ccf-submission-checker
Input needed: 代码/求解器配置
Expected output: 可复现性补充
Handoff required: no
```

```text
Priority: 低
Action: 填写第一作者姓名
Owner skill: ccf-submission-checker
Input needed: 作者信息
Expected output: 完整作者块
Handoff required: no
```

```text
Checks run: 结构完整性、引用交叉验证、数字一致性（E1/E2/E3/附录）、术语一致性、实验协议公平性、理论-证据对齐、边界披露
Checks skipped: 外部联网检索（网络受限）；真实部署验证（无数据）；代码运行复现（无代码）
Unresolved risks: 新颖性定位依赖外部检索确认；增益规模的工程意义是主要辩论点
```
