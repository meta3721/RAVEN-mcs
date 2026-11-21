# CCFA Citation Audit — RAVEN-MCS 参考文献全量核验

## 1. Report Metadata

- **Audit date:** 2026-08-18
- **Protocol:** nature-ref-verifier（字段级 Critical / Warning / Info；综合等级 Verified / Check suggested / Needs fix / Unverifiable）。仓库内无独立 skill 文件名为 `CCFA-citation-audit`，本报告按该协议对 `_paper_work/reference.bib` 全部 45 条做核验，编号对齐 `_paper_work/main.bbl`。
- **Sources queried:** Crossref DOI（优先）→ Crossref `query.title`+`query.author`（剔除 supplementary `component`）→ OpenAlex → WebSearch / IEEE Xplore / DBLP / AAAI OJS / PMLR / JSTOR / Zenodo / TfNSW Open Data Hub。
- **Input:** `_paper_work/reference.bib`（45 条）、`_paper_work/main.bbl`（[1]–[45]）
- **Machine dumps:** `citation_audit_raw.json`、`citation_audit_compare.json`（机器初判有假阳性；下表为人工裁定）
- **Scope:** 不改 `reference.bib`。本报告只核验、给修正建议。

## 2. 验证结果：45 条文献

- ✅ Verified: **34**
- ⚠️ Check suggested: **9**
- ❌ Needs fix: **2**
- ❓ Unverifiable: **0**

机器初判曾把若干 Crossref Early Access 残条、OpenAlex 预印本、以及 `Li, Tian`/`Gao, Jing` 姓名解析误判标成 Critical。下列等级已按出版方记录重裁。

## 3. ❌ 必须修正（2）

| # | Key | 问题 | 当前值 | 正确值 | 来源 |
|---|-----|------|--------|--------|------|
| [7] | `wang2024fewshot` | 第四作者姓名顺序颠倒 | `Yang, Xu` | `Xu, Yang`（Yang Xu, Hunan University） | Crossref `10.1109/infocom52122.2024.10621156`；INFOCOM 2024 program；DBLP `WangZYXSY24` |
| [27] | `chen2026fedcure` | 第三、第四作者名错误 | `Cao, Shuqing`；`Wang, Dawei` | `Cao, Shuqin`；`Wang, Wei` | AAAI OJS 正式页面 / Crossref `10.1609/aaai.v40i25.39176`。卷期页 `40(25):20418–20426` 已正确 |

建议补丁（仅这两条）：

```bibtex
% [7]
author={Wang, En and Zhang, Mijia and Yang, Bo and Xu, Yang and Song, Zixuan and Yang, Yongjian}

% [27]
author={Chen, Yue and Lu, Jianfeng and Cao, Shuqin and Wang, Wei and Li, Gang and Wen, Guanghui}
```

arXiv:2511.10227 HTML 把第三作者写成 Shuqing、且有页面把第四作者解析成 Dawei Wang；**以 AAAI 正式出版页为准**。

## 4. ⚠️ 建议核对（9）

| # | Key | 问题 | 详情 |
|---|-----|------|------|
| [11] | `zhang2026mapt` | Early Access 元数据漂移 | bib 仍 `note={Early access}` 且无卷期页。Crossref DOI `10.1109/tmc.2026.3678980` 现为 TMC **25(9):14336–14351, 2026**。IEEE 规则：已见刊则改正式卷期页。 |
| [12] | `mcmahan2017communication` | 第一作者中间名缺失 | 卷期页 **AISTATS / PMLR 54:1273–1282, 2017** 正确。PDF/PMLR 作者为 **H. Brendan McMahan**（bib 写 `McMahan, Brendan`）。OpenAlex 命中 arXiv:1602.05629（2016）属预印本年，**引用年应保持 2017**。 |
| [14] | `kairouz2021advances` | 作者列表截断 | 卷期页 **FnT ML 14(1–2):1–210, 2021** 与 Crossref `10.1561/2200000083` 一致。bib 用 `and others`；该文约 50+ 作者。IEEE 允许 *et al.*，但 TMC 长文常要求列出全部作者或至少前若干+DOI。 |
| [17] | `xie2019asynchronous` | 预印本年 ≠ 会明年 | bib 写 OPT **2020** + `arXiv:1903.03934`，正确。OpenAlex 只返回 arXiv **2019**。不要改成 2019，除非改引 arXiv 本身。 |
| [24] | `wang2024lightweight` | 预印本年 ≠ 会明年 | ICLR **2024**（FedAU）正确。arXiv:2306.03401 为 2023。Crossref 无 ICLR 记录属正常。 |
| [25] | `sun2025debiasing` | 预印本年 ≠ 会明年 | ICLR **2025** 正确（OpenReview `9h45qxXEx0`）。arXiv:2410.01209 为 2024。 |
| [29] | `liu2026multidimensional` | Early Access 元数据漂移 | DOI `10.1109/TDSC.2026.3652987` 可解析且标题作者匹配。Crossref 现为 TDSC **23(3):5058–5074, 2026**。bib 仍空卷期页 + Early access。 |
| [33] | `li2026stdfl` | Early Access 元数据漂移 | DOI `10.1109/TMC.2026.3673177` 匹配。Crossref 现为 TMC **25(9):13559–13576, 2026**。 |
| [35] | `karimireddy2020scaffold` | 中间名缺失 | PMLR **119:5132–5143, 2020** 正确。官方为 Reddi, **Sashank J.**；Stich, **Sebastian U.**。年 2020 是 ICML；arXiv:1910.06378 为 2019，不要改年。 |

Early-access 三条的建议字段（Crossref 现值）：

```bibtex
% [11] zhang2026mapt
volume={25}, number={9}, pages={14336--14351}

% [29] liu2026multidimensional
volume={23}, number={3}, pages={5058--5074}

% [33] li2026stdfl
volume={25}, number={9}, pages={13559--13576}
```

并删除对应 `note={Early access}`。

## 5. ✅ 已核实（34）— 摘要

作者、标题、年份、卷期、页码与出版方记录一致（允许 IEEE 缩写刊名、Title Case、以及 ACM article-number 写成 `1–N`）。

| # | Key | 核验要点 | 权威出处 |
|---|-----|----------|----------|
| [1] | `ganti2011mobile` | 49(11):32–39, 2011 | Crossref `10.1109/mcom.2011.6069707`（Crossref 略去中间名 K.；bib 更完整） |
| [2] | `guo2015mobile` | CSUR 48(1) Art. 7, 31 pages, 2015 | ACM `10.1145/2794400`；作者 7 人顺序正确 |
| [3] | `ma2014opportunities` | 52(8):29–35, 2014 | Crossref `10.1109/mcom.2014.6871666` |
| [4] | `wang2023outlier` | TNET 31(2):648–663, 2023 | Crossref `10.1109/tnet.2022.3201545` |
| [5] | `li2024robust` | TNET 32(5):3760–3775, 2024 | Crossref `10.1109/tnet.2024.3397309` |
| [6] | `wang2023transformer` | INFOCOM 2023, pp. 1–10 | Crossref `10.1109/infocom53939.2023.10228982` |
| [8] | `wang2025evolutionary` | TMC 24(3):1357–1371, 2025 | Crossref `10.1109/tmc.2024.3480983` |
| [9] | `xu2025rethinking` | TMC 24(6):5094–5105, 2025 | Crossref `10.1109/tmc.2025.3531362` |
| [10] | `liu2026pyramid` | TMC 25(1):1270–1286, 2026 | Crossref `10.1109/tmc.2025.3599322` |
| [13] | `yang2019federated` | TIST 10(2) Art. 12, 2019 | OpenAlex/ACM；作者 Qiang Yang 等 4 人 |
| [15] | `li2020federated` | SPM 37(3):50–60, 2020 | Crossref `10.1109/msp.2020.2975749` |
| [16] | `wang2026federated` | TMC 25(5):6784–6800, 2026 | Crossref `10.1109/tmc.2025.3640170`。与 [20] 页码接近但是**不同卷**，两边均被独立证实，不是串行。 |
| [18] | `liu2023adaptive` | TMC 22(2):674–690, 2023 | Crossref `10.1109/tmc.2021.3096846` |
| [19] | `sun2024staleness` | TMC 23(12):12621–12634, 2024 | Crossref `10.1109/tmc.2024.3416216`（首次查询误命中 supplementary） |
| [20] | `wang2023spatiotemporal` | TMC **22(11):6784–6799, 2023** | DBLP `journals/tmc/WangLLYYW23`；DOI `10.1109/tmc.2022.3195706`。Crossref 仍残留 EA 记录（年 2022、页 1–16）——**以印刷卷为准，bib 正确**。 |
| [21] | `wang2022unified` | NeurIPS 35:19124–19137, 2022 | Crossref `10.52202/068431-1390` |
| [22] | `jhunjhunwala2022fedvarp` | UAI / PMLR 180:906–916, 2022 | 标题作者匹配；OpenAlex 仅返回 arXiv:2207.14130 |
| [23] | `wu2023anchor` | ICML / PMLR **202:37379–37416, 2023** | PMLR `wu23e`。OpenAlex 把 `Gao, Jing` 解析成 `Jing, Gao` 为假阳性。 |
| [26] | `mohri2019agnostic` | ICML / PMLR 97:4615–4625, 2019 | 标题作者年匹配 |
| [28] | `liu2026pricing` | TSC 19(2):1062–1074, 2026 | Crossref `10.1109/tsc.2026.3664086`。作者顺序 Liu→Wang→Yang→Yang→Wu，**未颠倒**。 |
| [30] | `zhang2025incentive` | TDSC 22(4):3960–3976, 2025 | Crossref `10.1109/tdsc.2025.3542773` |
| [31] | `lu2025piece` | TIFS 20:9387–9398, 2025 | Crossref `10.1109/tifs.2025.3602314`。作者含 **Cao, Shuqin**（与 [27] 同人；[27] 写错、本条写对）。 |
| [32] | `zhang2026locally` | TKDE 38(2):1189–1205, 2026 | Crossref `10.1109/tkde.2025.3639070` |
| [34] | `li2020fedprox` | MLSys 2:429–450, 2020 | MLSys proceedings。OpenAlex 把 `Li, Tian` 颠倒为 `Tian, Li` 并落到 arXiv 2018，**假阳性**。 |
| [36] | `horvitz1952generalization` | JASA 47(260):663–685, 1952 | Crossref `10.1080/01621459.1952.10483446` |
| [37] | `hajek1971comment` | Godambe & Sprott (eds.), Holt, Rinehart and Winston, Toronto, **pp. 236–242, 1971** | MR0423625 / 多篇统计文献标准引文。Crossref 误命中 Basu 正文。 |
| [38] | `shimodaira2000improving` | JSPI 90(2):227–244, 2000 | Crossref `10.1016/s0378-3758(00)00115-4` |
| [39] | `byrd2019what` | ICML / PMLR **97:872–881, 2019** | PMLR `byrd19a`。标题含 `?` 导致 Crossref HTTP 400；人工核到正式出处。 |
| [40] | `ingelrest2010sensorscope` | TOSN 6(2) Art. 17, 2010；作者 6 人 | ACM `10.1145/1689239.1689247` |
| [41] | `barrenetxea2019sensorscope` | Zenodo dataset, 2019 | `10.5281/zenodo.2654726` 可解析（Crossref 对 DataCite DOI 返回 404 属预期） |
| [42] | `zheng2013uair` | KDD 2013, pp. 1436–1444 | ACM `10.1145/2487575.2488188`；USB proceedings `p1436.pdf` |
| [43] | `tfnsw2024traffic` | TfNSW Open Data Hub 数据集 | URL 仍有效（Last Updated 2026-08-03）。数据集无 DOI。 |
| [44] | `wilcoxon1945individual` | Biometrics Bulletin 1(6):**80–83**, 1945 | JSTOR `10.2307/3001968`（Crossref 只给首页 80） |
| [45] | `holm1979simple` | Scand. J. Statist. 6(2):65–70, 1979 | OpenAlex `10.2307/4615733` |

## 6. 🟢 Info（不计入 Needs fix）

- **大量 IEEE/ACM 条目缺 DOI。** 元数据本身正确。TMC 投稿建议给期刊/会议条目补 DOI（上表已列已知 DOI）。
- **刊名大小写 / 全称 vs 缩写：** 如 Crossref 的 sentence case 标题 vs bib 的 Title Case；IEEE 全称刊名。符合 IEEE 体例即可。
- **ACM article number：** [2] Art. 7、[13] Art. 12、[40] Art. 17 同时写 `pages={1--N}` 是 ACM 常见写法。
- **[1] Ganti 中间名：** bib 有 `Raghu K.`，Crossref 无 `K.` —— bib 更好，无需改。
- **[16] vs [20] 页码：** TMC 25(5):6784–6800 与 TMC 22(11):6784–6799 数值接近，两边均已独立核实，**不是复制粘贴错误**。

## 7. 查询失败与误匹配（方法学备注）

| 现象 | 处理 |
|------|------|
| Crossref 把 IEEE `_supp1-*.pdf` 当成独立 work | 过滤 `type=component` 后重查 |
| ICLR / MLSys / 部分 PMLR 不在 Crossref | OpenAlex + 会议官网 / PMLR |
| Zenodo DataCite DOI 在 Crossref 404 | 直接解析 `doi.org` / Zenodo |
| OpenAlex 西方姓名 `Last, First` 被反解析（`Li, Tian`→`Tian, Li`；`Gao, Jing`→`Jing, Gao`） | 以 PDF/PMLR/AAAI 页为准，不采机器 Critical |
| 书章节 Hájek 1971 | Crossref 命中 Basu 正文；改用标准统计引文 + MR 号 |

## 8. 建议行动（按优先级）

1. **必改（提交前）：** [7] 第四作者 `Xu, Yang`；[27] `Cao, Shuqin` 与 `Wang, Wei`。
2. **强烈建议：** [11]、[29]、[33] 用 Crossref 现卷期页替换 Early Access。
3. **可选：** [12] 补 `H. Brendan McMahan`；[35] 补 Reddi/Stich 中间名；[14] 决定保留 `et al.` 还是展开；给核心 IEEE 条目补 DOI。
4. **不要改：** [20] 的 2023 卷期页（Crossref EA 残条是错的）；[16] 页码；[17]/[24]/[25]/[34]/[35] 的会议正式年份。

未改 `reference.bib`。若需要，可按第 3–4 节直接打补丁并重编 `bibtex`。
