# 资源与预算

截至2026-10-18T11:50:43.800911+00:00，新增已审计完整根CPU=411.890625秒；保守占用=50.000000秒（前置整理30、交付与关闭预留20，实耗UNKNOWN，非实测）。本轮预算记账=461.890625/1000秒，余额=538.109375秒。若任一计量失败，另按其cap保守占用而非记为实测；本轮各计量原始行如下。

墙钟：从首次只读准备2026-10-18T18:58:19.5477347+08:00至当前，活动保守包络=3144.253/5400秒；worker会话墙钟分别列下，不能与活动包络相加。未申请额外旧余额。根费用包含worker树、监视器、启动和保存；独立PID总和仅作审计，不再相加。worker本地训练CPU、逐操作root上界、spent分类均是包含项，不与根费用叠加。

- {"label": "A", "charged_CPU": 0.53125, "job_CPU": 0.421875, "launcher_and_monitor_CPU": 0.109375, "audit": true, "returncode": 1, "limit": null, "wall": 0.5030093999957899, "actual_CPU": 0.53125}
- {"label": "A_identity", "charged_CPU": 1.484375, "job_CPU": 1.375, "launcher_and_monitor_CPU": 0.109375, "audit": true, "returncode": 0, "limit": null, "wall": 1.48683439999877, "actual_CPU": 1.484375}
- {"label": "B", "charged_CPU": 12.734375, "job_CPU": 11.640625, "launcher_and_monitor_CPU": 1.09375, "audit": true, "returncode": 1, "limit": null, "wall": 18.098547700006748, "actual_CPU": 12.734375}
- {"label": "B_repair", "charged_CPU": 2.953125, "job_CPU": 2.734375, "launcher_and_monitor_CPU": 0.21875, "audit": true, "returncode": 1, "limit": null, "wall": 3.0312498999992386, "actual_CPU": 2.953125}
- {"label": "B_repair2", "charged_CPU": 10.671875, "job_CPU": 10.109375, "launcher_and_monitor_CPU": 0.5625, "audit": true, "returncode": 1, "limit": null, "wall": 10.897185999987414, "actual_CPU": 10.671875}
- {"label": "B_repair3", "charged_CPU": 20.921875, "job_CPU": 19.75, "launcher_and_monitor_CPU": 1.171875, "audit": true, "returncode": 0, "limit": null, "wall": 21.233072399991215, "actual_CPU": 20.921875}
- {"label": "C", "charged_CPU": 356.15625, "job_CPU": 265.53125, "launcher_and_monitor_CPU": 90.625, "audit": true, "returncode": 0, "limit": null, "wall": 2036.917051299999, "actual_CPU": 356.15625}
- {"label": "D_validation", "charged_CPU": 6.28125, "job_CPU": 5.828125, "launcher_and_monitor_CPU": 0.453125, "audit": true, "returncode": 0, "limit": null, "wall": 6.115392499996233, "actual_CPU": 6.28125}

历史费用仅作定位，不并入本轮：
- OF-v1：已审计路径根CPU 493.984375秒，另保守占用2.15625秒，所列会话墙钟2689.562009秒。来源：ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/RESULT_OF.md。
- fixed_time_0.5：已审计路径根CPU 168.265625秒，另保守占用2388.0秒，所列会话墙钟750.707479秒。来源：ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/RESULT_FIXED05.md。
- fixed_time_2：已审计路径根CPU 526.90625秒，另保守占用0.0秒，所列会话墙钟2975.83399秒。来源：ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/RESULT_FIXED2.md。
- OF-no-Q-stop：已审计路径根CPU 552.15625秒，另保守占用0.0秒，所列会话墙钟2995.48084秒。来源：ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/RESULT_NOQSTOP.md。

fixed05旧失联调用2388秒为保守占用，旧实际CPU及退出墙钟UNKNOWN；不将其标为实测算法成本。不重复累计旧批次或共享暖启动。

概率适用身份：新strategy、collection_role、stop_rule和clock均已单独冻结。scope.service保留父服务模型整包元数据（其中旧CPU_limit=3000仅为继承标记），不作为本轮预算授权；本轮有效CPU上限1000由独立GapAuthorization和新根预算强制，注册历史保存当前根余量。既有注册保留原概率/时钟字段，新增注册采用新配置哈希。该诊断先验不提供概率跨策略校准保证。

本轮GPU=0，q-fit=0，A/B新增SGD=0，C实际新增SGD=2683（上限5000），C逻辑SGD=3354包含借用暖启动671步。训练保护与概率校准尚未成立，不作RMSE或风险保证。

单worker、单线程和既有单CPU affinity，BELOW_NORMAL优先级；未并行实验。内存来源与时间见gap/MEMORY_BEFORE_MODEL.json、MEMORY_BEFORE_TRAINING.json及MEMORY.jsonl；这些不是交付时当前读数。最低运行采样可用内存=2321399808字节。低于2GiB连续30秒或明显卡顿则保存暂停；没有证据把历史卡顿/关机归因于硬件规格。

资源设置修复：19:20:37定点查询发现worker优先级仍为Normal，早期ctypes设置未核实生效；于2026-10-18T11:20:53.9196679Z将本轮worker和monitor明确设为BelowNormal并复读确认。原单CPU worker亲和性始终为1，监视器单独计量。修复仅影响调度，不修改科学源码、随机状态、服务模型或参数；此前Normal阶段如实保留，不宣称自启动全程后台优先级。证据：PRIORITY_CORRECTION.json。终审/交付worker采用显式Windows句柄类型并检查设置返回值。

最终交付计量后关闭：以下计量行计入上述合计；前文可能已有同标签，按标签唯一索引，不能重复相加。
- {"label": "D_delivery", "charged_CPU": 0.15625, "job_CPU": 0.0625, "launcher_and_monitor_CPU": 0.09375, "audit": true, "returncode": 0, "limit": null, "wall": 0.1431901000032667, "actual_CPU": 0.15625}
- {"label": "D_validation", "charged_CPU": 6.28125, "job_CPU": 5.828125, "launcher_and_monitor_CPU": 0.453125, "audit": true, "returncode": 0, "limit": null, "wall": 6.115392499996233, "actual_CPU": 6.28125}

20秒交付保守包络覆盖非计量的编辑、定点状态读取、最终索引和本次关闭写入；这些实际CPU保持UNKNOWN，未伪装为测量。未用额度不自动转为新实验授权。

分项预算记账（含已明确标注的保守占用，不等同于全部实测）：{"A": 32.015625, "B": 47.28125, "C": 356.15625, "delivery": 26.4375}秒；建议阶段额度A60/B120/C700/保存交付120均在1000总额内，额度不等于消耗。
