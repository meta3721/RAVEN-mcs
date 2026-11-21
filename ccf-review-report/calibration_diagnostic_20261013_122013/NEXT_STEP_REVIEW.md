# 首条校准续行诊断

日期：2026-10-13（Asia/Shanghai）。技能：ccf-experiment-designer，design 模式。

**结论：计量设施已修复并通过限定验证；不建议直接续跑原七条，应先审批“可消费域、显式观测机会及未知支持传播”的单一规格修订。** 这是诊断结论，不是方法或实验验收通过。

状态：**DIAGNOSTIC_COMPLETE_WAITING_USER_REVIEW / RESULTS_NOT_REVALIDATED**。

## D0–D4

|阶段|结果|证据及含义|
|---|---|---|
|D0 身份|诊断通过，18项检查成立|T=100、4300注册、3305步；失败检查点与私有生产者配对、源码闭包、事件/注册/训练输入/决策前缀一致。恢复瞬间未另存快照，不声称独立证明了不中断运行的数值等价。|
|D1 计量|限定设施验收通过|正常父子进程、外层预算终止、内部规划子进程终止均覆盖；Job与逐PID读数差为0。旧外层零值可由启动器挂接竞态复现，旧真实CPU缺口仍未知。|
|D2 支持|诊断通过，根因和边界明确|792/800后备；四个无完成标记格核对正确，未来机会缺R发生层，任一不支持使全决策后备。未重放规划器，不估计全轨迹反事实后备率。|
|D3 概率主张|只能缩窄主张|634条age>5尝试结构性q=0，全R=1尝试重构的正性不成立；群组总体风险的识别需要额外桥接条件，当前证据不能证明。|
|D4 续行方案|唯一待审方案已提交|先定义可消费域与主张，再审批实施；下一建议批仅3个确定性机制检查，0新轨迹、0SGD、0q拟合。尚不可续采。|

本轮没有最终未修复的诊断阶段失败，故不把上述负面科学判断伪装成设施失败，也不覆盖旧STOP。未来实施若不能满足修订规格及原门槛，应另行提交失败报告。

## 本轮实际修改

新增 [windows_cpu_meter.py](C:/Cursor/raven.mcs/scripts/windows_cpu_meter.py)，在Windows以挂起状态创建启动器，加入根Job后才运行；记录解释器、规划子进程、控制台辅助进程的加入、退出和CPU。保留退出进程句柄，独立复核累计读数，预算触发时终止完整Job。

[run_accounted](C:/Cursor/raven.mcs/scripts/validate_conditional_bundle_b0.py:32) 已接入新设施，因此其校准调用方也使用新计量边界。新增限定诊断入口和可复查统计脚本；没有修改 `src/raven_mcs` 中的控制器、预测器、训练、概率或聚合算法。原2 CPU秒规划上限及科学门槛均不变。

完整证据在 [本轮诊断目录](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013)。原首条目录及七份报告只读，101项直接依赖文件保留，原计算源码闭包未改变。本轮训练、SGD、GPU、q拟合、新控制轨迹及规划重放全部为0。

## 交付与审批边界

- [RESOURCE_ACCOUNTING_CHECK.md](C:/Cursor/raven.mcs/ccf-review-report/calibration_diagnostic_20261013_122013/RESOURCE_ACCOUNTING_CHECK.md)：根因、逐PID证据、计费与旧缺口。
- [SUPPORT_DIAGNOSIS.md](C:/Cursor/raven.mcs/ccf-review-report/calibration_diagnostic_20261013_122013/SUPPORT_DIAGNOSIS.md)：决策、客户端资源格、服务尾部、R语义与异常传播；CSV另存诊断目录。
- [Q_IDENTIFIABILITY_NOTE.md](C:/Cursor/raven.mcs/ccf-review-report/calibration_diagnostic_20261013_122013/Q_IDENTIFIABILITY_NOTE.md)：事件、零支持证明、IPW条件及终点。
- [MINIMAL_REVISION_PROPOSAL.md](C:/Cursor/raven.mcs/ccf-review-report/calibration_diagnostic_20261013_122013/MINIMAL_REVISION_PROPOSAL.md)：唯一待审建议及最小预算。

43001现在是已观察的开发/诊断资料，也是原π_boot下的拟合候选资料；是否用于旧规格拟合仍须原资格审查。若批准据此改机制，它只能自动保留为开发证据，不能成为新方法的独立验证或正式确认。未运行43002–43008、B1或正式确认；后续等待用户审批，理由来自本轮执行指令的明确授权边界。
