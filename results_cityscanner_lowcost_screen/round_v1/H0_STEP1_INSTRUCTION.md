# 热点排序筛选：第 1 步指令

日期：2026-10-18。来源方案：`C:/Users/szr/Desktop/record/1/ccfa-review-reports/cityscanner-hotspot-screening-plan.md` 的 H0。本文件只授权第 1 步。第 2 步到第 6 步不因本步完成而获得授权。

```text
Mode: design
Venue and assumptions: IEEE TMC 现有 City Scanner 检查点上的回顾性筛选。本步只冻结规则并核对资产与候选时段。不推理，不计算 J，不选基线。
No-fabrication status: 候选时段计数只能来自本步读取的 atomic_units.parquet。方案里预先写下的 59 个和 50 个时段是待核验的旧元数据，不能抄进结果当本步计数。
Next CCFA owner: 执行者只交本步列出的文件。未经用户点名，不进入第 2 步，不改论文。
```

## 六步里本步的位置

| 步 | 方案章节 | 做什么 | 本步 |
| --- | --- | --- | --- |
| 1 | H0 | 冻结规则；核对 100 个检查点、轨迹身份、数据重复和候选时段 | 只做这一步 |
| 2 | H1 前半 | 每块第一个 RAVEN 检查点复现旧 RMSE_mu、MAE_mu、WorstGroupRMSE 和四个组 RMSE | 不做 |
| 3 | H1 后半 | 其余模型复现旧指标并写出逐单元预测 | 不做 |
| 4 | H2 | 三个简单对照；只在 validation 上选每块一个 \(b_H\) 并冻结 | 不做 |
| 5 | H3 | 在 test 上按冻结预算计算 J、捕获率和全 test 预测指标 | 不做 |
| 6 | H4 | 配对区间、筛选门槛和决定报告 | 不做 |

## 本步只交这些文件

写到 `results_cityscanner_lowcost_screen/round_v1/`：

1. `shared/PROTOCOL_FREEZE.json`：下面写死的规则。先写这个文件，再做数据核查。
2. `shared/ASSET_MANIFEST.csv`：100 个模型的检查点、评分文件、轨迹身份和状态。
3. `hotspot/POOL_MANIFEST.csv`：每个 split、每个时段的网格数、是否合格、排除原因。
4. `shared/H0_STATUS.json`：每块 `ready`、`INSUFFICIENT_SUPPORT`、`PAUSED_DUPLICATE` 或 `PAUSED_ASSET`。
5. `shared/H0_RESOURCE.md`：本步自己的 CPU 秒、wall、峰值 RSS。不把它记进推理预算。

若 `results_cityscanner_lowcost_screen/round_v1/` 里已有另一份 `PROTOCOL_FREEZE.json` 且方法、种子或阈值与本指令不一致，停止并报告，不覆盖。

Python 使用 `.venv_new\Scripts\python.exe`。核查脚本如需要，只放在本目录。不安装新包。不修改 `src/` 或 `TO_OVERLEAF_paper_tmc_r1_clean/`。不调用训练 runner，不 `torch.load` 检查点，不打开 `events.parquet` 的行。

## 写进冻结文件的规则

这些数在看到候选时段计数之前就写入。本步之后不得因计数或以后的 J 而改写。

两块：

| 块名 | 数据 | 结果入口 | 种子 | 评分文件 | 轨迹清单 |
| --- | --- | --- | --- | --- | --- |
| visit | `data/processed/cityscanner_nyc_pm25/atomic_units.parquet` | `results_c1_cityscanner/round_v1/` | 32001–32010 | 每种子目录里的 `CS_ACCEPTED.json` | `results_c1_cityscanner/round_v1/CS_TRACE_MANIFEST.json` |
| measured-O | `data/processed/cityscanner_nyc_p2_measured_o/atomic_units.parquet` | `results_joint_ou/round_v1/` | 33001–33010 | 每种子目录里的 `JO_ACCEPTED.json` | `results_joint_ou/round_v1/JO_TRACE_MANIFEST.json` |

评分文件不在 round 根目录。实际路径是 `runs/<dataset>/<method>/seed<seed>/CS_ACCEPTED.json` 或 `JO_ACCEPTED.json`。检查点是同级 `checkpoints/final.pt`。dataset 名分别是 `cityscanner_nyc_pm25` 和 `cityscanner_nyc_p2_measured_o`。

五个已训练方法，名称固定为 `fedavg_window`、`twostage_hajek`、`fedau_window`、`obsuse_window`、`raven`。目录名 `raven` 保持原样，不改称新的 `raven_mcs`。不纳入 `results_gatekeeping/` 里的六臂、`raven_wo_design` 或其他变体。

组映射和 \(\mu\) 从两份 `CS_TRAIN_SETUP.json`、`JO_TRAIN_SETUP.json` 抄录键和数组，不手写。visit 与 measured-O 的 \(\mu\) 不同，不能互换。

以后的主预算是每个时段 \(k=\lceil 0.20 N\rceil\)。10% 和 30% 只作敏感性，不能替换 20%。预测并列时按 `spatial_id` 的词典序，不看真值。

\[
J=\frac{\sum_{i\in T} y_i-\sum_{i\in S} y_i}{k\sigma}
\]

\(T\) 是真值最高的 \(k\) 个网格，\(S\) 是方法选中的 \(k\) 个，\(\sigma\) 是该块 train 目标的总体标准差（ddof=0）。J 越小越好。物理损失是分子除以 \(k\)，单位与 `target_value` 相同。汇总顺序是时段到日等权、日等权、10 个种子等权。两块分开。

非 RAVEN 候选的平局顺序按 Unicode 码点，现在写死为：

1. `Delivered-CellBlockMean`
2. `Delivered-SpatialMean`
3. `Fixed-Ensemble`
4. `fedau_window`
5. `fedavg_window`
6. `obsuse_window`
7. `twostage_hajek`

每块以后只选一个 \(b_H\)，全部种子共用，不为各个 test 日另选。选择只用 validation。本步不计算、不选择。

`Delivered-CellBlockMean` 以后使用 UTC 六小时块，该桶至少 3 个不同 unit 才启用，否则退回空间均值。不搜索桶数或最小计数。`Fixed-Ensemble` 以后是同一种子 FedAvg 与 TwoStage-Hájek 的 0.5/0.5，不拟合混合系数。

单块以后要记 `PASS_SCREEN`，必须同时满足方案第四节 H4 的七条：相对改善至少 10% 且 \(D\) 至少 0.01 个训练标准差；\(D\) 的单侧 98.75% 下界大于 0；捕获率点估计下降不超过 2 个百分点；全 test 的 RMSE_mu 和 WorstGroupRMSE 相对代价各不超过 5%；test 上的 J 点估计低于其余六个非 RAVEN 候选；7 天块重采样的 \(D\) 中位数为正。10% 和 30% 预算不能用来挽救 20%。这些门槛是本轮筛选阈值，不是部署合同。

Bootstrap 以后用 10000 次，随机种子 2026101801。主块长是 3 天循环移动块。7 天块只报告，不改主块长。四个预先比较是两方案乘两块；本文件没有定义第二个方案，也不把未用的比较份额收回。本步不抽样。

任何以后的决定都保留 `P2_VS_PROJECTION_UNRESOLVED`。本步不训练投影模型，不恢复 OF-v1。

候选时段规则：validation 与 test 分开；一个时段是同一个 `absolute_time`；合格要求至少 10 个不同 `spatial_id`。test 至少 40 个合格时段且至少 20 个有合格时段的 UTC 日期；validation 至少 20 个合格时段且至少 10 个日期。低于门槛记 `INSUFFICIENT_SUPPORT`。不把时段并成日，不降低 10 个网格的下限。

划分名是 `validation`，不是 `val`。

## 资产核查

对 2 块 × 5 方法 × 10 种子，共 100 行写入 `ASSET_MANIFEST.csv`。每行至少有：`block`、`method`、`seed`、检查点路径、评分路径、`n_windows`、`eventtrace_hash`、清单里的 `trace_hash`、`design_on`、文件是否存在、状态。

核对：

- `checkpoints/final.pt` 存在且字节数大于 0。不加载权重，不算新的文件散列。
- 评分 JSON 存在，`method` 和 `seed` 与路径一致，`n_windows` 为 100，`dataset` 与该块一致。
- 同一个种子的五个方法，`eventtrace_hash` 彼此相同，并等于该块轨迹清单里该种子的 `trace_hash`。
- 轨迹目录存在：visit 为 `artifacts/e3_c1_cityscanner_eventtraces_v1/cityscanner_nyc_pm25/seed32001` 到 `seed32010`；measured-O 为 `artifacts/e3_joint_ou_cs_p2_eventtraces_v1/cityscanner_nyc_p2_measured_o/seed33001` 到 `seed33010`。只确认 `training_eventtrace/events.parquet` 和 `trace_identity.json` 存在。若 `trace_identity.json` 含 `trace_hash` 或 `events_sha256`，与评分里的 `eventtrace_hash` 不一致则该种子为 `PAUSED_ASSET`。不读 parquet 行。

缺一个配对种子就暂停该块，不删种子，不用另一个种子顶上。`results_gatekeeping/` 不参与补齐。

## 数据与候选时段

只读两个 `atomic_units.parquet` 的列：`unit_id`、`spatial_id`、`absolute_time`、`split`、`target_value`、`target_group`。`target_value` 只用于检查是否有限，不用于排序，不用于丢掉时段。不读 `client_measurements.parquet`。

`is_warmup` 和 `support_flag` 本步不作为过滤器。两份 setup JSON 没有写明评分集合要去掉这些行。

每块检查：

- `unit_id` 在全表唯一。
- 同一个 `(spatial_id, absolute_time)` 不重复。若重复，状态 `PAUSED_DUPLICATE`。不求均值，除非能引用一份已经写明的聚合规则并记下路径。找不到规则就暂停该块。
- `split` 的取值只应出现 `train`、`validation`、`test`。出现 `val` 或其他名字则暂停。同一个 `unit_id` 或同一个 `(spatial_id, absolute_time)` 不跨 split。
- `target_value` 全部有限。非有限值的行数写入状态。不删除后继续。
- `target_group` 的取值集合与该块 setup 的 `h_encoding` 键一致。多出来或缺少都记入状态，不改映射。

候选时段只在 `validation` 和 `test` 上、按 `absolute_time` 分组。\(N\) 是该时段不同 `spatial_id` 的个数。\(N<10\) 的时段写入 `POOL_MANIFEST.csv`，`included=0`，原因是 `fewer_than_10_grids`。\(N\ge 10\) 的全部保留，`included=1`。不按真值、网格编号或任何模型结果删时段。

日期按 `absolute_time` 的 UTC 日历日。合格门槛用合格时段覆盖的日期数。每块、每个 split 在 `H0_STATUS.json` 里写下时段数、合格时段数、不同网格数、合格日期数，以及是否达到门槛。

方案正文里的 visit test 59 个时段、790 个单元、24 天，以及 measured-O 的 50 个、650 个、20 天，只作为旧元数据记在冻结文件的 `prior_metadata_not_measured_here`。本步计数与它们不同时，保留本步计数，不把旧数写进 `POOL_MANIFEST.csv`。

## 完成与停止

两块都是 `ready` 时，本步完成。一个块 `INSUFFICIENT_SUPPORT` 或暂停时，该块不进入以后的预测；另一个块的核查仍写完。本指令仍然不授权第 2 步。

出现下列情况即停，不改规则：

- 冻结文件与已有文件冲突。
- 100 个路径里缺检查点或评分，或 `n_windows` 不是 100。
- 同一种子五个方法的轨迹散列不一致，或与清单不一致。
- 重复的时空键没有已写明的聚合规则。
- 需要训练、加载模型、修改 `src/` 或论文才能继续。

本步不写 `shared/predictions/`、`REPRODUCTION_CHECK.csv`、`WINDOW_SCORES.csv`、`BASELINE_SELECTION.json` 或 `DECISION_REPORT.md`。不计算 J，不抽取 bootstrap。
