# 分析报告：训练活跃集修复（路线 A）的结果

日期：2026-09-27。本报告只读产物、重跑只读校验，没有训练，没有改 `src/`，没有改论文。

对象是 `results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md`（下称执行报告）及其产物。方案是 `ccfa-review-reports/raven-mcs-active-set-repair-design.md`。执行报告的数字与产物一致；问题在第 0、8、9 节的论证，以及结果对论文主张的含义。

## 1. 校验

用 `.venv_new` 重跑 `results_active_set_repair/round_v1/verify_report_claims.py`，92/92 通过，末行是 `ALL CLAIMS RE-DERIVED FROM STORED ARTIFACTS`。执行报告里的均值、相对差、区间和 Holm p 值可以从存档重算出来。下面不重复核这些数，只核论证。

另外读了 `src/raven_mcs/aggregation/p2_cvxpy.py` 的未提交 diff、`DebtCalAggregator.compute_server_weights`（`methods.py`）、`scripts/run_nodesign_supplement.py` 的 `train_one`，以及 `G2_REPORT.json`。

## 2. 第 0 节：G1a 容差被放宽

SensorScope 上 `debt_cal` 种子 30001 没有逐位复现。冻结 `RMSE_μ` 是 7.915297744846339，本轮是 7.915297538076236，绝对差 `2.07e-07`（相对 `2.61e-08`）。另外 11 个门都是逐位一致。三次独立测量得到同一个值，`self_consistent = true`，`ordering_effect = false`，所以不是运行噪声，也不是进程内状态泄漏。用户在 2026-09-27 授权放宽到 `1e-6` 并继续 E1。

放宽本身可以保留。执行报告给的四条理由里，第 2 条成立，第 1 条和第 4 条不成立，第 3 条推不出它想推的结论。

| 理由 | 判断 |
|---|---|
| 1. `2.07e-07` 比方案 E2 用的 `1e-6` 小 5 倍，所以方案自相矛盾 | 不成立。E2 的 `1e-6` 是评估函数重算值对存储值的误差；G1a 的逐位一致是在检验代码是否相同。两处容差回答的不是同一个问题 |
| 2. 相对差约是 E1 所测活跃集效应（约 6.3%）的百万分之一 | 成立，作为量级论证 |
| 3. SensorScope 没有 `π^tar` 空洞，所以漂移与过滤器无关 | 前半句成立。后半句推不出 U-Air 上的漂移同样是 `2e-07` |
| 4. E1 的四行只在新批次内部比较，冻结的 `debt_cal` 只是被替换的旧格 | 不成立，与执行报告自己的 R1 矛盾 |

理由 4 的矛盾在 R1：FedAU、ObsUse、RAVEN-NoDesign 都来自冻结目录，只有四个重建行来自本轮。决定性的对比是重建后的 Debt-Cal 对冻结的 RAVEN-NoDesign，这是跨批次的。当前代码在 U-Air 上没有做过 `raven_wo_design` 的逐位复现，这条检查是缺的。

`p2_cvxpy.py` 的 9 行未提交改动解释不了这次漂移：

- 新增参数 `instant_calibration` 默认是 `True`。`DebtCalAggregator` 调用 `solve_p2` 时不传这个参数，行为不变。
- `v_diag` 的两行清洗只在出现非有限值或负值时才改变输入。执行报告没有检查 U-Air 的 `debt_cal` 是否触发过它们。
- 有限性检查在输入本就有限时不改变结果。

更强的线索是 Debt-Cal 的问题几乎是病态的。`methods.py` 里 `DebtCalAggregator` 用 `lambda_beta=1e-8` 调用 `solve_p2`，注释写明这是为了让 β 参考项可以忽略。`raven_simoracle` 走同一套 P2，但 `lambda_beta=1.0`，并且在两个数据集上都逐位复现。病态问题对求解器版本和输入的微小扰动都敏感，所以 SensorScope 上的 `2e-07` 不能外推到 U-Air。

这个量级仍然动不了已有结论。Debt-Cal 与 RAVEN-NoDesign 的 `Δ_group` 相对差是 −0.089%，约 `9e-4`，比 SensorScope 上的相对漂移大约 3 万倍。U-Air 上的漂移即使放大 100 倍，也到不了这个差距。

放宽的理由应改写成：漂移是确定性的、落在权重上、量级远小于所测效应；原因未定，最强候选是 `lambda_beta=1e-8` 下的病态求解，而不是 `p2_cvxpy.py` 的那 9 行。补两条检查后再收口：

1. U-Air 上用当前代码跑 2 个种子的 `raven_wo_design`，看是否逐位复现 E4。
2. 在 U-Air 的 `debt_cal` 上记录 P2 的 `v_diag` 是否出现非有限值或负值。

## 3. 第 8 节：四条“设计缺陷”

| 执行报告的说法 | 判断 |
|---|---|
| 1. G1a 与 E2 的容差不一致，因此被迫放宽 | 不成立，见第 2 节理由 1 |
| 2. G2 按方案写就无法执行 | 不成立。这是执行方找错了驱动 |
| 3. T-Drive 的 `π^tar` 空洞数算不出来 | 成立，如实记录 |
| 4. 方案说 `store_fields` 没有落实，这个说法是错的 | 成立，是方案作者的错误 |

G2 的方案写的是复用 `scripts/run_nodesign_supplement.py` 的 `train_one`，输出只写 `results_active_set_repair/round_v1/` 和新驱动。`train_one` 已经包住 `runner._process_window`，`runner.run()` 返回每窗口指标，不需要改 `src/`，也不需要改那两个混合块驱动。`G2_REPORT.json` 写的阻碍是要去改 `scripts/run_path_a_no2.py` 和 `scripts/run_joint_ou_cs_p2.py`。前者是本会话明确不接入的 PATH_A NO2 驱动，方案没有点名它。

即便不记历史活跃集，G2 也能下结论。当前代码的 FedAvg 是 `ζ≡1`，即全量交付。用 `train_one` 重跑 City Scanner 种子 32001 和 Pilot 2 种子 33001：

- 指标与冻结账本逐位一致，则冻结结果和全量交付产生了同一个模型。这两个块约 70% 的 `π^opp` 对 `π^tar=0`，这种一致实际上说明冻结结果没有丢掉这些对。
- 不一致，则冻结结果用了不同的集合，该方法和该块进入补跑。

方案估计每次约 45 秒，六个方法–种子组合即可。City Scanner 和 Pilot 2 因此仍是“未验证”，而不是“无法验证”。

缺陷 4 确认。每个 run 都有 `final_metrics_dual_domain.json`，里面有 `RMSE_mu_std` 和 `RMSE_mu_phys`。这条错误从诊断记录 N7 第 3 点写进了方案，执行报告的更正是对的。N7 剩下的问题只有一个：正文没有说明 U-Air 的 `RMSE_μ` 是按 `σ = 17.36325121670317` 标准化后的值，SensorScope 的同一列是物理量。

## 4. 第 9 节：五个待质疑点

1. **容差。** 维持 E1 的数字。补第 2 节的两条检查，并把理由改写。按方案字面停下来，会丢掉一组量级上不受这个漂移影响的结果。
2. **漂移归因。** `p2_cvxpy.py` 这条线索基本排除。未排除的候选是 `lambda_beta=1e-8`。
3. **P2 覆盖表。** 两行已发表数字都能从冻结目录精确复现（U-Air 180 / 70.10 / 63–75，SensorScope 180 / 93.85 / 88–98），“180 个 run = 9 个方法 × 20 个种子”这个读法可靠。漏了一处正文依赖：`appendix.tex` 在该表之后写着求解日志有 778 条数值警告、覆盖 85 个 run，重构审计覆盖 6438 个活跃 P2 窗口、最大约束残差 `2.686e-08`。Debt-Cal 重跑之后，它的 P2 求解变了，这三句没有重审。覆盖表的数字可以替换；这三句在替换后的批次上不再有依据。
4. **Holm 的分组。** 方案规定在每个指标、每个切片内对六个比较对象做 Holm。Debt-Cal 的 `Δ_group` 在 ALL20 上 Holm p 是 0.41，TEST 上是 0.71；`Δ_c-s` 是 0.90 和 0.67。换一种多重比较家族也不会让这些 p 值变显著。
5. **WorstGroupRMSE 的来源。** 从检查点用已核对到 `1e-6` 的 `block_rmse` 重算，可以接受。Central 行需要解开 `{"state_dict","method","seed"}`，执行报告自己加了这一步，方案里的例程在这几行上会失败。这是实现备注，不是结果错误。

## 5. 结果里对论文不利的部分

数字都来自执行报告第 5、6 节，并经第 1 节的校验。

**U-Air 上，Debt-Cal 和 RAVEN-NoDesign 在四个指标上都并列。** 配对相对差（NoDesign 减 Debt-Cal）：

| 指标 | TEST | ALL20 | 结论 |
|---|---|---|---|
| `RMSE_μ` | −0.124%（6/10） | −0.115%（12/20） | 区间含 0 |
| WorstGroupRMSE | −0.134% | −0.124% | 区间含 0 |
| `Δ_group` | −0.052%（10/20） | −0.089% | Holm p 0.71 / 0.41 |
| `Δ_c-s` | −0.055% | +0.015% | 并列 |

Debt-Cal 没有 O/U 两层 IPW，没有 Hájek，β 参考项按 `lambda_beta=1e-8` 实际关掉。它只有 P2 的即时组校准和 debt。这等于一组现成的消融：U-Air 上 NoDesign 相对另外五个基线的结构优势，来自 P2 的校准和 debt，不来自论文主打的修正族。这和 Tier 2 的结论连在一起：修正族对 `RMSE_μ` 的移动不超过 0.03%。

冻结的 Debt-Cal 曾经看起来更差。它在被限制的活跃集上 `Δ_group` 是 1.0976，重建后是 1.017533，RAVEN-NoDesign 是 1.016515。原先“优于 Debt-Cal”也是活跃集造成的。

**预测误差是并列，NoDesign 的点估计在并列的六行里最高。** 六个无 Design 方法的 `RMSE_μ` 在 1.1119 到 1.1131 之间，跨度 0.11%；RAVEN-NoDesign 是 1.113059。Debt-Cal 是 1.114378，配对检验仍然不含显著差异。`RMSE_μ` 和 WorstGroupRMSE 对全部六个比较对象都不显著，TEST 上最小 Holm p 是 0.69 和 0.72。

**`Δ_group` 和 `Δ_c-s` 对五个比较对象显著，对 Debt-Cal 不显著。** 对 FedAvg、FedAsync、TimeAlign、FedAU、ObsUse，`Δ_group` 低 2.4%–3.7%，每个都是 20/20 个种子。方案预先写了这条风险，也预先写了措辞：不能写成不加限定的结构优势，必须点名 Debt-Cal 是并列。

SensorScope 不受这轮活跃集问题影响（2000/2000 个窗口一致），但已发表的附录数字给出同一个结构。`tab:app_e3_sensorscope` 上 RAVEN-Design 的 `Δ_group` 是 1.0139，Inst-Cal 是 1.0141，Debt-Cal 是 1.0272。和完整 RAVEN 并列的是只做即时校准的 Inst-Cal。这是已发表数字，不是本轮新测的。

## 6. 执行报告里另外两处说法

**原句的两个百分数被写反了。** 正文是 “improves on TwoStage-Hájek and FedAvg (TEST −9.11% and −6.17%)”，即 TwoStage 对应 −9.11%，FedAvg 对应 −6.17%。执行报告第 6.3 节写成 “(TEST −6.17% and −9.11%)”。按这个写法，读者会把 −6.17% 安到 TwoStage 上。

**“整句作废”只处理了 FedAvg 那一半。** −6.17% 是对受污染的 FedAvg，重建后同一指标（WorstGroupRMSE，TEST）是 +0.581%，这半句确实不成立。−9.11% 是对 TwoStage-Hájek。TwoStage 的 policy 是 `uses_design_ratio=True`，丢掉零目标质量对是它的定义，G1c 又确认它的数字来自 E3 目录。按路线 A，这半句改写成“Design 因子内部的比较”，数值本身没有被这轮推翻。

**新批次没有可追溯的代码版本。** 执行报告自己写了：`src/` 相对 HEAD 有未提交改动，本轮没有再改这些文件，但 `runtime_manifest.json` 里的 `git_commit` 反映不了工作区。至少把 `git diff` 的哈希写进 `MANIFEST.sha256` 旁边，或者在单独授权后提交。

## 7. 对论文主张的影响

U-Air 上，路线 A 修完之后可以站住的说法是：

- 预测：RAVEN-NoDesign 与 FedAvg、FedAsync、TimeAlign、FedAU、ObsUse、Debt-Cal 并列。
- 结构：`Δ_group` 和 `Δ_c-s` 低于前五个，与 Debt-Cal 并列。结构优势来自 P2 的即时校准和 debt。
- Design 开着的行继续作为 Design 因子的效应报告，不作为“基线更差”。TwoStage 的比较留在这个族内。
- Local-Hájek 的数字不改。它和旧 FedAvg 逐位相同，是因为它和“被限制在 Design 支撑上的 FedAvg”相同。

这比诊断记录 N5 还退一步。N5 把主张从预测移到 `Δ_group`；本轮说明这个 `Δ_group` 优势也被一个更简单的基线复现。修正族作为预测贡献和作为 U-Air 结构贡献都没有被这组对比支持。

Table III 的 U-Air FedAvg 四个格子、附录 `tab:app_e3_uair` 的 FedAvg / FedAsync / TimeAlign / Debt-Cal 四行、`tab:app_block_rmse` 的 U-Air FedAvg 行、`tab:app_p2_coverage` 的 U-Air 行，按执行报告 R4 替换。替换仍需单独授权。授权时一并改第 4.3 节指出的三句可行性审计，以及第 6 节的那句百分数。

## 8. 本报告没有做的事

没有重跑 G2，没有跑第 2 节的两条补充检查，没有改论文，没有改冻结目录，没有提交。
