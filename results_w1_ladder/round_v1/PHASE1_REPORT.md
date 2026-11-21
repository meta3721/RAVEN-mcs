# W1 阶梯与前沿：Phase 1 报告（round_v1）

```text
协议：raven-mcs-w1-ladder-frontier-execution-prompt.md
预注册：results_w1_ladder/round_v1/PREREG.md（sha256 698324b2f67ee96459c041723eff0319dd3b93df8997d9ddcc9d4cc82e58c0ce）
产物：RULER_CHECK.json / RULER_CHECK_seedlevel.csv / REPLAY_GATE.csv / RULER_INVARIANCE_deviation.csv
只读：未训练、未改 src/ 与论文、未写 artifacts/ 或任何已有结果目录、未提交
```

## 0. 一句话结论

**G1 按协议原文不可评估并触发失败即停**：`raven_wo_inst` 的 `p2_invocation_states.json` 是**空列表**（0 条），而其活跃窗口为 92–98（SensorScope）/66–74（U-Air）；协议要求三臂（`raven_wo_debt`、`raven_wo_use`、`raven_wo_inst`）各自"调用次数 = 活跃窗口数"，因此门 1 不成立，本轮按规则停在 Phase 1 末端，未进入 Phase 2–5。

**但 G1 的实质内容已在有落盘 states 的臂上验证通过**（标注为 `protocol_deviation`，需你批准）：`raven_wo_debt` / `raven_wo_use` / `raven_wo_obs` 的组成矩阵 `M` 逐元素最大差 **0.0**，`pair_state` 的 `w_atomic` 最大差 **5.55e-17**，`active_clients` 全等 ⇒ **Design-on 尺子 `R_on` 的共同性与模型无关性成立**。

**G2 全过**：320/320 格（2 数据集 × 20 种子 × 8 臂）自回放/借尺回放的端点与冻结值一致，最大误差 `Δ_group 8.88e-16`、`Δ_c-s 7.99e-15`，远小于 `1e-9` ⇒ **回放机器已对全部所需臂校准**，Phase 3–4 可以在已验证的尺子上搭建。

## 1. G1（协议原文版）

| 项 | 结果 |
|---|---|
| 三臂清单 | `raven_wo_debt`、`raven_wo_use`、`raven_wo_inst` |
| 不一致格数 | **40**（2 数据集 × 20 种子，全部由 `raven_wo_inst` 引起） |
| 典型值 | `sensorscope seed30001`：`raven_wo_inst 0 / 97`；`seed30002`：`0 / 98`；`uair` 同型（`0 / 66…74`） |
| 另两臂 | 调用次数 = 活跃窗口数（逐种子成立） |
| 协议动作 | **整轮停**（`RULER_CHECK.json: status = STOP_G1_count_mismatch`） |

**事实说明（不重新争论协议前提，只记事实）**：协议「Facts confirmed in the code」第 3 条称五个 E4 臂都写 `p2_invocation_states.json`；实测 `raven_wo_inst` 的该文件存在但为**空列表**（`0 KB`），而它的 `pair_state.parquet`、`window_metrics.json`、`final_metrics.json` 均正常。因此"三臂互校"这一形式在本仓库工件上不可执行。

## 2. G1 偏差版（`protocol_deviation`，需批准）：有 states 的臂

| 项 | 结果 | 容差 |
|---|---|---|
| 参与臂 | `raven_wo_debt`、`raven_wo_use`、`raven_wo_obs`（三臂均有 20 种子的非空 states） | — |
| `M` 逐元素最大差 | **0.0** | ≤1e-12 ✓ |
| `pair_state.w_atomic` 最大差 | **5.55e-17** | ≤1e-12 ✓ |
| `active_clients` 全等 | **是**（逐窗、逐种子） | — |
| 结论 | Design-on 尺子 `R_on`（取自 `raven_wo_debt`）在这三臂间**完全共有一致**，且与 debt/obs/use 的开关无关 | — |

`R_offp`（`raven_wo_design`）按协议没有同族兄弟可比，其有效性由 G2 保证（见下，40/40 通过）。

## 3. G2（自回放与借尺回放）

| 臂 | 尺子 | n | pass | max `Δ_group` 误差 | max `Δ_c-s` 误差 |
|---|---|---|---|---|---|
| `raven_wo_debt` | 自身 | 40 | 40 | 8.88e-16 | 6.88e-15 |
| `raven_wo_use` | 自身 | 40 | 40 | 6.66e-16 | 7.11e-15 |
| `raven_wo_obs` | 自身 | 40 | 40 | 6.66e-16 | 6.66e-15 |
| `raven_wo_design` | 自身（`R_offp`） | 40 | 40 | 6.66e-16 | 6.66e-15 |
| `raven` | 借 `R_on` | 40 | 40 | 6.66e-16 | 6.66e-15 |
| `inst_cal` | 借 `R_on` | 40 | 40 | 8.88e-16 | 6.88e-15 |
| `twostage_hajek` | 借 `R_on` | 40 | 40 | 8.88e-16 | 7.99e-15 |
| `local_hajek` | 借 `R_on` | 40 | 40 | 6.66e-16 | 7.33e-15 |

- 借尺对齐条件（`active_clients` 与 `raven_wo_debt` 逐窗相同）**在全部 160 个 E3 格上成立** ⇒ 无 `ruler_misaligned`。
- 端点公式：`Δ_group = ‖mean_r M_r α_r − μ‖₁`（`η` 常数、`S` = 活跃窗口数）；`Δ_c-s` 按 `client::stratum` 键、`w_atomic` 加权、按 `S` 平均后归一化，并与 `π^tar` 的**完整键集**取并集后求 L1。
- 该结果同时验证了协议要求的两件事：回放机器正确（对 8 个臂逐位复现冻结端点）与 `w_units` 口径（`twostage_hajek`、`local_hajek` 的 `Δ_c-s` 也通过，说明其局部权重在回放中按 `ζ,p` 口径处理正确）。

## 4. 停在何处、为什么

- 停点：**Phase 1 末端**（G1 失败即停）。
- 未做：Phase 2（需授权的 126 次复跑）、Phase 3（前沿）、Phase 4（阶梯）、Phase 5（代价/含义/证书）、Phase 6（可选新臂）。
- 未做原因不是技术障碍：G2 已证明回放机器对所需臂全部有效；唯一障碍是协议 G1 指定的三臂形式缺一个臂的落盘 states。

## 5. 需要你决定的三件事

1. **是否批准 G1 修正**：把 G1 的三臂集合改为"有非空 states 的 Design-on 族臂"（`raven_wo_debt`、`raven_wo_use`、`raven_wo_obs`），并把 `raven_wo_inst` 的缺失作为**记录事实**（不进入互校）；`R_offp` 仍只由 G2 保证。批准后即可继续 Phase 2–5。
2. **是否授权 Phase 2**（126 次复跑，约 46 分钟；逐位复现冻结运行，不产生新结果）：
   - 授权 ⇒ 可建 `R_raw`（`fedavg_window`/`fedau_window`/`debt_cal`），并拿到 `inst_cal`/`raven` 自己的 `V_r`，使 L5/L6 精确、L4 不必标 `open_loop_V`。
   - 不授权 ⇒ Phase 3/4 只在 `R_on`、`R_offp` 上做，L4 标 `open_loop_V`、L5/L6 用 `raven_wo_debt` 的 `V` 开环，且不报告 `R_raw` 前沿。
3. **（后续）是否授权 Phase 6**（唯一新训练臂 L2 的预测端点，20 seeds × 2 数据集 ≈15 分钟）。

## 6. 附：本轮与协议的口径对照（便于复核）

| 协议要求 | 实现 |
|---|---|
| `M` 与 `w` 的模型无关性（G1） | 已按偏差版验证；原文版因 `raven_wo_inst` 空 states 停 |
| 回放复现冻结端点（G2，容差 1e-9） | 320/320 通过，最大 7.99e-15 |
| `Δ_c-s` 的键与归一化 | 按 `client::stratum`，`w_atomic` 加权 /`S`，归一化后与 `π^tar` 并集求 L1 |
| `π^tar` 重建 | `build_pi_tar_client_stratum(atomic, spatial_to_client, split="test")`，键数 288（U-Air）/ 440（SensorScope 同族口径） |
| 预注册先于计算 | **有偏差**：三件只读诊断（公式校验、states 存在性、结构打印）先于 PREREG 写入；均未影响任何阈值/档位/口径，已在 PREREG §7 与本报告披露 |
