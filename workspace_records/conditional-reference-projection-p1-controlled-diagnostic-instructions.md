# 交给执行 AI 的指令：P1 小型共同状态机制传递实验

你在 `C:\Cursor\raven.mcs` 执行条件参考投影路线的 **P1 小型受控诊断**。先读 `ccf-review-report/conditional_reference_projection_p0_20261020_0855/P0_AUDIT_REPORT.md` 和 `P0_EVIDENCE_MATRIX.csv`，以及 `results_conditional_reference_projection/round_v1/` 的冻结协议、五臂源码和原始结果。P0 结论是 `GO_P1_DIAGNOSTIC_DESIGN`，同时 `PAPER_INTEGRATION_BLOCKED`；原三种子筛选仍为 `NO_GO_PREDICTIVE_SCREEN`。本次不修改论文，不覆盖旧结果，不把任何局部诊断写成已证实的长期部署收益。

## 科学问题与身份

核心问题不是“权重有没有不同”。权重不同但不改善预测，仍不能证明主方法值得采用。检验：在**同一时点、同一服务器模型和同一批实际可见的客户端信息**下，P（参考投影）、F（完整 P2）相对同支持 U 和完整 TwoStage 的**一次更新后的固定目标 validation 风险**是否有一致、有量级的增量；同时记录权重、可行性和结构指标，解释风险变化。

P/U/F 的服务器规则采用原方案，Design 事前 on、Gate 仅诊断、局部 Hájek 及 beta 构造与冻结协议一致，cap=.5、ESS_min=3、局部步数=2、局部学习率=.01、服务器 eta=.01。P 不能解 P2 再丢弃；F 保留原 P2。TwoStage 必须用其**原生完整协议**构造本地更新和服务器权重，不能拿 P 的本地更新只换一个服务器权重称为 TwoStage。报告中明确区分：P/U/F 在共同客户端更新上的服务器规则对照；TwoStage 在相同外生窗口与相同起始模型上的完整协议对照。

## 顺序执行与停止条件

**A. 运行前冻结，只读和轻量实现检查。**先检查项目适用指令、P0 提示的来源缺口、验证集标签可见性、事件到达/下载版本、beta 与 F 的债务/方差/陈旧状态。选定一种合法共同状态来源：建议以**一条 F 原协议开发种子轨迹的窗口前状态**作锚，复制其模型、版本和可见事件，再在该窗口做不提交的四臂影子更新。F 锚轨迹继续按自己的方法推进。影子臂各自隔离状态；不能让一臂的局部 SGD、P2 求解或评价改变其余臂或锚轨迹。若 F 状态无法安全复制，或 TwoStage 不能在相同窗口与起始模型下按自身协议运行，记录 `BLOCKED_MATCHED_STATE` 并停止，不用终点 `final.pt` 代替历史窗口前状态。

在读取 validation 标签前，固定 **seed 33001**、100 窗原事件流，并仅按训练事件元数据筛选 `K>=4`、非空且满足冻结可行域的窗口；`K<=3` 的 ESS 退化窗口只计数、不用于主要配对。按时间分为窗口 0–32、33–65、66–99 三段，从每段按窗口号取前三个合格窗口，最多九个。名单与剔除原因写入 `P1_FREEZE.json`；不得用组误差、validation 标签、P/F/TwoStage 得分挑窗口。若总合格数少于六个，记录 `INSUFFICIENT_DECISION_WINDOWS` 并停，不换种子补足。

确认 P/U/F 在同一窗口拿到相同的按客户端 ID 对齐的可见信息、参考 beta 和局部更新；确认每个影子更新的参数副本互不别名。TwoStage 的本地训练可因原协议不同而另算，但必须报告其与 P 的更新输入差异。先只运行一个冻结窗口，检查客户端 ID、向量维度、权重归一、cap/ESS、版本、Design/Gate、服务器步公式、重复评分一致性和影子状态隔离。任一关键检查失败，记录 `FAIL_IMPLEMENTATION` 并停止；不要通过放松冻结约束使其通过。实现可放独立 P1 目录，不改 `src/` 或原15条轨迹。

**B. 有界实验。**前置检查通过后，执行冻结名单其余窗口。每个窗口只允许一份锚状态，四个影子更新分别从该状态复制并在一步后立刻评分，评分完丢弃影子状态。评价同一 validation 组全集和冻结 μ，主指标为

`R_m = sum_g μ_g MSE_g(theta_after_one_step_m)`；同时保存 `R_before`、四组 MSE、`sqrt(R_m)`、WorstGroup、结构错配、`alpha`、beta、客户端 ID、更新向量摘要和 `||theta_m-theta_before||`。在相同窗口计算成对差 `R_P-R_U`、`R_F-R_P`、`R_P-R_TwoStage`、`R_F-R_TwoStage`；负数表示前者一步风险更低。不要把九个窗口当作九个独立数据集或计算无依据的显著性。固定窗口全部报告，不能只挑胜出窗口或改为最有利的评估时点。

资源上限：**单进程、CPU、180 CPU秒、360秒 wall**，包括锚轨迹、影子更新和评分；超过任一项停止并保存已得结果。启动前空闲内存至少 4 GiB；运行中可用内存连续 30 秒低于 2 GiB 时安全停止。资源不满足时记 `RESOURCE_DEFERRED`，不要靠关闭守卫或无限重试完成。若完整锚前缀和九个窗口明显超出上限，先在报告说明，不拆成多次不计账进程。保存 CPU/wall 的实测类别；缺测写 `UNMEASURED`。

**C. 分析与结论。**先对每窗报告 P/U/F 的 L1 权重差和两两服务器步差，再报告同窗预测风险差及符号。权重差、几何差、一步风险差分别解释，不把任一项替代另一项。用首个冻结窗口重复评分估计同一模型状态的数值误差，定义 `epsilon_score=max(重复评分的最大差,1e-7)`，并在其余评分前冻结这个值。`1e-7` 是防止完全确定性重复评分给出零容差的保守数值下限，不代表实用效果门槛。对候选 m=P（主要）、F（次要），分别和 b=U、TwoStage 配对。只有同时满足以下两个**事先固定的诊断门槛**，m 才有局部任务信号：① 在至少 `ceil(0.75*N)` 个预选窗口上有 `R_m < R_b-10*epsilon_score`；② 平均配对收益 `mean(R_b-R_m)` 至少为 `max(10*epsilon_score, 0.10*mean(abs(R_before-R_b)))`。`N` 是冻结后实际合格窗口数，必须至少为六。P 需同时通过 U 和 TwoStage 才记为 `P_SIGNAL`；F 同理记为 `F_SIGNAL`。这只是明确的筛选边界，不是统计显著性或实际部署收益的判据。

只要与 U 的方向有利但相对 TwoStage 不达标，就写“相对同支持消融有局部作用，尚无强基线效用”。若相对 TwoStage 仅出现零星、微小或受数值误差影响的优势，结果是 `P1_NO_TASK_SIGNAL`，不得进入训练扩展。若 P 或 F 过了上述门槛，只得出 `P1_MECHANISM_SIGNAL_ONLY` 并注明是哪一臂过门槛；它是设计以后独立端到端确认的依据，当前 `NO_GO` 不变。若权重几乎相同，或有明显权重差而风险不改善，给出相应的机制失败诊断并停止该分支。不要追加种子、调目标 μ、调 eta、改变约束、改选窗口或继续长期训练。

## 交付

在 `results_conditional_reference_projection/round_v1/p1_controlled_diagnostic_<日期时间>/` 保存 `P1_FREEZE.json`、`WINDOW_PAIR_RESULTS.csv`、`P1_REPORT.md`、`RESOURCE_AND_BUDGET.json`。CSV 一行一个窗口×方法，至少包括种子、窗口、方法身份、锚模型/事件标识、K、输入客户端 ID 摘要、beta/alpha 或其独立可读资产路径、可行性残差、可计算两两差异的更新向量资产路径、`R_before`、`R_after`、四组 MSE、WorstGroup、结构错配和状态。报告先列最终状态与完整成对表，再说明每个失败原因和证据位置。

最终状态只能在 `BLOCKED_MATCHED_STATE`、`INSUFFICIENT_DECISION_WINDOWS`、`FAIL_IMPLEMENTATION`、`RESOURCE_DEFERRED`、`P1_NO_TASK_SIGNAL`、`P1_MECHANISM_SIGNAL_ONLY` 中选择。此 P1 是开发种子上的局部机制诊断；没有独立确认，不向论文新增全面性能主张。若 P1 有信号，提交下一阶段建议即可，**不得自动启动新一轮三种子/五臂训练**。
