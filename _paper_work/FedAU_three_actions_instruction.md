# Cursor 执行指令：完成三个收尾动作（提升至 weak-accept）

> 论文已回填 FedAU 并修好两个 critical。本指令完成三个动作：
> 1) 论证 Δ_c-s 是部署端关键指标；2) 补"Obs+Use 两层"机制消融；3) 补 code/availability 声明。
> 目标文件：`D:\Cursor\raven.mcs\_paper_work\main.tex`（当前工作稿）。

---

## 动作 1：论证 Δ_c-s 是部署端关键指标（纯文字，无代码）

**插入位置**：§VII-A，在现有段落 "…universal RMSE dominance." 之后（该段落结尾是 `\emph{consistent structural correction with competitive deployment-target prediction risk and selective predictive gains}, rather than universal RMSE dominance.`），在 `\subsection{RAVEN as a Coupled Correction System}` 之前。

**插入文本**（LaTeX，直接粘贴）：

```latex
The finer client--stratum objective is the deployment-critical one.  Group-level
alignment ($\Delta_{\mathrm{group}}$) and client--stratum alignment
($\Delta_{c\text{-}s}$) capture different deployment risks.  A predictor can
match the aggregate group mass while still misrepresenting which clients and
opportunity strata produced the data, and this stratum-level error is exactly
what persists across windows and compounds through the long-term debt process.
The FedAU comparison makes the distinction concrete: participation reweighting
improves aggregate prediction on U-Air while degrading $\Delta_{c\text{-}s}$ on
both datasets, because rescaling whole clients cannot repair a mis-weighted
stratum.  Since RAVEN's deployment objective is to keep the selected training
mass representative at the finest stratum where selection acts,
$\Delta_{c\text{-}s}$ is the metric that directly tests that objective, so its
consistent, dataset-spanning reduction is the primary empirical result rather
than a secondary diagnostic.
```

**不要改动任何数字**；这一段只做"为什么 Δ_c-s 重要"的论证。

---

## 动作 2：补 "Obs+Use 两层" 机制消融（代码 + 运行 + 回填）

**目的**：形成单调证据链 `FedAvg(0层) → FedAU(仅Use) → ObsUse(Obs+Use) → TwoStage-Hajek(三层) → RAVEN(三层+校准+债务)`，正面回答"三层是否真比一两层强"。

**复用已有 FedAU 文件作为模板**（这些文件已存在）：
- `scripts/run_e3_fedau_window.py`
- `scripts/summarize_e3_fedau_window.py`
- `tests/unit/test_fedau_window_aggregator.py`
- `configs/method/fedau_window.yaml`

### 2.1 新增聚合器（`src/raven_mcs/aggregation/methods.py`）

照 `FedAUWindowAggregator` 的写法新增 `ObsUseWindowAggregator`：

```python
class ObsUseWindowAggregator(Aggregator):
    """ObsUse-Window: observation + usable-update inverse weighting (no design ratio)."""
    name = "obsuse_window"

    def __init__(self, epsilon: float = 1e-6) -> None:
        self.epsilon = float(epsilon)

    def compute_server_weights(self, payload: WindowAggregateInput) -> np.ndarray:
        # 服务器权重 ∝ raw_counts × (1/p̂_obs) × (1/q̂_use)，归一化。
        # 先读 base.py / window_runner.py 确认 p̂_obs 与 q̂_use 从哪取
        # （应与 FedAU-Window 的 q̂_use 来源一致，并叠加观测倾向 1/p̂_obs）。
        # 不用 design ratio，不用 hajek_local_loss，不用 P2/债务/惩罚。
        ...
        return _normalize(raw_counts * obs_inv * use_inv)
```

同时在 `get_aggregator` 的 `mapping` 里注册：
```python
"obsuse_window": ObsUseWindowAggregator,
"obsuse": ObsUseWindowAggregator,
```

### 2.2 注册策略（`src/raven_mcs/aggregation/method_policy.py`）

在 `POLICY_MAP` 里加：
```python
"obsuse_window": MethodPolicy(
    uses_observation_ipw=True,
    uses_usable_ipw=True,
    # 其余全部默认 False
),
```

### 2.3 新增方法配置 `configs/method/obsuse_window.yaml`

```yaml
name: obsuse_window
description: ObsUse-Window: observation + usable-update inverse weighting; no design ratio, no P2, no debt
uses_design_ratio: false
uses_obs_correction: true
uses_use_correction: true
uses_instant_calibration: false
uses_debt: false
uses_reference: false
uses_variance: false
uses_staleness: false
```

### 2.4 运行（照 `run_e3_fedau_window.py` 改方法名）

- 复制 `scripts/run_e3_fedau_window.py` 为 `scripts/run_e3_obsuse_window.py`，把方法名 `fedau_window` 换成 `obsuse_window`。
- 跑 **sensorscope + uair**，20 配对种子（30001–30020），同 selection trace，同骨干/步长。
- 复制 `scripts/summarize_e3_fedau_window.py` 为 `scripts/summarize_e3_obsuse_window.py`，产出 `per_seed / summary / holm / table / conclusion` 五个文件到 `_paper_work/obsuse_window_results/`。

### 2.5 回填（结果出来后）

1. §VI-A 基线清单加 ObsUse-Window（与 FedAU-Window 并列，同样注明"windowed adaptation, not official reproduction"）。
2. Table III 给 SensorScope/U-Air 各加一行 ObsUse-Window（真实数字，精度同表）。
3. fig3/fig4 的 CSV + `make_figures.py` 加 `ObsUse-Window`，重绘。
4. §VI-B 补一句单调链结论（只写数据支持的）：
   - 若 `FedAU → ObsUse → TwoStage-Hajek → RAVEN` 在 Δ_c-s 上单调改善 → 写"逐层加入观测/设计修正后，Δ_c-s 单调下降"；
   - 若 ObsUse 不优于 FedAU → 如实写，不得编造单调性。
5. 重编译校验（同前）。

---

## 动作 3：补 code/data availability 声明（纯文字）

**插入位置**：在 `\appendices`（约 2020 行）**之前**新增一小节（或段落）：

```latex
\section{Reproducibility and Data Availability}

All datasets are public and cited in
Section~\ref{subsec:eval_setup}: SensorScope
(DOI 10.5281/zenodo.2654726), U-Air, and NSW-Traffic.  The frozen selection
traces, target strata, the 20 paired seeds, and the result CSVs that reproduce
Tables~\ref{tab:main_effectiveness}--\ref{tab:e4_ablation} are archived with the
submission.  Source code, the feasibility solver (P2), and the windowed
aggregation implementations (including the FedAU-Window and ObsUse-Window
adaptations, which are windowed re-implementations rather than official
reproductions) will be released upon acceptance under an open-source license.
```

> 如果投稿系统要求匿名，把"upon acceptance"改成"in the camera-ready version"，并确认不泄露作者信息。

---

## 三个动作完成后的统一校验

1. 重编译（pdflatex+bibtex×3），0 错误、0 undefined、0 overfull。
2. 数字一致性：新增 ObsUse 数字在 表 ↔ 正文 一致，精度统一。
3. 无"全面优于"类绝对化表述；若 ObsUse 结果不是单调的，如实写。
4. availability 声明无作者信息泄露。

## 完成标准

- 动作 1 的 Δ_c-s 论证段已插入 §VII-A；
- 动作 2 的 ObsUse-Window 已实现、跑通、回填（表 + 图 + 叙事）；
- 动作 3 的 availability 声明已插入 \appendices 之前；
- 重编译通过，无矛盾、无越界声称。
