# FAILURE_REPORT_Z0

- 失败条件：RESOURCE_BLOCKED
- 实测值：等待 30 秒后可用内存 1432240128 字节（约 1.33 GiB）；过程中一度为 888061952 字节，低于 1 GiB
- 阈值：启动重库前至少 2.5 GiB；低于 2 GiB 不开始新批
- 差距：距 2.5 GiB 大约还差 1.17 GiB
- 首个问题：Z0 核对三个 seed 的事件 ID 和 Stage-1 质量之前
- 证据文件：本次进程的 GlobalMemoryStatusEx 读数
- 已证实原因：可用内存在 30 秒后仍低于 2 GiB
- 未知解释：无
- 已完成范围：没有写入协议冻结，没有回放，没有训练
- 预算累计：活动计算可忽略；30 秒是等待
- 可恢复状态：`results_zero_safe_buffer/round_v1/` 只有本失败记录。旧 support-consumption 目录未改
- 已取消队列：Z0 数据核对、Z1、Z2、Z3
- WAITING_USER_REVIEW

本轮没有把任何修订结果写成旧 S 方法通过。Z3 未执行，无新增预测收益。
