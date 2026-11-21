# 人工核查方案（排版 + 行政项）

对照稿：`TO_OVERLEAF_paper_tmc_r1_clean/`  
PDF：`main.pdf`（16 页）+ `supplemental.pdf`（8 页）  
作者行按你的要求**不查、不改**（仍为 `**** and Anfeng Liu`）。

这些改动**已经写进上述文件夹**，不必再从别处粘贴。核查时只打开这两个 PDF，源文件仅在你要改字时再用。

建议顺序：先看图和算法（一眼能判），再对表数字，最后扫主张天花板。大约 45–60 分钟。

---

## 0. 打开什么

| 文件 | 用途 |
| --- | --- |
| `main.pdf` | 主文全部改动 |
| `supplemental.pdf` | 附录编号、Fig.6–8、Table XIII |
| 不必打开 | `_paper_work/`、封印 E1–E4、`paper_ready_r2/` |

编译顺序（若你本地重编）：先 `main.tex`，再 `supplemental.tex`。

---

## Pass A — 图布局（约 15 分钟）

目标：双子图一行；(a)(b) 在图下；四联图在单栏 2×2；字不压柱；柱状图灰色条纹。

| # | PDF 位置 | 应看到 | 不通过则记下 |
| --- | --- | --- | --- |
| A1 | 主文 p.2 **Fig. 1** | (a)(b) **左右**横排，双栏总览图 | 仍上下叠；框内字被裁切 |
| A2 | 主文 p.11 **Fig. 2** | 单栏一行两图；(a) \(D_{\mathrm{aligned}}\) 全为负；(b) 17–18/20 | 子图上下叠；图例压柱 |
| A3 | 主文 p.11 **Fig. 3** | 单栏一行两图：T-Drive 质量 + TV | 上下叠；TV 虚线 0.05 看不见 |
| A4 | 主文 p.12 **Fig. 4** | 单栏一行两图：SS 近 0、UA 约 +7% | 数字压线；图例挡 U-Air 柱 |
| A5 | 主文 p.13 **Fig. 5** | **单栏 2×2**，不是通栏四连 | 仍占满双栏；caption 再写 insets |
| A6 | 补 p.7 **Fig. 6–8** | 编号从 **6** 起（接主文 Fig.5）；Fig.6–7 为单栏 2×2 | 又从 Fig.1 计；四联仍通栏 |
| A7 | 全部柱状图 | 灰色 + 条纹；子图名在图下 | 霓虹纯色；子图名在图上 |

---

## Pass B — 行政项（约 15 分钟）

| # | PDF 位置 | 应看到 | 不通过则记下 |
| --- | --- | --- | --- |
| B1 | 主文 p.8 **Algorithm 1** | 窗口关闭：\(R/O/U\) → Design **数据集开关** → \(\hat\beta\) → (P2) → \(\theta,Q\) | Design 写成“每个窗口现看现关” |
| B2 | 主文 p.10 T-Drive 段 | 脚注 URL 为 Microsoft Research *T-Drive trajectory data sample* | 误用 CRAWDAD 温度链接 |
| B3 | 主文 p.14 结论与参考文献之间 | 无编号节 **Data and Code Availability**；写明改编 FedAU/ObsUse；**不**声称完整公开训练栈 | 出现具体 GitHub 并写成可复现 |
| B4 | 主文 p.3 Related Work | Byrd & Lipton 2019 一句：过参数化分类里 IW 可失效，**不解释本稿 RMSE** | 写成“所以 RMSE 打平是因为 Byrd” |
| B5 | 补 p.7 **Table XIII** | 四块 \(\mathrm{RMSE}_g\)；WG 列 = 该行四块的 max。编译有约 100pt overfull，**必须看是否溢出栏宽** | WG 对不上；数字被裁切 |
| B6 | 补全文编号 | 表从 **VI** 起，图从 **6** 起，公式从 **(44)** 起 | 表又从 I、图又从 1 |
| B7 | 主文 p.4 Table I | 最近邻对照表可读 | 右栏 p 值列溢出到栏外 |

---

## Pass C — 数字对表（约 15 分钟）

只核这几处。对不上就停，不要现场改主张。

### C1. 主文 Table III（p.12）WorstGroupRMSE 必须等于补 Table XIII 的 WG 列

| 数据集 | 方法 | Table III WG | Table XIII WG |
| --- | --- | --- | --- |
| SensorScope | FedAvg-Window | \(8.6716\pm0.0471\) | 同 |
| SensorScope | FedAU-Window | \(8.6691\pm0.0522\) | 同 |
| SensorScope | ObsUse-Window | \(8.6618\pm0.0528\) | 同 |
| SensorScope | RAVEN (gated) | \(8.6707\pm0.0486\) | 同 |
| U-Air | FedAU-Window | \(1.1701\pm0.0689\) | 同 |
| U-Air | ObsUse-Window | \(1.1692\pm0.0689\) | 同 |
| U-Air | RAVEN (full) | \(1.2630\pm0.0716\) | 同 |
| U-Air | RAVEN (gated) | \(1.1703\pm0.0734\) | 同 |

### C2. 门控默认（Table III caption + 数字）

- SensorScope gated RMSE\(_\mu\) \(7.9380\pm0.0473\)，Design **开**
- U-Air gated RMSE\(_\mu\) \(1.1131\pm0.0638\)，Design **关**
- U-Air full Design RMSE\(_\mu\) \(1.1911\pm0.0659\) 只作诊断行

### C3. 欠服务块 Table IV（p.12）

- \(g^\star\)：SS = 2（UTC 12–18），UA = 3（UTC 18–24）
- VAL：SS vs FedAU / ObsUse 约为 \(+0.05\%\) / \(+0.15\%\)；UA 约为 \(-0.44\%\) / \(-0.27\%\)
- **未过** −0.5% 双对照赢规则；正文必须写 TEST 未开

### C4. Table XIII 与 \(g^\star\) 的关系（补 p.7 文字）

- 两边最差块都是 \(g=2\)
- SS：\(g^\star=2\) **等于**最差块
- UA：\(g^\star=3\) **不是**最差块（\(g=3\) 约 \(1.073\)，WG 是 \(g=2\) 的 \(1.1703\)）

---

## Pass D — 主张天花板（约 10 分钟）

扫摘要、RQ2 回答、讨论、结论。出现下列任一句即记为必须改回：

| 禁止写法 | 正确天花板 |
| --- | --- |
| 相对改编 FedAU/ObsUse 在 RMSE 或 WG 上“显著更好 / unique win” | 四块 WG **非劣**（+0.5% 规则），不是赢 |
| 把 U-Air −0.44% 写成赢 | VAL 负结果；TEST 未开 |
| Path B / 门控是第四个贡献 | 是 Contribution 2 的实践实现 |
| T-Drive 方法排名或端到端系统 | 证据等级 A；只提供真实 \(R\) |
| 裁剪 plug-in 无偏 | 稳定扰动，不是无偏 |
| 打开 G6 TEST 才能过关 | 不要打开 |

---

## 核查时不要改的

- 作者行
- 封印 E1–E4、`paper_ready_r2/`、`tdrive_protocol_seal_r1/`
- 为“好看”把 Fig.5 改回通栏四连（那是刚按打磨清单改掉的）
- 给 GitHub 加“完全可复现”的句子

---

## 通过标准

A–D 全部勾选，且 Pass D 无禁止写法，即可把这两个 PDF 当作人工核查通过的投稿包。若只 A/B 有版式问题，改 PDF 后重编即可；若 C/D 对不上，先停，不要现场改数字或主张。
