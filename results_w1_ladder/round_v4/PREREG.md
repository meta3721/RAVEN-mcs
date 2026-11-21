# W1 round v4 预注册（PREREG）

```text
协议：raven-mcs-w1-round-v4-execution-prompt.md（sha256 cb8451d0…，180 行）
输入：results_w1_ladder/round_v3/ 及其文件；只读 artifacts/、round_v2/、round_v3/。
写入：results_w1_ladder/round_v4/ 与 scripts/w1_v4_*.py。不改 src/、论文、round_v2/v3。不提交、不推送。
Python：.venv_new\Scripts\python.exe。Part B 仅在用户明确回复"授权 Part B"后执行（本文件落盘时未授权）。
种子：调参半 30001–30010；报告半 30011–30020；**主判定只用全部 20 个种子**（协议 A1）。
本文件在任何 A1–A4 计算之前落盘，落盘后不得修改。
```

## 0. 沿用的 v3 结论（不重跑）

T1 递推精确（80/80，`max e_r = 0`）；T2 同尺审计与分解（SS 全 11 臂同尺，UA `fedavg_window` 同尺；FedAvg→RAVEN 差 68.96% (SS) / 83.07% (UA) 来自 FedAvg→均匀）；T3(SS) `B1 = Proj_{C_r}(β̂)` 最强、组项/方差/时滞/p/q/真值 p/q 均在 ±0.10 G 带内、去 ζ 代价 0.92 pp（下界 0.75 pp）；T7 逐窗 L1 在 `C_r` 上精确平坦（中位极差 ≈1e-13）。

## 1. A0.2 勘误（`ERRATA_v3.md`）

三条 v3 更正 + E7、E8，逐条给出 v3 原句位置与更正表述（见该文件）。

## 2. A1：无超参数规则用 20 个种子重评

**对象**：T3 的 `B0`–`B3` × 全部 src；`uniform`；v2 的 `L5`、`L6`（冻结 λ，注明 β̂ 源 = `raven_wo_use`）；冻结臂 `raven`、`inst_cal`、`fedavg_window`。
**每组三块**：全部 20 种子、调参半、报告半；每块给 `Δ_group`、`Δ_c-s`、pp，以及配对差的 bootstrap 95% 区间（10 000 次，种子 `20261002`）。
**主判定**：只用 20 个种子；v3 T6 的 G 单位 + pp（0.5 pp）双线在 20 种子上重做，与 v3 报告半结果并排。
**`split_unstable`**：某对比的两个半的 pp 点估计符号相反，或一半的区间跨 0 而另一半不跨 → 标记。
**输出**：`FULL_SEED_LADDER.csv`、`FULL_SEED_DECISIONS.csv`。
**停止规则**：任何回放与 v3 同源值差 > 1e-9 → 停整轮。

## 3. A2：T5 修复与延伸（探索性）

1. **共用投影** `proj_Cr(β, K)`：B1 与 T5 调用**同一函数**。实现取协议给的第二方案：cvxpy + CLARABEL，容差 `1e-10`。
   **门**：`κ = 0` 与 B1 的 α L∞ 差 ≤ 1e-8，且两个端点之差 ≤ 1e-9；不通过停 A2。
2. **分数据集**：选择、报告、曲线全部按数据集分开，**禁止跨数据集平均**。
3. **κ 网格**：`{0, 1, 3, 10, 30, 100, 300, 1000, 3000, 1e4, 3e4, 1e5}`。
   **收敛判据**：调参种子上最后两个相邻点的 `Δ_group` 变化 < 该数据集可关差距 `(Δ_unif − Δ*)` 的 1%；未收敛写"未收敛"，不外推。
4. **绑定诊断**（删除 v3 的 `max_alpha`/`min_ess`）：只统计 `K ≥ 2` 的窗口，给 `frac_cap_bind`（某坐标达 `ᾱ`）、`frac_l2_bind`（`‖α‖²` 达 `1/Ē`）、`frac_vertex`（仅一个非零坐标）。最优 κ 下 `frac_vertex > 50%` → 报告"强 debt 把聚合推向单客户端"。
5. **两个端点**分别选 κ，另给按 `Δ_group + Δ_c-s` 选的 κ。
**输出**：`DEBT_STRENGTH_V4.csv`、`DEBT_STRENGTH_V4.json`。

## 4. A3：T4 大 ε 重解

目标改写为 `(1/ε)·½‖Mα − μ‖² + ½‖α − β̂‖²`（与原问题同 argmin），`ε ∈ {10, 30, 100, 1000}`，`ε = ∞` 端点用 `proj_Cr` 结果。
**门**：`ε = 1000` 与 `ε = ∞` 的 `Δ_group` 差 < 1e-4。**输出**：`GRID_EXTENSION_V4.csv`。

## 5. A4：A 部分结论（`PART_A_REPORT.md`）

逐条回答协议 A4 的 4 问（对比 1 与 2 的 pp/区间/G 判定/实践线/`split_unstable`；SS 的 ζ 是否仍过实践线、UA 写"同活跃集上不可识别"；A2 的收敛性/最优 κ/两端点方向/`frac_vertex`；据此给出 Part B 的臂集合）。
**停止规则**：A2 投影门不过 → 停 A2，A1 与 A3 照做；A1 回放差 > 1e-9 → 停整轮。

## 6. Part B（**待授权，未执行**）

三臂 `uniform_window` / `proj_beta` / `proj_beta_debt`（policy 与 `raven` 相同，仅换服务器权重；debt 用 `η = 0.01` 递推）；驱动 `scripts/run_h_headroom.run_arm("C0_frozen", ds, arm, seed, tag=…)`，`h.OUT = results_w1_ladder/round_v4/train`；门 B-G0（先复跑冻结 `raven` 2 个种子，`RMSE_mu`/`Delta_group`/`Delta_c_s` 差 ≤ 1e-12）、B-G1（`active_clients` 逐窗同 `R_on`）、B-G2（`uniform_window`/`proj_beta` 的结构端点等于 A1 同种子回放值 ≤ 1e-9）、B-G3（`proj_beta_debt` 等于 A2 同 κ 回放值 ≤ 1e-9）；规模 3 臂 × 2 数据集 × 20 种子 + 2 门 run（≈45 min；若只两臂 ≈30 min）。
臂集合由 A4 决定：A2 未收敛或 `frac_vertex > 50%` → 只训 `uniform_window` 与 `proj_beta`；否则加 `proj_beta_debt`（κ 取 A2 调参种子按 `Δ_group` 选值）。
**输出**：`PART_B_REPORT.md`、`TRADEOFF.csv`（列：`RMSE_μ`、WorstGroupRMSE、Tail RMSE、`Δ_group`、`Δ_c-s`（pp 与相对 `Δ*` 的剩余 pp）、每 run 墙钟、每窗口求解耗时中位数；配对对比 5 条，家族 = 每数据集 × 5 端点，bootstrap + Wilcoxon + Holm）。

## 7. 禁止写的结论

- 任何跨数据集平均的数字（v3 的 T5 池化读数即因此被撤）。
- 把 A2 或 `proj_beta_debt` 写成冻结 RAVEN 的性能（后者是新规则）。
- Part B 中写"预测更优"，除非配对区间完全在有利一侧且 Holm 显著，且同时引用 §VII-F 上限测量。
- 用报告半或调参半替代 20 种子的主判定。
- U-Air 上关于 ζ 作用的任何数字（不可识别）。
- 引用 `Δ*` 不加"同活跃集、同 `M_r`、同 `C_r`、事先知道全部窗口"限定。
