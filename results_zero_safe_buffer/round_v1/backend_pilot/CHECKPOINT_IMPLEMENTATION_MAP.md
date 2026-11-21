# CHECKPOINT_IMPLEMENTATION_MAP

实现文件：`results_zero_safe_buffer/round_v1/backend_pilot/checkpoint_store.py`。

| 字段 | 内容 | 本轮往返 |
|---|---|---|
| model_state | 参数名到数值列表 | 已用 `[1.0, 2.0]` 往返 |
| optimizer_state | `stateless_manual_sgd`、local/server 学习率、local_steps、step_count、momentum_buffer=null | 已往返；缺字段被拒绝 |
| version | 整数版本 | 已往返 |
| registration_snapshots | attempt id 到注册时参数 | 已往返 |
| client_state | 客户端侧必要状态 | 已往返空映射 |
| in_flight / pending | 未完成消息 | 已往返 |
| rng_state | Python `getstate()`；torch 键本轮为 null | Python 状态已往返；torch 为 UNRUN |
| data_cursor | 关闭游标 | 已往返 |
| ledger / eval_progress / budget | 账本、评估进度、累计预算 | 已往返 |

保存使用 pickle，并另写一个只含键名的 index json。加载时缺任一必需字段，或优化器不是上述手动 SGD 结构，会抛 `CheckpointIncomplete`。只含 `step_count` 的对象已被拒绝。

低内存时不能保存半步。恢复点是上一个完整关闭边界；重做的计算以后计入成本。本轮没有训练中的断点，也没有做保存后重放一段关闭的恢复试验。
