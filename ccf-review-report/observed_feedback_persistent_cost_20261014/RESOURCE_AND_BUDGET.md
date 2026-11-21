# 90 CPU秒批次资源账

日期2026-10-14。最终状态**PERSISTENT_REQUEST_COST_CHECK_PASSED / WAITING_USER_REVIEW**，本批计费**35.187500/90 CPU秒**。

- 唯一常驻A/B测试整调用：Job3.500000、外层启动/驱动.281250，合计3.781250 CPU秒，墙钟4.666787秒，根审计通过。
- 只读历史/证据核验：Job1.250000、驱动.156250，合计1.406250 CPU秒，墙钟1.879183秒，根审计通过。该进程没有加载控制器/数值求解，不是第二个测试worker或新增请求。
- 审查/读写/语法检查/文档交付保守30秒；未逐项实际测量UNKNOWN。包含初始只读路径查询失败、协议冻结及结束MD/链接核验，不冒充实测30秒。

互斥根测量合计5.187500秒，计量调用墙钟合计6.545970秒；剩余本批帽54.812500秒不授权追加请求或采集。初始累计4730.046875，本批后**4765.234375**；原5小时名义余额**13234.765625** CPU秒，历史实际缺口仍UNKNOWN，余额不授权后续3600秒申请。

测试初始化/A/B根验收上界分别3.051250/.270000/.176250秒，符合本轮6/2/2边界。整测试根费3.781250；其中列出的实际初始化/请求样本段3.437500，余下.343750包含桥/间隙、完整审计、数值核对、关闭/退出及最终monitor。局部计时、PID下界和.+02上界为复核，不再加到根总额。启动器bootstrap已含在完整驱动账与初始化段，不重复计费。

唯一新数学常驻worker、2次只读判断、1次实际原P2求解、1次cache命中。SGD=0、GPU=0、q拟合=0、新真实/随机轨迹=0、控制回放=0、实际模型提交=0；没有实际producer、diagnostic_prior采集入口或首条训练。45011只为待审建议；45001–45003及正式确认种子未用。

没有有效请求失败或性能重试。PID字段补正由已保存证据完成：原Popen句柄指启动器，实际worker区间来自其process_time和最终根保留PID，完整根上界均不变；没重新测试或放宽门槛。原旧P3冷失败/STOP/结果身份保留，1657个保护文件核验无变动。

新增代码位于scripts/observed_feedback_persistent_cost_budget.py、observed_feedback_persistent_worker.py、check_observed_feedback_persistent_cost.py及audit_observed_feedback_persistent_cost.py；改动只是显式初始化/常驻请求接线、必要单份响应、原完整审计一次输出及计量。既有OF公式、聚合器、概率/生产训练授权源码没有修改；不将新测试通道称为已实现生产采集入口。新增代码语法检查及实际A/B/只读审计通过，未重复旧四套、Job或成对保存设施基准。

MD交付在ccf-review-report/observed_feedback_persistent_cost_20261014；机器输入、请求、审计与根账在results_observed_feedback_persistent_cost_20261014。本次数学资源初始化未覆盖真实模型/数据/优化器；真实SGD、事件增长及完整producer队列费用仍UNKNOWN，由下一申请同一run限定首步核验，不将本次费用点承诺为生产费用分布。

[整批账](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/FINAL_BUDGET.json)、[互斥测试账](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/persistent_A_B.meter.json)、[证据审计](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/FINAL_DELIVERY_CHECK.json)。
