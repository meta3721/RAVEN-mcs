# Evaluation内部结构调整报告

已按指定指令实际修改规范稿，使用ccf-paper-writer组织英文表述，并进行ccf-humanization前后检查。实验保持暂停；未训练、推理、重评分、调参、求解或重新计算检验。本轮没有重画图。

## 三个重点的落实

1. **B节比较维度。** 保留五个独立斜体方法名段落及顺序，明确本地训练、服务器质量/参考、可行校准与债务。完整RAVEN介绍补入校正局部训练；共享骨干/窗口协议不再暗示相同局部权重、正质量支持或约束。辅助比较拆成Matched-support rules和Other comparisons两段：Count仅归一化计数，不执行C_r；Uniform在本配置下可行；投影和P2执行约束。明确Inst-Cal是无债务P2，与移除Inst不同；κ=1000仍为独立敏感性配置。公式29后既有配置定义未改。
2. **D/E分工。** D按City Scanner → Controlled station comparisons → Additional sensing protocols → Target-risk and arrival-risk comparison组织。E按Matched-support comparison → Reference reconstruction and feasible calibration → Component contributions组织，先解释参考到执行，再报告Count/Uniform描述性份额。所有组件消融按配对事件说明，不一概称固定支持。
3. **F诊断密度。** 先Support and constraint geometry，再Target-support variants，最后Reference sensitivity。保留正式窗口比例、范围阈值、六臂配对结构和必要预测状态；数值求解、完整开发扫描、全量敏感性与学习设置由真实补充内容承接。

完整RQ及A—F六小节保持。标题、摘要、引言、贡献、方法、理论与结论没有重写；Evaluation之前及Conclusion之后与本轮备份逐字一致。

## 原段落/图表 → 新位置

- `tab:cityscanner_real`：仍为RQ1入口、正文表II；25.8%/23.3%仍为种子均值之比，两协议均有受控U，预测领先方法原样保留。
- 原E的Fixed-configuration Design effects、`tab:main_effectiveness`、`fig:w1_design_gate`及对应解释 → D的Controlled station comparisons。最终为正文表III（p10）和图2（p9）；774配对窗、51.6%活跃支持重合及端到端身份集中在此。
- Under-served-block冻结规则、完整阈值和逐项结果 → 现有附录F、`tab:underserved_block`附近的实质段落，新定位label `app:underserved_block`。D保留“满足no-harm、未达到所要求改善”及直接入口。INT-R完整材料仍在`app:int_r`，D仅一句结果。
- T-Drive、NSW四区域 → D的Additional sensing protocols；风险语义单列在其后。原`fig:risk_noninterchangeability`保留为正文图4；平衡控制保留.0599%、上界.134%及`app:e1_balanced`入口，六场景全矩阵由`app:e2_layer_matrix`承接。
- `tab:trained_rules` → E固定支持比较，最终表V（p11），所有预测、WorstGroup与Wall列、债务敏感性行保留。直接参考只承担离线结构读出，不借用TwoStage端到端预测/时间。
- `tab:e4_ablation` → E组件分析，最终表VI（p12）。Design行仍在表中，但指向D的端到端解释；Inst/Inst-Cal、标准Debt与独立κ=1000的区别保留。
- 原Numerical accuracy独立段 → 正文仅保留入口；2.42×10^-5及残差/目标差完整内容已存在于`app:kappa_probe`、`app:p2_diagnostics`，未再复制一份。
- 原F开发轨迹细目 → 正文保留W阈值.01和不同支持批次说明；完整种子、183子集、cap/ESS、投影距离仍在`app:arrival_support`及`app:development_geometry`的现有表和分析。
- `tab:cityscanner_sixarm` → F几何之后，表VII（p13）。十条trace、每条三模型种子、10/10结构改善、图式多重性分配、101.9%保留率和3.83/4.14/8.15%非劣上界保留正文。HL估计、cluster区间、次级家族及自身client–stratum目标由`app:cityscanner_sixarm`完整承接。
- 稳定化/参考扰动和Prediction sensitivity完整参数、区间、检测能力 → 现有附录H `app:a5_a6_audit`，增加实质定位`app:reference_sensitivity`。去重H中与表格重复的日志说明；保留原始条件、触发比例及独有数字。A6a仍是误差为零的充分条件，不是扰动界必须满足的条件；A6b及共享状态没有被写成已核验。
- `tab:target_concentration`和完整分析 → 附录H内实际新增承载段Target-Concentration Sensitivity（`app:target_concentration`），最终补充表XXV（p11）。原稿没有独立目标集中度附录，故在已有参考/风险敏感性材料所在的H中承接，没有虚构原有标签或N系列文件。正文保留.0970%及低于2%实际意义标准的范围。
- 学习容量、更新规则 → 原`app:learning_capacity`/`app:update_rule_sensitivity`。为容纳迁入材料，压缩重复设置与引导语，保留预算、基线定义、独有结果和完整曲线/表；正文仍区分正式站点未超过训练均值与独立开发验证改善。

## 关键证据与统计保护

正文保留直接参考→投影1.188/1.399 TV pp及原区间，投影→Uniform对照.768/.286 TV pp及原区间，独立固定支持Design .922 TV pp及原区间。它们没有相加，也没有记为完整P2的新增收益。完整P2相对投影的结构、预测和时间取舍未删。

Count→Uniform的68.96%/83.07%放到上述机制比较之后，明确为共同路径上的均值差描述，不能解释为因果贡献率。校正局部权重恒定时的归一化抵消与客户端质量仍可能影响服务器聚合相连；异质构造只说明已有校正输入，不恢复F1预测结论。

既有SD/CI、配对单位、Wilcoxon/Holm家族、图式主链及独立次级家族、实际意义阈值和2%非劣状态保持。未显著没有改成等效，非劣未建立没有改成证明劣于。

## 核验与排版

- 修改前：正文14页，补充14页。修改后：**正文14页，补充14页**。保留双栏模板、字体与边距。
- main/supplemental顺序编译并更新书目，最终aux稳定；日志无LaTeX错误、未定义引用、重复label、缺字或Overfull。
- 对比备份，所有原table/figure完整内容在两文件合并后保留（表格仅允许浮动参数变化）；所有编号公式、证明、定理、命题和算法原样保留。原label全部保留且无重复，书目未改。
- 正文由8表变7表，补充table起始counter由8改7，总表数量不变；图仍为正文4、补充4，自动编号和跨PDF引用稳定。补充单栏表允许标准`[!htbp]`浮动，解除E/F之间的FloatBarrier以减少不必要空白；没有强制[H]、负间距、图像缩放或PDF拼接。
- 检查重排后的正文9–14页、补充相关6–14页及整页预览，修复了迁移过程中的重复空标题和重复label；最终页面未见遮挡、裁切或异常空白。图1仍在第三节，引言不引图表。
- 运行写作脚本：新Evaluation无em dash；等长句提示对应既有技术表注，分号密度提示包含数学/表格分隔，人工核对后保留必要统计说明，没有为消除提示改符号或数据。
- 构建日志、检查结果、分页图与来源差异保存于`C:/Cursor/raven.mcs/tmp/evaluation_internal_20261103/`，重点为`checks.json`、`citation_build_status.json`、`prose_quality.json`及三个TeX差异。没有运行实验。

本轮结构、迁移及页数验收已完成；没有新增科学有效性结论。A6b等原有条件/来源缺口仍按现有证据保留，未用组织改善替代缺失证据。上一轮City Scanner独立候选未在本轮重画或集成。

## 文件与安全回退

实际修改：规范目录的`main.tex`、`appendix.tex`、`supplemental.tex`及其编译产物；新增本报告及差异记录。现有脏工作树中的其他用户改动、图资产、绘图源码、CSV、模型和实验配置未触动。

备份：[evaluation_internal_20261103.zip](C:/Cursor/raven.mcs/ccf-review-report/backups/evaluation_internal_20261103.zip)，包括修改前三个TeX、书目、两份PDF与aux；未覆盖旧备份。

[完整源码差异](C:/Cursor/raven.mcs/ccf-review-report/EVALUATION_INTERNAL_RESTRUCTURE_DIFF.md)。若没有后续修改，解压到独立目录后仅恢复本轮三个TeX并重编译；备份PDF可用于查看回退基线。若已有后续用户修改，按差异反向合并本轮B/D/E/F、附录迁移及counter，不能用旧main.tex覆盖整篇新稿。不回退实验、历史停止报告或其他分支文件。

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)
- [补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)
