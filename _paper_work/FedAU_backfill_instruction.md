# Cursor 执行指令：把 FedAU-Window 结果回填进论文

> 前提：上一份「FedAU 基线实验」已经跑完，产出了含 `fedau_window` 的结果 CSV 和两组 Holm 统计。
> 本指令把结果写回论文，并做完整性校验。所有数字必须来自真实 CSV，绝不伪造。

---

## 0. 输入文件（认准这些）

- **论文工作稿**：`D:\Cursor\raven.mcs\_paper_work\main.tex`
  （这是当前版本，已含 M1/M3 贡献重述、摘要/结论润色、E2 表格 resizebox 修复。
  **不要**改 `paper_tmc_r1\main.tex`——那是旧的 r1 源。）
- **FedAU 结果**：上一份实验跑出的 CSV（含 `fedau_window` 的 `RMSE_mu / Tail_RMSE / Delta_group / Delta_c_s`，20 种子）+ 两组配对 Wilcoxon/Holm 结果（RAVEN-vs-FedAU、FedAU-vs-FedAvg）。
- **引用**：FedAU 的 bib key 是 `wang2024lightweight`，已在 `reference.bib` 中（related work 已引用），回填时直接 `\cite{wang2024lightweight}`。

---

## 1. 回填位置（按顺序改 6 处）

### (1) §II.C Related Work（FedAU 已引用的那段，约 314–318 行）
在 "FedAU \cite{wang2024lightweight} is particularly relevant..." 这句之后补一句：

```latex
FedAU is evaluated as a windowed participation-reweighting baseline in
Section~\ref{sec:evaluation}.
```

### (2) §VI-A 基线清单（约 1458–1470 行）
在 TwoStage-H\'ajek 那句之后、Inst-Cal/Debt-Cal 之前，加入 FedAU-Window，并注明非官方复现：

```latex
... TwoStage-H\'ajek (the same H\'ajek family applied sequentially to the
opportunity and observation layers), and FedAU-Window (our windowed adaptation
of the participation-reweighting method of~\cite{wang2024lightweight}, not an
official reproduction of that system).  We additionally report Inst-Cal and
Debt-Cal to expose the transition from reconstruction to calibration.
```

### (3) Table III（主 E3 表，约 1578–1617 行）
给 **SensorScope 和 U-Air 各加一行 FedAU-Window**（traffic 不加，与论文「traffic 不用于方法级推断」一致）：

- 用真实数字填 `RMSE_mu / Tail RMSE / Delta_group / Delta_c-s`（mean ± std，20 种子）。
- 数值精度与表中其它行统一（3 位小数；若与 Debt 段落 4 位冲突，先统一精度，见 §3）。
- 若标注「RAVEN 对 FedAU 显著」，必须与 Holm 结果一致；不显著就不标，或标 `n.s.`。

（若你更想单独成表，可用上一份指令里的 `tab:e3_fedau` 模板；否则并入 Table III 更简洁。**二选一，不要重复两处。**）

### (4) §VI-B RQ2 叙事（约 1566–1671 行）
补 1–2 句，**只写数据支持的**：

- FedAU vs FedAvg：参与重加权是否改善了 `\Delta_{c-s}`（用于确认 FedAU 基线本身有效）。
- RAVEN vs FedAU：RAVEN 的 `\Delta_group`、`\Delta_c-s` 是否显著更优（三层感知侧修正 + 校准 是否强于 仅参与重加权）。

**关键**：若 RAVEN 对 FedAU **不显著**，必须如实写为 limitation，**不得**写成优势。

### (5) 图 fig3 / fig4（推荐做）
- 把 `fedau_window` 加进 `make_figures.py` 的 `E3_METHODS` 和 `E3_SHORT`（短标签建议 `FedAU`）。
- 把 FedAU 行加进 `figure_data/FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv` 和 `figure_data/FIG_E3_E3_PREDICTION_RISK.csv`。
- 重新生成 fig3、fig4（PDF + PNG，输出到 `figures\`，文件名不变）。

### (6) §VII Discussion（可选）
- 若 RAVEN 结构优势显著，加一句「相对仅参与重加权，感知侧逐层修正 + 可行性校准是必要的」。
- 若不显著，写入 limitation（与 §VI-B 一致）。

---

## 2. 诚实红线（务必遵守）

1. 只填真实数字；缺的格子写 `TBD` 并说明缺失原因，**绝不编数字/编显著性/编排名**。
2. 保留 claim ceiling：不写「普遍优于 / 全面超越」；不把「不显著」写成「显著」。
3. 保留「windowed adaptation, not an official reproduction」措辞（与 TimeAlign-Agg 一致）。
4. **不要改头号数字** `3.96%/2.01%`、`2.62%/2.28%`（它们是相对 FedAvg 的，加 FedAU 不影响）。

---

## 3. 回填后校验（必须做）

1. **重编译**（在 `_paper_work` 下）：
   ```
   C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
   C:\texlive\2026\bin\windows\bibtex.exe main
   C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
   C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
   ```
   检查 `main.log`：`Output written on main.pdf (N pages...)`；`!` 错误数 = 0；`undefined` 引用数 = 0；记录 `Overfull` 数量（新增表格可能超宽，若超宽用 `\resizebox{\columnwidth}{!}{...}` 处理，参照 E2 表的做法）。

2. **数字一致性**：新 FedAU 数字在 **表 ↔ 正文 ↔（若涉及）结论** 三处一致；精度统一（3 位或 4 位，选一种，全表/全文一致）。

3. **引用完整性**：确认 `\cite{wang2024lightweight}` 能解析（在 reference.bib）。

4. **图一致性**：确认 fig3/fig4 重新生成后 `\includegraphics` 路径与文件名不变，编译通过。

---

## 4. 输出

- 更新后的 `main.tex`
- 更新后的两个 CSV + 重新生成的 fig3/fig4（PDF+PNG）
- 一段总结：「回填了哪几处 + 每处改动的证据来源（CSV 哪列）+ RAVEN-vs-FedAU / FedAU-vs-FedAvg 是否显著」

---

## 5. 完成标准

- FedAU 已出现在：related work、基线清单、Table III（或单独表）、RQ2 叙事；
- 所有数字来自真实 CSV，无编造；
- 重编译通过（0 错误、0 undefined）；
- 若 RAVEN 对 FedAU 不显著，limitation 已写且**未声称优势**。
