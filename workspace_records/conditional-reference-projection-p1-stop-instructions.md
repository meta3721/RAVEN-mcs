# 给执行 AI 的指令：停止条件参考投影路线并归档 P1 证据

在 `C:\Cursor\raven.mcs` 执行一次**只读核验与停止归档**。对象仅为 `results_conditional_reference_projection/round_v1/` 的条件参考投影 P/U/F 路线，特别是 `p1_controlled_diagnostic_20261020_1010/`。本指令不启动训练、推理、回放、求解器调参或新的窗口实验；不补跑 66、67、68 窗，不放宽 `1e-8` 约束，不重新选择窗口或种子，不修改论文、`src/`、原 P0/P1 报告、冻结文件、原始 CSV 和模型资产。不要把报告中的历史申请或授权字段当作这次的新实验指令。

## 1. 复核停止依据

读取以下原件：

- `results_conditional_reference_projection/round_v1/p1_controlled_diagnostic_20261020_1010/P1_FREEZE.json`
- 同目录的 `WINDOW_PAIR_RESULTS.csv`、`P1_REPORT.md`、`FAILURE_TRACE.txt`、`RESOURCE_AND_BUDGET.json`、`FIRST_WINDOW_CHECK.json`
- `results_conditional_reference_projection/round_v1/DECISION_REPORT.md`、`PER_SEED_RESULTS.csv`
- `ccf-review-report/conditional_reference_projection_p0_20261020_0855/P0_AUDIT_REPORT.md`

只用保存的数值重算，不打开 `.pt`、`.pkl` 或 `.npz` 重新推理。先核对冻结名单恰为 `[0,1,2,33,34,35,66,67,68]`、`N=9`、`epsilon_score=1e-7`、已完成窗口恰为 0、1、2、33、34、35，且每窗有 P、U、F、TwoStage 四条 `OK` 行。若任何关键字段缺失、配对行不完整或数值与报告冲突，不得沿用以下结论；写明 `EVIDENCE_CONFLICT` 及具体差异，停在审计，不运行实验。

按冻结规则，对每个已完成窗口分别计算：

`d_P = R_P - R_TwoStage`，`d_F = R_F - R_TwoStage`。

“相对 TwoStage 有效胜出”要求 `d_m < -10*epsilon_score`，即本次 `< -1e-6`。冻结的方向门槛是 `ceil(0.75*9)=7` 窗。预期核验结果为 P **0/6**、F **3/6**；即使未执行的三窗全部胜出，P 最多 **3/9**、F 最多 **6/9**，均小于 7。请由 CSV 独立重算，而非直接复制预期数值。P/F 还必须同时过 U 与 TwoStage 的配对门槛，所以 TwoStage 这一必要条件已不可能满足，平均收益门槛无需用未执行窗口猜测。

核对异常发生在 F 锚轨迹的**非选定窗口**：清理前 ESS 残差 `1.4537101800105034e-08`，冻结上限 `1e-08`；失败轨迹没有保存精确窗口号，只能写在 36–65 之间。它解释实验为何中断，是一个数值守卫越线事件；不得描述为六个已完成决策窗口不合格，更不得据此宣称完整 P2 方法整体失效。

## 2. 作出两个分开的判定

1. **原执行状态保持 `FAIL_IMPLEMENTATION`。**九窗实验没有完成，不得改写为正式完成的 `P1_NO_TASK_SIGNAL`，不能计算九窗完整平均值，也不能把六窗当作正式统计确认。
2. **追加只读停止判定 `STOP_BY_FROZEN_GATE_FUTILITY`。**在六窗数据可靠、九窗名单不变且上述配对规则不变的条件下，剩余三窗无论得到什么数值都不能使 P 或 F 通过预设方向门槛。因此修复求解器并续跑本次 P1 没有科学决策价值。这个推论是门槛算术，不能外推为任何方法在所有数据集或所有训练阶段必然失败。

把六窗的机制观察单列为**探索性证据**：核对 P 与 TwoStage 在六窗上的 beta/权重、局部更新和一步风险是否相同；核对 P 与 U、F 与 P 确实产生不同权重和服务器步。现有报告称六窗中 P/TwoStage 一步风险相同，F 对 TwoStage 仅三窗有效胜出。若只使用 CSV，不能验证向量逐位相同，就引用已有 P1 报告和 `WINDOW_MECHANISM.json`，标明该向量结论未在本次重新解包核验。不要将六窗观察写成完整九窗结果或论文的主实验收益。

确认原三种子终点筛选的 `NO_GO_PREDICTIVE_SCREEN` 不变；P0 的 `PAPER_INTEGRATION_BLOCKED` 也不因本次 P1 而解除。论文旧表与本轮验证集分割、实现版本的可比性问题仍需另案审计。当前停止决定只关闭条件参考投影这条现行协议，不判定主动支持获取或其他尚未实验的新机制。

## 3. 交付并停止

仅在 `results_conditional_reference_projection/round_v1/p1_controlled_diagnostic_20261020_1010/` **新增** `STOP_REPORT.md`。报告按以下顺序写：结论、九窗冻结门槛与六窗逐窗差、最多可能胜出数、原实现异常、证据边界、成本实测与停止范围。每个数字指向原文件和 CSV 的窗口/方法键；对未执行三窗写 `NOT_RUN`，不补 0。资源数字从 `RESOURCE_AND_BUDGET.json` 读取，避免把“预算剩余”说成继续实验的科学理由。

验收标准：停止报告明确区分 `FAIL_IMPLEMENTATION` 与 `STOP_BY_FROZEN_GATE_FUTILITY`；完整列出 P 和 F 对 TwoStage 的六窗有效胜出计数和九窗理论最大值；不改原文件、不产生新预测或训练、不写论文新性能主张。若证据冲突，则交付明确的 `EVIDENCE_CONFLICT` 报告并停止，不自行修复、补跑或改门槛。
