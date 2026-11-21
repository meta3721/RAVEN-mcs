# 限定校准准备及首条采集报告

日期：2026-10-13。技能：ccf-experiment-designer。状态：**COLLECTION_COMPLETE_RESOURCE_GATE_PENDING / WAITING_USER_REVIEW / RESULTS_NOT_REVALIDATED**。

种子43001的唯一采集轨迹已完整达到 **T=100**：4,300次注册、3,305个真实局部SGD步，GPU0。没有执行剩余七条、q拟合、B1真实16窗、正式确认或旧取消队列。首条仍只作为接口、采集和成本核验，不给出正式校准通过结论。

## 完成的定义与代码

- 消费事件改为明确的`consumed_by_T_v1(T=100)`：完整行政终点与预算中断分开；物理服务删失与消费标签分开。详见本目录 [事件与适用身份修订](C:/Cursor/raven.mcs/ccf-review-report/calibration_first_20261013/EVENT_AND_APPLICABILITY_REVISION.md)。
- 新增`ClockNamespace`及完整概率适用身份：包含初始模型、学习配置、TRAIN scaler、实验终点、服务机制/拟合规则、实际冻结服务参数内容身份；记录运行内时间和发布UTC。
- 新增`DiagnosticPriorQ`，固定事前Beta(1,1)均值0.5、角色`diagnostic_prior`。正式路径拒绝该角色；明确隔离的`calibration_only`入口连接真实FullWindowRunner、既有ClientTrainer和完整P2。
- 注册时冻结q及stage1输入；实际SGD按已观测TRAIN测量值和冻结权重执行。无观测记录保留，缺测量时不以target真值回填。候选0.02/0.20、0.1/4/8、四场景、age5、risk5、cap0.5/ESS3及现有实验门槛不变。
- 保存服务器模型、variance/debt、消息生命周期、概率记录和Torch/生产者随机状态；未来通知队列在独立私有生产者文件，未进入控制器快照。仅回收不可能再消费的张量及本源不再下载的旧检查点，不删除标签/事件。

主要代码位置：

- [calibration_identity.py](C:/Cursor/raven.mcs/src/raven_mcs/control/calibration_identity.py)、[probability.py](C:/Cursor/raven.mcs/src/raven_mcs/control/probability.py)、[schema.py](C:/Cursor/raven.mcs/src/raven_mcs/control/schema.py)。
- [lifecycle.py](C:/Cursor/raven.mcs/src/raven_mcs/control/lifecycle.py)、[planner.py](C:/Cursor/raven.mcs/src/raven_mcs/control/planner.py)、[preview.py](C:/Cursor/raven.mcs/src/raven_mcs/control/preview.py)、[persistence.py](C:/Cursor/raven.mcs/src/raven_mcs/control/persistence.py)。
- [dynamic_control.py](C:/Cursor/raven.mcs/src/raven_mcs/training/dynamic_control.py)、[calibration_first.py](C:/Cursor/raven.mcs/src/raven_mcs/experiments/calibration_first.py)、[conditional_bundle.py](C:/Cursor/raven.mcs/src/raven_mcs/experiments/conditional_bundle.py)。
- [隔离首条入口](C:/Cursor/raven.mcs/scripts/run_calibration_first.py)、[本次恢复入口](C:/Cursor/raven.mcs/scripts/resume_calibration_first.py)、[新增关键路径测试](C:/Cursor/raven.mcs/tests/control_b0/test_calibration_preparation.py)。恢复入口仅针对已记录的首条工程中断，不自动排后续种子；当前再次执行不会覆盖已有输出。

## 输入、种子与历史归属

审计98,710个本地文本文件，以及二进制资产文件名与伴随元数据，未发现43001用于旧方案选择或执行。命中的历史摘要子串、旧待审批计划和本轮授权断言逐项归类；未假称审计了不可访问的外部历史。原审计与复核分别保留。

公共目录在窗0前单独发布，包含30,960行元数据，无TEST目标值或测量值。训练值读取器只读取18,576行TRAIN原子记录及其测量值。维持既有受支持TEST空间×TOD目录质量作为本次事前部署目标，43客户端、172群组；不把旧v1事后读取目录的时序包装为合法新证据。输入字段`target_group`向共享目标接口`target_group_main`做同义别名，不改变群组或质量。

使用旧结果目录中与Design无关的原始数据及划分；未复用旧训练权重、参考质量、模型、预测、旧U或其他策略下载版本。新模型从记录的初始数值状态独立开始。226个受保护历史文件的校验均未发现改变，旧STOP、B0报告及失败结果保持原归属。

## 行为与数值核验

27项相关测试通过，覆盖新增先验隔离、终点/前缀删失、适用身份与跨run时钟、真实runner准入/权重接口，以及原B0生命周期/P2/预测/保存恢复。首次两项失败是Windows临时目录改名权限问题；改用项目内测试临时目录后原测试全部通过，未删除或跳过。

完整采集结束的17项记录核验通过：所有q保持诊断先验并在注册时冻结；所有stage1实际Design=on；模型数值有限；SGD步数等于正观测尝试数；消费唯一；事件/学习/终点/命名空间与冻结计划一致；服务核没有使用20之后的记录；核心源码与采集时内容身份一致。448个Python源/测试/入口文件语法检查通过。实际P2权重最大可行残差 **2.220446049250313e-16**，未放宽1e-7门槛；求解警告与修复/后备记录保留，不把可行修复称为最优性证明。

## 工程中断与恢复

首条在T=20.1、686步时发生规划设施问题：单调用CPU为4.515625秒，超过既定2秒。保留失败检查点、私有生产者和失败账。确认训练入口的顶层导入会在Windows规划子进程中执行；将入口导入移至`__main__`后，同一真实前缀只读核验为1.25 CPU秒，模型/生命周期未变。恢复使用原核心源码、原消息/RNG/命名空间，不重训686步前缀，参数与阈值不变。后续成功调用最大1.640625 CPU秒。该中断不从成本中扣除，首条拟合资料资格仍交用户评审，不自动算校准证据。

## 结果与仍待处理的依赖

- R=1成熟标签3,305条：消费1为1,493，消费0为1,812；995条无观测记录排除拟合但保留审计。完整T的消费删失为0，物理仍未决23条；16条为行政终点未消费。详见 [成熟/删失与支持统计](C:/Cursor/raven.mcs/ccf-review-report/calibration_first_20261013/SUPPORT_AND_CENSORING.md)。
- 正常实际决策1,000次，后备792次：全程 **79.2%**，暖启动之后 **99.0%**。暖启动200次，条件消息束动作7次，实验终点1次。后备均记录缺相容标记或服务尾部风险支持不足。未据此改warmup、risk门槛、特征、评分或场景数；该轨迹不能证明检测收益。
- 续段内部实测进程树CPU为1,345.828125秒，但外层结束计量为0，二者不一致。全批可确认的CPU下界 **1,520.640625秒**；含两项各120秒留额的保守计费为 **1,760.640625秒（0.48907小时）**。留额不是实测CPU，精确全生命周期CPU资源核验未通过。详见 [资源与剩余预算](C:/Cursor/raven.mcs/ccf-review-report/calibration_first_20261013/RESOURCE_COST_AND_REMAINING_BUDGET.md) 和 [当前资源关卡停止报告](C:/Cursor/raven.mcs/ccf-review-report/calibration_first_20261013/STOP_REPORT.md)。

原始证据位于`C:/Cursor/raven.mcs/results_calibration_first_20261013/`，包括冻结计划、审计、测试、失败/恢复记录、完整T100检查点及私有状态；报告目录只放MD。最新预算以`FINAL_BUDGET.json`及追加计费为准，保留原外层零值，不伪造精确实测总额。

检测收益、任务性能不退步和预测收益均未验收；q未拟合、未验证，完整动态概率依据、服务预测检验、完整外部基线及开发比较仍缺证据。T=100不能直接覆盖原拟议T=84的B1消费终点。本批结束，等待用户决定是否继续原定批次；不标记完整IMPLEMENTATION_ALIGNED。
