# Cursor 执行指令：P1（修正版）— 量化 Δ_c-s 缺陷的部署后果

> 目的：把"RAVEN 的 Δ_c-s 优势"量化成"部署收益"，回答审稿人的"so what"。
> 这是把 Significance 从 3 推到 4 的关键：证明"更差的 Δ_c-s → 更差的组级部署结果"。
> **不需要新跑实验**：用现有 run 产物（complete_aligned + drifting）计算。
> 目标仓库：`D:\Cursor\raven.mcs`。论文工作稿：`_paper_work\main.tex`。

---

## 0. 数据源（已确认存在）

每个 run 目录（`artifacts/e3_formal_runs_r1/runs/{dataset}/{method}/seed{seed}/` 与
`artifacts/e3_drifting_r1/runs/{dataset}/{method}/seed{seed}/`）里：

- `p2_invocation_states.json` —— P2 求解记录，含每窗口 **debt Q_r**、**alpha**、**compositions (M_r)**（RavenAggregator 的 solve_results 会记录 debt/M/alpha）。
- `window_metrics.json` —— 每窗口 alpha、beta_hat、active_clients。
- `final_metrics.json` —— 聚合指标（RMSE_mu/Tail_RMSE/Delta_group/Delta_c_s）。
- `checkpoints/final.pt` —— 最终模型（可用于在测试集重算最差组误差，可选）。

方法：`fedavg_window, fedau_window, obsuse_window, twostage_hajek, raven`。
场景：complete_aligned（e3_formal_runs_r1）+ drifting（e3_drifting_r1）。
数据集：sensorscope, uair。种子：30001–30020。

---

## 1. 先查清（写进交付，别猜）

读 `p2_invocation_states.json` 的 1–2 个窗口，确认：
1. 是否含每窗口 `debt` 向量 Q_r（|G|=4 维）与 `M`（组合矩阵）；
2. 是否含 `omega_r = M_r @ alpha_r`（有效部署组组合）或能否由 M、alpha 算出；
3. `ledger.jsonl` 是否有补充的每窗口记录。

**若 debt/M/omega 不全**：明确列出缺什么、从哪个文件能补（如 window_metrics 的 alpha + 冻结的 target wiring），**不要编造**。

---

## 2. 定义部署后果指标（按此计算）

**指标 A — 组级欠服务（under-service）**：
- 每窗口 r、每个部署组 g：由 `omega_r(g) = (M_r alpha_r)(g)` 判断该组是否"有效代表"（如 `omega_r(g) < 0.5 * mu_g` 视为欠服务；阈值写在方法里并说明理由）。
- **欠服务累积**：对每个组 g，统计整个时域里欠服务窗口数（这正是 debt Q_r 追踪的对象）。

**指标 B — 最差组结果（可选，若可行）**：
- 用 `checkpoints/final.pt` 在测试集上重算每个部署组 g 的 RMSE，取最差组。
- 若不可行（无测试集/加载复杂），明确说"未计算"，不得用 Tail_RMSE 冒充最差组。

---

## 3. 计算 + 统计

- 对 5 方法 × 2 场景 × 2 数据集 × 20 seed，从现有 artifacts 计算指标 A（欠服务累积）和（可行时）指标 B。
- 配对 Wilcoxon + Holm，比较族：
  - RAVEN vs FedAU（核心）；
  - RAVEN vs ObsUse；
  - RAVEN vs FedAvg（对照）。
- 产出到 `_paper_work/deployment_consequence_results/`：
  - `under_service.csv`（dataset × method × seed × 欠服务累积，按组）；
  - `summary.csv`、`holm.csv`、`conclusion.txt`。

---

## 4. 诚实判读（conclusion.txt 模板）

```
Deployment-consequence audit (complete_aligned + drifting, 20 seeds).
- Group under-service accumulation: RAVEN vs FedAU / ObsUse / FedAvg（显著/不显著，p_holm）
- 若 drift 下差异更大：注明（Δ_c-s 优势在漂移下对应更少长期欠服务组）
- Worst-group（若算了）：RAVEN vs FedAU 最差组 RMSE 差异
Author verdict (honest):
- [Δ_c-s 优势是否确实转化为更少的长期欠服务组？]
- [一句话：这支持/不支持"结构对齐有真实部署收益"的论断]
```

**红线**：不编数字、不编显著性、不挑组、不挑种子；阈值与指标定义写清楚；若结果不支持（RAVEN 欠服务并不更少），如实写并说明含义。

---

## 5. 回填（仅当结果支持）

若 RAVEN 欠服务累积显著更低（尤其 drift 下）：
- 在 §VII-A（Δ_c-s 部署端论证段）后补一段 + 一张图（组欠服务累积 by method，complete_aligned vs drifting）：
  "The Δ_c-s advantage translates into measurably fewer persistently under-served deployment groups (esp. under drift), i.e., the structural objective has a direct deployment consequence."
- 数字/图与计算结果一致，重编译 0 错误。

若结果不支持：如实写进 limitation，不声称部署收益。

---

## 6. 完成标准

- "哪些组级量能算、从哪来"的查清结论（写进交付）；
- under_service.csv + summary + holm + conclusion 四件套；
- 诚实结论（支持/不支持部署收益）；
- 若回填：图 + 段落 + 重编译通过。
