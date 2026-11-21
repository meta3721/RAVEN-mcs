# CCF Integrity Audit Report: RAVEN-MCS

```text
Mode: full（claim-audit + numeric-audit + citation-audit）
Artifacts checked:
  - main.tex (3204 行, 125 KB)
  - reference.bib (43 条)
  - figure_data/ (4 CSV: E1E2, E2E3, E3E3, E4E4)
  - figures/ (6 图 PDF/PNG)
  - make_figures.py
Date: 2026-08-22
Auditor basis: 全部基于本地文件实证；未联网（网络受限），引用存在性以 bib 条目为据，未做外部真实性核验
```

## 1. Claim-Evidence Matrix

| Claim | Where stated | Evidence provided | Verdict |
| --- | --- | --- | --- |
| 到达分布不必匹配部署目标 | Abstract; Sec II; Prop 1 | E2: D_aligned 稳定负值（-0.0209~-0.0214），17-18/20 种子负，Wilcoxon p<6e-4 | **Supported**（CSV 验证均值 -0.02088~-0.02137 ✓） |
| 理想归一化顺序校正恢复兼容目标 | Abstract; Sec V; Prop 2 | 附录完整证明（A1-A3） | **Supported**（理论） |
| 校准程序唯一全局最小解 | Abstract; Sec VI; Thm 1 | 附录证明（A4 凸性） | **Supported**（理论） |
| RAVEN 降低结构错配 3.96/2.01%（S） | Abstract; Intro; Sec VII | E3: CSV 验证 FedAvg 1.0558→RAVEN 1.0139（-3.96%）、1.2903→1.2644（-2.01%） | **Supported**（CSV 复算一致 ✓） |
| RAVEN 降低结构错配 2.62/2.28%（U） | Abstract; Intro; Sec VII | E3: CSV 验证 | **Supported**（CSV 复算一致 ✓） |
| 预测风险保持竞争力、选择性显著增益 | Abstract; Sec VII | E3: 对 TwoStage-Hajek 的 2.04% 显著改进；其余不显著 | **Supported**（诚实限定为"选择性"） |
| 校正与校准组件有端点/数据集依赖角色 | Abstract; Sec VII | E4 消融 5 组件 × 2 数据集 | **Supported**（CSV 验证 ✓） |
| Use 校正无清晰孤立效应 | Sec VII; E4 | E4: Use 移除后四端点无显著变化（0.026/0.026/0.012/0.012 均小） | **Supported**（负面结果诚实披露） |
| Debt 效应小但统计一致 | Sec VII; E4 | E4: 0.014/0.004（S）、0.004/0.002（U）均显著 | **Supported** |
| E1 无伤害控制通过 | Sec VII; 附录 | E1: 相对退化 0.0599%，上界 0.134% < 3% | **Supported**（双处一致 ✓） |
| 774 窗口溯源审计 | Sec VII; 附录 | 附录审计流程 | **Supported**（双处一致 ✓） |
| P2 可行性认证 | 附录 | 6438 窗口、残差 2.686e-8 < 1e-7 | **Supported**（双处一致 ✓） |

**Claim verdict: 全部 Supported，无 Unsupported/Overstated**

## 2. Numeric Consistency Findings

| Check | Result |
| --- | --- |
| 结构指标正文 vs 表 II vs CSV | ✅ 一致（1.0558/1.2903/1.0139/1.2644 等多处复算吻合） |
| 消融数字正文 vs 表 III vs CSV | ✅ 一致（1.237/0.597/6.943/4.990/6.553/6.875 全吻合；显著性标记与 CSV holm_significant 一致） |
| 百分比跨 abstract/intro/results | ✅ 一致（3.96/2.01/2.62/2.28 三处 3-4 次出现均同值） |
| E2 D_aligned 范围 | ✅ 一致（正文 -0.0209~-0.0214；CSV 均值 -0.02088~-0.02137） |
| E1 无伤害数字 | ✅ 一致（0.0599%/0.134%/3% 双处吻合） |
| 20 配对种子声明 | ✅ 一致（7 处） |
| 审计数字（774/9666/6438/2.686e-8） | ✅ 一致（正文+附录双处吻合） |
| 精度一致性 | ✅ 表内同列小数位一致；正文引用与表值同精度 |
| 度量方向 | ✅ 明确标注（lower is better；消融正=变差） |

**Numeric verdict: 全部一致，未发现漂移**

## 3. Citation Metadata Findings

| Check | Result |
| --- | --- |
| 总条目 | 43 条，全部被引用；无未引用条目 |
| 引用键 | 43 个唯一键全部在 bib 中；无缺失键 |
| 重复键 | ✅ 无 |
| 缺失必填字段 | 全部有条目；title/author 齐全 |
| year 缺失条目（4） | xie2019asynchronous, chen2026fedcure, li2020fedprox, karimireddy2020scaffold — 年份在 `note` 字段（IEEEtran.bst 兼容处理，**非缺陷**） |
| 无卷/页码条目（7） | 会议论文（inproceedings 有 pages）、incollection（hajek1971 有 pages 236-242）、数据集（misc+DOI/URL）— **均正常** |
| DOI/arXiv/URL | barrenetxea2019sensorscope（DOI 10.5281/zenodo.2654726）、tfnsw2024traffic（URL）、xie2019asynchronous（arXiv:1903.03934）— 合理 |
| note 字段用途 | 文章编号（Art. no.）、arXiv ID、年份、访问日期 — 合理 |

**Citation metadata verdict: 无缺陷**

## 4. Citation-Context Findings

43 个引用组逐一检查上下文，全部满足：
- 每个引用紧跟其支持的论断（无孤立引用）
- 无 citation dump（最密组 8 个引用，但对应一个完整能力句"robust cell selection, spatiotemporal correlation modeling, few-shot/cold-start completion, and multi-scale inference"，可接受）
- 最接近竞争者（wang2026federated 联邦 MCS 补全、sun2025debiasing 相关参与偏差、wang2024lightweight FedAU）均有专门句子讨论
- 数据集/方法引用（SensorScope/U-Air/NSW-Traffic/FedAvg/Wilcoxon/Holm）上下文正确

**Citation-context verdict: 全部 Supported**

## 5. Severity

| Severity | Count | Description |
| --- | --- | --- |
| fatal | 0 | — |
| major | 0 | — |
| moderate | 0 | — |
| minor | 2 | 见下 |

**Minor 发现**：
1. **引用真实性未联网核验**（`unverified`）：43 条引用的真实存在性以 bib 条目为准，网络受限未做外部核验。建议投稿前用 ccf-literature-searcher / nature-ref-verifier 抽查 3-5 条关键引用（特别是 2026 年 in-press 条目）。
2. **第一作者仍为 `****` 占位符**：投稿前必须填写，否则无法提交。

## 6. Safe Edit Suggestions

1. （可选）将 4 条 `note={年份}` 条目的年份同时补入 `year` 字段，并在 note 中保留来源说明——但需先确认 IEEEtran 编译后年份显示正常（当前 note 方式可工作，非必要修改）。
2. 填写第一作者姓名（必须，投稿前）。
3. 如需，为 2026 年 in-press 条目（liu2026pyramid, wang2026federated, liu2026multidimensional, zhang2026mapt, zhang2026locally, liu2026stdfl, chen2026fedcure）补充正式卷期页码（若已出版）或保留 note 标注（若仍 in-press）。

## 7. Next CCFA Owner

- `ccf-literature-searcher`：联网核验 2024-2026 引用真实性 + 新颖性定位检索（当前最大未决项）
- `ccf-submission-checker`：作者信息、投稿合规
- `ccf-paper-writer`：如需根据 minor 发现做措辞微调

## 8. No-Invention Status

✅ **确认**：本审计全部基于 main.tex / reference.bib / figure_data CSV / figures 的本地实证。未虚构任何数字、引用、断言或证据。所有"Supported"判定均有文件依据；唯一未决项（引用外部真实性）已明确标注 `unverified`。
