# 方案 1：City Scanner 固定巡检预算下的热点排序筛选

设计日期：2026-10-18。设计技能：ccf-experiment-designer。模式：design。

本文件是可交给执行 AI 的完整方案，不代表实验已经运行。目的为低成本筛选现有方法是否具有值得独立确认的应用价值，不启动训练，不修改论文，不恢复 OF-v1 或未完成的 P2–projection 训练。

## 一、问题、范围与成功的含义

问题：在相同的网格复核数量下，现有 RAVEN 补全预测能否帮助一个回顾性巡检决策选中污染程度更高的网格，优于现有强模型和简单预测方法？

任务为“有标签支持上的回顾性污染热点复核排序模拟”。每个决策时段是已有数据的一个 UTC 30 分钟时间槽，每个候选是一个 500 m 网格。以冻结模型对该时段候选排序，预算内选择若干网格，离线真值只用于评分。候选集是共同可评价支持，不推断全城未观测网格。不将短时测量称为日均 AQI 告警，不声称执行了真实派车或前瞻预警。等网格数量不等于等行车时间。

本轮通过仅表示 `PASS_SCREEN`：值得考虑独立数据确认。旧 test 已被多轮研究使用，不能因这次预先固定了指标就称其为全新盲测。City Scanner 两块也可能共享原始采样，不能称为两个独立城市。

下述 20% 复核比例、10% 改善、0.01 标准差绝对改善及预测保护线，均为本轮建议的研究筛选阈值，不是既有部署合同或行业标准。必须在计算新端点前冻结，不能看结果后放宽。

## 二、已核对的资产及固定比较范围

项目根目录 `C:/Cursor/raven.mcs/`，下列路径均相对于该目录。

| 块 | 数据 | 结果入口 | 种子 |
|---|---|---|---|
| visit | `data/processed/cityscanner_nyc_pm25/` | `results_c1_cityscanner/round_v1/` | 32001–32010 |
| measured-O | `data/processed/cityscanner_nyc_p2_measured_o/` | `results_joint_ou/round_v1/` | 33001–33010 |

每块固定五个已训练方法：`fedavg_window`、`twostage_hajek`、`fedau_window`、`obsuse_window`、`raven`。每个目录均已发现 10 个 `checkpoints/final.pt`，总计100个。实际身份为历史冻结的完整 RAVEN-Design 等方法；不能把旧 `raven` 检查点擅自改称新 `raven_mcs` 配置训练结果。

检查点格式：`<结果入口>/runs/<dataset>/<method>/seed<seed>/checkpoints/final.pt`。
原评分分别在同级 `CS_ACCEPTED.json` / `JO_ACCEPTED.json`；组目标、编码在 `CS_TRAIN_SETUP.json` / `JO_TRAIN_SETUP.json`。

元数据核对值：
- visit：train 9343，validation 3290，test 2090；test 2021-11-16至12-15，共30个UTC日期。
- measured-O：train 9253，validation 2089，test 1687；test 2021-11-21至12-15，共25个UTC日期。
- test 中同一30分钟至少10个单元的候选时段：visit 59个、790个单元、24天；measured-O 50个、650个单元、20天。执行时还需验证单元等于唯一网格，去重后重新核对。
- 划分名称是 `validation`，不是 `val`。

本轮不扩大到六臂目标支持模型，避免在很多旧变体中挑选赢家。现有 City Scanner 简单参考投影比较尚未完成，不把未完成模型补为结果，也不自动训练它。本轮正结果不能证明完整 P2 优于投影。

## 三、资源与输出约定

建议总任务输出：`results_cityscanner_lowcost_screen/round_v1/`，包含 `shared/`、`hotspot/`、`target_shift/`。若已存在相同方案且身份一致的完成缓存则复用；若冲突，停止并报告，不覆盖旧证据。两个方案共享逐单元预测，只做一次推理。

运行约束：CPU、单进程、torch intra/inter-op线程各1、BLAS线程1、无DataLoader工作进程、一次一个模型、batch=256。用 `eval()` 与 `inference_mode()`；禁止 optimizer、backward、训练 runner、客户端重训、全轨迹驻留。允许为简单基线计算固定的历史均值。

共同预算（两方案合计）：共享推理最多600 CPU秒、20分钟主动wall；每方案统计最多180 CPU秒、10分钟主动wall。CPU按根进程及其子进程合计，包含失败尝试，不能只报worker或成功步骤。预算是硬上限，不是运行时间预测；到限保存已完成批次并暂停审批，不自动延长。

沿用已有机器内存保护：导入重库前可用内存至少2.5 GiB；运行中低于2 GiB暂停进入下一批，持续30秒则保存并退出，低于1 GiB立即退出。单进程RSS超过1.5 GiB也保存退出。资源失败记 `BLOCKED_RESOURCE`，不是科学失败。可以按完整模型的已完成推理批次恢复，不能把未完成训练的partial_model当本实验模型。

## 四、逐步操作

### H0：冻结范围与只读检查

1. 写 `shared/PROTOCOL_FREEZE.json`，固定方法、种子、数据版本、split、组映射、预算、主指标、阈值、bootstrap方案及本文件。
2. 检查100个模型及对应ACCEPTED记录齐备、终点为100窗口、同seed配对轨迹身份相符。核对现有记录即可，不新增通用hash流程。
3. 检查 unit_id 唯一、split无重叠、真值有限、同一个 `(spatial_id,absolute_time)` 不重复。重复记录若旧协议已有明确聚合规则就照旧；否则暂停，不临时求均值掩盖重复。
4. 仅用元数据构造候选时段：validation和test分开，每个时段至少10个不同网格；保留所有合格时段，禁止按真值大小或模型效果筛时段。
5. test每块至少40个合格时段、20个有合格时段的日期；validation至少20个合格时段、10个日期。低于门槛记 `INSUFFICIENT_SUPPORT`，不把时间槽改成日、也不降低最小网格数。已知test元数据满足，最终以唯一网格核验为准。

成功：资产与候选集可复现。失败：给出文件、身份或支持缺口，暂停相关块后续计算。

### H1：恢复逐单元预测，并复现旧指标

1. 以 `ProcessedDataset` 恢复原空间索引、组映射和时间索引；必须沿用全数据元数据构造的旧空间索引，不能重新只按test编号。
2. 只用train原子目标拟合原均值和总体标准差（ddof=0），参照 `src/raven_mcs/e3/canary/dataset_load.py::apply_train_zscore_standardization`；不能重复标准化。
3. 模型为 `src/raven_mcs/models/common_ndmf.py::CommonNDMF`。可复用 `src/raven_mcs/e3/real_runner/runner.py::CommonNDMF_from_ckpt` 的结构恢复逻辑；审查导入副作用，必要时在独立推理脚本中调用模型类和load_state_dict，禁止创建完整训练runner。
4. 特征必须复用 `models/features.py::extract_features`：absolute_time转Unix小时、UTC hour/weekday、trend=time_index/(全数据max_time_index+1)。不能把Unix纳秒、原始datetime或无归一time_index当旧特征。空间ID未知时停止，不能默默映射到0。
5. 先对两个块的首个RAVEN模型验证。用与旧 `_predict` 相同的语义分批前向。恢复物理单位：`y_hat_phys=std_train*y_hat_z+mean_train`；真值同理。不能裁剪负预测或进行新后处理。
6. 用旧mu和旧全test集合重算 RMSE_mu、MAE_mu、WorstGroupRMSE及四个组RMSE，与ACCEPTED对比：每项绝对误差必须≤`1e-6 + 1e-5*abs(old_value)`。通过首模型后处理其余模型，每个模型都核对。与组组成有关的Delta指标不从最终预测重建。
7. 若已有同身份预测缓存，验证unit_id、尺度、终点和复现指标后复用。缓存必须覆盖validation和test，不能只凭文件名认定可用。
8. 每个模型写一个预测分片，完成即释放模型。每行至少：block、method、seed、split、unit_id、spatial_id、absolute_time_utc、date_utc、target_group、y_true_z、y_pred_z、y_true_phys、y_pred_phys。保存scaler与组映射。

成功：100个模型均可复现其旧预测指标。单块有缺失/不符不允许悄悄删除配对种子；暂停该块并写差异。无需训练复现。

### H2：构造强简单对照、冻结主比较者

除四个已训练对照，再加入三个固定简单对照，形成七个非RAVEN候选：

1. **Delivered-SpatialMean**：每个seed从对应EventTrace的U=1记录读取observed_unit_ids，限定原train。用client_measurements中的实际potential_measurement，不用隐藏的完整train目标或validation/test标签。重复的(client,unit)只计一次，同一unit多客户端测量先取均值；按网格求历史均值。无该网格历史时依次退回同region均值、全局已交付历史均值。
2. **Delivered-CellBlockMean**：同一历史信息，按网格×UTC六小时块求均值；该桶至少3个不同unit才启用，否则退回SpatialMean。不得搜索桶数或最小计数。
3. **Fixed-Ensemble**：同seed FedAvg与TwoStage-Hajek预测的0.5/0.5平均，不拟合混合系数；报告部署需要两次模型推理。

EventTrace入口：visit为 `artifacts/e3_c1_cityscanner_eventtraces_v1/cityscanner_nyc_pm25/seed*/training_eventtrace/events.parquet`；measured-O为 `artifacts/e3_joint_ou_cs_p2_eventtraces_v1/cityscanner_nyc_p2_measured_o/seed*/training_eventtrace/events.parquet`。读取最少列并逐seed释放。观测ID若为JSON字符串须解析。数据身份缺失时标记baseline unavailable，核心筛选不能因缺强简单基线而自动通过。

在validation上按第H3节主指标，先对天、再对seed等权，选择最小J的非RAVEN方法 `b_H`。每块一个，所有seed共用，不为各test天挑不同赢家。完全相等按预先写下的方法名词典序打破平局。记录全部validation值、选择结果后冻结 `hotspot/BASELINE_SELECTION.json`，随后才计算test热点端点。

### H3：计算冻结的巡检端点

主预算：每个时段 `k=ceil(0.20*N)`；N为该时段共同候选网格数。另算10%和30%作敏感性，不替代主预算。

每个方法按预测物理PM2.5从高到低选k个；预测并列按spatial_id词典序，与真值无关。设T为真值最高的k个，S为方法选择，sigma为该块train标准差：

`J_m(s,t) = [sum_{i in T} y_i - sum_{i in S} y_i] / (k*sigma)`。

J越小越好，表示每次复核机会损失的污染值，以训练标准差归一。另报分子除k的物理单位损失。J的差异衡量排序决策，不等于预测RMSE变化。主要汇总是时段内计算→同一天等权平均→日期等权平均→10个seed等权平均。两块独立报告。

次要端点：
- 热点捕获率H：真实top-k中被选中的比例。真值阈值并列时用分数成员：高于阈值权重1，等于阈值权重 `(k-严格高于者数)/并列者数`，H=所选成员权重之和/k。
- 全test的原目标RMSE_mu、WorstGroupRMSE；采用旧mu和旧评分集合，不能只报热点子集。
- 各region被选择比例、预算k、候选N、数据支持覆盖；仅作解释，不将选择比例再次当成功目标。
- 随机均匀选择的期望J可解析计算为 `(sum_T y/k - mean_all y)/sigma`，无需模拟，作为任务难度参照，不代替强基线。

### H4：配对不确定性与筛选门槛

每块都对固定的b_H与RAVEN计算：
- `D=J_bH-J_R`，正数为RAVEN改善。
- `G=D/J_bH`，J_bH≤1e-8时不计算相对改善，记无可测改善空间。
- `DeltaH=H_R-H_bH`。
- 两个预测代价 `RMSE_R/RMSE_bH-1`、`Worst_R/Worst_bH-1`。

Bootstrap 10000次，固定seed=2026101801：每次配对重采样10个seed；按完整test日历做长度3天的循环移动块重采样，截取到原日历长度。所有方法使用相同seed和日期抽样索引。保留无合格时段日历日，汇总时按有可用时段的抽样天加权；日期重复必须按重复次数计入。不能把网格/时段当独立样本。统计前缓存seed×日期的J/H，bootstrap只重采样小矩阵，不反复加载模型或复制全部预测。若抽样没有合格日期，重抽并记录；比例超过1%则暂停置信判定。

对D报告95%双侧区间，以及主判定所用单侧98.75%下界（bootstrap的0.0125分位数）。这是两方案×两块四个预先主比较的Bonferroni分配；即使某比较未执行也不回收alpha。该block-bootstrap是探索性不确定性估计，不是无假设有限样本保证。另用7天块做一次相关性敏感性，报告符号与区间，不选择更有利块长。

**单块 `PASS_SCREEN` 必须同时满足：**
1. 资产/评分核验通过，全部10个配对seed、规定支持完整。
2. 相对b_H，J下降至少10%，且D至少0.01训练标准差。
3. D的单侧98.75%下界>0。
4. 热点捕获率点估计不下降超过2个百分点。
5. 全test RMSE_mu和WorstGroupRMSE相对b_H的点估计代价各不超过5%。这只是筛选保护线，不能写成已证明统计非劣。
6. test上RAVEN的J点估计也低于其余六个非RAVEN候选；若只赢验证集选定者、却输给另一简单方法，记 `BEATS_SELECTED_ONLY`，不能作为通过。
7. 7天块敏感性bootstrap中D的中位数仍为正；其区间是否含零照实报告，不借此更换主块长。10%和30%预算完整披露，但不用于拯救20%主结果。

两块都通过才记 `PASS_BOTH_PROTOCOLS`；一块通过只能记 `PASS_ONE_PROTOCOL`并具名该块。任何结果都保留 `P2_VS_PROJECTION_UNRESOLVED`，除非未来另有已完成且核验的同协议投影证据；本轮不补训练。

点估计过实用线、区间未过：`INCONCLUSIVE`，暂停扩展，不自动增加seed/重训。点估计未过实用线：`FAIL_SCREEN`，并报告是小收益、预测代价、强基线胜出或无改善空间。技术/资源失败单列，不当成方法无效。

## 五、失败处理与具体报告

任一步失败，停止该步之后的依赖计算；保存完成的共享缓存和原始分数。不得改预算、改k、换时段、换主基线、删seed或启动训练。允许完成定位失败所需的轻量核验，然后提交报告，等待用户决定是否继续。一次失败不意味着自动取消另一个独立方案。

必须交付：
- `shared/ASSET_MANIFEST.csv`：块/方法/seed/检查点/原评分/配置/数据身份/状态。
- `shared/REPRODUCTION_CHECK.csv`：每个模型每个旧指标的old/new/diff/tolerance/pass。
- `shared/predictions/`：可复用的逐模型逐单元预测分片。
- `hotspot/POOL_MANIFEST.csv`：split/时段/date/N/k/入选或排除原因。
- `hotspot/WINDOW_SCORES.csv`：block/seed/method/budget/time/N/k/J/J_phys/H。
- `hotspot/DAILY_SCORES.csv`、`SUMMARY.csv`、`PAIRED_COMPARISONS.csv`：分别保存日分数、每法点估计、固定主比较及全部其他比较；主/次要标记明确。
- `hotspot/RESOURCE_AND_BUDGET.md`：本轮和共享累计CPU、wall、峰值RSS、最低可用内存、缓存复用、失败成本；不能重复计费也不能漏计共享成本。
- `hotspot/DECISION_REPORT.md`：每一步实际命令、脚本入口与参数、开始结束、输入输出；门槛实测值与判断；是否需要独立确认；当前能支持的主张。
- 若失败/不确定：`hotspot/FAILURE_REPORT.md`，写明失败阶段、预设阈值、实测值、影响范围、日志证据、可恢复位置、尚未执行任务、最小可选修复及其是否改变协议。不得把猜测根因写成已确认原因。

建议图仅两张：20%预算下每seed的配对J差；10/20/30%预算的J与H曲线（同轴单位标明）。不用挑选个案热图代替主比较。

报告结尾回答：收益是否进入巡检决策？是否胜过强简单对照？代价多大？是否仅为旧test探索？同协议投影缺口是否仍存在？本轮不自动将结果写入论文。

## 六、执行入口约定

执行AI先在新输出目录实现一个独立只读驱动 `screen_cityscanner.py`，而不是改旧训练驱动。以下是需实现的命令接口，不是当前已存在的可执行程序；所有阶段默认同时处理两个块，支持 `--block visit|measured-O` 明确缩小范围，不能按结果自动选择块。

```text
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py audit --experiment hotspot
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py predict --canary
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py predict --remaining
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py baselines
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py select-baseline --experiment hotspot
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py hotspot --split test
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py report --experiment hotspot
```

从项目根目录运行，Python使用现有 `.venv_new/Scripts/python.exe`。每个命令必须先检查上一阶段状态和剩余预算；失败返回非零，report仍可独立执行。开始推理前用少量同一模型单条与批量输出核对实现一致性即可，不额外堆叠冒烟实验。不安装新包，不在本轮设计阶段执行这些命令。
