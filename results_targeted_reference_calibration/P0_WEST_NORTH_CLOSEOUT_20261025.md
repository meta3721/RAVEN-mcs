# 结项记录：公开数据上的 West—North 组差校准

日期：2026-10-25。依据是 `C:\Users\szr\Desktop\record\1\ccfa-review-reports\targeted-reference-calibration-execution-review-20261025.md`。

原组差设计正式结项。`p0_same_value_screen_20261022_210125` 的状态保持 `INSUFFICIENT_DATA`，面板保持 `WRITTEN`，P1 保持 `NOT_RUN`。本记录不把该轮改成通过，也不改成 `RESOURCE_PAUSE`。

## 1. 结项决定

停止原 West—North 同期组差面板、原参考分配 P2，以及对 421 个设备日继续放宽同值规则。当前冻结面板不够做组差评价。校准效果没有估计。

已有四份运行目录里的状态、报告和表没有改写：

- `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_p1_20261022_161223`
- `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_identity_repair_20261022_175353`
- `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_redo_20261022_193538`
- `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_20261022_210125`

没有新建运行目录，没有实现或运行 M0–M4，没有读取 A/T 参考数值做效果分析。

## 2. 结项前的只读复核

直接重读最终 CSV 的身份、日期、段和纳入标记。标签文件只计行，没有用参考数值做误差分析。

| 对象 | 复核 |
| --- | ---: |
| `UNIQUE` | 2,970 |
| `SAME_VALUE_MULTI_MONITOR` | 16 |
| `UNRESOLVED_NO_EXACT_MONITOR` | 1 |
| 联结行合计 | 2,987 |
| 浓度不同而排除的设备日 | 421 |
| 含未联结行的设备日 | 1 |
| 有代表设备的站点 | 21 |
| 进入面板的站点 | 8，West 6，North 2 |
| D_fit / D_tune / V 标签行 | 195 / 99 / 207 |
| V/T 面板行 | 672，即 8 站 × 84 天 |
| 可评价标记 | 672 行均为否 |

进入面板的设备是 CA10、CA2、CA5、CA4、CA3、CA17、WA1、WA3。面板里的当日门槛是 West 5、North 3。V 覆盖 28 个日期，T 覆盖 56 个日期；这些日期都写在面板里，可评价标记为否。

`prepare_data.py` 第 1257–1299 行按设备、日期、参考型号分组：任一源行不可用则整个设备日排除，多个参考浓度也排除，全部浓度一致才保留。第 366–432 行按有效日选择型号和代表设备并检查四段支持。第 435–509 行用 `max(3, ceil(0.75 × 该组站点数))` 生成双组每日面板。North 固定站点为 2，日门槛为 3，所以可评价日和七天块都是 0。

421 个设备日的含义是：它们没有满足本轮“一个设备日只有一个标签”的构造规则。这个计数不表示这些日期不存在任何参考观测。2,970 行可以唯一联结；16 行的标签数值相同，监测器身份仍有多解；1 行未命中。

## 3. 已联结行内的 POC 上界

另做了一次只读盘点，用来判断单纯改选已经出现的 POC 能否恢复双组面板。输入只用 `row_linkage.csv` 里 `UNIQUE` 与 `SAME_VALUE_MULTI_MONITOR` 的事件键、站点、设备、参考型号、日期和段。没有使用浓度列。事件类型按日期做并集，只算可用性上界，不选定事件类型，也不合并数值。

候选序列是站点、设备、参考型号、POC、方法代码和采样时长。57 条序列中，D/V/A/T 分别达到 20/10/10/20 日、且 D_fit 与 D_tune 各自至少 1 日的站点仍是 8 个：West 6 个，North 2 个。North 里满足全部分段支持的只有 53-033-0057（WA1）和 53-061-1007（WA3）。

这不是一次新的 P0，没有选出新面板，也没有证明另一种参考协议已经通过。它只说明：在当前已经联结的公开配对行里，从已出现的 POC 中换一条固定序列，仍然到不了原来的双组门槛。拿原始传感器日期和完整 EPA 库重新配对不在这次盘点内。

## 4. 没有启动的事项

审查报告允许以后另立一次更窄的问题：在已经有配对的固定站点上，用现成 D/V 数据做时间前推校准。那是新的协议，要单独建目录，不能回写本轮状态。本次没有启动它。

原 P1、原 P2 和继续修补 421 个设备日，都没有执行。

## 5. 资源

此前已计量计算 CPU 仍是 21.5 秒，由 12.765625 与 8.734375 相加，写在同值筛选的账本里。本次只读复核的 `process_time` 没有跳过一个计时刻度，记 0；墙钟 0.054 秒。这个 0 不从 21.5 秒里扣除，也不写入已关闭目录的账本。

## 6. 记录

- 本结项记录：`C:\Cursor\raven.mcs\results_targeted_reference_calibration\P0_WEST_NORTH_CLOSEOUT_20261025.md`
- 执行审查：`C:\Users\szr\Desktop\record\1\ccfa-review-reports\targeted-reference-calibration-execution-review-20261025.md`
- 实验总结：`C:\Cursor\raven.mcs\results_targeted_reference_calibration\EXPERIMENT_SUMMARY_20261025.md`
- 最终实验报告：`C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_20261022_210125\EXPERIMENT_REPORT.md`
