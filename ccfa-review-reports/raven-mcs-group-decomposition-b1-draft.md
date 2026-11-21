# 方案 B1 说明与草稿：部署判据的**组分解恒等式**（含给实验设计方的验证接口）

```text
状态：说明 + 可入文草稿（未入文）。
契约：CCFA-Skills/ccf-paper-writer（入文时按流程：快照 → 改 → 重编译 → 逐项核对）。
零新假设；不新增编号公式；不改任何已发表数字。
现有验证：已在 50 checkpoint × 3 组权重 = 150 个格子上数值成立到 1.1e-16，
          并以其一阶导数预测 M2−run 的位移，与实测差 7.2e-6（纯二阶残差）。
```

## 1. B1 是什么（一句话）

论文公布的部署判据权重是 `μ_g / n_g`（**组内等权**），因此判据本身可以**精确分解**到组：

$$\mathrm{RMSE}_\mu^2=\sum_{g\in\mathcal G}\mu_g\,\mathrm{RMSE}_g^2,\qquad
\frac{\partial\,\mathrm{RMSE}_\mu}{\partial \mu_g}=\frac{\mathrm{RMSE}_g^2}{2\,\mathrm{RMSE}_\mu},$$

其中 `G` 是目标图的分组集合（U-Air 144 组、City Scanner 4 个 region、SS/U-Air 的 4 个块皆可），`RMSE_g` 是**组内** RMSE。

**三个直接后果**

1. **敏感度闭式**：目标图（`μ`）对已发表数字的影响不是定性判断，而是上面这个可算的导数——它等于每组的误差剖面。
2. **排名翻转的判据**：两个方法在权重 `μ` 与 `μ'` 下的次序只会因**误差剖面交叉**而翻转；即
   `sign(RMSE_{μ,a} − RMSE_{μ,b})` 在权重组之间保持，除非 `Σ_g Δμ_g (RMSE_{g,a}^2 − RMSE_{g,b}^2)` 变号。
3. **切换点的精确形式**：两个设置的**无差异条件**是该分解为零，而非一串聚合百分比：
   `Σ_g μ_g [RMSE_g²(on) − RMSE_g²(off)] = 0`。论文现在印的 `4.990 / 6.943 / 6.885 / 7.221` 只是它的**推论**（这就是方案 C1）。

## 2. 成立条件与其通用性（必须写清）

- 只有当 `μ` 在每组内**常数**时，"一组的权重"才有定义。论文的目标图按构造满足这一点（`μ` 定义在组上），所以恒等式对**任何**分组建模成立。
- **组内权重不必等权**：把 `RMSE_g` 定义为"按组内归一化权重加权的 RMSE"，恒等式**依然精确**；论文的 `μ_g/n_g` 只是让 `RMSE_g` 退化为普通的组内等权 RMSE（可解释性更好，也是我们数值验证的情形）。
- 通用性轴：跨数据集（任意组数）、跨目标图（任意 `μ`）、跨 arm、跨设置（on/off 都适用）——**不依赖任何新假设**。
- 它**不谈**训练：分解的是"打分"，不是"重训后的轨迹"。

## 3. 可入文草稿

**放置**（与方案 A 相同的硬约束）：命题必须放在**命题 3 之后**（`main.tex` 的 §III 理论块末尾），取编号 **4**；main 里 4 处、appendix 里 12 处硬编码的 `Proposition~1/2/3` 因此全部保持有效。`supplemental.tex` 的 `\setcounter{proposition}{3}` 同步改为 `{4}`。**不新增公式编号**（主文公式数保持 43）。

```latex
\begin{proposition}[Group decomposition of the deployment-target criterion]
\label{prop:group_decomposition}
Let the test units be partitioned into groups $g\in\mathcal G$, let
$\mu_g$ be the target mass of group $g$, and let $\mathrm{RMSE}_g$ be the RMSE of
the group's units under the within-group normalised weights.  Then
\begin{equation}
\mathrm{RMSE}_\mu^2=\sum_{g\in\mathcal G}\mu_g\,\mathrm{RMSE}_g^2 ,
\label{eq:group_decomposition}
\end{equation}
and, where the weights are $\mu_g/n_g$ and the partition is held fixed,
$\partial \mathrm{RMSE}_\mu/\partial\mu_g=\mathrm{RMSE}_g^2/(2\mathrm{RMSE}_\mu)$.
Consequently two arms exchange order between two target maps $\mu$ and $\mu'$
only if $\sum_g(\mu'_g-\mu_g)\big(\mathrm{RMSE}_{g,a}^2-\mathrm{RMSE}_{g,b}^2\big)$
changes sign.
\end{proposition}
\begin{proof}
Write $w_i=\mu_{g(i)}/n_{g(i)}$ and $e_i^2=(\hat Y_i-Y_i)^2$; then
$\mathrm{RMSE}_\mu^2=\sum_i w_i e_i^2
=\sum_g \mu_g\big(\tfrac1{n_g}\sum_{i:g(i)=g}e_i^2\big)
=\sum_g\mu_g\mathrm{RMSE}_g^2$.
The partial derivative follows by differentiating the sum, and the ordering claim
by applying the decomposition to both maps and subtracting.
\end{proof}
```

**配套 Remark（可选，把边界写清，避免被读成训练侧结论）**：

```latex
\begin{remark}[Scope of the decomposition]
\eqref{eq:group_decomposition} is a property of the criterion, not of the
training procedure: it re-weights a fixed set of predictions, so it constrains
how a reported value moves with the target map and not how a method would
perform under a different map.  The group errors themselves remain measured.
\end{remark}
```

（若不想新增公式编号 `eq:group_decomposition`，可把它并入正文行内公式：`RMSE_μ² = Σ_g μ_g RMSE_g²`，命题仍是命题。）

## 4. 为什么它比方案 A 通用（对照）

| | A（删除恒等式） | **B1（组分解）** |
|---|---|---|
| 覆盖对象 | 只有 Design 因子的零权重通道 | 判据本身：任意分组、任意目标图、任意 arm/设置 |
| 通用性 | 定义域内、单因子 | 跨数据集（144 组 / 4 组 / 4 块）、跨图、跨设置 |
| 给出幅度? | 否 | 是（闭式导数） |
| 可检验性 | 两行证明 | 已在 150 个格子上验到 1.1e-16；一阶预测吻合 7.2e-6 |
| 对切换点 (43) 的作用 | 无 | 把 (43) 变成可证的分解（C1） |

## 5. 它**不**买什么（入文时必须同时承认）

- 不把 `ρ_r > 0` 的支撑损失变成有界（那需要 B2 的显式假设）；
- 不把每组误差从"测得"变成"推出"，因此 (43) 的阈值仍是**数据支撑的**决策标准；
- 不涉及训练侧效应（分解的是打分）；
- 不替代 Design on/off 的选择：要判定切换，仍需要**两个设置各自**的组误差剖面。

## 6. 给实验设计方的验证接口（B1/C1 落纸前必须establish的事）

建议实验按下列条目设计，每条都给出容差与失败即停的规则（与既有协议同一风格）：

| # | 要establish的事 | 输入 | 判定 |
|---|---|---|---|
| **E1** | 恒等式在**每个数据集**上成立 | 每组 RMSE、`μ`、已发表 `RMSE_μ`（U-Air：E2 的 per-block 列；SS/U-Air：G2 stored per-seed block scores；City Scanner：`ENDPOINT_TABLE.csv`） | `|RMSE_μ − sqrt(Σ μ_g RMSE_g²)| ≤ 1e-12`，逐 (dataset, arm, seed) |
| **E2** | 一阶导数预测正确 | 同一 checkpoint 的两套权重（如 run 与 M2） | `|ΔRMSE_μ − Σ Δμ_g RMSE_g²/(2RMSE_μ)| ≤ 1e-4`，权重扰动 ≤5% |
| **E3** | 排名翻转 ⟺ 剖面交叉 | 多套权重下的 arm 排名与每组误差 | 若排名不变，检查 `Σ Δμ_g Δ(RMSE_g²)` 未变号；若变号则排名必须不同 |
| **E4** | (43) 的四个聚合数由分解还原（C1） | SS/U-Air 的 on/off 每组误差、`μ` | 由 `Σ_g μ_g Δ(RMSE_g²)` 重建 4.990/6.943/6.885/7.221 的符号与量级，偏差需解释（不是重算目标） |
| **E5** | 组内等权条件在实现中成立（否则 `RMSE_g` 要用组内归一化加权定义） | `_mu_weights_for_test` 的权重与分组 | 组内权重方差 = 0（或记录非零情形） |
| **E6** | 落地记录 | 脚本、哈希、每格数值 | 只写新目录；不改论文、不改 `src/` |

**不允许写进结论的句子**（与实验协议一致）："模型在外生目标下重训"、"切换点被证明"、"支撑损失有界"、"排名翻转等价于某方法更优"。

## 7. 落纸流程与页数

1. 命题 + 证明（或 Remark）：main **≈12–16 行**；C1 的推论另 **≈6–8 行**（放 §VII-E 的 "Setting the Design factor" 旁）；
2. 主文现为 **17 pp.**，需从 §VII-G 的重复边界陈述压缩等量文字；
3. `pdflatex -draftmode` 补 aux → 编 main → 编 supplement；核 main 17 pp. / supp 16 pp.、0 error / 0 undefined / 0 overfull；
4. `.aux` 检查：`prop:risk→1`、`prop:reconstruction→2`、`prop:practical_plugin→3`、`prop:group_decomposition→4`；附录两条命题顺延 5、6；
5. 硬编码自检：main 4 处、appendix 12 处 `Proposition~1/2/3` 仍指向同一对象，且无任何硬编码指向 4/5/6；
6. prose check（main）无 hard failure；`tools/freeze_appendix_refs.py --check` = 0/0；
7. 记录：诊断记录新增 §7 条目，把"B1 已入文"与"C1 已还原"分开记，并注明 (43) 阈值仍为数据支撑。
