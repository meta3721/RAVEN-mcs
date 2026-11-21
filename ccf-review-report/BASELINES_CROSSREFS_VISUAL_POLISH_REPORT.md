# 比较方案、定义、跨附录引用与数据图修订报告

## 交付状态

已实际修改规范main.tex和data_figures_revision.py，编译正文与补充材料至引用稳定，两份PDF均14页。七张原有数据图已确定性重绘并集成。**City Scanner优先集成项未完成：数据与表格核对通过，2×2候选已完成，但试排为15页；为遵守14页并保留主表和关键证据，正式稿保留主表，候选独立交付。**未以缩小模板字体、删对照或改变结果腾空间。

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)
- [补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)
- [规范源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)
- [确定性绘图源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/data_figures_revision.py)
- [City Scanner候选PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/baselines_visual_candidate/fig_cityscanner_core_candidate.pdf)
- [完整差异与逐图前后对照](C:/Cursor/raven.mcs/ccf-review-report/BASELINES_CROSSREFS_VISUAL_POLISH_DIFF.md)

实验继续暂停。没有训练、模型加载、推理、评分、优化器调用或新增统计检验；只读源码/配置/已有CSV，并计算绘图所需的既有均值与样本SD。

## 1. 方法介绍与身份核对

Evaluation B先介绍共同骨干与窗口协议，再逐一说明五方案，各自约35–55词，随后辅助比较，再定义指标。

1. FedAvg-Window：观测记录计数加权服务器聚合、均匀局部训练；FedAvg原引用保留，Window明确为本文适配。
2. TwoStage-Hájek：机会/观测校正进入局部Hájek训练和质量m；还包含可用性d，服务器归一化b=md，直接采用参考β，不执行P2或债务。核对 `aggregation/method_policy.py` 的twostage_hajek策略、`aggregation/methods.py` 的TwoStageHajekAggregator及`training/window_runner.py`的局部权重与Stage 2链。不是凭“两阶段”名称猜测只含R/O。
3. FedAU-Window：均匀局部训练、观测计数除以历史参与率；历史attempt/use、ε平滑及未见客户端取1保留在附录F-A。原FedAU引用保留，未移植其理论保证。
4. ObsUse-Window：均匀局部训练，计数除以冻结观测率与历史参与率；没有机会Design、P2或债务。与附录F-A及ObsUseWindowAggregator一致，仍为本文comparison rule。
5. RAVEN-Design：顺序纠正参考加完整P2，协调参考、组目标与债务，Design整运行固定on。

FedAsync、TimeAlign、Local-Hájek；matched-support Count/Uniform/projection；Inst-Cal、移除组件及NoDesign；Central/SimOracle及独立κ=1000规则按用途分开。FedIPW/FedPALS明确只是机制定位，没有冒称运行过的性能基线；不同实验保留各自的方法集合。

## 2. 首次出现与配置命名

摘要保持八句：将结果句的RAVEN统一为RAVEN-MCS，并给TwoStage-Hájek附短描述。TwoStage完整范围在Evaluation B明确，包括U校正。标题、引言及三项贡献没有改写。

公式29（eq:design_factor）本身逐字未改；其后明确RAVEN为框架简称，整运行on/off分别命名RAVEN-Design/RAVEN-NoDesign，并说明lagged ratio/因子1及其余步骤相同。没有声称此前未定义，也没有把Gate改成开关。相同步骤不等于活跃支持相同，U-Air的支持变化说明保留。

主要方法正文阅读顺序：TwoStage-Hájek先在摘要附短描述，再于B实质定义；两种RAVEN配置先在公式29后定义，再于B引用；FedAvg-Window/FedAU-Window/ObsUse-Window于B首次实质定义，早于对应应用表。相关工作的FedAU原方法、DeFedAvg未当作Window适配提前误用。各方法源行索引保留在本轮checks.json的names中；主图已统一RAVEN-Design，2S-Hájek与省略Window的映射在B集中说明。

## 3. 指标、跨附录引用与版面取舍

- 先定义deployment-group与client–stratum两种L1距离、范围[0,2]、方向及pp=50Δ，再解释Target RMSE、组内归一化WorstGroup、不同于它的Tail（UTC块2/3），最后说明实测wall-clock成本。
- 保留原RMSE公式、训练尺度17.363/575.776、City Scanner各协议训练尺度及物理/标准化区别。SD、CI、配对单位、Holm家族、+.5%描述容差和2%正式非劣界仍集中于C，未重检验或改变阈值。
- `tab:nearest_neighbor`保留补充完整版：五方法定义及City图优先于重复机制表；正文写Supplementary Table，明确并非性能基线。
- `tab:underserved_block`、`tab:f1_mechanism`、`tab:app_a5_a6_audit`、`tab:cityscanner_sixarm_cs`均保留补充，正文直接写Supplementary Table并自动编号。六臂client–stratum目标不同的边界保留。
- arrival-support表及附录结构图不提升：正文已有决定性几何解释，新增会重复占用版面；原formal/arrival/development分母分开。
- City Scanner已先后尝试完整候选和紧凑2×2集成，正文仍为15页。最后保留14页正式稿及候选；没有删除表II，未把未集成写成已完成。本轮已在允许范围内压缩重复设置、移除各RQ与标题重复的两行导语，未改结果段的效应数字或排名。

## 4. 数据图逐项结果

1. 图2风险语义：RAVEN-Design显示名、2S缩写映射、较轻纹理与边线，方向轴改Seeds with D<0；仍为原五方法20种子，均值±样本SD，18/18/17/17/17计数及分母20、零线和10线。紧凑高度下字号不变，误差线完整。
2. 图3机会诊断：减轻真实R纹理；原质量、TV与0.05诊断线不变，SS/UA协议说明保留。不是性能图。
3. 图4Design：减轻Estimated/Oracle纹理，保留错位三位小数标注、引线、NoDesign分母、正值更差和近零数值；脚本文字包围盒检查通过，没有伪造区间。
4. 补充图5/6：六方法与原240行过滤、种子30001–30020、完整均值±样本SD及RAVEN-Design身份不变；沿用已清楚的横向区间图，未提升不同支持图为matched-support比较。
5. 补充图7：降低重叠散点透明度，保留所有243个CERTIFIED窗、10个误覆盖点、62窗时间线及RESET 42；轴名与子图文字分开，身份仍是coverage-controlled变体。
6. 补充图8：沿用2×3、log遍历、200×3种子均值/min–max、物理单位与原最强适用基线规则；没有平滑或改成CI。版式已清楚，本轮只同源导出并补SVG。
7. City Scanner候选：紧凑2×2保留两协议五方法的组失配及target RMSE。由CS_E3.csv/JO_E3.csv各十种子均值±样本SD生成；逐字段核对主表三项端点的均值/SD四位小数一致（完整worst-group仍在主表/原2×3候选）。种子32001–32010与33001–33010；组降幅口径不变。无跨协议尺度合并，未只画有利组端点。

候选、PDF/SVG/PNG及统计账本统一在 `figures/baselines_visual_candidate/`。七张正式图在原文件名下集成；旧候选目录未覆盖。每张图的同方法颜色/点形保持，RAVEN为低饱和蓝；没有用图像生成模型。

## 5. 核验与仍未解决项

最终MiKTeX顺序编译成功，aux稳定，正文14页、补充14页。正文8表4图、补充连续编号5–8未变。检查最终正文全部页、补充受影响图页及候选，未见裁切或遮挡；图1仍在III，引言没有图表编号引用。日志无Overfull、未定义引用/文献、重复label或缺字。

完整表格环境、编号公式、算法与理论证明和引言/结论逐项对比均保持；附录、书目、make_figures.py、图1源和全部figure_data CSV逐字节未改。各七图统计账本与原账本逐字段一致；PDF均为矢量路径，无嵌入位图。完整校验为 `tmp/baselines_visual_20261102/checks.json`，City主表核对为city_table_check.json。

未完成的唯一集成项为City Scanner图进入14页正文。候选证据和可复现代码已交付；在不删除当前必要材料或越界压缩其他章节的约束下，本轮未解决其空间。缺少种子列的Design汇总及coverage窗口文件仍沿用原报告记录的身份缺口，没有猜测补齐。运行成本不升级为跨平台效率，任何结构结果均未升级为预测保证。

## 6. 回退与复现

修改前备份：[baselines_visual_20261102_123554.zip](C:/Cursor/raven.mcs/ccf-review-report/backups/baselines_visual_20261102_123554.zip)。文件原样核对可读取，不覆盖既有备份。主要恢复对象为main.tex、data_figures_revision.py及七图的PDF/PNG；新增SVG可保留为未引用资产。若无后续修改，可从ZIP独立解压后恢复这些文件，并顺序编译main和supplemental。若已有后续工作，按DIFF反向合并本轮命名、B/C设置、图表引用及导语去重，不能用旧整篇main.tex覆盖用户新改动。不要动实验、模型、配置或历史STOP_REPORT。

复现示例：在已有绘图依赖环境运行 `data_figures_revision.py --only fig2_e2 fig_g3_tdrive fig_w1_design_gate fig3_structural fig4_prediction fig_certificate fig_learning_capacity fig_cityscanner_candidate --out figures/baselines_visual_candidate`（从规范论文目录）。只调用上述选定函数；未执行make_figures.py总main。现有隔离依赖目录为项目tmp/data_figures_revision_20261026/site-packages，不改训练环境。

# Visual contracts (before rendering)

All plots are deterministic vector PDF/SVG with PNG previews, using existing data and existing filters. RAVEN uses muted blue plus a distinct marker/hatch. No new tests or scores.

- Risk semantics: RQ1, FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv, original five methods/20 seeds, mean±sample SD and D<0 counts; two panels; 3.5-inch single column.
- Opportunity mass: RQ1, FIG_G3_TDRIVE_H_MASS.csv and FIG_G3_TDRIVE_TV.csv, unchanged mass/TV, two panels, zero-origin bars; 3.5-inch column, .05 diagnostic line.
- Design: RQ2, FIG_W1_DESIGN_GATE.csv, four existing summary rows, no uncertainty invented; two panels, signed percentages over NoDesign; 3.5-inch column.
- Structural and prediction intervals: supplementary, original six methods and 240 filtered rows each, two datasets×two metrics, mean±sample SD complete; 3.5-inch column, separate support identity retained.
- Coverage: supplementary legacy coverage-controlled diagnostic, FIG_CERTIFICATE_WINDOWS.csv, all certified/miscoverage points and original timeline; 3.5-inch column, axes unchanged.
- Learning: supplementary development protocol, selected R2 CSVs and original baseline-selection rule, 2×3, three-seed mean/min–max, log passes, physical units; 7.16-inch full width. No smoothing.
- City Scanner: RQ1, CS_E3.csv and JO_E3.csv, five methods/ten seeds each, mean±sample SD, 2×2 group mismatch/target RMSE; 7.16-inch full width. Each row uses its own training scale; complete worst-group/client–stratum endpoints remain in main table.
