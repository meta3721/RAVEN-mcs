# 续行指令：复用已完成首批，补完剩余十条并给出最终筛选结论

日期：2026-10-19。使用技能：ccf-experiment-designer；报告与数字核对采用ccf-integrity-auditor的证据口径。

## 1. 当前判断与下一步

依据：`C:/Cursor/raven.mcs/results_zero_safe_buffer/round_v1/backend_pilot/training_run_v1/EXPERIMENT_REPORT.md`及FIRST_BATCH_REPORT、RESTORE_CHECK、SEED_COMPARISON、COST_PROJECTION、累计预算和实际CLI代码。

当前可接受的阶段状态：FIRST_BATCH_COMPLETE / TRAINING_VERIFIED。seed33001五臂各100关闭、9点评分，共5条完整轨迹和45个评分点。F1/F2进程内恢复通过，F1新进程恢复通过，最大误差和侧向评分差均为0。

科学效果尚未通过：首seed的L分别是I 1.9943576994、F1 2.0281256236、F2 1.9981927075、TwoStage 2.0020178982、FedAvg 2.0119143516。相对I，F1/F2的L约恶化1.69%/0.19%，最终RMSE约恶化12.25%/14.76%。不能把成本下降、D优势或FIRST_BATCH_COMPLETE写成预测收益。

建议补完原计划剩余两seed，而不是调参补救。理由：单seed不能替代预先规定的三seed判断；后续费用预测加20%余量为348.2625 CPU秒、374.455603秒wall，低于剩余2251 CPU秒、3440.005658秒wall。完成剩余10条是形成完整结论的有限投入，不是已预测它们能扭转结果。

本次先修正一个调度入口错误、补齐剩余输入与计时记录，再按原五臂顺序运行。不要重复首批，不重新建设训练后端，不再追加一轮全量静态审计。

## 2. 授权范围与文件边界

项目根目录：`C:/Cursor/raven.mcs`。

结果目录继续使用：`results_zero_safe_buffer/round_v1/backend_pilot/training_run_v1/`。五臂驱动位于上级backend_pilot目录。

首批报告明确记录此次训练只覆盖seed33001，因此不能把它当成剩余10条的授权。用户仅要求本次“评估状态、写下一步指令”，不启动训练。

如果用户随后明确要求“执行本指令，完成33002和33003的十条真实训练”，则按本文件成功阶段连续执行，不重复询问。没有该授权时，只完成必要可逆代码修正和非训练输入准备，交付启动入口与READY_FOR_REMAINING_AUTHORIZATION，止于训练前。

不改论文，不用test选择或判定，不改变候选、数据、μ、Design、Gate语义、H、学习配置和门槛；不增加S/P2/OF、新机制或新seed。任何失败暂停依赖工作，等用户审批后决定修复、停止还是继续。

## 3. C0：修正remaining入口误拦，保持首批结果有效

### 3.1 已定位的错误

`backend_pilot/run_pilot.py::_first_batch_ready`目前要求seed33001五行全部status=COMPLETE且restore_pass为真。

但实际清单里I、TwoStage、FedAvg的restore_pass是False，因为这些臂没有被安排缓存恢复重放；F1/F2为True。当前逻辑会使已经完成真实训练和规定恢复核验的首批仍被REMAINING_REFUSED拦住。EXECUTION_ENTRY.md还残留“首批五臂没有完成”的旧表述。

这属于入口判据实现错误，不是首批科学结果无效，不应通过重跑五条、强制把False改True或删除门槛来处理。

### 3.2 最小修正

入口读取具体证据并检查：

1. 首seed恰好五个规定臂，无重复；五臂状态COMPLETE，各有100关闭、9个既定评分点及可定位的模型/结果。
2. REAL_UPDATE_CHECKS中的必要真实训练检查通过；F1/F2的规定进程内恢复通过。
3. RESTORE_CHECK记录至少一个规定缓存臂的新进程恢复PASS，并对应同一首批/断点。原协议不要求即时臂也执行这一缓存检查。
4. 首批没有未处理的实现失败，累计预算有效；后续费用预测满足余量要求。

将“该臂未安排恢复”表示为NOT_REQUIRED或相应适用性字段；保留原False的历史含义，不能把未做过的恢复改成PASS。基于真实文件生成首批整体判定。

只做两个针对入口的非训练检查：现有合法首批应放行；复制的临时元数据中去掉一条完成证据或规定恢复证据应拒绝。不改真实结果，不再次神经训练，不扩成一套重复测试。

remaining执行还必须可续行：只运行未完成的合法队列项；已经COMPLETE且证据有效的33001五臂绝不重跑。剩余队列若部分完成，先核对完成项；中断项按完整断点resume，不能从close0覆盖重训。遇到无法解释的FAILED记录，先报告审批，不自动清掉。

更新EXECUTION_ENTRY.md和新的REMAINING_READINESS.md，避免计划文件继续把训练状态描述为UNRUN或声称没有真实训练。

成功：记REMAINING_GATE_FIXED，不修改任何首批预测值。失败：记录REMAINING_GATE_INVALID，给具体缺项，暂停训练。

## 4. C1：准备33002/33003冻结参考，补齐费用证据

### 4.1 只处理尚未完成的两个seed

seed33001冻结表已通过，不重建、不覆盖。生成或核验：

- `frozen_reference_seed33002.json`
- `frozen_reference_seed33003.json`

复用原reference_replay与已修复的稳定attempt映射，按同一冻结源U=1、m/c/group_mass定义建立只读表。每seed的I/F三个臂共用该表，不能重新为每臂拟合参考。

使用源记录/稳定attempt对应核对集合、重复项、retry、trace身份和各向量维度；数值误差≤1e-6。输出条数及首个差异位置。只读训练元数据，不使用validation/test误差。若已存在合法对应表则直接复用。

不要把同一表复制两份相比较，称为独立数值复现。将证据分清：原参考重建函数提供数值来源，驱动的独立源记录遍历核对ID和一对一映射，驱动加载核对读取字段与实际使用值。本项不是重新运行整批调度轨迹。

准备函数应参数化seed，不能运行硬编码33001的runtime_check来声称其余两个已通过；不需要重跑其余已经通过的纯检查。

成功：两seed均REFERENCE_READY。任一缺失/不一致记REFERENCE_IDENTITY_MISMATCH或BLOCKED_ASSET，暂停其后训练，不重新定义参考。

### 4.2 保持原成本门槛可核验

当前首批摘要保存总wall与分类CPU，但RunMonitor.categories未保存各类别wall。原门槛要求部署必需路径wall比，因此不能用总wall冒充部署wall。

在剩余运行前为分类计时补存CPU和wall起止，保持方法及训练执行顺序不变。分类：部署必需、科学评分、额外D诊断、恢复复验、输出/保存等；明确必需快照管理属于部署路径。分类不可重叠相加，所有费用仍进总硬预算。

对首批：优先从已有原始计时日志还原部署wall；若无足够原始数据，则标DEPLOY_WALL_UNMEASURED，不能按CPU比例估算，也不能把总wall标成部署wall。不要为补计时重跑首批。最终可给有证据支持的保守界；若无法证明≤1.25，成本判定写UNRESOLVED，不能无条件判整体PASS。

补齐首批与后续各臂资源峰值/最小空闲、实际使用/终态、观测损失等可由原日志导出的列；缺失项明确标记，不能编造0。

成功：新运行完整记录分类CPU/wall，旧首批的已测/未测字段明确区分。旧wall缺失是证据缺口，单独说明；不因此把已有预测结果改成无效，也不把未知成本自动判失败。

## 5. C2：执行剩余十条，禁止根据中途输赢改变队列

依赖：C0、两seed输入通过；用户已明确授权剩余10条；当前资源和累计预算满足条件。

工作目录：`C:/Cursor/raven.mcs`。

完成入口修正后使用：

```powershell
& 'C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe' 'results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py' --execute remaining --authorize-training
```

固定顺序：33002的I-Proj-ZS、F1-Proj-ZS、F2-Proj-ZS、TwoStage-Hájek、FedAvg-Window，再33003同序五臂。若已经合法完成部分项，跳过这些完成项，不覆盖。

每臂100关闭，编号0–99；完成20、30、…、100关闭时评分，共9点。保留首批45点，新增90点，总计135点。对固定validation评分；test不进入此轮选择。

CommonNDMF、原train尺度与特征、本地学习率0.01、本地2步、服务器学习率0.01、注册模型快照和attempt随机流保持不变。H=2、S_max=5、64客户端有效池、小K cap/ESS、二次参考投影、零质量隔离与latest-positive保持原配置。

外部基线继续用各自完整局部损失和概率链路，遵守真实到达和本臂时效；源U保持冻结，不重新抽取参与/网络结果。

已有恢复核验可复用；remaining代码如仍会自动额外跑一次新进程probe，应改为读取既有通过证据后跳过。不要逐seed重复新进程恢复或重复第一批，只保留新增路径实际需要的检查。若代码因新输入暴露错误，按失败规则暂停，不自动边改边无限重试。

每臂完成更新manifest、检查点、预测、生命周期和成本账，释放模型/缓存，检查下一臂启动条件。科学运行中途不根据误差决定停哪一个候选，不在33002后宣布跨seed赢家，也不追加高收益窗口。

成功：15条完整、每条9点、全部源身份一致，记THREE_SEED_RUN_COMPLETE。单个资源中断记RESOURCE_BLOCKED，不能将未完成当作方法输赢。

## 6. C3：统一重评分与预先固定的科学判定

优先复用逐点预测和模型，独立重算指标/汇总，不重训。核对首批原有五行L与新汇总数值一致，差异须有来源解释，不静默替换。

每seed每方法：

`RMSE_mu(r)=sqrt(sum_g mu_g*mean_{i in val_g}((prediction_i-y_i)^2))`

`L=mean_{r in {20,30,...,100}} RMSE_mu(r)`。

WorstGroupRMSE先每点取四组最大RMSE，再平均九点和seed。μ与目标组不重归一，不删困难组。报告各组误差、九点曲线、最终误差、实际投影失配、提交/替换和服务器步数。

三个seed完成后，按三seed平均L选全局F*∈{F1,F2}，全局N*∈{I,TwoStage,FedAvg}；完全相等按冻结名称排序。F*/N*选择一次，不能为最终误差、成本或每seed各换一个有利对手。

以下逐项给实测值、阈值、差距和PASS/FAIL/UNRESOLVED：

1. 主收益 `1-mean_s L_F*(s)/mean_s L_N*(s)≥2%`。
2. 至少2/3个配对seed的L严格更低。
3. 三seed平均最终RMSE_mu相对同一N*恶化≤1%。
4. 三seed平均九点WorstGroupRMSE相对同一N*恶化≤1%。
5. 部署必需CPU总和比≤1.20、wall总和比≤1.25。
6. 方法、源事件、时效、容量和15条/135点评估完整。

主收益不能用平均各seed百分比代替上述比值；原尺度RMSE与标准化训练损失分开。CPU/wall比是三seed对应成本总和之比，不用平均臂耗时或总实验耗时充当。

全部通过才记PASS_EXPLORATORY_TASK_SCREEN。只是已有validation上的小规模探索，不能宣称独立确认、统计显著、完整RAVEN/P2主方法已经成功。

首seed最终误差明显恶化必须保留，不能只展示九点均值或成本好看的部分；三seed若保护线失败，说明缓存支持/成本收益未转化为本协议的可接受预测效果。

## 7. 失败、证据不完整与停止规则

- 只胜I、未胜全局强N*：BUFFER_NOT_COMPETITIVE_WITH_STRONG_BASELINE。
- 主收益不足2%或配对方向不足2/3：FAIL_PRACTICAL_SCREEN。
- 最终RMSE或WorstGroup保护线失败：FAIL_PREDICTION_GUARD。
- 预测通过、已测成本超线：TASK_GAIN_COST_UNRESOLVED，并明确是实测超线。
- 成本关键字段未测，且不能由有效界证明门槛：COST_EVIDENCE_INCOMPLETE；区分于实测超线，不能记整体PASS。
- 仅D改善：同时注明GEOMETRY_GAIN_WITHOUT_TASK_GAIN。
- 源/方法/训练链错误：INVALID_COMPARISON，相关输出不用于科学优劣判断。
- 资源/预算或配对未完整：RESOURCE_BLOCKED，不等于方法无效。

多项条件并列报告。失败后不加seed、改H、换目标、降低2%/1%门槛、调整学习率、补服务器步数、删即时基线或重启S/P2救场。

完成原计划三seed后若效果失败，停止新增训练，用现有预测/日志做描述性原因分析：步数100/50/33的差别、正质量与独特观测保留、时效/驻留、几何失配和最终误差。只能描述关联，不能没有消融就认定某因素是因果原因。不另外立一个机制实验。

## 8. 资源、费用与断点

以最新持久账为准，本次起点训练已用149.0 CPU秒、159.9943418秒wall。剩余额度2251.0 CPU秒、3440.0056582秒wall；不得因为新seed或新进程清零。整个原计划硬上限仍2400 CPU秒、3600秒活动wall，含训练、评分、恢复、失败、重做和执行性分析。

C0/C1的非训练代码检查和冻结参考准备计原实现额度；真实运行中的数据/参考加载成本仍须如实记录在实际运行账，不能重复收费或把必需预处理移出部署成本。当前348.26/374.46秒只是首批外推，不保证新seed同耗时。

一次一个臂、CPU单进程、Torch/BLAS各1线程、DataLoader workers=0。启动前空闲内存≥2.5 GiB；低于2 GiB不开新批，持续30秒保存退出；低于1 GiB或RSS>1.5 GiB尽快退出。峰值与门槛统一bytes/MiB/GiB。不要自动关闭用户应用或使用云资源。

新seed五臂完成后更新剩余费用预测。若现有费用加预测余量超过硬上限，保存并暂停；不得靠减少本地步数、关闭数或评估点完成表格。

失败恢复使用真实完整断点，科学账本不重复消费，资源账保留所有真实尝试。已有恢复证据继续有效，不重领一次恢复预算。

## 9. 必交付文件及审批点

交付：

- REMAINING_READINESS.md、必要代码差异、更新后的EXECUTION_ENTRY.md。
- 两新seed的只读参考表与REFERENCE_PREPARATION_REPORT.md。
- 全部15行RUN_MANIFEST、135点评分及预测/模型索引。
- SEED_COMPARISON.csv、ALL_GATES_DECISION.csv、LIFECYCLE_COUNTS.csv、分类资源账及CUMULATIVE_BUDGET。
- DECISION_REPORT.md和更新后的EXPERIMENT_REPORT.md。

DECISION_REPORT先写整体状态，再逐项展示：全局F*/N*、三seed均值与配对方向、两条预测保护线、CPU/wall及缺失项、原计划是否完整、下一步是停止还是申请独立确认。不得把单项优势写成整体通过。

任何失败写FAILURE_REPORT_<stage>.md：条件、实测值/阈值/差距、首个seed/臂/attempt/关闭、文件/代码定位、已确认与未知原因、累计预算、完整断点、已完成/取消队列、停止/修复可选路线和新增成本；标WAITING_USER_REVIEW。

未经用户审批不实施失败后的补救。全部小试通过也只交付独立确认建议，不自动扩成十seed、不改论文。未获剩余训练授权则明确：首批已完成，剩余10条UNRUN，本次仅完成续行准备。
