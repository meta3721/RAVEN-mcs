# CCFA 论文评审报告 — RAVEN-MCS（B1/B2 后工作稿）

## 1. Report Metadata

- **Review date:** 2026-08-18（第二轮；相对同日第一轮报告，材料变化为 B1/B2 最差组 RMSE 与 \(\Delta_{c\text{-}s}\)–RMSE\(_\mu\) 关联审计，以及 §VII-A 负结果回填）
- **Target venue/year/track:** IEEE Transactions on Mobile Computing（TMC，CCF-A，计算机网络/移动计算期刊）
- **Paper title:** RAVEN-MCS: Deployment-Target Risk Alignment for Asynchronous Federated Data Completion in Mobile Crowdsensing under Two-Stage Non-Random Selection
- **Input materials reviewed:** `_paper_work/main.tex`、`_paper_work/main.pdf`（24 页，pdflatex+bibtex 全编译）、`_paper_work/worst_group_results/`（B1/B2）、既有 P0 drifting / P1 coverage 审计、`reference.bib`
- **Search basis:** 联网检索 Shimodaira 2000（JSPI，covariate-shift 加权似然）、FedAU（Wang & Ji, ICLR 2024 / arXiv:2306.03401）、Byrd & Lipton 2019（ICML，深度学习中 importance weighting 失效）；其余相关工作以论文自引为准
- **Report file:** `_paper_work/ccfa-review-reports/2026-08-18-raven-mcs-tmc-conference-review.md`
- **Reviewer mode:** `full`（scientific + writing + format + revision-action）
- **相对上一份报告的材料变化:** 上一轮（同日、5.5/10）在覆盖审计后仍把“独立于 0.5μ 覆盖阈值的下游指标”列为加分条件。本稿已执行该条件（checkpoint 重载最差组 / high-μ RMSE，以及 within-seed Spearman），结果为 **NOT_SUPPORTED**，并写入 §VII-A。这不是新的正结果，而是把上一轮的 significance 上限从“未测”变成“已测且失败”。

## 2. Desk Rejection Assessment

- **Paper length:** 通过（24 页含附录；TMC 期刊无会议式硬页限，体量偏长但不构成 desk reject）
- **Topic compatibility:** 通过（MCS + 异步联邦补全 + 选择偏置，属 TMC 范围）
- **Minimum quality:** 通过（结构完整、公式规范、有证明、有配对实验、有 limitation）
- **Policy/anonymity/compliance:** 通过但需注意：作者行混用 `**** and Anfeng Liu`；TMC 期刊通常单盲，具名可接受，半匿名不规范但不构成 desk reject
- **Prompt injection / hidden manipulation:** 未发现
- **Ethics and reviewability:** 通过（公开基准，无人体实验）
- **Desk rejection risk:** none
- **结论:** 不构成 desk reject，进入完整评审。

## 3. Paper Summary And Contribution Map

**一句话总结：** 把异步联邦 MCS 补全表述为部署目标风险对齐：到达律不必等于部署目标律；用标准分层 IPW/Hájek 重建，再用凸校准与债务做可行性对齐。RAVEN 被写成该表述的构造性实例。B1/B2 之后，正文已承认 \(\Delta_{c\text{-}s}\) 既不改变覆盖计数，也不变成最差组 RMSE 优势，且方法级上更差的 \(\Delta_{c\text{-}s}\) 并不对应更差的 RMSE\(_\mu\)。

- **Claimed problem:** 两阶段三层非随机选择（机会 \(R\) → 观测 \(O\) → 可用更新 \(U\)）使到达律 ≠ 部署目标律。
- **Claimed gap:** 现有异步/联邦补全把到达更新当作目标总体；参与感知 FL（FedAU 等）只纠正客户端参与，不建模感知侧顺序选择。
- **Method/contribution map（按当前引言）:**
  1. 部署目标风险语义 + 不可互换（Prop 1）。
  2. 分层重建：顺序 IPW/Hájek，各层只用合法 pre-outcome 信息（Prop 2 理想版）。
  3. 可行性校准：(P2) + 长期债务（Thm 1 唯一解 + 债务前缀界）。
- **Evidence package:** E1 no-harm；E2/RQ1 风险不可互换；E3/RQ2 结构+预测（含 FedAU-Window、ObsUse-Window、drifting）；E4/RQ3 消融；P1 覆盖审计（负结果）；B1 最差组/high-μ RMSE（负结果）；B2 \(\Delta_{c\text{-}s}\)↔RMSE\(_\mu\)（负结果）；20 配对种子 + Wilcoxon + Holm。
- **Stated limitations:** 不声称 universal RMSE；不声称覆盖后果；不声称最差组 RMSE 优势；裁剪下无精确无偏；solver 无回溯最优认证；Use 无孤立效应；Debt 效应极小；NSW-Traffic 不用于方法推断；无独立真实轨迹验证；FedAU-Window / ObsUse-Window / TimeAlign 均非官方复现。

## 4. Search And Related-Work Basis

```text
Queries used:
  Shimodaira 2000 improving predictive inference covariate shift importance weighting
  FedAU Wang Ji ICLR 2024 federated learning unknown participation adaptive aggregation
  Byrd Lipton 2019 what is the effect of importance weighting in deep learning
Sources searched:
  Web search / ICLR proceedings / OpenReview / PMLR / JSPI 书目页 / arXiv
Closest works found:
  FedAU (Wang & Ji, ICLR 2024): 未知参与统计下的自适应聚合重加权。论文已引并作 windowed 基线。
  Shimodaira (2000, JSPI 90:227–244): 训练协变量分布 ≠ 目标总体时的加权似然。论文未引。
  Byrd & Lipton (2019, ICML/PMLR 97:872–881): 过参数化网络中 importance weighting 随训练消失。论文未引。
  sun2025debiasing: 相关参与偏置去偏。论文已引，未作基线。
Unverified related-work risks:
  未逐条核对 reference.bib 全部 PDF；未核官方 FedAU 与 FedAU-Window 的权重更新是否算法等价。
Source-quality screening status:
  FedAU、Shimodaira、Byrd & Lipton 已核到正式出处；其余自引文献未逐条核对 PDF。
```

## 5. Expected Review Outcome

```text
Expected outcome: Weak reject（borderline-negative；比上一轮更稳的弱拒）
Main accept signal: 问题表述对 TMC 仍有价值；FedAU-Window 对比把“参与重加权 ≠ 层对齐”做实；负结果纪律在 TMC 少见，B1/B2 未藏。
Main reject signal: 2–4% 结构代理指标；覆盖打平；最差组 RMSE 不跟 \(\Delta_{c\text{-}s}\)；within-seed 上更差的结构对应更好的预测（FedAU 模式）。技术部件仍是标准 IW + 小 QP。
Confidence: 4/5
```

不给出接受概率。上一轮 5.5/10 的加分条件（“覆盖阈值消不掉的下游指标”）已被 B1/B2 实测并失败，因此本轮不再把同一条写成可快速加分路径。

## 6. Strengths And Weaknesses

**Strengths**
- 主张上限与负结果纪律比上一轮更严：覆盖、最差组 RMSE、结构–预测关联三条翻译测试都写进 §VII-A，且方向与证据一致。
- FedAU-Window 对比仍是最有力的机制证据：参与重加权可改善 U-Air 预测，但在两数据集上恶化 \(\Delta_{c\text{-}s}\)。
- 统计政策规范：配对 Wilcoxon + Holm + 20 种子 + 共享 selection trace；B1 与 sealed RMSE\(_\mu\) 的 reload 校验（382/400 差 \(<10^{-6}\)）写在审计产物中。
- 编译干净：24 页，0 `!`，0 undefined，0 Overfull。

**Weaknesses**

```text
Weakness: 定量收益仍只落在结构代理指标，且三条部署翻译测试均为负。
Evidence basis: Table III 3.96%/2.01%、2.62%/2.28%；§VII-A 覆盖 20/20 打平；B1 U-Air 最差组 FedAU 1.607 vs RAVEN 1.705（20/20）；B2 within-seed Spearman U-Air −0.79。
Reviewer deduction: \(\Delta_{c\text{-}s}\) 是作者自选目标上的强度分配，不是 MCS 部署者会改变的决策量。
Required fix: 需要覆盖/最差组/RMSE 之外的操作指标，或把投稿定位收到“表述+理论”并接受 TMC 长文风险。写作不能把负结果说成部署收益。
```

```text
Weakness: 技术新颖性仍偏增量。
Evidence basis: §I 贡献句承认积木标准；§II 引用 Horvitz–Thompson/Hájek；未引 Shimodaira 2000。
Reviewer deduction: 审稿人可将其读成 MCS 外壳的顺序 covariate-shift IW + 小凸规划。
Required fix: 补 covariate-shift / IW 失效文献并论证三层信息边界为何不能被单次密度比替代。
```

```text
Weakness: FedAU 为 windowed 改编；sun2025 仍未对比。
Evidence basis: §VI-A 基线清单；Availability 段自承非官方复现。
Reviewer deduction: 最强参与基线仍可能被质疑不公平或覆盖不全。
Required fix: 算法差异表，或补 sun2025 同协议对比。
```

```text
Weakness: 结论段未吸收 B1/B2；引言仍写 strongly convex。
Evidence basis: §VIII 仍写“consistent structural correction with comparable prediction”；§I L141。
Reviewer deduction: 诚实写在 limitation，主叙事仍像结构优势可独立成立。
Required fix: 结论点明结构优势不翻译为最差组/预测；引言改为 \(\lambda_\beta\)-strongly convex。
```

### Writing review scorecard (full mode)

| Dimension | Weight | Score (1-5) | Confidence | Evidence basis | Concrete repair |
| --- | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | §I 问题清楚 | 保持；勿把 \(\Delta_{c\text{-}s}\) 再升格为部署后果 |
| Contribution display | 12 | 4 | 4 | §I 表述优先 | 结论与摘要对齐 B1/B2 上限 |
| Paragraph logic | 10 | 4 | 4 | §VII-A 覆盖+B1/B2 段过密 | 拆成两个短段或加一句 topic sentence |
| Claim-evidence alignment | 14 | 4 | 5 | 摘要不声称覆盖；B1/B2 在 limitation | 结论补一句非翻译 |
| Method readability | 10 | 4 | 4 | §III–V | 引言 \(\lambda_\beta\) |
| Experiment narration | 10 | 3 | 4 | B1/B2 无表；Fig 3/4 无 Holm 星 | 主文加一小表或把数字留在 limitation 但给交叉引用 |
| Related-work positioning | 8 | 3 | 4 | §II 无 Shimodaira/Byrd | 加一段划界 |
| Terminology and notation | 8 | 4 | 4 | 全文稳定 | — |
| LaTeX and format | 8 | 4 | 5 | 编译 0 Overfull | 作者行半匿名整理 |
| Reviewer-facing risk | 8 | 3 | 4 | R2 将用 B1/B2 作拒稿弹药 | 接受 limitation 或换指标/venue |

**Writing score:** \(3.74/5\)。**Writing risk band:** moderate–high（experiment narration、related-work、reviewer-facing 各 3）。

### Format verdict

```text
Format verdict: 可审；无编译级阻断
Blocking compliance issues: 无
LaTeX/source issues: 作者行 **** + 具名混用；引言 strongly convex 未点 \(\lambda_\beta\)
Figure/table/caption issues: Fig 3/4 仍无显著性标记；B1/B2 无表
Citation/reference issues: 缺 Shimodaira / Byrd；sun2025 只引不比
Notation/equation issues: 无未定义引用（编译 0 undefined）
Suggested checks or build command: 已编译 `_paper_work` pdflatex×bibtex×pdflatex×2；24 页，0 !，0 Overfull
```

## 7. Potentially Missing Related Work

```text
Work: Shimodaira 2000, JSPI 90:227–244
Status: searched
Why relevant: 训练协变量分布 ≠ 目标总体 + 密度比加权，与本文核心同族
Overlap: 高（概念同族）
Needed comparison: 划清“顺序三层选择 + 可行性校准”相对单次密度比的差异
```

```text
Work: Byrd & Lipton 2019, ICML/PMLR 97:872–881
Status: searched
Why relevant: 过参数化模型中 IW 随训练消失；可解释“结构对齐不必降低 RMSE”
Overlap: 中
Needed comparison: 说明裁剪、有限容量补全模型、以及为何 \(\Delta_{c\text{-}s}\) 不翻译为 RMSE
```

```text
Work: sun2025debiasing
Status: user-provided（论文已引）
Why relevant: 相关参与导致 FedAvg 偏置
Overlap: 中高
Needed comparison: 同 seed 对比，或明确为何 windowed FedAU 已覆盖该轴
```

```text
Work: 官方 FedAU (ICLR 2024)
Status: searched；论文用 windowed 改编
Why relevant: 最直接的参与重加权方法
Overlap: 高
Needed comparison: 正文已对比改编版；审稿人仍可能要求官方实现或差异表
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
|---|---|---|---|---|---|
| 到达风险 ≠ 部署目标风险 | 摘要 / Prop 1 / §VI-A | E2（\(D_{\mathrm{aligned}}\approx-0.021\)）+ Prop 1 | adequate | 命题近乎平凡；实证干净 | 补 covariate-shift 文献定位 |
| RAVEN 相对 FedAvg 降低结构失配 3.96%/2.01%、2.62%/2.28% | 摘要 / §VI-B / Table III | 20 种子 mean±std | strong | 数字与正文一致；仍是最硬的正结果，但是代理指标 | 无需改数字；勿升格为部署后果 |
| 预测竞争性 + 选择性增益 | 摘要 / §VI-B | Table III；U-Air 对 TwoStage RMSE −2.04% | adequate | 对 FedAvg 预测不显著；U-Air 上 FedAU 预测更好 | 当前摘要已收窄，保持 |
| 相对 FedAU，\(\Delta_{c\text{-}s}\) 优势成立 | §VI-B | 两数据集 Holm-显著；U-Air \(\Delta_{\mathrm{group}}\)/预测仍利于 FedAU | strong for \(\Delta_{c\text{-}s}\) only | 机制论点成立，不能写成全面优于 FedAU | 已基本做到 |
| drifting 保持结构优势 | §VI-B | \(\Delta_{c\text{-}s}\) vs FedAU 两数据集 Holm-显著；U-Air \(\Delta_{\mathrm{group}}\)/预测仍利于 FedAU；vs TwoStage U-Air \(\Delta_{c\text{-}s}\) 不显著 | adequate | 不是“漂移处最能赢” | 已诚实 |
| \(\Delta_{c\text{-}s}\) 有覆盖后果 | §VII-A / P1 | vs FedAvg/TwoStage 20/20 打平；vs FedAU 5.8/13867.5 | absent as positive | 负结果成立 | 保持；勿改写为优点 |
| \(\Delta_{c\text{-}s}\) 有最差组 RMSE 后果 | §VII-A / B1 | SS 五方法约 9.05 无 Holm 差；U-Air FedAU 1.607 vs RAVEN 1.705（20/20，基线更好） | absent as positive；opposite on U-Air | 上一轮加分条件已关闭 | 已写入 limitation；结论应点明 |
| 更差 \(\Delta_{c\text{-}s}\) 伴随更差 RMSE\(_\mu\) | §VII-A / B2 | within-seed Spearman：SS \(\approx-0.09\)；U-Air \(\approx-0.79\) | absent as positive；U-Air 反向 | 结构–预测方法级关联是 FedAU 权衡，不是 RAVEN 的“所以更好” | 已写入；勿把 pooled SS +0.27 当成支持 |
| 理想顺序校正恢复目标律 | Prop 2 | 附录，A1–A3 | adequate | 识别全压强假设 | 已写边界 |
| 校准有唯一全局解 | Thm 1 | 附录，A4；\(\lambda_\beta\)-强凸 | strong | 引言仍写 strongly convex 而未点名 \(\lambda_\beta\) | 引言与摘要对齐附录措辞 |
| Use 层完成两阶段结构 | 贡献 2 / E4 | E4 无显著孤立效应 | adequate as completeness claim | 不能再写成经验必要 | 已改 |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines:** FedAvg / FedAsync / TimeAlign-Agg / Local-Hájek / TwoStage-Hájek / FedAU-Window / ObsUse-Window / Inst-Cal / Debt-Cal。Local-Hájek 在正式块退化为 FedAvg。TimeAlign、FedAU-Window、ObsUse-Window 均非官方复现。sun2025debiasing 仍缺。
- **Ablations:** E4 单因素移除，负结果诚实。ObsUse 链在 \(\Delta_{c\text{-}s}\) 上非单调，已写入。
- **Datasets:** SensorScope + U-Air 主比较；NSW-Traffic 仅 E2；泛化面仍窄。
- **Metrics:** RMSE\(_\mu\)、Tail RMSE、\(\Delta_{\mathrm{group}}\)、\(\Delta_{c\text{-}s}\)；覆盖与最差组 RMSE 为后补 limitation，**主表仍未报效应量，也未报 worst-group**。
- **Statistical rigor:** 配对 Wilcoxon + Holm + 20 种子 + 共享 trace。规范。B1 用同一 reload 路径；B2 用 sealed RMSE\(_\mu\)。18/400 reload 差最大 0.058，未覆盖 sealed 指标，可接受。
- **Robustness/failure:** drifting、覆盖、最差组、结构–预测关联构成完整压力测试。四者都没有把 RAVEN 推成全面赢家；后三者直接否定部署翻译。
- **Implementation details:** P2 solver 与源码仍为 camera-ready 承诺。
- **Artifacts/reproducibility:** 数据 DOI / 冻结 traces / 种子已声明；**源代码仍为 camera-ready 承诺**。B1/B2 CSV 在 `_paper_work/worst_group_results/`，不在投稿主表。
- **Limitations:** 优秀（§VII），且 B1/B2 未假装未做。结论段滞后于 limitation。

## 10. Multi-Reviewer Panel

```text
Reviewer: R1 Best-Justified
Expertise: TMC / MCS systems, sympathetic reading
Likely score: 6/10
Confidence: 4
Main positive signal: 到达≠目标的问题对 TMC 有价值；FedAU 对比把机制做实；B1/B2 诚实披露。
Main negative signal: 三条翻译测试失败后，只剩 2–4% 代理指标。
Evidence basis: §II、Table III、§VII-A 覆盖+B1/B2。
Fatal concern: 无。
Score-change condition: 若有覆盖/最差组/RMSE 之外的操作指标（能耗、时延、调度决策），可到 7。该条件不再包括 worst-group RMSE。
```

```text
Reviewer: R2 Critical
Expertise: skeptical TMC / FL empirical
Likely score: 4/10
Confidence: 4
Main positive signal: 写作诚实，未藏 B1/B2。
Main negative signal: 标准抽样校正 + 小 QP；2% 代理；覆盖打平；U-Air 最差组 FedAU 显著更好；within-seed Spearman −0.79。把贡献改写成 formulation 像实证撤退。
Evidence basis: §I 贡献句、§VII-A、B1 1.607 vs 1.705、B2 −0.79。
Fatal concern: significance collapse（代理指标无部署后果，且作者自己的 follow-up 证实）。
Score-change condition: 独立操作指标，或承认更适合 workshop/短文而非 TMC 长文。
```

```text
Reviewer: R3 Method / Soundness
Expertise: identification / convex programs
Likely score: 5/10
Confidence: 4
Main positive signal: 假设、理想/裁剪分离、证明完整。
Main negative signal: Prop 1 近乎测度论同义反复；Prop 2 压在 A1–A3；Thm 1 唯一性来自 \(\lambda_\beta\)。
Evidence basis: §V、附录。
Fatal concern: 无。
Score-change condition: 一个非平凡结构结论（例如债务在漂移下的非真空界）。
```

```text
Reviewer: R4 Evidence / Experiment
Expertise: empirical FL / MCS evaluation
Likely score: 6.5/10
Confidence: 4
Main positive signal: FedAU/ObsUse/drift/coverage/B1/B2 构成比上一轮更完整的证据包；负结果方向正确。
Main negative signal: FedAU 非官方；sun2025 未跑；主表无效应量、无 worst-group 表；B1/B2 只在讨论。
Evidence basis: Table III、§VI-B、§VII-A、worst_group_results。
Fatal concern: 无。
Score-change condition: 官方 FedAU 或 sun2025 同协议对比；主文给 B1 一小表。
```

```text
Reviewer: R5 Novelty / Positioning
Expertise: domain adaptation / survey sampling / FL
Likely score: 4.5/10
Confidence: 4
Main positive signal: 定位与证据更一致（不再假装方法赢基准）。
Main negative signal: 未划界 Shimodaira/Byrd；联合链的非平凡性仍靠叙述。
Evidence basis: §II；联网检索。
Fatal concern: 若划界后被认为是 MCS 外壳的 IW。
Score-change condition: 补文献并论证三层信息边界为何不能被单次密度比替代。
```

```text
Reviewer: R6 Writing / Clarity
Expertise: manuscript reviewability
Likely score: 6/10
Confidence: 4
Main positive signal: 故事线闭环；B1/B2 未藏。
Main negative signal: 结论未吸收 B1/B2；引言 strongly convex；Fig 3/4 无星；§VII-A 过密。
Evidence basis: §VIII、§I L141、Fig 3–4、§VII-A。
Fatal concern: 无。
Score-change condition: 结论一句非翻译 + \(\lambda_\beta\) 措辞。
```

```text
Reviewer: R7 Ethics / Reproducibility
Expertise: artifacts / responsible reporting
Likely score: 5.5/10
Confidence: 4
Main positive signal: 公开数据、冻结 traces、非官方复现披露、负结果披露。
Main negative signal: 评审阶段仍无代码；无独立真实轨迹验证。
Evidence basis: Reproducibility 段。
Fatal concern: 无（TMC 常接受 camera-ready 代码，但会降 repro 分）。
Score-change condition: 评审期匿名仓库。
```

```text
Reviewer: Domain Application
Expertise: MCS deployment practice
Likely score: 3/5 (practical validity)
Confidence: 4
Main positive signal: 问题来自真实 MCS 两阶段选择。
Main negative signal: 覆盖与最差组都不支持改变部署决策；评价用合成 selection trace。
Evidence basis: §VII-A P1/B1；无真实轨迹。
Fatal concern: 无独立致命，但强化 R2。
Score-change condition: 真实轨迹或操作指标。
```

```text
Reviewer: Evidence/Ablation (dedicated)
Expertise: experimental isolation
Likely score: 4/5
Confidence: 4
Main positive signal: E4 负结果诚实；B1/B2 补了缺失的下游审计。
Main negative signal: Use 无孤立效应仍留在贡献结构里；B1 未进主表。
Evidence basis: E4、§VII-A。
Fatal concern: 无。
Score-change condition: 主表收录 worst-group；或把 Use 从经验贡献降为理论完备性。
```

```text
Reviewer: Reproducibility (dedicated)
Expertise: independent rerun
Likely score: 3/5
Confidence: 4
Main positive signal: 种子、traces、DOI、协议密封。
Main negative signal: 无评审期代码与 P2 solver。
Evidence basis: Availability 段。
Fatal concern: 无。
Score-change condition: 匿名代码。
```

```text
Reviewer: Novice Advocate
Expertise: first-pass readability
Likely score: 4/5
Confidence: 4
Main positive signal: 摘要与贡献句可恢复主旨。
Main negative signal: §VII-A 一段叠三种负结果；新手会以为结构指标仍等于部署收益，因为结论没改。
Evidence basis: 摘要、§VIII vs §VII-A。
Fatal concern: 无。
Score-change condition: 结论与 limitation 对齐。
```

**Panel Synthesis**

```text
Agreement: 诚实度高；FedAU-Window 有用；定量影响小；新颖性增量；B1/B2 关闭了“结构→部署误差”捷径。
Disagreement: 表述优先是加分（R1/R5/R6）还是撤退（R2）；B1/B2 是科学成熟（R4）还是 significance 死刑证明（R2）。
Decisive positive axis: 问题表述 + 机制对比（FedAU 恶化 \(\Delta_{c\text{-}s}\)）+ 负结果纪律。
Decisive negative axis: 代理指标收益小 + 覆盖/最差组/RMSE 三条翻译失败 + 标准工具组合。
Unresolved evidence: 官方 FedAU / sun2025；covariate-shift 划界；真实代码。
AC stance: Weak reject（比上一轮更稳）。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
|---|---|---|---|---|---|---|---|---|
| M1 | major | 技术新颖性偏增量；未划界 covariate-shift IW | §I–II；Shimodaira 2000 已检索未引 | Novelty | related-work | 补 Shimodaira/Byrd 并论证三层信息边界 | ccf-literature-searcher / ccf-paper-writer | 划界成立 novelty 3→4 |
| M2r | moderate | FedAU 仅为 windowed 改编；sun2025 仍未对比 | §VI-A；Availability | Evidence | experiment | 差异表或补 sun2025 | ccf-experiment-designer | 差异表清晰则不再升为 major |
| M3 | moderate | Use 层无孤立效应（已承认） | E4 / 贡献 2 | Novelty | writing | 保持；勿再暗示三层经验必要 | — | 已部分消化 |
| M4 | major | 定量收益小；覆盖、最差组、结构–预测三条翻译均为负 | Table III；§VII-A P1/B1/B2 | Significance | accepted-limitation 或 experiment | 给 \(\Delta_{c\text{-}s}\) 一个覆盖/最差组/RMSE 消解不了的操作含义，或把 TMC 贡献限制为表述/理论 | ccf-paper-writer（写作）或 ccf-experiment-designer（新指标） | 有独立操作证据 significance 3→4；**worst-group 已测失败，不再作为加分条件** |
| M5 | moderate | 代码未发布 | Availability 段 | Reproducibility | reproducibility | 评审期匿名仓库 | ccf-submission-checker | 有代码 repro 3→4 |
| M6 | moderate | 缺 covariate-shift 文献 | §II | Positioning | related-work | 同 M1 | ccf-literature-searcher | 同 M1 |
| M7 | moderate | 结论未吸收 B1/B2；主叙事仍像结构优势可独立成立 | §VIII vs §VII-A | Clarity | writing | 结论补非翻译一句 | ccf-paper-writer | clarity 局部；不升 overall |
| m1 | minor | 引言 strongly convex 未写 \(\lambda_\beta\) | §I L141 vs 附录 | Clarity | writing | 改为 \(\lambda_\beta\)-strongly convex | ccf-paper-writer | — |
| m2 | minor | 主表未报效应量；B1 无表 | §VI；worst_group_results | Evidence | writing | 补 paired effect size；可选 B1 小表 | ccf-experiment-designer / ccf-paper-writer | — |
| m3 | minor | Fig 3/4 无显著性标注 | Fig 3/4 | Clarity | writing | 加 Holm 标记 | ccf-figure | — |

## 12. AC / Meta-Review

- **Reviewer consensus:** 这是一篇论证纪律很好、经验增量有限的 TMC 长文。FedAU-Window 之后，“最强基线缺失”不再是致命伤。B1/B2 之后，“结构对齐的 so-what 尚未检验”也不再成立——已经检验，结果为负。
- **Reviewer disagreement:** 表述优先是诚实还是撤退；B1/B2 是加分的科学成熟还是拒稿的 significance 证明。AC 采后者作为决策轴：诚实提高 Ethics，但不提高 Significance。
- **Decisive acceptance axis:** 把 MCS 异步补全从“到达即总体”改写成部署目标对齐，并用 FedAU 证明参与重加权不够。
- **Decisive rejection axis:** 2–4% 结构代理 + 覆盖打平 + 最差组不跟结构（U-Air 上 FedAU 更好）+ within-seed 负相关 + 标准积木。
- **AC stance:** Weak reject。Major Revision 仍可能，但修订必须是新操作指标或理论深度，不能再靠写作把负结果说成特征。
- **Discussion risks:** 讨论会集中在“这是不是把 IW 换了 MCS 外壳，再用 limitation 段把三次失败的翻译说成 formulation 的内在性质”。

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 3 | 4 | §I–II、§V；Shimodaira 未引 | 部件已知；划界后可到 4 |
| Soundness | 4 | 4 | §V、附录 | 自洽；Prop 1 偏平凡 |
| Evidence | 4 | 4 | Table III、FedAU/ObsUse/drift/coverage/B1/B2 | 完整度相对上一轮上升；官方 FedAU/sun2025 与主表 worst-group 可巩固，但不因负结果降到 3 |
| Significance | 3 | 4 | Table III、§VII-A P1/B1/B2 | 三条翻译失败把上限钉死；独立操作指标才可能 3→4；**worst-group 不再是修复条件** |
| Clarity | 4 | 4 | 全文；§VIII 滞后于 §VII-A | 结论对齐 B1/B2 可去局部风险 |
| Reproducibility | 3 | 4 | Availability 段 | 有 traces/种子，无评审期代码；有代码 3→4 |
| Ethics / Limitations | 5 | 4 | §VII 含 B1/B2 | 示范级；已满分 |

**Overall:** 5 / 10 ｜ **Scholarly Confidence:** 4 / 5
**Recommendation:** **weak-reject**（IEEE TMC/CCF-A；borderline-negative，比上一轮 5.5 更稳）
**Verdict:** 相对同日上一份报告，Evidence 完整度上升但分数保持 4；Significance 仍锁在 3，且加分条件收窄。总分 5.5→5.0。B1/B2 的诚实披露维持 Ethics=5，并阻止降到 4（clear reject）；它们不能把弱拒变成接收。

Compact summary:

```text
Quality: 4
Clarity: 4
Significance: 3
Originality: 3
Soundness: 4
Evidence: 4
Reproducibility: 3
Ethics / Limitations: 5
Overall: 5/10
Confidence: 4/5
Score-change conditions: 见下表
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | 覆盖/最差组/RMSE 之外的操作指标成立 | Significance | +0.5 to +1 overall（5→6/7） |
| Raise score | Shimodaira/Byrd 划界使三层链显得非平凡 | Novelty | dimension-only 3→4；overall 至多 +0.5 |
| Raise score | 评审期代码 | Reproducibility | dimension-only 3→4 |
| Lower score | 官方 FedAU 后 \(\Delta_{c\text{-}s}\) 优势消失 | Evidence / Significance | −0.5 to −1 overall |
| No quick change | 预测端不显著、覆盖打平、最差组不跟、Prop 1 平凡 | Significance / Novelty | 提交前不可靠写作修复 |

## 14. Questions For Authors

1. 在覆盖打平、U-Air 最差组 RMSE 显著差于 FedAU、且 within-seed Spearman 为负的情况下，2% 的 \(\Delta_{c\text{-}s}\) 下降对 MCS 部署决策的不可替代价值是什么？
2. FedAU-Window 与官方 FedAU 的权重更新有何不同？为何 sun2025debiasing 只引用不对比？
3. 三层中的 Use 在 E4 中无孤立效应，保留它的经验（而非理论）理由是什么？
4. 为何不把工作放进 covariate-shift / target-population 重加权谱系，并用 B2 的负相关对接 Byrd & Lipton 式 IW 失效？
5. 评审阶段能否提供匿名代码与 P2 solver，而不是只承诺 camera-ready？

## 15. Score Revision Criteria

```text
Raising the score would require:
  一个不能被覆盖阈值、最差组 RMSE 或 RMSE_μ 消解的操作/部署指标；或 covariate-shift 划界使联合链显得非平凡；评审期代码。官方 FedAU 或 sun2025 对比若不翻转 Δ_c-s，可巩固 Evidence，但单独不够把 overall 从 5 拉到 7。
Lowering the score would be triggered by:
  官方 FedAU 对比后 Δ_c-s 优势消失；被指出 Prop 2 假设在真实 MCS 中不可识别。
Concerns unlikely to change before submission:
  预测端不显著、覆盖打平、最差组不跟结构、U-Air 上结构–预测负相关、Prop 1 平凡性。这些是已测事实，不是措辞问题。
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: 1
Action: 决定投稿策略——(a) 接受 significance 上限，把 TMC 贡献明确限制为表述/理论；或 (b) 设计覆盖/最差组/RMSE 之外的操作指标。不要再把 B1/B2 改写成优势。
Owner skill: ccf-paper-writer（(a)）或 ccf-experiment-designer（(b)）
Input needed: 作者对 venue 风险的选择
Expected output: 定位修订或新实验协议
Handoff required: yes（改变研究阶段）
```

```text
Priority: 2
Action: 补 Shimodaira 2000 与 Byrd & Lipton 2019，并划清顺序三层 + 可行性校准相对单次密度比的差异；可用 B2 负相关作为 IW 不自动改善预测的经验注记。
Owner skill: ccf-literature-searcher + ccf-paper-writer
Input needed: §II 现有参与偏置段
Expected output: 一段划界文字 + bib 条目
Handoff required: yes
```

```text
Priority: 3
Action: 结论吸收 B1/B2；引言改为 λ_β-strongly convex；可选把 worst-group 均值做成极小表；FedAU 改编差异表。
Owner skill: ccf-paper-writer
Input needed: §VII-A 现有数字、附录 Thm 1
Expected output: 局部写作修订
Handoff required: yes（若进入改稿）
```

```text
Priority: 4
Action: 评审期匿名代码 + P2 solver。
Owner skill: ccf-submission-checker
Input needed: 仓库与匿名化策略
Expected output: Availability 段从承诺改为可审链接
Handoff required: yes
```

```text
Checks run: desk 评估、claim-evidence 审计、实验/基线/可复现审计、多审稿人 panel（含 domain/ablation/repro/novice）、写作评分、LaTeX 编译核验、联网相关工作抽查、相对同日旧报告的 delta。
Checks skipped: reference.bib 逐条 PDF 核对；官方 FedAU 代码级等价性核验；TMC 当年官方投稿页复核（期刊页限/单盲以既有惯例计）。
Unresolved risks: 表述转向被读成撤退；significance 在无新操作指标时弱拒稳定；R2 将直接引用 B1/B2。
```
