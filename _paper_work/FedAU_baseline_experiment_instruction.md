# Cursor 执行指令：为 RAVEN-MCS 论文补 FedAU-Window 基线

> 把本文件内容整体复制给 Cursor（或让 Cursor 读取本文件）即可。
> 目标：在现有实验框架内新增一个 `FedAU-Window` 基线并跑出结果，用于回应审稿意见「M2：最相关的参与重加权基线 FedAU 未对比」。

---

## 0. 仓库与环境

- 仓库根目录：`D:\Cursor\raven.mcs`（Python 包 `raven_mcs`，源码在 `src/raven_mcs/`）。
- 虚拟环境：`D:\Cursor\raven.mcs\.venv`（Python 3.11，已装 matplotlib/numpy/pandas/cvxpy/hydra-core 等）。
- 所有命令都在仓库根目录、使用该 venv 执行（Windows 下 `.venv\Scripts\python.exe`）。

**第一步先读这些文件（不要凭记忆猜 API）：**

1. `README.md`、`STATUS.md` —— 找到 E3 实验的真正运行入口（CLI 命令）。
2. `src/raven_mcs/aggregation/base.py` —— 看 `Aggregator` 和 `WindowAggregateInput` 有哪些字段（`client_ids`、`raw_counts`、`total_masses`、`beta_hat`、`compositions`、`mu`、`debt`、`variance_diag`、`staleness`、`extras` 等）。
3. `src/raven_mcs/aggregation/methods.py` —— 看已有基线怎么实现（重点是 `LocalHajekAggregator`、`TwoStageHajekAggregator`、`FedAvgWindowAggregator`、`DebtCalAggregator`）。
4. `src/raven_mcs/aggregation/method_policy.py` —— 看 `MethodPolicy` 的 `uses_*` 开关和 `POLICY_MAP` 注册方式。
5. `src/raven_mcs/training/window_runner.py` —— 看这些 `uses_*` 开关如何驱动 `beta_hat`（两阶段修正）与最终 `alpha` 的计算。
6. `src/raven_mcs/propensity/usable.py`、`src/raven_mcs/correction/second_stage.py` —— 看 `q_hat`（可用/参与倾向）和 `beta_hat` 是怎么估计的。
7. `configs/method/local_hajek.yaml`、`configs/method/twostage_hajek.yaml`、`configs/experiment/E3_main_complete.yaml` —— 看方法配置和实验配置格式。

---

## 1. FedAU-Window 的精确定义（必须严格按此实现）

FedAU 的核心是「按参与率倒数给客户端重加权」，在本论文的三层选择框架里**只对应 usable-update（参与）层**。因此：

**FedAU-Window 的服务器聚合权重：**

```
alpha_k  ∝  raw_count_k × (1 / p̂_part_k)
```

- `raw_count_k`：客户端 k 在本窗口的原始观测计数（与 FedAvg 相同来源）。
- `p̂_part_k`：客户端 k 的**滞后、pre-outcome 参与率估计**：

```
p̂_part_k = (k 在 r-1 及之前窗口的 usable 次数 + ε) / (k 在 r-1 及之前窗口的注册尝试次数 + ε)
```

- `ε` 是小的平滑常数（建议 1e-6，与代码库其它倾向估计一致），用于避免除零。
- 归一化到 `sum(alpha) = 1`（复用 `_normalize`）。

**FedAU-Window 明确「不用」的东西（这是它与 RAVEN 的关键区别）：**

- 不用 design ratio（机会/设计层修正 ζ）。
- 不用 observation IPW（观测层 1/p）。
- 不用 Hájek 局部损失（`uses_hajek_local_loss=False`）。
- 不用 P2 可行性校准、不用债务、不用 variance/staleness 惩罚。

即：**FedAU-Window ≈ 「仅 usable-update 层逆加权」，其余全部按 FedAvg 的原始计数**。

---

## 2. 需要改动/新增的文件（4 处）

### (a) 新增聚合器 —— `src/raven_mcs/aggregation/methods.py`

在文件里新增一个类（放在 `FedAvgWindowAggregator` 附近即可）：

```python
class FedAUWindowAggregator(Aggregator):
    """FedAU-Window: inverse-participation (usable-layer) client reweighting only.

    This is the windowed adaptation of FedAU (wang2024lightweight), NOT an
    official reproduction. It reweights each client by the inverse of its
    lagged, pre-outcome participation rate; it does NOT correct the
    opportunity/design or observation layers and does NOT run (P2) or debt.
    """

    name = "fedau_window"

    def __init__(self, epsilon: float = 1e-6) -> None:
        self.epsilon = float(epsilon)

    def compute_server_weights(self, payload: WindowAggregateInput) -> np.ndarray:
        # TODO(实现)：从 payload 取得每个客户端的滞后参与率 p̂_part_k。
        # 若 WindowAggregateInput 已暴露可用倾向 q_hat（payload.extras 或专用字段），
        # 优先直接复用 q_hat 作为 p̂_part_k 的来源，但务必确认它是 pre-outcome、lagged。
        # 若 payload 未暴露参与历史，需要从 window_runner 传入一个 lagged
        # participation_rate 字段（见 (d)），并在此消费。
        ...
        return _normalize(raw_counts * (1.0 / participation_rate))
```

> 关键：**先读 base.py 和 window_runner.py，确认参与率从哪来**。如果 `payload` 已经有 `q_hat` 或 `participation_rate`，直接复用；如果没有，就在 window_runner 里按 lagged 历史算好再放进 payload（如 `payload.extras["participation_rate"]`）。**不要用当前窗口的 U 结果**，也不要碰 test label。

### (b) 注册策略 —— `src/raven_mcs/aggregation/method_policy.py`

在 `POLICY_MAP` 里加：

```python
"fedau_window": MethodPolicy(
    uses_usable_ipw=True,      # 仅参与层逆加权
    # 其余全部默认 False（不用 design/observation/hajek/inst/debt/reference/variance/staleness）
),
```

### (c) 注册聚合器 —— `src/raven_mcs/aggregation/methods.py` 的 `get_aggregator`

在 `mapping` 里加：

```python
"fedau_window": FedAUWindowAggregator,
"fedau": FedAUWindowAggregator,
```

### (d) 新增方法配置 —— `configs/method/fedau_window.yaml`

```yaml
name: fedau_window
description: FedAU-Window: inverse-participation (usable-layer) client reweighting only; no design/observation correction, no P2, no debt
uses_design_ratio: false
uses_obs_correction: false
uses_use_correction: true
uses_instant_calibration: false
uses_debt: false
uses_reference: false
uses_variance: false
uses_staleness: false
```

### (e) 加入 E3 实验 —— `configs/experiment/E3_main_complete.yaml`

把 `methods` 列表加上 `fedau_window`：

```yaml
methods: [fedavg_window, fedasync_window, timealign_agg, local_hajek, twostage_hajek, fedau_window, inst_cal, debt_cal, raven]
```

---

## 3. 协议与诚实红线（必须遵守）

1. **公平性**：FedAU-Window 与所有 E3 方法共享同一骨干模型、同一 `E_loc` 局部步、同一步长、同一 usable 集、同一 selection trace、同一 20 个种子。**只允许聚合权重计算不同。**
2. **信息边界**：参与率必须 lagged（pre-outcome），不得用当前窗口的 U 结果、不得用 test label。这与论文 §III 的信息边界一致。
3. **声明措辞**：在论文/结果里必须写「windowed adaptation of FedAU, not an official reproduction」，与 TimeAlign-Agg 的声明一致。
4. **不伪造**：跑不出来就留 `TBD`，绝不编数字、编显著性、编排名。若 RAVEN 对 FedAU 不显著，如实报告为 limitation，不得写成优势。

---

## 4. 运行

1. 先确认环境与包：
   ```
   .venv\Scripts\python.exe -m pip install -e .
   .venv\Scripts\python.exe scripts/verify_run.py --check-environment
   ```
2. 按第 0 步找到的 E3 运行入口，跑 `E3_main_complete`（或等价命令），**至少覆盖 sensorscope 和 uair**（traffic 按论文不用于方法级推断，可跑可不跑）。
3. 若 E3 入口要求每个方法一个 config，确认新增的 `fedau_window.yaml` 被正确拾取；必要时照抄 `twostage_hajek` 的接入方式。

---

## 5. 输出（都要给出来）

1. **结果 CSV**：每个 dataset × seed × 方法的四个指标 `RMSE_mu`、`Tail_RMSE`、`Delta_group`、`Delta_c_s`（含 `fedau_window`）。
2. **统计**：配对 Wilcoxon + Holm，两组比较：
   - (a) RAVEN-MCS vs FedAU-Window（核心）；
   - (b) FedAU-Window vs FedAvg-Window（验证 FedAU 基线本身有效）。
3. **LaTeX 结果表**（填真实数字，替换 TBD）：

```latex
\begin{table*}[t]
\centering
\caption{E3 with participation-reweighting baseline (mean $\pm$ std over 20
paired seeds). Lower is better. FedAU-Window applies inverse-participation
client weights only. Holm-corrected families: RAVEN-vs-FedAU, FedAU-vs-FedAvg.}
\label{tab:e3_fedau}
\setlength{\tabcolsep}{4.5pt}
\begin{tabular}{llcccc}
\toprule
Dataset & Method & $\mathrm{RMSE}_{\mu}$ & Tail RMSE &
$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
\midrule
\multirow{4}{*}{SensorScope}
& FedAvg-Window   & TBD & TBD & TBD & TBD\\
& FedAU-Window    & TBD & TBD & TBD & TBD\\
& TwoStage-Hajek  & TBD & TBD & TBD & TBD\\
& RAVEN-MCS       & TBD & TBD & TBD & TBD\\
\midrule
\multirow{4}{*}{U-Air}
& FedAvg-Window   & TBD & TBD & TBD & TBD\\
& FedAU-Window    & TBD & TBD & TBD & TBD\\
& TwoStage-Hajek  & TBD & TBD & TBD & TBD\\
& RAVEN-MCS       & TBD & TBD & TBD & TBD\\
\bottomrule
\end{tabular}
\end{table*}
```

4. **一句话结论**（给作者的判读）：
   - 若 FedAU 的 `Delta_c_s` 优于 FedAvg → 参与去偏在本设置有效（基线可信）；
   - 若 RAVEN 的 `Delta_group`、`Delta_c_s` 显著优于 FedAU → M2 解决（三层+校准 强于 仅参与重加权）；
   - 若 RAVEN 不显著优于 FedAU → **必须如实报告**，并把贡献表述收紧。

---

## 6. 完成标准

- `fedau_window` 已在 methods.py / method_policy.py / configs 三处注册；
- E3 跑通 sensorscope + uair，20 种子，产出含 fedau_window 的四个指标 CSV；
- 两组配对 Wilcoxon + Holm 结果给出；
- 上表 TBD 全部替换为真实数字（或明确标注哪格因运行失败而缺失，绝不伪造）；
- 一句诚实结论（RAVEN vs FedAU 显著/不显著）。
