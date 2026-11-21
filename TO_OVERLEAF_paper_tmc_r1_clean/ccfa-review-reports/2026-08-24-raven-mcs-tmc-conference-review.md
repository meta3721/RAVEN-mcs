# CCFA 论文评审报告 — RAVEN-MCS（写作门控后清洁稿，2026-08-24）

## 1. Report Metadata

```text
Review date: 2026-08-24
Target venue/year/track: IEEE Transactions on Mobile Computing (TMC), CCF-A, regular paper
Paper title: RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed: TO_OVERLEAF_paper_tmc_r1_clean/main.tex (当前写作稿), reference.bib, figure_data/ (含 W1/G3 CSV), make_figures.py 已写出 fig_w1 / fig_g3; 对照 2026-08-23 清洁稿评审（5/10）与 post_review 门控记录（只作证据边界，不作新数字）
Search basis: 沿用 2026-08-22 已核公开文献（Shimodaira 2000 JSPI; Robins et al. 1994 JASA; Byrd & Lipton 2019 ICML; FedAU Wang & Ji ICLR 2024）。本轮未把稿件私有句子贴进检索。TMC 页限：Computer Society 第三方摘录 12 页常规 / 可投至 18 页 MOPC / 附录须独立 supplemental；官方 TMC Author Information HTML 本轮 404，标 uncertain
Report file: ccfa-review-reports/2026-08-24-raven-mcs-tmc-conference-review.md
Reviewer mode: full（scientific + writing + format + revision-action）
Material delta vs 2026-08-23: 标题改为 windowed-asynchronous; 摘要写门控与 Design 反转; 最近邻表; A5+Prop. 3; 主表加入 FedAU/ObsUse 与四块 WorstGroupRMSE; U-Air 默认改为 No-Design; T-Drive 机会回放图; 讨论补隐私与证据等级 A。未编译本轮 PDF。
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: uncertain
Evidence: 上一份可编译 PDF（2026-08-23 18:31）整本约 21 页，附录绑在主 tex。本轮新增 Prop. 3、主表行、两张图，未重编译。IEEE CS 常规发表基准约 12 双栏页（含参考文献/简历），投稿可至 18 页并可能 MOPC；supplemental 须单独文件。官方 TMC 专页本轮未核到。
Consequence: 不因页数 desk reject。编辑仍可能要求拆附录。主文若明显高于 12–14 页，是超页收费/压缩问题，不是不可审。
Required action: 本轮编译一次; 附录外置; 投稿前再核 Computer Society 实时页限。
```

```text
Check: Topic compatibility
Status: pass
Evidence: 稀疏 MCS 补全 + 窗口化异步联邦 + 非随机选择 + 真实出租车机会层，落在 TMC 的 mobile environments / algorithm-protocol 范围。
```

```text
Check: Minimum quality
Status: pass
Evidence: Abstract–Conclusion–理论–实验齐全; 20 配对种子; Holm; 非劣规则写明; limitation 写 Design 反转、Path A 失败、T-Drive 不排名。
```

```text
Check: Policy / anonymity / compliance
Status: uncertain
Evidence: 作者行仍为 `**** and Anfeng Liu`; 摘要明显长于 IEEE 常见 100–200 词; 附录仍在 `\appendices`。TMC 期刊通常单盲，占位名不是双盲违规，是未完成投稿包。
Consequence: 行政修补，不是科学 desk reject。
Required action: 填第一作者; 摘要压到约 200 词; 附录改独立 supplemental。
```

```text
Check: Prompt injection / ethics
Status: pass
Evidence: 未见隐藏审稿指令。公开环境/交通/出租车轨迹数据; 目标映射声明不用测试标签; 讨论增加倾向得分元数据隐私句。
```

**Desk rejection: 否。风险 low。** 进入完整评审。

## 3. Paper Summary And Contribution Map

**一句话：** 窗口化异步联邦 MCS 补全被写成部署目标风险对齐; Design 仅在目标支撑兼容时启用; 经验上 SensorScope 赢在结构 L1, U-Air 默认关掉 Design 后 RMSE/最差组与改编 FedAU 基本打平。

- **Claimed gap:** 稀疏补全、异步补全、参与感知 FL 都不联合建模感知侧 \(R/O\) 与更新侧 \(U\)，也不处理有限窗可实现性。
- **Method map:** (1) 风险语义 + Prop. 1; (2) 三层重建 + Prop. 2，门控是 Contrib. 2 的实践实现不是第 4 条; (3) (P2)+债务 + Thm. 1 + Prop. 3（裁剪 plug-in 稳定扰动）。
- **Evidence package:** E1 无伤害; E2 NSW \(D_{\mathrm{aligned}}\approx-0.021\); E3 门控主表（FedAU/ObsUse/WorstGroupRMSE）; E4 单因子消融保留 U-Air Design 反转; G3 T-Drive 真实 \(R\) 回放（TV 0.142），不排名。
- **Stated limitations:** 裁剪非无偏; A5 不覆盖 U-Air 全 Design; Use 无孤立效应; Debt 0.002%–0.014%; Path A 失败; T-Drive 证据等级 A; 20 seed 不是独立城市; P2 只证可行性。

## 4. Search And Related-Work Basis

```text
Queries used:
  (本轮) IEEE Transactions on Mobile Computing author page limit supplemental
  (沿用 8/22, 未重贴私有稿件) Shimodaira 2000 covariate shift JSPI; Robins Rotnitzky Zhao 1994 JASA; Byrd Lipton 2019 importance weighting ICML; FedAU Wang Ji ICLR 2024
Sources searched: Web search + prior verified proceedings/journal pages; TMC Author Information HTML 本轮 404
Closest works found:
  Shimodaira 2000: 单次密度比 / 目标风险加权似然。本稿仍未引。
  Robins et al. 1994: 顺序缺失数据 IPW。本稿仍未引。
  FedAU 2024: 参与重加权以保住原 FL 目标。本稿已改编进主表，仍非官方复现。
  Byrd & Lipton 2019: 过参数化网络中 IW 效应可消失。仍未引; 与有限容量补全不完全同机制。
Unverified related-work risks:
  tian2026reshaping / qiao2025asmafl / chen2026dvafl 仍未进入本稿（上一轮 _paper_work 曾出现）。
  sun2025debiasing 已引，主表对照是 ObsUse（观察+可用校正）而非官方相关参与去偏实现。
Source-quality screening status: 未使用 MDPI。TMC 页限来自 CS 政策第三方摘录，不是本轮官方 HTML。
```

## 5. Expected Review Outcome

```text
Expected outcome: Borderline positive / 弱偏收讨论
Main accept signal: 问题切分仍清楚; 上一轮两条加分条件（FedAU 同迹比较、外部最差组）已经进主表; Design 反转不再藏; T-Drive 给出真实机会层; 窗口异步与 FedAsync 划界写进标题/III-A。
Main reject signal: 在 TMC 更在乎的 RMSE 与四块 WorstGroupRMSE 上，门控 RAVEN 与改编 FedAU/ObsUse 非劣而不是赢; U-Air 默认等于关掉 Design; SensorScope RMSE 仍与 FedAvg 打平; 未引 Shimodaira/Robins; 无评审期代码。
Confidence: 4/5
```

相对 2026-08-23 清洁稿 **5.0 → 6.0**。那一轮写明“FedAU 比较或不可消去下游指标之一为正向才可能到 6”。两条都做了（改编 FedAU + 四块 WG），所以 overall 上到 6，不到 7：外部端点是非劣不是优势。

## 6. Strengths And Weaknesses

**Strengths**
- 到达律 ≠ 部署目标律仍是合法 TMC 问题; E2 的 \(D_{\mathrm{aligned}}\) 跨方法稳定为负。
- 门控默认与 U-Air Design 反转写进摘要/主表/讨论，不再把完整 Design 假装成 U-Air 默认。
- 主表加入改编 FedAU/ObsUse 与四块 WorstGroupRMSE; 非劣规则 (+0.5%) 与 “不是 Holm 赢 FedAU” 写明。
- T-Drive 把机会层从纯协议变量改成真实轨迹 \(R\)（证据等级 A），并写清 O/U 仍受控、不排名。
- Prop. 3 / A5 把“裁剪 plug-in 不是无偏”收成稳定界，并明确该界不解释 U-Air 反转。
- Use 无效应、Debt 极小、Local-Hájek 退化、Path A 失败都公开。

**Weaknesses**

```text
Weakness: 对改编 FedAU/ObsUse，外部端点是非劣，独特赢面仍是作者定义的 Δ_group / Δ_c-s。
Evidence basis: Table II。U-Air RMSE 门控 1.1131 vs FedAU 1.1128 vs ObsUse 1.1120; WorstGroupRMSE 1.1703 vs 1.1701 vs 1.1692。SensorScope 三方法 WG 几乎互换。SensorScope Δ_group 门控 1.0139 vs FedAU 1.0719。
Reviewer deduction: TMC 读者会问为什么不直接用参与重加权。分层 R/O/U 的增量没有落在部署 RMSE/最差组上。
Required fix: 证明改编/官方 FedAU 复制不了结构收益且该收益有外部后果; 或把贡献收成“结构对齐表述 + 支撑门控”，接受预测打平。
```

```text
Weakness: U-Air 论文默认 = 去掉 Design。审稿人可把主结果读成消融胜出，而不是 RAVEN 栈胜出。
Evidence basis: 摘要; Table II 门控行 = raven_wo_design; Table III Design −6.943% Δ_group / −6.553% RMSE; Fig. 3–4 的 U-Air RAVEN 仍是完整 Design。
Reviewer deduction: 诚实，但贡献叙事脆弱。完整栈在 U-Air 上伤害主端点; 门控像看到反转之后的赋值。
Required fix: 正文用一行写清门控在 TEST 打开前由支撑诊断预声明; 主文不要再让 Fig. 3–4 的 “RAVEN” 与默认行竞争。
```

```text
Weakness: 方法增量仍是顺序 IPW + 小 QP + 虚拟队列 + 数据集门。
Evidence basis: Prop. 1 不同概率律; Thm. 1 λ_β 强凸; Prop. 3 Lipschitz 扰动; §II 最近邻表无 Shimodaira/Robins 引用。
Reviewer deduction: MCS 对象组合有价值，单项定理浅。表能减 FedAU “只引不比”，减不了 covariate-shift 划界缺口。
Required fix: 引 Shimodaira 2000 与 Robins et al. 1994，把差异写成三层信息集 + 有限窗校准; Prop. 1 不宜当独立发现。
```

```text
Weakness: TMC 系统味道仍偏协议。T-Drive 不训练、不排名; O/U 仍 Complete-aligned; 无时延/能耗/通信。
Evidence basis: §VII T-Drive 段; G3 声明证据等级 A; Use 层 E4 全不显著。
Reviewer deduction: 真实 R 修好了上一轮 “完全没有轨迹” 的洞，但还不是端到端移动系统文。
Required fix: 接受证据边界，或补 T-Drive 方法 canary / 受控 U 日志之一。不要把回放写成系统部署。
```

```text
Weakness: 标题级 Use/Debt 经验必要性仍弱。
Evidence basis: Table III Use 全不显著; Debt 0.002%–0.014% ≪ 0.5% MPID。
Required fix: 强 censoring 场景，或继续把 Debt 留在 Contrib. 3 内部（本稿已降级，保留即可）。
```

### Writing / format scorecard

| Dimension | Weight | Score | Confidence | Evidence basis | Concrete repair |
| ---: | ---: | ---: | ---: | --- | --- |
| Storyline and motivation | 12 | 4 | 4 | 三问 + 窗口异步 vs FedAsync | 贡献段后用一句钉死“外部端点是非劣不是赢” |
| Contribution display | 12 | 4 | 4 | 三条贡献; 门控不另开第 4 条 | 保留。不要把 Prop. 3 再写成贡献 |
| Paragraph logic | 10 | 4 | 4 | RQ2 先报门控表 | 压缩重复的 claim-ceiling 句 |
| Claim-evidence alignment | 14 | 4 | 4 | 摘要写 7% 反转与 NI | 摘要仍偏长; 压到 200 词内只留 1 个效果句 |
| Method readability | 10 | 3 | 4 | 分层清楚; 无 Algorithm | 加 Algorithm 1：重建+(P2)+债务+门控 |
| Experiment narration | 10 | 3 | 4 | 主表清楚; Fig. 3–4 U-Air 仍是全 Design | 主文去掉或改标这两图，避免双默认 |
| Related-work positioning | 8 | 3 | 4 | 最近邻表有; 无密度比/顺序 IPW 文献 | 加 Shimodaira/Robins 对照轴 |
| Terminology consistency | 8 | 3 | 4 | raven / gated / full Design 三名 | 全文只保留 “RAVEN (gated)” 与 “full Design (diagnostic)” |
| LaTeX and format | 8 | 3 | 3 | 本轮未编译; 作者 ****; 附录在主文件 | 编译; 附录外置; 摘要词数 |
| Reviewer-facing risk | 8 | 3 | 4 | 门控像事后开关; FedAU 打平 | 预声明时间线 + 外部端点措辞降级 |

**Writing score:** \(3.56/5\)（中等风险）。比 8/23 的 claim-evidence 更好，因为反转不再藏; 术语和双图默认把实验叙述分拉低。

**Format verdict:** 可审，本轮 **not compiled**。Blocking 无。行政: 作者占位、摘要过长、附录未拆。Figure/table: 新 W1/G3 文件名与 `\includegraphics` 一致; Fig. 3–4 标题与门控默认冲突。Citation: 缺 Shimodaira/Robins/Byrd。Notation: A5/\(C_1\) 与实现裁剪符号一致。Suggested check: 在 `TO_OVERLEAF_paper_tmc_r1_clean/` 跑 pdflatex+bibtex 全编译。

## 7. Potentially Missing Related Work

```text
Work: Shimodaira, H. (2000). Improving predictive inference under covariate shift by weighting the log-likelihood function. JSPI 90:227–244.
Status: searched
Why relevant: 目标风险 ≠ 训练分布时的经典加权。
Overlap: 目标加权; 不是三层 R/O/U，也没有有限窗可行集。
Needed comparison: §II 写清“单次密度比 vs 顺序信息集 + P2”。
```

```text
Work: Robins, J. M., Rotnitzky, A., & Zhao, L. P. (1994). Estimation of regression coefficients when some regressors are not always observed. JASA 89:846–866.
Status: searched
Why relevant: 顺序缺失数据 IPW 的标准来源。
Overlap: 顺序逆概率; 不是 MCS 机会/观测/可用更新，也不是部署目标校准。
Needed comparison: 把 Prop. 2 放进该传统，强调信息边界与有限窗。
```

```text
Work: Byrd, J., & Lipton, Z. C. (2019). What is the effect of importance weighting in deep learning? ICML, PMLR 97:872–881.
Status: searched
Why relevant: 可解释结构对齐不必降低 RMSE。机制针对过参数化网络，与本稿补全模型不完全相同。
Needed comparison: 限定模型类后一句即可，不要写成同一定理。
```

```text
Work: Wang, S., & Ji, M. (2024). FedAU. ICLR.
Status: searched; 现已进入主表
Why relevant: 最近邻参与重加权。
Overlap: 改到达质量; 不修感知侧暴露。
Needed comparison: 已做窗口改编。仍缺官方实现。主文必须保持 “adapted, not official”。
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| 到达风险 ≠ 目标风险 | Abstract, Prop. 1, RQ1 | \(D_{\mathrm{aligned}}\approx-0.021\), 17–18/20 负; T-Drive TV 0.142 | adequate | 问题成立; Prop. 1 仍浅 | 降为 remark |
| 理想顺序校正恢复目标律 | Prop. 2 | A1–A3 | conditional | 不覆盖估计/裁剪/换 \(A_r\) | 保持条件句 |
| 裁剪 plug-in 是稳定扰动 | Prop. 3, A5 | Lipschitz +\(C_1\); 明确不解释 U-Air | adequate for stability | 不是无偏, 不是第 4 贡献 | 不要引用 \(C_1\) 当 RMSE 保证 |
| P2 唯一解 | Thm. 1 | \(\lambda_\beta\) 强凸 | strong but modest | 新意有限 | 保持 |
| SensorScope 结构更好 | Table II | \(\Delta_{\mathrm{group}}\) 1.0139 vs FedAvg 1.0558 (3.96%) | strong for L1 | RMSE 打平; WG 与 FedAU 互换 | 不要说全面更好 |
| U-Air 门控主端点更好 | Table II, Fig. W1 | vs 全 Design \(\Delta_{\mathrm{group}}\)/RMSE 约 −7%; vs FedAvg RMSE 1.113 vs 1.188 | adequate if default=No-Design | 这是关 Design 的收益 | 诊断行必须留下 |
| 对 FedAU/ObsUse 非劣 | Table II, 正文 TEST +0.48%/+0.44% | 预注册 +0.5% 规则; Holm 不显著 | adequate for NI | 不是赢 | 禁止 “best worst-group” |
| Design 仅在兼容支撑使用 | Abstract, RQ3, Discussion | G1 25.5% 零目标; oracle≈estimated | adequate for mechanism | 像数据集开关 | 写预声明时间线 |
| Use/Debt 必要 | Contrib. 2–3 内部 | Use 无效应; Debt 极小 | weak as necessity | 本稿已降级 | 保持降级 |
| 适合真实移动 MCS | 标题/G3 | 真实 \(R\), 受控 \(O/U\), 不排名 | adequate for replay | 不是系统文 | 保持证据等级 A |

## 9. Experiment / Benchmark / Reproducibility Audit

- **Baselines: 3/5。** 上一轮 2/5。FedAU/ObsUse 进主表，但是窗口改编; Local-Hájek 仍退化; FedCure 明确没跑; TimeAlign 仍非官方（已移附录）。
- **Ablations: 4/5 透明度。** Design 反转、Use/Debt 弱、Path A 失败都公开。门控来自支撑诊断，不是新估计器。
- **Datasets: 3/5 for TMC mobility。** 上一轮 2/5。T-Drive 真实 \(R\) 修好“零轨迹”; O/U 仍协议; 无方法排名。
- **Metrics: 4/5。** 结构 + RMSE\(_\mu\) + 四块 WorstGroupRMSE。仍无通信/时延/能耗/任务效用。
- **Statistics: 4/5。** 配对 Wilcoxon+Holm; 预注册 NI; 0.5% MPID。20 seed 是 EventTrace 随机性，正文已写。
- **Robustness: 3/5。** oracle vs estimated Design; Prop. 3; CLARABEL–SCS 尾差 0.0056。无独立城市、无官方 FedAU、无 T-Drive 训练。
- **Reproducibility: 3/5。** 公开数据与协议细节足够复述; 仍无评审期代码; 本轮 PDF 未编译; P2 只证可行性。

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-justified
Expertise: MCS completion / target shift
Likely score: 7/10
Confidence: 4
Main positive signal: 问题真实; 反转不藏; FedAU 和 WG 都进主表; T-Drive 有真实 R。
Main negative signal: 外部端点只是非劣。
Evidence basis: Abstract; Table II; Fig. W1; Fig. G3。
Score-change condition: 若结构收益能翻译成 FedAU 复制不了的任务效用，可到 8。
```

```text
Reviewer: Critical
Expertise: incremental FL + IPW skepticism
Likely score: 5/10
Confidence: 4
Main positive signal: 负结果公开。
Main negative signal: U-Air 赢在关 Design; 对 FedAU RMSE/WG 打平; 机制仍是 IPW+QP。
Evidence basis: Table II 门控=wo_design; Table III; 未引 Shimodaira。
Fatal concern if any: 无。不是错误，是增量不够。
Score-change condition: 官方 FedAU 若结构与 RMSE 双赢，降到 4。
```

```text
Reviewer: Method / soundness
Expertise: causal identification / convex programs
Likely score: 6/10
Confidence: 4
Main positive signal: 信息边界清楚; A5+Prop. 3 范围诚实。
Main negative signal: 识别要正确律; 门控改变 \(A_r\) 时界失效，而 U-Air 正是该情形。
Evidence basis: A1–A5; Prop. 3 声明; G1 51.6% \(A_r\) overlap。
Score-change condition: 把门控写成支撑诊断的预声明规则，而不是数据集名开关。
```

```text
Reviewer: Evidence / experiment
Expertise: FL empirical practice
Likely score: 6/10
Confidence: 4
Main positive signal: 对照集补上了上一轮缺的参与基线与外部端点。
Main negative signal: 改编而非官方; SensorScope RMSE 无增益; T-Drive 不排名。
Evidence basis: Table II; §VII setup “not official reproductions”。
Score-change condition: 官方 FedAU 同协议，或 T-Drive canary。
```

```text
Reviewer: Novelty / positioning
Expertise: covariate shift / participation bias
Likely score: 5/10
Confidence: 4
Main positive signal: 最近邻表把目标对象、R/O/U、有限窗校准分开。
Main negative signal: 仍不引 Shimodaira/Robins; 表不能代替文献。
Evidence basis: Table nearest_neighbor; bib 检索无上述键。
Score-change condition: 划界段 + 引用 → Originality 3→4，overall 不一定动。
```

```text
Reviewer: Writing / clarity
Expertise: journal readability
Likely score: 6/10
Confidence: 4
Main positive signal: 窗口异步写进标题; 摘要与门控一致。
Main negative signal: Fig. 3–4 与主表两个 U-Air RAVEN; 摘要过长; 无算法。
Evidence basis: fig:e3_structural 说明; Abstract; 无 algorithm 环境。
Score-change condition: 统一默认命名 + 算法 + 压缩摘要。
```

```text
Reviewer: Ethics / reproducibility
Expertise: artifacts / disclosure
Likely score: 5/10
Confidence: 4
Main positive signal: 反转、Path A、隐私、seed 范围、P2 可行性边界都写了。
Main negative signal: 无代码句; 作者占位。
Evidence basis: Discussion; author line; 无 github/availability。
Score-change condition: 评审期仓库 → Reproducibility 3→4。
```

```text
Reviewer: Domain application (TMC/MCS)
Expertise: mobility systems
Likely score: 5/10
Confidence: 4
Main positive signal: 真实出租车机会层; 间歇性 vs 协议 always-on 对照清楚。
Main negative signal: 不是端到端; 固定站网仍是主训练场; 无能耗/时延。
Evidence basis: T-Drive 段; Table I 角色 “replay, not ranking”。
Score-change condition: 方法级真实移动实验，而不是更多协议图。
```

```text
Reviewer: Novice advocate
Expertise: first-pass recoverability
Likely score: 5/10
Confidence: 3
Main positive signal: 框架图仍在; RQ 对齐理论链。
Main negative signal: 符号密; 默认方法随数据集变。
Evidence basis: §III–VI 密度; Table II 两行 RAVEN。
Score-change condition: Algorithm 1 与一张默认规则盒。
```

```text
Agreement: 可审; 问题成立; 上一轮 “FedAU 只引不比 / 无 WG / 无轨迹 / 藏反转” 已修。
Disagreement: 5 vs 7。分歧在“关 Design 的 U-Air 增益算不算方法贡献”，以及“对 FedAU 非劣够不够 TMC”。
Decisive positive axis: 评价包补全 + 负结果诚实。
Decisive negative axis: 外部端点无独特优势; 默认像支撑开关。
Unresolved evidence: 官方 FedAU; 本轮 PDF 页数; 评审期代码。
AC stance: Borderline positive (6/10)。不平均成 7，因为最强未解关切仍是独特性。也不回到 5，因为 8/23 自己写的上分条件已经发生。
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | major | 对 FedAU/ObsUse，RMSE 与四块 WG 是非劣不是赢 | Table II U-Air 1.1131 vs 1.1128 vs 1.1120 | Significance, Evidence | experiment / claim-qualification | 主文把独特赢面限制在 \(\Delta_{\mathrm{group}}\); 或补 FedAU 复制不了的任务效用 | ccf-paper-writer / ccf-experiment-designer | 外部独特赢 → Sig 3→4, overall 6→7; 若官方 FedAU 双赢 → overall 6→5 或 4 |
| M2 | major | U-Air 默认=关 Design，像消融当方法 | Table II 门控行; Table III; Fig. 3–4 | Soundness, Clarity | writing / method | 写预声明时间线; 主文消除双 RAVEN 图 | ccf-paper-writer | 时间线+图一致 → Clarity 3→4, 不自动 +1 overall |
| M3 | major | 未引 Shimodaira/Robins | §II; bib | Originality | related-work | 引用并写三层信息集 + 有限窗差异 | ccf-paper-writer | Originality 3→4; overall 0 to +0.5 |
| M4 | moderate | T-Drive 不排名; O/U 仍协议 | §VII G3 段 | Significance | experiment / accepted-limitation | 保持证据等级 A，或另开 canary | ccf-experiment-designer | 方法级移动结果 → Sig +0.5 |
| M5 | moderate | 无评审期代码; 本轮未编译 | Discussion; main.log 停在 8/23 | Reproducibility | reproducibility | 仓库 + pdflatex | ccf-paper-writer | Repro 3→4 |
| M6 | moderate | Use/Debt 经验弱 | Table III | Significance | accepted-limitation | 保持降级 | none | 不修 overall |
| m1 | minor | 摘要过长; 作者 `****` | Abstract; title page | Clarity | writing / format | 压到 ~200 词; 填作者 | ccf-paper-writer | 行政 |
| m2 | minor | 无 Algorithm 1 | 全文无 algorithm 环境 | Clarity | writing | 伪代码覆盖重建+P2+门控 | ccf-paper-writer | Clarity 局部 |
| m3 | minor | 附录仍在主 PDF | `\appendices` | Format | compression | 独立 supplemental | ccf-paper-writer | 页限风险下降 |

## 12. AC / Meta-Review

审稿人同意这是可审的 TMC 稿，不再是“对照集缺最近邻 / 主端点反转被措辞盖住”的弱拒。分歧在 5 和 7：同情者看到评价包按上一轮条件补齐; 苛刻者看到 U-Air 的预测收益来自闭 Design，且改编 FedAU 已经吃掉 RMSE/WG。

决定性接受轴是诚实与补全：窗口异步语义、门控、FedAU 表、四块 WG、T-Drive \(R\)、Prop. 3 范围。决定性拒绝轴是独特性：在 TMC 读者会带回家的误差数字上，门控 RAVEN 没有稳定地赢过改编参与/观测基线。

AC 给 **6 / borderline-positive**。讨论里会有人要 major revision（官方 FedAU、命名、文献划界），不是直接弱收。写作不能把 6 抬到 7。

讨论风险: 有人把门控读成 p-hacking。正文必须把 VAL 支撑规则和一次 TEST 打开写清楚。有人会要系统指标; 那是新实验，不是改句子。

## 13. Quantitative Scores

```text
Quality: 3
Clarity: 4
Significance: 3
Originality: 3
Soundness: 4
Evidence: 4
Reproducibility: 3
Ethics / Limitations: 5
Overall: 6
Confidence: 4
Score-change conditions: 见 §15。3 分项均附扣除与修复。
```

## Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 3 | 4 | §II 最近邻表; bib 无 Shimodaira/Robins; 机制=顺序 IPW+QP+门控 | MCS 对象切分真实。划界可到 4，难靠引用到弱收 |
| Soundness | 4 | 4 | A1–A5; Prop. 2–3; Thm. 1; 门控改变 \(A_r\) 时 A5 失效且已承认 | 不是错。预声明门控时间线可消除“事后开关”观感 |
| Evidence | 4 | 4 | Table II FedAU/WG; Fig. W1; T-Drive; E4 反转公开 | 改编非官方; SS RMSE 打平。官方 FedAU 或任务效用可到 5 |
| Significance | 3 | 4 | SS 结构 3.96% L1, RMSE 平; UA 外部端点≈FedAU; T-Drive 不排名 | 有用但窄。外部独特赢 → 4 |
| Clarity | 4 | 4 | 标题/摘要/门表一致; Fig. 3–4 双默认; 无算法 | 图与命名修好可到 4 稳或 5 |
| Reproducibility | 3 | 4 | 协议可复述; 无代码; 本轮未编译 | 仓库+编译 → 4 |
| Ethics / Limitations | 5 | 4 | 反转、Path A、隐私、seed、P2 可行性、证据等级 A | 保持。藏门控理由才会降 |

**Overall:** 6  | **Scholarly Confidence:** 4

**Recommendation:** borderline-positive（弱偏收讨论，不是弱收）
**Verdict:** 官方或更强参与基线若在结构与 RMSE 上同时更好，降 1 分。外部端点上对 FedAU 的独特优势，才可能 +1 到 7。

```text
Dimension: Significance
Score: 3
Confidence: 4
Evidence basis: Table II; T-Drive 不排名
Deduction: 部署者在 RMSE/WG 上看不到稳定替换 FedAU 的理由。
Repair condition: 预声明的外部任务/覆盖/最差组优势，且 FedAU 复制不了。
Expected score movement: Sig 3→4, overall 6→7
```

```text
Dimension: Originality
Score: 3
Confidence: 4
Evidence basis: §II; Prop. 1–3
Deduction: 组合对象新，元件旧，缺密度比/顺序 IPW 篱笆。
Repair condition: Shimodaira + Robins 对照段。
Expected score movement: Originality 3→4; overall 0 to +0.5
```

```text
Dimension: Reproducibility
Score: 3
Confidence: 4
Evidence basis: 无 availability; main.log 8/23
Deduction: 不能在不找作者的情况下审计实现。
Repair condition: 评审期代码 + 本轮编译日志。
Expected score movement: Repro 3→4; overall 不动或 +0.5
```

## 14. Questions For Authors

1. 在 RMSE 与四块 WorstGroupRMSE 上与改编 FedAU 非劣之后，还需要 RAVEN 的操作理由是什么？请指出 FedAU 复制不了的那一列。
2. U-Air 关 Design 的赋值，是支撑诊断预注册之后一次打开 TEST，还是看到 Table III 反转后的事后默认？
3. 是否准备在同迹上跑官方 FedAU（或作者发布实现），而不是仅窗口改编？
4. T-Drive 为什么停在机会回放、不做方法 canary？
5. 评审期是否提供代码与 P2 求解器脚本？

## 15. Score Revision Criteria

```text
Raising the score would require:
  外部端点上对 FedAU 的独特、预声明优势（Sig 3→4, overall 6→7）;
  或官方 FedAU 比较支持分层独特作用且不伤 RMSE。
  仅 Shimodaira/算法/代码: 维度 +1, overall 至多 +0.5, 仍是 6。
Lowering the score would be triggered by:
  官方参与重加权在结构与 RMSE 上同时更好（overall 6→5/4）;
  或门控被读成未预声明的 TEST 调参;
  或 Fig. 3–4 继续把完整 Design 标成 U-Air RAVEN 且正文不改。
Concerns unlikely to change before submission:
  Prop. 1 浅; Use/Debt 经验弱; T-Drive 若继续不训练则系统味道有限。
```

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | 外部端点独特赢，FedAU 复制不了 | Significance, Evidence | +1 overall (6→7) |
| Raise score | Shimodaira/Robins + Algorithm 1 + 代码 | Originality, Clarity, Repro | 维度 +1; overall 0 to +0.5 |
| Lower score | 官方 FedAU 结构+RMSE 双赢 | Evidence, Novelty | −1 overall |
| No quick change | 合成 O/U; Use 无效应; 定理元件浅 | Significance, Originality | 投稿前难动 |

## 16. Action Plan And CCFA Handoffs

```text
Priority: P1
Action: 统一默认命名; 主文处理 Fig. 3–4（改标或下附录）; 用一段写门控预声明时间线; 摘要压到约 200 词并保持反转与 NI。
Owner skill: ccf-paper-writer
Input needed: 当前 main.tex; Table II; Fig. W1
Expected output: 无双默认的修订稿
Handoff required: yes（需用户点名写作）
```

```text
Priority: P1
Action: §II 加入 Shimodaira 2000 与 Robins et al. 1994，差异写成顺序三层信息集 + 可行集校准。
Owner skill: ccf-paper-writer
Input needed: 已核出处
Expected output: Related Work 划界段
Handoff required: yes
```

```text
Priority: P2
Action: 决定是否跑官方 FedAU 或 T-Drive canary。不跑则把 M1/M4 写成接受的限度，不要加未经实验的系统句。
Owner skill: ccf-experiment-designer
Input needed: 用户是否授权新实验
Expected output: 协议或明确不跑
Handoff required: yes（新实验改变研究阶段）
```

```text
Priority: P3
Action: 本轮 pdflatex+bibtex; 附录改 supplemental; 填作者; Algorithm 1; 评审期代码句。
Owner skill: ccf-paper-writer
Input needed: 作者信息、代码许可证
Expected output: 可投包装
Handoff required: yes
```

```text
Checks run: desk; contribution; evidence; adversarial; claim-evidence table; experiment audit; 12-role panel; writing scorecard; LaTeX source inspect; 公开文献沿用 + TMC 页限检索
Checks skipped: 本轮 PDF 全编译; 官方 TMC Author Information HTML（404）; 未重跑外部实验
Unresolved risks: 页数; 官方 FedAU; 门控是否被读成事后开关
```

**Recommended next CCFA owner:** `ccf-paper-writer`（命名/文献/摘要/算法）。不要把本评审交给 `ccf-rebuttal-writer`。新实验需用户明确授权后再给 `ccf-experiment-designer`。

**Output self-check:** 16 段顺序完整; 表列对齐; overall 6 与 M1 未解独特性一致; 未承诺接收概率; 未编造官方 FedAU 数字; 3 分项均有扣除与修复条件。
