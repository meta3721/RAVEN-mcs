# 指令：方向 1 — 把 FedAU-Window / ObsUse-Window / TimeAlign-Agg 改编写死

这是 **规格诚实**，不是官方 FedAU 复现，不是方向 2（贴原文的 window port / 重训）。

GPT 审稿要的是：FedAU-Window、ObsUse-Window、TimeAlign-Agg 是改编，不是官方实现；给出精确策略和同一计算预算。现有数字已经在表里。本轮只把代码里的公式写进附录，让改编可核对。

**本轮默认不训练、不改任何表数字。**

把下面整段交给执行 AI。先读完本文件再改稿。

```text
You are the Direction-1 adapted-baseline spec executor for repo C:\Cursor\raven.mcs.
Read this entire file before editing.
Use CCFA-Skills/ccf-paper-writer (humanization preflight first; then prose-quality-guardrails).
Canonical manuscript:
  TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex
  TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
pdflatex: C:\Users\szr\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe

This round WRITES the implemented windowed policies. It does NOT retrain.
It does NOT authorize:
  claiming an official FedAU / ObsUse / TimeAlign / FLAMF reproduction
  Direction 2 (client-equal 1/p port, official estimator rewrite, new ranking)
  mixing any new row into Table II / tab:main_effectiveness
  editing numeric cells in T-Drive, NSW, XXI, XXII, E4, INT-R
  changing phi, Design on/off, Gate, SCD, P2, or EventTraces
  overlaying FEMNIST / FLASH / GPS participation onto MCS Y
  restoring OFF as target-mass reconstruction
  mentioning C1/C2/C3/C4, GPT, kill-bar, CLARABEL, or reviewers in the manuscript
  changing author placeholders
  committing unless the human asks

Paper method remains support-conditional Design: ON iff phi=0.
When Design is off, zeta=1 is an uncorrected opportunity factor.
Keep main.pdf = 14 pages and supplemental.pdf = 13 pages.
Copy the formulas from the cited source files. Do not "improve" the counters.
```

---

## 0. 停手条件

停手并问人（不要自己发明公式或开训）：

- 代码与本文件 §1 对不上，且无法从源文件读出唯一实现。
- 需要改 `src/`、配置、种子、或重跑 E3/E4/T-Drive 才能「对齐原文 FedAU」。
- 想把官方 FedAU 的 FEMNIST/CIFAR 结果写进 MCS 表。
- 主 PDF 到 15 页且压不回 14，或 supplemental 到 14 页且压不回 13。

---

## 1. 已核对的实现（写稿必须抄这个，不要改成「更像原文」）

权威源码（只读）：

- `src/raven_mcs/aggregation/methods.py`：`FedAUWindowAggregator`, `ObsUseWindowAggregator`, `FLAMFTimeAlignAdaptedAggregator`
- `src/raven_mcs/training/window_runner.py`：`_lagged_participation_rates`, `_client_observation_rates`, `_update_lagged_estimators`, `raw_counts`
- `src/raven_mcs/aggregation/method_policy.py`：`fedau_window`, `obsuse_window`, `flamf_timealign_adapted` / `timealign_agg`
- `configs/method/fedau_window.yaml`, `obsuse_window.yaml`, `timealign_agg.yaml`

聚合只在窗口关闭时发生一次。配对方法共用同一 EventTrace、同一 Common-NDMF 骨干。E3/E4 为配对种子 30001–30020。E1 为 5 个种子。没有按测试 RMSE 调选择过程。

### 1.1 公共量

对窗口 \(r\) 的聚合集 \(\mathcal{A}_r\) 中客户端 \(k\)：

- \(n_{k,r}\) = `raw_counts` = 该客户端本窗观测指示之和 \(\sum O\)（缺数据时代码写 1.0）。
- 计数器在**本窗聚合之后**才更新，所以本窗用的参与率是严格滞后、pre-outcome。

滞后参与计数（`_update_lagged_estimators`，按 EventTrace **record** 累加，不要改成「每窗每客户端只加一次」）：

- 本窗结束后，对该窗中客户端 \(k\) 的每条 record：\(N^{\mathrm{att}}_k \leftarrow N^{\mathrm{att}}_k+1\)。
- 若该 record 满足 `attempted=1` 且 \(U=1\)：\(N^{\mathrm{use}}_k \leftarrow N^{\mathrm{use}}_k+1\)。
- \(\varepsilon=10^{-6}\)。
- 本窗使用
  \[
  \widehat p^{\mathrm{part}}_{k,r}
  =
  \frac{N^{\mathrm{use}}_k+\varepsilon}{N^{\mathrm{att}}_k+\varepsilon}
  \]
  其中右侧计数来自 \(r\) **之前**已关闭的窗口。未见过的客户端：\(0+\varepsilon\) 对 \(0+\varepsilon\)，故 \(\widehat p^{\mathrm{part}}=1\)。

观测率（仅 ObsUse；`p_min=0.05`）：

- \(\widehat p^{\mathrm{obs}}_{k,r}\) = 客户端当前 risk set 上 `p_hat_model` 的均值，逐元素先 \(\max(\cdot,0.05)\)。
- 空 risk set：代码设为 1.0。

归一化：非负权重除以总和，和为 1。

### 1.2 FedAU-Window（`fedau_window`）

\[
\alpha_{k,r}
\propto
n_{k,r}\big/\widehat p^{\mathrm{part}}_{k,r},
\qquad
\widehat p^{\mathrm{part}}_{k,r}\leftarrow\max(\widehat p^{\mathrm{part}}_{k,r},\varepsilon).
\]

**明确不用：** Design / \(\widehat\zeta\)、观测 IPW、Hájek 局部损失、P2、债务、variance/staleness 惩罚。  
Policy：`uses_usable_ipw=True`，其余默认 False。  
这是把 FedAU 的「用参与历史估聚合权重」改编到窗口关闭 MCS 聚合；对齐的是 usable-update 层，不是原文的 FedAvg 目标，也不是官方代码。

### 1.3 ObsUse-Window（`obsuse_window`）

\[
\alpha_{k,r}
\propto
n_{k,r}\big/\bigl(\widehat p^{\mathrm{obs}}_{k,r}\,\widehat p^{\mathrm{part}}_{k,r}\bigr).
\]

相对 FedAU-Window：**多一层观测逆加权**。仍然不用 Design、P2、债务。  
Policy：`uses_observation_ipw=True`, `uses_usable_ipw=True`。

### 1.4 TimeAlign-Agg（canonical id `flamf_timealign_adapted`；别名 `timealign_agg`）

对 \(\mathcal{A}_r\) 中客户端覆盖的时间槽集合 \(S_k\)，令 overlap\((s)=\#\{j\in\mathcal{A}_r:s\in S_j\}\)。

\[
\alpha_{k,r}
\propto
\sum_{s\in S_k}\frac{1}{\mathrm{overlap}(s)}.
\]

**不用** \(n_{k,r}\)，不用 Design/观测/usable IPW，不用 P2/债务。总 credit 为 0 则实现报错（已跑通的表里未发生）。  
这是 teacher-frozen 时间覆盖改编，spirit of Wang et al. 异步时间感知聚合，**不是** FLAMF 官方复现。`flamf_original` 是未接入 stub，禁止写进任何结果表。

### 1.5 同一预算（必须写进附录，不要编造 GPU 小时）

只写稿上和 runner 已有的公平约束，不要发明未测量的 wall-clock：

- 同一 Common-NDMF 骨干与步长；
- 配对方法共享同一记录的选择 trace；
- E3/E4：20 配对种子 30001–30020；T-Drive / City Scanner / NSW 各用其已公布的种子与窗数；
- 不在测试集上调选择过程、组、层、或超参；
- FedCure 未实现，保持「not included」。

---

## 2. 要改的文件与落点

只改 canonical Overleaf 三个 tex。不要改 `tdrive_protocol_seal_r1/`、公开包 CSV、Table II 源。

### 2.1 附录（主交付）

在 `appendix.tex` 的 `\subsection{Deferred Constructions from the Main Text}` 内、`app:itar_lookup` 那段之后、`Proof of Proposition~1` 之前，新增：

```latex
\subsubsection{Windowed adaptations of FedAU, ObsUse, and TimeAlign}
\label{app:adapted_baselines}
```

内容必须包含：

1. 一句 claim ceiling：这些是窗口关闭改编，不是官方复现；FedAU 原文对齐的是未知参与下的原 FL 目标，这里对齐的是 usable-update（及 ObsUse 的观测层）。
2. FedAU-Window 公式（§1.2）+ 滞后计数（§1.1）。
3. ObsUse-Window 公式（§1.3）及与 FedAU 的差分（多 \(\widehat p^{\mathrm{obs}}\)，仍无 Design/P2/债务）。
4. TimeAlign-Agg 公式（§1.4）+ canonical id `flamf_timealign_adapted`。
5. 同一预算子弹（§1.5）。
6. 一句：表中数字仍是这些改编的已有结果，本附录不引入新 ranking。

不要贴 Python。不要写仓库路径。不要写 `confirmed` / `publication-ready`。不要 em dash。不要内部工程标签。

### 2.2 主文（只换句，不加段）

`main.tex` 约 1447–1452 行现有：

```text
FedAU-Window adapts participation debiasing ... Neither is an official reproduction.
```

**替换**为同等长度、指向附录的句子，例如：

```latex
FedAU-Window adapts participation debiasing
\cite{wang2024lightweight} to window-close aggregation:
\(\alpha_{k,r}\propto n_{k,r}/\widehat p^{\mathrm{part}}_{k,r}\) with a lagged
usable/attempt rate (Appendix~\ref{app:adapted_baselines}).
ObsUse-Window further divides by a lagged observation rate and still omits
Design, P2, and debt.  TimeAlign-Agg uses timestamp-overlap credits on the
same backbone.  None is an official reproduction.
```

不要在摘要/引言再抄一遍公式。不要改 Table II 表注里已有的 “windowed adaptations” 句，除非需要加一个 `\ref{app:adapted_baselines}` 且不增加行数。

`tab:nearest_neighbor` 已写 “windowed implementations, not official reproductions”。可在 caption 末加 `See Appendix~\ref{app:adapted_baselines}.` 若因此 overflow，则只保留主文+新附录，不动该 caption。

### 2.3 supplemental.tex

只在需要续编号时检查；标题不要改回 Target-Risk。不要为这个附录另开 supplemental 文件。

---

## 3. 禁止写入的句子

- official reproduction / we reimplement FedAU / faithful FedAU
- FedAU-Window recovers the original FedAvg objective
- 任何新 RMSE / Holm / 百分比
- 方向 2 的 client-equal \(1/\widehat p\)（无 \(n_{k,r}\)）——那不是本轮实现
- 把 FLASH/FEMNIST 参与统计当作 MCS \(U\)

允许写：unknown participation statistics；usable-update layer；window-close aggregation；not an official reproduction。

---

## 4. 人文化与页数

- 先读 `CCFA-Skills/ccf-humanization/references/humanization-policy.md`。
- 新散文 0 个 em dash；稿面不要出现 `C1`/`C2`/`RQ` 标签。
- 写完跑：
  `C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe CCFA-Skills\ccf-paper-writer\scripts\check_prose_quality.py TO_OVERLEAF_paper_tmc_r1_clean\appendix.tex`
- 编译：
  - `pdflatex` + `bibtex` + `pdflatex`×2 on `main.tex` → **14 pages**
  - `pdflatex` on `supplemental.tex` → **13 pages**
- 若 15/14：先压缩附录新小节（合并句子），不要删公式；主文用替换不要新增段落。现有 `\enlargethispage` / `\IEEEtriggeratref{51}` 不要无故改大到把参考文献裁掉；改完必须核对 [52][53][54] 仍在第 14 页。

---

## 5. 完成标准

- 附录 `\label{app:adapted_baselines}` 存在，三套公式与 §1 一致。
- 主文有指向该附录的一处（评估设置基线段）。
- 零处声称官方复现。
- 所有已有表数字未改。
- `src/` 未改。
- `main.pdf` 14 页，`supplemental.pdf` 13 页。
- 未 commit。

完成后用几句中文向人汇报：插入位置、主文是否只替换、页数、以及明确「未训练、未称官方」。
