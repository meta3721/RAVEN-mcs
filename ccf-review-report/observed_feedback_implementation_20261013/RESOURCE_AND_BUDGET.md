# 资源与预算

状态：WAITING_USER_REVIEW。最终四用例在一个常驻worker内通过。

本批计费 **137.968750/300 CPU秒**。实际互斥进程树+驱动测量合计 63.968750秒；另有两次根发布异常各22秒保守计费（Job/驱动实耗缺失），以及阅读/编辑/交付保守费用30秒。保守费用不是实耗；历史及未逐项计量缺口仍UNKNOWN。

计量调用墙钟合计 132.090271秒；旧累计4557.296875秒，本批后累计 4695.265625秒，原5小时名义余额 13304.734375秒，余额不授权后续。

最终 30 个完整当前请求（含预期PendingQ拒绝）最大保守根费用上界 0.645000秒，全部≤2。分类示例：

- STARTUP_AND_FIRST_MIN_CLIENTS：根上界 0.645000秒，进程CPU 0.421875秒，墙钟 0.587114秒，P2=0, cache=0。
- COLD_COMPLETE_CURRENT_P2：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.068417秒，P2=1, cache=0。
- P1_history_Q_first：根上界 0.035625秒，进程CPU 0.000000秒，墙钟 0.051620秒，P2=1, cache=0。
- P1_no_Q_stop_a：根上界 0.051250秒，进程CPU 0.015625秒，墙钟 0.051355秒，P2=0, cache=1。
- P2_K_below_three：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.048684秒，P2=0, cache=0。
- P2_deadline_24.0：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.051616秒，P2=1, cache=0。
- P2_empty_deadline：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.051033秒，P2=0, cache=0。
- P2_terminal_smallK：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.047315秒，P2=1, cache=0。
- P4_real_backend_success_commit：根上界 0.020000秒，进程CPU 0.000000秒，墙钟 0.052661秒，P2=None, cache=None。
- P4_pair_save：根上界 0.785625秒，进程CPU 0.671875秒，墙钟 1.857122秒，P2=None, cache=None。
- P4_pair_restore：根上界 0.473125秒，进程CPU 0.453125秒，墙钟 0.509272秒，P2=None, cache=None。

完整根费用窗口含监视，首次含Python/启动器成本。短区间Job量化时，使用max(原根差+0.02，PID区间+互斥monitor差+0.02)进一步保守校验，不能把PID再加进整批费用；这是提高上界，没有降低门槛或移动请求边界。

大类operation行包含内层请求，不能累加这些重叠行；整批账以charge文件为准。提交、模型加载、保存、恢复和关闭均保留在根Job从创建到退出费用中。P2列指完整目标求值/计算，单点可行域为精确解析解；仅K>3调用原数值求解器，另有一个显式原完整preview参考。未计算纯d，记录null。43客户端及冷启动有自由度的大池费用未验，不承诺生产2秒。

首次请求及一次冷数值加载曾超2秒；后按同约束的精确单点P2和懒加载修复，保留失败记录。Root读/rename冲突由新客户端共享delete及新publisher有界重试修复，旧设施源文件保留；中断预算保守记账。

训练/SGD/GPU/q拟合/真实及随机轨迹/真实回放均0，45001–45003未用，没有设施压力重测。

[完整计量账](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/FINAL_BUDGET.json)；[每请求费用与P2记录](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/REQUEST_COSTS.csv)。
