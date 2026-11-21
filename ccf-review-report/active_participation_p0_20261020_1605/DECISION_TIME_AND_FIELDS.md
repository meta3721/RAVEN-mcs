# 决策时点与字段

决策时点是一个完整 UTC 日结束、库存摘要已经形成之后、本地训练之前。摘要是这条新协议的假设，只能在观测之后获得，不能写成观测前已知。它的字节记在 `RESOURCE_ACCOUNTING.md`。

`P0_FREEZE.json` 在读取处理表之前写入。本审计没有打开预测结果，也没有把 validation/test 的 `target_value` 送进任何汇总或选择器。处理表里的该列曾被加载；43 个冻结日上的 O=1 行经核对全部属于 train，数值检查只用了这些 train 行和预热行。

## 允许进入选择器

| 字段 | 来源 | 产生时刻 | 持有者 | 传到服务器 | 进入选择器 |
|---|---|---|---|---|---|
| client_id | occupancy 的 `client_id`，等于 `spatial_id` | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| group | `target_group`，region0–3 | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| n_j | 当日可形成合法批次的唯一 O=1 cell-slot 数 | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| earliest_time, latest_time | 这些 cell-slot 的 `absolute_time` | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| 本臂已收到更新的幅度和时间 | 选择并收到上传之后 | 上一轮结束之后 | 服务器 | 已在服务器 | 是 |
| mu、k、冷启动和词表 | 冻结协议 | 实验前 | 服务器 | 不依赖当日测量值 | 是 |

预热词表只含 `absolute_time <= 2021-09-22 23:00 UTC` 且 `is_warmup` 的 train 网格，共 118 个。不在词表中的网格由服务器用冻结词表判定，不需要测量值。

## 禁止进入选择器

| 字段 | 原因 |
|---|---|
| 当前 `target_value` 和 `potential_measurement` | 只用于有限性资格检查，不进入排序 |
| 未选节点的梯度或损失 | 训练尚未开始 |
| U、`oracle_q`、`q_use_true`、网络成功、到达和版本年龄 | `cityscanner_p2_measured_o_eventtrace.py` 第 89–139 行由 `compute_usable_r3` 生成 |
| 未来日期的库存、网格和更新 | 会改变词表或名额 |
| validation/test 标签和分数 | 本阶段不使用 |
| 其他臂的更新历史 | 各臂分开维护 |
| 整个 `public_features` | 含 `support_n` 和 `o_observed`；本次读取列时没有加载它 |

旧 100 窗映射 `window_id_by_time_index` 会在窗口开始前看到后来的时间槽。它不是本协议的决策时点，本次没有调用它。
