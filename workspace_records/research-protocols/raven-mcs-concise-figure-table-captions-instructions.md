# RAVEN-MCS 图表标题和说明精简指令

请实际精简论文正文及补充材料的图表标题与说明，做到标题短、信息清楚、必要条件可查。不要只提出建议，不改实验或重画图片。

## 一、范围与回退

论文目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

主要修改 `main.tex`、`appendix.tex` 中 figure/table 环境的 `\caption{...}`。算法标题、论文标题、章节标题、图像内部文字不在本轮范围。

采用 ccf-paper-writer 和 ccf-humanization 进行文字精简，使用现有编译流程检查效果。先阅读当前稿及适用的 AGENTS.md，利用现有版本控制或一次备份保存回退记录。

图形文件、绘图代码、全部数据、误差线、表格行列、显著性标记、label、编号和引用对应关系均保持不变。必要说明可移动到图表邻近的结果段、实验设置或现有附录；只有确有必要时允许加入简短表下注释。不得把说明搬到引言，也不得改变图 1 位于第三节的安排。

此前摘要和引言的同词数要求保持生效，本轮不修改它们。图表说明允许缩短，不用另加文字抵消节省的篇幅。实验继续暂停。

## 二、统一采用“短标题＋必要说明”

1. Caption 第一句作为真正标题，直接说明对象和比较内容。表题一般以 5–10 个英文词为目标，图题一般以 5–12 个英文词为目标；这是目标，不是强制截断限制。已有更短且明确的标题可直接保留。
2. 不把样本数、全部协议设置、单位、统计检验、所有结果解读和开发历史都塞进标题句。它们按必要性放在后面的短说明、表下注释或正文。
3. 图注随后只保留识别子图、误差线、关键符号及阅读所需的简短说明；表格说明保留度量方向、统计口径和独有符号等必要信息。
4. 多子图应保留 (a)、(b)、(c) 的准确对应，不能为了短而只剩一个模糊总标题。已有下置子图标题不删除、不重画。
5. 省掉重复的 `results/comparison of the results/evaluation results of` 等套语，使用可区分的具体对象，例如 `City Scanner target-map variants`。
6. 不能将所有标题缩成 `Performance comparison`、`Experimental results`、`Ablation study` 而失去辨识度；相近图表标题仍应能区分数据、端点或协议。
7. `lower is better` 可在列标题有明确箭头或共享说明已经清楚时去重；没有其他读图依据时保留。不要无条件删除。
8. 不要求把所有 caption 压成一行，也不追求每个 caption 相同长度。含多子图或特殊统计单位的图表可以保留合理长度。

## 三、优先处理的当前对象

本次读取到的长说明包括：图 1 约 91 个空格词元；City Scanner 主表约 63；六臂目标支持表约 59；相同支持规则表约 58；补充 U-Air 完整方法表约 82。数字只用于定位，执行时以最新稿为准。

可采用以下短标题方向，再按实际对象核实，不要机械照抄到不对应的图表：

- `fig:raven_overview`：`RAVEN-MCS workflow.`
- `tab:datasets`：`Datasets and evaluation protocols.`
- `tab:cityscanner_real`：`City Scanner completion under two sensing protocols.`
- `tab:cityscanner_sixarm`：`City Scanner target-map variants.`
- `fig:risk_noninterchangeability`：`Target- and arrival-risk changes on NSW-Traffic.`
- `fig:g3_tdrive`：`T-Drive opportunity and target mismatch.`
- `tab:tdrive_hybrid`：`T-Drive comparison under real sensing opportunities.`
- `tab:main_effectiveness`：`Controlled station-protocol comparison.`
- `fig:w1_design_gate`：`Design sensitivity to estimated and oracle propensities.`
- `tab:trained_rules`：`Matched-support aggregation rules.`
- `tab:e4_ablation`：`Component-removal effects.`
- `tab:target_concentration`：`Target-concentration sensitivity on NSW-Traffic.`
- `tab:app_e3_uair`：`U-Air method comparison.`
- `fig:learning_capacity`：`Centralized learning curves across datasets.`
- `tab:certificate_stress`：`Candidate coverage diagnostic under stress.`

这些只是标题句的候选，不能以它们替代整段必要说明。例如“under real sensing opportunities”只指 R 来自真实机会，不代表 O/U 均为真实测量。覆盖候选的标题不能升级成“主方法覆盖保证验证”。

## 四、逐个判断：保留、移位、删除重复

先逐图逐表阅读 caption、图表内容及相邻正文，再作以下处理：

### A. 保留在图注或紧邻表下注释的信息

- mean、SD/SE/CI 的实际类型及误差线含义，不能把 min–max 改成 CI。
- 独立统计单位：种子、轨迹均值、每轨迹多个模型种子的区别。
- 非常规单位、标准化方式及不同子块不可直接横比的必要解释。
- 表内独有的符号，例如星号、dagger、rho，以及未在表头或图内清楚定义的缩写。
- 效果符号的方向、零线和基准线含义；不能让正负变化被误读为统一“越大越好”。
- 有效比较所必需的支持集和变体身份区别。

可以写短一些，但不能用泛泛“details in the text”代替缺失信息。

### B. 移入相应正文或既有设置中的信息

- 详细客户端定义、空间网格、训练设置、协议生成过程和已在方法中解释的状态更新。
- 结果的完整解释、为什么某一方法领先、未通过某项实用门槛的展开讨论。
- 保存参数重评分、历史候选身份和可重构检查等过程性细节。保留确实影响结果解释的事实，改成自然的研究说明。
- 图 1 关于空窗口和债务递推的细节，可与第三节或后续方法的现有解释合并，不在图注重复整个方法。

若正文已有同样准确的信息，直接去掉 caption 中的重复，不再复制一次。若是唯一信息，迁移后须有明确落点。

### C. 可以删除的内容

- 不增加读图信息的套话、重复方法全称和重复结果解读。
- 图内、表头或邻近说明已清楚呈现的相同定义和方向。
- 纯内部版本/审核措辞及不影响科学含义的目录式记录。

不能以“负面表述”或“标题太长”为由删除会改变比较结论、协议身份或证据范围的信息。

## 五、重点图表的保护条件

1. City Scanner 主表：明确两协议、样本统计、各自训练标准化尺度；不能让误差被理解成物理浓度单位或共享跨协议尺度。具体网格客户端身份放到已有设置即可，不必全塞标题。
2. 六臂目标支持表：保留“十条轨迹均值、每条三个模型种子”的统计层级，不能写成三十个独立重复；rho 的含义及共同目标比较范围仍可查。
3. 相同支持规则表：保留 matched support、时间单位、均值口径，以及 U-Air Count 与另一表 unrestricted FedAvg 的支持差异；κ=1000 仍是独立敏感性变体。
4. 补充 U-Air 完整方法表：方法特定支持集及其与其他图中同名 FedAvg 行的区别不能失踪；可用一句短注结合邻近正文交代，不需要重复整段过程说明。
5. 组件移除表：保留百分比定义、正负方向和 Holm 标记含义。
6. 风险差图：保留 D 的定义、负值的解释及方向计数与显著性不是同一概念的准确说明，后者如已在结果正文清楚解释可不在图注重复。
7. 覆盖诊断图表：保留候选变体身份、有效覆盖的定义及必要状态说明，不能因缩短而混成主方法的无条件覆盖保证。

## 六、执行与核验

按“正文图表→补充图表→全文检查”的顺序逐个处理，不用正则表达式截断 caption 第一行来自动完成。LaTeX caption 内有嵌套花括号、公式和引用，必须保持语法完整。

每个对象完成后核对：

- 标题能否直接识别对象与比较内容；短说明是否仍能支持准确读图。
- 删除的句子是重复还是迁移；必要迁移是否真的已写入对应正文。
- 实验数字、符号、表头、单位、误差线和方法身份未改变。
- 既有图表 label、计数、引用不变，无新增孤立图表。

不新增不必要的宏包或整套表格环境。需要表下注释时采用与现有模板兼容的简洁方式，不依靠继续缩小字号节省空间。

重新编译正文与补充材料，稳定跨文件引用。目视查看所有含图表的页面：caption 是否换行自然、是否有压线/裁切/溢出、注释是否过小，表格是否因此更易阅读。不能仅凭源码词数减少判定排版改进。

页数仍按既有约束：正文不超过 14 页，补充不长于正文；不通过改页边距、压小基础字号或异常负间距解决。

## 七、交付

交付更新后的 main.pdf、supplemental.pdf 及实际修改源码。在以下报告维护逐图表清单：

`C:/Cursor/raven.mcs/ccf-review-report/FIGURE_TABLE_CAPTION_CONCISION_REPORT.md`

清单包括每个修改对象的 label、原/新标题句、原/新完整 caption 词数、必要说明的保留或迁移位置。若转成表下注释，统计应同时报告说明总量，不能只算 caption 减少而声称整体内容减少。

报告注明编译状态、页数、实际版面检查和回退方式。已足够简练的对象可以标为保留，不为完成数量而逐项硬改。

最终回复给正文和补充 PDF、修改报告链接，简要展示几个代表性的标题前后对照。不改变研究主张，不启动实验，不重做图片。
