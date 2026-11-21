# Z2_IMPLEMENTATION_REPORT

- 状态：STATIC_READY
- 零质量到达后，旧正质量消息仍被提交；零消息是 REFERENCE_ZERO_EXCLUDED，没有进入 pending。
- 参考投影满足和为 1、非负、cap 和 ESS，并且与最小 TV 权重不是同一个解。
- 五个入口分别接到 project_reference、FedAvgWindowAggregator、TwoStageHajekAggregator。外部基线不再是拒绝占位。
- 断点所需字段已列出。真实 SGD、优化器状态和客户端快照没有执行，因此是 STATIC_READY，不是 TRAINING_VERIFIED。

Z3 未执行、无新增预测收益。
