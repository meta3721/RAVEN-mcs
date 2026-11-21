# 执行指令：依据现有主张统一RAVEN-MCS正文表述

请使用 `ccf-paper-writer`，依据下列全文检查记录直接修改规范论文；先应用 `ccf-humanization`，完成后用 `ccf-integrity-auditor` 核对主张与证据。请交付修改后的源码、PDF和简短报告，不要只返回建议。

本轮不是重新设计主张。最新版摘要、贡献列表及结论已经基本一致；需要修复的是正文中残留的定义范围、实验角色、理想与实现对象、主方法与历史诊断身份等局部表述。**已经准确的句子保留，不为了制造修改量而重写全文。**

## 1. 规范入口与工作起点

论文目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

主要修改 `main.tex`；只有必要的交叉表述需要同步时，才对 `appendix.tex`、`supplemental.tex`作局部文字修改。保持现有章节结构、核心表图位置和标签。

读取当前全文及以下记录：

- `C:/Cursor/raven.mcs/ccf-review-report/PAPER_CORE_ADVANTAGE_REVISION_REPORT.md`
- `C:/Users/szr/Desktop/record/1/ccfa-review-reports/favorable-claim-coverage-review.md`
- `C:/Cursor/raven.mcs/ccf-review-report/PAPER_CLAIM_EVIDENCE_MAP.md`
- `C:/Cursor/raven.mcs/ccf-review-report/PAPER_EVIDENCE_PENDING_ITEMS.md`

以下行号来自2026-10-18 01:16的main.tex。执行时按标签、原句和章节定位，采用当前工作树，不覆盖用户或其他AI后续修改；历史报告有追加修复时采用最新状态。

## 2. 保持不变的主张框架

- 问题：部署目标、R/O/U选择后的到达分布、当前窗口可行组成是不同对象。
- 方法：用各阶段结果发生前的合法信息重建目标质量参考，再在caps/ESS等约束下校准为可执行客户端权重。
- 理论：条件性理想目标矩恢复、精确凸程序唯一解、固定状态下的参考与决策扰动界；长期对齐还依赖债务增长条件。
- 应用：完整RAVEN在City Scanner两套协议中，平均组失配为已报告方法最低，相对组端点最佳对照TwoStage-Hájek下降25.8%/23.3%。这是描述性均值之比，不是预测收益或新增显著性结论。
- 机制：同支持对照分离Count→Uniform、校正参考及可行投影的作用。投影比较器、Inst-Cal、默认完整RAVEN、κ=1000敏感性规则身份不同。
- 诊断：组成方向、权重自由度、可调整目标质量不同；特定floor目标变体保留组收益。诊断不是已验证的收益预测器或自动选择规则。

主线继续突出City Scanner的完整方法组优势，并让站点机制实验解释它所涉及的参考与校准问题；不新增“预测全面领先”“所有组件必要”或“无条件长期公平”等主张。

## 3. 优先修复：两处明确的范围不一致

### A. VII-A指标定义：WorstGroupRMSE不能统称四个UTC块

定位：main.tex:1227–1228，原文：
`WorstGroupRMSE is the maximum of four UTC-block scores ...; Tail RMSE uses frozen blocks 2 and 3 ...`

问题：这句话作为全局定义过宽。正文City Scanner表II明确采用四个空间象限；附录NSW-Traffic四区域协议采用四个坐标区域；站点主比较和T-Drive才有相应UTC块定义。

修改要求：

- 总定义写为：对该协议预先冻结的群体分别评分并取最大值；群体内部按该协议评分口径归一化。
- 紧凑区分站点/T-Drive的UTC块与City Scanner/NSW四区域协议的空间群体；以各协议表注及附录定义为准。
- 将Tail RMSE的固定UTC块2和3明确限定于报告该端点的站点协议，不套到City Scanner空间群体上。
- 将SensorScope物理单位、U-Air/Traffic原标准化尺度与City Scanner各块训练z-score口径写清适用范围，避免用“main RMSE entries”概括所有主表。
- 不改任何群体、评分权重、数值或原始指标计算。此次只修正文定义与既有协议的一致性。

### B. VII-A种子说明：不能再用“主要比较20种子”笼统覆盖City Scanner

定位：main.tex:1211–1214，原文：
`Principal comparisons use 20 paired seeds ... T-Drive plus three supplemental rankings use ten.`

问题：City Scanner现为主要应用证据，两个块各10个配对种子；六臂是10条轨迹、每条3模型种子。原概括容易让读者把所有主要结果理解为20种子，并保留了旧的“附录排名”位置描述。

修改要求：明确受控站点主要对照20配对种子；City Scanner两个五方法块各10配对种子；T-Drive10；balanced control5。其他条件按各表说明，六臂以10轨迹×3模型种子单独说明，不能称30独立轨迹或与两个排名块合并。

保留种子不是独立城市的解释。无需为每个诊断建立长清单，但不能继续使用已过时的展示位置概括。

## 4. 同步实验角色和全文主线

### C. 数据表角色与实验开场

定位：Table I（`tab:datasets`），main.tex:1182、1184、1190、1192；VII开场main.tex:1135–1136。

- SensorScope/U-Air角色目前仍写`main comparison; ablation`，而City Scanner只写`hybrid`。将站点角色明确为受控机制/Design/消融比较；City Scanner明确为应用比较，同时保留real R、measured O、controlled U的协议身份。
- City Scanner P2显示名可改为`City Scanner Pilot 2`，避免与校准程序(P2)混淆。只改表中名称和必要的自然语言，不改引用标签、方法或协议。
- 表中NSW的`risk interchangeability`可统一为风险语义比较，避免与证明“可互换”的结论混淆。
- VII开场沿用“应用组对齐→同支持归因→预测/成本及有限支持诊断”的职责。`deployment consequences`可收紧为实际测量的预测和运行时间结果，避免暗示已经验证操作者效用或部署决策规则。

这些是叙述角色修订，不是将全部站点比较降为无效实验，也不是删去T-Drive及其他不利排名。数据表只改Role和必要显示名称，全部数字保留。

## 5. 方法和理论：收紧少量容易被扩大解读的表达

以下多为措辞精确化，不要夸大为已证实的数学错误。

### D. 参考构造与理想恢复的对象

定位：引言main.tex:133–135；III-C:366–371；IV开场:498–500；IV-C:656–664。

原句包括`reconstruct the target mass represented by delivered updates`、`restores relative corrected mass between usable clients`。

要求：描述实际算法时使用“估计的、稳定化的目标质量参考”及“把局部归一化移除的质量尺度纳入服务器参考”的准确含义。`restores`不应被理解成估计和截断之后仍在每个窗口精确恢复真实总体质量。理想正确比率下的总体矩恢复留在对应命题及其假设内。

不要给每个`corrected`机械加`estimated`，不要给每段新增一条否定句；在对象首次定义处交代清楚，此后统一术语。保留参考β、可行决策α、组成Mα之间的区别。

### E. 局部位移归一化不等于训练路径不变

定位：main.tex:624–627，原句：
`The displacement divides out the local learning rate and step count, preserving the server update scale.`

将其明确为去除显式学习率与步数乘因子的单位/尺度归一化。不要让读者理解为多步局部训练等于单步真实梯度，或改变本地学习率、步数后聚合方向和预测表现保持不变。不改归一化公式或算法。

### F. 图1与NoDesign的表述

定位：main.tex:152–160；T-Drive表注main.tex:1382。

- 图1开头`RAVEN-MCS aligns ... with a public deployment target`可改为直接描述“构造部署目标参考并在有限支持上校准”的过程，避免把框架功能写成对每个窗口精确对齐的保证。
- `RAVEN-NoDesign ... is not target-mass reconstruction`宜具体写成“省略机会到部署目标的比率校正，其他观测/可用性校正和校准仍保留”。
- 保持NoDesign作为不同变体的身份：其结果不能被当作Design-on完整目标重建的成功证据；也不能让读者误以为NoDesign完全没有任何校正。
- 图注与正文对Design窗口前固定、Gate仅诊断的说明保持一致。

### G. 风险命题与精确优化的表述

VI-B标题`Target Risk Is Not Arrival Risk`可保留；若改写，应强调评价测度及响应一般不同，而非任一固定预测器下风险值必定不同。现有“固定预测器也可能相等”的句子和命题不要删除。

P2唯一解指精确凸程序；求解器的数值近似和最优性核验另有实证状态。现有正文已基本准确，保留即可，不必到处新增数值免责声明，更不能把已有解改称通过全部认证的精确oracle。

债务记录质量欠配，不扩写为实际服务公平或预测公平已得到保证；长期界继续保留次线性条件。不要改公式、假设、证明或定理结论。

## 6. 覆盖部分：辅助诊断与历史候选身份分开

定位：V-F标题main.tex:845；VI-F标题main.tex:1097；VII-G覆盖段main.tex:1772–1775。

目前正文已经指出Gate是诊断、保证有条件，VII-G也明确`Design_t=Gate_t`候选；不是要求再宣布存在方法定义冲突。剩余问题是标题及衔接容易让它看起来是当前主方法的另一项主要安全保证。

- V-F标题可收紧为“Aggregate Opportunity-Coverage Diagnostic”，VI-F可突出稳定区间条件下的界。使用标准术语，保留数学对象和标签。
- VII-G用一句明确现有.959/.750来自另行评价的coverage-controlled候选，其Design/Gate耦合不同于窗口前配置Design的当前方法。不得重命名或追认成当前主方法的验证结果。
- 保留交换性、冻结预测器和历史分数等条件；CERTIFIED不等于假设已被证明。不得把.959概括成全面95%有效，也不得移除U-Air .750单元。
- 不改变Gate职责、不重接代码、不补覆盖实验。诊断不是新增贡献，保持篇幅紧凑。

## 7. 实验解释：保留优势，同时消除身份或量词漂移

### H. 清理旧项目代号和含混总结

- IV-C main.tex:665–666和V-C:777–778都用`W1 compares...`，VII内也有对应对照。将方法段改为自然的“同支持比较/机制对照”，保留一次清晰交叉引用，删除重复预告；不改已有来源路径或必要复现标识。
- 图`fig:w1_design_gate`中`with a flat RMSE`可改为平均RMSE变化很小的描述，不改称等价、无伤害或无预测代价。当前Holm结论和图的实际均值保留。
- INT-R、T-Drive、NSW四区域结果继续表述为其各自协议的检验，不能用于普遍宣称机会校正有效，也不能因不利而删除。

### I. 已经对齐的核心结果优先保留

以下段落已基本符合主张，只在发现具体漂移时微调，不进行无意义重写：

- City Scanner双面板、最低平均组失配及25.8%/23.3%的均值之比口径；预测最佳者及相对代价继续可见。
- 投影相对直接参考1.188/1.399 pp、相对Uniform .768/.286 pp、独立Design .922 pp。不同对照不相加，结构读出不嫁接成训练预测收益。
- Uniform解释68.96%/83.07%的来源归因；完整P2相对投影的端点和耗时取舍。
- floor的101.9%仅为特定目标支持变体的组改善保留率；floor同时改变边际，预测区间仍不确定。
- 183个K=8子集与4.651%描述几何调整能力，不是收益检测或自动停止规则。
- 集中式开发骨干、Adam、概率真值敏感性分别保留身份；不把47.01%/10.16%、oracle或独立敏感性变体归给默认RAVEN。

## 8. 全文最后检查与修改边界

按摘要→引言→相关工作→模型→方法→理论→实验→结论逐段核对。除以上已定位问题外，只有发现**具体原句、对应主张及明确不一致**时才增加修改。区分“实际错误”“容易歧义”“可保留的准确句子”，不能仅凭关键词批量替换或制造过度宣称。

保持：

- 核心优势仍突出；不把一次局部校准写成精确实现公共目标，不把组失配减少写成预测或公平性必然改善。
- Full RAVEN、NoDesign、投影、Inst-Cal、强债务变体及历史coverage候选各自准确。
- 理论、结构指标和预测结果的对象及保证范围不混用。
- 普通措辞按已授权范围直接处理；不得虚构用例、操作者、阈值或决策规则来消除科学缺口。
- 不运行训练、推理、重评分、回放、求解或新增统计检验；不修改数据、种子、参数、表体数值、图数据、方法代码或历史失败记录。
- 不新增文献检索或书目；相关工作已准确的最近邻边界保持。
- 正文不超过14页，补充不超过正文实际页数，沿用当前含参考文献的口径。不缩字体/边距，不删除核心证据，不为填满页面扩写。
- 只对必要位置做简洁修订，避免再次铺开重复负面总结。已知不利事实保留，推测性局限及工作日志不写进论文。

## 9. 交付及验收

直接在规范目录完成源码修改，编译正文和补充材料；核对交叉引用、页数以及修改页的表图布局。保留现有City Scanner正文展示和此前评分/术语修复。

输出简短报告：
`C:/Cursor/raven.mcs/ccf-review-report/PAPER_BODY_CLAIM_ALIGNMENT_REPORT.md`

报告按A–I列出实际修改位置、原意与修订后的适用范围；没有修改的准确段落说明保留理由即可。列出最终PDF页数及编译状态，明确本轮没有新增实验。若发现不能通过文字解决的科学问题，单独记录，不通过改名、删数据或虚构保证解决。

完成标准：通读正文时，数据角色、样本数、指标定义、方法身份和理论范围均支持既定主张；读者不会被旧设置引向“全面预测领先”“全部条件下精确目标恢复”或“历史Gate候选就是当前完整方法”的错误理解。
