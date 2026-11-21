# 决策时点与字段

本文件只来自协议和静态代码阅读。没有扫描处理表，也没有把任何字段送进选择器。

决策时点按冻结协议是一个完整 UTC 日结束、库存摘要形成之后、本地训练之前。摘要本身是新协议假设，不是观测前已知，其字节以后要计入成本。

## 允许进入选择器

| 字段 | 来源 | 产生时刻 | 持有者 | 传到服务器 | 进入选择器 |
|---|---|---|---|---|---|
| client_id | 处理表 `spatial_id`，`cityscanner_p2_measured_o.py` 第 233 行 | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| group | `target_group`，region0–3 | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| n_j | 当日 O=1 的唯一合法 cell-slot 数 | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| earliest_time, latest_time | 这些 cell-slot 的 `absolute_time` | 日终库存 | 逻辑网格 | 日终摘要 | 是 |
| 本臂以往实际上传的更新幅度和时间 | 选择之后的上传 | 上一轮结束之后 | 服务器 | 已在服务器 | 是 |
| mu、k、冷启动规则 | `P0_FREEZE.json` | 实验前冻结 | 服务器 | 不依赖当日数据 | 是 |

## 禁止进入选择器

| 字段 | 原因 |
|---|---|
| 当前 `target_value` | 测量值。代码在 O=1 时写入真实值，O=0 时写成 0.0 占位（同文件第 190–192 行） |
| 未选节点的梯度或损失 | 训练尚未开始 |
| 旧 U、`oracle_q`、网络成功和到达 | `stage2_r3.py` 的 `compute_usable_r3` 由随机数生成；`INGEST_REPORT.json` 将 U 标为 `CONTROLLED_EXPERIMENTAL` |
| 未来日期的库存或更新 | 会破坏日终截止 |
| validation/test 的 `target_value` 和分数 | 本阶段不读取 |
| 其他臂的更新历史 | 各臂历史必须分开 |
| 整个旧 `public_features` | 其中含当前 `o_observed` 和 `support_n`（第 198–208 行），不能整包当白名单 |

旧 100 窗事件把训练时间槽压进 `window_id_by_time_index`（`cityscanner_p2_measured_o_eventtrace.py` 第 20–28 行）。那个映射会在窗口开始前看到后来的库存，不能当作本协议的决策时点。

处理表与导入报告的哈希一致：`identity.json` 和 `INGEST_REPORT.json` 的 `data_hash` 都是 `06e2953afad17b27facfbf593d399be92255775c5c298e5c89924903a30a2de8`，`occupancy_sha256` 都是 `8b1deff66f1a23973d87b44f1e6da69cc2291ee8da77dc7d1db4f222ac3f96af`。这只证明两份登记指向同一处理结果，没有重新数行。
