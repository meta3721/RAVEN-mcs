# 下一步执行指令：补上真实事件驱动，运行首种子五臂批次

日期：2026-10-19。使用技能：ccf-experiment-designer。模式：design。

这是 `results_zero_safe_buffer/round_v1/backend_pilot/EXPERIMENT_REPORT.md` 后的续行指令。请完成实际驱动代码和下述授权范围内的执行，不再以重写方案、函数绑定表或重复静态测试替代推进。

## 1. 起点和本轮目标

项目根目录：`C:/Cursor/raven.mcs`。

已完成且可以复用：

- 零质量隔离的元数据回放及普通缓存几何机会核验。
- 原训练/聚合函数的对象绑定、服务器代数与评分公式检查。
- 零覆盖计数器修正、非训练断点往返。
- validation四组样本支持检查：1242、331、108、408。

当前 `BACKEND_STATIC_READY` 表示这些静态检查通过；真实模型、客户端训练、事件执行和恢复重放均未运行。`FiveArmBackend.resolve()` 中保存函数对象，不等于已实现一个可以跑完100关闭的实验驱动。

下一步只有两个任务：

1. 补齐可执行事件循环，把已绑定函数用于真实数据、真实模型和评分。
2. 获准后运行33001的五臂完整批次，验证真实训练和恢复，并估计剩余费用；条件满足再继续原定33002、33003。

不重复整批Z1，不重跑已通过的静态检查，不追加另一套短训练预实验，不改变原方法或门槛。

## 2. 授权范围

本文件首先是执行方案。用户仅要求“写出执行指令”不构成恢复训练授权，原“暂不训练”仍有效。

- 未获明确训练授权：完成第4节驱动实现、无训练的入口/参数检查，交付真实可用的启动命令，停止在首次神经训练之前。
- 用户后续明确授权执行本文件的五臂训练：从第5节开始连续推进，通过的阶段无需重复询问；失败或资源不足则暂停并报告。
- 不允许自行把配置中的 `training_authorized` 改成true，然后把此值当成人类授权证据。

本次不修改论文、不跑测试集筛选、不加seed、不增加候选、不启用S/P2/OF或主动采样。

## 3. 必读文件与输出

读取 `results_zero_safe_buffer/round_v1/backend_pilot/` 中：

- `EXPERIMENT_REPORT.md`、`TRAINING_READY_REQUEST.md`、`BACKEND_ADAPTER_MAP.md`、`BASELINE_INPUT_MAP.md`。
- `STATIC_CHECK_RESULTS.json`、`CHECKPOINT_IMPLEMENTATION_MAP.md`、`RESOURCE_LEDGER.jsonl`。
- `five_arm_backend.py`、`update_semantics.py`、`checkpoint_store.py`。

同时读取上级 `PROTOCOL_FREEZE.json`、`projection.py`、`zero_safe_scheduler.py`，原Stage-1回放、事件协议、CommonNDMF、ClientTrainer及原完整WindowRunner。以此前两份零质量隔离实验指令的冻结方法和科学门槛为准；本文件不重定义科学问题。

驱动代码建议新增为 `backend_pilot/run_pilot.py`，运行结果存入 `backend_pilot/training_run_v1/`。已有不同内容时另建目录并给入口索引，不覆盖静态报告、资源失败记录或旧实验。

## 4. E0：实现真正可执行的驱动

### 4.1 入口和计划模式

提供一个真实命令行入口，支持：仅显示计划、首seed五臂、续行剩余seed、从完整断点恢复。默认不得启动训练。

仅显示计划时：输出固定的15条队列、数据路径、模型/特征/尺度来源、方法配置、已用及剩余预算，不构造训练批次、不调用train_step。训练入口必须实际进入下列事件循环，不能只调用resolve或静态检查后退出。

在 `EXECUTION_ENTRY.md` 写出本机解释器路径、工作目录和可直接运行的精确命令，不交付含TBD的启动指令。Python解释器优先复用此前成功检查的环境，不安装新环境来改变软件依赖。

### 4.2 数据、模型与本地更新

每个seed仅依次保留一个臂的模型与必要缓存。沿用CommonNDMF、原空间索引/时间特征、train均值和标准差；评分预测还原到原任务单位。不得使用另一份时间归一化或validation尺度。

五臂从同seed同初始权重开始，分别维护自己的服务器版本和注册快照。本地学习率0.01、本地2步、服务器学习率0.01。实际本地更新调用原 `ClientTrainer.train_step`，不创建替代的小模型或简化损失。

原更新语义已经确认：

`u_i = (theta_registration - theta_local_i)/(0.01 * 2)`

`theta_new = theta_current - 0.01 * sum_i alpha_i*u_i`。

注意服务器起点是释放时当前模型，本地起点是注册快照；二者不能混用。扁平化与还原必须沿原参数排序、形状和dtype，不能错位或重复除以本地学习率。

I/F使用已冻结的观测内均匀本地权重；TwoStage使用原Stage-1 Hájek本地权重；FedAvg使用原观测内均匀权重。本轮不自行升级这些本地规则。

dropout等外生随机数使用已登记的seed+attempt ID规则，并真正设置Torch随机流；只生成一个整数而不用于训练不算完成。每次评分使用eval模式，之后恢复训练模式；评分不能扰动未来尝试的训练随机流。

### 4.3 真正的注册—交付—关闭循环

对每个臂维护模型、版本、概率历史、事件游标、注册快照、in-flight、pending和终态。

1. 注册：按固定事件顺序，捕获本臂当时模型快照及应在结果发生前冻结的参考/概率输入；合法观测和外生时延来自原事件资产。
2. 本地计算：用该尝试的注册快照和合法观测计算真实两步更新。即使为节省内存延后物理计算，也必须保证模型、特征、随机数和结果前信息与注册语义一致，不能读取后来模型或标签。
3. 交付：按固定到达顺序处理真实更新；执行本臂版本资格检查。I/F的零质量隔离、latest-positive替换、容量规则保持冻结。
4. 关闭：I立即消费；F1/F2按冻结年龄规则释放整池。HOLD不改变模型、优化器或版本；非空真实聚合才推进版本。结束只到关闭99，不能额外清池补步。
5. 完成20、30、…、100关闭时，保存实际模型并对固定validation评分。不得用误差改变调度。

冻结H=2、S_max=5、有效池容量64。I/F服务器使用真实二次参考投影，beta由释放集合内正质量m归一；小K时使用既有alpha_bar/ess_ball_bound的可行域。最小TV解仅作诊断，不替代投影。

同一客户端的正质量不同观测仍可能被替换，这是本轮冻结选择；不临时合并、不重复计入ESS。保留丢弃原因、观测ID和实际使用权重。

### 4.4 完整基线接线与冷启动

FedAvg的raw_counts、TwoStage的局部修正、d_weight、two_stage_mass、beta_hat必须由真实事件计算，不能继续用人工向量代替。

按已登记的原完整方法资格执行外部基线，不能将I/F缓存、cap/ESS或零质量过滤额外套给它们；原方法本来具有的B_r、U资格保留并说明m在该方法内的来源。

TwoStage实例化原ObservationPropensity、UsablePropensity，并实际执行结果前预测和结果后历史更新。原UsablePropensity在不足5个历史样本时返回0.5是原类的冷启动，可以保留；“全程硬填0.5”及“仅绑定类但不维护历史”不允许。记录冷启动覆盖率与历史更新时间。

保持共同源尝试和U输入，不通过原WindowRunner重新抽一次参与/到达来改变比较对象。若概率历史需要原未交付/失败尝试的记录，从原训练历史资产读取并按当时可得顺序更新，不能只拿U=1当全体成功标签；若必要输入缺失，记BASELINE_NOT_READY并暂停，不静默更改估计总体。

### 4.5 恢复状态必须来自运行中的真实对象

复用已有checkpoint_store，但由驱动收集真实模型张量、实际快照、队列、手动SGD配置/步数、概率估计器及其历史、Python/NumPy/Torch RNG、数据游标、账本、评估进度和预算。

手动SGD没有动量，因此momentum_buffer=null合理；不强制换成torch.optim。概率估计器状态与Torch RNG不能继续填null。快照可引用共享的不可变版本以省内存，但恢复后必须解析到完全相同参数，不能只保留版本号。

每个完成的关闭保存可恢复边界，保存前先确认内存。使用临时文件完成写入后再替换目标断点，避免覆盖唯一有效状态；失败保留上个完整断点。原有pickle往返只能证明容器可序列化，不能替代第5节恢复重放。

### E0通过与失败

通过条件：完整事件循环和真实输入路径已经写出；训练入口、评分、恢复函数均实际被调用链引用；无训练的计划命令可用，交付具体文件/函数和运行命令。记EVENT_DRIVER_IMPLEMENTED_UNRUN。

无训练授权时止于此，并明确真实更新与预测仍UNRUN，不再要求额外一轮“是否允许写代码”的审批。

输入/方法缺失记BASELINE_NOT_READY或BLOCKED_METHOD_IDENTITY；驱动仍仅返回绑定表记EVENT_DRIVER_INCOMPLETE。失败写报告，暂停依赖任务。

## 5. E1：获准后运行33001首个完整五臂批次

顺序固定：I-Proj-ZS → F1-Proj-ZS → F2-Proj-ZS → TwoStage-Hájek → FedAvg-Window。每臂100关闭、9点评分。这5条属于总15条，不另加一批短训练，也不因早期误差大而换seed。

### 5.1 在真实轨迹中验证关键路径

- 每臂首个有效更新，保存注册快照来源、观测ID、两步本地损失、返回更新范数、真实权重及服务器前后状态。用同一实际更新核对服务器公式，浮点最大差≤1e-6。不能仅以“参数变化了”判断正确。
- I/F每次投影约束违反≤1e-6；beta/alpha和实际组失配有记录。HOLD确实不改变模型/版本/步数。
- TwoStage首个实际窗口具有合法历史输入、局部损失及beta_hat；FedAvg计数来自真实观测。全程冷启动不能靠单个示例掩盖。
- 单次聚合不重复客户端，不重复消费消息；时效、容量和源事件边界满足冻结协议。

### 5.2 一次真实恢复核验

在首个F1或F2具有非空缓存的安全关闭边界保存断点，覆盖存在的在途状态。在同一运行中继续2个关闭，保存其动作、提交ID、模型/权重、随机及概率历史状态；再从断点加载重放这2个关闭。

要求离散动作/ID一致，模型、权重、历史数值和随后评分最大差≤1e-6。若所选边界之后的下一既定评分点较远，可在重放终点做一次专用于恢复的一致性评分，单列费用，不加入九点主指标。

重放分支的实际成本全部计入硬预算；科学账本只接受一条规范执行路径。预算账不能随断点回退。完成后继续同一条100关闭轨迹，不重新跑整个seed。

实现、数值或恢复检查失败立即暂停剩余臂，记TRAINING_BACKEND_INVALID或CHECKPOINT_RESTORE_FAILED；不当天自动修改后无限重跑。保存所有已执行范围和已消耗预算。

真实路径全部核验通过记TRAINING_VERIFIED；只有首seed完整五臂完成才记FIRST_BATCH_COMPLETE。两者都不等于方法有预测收益。

### 5.3 首批报告与预算判断

输出首seed五臂全部9点结果、各组误差、实际训练步数、观测损失、队列驻留和成本。首seed不做最终科学成败判断，也不据此选择F1/F2或删除较差臂。

用实测五臂分项费用估计剩余10条、评分和报告费用，并加20%余量。预测超过剩余预算，立即RESOURCE_BLOCKED并保存；不能缩水100关闭、本地步数或完整基线。

若真实核验、首批完成、预算预测三项均通过，且原训练授权覆盖整批15条，直接进入E2，无需再请求一次许可。

## 6. E2：完成原定其余10条，按原门槛决策

依次运行33002五臂、33003五臂。保留全部15条和135个检查点，未完成项写UNRUN或RESOURCE_BLOCKED，不能填估计值。

主指标：

`RMSE_mu(m,s,r) = sqrt(sum_g mu_g * mean_val_g((prediction-y)^2))`

`L_m(s) = mean_{r in {20,30,...,100}} RMSE_mu(m,s,r)`。

从三seed平均L选择全局F*∈{F1,F2}、全局N*∈{I,TwoStage,FedAvg}；完全相等按冻结名称顺序。禁止逐seed选赢家拼接。

必须同时满足：

1. `1 - mean_s L_F*(s)/mean_s L_N*(s) >= 2%`，且至少2/3seed配对L更低。
2. 三seed平均最终RMSE_mu、三seed平均九点WorstGroupRMSE，相对N*恶化均≤1%。WorstGroup先每点取组最大RMSE，再平均检查点/seed。
3. 部署必需路径CPU总和比≤1.20，活动wall总和比≤1.25，均对同一个N*比较。
4. 五臂三seed完整、实际方法身份和共同源事件有效，H=2、S_max=5、容量、单次消费等约束满足。

全部通过记PASS_EXPLORATORY_TASK_SCREEN；它仍是既有validation上的探索筛选，不是独立确认，不宣称显著或已证明完整RAVEN/P2实用价值。

只赢I而不赢强N*，记BUFFER_NOT_COMPETITIVE_WITH_STRONG_BASELINE；不足2%或方向不足记FAIL_PRACTICAL_SCREEN；保护线失败记FAIL_PREDICTION_GUARD；预测通过但成本超线记TASK_GAIN_COST_UNRESOLVED。只有D改善注明GEOMETRY_GAIN_WITHOUT_TASK_GAIN。无效实现记INVALID_COMPARISON，资源中断记RESOURCE_BLOCKED。多项失败全部报告。

## 7. 资源和计时：沿用预算，不重新领额度

现有B0–B1累计约3.203 CPU秒、35.26秒wall。继续E0的非训练可执行检查沿原600 CPU秒、1200秒活动wall总额度扣减；不把成功进程和阶段累计值重复相加。

E1–E2仍共用原2400 CPU秒、3600秒活动wall硬上限，包含真实训练、恢复重放、评分、失败尝试及执行性报告计算。当前报告中的训练额度尚未使用，但启动前核对是否已有后续运行，不凭旧报告清零。

监控先于重库和训练；root及子进程计入。一次一个臂，CPU单进程，Torch/BLAS各1线程，DataLoader workers=0。启动新臂或重库前可用内存≥2.5 GiB；低于2 GiB不开新批，持续30秒保存退出；低于1 GiB或进程RSS>1.5 GiB尽快保存退出。保存不成功则恢复上个完整关闭边界，重做费用不删除。不自动关用户程序，不自动用云，不无限重试。

各臂独立记录起止和分类计时：实际数据/概率处理、本地训练、快照管理、调度/聚合是部署必需路径；额外评估、事后D诊断、恢复核验单列，全部仍计入硬总账。不能把阶段累计CPU读数当单臂耗时，也不能事后任意扣除费用。

实际执行CPU、原源事件的raw_workload、模拟交付/等待分开记录：不能把模拟工作量当实测CPU，不能将已发生但未消费的计算从账本删除。未知通信字节保持null；不能将未知写0。没有必要为模拟延迟实际sleep。

## 8. 每阶段输出、失败报告与终点

E0：`EXECUTION_ENTRY.md`、`EVENT_DRIVER_IMPLEMENTATION.md`、本轮diff；未获授权写TRAINING_NOT_AUTHORIZED，训练仍UNRUN。

E1：`FIRST_BATCH_REPORT.md`、`REAL_UPDATE_CHECKS.json`、`RESTORE_CHECK.json`、`COST_PROJECTION.md`及首seed五臂模型/预测/日志。

E2：完整 `RUN_MANIFEST.csv`、`CHECKPOINT_METRICS.csv`、`SEED_COMPARISON.csv`、`LIFECYCLE_COUNTS.csv`、`RESOURCE_LEDGER.jsonl`、可恢复断点、`DECISION_REPORT.md`和 `EXPERIMENT_REPORT.md`。

机制表至少分别报告committed、实际alpha>0使用、正质量替换/溢出/过期/终点未消费、独特观测损失、全交付正质量驻留mean/p95、释放次数和实际投影失配；独特ID按seed和方法去重。可以引用既有零隔离回放，不冒充新增零隔离预测消融。

失败立即写 `FAILURE_REPORT_<E0/E1/E2>.md`，包含：

- 全部失败条件、实测值/阈值/差距；UNRUN明确写出。
- 首个seed、臂、attempt、关闭及具体文件/函数。
- 已证实原因与尚未知解释，区分代码、协议、科学效果和资源问题。
- 已完成范围、取消队列、累计费用、完整断点及恢复能力。
- 可选择的终止/修复路线和新增成本估计，但不擅自实施。
- 状态WAITING_USER_REVIEW。

任一失败后不追加seed、换目标、调H、删基线或叠加新机制。小试全部通过也只提交独立确认建议，不自动启动大规模实验或改论文。

交付时先回答：现在是否有真实模型训练？首批是否完整？恢复是否验证？能否在余量内完成15条？预测是否胜过强基线？不要再用“函数对象相同”回答这五个问题。
