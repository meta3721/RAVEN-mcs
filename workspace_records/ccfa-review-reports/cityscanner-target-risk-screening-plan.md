# 方案 2：City Scanner 部署目标变化下的风险稳定性筛选

设计日期：2026-10-18。设计技能：ccf-experiment-designer。模式：design。

本文件是可交给执行 AI 的完整方案，不代表已经计算新风险结果。只做冻结模型的离线筛选，不训练、不改论文、不恢复OF-v1或P2–projection训练。可独立执行；与方案1共享预测，避免重复推理。

## 一、研究问题与证据边界

问题：在同一个已训练模型上，平台改变四个区域的服务权重后，RAVEN是否比简单方法具有更低的最坏预测风险？

改变的是评分目标mu，不改变训练、模型或区域条件分布。结果只能解释已有支持上的目标重加权，不能称为新城市泛化、概念漂移适应、新目标训练收益或自动补齐未观测支持。目标权重是服务优先级，不是为使RAVEN胜出而搜索的参数。

本轮为筛选：旧test已用于多轮研究，两块可能共享原始数据。通过记 `PASS_SCREEN`，核心新增主张仍需未参与选方案的时间/空间数据确认。100个模型不是100个独立城市样本。

以下TV半径0.10、最坏MSE改善2%、名义RMSE保护1%等是建议的研究筛选阈值，非已有业务要求。先冻结再计算，不能事后替换。

## 二、固定资产

项目根目录 `C:/Cursor/raven.mcs/`。相对路径与范围：

| 块 | 数据目录 | 结果入口 | seed |
|---|---|---|---|
| visit | `data/processed/cityscanner_nyc_pm25` | `results_c1_cityscanner/round_v1` | 32001–32010 |
| measured-O | `data/processed/cityscanner_nyc_p2_measured_o` | `results_joint_ou/round_v1` | 33001–33010 |

每块五方法 `fedavg_window, twostage_hajek, fedau_window, obsuse_window, raven`，各10个最终检查点。路径为 `<入口>/runs/<dataset>/<method>/seed<seed>/checkpoints/final.pt`。

同级 `CS_ACCEPTED.json` / `JO_ACCEPTED.json` 已保存四个组RMSE，字段 `WorstGroupRMSE_R0` 至 `WorstGroupRMSE_R3`；先核对旧评分函数确为对应组的RMSE，再平方恢复组MSE。字段名的Worst不意味着这四个数都是全局最大值。

目标从 `CS_TRAIN_SETUP.json` / `JO_TRAIN_SETUP.json` 读取，组顺序均为region0–3：
- visit mu0约 `[.2373205742,.4746411483,.0708133971,.2172248804]`。
- measured-O mu0约 `[.6496975806,.1350806452,.0725806452,.1426411290]`。
最终用JSON全精度，不用上述截断值重建协议。

数据核对：visit train/validation/test分别9343/3290/2090行；measured-O分别9253/2089/1687行。全部test用于主分析，不沿用热点方案的N>=10时段筛选。四个组test行数分别为visit `[496,992,148,454]`，measured-O `[1080,210,121,276]`。组标签与编码必须按冻结映射核对。

本轮不加入六臂目标变体，不把未完成的简单投影训练当基线。当前结论对象是历史冻结完整RAVEN-Design模型，不改称新配置训练结果。

## 三、资源、输出与执行顺序

使用 `results_cityscanner_lowcost_screen/round_v1/shared/` 和 `target_shift/`。已有同身份完成预测可复用；冲突时暂停、不覆盖。

推荐先执行T0：利用已有四组RMSE做无推理支配预检。若本路线已被简单方法支配，可立即交付筛选失败，减少后续计算；方案1仍可独立检查排序，因为MSE支配不必然意味着排序支配。

若进入推理：单CPU进程，torch和BLAS各1线程，batch=256，一次一个模型，eval/inference_mode，无训练runner、无梯度、无optimizer。共享推理上限600 CPU秒/20分钟主动wall；本方案统计上限180 CPU秒/10分钟主动wall。包含失败尝试和子进程CPU，两个方案复用共享账而非各算一次或漏计。

内存：导入前可用≥2.5 GiB；运行低于2 GiB暂停下一批，持续30秒保存退出；低于1 GiB立即退出；RSS>1.5 GiB保存退出。到预算或资源线记 `BLOCKED_RESOURCE`，不自动重启或扩预算。新执行程序应在完整推理批次之间保存进度。

## 四、逐步操作

### T0：冻结目标集合，做最便宜的支配预检

在读取新比较结果之前写 `target_shift/PROTOCOL_FREEZE.json`：固定数据/方法/seed、组编码、mu0、目标集合、主半径、基线选择、阈值、统计规则及本方案。

定义组风险：

`e[m,s,g] = mean_{test units in g} (y_hat_z-y_z)^2`。

定义全组均值 `e_bar[m,g]=mean_s e[m,s,g]`。不可先平均RMSE再平方；必须各seed的组RMSE先平方，再平均MSE。

从100份旧ACCEPTED读取四组RMSE，平方生成 `GROUP_RISK_FROM_FROZEN.csv`。检查均有限、非负、完整10seed；缺字段不能由总体RMSE猜出四组风险。

对四个已训练非RAVEN方法分别检查：
- **均值支配**：所有g均有 `e_bar[b,g]<=e_bar[R,g]`，至少一组严格更小。
- **逐seed支配**：所有s,g均有 `e[b,s,g]<=e[R,s,g]`，且至少一项严格更小。
- 相差在 `1e-8 + 1e-6*max(abs(e_b),abs(e_R))` 内记numerically indistinguishable，不用浮点噪声宣布支配；有微小反向项时写近似支配，不套严格结论。

若均值支配成立，任意共同非负目标mu下，平均加权MSE都不能使RAVEN严格优于该方法；但这不自动等同于逐seed最坏风险的支配。若逐seed支配成立，则本轮“平均逐seed最坏风险”主端点也不可能优于它，可直接记 `FAIL_DOMINATED`，保存可复算的支配证据，停止本路线后续推理。均值支配而逐seed不成立，记录为强不利证据，仍可按冻结主端点继续，不偷换max与平均的顺序。

证明只针对当前模型、当前组风险和所测分布，不外推真实总体或未来数据。

### T1：构造目标集合与求解器

固定主集合：

`U_delta={mu: mu_g>=0, sum_g mu_g=1, 0.5*||mu-mu0||_1<=delta}`。

主半径delta=0.10，表示最多搬移10%的总目标质量。敏感性delta取0、0.05、0.20；另报整个单纯形的极端风险作描述，不能用其替换主半径。无需增设事后有利的区域上下界。

对每个m,s：

`W[m,s,delta]=max_{mu in U_delta} mu^T e[m,s]`。

主汇总 `W_bar[m,delta]=mean_s W[m,s,delta]`。它是平均逐seed最坏MSE，不是 `max_mu mu^T mean_s e`。后一种可以另报为COMMON_TARGET_WORST，不可混同。

四组小型LP：变量mu(4)和t(4)，最大化mu·e；约束mu>=0、t>=0、sum mu=1、mu-mu0<=t、mu0-mu<=t、sum t<=2delta。记录每个最坏目标mu*。复核可行性、目标重算残差≤1e-8；无需引入新的大型优化框架。

可用质量转移贪心优化加速bootstrap：按e从低组向高组转移最多delta质量，donor不能小于0、receiver不能大于1；只有严格提高目标的转移才有意义。先与100个真实组风险向量的LP结果比对≤1e-8再使用，不用近似采样目标代替最大化。

检查三个恒等关系：delta=0恢复mu0·e；W随delta不减；整个单纯形极值等于max_g e_g。失败属于实现错误，停止修复，不能进入效用判定。

### T2：共享预测、强简单基线与validation选择

只有T0未直接终止时才需补齐逐单元预测和validation。若方案1已输出通过核验的共享缓存，直接复用。

恢复方法：使用ProcessedDataset原有空间索引和group编码，train-only均值/总体标准差；CommonNDMF检查点；`models/features.py::extract_features`的Unix小时、UTC星期和原time_index/(max_time_index+1)特征。不能改时间尺度、组编号、模型结构或裁剪预测。原 `real_runner/runner.py::_predict` 提供评分语义，使用独立批量推理程序实现，不运行任何训练驱动。

每模型重算原全test RMSE_mu/MAE_mu/WorstGroupRMSE和四组RMSE，与旧ACCEPTED满足 `abs(new-old)<=1e-6+1e-5*abs(old)`。同时核对T0恢复组MSE与新预测组MSE。输出validation和test全部unit的标准化与物理单位预测；每模型完成即释放。

加入三个固定非RAVEN简单对照，连同四个已训练对照共七个：
1. Delivered-SpatialMean：每seed EventTrace中U=1的train observed_unit_ids；读取实际client_measurements，去重(client,unit)，同unit多客户端先平均；网格历史均值，缺失退同region、再退全局已交付历史均值。
2. Delivered-CellBlockMean：同历史，网格×UTC六小时桶至少3个unique unit时用桶均值，否则回退SpatialMean。
3. 同seed FedAvg和TwoStage-Hajek预测固定0.5平均，无混合系数拟合。

事件入口分别为 `artifacts/e3_c1_cityscanner_eventtraces_v1/<dataset>/seed*/training_eventtrace/events.parquet` 和 `artifacts/e3_joint_ou_cs_p2_eventtraces_v1/<dataset>/seed*/training_eventtrace/events.parquet`。只读取需要列并逐seed释放；observed_unit_ids字符串按JSON解析。禁止让简单基线使用隐藏完整train目标或test标签。缺强基线时可报告已有比较，但不记完整筛选通过。

在validation的组MSE上，使用同一mu0和U_0.10，选择W_bar最小的非RAVEN方法 `b_T`。每块一个固定方法，跨全部seed，不按test目标或seed另选。平局按固定方法名词典序。冻结选择结果，随后评价test主端点。b_T可以与热点方案b_H不同，二者回答不同任务。

### T3：主比较、归因和不确定性

计算全部方法的：
- 每seed/组MSE与物理尺度MSE。
- 名义目标MSE `mu0·e`，名义RMSE逐seed开根号后再平均。
- delta=0、.05、.10、.20下的W及对应最坏目标mu*；整个单纯形极端值。
- RAVEN相对固定b_T的 `D_W = mean_s(W_bT-W_R)`、`G_W=D_W/W_bar_bT`。
- 名义RMSE相对代价 `mean_s RMSE_R / mean_s RMSE_bT -1`。
- 全部其他简单方法的同指标比较与支配关系。

各方法最坏mu*可以不同，这正是最坏风险比较；不能由W_R<W_b推出RAVEN在每个相同mu都更好。

需要描述“整个U内都优于某个基线”时，另解：
`A_s=max_{mu in U} mu^T(e_R,s-e_b,s)`。
只有该共同目标差在相应口径上<=0才能支持逐点优势，不用两个最大值之差替代。此项是解释性分析，不作为更换主假设的入口。

Bootstrap10000次、seed=2026101802：配对重采样10seed，再按完整test日历用3天循环移动块抽样并截取到原长度。所有方法共享样本索引，日期重复计入重复次数。每次从抽到的逐单元平方误差重新汇总各组MSE，再重新求W；不能仅对冻结W表bootstrap后称其反映日期不确定性。为降低开销，先保存method×seed×日期×group的SSE及计数，用抽样日期的重复次数加权汇总SSE/count，数学上等价于上述逐单元计算；不要每次复制原始预测或启动LP进程。

若抽样造成任一目标组无单元，则丢弃该次并重抽；记录比例，超过1%记 `INSUFFICIENT_RESAMPLING_SUPPORT`、暂停置信判定，不填零或重归一删组。单模型数据中每组至少50个test unit、至少10个日期，否则只报描述性值。本次元数据满足，仍按缓存核验。

报告95%双侧区间；主比较D_W使用单侧98.75%下界（0.0125分位数），与两方案×两块四主比较共享Bonferroni预算，不因其他失败回收alpha。另用7天块作一次相关性敏感性，不能挑更有利结果。bootstrap为探索性估计，不宣称处理任意时间依赖的严格保证。

### T4：明确成功门槛

**每块 `PASS_SCREEN` 同时满足：**
1. 身份、预测复现、全部10seed、组覆盖、七个非RAVEN对照完整。
2. 主delta=.10下，RAVEN平均逐seed最坏MSE相对验证集选定b_T至少下降2%。这是MSE改善，不是RMSE下降2%。
3. D_W的单侧98.75%下界>0。
4. 名义目标RMSE相对b_T的点估计代价≤1%。此为实用筛选保护，不是已证明统计非劣。
5. delta=.05和.20下，最坏MSE相对b_T均不恶化超过2%；不允许只在一个精挑半径胜出。
6. delta=.10时RAVEN的最坏MSE点估计低于其余六个候选；若输给其他简单方法，标记 `BEATS_SELECTED_ONLY`而非完整通过。
7. 7天块敏感性bootstrap中D_W中位数仍为正；区间是否含零单独报告，不借此更换主块长。所有风险单位、max/mean顺序一致。

两块通过为 `PASS_BOTH_PROTOCOLS`；一块通过为 `PASS_ONE_PROTOCOL`，不能称跨协议稳定优势。无论通过多少块，保留 `P2_VS_PROJECTION_UNRESOLVED`。缺少City Scanner投影训练不是授权补训练。

判定其他状态：
- `FAIL_DOMINATED`：T0逐seed支配使主端点不可能胜出。
- `FAIL_SCREEN`：实用改善不足、保护线超限或更强简单方法胜出。
- `INCONCLUSIVE`：点改善达门槛但不确定性未过；不自动增加seed。
- `BLOCKED_DATA / BLOCKED_REPRO / BLOCKED_RESOURCE`：对象、复现、资源问题，不能写成科学失败。

## 五、报告、失败处置与下一步

任何失败后先输出本阶段已完成的结果和原因，不改delta、不改mu0、不增删区域、不删seed、不重新训练、不把组MSE支配改成别的有利主指标。可完成定位错误的轻量核验；是否修复或扩大由用户审阅后决定。另一方案若已获执行授权可使用完整共享缓存独立评估。

输出目录 `target_shift/` 必须包含：
- `PROTOCOL_FREEZE.json`、`BASELINE_SELECTION.json`。
- `GROUP_RISK_FROM_FROZEN.csv`：block/method/seed/group/old_RMSE/recovered_MSE。
- `DOMINANCE.csv`：baseline/RAVEN、每组差、是否mean支配/逐seed支配、数值边界和严格程度。
- `GROUP_RISK.csv`：split/block/method/seed/group/n_units/n_days/MSE_z/MSE_phys。
- `ROBUST_RISK.csv`：block/method/seed/delta/W_z/W_phys/mu_star0..3/solver residual/mean-max定义。
- `SUMMARY.csv`、`PAIRED_COMPARISONS.csv`：全部方法、固定主比较、其他描述性比较、收益、保护线、区间。
- `RESOURCE_AND_BUDGET.md`：共享与本方案成本、失败尝试、缓存复用、峰值RSS和停止原因。
- `DECISION_REPORT.md`：每一步实际命令和参数、输入输出、操作顺序、门槛实测值、PASS/FAIL/INCONCLUSIVE/技术阻断、可支持的主张。
- 若未通过，`FAILURE_REPORT.md`：失败阶段、具体阈值和实测值、根因证据与不确定部分、已完成/未执行项目、可恢复位置、最小修复及是否改变协议，等待审批。

建议图：各方法四组MSE点估计与seed散点；delta从0至.20的最坏MSE曲线；在固定主半径下逐seed配对差。不绘制只截取RAVEN获胜区域的目标图。

报告结尾必须回答：是否存在简单方法逐组支配？最坏风险是否真正改善？是否以牺牲名义风险换取？优势是否只在某个半径？结果对哪个协议成立？为何仍是探索性证据？是否尚缺同协议projection？

本轮成功只提交独立确认建议，不自动开展新训练或把数字写入论文。

## 六、执行入口约定

执行AI在新输出目录实现独立只读驱动 `screen_cityscanner.py`，与方案1共用预测和简单基线代码。下面是需实现的接口，不是当前已存在的程序；先写代码再执行，不能把这些命令的列出当成实验完成。

```text
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py audit --experiment target-shift
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py dominance --from-frozen
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py risk-solver-check
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py predict --canary
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py predict --remaining
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py baselines
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py select-baseline --experiment target-shift
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py target-shift --split test
python results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py report --experiment target-shift
```

从项目根目录使用现有 `.venv_new/Scripts/python.exe`，不安装新包。每个阶段检查前序状态和剩余预算。支配预检已失败的块不得进入后续求解/推理，report独立可用；若共享缓存已完整通过，predict命令只验证并复用。缺少projection不触发新训练。设计阶段不执行以上命令。
