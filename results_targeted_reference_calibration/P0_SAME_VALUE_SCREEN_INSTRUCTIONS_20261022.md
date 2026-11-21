# 补做指令：同值多监测键之后完成 P0 筛选

日期：2026-10-22。依据是 `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_redo_20261022_193538\EXPERIMENT_REPORT.md`。

本文件只授权把 P0 筛选做完。不授权 P1、模型拟合、训练、P2、P3、BelAir、联邦训练或论文改写。日期、West/North、支持门槛、5% 收益门槛和 2% 组差保护都不改。5% 和 2% 只写入冻结配置，本轮不计算。

执行位置仍是 `C:\Cursor\raven.mcs`。Python 使用 `C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`。PowerShell 不能用 `&&`。不要改 git 配置，不要提交、推送、reset 或 amend。不要改 `src\`、论文或冻结表内数字。

## 1. 已关闭的结果，不得改写

| 目录 | 状态 |
| --- | --- |
| `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_p1_20261022_161223` | `INVALID_RUN` |
| `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_identity_repair_20261022_175353` | `BLOCKED_METADATA` |
| `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_redo_20261022_193538` | `BLOCKED_METADATA`，面板 `NOT_RUN` |

这三份目录只读。不要改状态，不要删报告、联结表或脚本，也不要在这些目录里续跑。

`p0_redo_20261022_193538` 已经确认：

- 窗口内有参考值的源行 2,987 行，2,970 行连到唯一事件键。
- 旧键冲突仍是 381 个、7 站、142 日、965 行。
- 不能唯一联结的源行是 17 行，不是仅有的 8402。
- 8402 的身份数是 0。同日 FRM 的 13.3 与 14 都不是 12.6，不能替换。
- 另外 16 行的身份数是 2。匹配函数要求每个 EPA 键只有一个算术平均，且该平均与 `PM25FM` 精确相等，所以这两个键的浓度相同。除 7818 外，差别只在 POC。7818 同时差在 POC 和事件类型，浓度仍是 13.083333 µg/m³。
- 站点筛选、代表设备和支持门槛没有执行。排除表只有表头。

因此，这 16 行阻塞的是监测键不唯一，不是参考浓度不唯一。本文件只放行这一种情况。

## 2. 新运行目录与资源

新目录：

`C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_<实际日期时间>\`

EPA 日文件继续用只读缓存，不重新下载：

`C:\Cursor\raven.mcs\results_targeted_reference_calibration\source_cache_20261022\`

单进程、单线程。`OMP_NUM_THREADS`、`MKL_NUM_THREADS`、`OPENBLAS_NUM_THREADS`、`NUMEXPR_NUM_THREADS` 都设为 1。不用 GPU，不开多进程。

继承 CPU 为 7.53125 + 5.234375 = 12.765625 秒，写在账本开头，不清零，也不从本轮 300 CPU 秒里扣除。本轮新增上限仍是 300 CPU 秒、900 计算墙钟秒。RSS 超过 1.5 GiB，或可用内存连续 30 秒低于 1.5 GiB，保存进度并写 `RESOURCE_PAUSE`。EPA 文件分块读，只保留目标站点窗口内的行。

## 3. 先复核 17 行，再改分类

用与 `p0_redo_20261022_193538\prepare_data.py` 相同的匹配条件重算：参数 `88101`，方法名完全相同，原生时长符合仪器类型，算术平均十进制精确相等。`88502` 只检查未命中，不替补。`24-HR BLK AVG` 不并入 `1 HOUR`。

重算后的未唯一联结源行必须仍是：

`4551, 6209, 6869, 7578, 7818, 7833, 8342, 8402, 8717, 8738, 8747, 8781, 8842, 11956, 11990, 12004, 12375`

并且：

- 8402 的身份数是 0。
- 其余 16 行的身份数是 2，每个命中键的算术平均都等于该源行的 `PM25FM`。

若集合、身份数或均值相等性有任何一项不同，状态写 `BLOCKED_METADATA`，停止。不要扩大放行范围，不要改用最小 POC、第一条、平均值或与 PurpleAir 的距离。

A/T 的浓度继续不写入对外表格。D_fit、D_tune、V 可以写出已经在上一份报告中出现过的浓度。

## 4. 唯一新增的标签规则

监测键定义不变：

`88101 + AQS 站点 + 日期 + POC + 方法代码 + 事件类型 + 原生采样时长`

一行的处理：

1. 恰好一个键：`UNIQUE`。参考值就是该键的算术平均。
2. 两个或更多键，且每个键的算术平均都等于同一个源值：`SAME_VALUE_MULTI_MONITOR`。参考值就是这个共同浓度。保存按 POC、方法代码、事件类型排序后的全部键。不指定其中一个 POC 为真监测器，也不把事件类型 None 优先于 Included。
3. 零个键，或命中键的算术平均并不都等于该源值：该行不可用。8402 属于零个键。

设备日是“设备 × 日期 × 参考型号”：

- 任一源行不可用：整个设备日为 `EXCLUDED_UNRESOLVED_ROW`。已经连上的兄弟行不能单独留下。IA3 在 2019-01-27 的 FRM 因此仍不可用，源行 8465 的 13.3 不能充当该日参考。
- 全部源行都是 `UNIQUE` 或 `SAME_VALUE_MULTI_MONITOR`，且这些行只有一个参考值：设备日有效。标签就是该值。
- 这些行出现两个不同参考值：`EXCLUDED_AMBIGUOUS_MONITOR`。这包括原先 381 个旧冲突键里同一设备日对应两个 POC、两个浓度的情况。不得用本文件把它们合成一个标签。

有效设备日的计费键是该日全部命中键的有序集合。集合相同只计一次，不按设备数或 POC 数重复计费。集合不同则分开计，即使浓度碰巧相同。不要把计费键偷换成最小 POC。

## 5. 接着做上一轮没有做的筛选

只使用第 4 节的有效设备日：

1. 固定参考型号：先比覆盖的时间段数，再比 154 天内有效日数，平局按型号名称字典序。
2. 在胜出的型号下选一个代表设备：有效配对日最多，平局按 ID 字典序。支持不足就剔除该站点，不换设备、不换型号。
3. 代表设备在 D、V、A、T 至少 20、10、10、20 日，D_fit 与 D_tune 各自至少 1 日。
4. 通过还需要至少 10 个独立站点、每组至少 4 个，V 至少 20 个可评价日，T 至少 40 个可评价日，并覆盖从 2019-05-04 起至少 7 个七天块。
5. 一日可评价，当且仅当每组至少有 `max(3, ceil(0.75 × 该组固定站点数))` 个站点有有效配对。
6. 写出 V/T 面板。训练入口只能读 D 的标签；A/T 标签读取必须拒绝。本轮没有模型，不把预测不变性写成已验证。

支持不足写 `INSUFFICIENT_DATA`。不得换窗口、换区域、降低门槛或再删站点来凑通过。

## 6. 状态与交付

- 第 3 节复核失败：`BLOCKED_METADATA`
- 同一计费键出现不同参考值，或实现挑选了 POC、第一条、平均值：`INVALID_RUN`
- 筛选完成但支持不够：`INSUFFICIENT_DATA`
- 筛选完成且支持够：`PASS_P0`
- 触达资源上限：`RESOURCE_PAUSE`

任何状态下 P1 都是 `NOT_RUN`。不要实现 M0–M4，不要写 RMSE、ContrastMAE、收益或区间，也不要用 0 填充。

新目录至少交付：`P0_DATA_AUDIT.md`、`P0_status.json`、`protocol_freeze.json`、`row_linkage.csv`、`same_value_multimonitor_rows.csv`、`excluded_device_days.csv`、`reference_events_metadata.csv`、`representative_devices.csv`、`split_manifest.csv`、`evaluation_panel.csv`、`ISOLATION_CHECK.md`、`RESOURCE_AND_BUDGET.md`、`README.md`、`NEXT_STAGE_REQUEST.md`。非 `PASS_P0` 时另写 `FAILURE_REPORT.md`。

`same_value_multimonitor_rows.csv` 记录源行、日期、段、设备、站点和排序后的键。A/T 不写浓度。`excluded_device_days.csv` 记录排除原因和源行号，同样不写 A/T 浓度。

## 7. 结束回复

用中文报告：

1. 三份旧状态是否未改。
2. 17 行复核是否与第 3 节一致。
3. 本轮 P0 状态。若已筛选：独立站点数、West、North、V 可评价日、T 可评价日和七天块数。未筛选则写未确定。
4. 同值多键行数，以及因不同浓度被排除的设备日数。
5. 继承 CPU、本轮 CPU、墙钟和内存。
6. 审计、排除表、状态和下一阶段说明的绝对路径。

然后停止。即使 `PASS_P0`，也只在 `NEXT_STAGE_REQUEST.md` 中说明 P1 尚未授权。
