# Executable instruction: W1 round v3 — attribution of the structural gain

```text
Mode: design, then one execution prompt. This file starts no run.
Venue: IEEE TMC revision of RAVEN-MCS, external review W1 (major).
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Input: results_w1_ladder/round_v2/ (EXECUTION_REPORT.md and its 33 files).
Scope: SensorScope and U-Air, read-only replay. No training, no Phase 2, no City Scanner.
```

## What round v2 established, and what it did not

**Established; carried forward without re-running:**

- G1 (v2 arm set), G2, G4, G5 (`L5_zerodebt`, `L6_openloopQ`), F1 and C3 all pass. Replay of α with frozen inputs is exact.
- The closable structural headroom against uniform weights is small:
  - SensorScope: 3.85 pp of target mass (group TV) and 2.12 pp (c-s).
  - U-Air: 0.93 pp and 1.25 pp.
  - The best rung, L6, recovers 0.28–0.58 pp of it.
- L6 − L5 and L5 − L3 are within ±0.10 of the closable gap in G units (the closable gap is the denominator of `G`).

**Wrong or over-read in round v2; to be corrected in v3:**

1. **The attribution reads "target matching inside `C_r`". The ladder itself says otherwise.**
   - L4′ keeps the group term and debt but sets the β̂ anchor to `1e-8`. It lands at uniform (`G ≈ 0.003`).
   - L3 keeps the group term with a strong anchor (`ε = 1`). It reaches `G ≈ 0.18`.
   - So the gain comes from the reference β̂, not from the group term.
   - SensorScope makes this sharper. `R_on` and `R_offp` are the same object there (identical active sets and `M_r`), yet RAVEN has `G = 0.189` and RAVEN-NoDesign `G = 0.006` on that same ruler. With `M` fixed, the only thing that differs is β̂, through the ζ-weighted masses.
   - Round v2 never tested this directly. There is no rung `α = Proj_{C_r}(β̂)` and no swap of the β source.
2. **The decision threshold had the wrong units.** `τ_eq = 0.10` was applied in Δ units, but the whole closable gap is 0.026–0.069 in Δ units. Rows ① and ② could therefore not fail. The design intent was G units (PREREG v1 §3). The decision must be re-run in G units with a confidence interval on ΔG.
3. **"Per-window optimum gives no gain" is not supported.**
   - `Δ_myo ≈ Δ_unif` (difference ≤ 2.6e-5) while L3 reaches `G ≈ 0.2`.
   - Each window covers only a few of the 144 groups, so per-window `‖M_r α − μ‖₁` is almost flat on `C_r`. The L1 argmin is not unique, and the solver returned a point near uniform.
   - `Δ_myo` is the value of one degenerate rule. It is not "the best a debt-free rule can do".
4. **Most of the published FedAvg→RAVEN gap may come from dropping count weighting.**
   - On SensorScope, FedAvg's frozen `Δ_group` is 1.0558, uniform is 1.0269 and RAVEN is 1.0139.
   - L1 (count weighting) is worse than uniform (`G = −0.10`).
   - If FedAvg's ruler equals `R_on` on SensorScope, then about 69 % of the reviewer-quoted improvement of 0.0419 is earned by uniform weights.
   - Round v2 did not check this. It looks checkable without Phase 2.
5. **The debt-recursion failure was diagnosed only part-way.**
   - The runner uses `η = self.eta = 0.01` (`window_runner.py` line 130). The first recorded increments, `0.00968, 0.01947, …`, equal `η = 0.01` times the η = 1 values.
   - "No constant η reproduces Q" was fitted by a scalar on the L1 norm of Q. That is not a simulation of the recursion with `η = 0.01`.
   - The paper's `eq:debt_bound` derivation relies on this recursion, so the residual must be located window by window.
6. **`G` is fragile.** 31 of 70 cells have a seed CV of the denominator above 25 %. U-Air `R_on` gives `G = 0.124 ± 0.383` per seed. Absolute pp must be the primary reading and `G` secondary.

## Claim–evidence matrix for v3

| question | task | stop / caveat |
|---|---|---|
| Does the structural gain come from the reference β̂ projected onto `C_r`? | T3 | `Proj` replay fails to reproduce L3 at `ε→∞` (internal check) |
| Which factor inside β̂ carries it: ζ, p or q? | T3 β-source swap | source windows not aligned → excluded and counted |
| Is FedAvg's published `Δ_group` on the same ruler as RAVEN's? | T2 | reproduction > 1e-9 → "different ruler", no decomposition |
| Can an online rule get closer to `Δ*` if debt is strong enough? | T5 | exploratory; a new rule, not the frozen method |
| Do the v2 decisions survive in G units? | T6 | — |
| Does the logged Q follow `Q_{r+1} = [Q_r + 0.01(μ − M_r α_r)]_+`? | T1 | — |
| Is per-window L1 matching degenerate? | T7 | — |

---

你在仓库 `C:\Cursor\raven.mcs` 里执行。

- 只读 `artifacts/` 与 `results_w1_ladder/round_v2/`。
- 新文件只写 `results_w1_ladder/round_v3/` 与 `scripts/w1_v3_*.py`。可以 import `scripts/w1_replay.py`、`scripts/w1_ladder.py` 里的函数，但不改它们。
- 不改 `src/`、不改论文、不改 round_v2。不训练，不复跑。不提交，不推送。
- Python 用 `.venv_new\Scripts\python.exe`。

## T0：预注册与勘误（先写，后算）

1. 写 `round_v3/PREREG.md` 并计算 SHA-256，内容包括：
   - T2–T7 的全部定义与网格；
   - 种子拆分沿用 `30001–30010` 调参、`30011–30020` 报告；
   - 本文件 T6 的阈值与 Holm 家族枚举。
2. 写 `round_v3/ERRATA_v2.md`，逐条列出上面"Wrong or over-read"的 1–6 条。每条给出 v2 报告中的原句位置（文件、节号）和更正后的表述。不改 round_v2 的任何文件。
3. PREREG 中必须写明：T4、T5 是**探索性**的。它们的网格是在看过 v2 的端点选择之后定的，结论只能写"探索性"，不进入 W1 的主判定。

## T1：debt 递推逐窗诊断（只读）

**输入。** `raven_wo_use`、`raven_wo_obs` 的 `p2_invocation_states.json`，2 个数据集 × 20 个种子。

对每个 run，用**记录的** `α_r`（`window_metrics.alpha`）和 `M_r`、`μ`（states），**不使用任何回放 α**，做两步：

```text
Q̃_{r+1} = max(Q_r^rec + 0.01 · (μ − M_r α_r), 0)        # 一步预测
e_r     = ‖Q̃_{r+1} − Q_{r+1}^rec‖_∞
```

记录：
- 每个 run 的 `max_r e_r`；
- 第一个 `e_r > 1e-12` 的窗口号，以及该窗口的 `K_r`、求解状态、是否有 fallback 或 feasibility repair。

在第一个超标窗口上，依次检验下列假设，每条给"是 / 否 + 数值"：

| 假设 | 检验 |
|---|---|
| H1：states 的第 j 条对应的不是第 j 个活跃窗口 | 用 `window_metrics.active_clients` 的长度与 `len(M[0])` 逐条比对 |
| H2：`α` 在 debt 更新前被重新归一化 | 用 `α / α.sum()` 代替 `α` 重算 `e_r` |
| H3：存在调用了 P2、但没有更新 debt 的窗口（或反之） | 比较 states 条数、活跃窗口数与 Q 变化次数 |
| H4：`η` 不是 0.01 | 在该 run 的 `config_snapshot.json`、`runtime_manifest.json` 中搜索 `eta` |

**输出。** `DEBT_RECURSION.csv` 与 `DEBT_RECURSION.md`。

**判定。**
- 若全部 run 的 `max e_r ≤ 1e-12`：v2 的"递推不成立"更正为"v2 的拟合方法有误"，T5 使用此递推。
- 否则：T5 仍然使用此递推作为新规则的**定义**（新规则是自洽的，不需要复现冻结轨迹）。报告中写明冻结轨迹偏离它的窗口与幅度，供论文 `eq:debt_bound` 一节核对。

## T2：同尺子审计——冻结基线的 `Δ_group` 是否与 RAVEN 同尺（只读）

对 E3 冻结臂 `fedavg_window, fedau_window, obsuse_window, fedasync_window, flamf_timealign_adapted, debt_cal, twostage_hajek, local_hajek, raven_simoracle` 和 E4 的 `raven_wo_design`，在每个 `(ds, seed)` 上：

1. 按 `window_id` 对齐到 `R_on`，要求 `active_clients` 完全相同。报告对齐窗口比例 `a`。
2. 若 `a = 100%`：用该臂冻结的 `window_metrics.alpha` 在 `R_on` 上回放 `Δ_group` 与 `Δ_c-s`（`Δ_c-s` 用该臂自己的 `pair_state.w_atomic`），与它的冻结值比较。
   - `≤ 1e-9`：该臂与 RAVEN **同尺**。
   - 否则：**异尺**。
3. 若 `a < 100%`：记 `ruler_misaligned`，不回放。

**输出。** `SAME_RULER_AUDIT.csv`，列为 `ds, arm, seed, aligned_frac, err_group, err_cs, verdict`。

**分解（仅对同尺的臂、按数据集计算）。** 写 `GAP_DECOMPOSITION.csv`：

```text
Δ_FedAvg − Δ_RAVEN = (Δ_FedAvg − Δ_unif) + (Δ_unif − Δ_RAVEN)
```

两段各给 20 个种子的均值、配对 bootstrap 95% 区间（10 000 次，种子 `20261002`）和占比。`fedau_window`、`obsuse_window` 同样分解。

若 FedAvg 在某数据集上异尺：该数据集只写"published FedAvg–RAVEN `Δ_group` 差跨两把尺子，不可分解"，不给数字。

## T3：参照源与投影阶梯（核心，只读）

在 `R_on` 上（SensorScope 也可用 `R_offp`，二者相同）定义下列规则。`Proj_C(β)` 指 `argmin_{α ∈ C_r} ‖α − β‖²`，用 cvxpy + CLARABEL 求解，`C_r` 参数与 v2 相同。

| 规则 | 定义 | 回答的问题 |
|---|---|---|
| B0(src) | `α = β_src`，不投影（可能在 `C_r` 外，记录越界量） | 未经可行集约束的参照本身 |
| B1(src) | `α = Proj_C(β_src)` | 只做可行投影 |
| B2(src) | v2 的 L3：`argmin ½‖Mα−μ‖² + ½‖α−β_src‖²`（`ε = 1`） | 加上组匹配项 |
| B3(src) | `solve_p2(debt=0)`，冻结 λ，`β = β_src`，V 取自 `raven_wo_use` 轨迹 | 完整瞬时 P2 |

β 来源 `src` 取各臂冻结的 `window_metrics.beta_hat`，只用 `active_clients` 与 `R_on` 逐窗相同的窗口：

| src | 含义 | 预期可用 |
|---|---|---|
| `raven` | ζ, p, q 全开 | 两个数据集 |
| `raven_wo_obs` | 去掉 p | 两个数据集 |
| `raven_wo_use` | 去掉 q | 两个数据集 |
| `raven_wo_design` | 去掉 ζ | SensorScope；U-Air 预计不对齐 |
| `raven_simoracle` | 真值 p、q | 先检查对齐 |
| `uniform` | `1/K` | 两个数据集 |
| `count` | v2 的 L1 重建计数 | 两个数据集，标 `reconstructed_input` |

**内部检查（失败即停）。**
1. `B2(raven)` 必须复现 v2 的 L3 报告值（差 `≤ 1e-9`）。
2. `B3(raven)` 必须复现 v2 的 L5（差 `≤ 1e-7`）。
3. 再加一个连续性检查：L3 在 `ε ∈ {10, 100, 1000}` 时应单调趋近 `B1(raven)`，记录差值。

**对齐处理。** 某 src 在某种子上的对齐窗口比例 `< 100%` 时，该 `(src, seed)` 不计入。若可用种子少于 8 个，整个 src 在该数据集上记 `insufficient_alignment`。

**输出。** `SOURCE_LADDER.csv`，列为 `ds, src, rule, seed, split, d_group, d_cs, tv_group_pp, tv_cs_pp, G_group, G_cs, outside_Cr_l1, aligned_frac`。

**登记的配对对比**（报告种子，`d_group` 与 `d_cs` 各一套）：

| 对比 | 含义 |
|---|---|
| `B1(raven) − B0(raven)` | 投影的作用（对应 TwoStage-Hájek → 投影） |
| `B2(raven) − B1(raven)` | 组匹配项的增量 |
| `B3(raven) − B2(raven)` | 方差与时滞项的增量 |
| `B1(raven) − B1(raven_wo_design)` | ζ 的作用（仅 SensorScope） |
| `B1(raven) − B1(raven_wo_obs)` | p 的作用 |
| `B1(raven) − B1(raven_wo_use)` | q 的作用 |
| `B1(raven_simoracle) − B1(raven)` | 估计误差的作用（若对齐） |
| `B1(raven) − B1(uniform)` | 参照相对均匀的总作用 |

## T4：网格延伸（探索性，只读）

v2 中所有带网格的档位都选在网格端点。补下列网格，只在调参种子上看曲线，不做报告种子上的判定：

- L3 的 `ε ∈ {1, 3, 10, 30, 100, 1000, ∞}`，其中 `∞` 即 `B1(raven)`。
- L4 的 `λ_v ∈ {0, 0.001, 0.003, 0.01}`。
- L5 的 `λ_g ∈ {0, 0.1, 0.3, 1}`，调用 `solve_p2(..., instant_calibration=False)` 以允许 `λ_g < 1`。必须在报告中注明：这越出了论文的 P2 合法域。

**输出。** `GRID_EXTENSION.csv`。

## T5：在线 debt 强度扫描（探索性，只读；新规则，非冻结方法）

**目的。** `Δ*` 的优势来自跨窗口分配。debt 是论文里唯一的跨窗口机制，而冻结强度下它几乎不起作用（L6 − L5 ≈ 1e-4）。这里测：强度放大后，在线规则能把差距关掉多少。

**规则。** 对 `κ ∈ {0, 1, 3, 10, 30, 100, 300, 1000}`：

```text
α_r     = argmin_{α ∈ C_r}  −κ Q_rᵀ M_r α + ½ ‖α − β̂_r‖²
Q_{r+1} = max(Q_r + 0.01 · (μ − M_r α_r), 0),   Q_0 = 0
```

- 自洽递推：每档用自己的 α。不用 V，不用组项，β̂ 取 `raven` 的 `beta_hat`。
- `κ = 0` 必须等于 `B1(raven)`（差 `≤ 1e-9`），否则停止。
- 另做一组带组项的变体：`+ ½‖M_r α − μ‖²`，同样的 κ 网格。

**选择。** 在调参种子上按 `Δ_group` 选 κ，在报告种子上报告。

**输出。** `DEBT_STRENGTH.csv`，列为 `ds, variant, kappa, seed, split, d_group, d_cs, tv_group_pp, G_group, G_cs, max_alpha, min_ess`。

**报告时必须写明：**
1. 这是**不同于冻结方法的新规则**。其预测端点未知。任何"调大 κ 会更好"的说法，都要加"未训练、预测端点未测"。
2. 若 `G` 随 κ 单调上升且最优 κ 在网格端点：报告"网格未收敛"，不外推。
3. 同时报告 `Δ_c-s` 的方向：结构端点之间可能出现此消彼长。

## T6：G 单位重判（只读，复用 v2 与 v3 的逐种子数值）

对 v2 登记的配对对比和 T3 的配对对比，在报告种子上计算：

```text
ΔG = (Δ_a − Δ_b) / (Δ_unif − Δ*)     # 比值之比：分子、分母先对种子取均值
```

95% 区间用配对 bootstrap，分子与分母**同一次重抽**。

**判定阈值（预注册，执行前可由用户修改，只改 PREREG）：**

- 等效：`ΔG` 区间完全在 `[−0.10, +0.10]` 内。
- 必要：区间完全在 `+0.10` 以上（方向为"去掉该项后更差"）。
- 实践意义：绝对改善的区间下界 `≥ 0.5 pp` 目标质量（group TV）。此线与 `G` 独立，两者都报告。

**Holm 家族** = v2 的 16 条加 T3 的登记对比（按实际可算条数），按数据集 × 端点分别报告。T4、T5 不进入家族。

**输出。** `G_UNIT_DECISIONS.csv`。原 Δ 单位的 v2 判定列并排保留，标 `superseded_units`。

## T7：逐窗 L1 匹配的退化诊断（只读）

在 `R_on` 上对每个活跃窗口：

1. 在 `C_r` 上分别求 `min ‖M_r α − μ‖₁` 与 `max ‖M_r α − μ‖₁`，记录极差 `range_r`。
2. 再求带打破平局的版本：`min ‖M_r α − μ‖₁ + 1e-6 ‖α − β̂_r‖²`，记为 `Δ_myo_tb`。

**输出。** `MYOPIC_DIAG.csv`：`range_r` 的分位数，`Δ_myo`、`Δ_myo_tb` 与 `Δ_unif` 的比较。

若 `range_r` 的中位数 `< 1e-3`：在 ERRATA 中把 v2 的 `Δ_myo` 结论改写为"逐窗 L1 目标在 `C_r` 上近乎平坦，argmin 不唯一；`Δ_myo` 不代表不记账规则的最优"。

## 失败即停

| 条件 | 动作 |
|---|---|
| T3 内部检查 1 或 2 失败 | 停 T3–T6，先查回放实现 |
| T5 中 `κ = 0` 与 `B1(raven)` 不等 | 停 T5 |
| 任一新求解的状态非 `optimal` 且没有可行性修复记录 | 该格记 `solver_fail`，不计入均值 |
| 任何 `Δ_rule < Δ* − 1e-7`（同尺子、同种子） | 整轮停：违反下界，必有实现错误 |

## 验收清单（`round_v3/EXECUTION_REPORT.md` 逐条回答）

1. T1：每个 run 的 `max e_r`，H1–H4 的判定，以及对 v2 第 8 节偏差 3 的更正或确认。
2. T2：各臂同尺 / 异尺 / 未对齐的计数；同尺数据集上的 `GAP_DECOMPOSITION`，含两段的占比与区间。
3. T3：`SOURCE_LADDER` 的主表（报告种子均值，pp 与 `G` 并列），8 条配对对比的结果，以及"结构收益由哪一项承担"的一句话结论。结论只能从判定表套出。
4. T4、T5：曲线与"是否收敛"。T5 的最优 κ 下的 pp 与 `G`，标"探索性"。
5. T6：G 单位判定表，与 v2 的 Δ 单位判定并排。
6. T7：`range_r` 分位数与 `Δ_myo_tb`。
7. `ERRATA_v2.md` 的终版。
8. 特殊状态格子清单：`ruler_misaligned`、`insufficient_alignment`、`reconstructed_input`、`solver_fail`。

## 禁止写的结论

- 任何关于 `RMSE_μ` 或 WorstGroupRMSE 的结论。
- 把 T4 或 T5 的结果写成冻结方法的性能，或写"RAVEN 调参后可达 …"。
- 不加"同活跃集、同 `M_r`、同 `C_r`、事先知道全部窗口"的限定就引用 `Δ*`。
- 在异尺或未对齐的格子上做 T2 分解。
- 把 `G` 作为唯一读数。凡给 `G`，同行必须给 pp。
- 把 v2 的 Δ 单位判定继续当作主判定。

## 本轮之后（不在本轮）

依 T2、T3、T6 的结果，从下面两种贡献表述中选一种，另行授权改稿。

- **若 T3 显示 `B1(raven) ≈ B3(raven)`，且 ζ 承担主要作用：**
  "结构对齐来自机会层校正后的参照 β̂ 在可行集上的投影；P2 的组项、方差项、时滞项与 debt 在登记的等价界内无独立贡献。"

  这样 Design 与选择层重建得到正面归属，P2 与 debt 降级为可行性实现与可审计记账。
- **若 T2 显示 FedAvg→RAVEN 差的大部分来自 FedAvg→均匀：**
  正文的结构改善必须改为相对均匀权重报告，并同时给出 pp 与可回收余量。

是否需要 Phase 2（采集复跑）：只有当 T3 的结论依赖 L2，或审稿人要求 `R_raw` 上的前沿时，才建议授权。本轮不需要。
