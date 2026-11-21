# 下一次限定实现申请

明确选择：**规格可实现，申请下一次限定实现**。状态保持WAITING_USER_REVIEW，本文件不是实施或采集授权。

申请只实施一个候选`reachability_stop/observed-feedback-v1`：独立方法配置、无未来预测器的控制接口、完整实际P2与缓存提交绑定、因果消息生命周期、历史L/Q状态与保存恢复、新版本注册固定q适用身份。旧schema/runner有v3及预测器硬绑定，需独立新模块；不改旧方法、不重写原失败。

数量：1个独立实现、4个新增关键路径用例、1个常驻测试worker；真实/随机轨迹0。种子角色：只用明示isolated数学fixture用例ID，无真实数据种子；45001–45003仅预留未来开发，当前不使用。预算：**300 CPU秒上限**，完整根账含检查、编译失败、序列化/启动/监视与保存；GPU0、SGD0、q拟合0、随机回放0、真实控制回放0、新采集0。不重复上一批已经通过的计量/成对设施用例。

实现规模预计为新schema/controller/preview绑定与lifecycle适配、probability身份和4个接口用例；代码与人员成本按一次局部开发预计1–2个开发日，属于设计估计而非实耗保证。300 CPU秒为可用计算硬上限，开发人员时间不计作CPU。若未完成，保留进度报告，不能自动补预算。

成功条件：另一AI按规格无需猜阈值或事件语义；真实完整P2计算/提交一致；同当前池下历史反馈改变非强制动作并由去debt消融解释；注册p/q/Design冻结、唯一消费、age/deadline、缓存失效和恢复字段通过；完整开销被计量且没有绕过2秒。PendingQ可保留并完成独立模块，但只能标隔离输入实现通过，不能标完整生产方法就绪或已有收益。

失败条件：需未知未来/非法q、跨窗口作用无法在真实P2路径出现、关键接口最终失败、数值/信息违规、2秒不可兑现、预算耗尽或必须改变公式/参数。普通工程错误在同规格预算内修复；最终失败提交详细原因/证据/预算及取消任务，再等待用户决定，不自动换候选或采集。

准备依据：源码审计、唯一规则完整定义、有限信息/消费/deadline/debt性质推导，以及精确代数中同池同质量不同Q方向导致CLOSE/WAIT、κ=0后二者WAIT。代数没有真实P2执行，不把它当实现验收；创新性needs-search，任务/控制/预测收益均needs-evidence。

即使下一次实现通过，也只提交结果与概率/首条成本核验的具体申请，再等待审批。后续36条完整开发计划不能自动启动；不恢复t80/v3、动作差值生产证书、七条旧校准、B1或正式确认。原性能门槛和旧失败保留。

本次交付索引：[准备结论](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/METHOD_PREPARATION.md)、[唯一完整规格](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/METHOD_SPEC_CANDIDATE.md)、[性质与限制](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/PROPERTY_LEDGER.md)、[最小证据计划](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/MINIMAL_EVIDENCE_PLAN.md)、[本批预算](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/BUDGET_LEDGER.md)。报告目录只有MD，机器证据存独立results_observed_feedback_preparation_20261013。
