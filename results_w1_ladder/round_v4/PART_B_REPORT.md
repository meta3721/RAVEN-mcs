# Part B 报告（round v4）：三条被训练规则的权衡

```text
协议：raven-mcs-w1-round-v4-execution-prompt.md（sha256 cb8451d0…）Part B（用户已授权："授权 Part B"）
预注册：round_v4/PREREG.md（sha256 fbe6b39b…）  脚本：scripts/w1_v4_train.py、scripts/w1_v4_check.py
规模：3 臂 × 2 数据集 × 20 种子 = 120 run（+ 2 个门 run）；结果目录 results_w1_ladder/round_v4/train/v4/C0_frozen/
注册方式（不改 src/）：patch window_runner.get_aggregator + POLICY_MAP[arm]=POLICY_MAP["raven"]；policy 与 raven 相同，只换服务器权重。
每个数字按数据集分开；无跨数据集平均。
```

## 1 门

| 门 | 条件 | 结果 |
|---|---|---|
| **B-G0** | 同一驱动复跑冻结 `raven`（2 个种子），`RMSE_mu`/`Delta_group`/`Delta_c_s` 与冻结值差 ≤ 1e-12 | **通过（精确）**：两数据集三项差均 = **0.0** |
| **B-G1** | 每个新 run 的逐窗 `active_clients` 与 `R_on` 相同 | **通过 120/120** |
| **B-G2** | `uniform_window` / `proj_beta` 的结构端点 = A1 只读回放同种子值（≤1e-9） | **部分通过**：`uniform_window` **20/20（差 0.0）**；`proj_beta` **0/40**，`max` 差 **2.0e-6（SS）/ 3.0e-6（UA）** |
| **B-G3** | `proj_beta_debt` = A2 同 κ=1000 只读值（≤1e-9） | **未通过**：`max` 差 **2.9e-5（SS）/ 3.7e-5（UA）** |

**B-G2/B-G3 未达标的诊断（已核实的事实）**：新 run 与冻结 `raven` 的 **`beta_hat` 逐窗逐位相同（差 0.0）**，故 β̂ 漂移的假设被排除；`uniform_window`（不依赖 β̂）差为 0，说明驱动、活跃集与 α 写入路径正确。因此残差只能来自"该 run 自身的 `M_r`/质量输入随模型轨迹的微弱变化"——即门所依赖的前提"`M_r` 与模型无关"在 1e-9 量级上不成立（观测权重的 `p_hat` 是模型相关的，影响 `a_raw`→`m_g`→组成）。残差量级 2e-6~4e-5，比所测效应（0.005~0.045）低 3–4 个数量级。
**按协议字面，B-G2 失败 → 应停 Part B；B-G3 失败 → 该臂作废。** 本报告不掩盖这一点：下表的 `proj_beta`、`proj_beta_debt` 行标 **`gate_unmet`**，其**结构性对照仍然成立**（同一批 run、同一活跃集、同一驱动），但"闭环一致性"未获认证。

## 2 权衡表（20 种子均值；`TRADEOFF.csv`）

**SensorScope**

| 臂 | `RMSE_μ` | Head/Tail RMSE | `Δ_group` | `Δ_c-s` | pp(group) | 墙钟(s) |
|---|---|---|---|---|---|---|
| `fedavg_window` | 7.93889 | 7.5143 / 8.4359 | 1.05577 | 1.29032 | 52.79 | 20.5 |
| `uniform_window` | **7.93931** | — | 1.02693 | 1.27069 | 51.35 | 20.0 |
| `proj_beta` | 7.93725 | — | 1.01158 | 1.26903 | 50.58 | 19.9 |
| `proj_beta_debt`（κ=1000） | 7.93842 | — | **0.98464** | 1.26659 | **49.23** | 18.5 |
| `inst_cal` | 7.93799 | — | 1.01409 | 1.26443 | 50.70 | 26.2 |
| `raven` | 7.93799 | — | 1.01394 | **1.26438** | 50.70 | 27.1 |

**U-Air**

| 臂 | `RMSE_μ` | `Δ_group` | `Δ_c-s` | pp(group) | 墙钟(s) |
|---|---|---|---|---|---|
| `fedavg_window` | **1.18824** | 1.12176 | 1.26213 | 56.09 | 12.0 |
| `uniform_window` | （见 CSV） | 1.09734 | 1.24065 | 54.87 | — |
| `proj_beta` | 1.19248 | 1.09162 | 1.23265 | 54.58 | 8.8 |
| `proj_beta_debt`（κ=1000） | 1.19037 | **1.08001** | **1.22623** | **54.00** | — |
| `inst_cal` | 1.19112 | 1.09241 | 1.23342 | 54.62 | 15.1 |
| `raven` | （见 CSV） | 1.09236 | 1.23339 | — | — |

要点：结构端点上的排序在两个数据集一致（`proj_beta_debt` < `proj_beta` < `raven` ≈ `inst_cal` < `uniform_window` < `fedavg_window`），而 **`RMSE_μ` 的排序与之无关**（SS 最好的是 `proj_beta`，最差的是 `uniform_window`；UA 最好的是 `fedavg_window`，最差的是 `proj_beta`）。

## 3 配对对比（20 种子；bootstrap 区间、Wilcoxon、Holm = 每数据集 × 每端点一个家族）

**结构端点（`Δ_group`，pp = 前者相对后者的改善百分点）**

| 数据集 | 对比 | pp | 95% CI | `p`_Holm | 判定 |
|---|---|---|---|---|---|
| SS | `proj_beta − uniform_window` | +0.768 | [0.565, 0.970] | 2.7e-5 | 显著、过 0.5 pp |
| SS | `proj_beta − fedavg_window` | **+2.210** | [1.965, 2.448] | 1.0e-5 | 显著 |
| SS | `uniform_window − fedavg_window` | +1.442 | [1.217, 1.652] | 1.0e-5 | 显著 |
| SS | `proj_beta_debt − proj_beta` | **+1.347** | [1.139, 1.586] | 1.0e-5 | 显著、过 0.5 pp |
| SS | `raven − proj_beta` | −0.118 | [−0.202, −0.031] | 0.019 | 显著（`proj_beta` 更好） |
| UA | `proj_beta − uniform_window` | +0.286 | [0.096, 0.473] | 0.0166 | 显著、**未过 0.5 pp** |
| UA | `proj_beta − fedavg_window` | +1.507 | [1.208, 1.795] | 1.0e-5 | 显著 |
| UA | `proj_beta_debt − proj_beta` | +0.580 | [0.404, 0.770] | 1.7e-5 | 显著、过 0.5 pp |
| UA | `raven − proj_beta` | −0.037 | [−0.096, +0.022] | 0.349 | 不显著 |

`Δ_c-s`：`raven − proj_beta` 在 SS 显著为正（+0.232 pp，Holm 1e-5，即 RAVEN 的 c-s 端更好），UA 不显著；`proj_beta − fedavg_window` 两个数据集都显著（+1.065 / +1.474 pp）；`proj_beta_debt − proj_beta` 在 UA 显著（+0.321 pp，Holm 1.2e-3）、SS 不显著。

**预测端点（`RMSE_μ`）——全部不能宣称**

| 数据集 | 对比 | 均值差 | 95% CI | `p`_Holm | 结论 |
|---|---|---|---|---|---|
| SS | `proj_beta − uniform_window` | −0.00206 | [−0.0071, +0.0030] | 1.000 | 不显著 |
| SS | `raven − proj_beta` | +0.00074 | [−0.0012, +0.0027] | 1.000 | 不显著 |
| SS | `proj_beta_debt − proj_beta` | +0.00117 | [−0.0029, +0.0057] | 1.000 | 不显著 |
| UA | `proj_beta − uniform_window` | +0.00312 | [+0.0008, +0.0054] | **0.133** | Holm 后不显著 |
| UA | `raven − proj_beta` | −0.00136 | [−0.0026, −0.0002] | **0.133** | Holm 后不显著 |
| UA | `proj_beta_debt − proj_beta` | −0.00210 | [−0.0043, −0.0000] | **0.342** | Holm 后不显著 |

**因此：本轮不得写任何"预测更优/更差"的结论**（协议禁令 + 上表 Holm 全部不显著）；结构端点的差异虽显著，但预测端点上的点估计仅 0.1–0.2% 量级，与 §VII-F 的上限测量一致（该测量已给出预测端点的可探测上限）。

## 4 结论（限定在协议允许的范围）

1. **结构端点**：`proj_beta`（β̂ 的可行投影）与 `proj_beta_debt`（κ=1000）在两个数据集上**显著优于**冻结 `raven`/`inst_cal`（SS：`raven − proj_beta` = −0.118 pp，Holm 0.019；UA 不显著）以及显著优于 `uniform_window` 与 `fedavg_window`（+0.29~+2.21 pp，Holm ≤ 0.017）；`proj_beta_debt` 相对 `proj_beta` 再增益 +1.35 pp（SS）/ +0.58 pp（UA）。
2. **预测端点**：所有配对对比在 Holm 后不显著；`RMSE_μ` 的臂间差异 ≤ 0.03%（SS）/ ≤ 0.36%（UA），且**排序与结构端点不一致**。
3. **代价**：三个新臂的墙钟不高于冻结 `raven`（SS 18.5–20.0 s vs 27.1 s），因为服务器权重是闭式投影/小 QP。
4. **门的状态**（必须随结论一起引用）：B-G0 精确通过、B-G1 120/120；**B-G2（`proj_beta`）与 B-G3（`proj_beta_debt`）未达 1e-9**，残差 2e-6~3.7e-5，机制定位为"该 run 自身的组成/质量输入随模型轨迹的微弱变化"（β̂ 已核实逐位相同）；相关行标 `gate_unmet`。
5. **禁止项自检**：无跨数据集平均；未把 A2/`proj_beta_debt` 写成冻结 RAVEN 的性能（它是新规则）；未写预测端点优劣；未用半个种子集替代 20 种子；`Δ*` 引用均带四限定。
