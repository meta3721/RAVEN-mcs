# OF-v1停止与论文证据整合

## 已落实的停止范围

检查时间：2026-10-18T12:28:08.7269443Z。用户决定停止OF-v1、OF-no-Q-stop、GAP20-fixed-reference的新增训练、自主轨迹、搜索、q拟合、种子扩展和完整P3排程；不涉及其他分支，不删除窗内RAVEN的Q及更新。

按分支脚本、run_id/结果目录和命令行核验，排除审计进程自身后活动匹配数0。Windows任务计划已读取动作字段并匹配本分支，匹配0；本地Codex automations匹配0。聊天查询上限50，实际返回可见最近10条及全部置顶（0条），其中无匹配实验任务。没有执行进程终止或排程暂停，不能写成已杀死任务。交付前于2026-10-18T14:39:24.4745554Z再次定向检查进程，匹配仍为0；其他分支不受影响。

旧STATUS.md为早期E1/P10状态，不管理OF-v1，不改写。没有为此建立新队列系统；本记录是用户停止决定的现行交接入口。历史WAITING_USER_REVIEW、STOP/失败报告及冻结参数均保留。

实验有效性与安排分开：小范围对照T100完整有效，科学结论L_MECHANISM_UTILITY_NOT_ESTABLISHED保留；后续扩展由用户决定停止，完整P3没有完成。本轮新增训练、推理、采集、回放、求解、统计检验均为0。

## 已保留资产

- 原四臂：results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1及results_observed_feedback_autonomous_pilot_45001_recovery_20261015中的fixed05_resume1/fixed2_resume1/noqstop。
- 新诊断：results_of_v1_small_scope_20261018_190539/，原DECISION/失败记录、CSV、FREEZE、控制器及轨迹均只读保留。
- 共同父点：results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop/trajectory/tick0200.complete.json。
- 新终点：results_of_v1_small_scope_20261018_190539/gap/trajectory/tick1000.complete.json。

## 论文修订与编译

已原位修改规范main.tex、appendix.tex、supplemental.tex并成功编译main.pdf和supplemental.pdf。修订前正文14页、补充14页；最终仍为14/14页（均含各自参考文献），满足正文不超过14页、补充不长于正文的要求。没有用迁移宣称净节省完整页数，没有改模板、字号、边距、行距或使用负间距。

- **正文第13页，Evaluation的Update-Rule Sensitivity and Coverage Scope**：新增约60词的单段，区分关窗时机和窗内权重。保留129/799动作变化，以及H相对S窗口缩短30.08%、G增加0.02584的成对发现。附录指向由LaTeX解析为L-A。没有改写摘要、引言贡献、方法、理论或结论。
- **补充第13–14页，附录L-A，Release-Timing Reference Study**：新增约310个空格分隔词项（含公式、排除表体的粗计），说明Traffic单一已使用开发种子45001、真实TRAIN、完整P2与学习配置、q=.5诊断先验、共同t20分叉、实际滚动/固定参考及指标。预测精度没有评价。
- **补充第14页，表XXXII**：全部五策略及G/W/J均入表，六位小数、越低越好。保留OF与去额外停止项相同、固定2质量较好而窗口较长等实际排序；没有把同值行作为重复样本。
- 为容纳新增证据，压缩附近开发学习/几何、服务器更新敏感性、City Scanner附录协议及重复图表标题，保留全部数值与关键比较条件。将旧Projection-with-Debt Sensitivity合并到P2诊断E-A（补充第7页），保留app:trained_rule_probe及app:kappa_probe标签；它仍是独立kappa=1000敏感性规则。学习曲线只调整标准浮动位置，图像及宽度不变。City Scanner正文主表和六臂布局保留。

## 数字、身份与语言核验

按ccf-paper-writer及ccf-humanization完成修订，并按ccf-integrity-auditor核对新增主张：

1. 从五臂CLOSURES.json重新求原定义的G/W/J，与CSV和原验证摘要在1e-12绝对容差内一致。没有模型加载、重新预测、求解或新增检验。G差的浮点求和差异约5e-15，不影响显示精度。
2. 从A_PER_GRID逐行核对799格、582自由格、129次CLOSE→WAIT，以及参考差均值/中位数；从t20实际关闭记录核对c_ref=ell+.02*age。H/S自主轨迹与同状态影子动作没有拼成一个效用试验。
3. 五臂合法终点标记存在，所指model/private文件存在且大小与标记一致。本轮没有重新读取或复制这些大型模型；最终配对可读性依赖既有C_VALIDATION和原各臂验证记录，不冒称本轮重新加载验证。
4. 三臂暖启动关闭记录的科学字段一致；策略相关fingerprint/dependency_hash及概率/时钟命名空间不同，不写成全部身份相同。新S臂来源为合法noqstop/tick0200，不是B的SGD0验证点。
5. 对本轮编辑前工作树做内容比较：正文原37个数学环境、9个表体；附录原28个数学环境、22个表体均原样保持。正文几何段之前全部内容、结论及数据代码说明之后全部内容不变；附录P2诊断之前的全部证明及既有内容不变。正文仍为41个编号公式，补充硬编码起点不变；新增两行控制式不编号。
6. 无新增文献，未改reference.bib及既有书目内容。没有将CPU费用、审批枚举、失败门槛、内部文件名或C盘路径写入论文。语言检查无硬错误；紧凑定义与结果句触发的句长提示及一次分号密度提示已人工复核，没有为了机械清零删掉必要条件。

可读差异：[OF_V1_PAPER_REVISION_DIFF.md](C:/Cursor/raven.mcs/ccf-review-report/OF_V1_PAPER_REVISION_DIFF.md)。逐项原始字段：[OF_V1_PAPER_EVIDENCE_MAP.md](C:/Cursor/raven.mcs/ccf-review-report/OF_V1_PAPER_EVIDENCE_MAP.md)。临时机器核验为tmp/of_stop_paper/final_evidence_audit.json，状态PASS。

## 编译与页面验收

使用项目现有MiKTeX pdflatex，禁用自动安装，单文档顺序构建，子进程BelowNormal优先级；未并行实验或编译。按main/supplemental外部aux依赖重复构建，最后两者退出码均0。正文与补充引用已稳定，没有未定义引用、重复标签、待重跑提示或Overfull框。

正文保留25处、补充34处Underfull提示，未为清除全稿提示越界重排；已阅读受影响的正文第13、14页、补充第7、12、13、14页，新增段落、控制公式、五臂表、学习表和曲线没有截断、遮挡或异常空页。表XXXII和必要单位说明完整可见。交叉引用为附录L-A（补充13页）、表XXXII（补充14页）、旧敏感性E-A（补充7页）。

编译日志及逐页渲染仅保存在tmp/of_stop_paper，不向ccf-review-report放置非MD产物。规范PDF留在论文原目录。

## 停止后的有效资产与成本归属

完整索引及参数来源见证据对应记录。新增小范围比较的CSV、FREEZE、gap_local.py、stage_c.py、ARM_FROZEN_PLAN、C_VALIDATION、A_RESULT、A_PER_GRID和合法父点/终点保留原路径。B阶段的开发失败尝试、SGD0验证状态、历史故障及旧STOP/DECISION均未删除或覆盖，不能当作额外独立效用样本。

已有小范围批次费用仍按BUDGET_FINAL.json截至2026-10-18T11:50:43.800911+00:00的原记录：已审计根CPU411.890625秒，另保守占用50秒（实际未知），预算记账461.890625/1000秒；活动墙钟包络3144.253177秒。唯一S臂根CPU356.15625秒、会话墙钟2036.9170513秒是包含项，不再相加。历史各臂费用另在原RESOURCE_AND_BUDGET.md，未并入本批或形成加速比。

本轮是独立的论文整理与编译，不是原采集预算的自动续行；没有将原预算余额授权为新实验，也没有将这些历史费用冒称本轮编辑实耗。本轮编辑/编译没有完整根计量，CPU及墙钟总实耗未知。新增实验、SGD、采集、模型推理、q拟合、回放、P2求解、参数搜索及统计检验均为0。

没有新增公开上传或复制共享模型，没有改变本地复现归档范围，因此Data and Code Availability按原文保持，不声称控制资产已打包或公开可下载。原结果记录中的paper_modified=false描述其历史交付时刻，未被重写为本轮状态。

## 未解决问题与交接边界

本轮停止安排与论文整合完成；不再自动继续OF-v1/OF-no-Q-stop/GAP20新增实验、校准、扩种子或完整P3。保留L_MECHANISM_UTILITY_NOT_ESTABLISHED。单种子结果不能回答多种子控制效用、概率校准、充分训练后的预测表现或训练不退步；这些缺口没有被文字修订解决。没有把效用未达标归因于电脑配置。若将来重新研究该分支，需要用户另行明确批准范围与预算。

