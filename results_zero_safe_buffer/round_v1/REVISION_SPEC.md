# REVISION_SPEC

协议名：`zero-safe-buffer-v1`。

唯一消费规则修订：参考质量 m=0 的消息在合法性核验后立即记为 REFERENCE_ZERO_EXCLUDED。它不进入 pending，不替换同客户端消息，不占 64 个有效槽位，不触发释放，也不触发旧正质量消息过期。
非有限或负的 m 记 INVALID_REFERENCE_MASS 并暂停。正零分界仍是 m>0。

未改：同客户端只保留一条最新正质量消息，旧消息记 SUPERSEDED_POSITIVE。这不假设新消息包含旧观测。
未改：H=2、S_max=5、池容量 64、cap/ESS、μ、Design、100 窗、I/F1/F2 的年龄规则、注册时下载本臂当前版本。
S-Proj、完整 P2 和主动采样不在本轮。

Z1 只读 measured-O 的 train 元数据和 U=1 事件。Z3 若以后获准，用 train 训练、validation 筛选；旧 test 不参与选择。现有划分不是独立确认，本版本不是盲测。

已有缺口：参考投影和两条外部基线还没有在新事件上跑过真实 SGD。旧 P2 只恢复过调度计数器，不能当成训练后端已完成。
零质量消息的字节长度在轨迹里不存在，byte_cost 记 null，raw_workload 仍保留。
