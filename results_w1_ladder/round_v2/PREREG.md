# W1 同支持前沿与必要性阶梯——预注册（round_v2）

```text
与 round_v1 的关系：round_v1 的 PREREG.md 未修改（sha256 698324b2…），它在 Phase 1 按协议原文
  的 G1 失败即停（status=STOP_G1_count_mismatch）。按协议「需要修改时新开 round_v2」，本文件为
  v2 的预注册：**唯一实质改动是 G1 的臂集合**，其余条款与 v1 逐条相同，并新增「本轮发现的事实」一节。
本文件写入后不得修改。
```

## 1. 与 v1 的唯一实质改动：G1 臂集合

| 项 | v1（协议原文） | **v2（本文件）** |
|---|---|---|
| G1 互校臂 | `raven_wo_debt`、`raven_wo_use`、`raven_wo_inst` | `raven_wo_debt`、`raven_wo_use`、`raven_wo_obs`（**均有非空 `p2_invocation_states.json`**） |
| `raven_wo_inst` | 参与互校 | **排除**，原因见 §5（该臂 states 为空列表：0 条 vs 活跃窗口 92–98 / 66–74） |
| 失败条件 | 三臂任一调用次数 ≠ 活跃窗口数，或 `M`/`w` 差 > 1e-12 | **同上，但只对 v2 的三臂** |
| `R_on` 来源 | `raven_wo_debt` | 不变（`raven_wo_debt`），并由 v2 三臂互校背书 |
| `R_offp` | 由 G2 保证 | 不变（`raven_wo_design`，由 G2 保证） |

其余全部条款（§2 调参/报告种子拆分、§3 阈值与判定表、§4 统计与 Holm 家族、§5 停止规则、§6 其他冻结项、§7 禁止写的结论）与 v1 逐字相同，见 `../round_v1/PREREG.md` §1–§6。

## 2. 沿用 v1 的全部冻结项（摘要，逐字同 v1）

- 档位 L0、L1、L2、L3、L4、L5、L6、L4′ 及其 7 点调参网格（v1 §1）。
- 调参 `30001–30010` / 报告 `30011–30020`；报告种子不得再选任何东西（v1 §2）。
- `τ_near = 0.80`、`τ_eq = 0.10`、必要性方向 `+0.10` 与判定表（v1 §3）。
- bootstrap 10 000 次、种子 `20261002`、Wilcoxon 符号秩、Holm 家族 = 2 数据集 × 2 端点 × 5 对比 = 20 个检验（v1 §4）。
- 门 G1–G5、F1、C3 与失败即停动作（v1 §5）。
- 求解器 CLARABEL 容差 `1e-6`；`C_r = {1ᵀα=1, 0≤α≤ᾱ, ‖α‖²≤1/Ē}`，`ᾱ = min(1, max(0.5, 1/K))`，`Ē = min(min(3,K), K)`；
  `Δ*` 的可辩护定义（同活跃集/同 `M_r`/同 `C_r`/事先知道全部窗口；不推广到其他图、信息集、活跃集；Design-on 与 Design-off 分尺子各算一次）；
  `G_F(rule) = (Δ_F(unif) − Δ_F(rule))/(Δ_F(unif) − Δ*_F)`，分母 <1e-6 记 `NA_degenerate`；`headroom_debt = Δ_myo − Δ*`，且 `Δ_myo` 不是在线规则下界（v1 §6）。
- 输出目录（v2）：`results_w1_ladder/round_v2/`；脚本：`scripts/w1_capture.py`、`scripts/w1_replay.py`。
- 禁止写的结论：v1 §6 末列出的 8 条，逐条适用。

## 3. 本轮新增的事实（只记录，不争论）

| 事实 | 证据 | 对设计的影响 |
|---|---|---|
| `raven_wo_inst` 的 `p2_invocation_states.json` 为空列表 | `artifacts/e4_core_mechanism_ablation_r1/runs/{sensorscope,uair}/raven_wo_inst/seed*/p2_invocation_states.json`（0 KB，`[]`），同目录 `pair_state.parquet`/`window_metrics.json`/`final_metrics.json` 正常 | 该臂不参与 G1 互校；其端点仍由 G2 借尺回放验证（v1 已通过） |
| 有 states 的 Design-on 族臂 | `raven_wo_debt`、`raven_wo_use`、`raven_wo_obs` 各 20 seeds 非空 | v2 的 G1 三臂 |
| v1 的 G1 实测值（偏差版） | `M` 最大差 `0.0`；`w_atomic` 最大差 `5.55e-17`；`active_clients` 全等 | v2 预期同样通过 |
| v1 的 G2 实测 | 320/320 通过，`Δ_group` ≤ `8.88e-16`、`Δ_c-s` ≤ `7.99e-15` | 回放机器对 8 个臂全部校准 |
| Phase 2 授权状态 | **未授权**（用户仅批准修正 G1） | Phase 3/4 只在 `R_on`、`R_offp` 上做；L4 标 `open_loop_V`；L5/L6 用 `raven_wo_debt` 的 `V` 开环；不报告 `R_raw` 前沿 |

## 4. 执行顺序偏差（沿用 v1 的披露）

v1 §7 已披露：三件只读诊断先于预注册落盘；v2 在此重述并补充——v2 的预注册同样写在 v2 的任何计算之前。

## 5. `raven_wo_inst` 排除的完整理由（写给复核者）

1. 协议 G1 的形式要求"三个臂的调用次数等于各自的活跃窗口数"；`raven_wo_inst` 为 0 ≠ 92–98（SensorScope）/66–74（U-Air），故该形式不可执行。
2. 排除后 G1 的**实质命题**（组成矩阵 `M` 与单位权重 `w_atomic` 与模型无关、且在 Design-on 族内共享）仍有三个独立臂可互校，且 v1 已实测通过。
3. `raven_wo_inst` 的端点并未失去验证：其 `Δ_group`/`Δ_c-s` 已在 v1 的 G2 中以借尺回放通过（40/40）。
4. 若未来要恢复"含 inst 的三臂互校"，唯一途径是 Phase 2 式采集（重跑该臂并落盘 states）；本 v2 不要求，也不据缺失做任何推断。
