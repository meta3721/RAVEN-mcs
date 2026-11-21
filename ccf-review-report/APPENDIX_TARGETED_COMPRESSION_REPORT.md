# 附录定点修复与压缩报告

本轮已完成三处引用处理、授权范围内的删减和局部浮动优化。**正文14页，补充由15页压至14页**；达到目标后停止进一步删减。A—H组织、Reading guide和关键证据保持。

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)
- [补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)
- [规范正文源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)
- [规范附录源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex)
- [本轮完整差异](C:/Cursor/raven.mcs/ccf-review-report/APPENDIX_TARGETED_COMPRESSION_DIFF.md)

使用ccf-paper-writer的compress模式，并按ccf-humanization检查新表述；没有新增实验、推理、评分、参数选择、求解或统计检验。

## 三处正文引用

1. **F-C掩蔽代价。** 已读取本轮交叉引用核查记录，记录没有提供可准确定位的新结果。沿用已确认的证据缺口判断，删除正文关于SensorScope至多0.175%、比例0.388和U-Air 6.6%—7.5%、比例0.354—0.466的非核心量化比较，同时删除仅依赖它的“零目标比例不能预测代价”推断及引导句。没有倒推数据、补表或改成新的正向概括。F-C的离线零目标计数、查找对象、配置规则、回顾性权衡公式和表均保留；正文方法对这些定义的引用仍有效。本次是撤去缺少当前可核查支撑的主张，不是恢复或验证了这组结果。
2. **F-D/F-E。** 稳定化误差的中位数及最大值分句直接引用`app:a5_a6_audit`（F-D）；替换估计边际后的参考/预测变化另引`app:reference_sensitivity`（F-E）。没有改结果数字。
3. **H-B。** 正式站点模型与training-mean比较分句补`app:formal_prediction_references`（H-B）；独立开发验证继续指H-A，学习/更新预算分别指H-A/H-C。没有把独立开发收益归于RAVEN聚合。

三处处理均在正文Reference sensitivity附近及其前一段完成；摘要、引言、贡献、其他Evaluation结果与结论没有重写。

## 压缩与局部排版记录

- 首轮只做上述引用处理、删除INT-R末尾重复的范围说明，并将两张延迟表的声明移近相关主题。编译仍为14/15页。
- 检查三个规范TeX及标签依赖后，确认H中`Release-Timing Reference Study`、`app:release_timing`、`tab:release_timing`没有正文、图注、其他附录或数据声明的外部引用；其唯一表引用在该子节内部。它是独立开发释放策略分析，不支撑本文参考重建与有限窗口聚合的核心主张。
- 按本轮明确授权，**完整删除这一非核心子节及整张释放时机表**，包括全部比较策略与有利/不利结果，没有只删部分行。没有触动开发学习、正式预测参照、服务器更新敏感性或开发几何。此后仍为15页，继续只处理浮动安排。
- 将INT-R完整比较表的声明前移至相邻的欠服务块子节之前，使其能够提前进入浮动队列；内容仍属于D-H。将局部权重常量表声明移至E-A入口，允许该表及层内异质机制表使用标准`[!htbp]`。没有全局改模板、缩小字体/边距、负间距、栅格化或删除实际第15页。
- 最终INT-R说明D-H在补充p8，对应`tab:int_r_e3`为表XVI、p9；局部归一化说明E-A在p8，对应`tab:app_local_hajek`为表XIX、p9。原两页间距均缩至一页。编号变化由label自动处理。
- 最终达到14/14后，不再压缩证明、关键设置或其他结果。

## 被移除材料的保存位置

释放时机完整原文、原表和两份修改前PDF均保留于本轮ZIP；单独摘录另存于 `C:/Cursor/raven.mcs/tmp/appendix_targeted_20261104/removed_release_timing.tex`。完整删除差异也收入本轮DIFF，便于恢复。先前结构重组备份和历史报告未覆盖。

原实验结果目录均保留，包括：

- `C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/`
- `C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/`
- `C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/`

这些目录及其DECISION_METRICS.csv、VALIDATION_AND_SUMMARY.json未修改，也没有借用不同协议的统计量重建删除的表。原表的确切论文版本可从本轮备份恢复。

## 内容与编译验收

- A—H八个一级标题及对应关系不变；Reading guide、自动页码、F-D/F-E/H-B等稳定小节入口保留。supplemental.tex及书目本轮逐字节未改。
- 所有保留表格的完整内容与修改前相同，仅浮动参数/位置变化；唯一删表是整个`tab:release_timing`。全部图块及图资产保持，未将支持不同的U-Air图/表当作重复删除。
- equation、align、multline、proof、restated、algorithmic、proposition、corollary逐块计数及内容保持。主要证明没有改成sketch；基线公式、数据/支持/尺度、六臂十轨迹×三模型种子与检验身份、主方法/覆盖变体/开发协议的区别均保留。
- 仅删除释放时机子节的两个标签；保留标签无重复。扫描ref/eqref/pageref时正确排除宏参数`#2`，无悬空引用，也没有留下“该释放研究仍在附录展示”的表述。
- 最终现有MiKTeX顺序构建成功，更新两份书目并按xr依赖编译至aux稳定。正文14页、补充14页，无LaTeX错误、未定义/重复引用、缺字或Overfull。
- 检查受影响正文p12、补充p5–14的实际分页渲染，特别检查p8–10及最后两页：表格、图例、误差线和公式完整，无可见遮挡或裁切。最后一页仍有实际开发几何结果和参考文献，没有删页或拼接PDF。
- 写作检查无em dash；原技术表述的句长及分号提示经人工核对，不以机械改动数学符号消除提示。本轮没有新增科学结论。

核验记录位于 `C:/Cursor/raven.mcs/tmp/appendix_targeted_20261104/`：`checks.json`、`citation_build_status.json`、`prose_quality.json`及分页预览。当前任务的引用、篇幅和页面核验已通过，无遗留阻塞；这不构成对所有历史实验或整篇论文科学有效性的重新认证。

## 回退

实际编辑仅main.tex和appendix.tex及编译产物；supplemental.tex模板未改。备份直接入口在下方。

若尚无后续修改，先解压到独立目录，只恢复本轮main.tex、appendix.tex后重编译两份PDF。若已有后续用户修改，按本轮DIFF反向合并三处正文修复、重复段删除、释放子节及两个表的局部位置，不用旧整篇源码覆盖后续工作。不恢复实验、不修改原始数据、模型、配置或历史停止状态。

[本轮修改前备份](C:/Cursor/raven.mcs/ccf-review-report/backups/appendix_targeted_20261104_120255.zip)
