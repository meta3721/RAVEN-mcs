# CCFA 论文评审报告（盲审口径）— RAVEN-MCS / IEEE TMC

> `ccf-paper-reviewer` full 模式，**仅依据投稿人提交给审稿人的材料**（submitted manuscript + supplemental）。
> 本报告**刻意不使用**任何历史评审、既有评分、实验室内部证据、复现包、`post_review/`、冻结实验日志或工作区当前 tex 的其他版本。
> 仅评估，不改写稿件正文。

---

## 1. 报告元信息（Report Metadata）

```text
评审日期: 2026-09-12
目标期刊/年份/类型: IEEE Transactions on Mobile Computing (TMC), CCF-A, 正刊 regular paper
稿件标题（提交版）: RAVEN-MCS: Target-Risk-Calibrated Windowed-Asynchronous Federated Data
                  Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
评审口径: 盲审（reviewer-visible materials only）
已审材料（唯一输入集，已用 SHA-256 确认与投稿门户副本一致）:
  deliverable/.../RAVEN_MCS_TMC_PAPER_OVERLEAF_R1.zip 内的 TO_OVERLEAF_paper_tmc_r1_clean/
    main.tex            95,191 字节 / 2,097 行
    appendix.tex        47,572 字节 / 1,436 行（经 supplemental.tex \input）
    supplemental.tex     2,346 字节
    reference.bib       16,871 字节（48 条）
    main.pdf            16 页（pdfTeX-1.40.29，编译于 2026-08-28 18:01）
    supplemental.pdf     8 页（编译于 2026-08-28 17:31）
    figures/*.pdf（8 张向量图）、figure_data/*.csv（7 个绘图源）
  投稿门户副本 deliverable/.../SCHOLARONE_UPLOAD/{main.pdf, supplemental.pdf}
    —— SHA-256 与 zip 内副本逐字节一致
明确未使用（盲审纪律）:
  ccfa-review-reports/ 下的任何历史评审与评分；post_review/ 下任何内部实验；
  RAVEN_MCS_PUBLIC_REPRO_R1 复现包；封存实验日志（E1–E4 gate/seal）；Deliverables 下的
  内部审计报告；工作区当前 tex（该版本标题与命名体系均与提交版不同，不属审稿人可见范围）
检索基础（公开安全检索，未粘贴稿件私有文字）:
  "inverse probability weighting federated learning mobile crowdsensing non-random selection"
  "Hajek normalization target population federated learning two-stage enrollment participation"
  "sparse mobile crowdsensing data completion deployment target distribution shift"
报告文件: ccfa-review-reports/raven-mcs-tmc-blind-review.md
评审模式: full（科学 + 写作 + 格式 + desk + panel + AC）
```

**一条必须先说明的观察（不构成学术扣分，但影响本轮结论的适用范围）。**
本轮评审对象是**投稿包内那一份稿件**。工作区中另存在一个标题为 "Target-**Mass**-Calibrated"、方法命名为 "RAVEN-Design / RAVEN-NoDesign" 的更新版本（含 T-Drive 排序表、City Scanner 排序表、INT-R 与覆盖度压力审计等附录）。两个版本作者块、数据集角色、附录结构均不同。按盲审纪律，**本报告只评本次提交的版本**；若作者实际提交的是另一版本，本报告的适用性随之改变。此外，投稿包内的 pdf 编译于 2026-08-28，而包内 `main.tex` 与之同源，可自洽复现。

---

## 2. 桌面拒稿评估（Desk Rejection Assessment）

```text
Check: 论文篇幅
Status: pass
Evidence: main.pdf 16 页（本机 PyMuPDF 页计数），supplemental.pdf 8 页独立成篇。
  投稿包 README 自述 IEEE CS 规则为"regular papers 12 published pages；submissions may be
  up to 18 pages"。16 页在投稿上限内，属"发表后可能收 MOPC"而非 desk reject。
Consequence: 不构成桌面拒稿；最终排版超 12 页时需压缩或付费。
Required action: 投稿前确认 ScholarOne 对本刊的页数上限；若需避免 MOPC，压缩 4 页。
```

```text
Check: 选题契合度
Status: pass
Evidence: 窗口化异步联邦 + 移动群智感知稀疏补全 + 非随机 R/O/U 选择 + 公开部署目标
  （main.tex L121–L152）。全部测试数据为公开真实数据（SensorScope、U-Air、NSW-Traffic、
  T-Drive）。
Consequence: 落在 TMC 的 mobile systems / crowdsensing / FL 选题范围。
Required action: none
```

```text
Check: 最低质量线
Status: pass
Evidence: 摘要 177 词；含引言、相关工作（3 小节）、系统模型、方法、校准、理论
  （Prop. 1–3、Thm. 1、Assumption 1）、评估（E1–E4）、Discussion and Limitations、
  结论、Data and Code Availability、48 条参考文献；附录 5 部分含完整证明。
  引文编号经程序核对：正文出现的引用号覆盖 [1]–[48]，无缺号、无 "??"、无未替换宏。
Consequence: 可评审。
Required action: none
```

```text
Check: 政策 / 匿名 / 合规
Status: pass for double-anonymous review（附一处残留风险）
Evidence: 作者块为 `**** and Anfeng Liu`，第一作者邮箱为 `****@csu.edu.cn`，符合匿名投稿；
  稿件语言为 "we propose / our method"，无第一人称致谢泄露。
  但第二作者真实姓名、单位（Central South University）、基金号 U24A20248 与真实邮箱
  (afengliu@mail.csu.edu.cn) 仍在标题页与 supplemental 标题页中完整出现。
Consequence: 若 TMC 本轮为双盲评审，标题页的具名信息会破坏匿名；若为单盲则不构成问题。
Required action: 投稿前确认该刊当前评审模式；若双盲，需完整去标识化标题页与基金信息。
```

```text
Check: 提示注入 / 隐藏操纵
Status: pass
Evidence: 逐节扫描 main.tex / appendix.tex / caption / bib key，未发现面向 LLM 或审稿人的
  隐藏指令；模板虽定义了 \red/\blue 宏，但正文中仅出现在宏定义处，未用于标记修订。
  全文彩色文字仅 70 处，全部来自向量图中深蓝/灰色标注文字，无红色修订痕迹。
Consequence: none
Required action: none
```

```text
Check: 伦理与可评审性
Status: pass with disclosure
Evidence: 四个数据集均为公开来源且逐条给出获取地址与脚注链接；§Mobility, Identification,
  and Privacy（main.tex L1997–L2021）明确讨论协变量隐私成本，并声明"RAVEN uses only
  lagged pre-outcome histories… needs only aggregated selection statistics at the server"。
  §Evidence Scope L2005–L2007 明确"not an end-to-end system, not real federated updates"。
  轨迹类数据（T-Drive）未给出再分发/去标识化边界的专门说明。
Consequence: 可评审；轨迹数据治理说明偏薄属可补强项。
Required action: 若将轨迹文件一并归档，补一句去标识化与再分发范围说明。
```

```text
Desk rejection risk: low
Reason: 选题、最低质量线、伦理均通过；篇幅在投稿上限内；匿名状态取决于该刊当期评审模式。
Can be fixed before review? yes（标题页匿名口径、篇幅压缩）
```

---

## 3. 论文摘要与贡献图谱（Paper Summary And Contribution Map）

**一段式摘要。** 论文把"窗口化异步联邦移动群智感知数据补全"表述为**面向公开部署目标的对齐问题**，而非"到达更新频率"问题。感知过程被拆成两层三阶：感知侧的机会 $R$ 与观测 $O$，更新侧的可用更新 $U$；三者复合后，到达律不必等于部署目标律，因此优化到达分布可能优化**错误的总体风险**。方法（RAVEN-MCS）先用合法的事前（pre-outcome）历史做逐层逆概率校正与局部 Hàjek 归一化，得到"目标相关质量"的参考分布；再通过强凸规划 (P2) 把这个参考投影到当前窗口可行的聚合集上，并用长期"目标债务"记录残余欠服务。理论上：Prop. 1 证明两套风险泛函一般不可互换；Prop. 2 在 A1–A3 下证明理想逐层估计相合到兼容目标质量；Thm. 1 给 (P2) 唯一全局解；Prop. 3 给剪枝插值相对于理想参考的 Lipschitz 稳定性。实现层面，方法由**数据集级 gating**决定是否启用 Design 分支：SensorScope 保留 Design，U-Air 关闭 Design。

- **声称的问题**：进入学习的样本未必采样自部署预测器所要服务的总体。
- **声称的缺口**：稀疏 MCS 补全、异步联邦补全、参与感知 FL 三条线都没有联合识别"感知侧可用性"与"更新侧可用性"，也没有把重建目标映射到有限移动窗口。
- **方法与贡献图谱**
  1. 两阶段非随机选择下的部署目标风险语义，以及目标风险与到达风险的不可互换性（Prop. 1）。
  2. 分层校正的目标质量重建：机会/Design、观测、可用更新分别按各自合法信息边界处理，而非折叠成单一缺失概率；理论上给出理想估计的一致性（Prop. 2）。
  3. 可行性感知的即时校准 (P2) 与长期目标债务会计（Thm. 1、Prop. 3），把统计上正确的参考质量映射为当前可行的聚合决策。
- **证据包**：E1 平衡无伤控制（5 seeds）；E2 NSW-Traffic 风险语义（20 seeds，$D_{\mathrm{aligned}}$）；E3 主表（SensorScope 与 U-Air，各 20 paired seeds，Complete-aligned 协议）；T-Drive 真实出租车机会回放（$R$ 真实，$O/U$ 为控制）；E4 单因子消融（Design/Obs/Use/Inst/Debt）；补充材料含完整证明、E2 全量统计、Local-Hàjek 退化分析、P2 可行性诊断、逐块 RMSE、运行时诊断。
- **自述局限**：不主张通用 RMSE 优势（L1964 "The claim is not universal RMSE dominance"）；不主张最优 worst-group 方法；T-Drive 不是排序、不是端到端系统；U 与 O 未联合实测；不在目标支持外识别；不校正任意隐藏混淆；剪枝下不主张无偏；提交时不提供完整训练栈的公开快照。

---

## 4. 检索与相关工作基础（Search And Related-Work Basis）

```text
检索式:
  inverse probability weighting federated learning mobile crowdsensing non-random selection
  Hajek normalization target population federated learning two-stage enrollment participation IPW
  sparse mobile crowdsensing data completion deployment target distribution shift reweighting
已检索来源:
  arXiv / ar5iv / Semantic Scholar / IEEE Xplore 摘要页 / 公开论文 PDF（Temple 大学镜像）
最近的公开工作:
  FedIPW / "Who Trains Matters"（arXiv:2604.26604）—— 两阶段（enrollment → participation）
    的选择偏差 IPW，指向目标总体平均更新。这是与本稿最接近的"两阶段 + IPW + 目标总体"工作。
  FedAU（Wang & Ji, ICLR 2024）—— 用参与历史估计聚合权重，使未知参与不替换原 FL 目标。本稿
    把它改编为 window-close 版本作为主基线之一，属合理做法。
  FLOSS（Goetze et al., PACMI '25）—— 面向 opt-out 与 straggler 的客户端级 IPW。
  FedCure（AAAI 2026）—— 半异步场景下缓解参与偏差；本稿明确声明"is not included"。
未解决的定位风险:
  本稿与 FedIPW 的差异是真实但需要更显式的论证：FedIPW 在客户端名册上做 enrollment 与
  round-level participation 的两阶段校正；本稿在 MCS **感知单元**上做机会/观测/可用更新
  三阶校正，并把目标定义为 $h(i)$ 上的公开度量。这条"对象不同"的切分是成立的，但稿件只用
  §Related Work 的一段话处理，未给出结构化的逐族对照。
来源质量筛查: 未发现低质量来源；48 条引文中 2025–2026 年的条目较多，均为 IEEE/ACM 期刊或
  顶级会议来源，格式为 IEEEtran 标准样式。
```

**新颖性判断。** 公开检索未发现把"感知侧机会与观测 + 更新侧可用性"作为三阶选择、并以公开部署度量为对齐对象的既有工作。FedIPW/FLOSS/FedAU 都在客户端名册层面，FedPALS 类工作在标签边缘层面，稀疏 MCS 补全工作在缺失值插补层面。**问题表述的组合是有新意的**；但每块技术砖（IPW、Hàjek 比、强凸校准、债务递推）都是既有工具，"新"在其组合与对齐对象，而非技术本身——论文自己在 L230–L232 也是这么说的。

---

## 5. 预期评审结果（Expected Review Outcome）

```text
Expected outcome: 拒稿（Overall 4/10，明确拒稿而非偏弱拒）
Main accept signal: TMC 原生的问题表述（部署目标质量 vs 到达律）；两层三阶 R/O/U 的合法信息边界
  写得非常精确；理论边界诚实（不宣称优化目标风险、不宣称无偏、不宣称最优）；统计流程规范
  （paired seeds、Wilcoxon+Holm、预注册的 under-served 检查并如实报告为负）；表述上没有一处
  过度声称（全文 0 处 "state-of-the-art" / "outperform" / "SOTA"）。
Main reject signal: 所提方法在**任何一个用户可感知指标上都没有取得显著优势**——主表的结论
  仅是"非劣（+0.5% 规则）"；论文自己的 E4 消融显示其"获胜指标"（结构对齐 Δ）与预测指标脱钩
  （去掉 Design 使 SensorScope 的 Δ_group 恶化 1.237%，而 RMSE_μ 只动 0.005%）；同时
  Use 与 Debt 在全部四个端点上无显著作用；此外 Design 的启用规则在稿件中只被定性描述，
  读者无法重建；主实验的协议机会是 always-on、且并非移动客户端。
Confidence: 5/5（审稿人可见材料完整：正文 16 页 + 补充 8 页 + 全部图件与源）
```

相对解释（近似，非官方分档）：作为**测量/协议类论文**（强调"这个问题被系统性忽略了，我们用规范化协议把它测清楚了"），本稿处于 average；作为 **TMC 正刊的方法论文**，处于 below average，因为其核心方法没有在目标指标上兑现。

---

## 6. 优点与弱点（Strengths And Weaknesses）

### 优点

- **问题表述是 TMC 原生的，且动机链条完整。** main.tex L121–L134 用"机会 → 观测 → 可用更新"三段把"到达分布 ≠ 部署目标分布"讲清楚，并明确 windowed-asynchronous 与 immediate-update FedAsync 的区别（L117–L119）。这不是 FL 方法的换皮。
- **信息边界写得精确，这是全文最扎实的技术细节。** §Two-Stage, Three-Layer Non-Random Selection 明确定义 $p^{\mathrm{obs}}$ 的历史集 $\mathcal{H}^{\mathrm{obs}}$（不含当前观测结果与标签）与 $q^{\mathrm{use}}$ 的历史集 $\mathcal{H}^{\mathrm{use}}$（可含已实现的注册状态，不含未来 $U$ 结果与当前更新向量），L940–L955 再把该边界固化为实现约束。
- **理论边界诚实，且证明是真做完的。** 补充材料附录 A 给出 Prop. 1–3、Thm. 1 与债务界的完整推导，其中 Prop. 2 的证明由 IPW 条件恒等式（$E[O_e/p_e]=1$、$E[U/q]=1$）、塔性质与加权簇弱大数律组成，逻辑闭合；附录 A.G 的 Proof-Obligation Summary 明确列出"不主张目标支持外识别、不主张对任意隐藏混淆稳健、不主张剪枝下精确无偏、不主张通用预测优势"。
- **统计流程规范，且如实报告负面结果。** 全部方法比较按 seed 配对；Wilcoxon + Holm 在预先声明的比较族内进行；under-served-block 检查明确预注册、只在验证集上看、结果是"no win"，并写进摘要（L88–L90）与结论（L2068）。
- **表述零过度声称。** 全文检索：`state-of-the-art` 0 次、`outperform` 0 次、`SOTA` 0 次、`first to` 0 次；`non-inferior` 11 次、`no-harm` 7 次、`pre-registered` 7 次、`not significant` 4 次。这种自我设限在投稿中是加分项。
- **附录提供了一项很少见的溯源审计。** 附录 E.D 用 774 个窗口的配对哈希证明：full RAVEN 与 w/o-Design 的机会/观测/可用更新/注册事件完全一致，差异只从设计权重/P2 支持层开始，排除"消融效应来自选择轨迹泄漏"。

### 弱点

```text
Weakness: 方法在任何用户可感知指标上都没有取得显著优势，主表结论只是"非劣"。
Evidence basis: main.tex Table III（L1739–L1759）。SensorScope 上 RAVEN-MCS (gated) 的
  RMSE_μ 7.9380 vs FedAvg 7.9389 / FedAU 7.9364 / ObsUse 7.9293；WorstGroupRMSE 8.6707 vs
  FedAvg 8.6716 / FedAU 8.6691 / ObsUse 8.6618。U-Air 上 RAVEN (gated) 1.1131/1.1703 vs
  FedAU 1.1128/1.1701、ObsUse 1.1120/1.1692。正文自述非劣区间为 TEST +0.48% 与 +0.44%
  （L1711），并明说 "we do not claim a Holm-significant win over FedAU"（表注 L1734）。
Reviewer deduction: 在 20 paired seeds 与 ~0.05 的标准差下，这些差异远小于噪声；论文唯一可
  主张的是"不比别人差"。对一篇以方法命名的 TMC 投稿，这不足以支撑贡献。
Required fix: 取得任一预测端点的显著优势（20 seeds 级 Holm 显著），或把论文重新定位为
  测量/协议贡献并同步弱化方法命名与标题。
```

```text
Weakness: 论文自己的 E4 消融证明其"获胜指标"（结构对齐）与预测指标脱钩。
Evidence basis: Table IV（L1861–L1888）。SensorScope 去掉 Design：Δ_group +1.237%（Holm 显著）
  而 RMSE_μ 仅 +0.005%；去掉 Use：四个端点全部不显著（+0.026/+0.026/+0.012/+0.012）；
  去掉 Debt：结构变化仅 0.0141%/0.0040%，预测 <0.001%。U-Air 去掉 Design 反而使
  RMSE_μ 改善 6.553% 而 Δ_group 恶化 6.943%。
Reviewer deduction: 论文的排序头条是 Δ_group/Δ_c–s，但该指标在论文自己的消融中不随预测端点
  移动，说明它与"预测器服务部署目标"解耦；而 Use（可用更新校正）作为三层之一，在最能体现
  其价值的 Complete-aligned 家族中没有任何独立作用。这两点合起来使"五组件耦合架构"的实证
  回报无法被验证。这是本稿最致命的证据，且完全来自稿件内部。
Required fix: 补一个"结构对齐 ↔ 预测端点"的关联实验（例如人为改变 ω̄_R 与 μ 的距离并观察
  RMSE_μ 是否单调响应）；否则需要从贡献陈述与 Algorithm 1 中裁掉无边际作用的模块。
```

```text
Weakness: Design 的启用规则在稿件内无法重建——只有定性描述与一个来源含混的数字。
Evidence basis: 全文检索提交包，没有任何一处给出 gating 的判定式。可用的只有：
  "Design is kept on SensorScope, where target support is compatible, and dropped on U-Air,
   where 25.5% of risk units have π^tar=0"（L1561–L1564）；§Discussion "Design is kept when
  target support is compatible and dropped when it is not"（L1965–L1966）；以及一个被否掉的
  候选方案 "A support-compatible mixture target was tested… and failed the SensorScope
  do-not-break rule"（L1566–L1568）。而 25.5% 的确切语义在提交包中始终是
  "risk units"（L212、L1413、L1909、L1977），没有任何附录把它定义为一个训练侧统计量。
Reviewer deduction: 这是稿件最核心的机制之一（摘要 L84–L90 用整整两句讲它，Contribution 2
  把它称为 "the practical realization of Contribution 2"），却无法从稿件重建：读者既不知道
  阈值、也不知道该统计量的分母与计算口径，更无法排除它是事后按结果选定的（稿件承认它是
  在观察到 U-Air 反转之后才选择的策略）。可复现性因此在该维度上归零。
Required fix: 在正文给出 gating 的显式判定式（统计量定义、分母、阈值、冻结时点），并说明
  该规则在任何 RMSE 结果产生之前就已固定；或把 Contribution 2 的措辞改为"Design 分支在
  SensorScope 上有效、在 U-Air 上失效的经验观察"，不再称其为可推广的 gate。
```

```text
Weakness: 主实验的"机会"是 always-on 协议构造而非移动机会，与论文动机存在代表性落差。
Evidence basis: L1536–L1540 定义 Complete-aligned 为"opportunity, observation, and
  usable-update selection are all active and non-random in the same direction"；§Evidence
  Scope L2006–L2007 明确 "Original SensorScope and U-Air traces are not claimed to contain
  mobile clients"；T-Drive 是唯一的真实移动机会，但 L1504–L1508 与 L1673–L1676 明确它
  "supplies a real-mobility opportunity replay, not a method ranking"，且 $O/U$ 为控制。
Reviewer deduction: 论文的第一句动机是"移动参与本质上是间歇的"，而承载全部方法排序的两个
  数据集用的是站点轨迹上的 always-on 协议机会。T-Drive 仅用于展示 TV 失配，不用于任何方法
  比较。因此"解决移动群智感知问题"这一宣称的生态效度（external validity）偏弱。
Required fix: 在主实验中至少部分使用间歇机会（哪怕是协议稀疏化），或把摘要与结论中的
  "mobile crowdsensing" 限定为"站点感知阵列 + 移动机会回放"的证据层级。
```

```text
Weakness: 强基线的改编自由度与"非劣"阈值的裁定权都在作者手里。
Evidence basis: L1544–L1556 明确 FedAU-Window、ObsUse-Window、TimeAlign-Agg 均为窗口化改编
  （"not an official reproduction"）。"非劣"被定义为预注册的 mean-relative +0.5% 规则
  （L1603–L1605）。而 ObsUse-Window 恰是"应用本论文的观测与可用更新校正、但不含 Design、
  P2 与 debt"（L1554–L1555）——即论文自身模块的一个子集。
Reviewer deduction: 一个由作者按目标方法拆解出来的对照（ObsUse-Window）与完整方法在主表上
  数值几乎相同（SensorScope 8.6618 vs 8.6707；U-Air 1.1692 vs 1.1703），这本身就是"完整
  方法未超过其自身子集"的强证据。此外 +0.5% 均值相对阈值的来源未被论证（为何是 0.5% 而非
  适应该数据集噪声水平的更小值），而它恰好是论文唯一的外部结论。
Required fix: 给出 +0.5% 阈值的事前论证（或改为基于噪声尺度的等效性检验）；补一版与官方
  FedAU 设定更接近的实现，并报告改编基线的超参搜索范围。
```

```text
Weakness: 可读性与版面：核心消融图的字号低于印刷可读下限。
Evidence basis: 对提交版 main.pdf 逐 span 解析：全文有 150 处文字小于 6pt。第 13 页（E4 表
  + Fig. 5）最严重，共 56 处，最小字号 3.71pt，出现在面板轴标注 "Δ_group"、"Δ_c–s" 与显著
  性星号处；第 12 页 23 处（最小 4.98pt，为 Table III 表头 Δ 下标）；第 11 页 22 处
  （最小 4.95pt，Fig. 3 的 TV 标注与 Fig. 2 的图例）。表格本身用 \scriptsize +
  \shortstack + \tabcolsep=1pt（L1737–L1738）。
Reviewer deduction: 3.7–5pt 的文字在印刷与屏幕上均难以辨读，而 Fig. 5 正是支撑"组件作用是
  端点相关而非单调"这一关键论断的图。表 III 的 Δ 指标未在表内注明定义与量纲。
Required fix: 重绘 Fig. 5（提高面板字号、减少面板内的数值标签）；Table III 表注补 Δ 指标
  定义；把消融表从 \tiny/\scriptsize 提升到 \footnotesize 并压缩列。
```

```text
Weakness: 复制与复现材料在稿件内的承诺偏软。
Evidence basis: §Data and Code Availability（L2085–L2092）:"Frozen selection traces, target
  maps, the 20 paired seeds, and the tabulated results in this paper are archived with the
  submission." 紧接着 "A complete public snapshot of the sealed training stack is not
  claimed at submission." 附录 E.C 还自述 P2 求解器只用了一个求解器复算，且 "a formal
  rerun was not authorized"（L2030–L2035）。
Reviewer deduction: 对一篇以"协议、目标构造、可行性约束"为核心贡献的稿件，训练栈快照与
  P2 求解器的交叉验证恰恰是审稿人最需要的东西，而两者都被明确排除在承诺之外。
Required fix: 至少给出可执行的训练入口与环境锁；补第二个求解器在完整窗口上的交叉验证。
```

---

## 7. 可能缺失的相关工作（Potentially Missing Related Work）

```text
Work: FedIPW / "Who Trains Matters: Federated Learning under Enrollment and Participation
  Selection Biases"（arXiv:2604.26604）
Status: searched（公开可检索；arXiv 与 ADS 均有条目）
Why relevant: 两阶段（enrollment → round participation）选择偏差下的 IPW，目标总体平均更新
Overlap: 术语与结构上最接近：两阶段选择 + IPW + 目标总体。差异在对象：FedIPW 在客户端
  名册上，本稿在 MCS 感知单元上，且本稿对齐的是 h(i) 上的公开度量。
Needed comparison: 不必作为 MCS 基线运行，但稿件应给出一段结构化的对象对照（谁在选择、
  选择什么单位、对齐什么量），而不是一句话带过。
```

```text
Work: FLOSS（Goetze et al., PACMI '25）
Status: searched
Why relevant: 客户端级 opt-out / straggler 的 IPW 聚合
Overlap: 与 $U$ 层（可用更新）语义相通，但对象仍是客户端名册
Needed comparison: 已是引文；建议明确说明本稿 U 层与 FLOSS 的 straggler 处理在估计量上的差异
```

```text
Work: FedCure（AAAI 2026）
Status: searched（作者已引用并明确排除）
Why relevant: 半异步 FL 的参与偏差缓解
Overlap: 与"更新侧可用性偏差"主题相邻
Needed comparison: 稿件已在 L1556 声明 "FedCure is not included"，属可接受的显式排除
```

---

## 8. 主张—证据审计（Claim-Evidence Audit）

| 主张 | 出处 | 提供的证据 | 强度 | 评审扣分 | 需要的修复 |
| --- | --- | --- | --- | --- | --- |
| 到达风险与部署目标风险在法则不同时不可互换 | 摘要；Prop. 1；Fig. 2 | NSW E2 的 $D_{\mathrm{aligned}}$ 显著为负（$p\approx5\times10^{-4}$） | adequate | 该命题本身接近线性泛函区分的同义反复；E2 的验证价值主要在于"两套权重下位移量不同" | 在 T-Drive 真实 $R$ 上复算同一统计量，使验证与动机中的"真实移动机会"对齐 |
| 理想逐层校正可恢复兼容目标质量 | 摘要；Prop. 2；附录 A.B | 完整证明：IPW 恒等式 + 塔性质 + 加权簇弱大数律 | strong as conditional math | 恢复的是"质量/组质量"，不是 $\mathcal{R}_\mu(\theta)$；论文已自述，但仍以 target-risk 命名全文 | 标题与关键词改为 target-mass 口径（与 Prop. 2 一致） |
| RAVEN 默认在结构对齐上优于 FedAvg | Table III；§RQ2 | SensorScope Δ_group 1.0139 vs 1.0558（−3.96%） | adequate | 该指标经 E4 证明不预测 RMSE（Design 使其改善 1.237% 而 RMSE 仅动 0.005%） | 建立 Δ ↔ RMSE 的关联实验，或更换为可感知指标 |
| RAVEN 默认在预测上不劣于强基线 | 摘要；Table III 表注；结论 | TEST 相对变化 +0.48%/+0.44%，在预注册 +0.5% 内 | weak | 结论只是"非劣"；且 ObsUse-Window（方法自身的子集）数值上更优；10 vs 20 种子切片未说明 | 给出 +0.5% 阈值的噪声学论证；统一用 20 种子均值表述 |
| Design 的启用是"目标支持兼容性"的实用实现 | 摘要；Contribution 2；§Discussion | 定性描述 + 25.5% + 被否掉的 mixture 目标；无判定式 | absent | 核心机制不可重建，且被承认是观察到 U-Air 反转之后选定的 | 给出显式判定式（统计量/分母/阈值/冻结时点），或降级为经验观察 |
| Use（可用更新校正）是必要的选择层 | Contribution 2；三层框架 | E4：Use 在四个端点上均不显著（两数据集 8 个端点全部不显著） | absent（对该层而言） | 论文自述 "does not establish the marginal indispensability of usable-update correction" | 从贡献陈述与算法中裁掉，或补一个 U 真正起作用的实验 |
| 目标债务在长期会计上有效 | §Long-Term Target Debt；E4 | 债务界（$\ell_1$ 失配 ≤ 2·Q_R/S_R）；E4 Debt 行 | adequate for accounting | 实测效应 0.002%–0.014%，论文自述"well below the 0.5% practical threshold" | 保持为会计项即可，勿列为贡献 |
| 真实出租车机会下存在同样的四块失配 | Fig. 3；§RQ1 | TV 0.142（T-Drive）vs 0.192/0.278（协议） | adequate | 仅证明机会分布失配，不提供任何方法层面的证据 | 明确写成"问题存在性证据"，勿靠近方法结论 |
| 无伤控制成立 | §RQ1；补充 A.A | E1 相对劣化 0.0599%，单侧 95% 上界 0.134% < 3% | adequate | 5 seeds，且作者自述 "does not establish RAVEN superiority" | 无需修改 |

---

## 9. 实验 / 基准 / 复现审计（Experiment / Benchmark / Reproducibility Audit）

- **基线**：FedAvg-Window、FedAsync-Window、TimeAlign-Agg、Local-Hàjek、TwoStage-Hàjek、FedAU-Window、ObsUse-Window，共 7 个。其中 3 个是作者自实现的窗口化改编（FedAU/ObsUse/TimeAlign），论文诚实标注；但改编基线的超参范围与调优预算未报告，"未调参"与"调过但未报告"在稿件内无法区分。
- **关键结构问题**：ObsUse-Window 被定义为"本论文的观测与可用更新校正，去掉 Design/P2/debt"（L1554–L1555）。它在两个数据集的四个端点上与完整方法数值几乎相同（SensorScope 8.6618/1.3062 vs 8.6707/1.2644；U-Air 1.1692/1.3235 vs 1.1703/1.2949）。这等于论文自己的表里承认：**完整方法没有超过它的自身子集**，只在 Δ 指标上不同。
- **消融**：E4 单因子移除五个组件，覆盖两个数据集四个端点。结论是"组件作用端点相关"：Design 在 SensorScope 有益、在 U-Air 有害；Obs 端点间符号相反；Use 全不显著；Inst 是权衡；Debt 一致但量级 <0.015%。
- **数据集**：SensorScope（55 站点）、U-Air（36 站点）、NSW-Traffic（43 站点）用于 E2；T-Drive（9994 栅格、5837 出租车）用于机会回放。**没有任何数据集包含移动客户端**（L2006–L2007 自述），也没有任何实测的可用更新层。
- **指标**：$\mathrm{RMSE}_\mu$、WorstGroupRMSE、Tail_RMSE（预测类）与 $\Delta_{\mathrm{group}}$、$\Delta_{c\text{-}s}$（结构类）。前两者是用户可感知的；后两者与前两者的关系未经建立。
- **统计严谨度**：paired seeds（E1 用 5，E2–E4 用 20）；Wilcoxon + Holm 在预声明族内；数值并列阈值 $10^{-12}$；所有表格报 mean ± std。**亮点**：under-served-block 检查明确预注册、只在验证集评、结果如实报为负，并写进摘要。**缺口**：正文的 +0.48%/+0.44% 用的是 TEST 切片，而 Table III 是 20 种子均值，两个口径混用未加说明。
- **运行时与实现细节**：主文只用一段（L2030–L2035）交代 P2 求解与求解器交叉验证（CLARABEL 与 SCS 在 $\ell_1$ 上匹配到 $10^{-8}$，最差窗口分配差 0.0056），并自述"a formal rerun was not authorized"。对一篇以 P2 为核心机制的论文，这属于偏薄的实现披露。
- **产物与可复现性**：§Availability 承诺归档 selection traces / target maps / seeds / tabulated results，同时明确不承诺训练栈公开快照。稿件内**未给出 gating 判定式**，因此即使有 traces，读者也无法复现"在哪一分支上运行了哪个方法"。
- **本机能独立核对的项**：页数（main 16 / supplemental 8）、引文完整性（[1]–[48] 无缺号）、图件字号分布（150 处 <6pt，最小 3.71pt）、全文过度声称词频（0 处 SOTA/outperform）、摘要词数（177）。

---

## 10. 多审稿人小组（Multi-Reviewer Panel）

```text
Reviewer: Best-justified（TMC MCS/FL，同情视角）
Expertise: 移动群智感知系统与联邦学习
Likely score: 6/10
Confidence: 5
Main positive signal: 问题原生且动机链条完整；两层三阶的合法信息边界写得比同类工作精确；
  表述零过度声称；预注册检查如实报负；E4 的 774 窗口溯源审计罕见地认真
Main negative signal: 方法在预测端点没有一次胜利；ObsUse 子集与完整方法数值相同
Evidence basis: L121–L152；L447–L520；Table III；Table IV；附录 E.D
Fatal concern if any: none（但"从不获胜"叠加"子集持平"已接近致命）
Score-change condition: 任一预测端点的 20 种子 Holm 显著优势
```

```text
Reviewer: Critical（TMC 系统怀疑视角）
Expertise: 系统评估方法学
Likely score: 3/10
Confidence: 5
Main positive signal: 披露完整，没有一处夸大
Main negative signal: gating 规则不可重建且承认事后选定；Use/Debt 空转；Δ 指标与预测脱钩；
  主实验是 always-on 协议机会、非移动客户端；ObsUse 子集持平；+0.5% 阈值无学理论证
Evidence basis: Table III/IV；L1561–L1568；L1960–L1995；L2006–L2007
Fatal concern if any: gating 不可重建 + 无预测胜利 + 子集持平，三者合起来构成方法贡献不成立
Score-change condition: 显式 gate 规则 + 任一预测端点的显著优势
```

```text
Reviewer: Method / soundness
Expertise: 因果推断与调查抽样
Likely score: 5/10（Soundness 3）
Confidence: 5
Main positive signal: 三层合法历史边界精确；Prop. 2 证明闭合；Prop. 3 与 Thm. 1 条件写清
Main negative signal: Prop. 1 平凡；Prop. 2 是标准 Hàjek 比相合性；P2 是强凸 QP 的标准结论；
  三层估计量恢复的是质量，不是风险；gating 与 A5 的关系只有定性说明
Evidence basis: 附录 A.A–A.G；L1236–L1437
Fatal concern if any: none
Score-change condition: 给出"折叠单层 IPW 会失败"的判决性反例，或把 gating 变为可证的支持规则
```

```text
Reviewer: Evidence / experiment
Expertise: 实证统计与联邦学习评估
Likely score: 3/10（Evidence 2）
Confidence: 5
Main positive signal: paired seeds、Wilcoxon+Holm、预注册检查、表格报 mean±std；表述与数字一致
Main negative signal: 无任何显著优势；TEST 与 ALL20 口径混用；ObsUse 子集持平；10 种子与
  20 种子切片混用；+0.5% 阈值无依据；E4 的 Use/Debt 空转
Evidence basis: Table III（L1739–L1759）；L1700–L1716；Table IV
Fatal concern if any: none 单独致命，但 Evidence 维度已到 2/5
Score-change condition: 20 种子级显著优势；或完成 Δ ↔ 预测端点关联实验
```

```text
Reviewer: Novelty / positioning
Expertise: 参与偏差联邦学习
Likely score: 5/10（Originality 3）
Confidence: 4
Main positive signal: 感知单元级 R/O/U + h(i) 公开度量 + 有限窗口校准的组合在公开文献中未见
  直接对应；FedIPW/FLOSS/FedAU 都在客户端名册层面
Main negative signal: 每块技术砖都是既有工具；组合式创新未在实证上兑现；与 FedIPW 的对象切分
  只用一段话处理
Evidence basis: §Related Work L256–L413；L230–L232 自述
Fatal concern if any: none（但标题用 "Target-Risk-Calibrated" 而证明只到质量恢复，构成口径不一致）
Score-change condition: 结构化对象对照表 + 折叠式单层 IPW 的失败反例
```

```text
Reviewer: Writing / clarity
Expertise: TMC 可读性
Likely score: 5/10（Clarity 3）
Confidence: 5
Main positive signal: 摘要 177 词、结构清晰；RQ1–RQ3 的组织与理论链对应；图表均有角色说明
Main negative signal: 8 组核心符号先于主表出现；Table III 的 Δ 指标未注明定义；Fig. 5 面板
  字号 3.71pt；gating 只用 "gated" 一词带过；TEST 与 20 种子两个口径并存
Evidence basis: 全文 span 字号解析（150 处 <6pt，p13 最小 3.71pt）；L1739–L1739 表头；
  L1561–L1568
Fatal concern if any: none
Score-change condition: 术语表 + 表注重绘 + Fig. 5 增量重绘
```

```text
Reviewer: Ethics / reproducibility
Expertise: 产物与许可
Likely score: 5/10（Reproducibility 3）
Confidence: 5
Main positive signal: 四个公开数据集均给出获取地址；隐私成本有专门讨论；避免了不必要的原始
  数据集中化
Main negative signal: 核心 gating 规则不可重建；训练栈快照明确不承诺；P2 求解器只有单次交叉
  验证且自述 "a formal rerun was not authorized"
Evidence basis: L2085–L2092；L2030–L2035；全文 gating 检索
Fatal concern if any: none
Score-change condition: 给出判定式 + 可执行训练入口 + 完整窗口的第二求解器验证
```

```text
Reviewer: Domain application（MCS 部署）
Expertise: 城市感知部署
Likely score: 4/10（Significance 2）
Confidence: 5
Main positive signal: 用了真实出租车轨迹机会；协议机会的构造过程交代清楚；明确指出原始
  SensorScope/U-Air 不含移动客户端
Main negative signal: 主排序实验用 always-on 协议机会、站点并非移动客户端；没有实测的观测
  缺失层与网络/更新层；没有端到端部署证据；论文第一句动机是"移动参与本质间歇"，而证据层
  达不到该动机
Evidence basis: L1536–L1540；L2006–L2007；Table III
Fatal concern if any: none
Score-change condition: 在间歇机会上完成方法排序，或补实测 O/U
```

```text
Reviewer: Evidence/ablation
Expertise: 组件隔离
Likely score: 4/10
Confidence: 5
Main positive signal: E4 五组件单因子移除 + Holm 家族 + 774 窗口哈希溯源，隔离做得认真
Main negative signal: Use/Debt 空转；Design 使"获胜指标"改善而预测不动；ObsUse 子集与完整
  方法持平；Inst-Cal 与完整方法在附录数值上不可区分
Evidence basis: Table IV；L1903–L1949；L1718–L1723
Fatal concern if any: none
Score-change condition: 一个在该族中真正承重的组件级实验
```

```text
Reviewer: Reproducibility（artifact）
Expertise: 发布工程
Likely score: 4/10
Confidence: 5
Main positive signal: 承诺归档 traces/targets/seeds/tabulated results；图件全部为向量 PDF 且
  附带绘图源 CSV
Main negative signal: 无训练栈快照；无 gating 判定式；P2 求解器无完整交叉验证；未提供代码入口
Evidence basis: L2085–L2092；投稿包文件清单
Fatal concern if any: none
Score-change condition: 可执行入口 + 环境锁 + gating 定义
```

```text
Reviewer: Novice advocate
Expertise: 首遍 TMC 阅读
Likely score: 5/10（accessibility 3）
Confidence: 5
Main positive signal: 摘要把问题、方法、主要负面结果与范围都写了；RQ1–RQ3 提供了明确的阅读
  路径
Main negative signal: 符号密度高；"gated" 一开始就出现但从未定义；Table III 有同一数据集下
  两个 RAVEN 行（full Design vs gated）而无行内标注；+0.5% 的裁定含义需读两遍
Evidence basis: L71–L91；L1561–L1568；Table III
Fatal concern if any: none
Score-change condition: 一页术语与判定规则表
```

```text
Agreement:
  问题表述是 TMC 原生的，且两层三阶的合法信息边界写得精确。
  表述上没有一处过度声称；预注册检查如实报负。
  主表结论严格限于"非劣"，且论文自己说明了这一点。
  Use 与 Debt 在该实验族中没有独立作用，论文自己也承认。
Disagreement:
  这份稿件应被读作"测量/协议论文"还是"方法论文"。若读作前者，问题是"生态效度不足"；
  若读作后者，问题是"方法从未在任何可感知指标上获胜，且未超过自身子集"。
  分歧不在事实，而在论文自称的贡献类型（标题与命名都指向方法）。
Decisive positive axis:
  一个被明确定义、诚实测量、并附带负面结果的 MCS 选择偏差分析框架。
Decisive negative axis:
  所提方法在其自己选择的指标上从未取得显著优势，其"获胜指标"经其自身消融证明与预测脱钩，
  而控制该方法的启用规则在稿件中无法重建。
Unresolved evidence:
  gating 判定式；+0.5% 阈值依据；Δ 指标与预测端点的关联；20 种子均值口径的统一；
  训练栈可执行性；间歇机会下的方法排序。
AC stance:
  拒稿（Overall 4/10）。这不是"表述问题"类的拒稿——稿件的表述质量高于均值；
  这是贡献证据不足的拒稿。
```

---

## 11. 关注点清单（Concerns Table）

| ID | 严重度 | 关注点 | 证据基础 | 受影响维度 | 修复类别 | 需要的行动 | 归属技能 | 分数变动条件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | major | 方法在任何用户可感知指标上均无显著优势，主结论仅为"非劣" | Table III（L1739–L1759）；L1711–L1716 | Evidence；Significance | experiment | 取得任一预测端点的 20 种子 Holm 显著优势 | ccf-experiment-designer | 达成则 Evidence 2→4、Overall 4→6 |
| B2 | major | E4 证明获胜指标（Δ）与预测端点脱钩；Use/Debt 无边际作用 | Table IV（L1861–L1888）：Design 使 Δ_group +1.237% 而 RMSE_μ +0.005%；Use 八端点全不显著 | Evidence；Soundness | experiment | 补 Δ ↔ RMSE 关联实验，或裁掉无作用模块 | ccf-experiment-designer | 完成后 Evidence 2→3、Overall +1 |
| B3 | major | Design 的启用规则在稿件内不可重建，且承认事后选定 | 全文检索无判定式；L1561–L1568、L1965–L1966 仅定性；25.5% 语义在包内始终是 "risk units" | Soundness；Reproducibility | method/soundness | 给出统计量/分母/阈值/冻结时点的显式判定式，或降级为经验观察 | ccf-experiment-designer / ccf-paper-writer | 给出判定式后 Soundness +1 |
| B4 | major | 主实验用 always-on 协议机会、数据集不含移动客户端，与"移动参与间歇"的动机落差大 | L1536–L1540；L2006–L2007；T-Drive 明确不用于方法排序（L1504–L1508） | Significance | experiment | 在间歇机会上完成方法排序，或限定宣称的证据层级 | ccf-experiment-designer | 达成则 Significance 2→3 |
| B5 | moderate | ObsUse-Window（方法自身子集）在数值上不劣于完整方法 | Table III：SensorScope 8.6618/1.3062 vs 8.6707/1.2644；U-Air 1.1692/1.3235 vs 1.1703/1.2949 | Evidence；Significance | experiment | 说明完整方法相对其子集的增量价值，或重构方法叙事 | ccf-experiment-designer | 解释清楚后 Overall +0.5 |
| B6 | moderate | "+0.5% 均值相对"阈值无噪声学依据，却是唯一外部结论 | L1603–L1608；摘要 L86–L87 | Evidence；Soundness | experiment | 给出阈值的事前论证，或改为基于标准差的等效性检验 | ccf-experiment-designer | 论证后 Evidence +0.5 |
| B7 | moderate | TEST 切片与 20 种子均值两个口径混用 | L1711 用 TEST +0.48%/+0.44%；Table III 表注为 20 种子均值 | Evidence；Clarity | writing | 统一为 20 种子均值表述，或同时给出两个切片 | ccf-paper-writer | Clarity +0.5 |
| B8 | moderate | Fig. 5 与 Table III 存在低于印刷可读下限的字号 | 程序解析：p13 最小 3.71pt（Δ_group/Δ_c–s 轴标注、显著性星号），p13 共 56 处 <6pt，p12 共 23 处 <6pt | Clarity | writing | 重绘 Fig. 5；Table III 表注补 Δ 定义并提升字号 | ccf-visual-composer | Clarity +0.5 |
| B9 | moderate | 训练栈无公开快照；P2 求解器仅单次交叉验证 | L2085–L2092 "not claimed at submission"；L2030–L2035 "a formal rerun was not authorized" | Reproducibility | reproducibility | 提供可执行训练入口与环境锁；补完整窗口的第二求解器验证 | ccf-submission-checker | Reproducibility 3→4 |
| B10 | moderate | 标题/关键词用 "Target-Risk-Calibrated"，而 Prop. 2 只到质量恢复 | L56、L94 vs Prop. 2 陈述（L1266–L1335）与自述边界 L1413–L1417 | Clarity；Novelty | writing | 改为 target-mass 口径，或补上质量→风险的桥接论证 | ccf-paper-writer | 改口径后 Clarity +0.5 |
| B11 | minor | 标题页同时含匿名占位符与真实姓名/单位/基金号/邮箱 | main.tex L58–L61；supplemental 标题页 | 政策/格式 | venue-mismatch | 按该刊当期评审模式统一匿名或统一具名 | user | 不构成学术分变动 |
| B12 | minor | 16 页对 12 页发表长度的压缩压力 | main.pdf 16 页；投稿包 README 自述规则 | 格式 | compression | 压缩 4 页或接受 MOPC | ccf-paper-writer | 不影响科学分 |
| B13 | minor | 相关工作中的对象切分只用一段话处理（尤其对 FedIPW） | L327–L413；检索确认 FedIPW 为最接近工作 | Novelty | related-work | 增加结构化对象对照（选择主体/选择单位/对齐量） | ccf-paper-writer | Novelty +0.5 |
| B14 | minor | 轨迹数据的再分发与去标识化边界未说明 | §Availability 未涉及；§Privacy 只涉协变量 | Ethics/Limitations | ethics/limitations | 补一句轨迹治理范围 | ccf-paper-writer | Ethics 保持 4–5 |

---

## 12. AC / 元评审（AC / Meta-Review）

**审稿人共识。** 这是一篇在表述与披露上明显优于均值的稿件，其问题不是"不诚实"或"写得乱"，而是**所提方法没有兑现**。三点共识：其一，问题表述是 TMC 原生的，两层三阶的合法信息边界定义精确；其二，主表的结论严格限于"不比强基线差"，论文自己反复说明这一点，没有任何一处夸大；其三，论文自己的 E4 消融显示其"获胜指标"（结构对齐 Δ）与预测端点脱钩，Use 与 Debt 无边际作用——这是最致命的证据，且完全来自稿件内部。

**审稿人分歧。** 分歧在"该按哪种贡献类型评"。若按测量/协议论文评，本稿的核心缺陷是生态效度（协议机会 always-on、数据集非移动客户端），属于可以靠补充实验缓解的问题；若按方法论文评，缺陷是根本性的：方法从未在用户可感知指标上获胜，并且没有超过它自己的一个子集（ObsUse-Window）。由于标题（"Target-Risk-Calibrated…"）、贡献命名（Contribution 1–3）与算法结构（Algorithm 1）都把本稿定位为方法论文，AC 按后者定档。

**决定性接受轴。** 一个被明确定义、诚实测量、并附带负面结果的 MCS 选择偏差分析框架——如果期刊愿意接收 negative/measurement 类工作，这份稿件是可发表的。

**决定性拒稿轴。** 方法贡献的三重失效：① 在任何预测端点无显著优势；② 其获胜指标经自身消融证明与预测脱钩；③ 控制该方法启用的核心规则（gating）在稿件中无法重建，且作者承认它是观察到 U-Air 反转之后才选择的。再加上离题式的外在效度问题（always-on 协议机会、无移动客户端、无实测 U），本文无法作为 TMC 方法论文接收。

**AC 立场：拒稿（Overall 4/10，明确拒稿）。** 与"表述类拒稿"不同，本稿的表述质量高于均值；拒稿原因是贡献证据不足。若作者补充 ① 任一预测端点的显著优势 或 ② gating 的显式可证规则 + 间歇机会上的方法排序，本稿有重投为可接收工作的潜力。

**讨论风险。** (1) 审稿人会追问 gating 的判定式——这是全文最脆弱的一点，且作者无法用"预注册"辩护，因为稿件本身承认它是事后选的；(2) 审稿人会注意到 ObsUse-Window 是方法的子集却在数值上不差，从而质疑完整架构的必要性；(3) 审稿人会把标题里的 "Target-Risk-Calibrated" 与 Prop. 2 只到质量恢复并置，质疑口径；(4) 审稿人可能读不清 Fig. 5（3.71pt）；(5) 若本刊当期为双盲，标题页的真实姓名与基金信息会触发匿名合规问题。

---

## 13. 定量评分（Quantitative Scores）

### Scorecard

| 维度 | 分数 (1-5) | 置信 (1-5) | 证据基础 | 扣分 / 分数变动条件 |
|:---|:---:|:---:|:---|:---|
| Novelty 新颖性 | 3 | 4 | §Related Work L256–L413；L230–L232 自述"新颖性不是 IPW/Hàjek 本身"；公开检索未见直接对应工作 | 扣分：组合式创新（IPW + Hàjek + 强凸校准 + 债务）未在实证上兑现；与最接近工作 FedIPW 的对象切分只用一段话。修至 4：结构化对象对照 + "折叠单层 IPW 失败"的反例；修至 5：实证独特性 |
| Soundness 可靠性 | 3 | 5 | 附录 A.A–A.G（完整证明）；Prop. 2（L1266–L1335）；Prop. 3 与 Thm. 1；gating 仅定性（L1561–L1568） | 扣分：gating 是核心机制却不可重建且事后选定；Prop. 1 平凡、Prop. 2 为标准 Hàjek 比相合性；三层估计量恢复质量而非风险。修至 4：给出 gating 判定式或把 A5 条件与 gating 的关系推进为可证规则 |
| Evidence 证据 | 2 | 5 | Table III（L1739–L1759）；Table IV（L1861–L1888）；L1711–L1716；Table V（under-served） | 扣分：无任一预测端点的显著优势；获胜指标经 E4 证明与预测脱钩；Use/Debt 八端点全不显著；ObsUse 子集数值持平；TEST 与 20 种子口径混用；+0.5% 阈值无依据。修至 3：完成 Δ ↔ 预测关联实验并裁掉空转模块；修至 4：任一预测端点的 20 种子 Holm 显著优势 |
| Significance 重要性 | 2 | 5 | Table III；L1536–L1540；L2006–L2007；T-Drive 不用于排序（L1504–L1508） | 扣分：主排序用 always-on 协议机会且数据集不含移动客户端；无实测 O/U；无端到端证据；结论只是"不劣"。修至 3：间歇机会上的方法排序；修至 4：实测移动层上的优势 |
| Clarity 清晰度 | 3 | 5 | 摘要 177 词；RQ1–RQ3 结构；Table III 表头与 Fig. 5 字号；gating 表述 | 扣分：150 处 <6pt 文字（p13 最小 3.71pt）；Δ 指标未在表内注明定义；gating 未定义即使用；同一数据集下两个 RAVEN 行无行内标注。修至 4：术语/判定规则表 + Fig. 5 重绘 + 表注补定义 |
| Reproducibility 可复现 | 3 | 5 | L2085–L2092；L2030–L2035；附录 E.C | 扣分：训练栈快照明确不承诺；gating 判定式缺失；P2 求解器仅单次交叉验证；无代码入口。修至 4：可执行入口 + 环境锁 + 判定式；修至 5：mismatches=0 级的哈希校验与完整交叉验证 |
| Ethics / Limitations 伦理与局限 | 4 | 5 | §Mobility/Identification/Privacy（L1997–L2021）；§Evidence Scope（L2023–L2043）；附录 A.G 的义务清单 | 扣分：轨迹数据治理边界未说明；其余披露充分且诚实。修至 5：补轨迹治理一句 |

**Overall:** 4/10 ｜ **Scholarly Confidence:** 5/5

**Recommendation:** reject
**Verdict:** 之所以是 4 而不是 5–6（borderline）：决定性负面证据全部来自稿件内部——方法从未在可感知指标上获胜、其获胜指标经自身消融证明与预测脱钩、控制启用的核心规则不可重建且事后选定、控制组之一是方法自身子集且数值持平。之所以不是 2–3（strong reject）：问题表述有新意、信息边界精确、理论边界诚实、统计流程规范、零过度声称，且 E4 的溯源审计与预注册检查体现了高于均值的科研纪律。

```text
Quality: 3
Clarity: 3
Significance: 2
Originality: 3
Soundness: 3
Evidence: 2
Reproducibility: 3
Ethics / Limitations: 4
Overall: 4/10
Confidence: 5/5
Score-change conditions:
  4 -> 5：给出 gating 的显式判定式，且完成 Δ_group/Δ_c–s ↔ RMSE_μ 的关联实验
  4 -> 6：在冻结 20 种子主表上取得任一预测端点的 Holm 显著优势（且不改口径）
  4 -> 7：在间歇/真实移动机会上完成方法排序并取得优势，同时补实测可用更新层
  4 -> 3：若作者在回复中把"非劣"表述为优势，或把 Title 的 target-risk 口径当真
  4 -> 2：若发现 25.5% 与 gating 的赋值确由测试结果反推（当前稿件已接近这一描述）
```

### 写作 / 展示评分卡（full 模式）

| 维度 | 权重 | 分数 (1-5) | 置信 | 证据基础 | 具体修复 |
| --- | ---: | ---: | ---: | --- | --- |
| 故事线与动机 | 10 | 4 | 5 | L121–L152 的动机链条完整且原生 | 无 |
| 贡献展示 | 10 | 2 | 5 | 三条贡献（L186–L228）中，Contribution 2 的实用实现（gating）不可重建，Contribution 3 的组件（Use/Debt）经 E4 证明空转 | 按 E4 事实重写 Contribution 2/3 的作用范围 |
| 段落逻辑 | 10 | 4 | 5 | RQ1–RQ3 与理论链一一对应；每小节以 Answer 收束 | 无 |
| 主张—证据对齐 | 12 | 4 | 5 | 表述零过度声称；但"gated 默认实现 Contribution 2"这一主张无证据支撑 | 该句降级为经验观察 |
| 方法可读性 | 9 | 3 | 5 | 8 组核心符号先于主表；gating 未定义即使用 | 一页术语 + 判定规则表 |
| 实验叙述 | 9 | 4 | 5 | 表格先于解释；每个 RQ 有明确答案句 | 统一 TEST/20 种子口径 |
| 相关工作定位 | 8 | 3 | 4 | FedIPW/FLOSS/FedCure 均已引用，但对象切分只有一段话 | 增加结构化对象对照表 |
| 术语与记号一致性 | 8 | 3 | 5 | 标题 target-risk vs 证明 target-mass；"RAVEN-MCS (gated)" 与 "RAVEN (full Design)" 同行不同名 | 统一口径与行名 |
| 散文纪律 | 10 | 4 | 5 | 无 em dash 滥用；句式稳定 | 无 |
| LaTeX 与格式纪律 | 6 | 3 | 5 | 16 页；Table III 用 \scriptsize+\shortstack+\tabcolsep=1pt；Fig. 5 最小 3.71pt | 重绘 Fig. 5；提升表字号；压缩 4 页 |
| 面向审稿人的风险 | 8 | 3 | 5 | 负面结果已如实呈现（正面）；但 gating 不可重建与 Fig. 5 字号是可预期的审稿人攻击点（负面） | 给出判定式并重绘图 |
| **写作总分** | 100 | **3.42** | 5 | 加权均值 | 风险档：**中高** |

---

## 14. 给作者的问题（Questions For Authors）

1. Design 的启用规则能否以一行判定式给出：统计量是什么、分母是什么、阈值取多少、在哪个时点冻结？稿件的摘要与 Contribution 2 用两句话描述它，但全文没有任何一处可以让读者重建该规则；而 §Discussion 承认"在 U-Air 上反转之后才选择关闭"。如果该规则是事后选定的，它对第三个数据集还成立吗？
2. 25.5% 这个数字的确切定义是什么？稿件在四处（L212、L1413、L1909、L1977）称其为 "risk units with zero target mass"，但包内没有任何附录给出它的分母。它是训练单元的占比、窗口的占比，还是事件出现的占比？
3. Table III 中 SensorScope 的 RAVEN-MCS (gated) 与 FedAU/ObsUse 的差异（7.9380 vs 7.9364/7.9293）在 20 paired seeds、标准差约 0.05 的条件下如何解读？"+0.5% 规则"为何取 0.5%，而不是与噪声尺度挂钩的等效性界？
4. 正文用 TEST 切片报 +0.48%/+0.44%（L1711），而 Table III 报 20 种子均值。为何排序叙述用切片？20 种子下的对应值是多少？
5. ObsUse-Window 被定义为"本论文的观测与可用更新校正，去掉 Design、P2 与 debt"（L1554–L1555）。它在两个数据集的预测端点上与完整方法数值持平（SensorScope 8.6618 vs 8.6707；U-Air 1.1692 vs 1.1703）。完整方法相对这一子集的增量价值体现在哪个指标上？
6. E4 显示去掉 Design 使 SensorScope 的 $\Delta_{\mathrm{group}}$ 恶化 1.237%（Holm 显著），而 $\mathrm{RMSE}_\mu$ 只变化 0.005%；同时 Use 在八个端点上全部不显著，Debt 的效应小于 0.015%。请给出证据说明这些组件在预测意义上的必要性；否则为什么 TMC 读者应当关心 $\Delta$ 指标？
7. 标题写 "Target-Risk-Calibrated"，而 Prop. 2 的结论是目标质量/组质量恢复（附录 A.B 亦如此）。质量恢复与 $\mathcal{R}_\mu(\theta)$ 之间的桥接论证在哪里？
8. §Availability 明确不承诺训练栈的公开快照，而 P2 是全文的核心机制之一。能否提供可执行的训练入口、环境锁与第二个求解器在完整窗口上的交叉验证？

---

## 15. 分数修订条件（Score Revision Criteria）

```text
提升分数需要:
  1. 给出 gating 的显式判定式（统计量、分母、阈值、冻结时点），并附一个第三方数据集上的
     验证，证明它对结果无泄漏。→ Soundness 3→4、B3 关闭、Overall 4→5。
  2. 完成"结构对齐 ↔ 预测端点"的关联实验（人为改变 ω̄_R 与 μ 的距离，观察 RMSE_μ 是否
     单调响应），并据此裁掉或保留 Use/Debt。→ Evidence 2→3、Overall +1。
  3. 在冻结的 20 种子主表上取得任一预测端点的 Holm 显著优势。→ Evidence 3→4、
     Overall →6。
  4. 在间歇机会（或真实移动数据）上完成方法排序并取得优势，同时补实测可用更新层。
     → Significance 2→3、Overall →7。
  5. 提供可执行训练入口与环境锁，并把 Fig. 5 重绘到 ≥7pt。→ Reproducibility 3→4、
     Clarity 3→4。
降低分数会由以下情况触发:
  - 在回复中把"非劣"表述为"优于"或"达到 SOTA"。→ Overall →3。
  - 被证实 25.5% 与 gating 的赋值由测试集结果反推。→ Overall →2。
  - 把 TEST 切片数字当作 20 种子结论陈述。→ Overall →3。
投稿前不太可能改变的问题:
  主实验协议机会为 always-on 且数据集不含移动客户端（需新数据或新协议）；无实测 O/U；
  20 seeds 不是独立城市；标题页匿名口径取决于该刊当期评审模式。
```

---

## 16. 行动计划与 CCFA 交接（Action Plan And CCFA Handoffs）

```text
Priority: P0
Action: 给出 Design gating 的显式判定式，并把 Contribution 2 中"practical realization of
        the same reconstruction"的措辞降级为经验观察（在规则未给出之前）
Owner skill: ccf-paper-writer（若只是写清规则）/ ccf-experiment-designer（若要重定义规则）
Input needed: gating 统计量的原始定义与冻结记录
Expected output: 正文内可重建的一行规则
Handoff required: yes
```

```text
Priority: P0
Action: 明确论文的贡献类型：若坚持方法论文，必须补入任一预测端点的显著优势；若转向测量/
        协议论文，则同步修改标题、摘要与 Contribution 1–3 的措辞
Owner skill: ccf-paper-writer + ccf-experiment-designer
Input needed: 作者对贡献类型的决定
Expected output: 口径与证据一致的稿件
Handoff required: yes
```

```text
Priority: P1
Action: 补"结构对齐 ↔ 预测端点"关联实验；据结果裁掉或保留 Use/Debt
Owner skill: ccf-experiment-designer
Input needed: 训练授权
Expected output: 一张新的冻结表
Handoff required: yes
```

```text
Priority: P1
Action: 重绘 Fig. 5（面板字号 ≥7pt，减少面板内数值标签）；Table III 表注补 Δ 指标定义；
        把消融表字号从 \scriptsize 提升
Owner skill: ccf-visual-composer
Input needed: 现有绘图源码与数据
Expected output: 重绘后的向量图与表格
Handoff required: yes
```

```text
Priority: P1
Action: 统一 TEST 与 20 种子口径；论证 +0.5% 阈值的来源或改用基于标准差的等效性检验
Owner skill: ccf-paper-writer
Input needed: 20 种子相对差分布
Expected output: 统一口径的排序叙述
Handoff required: yes
```

```text
Priority: P2
Action: 补相关工作的结构化对象对照（选择主体 / 选择单位 / 对齐量），特别是与 FedIPW 的差异
Owner skill: ccf-paper-writer
Input needed: 无
Expected output: 一张对照表或一段结构化论述
Handoff required: yes if the user asks
```

```text
Priority: P2
Action: 确认该刊当期评审模式，统一标题页匿名口径；压缩至 12 页或准备 MOPC
Owner skill: user / ccf-submission-checker
Input needed: TMC ScholarOne 当期规则
Expected output: 合规的上传包
Handoff required: yes
```

```text
Checks run:
  desk checks（篇幅/选题/最低质量/匿名/注入/伦理）
  PDF 层程序化审计：main 16 页、supplemental 8 页；引文 [1]–[48] 无缺号、无未替换宏；
    彩色文字 70 处（全部为图中标注，无红色修订痕迹）
  版面可读性审计：逐 span 字号分布（150 处 <6pt；最小 3.71pt 于 p13 Fig. 5）
  主张语言审计：SOTA/outperform/state-of-the-art/first-to 各 0 次
  理论独立复核：附录 A.A–A.G 的 Prop. 1–3、Thm. 1、债务界推导逐条阅读
  claim-evidence 对照：摘要/引言/结论的每条主张对回 Table III/IV/V 与附录
  公开相关检索：3 组公开安全检索式（IPW+FL + MCS 选择偏差；两阶段 IPW 目标总体；稀疏 MCS
    补全的分布偏移）
Checks skipped:
  任何 GPU 重训练；任何内部复现包校验；任何历史评审对比（盲审纪律要求排除）
Unresolved risks:
  gating 判定式缺失；+0.5% 阈值依据；Δ 指标与预测端点的关系；训练栈不可执行；
  标题页匿名口径；Fig. 5 与 Table III 的字号
```

**可交接的下一个 CCFA 技能**

- `ccf-experiment-designer`：预测端点显著优势、Δ ↔ 预测关联实验、间歇机会排序
- `ccf-paper-writer`：gating 规则表述、贡献类型口径统一、TEST/20 种子统一、相关工作对照
- `ccf-visual-composer`：Fig. 5 重绘、Table III 重排
- `ccf-submission-checker`：匿名口径、页数规则、可执行训练入口与环境锁
- `ccf-rebuttal-writer`：若需把 B1–B14 摄入 revision ledger（本报告不写 rebuttal 文本）
