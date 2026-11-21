# Cursor 执行指令：P3 — Design 反转能否被“修掉”

> 目的：回答审稿人 W1 / M4。U-Air 上去掉 Design 后 \(\Delta_{\mathrm{group}}\)、RMSE\(_\mu\)、Tail RMSE 同时显著变好，完整 RAVEN 只保住 \(\Delta_{c\text{-}s}\)。本实验要判断：**是否存在一个预声明、不用测试标签的规则，使 Design 不再伤害部署主端点。**
> 不是再写一段 trade-off。成或败都要能写进论文。
> 仓库：`D:\Cursor\raven.mcs`。工作稿：`_paper_work` 或清洁稿，**本实验不改任何已封印的 E3/E4 数字。**

---

## 0. 先承认机制，再设计

Design 不是只改 P2。`WindowRunner` 里 `uses_design_ratio=False` 会把 \(\hat\zeta\leftarrow 1\)，从而同时改变：

1. 局部 Hájek 训练权重（模型本身）
2. 重建参考 \(\hat\beta\)
3. 再进入 (P2) 的 \(\lambda_\beta\|\alpha-\hat\beta\|^2\)

所以 U-Air 上 6.5% 的 RMSE 变化，**很可能主要来自模型，而不是聚合权重**。只改 \(\lambda_g/\lambda_\beta\) 可能修 \(\Delta_{\mathrm{group}}\)，修不了 RMSE。实验必须把这两层拆开。

已有对照（不要重跑）：

- 完整 RAVEN：`raven`（E3 / E4 参考）
- 去掉 Design：`raven_wo_design`（E4）
- 协议：Complete-aligned，SensorScope + U-Air，种子 30001–30020
- 产物：`artifacts/e4_core_mechanism_ablation_r1` 与 `artifacts/e3_formal_runs_r1`

---

## 1. 预声明（写进方法，禁止事后改）

**主端点（deployment target，审稿人口径）**

- \(M_1\): \(\Delta_{\mathrm{group}}\)
- \(M_2\): \(\mathrm{RMSE}_\mu\)
- \(M_3\): Tail RMSE

**次端点**

- \(S_1\): \(\Delta_{c\text{-}s}\)（论文原来的结构卖点）

**非劣界（相对 `raven_wo_design`，U-Air）**

- \(M_1,M_2,M_3\) 的配对均值相对变化 \(\ge -0.5\%\)（即不允许再差过 w/o-Design 的 0.5%）
- 统计：配对 Wilcoxon + Holm，族 = `{U-Air} × {M1,M2,M3}` 上「候选 vs w/o-Design」

**成功（才能把完整 Design 留在默认方法里，或换成新默认）**

候选 \(V^\star\) 必须同时满足：

1. U-Air：对 \(M_1,M_2,M_3\) 相对 `raven_wo_design` 非劣（上界）
2. U-Air：\(S_1\) 仍 Holm-显著优于 FedAvg-Window（保住“结构对齐”这句话）
3. SensorScope：对 \(M_1,S_1\) 相对完整 RAVEN 非劣（不要为修 U-Air 把 SS 打坏）
4. 选 \(V^\star\) 的规则只用训练/验证量，**禁止用测试 RMSE / 测试 \(\Delta\)**

**失败（同样是有效科学结果）**

所有预声明候选都不满足 1–3。则默认方法改为 `raven_wo_design`（或数据集门控后的那个），并把 Design 从标题级必要组件降级。这也能回审稿人，只是论文主张变窄。

---

## 2. Phase A — 机制审计（不新训，先做）

对每个 dataset × seed，读 `raven` 与 `raven_wo_design` 的：

- `final_metrics.json`
- `window_metrics.json`（`alpha`, `beta_hat`）
- `p2_invocation_states.json`（`M`, `alpha`, 若有 `beta`）

计算并写入 `_paper_work/design_noharm_results/phase_a/`：

| 量 | 含义 |
|---|---|
| \(\|M\hat\beta_{\mathrm{on}}-\mu\|_1\) vs \(\|M\hat\beta_{\mathrm{off}}-\mu\|_1\) | Design 是否把参考拉离部署组 \(\mu\) |
| \(\|M\alpha_{\mathrm{on}}-\mu\|_1\) vs off | 已知，对应 \(\Delta_{\mathrm{group}}\) |
| max / P99 \(\hat\zeta\), ESS(\(\hat\zeta\)) | 机会比是否极端 |
| 窗口级 \(\mathrm{sign}(\Delta_{\mathrm{group}}^{\mathrm{on}}-\Delta_{\mathrm{group}}^{\mathrm{off}})\) 的比例 | 伤害是系统性的还是少数窗 |

**判读（写进 `phase_a/conclusion.txt`，不许编）**

- 若 \(\hat\beta_{\mathrm{on}}\) 明显更偏离 \(\mu\)：P2 的 \(\lambda_\beta\) 是 \(\Delta_{\mathrm{group}}\) 的主因，Phase B 的约束/降 \(\lambda_\beta\) 有希望修结构，**不保证修 RMSE**。
- 若 \(\hat\zeta\) ESS 很低：优先试裁剪，而不是硬关 Design。
- 若结构差小、RMSE 差大：主因是局部训练，必须走 Phase C 的整策略门控，P2 修补不够。

---

## 3. Phase B — 三个预声明候选（按这个顺序，禁止加到赢为止）

所有候选共享同一 Complete-aligned eventtrace，禁止重调学习率/局部步数。

### B0. `raven_valgate`（先算，几乎零成本）

对每个数据集，用**验证集**（不是测试集）比较已有 `raven` vs `raven_wo_design`：

```
if val RMSE_μ(wo) + 0.5% < val RMSE_μ(full)
    or val Δ_group(wo) + 0.5% < val Δ_group(full):
        pick wo_design
else:
        pick full
```

同一数据集 20 个种子必须用**同一选择**（用 20 种子验证均值，或预先留下 seed 30000 作门控、30001–30020 作推断；二选一写死，推荐：**验证均值门控，推断集仍是 30001–30020 测试指标**）。

这是审稿人最难攻击的规则：Design 变成数据自适应开关，不是永远开。

若验证指标当前 run 里没有：用 checkpoint 在 validation split 上重算，禁止碰 test split。

### B1. `raven_p2_noharm`（只改聚合，模型仍是 Design 训练的）

同一窗口内同时形成两个参考：

- \(\hat\beta^{\mathrm{on}}\)：现有 Design 开
- \(\hat\beta^{\mathrm{off}}\)：\(\hat\zeta=1\) 后的参考
- \(\alpha^{\mathrm{off}}\)：用 off 参考跑一次标准 (P2)

然后解：

```
min  原 (P2) 目标（仍可用 β_on，或把 λ_β 接到 β_on）
s.t. 原可行集
     ||Mα − μ||_1  ≤  ||M α_off − μ||_1
```

即：**允许 Design 只在不伤害组对齐时影响权重**。

实现注意：

- \(\alpha_{\mathrm{off}}\) 必须来自同窗、同 \(M\)、同债务、同 \(\lambda\)，只关 Design 比。
- 若现有 `p2_invocation_states` 不足以重建 \(M,\mu,V,\tau,Q\)，才允许按 E4 runner **重放聚合**（复用 eventtrace，不重训局部模型）。RMSE 仍用 **原 raven checkpoint** 时，只能报告结构端点；要报 RMSE 必须重训或至少用该窗 \(\alpha\) 做一次后续训练。**不要用旧模型 + 新 \(\alpha\) 冒充测试 RMSE。**

因此 B1 的正式 RMSE 结论放到 Phase C。Phase B 只把 B1 当结构可行性探针。

### B2. `raven_lambda_beta_quarter`

Design 全开，只把 \(\lambda_\beta: 1.0 \to 0.25\)（\(\lambda_g\) 保持 1.0）。这是“降低对 Design 参考的忠诚”，不是关层。

只跑 U-Air 20 种子 + SensorScope 20 种子，若 Phase A 显示 \(\hat\beta\) 偏离 \(\mu\)。

---

## 4. Phase C — 必须新训的正式比较（只有 B0 不够、或 B1 结构看起来能赢时才开）

新方法写入 `method_policy.py`，E4 同协议：

| method | 含义 |
|---|---|
| `raven_valgate` | B0 选中的整策略（实质是已有两个 run 的选择，不必新训） |
| `raven_p2_noharm` | B1 的全窗口训练（Design 局部损失 + 约束 P2） |
| `raven_lambda_beta_quarter` | B2 全训 |

对照固定为：`raven`, `raven_wo_design`, `fedavg_window`。

产出 `_paper_work/design_noharm_results/`：

- `per_seed.csv`
- `summary.csv`
- `holm.csv`
- `decision.txt`（只填预声明的成功/失败句，见下）

---

## 5. `decision.txt` 只许四选一

```
VERDICT=VALGATE_SOLVES
# B0 在 U-Air 选 wo_design、SensorScope 选 full；测试满足非劣。
# 论文：Design 改为 validation-gated，不再声称五模块常开。

VERDICT=CONSTRAINED_SOLVES
# B1 或 B2 满足 §1 成功条件。
# 论文：默认 RAVEN 换成该变体；Table III 改为“约束后不再反向”。

VERDICT=DESIGN_DROPPED
# 所有候选失败。
# 论文：U-Air/默认关掉 Design；贡献改为两层（Obs+Use）+校准；
# Table III 的反向写成“因此默认不含 Design”。

VERDICT=UNRESOLVED_NEEDS_MORE
# 验证指标缺失 / runner 不能重建约束 / 只完成 Phase A。
# 不得把 Phase A 写成已经修好。
```

---

## 6. 红线

- 不改封印 E3/E4 数字，不覆盖 `paper_ready_r2/`。
- 不用测试 RMSE 选 \(\lambda\)、选门控、选“哪个变体写进摘要”。
- 不把 Tail RMSE 当最差组。
- 不用旧 checkpoint + 新 \(\alpha\) 报告 RMSE。
- 失败必须写进正文。藏起来比现在的 trade-off 更糟。
- T-Drive 不进本实验。

---

## 7. 论文怎么落（先跑后写）

- `VALGATE_SOLVES`：RQ3 增加一句“Design 由验证非劣规则开关”；摘要不再把 Design 写成必要层。
- `CONSTRAINED_SOLVES`：方法节把 (P2) 写成带 group no-harm 约束；Table III 用新默认重报。
- `DESIGN_DROPPED`：这是对审稿人最硬的回答。主张变窄，但 W1 关闭。

预估工作量：Phase A 数小时；B0 若有 val 则一天内；B1 重放视状态完整性；Phase C 全训与一次 E4 同量级（2 数据集 × 20 种子 × 1–2 新方法）。

---

## 8. 建议执行顺序

1. 先做 Phase A + B0（不新训）。
2. 把 `decision.txt` 的候选缩到一个。
3. 只有 B0 不够且 Phase A 显示是 \(\hat\beta\) 偏离时，再训 B1/B2。
4. 停。不要为了找一个能赢的 \(\lambda\) 再扫网格。
