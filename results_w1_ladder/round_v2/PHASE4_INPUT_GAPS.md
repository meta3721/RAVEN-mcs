# Phase 4 输入与门的实测发现（round_v2）

```text
本文件只记录在 Phase 4 施工期由实测得出的、会改变阶梯实现方式的事实与偏差。
阶梯数值结果见 PHASE4_REPORT.md。脚本：scripts/w1_ladder.py、scripts/w1_debt_rule_diag.py、
scripts/w1_debt_eta_infer.py（均只读，只写 results_w1_ladder/round_v2/）。
```

## 1. G5 结果：L5 精确通过，协议写的 debt 递推公式不成立

第一轮 G5（`debt=Q` 由协议公式 `Q_{r+1} = [Q_r + η(μ − M_r α_r)]_+` 递推）结果：

| 锚臂 | 模式 | 通过数 | `max α` L∞ | 端点差 | `max` debt L∞ |
|---|---|---|---|---|---|
| `raven_wo_debt`（= `inst_cal` 策略） | L5（debt = 0） | **40/40** | 3.21e-9（SS）/ 1.16e-9（UA） | ≤ 4.44e-11 | — |
| `raven_wo_obs` | L6（递推 Q） | **0/20** | 1.57e-1 | 2.51e-2 | 5.12e-1 |
| `raven_wo_use` | L6（递推 Q） | **0/20** | 1.60e-1 | 2.51e-2 | 5.12e-1 |

L5 通过说明**回放机器本身是精确的**（`solve_p2` + 冻结 λ/β̂/V 与冻结 α 一致到 1e-9 量级）。L6 失败只可能来自 `Q` 的输入。

### 1.1 根源：`pair_state.eta_r` 不是 debt 步长，且没有任何常数 η 能复现记录的 Q

- runner 的 debt 更新：`update_debt(Q, mu=μ, omega=M_rα_r, eta=float(self.eta), active=True)`
  （`src/raven_mcs/aggregation/debt.py:8-31`，调用点 `src/raven_mcs/training/window_runner.py:1194`），
  公式结构与协议一致，但 η 取 `self.eta`，其默认值为 **0.01**（`window_runner.py:130`）。
- 我最初把 `pair_state.eta_r`（恒为 1.0）当作 η 使用 —— 该列与 debt 步长无关，导致递推 Q 比记录值大约 100 倍。
- 即便把 η 当自由参数拟合，**也没有常数 η 能复现记录的轨迹**（2 数据集 × 2 有 debt 臂 × 5 种子）：
  最优 η ∈ {0.002, 0.005, 0.008, 0.0095, 0.011}，对应残差 `max|Q_prop − Q_rec|_∞` ∈ [3.7e-4, 3.90e-3]。
  单格示例（SensorScope `raven_wo_use` seed 30001）：记录 Q 的逐窗 L1 = 0, 0.00968, 0.01947, 0.02900, 0.03849；
  协议公式（η=1）给 0.968, 1.947, 2.900, 3.849, 4.775；增量对残差的最佳标量 c = 0.002985，
  拟合残差 3.17e-3（未解释）。
- **结论**：冻结产物里的 Q 轨迹不能由记录下来的 `(M_r, α_r, μ)` 自洽重建。

### 1.2 处置（对协议的偏差，已登记）

1. **L6 与 L4′ 的 debt 改为"记录值开环输入"**：`debt = states[r]["debt"]`（`open_loop_Q`），
   不再使用协议写的自递推。证据：喂入记录 Q 时，回放 α 与冻结 α 一致到 **1.99e-10**，
   `Δ_group` = 1.000658262621 vs 冻结 1.000658262616（差 5e-12）；喂 0 时 α 差 1.3e-3。
2. **阶梯的 R_on 状态源从 `raven_wo_debt` 改为 `raven_wo_use`**：前者的 `debt ≡ 0`（其策略
   `uses_debt=False`），若用它做源，L6 会退化为 L5。`raven_wo_use` 是 Design-on、`uses_debt=True`、
   且有非零 Q 的臂；G1（round_v2）已实测该族 `M` 与 `w_atomic` 相同，故仍是同一把尺子。
3. **R_offp 阶梯本轮不做**（登记为未完成项）：预注册的判定表与 Holm 家族只针对主尺子（Design-on），
   Phase 3 已给出 R_offp 的前沿数值；补做 R_offp 阶梯属可选加固。
4. G5 重跑（`L5_zerodebt` / `L6_openloopQ`）的结果写入 `G5_REPLAY_CHECK.csv`。

### 1.3 对后续相位与写作的影响

- Phase 5 的 C3 证书读 `final_metrics.Q_norm1_over_S`（冻结运行的报告值），**不做 Q 的重建**——
  与本节结论一致：Q 不可自洽重建，只能引用记录值。
- 论文侧（若日后获授权写入）："debt 记账"作为一个机制，其轨迹在冻结产物中**不可自包含复现**，
  只能开环引用；这属于可复现性观察，不是性能结论。

## 2. L1 / L2 的输入可得性

| 档位 | 协议指定输入 | 冻结产物中的情况 | 处置 |
|---|---|---|---|
| L1 Count | `raw_counts` | 在 runner 内存中构造（`window_runner.py:1063-1067`），只进入 `sag_window_logs`（:519），**未落盘**；已核查该 run 目录全部 JSON/parquet，无 mass/count 字段 | **重建**：`raw_counts = 1/w_atomic` = 该客户在该窗口的原子单元数（见下），标 `reconstructed_input` |
| L2 直接目标重加权 | `payload.total_masses`（m_k） | 同上（`window_runner.py:1068-1071`），未落盘 | **`input_unavailable`**：不做替代，L2 行写 NaN 并标 `input_unavailable`；`L3−L2` 对比记 `NA_input_unavailable` |

L1 重建的依据（实测，SensorScope seed 30001）：在一个 `(窗口, 客户端)` 块内 `w_atomic` 全部相等且
求和恰为 1（257 个块：1/2/3/4 行的块数 119/96/38/4），故行权 = 1/单元数。
L2 不能借用任何代理：把 β̂ 当 m_k 的代理时，`β̂/raw_counts` 在窗口内的变异系数中位数 0.55、最大 1.18
（即 m_k 与 `raw_counts` 不成比例），因此**没有**可从产物导出的忠实 m_k。

**要补齐 L1/L2 的唯一途径**：Phase-2 式带插桩的重跑（同时可产出精确 `V_r`、`Q_r`、`m_k`、`raw_counts`
与 `R_raw` 尺子），需用户单独授权。

## 3. 已冻结、未改动的项

- 档位定义、7 点调参网格、调参/报告种子拆分（30001–30010 / 30011–30020）、阈值 `τ_near=0.80`、
  `τ_eq=0.10`、bootstrap 10 000（种子 20261002）、Wilcoxon、Holm 家族（登记 20，实算 16，4 个 NA）均按预注册执行。
- `C_r` 参数 `alpha_max=0.5`、`e_min=3`、`max_server_learning_rate=1.0`、CLARABEL 容差 `1e-6`（与冻结 run 的 λ 一致：λ_g=1.0, λ_β=1.0, λ_v=0.1, λ_s=0.1）。
