# 手动下载清单（M1 / M2）——放好文件我就能按预注册继续跑

```text
来源与窗口都已在预注册里冻结：
  ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md
  sha256 18F43D5912E3EA141DF809C58F200678AFF1380838ED9B78F540033046843A5E
本清单只说明"下载什么、放哪里、我会先验什么"，不修改任何规则。
City Scanner 网格（用于核对范围）：lon [-74.009636, -73.733231]，lat [40.008129, 40.913586]
（即纽约市五区；500 m 格，446 个占用单元，已在本地核对通过）
```

## 落地目录与文件名（请照抄，不要改名、不要重新打包）

```text
C:\Cursor\raven.mcs\data\raw\exogenous_target\
    acs2021_b01003_bg_36005.json          # Bronx
    acs2021_b01003_bg_36047.json          # Kings (Brooklyn)
    acs2021_b01003_bg_36061.json          # New York (Manhattan)
    acs2021_b01003_bg_36081.json          # Queens
    acs2021_b01003_bg_36085.json          # Richmond (Staten Island)
    tl_2021_36005_bg.zip                  # TIGER/Line 2021 block-group 多边形
    tl_2021_36047_bg.zip
    tl_2021_36061_bg.zip
    tl_2021_36081_bg.zip
    tl_2021_36085_bg.zip
    nyc311_2020_2021.csv                  # NYC 311，2020-01-01 .. 2021-12-31
    NOTES.txt                             # 每个文件的下载 URL 与日期（我会抄进下载日志）
```

可选（只在 M1-a/M1-b 都失败时才用，先不用下）：

```text
    acs2021_b01003_tract_36.json          # tract 级回落（5 个县，同一张表）
    tl_2021_36_tract.zip                  # TIGER2021 tract（纽约州，或 5 个县级 tl_2021_360xx_tract.zip）
    usa_ppp_2020_UNadj.tif                # WorldPop 2020 UN-adjusted 100 m（约 300 MB）
```

---

## 1. M1-a：ACS 2021 五年估计，表 B01003（总人口），block group 级

**逐个县一次请求**（Census API 不允许多个 `in=` 县并列），共 5 次，各自另存为上面的 JSON：

```text
https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=block%20group:*&in=state:36%20county:005
https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=block%20group:*&in=state:36%20county:047
https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=block%20group:*&in=state:36%20county:061
https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=block%20group:*&in=state:36%20county:081
https://api.census.gov/data/2021/acs/acs5?get=NAME,B01003_001E&for=block%20group:*&in=state:36%20county:085
```

- 无需 API key（少量请求即可）；返回是 JSON 数组，第一行是表头 `["NAME","B01003_001E","state","county","tract","block group"]`。
- 如果 API 不方便，可用 **data.census.gov** 手动导出：Tables → `B01003` → *2021: ACS 5-Year Estimates Detailed Tables* → Geography = *Block Group within New York* → 选 5 个县 → Download CSV，然后按上面改名（CSV 也可以，我会识别 `.csv` 或 `.json`）。
- **不要**用 2022 或 2023 的五年估计（预注册冻结在 **2021**，因为它覆盖采集窗口 2020-01–2021-12）。

**几何（面积重分配用）**：TIGER/Line 2021，block group，县级 zip（每个约 1–3 MB）：

```text
https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_36005_bg.zip
https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_36047_bg.zip
https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_36061_bg.zip
https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_36081_bg.zip
https://www2.census.gov/geo/tiger/TIGER2021/BG/tl_2021_36085_bg.zip
```

（该目录同时有州级 `tl_2021_36_bg.zip`，约 20 MB；县级更小，二选一即可，县级优先。）

## 2. M2：NYC 311 Service Requests，资源 `erm2-nwe9`

冻结窗口：**created_date ∈ [2020-01-01, 2022-01-01)**（本地纽约时间；我在脚本里转 UTC，与你无关）。
**只保留三类列即可**：`Created Date`、`Latitude`、`Longitude`（多带列也行，只是文件更大）。

**推荐（网页导出）**：打开
<https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/about_data>
→ *Filter* → `Created Date` **is between** `2020-01-01` 和 `2021-12-31` → *Export* → **CSV**。
（两整年全市约 2.0–2.4 M 行；不需要按坐标过滤，我在本地按冻结的 bbox 过滤。）

**备选（SODA 分页，每次 5 万行，把 `$offset` 从 0 起每次加 50000 直到返回空）**：

```text
https://data.cityofnewyork.us/resource/erm2-nwe9.csv?$select=created_date,latitude,longitude&$where=created_date%20%3E=%20%272020-01-01T00%3A00%3A00%27%20AND%20created_date%20%3C%20%272022-01-01T00%3A00%3A00%27&$limit=50000&$offset=0
```

有 Socrata app token 的话在末尾加 `&$$app_token=<TOKEN>` 可提高限额。
把分页结果**按行首尾相接**存成一个 `nyc311_2020_2021.csv`（表头只留一次）。

## 3. 我会先做的验收（不通过就停下报告，不猜、不替代）

| 文件 | 验收条件 |
|---|---|
| ACS 5 个 JSON/CSV | 每个县 ≥ 1000 个 block group 行；`B01003_001E` 全为数值；含 `state/county/tract/"block group"` 地理键；五区人口合计落在 **8.3–9.0 M**（2021 ACS 5 年 NYC 约 8.8 M） |
| TIGER 5 个 zip | 每个含 `.shp/.shx/.dbf/.prj`；五县 block group 多边形合计约 **6,000–6,500** 个 |
| `nyc311_2020_2021.csv` | ≥ 1.5 M 数据行；`created_date` 可解析；≥ 90% 行经纬度非空；时间范围覆盖 **2020-01-20 → 2021-12-15 UTC** |
| 任意一个 | 我会对落地的每个文件算 sha256 并写进 `results_exogenous_target/round_v1/DOWNLOAD_LOG.json`；`NOTES.txt` 里的 URL/日期会一并记录 |

## 4. 拿到数据后我立即执行的动作（仍按预注册，不训练、不改论文）

1. 用冻结的 area-weighted 规则把 block-group 人口摊到 446 个 500 m 单元 → **M1 图**（每 cell 的正质量在其 8 个合法 stratum 上均分）。
2. 用 311 记录算 `count(cell, block, weekday)` → **M2 图**。
3. 对 M1、M2 与对照图各算 `n_keys / n_zero_keys / zero_key_share / rho_delivered / gate`，并写明两图 gate 是否一致（若不一致，按预注册写"门依赖于目标图的时间边际"，不挑更有利的那张）。
4. 端点表仍为 `TBD`，除非你另行授权用 50 个冻结 checkpoint 在新 `μ` 上做一次**前向评估**（那是推理，不是训练）。

## 5. 一个提醒（不影响你下载）

上一轮已查明：附录里 City Scanner 那行的"覆盖 0 → Design on"来自 region 级零检验（`compute_joint_ou_cs_p2_phi.py`，其 `n_zero` 恒为 0），与论文 `eq:design_gate` 的键级定义不是同一个对象；键级对照在同一块上给出 `ρ = 14.35%` ⇒ gate 应为 **off**。数据到手后我会用**同一套键级定义**同时报告 M1、M2 与对照三行，把这个不一致一次性摆清，但**本轮不改论文**。
