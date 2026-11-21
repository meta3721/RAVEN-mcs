# INTRODUCTION_BACKGROUND_STATUS_GAP_METHOD_REPORT

日期：2026-10-30。完成 ccf-paper-writer 局部重组和 ccf-humanization 表述核验；按最新指令执行，实验保持暂停。

## 交付与范围

- 已原位修改 [main.tex](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex>)，成功编译 [正文PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf>) 和 [补充PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf>)，分别 **14页、14页**。
- 修改范围严格限于 Introduction 与 Related Work 两个 section 命令之间；范围外源码按字节与本轮备份相同。appendix.tex、supplemental.tex、reference.bib 也按字节不变；图表、公式、算法、实验数据与阈值未修改。书目内容未改，正文首次引文顺序改变使自动引用编号相应更新。
- 上一步仅生成临时候选，未替换规范 main.tex；本轮开始时规范稿与上一步编辑前备份按字节完全一致。因此没有用旧文件覆盖当前稿，先前图表迁移及其他修复全部保留；旧候选不构成现行引言。

## 词数与结构

W0 = **481**；W1 = **481**。采用指令给出的 introduction_word_count 函数，不按 TeX 空格数计数；排除 section 标题、命令、label/cite/ref 参数和行内数学，连字符术语按一个词元计，编号贡献计入总数。函数及冻结记录见 tmp/intro_four_part_20261030.py 与 tmp/intro_background_status_gap_20261030/baseline.json。

- 第一部分背景：49词元，3句，5篇不同引用。
- 第二部分现状：63词元，5句，6篇不同引用。
- 第三部分问题：45词元，3句，6篇不同引用。
- 前三段合计 **157词元，占32.64%**。
- 第四部分方法及贡献：**324词元，占67.36%**；方法及执行链154词元、9句，理论38词元、1句，实验49词元、1句，过渡及贡献83词元、4句；三项条目分别27、26、27词元，首词均为 **We**。

四部分按“背景—现状—问题—方法及贡献”顺序出现。第一方法句使用指定的 To address the above challenges, we propose RAVEN-MCS … a novel framework that … 结构；末尾为 enumerate 三项贡献，无额外文章安排。

## 各段引用及语义核验

- 第1段（5篇）：`ganti2011mobile` → [1], `wang2025evolutionary` → [2], `xu2025rethinking` → [3], `liu2025nonaligned` → [4], `mcmahan2017communication` → [5]。
- 第2段（6篇）：`wang2024fewshot` → [6], `liu2025nonaligned` → [4], `xie2019asynchronous` → [7], `wang2024lightweight` → [8], `morishita2026who` → [9], `listozec2024overcoming` → [10]。
- 第3段（6篇）：`wang2024lightweight` → [8], `sun2025debiasing` → [11], `chen2026fedcure` → [12], `xie2019asynchronous` → [7], `morishita2026who` → [9], `listozec2024overcoming` → [10]。
- 第四部分各段及贡献没有新增外部引文：所述方法与理论、结果来自本文现行 IV–VII 节；不是将外部论文当作 RAVEN 效果证据。

引用按事实分布，以下原文只用于确认研究对象和机制，不将作者对缺口的推理伪装为这些论文的实测结论：

- `ganti2011mobile`：分布式移动载体进行环境及交通感知，依据[作者公开原文](https://www.ece.stonybrook.edu/~fanye/papers/IEEE-Com-Mag-11.pdf)；不引申为本文覆盖或预测保证。
- `wang2025evolutionary`：不均匀稀疏观测和时空相关性下的缺测推断，依据[作者公开论文](https://cis.temple.edu/~wu/research/publications/Publication_files/A_New_Data_Completion_Perspective_on_Sparse_CrowdSensing_Spatiotemporal_Evolutionary_Inference_Approach.pdf)第一页摘要。
- `xu2025rethinking`：稀疏补全与下游任务及成本间的关系，依据[IEEE原文页](https://ieeexplore.ieee.org/abstract/document/10845194)和[作者稿](https://micxyb.github.io/papers/Rethinking_the_Effect_of_Sparse_Data_Completion_on_Sparse_Mobile_Crowdsensing_Tasks.pdf)；这里只作为补全动机，不宣称任何补全都改善下游任务。
- `liu2025nonaligned`：稀疏记录及非对齐多尺度信息整合，直接读取此前保存的原始PDF抽取文本第一页：C:/Users/szr/Desktop/record/1/literature-search-20261029-raven-references/sources/nonaligned.txt；未将尺度整合写成部署质量校准。
- `mcmahan2017communication`：共享本地计算的模型更新、保留分布式训练记录，依据[PMLR原文页](https://proceedings.mlr.press/v54/mcmahan17a.html)摘要。
- `wang2024fewshot`：用少量目标数据调整辅助数据预训练模型，依据[INFOCOM官方摘要](https://infocom.info/infocom24/day/3/track/Track%20A)中 CDFMC 说明；与非对齐多尺度路线并列概括，不称两者都采用同一种迁移算法。
- `xie2019asynchronous`：异步更新和陈旧模型处理，依据[作者v5摘要](https://arxiv.org/abs/1903.03934v5)；保留已核定 OPT 2020 书目身份与旧键，未将其同步化或作为感知记录选择纠偏工作。
- `wang2024lightweight`：依据参与历史估计聚合权重，见[ICLR正式摘要](https://proceedings.iclr.cc/paper_files/paper/2024/hash/03a9a9c1e15850439653bb971a4ad4b3-Abstract-Conference.html)；不说其未研究非均匀参与。
- `sun2025debiasing`：相关、非均匀参与的偏差及去偏算法，见[ICLR正式摘要](https://proceedings.iclr.cc/paper_files/paper/2025/hash/464917b6103e074e1f9df7a2bf3bf6ba-Abstract-Conference.html)。
- `chen2026fedcure`：通过联盟构建和参与感知调度缓解半异步参与偏差，见[AAAI原文页](https://ojs.aaai.org/index.php/AAAI/article/view/39176)摘要；第三段使用 participation-bias mitigation 的宽泛准确措辞，不把其写成感知单元IPW。
- `morishita2026who`：分别处理 enrollment/participation，并提供有限信息下的总体摘要校准，见[作者原文](https://arxiv.org/html/2604.26604v1)第3–6节；明确承认其已有校准能力。
- `listozec2024overcoming`：凸组合目标标签匹配及样本ESS正则，亦研究目标在客户端凸包外时的行为，见[作者原文](https://arxiv.org/html/2411.03799v2)第3节；没有将其描述成“不做目标匹配/不处理不可达目标”。

第三段前两句分别把文献放在其确实涉及的“参与/更新”“总体校准/目标匹配”短语之后；“仍须连接原子选择与有约束窗口执行”是本文场景的对象区分及作者推论，不是对所有现有方法无效的判断。

未新增书目。正文实际引用45篇（此前46篇）；`li2024robust`从本轮精简背景中移除，但bib条目保留，不将其当作存在问题的引用。2025实际引用仍15篇，2026仍7篇，近期引用数量未回退。引用显示保持逐项编号，未恢复区间压缩。访问受限的 SC-AFL 页面未用于本轮新增论断；第三段使用已直接核对的 FedAsync 支撑异步聚合对象，原相关工作中的 SC-AFL 引用未改。

## 方法、理论与实验对应

- R/O/U的顺序及预结果边界对应III-B、IV-A至IV-D；局部归一化与客户端间质量区别对应IV-B/IV-C。明确可用性校正先缩放质量，再归一化参考，不让参考权重直接等同可执行权重。
- P2参考锚与组组成项作用于不同空间，对应V-A/V-C；债务依据组成、聚合后再更新，对应V-B/V-D；Design预配置与独立诊断Gate对应V-D/V-E。未更换完整目标函数或方法。
- 理论句对应VI-B Proposition 2、VI-C Theorem 1、VI-D Proposition 3：理想恢复保留正确比率、兼容支持、顺序识别与cluster regularity，唯一性限定凸校准及正参考锚，扰动性质限定固定窗口状态。没有宣称无条件长期对齐；贡献中的 accumulated under-service 是记账机制，不是长期收敛结论。
- 实验句对应VII-B和当前Table II；仅在本报告定位，不在引言引用表号。完整RAVEN在两协议各自五方法中的平均组失配最低，25.8%/23.3%仍指相对TwoStage-Hájek的**种子均值之比**，不是平均成对降幅、百分点或预测收益；没有从四舍五入后的表格重算。两协议均真实机会、受控交付，观测分别受控和实测。保留不同协议及其他预测排名于原实验段，未将其扩成真实端到端部署。
- 第三项贡献把 matched-support comparisons 与 separate geometry diagnostics 分开，不将不同支持集或开发轨迹混算。

## 编译与页面检查

最终构建为单进程、低优先级、依次 LaTeX/BibTeX/LaTeX；8次工具调用退出码均0，main/supplemental辅助引用状态稳定。无未定义引用、重复标签、Overfull；BibTeX无warning。既有epstopdf shell-escape禁用提示保留，未为此开启shell命令。

正文14页，补充14页；引言横跨第1–2页，编号贡献位于第2页。已阅读最终正文第1、2页，图1第3页及书目第13–14页和补充第14页预览，未见截断、重叠、缺字或超宽。Section III起于第2页，图1位于第3页，Section IV起于第4页，仍在第三节范围内；Evaluation起于第7页。所有表/图/定理的label编号与备份一致，引言无图表环境或图表编号引用，所有表格编号引用继续限定Evaluation之后或补充材料。

本地ccf-humanization检查无error/warning、em dash为0；唯一advisory为477个可见词计数下一个分号的密度2.1/千词，人工核对后保留：该分号连接债务记账与滞后正则状态两类职责。检查器词数不是本任务约定词数，**W0/W1一律使用上述481词元口径**。

一次编译请求因自动审批超时未启动；依系统提示重试一次后成功。没有遗留编译阻断。未训练、推理、采集、回放、求解或统计重算。

## 回退

备份目录：[introduction_background_status_gap_20261030_161205](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/introduction_background_status_gap_20261030_161205>)。包含修改前源码、正文/补充PDF、书目、辅助文件、最终main.tex.diff及本轮核验记录。旧图一备份及前轮回退材料未覆盖。

若之后没有其他修改，可从该目录还原main.tex并重新编译；若已有后续编辑，只恢复Introduction两节标记之间的文本，按main.tex.diff合并，不能用旧main.tex覆盖后来工作。补充源码从未修改；引用顺序回退后需重建bbl/aux和两份PDF。

未解决项：本轮规定的结构、比例、同词数、引用及编译要求均已完成；不因此声称新增研究证据或完成其他投稿要求。

## 最终英文引言（引用编号与本次PDF一致）

Mobile crowdsensing (MCS) uses distributed mobile sensors to observe urban and environmental fields for applications including traffic and air-quality monitoring [1]. Uneven sampling leaves spatial and temporal gaps, motivating data completion for wider coverage and downstream sensing tasks [2][3][4]. Federated learning shares model updates while keeping the underlying sensing records distributed [5].

Existing work spans completion representations, distributed training, and target-aware aggregation. Transfer and multiscale methods exploit related sensing tasks and non-aligned observations [4][6]. Although asynchronous learning accommodates irregular updates [7], participation correction adjusts unequal client contributions [8]. FedIPW corrects enrollment and participation with population-summary calibration [9], while FedPALS matches known target label mixtures with convex aggregation and sample-ESS regularization [10]. These approaches address representation, update timing, and population composition.

Participation-bias mitigation [8][11][12] and asynchronous aggregation [7] concern updates, whereas sensing selection also acts within client records. Population calibration [9] and target matching [10] do not automatically make corrected references executable under window-specific caps and effective-support constraints. Statistical reconstruction therefore needs connecting to constrained execution and accumulated target service.

To address the above challenges, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), a novel framework that reconstructs sensing-unit target references and calibrates executable client weights within finite windows. Specifically, opportunity (R), observation (O), and update usability (U) select records and updates sequentially. Lagged opportunity ratios and observation propensities estimated without current responses supply correction weights for normalized local training and client reference mass. Pre-outcome usability correction rescales client masses before reference normalization, retaining relative mass removed from local training. P2 calibrates this reference under weight caps and minimum effective support, coordinating client-weight fidelity with deployment-group composition. Reweighting cannot create missing sensing support or ensure exact target matching. Debt records group under-service across windows; lagged variance and staleness proxies regularize decisions without inspecting current update vectors. Aggregation precedes debt and history updates, with debt computed from aggregate group composition. Design is configured before opening and fixed within each window, while coverage Gate remains diagnostic.

Our theoretical analysis establishes ideal pooled target-moment recovery under correct ratios, compatible support, sequential identification, and cluster regularity, together with unique feasible calibration under convexity and a positive reference anchor, and reference-perturbation stability at a fixed window state. Experimental results show that full RAVEN achieves the lowest mean group mismatch among five methods in two City Scanner protocols with real opportunities and controlled delivery, with reductions of 25.8% and 23.3% relative to TwoStage-Hájek by ratios of seed means, using controlled and measured observation, respectively.

Our contributions follow.

1. We formulate deployment mass and sequential selection over atomic sensing units, with information boundaries connecting within-client correction to the between-client reference and supporting ideal pooled target-moment recovery.

2. We develop constrained window calibration linking reference fidelity, group composition, and accumulated under-service, with fixed-state perturbation analysis separating reference errors from limitations imposed by available support.

3. We evaluate group alignment and prediction under two City Scanner protocols, using matched-support comparisons and separate geometry diagnostics to distinguish weighting mechanisms from limitations of available support.
