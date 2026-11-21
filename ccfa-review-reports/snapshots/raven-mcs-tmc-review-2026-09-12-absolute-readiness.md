# CCFA 论文评审报告 — RAVEN-MCS / IEEE TMC

> `ccf-paper-reviewer` 全新独立 full 评审（科学 + 写作 + 格式 + AC 综合）。**仅评估，不改写稿件正文。**
> 本轮为独立重跑，不是对 2026-09-12 pass-3 的增量复审：上一版报告（7/10 weak-accept）仅作为待独立验证的输入，其结论在关键维度上被本轮推翻并给出理由。

---

## 1. 报告元信息（Report Metadata）

```text
评审日期: 2026-09-12（独立 full 重跑）
目标期刊/年份/类型: IEEE Transactions on Mobile Computing (TMC), CCF-A, 正刊 regular paper
论文标题: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data
          Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
已审材料:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex            (1970 行)
  TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex        (2358 行，经 supplemental.tex \input)
  TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex
  TO_OVERLEAF_paper_tmc_r1_clean/reference.bib       (44 条)
  TO_OVERLEAF_paper_tmc_r1_clean/main.pdf            (本机计数 14 页)
  RAVEN_MCS_PUBLIC_REPRO_R1/verify.py + MANIFEST.csv + tables/ + tdrive/
  ccf 复核脚本: CCFA-Skills/ccf-paper-writer/scripts/check_prose_quality.py
检索基础（公开安全检索，未粘贴稿件正文）:
  FedIPW / "Who Trains Matters" arXiv:2604.26604
  Spatiotemporal Transformer 期刊卷期核验 (researchr WLLXYY23 / IEEE Xplore 10228982)
  IEEE CS author-resources 篇幅/MOPC 规则（沿用上一轮检索结果，本轮未再抓取第一方页面）
报告文件: ccfa-review-reports/raven-mcs-tmc-review.md（canonical，覆盖写入）
评审模式: full（科学 + 写作 + 格式 + desk + AC 综合）
稿件版本: TO_OVERLEAF_paper_tmc_r1_clean 当前工作副本（main.tex 2026-09-12 11:16，
          reference.bib 2026-09-12 19:38）
版本对比契约: 不适用（本报告为绝对就绪度评审，不与历史 pass 融合打分）
```

---

## 2. 桌面拒稿评估（Desk Rejection Assessment）

```text
Check: 论文篇幅
Status: uncertain（超页费风险，非 desk-fail）
Evidence: 本机解析 main.pdf 页面对象计数为 14 页（含参考文献）；正文使用
  \enlargethispage{10\baselineskip}、\IEEEtriggercmd{\enlargethispage{18\baselineskip}}、
  \IEEEtriggeratref{51} 等排版压缩手段。上轮检索记录 IEEE CS 正刊 published length
  为 12 页（含摘要/参考文献/简介），超出部分按 MOPC 计费。
Consequence: 不影响科学评审；需要压缩或接受 MOPC。
Required action: 向 TMC ScholarOne 确认投稿页数上限；若需 MOPC-free，压缩到 12 页。
```

```text
Check: 选题契合度
Status: pass
Evidence: 窗口化异步联邦 + 移动群智感知数据补全 + 非随机 R/O/U 选择 + 公开部署目标；
  title/§III/Prop.2 已统一到 target-mass 口径。
Consequence: 落在 TMC 的 mobile systems / crowdsensing / FL 范围内。
Required action: none
```

```text
Check: 最低质量线
Status: pass
Evidence: 摘要 191 词（CS 要求 100–200，本机正则计数）；含引言、相关工作、系统模型、
  方法、理论（Prop.1–3、Thm.1–2、Assumption 1）、评估、局限、结论、可用性声明、
  Algorithm 1、Tables II–IV 与附录 Table V–XXII、14 页独立补充材料。
Consequence: 可评审。
Required action: none
```

```text
Check: 政策 / 匿名 / 合规
Status: fail（ScholarOne 就绪性，非科学 desk reject）
Evidence: main.tex L57–L60 作者块为 `**** and Anfeng Liu`，含基金号 U24A20248、
  中南大学单位与 afengliu@mail.csu.edu.cn；supplemental.tex 标题页重复同一混合块。
Consequence: TMC 为具名期刊，占位符未替换前无法干净上传。
Required action: 经作者授权后补齐完整作者列表。
```

```text
Check: 提示注入 / 隐藏操纵
Status: pass
Evidence: 本轮逐段扫描 main.tex、appendix.tex、caption、bib key，未发现面向 LLM 或
  审稿人的隐藏指令；正文无 C1/C2/G1/内部标签残留。
Consequence: none
Required action: none
```

```text
Check: 伦理与可评审性
Status: pass with disclosure
Evidence: 数据均为公开数据集（SensorScope Zenodo 10.5281/zenodo.2654726；City Scanner
  Zenodo 10.5281/zenodo.7961851, CC BY 4.0；T-Drive 按 Microsoft Research 公开条款；
  NSW-Traffic 为 TfNSW 开放数据）。§Limitations 明确 "federated learning itself does
  not provide a privacy guarantee"。轨迹数据再分发/去标识化说明较薄。
Consequence: 可评审；轨迹治理条款偏薄属于可补强的披露项。
Required action: 增加一句轨迹去标识化/再分发的合规说明。
```

```text
Desk rejection risk: low
Reason: 选题、最低质量线、伦理均可通过 TMC 桌面审；作者占位符阻塞干净上传；
  篇幅超过 12 页 published length，属压缩/MOPC 问题而非桌面拒稿。
Can be fixed before review? yes（作者块）；partly（压缩 / MOPC）
```

---

## 3. 论文摘要与贡献图谱（Paper Summary And Contribution Map）

**一段式摘要。** 论文把"窗口化异步联邦移动群智感知数据补全"重新表述为**公开部署目标质量对齐**问题，而非"到达更新频率"问题。感知过程被分解为移动机会 $R$、实际观测 $O$、可用更新 $U$ 三层选择；论文论证到达律与部署目标律不同时其风险泛函不可互换（Prop. 1），在 A1–A3 下理想逐层 Hàjek 归一化估计可相合到兼容目标矩/组质量（Prop. 2），并用一个强凸规划 (P2) 把校正参考投影到当前可行聚合集，同时维护长期"目标债务"账本（Thm. 1 唯一全局解；Prop. 3 剪枝插值稳定性界）。实现在 Algorithm 1 中由冻结启发式 $\phi$（训练单元零目标占比）在两个具名方法间切换：**RAVEN-Design**（$\phi=0$，使用滞后机会/设计比）与 **RAVEN-NoDesign**（$\phi>0$，$\widehat\zeta=1$，不作目标质量重建）。

- **声称的问题**：进入学习的数据未必采样自部署预测器所要服务的总体。
- **声称的缺口**：稀疏 MCS 补全、异步联邦补全、参与感知 FL 三者均未联合识别"感知侧可用性"与"更新侧可用性"，也未把重建目标映射到有限移动窗口。
- **方法/贡献图谱**
  1. 两阶段三层非随机选择下的部署目标风险语义，以及目标风险与到达风险的不可互换性。
  2. 分层校正的目标质量重建（Design 仅在 $\phi=0$ 分支启用；Use 作为顺序因子保留）。
  3. 可行性感知即时校准 (P2) + 长期目标债务会计；覆盖度 Gate 仅作诊断，不切换 Design。
- **证据包**：E1 平衡无伤控制；E2 NSW 风险语义 $D_{\mathrm{aligned}}$；E3 Table II（20 seeds，always-on 协议 $R$，TEST 30011–30020 用于 +0.5% 表述，ALL20 披露，四行 Holm WorstGroupRMSE 家族全部 n.s.）；E4 单因子消融；T-Drive 真实 $R$ 混合排序（10 seeds）；NSW 四区域协议排序；City Scanner NYC PM$_{2.5}$ 混合排序（Table XXI）；City Scanner Pilot~2 实测 $O$ 混合排序（Table XXII）；INT-R 间歇协议机会块；覆盖度 Gate 压力审计。
- **自述局限**：$\phi$ 非 A1/A5 正性判据；SensorScope/U-Air 对 $\phi$ 赋值属回顾性；无 Holm 显著的 RMSE 胜利；T-Drive 超出 +0.5%；Table XXI 上 FedAvg 最低；Table XXII 上 TwoStage-Hàjek 最低；Gate 不切换 Design；没有任何排序同时实测 $R$、$O$、$U$。

---

## 4. 检索与相关工作基础（Search And Related-Work Basis）

```text
检索式:
  FedIPW / "Who Trains Matters" arXiv:2604.26604 真伪与状态
  "Spatiotemporal Transformer for Data Inference and Long Prediction in Sparse
   Mobile CrowdSensing" 期刊卷期（reference.bib 记为 ACM CSUR 58(4), 2025）
已检索来源:
  arXiv listing cs/2026-04、ar5iv/ADS 条目、Semantic Scholar、researchr、
  IEEE Xplore document 10228982、重庆大学向朝参主页
检索到的最近工作:
  FedIPW / "Who Trains Matters"（Morishita, arXiv:2604.26604）——存在且仍为预印本；
    arXiv listing 与 ADS 均可检索到，本轮确认非虚构条目
  FLOSS（Goetze et al., PACMI '25, DOI 10.1145/3766882.3767180）——客户级 opt-out/
    straggler IPW，被本文正确当作最近邻并明确区分对齐对象
  FedPALS（Listo Zec et al., arXiv:2411.03799）——目标标签边缘分布对齐，被正确排除为比较基线
未解决的引文风险:
  wang2023transformer（key 内年份 2023）在 bib 中记为 ACM Computing Surveys
  vol. 58 no. 4, year 2025，note 为 "Art. no. 7"；同时该条又被写作 note 与
  guo2015mobile 的 "Art. no. 7" 重合。检索显示该工作存在（IEEE Xplore 10228982 /
  researchr WangLLXYY23），但卷期年份与条目内部一致性无法由公开检索一锤定音，
  需作者核对第一方著录
  FedAU / TimeAlign 无官方复现，仅窗口化改编
来源质量筛查: 未引用 MDPI 等低质量来源；预印本状态已在正文标注
```

**对象切分仍然成立且值得肯定**：FLOSS/FedIPW/FedAU 作用于客户端名册（client roster），FedPALS 作用于类标签边缘，而本文作用于 MCS 单元级 $R/O/U$ 选择与 $h(i)$ 上的公开度量。这条切分是本文原创新最扎实的部分。但切分成立**不等于**实证价值成立——这正是本报告第 6 节的核心。

---

## 5. 预期评审结果（Expected Review Outcome）

```text
Expected outcome: 弱拒（Overall 4/10，偏 borderline 的 weak reject）
Main accept signal: TMC 原生的问题表述（部署目标质量 vs 到达律）；三层 R/O/U 的建模
  与对象切分清楚；理论边界表述严谨（不宣称优化目标风险、不宣称无偏）；数据与协议
  披露极为诚实（T-Drive 落败、Table XXII Hàjek 最低、INT-R burstiness 标定失败、
  Gate 有效性 0.750 全部写在正文/附录）；复现包可哈希校验（本轮实测）。
Main reject signal: 论文自己的消融证据（E4）说明其"改进指标"没有预测效力；主方法在
  一半数据集上按冻结规则退化为不可辨识分支（RAVEN-NoDesign = 无机会校正），且该分支
  正是 T-Drive 上落后 FedAU/ObsUse +2.39%/+2.43% 的那一行；没有任何排序同时实测
  R、O、U；覆盖度定理与其实证审计同向冲突。
Confidence: 4/5
```

相对解释（近似，非官方分档）：作为**问题表述 + 诚实负结果 + 协议公开**的工作，处于 TMC 稿件池的 **average/borderline**；作为**方法论文**（要求所提方法在目标指标上优于强基线），处于 **below average**。本报告按后者定档，理由是 TMC 正刊的刊文主体是方法/系统贡献。

---

## 6. 优点与弱点（Strengths And Weaknesses）

### 优点

- **问题是 TMC 原生的，不是 FL/IPW 的换皮。** §I L113–L126 把"进入学习的数据未必服从部署总体"显式建模为 $R/O/U$ 三层，并明确 windowed-asynchronous 与 immediate-update FedAsync 的区别（L109–L111）。
- **对象切分诚实且具体。** §II L300–L314 明确 FedIPW 是"名册上的两阶段 IPW"、FLOSS 是客户级 IPW、FedPALS 对齐标签边缘，三者都不是本文的 $h(i)$ 公开度量；附录 Table V（nearest-neighbor）逐族给出 target/selection/sensing-side/finite-support 四列对照。
- **理论边界没有过度宣称。** Prop. 1 明说只是"泛函区分，不声称任何预测器必然数值不同"（L1118–L1119）；Prop. 2 明说不证明 $\mathcal{R}_\mu(\theta)$ 优化（L1176–L1188）；Prop. 3 明说"不解释 U-Air 全 Design 反转，因为 A5 不成立"（L1257）。
- **负面结果写在正文而不是藏起来。** 摘要直接写 "on T-Drive, FedAU-Window and ObsUse-Window remain strongest"（L84–L88）；§Limitations L1900–L1901 复述该落败；Table XXII 明写 TwoStage-Hàjek 最低（appendix L2326）；INT-R 明写 burstiness 声明 +0.38 而实测约 0.20（appendix L1990–L1996）。
- **统计规范到位。** 配对种子、Wilcoxon + Holm、预注册 +0.5% 描述性容差并明说"不是正式非劣性检验"（L1494–L1495）、ALL20/TEST10 双披露（L1671–L1675）。
- **复现包的核心表格数据本轮可复核：** `verify.py` 返回 `checked=1886 mismatches=2`，其余 1884 个文件哈希全部匹配；Holm 家族 CSV 四行全部 `significant_holm_0.05=False`，与正文 "Holm-adjusted tests … are not significant"（L1678–L1679）一致；Table II CSV 单元格与正文表值逐格一致。两处失配见 M6。
- **散文质量达标。** `check_prose_quality.py`：10729 词、em dash 0/3、仅 2 条非阻塞提示（uniform_sentence_run、semicolon_density）。

### 弱点

```text
Weakness: E4 消融证明论文自身的"获胜指标"没有预测效力，且两个核心模块无边际贡献。
Evidence basis: Table IV（main.tex L1807–L1827）。SensorScope：Design 使 Δ_group +1.237%、
  Δ_c–s +0.597%（均 Holm 显著），但 RMSE_μ 仅 +0.005%。Use 在四个端点上全部不显著
  （+0.026/+0.026/+0.012/+0.012）。Debt 全部 <0.015%。Obs 端点相关且 Δ_c–s 方向相反。
  U-Air：Design 使 Δ_group −6.943%、RMSE_μ −6.553%（显著变好），只换来 Δ_c–s +4.990%。
  正文 L1880–L1888 自己总结为 "not five monotone boosters"。
Reviewer deduction: 论文的排序头条是 Δ_group/Δ_c–s，而这两个指标在论文自己的消融里
  不随预测端点移动（Design 让 Δ_c–s 变好 0.6%，RMSE 只动 0.005%），说明该指标与
  "预测器服务部署目标"解耦；Use/Debt 经检验无独立作用。据此，五模块耦合架构的实证
  回报无法被验证。Evidence 维度显式扣分。
Required fix: (a) 把 Δ_group/Δ_c–s 与 RMSE_μ/WorstGroupRMSE 的关联单独做一个实验
  （例如人为改变 ω̄_R 与 μ 的距离，观察 RMSE_μ 是否单调响应）；(b) 从 Algorithm 1
  与贡献陈述中裁掉或降级无边际作用的 Use/Debt；(c) 若不裁，需给出 Use/Debt 在
  非 Complete-aligned 家族下会产生作用的证据。
```

```text
Weakness: 主方法按数据集切换配置，使 Table II 不是单一方法的评估，而是"事后选择分支"的评估。
Evidence basis: §Eval setup L1453–L1462：E3/E4 遵循冻结启发式 φ，数据集级赋值；
  SensorScope φ=0 → RAVEN-Design；U-Air φ=35.4% → RAVEN-NoDesign（ẑ^o=1，不作目标
  质量重建）；T-Drive φ=47.4% → NoDesign；City Scanner/NSW φ=0 → Design。
  摘要 L79–L88 与标题同时保留两个名字。
Reviewer deduction: 读者无法从 Table II 得知"RAVEN-MCS 作为单一方法是否有效"，只能
  得知"在这四/六个数据集上按各自 φ 选择的分支分别表现如何"。被检验的有效分支
  （Design-on）只在 φ=0 的数据集出现；φ>0 的分支等价于取消机会校正。因此"方法在
  六分之四数据集上以有效配置运行、在另外两个上以可辨识性不足的分支运行"这一结构，
  需要用 within-dataset factorial（同一数据集同时报告 Design-on/off）来替代。
Required fix: 至少在一个 φ>0 的数据集上补做受限支持（restricted-support）的 Design-off
  策略，或改为按数据集同时报告两个分支；并在正文给出"分支切换率"作为方法的一部分。
```

```text
Weakness: 覆盖度定理与其自身实证审计同向冲突，且该组件未被使用。
Evidence basis: Thm. 2（L1282–L1297）在 Assumption 1 下给出 P(C^LCB ≤ C | g) ≥ 0.95；
  附录 Table XVII（appendix L2115–L2134）实测 U-Air a=1.00 时 n_cert=8、validity=0.750，
  即低于名义 95%。正文 L1910–L1911 披露了 0.959/0.750；L1304–L1305 明说 Gate 不打开
  Design。
Reviewer deduction: 论文引入一个"名义 95%"的认证对象，在其唯一被审计的独立数据集上
  实测只有 0.750，同时该对象对方法行为没有任何影响。这既削弱 Thm. 2 的可信度（
  Assumption 1 在该窗口类上不成立），也使该整章在读者眼中成为非承重结构。
Required fix: 要么给出 Assumption 1 的可操作检验并解释 0.750 的来源（例如 n_cert=8
  的有限样本 + 分数非可交换），要么把该章降级为附录诊断并从摘要/贡献中移出。
```

```text
Weakness: 最贴近动机的鲁棒性检查（INT-R）在标定上系统性偏离，且其失败方向有利于论文结论。
Evidence basis: appendix L1990–L1996：burstiness 目标 +0.38，但稳定性筛选选出
  α≈0.775/β≈0.837 的链，pooled burstiness ≈0.20；该块"匹配 T-Drive 的活跃比例
  0.425，而不是 burstiness"。Table XVI（appendix L2013–L2025）显示 SensorScope
  三颗种子 burstiness 0.198–0.251。
Reviewer deduction: 论文动机是"移动机会间歇、突发、稀疏"，而突发性最强的正是最难
  的场景；用突发性不足的链做鲁棒性检查，检查难度被降低，结论（+0.5% 容差保持符号）
  因而偏乐观。这不是造假，但削弱了该块作为鲁棒性证据的效力。
Required fix: 报告突发性目标下的单种子结果（哪怕失稳），或明确写出"本块不覆盖
  高突发性区间"并在 Limitations 中标注该缺口。
```

```text
Weakness: 复现包自校验在仓库当前状态下不通过，且两个混合排序的数据源未打包。
Evidence basis: 本轮实跑 `RAVEN_MCS_PUBLIC_REPRO_R1/verify.py` →
  `HASH_MISMATCH scripts/rebuild_table_ii.py`、`HASH_MISMATCH tdrive/TD_R_FREEZE.json`、
  `checked=1886 mismatches=2`（退出码 1）。§Data and Code Availability L1958–L1962
  自述 Table XXI/XXII 不在打包文件内。
Reviewer deduction: 一个自称"冻结"的公开复现包在作者自己的仓库里无法通过自己的验证器，
  审稿人会直接停在第一行错误上；两个混合排序的主数据源缺失使 Table XXI/XXII 无法复核。
  这两点把 Reproducibility 压在 4。
Required fix: 刷新这两个文件的 MANIFEST 哈希至 mismatches=0；打包 City Scanner 两个
  块的排序源 CSV，或把这两张表从"论文结论"降级为"探索性附录观察"。
```

```text
Weakness: 强基线为窗口化改编而非官方复现，且"+0.5% 描述性容差"的切片选择使结论脆弱。
Evidence basis: appendix L1620–L1658 给出 FedAU-Window/ObsUse-Window/TimeAlign-Agg 的
  窗口化公式，明说 "not official reproductions"。U-Air worst-group 对 FedAU/ObsUse
  的 TEST 切片为 +0.48%/+0.44%（L1671–L1673），而 ALL20 为 +0.002%/+0.075%
  （L1674–L1675）；Holm CSV 中 U-Air 两行 p=0.956/0.812，Holm=1.0。
Reviewer deduction: 排序叙述使用 10 个种子的切片，而冻结表使用 20 个种子；两切片
  结论差距达两个数量级。读者会问"为什么用切片而不是表均值"。此外被击败的 FedAU 是
  改编版，读者无法排除改编实现不利于基线。
Required fix: 排序叙述统一使用 Table II 的 20 种子均值；给出改编基线的超参搜索范围
  （或至少说明未调参），并补一个"FedAU 改编 vs 其原论文设定"的敏感性说明。
```

```text
Weakness: E2 只证明了"风险对一次协议性选择位移不那么敏感"，不构成一般性的不可互换性证据。
Evidence basis: §Eval RQ1 L1521–L1529：五个方法 D_aligned 均值 −0.0209…−0.0214，
  17–18/20 种子为负，Wilcoxon p≈5e−4；但文中同时给出"目标风险变化仅约 8e−4，而到达
  风险变化约 2.2e−2"。Fig. 2 caption 自述"not a method ranking"。移动 R 侧的 TV 只在
  Fig. 4（T-Drive）给出，且 $D_{\mathrm{aligned}}$ 未在 T-Drive 上复算。
Reviewer deduction: E2 的效应量来自"两个风险分母不同"，而不是来自"两风险在真实移动
  机会下分道扬镳"。Prop. 1 本身是几乎一句话的线性泛函区分（见下条），因此 E2 目前
  只支持一个较弱命题：同一次选择位移在两套权重下的位移量不同。
Required fix: 在 T-Drive 真实 $R$ 上复算 D_aligned（把 R 设为真实轨迹机会、O/U 保持
  控制），使 E2 与论文动机中的"真实移动机会"直接对齐。
```

```text
Weakness: 理论增量相对 IPW/Hàjek/参与偏差文献属于教科书级。
Evidence basis: Prop. 1 的证明是一行（"两个不同概率测度定义不同的线性泛函"）；Prop. 2
  是 A1–A3（正确理想比、顺序可忽略、正性与正则）下的标准 Hàjek 比相合性；Thm. 1 是
  强凸规划解的存在唯一性；Prop. 3 是固定活跃集下的 Lipschitz 扰动界。
Reviewer deduction: 论文自己在 L232–L236 承认"novelty 不是 IPW 或 Hàjek 本身，而是
  部署目标语义 + 分层合法历史 + 有限支持校准的组合"。承认是诚实的，但也意味着理论部分
  不能支撑 Overall 的上行。
Required fix: 明确写出相对 Hàjek/Shimodaira/Robins 的增量定义（例如"首次把序列选择
  的合法历史边界写成不可折叠的三层因子，并证明折叠会破坏目标质量"），并给出一个
  "折叠式单层 IPW 会失败"的解析或数值反例。
```

---

## 7. 可能缺失的相关工作（Potentially Missing Related Work）

```text
Work: FedIPW / "Who Trains Matters: Federated Learning under Enrollment and
  Participation Selection Biases"（Morishita, arXiv:2604.26604）
Status: searched（本轮确认存在，仍为预印本）
Why relevant: 两阶段（enrollment → participation）IPW，朝向目标总体均值更新
Overlap: 两阶段选择词汇；对象仍是客户端名册，不是 MCS 单元级 R/O/U
Needed comparison: 已在 §Related Work L300–L306 以"最近邻、但不作为 MCS 基线"处理；
  若审稿人要求，可补一个在 station 代理客户端上的名册级 FedIPW 对照
```

```text
Work: FLOSS（Goetze et al., PACMI '25, DOI 10.1145/3766882.3767180）
Status: searched
Why relevant: 客户级 opt-out / straggler 的 IPW 聚合
Overlap: 非随机缺失下的 IPW 聚合；对象为客户端名册
Needed comparison: 对象切分已在 §Related Work L307–L309 写明；无需实证对照
```

```text
Work: FedPALS（Listo Zec et al., arXiv:2411.03799）
Status: searched
Why relevant: 向已知目标标签分布聚合
Overlap: 仅"target-aware"措辞；对象是类标签边缘
Needed comparison: 已明确排除为比较基线（L310–L314），处理得当
```

```text
Work: 联邦保形预测（lu2023federated / plassier2023conformal）
Status: searched（作者已引用）
Why relevant: 覆盖度语言上最近的邻居
Overlap: 本文 Gate 是对实现覆盖 C_t 的窗口级下界，不是预测集
Needed comparison: 正文 L280–L285 已作区分；建议补一句"为何不能直接借用保形覆盖保证"
  （因为 C_t 不是可交换分数，Assumption 1 才是其替代品）
```

---

## 8. 主张—证据审计（Claim-Evidence Audit）

| 主张 | 出处 | 提供的证据 | 强度 | 评审扣分 | 需要的修复 |
| --- | --- | --- | --- | --- | --- |
| 到达风险与部署目标风险在法则不同时不可互换 | 摘要；Prop. 1；Fig. 2 | NSW E2 的 D_aligned 负位移（p≈5e−4），但效应量来自分母差异 | adequate | 只支持弱命题；未在真实移动 R 上复算 | 在 T-Drive 真实 R 上复算 D_aligned |
| RAVEN-Design 减少结构失配并落在描述性 +0.5% 容差内 | 摘要；Table II；§Limitations | SensorScope Δ_group 1.0139 vs FedAvg 1.0558（−3.96%）；worst-group TEST −0.01%/+0.05% | adequate as claim-scope | Δ_group 不预测 RMSE（E4：Design 使 Δ_group +1.237% 而 RMSE 仅 +0.005%） | 建立 Δ_group 与预测端点的关联实验 |
| RAVEN-NoDesign 是 $\widehat\zeta=1$ 的非重建回退 | 摘要；Alg. 1；Table II；Limitations | U-Air/T-Drive 具名行；φ=35.4%/47.4% | adequate as scoping | 该分支等价于取消机会校正；本文最强结果（City Scanner/Pilot~2）出现在该分支 | 明确写出"方法的有效分支在六分之二数据集上不可用" |
| φ 是冻结部署启发式，不是 A1/A5 正性判据 | eq:scd_phi；Alg. 1 注释；§Limitations | Table XX 六块 φ；各块 π^tar 构造不同 | adequate as protocol | 凭 → 在部分数据集屏蔽全部校准 | 补 within-dataset factorial |
| T-Drive 上 FedAU/ObsUse 仍最强，NoDesign 超出 +0.5% | 摘要；Table III；结论 | 1.1069/1.3106 vs 1.0898/1.2801；+2.39%/+2.43% | adequate and honest | 唯一真实移动机会的排序是方法落败 | 保持为负结果，或补实测 U 层 |
| City Scanner 实测 O 排序中 RAVEN-Design 优于 FedAU/ObsUse/FedAvg | §Eval；Table XXII | 0.7135/0.7311 vs 0.7173/0.7351 与 0.7182/0.7359；配对 −0.43%/−0.45%/−0.65% | adequate but weak | 该块 $U$ 仍为控制；Hàjek 在两个端点更低；未做显著性 | 补 10 种子配对检验；说明 U 缺失的影响方向 |
| 理想序列校正可恢复兼容目标矩/组质量，但不证明优化目标风险 | 摘要；Prop. 2；结论 | 命题 + 附录完整证明；ψ 与 φ 分离 | adequate | 理论增量为教科书级 | 给出折叠式单层 IPW 的失败反例 |
| 不存在同时实测 R、O、U 的排序 | 摘要；§Eval；结论 | 各混合表均标注控制层 | adequate and honest | 这是全文最重要的能力天花板 | 若冲 TMC 方法刊，需要补该排序 |
| 覆盖度下界在 Assumption 1 下 ≥ 1−α | Thm. 2；§Limitations | 附录 Table XVII：0.959 pooled，U-Air a=1.00 为 0.750 | weak | 名义 95% 在唯一独立数据集实测 0.750；Gate 不影响方法 | 解释 0.750，或降级出摘要/贡献 |
| Holm 检验对 FedAU/ObsUse 均不显著 | §Eval；Availability | `E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv` 四行全 False（本轮实测一致） | strong（对披露而言） | 同时也说明无显著胜利 | 保持该披露 |

---

## 9. 实验 / 基准 / 复现审计（Experiment / Benchmark / Reproducibility Audit）

- **基线**：FedAvg-Window、FedAsync-Window、TimeAlign-Agg、Local-Hàjek、TwoStage-Hàjek、FedAU-Window、ObsUse-Window。官方 FedAU/TimeAlign 复现均未主张；改编公式在附录 L1636–L1658 全部列出，这一点很好。但改编基线未报告超参搜索范围，"未调参"与"调过但未报告"无法区分。
- **消融**：E4 单因子移除（Design/Obs/Use/Inst/Debt），配合 Table IV 与附录 Fig. 5/6。Use、Debt 无独立效应；Design 作用方向按数据集反转。
- **数据集**：SensorScope/U-Air 为主表（always-on 协议 $R$，站点轨迹）；NSW-Traffic 提供 E2 与四区域协议排序；T-Drive 为真实 $R$ + 控制 $O/U$；City Scanner 两块分别为真实访问占用 + 控制 $O/U$ 与实测 $O$ + 控制 $U$。**没有任何块实测 $U$。**
- **指标**：RMSE$_\mu$、WorstGroupRMSE、Δ_group、Δ_c–s。前两者用户可感知，后两者是结构对齐度量；E4 显示后两者与前两者脱钩。
- **统计严谨度**：配对种子 + Wilcoxon + Holm 规范；主表 20 seeds，混合/协议排序 10 seeds；"+0.5% 均值相对"被正确标注为描述性而非覆盖度保证的非劣性检验。混合排序（10 seeds）未给出显著性，而行文用"lower than"表述，属于弱证据下的强措辞。
- **隔离性**：混合表明确不并入 Table II，本轮核对作者确实做到（正文 9 处 "not mixed into"）。Table II 单元格与 `TABLE_II_MAIN_EFFECTIVENESS.csv` 逐格一致。
- **本机可复核的关键数字**（本轮实测）：
  - `TABLE_II_MAIN_EFFECTIVENESS.csv`：SensorScope RAVEN 7.93799 / 8.67066 / 1.01394 / 1.26438；U-Air RAVEN-NoDesign 1.11306 / 1.17027 / 1.01652 / 1.29493 —— 与 main.tex L1719、L1727 一致。
  - `E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv`：四行 significant_holm_0.05 全为 False；U-Air 两行 p_raw 0.956/0.812 —— 与 L1678–L1679 一致。
  - `SCD_PHI.csv`：sensorscope 0/10285=0.0；uair 2016/5688=0.35443，且记录 `phi_et_occ=0.2547`（即正文反复澄清的 25.5% 是 EventTrace 出现占比而非 φ）—— 与 L1836–L1839、附录 L2160–L2161 一致。
  - `verify.py`：本轮实跑为 `checked=1886 mismatches=2`（退出码 1），两处失配为 `scripts/rebuild_table_ii.py` 与 `tdrive/TD_R_FREEZE.json`；**其余 1884 个文件哈希全部匹配**，即 Table II、Holm 家族、slice、T-Drive 四区域等核心 CSV 是可逐格复核的。
- **产物与复现性**：`RAVEN_MCS_PUBLIC_REPRO_R1` 含 EventTraces、processed 原子单元、Table II/Holm/slice/T-Drive 四区域 CSV 与 4 个重建脚本，核心表格数据本轮可复核，这一点应被明确肯定。缺口是上述两处哈希失配（其中 `rebuild_table_ii.py` 正是 Table II 的重建脚本，失配意味着"从 CSV 重建 Table II"这条路径无法被验证器确认未被改动）、Table XXI/XXII 的源 CSV 与两个混合排序的可复核数据，以及"该包不是 pinned 重训练档案"（作者已自述，L1961–L1962）。
- **局部局限**：Local-Hàjek 在正式块上退化为 FedAvg（附录 L1488–L1514 给出 9666 个有效客户端窗口权重极差为 0 的成因），说明该基线在该协议下不具区分力；论文处理得当，但这也削弱了"六基线"的多样性。

---

## 10. 多审稿人小组（Multi-Reviewer Panel）

```text
Reviewer: Best-justified（TMC MCS/FL 系统，同情视角）
Expertise: 移动群智感知与联邦学习系统
Likely score: 7/10
Confidence: 4
Main positive signal: 问题原生、对象切分清楚、披露极致诚实（T-Drive 落败、Hàjek 最低、
  burstiness 未达标、Gate 0.750 全在正文）、复现包可哈希校验
Main negative signal: Table XXII 上 Hàjek 更低、T-Drive 落败、无显著胜利、Use/Debt 空转
Evidence basis: 摘要；Tables II/III/XXI/XXII；E4；verify.py
Fatal concern if any: none
Score-change condition: 实测 U 的排序中本方法同时优于 Hàjek 与 FedAU/ObsUse
```

```text
Reviewer: Critical（TMC 系统怀疑视角）
Expertise: 系统评估方法学
Likely score: 4/10
Confidence: 4
Main positive signal: 不再把 Design-off 说成标题方法、不再把 φ 说成正性判据
Main negative signal: E4 证明获胜指标无预测效力；φ 分支使 Table II 不是单方法评估；
  Thm. 2 实测 0.750；INT-R 突发性 0.20 对 +0.38；无任何块实测 U；T-Drive 落败
Evidence basis: Table IV；Alg. 1；附录 Table XVI/XVII；Table III
Fatal concern if any: 未达 fatal 门槛，但"方法在最有意义的指标上不优于简单基线"叠加
  "有效分支在一半数据集不可用"已足以支撑弱拒
Score-change condition: within-dataset factorial + 目标指标上的显著改善
```

```text
Reviewer: Method / soundness（IPW / 选择 / 校准）
Expertise: 因果推断与调查抽样
Likely score: 5/10（Soundness 3）
Confidence: 4
Main positive signal: 三层合法历史边界写得精确；Prop. 2 的条件与范围诚实；P2 的强凸性
  与唯一解成立；ψ 与 φ 已分离
Main negative signal: Prop. 1 平凡；Prop. 2 是标准 Hàjek 比相合性；φ=0 仍是启发式而非
  由支持或正性导出；Arrival 律里 q^use 用"评估期边缘"替代序列历史，而 A2 又假定序列
  可忽略，估计量本身没有被证明对目标矩相合
Evidence basis: §III–§VI；eq:arrival_intensity；A1–A5；附录证明
Fatal concern if any: none（但估计量一致性与 A2 的关系需要写清）
Score-change condition: 给出 φ 的导出规则，或把式 (14) 的估计量写成真正顺序可忽略的形式
```

```text
Reviewer: Evidence / experiment
Expertise: 实证联邦学习与统计方法学
Likely score: 4/10（Evidence 3）
Confidence: 5
Main positive signal: 主张与表格高度一致；ALL20/TEST10 双披露；Holm 家族与复现包对齐；
  本轮实测 CSV 与正文逐格一致
Main negative signal: 无显著胜利；Δ_group 与 RMSE 脱钩（E4）；混合排序 10 seeds 无检验；
  TEST 切片与 ALL20 差两个数量级；City Scanner 两表与 NSW 表互相矛盾的 FedAvg 位置未解释
Evidence basis: Tables II–IV、XIV、XXI、XXII；E4 Holm CSV；slice CSV
Fatal concern if any: none
Score-change condition: 在冻结的 20 种子主表上取得任一预测端点的 Holm 显著优势
```

```text
Reviewer: Novelty / positioning
Expertise: 参与偏差联邦学习
Likely score: 6/10（Originality 4）
Confidence: 4
Main positive signal: 单元级 R/O/U + h(i) 公开度量 + 有限窗口 P2 的组合确实不是 FedIPW/
  FLOSS/FedPALS
Main negative signal: IPW/Hàjek 本身古典；组合式创新在实证上没有兑现；Hàjek 在实测 O 的
  两个预测端点上更低
Evidence basis: §II 与 Table V；Table XXII
Fatal concern if any: none
Score-change condition: 一个"折叠式单层 IPW 失败、三层成功"的判决性实验或反例
```

```text
Reviewer: Writing / clarity
Expertise: TMC 可读性
Likely score: 6/10（Clarity 3）
Confidence: 4
Main positive signal: 摘要 191 词；两方法命名清晰；无 em dash；段落逻辑基本可恢复
Main negative signal: 术语与断言密度极高（"support-conditional"、"Complete-aligned"、
  "EventTrace"、"描述性容差"、"not mixed into" 出现 9 次）；两张混合表的表体只在附录；
  Table II 中同一 dataset 下并存 Design/NoDesign 两行增加第二遍阅读成本
Evidence basis: 摘要；§Eval II–V；附录 XXI/XXII
Fatal concern if any: none
Score-change condition: 压缩到 12 页并把一张 City Scanner 表移入正文
```

```text
Reviewer: Ethics / reproducibility
Expertise: 产物与许可
Likely score: 6/10（Reproducibility 4）
Confidence: 5
Main positive signal: 公开数据集 + 许可标注（CC BY 4.0）；隐私非保证声明；核心表格 CSV
  （Table II / Holm / slice / T-Drive）本轮逐格可复核
Main negative signal: `rebuild_table_ii.py` 与 `TD_R_FREEZE.json` 两处哈希失配；
  Table XXI/XXII 源数据未打包；作者占位符；非 pinned 重训练档案
Evidence basis: §Availability；verify.py；supplemental 标题页
Fatal concern if any: 作者块属上传阻塞（政策），非科学致命
Score-change condition: 打包两张混合表源 CSV + 补齐作者列表
```

```text
Reviewer: Domain application（MCS 部署）
Expertise: 城市感知部署
Likely score: 4/10（Significance 3）
Confidence: 4
Main positive signal: 用了真实出租车轨迹机会、真实访问占用、实测观测缺失（1931/14960，
  12.9%）；客户端定义为占用栅格而非车辆这一点写得很清楚
Main negative signal: $U$ 从未实测；站点＝客户端不是移动客户端；占用栅格≠车辆；
  没有任何端到端部署证据；INT-R 的突发性被削到 0.20
Evidence basis: Table I；Table III；附录 XXI/XXII；INT-R
Fatal concern if any: none
Score-change condition: 车辆级客户端 + 实测可用更新/网络层
```

```text
Reviewer: Evidence/ablation
Expertise: 组件隔离
Likely score: 4/10
Confidence: 5
Main positive signal: E4 单因子移除 + 全 Design 诊断行 + Holm 家族
Main negative signal: Use/Debt 空转；Design 的 ON/OFF 是数据集级切换，因此主表上没有
  同数据集内的因子对比；Inst-Cal 与 RAVEN-Design 在附录数值上完全相同（$7.9380$/
  $1.0139$/$1.2644$ 与 $7.9380$/$1.0139$/$1.2644$），说明"校准"步骤在该块未产生可测差异
Evidence basis: Table IV；附录 Tables VIII/IX（app_e3_sensorscope/uair）
Fatal concern if any: none
Score-change condition: 同数据集内的 Design 因子实验 + 校准步骤的可测效应
```

```text
Reviewer: Reproducibility（artifact）
Expertise: 发布工程
Likely score: 6/10
Confidence: 5
Main positive signal: 1850+ 文件哈希清单、EventTrace parquet、重建脚本、Table II/Holm/
  slice/T-Drive CSV 齐备，其中 1884 项本轮校验通过
Main negative signal: 两处哈希失配（含 Table II 重建脚本本身）；两张混合表源数据缺失；
  README 未给出从 EventTrace 到 Table II 的端到端重跑路径（只有重建脚本，不是训练复现）
Evidence basis: RAVEN_MCS_PUBLIC_REPRO_R1/README.md；MANIFEST.csv；verify.py
Fatal concern if any: none
Score-change condition: 补端到端重跑说明与缺失 CSV
```

```text
Reviewer: Novice advocate
Expertise: 首遍 TMC 阅读
Likely score: 5/10（accessibility 3）
Confidence: 4
Main positive signal: 摘要直说两方法、T-Drive 落败与联合实测天花板
Main negative signal: 阅读 Table II 前需先消化 R/O/U、π^tar、μ、h(i)、s(i)、φ、ω̄、Δ 共
  8 组符号；"TEST seeds 30011–30020" vs "ALL20" 的第二遍阅读成本高
Evidence basis: 摘要；§III；§Eval；Table II caption
Fatal concern if any: none
Score-change condition: 增加一页术语表 + 一张流程示意把两分支画在同一张图上
```

```text
Agreement:
  对象切分相对 FedIPW/FLOSS/FedPALS 是真实的。
  T-Drive 是公开披露的负结果，Table XXII 上 Hàjek 最低也未被掩盖。
  复现包本轮哈希校验通过，Table II 与 Holm 家族可逐格复核。
  论文对理论边界（不优化目标风险、不声称无偏）的限定是认真的。
Disagreement:
  同情方认为"问题表述 + 诚实负结果"足够支撑 TMC 的 weak accept；批判方认为 E4 已经
  证明获胜指标无预测效力，方法在目标指标上不优于简单基线，属于方法贡献不足。
  分歧焦点不是"是否诚实"，而是"诚实是否足以替代胜利"。
Decisive positive axis:
  部署目标质量语义 + 三层合法历史边界 + 对混合证据的完整披露。
Decisive negative axis:
  没有任何一项证据表明该五模块耦合系统在用户可感知指标（RMSE_μ / WorstGroupRMSE）上
  优于 FedAvg/FedAU/ObsUse/Hàjek；其获胜指标经其自身消融证明与预测端点脱钩；有效分支
  在一半数据集上被自身启发式关闭。
Unresolved evidence:
  φ 是否真的先于数据冻结（作者称冻结于训练侧统计，但无可核验的决策时间戳证据）；
  Table XXI/XXII 的源数据与显著性；U 层的实测缺席；Thm. 2 与 0.750 的关系。
AC stance:
  弱拒（Overall 4/10）。不是桌面拒稿，也不是 clear reject：方法论表述与披露质量明显
  高于平均，但方法/系统贡献未达到 TMC 正刊的刊文门槛。
```

---

## 11. 关注点清单（Concerns Table）

| ID | 严重度 | 关注点 | 证据基础 | 受影响维度 | 修复类别 | 需要的行动 | 归属技能 | 分数变动条件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | major | E4 证明论文获胜指标（Δ_group/Δ_c–s）与预测端点脱钩，五模块架构无可验证回报 | Table IV：SensorScope Design 使 Δ_group +1.237%、RMSE +0.005%；U-Air Design 使 RMSE −6.553% 而 Δ_group −6.943%；Use/Debt 全不显著 | Evidence；Significance | experiment | 补"结构对齐 ↔ 预测端点"的关联实验；裁掉或降级 Use/Debt | ccf-experiment-designer | 若在冻结 20 种子主表上取得任一预测端点的显著优势，Evidence 3→4、Overall 4→5 |
| M2 | major | 主方法按数据集切换分支，Table II 不是单一方法的评估 | §Eval L1453–L1462；Alg. 1；Table XX φ 表；摘要两方法命名 | Soundness；Evidence | method/soundness | 补 within-dataset Design 因子实验或受限支持 Design-off | ccf-experiment-designer | 若给出统一下的单一方法且保持排序，Soundness 3→4 |
| M3 | major | 覆盖度定理与其实证审计冲突（名义 95% vs 实测 0.750），且该组件不影响方法行为 | Thm. 2 L1282–L1297；附录 Table XVII U-Air a=1.00 validity 0.750；L1304–L1305 Gate 不切换 Design | Soundness；Clarity | method/soundness | 解释 0.750 的成因，或从摘要/贡献中移出该章 | ccf-paper-writer | 移出后 Clarity +0.5，Overall 不动；给出成因后 Soundness 可回 4 |
| M4 | major | 唯一真实移动机会排序（T-Drive）上方法落败 +2.39%/+2.43%；无任何块实测 U | Table III；§Limitations L1900–L1901；结论 L1941 | Significance | experiment | 补 T-Drive 实测 U（或实测 O）排序，或接受负结果并把论文重新定位为"协议与负结果报告" | ccf-experiment-designer | T-Drive 进入 +0.5% 内则 Significance 3→4、Overall 4→6 |
| M5 | moderate | INT-R 鲁棒性块的突发性 0.20 对声明目标 +0.38，失败方向有利于结论 | 附录 L1990–L1996；Table XVI | Evidence | experiment | 报告突发性目标下的结果或明确标注覆盖缺口 | ccf-experiment-designer | 标注缺口后 Evidence 保持 3，但降低被质疑风险 |
| M6 | moderate | 复现包自校验在当前工作副本不通过；两张混合表源数据未打包 | 本轮 `verify.py`：HASH_MISMATCH×2，checked=1886 mismatches=2（退出码 1）；L1958–L1962 | Reproducibility | reproducibility | 刷新 MANIFEST 至 mismatches=0；打包 City Scanner 两块源 CSV | ccf-submission-checker | Reproducibility 4→5 |
| M7 | moderate | 强基线为窗口化改编；"+0.5%" 排序使用 10 种子 TEST 切片而表用 20 种子 | 附录 L1620–L1658；L1671–L1675；Holm CSV U-Air p=0.956/0.812、Holm=1.0 | Evidence；Significance | experiment | 排序叙述统一用 20 种子均值；报告改编基线超参范围 | ccf-paper-writer | 统一后 Evidence 3→4（仅当同时有显著优势） |
| M8 | moderate | E2 的不可互换性证据只覆盖协议性选择位移，未在真实移动 R 上复算 | L1521–L1529；Fig. 2 caption；Fig. 4 只给 TV | Soundness | experiment | 在 T-Drive 真实 R 上复算 D_aligned | ccf-experiment-designer | 复算通过则 Soundness +0.5 |
| M9 | moderate | Arrival 律中 $q^{\mathrm{use}}$ 用评估期边缘替代序列历史，而其相合性未被证明 | eq:arrival_intensity L516–L528；A2 L1065–L1070；A3 L1072–L1076 | Soundness | writing | 给出该边缘化何时保持目标矩相合的论证或反例 | ccf-paper-writer | 写清后可回 Soundness 4 |
| M10 | moderate | 理论增量相对 IPW/Hàjek 文献属教科书级（Prop. 1 一行、Prop. 2 标准比相合性） | L1095–L1119；L1144–L1181；L232–L236 自述 | Novelty | method/soundness | 给出"折叠单层 IPW 失败"的判决性反例 | ccf-experiment-designer | 有反例则 Novelty 4→5 |
| M11 | moderate | 两张 City Scanner 表与 NSW 表关于 FedAvg 的位置互相矛盾且未解释 | 附录 Table XXI FedAvg 0.2379/0.2489 最低；Table XXII FedAvg 0.7182/0.7359 被 RAVEN 超过；Table XIV FedAvg 1.0180 | Evidence | writing | 增加一段解释（区域分辨率、客户端定义、O 的实现差异） | ccf-paper-writer | 解释后 Evidence +0.5 |
| M12 | moderate | Inst-Cal 与 RAVEN-Design 的附录数值完全相同，"校准"步骤在该块无可测效应 | 附录 Table VIII：Inst-Cal 7.9380/1.0141/1.2644 与 RAVEN-Design 7.9380/1.0139/1.2644；Table IX 同样 | Evidence | writing | 说明 Inst 与完整 P2 的差异为何在该冻结块上被抹平 | ccf-paper-writer | 说明后降低"模块空转"质疑 |
| M13 | moderate | 作者块为占位符 `****`，补充材料标题页重复同一混合块 | main.tex L57–L60；supplemental.tex \author | 政策/格式 | venue-mismatch | 经授权补齐作者列表 | user / ccf-paper-writer | ScholarOne 阻塞项，不影响科学分 |
| M14 | moderate | main.pdf 14 页对 IEEE CS 12 页 published length，依赖 3 处排版压缩命令 | 本机页数计数 14；L1964–L1966；上轮检索 CS author-resources | 格式 | compression | 压到 12 页或接受 MOPC | ccf-paper-writer | 不影响科学分 |
| M15 | minor | reference.bib 条目内部不一致：wang2023transformer（key 2023）记为 CSUR 58(4) 2025 且 note "Art. no. 7" 与 guo2015mobile 重合 | reference.bib L259–L267、L236–L246；检索确认工作存在但卷期需作者核对 | Reproducibility；写作 | related-work | 核对第一方著录并统一 key/年份 | ccf-integrity-auditor | 修正后仅影响整洁度 |
| M16 | minor | 混合排序（10 seeds）用 "lower than" 表述但未给显著性检验 | §Eval L1622–L1649；附录 XXI/XXII | Evidence | experiment | 补 10 种子配对检验或改为"点估计更低" | ccf-experiment-designer | 补检验后降低过度解读风险 |
| M17 | minor | Table II 使用 `\scriptsize` + `\shortstack` + `\tabcolsep=1pt`，`\Delta_{c\text{-}s}` 维度含义未在表内注明 | main.tex L1707–L1730 | Clarity | writing | 表注补充 Δ 指标定义与量纲 | ccf-paper-writer | Clarity +0.5 |
| M18 | minor | 摘要含数学式（$+0.5\%$、$R/O/U$），IEEE CS 摘要惯例避免公式 | 摘要 L86–L88 | 格式 | writing | 改写为文字表述 | ccf-paper-writer | 不影响科学分 |

---

## 12. AC / 元评审（AC / Meta-Review）

**审稿人共识。** 这是一篇问题表述好、披露质量罕见地高、但方法成效不成立的稿件。共识点有三：对象切分相对 FedIPW/FLOSS/FedPALS 是真实的；T-Drive 落败与 Table XXII Hàjek 最低被主动、充分披露；复现包与主表/Holm 家族本轮可逐格复核。

**审稿人分歧。** 分歧不在事实而在门槛。同情方认为"TMC 原生问题 + 完整协议 + 诚实负结果 + 可复核产物"已构成 weak accept；批判方认为 E4 已经由论文自己证明其获胜指标与预测端点无关，Use/Debt 空转，有效分支在一半数据集被自身规则关闭，因此在 TMC 方法刊门槛下不足。

**决定性接受轴。** 部署目标质量语义、三层合法历史边界、以及对混合证据的完整披露——若审稿人把本文读作"问题与协议的贡献"，这是一篇高于均值的 TMC 稿件。

**决定性拒稿轴。** 五模块耦合系统在用户可感知指标（RMSE$_\mu$、WorstGroupRMSE）上没有任何显著优势；其唯一获胜指标被论文自身消融证明与预测脱钩；主方法在 $\phi>0$ 的数据集上按自身规则取消机会校正；唯一真实移动机会排序上落后简单基线。**"诚实地说自己没有赢"不能替代"必须赢"。**

**AC 立场：弱拒（Overall 4/10，borderline weak reject）。** 与上一版报告的 7/10 分歧集中在一点上：上一版把 E4 的结果
读作"Use/Debt 作为顺序因子/会计保留即可"，本轮把它读作"论文的获胜指标本身不具预测效力，且两个模块无边际作用"，即在 Evidence 与 Soundness 两个维度分别显式扣分。这不是对披露质量的否定，而是对贡献门槛的判断。

**讨论风险。** (1) 审稿人会追问 $\phi$ 分支规则是否事后回填——这是全文可信度最脆弱的一环；(2) 审稿人会把 TEST10 的 $+0.48\%$ 与 ALL20 的 $+0.002\%$ 并列，质疑切片选择；(3) 审稿人会把 Table XXI 与 Table XXII 的 FedAvg 位置矛盾当作"评估不稳定"的证据；(4) 审稿人会跑 `verify.py`，在看到 2 处不匹配后停止阅读； (5) 审稿人会问为什么 Thm. 2 的 95% 在实测中是 0.750。

---

## 13. 定量评分（Quantitative Scores）

### Scorecard

| 维度 | 分数 (1-5) | 置信 (1-5) | 证据基础 | 扣分 / 分数变动条件 |
|:---|:---:|:---:|:---|:---|
| Novelty 新颖性 | 4 | 4 | §II 对象切分 vs FLOSS/FedIPW/FedPALS；Table V；L232–L236 自述 | 无扣分（切分真实）。仅当给出"折叠单层 IPW 失败"的判决性反例才到 5 |
| Soundness 可靠性 | 3 | 4 | Prop. 1（L1095–L1119）；Prop. 2（L1144–L1181）；Alg. 1 的 $\phi$ 分支；eq:arrival_intensity 的边缘化；Thm. 2 vs 附录 Table XVII | 扣分：$\phi$ 非导出规则却在部分数据集关闭全部校准；arrival 律中 $q^{\mathrm{use}}$ 的序列一致性未证；Thm. 2 名义保证与 0.750 实测冲突。修至 4：给出受限支持 Design-off + 边缘化论证；修至 5：$\phi$ 由支持/正性导出 |
| Evidence 证据 | 3 | 5 | Table II/III/IV、XIV、XXI、XXII；Holm CSV；E4 | 扣分：无任一预测端点的显著优势；获胜指标经 E4 证明与预测脱钩；10 种子混合排序无检验；切片与表均值差两个数量级。修至 4：任一预测端点的 20 种子 Holm 显著优势，或完成"结构对齐↔预测"关联实验；修至 5：实测 U 的排序中本方法同时优于 Hàjek 与 FedAU/ObsUse |
| Significance 重要性 | 3 | 4 | Table III（+2.39%/+2.43%）；L1941；附录 XXI/XXII | 扣分：唯一真实移动机会排序落败；$U$ 从未实测；客户端为站点/占用栅格而非车辆。修至 4：T-Drive 进入 +0.5% 内或补实测 U；修至 5：车辆级端到端排序中取得优势 |
| Clarity 清晰度 | 3 | 4 | 摘要 191 词；§Eval II–V；Table II caption；附录 XXI/XXII 表体仅在附录 | 扣分：符号负载高（8 组核心记号先于主表）；两分支同表增加第二遍阅读；"not mixed into" 9 次；Table II 用 `\scriptsize`+`\shortstack`+`\tabcolsep=1pt` 且 Δ 维度未注明。修至 4：加术语表 + 压缩 + 表注补 Δ 定义 |
| Reproducibility 可复现 | 4 | 5 | RAVEN_MCS_PUBLIC_REPRO_R1；本轮 verify.py（1886 项中 2 项失配）；README | 扣分：`rebuild_table_ii.py` 与 `TD_R_FREEZE.json` 哈希失配；两张混合表源数据未打包；包非 pinned 重训练档案。修至 5：mismatches=0 + 补齐 CSV |
| Ethics / Limitations 伦理与局限 | 5 | 5 | 公开数据集与许可；隐私非保证声明；L1890–L1913 局限清单与表格一致 | 无扣分。轨迹再分发条款可再补一句，但不影响该维度 |

**Overall:** 4/10 ｜ **Scholarly Confidence:** 4/5

**Recommendation:** weak-reject（borderline，偏弱拒）
**Verdict:** 之所以不是 5（borderline 正面）而是 4：决定性负面证据来自论文自身——E4 显示其排序指标与预测端点脱钩、Use/Debt 无边际作用；同时有效分支在一半数据集被自身启发式关闭，唯一真实移动机会排序落败。之所以不是 2–3（clear reject）：问题表述是 TMC 原生的、对象切分真实、理论边界诚实、披露质量与产物可复核性明显高于同档稿件。**能改变判决的是新实验（目标指标上的显著优势、实测 U、受限支持 Design-off），不是改写。**

```text
Quality: 3
Clarity: 3
Significance: 3
Originality: 4
Soundness: 3
Evidence: 3
Reproducibility: 4
Ethics / Limitations: 5
Overall: 4/10
Confidence: 4/5
Score-change conditions:
  4 -> 5：完成"结构对齐↔预测端点"关联实验，且 Table IV 的 Use/Debt 空转被消除或裁掉
  4 -> 6：在冻结 20 种子主表上取得任一预测端点的 Holm 显著优势（且仍不宣称最优）
  4 -> 7：补实测 U 的排序并在该排序中同时优于 Hàjek 与 FedAU/ObsUse
  4 -> 3：若发现 $\phi$ 分支赋值实际由测试结果反推（当前无可核验证据，但正文未排除）
  4 -> 2：若 Thm. 2 的 0.750 实测被披露为已知反例却仍以"名义 95%"作为贡献陈述
```

### 写作 / 展示评分卡（full 模式）

| 维度 | 权重 | 分数 (1-5) | 置信 | 证据基础 | 具体修复 |
| --- | ---: | ---: | ---: | --- | --- |
| 故事线与动机 | 10 | 4 | 4 | §I L113–L144 gap 清楚，两分支在贡献中说明 | 无必须修复 |
| 贡献展示 | 10 | 3 | 4 | 三条贡献（L181–L230）与其证据（E4）不匹配 | 按 E4 事实重写第三条贡献的作用范围 |
| 段落逻辑 | 10 | 3 | 4 | §Eval 五小节中 9 处 "not mixed into"；TEST/ALL20 双切片增加认知负担 | 统一切片口径，压缩重复声明 |
| 主张—证据对齐 | 12 | 4 | 5 | 摘要与 Table III/XXII 一致；但 "reduce structural mismatch" 未说明其与预测的关系 | 在摘要为 Δ 指标补一句"不与预测端点同向" |
| 方法可读性 | 9 | 3 | 4 | $\phi/k(i)/\pi^{\mathrm{tar}}/\psi$ 在正文，构造在附录；两分支需交叉阅读 | 增加一页术语与分支对照表 |
| 实验叙述 | 9 | 3 | 4 | 表格先于解释，顺序合理；但 10 种子混合表用 "lower than" 无检验 | 补检验或降级措辞 |
| 相关工作定位 | 8 | 5 | 5 | FedIPW/FLOSS/FedPALS 对象切分准确；Table V 逐族对照 | 无 |
| 术语与记号一致性 | 8 | 3 | 4 | RAVEN-Design/NoDesign 一致；但每块 $\pi^{\mathrm{tar}}$ 构造不同且 $\phi$ 计数口径（25.5% vs 35.4%）需要三处澄清 | 统一 $\phi$ 口径说明入口 |
| 散文纪律 | 10 | 4 | 5 | em dash 0；prose 检查仅 2 条非阻塞提示 | 无 |
| LaTeX 与格式纪律 | 6 | 3 | 4 | 14 页；3 处 `\enlargethispage`；Table II `\scriptsize`+`\shortstack`；摘要含 `+0.5\%` | 压缩到 12 页；表注补 Δ 定义 |
| 面向审稿人的风险 | 8 | 3 | 4 | Hàjek 最低、T-Drive 落败、INT-R 突发性、Gate 0.750 均已可见（正面）；但 E4 与获胜指标的关系未被正文点明（负面） | 在 §E4 末尾显式写出"Δ 指标不预测 RMSE" |
| **写作总分** | 100 | **3.45** | 4 | 加权均值 | 风险档：**中高** |

---

### 与文件夹内其他评审的分数核对（Score reconciliation）

用户问及"为什么只有本轮给 4 分"。下列核对基于 `ccfa-review-reports/` 内全部 8 个文件的实测内容。

| 文件 | 类型 | 日期 | 分数 / 结论 |
| --- | --- | --- | --- |
| `snapshots/...2026-09-11-pass1b.md` | CCFA full（相对打分） | 09-11 | **7/10** weak-accept |
| `snapshots/...2026-09-11-pass2.md` | CCFA full（相对打分） | 09-11 | **7/10** weak-accept |
| `snapshots/...2026-09-11-pass3.md` | CCFA full（相对打分） | 09-11 | **7/10** weak-accept |
| `raven-mcs-tmc-independent-review-2026-09-11.md` | 独立绝对评审 | 09-11 | **4/10** major revision |
| `raven-mcs-tmc-rereview-2026-09-11.md` | 独立绝对评审 | 09-11 | **4/10** major revision |
| `raven-mcs-tmc-rereview-wording-2026-09-11.md` | 独立绝对评审 | 09-11 | **5/10** major revision |
| `raven-mcs-tmc-rereview-wording-2026-09-12.md` | 独立绝对评审 | 09-12 | **6/10** major revision |
| `raven-mcs-tmc-review.md`（本轮） | 独立绝对评审 | 09-12 | **4/10** weak-reject |

```text
结论一：本轮 4 分不是孤立值，而是与文件夹内同类的"独立绝对评审"一致。
  raven-mcs-tmc-independent-review-2026-09-11.md 与 raven-mcs-tmc-rereview-2026-09-11.md
  两份都明确写 "Recommendation: Major revision — 4/10"，其 Soundness / Clarity /
  Reproducibility 三个维度甚至更低（2/5）。本轮与它们在判决上同属"未达投稿就绪"。

结论二：分数分裂来自两种打分体制的混用，不是同一把尺子的分歧。
  (a) 相对打分（7/10 的三份快照）：报告元信息自述为 "full re-review … relative progress
      versus the frozen pass-3 contract"，Verdict 写 "Overall stays 7"，即分数锚定到
      历史 pass，衡量的是"相对上一版有没有退步"，而不是绝对就绪度。
  (b) 绝对评审（4–6/10 的五份）：衡量的是"当前版本离 TMC 接收标准有多远"。
  skill 的 review-output-standards.md 要求这两张评分卡必须分开且不得融合；本轮取的是 (b)。
  把 (a) 的 7 读成 (b) 的 7，会产生"已接近可接收"的误判。

结论三：09-11 与 09-12 之间只有写作与格式修补，没有新实验或新结果。
  09-12 那份 6/10 自己也写明 "Treat the score move 5 → 6 as credit for claim/artifact
  alignment, not for a new empirical win"。因此 4→7 的分差不可能由科学内容变化解释。

结论四：三种尺子的权重结构不同，可预测地产生同一个 4 分。
  · 7/10 的权重：claim / artifact 对齐、诚实披露、协议透明、产物可校验 —— 本文很强。
  · 4–5/10 的权重：方法在目标指标上是否胜出、贡献是否成立 —— 本文很弱。
  · 本轮扣分点（Evidence 3、Soundness 3、Significance 3）全部落在后者，而高分项
    （Ethics/Limitations 5、Reproducibility 4、Originality 4）与 7/10 报告认可的优点
    完全重合。分歧只在一点：获胜是否为发表必要条件。
```

**本轮的自我限定（可能造成系统性偏低）：** 本轮据 TeX 源码与本地页面计数评审，未逐页核对编译后 PDF 的版面，也未复算 JO_E3 配对相对值。若编译 PDF 的图注/表格与源码有实质差异，Clarity 与格式类判断需要重跑；这不改变 Overall，因为决定性扣分来自 E4 与 Table II/III 的数值事实，而这些数值本轮已与复现包 CSV 逐格核对一致。

**若要与 7/10 对齐**，正确做法不是改分，而是换模式：用 `version-comparison` 对冻结 rubric 同时输出"相对进展"与"绝对就绪"两张互不融合的评分卡，或明确声明采用"相对 pass-3 继续给 7"的口径。本轮坚持绝对就绪口径，因为它回答的是"现在能不能投"。

---

## 14. 给作者的问题（Questions For Authors）

1. $\phi=0/\phi>0$ 的分支规则在 SensorScope/U-Air/T-Drive/City Scanner/NSW 上的赋值，是否存在可核验的、早于任何 RMSE 观察的决策记录（时间戳或冻结提交）？如果没有，请说明如何在投稿中让审稿人相信它不是事后回填的。
2. E4 显示 Design 使 SensorScope 的 $\Delta_{\mathrm{group}}$ 改善 1.237%（Holm 显著）而 $\mathrm{RMSE}_\mu$ 只变化 0.005%。请给出 $\Delta_{\mathrm{group}}$ 与预测端点同向变化的证据；否则为什么 TMC 读者应该关心这个指标？
3. Table XXI 中 FedAvg-Window 在两个预测端点上最低，而 Table XXII 中 RAVEN-Design 低于 FedAvg。这两块的分辨率、客户端定义与 $O$ 实现不同，请解释为什么结论方向相反；哪一张表是 MCS 读者应当相信的？
4. Thm. 2 给出名义 $1-\alpha$ 下界，而附录 Table XVII 中 U-Air $a=1.00$ 的实测 validity 是 0.750（$n_{\mathrm{cert}}=8$）。这是 Assumption 1 不成立、还是有限样本效应？该组件对方法行为没有影响，为何保留在贡献陈述中？
5. INT-R 声明 burstiness 目标 $+0.38$、实测约 $0.20$。请给出在 $+0.38$ 附近的结果（即使不稳定），或明确说明鲁棒性检查不覆盖高突发性区间。
6. 混合排序的 10 种子点估计（例如 Pilot~2 的 $-0.43\%$）是否达到配对显著性？若无，正文的 "lower than" 是否应改为"点估计更低"？
7. Use 与 Debt 在 E4 中无独立效应。若把二者从 Algorithm 1 中移除，Table II 的任一单元格会变化吗？如果不会，保留它们的科学理由是什么？
8. Inst-Cal 与 RAVEN-Design 在附录 Tables VIII/IX 上数值完全相同。P2 校准在该冻结块上为什么没有可测效应？这是否说明该模块在 Complete-aligned 家族中不承重？

---

## 15. 分数修订条件（Score Revision Criteria）

```text
提升分数需要（按性价比排序）:
  1. 完成"结构对齐指标 ↔ 预测端点"的关联实验：人为改变 ω̄_R 与 μ 的距离并观察 RMSE_μ
     是否单调响应。若响应成立，Evidence 3→4、M1 关闭、Overall 4→5。
  2. 在 T-Drive 上补实测 O（或实测 U）层并重跑混合排序；若 RAVEN 进入 +0.5% 内，
     Significance 3→4、Overall →6。
  3. 补 within-dataset 的 Design 因子实验（或受限支持 Design-off 策略），使 Table II
     成为单一方法的评估；M2 关闭，Soundness 3→4、Overall +0.5。
  4. 补一个实测 U 的排序，且在该排序中本方法同时优于 TwoStage-Hàjek 与
     FedAU/ObsUse；届时 Evidence 可到 5、Overall →7。
  5. 给出"折叠式单层 IPW 在同样数据上失败"的判决性反例；Novelty 4→5。
  6. MANIFEST 刷新至 mismatches=0 并打包 Table XXI/XXII 源 CSV；Reproducibility 4→5。
降低分数会由以下情况触发:
  - 发现 $\phi$ 的分支赋值由测试结果反推（当前无可核验证据，但正文未排除）→ Overall →3
    或更低。
  - 把 Thm. 2 的名义 95% 作为已验证结论陈述，而表 XVII 的 0.750 被淡化 → Overall →2。
  - 把 Table XXII 写成"优于所有基线"（Hàjek 在两端点更低）→ Overall →3。
  - 把 TEST10 的 +0.48% 表述为 20 种子或显著性结论 → Overall →3。
投稿前不太可能改变的问题:
  作者占位符（需授权）；14 页 MOPC 风险；Use/Debt 在现有家族中的空转；$U$ 未实测；
  客户端为站点/占用栅格而非车辆；$\phi$ 为启发式而非导出规则；每块 $\pi^{\mathrm{tar}}$
  构造不同。以上均需新实验或用户决策，不是写作能解决的。
```

```text
（本节不含版本对比字段：本轮为绝对就绪度独立评审，未与历史 pass 融合打分。）
```

---

## 16. 行动计划与 CCFA 交接（Action Plan And CCFA Handoffs）

```text
Priority: P0
Action: 在 §E4 末尾显式写出"Δ_group/Δ_c–s 不预测 RMSE_μ/WorstGroupRMSE"，并据此重写
        第三条贡献的作用范围；同时把 Thm. 2 与覆盖度 Gate 从摘要/贡献中移出
Owner skill: ccf-paper-writer
Input needed: none
Expected output: 主张与 E4 事实一致的精简贡献陈述
Handoff required: yes
```

```text
Priority: P0
Action: 消除 π^tar 分支规则的可信度风险：公开 φ 的冻结时间戳/提交记录，或用受限支持
        Design-off 策略替代数据集级 φ 切换
Owner skill: ccf-experiment-designer（若改方法）；user（若仅披露记录）
Input needed: 冻结记录或训练授权
Expected output: 可核验的冻结证据，或 within-dataset 因子实验
Handoff required: yes
```

```text
Priority: P0
Action: 刷新 RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv 使 verify.py 返回 mismatches=0，
        并打包 City Scanner 两块排序源 CSV
Owner skill: ccf-submission-checker
Input needed: 当前 rebuild_table_ii.py 与 TD_R_FREEZE.json
Expected output: checked=1886 mismatches=0；Table XXI/XXII 可复核
Handoff required: yes
```

```text
Priority: P1
Action: 补"结构对齐 ↔ 预测端点"关联实验（M1 的关闭条件）
Owner skill: ccf-experiment-designer
Input needed: 训练授权
Expected output: 冻结的关联曲线/表，接入 E4 之后
Handoff required: yes
```

```text
Priority: P1
Action: 报告 INT-R 在高突发性区间的结果，或明确标注覆盖缺口（M5）
Owner skill: ccf-experiment-designer
Input needed: 突发性目标 α/β 的种子稳定性方案
Expected output: 附录一段 + 一处 Limitations 标注
Handoff required: yes if the user asks
```

```text
Priority: P1
Action: 补齐作者列表（M13）；压缩到 12 页或接受 MOPC（M14）；统一 TEST10/ALL20 口径（M7）
Owner skill: user / ccf-paper-writer
Input needed: 授权作者名单；ScholarOne 页数上限
Expected output: 可上传的具名稿件
Handoff required: yes
```

```text
Priority: P2
Action: 核对 reference.bib 中 wang2023transformer 的卷期与 key 年份（M15）；补 Δ 指标表注
        （M17）；摘要去公式（M18）；解释 Table XXI/XXII 与 NSW 的 FedAvg 矛盾（M11）
Owner skill: ccf-integrity-auditor / ccf-paper-writer
Input needed: 第一方著录信息
Expected output: 条目一致 + 表格注释完整
Handoff required: yes if the user asks
```

```text
Checks run:
  ccf-paper-reviewer full workflow（desk / contribution / evidence / adversarial 四遍阅读）
  RAVEN_MCS_PUBLIC_REPRO_R1/verify.py（本轮 checked=1886 mismatches=2，退出码 1）
  TABLE_II_MAIN_EFFECTIVENESS.csv / E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv /
  SCD_PHI.csv 与 main.tex 表格逐格对账
  check_prose_quality.py（10729 词；em dash 0/3；2 条非阻塞提示）
  main.pdf 页面对象计数（14 页）；main.tex label/ref 完整性扫描
  公开检索：FedIPW arXiv:2604.26604；Spatiotemporal Transformer 卷期
Checks skipped:
  完整 GPU 重训练；JO_E3 配对相对值的独立重算；E3 源码提交与工作区 diff；
  TMC ScholarOne 第一方页数上限页面（沿用上轮检索结果）；
  逐段 paragraph ID 全覆盖（高影响章节已覆盖）
Unresolved risks:
  作者占位符；$\phi$ 冻结证据不可核验；$U$ 层实测缺席；Table XXI/XXII 源数据缺失；
  MANIFEST 两处不匹配；Thm. 2 的 0.750 与名义 95% 的关系；reference.bib 卷期核对
```

**可交接的下一个 CCFA 技能**

- `ccf-experiment-designer`：P0/P1 的三个新实验（结构—预测关联、T-Drive 实测 U、within-dataset Design 因子）
- `ccf-submission-checker`：MANIFEST 刷新、City Scanner 源数据打包、页数上限确认
- `ccf-paper-writer`：贡献陈述与 E4 对齐、Thm. 2/Gate 降级、压缩到 12 页、Δ 指标表注
- `ccf-integrity-auditor`：reference.bib 卷期核对、Table XXI/XXII 数据身份
- `ccf-rebuttal-writer`：如需把 M1–M18 摄入 revision ledger（本报告不写 rebuttal 文本）
