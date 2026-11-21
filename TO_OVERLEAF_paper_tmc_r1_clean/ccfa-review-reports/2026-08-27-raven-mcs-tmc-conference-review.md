# CCFA 论文评审报告 — RAVEN-MCS（压缩稿 + G6 入正文后独立复审，2026-08-27）

## 1. Report Metadata

```text
Review date: 2026-08-27
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A, regular paper
Paper title: RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex（投稿主文）
  supplemental.tex + appendix.tex; main.pdf 16 页; supplemental.pdf 8 页
  reference.bib; Table II; W1 / T-Drive / E4 图
  post_review/G1–G6 DECISION.md 与 VAL_GATE（主张边界，不升格未发表赢面）
  对照 2026-08-26 评审（当时主文未压、附录未拆、G6 未入正文）
Search basis: IEEE Computer Society Author Guidelines; 第三方摘录 TMC 常规 12 页 / 投稿可至 18 页 MOPC / supplemental 必须单独文件。未把稿件私有句子贴进检索。Shimodaira 2000、Robins et al. 1994、FedAU 2024 沿用已核出处。
Report file: ccfa-review-reports/2026-08-27-raven-mcs-tmc-conference-review.md
Reviewer mode: full（scientific + writing + format + revision-action）
Material delta vs 2026-08-26: G6 负结果写入摘要/RQ2/新小节/讨论/结论; Shimodaira/Robins 已引; 附录外置; 主 PDF 23→16 页; Fig. 3–4 迁 supplemental。
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: pass (submission); uncertain (published 12-page / MOPC)
Evidence: 本地 latexmk 主文 16 页（正文约至 p.14，参考文献 p.15–16）≤ 18 页投稿上限。附录在独立 supplemental.pdf（8 页）。发表基准仍是 12 双栏页含参考文献/简历。
Consequence: 不因页数 desk reject。录用后可能超页收费。
Required action: 投稿上传两个 PDF; 若要避开 MOPC 需再压约 4 页。
```

```text
Check: Topic compatibility
Status: pass
Evidence: 稀疏 MCS 补全 + 窗口化异步联邦 + 非随机选择 + 出租车机会层，落在 TMC mobile environments / algorithm-protocol。
```

```text
Check: Minimum quality
Status: pass
Evidence: Abstract–Conclusion、三条贡献、理论、主表、20 配对种子、Holm、+0.5% 非劣、Design 反转、欠服务块负结果、T-Drive 不排名均在正文。
```

```text
Check: Policy / anonymity / compliance
Status: uncertain
Evidence: 作者行仍为 `**** and Anfeng Liu`。TMC 通常单盲，占位名不是双盲违规，是未完成投稿包。
Consequence: 行政修补。
Required action: 填第一作者。
```

```text
Check: Prompt injection / ethics
Status: pass
Evidence: 未见隐藏审稿指令。公开环境/空气/出租车数据; 讨论含倾向得分元数据隐私句。
```

**Desk rejection: 否。风险 low。** 进入完整评审。

## 3. Paper Summary And Contribution Map

**一句话：** 窗口化异步联邦 MCS 补全被写成部署目标风险对齐；Design 按数据集门控；经验上独特赢面仍是作者定义的结构 L1；TMC 更在乎的 RMSE 与四块 WorstGroupRMSE 对改编 FedAU/ObsUse 非劣；预注册欠服务块是 VAL 负结果。

- **Claimed problem:** 到达律不必等于公开部署目标 \(\mu\)；感知侧 \(R/O\) 与更新侧 \(U\) 顺序选择。
- **Claimed gap:** 稀疏补全、异步补全、参与感知 FL 都不联合建模三层选择，也不处理有限窗可实现性。
- **Method map:** (1) 风险语义 + Prop. 1；(2) 三层重建 + Prop. 2，门控是 Contrib. 2 的实践实现；(3) P2+债务 + Thm. 1 + Prop. 3。正好三条贡献。
- **Evidence package:** E1 无伤害；E2 \(D_{\mathrm{aligned}}\approx-0.021\)；E3 门控主表（FedAU/ObsUse/WorstGroupRMSE）；欠服务块 VAL 表（负结果）；E4 保留 U-Air Design 反转；T-Drive 真实 \(R\)（TV 0.142），不排名。
- **Stated limitations:** 裁剪非无偏；A5 不覆盖 U-Air 全 Design；Use 无孤立效应；Debt 0.002%–0.014%；Path A 失败；T-Drive 证据等级 A；20 seed 不是独立城市；P2 只证可行性；欠服务块 TEST 未开。

## 4. Search And Related-Work Basis

```text
Queries used:
  IEEE Transactions on Mobile Computing page limit supplemental Computer Society
  （沿用已核）Shimodaira 2000; Robins et al. 1994; FedAU Wang & Ji ICLR 2024
Sources searched: Web search; Computer Society Author Guidelines; 第三方 TMC 页限摘录。官方 TMC Author Information HTML 本轮未直接打开。
Closest works found:
  Shimodaira 2000: 已在 §II 引用为密度比 / 目标风险加权篱笆。
  Robins et al. 1994: 已在 §II 引用为顺序 IPW 篱笆。
  FedAU 2024: 主表是窗口改编，不是官方复现（caption 已写）。
Unverified related-work risks:
  Byrd & Lipton 2019（ICML; IW 在过参数化网络中可消失）仍未引；与有限容量补全不完全同机制。
  tian2026reshaping / qiao2025asmafl / chen2026dvafl 仍未进入本稿（unverified，不当已发表对照）。
Source-quality screening status: 未使用 MDPI。页限来自 CS 通用政策 + 第三方摘录，不是本轮官方 TMC HTML。
```

## 5. Expected Review Outcome

```text
Expected outcome: Borderline positive / 弱偏收讨论
Main accept signal: 问题切分清楚; Design 反转与欠服务块负结果公开; 改编 FedAU/ObsUse 与四块 WG 在主表; T-Drive 证据等级 A; 附录已外置; 16 页可投。
Main reject signal: RMSE 与四块 WorstGroupRMSE 上与改编 FedAU/ObsUse 非劣不是赢; U-Air 默认 = 关 Design; 第二条预注册外部端点同样未赢。
Confidence: 4/5
```

相对 2026-08-26 **overall 维持 6**。本轮行政风险下降（附录外置、摘要压缩、G6 诚实写入）。Novelty 因 Shimodaira/Robins 划界可从 3 提到 4，但 Significance 仍锁在 3，**不能把总分抬到 7**。

## 6. Strengths And Weaknesses

**Strengths**

- 到达律 ≠ 部署目标律仍是合法 TMC 问题；E2 \(D_{\mathrm{aligned}}\) 跨方法为负。
- 门控、U-Air Design 反转、欠服务块 VAL 失败都写进摘要/主表/讨论，没有把 −0.44% 写成赢。
- 主表含改编 FedAU/ObsUse 与四块 WorstGroupRMSE；明确不是 Holm 赢 FedAU。
- T-Drive 把 \(R\) 写成真实轨迹，禁止系统/排名过度声明。
- Prop. 3 / A5 把裁剪 plug-in 收成稳定扰动，并声明不解释 U-Air 反转。
- 主/补分包符合 Computer Society “附录须独立 supplemental” 的投稿形态。

**Weaknesses**

```text
Weakness: 对改编 FedAU/ObsUse，外部预测端点是非劣；独特赢面仍是 Δ_group / Δ_c-s。
Evidence basis: Table II。U-Air RMSE 门控 1.1131 vs FedAU 1.1128 vs ObsUse 1.1120；WorstGroupRMSE 1.1703 vs 1.1701 vs 1.1692。
Reviewer deduction: TMC 读者会问为什么不直接用参与重加权。分层 R/O/U 的增量没有落在部署 RMSE/最差组上。
Required fix: 新的预注册外部端点上赢且 FedAU 复制不了；或把贡献明确收成「结构对齐 + 支撑门控」，接受预测打平。写作改不了这一条。
```

```text
Weakness: 预注册欠服务块同样未赢改编 FedAU/ObsUse。
Evidence basis: Table IV; VAL_GATE。SS +0.05%/+0.15%；UA −0.44%/−0.27%。TEST 未开。
Reviewer deduction: 关闭了既定 6→7 路径。正文诚实，故不降到 5。
Required fix: 禁止升格、禁止打开 TEST。新家族才能冲击 7。
```

```text
Weakness: U-Air 默认关掉 Design。
Evidence basis: Abstract; Table II; Path B DECISION。
Reviewer deduction: 同情者读成支撑门控; 挑剔者读成 test 调参。
Required fix: 保持现有时间线（VAL 规则、一次 TEST）。不要再改默认。
```

```text
Weakness: 无 Algorithm 环境; 作者占位; 无代码可用性句; 四块逐组 RMSE 表未进 supplemental。
Evidence basis: 全文无 \begin{algorithm}; \author{****}; G2 协议要求逐组表放 supplement，appendix.tex 无 RMSE_block 表。
Reviewer deduction: 方法难复述; 行政未完成; 外部端点透明性不足。
Required fix: Algorithm 1; 填作者; 一句代码/数据可用性; 把已有 per_seed RMSE_block 收成 supplemental 表。
```

## 7. Potentially Missing Related Work

```text
Work: Byrd & Lipton (2019). What is the effect of importance weighting in deep learning? ICML, PMLR 97:872–881.
Status: searched
Why relevant: 可解释「结构对齐不必降低 RMSE」。
Overlap: 机制不完全相同（过参数化分类 vs 有限容量补全）。
Needed comparison: 可选一句篱笆，不是必须实验。
```

```text
Work: FedCure (chen2026fedcure) official system; official (unadapted) FedAU.
Status: user-provided citation / not run
Why relevant: 半异步参与偏置; 官方参与重加权。
Overlap: 主表已是窗口改编 FedAU。
Needed comparison: FedCure 未跑可保留为局限。官方 FedAU 可能降低现稿（若结构+RMSE 双赢）。
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| 到达律与部署目标风险不可互换 | Abstract; Prop. 1; E2 | \(D_{\mathrm{aligned}}\approx-0.021\)，20 seeds | strong | 问题成立 | 保持 |
| 理想顺序校正恢复兼容目标 | Abstract; Prop. 2 | 附录证明; A1–A3 | adequate | 理想而非 plug-in | 已限定 |
| 裁剪 plug-in 是稳定扰动 | Abstract; Prop. 3 | A5; \(C_1\) 保守 | adequate | 不解释 U-Air | 保持 |
| SensorScope Design 改进结构对齐 | Table II; W1 | \(\Delta_{group}\) 1.0139 vs FedAvg 1.0558 | adequate | RMSE 几乎打平 | 不要写成 RMSE 赢 |
| U-Air 关 Design 因支撑不兼容 | Abstract; W1; E4 | 25.5% \(\pi^{tar}=0\); oracle≈estimated | strong | 不是估计失败 | 保持 |
| 四块 WG 非劣于改编 FedAU/ObsUse | Abstract; Table II | TEST +0.48%/+0.44% 在 +0.5% 内 | adequate | 不是赢 | 禁止升级措辞 |
| 欠服务块未过 0.5% | Abstract; Table IV | VAL 百分比 | adequate | 负结果 | 禁止 TEST 救场 |
| T-Drive 再现四块错配 | Fig. G3 | TV 0.142 | adequate | 证据等级 A | 不排名 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines:** 改编 FedAU/ObsUse 在主表。TwoStage-Hájek 在 U-Air 上明显更差。Local-Hájek=FedAvg。FedCure 未跑。官方 FedAU 未跑。
- **Ablations:** E4 保留 U-Air Design 反转。Use 无孤立效应。Debt 定量很小。
- **Datasets:** SensorScope、U-Air 主推断；NSW-Traffic 仅 RQ1；T-Drive 不排名。
- **Metrics:** RMSE\(_\mu\)、四块 WorstGroupRMSE、\(\Delta_{group}\)、\(\Delta_{c-s}\)。欠服务块是第二预注册预测端点。
- **Statistics:** 20 配对种子; Wilcoxon+Holm; +0.5% 预注册规则。欠服务块 10 个 VAL 种子。
- **Robustness:** Path A 失败公开; oracle Design 跟踪 estimated。
- **Reproducibility:** 超参与种子协议在正文; 无代码句; GitHub 快照仍不覆盖 G0–G5/封印 E3。
- **Limitations:** 讨论节完整。

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-justified
Expertise: MCS completion / FL
Likely score: 7/10
Confidence: 4
Main positive signal: 问题合法; 负结果公开; 16 页可投。
Main negative signal: 预测端点打平改编 FedAU。
Evidence basis: Table II; Abstract.
Score-change condition: 外部端点独特赢 → 8; 把非劣写成赢 → 5。
```

```text
Reviewer: Critical
Expertise: TMC empirics
Likely score: 5/10
Confidence: 4
Main positive signal: 不隐瞒反转。
Main negative signal: 默认关掉 Design; 独特赢面是 P2 目标。
Evidence basis: Table II; Path B。
Score-change condition: 读成 TEST 调参维持 5; 新外部赢 → 6/7。
```

```text
Reviewer: Method / Soundness
Expertise: IPW / convex calibration
Likely score: 4/5 soundness
Confidence: 4
Main positive signal: A5 与 Prop. 3 对齐实现裁剪。
Main negative signal: 无 Algorithm 1，III–V 难复述。
Evidence basis: §VI; 无 algorithm 环境。
Score-change condition: 伪代码 → Clarity 局部 +1。
```

```text
Reviewer: Evidence / Experiment
Expertise: FL baselines
Likely score: 4/5 evidence
Confidence: 4
Main positive signal: 同迹改编 FedAU; 预注册 NI 规则。
Main negative signal: 非劣不是赢; G6 VAL 失败。
Evidence basis: Table II; Table IV.
Score-change condition: 新端点赢 → Evidence/Significance +1 且 overall 6→7。
```

```text
Reviewer: Novelty / Positioning
Expertise: covariate shift / participation FL
Likely score: 4/5 originality (positioning); method still incremental
Confidence: 4
Main positive signal: 近邻表 + Shimodaira/Robins。
Main negative signal: 元件仍是 IPW + 小凸规划 + 数据集门控。
Evidence basis: §II Table I; cites 38–39。
Score-change condition: 写作已到位; 再引 Byrd 只巩固，不改 overall。
```

```text
Reviewer: Writing / Clarity
Expertise: TMC readability
Likely score: 4/5
Confidence: 4
Main positive signal: 摘要含反转与负结果; 附录已拆。
Main negative signal: 无算法盒; 作者 ****。
Evidence basis: Abstract; \author。
Score-change condition: Algorithm 1 + 填作者 → 行政/Clarity，overall 不动。
```

```text
Reviewer: Ethics / Reproducibility
Expertise: artifacts
Likely score: 5 ethics / 3 repro
Confidence: 4
Main positive signal: 局限与隐私句。
Main negative signal: 无 availability 句; 代码快照不全。
Evidence basis: Discussion; 无 GitHub 句。
Score-change condition: 可复核入口 → Repro 3→4; overall 0 到 +0.5。
```

```text
Reviewer: Domain application
Expertise: mobile sensing
Likely score: 4/5 practical
Confidence: 4
Main positive signal: T-Drive 真实 R。
Main negative signal: O/U 仍受控; 非端到端系统。
Evidence basis: G3; 证据等级 A。
Score-change condition: 证据 B 加强 TMC 属性，不补预测赢面。
```

```text
Reviewer: Novice advocate
Expertise: first-pass TMC reader
Likely score: 4/5 accessibility
Confidence: 4
Main positive signal: 门控默认在摘要一句说清。
Main negative signal: 无伪代码; Fig. 3–4 已不在主文，需 supplemental 指引。
Evidence basis: Intro organization; RQ2 段。
Score-change condition: Algorithm 1。
```

```text
Agreement: 问题合法; 不 desk reject; 外部预测不是赢; 负结果应保留。
Disagreement: 同情者给 7，挑剔者给 5; AC 不平均成 6.5。
Decisive positive axis: 诚实门控 + 同迹 FedAU + 可投页数。
Decisive negative axis: 改编 FedAU/ObsUse 上无独特部署预测优势。
Unresolved evidence: 官方 FedAU; 评审期完整代码。
AC stance: Borderline positive，6/10，confidence 4。进入讨论，不是弱收。写作/引用不能把 overall 抬到 7。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | major | RMSE/WG 相对改编 FedAU 非劣不是赢 | Table II | Significance | experiment | 新预注册外部端点赢; 或接受打平叙事 | ccf-experiment-designer | 独特赢 → 6→7 |
| C2 | major | 欠服务块 VAL 失败 | Table IV; VAL_GATE | Significance | accepted-limitation | 保持负结果; 不打开 TEST | — | 写成赢则降分 |
| C3 | major | U-Air 默认 = 关 Design | Abstract; Table II | Originality, Clarity | writing | 保持 VAL 时间线 | ccf-paper-writer | 读成 TEST 调参 → 6→5 |
| C4 | minor | Byrd 2019 未引 | §II | Originality | citation/positioning | 可选一句 IW 失效篱笆 | ccf-paper-writer | 维度不动或局部 +; overall 0 |
| C5 | moderate | 评审期代码不完整 | 无 availability 句 | Reproducibility | reproducibility | 一句代码/数据; 推送 G0–G5 入口 | — | Repro 3→4; overall 0 到 +0.5 |
| C6 | moderate | 作者占位 | `\author{****}` | format | writing | 填第一作者 | ccf-paper-writer | 行政 |
| C7 | minor | 无 Algorithm 1 | 无 algorithm 环境 | Clarity | writing | 窗口关闭伪代码 | ccf-paper-writer | Clarity 局部 |
| C8 | moderate | 官方 FedAU 未跑 | Table II caption | Evidence | experiment | 仅在授权下跑; 可能降分 | — | 结构+RMSE 双赢 → 6→5/4 |
| C9 | minor | 四块逐组 RMSE 未进 supplemental | appendix.tex; G2 PROTOCOL | Evidence | writing | 用已有 per_seed.csv 做表 | ccf-paper-writer | 透明性, 不改 overall |
| C10 | minor | 16 页仍可能 MOPC | main.pdf 16 页 vs 发表 12 页 | format | compression | 仅当用户要求再压理论/相关工作 | ccf-paper-writer | 行政/收费 |

## 12. AC / Meta-Review

审稿人同意：可审、不 desk reject、预测端点非劣、负结果必须保留。分歧只在 5 还是 7。AC 取 **6**。相对 8 月 26 日，行政风险下降，科学决定轴未动。讨论风险：把 \(\Delta_{group}\) 写成部署效用，或把 U-Air 关 Design 写成通用稳健 Design。

## 13. Quantitative Scores

```text
Quality: 4
Clarity: 4
Significance: 3
Originality: 4
Soundness: 4
Evidence: 4
Reproducibility: 3
Ethics / Limitations: 5
Overall: 6
Confidence: 4
Score-change conditions: 见 §15
```

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 4 | 4 | §II 近邻表 + Shimodaira/Robins | 元件仍旧。再引 Byrd 不改 overall |
| Soundness | 4 | 4 | §VI A5/Prop. 3 | 无伪代码。Algorithm 1 → Clarity 不是 Soundness |
| Evidence | 4 | 4 | Table II 支持非劣 | 不支持独特赢。新端点赢 → 4→5 且 overall 6→7 |
| Significance | 3 | 4 | Table II RMSE/WG 打平; Table IV 负结果 | 部署替换理由弱。新外部胜利 → 3→4 且 6→7 |
| Clarity | 4 | 4 | 摘要含门控与负结果 | 无 Algorithm。补伪代码 → 局部 + |
| Reproducibility | 3 | 4 | 协议在正文; 无代码句 | 可复核入口 → 3→4; overall 0 到 +0.5 |
| Ethics / Limitations | 5 | 5 | 反转、等级 A、隐私、TEST 未开 | 把负结果写成赢会降分 |

**Overall:** 6 / 10  | **Scholarly Confidence:** 4 / 5

**Recommendation:** borderline  
**Verdict:** 只有新的预注册外部端点相对改编 FedAU **和** ObsUse 达到 −0.5% 且知情复制仍输，才能 6→7。写作、Byrd、Algorithm、填作者、拆附录（已完成）都不能单独把总分抬到 7。

### Writing scorecard

| Dimension | Weight | Score (1-5) | Confidence (1-5) | Evidence basis | Concrete repair |
| --- | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | §I 到达律 ≠ 目标 | 保持 |
| Contribution display | 12 | 4 | 4 | 三条贡献; 门控非第四条 | 保持 |
| Paragraph logic | 10 | 4 | 4 | 引言不再倾倒数字 | 保持 |
| Claim-evidence alignment | 14 | 4 | 4 | 摘要与 Table II/IV 一致 | 禁止升级非劣 |
| Method readability | 10 | 3 | 4 | 无 Algorithm | 加 Algorithm 1 |
| Experiment narration | 10 | 4 | 4 | Table II 在主文; Fig 3–4 在补 | supplemental 加逐组表 |
| Related-work positioning | 8 | 4 | 4 | 近邻表 + 两篇经典篱笆 | 可选 Byrd |
| Terminology and notation | 8 | 4 | 4 | gated / full Design 已区分 | 保持 |
| LaTeX and format | 8 | 4 | 4 | 16 页; 附录外置 | 填作者 |
| Reviewer-facing risk | 8 | 4 | 4 | 负结果公开 | 勿打开 G6 TEST |

**Writing score:** \(3.90/5\)。**Writing risk band:** moderate。

## 14. Questions For Authors

1. 若审稿人问「为何不用改编 FedAU」，除 \(\Delta_{group}\) 外，现有证据里还有哪条 **部署预测** 理由？
2. U-Air 关 Design 的规则是否在打开 TEST 之前就冻结？（正文已写 VAL，需在回复里能指到。）
3. 评审期能否给出与 Table II 同迹的最小可运行入口，而不是不完整 GitHub？
4. 是否授权跑官方 FedAU？（可能降分。）

## 15. Score Revision Criteria

```text
Raising the score would require:
  新的预注册外部端点，VAL+TEST 相对改编 FedAU 与 ObsUse 均 ≤ −0.5%，且 μ-知情复制仍输。不是 G6 救援。
Lowering the score would be triggered by:
  把 Table IV 或 −0.44% 写成赢; 打开 G6 TEST 换端点; 官方 FedAU 在结构与 RMSE 上双赢却沉默; 把门控读成 TEST 调参且作者无法出示 VAL 规则。
Concerns unlikely to change before submission:
  Use 无孤立效应; Debt 极小; T-Drive 证据等级 A; 20 seed 不是独立城市; 发表 12 页 MOPC。
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | 新预注册外部端点赢 FedAU 且复制不了 | Significance, Evidence | +1 overall (6→7) |
| Raise score | Algorithm 1 + 代码句 + 填作者 | Clarity, Repro, format | 维度 +1; overall 0 到 +0.5 |
| Lower score | 官方 FedAU 结构+RMSE 双赢 | Evidence, Novelty | −1 overall |
| Lower score | 宣称欠服务块胜利或打开 TEST | Ethics, Evidence | −1 overall |
| No quick change | 再压到 12 页或升 T-Drive 到证据 B | format / domain | 不改 6 |

## 16. Action Plan And CCFA Handoffs

```text
Priority: P0（现在就能改，不改科学分，降低行政风险）
Action: 填第一作者; 加 Algorithm 1（窗口关闭: R/O/U → 参考质量 → P2）; 正文一句代码/数据可用性（不要把不完整仓库写成可复现）; supplemental 增加四块 RMSE_g 表（数据已在 G2 per_seed.csv）。
Owner skill: ccf-paper-writer
Input needed: 作者姓名; 是否公开仓库 URL。
Expected output: 修订主文/supplemental。
Handoff required: yes
```

```text
Priority: P1（可选写作，不改 overall）
Action: Related Work 加 Byrd & Lipton 2019 一句，限定「过参数化分类 vs 有限容量补全」。
Owner skill: ccf-paper-writer
Input needed: 已核 bib。
Expected output: 一段篱笆。
Handoff required: yes
```

```text
Priority: P2（只有授权才做；唯一可能 6→7）
Action: 全新预注册外部端点协议。禁止 G6 救援、禁止扫描 RMSE_block 选 g*、禁止升格 S2/S3。
Owner skill: ccf-experiment-designer
Input needed: 用户书面授权。
Expected output: PROTOCOL + VAL 门; 失败则停。
Handoff required: yes
```

```text
Priority: P3（高风险）
Action: 官方 FedAU 或 FedCure。可能降低现稿。
Owner skill: ccf-experiment-designer
Input needed: 明确接受降分风险。
Expected output: 同迹对比或记录为未跑局限。
Handoff required: yes
```

```text
Priority: do-not
Action: 打开 G6 TEST; 把 −0.44% 四舍五入成赢; 把 Path B 写成第四贡献; 为 Use/Debt 造选择过程。
Owner skill: —
Input needed: —
Expected output: 不执行。
Handoff required: no
```

```text
Checks run: 主文主张 vs Table II / Table IV; 附录是否外置; Shimodaira/Robins 是否在 bib 与正文; 作者/算法/代码句; 本地 16+8 页编译; CS 页限检索。
Checks skipped: 官方 TMC Author Information HTML; 官方 FedAU 实现核对; GitHub 全量快照审计。
Unresolved risks: 审稿人把 Δ_group 写成 objective compliance; 不完整代码仓库; 录用后 MOPC。
```
