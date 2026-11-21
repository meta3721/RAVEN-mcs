# T1 报告：debt 递推逐窗诊断（round v3）

```text
协议：raven-mcs-w1-round-v3-execution-prompt.md（sha256 ae1c8214…）T1
预注册：round_v3/PREREG.md（sha256 dd53b461…）
脚本：scripts/w1_v3_debt.py（只读；只写 round_v3/）
输入：raven_wo_use / raven_wo_obs 的 p2_invocation_states.json + window_metrics.json，2 数据集 × 20 种子 = 80 run
只用记录量：states 的 M / mu / debt 与 window_metrics 的 alpha。未使用任何回放 α。
```

## 1. 结果：递推**精确成立**（η = 0.01）

```text
Q̃_{r+1} = max(Q_r^rec + 0.01 · (μ − M_r α_r^rec), 0)
e_r     = ‖Q̃_{r+1} − Q_{r+1}^rec‖_∞
```

| 数据集 | 臂 | run 数 | `max_r e_r ≤ 1e-12` | `max_r e_r` 实测 |
|---|---|---|---|---|
| SensorScope | `raven_wo_use` | 20 | **20/20** | **0.0** |
| SensorScope | `raven_wo_obs` | 20 | **20/20** | **0.0** |
| U-Air | `raven_wo_use` | 20 | **20/20** | **0.0** |
| U-Air | `raven_wo_obs` | 20 | **20/20** | **0.0** |
| **合计** | | **80** | **80/80** | **0.0**（逐窗逐分量精确相等，无浮点残差） |

- 无任一 run 出现 `e_r > 1e-12`，故**没有"第一个超标窗口"**：H1–H4 在该窗口上的判定**不适用**（协议只在存在超标窗口时要求逐条检验）。
- 附带记录（`DEBT_RECURSION.csv`）：states 条数 = 活跃窗口数（97/97 SS、66/66 与 74/74 UA）；每 run 的 Q 变化次数 = states 条数 − 1（除 Q_0 = 0 外每窗都更新）；`α` 的逐窗和均为 1（记录值本身不需要再归一化）。
- **判定（协议原文）**：全部 run `max e_r ≤ 1e-12` → **v2 的"递推不成立"更正为"v2 的拟合方法有误"**；T5 使用此递推作为新规则的定义。

## 2. v2 的误判机制（已复现并定量）

v2 的 `scripts/w1_debt_eta_infer.py` 在网格搜索 η 时，除循环内逐窗比较外，还在循环**之后**多比较了一次：

```text
err = max(err, ‖Q_n − rec[n-1]‖_∞)      # Q_n 是"第 n 窗更新后"，rec[n-1] 是"第 n-1 窗更新前"
```

这是一次**尾部错位一拍**的比较。实测（SensorScope `raven_wo_use` seed 30001）：

| η | 循环内（正确对齐）最大误差 | v2 式尾部项 |
|---|---|---|
| **0.01** | **0.000e+00** | 3.286e-03 |
| 0.008 | 1.013e-03 | 3.304e-03 |
| 0.002 | 4.054e-03 | 4.425e-03 |

尾部项（≈3.3e-3，量级 = 单步正部质量 `max_j‖0.01(μ−M_jα_j)‖_∞ ≈ 9.97e-3` 的一部分）**大于 η=0.01 时的真实残差（0）**，因此 η 的 argmin 被这一人为项主导，网格选到 0.002–0.011 之间的错误值，并据此得出"没有常数 η 能复现记录轨迹"的结论。该结论**不成立**。

## 3. 对 round v2 结论与论文的影响

| v2 结论/处置 | T1 后的状态 |
|---|---|
| `round_v2/EXECUTION_REPORT.md` §8 偏差 3："协议写的 debt 递推公式不成立" | **撤回**：公式与冻结实现一致（`src/raven_mcs/aggregation/debt.py:update_debt`，η = `self.eta` = 0.01，`window_runner.py:130/1194`） |
| `round_v2/PHASE4_INPUT_GAPS.md` §1.1（"没有常数 η 能复现"） | **撤回**，机制见 §2 |
| v2 把 L6/L4′ 的 debt 改为 `open_loop_Q`（记录值开环） | **不再必要**，但 v2 的**数值不受影响**：记录 Q 与递推 Q 逐位相同（e ≡ 0），故 v2 的 L6/L4′ 与"按递推自洽求解"等价。v3 的 T5 直接使用递推 |
| 论文 `eq:debt_bound` 的推导前提（该递推） | **获得实现层验证**：冻结 run 的 Q 轨迹逐窗逐分量满足该递推（80/80 run，误差 0.0） |
| v2 的 C3 证书（240/240 通过，比值 0.72–0.82） | 不变（读的是 `final_metrics.Q_norm1_over_S`） |

## 4. 输出

| 文件 | 内容 |
|---|---|
| `DEBT_RECURSION.csv` | 80 行：`ds, arm, seed, n_states, n_active, n_pairs, max_e, median_e, first_bad_window, q_change_count, …` |
| `DEBT_RECURSION.json` | 汇总：`runs_all_within_tol = 80/80`、`max_e_overall = 0.0` |
| `DEBT_RECURSION_HYPOTHESES.csv` | 未生成（无超标窗口 → H1–H4 不适用） |
