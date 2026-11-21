# 预注册：City Scanner 外生目标图（M1 空间人口 / M2 时间需求）

```text
写入日期：2026-10-02（本文件落盘时间即计时基准）
协议来源：raven-mcs-exogenous-target-execution-prompt.md（用户提供，逐字遵循）
本轮只做三件事：预注册、只读计算、证明骨架。
不训练；不改 src/；不改 TO_OVERLEAF_paper_tmc_r1_clean/；不改已有结果目录；不提交、不推送。
```

## 0. 本轮能产出 / 不能产出

| 主张 | 本包能产出 | 不能产出 |
|---|---|---|
| Design 恰好删除那些所在 `(client, stratum)` 公共目标质量为 0 的已送达单元 | 来自 `eq:design_ratio_simple` 与 `eq:design_gate` 的恒等式 + 证明骨架 | 新的经验性胜出 |
| 把评估派生图换成冻结的外生图会改变 City Scanner 上的门判定 | M1、M2 与现有评估派生图各自的 `ρ_r` 与 `D_r` | 定理 |
| `eq:design_switch` 是某损失下的最优修剪 | 本包不产出 | 不得推导 |

## 1. 先纠正两个不能执行的说法（本文件据此写死）

1. **`ρ_r = 0` 不推出 `ε_π = 0`。** `ε_π` 是机会估计 `π̂^opp` 对 `π^opp` 的误差；`ρ_r` 是已送达单元中其 `(client, stratum)` 公共目标质量为 0 的比例。两者不是同一个量。证明骨架中禁止出现 `ρ_r = 0 ⇒ ε_π = 0`。
2. **`eq:design_switch` 不是外生图的推论。** 它是 SensorScope/U-Air 消融数字上的无差异条件（`4.990`、`6.943`、`6.885`、`7.221`）。本轮不推导它、不写成推论、不重跑那两个数据集；它也不出现在证明骨架里。

仓库中没有名为 "Support Lemma" 的对象。证明只能使用当前 `.tex` 已写出的定义；某步推不出来就写 `GAP`，不用外部论文补，本轮不新增引用。

## 2. 数据块与冻结对象

- 数据块：**仅** `cityscanner_nyc_pm25`。不使用 SensorScope、U-Air、E2、E4 及其 `θ` 产物。
- client = 500 m 网格单元（`spatial_id`，格式 `g{gx:04d}_{gy:04d}`）；stratum = `{region}::block{b}::{weekday label}`，由 `src/raven_mcs/data/cityscanner.py` 构造：
  - `region ∈ {region0..region3}`，由单元 `gx/gy` 相对**该块单元中位数** `mx, my` 的象限决定：`region = (gx>=mx)<<1 | (gy>=my)`；
  - `block = UTC_hour // 6`（4 段）；
  - `weekday label = "weekend"` 当 UTC `dayofweek >= 5`，否则 `"weekday"`；
  - 因此协议层 stratum 词汇表 **S = 4 region × 4 block × 2 label = 32**（与 `atomic_units.parquet` 中观察到的 32 个 stratum 一致）。
- 时区：**UTC**（与 `cityscanner.py` 一致）。
- 现有图：`build_pi_target(..., split="test")` 在本块上的结果，**评估派生**，仅作第二步对照，不作为决定正质量的依据。
- Design on：`ζ = π^tar / max(π̂^opp, π_min)`；Design off：`ζ ≡ 1`。
- 门：`eq:design_gate`，`ρ_r = n^zero_r / n_r`，`D_r = on ⟺ ρ_r = 0`。
- 切换点 `eq:design_switch`：本轮的对象之外。

### 2.1 网格对齐规程（冻结，第二步按此重算原点）

`cityscanner.py` 的原点是**保留下来的 GPS 的最小 lon/lat**（不是固定 bbox）：

```text
lon0 = min(longitude), lat0 = min(latitude)        在物理过滤之后
lon1 = max(longitude), lat1 = max(latitude)
mid_lat = (lat0 + lat1)/2
lat_deg = (cell_km)/EARTH_KM_PER_DEG_LAT
lon_deg = (cell_km)/(EARTH_KM_PER_DEG_LAT * max(0.2, cos(mid_lat)))
gx = floor((lon - lon0)/lon_deg),  gy = floor((lat - lat0)/lat_deg)
```

物理过滤（`_physical_filter`）：丢弃 lat/lon/time/pm25 非有限的行；丢弃 `pm25 < 0` 或 `pm25 > 1000`。
`cell_km = 0.5`。时间列是 **epoch 秒**（`cityscanner.py` 按中位数是否 > 1e12 判断 s/ms；本块为 s）。
第二步用同一套规则从 `data/raw/cityscanner_nyc_pm25/NYC_Pilot{1,2}_PM*.csv` 重算 `lon0/lat0/lon1/lat1`，并与 `atomic_units.parquet` 里已存的 `public_features.gx/gy` **逐单元核对**；不一致即判"网格对不齐"，按第 8 节停止。

## 3. 冻结的映射规则

键空间与归一化（两图共用）：

```text
网格单元集合 C = atomic_units.parquet 中出现的全部 spatial_id（446 个）
合法键集合 K = {(c, s) : c ∈ C, s ∈ S, region(s) = region(c)}   （|K| = 446 × 8 = 3568）
两张图都定义在 K 上；π^tar(c, s) = 0 表示该键为空
归一化：Σ_{(c,s) ∈ K} π^tar(c, s) = 1
全零图 = 失败：停止并报告，不改规则
```

**M1，空间人口（主图）。** 数据源优先级（冻结，逐级回落，全部失败即停止）：

| 级别 | 数据 | 冻结版本/表 | 备注 |
|---|---|---|---|
| M1-a | ACS 5 年人口 | **ACS 2021 5-year**（2017–2021），表 **B01003_001E**（总人口），地理层级 **block group**，州 36，县 005/047/061/081/085 | 覆盖采集窗口（2020-01–2021-12）的最近一期 |
| M1-b | ACS 5 年人口（回落 1） | 同上但地理层级 **tract** | 仅当 block group 取回失败 |
| M1-c | WorldPop（回落 2） | **WorldPop 2020 UN-adjusted, 100 m, USA** | 仅当 ACS 两次都失败 |

空间聚合（冻结）：
- M1-a/M1-b：**按面积重分配**。每个 ACS 单元（block group 或 tract）的人口乘以其与 500 m 单元的多边形交面积占该 ACS 单元面积的比例，累加到该 500 m 单元；多边形取自 **TIGER/Line 2021**（block group 或 tract，纽约州，县 005/047/061/081/085）。面积用等面积近似（经纬度按 `lat_deg/lon_deg` 的同一常数换算为 m）。
- M1-c：**像素中心落入即计入**。100 m 栅格像素中心落在某 500 m 单元内则该像素值累加到该单元。

映射规则（写死）：

```text
π^tar_M1(c, s) ∝ Pop(c)     若 s ∈ S 且 region(s) = region(c)
π^tar_M1(c, s) = 0          否则
同一 cell 的正质量在其 8 个合法 stratum 上【均分】
Pop(c) = 0 的 cell，其全部合法 stratum 均为 0
```

**假设（写成假设，不得写成数据事实）：** 人口不随 block 与 weekday 变化。

**M2，时间变化的需求（敏感性图）。** 数据源：**NYC 311 Service Requests**（NYC Open Data，Socrata 资源 `erm2-nwe9`），同一 bbox、同一 500 m 网格。

- 冻结时间范围：**2020-01-01T00:00:00Z ≤ created_date < 2022-01-01T00:00:00Z**（即 2020 与 2021 两个整日历年）。
  依据：City Scanner 实际采集窗口经本轮本地核对为 **2020-01-20 23:11 UTC → 2021-12-15 14:35 UTC**（原始 PM 文件按 `_physical_filter` 保留行的时间范围），该范围完整落在上述两个日历年之内，因此不需要外推；不是"未知则取 2019 全年"的情形。
- 时区：311 的 `created_date` 为**纽约本地时间**，计算 `block`/`weekday` 前一律转换为 **UTC**（与 `cityscanner.py` 一致）。
- 记录筛选：坐标可解析且落在网格 bbox 内、时间可解析；**不按投诉类别过滤**。
- 计数：`count(c, block, weekday label)`；`(c, block, weekday)` 计数为 0 即该键为空。
- region：沿用该 cell 在 City Scanner 中的 region（`target_group`），**不重新划分**。

```text
π^tar_M2(c, s) ∝ count(c, block(s), weekday(s))
```

## 4. 两条共同的禁止（写死）

决定哪些键为正时，不得使用：测试集；训练集标签；当前 `build_pi_target(split="test")` 的支撑；任何模型预测；任何方法的成绩。现有 `π^tar` 只允许在第二步作为对照读入。

## 5. 第二步的输出列（定义冻结）

| 列 | 定义 |
|---|---|
| `n_keys` | 键数（= \|K\| = 3568） |
| `n_zero_keys` | `π^tar = 0` 的键数 |
| `zero_key_share` | `n_zero_keys / n_keys` |
| `rho_delivered` | 已送达**训练**单元中，所在键 `π^tar = 0` 的比例；**分母是送达单元数，不是键数** |
| `gate` | `on` 当且仅当 `rho_delivered = 0` |
| `removed_unit_share` | 等于 `rho_delivered` |
| `removed_mass_share` | 被删单元在 Design-on 权重下的质量占比；轨迹给不出权重则填 `TBD`，**不估算** |

- 送达单元从该块已有的 EventTrace 读取（`artifacts/e3_c1_cityscanner_eventtraces_v1/cityscanner_nyc_pm25/seed*/training_eventtrace/events.parquet`，每个事件给出 `risk_set_unit_ids`、`observed_unit_ids`、`O`、`U`）。读不到即停止，**不重生成轨迹**。
- 端点：**不训练**。只有当某个冻结 checkpoint 仍在、且可在新 `μ` 上重新做一次前向评估时，才填写端点表（那是推理）；否则端点列全部 `TBD` 并写明缺什么。禁止用 E2、E4 的产物填表。

## 6. 预先写明的读法（算完不许改）

- M1 的 `gate = on` 是**允许**的结果：一张只随空间变化的人口图可能在这个网格上没有制造支撑洞。不得为了得到 `off` 去改均分规则。
- M2 的 `gate = off` 也是**允许**的结果：它只说明 311 计数有洞，不说明 Design 因此更好或更差。
- 两张图的 `gate` 不同，就写「**门依赖于目标图的时间边际**」，**不得**选一张更有利的图作为主结果。

## 7. 输出物与路径

```text
ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md   （本文件）
scripts/exogenous_target_cityscanner.py                             （只读脚本）
results_exogenous_target/round_v1/                                  （只写此目录）
results_exogenous_target/round_v1/MAP_SUMMARY.csv
results_exogenous_target/round_v1/PROOF_SKELETON.md
results_exogenous_target/round_v1/EXECUTION_REPORT.md
results_exogenous_target/round_v1/DOWNLOAD_LOG.json
```

## 8. 失败与停止规则

下载失败、网格对不齐、轨迹缺失：**停在该步，报告，不换数据源继续**。全零图：停止并报告，不改规则。任何"为了得到更好看的门"而修改映射、均分或筛选的行为均禁止。

## 9. Download log（第二步填写；只记事实，不改规则）

| 项 | 状态 |
|---|---|
| 下载尝试时间 | 2026-10-02，预注册落盘（10:35:08 +08:00）之后 |
| ACS 2021 B01003 block group（Census API） | **FAIL**：`https://api.census.gov/...` → `curl(35) schannel SEC_E_NO_CREDENTIALS`；`.NET` 同样失败；`http://` 入口 302 → HTTPS 后同样失败 |
| TIGER 2021 多边形（NY，`tl_2021_36_bg.zip`） | **FAIL**：`http://www2.census.gov/...` → HTTP **403**，未取回字节；HTTPS 路径同样被阻断 |
| WorldPop 2020 UN-adj 100 m（仅回落时） | **FAIL**：`http://data.worldpop.org/...` → 302 → HTTPS 后同上 |
| NYC 311（Socrata `erm2-nwe9`，2020–2021，bbox 过滤） | **FAIL**：`http://data.cityofnewyork.us/...` → 301 → HTTPS:443 后同上 |
| 环境对照 | `https://example.com` **FAIL**（同一错误），故失败为环境级 HTTPS 阻断，非源站问题 |
| 成功/失败结论 | **M1、M2 在数据获取步骤失败并停止**；按协议第 8 节未换任何数据源。原始 City Scanner PM 文件的 sha256 已记入 `results_exogenous_target/round_v1/DOWNLOAD_LOG.json`；对照行、网格对齐核对与证明骨架不受影响，见 `EXECUTION_REPORT.md` |

## 10. 手动落地（事后追加，仅记录操作事实，不改任何规则）

由于本环境全部 HTTPS 被阻断（见 §9），用户改为**手动下载**上述冻结来源。落地目录与文件名、每个来源的精确 URL、以及照单验收条件写在
`results_exogenous_target/round_v1/MANUAL_DOWNLOAD_SHEET.md`。手动落地不改变 §3 的来源、版本、规则与窗口；文件到位后由脚本按 §5 的列定义计算，并对每个落地文件补记 sha256 与下载日期。

**落地结果（2026-10-02，事实记录）**：14 个文件到位（5 个 ACS JSON、5 个 TIGER zip、1 个 311 CSV、`NOTES.txt`，另 3 个可选回落未用）。三处**路由偏差**（版本/表/图层/窗口均未变，见 `NOTES.txt` 与执行报告 §7）：① ACS 数值改用官方 table-based summary file（同一 2021 五年、同一表 B01003）；② TIGER 县级 URL 404，改用州级文件后按 `COUNTYFP` 拆分；③ 311 用 SODA 按 `unique_key` 分页（6,162,906 行）。运行结果：三图 `gate` 全为 `off`（对照 `ρ=0.14348`；M1 `0.01004`；M2 `0.00983`），`removed_mass_share` 保持 `TBD`；详见 `results_exogenous_target/round_v1/EXECUTION_REPORT.md` 与 `MAP_SUMMARY.csv`。
