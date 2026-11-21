# 方案 A 说明与草稿：把 `eq:design_gate` 的语义写成一条可证命题 + 一条显式 Remark

```text
状态：草稿（未入文）。经授权后才动 TO_OVERLEAF_paper_tmc_r1_clean/。
契约：CCFA-Skills/ccf-paper-writer（并入文时按其流程：先快照 → 改 → 重编译 → 逐项核对）。
不新增假设、不新增编号公式、不改任何数字与结论。
依据：PROOF_SKELETON.md 第 1 节（恒等式）、main.tex eq:design_factor (32)、eq:design_gate (42)、
      §VII-E 的 "Setting the Design factor"；本轮外生实验只作动机，不作证明步骤。
```

## 1. 这一段要解决什么

论文现在的 `eq:design_gate`（42）只**定义**了 `ρ_r` 与 `D_r = on ⟺ ρ_r = 0`，它的**语义**（"门关掉时究竟删掉了什么"）没有以命题形式写出来；同时读者会自然地把"`ρ_r = 0`"误读成"参考实现无误差"。方案 A 做两件事：

1. 把 `eq:design_factor` 与 `eq:design_gate` 之间**本来就成立**的等价关系写成一条 **Proposition**（可证、两行证明、零新假设）；
2. 把**推不出来的部分**写成一条 **Remark**，明确 ① `ρ_r` 是**单元计数**份额、② 被删**质量**份额没有数据无关正下界、③ `ρ_r > 0` 时命题 3 的共享 `A_r` 前提失效、④ `ρ_r = 0` **不**推出任何插值误差为零。

这样"有命题"与"不越界"同时成立，且**不引入任何为结论量身定制的新假设**。

## 2. 命题的精确陈述（可直接入文，无新编号公式）

**放置位置（有硬约束）**：必须放在**命题 3 之后**（`main.tex` 现为 §III 理论块末尾，`prop:practical_plugin` 之后约 L1303–1340），这样新命题拿到编号 **4**，而 main 与 appendix 里**硬编码的 "Proposition 1/2/3" 字符串**（main 4 处、appendix 12 处，均为 `Proposition~N` 而非 `\ref`）全部保持有效。若放在 `eq:design_gate`（§III-D，L1030 一带）旁边，新命题会变成 **1**，把 Prop 1/2/3 全部后移一位 → 那 16 处硬编码同时出错，不可接受。

置放位置见上（命题 3 之后，取编号 **4**）。命题内部的句子直接引用既有的 `eq:design_factor` 与 `eq:design_gate`：

```latex
\begin{proposition}[Design deletion identity]
\label{prop:design_deletion}
Under \eqref{eq:design_factor} and the floor $\pi_{\min}>0$ of A6a, a delivered
pair $(k,i)\in\mathcal E_r$ receives a zero design weight if and only if
$\pi^{\mathrm{tar}}_{k,s(i)}=0$.  Consequently $D_r=\mathrm{on}$ leaves every
delivered pair with a positive design weight if and only if $\rho_r=0$.
\end{proposition}
\begin{proof}
For $D_r=\mathrm{on}$, A6a gives
$\widehat\pi^{\mathrm{opp}}_{k,r,s}\ge\pi_{\min}>0$, so the denominator of
\eqref{eq:design_factor} is strictly positive and the factor vanishes exactly
when its numerator $\pi^{\mathrm{tar}}_{k,s(i)}$ does.  For $D_r=\mathrm{off}$
the factor equals $1$ everywhere.  The pairs on which the factor is zero are
therefore exactly those counted by $n^{\mathrm{zero}}_r$, and none of them is
deleted precisely when that count is zero.
\end{proof}
```

- 编号影响：**不新增公式编号**（引用既有 (32) 与 (42)），主文公式数保持 43。
- **命题计数器**：`supplemental.tex` 的 `\setcounter{proposition}{3}` 必须同步改为 `{4}`，否则附录自己定义的两条命题（`prop:pairwise-lcb-barrier`、`prop:drift-boundary`）会与主文新命题撞号；这两条在附录中是用 `\ref` 引用的（无硬编码），因此只需改计数器这一个数字。
- 依赖：只有 `eq:design_factor` 与 A6a 的 `π_min > 0`；A5、A6b、命题 1–3 都不需要。

## 3. Remark 的精确陈述（把边界写在明面上）

置于 §VII-E 的 "Setting the Design factor"（或紧随命题 4）：

```latex
\begin{remark}[What the gate does not bound]
\label{rem:design_gate_scope}
$\rho_r$ is the share of delivered \emph{units} on zero-target keys.  The
corresponding share of aggregation \emph{mass} is not bounded below by the
definitions: the factor of \eqref{eq:design_factor} can be arbitrarily small on
pairs with $\pi^{\mathrm{tar}}>0$.  When $\rho_r>0$ the implemented and ideal
references no longer share $\mathcal A_r$, so
Proposition~\ref{prop:practical_plugin} does not apply; and $\rho_r=0$ removes
that obstacle without implying that any interpolation error vanishes.  The gate
is a support condition on the delivered keys, not a bound on the endpoint cost of
deleting them.
\end{remark}
```

（`prop:practical_plugin` = 命题 3 的既有 label，§VII-F 已在用。）

## 4. 必须同时补的一句"对象"限定（关键，来自本轮实验）

`ρ_r` 的键是 `(client, stratum)`。若某个 block 冻结的目标图定义在更粗的层级，其门值是按那个对象算的，两者不可互换。建议在 §III-D 的 `eq:design_gate` 后加一句（约一行）：

```latex
The gate is evaluated on the delivered $(k,s)$ keys; a block whose frozen target
map is defined at a coarser level reports the gate on that object.
```

这一句把 City Scanner 那一类 region 级实现与键级定义分开，避免读者把 region 级的"零覆盖"读成键级结论（本轮实测：同一块键级 `ρ_r = 14.35%`，region 级检验按构造恒为 0）。

## 5. 与现有文本的衔接（最小改动清单）

| 位置 | 动作 | 行数 |
|---|---|---|
| `main.tex` §III（命题 3 之后，L1303–1340 一带） | 插入命题 4 + 证明 | ≈ 14–18 行 |
| `main.tex` §III-D，`eq:design_gate` 之后 | 插入第 4 节的"对象"限定句 | 1–2 行 |
| `main.tex` §VII-E "Setting the Design factor" 末 | 插入 Remark | ≈ 8–10 行 |
| `supplemental.tex` | `\setcounter{proposition}{3}` → `{4}` | 1 行 |
| 其他章节、表格、数字、硬编码的 Proposition 1/2/3 | **不动** | 0 |

- 页数：主文现在正好 **17 pp.**，上述 ≈25–30 行需从 §VII-G 的重复边界陈述等处压缩等量文字（记录自己建议过这处压缩），以保住 17 pp. / 16 pp.。
- 引用：命题 4 与 Remark 用 `\ref`；不引入新 `\eqref` 编号。

## 6. 这一段能买到什么、买不到什么

**买到（可核验）**
- 论文里出现一条**可证**的命题，且它直接对应已发表的 `eq:design_gate`（同一对象、同一条件）；
- 把"`ρ_r = 0` ⇒ 参考无误差"这类误读**在正文里堵住**（Remark 明写不推出）；
- 把键级/region 级的对象边界写明，消除附录那行与本轮实测之间的表面冲突。

**买不到（必须承认）**
- 不给出 `ρ_r > 0` 时被删**质量**份额的下界（那需要新增权重要求，见方案 B）；
- 不把切换点 `eq:design_switch`（43）变成定理（它是两块数据上的测得无差异条件；本块无 Design-off 臂，连测都测不了）；
- 不把命题 3 扩展到 `ρ_r > 0` 的情形（需要训练/分布稳定性假设，见 W3）。

## 7. 禁区（起草时已遵守，入文后同样适用）

- 不写 `ρ_r = 0 ⇒ ε_π = 0`（两者是不同对象：`ε_π` 是 `π̂^opp` 对 `π^opp` 的误差）；
- 不把 `eq:design_switch` 写成命题 4 或任何结论的推论；
- 不把 Remark 的缺口写成"我们证明了端点不变"；
- 不把 region 级实现的门值表述为键级结论；
- 不引入新假设来"补"质量份额下界。

## 8. 入文后的验收（与既有核对流程一致）

1. `pdflatex -draftmode` 补全 `main.aux` → 编 `main.tex` → 编 `supplemental.tex`；
2. main **17 pp.** / supplement **16 pp.**、0 error / 0 undefined / 0 overfull；
3. 公式数仍为 **43**（命题 4 不新增编号公式）；`.aux` 中 `prop:risk→1`、`prop:reconstruction→2`、`prop:practical_plugin→3`、`prop:design_deletion→4`，附录两条命题顺延为 5、6；
4. 硬编码自检：`grep -c 'Proposition~[123]'`（main 4 处、appendix 12 处）在改后仍在同一批句子里指向同一对象，且**没有**任何硬编码指向 4/5/6；
5. `check_prose_quality.py`（main）无 hard failure；`tools/freeze_appendix_refs.py --check` = 0/0；主文 em dash 不增加（现为 2/3）；
6. `pdftotext` 抽查新命题与 Remark 已入版；
7. 快照目录：`snapshots/2026-10-02-pre-design-gate-proposition/`；
8. 诊断记录写入 §7 新条目（含"关掉哪一条开放项、留下哪一条"）——把 "M1 已写公式" 与 "命题化" 分开记，避免把 A 说成把 (43) 也定理化了。

## 9. 备选（更保守）

若不想新增 `Proposition` 编号与证明环境，可只加 §3 的 Remark（+第 4 节那一句对象限定），成本降到约 10 行、零新编号：它仍然堵住误读、写明边界，但**没有**"一条可证的命题"这一项观感收益。建议仍以 A（命题 + Remark）为准，B 视审稿反馈再决定。
