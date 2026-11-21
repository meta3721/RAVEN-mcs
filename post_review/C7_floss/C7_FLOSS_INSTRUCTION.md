# 指令：关闭 C7（FLOSS cite-and-split + FedPALS 书目核对）

本文件是 **ccf-literature-searcher + ccf-paper-writer** 执行授权。  
把下面整段交给执行 AI。**不是**训练、不是作者栏、不是压页、不是改 Table II。

审稿表（`ccfa-review-reports/raven-mcs-tmc-review.md`，2026-09-10）：

| ID | 严重度 | 缺口 | 本轮产物 |
|---|---|---|---|
| C7 | minor | FLOSS 未引；FedPALS bib 可能过期 | Related Work 对象分裂引用；书目与公开记录对齐 |

**不要**把 C7 当成作者占位符。作者栏 `**** and Anfeng Liu` 是 **C5**，本轮禁止改 `\author`。

```text
You are the C7 related-work closer for repo C:\Cursor\raven.mcs.
Read this entire file before editing.
Canonical manuscript: TO_OVERLEAF_paper_tmc_r1_clean/main.tex
Canonical supplement: TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex
Bibliography: TO_OVERLEAF_paper_tmc_r1_clean/reference.bib
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
Skill: ccf-literature-searcher + ccf-paper-writer + ccf-humanization
Do not train. Do not retune phi, p_obs, s_max, grid, or Design from RMSE.
Do not overwrite tdrive_protocol_seal_r1/.
Do not change any Table II / tab:tdrive_hybrid numeric cell.
Do not mix T-Drive into tab:main_effectiveness.
Do not set Design_t := Gate_t.
Do not restore formal non-inferior.
Do not edit \author or C5 placeholders.
Do not run FLOSS, FedIPW, or FedPALS as comparators.
Do not add a FLOSS/FedPALS numbers row to any results table.
Do not commit unless the human asks.
```

---

## 0. 审稿要关的点（分析冻结）

C7 是 **定位 / Related Work**，不是实验缺口。

- FLOSS（Goetze, Felten, Albrecht, Bhattacharya；PACMI 2025；ACM `10.1145/3766882.3767180`）做 **client 名册上的 opt-out / straggler IPW**。与本文化的 MCS **单元级 R/O/U** 对象不同。审稿明确：workshop 论文，**不是**必须可执行的 MCS 基线；一句引用 + 对象分裂即可。
- FedPALS（Listo Zec et al.）做 **标签边际** 上的 target-aware 凸聚合。已引用；审稿只要求核对该公开版本是否已从 2024 preprint 升格。OpenReview `dQAsAmb1Xb` 在本指令起草时仍是 **TMLR Paper 7972 submission**，不是已发表 TMLR 卷期。不得编造 volume/pages。
- 关闭 C7 **不会**把 Overall 从 5 拉上去（审稿：Unlikely to move Overall）。不要为 C7 扩 Related Work、不要加第三段免责。

**与相邻编号的边界**

| ID | 本轮 |
|---|---|
| C5 作者栏 | 禁止 |
| C6 压到 ≤18 页 | 禁止借 C7 砍 FedIPW/FedPALS/FLOSS 对象句；也禁止为 C7 加段 |
| C11 出租车许可证 / FL≠privacy | 禁止 |
| C3 非劣措辞 | 禁止重开 |

---

## 1. 写前核对（不通过则停）

1. `tab:main_effectiveness` 四个 SCD 格仍是 `7.9380` / `1.0139` / `1.1131` / `1.0165`。
2. `\author` 仍是 `**** and Anfeng Liu`（不要“顺手补全”）。
3. 先 grep 工作副本（大小写不敏感）：

```text
FLOSS
goetze2025floss
listozec2024overcoming
```

**分支 A — 正文已有 cite-and-split（当前工作树就是这样）：**  
`main.tex` Related Work 已有 FLOSS 两句 + FedPALS 标签边际分裂；`appendix.tex` `tab:nearest_neighbor` 已有 FLOSS 行；`reference.bib` 已有 `@inproceedings{goetze2025floss}`（DOI `10.1145/3766882.3767180`）。  
本轮 **不要再加一段**。只做 §3 书目封口 + §4 核对句是否仍对象正确。若对象句已正确且 bib 已对齐公开记录：写报告宣布 **C7 CLOSED**，允许 0 行正文 diff。

**分支 B — 正文没有 FLOSS：**  
按 §2 插入 **至多两句**，紧挨现有 FedIPW 段落后。不要新开 subsection。

4. 公开检索只用 ACM / arXiv / dblp / OpenReview。排除 MDPI。不要把 FLOSS 写成 TMC/ICML 必比基线。

---

## 2. 若需补写：对象分裂句（分支 B）

允许的科学内容（不要改主张）：

- FLOSS 校正 **client opt-out / straggler** 造成的参与缺失；本文化对象是 **sensing-unit R/O/U** 相对公开部署测度 \(h(i)\)。
- FLOSS 与 FedIPW 同属 client-roster 参与校正；不是 MCS 完成基线；**不跑**。
- FedPALS 的 “target” 是 **class-label marginals**，不是 MCS 机会/观测，也不是 \(\mu\) on \(h(i)\)；**不跑**。

禁止写成：FLOSS 是最近 MCS 基线；FLOSS 支持本文化 Design 开关；FLOSS/FedPALS 数字；“to address reviewer C7”。

英文：直接学术陈述；不要 em dash（LaTeX `---`）；不要把内部标签 `C7` 写进正文。全文 em dash 仍 ≤ 3。页数：只换词或至多两句，不扩 Related Work。

附录 `tab:nearest_neighbor`：若还没有 FLOSS 行，加一行  
`FLOSS | client roster | opt-out / straggler | no | no`  
不要把该表并进 Table II。FedPALS 行可选；若加，Target 列必须是 label marginals，不是 \(\mu\)。

---

## 3. 书目封口（两分支都做）

### 3.1 FLOSS — 冻结记录（起草时核对）

公开记录：

- ACM DOI `https://doi.org/10.1145/3766882.3767180`
- arXiv `2507.23115`（可作 `eprint`，**主入口仍是 ACM inproceedings**）
- PACMI '25，Workshop on Practical Adoption Challenges of ML for Systems
- 会议日期 2025-10-13–16，Seoul, Republic of Korea
- ISBN `979-8-4007-2205-9`

`goetze2025floss` 保持 `@inproceedings`。可补 `publisher={ACM}`、`address={Seoul, Republic of Korea}`。  
若 ACM 记录现有 pages / article number，抄进去；没有就不要编。作者必须含 Goetze, Felten, Albrecht, Bhattacharya。

### 3.2 FedPALS — 仍可能是 preprint

起草时：

- arXiv `2411.03799`（公开页有 v2，约 2025-08-26）
- OpenReview `https://openreview.net/forum?id=dQAsAmb1Xb` = TMLR Paper 7972 **submission**
- **没有**已发表 TMLR 卷期

执行时再打开上述 OpenReview。决策：

| 公开状态 | bib |
|---|---|
| 仍是 submission / under review | 保持 `@misc{listozec2024overcoming}`；`howpublished={arXiv preprint arXiv:2411.03799}`；`note` 可写 `TMLR submission (OpenReview: dQAsAmb1Xb)`。不要写 “published in TMLR”。 |
| 已 accept/published 且有 volume 或 TMLR 年 | 升为 `@article`，填真实 volume/year/url。不确定则 **停，问人**。 |
| 只有更新的 arXiv vN | 可在 note 写 latest arXiv version；不要改 key。 |

不要新增第二个 FedPALS key。不要把 FedPALS 写进主文方法矩阵。

---

## 4. 成功条件

1. `main.tex` 对 `FLOSS` / `goetze2025floss` 至少 1 处，且同一段落写明 **client-level** vs **MCS unit-level R/O/U**。
2. `appendix.tex` `tab:nearest_neighbor` 有 FLOSS 行（或报告说明已有）。
3. `reference.bib`：`goetze2025floss` DOI 为 `10.1145/3766882.3767180`；FedPALS 条目与 OpenReview/arXiv **当前**公开状态一致。
4. 正文 **0** 处声称跑过 FLOSS/FedPALS，或把它们当 Table II 方法。
5. Table II 数字、`\author`、`eq:scd_phi`、Gate≠Design 未改。
6. 报告：`post_review/C7_floss/C7_REPORT.md`（分支 A/B、bib 是否改、OpenReview 状态、grep 计数）。

---

## 5. 明确不要做

- 训练；实现 FLOSS IPW；把 FedPALS 接到 P2。
- 为“补文献”再扫一页 Related Work。
- 把 25.5% 写成 train-unit \(\phi\)。
- 改 C5 作者、C6 压缩、C11 许可证。
- 提交 / push。

预计墙钟：**30–60 min**（分支 A 更短）。不是实验轮。
