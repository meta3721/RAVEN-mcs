# City Scanner正文证据重组报告

日期：2026-10-17。规范目录：`TO_OVERLEAF_paper_tmc_r1_clean/`。执行ccf-paper-writer、ccf-humanization、ccf-experiment-designer的result-presentation、ccf-integrity-auditor、ccf-visual-composer的表格整合/页面检查，以及ccf-submission-checker的编译与用户页数预算核验。未做官方期刊规则的新一轮认证。

## 完成结果与当前稿保护

已直接修改规范`main.tex`、`appendix.tex`、`supplemental.tex`并成功顺序编译两个PDF。City Scanner现为Evaluation VII-B“Real Sensing Opportunities and Measured Observation”的主要实证，含正文Table II双协议完整10行结果及两段分析，不再仅以附录指引承接。摘要、引言和结论最小联动，保留“序贯参考重建—有限窗口可行校准”的中心机制。

本轮开始及中断恢复后均读取当前文件，确认起点一致；起点已经包含其他AI的S1图表/评分身份、S2假设、S3可访问索引与S4术语修复，不回退历史副本。II—VI逐字保持，已有Appendix A—I内容逐字保持，书目与四幅正文图及原始结果不变。源文件定向差异见`CITYSCANNER_EVIDENCE_REBALANCE_DIFF.md`；临时基线仅用于审查，不是另一套论文final稿。

## 证据为什么进入正文

真实场景结果回答结构校准在实际访问占用及实测观察下的表现；受控站点结果识别Uniform、参考投影、Design与完整P2的独立贡献。两类证据并列，既不把站点构造包装成移动系统实测，也不将真实场景排名替代同支持机制比较。

正文Table II每块保留FedAvg-Window、TwoStage-Hájek、FedAU-Window、ObsUse-Window、RAVEN-Design。列为RMSEμ、WorstGroupRMSE、Δgroup、Δc-s，四位小数mean±样本SD；按协议内部各端点最小值加粗，没有新增显著性星号。客户端是500m×30min占用网格，不是车辆。两块RMSE都采用各自训练集z-score，不能拿0.25对0.71作跨数据集物理预测排名。

- 访问占用块：真实R，受控O/U，10配对种子。RAVEN组失配0.0706最小，但FedAvg的RMSE/WorstGroup 0.2379/0.2489最小。RAVEN配对RMSE相对FedAU/ObsUse为−1.71%/−1.34%，相对FedAvg为+5.59%，均在正文可见。
- Pilot 2：union-GPS R、有限PM实测O、受控U，10配对种子。TwoStage-Hájek预测0.7097/0.7273最佳，RAVEN组失配0.0465最佳。RAVEN相对FedAU/ObsUse/FedAvg的配对RMSE为−0.43%/−0.45%/−0.65%，原−0.5%对前两者门槛仍未通过。NO₂只提供位置；跨块差异不能解释成只改变O的因果效应。

## 原始数值与方法身份核对

访问占用采用`results_c1_cityscanner/round_v1/tables/CS_E3.csv`、`CS_E3_SUMMARY.csv`、`CS_E3_PAIRED.csv`及冻结setup/decision/accepted记录；Pilot 2采用`results_joint_ou/round_v1/tables/JO_E3.csv`及相应SUMMARY/PAIRED/setup/decision/accepted记录。逐方法核对10种子四端点的均值和样本SD、所有既有配对相对差；均在打印精度或保存精度一致。配对相对差没有替换为显示均值之比。当前标准化加载/评分接口与既有复现记录显示训练集拟合z-score，未本轮加载数据模型或重新评分。

六臂采用`results_gatekeeping/round_v1/EXECUTION_REPORT.md`后续Part B、`PREREG.md`修订、`C1_PRIMARY.json`、`C1_ARM_SUMMARY.csv`、`C1_RUNS.csv`、`C1_SECONDARY.csv`、`C1_MAPS.json`及现有实现接口。180个唯一臂/轨迹/模型种子单元=6×10×3，150新增、30复用；这是历史训练归属，不是本轮训练费用。核对全部六臂汇总均值与SD来自10个轨迹内三模型种子均值，没有新增检验、bootstrap或功效计算。

补充Table XXVIII覆盖六臂、ρ、预测与两结构端点，邻文给出实际目标图与零质量处理。控制图1164键含812零键；floor以最小正质量4.78469e−4填零并归一，改变群体边际；M1mu/M2mu按区匹配公共μ，剩70/33零键。Δc-s相对各臂目标，不能作共同目标排名。顶层JSON旧描述提到3568键，但实际checks、注册修订和源码均显示1164键，3568为拒绝方案。采用实际定义，保留原文件。

正文VII-E及附录J-D保留101.9%组对齐改善保留率；主对比先轨迹内平均RMSE，再作ctrl/floor−1，保存HL=−0.019%、95% percentile trace-cluster CI=[−1.89%,+12.28%]、p=.922。宽区间不建立删除成本或等价，floor也不是纯删除干预。全10轨迹保留；去32005只是原敏感性，其区间[−2.32%,+3.53%]仍未确定。四成员次比较无Holm显著，floor/M1/M2的2%非劣链仍未通过。未用独立训练变体追认外生目标固定预测重评分。

## 位置、布局与腾版面措施

- 原附录两张City Scanner排名表合成正文Table II，第9页；原表标签作为兼容别名指向新表。附录J-B/C保留数据构建、过滤、目标、拆分与种子定义，删除重复排名和重复结果讨论。
- 原主表改为受控站点机制角色，现为Table IV，第10页，仍保留全部Design两臂；同支持规则表为V，第11页，数值和耗时完整；消融为VI。集中度VII、开发几何VIII。所有原主表数值单元保持。
- 离线配置与回顾性多端点图移到已有Appendix J-A，合并重复说明；原两式内容及标签保留，现为补充(71)/(72)。正文保留预窗口信息条件、Gate职责及主要代价结论。正文核心方法与理论公式未动。
- 新六臂表位于补充第13页，Table XXVIII。补充表从IX连续到XXX，22张；加正文8张，仍共30张结果表。未删更强方法或恢复重复消融图。
- 合并City Scanner重复过滤/设置措辞及几何说明；学习曲线保持原尺寸，调整为页底浮动，使参考文献和结果能正常排入14页。模板、字号、行距、页边距及图表数据不改。

按排除数学、图表/图注、算法、引用命令的同一近似词数口径：main.tex 6270→6386（+116），appendix.tex 5568→5534（−34），supplemental.tex自身208→208；总计净增加82词，属于证据地位重组而非宣称全文又压缩了多少。搬移不当作净节省。

## 编译、语言与页面验收

当前起点正文14页、补充14页；最终仍为14/14，均含参考文献，满足正文≤14及补充≤正文实际页数。中间补充曾15页，合并重复说明和正常浮动调整后达标。两个最终日志均无未定义引用、重复标签、超宽和重编提示；MiKTeX仅提示未检查更新，本轮未更新环境。书目内容与引用键集合不变，无须凭空增加引用。

手写计数器已与aux一致：正文4图、8表、1算法、41式；补充延续，原两式已迁至附录。所有旧编号数学表达按标签及内容跨文件核对保留，所有原表数值保留。保护II—VI、既有证明及本次起点修复的检查通过。

最终28页全部顺序渲染并目视检查缩略拼页；放大检查正文9/11/12及补充12/13/14页，新10行主表、六臂附表、负结果、来源定义及学习曲线可读，未见裁切、遮挡或异常空白。新主表及六臂表采用全宽footnotesize，未缩小到比原脚注表更小的字号。

Humanization修订了工程式地位宣告、重复短句和统计解释。新增City Scanner正文段落自动语言检查零提示；六臂段落仅有一处分号密度建议，无节奏或错误级提示，人工核读保留必要的并列定义。没有为改善表述删掉不利结果或科学条件。

## 有效边界与待决事项

City Scanner进入正文不证明稳定预测领先、不证明训练充分或超过简单均值，也不改变完整P2各项必要性仍未建立的事实。FedAvg/TwoStage的优势、U-Air Design代价、旧主模型未超过训练均值、Use不显著、默认Debt微小及投影/完整方法取舍仍在正文。

现有包内`cityscanner/`、`cityscanner_p2/`六份排名CSV与原结果逐行一致；材料入口`RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/SUBMISSION_EVIDENCE_INDEX.md`已更新新位置。六臂原始小文件仍明确标为本地工作树local-only，未上传或宣称公开；正式投稿独立材料交付仍需作者安排。原始CSV/JSON、运行、协议和失败报告未覆盖。

原F1预测评分、漂移执行身份、外生目标评分争议及S1余下部分支持身份沿用现有待决记录。本轮不执行无关修复、不启动实验、不把14页达标等同科学或期刊投稿全面验收。具体定位见更新后的`PAPER_CLAIM_EVIDENCE_MAP.md`与`PAPER_EVIDENCE_PENDING_ITEMS.md`。
