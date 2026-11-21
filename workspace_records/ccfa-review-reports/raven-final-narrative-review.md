# RAVEN-MCS：导师要求与最终学术叙事对照审查

审查日期：2026-10-30。模式：写作审查，仅评估，不修改论文、不恢复实验、不重新给出投稿评分。

## 审查对象与结论

- 导师文档：[2026-10-11打磨论文.docx](C:/Users/szr/Documents/xwechat_files/wxid_6u3gb5i5cvyq22_ceae/msg/file/2026-10/2026-10-11打磨论文.docx)，重点对照第 119–156、399–416 个段落，以及本轮提供的四张截图。
- 当前正文：[main.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)，文件修改时间 2026-10-30 17:11；[正文 PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)，14 页。
- 当前附录：[appendix.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex)，文件修改时间 2026-10-30 16:59；[补充 PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)，14 页。
- 页码均为本轮读取的 PDF 文件页码；源文件行号随后续修改而变化。

当前稿不需要因为这些写作要求整体重写。问题集中在附录中的内部编号、核查过程和历史方案叙述，以及实验分析中重复的范围声明。另有三处会影响科学含义的措辞错误，应优先于语气润色修复。

导师要求的适用重点是：让读者看到最终问题、机制、证明和结果，去掉内部修补及筛选历史。实际比较排序、统计区间和理论适用条件仍应准确呈现；把这些事实写得集中、简洁，比把它们删掉更符合最终论文叙事。

## 一、优先修正三处科学含义不准确的表达

### 1. 附表把截断“触发比例”写成“未触发比例”

位置：补充 PDF 第 11 页，Table XXV；[appendix.tex:1477](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1477)。解释段在源文件 1504–1511 行，补充第 9–10 页。

原表行名：

- `q_min floor inactive`：5.22% / 5.18%。
- `d_max ceiling inactive`：24.22% / 23.75%。

但解释段明确说，前一组是概率低于 floor 的比例，后一组是倒数超过 ceiling 的比例，均表示稳定化被触发。表名与正文含义相反。

处理建议：先以统计字段定义核实，再统一为“floor activation rate”“ceiling activation rate”等准确名称，并明确分母为 observed client-windows。保留原数值，不要为了适配现有行名直接用 100% 相减。

严重程度：高；这是结果语义错误，不是负面语气问题。后续责任：ccf-integrity-auditor 核实字段，ccf-paper-writer 统一文字。

### 2. “A5 holds”超过了实际已核验的条件范围

位置：补充 PDF 第 9–10 页；[appendix.tex:1487](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1487)、[appendix.tex:1539](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1539)。正文对 A5 的定义见 [main.tex:829](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:829)。

原文标题为 `A5 holds.`，随后给出正机会/观测/可用性边际与正分母。然而 A5 还包括理想参考与实际参考共享 active support、M、C；附录后文又说，因存储状态缺 active-set lists，这些仍作为比较假设。

处理建议：标题和结论只覆盖已检查的 positivity 与正质量条件。另用一句交代共享状态是比较的给定条件。不能把局部数值检查说成完整验证 A5，也不应声称本轮已通过该假设。

严重程度：高；措辞扩大了验证范围。后续责任：ccf-integrity-auditor / ccf-paper-writer。

### 3. A6a 被误写成稳定化误差为零的必要条件

位置：补充 PDF 第 9 页；[appendix.tex:1438](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1438)。

原文：`epsilon_stab,r = 0 also needs A6a.`

正文命题却明确说明 A6a 是充分条件，归一化抵消失真时不是必要条件；见正文第 7 页，[main.tex:1002](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1002)，附录命题重述也有相同说明。

处理建议：统一充分性与必要性的方向；以正文命题实际陈述为准。不能简单删除 A6a，也不能把包含误差项的扰动界改成无误差保证。

严重程度：高；正文与附录存在逻辑冲突。后续责任：ccf-paper-writer，必要时由 ccf-integrity-auditor 检查一致性。

## 二、与截图要求直接冲突的内部叙述

### 4. 内部实验代号和脚本名仍出现在附录

位置一：补充 PDF 第 9 页；[appendix.tex:1447](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1447)。

原文包含 `build_full_runner`、`run_e3_real`、`E1-R2 weight-safety calibration`、`E2 traffic runner`。这段在解释“哪个 runner 默认 a_max=20，哪个实验用了 40”，仍是内部配置排错记录。

建议：正文式陈述该组实验实际使用的参数及所属实验设置。若不同实验参数不同，以实际章节/表格名称区分；脚本入口与内部代号留在复现材料。不要只删除不同参数的事实。

位置二：补充 PDF 第 12 页；[appendix.tex:1729](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1729)。

`fedavg_window`、`raven_wo_design`、`raven_ctrl` 等代码键，应统一为表中正式名称，如 FedAvg、RAVEN-NoDesign、RAVEN-control、RAVEN-floor。1164 个键、812 个零值以及 floor 构造属于方法细节，应保留。

位置三：补充 PDF 第 14 页；[appendix.tex:1948](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1948)。

`OF-v1`、`OF-no-Q-stop`、`GAP20-fixed-reference` 仍带开发版本/检查点命名。应按机制定义自然名称，区分滚动参考、有无停止债务项、固定参考和定时关闭。对应关系留在复现材料，公式和对比结果保留。

严重程度：中；直接违反导师“不使用内部实验编号”的要求。后续责任：ccf-paper-writer。

### 5. 多处标题仍把科学分析包装为内部审计

可定位的例子：

- 补充第 6 页，Table XII：`Local-Hajek provenance audit.`，源文件 847 行。
- 补充第 6 页，Table XV：`Numerical feasibility audit of warning-affected P2 allocations.`，源文件 968 行。
- 同表列名 `Frozen result`，源文件 974 行。
- 补充第 8 页，小节 `Provenance of the w/o-Design Endpoint Trade-off`，源文件 1312 行。
- 补充第 9 页，Appendix H：`Support-Hypothesis Audit for A5, A6a, and A6b`，源文件 1432 行。
- 补充第 10 页，Appendix I：`Coverage-Stress Audit of the Candidate Gate`，源文件 1546 行。
- 正文第 11–12 页，`774-window U-Air audit`、`support audit`、`audited active windows`，见源文件 1625、1649、1667 行。

处理建议：标题写研究对象与分析内容，如局部权重抵消、数值可行性、支持条件、覆盖压力敏感性。段落直接报告实验设计、结果和解释。`Frozen result` 应呈现为测量量或结果，而不是冻结状态。严禁全局替换 `audit` 后原样保留核查日志式段落。

严重程度：中；集中清理这一组，最能改善“像审计报告”的观感。后续责任：ccf-paper-writer，ccf-humanization 作为辅助。

### 6. 版本历史与当前方法身份仍混在一起

位置：正文第 13 页，[main.tex:1753](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1753)；补充第 10、12 页，[appendix.tex:1549](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1549)、[appendix.tex:1594](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1594)。

原文使用 `historical coverage-controlled candidate`、`Historical coverage candidate`、`historical candidate`，并给出 Design=Gate 的候选结果。

问题：时间上的“历史版本”不能代替机制定义，读者容易把候选变体、诊断模块和最终 RAVEN 混淆。

建议：若保留此组证据，作为明确定义的“覆盖控制变体”或相关诊断比较介绍，按机制命名，清楚区分 Design=Gate 与主方法的预配置 Design。无需讲开发历史。已有 0.959 总体覆盖率和 U-Air 的 0.750 子组结果若继续支撑覆盖分析，就应按相同口径保留。不能删除身份区别后将其结果归到最终方法。

严重程度：中；涉及最终方法身份，应先统一对象再润色。后续责任：ccf-paper-writer。

### 7. 反修补叙述与作者内部评价仍未清完

例子：

- 补充第 5 页：`Complete-counteracting does not establish the proposed directional event.`，源文件 811 行。`proposed directional event` 没有在这里给读者清楚的科学对象，更像对内部假设的裁决。
- 补充第 6 页：`does not move the main-comparison or worst-group headlines`，源文件 962 行。`headlines` 应落到具体端点或排序是否改变。
- 补充第 6 页：`Point-level optimality checks do not all pass; endpoint agreement is not certification.`，源文件 997 行。需说明什么最优性残差/准则没有满足，端点误差达到什么量级；不能只写核验的通过/失败。
- 补充第 8 页：`not selection-trace leakage`，源文件 1322 行。直接说明两臂共享 R/O/U 和注册事件，差异来自 Design 引起的正质量支持变化即可；哈希一致性可留复现记录。
- 补充第 10 页：`The consequence for the theory is the one recorded in the main text.`，源文件 1526 行。直接陈述非零稳定化误差及其适用形式。

处理原则：结果、诊断量和科学含义进入论文；修改经过、核验判决与作者对标题效果的评价移出论文。数值可行性、实际最优性差距若影响解释，仍需保留准确说明。

严重程度：中。后续责任：ccf-paper-writer。

## 三、防御性措辞、结构与可读性

### 8. 有些限制语句有科学意义，但位置重复、叙事靠后

需要集中处理的例子：

- 引言第 1 页，在方法流程中插入 `Reweighting cannot create missing sensing support or ensure exact target matching.`，见 [main.tex:102](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:102)。它打断重构—校准—债务的解释，可将范围融入有限支持下的校准目标，在几何分析处展开。
- 正文第 5–6 页，`Inactive clipping alone does not establish these conditions`、`The catalogue check ... does not establish the assumptions below`、`Inactive stabilization alone does not establish correct ratios`，见源文件 595、800、820 行。其含义可通过一次清楚的假设定义表达，避免连续进行否定式解释。
- 正文第 8–10 页，`It is not a non-inferiority proof`、`miss the declared ... criterion`、`do not establish prediction superiority`，见源文件 1220、1282、1476 行。涉及不同实验时不是同一句话，但应把检验类型与阈值在设置中统一定义，结果段集中呈现效应、区间和排序，不再反复评论“未证明什么”。
- 正文第 10 页，`It does not validate a transferred station lookup.`，见源文件 1416 行。设置已经说明使用本地四区域目标图，应突出该设置本身。
- 正文第 13 页结论，`prediction rankings remain protocol-dependent`，见源文件 1770 行。实验中已解释，可压缩结论中的再次告诫，让结论更多收束已建立的连接与核心证据。

不能删掉的对应事实：六臂比较的 2% 非劣上界为 3.83/4.14/8.15%；主方法与简单投影的端点/运行时间比较；U-Air 的 Design 排序翻转；固定状态与共享支持条件；债务次线性条件。它们会改变读者能从结果推出的结论。

严重程度：中；建议合并，不宜按否定词数量机械删除。后续责任：ccf-paper-writer。

### 9. “terminal-window correction”仍像内部修复标签，含义不完整

位置：正文 PDF 第 11 页；[main.tex:1502](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1502)。

原文：`Prediction scores use saved model parameters with the terminal-window correction.`

问题：没有在相邻处解释修正的是窗口索引、参数时点还是评分规则；“correction”将读者带入修复历史，也不足以复现最终评分。

建议：核对实际评分定义后，直接说明使用哪个时点的模型、怎样处理末窗口，以及比较各臂是否采用同一规则；必要细节放实验设置或复现说明。不能只删掉 correction 一词。本轮未检查评分代码，不据此判定评分实现有误。

严重程度：中；优先补清最终定义。后续责任：ccf-integrity-auditor 核对定义，ccf-paper-writer 表述。

### 10. 摘要仍未完全落实用户要求的四段逻辑

位置：正文第 1 页；[main.tex:72](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:72)。

当前摘要从背景和可执行性缺口直接进入 RAVEN，未给“现有研究状况”独立的一句话；理论句之后还依次补充百分比、观测控制方式、matched-support 分析，末尾又回到支持范围，结构不够集中。

建议：按用户已确定的“背景一句—问题一句—现有研究一句—提出方法—具体机制—理论一句—实验一句”重组。方法细节突出从 sensing-unit reference 到 executable mixture 的连接；实验句聚焦 City Scanner 组失配的 25.8%/23.3%，并准确标明比较对象与协议。统计口径的详细解释可以留实验节。

按项目既有同一套归一化计词函数，当前摘要为 169 词元；这不是投稿系统的官方计词规则。若执行既定“总字数保持不变”，应继续使用同一函数，不用填充套话凑词。

严重程度：中；属于既定修改要求尚未完全落实。后续责任：ccf-paper-writer。

### 11. 引言主体结构已落实，但一处转折关系是强行拼接

位置：正文第 1 页；[main.tex:89](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:89)。

原文：`Although asynchronous learning accommodates irregular updates, participation correction adjusts unequal client contributions.`

问题：异步训练适应不规则到达与参与校正调整客户端贡献是两个并列方向，不构成自然的让步关系。不能为满足“多用 However/Although”而制造不存在的转折。

建议：先按并列关系综述方向；真正的转折用于引出这些工作与记录内选择、有限窗口可执行性之间的缺口。保留最新确定的四段顺序和三个 We 开头的贡献点。

本轮计数：引言 481 词元，前三部分 157 词元，占 32.6%，已符合约三分之一的要求；无需因此重写整个引言。前三段引用数量结构也已落实到背景 5 篇、研究现状 6 篇的配置。本轮未重新做文献真实性或逐篇支持性核验。

严重程度：低；局部连接词问题。后续责任：ccf-paper-writer。

### 12. 复现声明仍在描述内部验收状态

位置：正文第 13 页；[main.tex:1776](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1776)。

原文写本地 bundle 已维护，但尚未核验它是否完整覆盖所有协议，且目前没有公开链接。

问题：`have not been verified as a complete package` 是内部盘点过程，读者真正需要知道材料的明确范围与实际获取方式。

建议：先确定现有材料确实包含什么，再给事实性的范围和可用入口。若没有公开链接，就准确反映当前状态；不能为了消除负面措辞而声称已经公开、完整可复现，或凭空添加 available upon request。该项需要材料事实支持，不能只靠文字美化解决。

严重程度：中；涉及可复现声明的实质准确性。后续责任：ccf-submission-checker 核对交付范围，ccf-paper-writer 表述。

## 四、较小的表达问题

- [main.tex:306](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:306)：预配置 Design 的定义指向 Aggregate Opportunity-Coverage Diagnostic，而配置与窗口逻辑主要在 V-D。应核对指向，减少将诊断与配置混为一谈的风险。
- [appendix.tex:744](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:744)：`under the balanced Balanced control` 有明显重复。
- [appendix.tex:1967](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:1967)：三个常数保留约 15 位小数，影响阅读。论文可用恰当精度和近似号，执行精确值保留在正式配置中；若数值精度影响阈值判断，不应直接改执行参数。
- `frozen`、`existing`、`formal`、`development` 的重复使用需逐项判断。预先固定、防止时序泄漏、区分不同协议时有必要；“Frozen result”“existing tables already report”这类状态提示可以移除。不能把预注册或时序约束一并抹掉。
- 小标题与独立公式不应机械批量合并。引言三项编号贡献是用户明确要求；P2、A1–A6、Theorem/Proposition、Gate/WARMUP/RESET 是正式方法对象，不等于截图中禁止的内部编号。

## 五、已经落实的部分与建议顺序

已落实：正文与补充均为 14 页；图 1 的首次介绍和源代码位置在第三节；引言四部分与 We 开头的三项贡献已形成；当前源文件未检出 `Proof sketch`，正文证明已使用正式 Proof 并给出附录指向，附录有对应命题/定理重述。本轮未重新逐项证明数学正确性，也未重新做图像视觉排版检查。

建议修改顺序：

1. 先纠正截断比例行名、A5 验证范围、A6a 充分性三处错误。
2. 统一内部实验/代码名称，清理 audit/provenance/frozen-result 式标题与过程叙述。
3. 清楚区分当前方法、诊断模块与覆盖控制比较变体，补清最终评分定义。
4. 合并重复限定，按既定顺序微调摘要和引言，整理复现声明。
5. 编译正文及补充，复核表名、交叉引用和改写后的理论条件。无需为这一轮措辞修复重新训练模型。

本轮交付为审查记录；论文源文件、PDF、实验数据和代码均未修改。后续主责任技能为 ccf-paper-writer，涉及条件/数字含义的三项先由 ccf-integrity-auditor 核对。
