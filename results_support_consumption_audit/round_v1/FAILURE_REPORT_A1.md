# FAILURE_REPORT_A1

- 失败条件：RESOURCE_BLOCKED
- 实测值：available_bytes=1944739840
- 差距：heavy import requires 2.5 GiB and a new block requires 2.0 GiB
- 首个问题：before parquet
- 来源：GlobalMemoryStatusEx
- 已证实原因：free memory stayed below the gate for 30 seconds
- 未知原因：ledger rows not yet split by mass
- 已完成范围：A0
- CPU 秒：0.031250
- wall 秒：30.057814
- 峰值 RSS 字节：25722880
- 最小可用内存字节：1910116352
- 可恢复状态：已写文件保留；旧 round_v1 未改
- 取消的后续：A1 A2 A3 A4
- WAITING_USER_REVIEW

本轮无新增训练，没有新增预测收益；五臂申请尚未执行。
