# 正文主张一致性修订报告

日期：2026-10-18。规范目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。以本轮开始时的当前工作树为基准，修改`main.tex`及`appendix.tex`的一处衔接段；未回退此前修复，未新增实验。

## A—I逐项处理

**A．指标范围（VII-A，第8页）。** 原总定义把WorstGroupRMSE统一称为四UTC块最大值。现定义为协议预先冻结群体的评分最大值，群体内权重按协议重新归一；分别说明SensorScope/U-Air和T-Drive采用UTC块，City Scanner及NSW四区域协议采用空间群体。Tail RMSE的UTC块2、3限定在报告该端点的站点协议。SensorScope物理单位、U-Air/Traffic原训练标准化尺度17.363/575.776和City Scanner各块训练z-score分别说明。原RMSE公式和所有评分结果不变。

**B．种子与层级（VII-A，第8页）。** 将“Principal comparisons use 20 paired seeds”改为按协议说明：受控站点20配对种子，City Scanner两个五方法块各10种子，T-Drive 10，balanced control 5；六臂为10条轨迹、每条3模型种子。开发学习的三种子及一条Uniform轨迹保留，其他计数以各表为准，不再按旧“附录排名”位置概括。种子不代表独立城市的说明保留；站点区间的既有bootstrap说明也明确限于该比较范围，未改变检验或区间计算。

**C．数据与实验角色（VII开场第7页、Table I第8页）。** 站点Role改为受控机制、Design及消融；City Scanner改为应用比较，并保留两套real R、controlled O/U或measured O/controlled U身份。显示名称`City Scanner P2`改为`City Scanner Pilot 2`，避免与优化程序(P2)混淆。NSW角色改为风险语义及四区域比较。VII开场按应用组对齐、同支持机制归因、预测/运行时间与有限支持诊断组织，不再使用笼统的“deployment consequences”。数据表只改Role和该显示名称，数据量、划分、群体数、分层及Max s不变。

**D．实际参考与理想恢复（I第1页、III-C第3页、IV第4—5页）。** 引言和IV首次介绍实际参考时明确其为估计、稳定化的目标质量参考；III-C说明兼容目标为客户端校正质量估计规定部署对象。IV-C将“restores relative corrected mass”改为：`m d`把局部归一化移除的质量尺度与可用更新纠偏纳入服务器相对参考。保留理想未截断因子分解、实际β与最终α及Mα的区别，不将每窗口实现写成总体质量精确恢复。

**E．位移归一化（IV-B，第5页）。** 原“preserving the server update scale”改为去除显式本地学习率及步数因子，位移仍由训练路径决定。归一化公式、局部目标、γ、步数和服务器更新全部不变，未宣称多步更新等于单步梯度或方向不随训练配置变化。

**F．图1与NoDesign（图1第2页、Table III图注第10页）。** 图1改为描述参考构造和有限支持校准过程；NoDesign明确省略机会到目标比率、保留观测/可用性校正及校准，替代过宽的“is not target-mass reconstruction”。图1末尾对(P2)的重复说明紧凑合并。窗口前固定Design、Gate仅诊断的规则保留；T-Drive全部方法行、排名及不利结果不动。

**G．理论与辅助覆盖的范围。** VI-B保留一般风险测度区别及“固定预测器的风险仍可能相等”；VI-D/E、V-B及附录证明保留精确凸程序唯一解、固定状态扰动界、数值核验独立性和次线性债务条件，未修改公式、假设或证明。覆盖标题改为V-E `Aggregate Opportunity-Coverage Diagnostic`（第6页）与VI-F `Stable-Regime Aggregate Coverage Bound`（第7页），沿用原标签。VII-G覆盖段（第13页）明确.959/.750属于另行评价的`Design=Gate`候选，区别于当前窗口前配置Design的方法；交换性、冻结预测器、历史分数及CERTIFIED的条件性原文保留。

**H．代号及局部总结（IV-C/V-C第5页、图4第10页）。** 删除IV末重复的W1预告，仅在V-C保留一次自然表述的同支持比较和VII-E交叉引用；内部文件路径及复现标识不改。图4的“flat RMSE”改为“little change in mean RMSE”，不改均值、Holm结论或称为等价。INT-R、T-Drive和NSW四区域协议及不利排名均保留。

另同步Appendix F开场（补充第7页）：旧文把U-Air某设置称为“部署使用”的设置，并在“报告两臂”后只列单一设置；现明确该处同骨干上下文固定Design on，Table IV另列两数据集各自固定on/off两臂。仅替换这一衔接段，既有S1支持集及评分修复、图注、表体均不动。

**I．已准确的核心结果保留。** 摘要、贡献列表及引言末实证概述、City Scanner整个结果小节、VII-E同支持归因及其后几何/学习/更新规则结果、结论均保持原文。25.8%/23.3%仍是完整RAVEN在两个协议中相对最佳已报告组对照的描述性均值之比；1.188/1.399、.768/.286和.922 pp比较不合并。68.96%/83.07%、完整P2与投影的取舍、101.9%和原预测区间、183个K=8与4.651%、骨干及敏感性规则身份均保留，无新增效果主张。

## 编译与一致性验收

- 使用现有MiKTeX `pdflatex`，禁用shell escape、单进程顺序编译正文和补充，直至引用稳定。最终正文**14页**、补充**14页**，均含各自参考文献；修改前亦为14/14页。没有调整模板、字号、边距、行距或浮动参数。
- 最终日志无未定义引用、重复标签、overfull box或待重编译提示。常规underfull提示及禁用shell escape的epstopdf提示不影响构建；未安装/更新环境。书目及引用键未改，现有bbl复用。
- 源码逐块比较通过：全部数学环境、假设、命题、定理、算法、结果表体和图资产引用不变；Table I数字与划分单元不变；全部标签和跨PDF编号不变；`reference.bib`、`supplemental.tex`不变。正文核心表图保持原顺序与浮动设置，City Scanner Table II仍在第9页。附录衔接缩短后，开发学习Table XXIX自然浮动至补充第13页，仍在原章节附近，未增删或改数值。
- 已顺序渲染两份PDF共28页并检查缩略图，放大核读图1、IV-B/C、覆盖与理论、数据/指标设置、City Scanner、T-Drive/Design、覆盖结果及附录衔接页面；未见遮挡、截断或超宽。
- 使用ccf-humanization及文字质量脚本核读。全稿无em dash及脚本error；uniform-sentence-run和分号密度提示已人工核读，涉及既有公式衔接、跨节串联和紧凑比较，不为消除模式提示重写准确内容。未加入防御式收尾或内部审批叙述。

定向差异见`PAPER_BODY_CLAIM_ALIGNMENT_DIFF.md`。按排除数学、表图及图注等的相同近似英文词数口径，正文6217→6293、附录5453→5431，净增加54词；本轮修复定义范围，不宣称新增页数压缩。

## 边界

本轮为定义与叙述一致性修订，没有通过文字补齐完整P2采用理由、训练充分性或历史待决评分。既有F1、漂移及外生目标未闭合状态不变，继续由`PAPER_EVIDENCE_PENDING_ITEMS.md`记录。未发现需要改变方法或科学结论才能完成本轮指定修复的新问题。

训练、推理、重评分、回放、求解、新统计检验和文献检索均为0；方法代码、数据、冻结参数、实验协议及历史失败记录未修改。
