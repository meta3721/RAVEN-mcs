# CCFA 论文评审报告 — RAVEN-MCS（pass 3，写作修订后）

## 1. Report Metadata

- **Review date:** 2026-08-18（第三轮）
- **Target venue/year/track:** IEEE Transactions on Mobile Computing（TMC，CCF-A，计算机网络/移动计算期刊）
- **Paper title:** RAVEN-MCS: Deployment-Target Risk Alignment for Asynchronous Federated Data Completion in Mobile Crowdsensing under Two-Stage Non-Random Selection
- **Input materials reviewed:** `_paper_work/main.tex`、`_paper_work/main.pdf`（24 页，作者已编译）、`reference.bib`、既有 P0/P1/B1/B2 审计产物
- **Search basis:** 沿用 pass 2 对 FedAU / Shimodaira 2000 / Byrd & Lipton 2019 的检索；本轮补检 sequential IPW / missing-data（Robins, Rotnitzky & Zhao 1994 一类）
- **Report file:** `_paper_work/ccfa-review-reports/2026-08-18-raven-mcs-tmc-conference-review-pass3.md`
- **Reviewer mode:** `full`
- **相对 pass 2（5.0/10）的材料变化:** 写作修订，无新实验。可见改动：(i) §II 补 Shimodaira/Byrd 并给出两点划界；(ii) 引言改为 \(\lambda_\beta\)-strongly convex；(iii) 结论吸收覆盖/最差组/Spearman 三条边界；(iv) 作者行改为 `Author One and Author Two`。未改：主表效应量、Fig 3/4 Holm 星、FedAU 算法差异表、sun2025 对比、评审期代码、科学数字。

## 2. Desk Rejection Assessment

- **Paper length:** 通过（24 页含附录）
- **Topic compatibility:** 通过
- **Minimum quality:** 通过
- **Policy/anonymity/compliance:** 通过（TMC 期刊通常单盲；现为占位作者名 + NSFC 致谢，可接受）
- **Prompt injection / hidden manipulation:** 未发现
- **Ethics and reviewability:** 通过
- **Desk rejection risk:** none
- **结论:** 不 desk reject。

## 3. Paper Summary And Contribution Map

**一句话总结：** 异步联邦 MCS 补全被写成部署目标风险对齐：到达律 ≠ 目标律；分层 IPW/Hájek 重建后再做可行性校准。RAVEN 是构造性实例。经验上相对 FedAvg 有 2–4% 结构代理收益；覆盖、最差组 RMSE、结构–预测关联三条翻译均为负，结论现已点明。

- **Claimed problem / gap / method:** 与 pass 2 相同（三层选择、参与重加权不够、表述+理论+构造实例）。
- **Evidence package:** 与 pass 2 相同（E1–E4、FedAU-Window、drift、P1、B1/B2）。无新表。
- **Stated limitations:** 与 pass 2 相同，且结论现在复述三条非翻译边界。

## 4. Search And Related-Work Basis

```text
Queries used (this pass): sequential inverse probability weighting missing data Horvitz Thompson
Sources searched: web / PMC / survey-sampling notes
Closest works found:
  Shimodaira 2000 JSPI — 已引，§II 划界成立。
  Byrd & Lipton 2019 ICML — 已引，用来解释结构不自动降 RMSE。
  FedAU ICLR 2024 — 已引并作 windowed 基线。
  Robins, Rotnitzky & Zhao 1994 一类 sequential / augmented IPW — 未引。
Unverified related-work risks:
  顺序缺失数据 IPW / AIPW 仍未划界；Byrd 的过参数化设定与本稿补全模型是否同类未论证。
Source-quality screening: Shimodaira / Byrd / FedAU 已核正式出处；Robins 1994 本轮检索到二次综述引用，未打开原文 PDF。
```

## 5. Expected Review Outcome

```text
Expected outcome: Borderline / weak reject
Main accept signal: 问题表述清楚；FedAU 机制对比仍在；负结果纪律完整；covariate-shift 划界补上后，IW-外壳攻击变弱。
Main reject signal: Significance 未动。2–4% 代理 + 三条翻译失败 + 标准积木。写作不能把弱拒变成接收。
Confidence: 4/5
```

相对 pass 2：Novelty 3→4 使 overall **5.0→5.5**。仍低于弱收线（7）和 borderline-positive（6）。

## 6. Strengths And Weaknesses

**Strengths**
- Pass 2 要求的 Shimodaira/Byrd 划界已写入 §II：顺序三层信息集 + 可行集校准，相对单次密度比。
- 结论与 §VII-A 对齐：结构收益“不翻译为更好覆盖、更低最差组误差、或正的 within-seed 结构–预测关联”。
- \(\lambda_\beta\)-strongly convex 与附录一致。
- 负结果包（Use / Debt / drift / 覆盖 / B1/B2）仍完整。

**Weaknesses**

```text
Weakness: Significance 仍锁在代理指标，三条部署翻译已测失败。
Evidence basis: Table III；§VII-A；§VIII 新句只是复述负结果。
Reviewer deduction: 写作使主张更难被打，但不创造 TMC 所需的部署后果。
Required fix: 覆盖/最差组/RMSE 之外的操作指标，或接受表述论文的 venue 风险。
```

```text
Weakness: 积木仍是 HT/Hájek + 小 QP；sequential IPW 文献仍未引。
Evidence basis: §I–II；本轮检索到 Robins et al. 1994 一类。
Reviewer deduction: 划界 Shimodaira 足够把 Novelty 从“未定位”升到“已定位的增量贡献”，不足以变成非平凡方法。
Required fix: 可选补 sequential missing-data；不能指望再升 overall。
```

```text
Weakness: Byrd 类比可能过宽。
Evidence basis: §II “over-parameterized models”；本稿是有限容量补全模型。
Reviewer deduction: 审稿人可能认为这是方便的事后解释。
Required fix: 收窄为“IW 不保证预测收益”，不要绑定过参数化机制。
```

```text
Weakness: FedAU 改编差异、sun2025、评审期代码、主表效应量、Fig 3/4 星标仍缺。
Evidence basis: §VI-A、Availability、Table III、Fig 3/4 captions。
Reviewer deduction: 次要但可被点名。
Required fix: 差异表 / 匿名仓库 / 效应量或星标。
```

### Writing review scorecard (full mode)

| Dimension | Weight | Score | Confidence | Evidence basis | Concrete repair |
| --- | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | §I | 保持 |
| Contribution display | 12 | 4 | 4 | §I + §VIII | 摘要仍只写 coverage，可加半句 worst-group |
| Paragraph logic | 10 | 4 | 4 | §II 新段可读 | Byrd 句可再收 |
| Claim-evidence alignment | 14 | 4 | 5 | 结论对齐 B1/B2 | 摘要可选对齐 |
| Method readability | 10 | 4 | 4 | \(\lambda_\beta\) 已改 | — |
| Experiment narration | 10 | 3 | 4 | B1 无表；Fig 3/4 无星 | 小表或星标 |
| Related-work positioning | 8 | 4 | 4 | Shimodaira/Byrd 已划界 | 可选 sequential IPW |
| Terminology | 8 | 4 | 4 | 稳定 | — |
| LaTeX and format | 8 | 4 | 5 | 24 页已编译 | — |
| Reviewer-facing risk | 8 | 3 | 4 | M4 仍是拒稿轴 | 新操作指标，非措辞 |

**Writing score:** \(3.82/5\)（pass 2 为 3.74）。**Risk band:** moderate（related-work 已离开 3；reviewer-facing 与 experiment narration 仍为 3）。

### Format verdict

```text
Format verdict: 可审；作者已编译 24 页
Blocking compliance issues: 无
LaTeX/source issues: 无未定义引用（main.log 无 undefined / Overfull / !）
Figure/table/caption issues: Fig 3/4 仍无 Holm 标记；B1/B2 无表
Citation/reference issues: Shimodaira/Byrd 已入 bib 并引用；sun2025 仍只引不比；sequential IPW 未引
Notation/equation issues: \(\lambda_\beta\) 已与附录对齐
Suggested checks: 已见 pass3.log / main.pdf 24 pages
```

## 7. Potentially Missing Related Work

```text
Work: Shimodaira 2000
Status: searched；现为 user-provided citation
Why relevant: 目标总体重加权
Overlap: 高
Needed comparison: 已做两点划界。可关闭为主要缺口。
```

```text
Work: Byrd & Lipton 2019
Status: searched；现为 user-provided citation
Why relevant: IW 不必改变拟合预测
Overlap: 中；模型类可能不匹配
Needed comparison: 收窄类比，避免过参数化断言。
```

```text
Work: Robins, Rotnitzky & Zhao 1994 一类 sequential / augmented IPW
Status: searched
Why relevant: 顺序缺失下的分层逆概率加权，比单次 Shimodaira 更近
Overlap: 中高（顺序校正）
Needed comparison: 说明 MCS 三层信息边界与可行集校准相对缺失数据 AIPW 的差异
```

```text
Work: 官方 FedAU；sun2025debiasing
Status: searched / user-provided
Why relevant: 参与重加权
Overlap: 高
Needed comparison: 差异表或同协议对比（未变）
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence | Strength | Reviewer deduction | Required fix |
|---|---|---|---|---|---|
| 到达风险 ≠ 目标风险 | 摘要 / Prop 1 / E2 | \(D_{\mathrm{aligned}}\approx-0.021\) | adequate | 命题平凡，实证干净 | 已有 covariate-shift 定位 |
| vs FedAvg 结构 −3.96%/−2.01%、−2.62%/−2.28% | 摘要 / Table III | 20 种子 | strong | 最硬正结果，仍是代理 | 勿升格 |
| vs FedAU 的 \(\Delta_{c\text{-}s}\) | §VI-B | 两数据集 Holm | strong for \(\Delta_{c\text{-}s}\) | U-Air 预测/Δ_group 仍利于 FedAU | 保持 |
| 预测可比、选择性增益 | 摘要 / §VI-B | vs TwoStage U-Air −2.04% | adequate | 对 FedAvg 不显著 | 保持 |
| 非覆盖 / 非最差组 / 非正 Spearman | §VII-A；**§VIII 新句** | P1/B1/B2 | strong as negative | 结论现与证据对齐 | 摘要仍只写 coverage |
| 相对单次密度比的两点差异 | §II 新段 | 论证，非新定理 | adequate as positioning | 足够支撑 Novelty 4，不是新理论 | 可选 sequential IPW |
| Use 层经验必要 | E4 | 无孤立效应 | absent as empirical | 已承认 | 保持 |
| 校准唯一解 | Thm 1 | \(\lambda_\beta\)-强凸 | strong | 引言已对齐 | 已消化 |

## 9. Experiment / Benchmark / Reproducibility Audit

与 pass 2 相同。无新运行、无新表、无官方 FedAU、无 sun2025、无评审期代码。B1/B2 仍只在讨论。统计政策仍规范。

## 10. Multi-Reviewer Panel

```text
Reviewer: R1 Best-Justified
Likely score: 6/10  Confidence: 4
Main positive: 问题仍值得 TMC 讨论；划界后更像一篇诚实的表述论文。
Main negative: 仍无操作指标。
Evidence: §II 新段、Table III、§VII–VIII。
Fatal: 无。
Score-change: 覆盖/最差组/RMSE 之外的操作指标 → 7。
```

```text
Reviewer: R2 Critical
Likely score: 4/10  Confidence: 4
Main positive: 结论不再假装结构即部署。
Main negative: 2% 代理 + 三次翻译失败 + HT/QP。划界是文献修补，不是贡献升级。
Evidence: Table III、B1/B2、§II。
Fatal: significance collapse（仍在）。
Score-change: 新操作指标或换 venue。
```

```text
Reviewer: R3 Soundness
Likely score: 5/10  Confidence: 4
Main positive: \(\lambda_\beta\) 措辞与证明一致。
Main negative: Prop 1 平凡；Byrd 机制类比偏宽。
Evidence: §I L141、附录、§II。
Fatal: 无。
Score-change: 非平凡结构定理。
```

```text
Reviewer: R4 Evidence
Likely score: 6.5/10  Confidence: 4
Main positive: 证据包未缩水。
Main negative: 仍无 B1 表、效应量、官方 FedAU。
Evidence: 同 pass 2。
Fatal: 无。
Score-change: 同 pass 2。
```

```text
Reviewer: R5 Novelty
Likely score: 5.5/10  Confidence: 4
Main positive: Shimodaira 两点划界正是上一轮要求的。
Main negative: sequential IPW 仍更近；方法增量本质未变。
Evidence: §II；Robins 1994 检索。
Fatal: 无（IW-only 攻击已减弱）。
Score-change: 补 sequential IPW 可巩固 4/5 novelty，难再抬 overall。
```

```text
Reviewer: R6 Writing
Likely score: 6.5/10  Confidence: 4
Main positive: 结论吸收 B1/B2；\(\lambda_\beta\) 已改。
Main negative: 摘要未同步 worst-group；Fig 3/4 无星。
Evidence: 摘要 vs §VIII；Fig captions。
Fatal: 无。
Score-change: 摘要半句 + 图星标。
```

```text
Reviewer: R7 Repro
Likely score: 5.5/10  Confidence: 4
未变：camera-ready 代码承诺。
```

```text
Reviewer: Domain application  3/5  — 操作者仍不会据此改部署。
Reviewer: Evidence/ablation  4/5  — 未变。
Reviewer: Reproducibility    3/5  — 未变。
Reviewer: Novice advocate    4/5  — 结论现在不会误导“结构=部署收益”。
```

**Panel Synthesis**

```text
Agreement: 写作修订有效；Significance 未动；不 desk reject。
Disagreement: Novelty 4 是“定位完成”还是“仍增量”（R5 vs R2）。AC 给 Novelty 4、overall 只 +0.5。
Decisive positive axis: 表述 + FedAU 机制对比 + 负结果纪律 + covariate-shift 划界。
Decisive negative axis: 代理收益小 + 三条翻译失败。
Unresolved evidence: 官方 FedAU / sun2025 / 代码 / 操作指标。
AC stance: Borderline / weak reject（5.5）。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
|---|---|---|---|---|---|---|---|---|
| M4 | major | 结构收益无覆盖/最差组/RMSE 翻译 | Table III；§VII-A；§VIII | Significance | accepted-limitation 或 experiment | 新操作指标，或接受表述论文定位 | ccf-experiment-designer / ccf-paper-writer | 有独立操作证据 3→4；**写作已不能修** |
| M1 | moderate | 方法仍为标准 IW+QP；sequential IPW 未引 | §I–II；Robins 1994 检索 | Novelty | related-work | 可选补顺序缺失数据文献 | ccf-literature-searcher | 巩固 Novelty 4，难动 overall |
| M2r | moderate | FedAU windowed 改编；sun2025 未比 | §VI-A | Evidence | experiment | 差异表或对比 | ccf-experiment-designer | 不再升 major |
| M5 | moderate | 无评审期代码 | Availability | Reproducibility | reproducibility | 匿名仓库 | ccf-submission-checker | repro 3→4 |
| m-byrd | minor | Byrd 过参数化类比过宽 | §II | Soundness/Clarity | writing | 收窄措辞 | ccf-paper-writer | — |
| m2 | minor | 主表无效应量；B1 无表 | Table III | Evidence | writing | 效应量或小表 | ccf-paper-writer | — |
| m3 | minor | Fig 3/4 无 Holm 星 | Fig 3/4 | Clarity | writing | 加标记 | ccf-figure | — |
| M6 | — | Shimodaira 缺口 | 已引并划界 | — | — | **关闭** | — | Novelty 3→4 已兑现 |
| M7 | — | 结论未吸收 B1/B2 | §VIII 已写 | — | — | **关闭** | — | — |
| m1 | — | strongly convex 未写 \(\lambda_\beta\) | L141 已改 | — | — | **关闭** | — | — |

## 12. AC / Meta-Review

- **Reviewer consensus:** 这轮是有效的写作修订，不是科学修订。该补的文献补了，该对齐的结论对齐了。
- **Reviewer disagreement:** 划界是否让工作“够新”。AC：够把 Novelty 从 3 拉到 4，不够改变拒稿轴。
- **Decisive acceptance axis:** MCS 到达≠目标的表述 + 参与重加权不够的机制证据。
- **Decisive rejection axis:** 2–4% 代理指标，且作者自己的 B1/B2 证明它不变成部署误差。
- **AC stance:** Weak reject / borderline-negative。回到 pass 1 的 5.5，但 significance 上限比 pass 1 更硬（B1/B2 已测）。
- **Discussion risks:** “文献段写好了，所以呢仍然没有。”

## 13. Quantitative Scores

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 4 | 4 | §II Shimodaira/Byrd 两点划界 | 从 3 升到 4，因定位完成；方法仍增量。再升需要非平凡定理或 sequential IPW 上的实质差异，且难动 overall |
| Soundness | 4 | 4 | §V、附录、\(\lambda_\beta\) | Byrd 类比为小瑕疵，不降到 3 |
| Evidence | 4 | 4 | Table III、FedAU、P1、B1/B2 | 无新实验；官方 FedAU 可巩固 |
| Significance | 3 | 4 | Table III、§VII–VIII | **三条翻译失败**；新操作指标才可能 3→4 |
| Clarity | 4 | 4 | 结论已对齐；摘要未完全同步 | 局部可修，不升 overall |
| Reproducibility | 3 | 4 | Availability | 评审期代码 3→4 |
| Ethics / Limitations | 5 | 4 | §VII–VIII | 满分 |

**Overall:** 5.5 / 10 ｜ **Scholarly Confidence:** 4 / 5
**Recommendation:** **weak-reject** / borderline-negative（IEEE TMC）
**Verdict:** 相对 pass 2，Novelty 3→4，overall 5.0→5.5。相对 pass 1 的 5.5，分数相同但更稳：so-what 已测失败，不能再靠“尚未检验的下游指标”幻想加分。

```text
Quality: 4
Clarity: 4
Significance: 3
Originality: 4
Soundness: 4
Evidence: 4
Reproducibility: 3
Ethics / Limitations: 5
Overall: 5.5/10
Confidence: 4/5
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | 覆盖/最差组/RMSE 消不掉的操作指标 | Significance | +0.5 to +1 overall（5.5→6/7） |
| Raise score | 评审期代码 | Reproducibility | dimension-only |
| Lower score | 官方 FedAU 后 \(\Delta_{c\text{-}s}\) 优势消失 | Evidence | −0.5 overall |
| No quick change | 预测不显著、覆盖打平、最差组不跟、负 Spearman | Significance | 写作不可修 |

## 14. Questions For Authors

1. 在结论已承认三条翻译失败之后，2% 的 \(\Delta_{c\text{-}s}\) 对 MCS 部署决策的剩余不可替代价值是什么？
2. FedAU-Window 与官方 FedAU 差在哪？为何 sun2025 仍不对比？
3. Byrd 的过参数化机制如何适用于本稿的补全模型？
4. 评审期能否提供匿名代码，而不只是 camera-ready 承诺？

（Use 层的经验理由、covariate-shift 为何不是单次密度比：上一轮问题 3/4 已基本被正文回答，不再作为决策问题。）

## 15. Score Revision Criteria

```text
Raising the score would require: 新的操作/部署指标；代码可审。sequential IPW 补引只巩固 Novelty。
Lowering the score would be triggered by: 官方 FedAU 翻转 Δ_c-s；识别假设被指出在真实 MCS 不可用。
Concerns unlikely to change before submission: 覆盖打平、最差组不跟、U-Air 负 Spearman、对 FedAvg 预测不显著。
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: 1
Action: 在弱拒稳定的前提下做投稿决策——坚持 TMC 表述论文，或换更小 venue / 短文，或设计新操作指标。
Owner skill: 作者决策；实验则 ccf-experiment-designer
Input needed: 风险偏好
Expected output: go / no-go
Handoff required: yes
```

```text
Priority: 2
Action: 评审期匿名代码；FedAU 差异表；可选收窄 Byrd 句、摘要补 worst-group、Fig 星标。
Owner skill: ccf-submission-checker / ccf-paper-writer / ccf-figure
Input needed: 仓库、现有数字
Expected output: 局部修订
Handoff required: yes（若改稿）
```

```text
Checks run: desk、claim-evidence、实验审计、panel、写作评分、编译 log、相对 pass 2 的 delta、Shimodaira 兑现核验、sequential IPW 抽查。
Checks skipped: bib 逐条 PDF；官方 FedAU 代码等价；未重新跑实验。
Unresolved risks: Significance 在无新指标时弱拒稳定。
```
