# 补做指令：公开参考校准 P0

日期：2026-10-22。本文件只授权补做 P0。不授权 P1、模型拟合、训练、P2、P3、BelAir、联邦训练或论文改写。

执行位置是当前工作区 `C:\Cursor\raven.mcs`。不要在桌面结果目录里再开一套运行副本。Python 使用 `C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`。PowerShell 不能用 `&&`。不要改 git 配置，不要提交、推送、reset 或 amend。不要改 `src\`、论文、冻结表内数字，也不要把 Overleaf 密码写入任何文件。

## 1. 已关闭的结论，不得改写

两份旧结果都保持为失败或阻塞记录。禁止把它们的状态改成 `PASS_P0`，禁止覆盖其中的报告、状态和联结表。

| 目录 | 状态 | 含义 |
| --- | --- | --- |
| `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_p1_20261022_161223` | `INVALID_RUN`，P1 `NOT_RUN` | 旧键“站点 + 日期 + 参考型号”不能唯一确定参考。381 个候选键、7 站、142 日。不是算力失败，也不是模型失败。 |
| `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_identity_repair_20261022_175353` | `BLOCKED_METADATA`，面板 `NOT_RUN`，P1 `NOT_RUN` | 381 个旧键中 380 个、965 行中 964 行已连到唯一监测记录。源行 8402 不能联结。 |

已核对且本轮沿用的身份规则写在旧目录的 `IDENTITY_RULES.md`。日期窗、West/North、5% 收益门槛和 2% 组差保护都不改。这些百分比本轮只写入冻结配置，不计算，因为 P1 不运行。

继承已记账的计算 CPU，不清零：3.40625 + 3.96875 + 0.15625 秒。下载墙钟 16.702 秒继续单列，不算模型 CPU。分项以两份 `resource_ledger.jsonl` 为准。

## 2. 先替换残留，只保留失败记录

先做文件整理，再跑补做 P0。整理不得改写保留文件的内容。整理前后各读一次两份 `P0_status.json`，确认仍分别是 `INVALID_RUN` 和 `BLOCKED_METADATA`。

### 2.1 保留

`p0_p1_20261022_161223` 只保留这些失败记录：

- `FAILURE_REPORT.md`、`P0_DATA_AUDIT.md`、`P0_status.json`、`failure_statistics.json`
- `conflicts.csv`、`conflicts_by_site_split.csv`、`conflict_examples_D_fit_only.csv`
- `SOURCE_IDENTITY_REVIEW.md`、`ISOLATION_CHECK.md`、`isolation_results.json`
- `NEXT_STAGE_REQUEST.md`、`P1_CALIBRATION_REPORT.md`、`README.md`
- `RESOURCE_AND_BUDGET.md`、`resource_ledger.jsonl`
- `protocol_freeze.json`、`environment.json`、`source_counts.json`、`site_map.csv`
- `reference_events_metadata.csv`、`representative_devices.csv`、`split_manifest.csv`、`evaluation_panel.csv`
- `source_dictionary.txt`、`source_S_tables_pdfpage_4.txt`、`source_S_tables_pdfpage_5.txt`、`source_S_tables_pdfpage_6.txt`、`source_S_tables_pdfpage_7.txt`
- `P0_1_inspect_source.log`、`P0_2_prepare_data.log`、`P0_3_explain_p0_failure.log`
- `dependency_resource.json`、`preparation_resource.json`、`worker_usage_explain_p0_failure.json`、`worker_usage_inspect_source.json`、`worker_usage_prepare_data.json`

`p0_identity_repair_20261022_175353` 只保留这些阻塞记录：

- `IDENTITY_RULES.md`、`P0_DATA_AUDIT.md`、`P0_status.json`、`NEXT_STAGE_REQUEST.md`、`README.md`
- `RESOURCE_AND_BUDGET.md`、`resource_ledger.jsonl`、`download_log.json`、`linkage_summary.json`
- `conflict_row_linkage.csv`、`conflict_key_status.csv`、`unresolved_reference_row.csv`
- `dfit_match_summary.json`、`dfit_epa_candidates.csv`、`epa_window_target_sites.csv`
- `supplement_page_index.json`、`supplement_pdfpage_2.txt`、`supplement_pdfpage_9.txt`、`supplement_pdfpage_10.txt`、`supplement_pdfpage_20.txt`、`supplement_pdfpage_21.txt`
- `RUN_DIRECTORY.txt`

### 2.2 移走唯一输入，然后删除残留

下面三份是唯一本地副本，不是失败记录。整文件移到工作区只读缓存，不改字节，不重新下载：

- `p0_identity_repair_20261022_175353\daily_88101_2019.zip`
- `p0_identity_repair_20261022_175353\daily_88502_2019.zip`
- `p0_p1_20261022_161223\source_supplement.pdf`

缓存目录：

`C:\Cursor\raven.mcs\results_targeted_reference_calibration\source_cache_20261022\`

同时把 `source_dictionary.docx` 移入该缓存。移完后，从两个旧目录删除其余残留，至少包括：

- `p0_p1_20261022_161223\.venv\`
- `p0_p1_20261022_161223\__pycache__\`
- 该目录下全部 `.py`
- `p0_identity_repair_20261022_175353\extract_and_match_dfit.py`
- `p0_identity_repair_20261022_175353\build_linkage.py`

不得删除第 2.1 节列出的记录。不得修改原数据包 `C:\Users\szr\Desktop\record\1\dataset_dense_reference_evidence\epa_purpleair_2021.zip`。

## 3. 补做目录与预算

新运行只写到：

`C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_redo_<实际日期时间>\`

单进程、单线程。设置 `OMP_NUM_THREADS=1`、`MKL_NUM_THREADS=1`、`OPENBLAS_NUM_THREADS=1`、`NUMEXPR_NUM_THREADS=1`。不用 GPU，不开多进程。

本轮 P0 新增计算上限仍是 300 CPU 秒、900 计算墙钟秒，与继承成本相加后暂停；继承成本不从这 300 秒里扣除，而是另记在账本开头。进程 RSS 超过 1.5 GiB，或可用内存连续 30 秒低于 1.5 GiB，保存进度并写 `RESOURCE_PAUSE`。EPA 日文件分块读，只保留目标站点窗口内的行。不要再次下载这两个 zip。

依赖缺失时只安装到本运行目录的局部虚拟环境，不升级 `.venv_new`，也不重建已删除的桌面 `.venv`。

## 4. 冻结的数据规则

总大纲和 2026-10-22 的 P0/P1 指令仍然有效。本文件只替换其中不完整的事件键，并增加一条已经点名的未联结行处理。除此之外，不改区域、日期、支持门槛、面板规则、模型定义、5% 或 2%。

### 4.1 时间、组别和支持

- D_fit：2019-01-26—2019-02-22
- D_tune：2019-02-23—2019-03-08
- V：2019-03-09—2019-04-05
- A：2019-04-06—2019-05-03，只做元数据
- T：2019-05-04—2019-06-28，只做元数据
- 组别只使用源数据 `West` 与 `North`
- 代表设备在 D、V、A、T 至少有 20、10、10、20 个有效配对日，并且 D_fit、D_tune 各自至少 1 日
- 通过条件：至少 10 个独立站点，每组至少 4 个；V 至少 20 个可评价日；T 至少 40 个可评价日，并覆盖从 T 首日起至少 7 个连续七天块
- 一日可评价，当且仅当每组至少有 `max(3, ceil(0.75 × 该组固定站点数))` 个站点有有效配对

支持不足就写 `INSUFFICIENT_DATA`。不得换窗口、换区域、降低门槛、插值参考或删站点来凑通过。

### 4.2 事件键

一行必须同时满足以下条件，才算连到唯一监测记录：

1. EPA 参数是 `88101`。`88502` 只用于证明未命中，不能替补 FRM/FEM。
2. EPA `Method Name` 与源行 `FEMorFRMtype` 完全相同。
3. EPA `Arithmetic Mean` 与 `PM25FM` 十进制精确相等。不使用 `1st Max Value`，不设接近容差，不与 PurpleAir 读数比较。

采样时长按仪器类型固定：重力法 `R & P Model 2025` 用 `24 HOUR`；连续 FEM（BAM-1020、BAM-1022、T640）用 `1 HOUR` 的日算术平均。`24-HR BLK AVG` 是另一条计算时长；均值不同则不合并、不平均。

同一 POC、方法、事件类型、原生时长和均值，只因 `Pollutant Standard` 重复时合并为一条。合并前提是均值已经相同。

事件键为：

`AQS 站点 + 日期 + 参数 88101 + POC + 方法代码 + 事件类型 + 原生采样时长`

共址设备连到同一键时只计一次参考，不按设备数重复计费。

### 4.3 什么才是一个有效设备日

对“设备 × 日期 × 参考型号”：

- 全部源行都连到同一个事件键：这是一个有效配对，参考值取该键的均值。
- 源行连到多个事件键：该设备日为 `EXCLUDED_AMBIGUOUS_MONITOR`。多个 POC 是不同监测序列，不是重复行。不得取最小 POC，不得保留第一条，不得平均，不得按与传感器的距离挑选。
- 任一源行不能联结：整个设备日为 `EXCLUDED_UNRESOLVED_ROW`。已经连上的兄弟行也不能单独留下来充当该日参考。

源行 8402 是已知的未联结行：IA3，站点 19-153-0030，2019-01-27，FRM，`PM25FM` 12.6。因此 IA3 在这一天的全部参考行都不可用，包括已连到 POC 1、均值为 13.3 的源行 8465。不得把 12.6 改成 13.3 或 14。

重算后，未联结行必须仍然只有 8402。若出现其他未联结行，或 8402 突然能够精确联结，状态写 `BLOCKED_METADATA`，停止，不要扩大排除名单。

### 4.4 处理顺序

1. 用原数据包和缓存中的 EPA 日文件重算联结。A/T 的参考数值不写入对外表格，只保存是否可联结。
2. 固定每个站点的参考型号：先比覆盖的时间段数，再比 154 天内唯一有效参考日数，平局按型号名称字典序。有效日只统计第 4.3 节的有效设备日。不用浓度大小。
3. 在胜出的型号下选一个代表设备：154 天有效配对日最多，平局按 ID 字典序。支持不足就剔除该站点，不换设备、不换型号。
4. 生成 V/T 的 `evaluation_panel.csv`。所有后续模型必须共用这一面板；本轮不跑模型。
5. 做接口隔离检查：训练入口只能读 D_fit 与 D_tune 的标签；A/T 标签读取必须拒绝。不训练模型，所以不声称预测不变性已经验证。

## 5. 状态与交付

只允许这些 P0 状态：

- 身份、单位、去重、支持和接口检查都通过：`PASS_P0`
- 站点或日期不够：`INSUFFICIENT_DATA`
- 重算后的未联结范围与第 4.3 节不符：`BLOCKED_METADATA`
- 同一新事件键出现不同参考值，或实现把第一条、平均值、最小 POC 写进了标签：`INVALID_RUN`
- 触达资源上限：`RESOURCE_PAUSE`

任一状态下 P1 都是 `NOT_RUN`。不要创建数值拟合脚本，不要写入 RMSE、ContrastMAE、收益或区间。不要把缺数值填成 0。

本运行目录至少交付：

- `P0_DATA_AUDIT.md`：来源、重算计数、排除的设备日、站点筛选和最终状态
- `site_map.csv`、`reference_events_metadata.csv`、`representative_devices.csv`
- `excluded_device_days.csv`：日期、站点、设备、型号、排除原因、源行号；不导出 A/T 浓度
- `split_manifest.csv`、`evaluation_panel.csv`
- `protocol_freeze.json`、`P0_status.json`、`ISOLATION_CHECK.md`
- `RESOURCE_AND_BUDGET.md`：继承 CPU 与本轮 CPU、墙钟、内存分开
- `README.md`：实际 PowerShell 命令
- `NEXT_STAGE_REQUEST.md`：即使 `PASS_P0`，也只说明 P1 尚未授权；不实现、不运行 P1

非 `PASS_P0` 时另写 `FAILURE_REPORT.md`。

## 6. 结束回复

用中文报告：

1. 两份旧状态是否仍为 `INVALID_RUN` 和 `BLOCKED_METADATA`，残留删除了什么，唯一输入移到了哪里。
2. 补做 P0 的状态，以及未运行 P1 的原因。
3. 重算后的未联结行是不是仍然只有 8402。
4. 若已经完成筛选：独立站点数、West/North 站点数、V 可评价日、T 可评价日和七天块数。未完成则明确写未确定。
5. 继承 CPU、本轮 CPU、墙钟和内存。
6. 审计、排除表、状态文件和下一阶段说明的绝对路径。

然后停止。
