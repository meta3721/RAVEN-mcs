# CCFA 论文评审报告 — RAVEN-MCS（G6 VAL 之后独立复审，2026-08-26）

## 1. Report Metadata

```text
Review date: 2026-08-26
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A, regular paper
Paper title: RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex（投稿写作目标; 相对 2026-08-24 评审，主文未纳入 G6）
  reference.bib; Table II / Fig. 3–4 / Fig. W1 / T-Drive 图与 caption
  post_review/G6_cannot_copy_endpoint/{PROTOCOL,GSTAR,VAL_GATE,DECISION}.md（未写入正文的门控实验，只作证据边界）
  对照 2026-08-24 清洁稿评审（6/10）
Search basis: 公开检索 TMC/Computer Society 页限（第三方摘录: 常规 12 页、投稿可至 18 页 MOPC、附录须独立 supplemental）。相关工作沿用已核出处（Shimodaira 2000 JSPI; Robins et al. 1994 JASA; FedAU Wang & Ji ICLR 2024）。本轮未把稿件私有句子贴进检索。
Report file: ccfa-review-reports/2026-08-26-raven-mcs-tmc-conference-review.md
Reviewer mode: full（scientific + writing + format + revision-action）
Material delta vs 2026-08-24: 主文主张仍是四块 WorstGroupRMSE 非劣，不是独特赢。新增未发表 G6：预注册欠服务块 RMSE_g*，VAL 未过 −0.5% 赢规则，TEST 未开。GitHub 现有 origin（meta3721/meta，分支含 G6 提交 b4af7a9）；G0–G5 与 Overleaf 清洁稿仍未进该提交。
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: uncertain
Evidence: 最近一次可核编译记录仍是 2026-08-23 PDF，整本约 21 页，`\appendices` 绑在 main.tex。本轮未重编译。Computer Society 常规发表约 12 双栏页（含参考文献/简历），投稿可至 18 页并可能 MOPC；supplemental 须单独文件。官方 TMC Author Information HTML 仍未在本轮直接打开。
Consequence: 不因页数 desk reject。编辑可能要求拆附录。超 12–14 页是收费/压缩问题，不是不可审。
Required action: 编译一次; 附录外置; 投稿前再核 Computer Society 实时页限。
```

```text
Check: Topic compatibility
Status: pass
Evidence: 稀疏 MCS 补全 + 窗口化异步联邦 + 非随机选择 + 出租车机会层，落在 TMC 的 mobile environments / algorithm-protocol 范围。
```

```text
Check: Minimum quality
Status: pass
Evidence: Abstract–Conclusion、理论、主表、20 配对种子、Holm、+0.5% 非劣规则、Design 反转、Path A 失败、T-Drive 不排名均在正文。
```

```text
Check: Policy / anonymity / compliance
Status: uncertain
Evidence: 作者行仍为 `**** and Anfeng Liu`。摘要明显长于 IEEE 常见 100–200 词。附录仍在主 PDF。TMC 期刊通常单盲，占位名不是双盲违规。
Consequence: 行政修补，不是科学 desk reject。
Required action: 填第一作者; 摘要压缩; 附录改独立 supplemental。
```

```text
Check: Prompt injection / ethics
Status: pass
Evidence: 未见隐藏审稿指令。公开环境/空气/出租车数据; 讨论含倾向得分元数据隐私句。
```

**Desk rejection: 否。风险 low。** 进入完整评审。

## 3. Paper Summary And Contribution Map

**一句话：** 窗口化异步联邦 MCS 补全被写成部署目标风险对齐；Design 按数据集门控；经验上独特赢面是作者定义的结构 L1，TMC 更在乎的 RMSE 与四块 WorstGroupRMSE 与改编 FedAU/ObsUse 非劣。

- **Claimed problem:** 到达律不必等于公开部署目标 \(\mu\)；感知侧 \(R/O\) 与更新侧 \(U\) 顺序选择。
- **Claimed gap:** 稀疏补全、异步补全、参与感知 FL 都不联合建模三层选择，也不处理有限窗可实现性。
- **Method map:** (1) 风险语义 + Prop. 1；(2) 三层重建 + Prop. 2，门控是 Contrib. 2 的实践实现；(3) P2+债务 + Thm. 1 + Prop. 3（裁剪 plug-in 稳定扰动）。正好三条贡献。
- **Evidence package:** E1 无伤害；E2 \(D_{\mathrm{aligned}}\approx-0.021\)；E3 门控主表（FedAU/ObsUse/WorstGroupRMSE）；E4 保留 U-Air Design 反转；G3 T-Drive 真实 \(R\)（TV 0.142），不排名。
- **Unpublished extra (not in paper):** G6 VAL：\(g^\star=\arg\max(\mu-\pi^{opp,4})\)，SS \(g^\star=2\)、UA \(g^\star=3\)；相对 FedAU/ObsUse 未达 \(\le-0.5\%\)；TEST 未开。
- **Stated limitations:** 裁剪非无偏；A5 不覆盖 U-Air 全 Design；Use 无孤立效应；Debt 0.002%–0.014%；Path A 失败；T-Drive 证据等级 A；20 seed 不是独立城市；P2 只证可行性。

## 4. Search And Related-Work Basis

```text
Queries used:
  IEEE Transactions on Mobile Computing page limit supplemental Computer Society
  （沿用已核、未重贴私有稿件）Shimodaira 2000; Robins et al. 1994; FedAU 2024
Sources searched: Web search; 第三方 Computer Society 页限摘录。官方 TMC 专页 HTML 本轮未直接核到。
Closest works found:
  Shimodaira 2000: 单次密度比 / 目标风险加权似然。本稿仍未引。
  Robins et al. 1994: 顺序缺失数据 IPW。本稿仍未引。
  FedAU 2024: 参与重加权保住原 FL 目标。主表是窗口改编，不是官方复现。
Unverified related-work risks:
  tian2026reshaping / qiao2025asmafl / chen2026dvafl 仍未进入本稿（状态 unverified，不当作已发表对照）。
  Byrd & Lipton 2019 仍未引。
Source-quality screening status: 未使用 MDPI。页限不是本轮官方 HTML。
```

## 5. Expected Review Outcome

```text
Expected outcome: Borderline positive / 弱偏收讨论
Main accept signal: 问题切分清楚; Design 反转公开; 改编 FedAU/ObsUse 与四块 WG 在主表; T-Drive 证据等级 A 写清; 窗口异步与 FedAsync 划界在标题/III-A。
Main reject signal: RMSE 与四块 WorstGroupRMSE 上与改编 FedAU/ObsUse 非劣不是赢; U-Air 默认 = 关 Design; 未发表 G6 显示第二条预注册外部端点同样未赢; 未引 Shimodaira/Robins; 评审期完整代码仍不在 GitHub 快照里。
Confidence: 4/5
```

相对 2026-08-24 **overall 维持 6**。那一轮 5→6 的条件（同迹 FedAU + 外部 WG）已经满足。6→7 的条件是「预声明外部端点上赢，且改编 FedAU 复制不了」。G6 按该条件设计并在 VAL 失败，因此 **不能把分数抬到 7**；主文从未声称 G6 胜利，因此 **也不因此降到 5**。

## 6. Strengths And Weaknesses

**Strengths**
- 到达律 ≠ 部署目标律仍是合法 TMC 问题；E2 \(D_{\mathrm{aligned}}\) 跨方法为负。
- 门控与 U-Air Design 反转写进摘要/主表/讨论；Fig. 3–4 caption 标明 U-Air 图中 RAVEN 是 full Design。
- 主表含改编 FedAU/ObsUse 与四块 WorstGroupRMSE；明确「不是 Holm 赢 FedAU」。
- T-Drive 把 \(R\) 从纯协议变量改成真实轨迹，并禁止系统/排名过度声明。
- Prop. 3 / A5 把裁剪 plug-in 收成稳定扰动，并声明不解释 U-Air 反转。
- Use 无效应、Debt 极小、Local-Hájek 退化、Path A 失败公开。

**Weaknesses**

```text
Weakness: 对改编 FedAU/ObsUse，外部预测端点是非劣；独特赢面仍是 Δ_group / Δ_c-s。
Evidence basis: Table II。U-Air RMSE 门控 1.1131 vs FedAU 1.1128 vs ObsUse 1.1120；WorstGroupRMSE 1.1703 vs 1.1701 vs 1.1692。SensorScope 三方法 WG 几乎互换。SensorScope Δ_group 门控 1.0139 vs FedAU 1.0719。
Reviewer deduction: TMC 读者会问为什么不直接用参与重加权。分层 R/O/U 的增量没有落在部署 RMSE/最差组上。
Required fix: 新的预注册外部端点上赢且 FedAU 复制不了；或把贡献收成「结构对齐 + 支撑门控」，接受预测打平。
```

```text
Weakness: 未发表 G6 显示「欠服务块 RMSE_g*」同样未赢改编 FedAU/ObsUse。
Evidence basis: post_review/G6 VAL_GATE.json。SS vs FedAU +0.05%、vs ObsUse +0.15%；UA vs FedAU −0.44%、vs ObsUse −0.27%。两集都是 no-harm、都不是 win。SS 上 g*=2 与 G2 worst block 重合。TEST 按协议未开。
Reviewer deduction: 关闭了上一轮写明的 6→7 路径。不是正文造假（正文只声称 NI），但是加分实验失败。把 −0.44% 写成赢会降分。
Required fix: 正文可加一句诚实负结果；禁止升格 S2/S3 或打开 TEST 救场。
```

```text
Weakness: U-Air 论文默认 = 去掉 Design。可被读成消融胜出。
Evidence basis: 摘要; Table II 门控行 = raven_wo_design; Table III / Fig. W1 约 −7% RMSE。
Reviewer deduction: 诚实，但贡献叙事脆弱。完整栈伤害 U-Air 主端点。
Required fix: 一行写清门控在 TEST 前由支撑诊断预声明; 勿让 Fig. 3–4 的 full Design 与默认行在视觉上竞争（caption 已标注，图本身仍写 RAVEN-MCS）。
```

```text
Weakness: 方法增量仍是顺序 IPW + 小 QP + 虚拟队列 + 数据集门。
Evidence basis: Prop. 1–3; §II 最近邻表无 Shimodaira/Robins。
Reviewer deduction: 原创性在组合与信息集，不在新估计量。缺经典篱笆会被写成「又一个 IW」。
Required fix: 引用并对齐顺序三层信息集 + 有限支持校准。
```

```text
Weakness: T-Drive 无方法排名; O/U 仍受控。
Evidence basis: Discussion; G3 claim ceiling。
Reviewer deduction: 改善 venue fit，但不是端到端移动系统论文。
Required fix: 保持等级 A 用词。单独授权 canary 才可谈排名。
```

## 7. Potentially Missing Related Work

```text
Work: Shimodaira, H. (2000). Improving predictive inference under covariate shift by weighting the log-likelihood function. JSPI.
Status: searched / previously verified
Why relevant: 目标风险加权的标准统计表述。
Overlap: 目标加权似然; 不是 R/O/U 顺序信息集，也不是有限窗 P2。
Needed comparison: 一段划界，说明 RAVEN 不是单次密度比。
```

```text
Work: Robins, Rotnitzky, Zhao (1994). Estimation of regression coefficients when some regressors are not always observed. JASA.
Status: searched / previously verified
Why relevant: 顺序缺失 / IPW 的经典来源。
Overlap: 顺序校正思想; 不是 MCS 窗口联邦，也不是部署 μ 校准。
Needed comparison: 信息集与可行集差异。
```

```text
Work: Wang & Ji, FedAU, ICLR 2024.
Status: user-provided / cited as adapted baseline
Why relevant: 最近邻参与去偏。
Overlap: 修 U 层参与; 不修感知侧 R/O，不用 μ。
Needed comparison: 已在主表。官方复现仍缺; 若官方双赢结构和 RMSE 会降分。
```

```text
Work: Byrd & Lipton (2019). What is the effect of importance weighting in deep learning? ICML.
Status: searched / previously verified; 未引
Why relevant: 过参数化下 IW 效应可消失，可解释 SensorScope RMSE 打平。
Needed comparison: 可选一句; 补全模型容量有限，不完全同机制。
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| 到达律 ≠ 部署目标律 | Intro; E2 | \(D_{\mathrm{aligned}}\approx-0.021\) | strong | 动机成立 | 保持 |
| 门控默认; U-Air 关 Design 因支撑不兼容 | Abstract; Fig. W1; Discussion | 估计/oracle Design 同步变差约 7% | strong | 不是 propensity 失败 | 写预声明时间线 |
| 四块 WG 非劣于改编 FedAU/ObsUse | Abstract; Table II | UA TEST +0.48% / +0.44% 在 +0.5% 内 | adequate for NI | 不是赢 | 禁止写成 best worst-group |
| 结构 L1 优于 FedAU | Table II \(\Delta_{group}\) | SS 1.0139 vs 1.0719 | adequate but internal | objective compliance 风险 | 需要外部后果 |
| T-Drive 真实机会 mismatch | Fig. G3; TV 0.142 | 真实 \(R\)，受控 O/U | adequate for level A | 不是系统论文 | 禁止排名/能耗 |
| 裁剪 plug-in 稳定扰动 | Prop. 3; A5 | 理论 + 声明不解释 U-Air 反转 | adequate | 不是无偏估计 | 勿把 \(C_1\) 当 RMSE 保证 |
| 改编 FedAU 复制不了外部预测优势 | 不在正文; G6 协议曾试图证明 | G6 VAL 失败 | **negative / unpublished** | 不能写入正面主张 | 可写一句负结果 |
| P2 最优 | solver 讨论 | 可行性 + 残差，非最优性证明 | weak if overclaimed | 正文若只写可行性则 OK | 保持「可行性不是最优」 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines:** 改编 FedAU/ObsUse/TwoStage/FedAvg 同迹。官方 FedAU、FedCure 未跑。Local-Hájek 已降级。标注 adapted，公平。
- **Ablations:** E4 单因子; U-Air Design 反转保留。Path A 失败公开。
- **Datasets:** SensorScope、U-Air Complete-aligned; T-Drive 只作 \(R\) 回放。
- **Metrics:** RMSE\(_\mu\)、WorstGroupRMSE、\(\Delta_{group}\)、\(\Delta_{c\text{-}s}\)。后两者在 P2 目标附近。
- **Statistics:** 20 seed 正式表; G2 VAL/TEST 10+10; Holm; +0.5% MPID。G6 VAL 10 seed，TEST 未开。
- **Robustness/failure:** Design 反转、Path A、G6 VAL 负结果（未进正文）。
- **Implementation:** POLICY_MAP 冻结; 无 Algorithm 1。
- **Artifacts:** 分支 `paper-data-clean-and-package-r1` 已推 GitHub，含 G6 协议与 VAL 表。G0–G5、密封 E3 运行、Overleaf 清洁稿仍未进该快照。正文无 code availability 句。
- **Limitations:** 与声明基本对齐。G6 若写入必须标 VAL-only、TEST 未开。

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-Justified
Expertise: MCS / 选择偏倚
Likely score: 7 (weak accept tendency)
Confidence: 4
Main positive signal: 风险语义清楚; 负结果公开; 最近邻基线已进主表。
Main negative signal: 预测打平参与重加权。
Evidence basis: Table II; Discussion
Score-change condition: 外部端点独特赢。
```

```text
Reviewer: Critical
Expertise: FL baselines
Likely score: 5 (borderline negative)
Confidence: 4
Main positive signal: 改编 FedAU 比较存在。
Main negative signal: 门控 RAVEN ≈ FedAU/ObsUse on RMSE/WG; U-Air 默认是消融; G6 再失败。
Evidence basis: Table II; G6 VAL_GATE
Fatal concern if any: 无（不是不可审错误）
Score-change condition: 官方 FedAU 双赢 → 4; 独特外部赢 → 7。
```

```text
Reviewer: Method / Soundness
Expertise: IPW / 凸校准
Likely score: 4/5 soundness
Confidence: 4
Main positive signal: A5+Prop. 3 与实现对齐; 不解释 U-Air 反转。
Main negative signal: Prop. 1 浅; 无 Algorithm。
Evidence basis: §III–IV; appendix proofs
Score-change condition: 算法盒 + Shimodaira/Robins 划界。
```

```text
Reviewer: Evidence / Experiment
Expertise: 实证协议
Likely score: 4/5 evidence for stated NI claims; 3/5 for uniqueness
Confidence: 4
Main positive signal: 预注册 NI 规则; 不 Holms 充赢。
Main negative signal: 独特赢在作者指标; G6 外部端点失败。
Evidence basis: Table II; G2 PROTOCOL; G6 DECISION
Score-change condition: 新预注册家族胜利，不是 G6 救援。
```

```text
Reviewer: Novelty / Positioning
Expertise: covariate shift / FL
Likely score: 3/5 originality
Confidence: 4
Main positive signal: 最近邻表存在。
Main negative signal: 未引 Shimodaira/Robins。
Evidence basis: §II; bib
Score-change condition: 划界段。
```

```text
Reviewer: Writing / Clarity
Expertise: TMC 可读性
Likely score: 3/5
Confidence: 4
Main positive signal: Fig. 3–4 caption 已区分 U-Air full Design。
Main negative signal: 摘要过长; 无 Algorithm; 双 RAVEN 视觉; 作者占位。
Evidence basis: abstract; Fig. 3–4; \author
Score-change condition: 压缩摘要 + Algorithm 1 + 默认命名统一。
```

```text
Reviewer: Ethics / Reproducibility
Expertise: artifacts
Likely score: 5/5 ethics; 3/5 repro
Confidence: 4
Main positive signal: 隐私句; 无人体实验问题。
Main negative signal: 正文无代码声明; GitHub 快照缺 G0–G5/密封运行。
Evidence basis: Discussion; github.com/meta3721/meta
Score-change condition: 评审期代码覆盖 E3/E4 与门控脚本。
```

```text
Reviewer: Domain Application (TMC)
Expertise: 移动感知部署
Likely score: 3/5 practical significance
Confidence: 4
Main positive signal: 真实出租车 R。
Main negative signal: 部署者在 RMSE/WG 上看不到替换 FedAU 的理由; 无端到端更新。
Evidence basis: Table II; T-Drive 等级 A
Score-change condition: 外部任务效用或覆盖指标上的预注册胜利。
```

```text
Reviewer: Novice Advocate
Expertise: 可读性
Likely score: 3/5 accessibility
Confidence: 4
Main positive signal: 门控故事在摘要里能读到。
Main negative signal: 符号密; 无伪代码; 图与表默认不一致。
Evidence basis: §III; Fig. 3 vs Table II
Score-change condition: Algorithm 1。
```

```text
Agreement: 不是 desk reject; 结构故事成立; RMSE/WG 与改编 FedAU 打平是决策轴。
Disagreement: Best-justified 愿给弱收（问题新）; Critical 愿给弱拒（增量不可操作）。
Decisive positive axis: 选择层语义 + 诚实负结果 + 同迹最近邻基线。
Decisive negative axis: TMC 面向 RMSE/WG 无独特赢; G6 关闭了设计好的加分实验。
Unresolved evidence: 官方 FedAU; 评审期完整代码; TMC 官方页限 HTML。
AC stance: Borderline positive (6/10)。讨论会问「为何不用 FedAU」。没有新的预注册外部胜利，不升到 7。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | major | RMSE/WG 相对改编 FedAU 非劣不是赢 | Table II | Significance, Evidence | experiment | 新预注册外部端点胜利，或收缩贡献 | ccf-experiment-designer | 独特赢 → 6→7; G6 救援禁止 |
| C2 | major | G6 VAL 失败关闭既定 6→7 路径 | G6 VAL_GATE | Significance | experiment | 可写一句负结果; 不打开 TEST | ccf-paper-writer | 写入负结果不降分; 写成赢则降分 |
| C3 | major | U-Air 默认 = 关 Design | Abstract; Table II | Originality, Clarity | writing | 预声明时间线; 统一图标签 | ccf-paper-writer | 读成 TEST 调参 → 6→5 |
| C4 | moderate | 未引 Shimodaira/Robins | §II; bib | Originality | related-work | 划界段 | ccf-paper-writer | 维度 +1; overall 0–+0.5 |
| C5 | moderate | 评审期代码不完整 | 无 availability; GitHub 缺 G0–G5 | Reproducibility | reproducibility | 推送门控+密封入口+脚本 | — | Repro 3→4; overall 不动或 +0.5 |
| C6 | moderate | 附录在主文件; 摘要过长; 作者占位 | `\appendices`; `\author{****}` | format | compression | 拆 supplemental; 压摘要; 填作者 | ccf-paper-writer | 行政, 不改科学分 |
| C7 | minor | 无 Algorithm 1 | 全文无 algorithm 环境 | Clarity | writing | 伪代码 | ccf-paper-writer | Clarity 局部 |
| C8 | moderate | 官方 FedAU 未跑 | §6.2; 主表注 adapted | Evidence | experiment | 仅在授权后跑; 双赢则记 limitation | ccf-experiment-designer | 结构+RMSE 双赢 → 6→5/4 |

## 12. AC / Meta-Review

审稿人会同意这不是不可审稿，也同意「到达律不是部署目标」值得在 TMC 出现。分歧在增量是否可操作：同情者看到结构 L1、支撑门控和诚实反转；怀疑者看到 Table II 上 FedAU/ObsUse 已经把 RMSE 和四块 WG 做平，G6 又没能在欠服务块上打开差距。

决定性接受轴：语义切分 + 同迹最近邻比较 + 负结果不藏。  
决定性拒绝轴：没有 FedAU 复制不了的外部预测后果。

AC 立场：Borderline positive，6/10，confidence 4。进入讨论，不是弱收。G6 之后，用写作或引用把 overall 抬到 7 不再可信。

讨论风险：有人要求官方 FedAU；若官方更好，分数下降。有人把 U-Air 门控读成看过测试再关 Design。

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 3 | 4 | §II 最近邻表; 无 Shimodaira/Robins | 组合新、元件旧。划界段 → 3→4; overall 至多 +0.5 |
| Soundness | 4 | 4 | Prop. 1–3; A5 不覆盖 U-Air 反转 | 无致命错误。勿把 Prop. 3 当无偏 |
| Evidence | 4 | 4 | Table II NI 与正文一致; G6 未进正文且为负 | 对已声称的 NI 足够。独特赢证据不足，但不构成正文造假 |
| Significance | 3 | 4 | Table II RMSE/WG 打平; G6 VAL 失败 | 部署替换理由弱。新外部胜利 → 3→4 且 overall 6→7 |
| Clarity | 4 | 4 | 门控写进摘要; Fig. 3–4 caption 已区分 | 摘要过长、无算法、双默认视觉。Algorithm+压缩 → 局部 + |
| Reproducibility | 3 | 4 | 无正文代码句; GitHub 仅部分历史+G6 | 推送 G0–G5/E3 入口 → 3→4 |
| Ethics / Limitations | 5 | 4 | 隐私句; Design 反转; T-Drive 等级 A | 无伦理红线。G6 负结果若隐瞒反而有风险 |

**Overall:** 6  | **Scholarly Confidence:** 4

**Recommendation:** borderline-positive（弱偏收讨论，不是弱收）  
**Verdict:** 新的预注册外部端点上相对 FedAU 的独特优势才可能 +1 到 7。G6 已失败，不能靠打开 TEST 或改 \(g^\star\) 来凑。官方 FedAU 若结构+RMSE 双赢，降 1 分。

```text
Quality: 4
Clarity: 4
Significance: 3
Originality: 3
Soundness: 4
Evidence: 4
Reproducibility: 3
Ethics / Limitations: 5
Overall: 6
Confidence: 4
Score-change conditions: 见 §15
```

### Writing scorecard

| Dimension | Weight | Score (1-5) | Confidence | Evidence basis | Concrete repair |
| ---: | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | Intro 风险语义 | 保持 |
| Contribution display | 12 | 4 | 4 | 三条贡献; 门控不单列 | 保持 |
| Paragraph logic | 10 | 3 | 4 | 评价段仍密 | 每段先结论句 |
| Claim-evidence alignment | 14 | 4 | 4 | NI 与 Table II 对齐 | 勿把 G6 写成赢 |
| Method readability | 10 | 3 | 4 | 无 Algorithm | Algorithm 1 |
| Experiment narration | 10 | 4 | 4 | Table II caption 有 NI 规则 | Fig. 3 默认命名 |
| Related-work positioning | 8 | 3 | 4 | 有表无经典篱笆 | Shimodaira/Robins |
| Terminology consistency | 8 | 3 | 4 | 图 RAVEN vs 表 gated | 统一 |
| LaTeX / format | 8 | 3 | 4 | 附录、摘要、作者 | 拆附录; 压摘要; 填作者 |
| Reviewer-facing risk | 8 | 3 | 4 | 消融即默认; G6 诱惑 | 时间线; 不救 G6 |

**Writing score:** \(3.48/5\)。**Writing risk band:** moderate。

对每个 \(\le 3\) 的写作维：缺算法让 III 节难复述（加 Algorithm 1）；相关工作表不接经典 IW（加两段引用）；图/表「RAVEN」不一致（改图例或把 Fig. 3–4 下附录）；附录绑主文件与过长摘要是投稿行政风险。

## 14. Questions For Authors

1. 在 RMSE 与四块 WorstGroupRMSE 已与改编 FedAU 非劣、G6 欠服务块 VAL 也未赢之后，部署者仍选择 RAVEN 的操作理由是哪一列、哪一个预注册端点？
2. U-Air 关 Design 的赋值，能否指出 TEST 打开前的支撑诊断文件与日期？
3. 是否计划把 G6 VAL 负结果写进 Discussion，而不是另开端点？
4. 评审期 GitHub 是否会包含 E3/E4 密封入口与 G0–G5，而不只是 G6 目录？
5. 官方 FedAU 若不跑，能否接受「最近邻比较仅限窗口改编」这一上限？

## 15. Score Revision Criteria

```text
Raising the score would require:
  一条新的、预注册的、不在 P2 目标里的外部端点，对改编 FedAU 与 ObsUse 同时达到 −0.5% 赢规则（VAL 与 TEST），且 μ-知情复制仍输。
  G6 救援（换 g*、打开 TEST、升格 S2/S3）不算。
  仅 Shimodaira / Algorithm 1 / 推送已有代码: 维度 +1, overall 至多 +0.5, 仍是 6。
Lowering the score would be triggered by:
  官方参与重加权在结构与 RMSE 上同时更好（6→5/4）;
  把门控读成未预声明的 TEST 调参;
  把 G6 −0.44% 写成胜利。
Concerns unlikely to change before submission:
  Prop. 1 浅; Use/Debt 经验弱; T-Drive 不训练则系统味道有限; G6 已关闭原定加分实验。
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | **新**外部端点独特赢，FedAU 复制不了 | Significance, Evidence | +1 overall (6→7) |
| Raise score | Shimodaira/Robins + Algorithm 1 + 完整代码快照 | Originality, Clarity, Repro | 维度 +1; overall 0 to +0.5 |
| Lower score | 官方 FedAU 结构+RMSE 双赢 | Evidence, Novelty | −1 overall |
| Lower score | 宣称 G6 胜利或打开 TEST 换端点 | Ethics, Evidence | −1 overall |
| No quick change | 合成 O/U; Use 无效应; G6 已失败 | Significance | 投稿前难动 |

## 16. Action Plan And CCFA Handoffs

```text
Priority: P0
Action: 不要救 G6。不要打开 TEST、不要换 g*、不要升格 S2/S3。
Owner skill: （作者决策）
Input needed: G6 PROTOCOL §6
Expected output: 维持 G6_RECORDED_NEGATIVE
Handoff required: no
```

```text
Priority: P1
Action: 可选一句 Discussion：预注册欠服务块 VAL 未过 0.5% 赢规则，TEST 未开。
Owner skill: ccf-paper-writer
Input needed: G6 DECISION.md
Expected output: 诚实 limitation，不改变 6 分
Handoff required: yes（需用户点名写作）
```

```text
Priority: P1
Action: 推送 G0–G5 与 Overleaf 清洁稿（或最小可复现入口）; 正文加 code availability。
Owner skill: （仓库整理）
Input needed: 现有 post_review/ 与密封路径
Expected output: 评审期可审计快照
Handoff required: yes
```

```text
Priority: P2
Action: Shimodaira 2000 + Robins et al. 1994 划界; Algorithm 1; 摘要压到约 200 词; 附录外置; 填作者; 本轮编译。
Owner skill: ccf-paper-writer
Input needed: 已核出处; 当前 main.tex
Expected output: 清晰度修补
Handoff required: yes
```

```text
Priority: P3
Action: 仅当用户明确要冲 7 时，另写新协议（新端点、新停止规则），不得复用 G6。
Owner skill: ccf-experiment-designer
Input needed: 用户授权
Expected output: 新 PROTOCOL.md，先冻结再跑
Handoff required: yes
```

```text
Checks run: 主文主张 vs Table II; Fig. 3–4 caption; G6 VAL_GATE 与协议停止规则; 作者/附录/摘要; 公开页限检索; 已核 Shimodaira/Robins/FedAU 是否仍缺引。
Checks skipped: 本轮未重编译 PDF; 未打开官方 TMC Author Information HTML; 未跑官方 FedAU; 未把私有稿句送入网络检索。
Unresolved risks: GitHub 快照不覆盖密封 E3; 官方 FedAU 可能更强; 门控时间线若无法出示文件会被读成事后赋值。
```
