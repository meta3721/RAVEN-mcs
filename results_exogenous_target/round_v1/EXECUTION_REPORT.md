# EXECUTION_REPORT — City Scanner 外生目标图（round_v1，已完成）

```text
执行日期：2026-10-02（数据由用户手动落地后继续）
协议：ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md
      sha256 7773296B...（落盘早于任何 ρ_r 计算；§10 记录手动落地）
脚本：scripts/exogenous_target_cityscanner.py --build
只读约束：未训练；未改 src/；未改论文；未改任何已有结果目录；未提交、未推送。
写入范围：results_exogenous_target/round_v1/ 与 data/raw/exogenous_target/ 的读取
```

## 0. 一句话结论

三张图（外生 M1、外生 M2、评估派生对照）在 City Scanner 上**全部 `gate = off`**：外生图确实制造了支撑洞，但很小（`ρ ≈ 0.98–1.00%`），而现有评估派生图制造的洞大得多（`ρ = 14.35%`）；运行期该块实际是 **Design on**（`CS_ACCEPTED.json: design_on = true`）。因此按论文 `eq:design_gate` 的键级定义，**该块的设置与门不一致**；本轮按协议只报告、不修文。

## 1. 预注册是否早于第一次 `ρ_r` 计算 —— 是

预注册落盘 `2026-10-02T10:35:08 +08:00`（sha256 `7773296B…`），其后才发生网格对齐、对照行与 `ρ_r` 计算；§9/§10 只追加事实型日志（下载失败、手动落地），未改任何规则。

## 2. 三行的 `n_zero_keys`、`rho_delivered`、`gate`

键空间 `K` = 446 cells × 8 合法 stratum = **3568**；`rho_delivered` 的分母是**已送达训练单元**（10 seeds、`U=1` 事件的 risk set，共 **29189** 个），`n_unmapped_to_K = 0`。

| 图 | n_keys | n_zero_keys | zero_key_share | rho_delivered | gate | 全事件口径 ρ / gate |
|---|---|---|---|---|---|---|
| 对照：评估派生 `build_pi_target(split="test")` | 3568 | **3216** | 0.9013 | **0.14348** (4188/29189) | **off** | 0.20133 / off |
| **M1：空间人口**（ACS 2021 5-yr B01003，面积重分配） | 3568 | **304** | 0.0852 | **0.01004** (293/29189) | **off** | 0.01777 / off |
| **M2：时间需求**（NYC 311，2020–2021） | 3568 | **199** | 0.0558 | **0.00983** (287/29189) | **off** | 0.01113 / off |

- 逐 seed：M1 `0.00673–0.01443`、M2 `0.00433–0.01496`，**每个 seed 都是 off**。
- 预先写明的读法核对：M1 `gate = on` **未出现**；M2 `gate = off` **出现且被允许**；M1 与 M2 的 gate **相同**，故没有触发"门依赖于目标图的时间边际"的分支，也不存在"挑更有利的图"的情形。
- `removed_unit_share = ρ_delivered`；`removed_mass_share = TBD`（run 目录只有 checkpoint 与 `CS_ACCEPTED.json`，读不到 per-key 权重，协议禁止估算）。
- 图的可审计指纹（float64 字节的 sha256）：control `fe615ff489ad…`、M1 `d7b906fd711d…`、M2 `14dae5d40071…`。

## 3. 两张外生图的构建事实（冻结规则逐条对照）

**M1（空间人口）**
- 数据：ACS 2021 五年估计表 **B01003**，block group 级，五县（36005/36047/36061/36081/36085），6,807 个 block group，五区人口合计 **8,736,047**。
- 几何：TIGER/Line 2021 BG 多边形 6,807 个（与 ACS 行数**逐一相等**）。
- 聚合：**面积重分配**（Sutherland–Hodgman 对 500 m 单元裁剪，环带符号求和以计洞），21,891 次裁剪；`Σ_cell Pop = 8,736,047`（与源合计一致，仅落在 446 个存储单元内 1,417,570，其余落在未占用单元或网格之外）。408/446 个单元有正人口，**38 个单元为 0**（水域/公园/机场类）。
- 映射：每 cell 的正质量在其 8 个合法 stratum 上**均分**，全键归一化（`Σ π = 1`）。`n_zero_keys = 304 = 38 × 8` ✓ 与 38 个零人口 cell 完全对应。

**M2（时间需求）**
- 数据：NYC 311 资源 `erm2-nwe9`，`created_date ∈ [2020-01-01, 2022-01-01)`（本地纽约时间），**6,162,906 行**。
- 时间：本地→**UTC** 转换；DST 重复小时按 `ambiguous=True` 固定为 DST，`nonexistent="shift_forward"`；受影响行 **1,546**（两年各一小时，占 0.025%，已记录）。UTC 区间 `2020-01-01T05:00Z – 2022-01-01T04:59:36Z`，完整覆盖采集窗口（2020-01-20 23:11 – 2021-12-15 14:35 UTC）。
- 空间：无坐标 150,062 行（2.44%）；bbox 之外 469,105 行；落在 446 个存储单元内 **1,174,758 行**（其余 4,368,981 行在未占用单元——311 覆盖全城而 City Scanner 只走过 446 个单元，属预期）。
- 计数：`count(cell, block, weekday)`，`n_nonzero_keys = 3369`，全键归一化（`Σ π = 1`）。

## 3b. 三张图的边际（新量化出来的部分）

City Scanner 的部署目标组 `target_group` 是 **region**（4 组），所以每张图都隐含一组 `μ`（组权重），这正是判据 `RMSE_μ` 使用的权重：

| 图 | region0 | region1 | region2 | region3 |
|---|---|---|---|---|
| 对照（评估派生，test） | 0.2373 | **0.4746** | 0.0708 | 0.2172 |
| M1（ACS 人口） | **0.3061** | 0.3677 | 0.0613 | 0.2650 |
| M2（311 需求） | 0.2169 | 0.3992 | **0.0438** | **0.3402** |

- 组权重变化很大：region3 从 0.2172 升到 0.2650（M1）/0.3402（M2），region1 从 0.4746 降到 0.3677/0.3992。也就是说**判据自身的权重**随目标图来源移动，这不是小扰动。
- 时间边际：M1 在 block 上恒为 0.25、weekday/weekend 0.5/0.5（这是**假设**——人口不随 block 与 weekday 变化，已在预注册写明）；M2 为 block0–3 = 0.324/0.105/0.275/0.295、weekend 0.2996；对照为 0.064/0.089/0.306/0.541、weekend 0.2923。
- 键级图与边际已落盘：`MAPS_KEY_LEVEL.csv`（3568 键 × 三图 π）、`MAP_MARGINALS.csv`。

**本轮量化到哪一步**：`π^tar`（判据的输入）已经从**外生公开数据**量化并可复现；门的结果也量化了（三图 `off`）。**未量化**的是"删除造成的端点后果"（`RMSE_μ/Δ_group` 在新 `μ` 下的真实值——需要一次前向评估）与"质量份额的数据无关下界"（按定义推不出，`PROOF_SKELETON.md` 的 `GAP`）。

## 4. 端点表是真前向评估还是 TBD —— **实测前向评估（本层已完成）**

对 50 个冻结 checkpoint（5 arms × 10 seeds）各做一次前向（`_predict`，2090 个测试单元），**同一份预测**用三套 region 权重打分（`_mu_weights_for_test` + `rmse_mu`）；`scripts/exogenous_target_endpoints.py`，产物 `ENDPOINT_TABLE.csv`（50 行）/`ENDPOINT_TABLE.json`。

**复现门**：每个种子与它自己的 `CS_ACCEPTED.json` 的 `RMSE_μ` 之差，**最大绝对差 = 5.551e-17**（容差 1e-6），即存储值可由 checkpoint 重放**逐位复现**（本块不存在 U-Air 树那种镜像/θ 差异）。事后核对：由 `CS_ACCEPTED.json` 重算的 10 种子均值为 `fedavg 0.23788 / twostage 0.25095 / raven 0.25490 / obsuse 0.25657 / fedau 0.25817`，与既定五个数一致。

**三套权重下的 10 种子均值**

| arm | `run`（本块 test-region share） | `M1`（ACS 人口） | `M2`（311 需求） | Δ(M2−run) |
|---|---|---|---|---|
| `fedavg_window` | 0.2378839 | 0.2375164 | 0.2374858 | −0.167% |
| `twostage_hajek` | 0.2509520 | 0.2508171 | 0.2504281 | −0.209% |
| `raven` | 0.2549033 | 0.2548301 | 0.2544299 | −0.186% |
| `obsuse_window` | 0.2565709 | 0.2563015 | 0.2562092 | −0.141% |
| `fedau_window` | 0.2581655 | 0.2579923 | 0.2579219 | −0.094% |

- **排名在三个权重下完全相同**：`fedavg_window < twostage_hajek < raven < obsuse_window < fedau_window`（按 10 种子均值升序）。没有出现翻转。
- **移动很小**：换权重使每个 arm 变化 ≤0.21%，方向一致（M1/M2 都略低）；因此**论文 City Scanner 那一行的 `RMSE_μ` 对 region 权重来源不敏感**（在 0.2% 量级内），arm 顺序不是评估派生权重的产物。
- **`WG_run = WG_M1 = WG_M2`，逐行最大差 = 0.0**（远小于 1e-8）。原因：`_mu_weights_for_test` 在 region 内给等权，四个 `μ_g` 全为正时，各 region 的等权 RMSE 与其最大值不随 `μ` 变。**这只说明最差 region 对这三套 region 权重不变，不能解释成"最差组对目标图稳健"。**
- 相对 `fedavg_window` 的 10 对配对相对差均值：`twostage` +3.90…+4.03%、`raven` +5.57…+5.71%、`obsuse` +6.97…+7.03%、`fedau` +7.37…+7.47%（三套权重下同量级）；更小的种子数为 5/10、5/10、1/10、1/10。**不做 Holm，不称显著。**
- 本轮**未**计算 Tail（`CS_ACCEPTED.json` 无 Tail），**未**计算 `Δ_group`/`Δ_c-s`（依赖未落盘的窗口聚合权重，换 `μ` 打分得不到），这两列仍为 `TBD`。

## 5. 证明骨架里有几处 `GAP` —— 1 处

`PROOF_SKELETON.md`：第 1 节删除恒等式（`π_min > 0` 与 A6a 使分母严格为正 ⇒ `ζ = 0 ⟺ π^tar = 0`；门 `ρ_r = 0` ⟺ Design 不删除已送达单元；对任何公共图成立，且不涉及 `ε_π`）；第 2 节 **1 处 GAP**（`ρ_r > 0` 时被删**质量**份额的数据无关正下界推不出）；第 3 节与命题 3 的边界（`ρ_r > 0` 使共享 `A_r` 前提失效 ⇒ 命题 3 不被适用；`ρ_r = 0` 不推出任何插值误差为零）。`eq:design_switch` 未出现。

## 6. 与论文有关、必须上报的一致性问题（本轮不改论文）

1. **该块的目标是 region 级，论文的门是键级：两者不是同一个对象（更正）。** `CS_PHI_DECISION.json` 记录该块运行期目标为 `pi_i_tar = mu_of_region_h_i`、`mu_split = test_units_region_share_no_Y`，四个 region 权重（0.23732 / 0.47464 / 0.07081 / 0.21722）与 `MAP_MARGINALS.csv` 中 `control` 的 region 边际一致，且 `phi_train_unit = 0`；按该块自己的规则 `Design_ON iff phi_train_unit == 0` 得到 `design_on = true`，**这与它自己的图并不矛盾**。而 `eq:design_gate` 的 `ρ_r` 定义在 `(client, stratum)` **键级**：同一块上对照图的键级 `ρ_r = 14.35%`，按论文的门应为 `off`。因此附录 `tab:scd_phi_freeze` 里 City Scanner 那行的「覆盖 0」是**region 级检验的结构性零**，而不是键级支撑为空的证据。**本轮不改论文。**
2. **附录那一列的"零覆盖"是结构性零，不是证据。** `tab:scd_phi_freeze` 的 City Scanner PM2.5 行（9343 / 0 / 0 / on）来自 `scripts/compute_joint_ou_cs_p2_phi.py` 一族：其零检验是 `pi_i = train["target_group"].map(mu)`，`mu` 为 **4 个 region 的 test 份额**，且 `any(mu <= 0)` 直接报错（45–52 行），故 `n_zero` **恒为 0**。它检验的是 region 级目标，不是 `(client, stratum)` 键的支撑。
3. **现有评估派生图删得比外生图多一个数量级。** 键级 `ρ`：test 派生 14.35%（全事件 20.13%）vs 外生 M1 1.00%（1.78%）、M2 0.98%（1.11%）。也就是说，现有图删掉的大部分已送达单元**并非城市层面没有需求**，而是它们的键在 **test** 里没有质量（train-only 键）——这正是"评估派生"的直接后果，也正是外生图能提供的对照价值。
4. 尺寸提示：外生图**不能**把该块翻成 `on`（M1 与 M2 都 `off`）；因此若要让论文的 City Scanner 行与门自洽，需要的是**改写该行/该设置**或**重新定义门的适用条件**，而不是换一张更"干净"的图。本轮不裁定。

## 7. 与预注册清单的两处路由偏差（数据同版本同表，已记录）

| 项 | 清单原地址 | 实际使用 | 影响 |
|---|---|---|---|
| ACS 数值 | `api.census.gov` 五个县级请求 | 官方 **table-based summary file** `acsdt5y2021-b01003.dat`（同一 2021 五年、同一表 B01003、`E001` 为估计值），按 API 形状转成 JSON | 无：版本、表、地理层级一致；`NAME` 由 GEOID 构造（已在 `NOTES.txt` 说明） |
| TIGER 几何 | 五个**县级** zip | 县级 URL 404，改用**州级** `tl_2021_36_bg.zip` 后按 `COUNTYFP` 拆成五个县级 zip | 无：同一 TIGER2021 BG 图层；拆分后多边形数与 ACS 行数逐一相等（1182/2156/1292/1803/374） |
| 311 | 网页导出或 SODA | SODA 分页（`$select=unique_key,created_date,latitude,longitude`、按 `unique_key` 排序、`$limit=50000` 翻页） | 无：窗口与列一致；`unique_key` 仅用于保证分页不重叠 |

原始 `NOTES.txt`（3,168 B）的 sha256 已记入 `DOWNLOAD_LOG.json`；每个落地文件的 sha256 同。

## 8. 验收清单核对

| 文件 | 预注册验收条件 | 实测 | 结论 |
|---|---|---|---|
| ACS × 5 | 每县 ≥1000 BG；`B01003_001E` 全数值；五区合计 8.3–9.0 M | 1182/2156/1292/1803/374（合计 6807）；合计 **8,736,047** | PASS |
| TIGER × 5 | 每个含 `.shp/.shx/.dbf/.prj`；多边形合计 6,000–6,500 | 5×四件套齐全；合计 **6,807** | PASS（**我预估的 6,000–6,500 区间偏低，实际 6,807；该区间只是我的经验值，不是规则门槛，且多边形数与 ACS 行数逐一相等**） |
| 311 | ≥150 万行；时间可解析；≥90% 有坐标；覆盖采集窗口 | **6,162,906** 行；0 行时间不可解析；97.56% 有坐标；覆盖 2020-01-20→2021-12-15 | PASS |
| 网格对齐 | 与原存储单元一致 | 446 = 446，`gx/gy` 与 `spatial_id` 一致 | PASS |
| stratum 词汇 | 32 | 32，与观测一致 | PASS |

## 9. 复现入口

```text
python scripts/exogenous_target_cityscanner.py --build
results_exogenous_target/round_v1/
    MAP_SUMMARY.csv          # 三行（n_keys / n_zero_keys / zero_key_share / rho_delivered / gate / …）
    DOWNLOAD_LOG.json        # 落地文件 sha256、图指纹、逐 seed ρ、敏感性、M1/M2 构建统计、DST 计数
    GRID_ALIGNMENT.json      # 原点、bbox、446 单元核对
    PROOF_SKELETON.md        # 三句骨架（1 处 GAP）
    EXECUTION_REPORT.md      # 本文件
    extracted/               # 展开后的 TIGER 县级 shapefile（脚本自动生成）
预注册（含 §9 下载日志与 §10 手动落地）：
    ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md
手动下载清单：results_exogenous_target/round_v1/MANUAL_DOWNLOAD_SHEET.md
```
