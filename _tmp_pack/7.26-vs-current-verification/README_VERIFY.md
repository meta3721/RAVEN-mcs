# 7.26 版 vs 当前版：方法学差异逐条核实

**用途**：在 Overleaf 上逐条核实两版论文的方法学差异。
**生成日期**：2026-09-19
**两版来源**

| 版本 | 文件 | 说明 |
| --- | --- | --- |
| **7.26 版** | `jul26/RAVEN_MCS_2026_7_26_.pdf`（21 页） | 页面/行号以本 PDF 为准；纯文本版 `jul26/jul26_plain.txt` 便于搜索 |
| **当前版** | `current_paper/main.tex` + `appendix.tex` | 本包内含完整 Overleaf 工程，可直接编译 |

> **核实方法**：每条差异给出 ① 7.26 的 **PDF 页码 + 行号** 与 ② 当前版的 **文件名 + 行号**。
> 在 Overleaf 上用 `Ctrl+F` 搜引号内的原文即可定位；PDF 用阅读器的"跳转到页"。

---

## 结论摘要（先看这个）

| # | 差异 | 7.26 | 当前版 | 性质 |
| --- | --- | --- | --- | --- |
| D1 | Design 启用机制 | 方法内部的**支持兼容性条件** | 外部给定的**数据集级冻结判据**（$\phi$） | 机制替换 |
| D2 | 理论工具链 | Lyapunov 漂移 + 窗口可达性 + 目标风险收敛界 | 全部删除，改为质量相合 + 唯一解 + 稳定性 | **理论收缩** |
| D3 | 优化对象的命名与定位 | Target-**Risk**-Calibrated | Target-**Mass**-Calibrated | 口径换靶 |
| D4 | 真实移动数据集 | T-Drive-**Speed**（$Y$=速度） | T-Drive 仅作机会回放，$Y$ 不再来自轨迹 | 数据角色替换 |
| D5 | 统计规范 | 无预注册、Holm 少 | 预注册、Holm 家族、非劣规则 | 加强（但作用在更弱的主张上） |

**不变的部分**（也必须核实，否则会误判）：**P2 目标函数五项与系数两版完全相同**。见 D0。

---

## D0｜不变项：P2 目标函数（先确认这条，避免误判）

**7.26 原文**（PDF p10，式 (107)）：

> `RAVEN-MCS selects the aggregation vector by solving P2 : min αr∈Cr −QTr Mrαr + λg/2 ‖Mrαr − µ‖2 + λβ/2 ‖αr − βbr‖2 + λv/2 αTr V rαr + λsτ Tr αr.`

**当前版**（`main.tex` L918–L929，`eq:P2_objective`）：

```latex
J_r(\alpha) = -Q_r^{\top}M_r\alpha
 + \frac{\lambda_g}{2}\|M_r\alpha-\mu\|_2^2
 + \frac{\lambda_\beta}{2}\|\alpha-\widehat\beta_r\|_2^2
 + \frac{\lambda_v}{2}\alpha^{\top}V_r\alpha
 + \lambda_s\overline\tau_r^{\top}\alpha.
```

**逐项一致。** 差异不在优化器，而在它的**来历**（见 D2）、**启用机制**（D1）与**声称优化的对象**（D3）。

---

## D1｜Design 启用机制：从"支持兼容性条件"变成"冻结启发式 φ"

### 7.26 的说法

7.26 **全文没有 "compatible" 这个词**（已用程序确认：命中数 0）。
Design 的启用在 7.26 中是方法内部的一个条件分支，但没有给出显式判据；请核对以下位置：

- PDF p1 第 23 行附近（摘要）："…combines **target-to-opportunity design correction** with stabilized Hájku observation weighting…"
- PDF p2 第 44 行附近："Each client combines the resulting **target-to-opportunity design ratio** with a lagged observation propensity…"
- PDF p2 第 75 行附近（贡献 2）："We develop RAVEN-MCS, which integrates **lagged target-to-opportunity design correction**…"

### 当前版的说法

- `main.tex` **L1470**：`for that assignment.  A support-compatible mixture target failed a` —— **"support-compatible" 出现在当前版，7.26 没有**
- `main.tex` **L1850**：`$2016$ of $5688$).  The $25.5\%$ figure is the realized always-on` —— **25.5% 是当前版新引入的（7.26 命中数 0）**
- `main.tex` **L1853**：`$51.6\%$.  Oracle Design tracks estimated` —— **51.6% 同为新增（7.26 命中数 0）**
- `main.tex` **L994**：$\phi$ 的定义式标签 `\label{eq:scd_phi}`（定义式本体在 L984 起）；**L1011–L1012** Algorithm 1 及其标题 `Window-close RAVEN-MCS: RAVEN-Design if $\phi=0$, else RAVEN-NoDesign`
- `appendix.tex` **L2161 / L2174**：把 25.5% 明确标注为 EventTrace 出现占比，而不是 φ

**核实要点**：在 7.26 的 PDF 里搜 `25.5`、`51.6`、`compatible`、`φ`（phi）——**全部 0 命中**；在当前版里搜同样四个词——全部有命中。这条差异是黑白分明的。

---

## D2｜理论工具链：5 个证明模块被整体删除

以下每一行都是 **7.26 有、当前版 0 命中**（已程序化确认）。

| 模块 | 7.26 位置 | 7.26 原文（节选） | 当前版 |
| --- | --- | --- | --- |
| **Lyapunov 漂移** | PDF **p10 第 3 行** | "Consider the **Lyapunov function** L(Qr) = 1/2 ‖Qr‖2" | **无**（`main.tex`/`appendix.tex` 均无 Lyapunov） |
| **一窗口债务漂移** | PDF **p10 第 9 行** | "Using [x]2 + ≤ x2, the **one-window debt drift satisfies** …" | **无** |
| **二阶漂移与 λg 的耦合** | PDF **p10 第 86 行** | "**The instantaneous calibration term then dominates the normalized second-order drift term** ηr‖µ − Mrαr‖2 2/2."（配合式 (108) `λg ≥ ηmax`） | **无**；$\lambda_g$ 现为自由参数（`main.tex` L924、L1086） |
| **近似窗口可达性** | PDF **p13 第 86 行** | "**Assumption 5 (Approximate window reachability).** There ex-ist an integer W < ∞ and ϵreach ≥ 0 …" | **无**（全库 "reachab" 0 命中） |
| **目标风险收敛定理** | PDF **p14 第 162 行** | "**Theorem 3** shows that target-risk optimization additionally depends on the complete per-window client–record discrepancy and on residual measurement, optimization, staleness, and variance errors." | **无** |
| **逐窗口目标梯度偏差** | PDF **p13 第 220 行**（标题）+ **p14 第 22 行**（Lemma 3） | "H. **Per-Window Target-Gradient Bias**" / "**Lemma 3 (per-window target-gradient bias).** Under Assumptions 1 and 4, …" | **无** |
| **聚合方差界** | PDF **p13 第 165 行** | "**Lemma 2 (Aggregate variance bound).** Define Σ2 r = …" | **无** |
| **条件中心化** | PDF **p12 第 73 行** | "**Assumption 4 (Local SGD and conditional centering).** There exists a constant Csgd > 0 such that …" | **无** |
| **可达成性审计** | PDF **p15 附近**（VI-G "Support and Reachability Audit"） | 见 VI-G 小节 | **无** |

**当前版替换成了什么**（请对照核实）：

- `main.tex` **L1149** `\begin{proposition}[Normalized target reconstruction]`（7.26 无此命题；它对应 7.26 的 V-D "Perturbation of the Two-Stage Reference"，并被弱化为稳定性陈述）
- `main.tex` **L1198** `\begin{theorem}[Unique solution of the calibration program]`（7.26 的 Thm. 1 是 "**Target-debt growth**"，含 $O(S_R^{-1/2})$ 速率与 $\epsilon_{\mathrm{reach}}$ 残差；当前版只证"存在唯一解"）
- `main.tex` **L1230** `\begin{proposition}[Practical plug-in perturbation]`
- `main.tex` **L1287** `\begin{theorem}[Stable-regime aggregate lower coverage]`（当前版新增；7.26 无对应定理）

**核实要点**：在 7.26 PDF 里搜 `Lyapunov`、`reachability`、`Theorem 3`、`conditional centering` —— 各有命中；在当前版 `main.tex` + `appendix.tex` 里搜同样四词 —— **全部 0 命中**。

---

## D3｜优化对象：Target-Risk → Target-Mass

| | 7.26 | 当前版 |
| --- | --- | --- |
| 标题 | PDF **p1 第 2 行**："RAVEN-MCS: **Target-Risk-Calibrated** Asynchronous Federated Data Completion under Two-Stage Non-Random Selection" | `main.tex` **L55**："RAVEN-MCS: **Target-Mass-Calibrated** Windowed-Asynchronous …" |
| 摘要定位 | PDF **p1 第 19 行**："proposes RAVEN-MCS, a **target-risk-calibrated** asynchronous federated data-completion framework…" | `main.tex` L70 起摘要：改为 "treats windowed-asynchronous federated completion as **target-mass alignment**" |
| 章节标题 | PDF：**III. SYSTEM MODEL AND PROBLEM FORMULATION**，含 §III-F "Target-Risk Misalignment"、§III-G "Ideal Two-Stage Corrected Quantities"、§III-H "**Target-Risk-Calibrated Asynchronous Problem**" | `main.tex` **L324**："System Model and **Target-Mass** Formulation"；III-F/G/H 三个小节**均已取消** |
| 缩写含义 | PDF 未展开为 "Risk Alignment Via…"（0 命中） | `main.tex` **L148**："**Reference Alignment** Via Exposure-aware Normalization"；另见 **L618** |

**词频对照（程序统计）**：7.26 中 "Target-Risk" 命中 **26** 次、"Target-Mass" **0** 次；当前版反之（Target-Risk 1 次、Target-Mass 18 次）。

---

## D4｜真实移动数据集：T-Drive-Speed → T-Drive 机会回放

| | 7.26 | 当前版 |
| --- | --- | --- |
| 数据集名 | PDF **p15 第 19 行**表格行："**T-Drive-Speed**" | "T-Drive-Speed" **0 命中** |
| 目标构造 | PDF **p15 第 43 行**："For **T-Drive-Speed**, vehicles are partitioned by identity into a reference fleet and a client fleet. … the reference fleet is used only to construct the public speed field" | `main.tex` **L1380–L1381**：T-Drive `\cite{yuan2010tdrive}` "is the public Microsoft Research taxi-trajectory sample"；其后 **L1383–L1388** 明确 $O/U$ 为 Complete-aligned 控制、$\phi>0$ 故用 RAVEN-NoDesign，**不产出 $Y$** |
| 角色 | 真实移动一致性实验（含参考车队/客户端车队分离） | **机会回放**：`main.tex` **L1405** "T-Drive is a hybrid ranking under real $R$"（提交版的措辞更弱，写 "not a ranking"） |
| 站点数据集 | 7.26 中 **"SensorScope" 0 命中**（当时主叙述围绕 T-Drive-Speed 与受控基准） | 当前版 SensorScope 命中 **81** 次，成为主表核心 |

**核实要点**：7.26 PDF 搜 `T-Drive-Speed`（有）与 `SensorScope`（无）；当前版 `main.tex` 搜 `T-Drive-Speed`（无）与 `SensorScope`（大量）。

---

## D5｜统计规范（这次是加强，不是删减）

| | 7.26 | 当前版 |
| --- | --- | --- |
| Holm | 1 次 | **20 次** |
| Wilcoxon | 1 次 | 4 次 |
| 预注册（pre-registered） | **0 次** | **5 次** |
| +0.5% 非劣规则 | **无** | 有（`main.tex` 指标策略段） |

**核实要点**：这些是**加强项**，但要注意它们作用在一个**比 7.26 更弱的主张**上——即"D3 把目标从风险换成质量"之后，统计再严谨也无法补回风险端的结果。

---

## 建议的核实顺序（约 20 分钟）

1. **先验 D0**：确认两版 P2 五项相同（7.26 PDF p10 式 107 vs `main.tex` L918–929）。这一步排除"目标函数被改过"的误判。
2. **再验 D2**：在 7.26 PDF 搜 `Lyapunov`、`Theorem 3`、`reachability`、`conditional centering`；在当前版搜同样四词。**这是差异最大、最无争议的一条。**
3. **验 D1**：在 7.26 PDF 搜 `25.5`、`51.6`、`compatible`（均 0）；在当前版搜（均有）。**黑白分明。**
4. **验 D3**：看两版标题（7.26 PDF p1 第 2 行 vs `main.tex` L55）。
5. **验 D4**：7.26 PDF 搜 `T-Drive-Speed`；当前版搜 `SensorScope`。

---

## 附一：附录已改为"可独立编译"（重要，关系到你能否核查）

**你之前看到的 `Section ??` 和 `Proof of Theorem ??` 不是源码错误**，而是编译依赖问题：

- 附录原有 **67 处**引用指向正文的 **27 个标签**，靠 `xr` 包读取 `main.aux` 解析；
- **只要没先编译 `main.tex`，附录就会出现 125 条未定义引用、PDF 里 122 个 `??`**（已实测复现），其中就包括 `\subsection{Proof of Proposition~\ref{...}}` 这类标题；
- 现在已改为：**附录内所有指向正文的引用都换成实际编号**（如 `Section~VI`、`Theorem~1`、`Eq. (32)`），并让附录自带参考文献。

**实测结果**

| 场景 | 修复前 | 修复后 |
| --- | --- | --- |
| 附录单独编译（无 `main.aux`） | 125 条未定义引用 / 122 个 `??` | **0 条 / 0 个** |
| 附录 + `main.aux` 齐全 | 0 | 0 |
| 主文档内部引用 | 0 | **0**（未受影响） |

**再生成方式**（若 `main.tex` 改了编号）：先编 `main.tex`，再运行

```bash
python tools/freeze_appendix_refs.py --apply
```

（该脚本已放在工作区 `tools/freeze_appendix_refs.py`，会从 `main.aux` 读回真实编号并重写 `appendix.tex`。）

**Overleaf 编译方式**：现在两种顺序都能编过。
- 推荐：把 `main.tex` 设为根文档 → 编译（含 BibTeX）→ 再把 `supplemental.tex` 设为根文档 → 编译（含 BibTeX）。
- 附录也可以**直接单独编**，不再有 `??`。

---

## 附二：本包文件清单

```text
7.26-vs-current-verification/
├── README_VERIFY.md              ← 本文件
├── jul26/
│   ├── RAVEN_MCS_2026_7_26_.pdf  ← 7.26 原稿（21 页，页码以此为准）
│   └── jul26_plain.txt           ← 7.26 纯文本（便于 Ctrl+F 全文搜索）
└── current_paper/                ← 当前版完整 Overleaf 工程
    ├── main.tex / appendix.tex / supplemental.tex   ← appendix.tex 已冻结跨文档引用
    ├── reference.bib / main.bbl
    ├── figures/                  ← 9 张矢量图（仅 PDF，已剔除未引用的 PNG）
    └── （main.pdf 15 页；supplemental.pdf 14 页）
```

**Overleaf 上传方式**：把 `current_paper/` 内的**全部内容**（不要连文件夹本身）压成 zip 上传；上传后把 `main.tex` 设为根文档先编一次，再切 `supplemental.tex` 编一次。附录即使单独编也不会出现 `??`。
