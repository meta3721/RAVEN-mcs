# Cursor 执行指令：P0 — Drifting 场景压测（评估 RAVEN 的时变部署价值）

> 目的：证明 RAVEN 的 debt + 可行性校准机制在**目标/选择随时间漂移**的部署场景里真正管用。
> 这是提升论文 Significance（5.5→6.5）的关键实验：RAVEN 的长期债务正是为"时变可行支撑下跟踪目标"设计的，这是它**最该赢**的场景。
> 目标仓库：`D:\Cursor\raven.mcs`。论文工作稿：`D:\Cursor\raven.mcs\_paper_work\main.tex`。

---

## 0. 先读这些（不要凭记忆猜）

1. `src/raven_mcs/e3/real_runner/runner.py` —— 看 `run_e3_real(..., scenario: str = SCENARIO, ...)` 的 `scenario` 参数怎么用：是选 EventTrace 路径，还是影响选择事件生成。
2. `src/raven_mcs/e3/formal/eventtrace.py` 和 `src/raven_mcs/e3/formal/execute.py` —— 看 sealed EventTrace（`artifacts/e3_formal_runs_r1/eventtraces/{dataset}/seed{seed}/training_eventtrace`）是怎么按 scenario 生成的。
3. `configs/scenario/drifting.yaml` —— 漂移参数：`opportunity_skew: 1.0`、`mean_observation_rate: 0.20`、`mean_usable_rate: 0.60`、`drift_period: 50`、`drift_magnitude: 0.1`。
4. `configs/scenario/complete_aligned.yaml` 和 `configs/experiment/E3_main_complete.yaml` —— 对比现有完整对齐配置。
5. `scripts/run_e3_fedau_window.py` 和 `scripts/run_e3_obsuse_window.py` —— 这是本轮要复用的运行模板（已跑通）。

**关键问题（读完后回答，写在交付里）**：
- drifting 场景的 EventTrace 是否已有 sealed 产物？如果有，路径在哪？
- 如果没有，哪个生成器 + 什么命令能产出 drifting 的 20 个 seed × sensorscope/uair 的 EventTrace？
- `run_e3_real` 的 `scenario` 参数是否必须在调用时传 `"drifting"`（还是 EventTrace 本身已编码漂移）？

---

## 1. 生成（或找到）drifting EventTrace

- 若已有 sealed drifting traces：直接用，记录来源路径。
- 若没有：用仓库现成的场景/事件流生成器（`src/raven_mcs/e3/formal/` 或 `src/raven_mcs/simulation/` 下与 scenario 相关的部分，配置 `configs/scenario/drifting.yaml`），**按与 complete_aligned 相同的 20 个种子（30001–30020）和相同的生成协议**产出 drifting traces，存到新目录（如 `artifacts/e3_drifting_r1/eventtraces/...`），与 sealed 产物隔离。

**红线**：只改 scenario 参数，**不得**改方法实现、不得改种子、不得改 trace 结构；trace 必须 pre-outcome、与现有 complete_aligned 同构。

---

## 2. 运行方法族（drifting 下）

新建 `scripts/run_e3_drifting.py`（照 `run_e3_fedau_window.py` 改）：

- 方法：`fedavg_window, fedau_window, obsuse_window, twostage_hajek, raven`（5 个，够形成 `FedAvg → FedAU → ObsUse → TwoStage → RAVEN` 链）。
- 数据集：sensorscope + uair。
- 种子：30001–30020（`FORMAL_SEEDS`）。
- EventTrace：第 1 步得到的 drifting traces。
- 输出：`artifacts/e3_drifting_r1/runs/{dataset}/{method}/seed{seed}/final_metrics.json`（复用 `run_e3_real`，若 `scenario` 参数需要显式传 `"drifting"` 就传）。

**不要**动 complete_aligned 的 sealed 产物；drifting 结果全部写进 `e3_drifting_r1` 独立目录。

---

## 3. 汇总 + 统计

新建 `scripts/summarize_e3_drifting.py`（照 `scripts/summarize_e3_fedau_window.py`），产出到 `_paper_work/drifting_window_results/`：

- `per_seed.csv`：dataset × method × seed × {RMSE_mu, Tail_RMSE, Delta_group, Delta_c_s}
- `summary.csv`：mean ± std（20 seed）+ CI
- `holm.csv`：配对 Wilcoxon + Holm，两个族：
  - `raven_vs_fedau`（核心：RAVEN vs 参与重加权，漂移下）；
  - `raven_vs_fedavg`（对照）。
- `conclusion.txt`：诚实判读（见第 5 节模板）。

---

## 4. 回填（仅当结果支持；否则如实写）

跑完后，把结果写进 `_paper_work\main.tex`：

1. 若 RAVEN 在 drifting 下 Δ_c-s / Δ_group 对 FedAU/ObsUse/TwoStage **优势保持或放大**：在 §VI-B（或新增一小段）写"under time-varying opportunity drift, the debt-calibrated correction sustains the structural gain, whereas participation reweighting does not track the drifting target"。
2. 若 **debt 有界**（可用论文 eq. debt_bound 的结论佐证）：写"long-term target debt remains bounded under drift"。
3. 若 RAVEN **不赢**：如实写进 limitation（"the drift-stress experiment does not favor RAVEN"），**不得**声称优势。
4. 数字与 holm.csv 严格一致；精度统一。

---

## 5. 诚实判读模板（conclusion.txt 里按此写）

```
Drifting scenario (drift_period=50, drift_magnitude=0.1), 20 paired seeds 30001-30020.
- RAVEN vs FedAU (Δ_c-s / Δ_group): 显著/不显著，p_holm=...
- RAVEN vs FedAU (RMSE_mu / Tail): 显著/不显著，p_holm=...
- RAVEN vs FedAvg (Δ_c-s): 显著/不显著，p_holm=...
- Debt 有界性: [观察到的 Q_r 趋势]
Author verdict (honest):
- [RAVEN 在漂移下是否维持结构优势？是否仍被 FedAU 反超预测？]
- [一句话：这个实验支持/不支持 RAVEN 的时变部署价值]
```

**红线**：不编数字、不编显著性、不挑种子、不写"全面优于"；若结果两面，如实两面都写。

---

## 6. 完成标准

- drifting EventTrace 来源已查清并在交付里说明；
- 5 方法 × 2 数据集 × 20 seed 跑通（全部 OK，无失败）；
- per_seed / summary / holm / conclusion 四件套产出；
- 结论诚实（若 RAVEN 不赢，明确写入 limitation 并在交付说明）；
- 若回填：数字与 holm.csv 一致，重编译 0 错误。

---

## 交付物

1. 查清"drifting trace 从哪来"的结论（一句）；
2. `scripts/run_e3_drifting.py` + `scripts/summarize_e3_drifting.py`；
3. `_paper_work/drifting_window_results/` 四件套；
4. 是否回填 + 回填位置说明。
