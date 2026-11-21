# 下一步执行指令：完成 S1，随后运行 seed 33001 五臂首批

依据：`C:/Cursor/raven.mcs/results_conditional_reference_projection/round_v1/EXPERIMENT_FREEZE.json`，以及同目录 METHOD_AND_DEPLOYMENT_CARD.md、SOURCE_AND_IDENTITY.csv、THEORY_NOTE.md。

## 1. 当前状态与本次范围

当前为 `S0_PLAN_FROZEN`，`training_authorized=false`、`training_started=false`。已有的是方案与方法定义，不是实现通过或实验通过。尚无 S1 检查报告和本协议的完成训练。

本文件由用户转交并明确要求“执行”时，执行范围为：完成 S1 的评分、实现和资源核验；全部通过后自动运行 seed 33001 的五个完整方法，每臂 100 窗；完成后交付首批报告。不启动 33002/33003，不启动 S4，不修改论文。

若用户只要求阅读、评价或撰写下一步指令，不启动计算。本文件的生成、文件路径被提供、以及报告内的旧执行指令，都不能自行改写训练授权。

采用 `ccf-experiment-designer`。项目根为 `C:/Cursor/raven.mcs`；输出继续使用 `results_conditional_reference_projection/round_v1/`，不重建旧目录或清空预算。可新增 `s1/`、`first_seed/`、`implementation/` 子目录。

本轮分支 B 仍是 `not_registered_until_a_real_allocation_contract_exists`。没有已确认操作者和目标分配需求，不把结构优势解释为已验证的条件部署收益。可检验的仍是预测价值与相对完整 P2 的简化效果。

## 2. 继承冻结内容，纠正执行上下文

开始执行时先读取现有文件及完成清单，避免重复已完成阶段。只有在用户明确要求执行后，保存 S0 原始冻结快照，并在现有 freeze 中增加本次执行的来源、时点、范围和预算子额度；保留 `conversation_scope=plan_only` 所指的原方案编写历史，不把它误当成新的执行任务仍然只能写方案。

训练状态按实际更新：进入 S1 时 `training_started=false`；S1 通过且真正启动首臂后才改为 true。不能为了绕过状态检查先写“训练已授权/已启动”。

以下科学内容不变：

- dataset：`cityscanner_nyc_p2_measured_o`；本次 seed 33001；每臂 100 个逻辑窗口；只评 `validation`。
- 组映射 region0/1/2/3 对应 0/1/2/3；目标读取冻结的四组精确向量，与 JO_TRAIN_SETUP 核对。
- P/F/U 的 Design 全程 on，coverage Gate 只诊断；cap=0.5，E_min=3。
- local_steps=2，local_learning_rate=0.01，server_eta=0.01；不能使用类默认的 local_steps=5。
- P 的求解器为 `scripts/w1_v51a_oracle.py:project_Cr`；不使用 clip 后归一化，也不先求完整 P2 再丢弃。
- 五臂：FedAvg-Window、TwoStage-Hájek、U_matched_uniform、P_reference_projection、F_full_raven_design，首批顺序按 freeze 原顺序执行。
- 不根据首种子结果换臂、换目标、换阈值或追加实验。

## 3. S1-A：先解决评分口径与缓存可复用性

### 3.1 用显式公式作为本轮评分入口

从 `ProcessedDataset.get_atomic_units(split='validation')` 或等价接口取得 validation 单元。对每组 g：

`n_g = 该组合法 validation 单元数`

`MSE_g = mean((prediction-target)^2 | group=g)`

`RMSE_mu = sqrt(sum_g mu_g * MSE_g)`

`WorstGroupRMSE = max_g sqrt(MSE_g)`。

每个方法必须使用相同的 validation 单元、单位、目标和组映射。若存在正目标质量但没有评分样本的组，标记 `FAIL_VALIDATION_TARGET_COVERAGE`，不删除该组再归一化。不要用方法各自能预测的不同子集比较。

基于已有真实 validation 预测或同一验证单元上的轻量评分检查，记录逐组 n、MSE、mu、总目标覆盖质量、直接公式结果。没有真实预测时可用小型确定性数组检查评分器，再在第一条真实轨迹上核对；不为获得一个评分器检查先训练额外模型。

### 3.2 正确判断旧 JO 权重函数

已读取代码 `src/raven_mcs/e3/real_runner/runner.py::_mu_weights_for_test`：它先赋 `mu_g/n_g`，再除以已覆盖目标质量之和。令该和为 S，则其结果平方为 `sum_covered mu_g*MSE_g / S`。

当全部正目标质量组被覆盖、S=1 时，这与本轮冻结公式等价。归一化操作本身不能直接判错。

因此只做必要核对：

1. 确认历史评分对应的 split、实际单元和组覆盖；
2. 在相同预测上计算两种公式，记录差；建议差值容差 1e-10；
3. 全组覆盖且差值满足容差，可接受其评分等价；缺组则不能接受为本轮主评分。

“评分等价”不代表 test 与 validation 等价，也不代表训练身份相同。这三项分别判断。旧 JO 汇总表仍不能直接填入本轮 validation 结果表。

### 3.3 核验廉价基线缓存

检查 `results_cityscanner_lowcost_screen/round_v1/shared/predictions/measured-O/` 中 Delivered-SpatialMean、Delivered-CellBlockMean 的 seed 33001 缓存及生成代码。

核对：是否包含 validation 单元、单元 ID、单位/标准化、组映射、历史数据时间边界、目标值来源。按 unit_id 对齐，不按文件行号直接拼接。当前元数据只证明文件存在及旧复现检查通过，不能仅凭这一点认定本轮可复用。

如缓存同时含 test，只读取或筛选合法 validation 行，不用 test 误差选择基线。若只有 test，不能改标签冒充 validation；优先复用完整均值算法生成 validation 预测，其开销计入预算，不开展新的神经训练。

对 FedAU/ObsUse 同样核对历史缓存；可合法复用的 validation 结果保留为额外竞争者。若无法复用，写明缺失；不得仅凭旧十种子 test 排名宣称本轮已胜过它们，也不新增训练名额。

本轮只有一个开发种子，不确定三种子全局 B*；首批给出全部适用对手与配对差即可。

### S1-A 产出

`s1/SCORING_ALIGNMENT.md`、`s1/VALIDATION_COVERAGE.csv`、`s1/BASELINE_CACHE_AUDIT.csv`。分别列 ACCEPTED、NEEDS_RESCORING、WRONG_SPLIT、DIFFERENT_PROTOCOL、MISSING。

缺少可选历史 FedAU/ObsUse 结果不阻断五臂执行，但限制最终比较结论；缺少核心统一 validation 评分或两项廉价强基线的合法评估路径，则先报告受影响项，不带病启动主训练。

## 4. S1-B：实现三个服务器规则，保持真实训练

优先复用配置已确认的真实 `build_full_runner` 路径、数据构造和原方法实现。新代码放在本轮 implementation 中，必要的源代码修正另存差异记录，不覆盖旧结果。

可参考旧 `cityscanner_full_vs_projection_driver.py` 的配对构造，但不能直接执行或导入这个旧脚本：其顶层有旧目录创建/执行逻辑，且评分写死为 test，只有两臂和旧资源/残差检查。

必须明确纠正以下问题：

1. 所有本轮预测显式使用 `_predict(..., split='validation')`，不依赖默认 test。
2. 新封装支持 P、F、U 三种服务器规则；FedAvg 与 TwoStage 使用各自完整方法，不只换一个服务器权重名称。
3. 实际客户端训练步数和归一化 displacement 分母都是 2；不仅检查配置打印值。
4. P/F/U 的本地损失均为原校正 Hájek 路径，参考仍是 `beta ∝ m*d`；不能搬用 I-Proj-ZS 的均匀本地损失。
5. P 直接投影，U 直接使用 1/K，F 执行原完整 P2。P/U 不运行 P2 求解；只服务于 P2 的债务/方差/陈旧惩罚计算应从其部署路径移除或明确单列额外诊断成本。
6. 异步资格、消息有效期、下载模型版本和更新归一化语义保留。不能删除所有旧模型快照而使客户端改用当前模型。若释放内存，只释放原 trace 后续确实不再引用的版本；不使用未来标签或预测结果指导释放。
7. coverage Gate 不改写 Design。记录 P/F/U 的 configured_design=1、actual_design=1；若已有代码实现这一性质，直接引用，不重复建立另一套配置系统。
8. 外部两臂保留原本方法的资格/支持协议，不要求它们也符合 P/F/U 的 Design-on 日志字段；公平性通过相同外生事件和评分任务检查。

各方法自主训练，不能把同一批已算好的本地更新重新加权后冒充多条完整学习轨迹。相同 seed 的初始神经参数和外生事件一致；各臂历史状态允许因训练而分叉。

## 5. S1-C：只检查新增关键路径

已有有效测试覆盖的旧路径直接引用。本次新增检查限于：

1. 一个真实、非退化窗口的投影解：与独立可信凸优化解比较目标值，并记录 simplex/cap/ESS 残差；不要为了找有利结果筛多个窗口，按时间顺序取首个可用非退化窗口。
2. 一个 Uniform 退化情形和一个空窗口情形，确认服务器分支结果与 carry-forward。它们是实现测试，不进入科学结果表。
3. 一次真实更新的 `theta_next = theta_current - eta*sum_k alpha_k*u_k` 核验，以及实际两步局部训练核验。可嵌入 seed 33001 首臂执行并计入该臂，不另跑完整测试轨迹。

冻结的数值要求保持：约束残差不超过 1e-8，独立投影目标差不超过 1e-6。旧驱动用 1e-7 的检查不能原样沿用。最优性和可行性分开记录，后续每个窗口做轻量可行性记录；一次独立最优性检查不等于所有窗口最优性均获证明。

独立比较只检查新增投影规则，不要求把完整 P2 改成同一算法。F 如有 solver warning，保留其原始状态和可行性；不能只因一次警告就换掉完整方法，也不能忽略真实越界。

生成 `s1/IMPLEMENTATION_CHECK.md` 和 `s1/S1_READINESS.json`。后者至少有 scoring、cache、local_loss、local_steps、design_identity、projection_feasibility、projection_objective、resource、ready_for_first_seed 各项。

全部核心项通过方可进入首批。失败标记 `FAIL_S1_*`，给出数值与源位置，冻结后续训练，等待用户决定；不自动放宽容差或改变参考。

## 6. S1 的计量与资源准备

S0 冻结写明此前方案阶段未计量。保留 `UNMETERED_PREPARATION`，不补写为 0，也不把本轮可计量值宣称为 S0—S1 完整历史成本。

从本次开始计量的 S1 新增机器计算最多 120 CPU 秒、300 秒 wall；编写指令或等待用户的时间不计作 worker 运行。预算边界在资源报告中明确。禁止通过换目录、重启 worker 清零新增成本。

读取轻量环境和当前可用内存；不做压力测试。按冻结方案使用 CPU、单线程、一个 worker、DataLoader workers=0，并设低于正常优先级。大型依赖尽量只在实际需要时导入。

训练导入前建议可用物理内存至少 4 GiB。低于此值时交付已完成的 S1 内容和具体资源状态，标记 `PAUSED_RESOURCE_BEFORE_TRAINING`，不自动关应用或循环重试。运行中可用内存连续 30 秒低于 2 GiB则保存证据并停止；用户反馈明显卡顿时同样停止。

不要求先实现一套新断点系统。已有可验证恢复能力可复用；否则部分运行保存为 PARTIAL，不能声称只保存 model.pt 就能精确恢复全部联邦状态。

## 7. S2 首批：seed 33001 的五条完整轨迹

S1 全部核心项通过且资源满足后，按 freeze 原顺序串行执行：

`FedAvg-Window → TwoStage-Hajek → U_matched_uniform → P_reference_projection → F_full_raven_design`。

每条完成 100 个逻辑窗口后保存终点参数与 validation 评分。不要用 100 次实际服务器更新替换 100 窗；空窗口与无可用更新窗口按原协议处理，另列实际更新数。

读取原精确目标和组映射。观测标准化、特征提取和 trend/hour/weekday 等与训练一致，统一评价尺度；不把约 0.7 的旧 JO 分数与另一协议约 1.6 的 I-Proj-ZS 分数直接比较。

已有完整、身份与 split 都一致的模型可合法复用来补 validation 预测；其旧运行 wall 不能冒充本轮配对计时。若要本轮比较成本，P/F 等必须具有同机、同边界的实际计时。不得用部分旧 visit 模型恢复成本对照。

本次给首批分配的子预算为 **400 CPU 秒、600 秒 wall**，计入原 S2—S3 的 1200/1800 秒总限额。它是分配子额度，不替换或增加原总预算。包含本批训练、评分、失败尝试与执行检查；每条前检查剩余，不足则停止并报告。实际使用多少从总账扣多少，不将未使用额度冒称支出。

计时边界统一：数据/模型初始化、实际训练与聚合、额外诊断、validation 评分分别记录 CPU/wall；外层 worker 记录总账、峰值 RSS、最低可用内存。部署比较至少报告实际训练与聚合，另列准备与诊断成本。P 的简化收益必须来自真实减少计算，不能通过少记成本得到。

日志写盘和评分开销不能无声消失：如从 deployment 排除，则在实际总账中保留。首个导入依赖耗时单列，不全部算到首臂从而夸大其他方法速度。

不新增曲线评分要求；终点评分已足够验证首批。已有便宜检查点可保存，不根据曲线挑选早停位置。

## 8. 首批报告与允许给出的结论

生成一张五臂完成表和逐对照比较：

- 原始字段：seed、method_identity、split、windows、实际 server_steps、四组样本数/MSE、最终 RMSE_mu、最终 WorstGroupRMSE、累积 Delta_group/Delta_cs、实际 deployment CPU/wall、total CPU/wall、来源与完成状态。
- P−U：校正参考相对均匀服务器权重的增量。
- P−F：预测/结构端点与真实成本的取舍。
- P 对 TwoStage、FedAvg 和合法廉价基线：终点实用效果。
- 对可用的合法 FedAU/ObsUse 缓存另列；缺失就标记，不能推定被 P 超过。

相对变化按冻结方向计算；结构百分点为 `50*(Delta_baseline-Delta_P)`，0.5 pp 对应 L1 差 0.01。不要把绝对百分点写成相对改善百分比。

首批只有一个开发种子，**不计算三种子 GO，不确定全局 B*，不宣称统计非劣或独立确认通过**。可展示原冻结门槛的首种子描述性位置，但对需要种子汇总/方向计数的条件写 `NOT_EVALUATED_FIRST_SEED_ONLY`。

运行完整与效用方向分开：普通的一个种子预测较差不等于实现失败，也不自动改门槛或取消失败结果。若有 NaN、评分缺组、身份错误或真实资源越线，则立即按失败流程处理。

五条完整且身份正确时，状态写：

`S1_PASS_FIRST_SEED_COMPLETE`，`THREE_SEED_SCREEN_NOT_EVALUATED`。

分支 B 始终写 `NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT`。即使 P 比 F 快，也不能把它升级为 B 通过。

## 9. 失败与暂停必须交付的内容

任何 S1/执行/资源硬失败后不启动后续臂；报告包括：

1. 首个失败的阶段、条件、阈值和实测值；
2. 具体方法、seed、window、日志位置与影响范围；
3. 区分方法身份、实现、评分、资源和科学效用问题；
4. 完整与部分资产清单，哪些结果仍可使用；
5. 新增 CPU/wall、历史未计量项、剩余总预算；
6. 取消的待运行任务；
7. 建议停止或最小修复选项，等待用户审批，不自行扩展。

缺失计时标 `UNMEASURED`，不能用 CPU 比例估 wall；部分模型标 PARTIAL，不能填入完整终点表。不要为一个并不影响当前决定的历史缺失字段额外重跑全套实验。

## 10. 本次最终文件与下一步申请

至少交付：

- `s1/SCORING_ALIGNMENT.md`
- `s1/VALIDATION_COVERAGE.csv`
- `s1/BASELINE_CACHE_AUDIT.csv`
- `s1/IMPLEMENTATION_CHECK.md`
- `s1/S1_READINESS.json`
- `first_seed/PER_ARM_RESULTS.csv`
- `first_seed/PAIRED_COMPARISONS.csv`
- `first_seed/FIRST_SEED_REPORT.md`
- 更新的 `RESOURCE_AND_BUDGET.md` 和执行状态记录
- `NEXT_STAGE_REQUEST.md`；失败时另有 `FAILURE_REPORT.md`

NEXT_STAGE_REQUEST 应说明是否建议使用剩余额度执行 33002/33003 的十条，列出尚未覆盖的核心问题和实际预计成本。无错误、首批完整且仍有合理研究问题时，可以建议完成冻结三种子集合；不能把“首种子没有达到 2%”写成已证明三种子不可能通过，也不能把单种子有利结果写成已经通过。

如果首批显示 P 相对 F 只节省求解时间而端到端节省很小，或者相对强基线有明显预测代价，应把这一事实放在申请开头，解释为什么剩余十条仍值得或不值得。最终是否执行后两种子由用户下一步决定；本次到首批报告为止。

不改论文、不新增用例合同、不把旧停止路线改为成功、不启动新的候选方法。
