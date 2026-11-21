# ERRATA_v3：round v3 的三条更正与 E7/E8（round v4 / A0.2）

```text
只更正表述，不改 round_v3 的任何文件。
每条给 v3 原句位置（文件 + 节/列）、原句或原读数、更正后表述、以及由哪个任务定案。
```

## R1 无超参数规则只在报告半上评估 → U-Air 结论半间不稳

| 项 | 内容 |
|---|---|
| 位置 | `round_v3/EXECUTION_REPORT.md` §3（"主表（报告种子均值）"整表）与 §3 的一句话结论；`SOURCE_LADDER.csv` 的 `split` 列 |
| 原读数 | U-Air `B1(raven)` 的 `G` = 0.2475（报告半）；结论由此写"B1 把约 25% 的差距关掉" |
| 事实 | `B0`–`B3`、`uniform`、`L5/L6`（冻结 λ）**没有超参数**，却只在报告半上评估；`DEBT_STRENGTH.csv` 显示 U-Air `κ=0`（即 B1）在报告半 `G` = 0.247、在调参半 `G` = 0.003 |
| 更正 | 无超参数规则一律用**全部 20 个种子**报告，并同时给两个半；U-Air 的"B1 关掉约 25%"只在报告半成立，**不得作为结论** |
| 定案 | **A1**（`FULL_SEED_LADDER.csv`、`FULL_SEED_DECISIONS.csv`） |

## R2 T5 汇总池化了两个数据集，"此消彼长"一句不成立

| 项 | 内容 |
|---|---|
| 位置 | `round_v3/EXECUTION_REPORT.md` §4 末段；`round_v3/EXPLORE_SUMMARY.json` 的 `report_best_*` |
| 原读数 | `d_group = 1.0322`、`d_cs = 1.2505`，并据此写"结构端点之间出现此消彼长" |
| 事实 | `1.0322` = (SensorScope 0.9942 + U-Air 1.0701)/2，`1.2505` 同样池化；κ 也是在池化曲线上选的。**分数据集**看，κ 由 0 升到 1000 两个端点**同时下降**：SS `Δ_c-s` 1.2825 → 1.2807，UA 1.2281 → 1.2202 |
| 更正 | 删除"此消彼长"；T5 的选择、报告与曲线全部按数据集分开，**禁止跨数据集平均** |
| 定案 | **A2**（`DEBT_STRENGTH_V4.csv/.json`） |

## R3 T5 的门未过且读数无信息量

| 项 | 内容 |
|---|---|
| 位置 | `round_v3/EXECUTION_REPORT.md` §4 第 1 条与 §8"门未通过"行；`DEBT_STRENGTH.csv` 的 `max_alpha`/`min_ess` 列 |
| 原读数 | `κ=0` 与 B1 差 1.11e-05 > 1e-9；`max_alpha = 1.0`、`min_ess = 1.0` 每行相同；κ 曲线在 1000 仍在下降 |
| 事实 | 1.11e-05 的差最可能来自**两条代码路径各自求解投影**（v3 的 B1 用 `w1_ladder.project_seq`，T5 用自建 QP）；`max_alpha/min_ess` 的读数来自 `K = 1` 的窗口，与"约束是否绑定"无关；曲线未收敛 |
| 更正 | ① B1 与 T5 必须调用**同一个** `proj_Cr`，门改为 α L∞ ≤ 1e-8 且两端点差 ≤ 1e-9；② 删除 `max_alpha`/`min_ess`，改为只统计 `K ≥ 2` 窗口的 `frac_cap_bind`/`frac_l2_bind`/`frac_vertex`；③ κ 网格延伸到 1e5，给收敛判据（最后两点 `Δ_group` 变化 < 可关差距的 1%） |
| 定案 | **A2** |

## E7 v2 的 L3/L5/L6 用的是 `raven_wo_use` 的 β̂（q 关），不是 RAVEN 的

| 项 | 内容 |
|---|---|
| 位置 | `round_v2/PHASE4_REPORT.md` §2 表头（"L5 完整瞬时 P2（debt=0）"、"**L6 P2 + debt**"）；`round_v3/SOURCE_LADDER_CHECKS.csv`（字面 RAVEN-β̂ 版本差 2.62e-3 / 2.46e-3） |
| 事实 | v2 的 `R_on` 状态源是 `raven_wo_use`（v3 已记录）；因此 v2 的 L3/L5/L6 是"以 `raven_wo_use` 参照为 β̂"的规则，**不是 RAVEN 自身的参照**（E3 `raven` 与 E4 `raven_wo_use` 相差 `uses_usable_ipw` 标志） |
| 更正 | v2 的标签改为"P2 + debt on the `raven_wo_use` reference"；A1 中两者的 20 种子读数**并列报告** |
| 定案 | **A1** |

## E8 `ε ≥ 30` 的 `solver_fail` 来自目标缩放，不是问题本身

| 项 | 内容 |
|---|---|
| 位置 | `round_v3/EXECUTION_REPORT.md` §8 `solver_fail` 行；`round_v3/GRID_EXTENSION.csv`（缺 ε=30/100/1000 行） |
| 事实 | `½‖Mα−μ‖² + ½ε‖α−β̂‖²` 在 ε ≥ 30 时目标尺度失衡，CLARABEL 失败 |
| 更正 | 等价改写 `(1/ε)·½‖Mα−μ‖² + ½‖α−β̂‖²`（同 argmin）后重解；`ε = ∞` 端点用 `proj_Cr` |
| 定案 | **A3**（`GRID_EXTENSION_V4.csv`） |

## 汇总

| 条 | 定案任务 | 状态 |
|---|---|---|
| R1 半间不稳 | A1 | 待 |
| R2 池化/此消彼长 | A2 | 待 |
| R3 门与绑定诊断 | A2 | 待 |
| E7 β̂ 标签 | A1 | 待 |
| E8 大 ε 缩放 | A3 | 待 |
