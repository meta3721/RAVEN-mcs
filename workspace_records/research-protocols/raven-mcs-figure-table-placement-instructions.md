# RAVEN-MCS：图表、表格引用及引言实验内容迁移指令

请按照以下步骤实际修改当前论文，并编译、核验后交付。任务为内容位置与相关衔接调整，不是新一轮实验或整篇重写。

## 一、最新要求及执行范围

本指令依据用户 2026-10-30 的最新要求执行，优先于此前“在引言中展示主要应用结果和表格指向”的建议。

必须达到：

1. 所有 `Table I`、`Table II`、`Tables …` 等表格编号表述，以及通过 `\ref`、`\autoref`、`\cref` 等形成的表格编号引用，均只出现在正文 Evaluation（实验评价与结果分析）及之后的部分，或独立补充材料中。Evaluation 内的 Experimental Setup 可以引用数据集表。
2. Introduction 不含图、表浮动体，不引用任何图表编号，不陈述实验结果。禁止通过改成 “the results below”“the supplementary evidence”等含糊用语继续把实验结论留在引言。
3. Figure 1 的完整工作流移入第三节 `System Model and Target-Mass Formulation`，并在该节首次解释和引用。正文第一、二节均不提前引用 Figure 1。
4. 正文其他数据图、实验表格及其分析保留在 Evaluation 及之后。补充材料中的证据图表可以继续保留，但正文前置章节不再提前引用其表格编号。
5. 只调整位置和必要衔接；全部实验结果、算法定义、理论条件和引文真实性保持不变。实验继续暂停。

本次“引言”指 Introduction，不自动扩展到 Abstract。摘要按现有要求保留其方法及必要的核心结果，不因本轮迁移擅自删除摘要结果。

论文目录：

`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`

修改对象主要为该目录中的 `main.tex`，必要时同步调整 `appendix.tex`、`supplemental.tex` 的引用及编号延续。不修改模型或实验脚本，不重绘图片，不更改图表数据。

采用 ccf-paper-writer 进行有边界的结构调整，ccf-humanization 清理衔接及重复表达，ccf-submission-checker 进行编译与排版核验。遵守项目适用的 AGENTS.md。当前审查位置为执行线索，以实际最新源码和 PDF 为准，不机械套用旧行号。

## 二、已核实的位置问题

核查版本：`main.tex` 修改于 2026-10-29 21:45，`main.pdf` 编译于当日 21:45；正文 14 页。

当前图 1 在引言中定义，PDF 第 2 页显示；第三节系统模型从 PDF 第 3 页开始。前置章节共有六处带表格编号的表述，涉及七个引用目标：

- 引言第 148 行附近：`Table~\ref{tab:cityscanner_real}`。
- 引言第 153 行附近：`Table~\ref{tab:trained_rules}`。
- 引言第 157 行附近：`Table~\ref{tab:cityscanner_sixarm}`。
- 引言第三项贡献第 179 行附近：`Tables~\ref{tab:cityscanner_real} and~\ref{tab:trained_rules}`。
- Related Work 第 222 行附近：`Table~\ref{tab:nearest_neighbor}`。
- Section IV 第 601 行附近：`Table~\ref{tab:f1_mechanism}`。

此外，引言第 113 行附近提前引用 `Fig.~\ref{fig:raven_overview}`；第 130–145 行附近定义该图；第 147–157 行和第三项贡献第 174–179 行陈述应用结果或机制分析发现。

这些是内容位置问题，不表示原有实验无效。不能通过删证据或改结果解决。

## 第 0 步：确认版本和回退记录

1. 阅读当前正文、补充材料及相应源码，确认章节边界：I Introduction、II Related Work、III System Model、IV Reconstruction、V Calibration、VI Theory、VII Evaluation、VIII Conclusion。
2. 检查这些边界是否已在新稿变化，建立当前的实际位置清单。
3. 使用现有版本控制或已有备份保留当前版本；如果没有覆盖该稿的记录，先建立一次备份。不得覆盖其他人已完成的润色，也不得复原成更旧版本。
4. 记录原图、表、公式、算法和定理的 label、编号、数量，以及 PDF 页数。

成功条件：明确当前稿，原始证据与回退方式可查。

## 第 1 步：将 Figure 1 移到第三节系统模型

操作：

1. 将 `fig:raven_overview` 对应的整个 `figure*` 环境从 Introduction 移走，包含 `includegraphics`、caption 和 label，不能只把图片文件调用复制到另一处。
2. 在第三节标题后、首个子节前，或第三节最初的系统介绍段后，加入简洁的框架导读，并在此首次引用该图。位置应便于读者先理解系统对象，再阅读 R/O/U 定义。
3. 可按实际符号使用下面的句式，必要时调整语法，但不添加新方法：

   `Figure~\ref{fig:raven_overview} summarizes the sensing-to-aggregation workflow. Clients construct normalized updates from local sensing records, and the server reconstructs reference mass and calibrates feasible weights at window close.`

4. 图中的 P2、债务、Design/Gate 等内容在第三节只作框架导读，具体定义继续留在后续方法节。不要为了迁图复制后文全部推导。
5. 保持图形文件、工作流、图号和 `fig:raven_overview` label 不变；不要重新生成或重绘图 1。
6. 图注中关于 City Scanner 客户端具体栅格身份的实验实现细节，若不影响通用框架理解，可移到 Evaluation 的数据/客户端定义处，已有相同内容则合并。Design 在窗口前配置、Gate 仅诊断的身份区别保留准确。
7. 删除引言原有 `Fig.~\ref{fig:raven_overview}`，改成完整、自然的方法介绍句，不能留下空括号。

编译后检查浮动体实际位置。源码迁入第三节不代表 PDF 已满足要求。可使用现有 `placeins` / `\FloatBarrier` 控制其在第三节结束前排出，但不得默认用 `\clearpage`、大幅负间距或缩小图片字体强行定位。

成功条件：正文图 1 仅有一个实例；首次引用和完整图形均属于第三节；第一、二节没有该图或其编号引用；图形在 PDF 中未落回第三节标题之前，也未拖到第四节方法细节之后。

失败处理：若双栏浮动难以在第三节排出，调整图在第三节内的源位置和常规浮动设置，再目视检查。不能只凭源码位置宣称完成。

## 第 2 步：清理引言的图表引用和实验结论

不能只删除 Table/Fig 的编号，须处理其承载的实验叙述。

1. 对当前第 147–157 行附近的应用证据段落进行分句处理：
   - “City Scanner 最低平均组失配”等实际结论归入 Evaluation 中 City Scanner 对应结果段。
   - 真实 R、控制 U、两协议 O 身份不同等实验设置归入 Evaluation 的设置或 City Scanner 协议介绍。
   - 投影、Uniform、参考校正的具体比较与几何发现归入相同支持归因或几何分析小节。
   - 目标支持变体的具体结果归入已有六臂比较小节。
2. 原引言如需保留验证概述，最多用一至两句说明评估对象和评估设计，不包含结果或证据编号。例如：

   `We evaluate the roles of reference correction and feasible calibration through matched-support comparisons and support-geometry analysis.`

   这是对研究安排的说明，不是对实验发现的提前报告。不要将现有评估安排包装成未经论证的新型实验方法贡献。
3. 三项贡献继续保留。前两项突出原子单元重构、可行校准与准确的理论贡献；第三项改为说明评估覆盖哪些科学问题，而不是宣称已取得最低失配或更好预测。
4. 引言中所有“最低、改善、超过、优于、下降多少、十条轨迹全部成立、消融显示”等经验性结果陈述均重新检查，不论是否带数字或表格引用。
5. 引言可保留正确的理论机制和理论结论及其定理指向，不能误删为“实验结果”。保留相关工作文献引用，不能把 `[3]` 之类文献编号与 Table III 混淆。
6. 检查是否仍有引言直指实验结果附录的语句。纯实验证据的提前指向与对应结果一起迁移，不能以 Appendix 引用绕过用户要求；真正的定义或理论证明指向不属此类。

成功条件：引言无图表环境、无图表编号引用、无定量或定性的实验结果；仍清楚说明问题、缺口、方法机制和编号贡献，不变成泛泛背景。主要创新表达不能因迁移结果而丢失。

## 第 3 步：把 Related Work 和方法部分的表格引用迁到 Evaluation

### Related Work 的接近方法比较

当前 `tab:nearest_neighbor` 是信息要求和保证范围的比较表，不是方法性能排名。保留相关工作中关于 FedIPW、FedPALS 与 RAVEN 差异的独立、准确文字，但去掉提前引用该表的部分。

在 Evaluation 的 Methods and pairing 或相应基线说明中，加入对该表的准确引用，说明它比较方法对象、信息条件和保证范围。表本体可继续位于独立补充材料，不必为了迁引用把宽表塞进正文。不能把这次迁移写成“本实验已经运行了 FedIPW、FedPALS”等未完成比较。

### Section IV 的观测异质性检查

当前 `tab:f1_mechanism` 的实验指向移至 Evaluation 的观察校正、局部权重或敏感性分析对应段落。方法节保留常数权重经 Hájek 归一化相消的数学解释及真正的推导指向；不提前陈述具体样本上的检查结果。

### 其他前置实验旁注

检查 Section III–VI 是否仍出现 empirical trace、数值求解检查、现有轨迹中的 clipping 或实验 stress levels 等旁注。与本轮迁移内容直接相关的实验解释归回 Evaluation 对应小节；纯数学条件、定义、常数、定理、算法和证明保持原意，不因其中有数字而删除。

成功条件：Evaluation 开始前没有任何表格编号引用或表格浮动体；相关工作与方法仍可独立理解；被迁移的比较信息在 Evaluation 或后续材料中有准确落点。

## 第 4 步：合并迁入内容，不重复增加实验段落

1. 本次大部分实验事实已在 Evaluation 详述。逐句核对落点：已充分说明的，直接去掉前置重复句；只有原处承载独有的必要解释时，才把它融合进后文。
2. 报告中记录每项是“迁移”还是“删除前置重复、后文已有”，避免把不重复复制误写成证据遗失。
3. City Scanner 主比较、六臂支持比较、相同支持投影、消融、几何分析及辅助诊断保持原有实质结果。Table II、III、VI 等主证据继续留在正文 Evaluation。
4. 保留效果的端点、比较对象、统计单位、区间和重要边界。25.8%、23.3% 为组失配下降，不能改成 RMSE 下降；不同协议或支持集的效应不能合并。
5. 结论和 Data and Code Availability 位于 Evaluation 之后，可保留必要结果总结和图表引用；不要借这次迁移额外塞入全部重复数字。

成功条件：引言更聚焦方法，后文证据完整；没有新增实验、扩大主张、改变数据或制造重复结果分析。

## 第 5 步：全局扫描与编号检查

按实际章节边界检查，不依靠固定行号或单个英文关键词：

- Introduction 范围内，检查 figure/table/figure*/table*，以及 wrapfigure、subfigure、input 引入的图表等实际存在形式。
- 检查 `Fig.`、`Figure`、`Table`、`Tables` 与自动引用的实际输出。包括 `\ref`、`\autoref`、`\cref`、`\Cref`、多 label 引用和自定义宏。
- Evaluation 之前的表格编号引用为零。排除未渲染注释，不能把 bibliography 的文献标题或无关普通单词误判为表格指向。
- 引言经验性结果陈述为零。人工检查“lowest/better/improves/reduces/outperforms/results demonstrate”等语义；不能仅因字符串无命中就判定通过。
- 第三节首次引用并容纳图 1；其他数据图均在 Evaluation 及以后，所有图表均有有意义的文字解释和编号引用。
- 重新检查附录图表引用，迁移后不能造成孤立标签。正文和补充材料的 xr 交叉引用保持正常。
- 保留原 label 和正常计数。图 1 移动通常无需改编号；若发生真实编号变化，核对补充材料 setcounter 及全部自动引用，不使用手写编号补丁。

成功条件：上述结构约束全部满足，且无重复定义、引用问号或证据指向丢失。

## 第 6 步：编译、逐页核验与交付

1. 使用现有编译工具，按需要交替编译 main 和 supplemental，直到跨 PDF 引用稳定。对局部编译错误最多作三轮针对性修复；未解决的报告首个根本错误及位置，不能用旧 PDF 充数。
2. 检查引言页、Related Work 页、第三节全部页面、第三与第四节交界、Evaluation 开始页及所有图表页。
3. 重点确认：图 1 在第三节实际显示；引言无图表或实验结果；实验表格不因浮动漂到 Evaluation 标题之前；表格引用和浮动体位置都符合要求。
4. 保持正文不超过 14 页，补充材料不长于最终正文。若迁图引起排版变长，优先去除重复文字、优化正常浮动，不删主证据、不压小基础字号，不用异常间距强行达标。
5. 对比原稿确认图形数据、全部表格数值、公式、算法、理论条件及参考文献条目未被未经授权地改动。

交付更新后的 `main.pdf`、`supplemental.pdf` 和实际修改源码；在 `C:/Cursor/raven.mcs/ccf-review-report/FIGURE_TABLE_PLACEMENT_REPORT.md` 写一份简洁报告，包括：

- 检查和修改的实际版本。
- 引言图表及实验内容清理位置；六处原表格引用各自的新位置或合并去向。
- Figure 1 在源码中的新位置、最终 PDF 页码、首次引用位置，以及第三节起止页。
- 迁移前后图表数量和编号核对、引用检查结果、编译状态及最终页数。
- 是否仍有不满足项；若有，说明原因、受影响范围及需要作者决定的选项。
- 备份及回退说明。

完成条件不能只写“源文件已修改”。只有最终 PDF 的实际版面和语义检查都通过，才标记结构迁移完成。作者信息、公共复现链接等其他待办不应借本轮任务擅自填写或修改。

本轮只按该指令处理位置与衔接，不恢复实验，不扩展研究范围，也不重做已完成的其他润色。
