# W1 round v3 预注册（PREREG）

```text
协议：raven-mcs-w1-round-v3-execution-prompt.md（attachment, sha256 ae1c8214…，278 行）
输入：results_w1_ladder/round_v2/（EXECUTION_REPORT.md 及其 33 个文件）
写入范围：results_w1_ladder/round_v3/ 与 scripts/w1_v3_*.py。只读 artifacts/ 与 round_v2/；不改 src/、论文、round_v2；不训练、不复跑。
本文件在执行任何 T1–T7 计算之前落盘；落盘后不得修改（T6 阈值如需改动，按协议只改本文件并重算 SHA-256，且在报告中披露）。
种子拆分：调参 30001–30010；报告 30011–30020（沿用 v2）。
```

## 0. 与 v2 的关系

- v2 的门（G1 v2 臂集合、G2、G4、G5、F1、C3）与其通过的数值**直接沿用，不重跑**。
- v2 的 6 条过度解读按 T0.2 的 `ERRATA_v2.md` 更正；**round_v2 的任何文件都不修改**。
- v2 的 Δ 单位判定**不再作为主判定**；T6 在 G 单位上重判（v2 列并排保留，标 `superseded_units`）。

## 1. T1：debt 递推逐窗诊断（只读）

**输入**：`raven_wo_use`、`raven_wo_obs` 的 `p2_invocation_states.json`，2 数据集 × 20 种子（共 80 run）。
**递推**（只用记录量，不用任何回放 α）：

```text
Q̃_{r+1} = max(Q_r^rec + 0.01 · (μ − M_r α_r^rec), 0)
e_r     = ‖Q̃_{r+1} − Q_{r+1}^rec‖_∞
```

- 记录每个 run 的 `max_r e_r`；第一个 `e_r > 1e-12` 的窗口号，及其 `K_r`、求解状态、是否 fallback / feasibility repair。
- 在该窗口上逐条判定 H1–H4（假设与检验按协议原文）：
  - H1：states 第 j 条 ≠ 第 j 个活跃窗口 → 用 `len(window_metrics.active_clients)` 与 `len(M)` 逐条比对；
  - H2：α 在 debt 更新前被重新归一化 → 用 `α/α.sum()` 重算 `e_r`；
  - H3：存在调用 P2 但未更新 debt 的窗口（或反之）→ 比较 states 条数、活跃窗口数、Q 变化次数；
  - H4：η ≠ 0.01 → 在 `config_snapshot.json`、`runtime_manifest.json` 中搜 `eta`。
**判定**（协议原文）：全部 run `max e_r ≤ 1e-12` → v2 的"递推不成立"更正为"v2 的拟合方法有误"，T5 用此递推；否则 T5 仍用此递推作为新规则的**定义**，并报告冻结轨迹偏离它的窗口与幅度。
**输出**：`DEBT_RECURSION.csv`、`DEBT_RECURSION.md`。

## 2. T2：同尺子审计（只读）

**臂集合**：E3 的 `fedavg_window, fedau_window, obsuse_window, fedasync_window, flamf_timealign_adapted, debt_cal, twostage_hajek, local_hajek, raven_simoracle` 与 E4 的 `raven_wo_design`；每个 `(ds, seed)`。
1. 按 `window_id` 对齐到 `R_on`，要求 `active_clients` 完全相同；报告对齐比例 `a`。
2. `a = 100%`：用该臂冻结的 `window_metrics.alpha` 在 `R_on` 上回放 `Δ_group` 与 `Δ_c-s`（`Δ_c-s` 用该臂自己的 `pair_state.w_atomic`），与其冻结值比较；`≤ 1e-9` → **同尺**，否则 **异尺**。
3. `a < 100%` → 记 `ruler_misaligned`，不回放。
**分解**（只对同尺臂，按数据集）：`Δ_FedAvg − Δ_RAVEN = (Δ_FedAvg − Δ_unif) + (Δ_unif − Δ_RAVEN)`；每段给 20 种子均值、配对 bootstrap 95% 区间（10 000 次，种子 `20261002`）与占比；`fedau_window`、`obsuse_window` 同样分解。异尺的数据集只写"跨两把尺子，不可分解"，不给数字。
**输出**：`SAME_RULER_AUDIT.csv`、`GAP_DECOMPOSITION.csv`。

## 3. T3：参照源与投影阶梯（核心，只读）

在 `R_on`（SensorScope 亦可用 `R_offp`，两者实测同一对象）上，`Proj_C(β) = argmin_{α∈C_r}‖α−β‖²`（cvxpy + CLARABEL，`C_r` 参数与 v2 相同：`alpha_max=0.5`、`e_min=3`、`max_server_learning_rate=1.0`、容差 `1e-6`）。

| 规则 | 定义 |
|---|---|
| B0(src) | `α = β_src`，不投影；记录越界量 `outside_Cr_l1` |
| B1(src) | `α = Proj_C(β_src)` |
| B2(src) | v2 的 L3：`argmin ½‖Mα−μ‖² + ½·1·‖α−β_src‖²`（ε = 1） |
| B3(src) | `solve_p2(debt=0)`，冻结 λ（λ_g=1, λ_β=1, λ_v=0.1, λ_s=0.1），`β = β_src`，V 取自 `raven_wo_use` 轨迹 |

**src 集合**：`raven`、`raven_wo_obs`（去 p）、`raven_wo_use`（去 q）、`raven_wo_design`（去 ζ，SS 可用 / UA 预计不对齐）、`raven_simoracle`（先查对齐）、`uniform`（1/K）、`count`（v2 的 L1 重建计数，标 `reconstructed_input`）。β 取各臂冻结的 `window_metrics.beta_hat`，只用 `active_clients` 与 `R_on` 逐窗相同的窗口。

**内部检查（失败即停 T3–T6）**：
1. `B2(raven)` 复现 v2 的 L3 报告值（差 ≤ 1e-9）；
2. `B3(raven)` 复现 v2 的 L5（差 ≤ 1e-7）；
3. 连续性：L3 在 `ε ∈ {10,100,1000}` 单调趋近 `B1(raven)`，记录差值。

**对齐处理**：`(src, seed)` 对齐比例 < 100% → 该种子不计入；可用种子 < 8 → 该 src 在该数据集记 `insufficient_alignment`。
**输出**：`SOURCE_LADDER.csv`（`ds, src, rule, seed, split, d_group, d_cs, tv_group_pp, tv_cs_pp, G_group, G_cs, outside_Cr_l1, aligned_frac`）。
**登记的配对对比**（报告种子，`d_group`/`d_cs` 各一套）：`B1(raven)−B0(raven)`、`B2(raven)−B1(raven)`、`B3(raven)−B2(raven)`、`B1(raven)−B1(raven_wo_design)`（仅 SS）、`B1(raven)−B1(raven_wo_obs)`、`B1(raven)−B1(raven_wo_use)`、`B1(raven_simoracle)−B1(raven)`（若对齐）、`B1(raven)−B1(uniform)`。

## 4. T4：网格延伸（**探索性**）

只在调参种子上看曲线，不做报告种子判定：L3 的 `ε ∈ {1,3,10,30,100,1000,∞}`（`∞` = `B1(raven)`）；L4 的 `λ_v ∈ {0,0.001,0.003,0.01}`；L5 的 `λ_g ∈ {0,0.1,0.3,1}`，用 `solve_p2(..., instant_calibration=False)` 允许 `λ_g<1`，报告中必须注明**越出论文 P2 合法域**。输出 `GRID_EXTENSION.csv`。

## 5. T5：在线 debt 强度扫描（**探索性**，新规则）

对 `κ ∈ {0,1,3,10,30,100,300,1000}`：

```text
α_r     = argmin_{α∈C_r}  −κ Q_rᵀ M_r α + ½‖α − β̂_r‖²      （β̂ 取 raven 的 beta_hat）
Q_{r+1} = max(Q_r + 0.01·(μ − M_r α_r), 0),  Q_0 = 0        （自洽递推，每档用自己的 α）
```

- `κ = 0` 必须等于 `B1(raven)`（差 ≤ 1e-9），否则停 T5；
- 另做带组项变体 `+ ½‖M_r α − μ‖²`，同 κ 网格；
- 调参种子上按 `Δ_group` 选 κ，报告种子上报告；
- 必须写明：这是**不同于冻结方法的新规则**，预测端点未知；若 `G` 随 κ 单调上升且最优在网格端点 → 写"网格未收敛"，不外推；同时报告 `Δ_c-s` 方向。
**输出**：`DEBT_STRENGTH.csv`。

## 6. T6：G 单位重判（只读）

对 v2 的登记对比与 T3 的登记对比，在报告种子上：

```text
ΔG = (Δ_a − Δ_b) / (Δ_unif − Δ*)      # 比值之比：分子分母先对种子取均值
```

95% 区间用配对 bootstrap，分子与分母**同一次重抽**（10 000 次，种子 `20261002`）。

**阈值（预注册，执行前可由用户修改——本文件为执行前定稿）**：
- **等效**：`ΔG` 区间完全在 `[−0.10, +0.10]` 内；
- **必要**：区间完全在 `+0.10` 以上（方向为"去掉该项后更差"）；
- **实践意义**：绝对改善的区间下界 `≥ 0.5 pp` 目标质量（group TV）。此线与 `G` 独立，两者都报告。
- **Holm 家族** = v2 的 16 条 + T3 的登记对比（按实际可算条数）；按数据集 × 端点分别报告（8 个家族，各 4 条 v2 + T3 实际可算条数）。为可与 v2 对照，**同时**给出 v2 式池化家族（跨 2 数据集 × 2 端点）的 Holm，两套并列披露，主判定用按数据集 × 端点的那套。
- T4、T5 不进入家族。
**输出**：`G_UNIT_DECISIONS.csv`（v2 的 Δ 单位判定列并排保留，标 `superseded_units`）。

## 7. T7：逐窗 L1 匹配的退化诊断（只读）

在 `R_on` 上对每个活跃窗口：
1. 在 `C_r` 上求 `min ‖M_r α − μ‖₁` 与 `max ‖M_r α − μ‖₁`，记极差 `range_r`；
2. 带打破平局的版本 `min ‖M_r α − μ‖₁ + 1e-6‖α − β̂_r‖²`，记 `Δ_myo_tb`。
**输出**：`MYOPIC_DIAG.csv`（`range_r` 分位数、`Δ_myo`、`Δ_myo_tb`、`Δ_unif` 比较）。
若 `range_r` 中位数 `< 1e-3` → 在 ERRATA 中把 v2 的 `Δ_myo` 结论改写为"逐窗 L1 目标在 `C_r` 上近乎平坦、argmin 不唯一；`Δ_myo` 不代表不记账规则的最优"。

## 8. 失败即停（协议原文）

| 条件 | 动作 |
|---|---|
| T3 内部检查 1 或 2 失败 | 停 T3–T6，先查回放实现 |
| T5 中 `κ = 0` ≠ `B1(raven)` | 停 T5 |
| 任一新求解状态非 `optimal` 且无可行性修复记录 | 该格记 `solver_fail`，不计入均值 |
| 任何 `Δ_rule < Δ* − 1e-7`（同尺子、同种子） | **整轮停**：违反下界，必有实现错误 |

## 9. 禁止写的结论（协议原文）

- 任何关于 `RMSE_μ` 或 WorstGroupRMSE 的结论；
- 把 T4/T5 结果写成冻结方法的性能，或"RAVEN 调参后可达 …"；
- 不加"同活跃集、同 `M_r`、同 `C_r`、事先知道全部窗口"限定就引用 `Δ*`；
- 在异尺或未对齐的格子上做 T2 分解；
- 把 `G` 作为唯一读数（凡给 `G`，同行必须给 pp）；
- 把 v2 的 Δ 单位判定继续当作主判定。

## 10. 探索性声明

**T4、T5 是探索性的**：其网格是在看过 v2 的端点选择之后定的；结论只能写"探索性"，不进入 W1 的主判定。
