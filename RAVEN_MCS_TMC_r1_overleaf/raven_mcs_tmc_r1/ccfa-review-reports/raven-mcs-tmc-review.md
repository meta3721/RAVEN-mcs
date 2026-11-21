# CCF-Paper-Reviewer 标准审稿报告 — RAVEN-MCS（IEEE TMC 投稿）

> 按 `ccf-paper-reviewer` 技能 `references/fixed-output-format.md` 标准模式 16 节输出；评分按 `calibration-and-rank.md`；审稿人面板按 `reviewer-panel.md`；写作分按 `writing-review/writing-review-rubric.md`。审阅材料：压缩包 `RAVEN_MCS_TMC_r1_overleaf.zip` → `raven_mcs_tmc_r1/`（main.tex 2517 行、appendix.tex 1607 行、supplemental.tex、reference.bib、figures/*.pdf）。正文行号以 main.tex 为准。

---

## 1. Report Metadata

```text
Review date:            2026-02-12
Target venue:           IEEE Transactions on Mobile Computing (TMC)（README 明确标注）
Paper title:            RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data
                        Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials:        main.tex、appendix.tex（完整证明）、supplemental.tex、reference.bib、
                        figures/*.pdf（10 图）
Search basis:           未执行外部检索；相关工作覆盖依据参考列表与引言/相关工作节
Reviewer mode:          full（科学 + 写作 + 格式 + 可复现）+ venue-fit（TMC 系统/移动感知期刊）
Manuscript version:     TMC 返修稿（r1）；匿名投稿（作者 **** 占位）
Evidence boundary:      LaTeX 源码与数值已核验；PDF 渲染与图片视觉未核验（模型不能读图）；
                        补充材料统计数据未逐条复现
```

## 2. Desk Rejection Assessment

| Check | Status | Evidence / Consequence |
|---|---|---|
| Paper length | pass | IEEEtran journal；正文 + 独立补充 PDF（supplemental.tex 单独编译）符合 TMC 做法 |
| Topic compatibility | pass | 移动群智感知 + 联邦学习 + 非随机选择，正属 TMC 核心范围 |
| Minimum quality | pass | 问题/模型/重建/校准/理论/评估/讨论/结论 + 完整证明附录齐全 |
| Policy / Anonymity | pass（投稿时） | 作者 **** 占位符合匿名；camera-ready 前必须补全作者/单位 |
| Prompt injection | pass | 未发现针对审稿人/LLM 的隐藏指令 |
| Ethics / Reviewability | pass | 公开数据集（SensorScope/U-Air/NSW/T-Drive 均给 DOI/链接），隐私边界有讨论 |

**Desk rejection risk: none**

## 3. Paper Summary And Contribution Map

**一句话**：RAVEN-MCS 把"窗口异步联邦数据补全"重新定义为**部署目标风险对齐**问题——服务器在窗口关闭时才更新（区别于 FedAsync 即时更新），从合法的预结果 R/O/U 历史重建与部署目标相关的质量，并在当前可行聚合窗口内校准该参考；当部署律与到达律不一致时，两者风险不可互换。

- **问题**：MCS 补全在三级（opportunity/observation/usable-update）两级非随机选择下训练，到达律无需匹配公开部署目标。
- **Gap**：现有方法以"可用更新频率/到达律"为参考语义，未对齐部署目标风险。
- **贡献**：(1) 目标风险 vs 到达风险不可互换的形式化（Prop 1）；(2) 分层选择感知目标重建（Prop 2，O/U 三层分离 + 局部 Hájek 归一化）；(3) 可行感知校准（P2 唯一可解 Thm 1；裁剪 plug-in 为 Lipschitz 扰动 Prop；长期目标债务）；(4) 有限样本聚合覆盖率证书 + 候选 Gate 审计（Thm agg-lcb 等）。
- **证据包**：E1 无伤害对照、E2 风险不可互换、SensorScope/U-Air 的 E3/E4 支持条件 Design、T-Drive 真实机会 replay（非排名）、覆盖率压力审计。
- **诚实界限**：非通用 RMSE 优势；Design 在 U-Air 逆转并公开；usable-update 无孤立效应；债务效应极小；覆盖率证书在 U-Air 自然可用性下不成立。

## 4. Search And Related-Work Basis

```text
Queries used:       无外部检索
Sources searched:   无
Closest works:       FedAsync、FedAU（wang2024lightweight）、ObsUse、TwoStage-Hájek、
                     FedCure（显式不纳入）、FedVARP/Anchor/agnostic FL（参与偏差）、
                     federated conformal（lu2023, plassier2023）
Unverified risks:    若干 2025/2026 文献存在性/卷期需核验（见 §7、P2）
```

## 5. Expected Review Outcome

```text
Expected outcome:   Borderline positive → lean accept（6.5–7/10）；审稿人预计要求 minor–major 澄清
Main accept signal:  方法严谨、统计规范（配对 Wilcoxon+Holm、预注册、记录阴性）、局限诚实、可复现包
Main reject signal:  主外部端点（worst-group RMSE）仅"非劣"非"优于"；组件消融多为非显著；
                     仅 2 数据集支撑主结论；覆盖率证书在关键条件下经验无效
Confidence:          4/5（源码全文 + 完整证明 + 统计协议清楚；未逐条复现数值、未读图）
```

## 6. Strengths And Weaknesses

### Strengths
1. **理论上干净、证明完整**：Prop 1（两风险不可互换）、Prop 2（分层重建一致性）、Thm 1（可行集非空 + 唯一极小，PSD Hessian 论证）、Prop practical_plugin（裁剪稳定性，明确非无偏 claim）、Thm agg-lcb（有限样本覆盖率，含交换性/零点裁剪/false-safe 边界）——全部在 appendix 有完整证明，每条都写明不声称的范围。
2. **统计纪律极强**：配对 Wilcoxon + Holm 校正、20 seeds、预注册 $+0.5\%$ mean-relative 非劣规则、recorded negative（under-served-block 检查测试集未打开）、冻结目标/协议/分组、$10^{-12}$ 计为平手。
3. **诚实且不自洽于 SOTA**：U-Air Design 逆转被主动报告并归因于支持不兼容而非 plug-in 失败（Oracle Design 跟踪估计 Design）；usable-update 无孤立效果、债务效应 $0.002\%$–$0.014\%$ 被如实标注"远低于 $0.5\%$ 实践阈值"；覆盖率在 U-Air $a=1.00$ 经验有效性 $0.750$ 未达 $95\%$ 也照实报告。
4. **支持条件 Design 有原则**：Design 仅在目标支持兼容时用（SensorScope on / U-Air off），不强行套用单一机制。
5. **可复现**：发布 `RAVEN_MCS_PUBLIC_REPRO_R1`（配对 seed、冻结目标图、协议配置、事件文件与索引、哈希校验器）。

### Weaknesses（每条含证据与修复）
**W1（major，实证强度）** — 主外部端点只"非劣"不"优于"，实证亮点主要是结构性对齐而非预测提升。
- 证据：worst-group RMSE"与 FedAU/ObsUse 可互换（TEST −0.01%/+0.05%、U-Air +0.48%/+0.44%，均在 $+0.5\%$ 规则内）"；SensorScope 结构改进小（Δ_group 3.96%、Δ_c-s 2.01%）；U-Air 下 Design-off 才是主分配。
- Reviewer deduction：若主要增益是"目标对齐"而预测/最差组未胜过简化基线，读者会质疑：这套复杂机制换来的工程/计算/可维护成本，回报是否只限于结构度量上的小改善？
- Required fix：明确"结构对齐为主、预测非劣"的定位；或补端到端/下游价值分析（按部署目标加权的实际决策收益）。

**W2（major，泛化基线）** — 主 E3/E4 结论仅 2 个"科学可比"数据集；NSW-Traffic 只用 E2，T-Drive 只是机会 replay 不排名。
- 证据：Table `tab:datasets`；"E3 main 仅 SensorScope/U-Air"。
- Required fix：补第 3 个 E3/E4 类数据集；或给出"需要何种数据规模/类型才能支撑跨场泛化"的判据。

**W3（moderate，机制贡献占比）** — E4 组件消融多数不显著：Obs/Use/Inst/Debt 多为非显著或相反符号；唯一大效应（Design）在 U-Air 逆转。
- 证据：Table `tab:e4_ablation`（Use 两数据集全非显著；Obs/Inst 端点权衡；Debt 显著但量级 $<0.5\%$）。
- Required fix：明确区分"系统级耦合效应"与"组件边际贡献"，对非显著组件降级定位。

**W4（moderate，覆盖率证书操作性）** — 覆盖率 Gate 被审慎声明"不用于切换 Design"，且在关键条件下经验无效。
- 证据：U-Air $a=1.00$ 有效性 $0.750$；"Gate does not switch Design in Algorithm~window_close"；"not used in E3"。
- Required fix：给证书/Gate 一个确实会触发/使用的操作场景，或明确定位为"诊断/监测组件"。

**W5（minor，可读性）** — 摘要与引言符号过密（R/O/U、Design、P2、debt、CERTIFIED、window-close），单一最精炼贡献不易快速抓取。
- 证据：Abstract（L65–83）连续术语；novelty 定位（非 IPW/Hájek）到 L225–229 才显式出现。
- Required fix：摘要用一句朴素的话讲"做什么、为何新、有何证据"；引言早段点明"novelty = 目标语义 + 分层合法历史 + 有限支持校准的组合"。

## 7. Potentially Missing / Unverified Related Work

| Work | Status | Why relevant | Overlap | Needed comparison |
|---|---|---|---|---|
| FedAU / participation debiasing | 已述 | 最强参与基线 | 高 | 已对比，非劣——补"何时优于 FedAU"判据 |
| FedCure (AAAI'26) | 显式不纳入 | 半异步参与偏差 | 中高 | 建议纳入或给出更强排除理由 |
| federated conformal 覆盖率 | 已述 | 与覆盖率证书相关 | 中 | 区分"聚合覆盖率"与"逐点 conformal" |
| 若干 2025/2026 文献 | **unverified** | 存在性与卷期 | — | 见 P2 引文核验 |

## 8. Claim-Evidence Audit（节选）

| Claim | Where | Evidence | Strength |
|---|---|---|---|
| 目标风险 ≠ 到达风险 | Prop 1 + 证明 | E2 + T-Drive replay | **strong** |
| 理想顺序重建恢复兼容目标 | Prop 2 + 证明（条件限定） | 支持/可识别条件下 | strong |
| 校准唯一可解 | Thm 1 + 证明（PSD Hessian, λ_β>0） | 数学 | strong |
| 裁剪 plug-in 是稳定扰动（非无偏） | Prop practical_plugin | 保守 C1，自限不适用 U-Air | strong |
| Design 减少结构失配且 RMSE 竞争 | E3 | SensorScope 3.96%/2.01%；worst-group 非劣 | **moderate**（量小、仅为非劣、1 数据集为正） |
| coverage 有限样本 LCB（Gate） | Thm agg-lcb + 审计 | pooled 0.959，但 U-Air a=1.00 0.750 | **moderate**（条件成立时对；关键条件不成立） |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines**：同骨干 FedAvg/FedAsync/TimeAlign/Local-Hájek/TwoStage-Hájek + FedAU/ObsUse-Window（明确"非官方复现"）；共享选择 trace、配对 seed。✓
- **Datasets**：主 E3/E4 仅 2 个；NSW-Traffic 仅 E2；T-Drive replay。⚠️ 泛化薄。
- **Metrics**：RMSE_μ、WorstGroupRMSE、Δ_group/Δ_c-s、Tail_RMSE，定义清晰。✓
- **Statistical rigor**：配对 Wilcoxon + Holm、20 seeds、预注册规则、记录阴性。**强于多数论文**。✓
- **Robustness**：E4 单因子消融 + 覆盖率压力审计（availability 0.20–1.00）。✓（多数消融非显著，见 W3）
- **Reproducibility**：公开包 + 哈希校验器；P2 解的最优性自陈"不回溯证明精确最优"。⚠️ 需独立复现确认。
- **Limitations**：诚实（支持条件、非因果、覆盖不写 U-Air 自然可用性、replay 非端到端）。✓

## 10. Multi-Reviewer Panel

| Reviewer | Score | Main positive | Main negative | Evidence |
|---|---|---|---|---|
| Best-Justified | 7/10 | 方法严谨、目标对齐语义新、统计诚实一流 | — | Prop 1/2、Thm 1/agg-lcb |
| Critical | 5/10 | — | 主端点仅"非劣"、组件多非显著、2 数据集 | E3/E4、§9 |
| Method/Soundness | 7/10 | 证明完整、边界诚实、不无偏声称 | 记号密集 | appendix 全证明 |
| Evidence/Ablation | 5/10 | 配对+Holm+预注册 | 无预测性"赢"；Design 在 U-Air 逆转 | tab:e4_ablation |
| Novelty/Positioning | 6/10 | 明确区别于 IPW/Hájek 组合 | 需精确对照 FedAU/FedCure | L225–229、§7 |
| Writing/Clarity | 5/10 | 结构清晰 | 摘要符号过密、单一贡献不突出 | Abstract L65–83 |
| Ethics/Reproducibility | 6/10 | 可复现包、隐私讨论 | 引文若干待核验 | §7、P2 |
| Domain (MCS/TMC) | 6/10 | 问题真实（TMC 核心） | 无端到端真实联邦/移动验证 | T-Drive replay 局限 |
| AC | **6.5–7/10** | 见 §12 | | |

## 11. Concerns Table

| ID | Sev | Concern | Evidence | Fix class | Owner | Score-change |
|---|---|---|---|---|---|---|
| C1 | major | 主端点仅非劣非优于；增益多为结构性且小 | E3 数字 | requires-new-result / claim-qualification | experiment-designer | −（表达即可防降） |
| C2 | major | 主结论仅 2 数据集 | tab:datasets | requires-new-result | experiment-designer | +可泛化 |
| C3 | moderate | 组件消融多非显著，贡献占比不清 | tab:e4_ablation | writing / claim-qualification | paper-writer | 表述定位 |
| C4 | moderate | 覆盖率 Gate 操作价值与条件性 | U-Air 0.750；"not used" | writing / method | paper-writer | 定位 |
| C5 | minor | 摘要/引言可读性、novelty 单句化 | Abstract | writing | paper-writer | +Clarity |
| C6 | minor | 引文 2025/2026 卷期/存在性核验 | reference.bib | integrity | integrity-auditor | 无分变 |
| C7 | minor | camera-ready 作者/单位补全 | **** 占位 | format | submission-checker | 投稿前 |

## 12. AC / Meta-Review

- 共识：方法学、统计规范、诚实性是显著强度；实证显著性与泛化范围是主要扣分。
- 分歧：Best-Justified 认为目标风险对齐语义已构成充分贡献；Critical 认为无预测性/下游增强则机制复杂度与回报不成比例。
- 决定性接受轴：严谨且可复现的目标风险对齐方法学（区别于纯 IPW/Hájek）。
- 决定性拒绝轴：仅"非劣"+2 数据集+多组件非显著，可能被审为"理论厚、实证薄"。
- **AC stance：Borderline positive（6.5–7/10）→ lean accept**。建议作者按 C1/C2 补强实证或明确"结构对齐为主、预测非劣"定位；可接受 minor–major 修改后再审。

## 13. Quantitative Scores

| Dimension | Score(1-5) | Conf | Evidence basis | Deduction / condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 4 | 4 | 目标风险对齐 + 分层合法历史 + 有限支持校准；区别于 IPW/Hájek | 组合型新颖 |
| Soundness | 4 | 4 | 完整证明、边界诚实、不无偏 | 稳 |
| Evidence | 3 | 4 | 统计规范强，但主点非劣、2 数据集、多组件非显著 | 补第 3 数据集/下游分析 +1 |
| Significance | 4 | 4 | TMC 核心问题、目标风险语义普适 | 实证收益小 → 或 3–4 |
| Clarity | 4 | 3 | 结构清晰、术语稠密 | 摘要/novelty 单句化后 5 |
| Reproducibility | 4 | 4 | 公开包 + 哈希校验器 | 独立复现未确认 |
| Ethics/Limitations | 5 | 4 | 罕见诚实的边界披露 | — |
| **Overall** | **6.5/10** | 4 | borderline positive → lean accept | C1/C2 后 7–7.5 |
| **Recommendation** | **borderline / weak-accept** | | | |

## 14. Questions For Authors

1. 除 RMSE/结构度量外，能否量化"部署目标对齐"带来的端到端/下游收益（按目标加权的实际决策改善）？
2. E3/E4 是否可加第 3 个"科学可比"数据集以支撑跨场泛化？
3. 覆盖率 Gate 既然不切换 Design，其拟采用的操作场景为何？U-Air 自然可用性下证书不成立时，（a）仍仅作诊断（b）或有其他动作？
4. FedCure（AAAI'26）能否纳入，或给出更充分的不纳入理由？
5. 若干 2025/2026 文献（如 wang2023transformer 的 year 字段与键不一致；morishita2026who、islam2025seafl 等）请提供 DOI/链接以便核验。

## 15. Score Revision Criteria

```text
Raising the score would require:
  - 补第 3 数据集或端到端/下游价值分析（C2/C1）→ +0.5~+1 Evidence/Overall
  - "结构对齐为主、预测非劣"定位 + 摘要可读化（C3/C5）→ +Clarity
  - 引文核验（C6）→ +Reproducibility
Lowering the score would be triggered by:
  - 复核发现覆盖率/重建数值与源数据不一致
  - 非劣性规则被质疑为选择性阈值（补充已预注册，风险低）
Concerns unlikely to change before submission:
  - 核心机制复杂度、2 数据集规模（需新实验）
```

## 16. Action Plan And CCFA Handoffs

| Priority | Action | Owner skill | Input | Handoff |
|---|---|---|---|---|
| P1 | 定位重构（结构对齐为主、预测非劣）+ 摘要单句贡献 | ccf-paper-writer | 本文 §6/W1、W5 | yes |
| P1 | 第 3 数据集或端到端/下游价值分析 | ccf-experiment-designer | 需用户提供数据 | yes |
| P2 | 覆盖率 Gate 操作场景明确化 / 定位诊断 | ccf-paper-writer | 本文 C4 | no |
| P2 | 引文卷期与存在性核验 | ccf-integrity-auditor | reference.bib | no |
| P2 | camera-ready 作者/单位补全 | ccf-submission-checker / user | — | no |
| P2 | P2 求解器最优性与可复现包独立复现核验 | user / ccf-integrity-auditor | 复现包 | no |

```text
Checks run:      main.tex 全文、appendix.tex 证明、supplemental.tex、reference.bib、README、数值抽查
Checks skipped:  PDF 渲染、图片视觉、figure_data CSV 逐条复算、外部文献检索
Unresolved risks: 引文存在性、独立数值复现、图片质量
```
