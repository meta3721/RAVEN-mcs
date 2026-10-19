# FAILURE_REPORT_P0

- 状态：RESOURCE_EXIT
- 未满足条件：RESOURCE_EXIT: available memory 621633536 bytes is below 1073741824
- 实测与阈值：见同目录 P0_STATUS.json
- 首个失败位置：见状态文件的 evidence
- 原因层：资源门槛在重型导入之前触发，没有进行回放。
- 已完成范围：none
- CPU 秒：0.109375
- wall 秒：0.011848099995404482
- 峰值 RSS 字节：22552576
- 最小可用内存字节：623198208
- 取消的后续队列：P0 P1 P2 P3 P4
- WAITING_USER_REVIEW

无新增训练、尚无预测收益结果。
