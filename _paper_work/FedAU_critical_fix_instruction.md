# Cursor 执行指令：修复 FedAU 回填引入的两个 Critical 问题

> 论文当前含 FedAU-Window 回填，但有两处必须修的缺陷。本指令给出**精确的旧文本→新文本**，Cursor 只需做字面替换，不要自由改写。改完重编译校验。

---

## 目标文件

`D:\Cursor\raven.mcs\_paper_work\main.tex`

（这是当前工作稿。不要动 `paper_tmc_r1\main.tex`。）

---

## Critical #1：结构段落自相矛盾（必改）

**问题**：§VI-B 结构段现在写"RAVEN 的两个结构指标 Holm-显著低于**六个**同骨干基线"——但 FedAU（第六个基线）在 U-Air 的 `Δ_group=1.0557` **低于** RAVEN 的 `1.0924`，所以"低于六个基线"与论文自己的 Table III 矛盾。

**精确替换**（把 "six" 改回 "five"，并显式列出那五个非重加权基线）：

旧文本（old_string）：

```
than those of each of the six same-backbone baselines.  Fig.~\ref{fig:e3_structural}
```

新文本（new_string）：

```
than those of each of the five non-reweighting same-backbone baselines
(FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hajek, TwoStage-Hajek).  Fig.~\ref{fig:e3_structural}
```

> ⚠️ **不要改** Table III 的 caption（那里 "six same-backbone baselines" 是对的，指图里有 6 个基线）。只改这一句。

---

## Critical #2：FedAU 混合结果缺机制解释（强烈建议）

**问题**：结构段报告了"Δ_c-s 上 RAVEN 显著优于 FedAU，但 U-Air 上 Δ_group/预测是 FedAU 更低"，却没解释**为什么**。审稿人会问原因。

**精确替换**（在现有 FedAU 对比句结尾追加一句机制解读）：

旧文本（old_string）：

```
to the finer client--stratum objective rather than a blanket dominance.
```

新文本（new_string）：

```
to the finer client--stratum objective rather than a blanket dominance.
This contrast has a clean mechanism interpretation.  Participation reweighting
can improve prediction when update-side censoring dominates, as it does on
U-Air, but it rescales whole clients without reconstructing the sensing-side
strata, so it degrades the finer client--stratum composition on both datasets.
RAVEN's layered correction targets exactly the strata that participation
reweighting leaves uncorrected, which is why the two methods separate cleanly
on $\Delta_{c\text{-}s}$.
```

---

## （可选，非 critical）同段 RQ2 答案句补全

为让"consistently"不被误读成"对 FedAU 也全胜"，可再做一处小改：

旧文本：

```
including a significant gain in the finer client--stratum alignment over the
participation-reweighting baseline FedAU-Window.
```

新文本：

```
including a significant gain in the finer client--stratum alignment
$\Delta_{c\text{-}s}$ over the participation-reweighting baseline
FedAU-Window, though not in $\Delta_{\mathrm{group}}$ on U-Air.
```

---

## 改完后的校验（必须做）

在 `_paper_work` 目录下重编译：

```
C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
C:\texlive\2026\bin\windows\bibtex.exe main
C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
C:\texlive\2026\bin\windows\pdflatex.exe -interaction=nonstopmode main.tex
```

检查 `main.log`：

1. `Output written on main.pdf (N pages...)`（页数应与改前接近，约 23 页）。
2. `!` 错误数 = 0。
3. `undefined` 引用数 = 0。
4. `Overfull` 数量 = 0（若新增机制句导致超宽，检查后处理，一般不会）。

**自检清单（改完读一遍）**：

- 结构段里现在说的是"five non-reweighting baselines"，且显式列出那五个名字；
- FedAU 对比句仍在，且既说了 Δ_c-s 优势、也说了 U-Air Δ_group/预测是 FedAU 更低；
- 新增机制句解释了"为什么参与重加权在 Δ_c-s 上更差、在 U-Air 预测上更好"；
- 没有任何"RAVEN 全面优于 FedAU"的绝对化表述。

---

## 完成标准

- Critical #1 已修（"six"→"five non-reweighting ..."）。
- Critical #2 已修（机制解释句已加）。
- 重编译通过（0 错误、0 undefined、0 overfull）。
- 论文无"表与自己矛盾"的声称。
