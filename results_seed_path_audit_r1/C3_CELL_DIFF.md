# 第 1 步：受影响印刷单元格的逐格 diff 清单（重采源到 θ 口径）

审计背景：U-Air 的 E3/E4 树在种子 **30007 / 30016 / 30018** 的最后一个窗口不聚合（`window_id=79, active=False, a_r_size=0`），
运行期 `RMSE_mu` 因此取的是**内存镜像**的值；θ 副本（= 落盘 checkpoint 重新前向）才是论文口径。
本清单给出**每一个印刷数字**的旧值 → 新值，以及**不需要改**的单元格及其证据。

- 采样范围：20 seeds × 受影响臂；其中只有这 3 个种子需要换值，其余 17 个两口径完全相同 → 修正均值 = (17 个冻结值 + 3 个 θ 值)/20
- 预测类指标（`RMSE_μ`、Tail RMSE、每块 RMSE、`WorstGroupRMSE`）可能受影响；结构类（`Δ_group`、`Δ_c-s`）与模型无关
- 复现脚本（只读，全部在 `results_seed_path_audit_r1/`）：`c_impact_recalc.py`、`c3_cell_diff.py`、`c4_t4_stats.py`、`c5_w1_recompute.py`、`c6_wg_relatives.py`
  → 产物 `C_IMPACT_RECALC.csv/.json`、`C3_CELL_DIFF.csv/.json`、`C4_T4_STATS.csv`

一句话结论：**7 个表格格 + 6 个 Table IV 格 + 5 处正文数字 + 1 个图数据文件（2 列）/ 3 个 PDF** 需要更新；
`WorstGroupRMSE` 列、`Δ` 列、per-block 表、以及 NoDesign/FedAU/ObsUse/FedAvg 行**本来就是 θ 口径**，不动。

---

## 1. 表格单元格：需要替换（7 格，全部只动 `RMSE_μ` 列）

| 文件:行 | 表 | 行 | 列 | 旧值 | 新值 | 旧 ± | 新 ± | 判据 |
|---|---|---|---|---|---|---|---|---|
| main.tex:1895 | 表 III (U-Air) | TwoStage-Hájek | `RMSE_μ` | 1.2160 | **1.2202** | ±0.0716 | ±0.0672 | 印刷值 = 镜像 |
| main.tex:1898 | 表 III (U-Air) | **RAVEN-Design** | `RMSE_μ` | 1.1911 | **1.1954** | ±0.0659 | ±0.0635 | 印刷值 = 镜像 |
| appendix.tex:1880 | `tab:app_e3_uair` | Local-Hájek | `RMSE_μ` | 1.1882 | **1.1923** | ±0.0649 | ±0.0629 | 印刷值 = 镜像 |
| appendix.tex:1881 | `tab:app_e3_uair` | TwoStage-Hájek | `RMSE_μ` | 1.2160 | **1.2202** | ±0.0716 | ±0.0672 | 印刷值 = 镜像 |
| appendix.tex:1882 | `tab:app_e3_uair` | Inst-Cal | `RMSE_μ` | 1.1911 | **1.1954** | ±0.0659 | ±0.0635 | 印刷值 = 镜像 |
| appendix.tex:1884 | `tab:app_e3_uair` | RAVEN-Design | `RMSE_μ` | 1.1911 | **1.1954** | ±0.0659 | ±0.0635 | 印刷值 = 镜像 |
| appendix.tex:1885 | `tab:app_e3_uair` | RAVEN-SimOracle | `RMSE_μ` | 1.1914 | **1.1958** | ±0.0654 | ±0.0630 | 印刷值 = 镜像 |

同表其余行**保留**（已核验为 θ 口径或不受影响）：表 III 的 U-Air FedAvg 1.1119 / FedAU 1.1128 / ObsUse 1.1120 / RAVEN-NoDesign 1.1131；
附录的 FedAvg 1.1119 / FedAsync 1.1119 / TimeAlign 1.1120 / Debt-Cal 1.1144 / RAVEN-NoDesign 1.1131；两表的 SensorScope 全体（无复制块）。

## 2. 表格单元格：核验后**不需要改**

| 列 / 表 | 为什么不动 | 证据 |
|---|---|---|
| 表 III + 附录 per-block 表的 `WorstGroupRMSE` 列（1.2630 / 1.2907 / 1.1703 …） | 印刷值**已经是 θ 口径**：θ 的 20-seed WG 均值 = 1.2630 与印刷值一致；若按镜像重算会低约 0.0075 | `C3_CELL_DIFF.csv` 全部判为 `theta (keep)`；E2 的 `WorstGroupRMSE_std` 列逐种子重估 |
| 附录 `tab:app_block_rmse` U-Air 六行的 g0–g3 | 每块 RMSE 全部 = E2 θ 值 | 24 个格子全部 `theta (keep)` |
| 所有 `Δ_group` / `Δ_c-s` 列与百分比（6.943、4.990 等） | 结构指标与模型无关 | `C4_T4_STATS.csv`：用树值重算的 20 个百分比与印刷值 **bit-identical**（−6.943368…、+4.989835…） |
| §V 的 2.46%（main.tex:1836） | 分母取 TwoStage 的 WG（两者都是 θ）：θ 重算 = 2.4578% ≈ 2.46%，10/10 胜 | `c6_wg_relatives.py` |
| §V 的 +0.48% / +0.44%、+0.002% / +0.075%（main.tex:1828, 1830） | 这几格是 **RAVEN-NoDesign**（干净臂）对 FedAU/ObsUse：θ 重算 +0.478/+0.443 与 +0.002/+0.075 ✓ | `c6_wg_relatives.py` |
| 表 III 题注 +7.9% / +8.0%（main.tex:1874，X-3 修复） | 由 θ 的 WG 计算：+7.9443% / +8.0240% ✓ 不变 | `c3_cell_diff.py` derived |
| §VII-F 的 e_ref 0.077 / 1.15 | 由事件轨迹与权重构造，与预测无关 | `CALIBRATION_ABSORPTION.json` 输入不含模型输出 |
| SensorScope 全部数字 | SensorScope 树无复制块（0/323 run 触发） | `A1_INACTIVE_FINAL_SWEEP.csv` |

## 3. Table IV（`tab:e4_ablation`，U-Air 五行 × 4 指标 = 20 格）

| 行 | 指标 | 旧（印刷） | 新（θ） | 变化 | Holm p |
|---|---|---|---|---|---|
| Design | `RMSE_μ` | −6.553 | **−6.885** | 是 | 9.5e−6 ✓ 显著不变 |
| Design | Tail RMSE | −6.875 | **−7.221** | 是 | 9.5e−6 ✓ |
| Use | `RMSE_μ` | +0.024 | **+0.025** | 是（第 3 位） | 0.883 ✗ |
| Use | Tail RMSE | +0.025 | **+0.026** | 是（第 3 位） | 0.883 ✗ |
| Inst | `RMSE_μ` | +0.131 | **+0.143** | 是 | 0.0194 ✓ 显著不变 |
| Inst | Tail RMSE | +0.136 | **+0.149** | 是 | 0.0194 ✓ |
| Obs | `RMSE_μ` / Tail | −0.010 / −0.010 | −0.0098 / −0.0103 | 否（3 位小数不变） | 1.0 ✗ |
| Debt | `RMSE_μ` / Tail | <0.001 / <0.001 | 0.00067 / 0.00072 | 否 | 1.0 ✗ |
| Design/Obs/Use/Inst/Debt | `Δ_group`、`Δ_c-s`（10 格） | — | — | **全部不变**（bit-identical） | 不变 |

Inst 行的来源（`e4_wo_inst_reference_penalty_final_correction_r1/final_corrective_runs`，generation 2）**同样带触发**（30007/30016/30018 末窗不聚合，本次新发现），其 θ 值：1.142423→1.189399、1.173732→1.158093、1.129598→1.186332。

## 4. 正文数字（5 处）

| 位置 | 旧 | 新 | 备注 |
|---|---|---|---|
| main.tex:1586–1588（§V） | 成本 6.553% / 尾 6.875% | **6.886% / 7.221%** | 6.943%、4.990% 不变 |
| main.tex:1866–1868（表 III 题注） | 同上 | **同上** | 与题注同步 |
| main.tex:2014–2015（§VII-E 段） | `RMSE_μ` 6.553% | **6.886%** | Δ_group 6.943% 不变 |
| main.tex:2047–2048（Inst 段） | 0.131% / 0.136% | **0.143% / 0.149%** | `p_Holm=0.0194` 不变 |
| main.tex:1820（§V） | Design-on `RMSE_μ` = 1.1911 | **1.1954** | 1.0924（Δ_group）不变 |
| main.tex:1911–1912（图题 fig:w1_design_gate） | RMSE "约 7.1%" | **"约 7.5%"** | Δ_group "约 7.5%" 不变；main.tex:1822 的"约 7%"仍成立 |

## 5. 图与图数据（口径已核对）

| 文件 | 单元格 | 旧 | 新 |
|---|---|---|---|
| `figure_data/FIG_W1_DESIGN_GATE.csv` | U-Air / Estimated / `RMSE_mu_pct` | 7.07231 | **7.4565** |
| 同上 | U-Air / Oracle / `RMSE_mu_pct` | 7.10791 | **7.5045** |
| 同上 | 两行 `Delta_group_pct` | 7.49898 / 7.47623 | **不变**（口径 = 逐种子相对平均，已用同口径核对 ✓） |
| `figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv` | U-Air 5 组件 × {`RMSE_mu`, `Tail_RMSE`} 的 `relative_change_percent`、`paired_mean_difference`、`Holm_p`、`direction`、`qualitative_magnitude` | 见第 3 节 | 见第 3 节 |

需要重生成的图（`make_figures.py` 从 `figure_data/` 读取）：`figures/fig_w1_design_gate.pdf`、
`figures/fig5_e4_component_ablation.pdf`（附录 Fig. `fig:e4_ablation`）、`figures/fig6_e4_uair_excl_design.pdf`（附录 Fig. `fig:uair_excl_design`）及对应 `.png`；
**实施时另发现** `figure_data/FIG_E3_E3_PREDICTION_RISK.csv`（fig4 的数据源）同样是镜像口径，见第 8 节。

## 6. 本步新发现的额外受影响范围（需你决定是否一并处理）

1. **gen-2 w/o-Inst 校正跑**（Table IV Inst 行来源）也带触发 → 已并入第 3 节处理。
2. **H headroom 的 U-Air `raven_simoracle` 跑**：`results_h_headroom/round_u1/runs/` 中 C0_frozen（3 个）、C1_tilt_strong（30014）、C3_low_capacity（3 个）、C4_block_uniform（3 个）共 **10 个 run** 的末窗不聚合 → §VII-F 引用的 H 事实（`|H| ≤ 0.217%`、区间、可检测效应 0.70–0.80）来自这些 run-time 值；若要 θ 一致需同法重采源（只读重估 10 次）。
3. **§VII-F 的两个 U-Air 配对数字**来自冻结 E3 树（`results_ceiling_class_r1/compute_ceiling_class_paired.py`）：oracle-margin swap **+0.040%**、TwoStage-Hájek **2.04% [1.33, 2.75]** → 属镜像口径；可把该脚本改读 E2 的 θ 序列后重算（不新增训练）。
   （SensorScope 侧与 e_ref 不受影响。）

## 7. 授权请求

- (a) 应用第 1–5 节（7 个表格格 + 6 个 Table IV 格 + 5 处正文 + 图数据 2 列 + 3 个 PDF 重建），改后重编译 main/supplement 并核对页数与 0 error/0 undefined/0 overfull；
- (b) 第 6 节的第 2、3 项是否一并处理（都是只读重算，无新训练）；
- (c) 是否在补充材料加一句两口径的可复现性说明（镜像 vs θ）。

---

## 8. 应用记录（2026-09-29 已执行，(a) 项；诊断记录 §7 item 47）

第 1–5 节全部落地。实施中发现两处此前未列入清单的受影响对象，一并处理：

1. **`figure_data/FIG_E3_E3_PREDICTION_RISK.csv`（fig4 的数据源）也是镜像口径**：U-Air 九个受影响 E3 臂 × 三个种子都要换值。其中 FedAvg-Window、FedAsync-Window、TimeAlign-Agg、Debt-Cal 四个臂的 θ `Tail_RMSE` 此前无现成产物，已补测（`c7_e3_arms_theta.py` → `C7_E3_ARMS_THETA.csv`，12 次只读前向）。该文件另有 `MAE_mu` / `RMSE_rho` 两列仍是镜像值，但 fig4 不画这两列，按"不引入未经 θ 重算的数字"保留原值并在记录中披露。
2. **重建的是 4 个图而非 3 个**：`fig_w1_design_gate`、`fig4_e3_prediction_risk`、`fig5_e4_component_ablation`、`fig6_e4_uair_excl_design`（PDF+PNG）；其余 5 个 PDF 的字节变化只来自 matplotlib 写入的构建时间元数据（PNG 哈希证明内容未变）。

核验（成品级）：main **17 pp.**、supplement **16 pp.**、0 error、0 undefined、0 overfull；`main.tex` em dash 2/3、`appendix.tex` 0；`check_prose_quality.py` 无 hard failure；`tools/freeze_appendix_refs.py --check` = 0 to freeze / 0 unresolvable。用 `pdftotext` 在成品 PDF 中逐项确认新值已入版：正文 `1.1954`、题注 `6.886% / 7.221%`、表 III `1.2202±0.0672` 与 `1.1954±0.0635`（`1.2630` 不动）、Table IV `−7.221 / +0.026 / +0.143 / +0.149`、§VII-E 段 `0.143% / 0.149%`、附录五行 `1.1923 / 1.2202 / 1.1954 / 1.1954 / 1.1958`、图 4 题注与图中数值 `7.50 / 7.48 / 7.46 / 7.50`。

快照：`snapshots/2026-09-29-pre-theta-resource/`（两个 `.tex`、三个 CSV、四个 PDF）。

## 9. 残留两项复核结果（2026-09-29，X-4b 据此关闭；记录 §7 item 48）

**① H 网格（真实影响，但只落在诊断记录里）。** 触发的是 `round_u1` 的 **Design-on oracle**（`raven_simoracle`）：C0/C3/C4 各 30007/30016/30018、C1 的 30014，共 10 个 run。已按每个 run 自己的接线在 θ 处重估（`c9_h_theta_recheck.py`：C0/C1 用生产 target bundle，C4 用按 `run_h_headroom.block_uniform_target` 原样复建的 block-uniform override，C3 用 `DiurnalBlindNDMF`），逐 run 偏移为 +4.10% / −1.35% / +5.02% 量级；C0 三个值与 E3 树同 run 的 θ 值**逐位一致**（`1.189208 / 1.157351 / 1.185403`），构成接线自证。
**论文不受影响**：U-Air 所引 H 固定使用 Design-off oracle（`FREEZE_ARM_DATASET=uair`），这 10 个 run 不进入该列，六个 `H_RMSE_mu` 单元修正后 bit-identical → §VII-F 的 `\|H\| ≤ 0.217%`、区间与 MDE 全部成立。修正只落在**记录的 §3A H4 表**：C0/C1/C3/C4 的支撑成本 `+6.968/+6.989/+6.980/+6.991%` → `+7.356/+7.186/+7.366/+7.388%`（C2/C5 不变），引用区间变为 `+6.31…+7.39%`，最小 CI 下界 `+4.751%`（C5），故"六个下界都在 +4.75% 以上"仍成立。

**② §VII-F 的 `+0.040%` 与 `2.04%`（误报，已撤回）。** `compute_ceiling_class_paired.py` 只在 **SensorScope** 半边读冻结树；U-Air 半边走 `rebuilt_uair()`，读的是 `E2_UAIR_CELLS.csv` 的 θ 列 `RMSE_mu_std`，所以这两个数字本来就是 θ 口径（该 JSON 记的是 `calibrated − oracle`，论文引用的是 `oracle − calibrated`）。**无需改动。**

结果：**论文中已无任何镜像口径的印刷数字**，X-4b 关闭（items 46–48：裁定 → 落纸 → 残留复核）；X-4/X-5/X-7 按其自身范围继续开放。
