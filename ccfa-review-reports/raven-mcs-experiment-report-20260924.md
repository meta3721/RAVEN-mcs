# 实验报告：NoDesign 统一主设置、校正空间 H、Table II 的 U-Air FedAvg 格

日期：2026-09-24。正文与已冻结结果目录均未改写。

本报告覆盖同一轮里的三件实验：补齐 City Scanner 与 Pilot 2 的 RAVEN-NoDesign；测量校正族在加强条件下的预测空间 H；核实 Table II 里 U-Air 的 FedAvg-Window 格。后两件是在前一件的复现检查中发现的。

## 1. 目的

论文删掉 \(\phi\) 之后，不再回答每个块为什么报告 Design 或 NoDesign。同时，已发表产物里整条倾向校正路径对 \(\mathrm{RMSE}_\mu\) 的移动都在 \(\pm 0.03\%\) 以内。本轮要回答两件事：

1. 若规定所有块都以 RAVEN-NoDesign 为主行、RAVEN-Design 为次行，City Scanner 与 Pilot 2 上缺的 NoDesign 行是什么。
2. \(\pm 0.03\%\) 是估计器没做好，还是这些协议下重加权本来就几乎不能移动 \(\mathrm{RMSE}_\mu\)。用 oracle 校正相对不加权 FedAvg 的相对差 \(H\) 来区分。

第三件是过程中发现的：U-Air 上 2026-08-11 冻结的 FedAvg-Window 会丢掉 \(\pi^{\mathrm{tar}}=0\) 的客户端，Table II 里“NoDesign 相对 FedAvg 改善约 6%”这一比较因此不成立。

## 2. 方案

### 2.1 NoDesign 补行

| 块 | 种子 | 窗口 | 主行 | 对照 |
|---|---|---|---|---|
| City Scanner 到访占用 | 32001–32010 | 100 | `raven_wo_design` | 已冻结的 FedAvg、TwoStage-Hájek、FedAU、ObsUse、RAVEN-Design |
| Pilot 2 实测 \(O\) | 33001–33010 | 100 | `raven_wo_design` | 同上 |

规则在跑之前定下：NoDesign 是主行，不因结果改回 Design。每个块先重跑一个已冻结的 RAVEN-Design 种子，\(\mathrm{RMSE}_\mu\) 容差 \(10^{-9}\)，通过后才训练新行。输出只写 `results_nodesign_supplement/`。

City Scanner 原驱动 `scripts/run_c1_cityscanner.py` 已被截成 2 字节且不在 git 中。训练阶段按 Pilot 2 驱动 `scripts/run_joint_ou_cs_p2.py` 重建为 `scripts/run_nodesign_supplement.py`，使用同一批冻结 EventTrace。

### 2.2 H（预注册）

预注册文件：`ccfa-review-reports/raven-mcs-h-headroom-preregistration.md`。写入时尚未生成任何压力条件的 trace 或 RMSE。

\[
H_{c,b,s}=\frac{\mathrm{RMSE}_\mu(\mathrm{FedAvg})-\mathrm{RMSE}_\mu(\text{较好的 oracle})}{\mathrm{RMSE}_\mu(\mathrm{FedAvg})}
\]

较好的 oracle 按该条件、该数据块上 5 个种子的均值选定，所有种子用同一个臂。两个 oracle 臂是：

- RAVEN-SimOracle：真 \(p\)、真 \(q\)，Design 开。
- RAVEN-SimOracle-NoDesign：真 \(p\)、真 \(q\)，\(\zeta\equiv 1\)。只在驱动内注册，不改 `src/`。

条件（一次只动一个旋钮，外加一个组合）：

| 条件 | 机会倾斜 \(\theta\) | 尾时段观测缩放 | 骨干 | 目标 |
|---|---|---|---|---|
| C0 冻结 | 1.25 | 0.55 | CommonNDMF | 测试份额 \(\mu\) |
| C1 强倾斜 | 2.5 | 0.25 | CommonNDMF | 测试份额 |
| C2 极端倾斜 | 4.0 | 0.10 | CommonNDMF | 测试份额 |
| C3 低容量 | 1.25 | 0.55 | 去日周期 CommonNDMF | 测试份额 |
| C4 时段均衡 | 1.25 | 0.55 | CommonNDMF | 四时段各 1/4 的 \(\mu'\) |
| C5 组合 | 4.0 | 0.10 | 去日周期 | \(\mu'\) |

数据块：SensorScope、U-Air。种子：30001–30005。C0 复用冻结 E3 trace；C1、C2、C5 用同一 R3 生成器重生成。

**GO：** 某个 \(c\in\{\mathrm{C1},\ldots,\mathrm{C5}\}\) 且某个数据块上，\(H\ge 0.5\%\) 且 95% 置信区间下界 \(>0\)。否则 **STOP**，不跑第 2 阶段的方法比较。0.5% 不因结果调整。

门槛检查后、任何压力条件之前做了修订 1：U-Air 的 FedAvg 格记为已知不可复现；trace 比较忽略后来生成器多写的三个元数据键；增加 NoDesign oracle，并单独报告 Design 支撑代价 \((\mathrm{RMSE}_{O,\mathrm{design}}-\mathrm{RMSE}_{O,\mathrm{nodesign}})/\mathrm{RMSE}_{O,\mathrm{nodesign}}\)。

### 2.3 Table II 审计

只重跑受影响的格：U-Air、FedAvg-Window、种子 30001–30020、当前 runner（保留全部已交付客户端）。WorstGroupRMSE 按 Table II 的四时段定义重算。先用冻结检查点核对算法与 `TABLE_II_WORSTGROUP_PER_SEED.csv` 一致（容差 \(10^{-6}\)），再训练。输出只写 `results_table2_audit/` 与 `results_h_headroom/round_v1/table2_audit/`。

## 3. 过程

1. City Scanner 与 Pilot 2 的复现门槛都通过：重跑冻结 RAVEN 的 canary 种子，\(\Delta\mathrm{RMSE}_\mu=0\)。随后各训练 10 个 NoDesign 种子。
2. H 的第一次门槛失败。RAVEN、TwoStage-Hájek、RAVEN-SimOracle 在 U-Air seed30001 上逐位复现；SensorScope 上 FedAvg 与 SimOracle 也逐位复现。只有 U-Air FedAvg 对不上：当前代码 1.1713，冻结值 1.2108。
3. 原因：2026-08-11 的 runner 把 \(\pi^{\mathrm{tar}}=0\) 的“客户端 \(\times\) stratum”从活跃集剔除，FedAvg 也不例外。U-Air 训练对里有 72/288 个这样的对；SensorScope 为 0/440，Traffic 为 0/344。第 0 窗口的 `client-005` 在冻结 FedAvg、RAVEN、TwoStage 中被剔除，在 2026-08-17 的 FedAU 与 ObsUse 中保留。后两者用当前代码逐位复现。产生冻结 E3 的那版 runner 从未提交，无法二分。
4. 按修订 1 重跑门槛，两块都通过。U-Air FedAvg 格标记为已知不可复现。
5. C5 首次崩溃：生成 trace 时误把“时段均衡目标”的注入打开，而该注入只在训练时有数据。修复后只重跑 C5。C0–C4 的已完成运行未重跑。
6. C3 的模型替换是生效的（客户端训练加载的是被替换后的 `DiurnalBlindNDMF`）。小时均值的离散只占目标标准差的一小部分（SensorScope 小时均值标准差 0.66，对目标标准差 3.37；U-Air 为 0.10 对 1.05），所以去掉小时特征几乎不改变 RMSE。C3 与 C5 里的容量旋钮在这两份数据上没有力度。
7. 12 个 H 单元格全部完成后写出 `H_DECISION.json`。Table II 审计在此之后单独跑完 20 个种子。

## 4. 结果

### 4.1 City Scanner：NoDesign 优于 Design，仍差于 FedAvg

10 个种子，\(\mathrm{RMSE}_\mu\) 均值：

| 方法 | \(\mathrm{RMSE}_\mu\) | WorstGroupRMSE |
|---|---|---|
| FedAvg-Window | 0.2379 | 0.2489 |
| RAVEN-NoDesign | 0.2463 | 0.2587 |
| TwoStage-Hájek | 0.2510 | 0.2629 |
| RAVEN-Design | 0.2549 | 0.2671 |
| ObsUse-Window | 0.2566 | 0.2685 |
| FedAU-Window | 0.2582 | 0.2700 |

NoDesign 相对 FedAU、ObsUse 的配对相对差约 \(-3.0\%\)、\(-2.6\%\)（10 种子中赢 8 个、7 个），但配对标准差约 10%，不能写成显著。相对 FedAvg 为 \(+3.3\%\)（赢 3/10）。FedAvg 仍是这一块最好的方法。

### 4.2 Pilot 2：NoDesign 是较差的一行

| 方法 | \(\mathrm{RMSE}_\mu\) | WorstGroupRMSE |
|---|---|---|
| TwoStage-Hájek | 0.7097 | 0.7273 |
| RAVEN-Design | 0.7135 | 0.7311 |
| FedAU-Window | 0.7173 | 0.7351 |
| ObsUse-Window | 0.7175 | 0.7352 |
| FedAvg-Window | 0.7182 | 0.7359 |
| RAVEN-NoDesign | 0.7204 | 0.7381 |

NoDesign 相对 FedAU、ObsUse 约 \(+0.5\%\)（各赢 5/10），相对 FedAvg 约 \(+0.3\%\)。Design 在 9/10 个种子上优于 NoDesign，配对相对差约 \(-0.95\%\)。Pilot 2 上没有 \(\pi^{\mathrm{tar}}=0\) 的训练对，Design 不丢数据。主行仍按事先规则记为 NoDesign。

### 4.3 H：判定 STOP

`results_h_headroom/round_v1/H_DECISION.json`：`decision=STOP`，`go_cells=[]`。12 个单元格都没有 \(H\ge 0.5\%\) 且置信区间下界 \(>0\)。第 2 阶段不执行。

| 条件 | SensorScope \(H\) [95% CI] | U-Air \(H\) [95% CI] | U-Air Design 支撑代价 |
|---|---|---|---|
| C0 | +0.02% [−0.09, +0.13] | +0.22% [−1.18, +1.63] | +7.03% |
| C1 | −0.03% [−0.13, +0.08] | +0.77% [−0.26, +1.80] | +8.76% |
| C2 | +0.07% [−0.11, +0.26] | −0.07% [−1.46, +1.31] | +6.07% |
| C3 | +0.03% [−0.08, +0.13] | +0.24% [−1.19, +1.67] | +7.01% |
| C4 | +0.02% [−0.09, +0.14] | +0.22% [−1.18, +1.63] | +7.07% |
| C5 | +0.08% [−0.12, +0.27] | −0.09% [−1.47, +1.28] | +5.98% |

U-Air 上六个条件的 Design 支撑代价置信区间下界都大于 0（+0.5% 到 +6.5%）。SensorScope 上该代价约为 0。U-Air 上均值更好的 oracle 在全部条件下都是不带 Design 的那一臂。

最接近 GO 的是 U-Air C1 的 +0.77%，置信区间包含 0。

C3 的 RMSE 与 C0 几乎相同（U-Air FedAvg 1.0907 对 1.0903；SensorScope 7.9096 对 7.9089）。这只说明“去掉小时特征”在这两份数据上不是有效的设定错误，不能写成“低容量下也没有空间”。

### 4.4 Table II：U-Air FedAvg 应使用全量交付的重跑

20 个种子。冻结 FedAvg 的逐种子重算均值是 1.1923；正文 Table II 印的是 1.1882，两者相差约 0.35%，来自存储值与重算值，不是本轮新跑引入的。

| 方法 | \(\mathrm{RMSE}_\mu\) | WorstGroupRMSE | \(\Delta_{\mathrm{group}}\) | \(\Delta_{c\text{-}s}\) |
|---|---|---|---|---|
| FedAvg（冻结，带过滤） | 1.1923 \(\pm\) 0.0629 | 1.2596 | 1.1218（正文） | 1.2621（正文） |
| FedAvg（当前，全量交付） | 1.1119 \(\pm\) 0.0603 | 1.1690 \(\pm\) 0.0692 | 1.0446 \(\pm\) 0.0397 | 1.3138 \(\pm\) 0.0337 |
| FedAU-Window | 1.1128 | 1.1701 | 1.0557 | 1.3291 |
| ObsUse-Window | 1.1120 | 1.1692 | 1.0413 | 1.3235 |
| RAVEN-NoDesign | 1.1131 | 1.1703 | 1.0165 | 1.2949 |
| RAVEN-Design | 1.1954 | 1.2630 | 1.0924 | 1.2334 |
| TwoStage-Hájek | 1.2202 | 1.2907 | — | — |
| Local-Hájek | 1.1923 | 1.2596 | — | — |

Local-Hájek 的逐种子值与冻结 FedAvg 完全相同，因此带有同一种过滤。FedAU 与 ObsUse 的冻结行用当前代码逐位复现，不受影响。

RAVEN-NoDesign 相对**冻结** FedAvg：20 种子 \(\mathrm{RMSE}_\mu\) 配对相对差 \(-6.62\%\)（赢 19/20）；TEST 种子 \(-5.80\%\)。这就是正文里约 \(-6.17\%\) 的来源。

RAVEN-NoDesign 相对**当前** FedAvg：20 种子 \(+0.09\%\)（赢 7/20）；TEST 种子 \(+0.55\%\)（赢 3/10）。FedAU、ObsUse 相对当前 FedAvg 都在 \(\pm 0.15\%\) 以内。正文“NoDesign improves on FedAvg (TEST \(-6.17\%\))”在全量交付的 FedAvg 上不成立。NoDesign 相对这四个方法仍有的差别在 \(\Delta_{\mathrm{group}}\)（1.0165，对当前 FedAvg 的 1.0446）。

## 5. 结论

- 校正族在这些协议上移动 \(\mathrm{RMSE}_\mu\) 的空间，在加强倾斜、改目标之后仍然小于预注册的 0.5% 门槛。\(\pm 0.03\%\) 是空间上限，不是某一条估计器没调好。
- U-Air 上稳定的效应是 Design 丢掉零目标质量训练对，代价约 6%–9%。这解释了 NoDesign 在 U-Air、City Scanner 上更好，在支撑完整的 Pilot 2 上更差。
- Table II 的 U-Air FedAvg 格（以及补充材料里与之重合的 Local-Hájek）使用了被削弱的 FedAvg。换成全量交付后，NoDesign、FedAU、ObsUse 与 FedAvg 在预测上并列。
- 第 2 阶段方法比较按预注册不执行。正文尚未修改。

## 6. 产物

| 路径 | 内容 |
|---|---|
| `scripts/run_nodesign_supplement.py` | NoDesign 补行驱动 |
| `results_nodesign_supplement/round_v1/tables/` | City Scanner、Pilot 2 的种子行、汇总、配对 |
| `scripts/run_h_headroom.py` | H 驱动 |
| `results_h_headroom/round_v1/` | 门槛、运行、`tables/H_summary.csv`、`H_DECISION.json` |
| `ccfa-review-reports/raven-mcs-h-headroom-preregistration.md` | 预注册、修订 1、STOP 记录 |
| `scripts/audit_table2_uair_fedavg.py` | Table II 审计 |
| `results_table2_audit/` | 当前 FedAvg 的 20 种子与配对 |
