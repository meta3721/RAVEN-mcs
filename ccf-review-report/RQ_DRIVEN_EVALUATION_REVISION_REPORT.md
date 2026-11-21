# RQ驱动Evaluation重组与编译报告

本轮执行了 `raven-mcs-rq1-rq3-evaluation-rewrite-instructions.md`（2026-11-01修订版），使用 ccf-paper-writer 完成实质改写，并按 ccf-humanization 检查表述。实验继续暂停；未训练、推理、重评分、回放、重新求解或重新进行统计检验。

## 1. 正式交付与修改范围

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)
- [补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)
- [main.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)
- [appendix.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex)
- [逐项说明及完整源码差异](C:/Cursor/raven.mcs/ccf-review-report/RQ_DRIVEN_EVALUATION_REVISION_DIFF.md)

实际编辑限于 main.tex 的 Evaluation 及 appendix.tex 的对应内容位置、标题和引用。Evaluation之前的标题、摘要、引言、贡献、系统模型、方法与理论，以及Conclusion及其后文本，逐字保持不变。supplemental.tex 和 reference.bib 保持不变。图片、绘图代码、实验数据、模型、配置和历史停止报告未改。

范文 MapT-STC 第10–15页用于借鉴“先列问题—介绍数据及比较设置—逐项回答”的组织方式；未采用其问题内容、结果、划分或方法结论。

## 2. 新结构与各RQ的实际回答

Evaluation开头先说明三个评价层次，再一次性列出：

1. **RQ1:** How effectively does RAVEN-MCS align aggregated client contributions with deployment targets under sequential sensing and update selection?
2. **RQ2:** How do reference reconstruction and feasible calibration contribute to deployment-group alignment on matched client support?
3. **RQ3:** How do target support and aggregation constraints shape the feasible adjustment of deployment-group mass?

随后依次为 A. Datasets and Selection Protocols；B. Baselines and Evaluation Measures；C. Implementation and Statistical Settings；D. Deployment-Target Alignment (RQ1)；E. Mechanism Contributions (RQ2)；F. Target Support and Feasible Adjustment (RQ3)。各结果小节均以比较目的开篇，以现有证据的直接答案收尾。

### RQ1：整体部署目标对齐

**答案：**完整RAVEN在两套City Scanner协议的五方法比较中取得最低平均组失配；预测及其他结构端点具有各自的实际领先方法。T-Drive与NSW协议的结果限定了这一应用结论的范围。

- 正文第9页表II `tab:cityscanner_real`：相对TwoStage-Hájek的组失配降幅25.8%和23.3%，保持“种子均值之比”，未改成平均成对降幅或百分点。
- 两协议分别包含真实机会、受控观测与交付，以及实测观测、受控交付，未写成两个独立数据集或完整真实部署验证。
- 风险语义图2说明部署目标风险与到达风险的评价分布不同；该现象不归为RAVEN独有优势。
- 第10页表III `tab:tdrive_hybrid`、图3及相应附录保留真实机会诊断、T-Drive与NSW跨协议实际排序，包括不利的Design/预测/组端点。

### RQ2：参考重构与可行校准的机制作用

**答案：**Count到Uniform解释了大量结构变化；在共同支持与约束上，纠正参考投影仍提供独立的组对齐增量。完整P2协调不同结构端点与成本，不能概括为优于简单投影的所有端点。

- 第11页表IV `tab:trained_rules`：按 Count→Uniform、直接参考→投影、Uniform→投影、投影→完整P2 的顺序解释。直接参考仍限于已有离线结构读出，没有增加预测或时间结果。
- SensorScope的0.768 pp、U-Air的0.286 pp属于投影相对Uniform。独立的SensorScope projected Design-on/off 的0.922 pp未与前者相加，均未归为完整P2相对投影的收益。
- 保留简单投影在SensorScope组端点及运行时间上的优势，以及完整RAVEN在部分客户端—分层端点的不同表现；预测不显著未改成等效。
- 第11页表V `tab:main_effectiveness`、图4紧随规则比较。U-Air的774配对窗口、51.6%活跃集重合及支持变化说明紧邻Design对照，不能承担同支持权重干预解释。
- 第12页表VI `tab:e4_ablation`保留Obs、Use、Inst-Cal、Debt的端点取舍及统计结果；标准Debt量级小与独立κ=1000敏感性规则分开。
- Local-Hájek退化与F1机制材料解释校正输入及归一化作用，未恢复未闭合的F1预测结论，未称一般MNAR纠偏。

### RQ3：目标支持与约束决定的可调空间

**答案：**支持决定哪些组质量能够被代表，cap与ESS限制这些质量能够如何调整；权重自由度、组成自由度和预测敏感性是不同对象。

- 第13页表VII `tab:cityscanner_sixarm`由原应用段迁入本节。控制图、floor、外部形状与Design保持各自含义；10条trace各3个模型种子未改成30条独立trace。共同组目标与各臂客户端—分层目标仍分开。
- 保留floor改变目标边际的事实，预测2%非劣未建立，以及3.83%、4.14%、8.15%的上界和原有区间、检验结论。
- 正式窗口的forced-Uniform比例78.6%、90.2%、79.0%及各分母保持原样。3279窗口的L1组成评价范围近乎平坦，未推成P2平方L2项恒定。
- formal traces、arrival logs与development protocol分别说明；开发轨迹K=8、ESS=4、cap=.25、可调目标质量等几何结果不与旧主实验窗口混算。
- 概率下限/上限触发、稳定化误差、参考扰动及估计/真实边际比较作为辅助解释。A6a仍为稳定化误差项为零的充分条件；共享状态/A6b未写成已核验；宽松最坏界未写成紧的数值预测。
- 第13页表VIII `tab:target_concentration`保留集中度梯度、原区间和实际意义标准；所评估oracle未称为所有策略的严格上界。

## 3. 内部“贡献—证据—匹配”对应

以下对应仅用于本报告定位，不是新增统计置信度或论文结果：

1. **重建参考与可执行聚合的连接：**RQ2的规则阶梯及同支持投影比较检验参考增量和可行化；RQ3的支持几何解释可执行空间。它们不证明完整P2的每个额外项均必要。
2. **感知单元目标、顺序选择与信息边界：**原有方法定义及条件证明承担理论论证；风险语义实验解释评价对象，Local-Hájek/F1材料解释输入与归一化机制。City Scanner整体比较不等于三个选择层的独立验证。
3. **应用组对齐及机制认识：**RQ1的两套City Scanner协议承担完整方法的主要应用证据；RQ2区分Uniform解释的部分和参考增量，RQ3解释支持限制。结构结果不升级为普遍预测领先。

## 4. 段落和图表迁移

- 原Experimental Setup拆为A–C；其中提前出现的离线结构效果移到RQ2。
- 原Real Sensing Opportunities and Measured Observation的两套五方法应用比较归RQ1，六臂目标支持段与整表归RQ3。
- 原Risk Semantics and External Protocols归RQ1；arrival-weighted验证效果并入相关评价分布说明。
- 原Design Effects与Attributing Structural Gains归RQ2；U-Air支持变化解释与其对照保持相邻；求解数值诊断简述后指向既有附录。
- 原Prediction Sensitivity and Adjustment Geometry归RQ3；目标支持、几何为主体，参考扰动和集中度为辅助。
- 原训练均值/测试标签拟合常数细节迁入附录K的Formal-Protocol Prediction References；正文仍明确正式站点模型未超过训练均值，开发验证改善与之属于不同协议。
- 原完整更新规则/优化器敏感性两段迁入附录K的Update-Rule Sensitivity；原数值、预算、区间完整保留。
- 独立释放/停止分支与coverage-controlled变体已有详细附录M、I；删除正文重复摘要，保留原附录轨迹、结果和身份，包括coverage-controlled的Design:=Gate，未改名为主方法结果。
- 删除/合并重复配置说明、审计式过程说明和重复限制收尾；保留会改变比较解释的支持条件、统计结论及不利排序。没有用内部“通过/失败/中等匹配”替代RQ答案。

正文表格编号及PDF页码（修改前→修改后）：

- 数据概况 `tab:datasets`：I/p8 → I/p8。
- City Scanner五方法 `tab:cityscanner_real`：II/p9 → II/p9。
- T-Drive `tab:tdrive_hybrid`：IV/p10 → III/p10。
- 实际训练规则 `tab:trained_rules`：VI/p12 → IV/p11。
- Design对照 `tab:main_effectiveness`：V/p11 → V/p11。
- 组件移除 `tab:e4_ablation`：VII/p12 → VI/p12。
- City Scanner六臂 `tab:cityscanner_sixarm`：III/p10 → VII/p13。
- 集中度梯度 `tab:target_concentration`：VIII/p12 → VIII/p13。

表、图仍各有唯一正式位置。正文仍为8表4图；补充表/图继续从IX/5编号。图1仍在第三节。图2–3服务RQ1，图4服务RQ2；没有新增重复结果图。全部原label保留且无重复；旧 `subsec:eval_rq3` 作为机制段的兼容label保留，新RQ3用 `subsec:rq3_adjustment`，未按旧名称误配语义。旧混合限制段label移至真实承载coverage诊断的附录位置。

## 5. 数值、统计与语言核验

- 按label对照修改前后，正文及附录的完整table/figure环境（含数据、说明、label）均相同，仅位置和自动编号变化。
- 编号equation/align、proof、theorem、proposition、corollary、restated及algorithmic环境均保持原样。
- 保留均值±样本SD、配对区间、trace-cluster分析、种子均值之比、既有Wilcoxon/Holm家族、数值tie阈值、描述性+.5%容差及正式2%非劣界；未重新统计或改变阈值。
- 只读核对现有20种子配置：SensorScope和U-Air均为2个局部步，窗口预算分别100/80。依据为 `artifacts/e3_formal_runs_r1/runs/{sensorscope,uair}/raven/seed30001..30020/config_snapshot.json` 与 `window_metrics.json`。未补造学习率或扩大到其他协议。
- humanization检查后以发现和机制开篇，合并重复防御性限制。自动语言检查的一条等长句提示对应原有技术表注，另一条分号密度提示包含数学及表格分隔；保留必要统计说明，未为消除提示改变证据。
- 近似词数采用同一脚本：Evaluation范围内去除数学、LaTeX命令和浮动体后的英文词数，**3430 → 3491（+61）**。新增RQ和必要机制连接抵消了重复文字删减；本轮不声称全文净压缩。

## 6. 编译与页面验收

使用现有MiKTeX工具链、单进程顺序编译正文与补充，更新两份书目并交替编译至aux稳定。最终8次工具链调用成功，交叉引用稳定。

- 修改前：正文14页，补充14页。修改后：**正文14页，补充14页**。
- 最终日志无LaTeX错误、未定义引用/文献、重复label、缺字或Overfull警告。
- 阅读最终两份PDF全部28页的分页预览，并放大检查重排结果页、迁移后的附录页；未发现图表裁切、遮挡、明显异常空白或悬空图例。
- 图1位置、引言无图表编号引用、正文表引用集中在Evaluation及之后的安排保持。
- 可复核的编译与范围检查记录保留于 `C:/Cursor/raven.mcs/tmp/rq_evaluation_20261101/` 的 `citation_build_status.json`、各编译日志、`checks.json`、分页预览和差异文件。未运行模型或性能测试。

## 7. 仍未由本轮解决的证据问题

本轮是组织与表述修订，不升级证据：三层校正的独立贡献、完整P2所有项的实际必要性、普遍预测收益、各敏感性比较中的非劣/等效、共享状态/A6b的经验核验，均未因重组而确立。F1未闭合预测、身份未闭合漂移、存在评分争议的外生目标排名及独立停止分支未新增到核心证据。已有理论仍由其证明和条件支撑，实验未被写成渐近恢复、误差界覆盖或无条件长期实现的验证。原有复现信息缺口未通过猜测补齐。

## 8. 回退入口

修改前备份：[rq_evaluation_20261101_234754.zip](C:/Cursor/raven.mcs/ccf-review-report/backups/rq_evaluation_20261101_234754.zip)。归档已核对可读取，包含原main.tex、appendix.tex、supplemental.tex、reference.bib、两份PDF及编译辅助记录；未覆盖旧备份。

若之后尚无新修改：将归档解压至独立临时目录，核对其中论文路径，仅恢复本轮改动的main.tex、appendix.tex及对应两份PDF，再按现有流程顺序编译以更新辅助文件。supplemental.tex和reference.bib本轮未改，无需恢复。

若之后已有论文修改：以本轮完整差异反向合并Evaluation及附录迁移部分，保留后续内容，再重新编译；不得直接用归档main.tex覆盖后续用户修改。不要恢复或修改实验数据、配置、模型、历史STOP_REPORT或其他分支资产。备份与本轮报告保留。
