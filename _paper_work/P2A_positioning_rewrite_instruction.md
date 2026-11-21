# Cursor 执行指令：P2-A — 论文定位重构（表述+理论为贡献）

> 目的：把论文从"方法赢了什么指标"重新定位为"**提出了一种新问题表述**"，方法作为构造性实例，诚实边界作为特征而非缺陷。
> 依据：P0/P1 已证明实证天花板（Δ_c-s 指标级稳健优势、无预测/覆盖增益）。P2-A 用写作把贡献重心移到**表述与理论**——这是最后、且诚实可行的提升。
> 目标文件：`D:\Cursor\raven.mcs\_paper_work\main.tex`。**全部是文字替换，不改任何数字/公式/表/图**。

---

## 改动 1：贡献定位句（引言，~L159）

**旧文本：**
```
Our main contributions are as follows.  Our contribution is a \emph{joint}
formulation and mechanism chain rather than a new estimator or optimizer: the
individual building blocks---survey-sampling weighting and convex
calibration---are standard, and we combine them only where the
deployment-target semantics require it.
```

**新文本：**
```
Our main contributions are as follows.  Our contribution is a \emph{problem
formulation} and its analysis rather than a method that wins benchmarks: we
define deployment-target risk semantics under two-stage non-random selection,
establish their non-interchangeability and the identification conditions under
which sequential correction recovers the target law, and provide a
constructive mechanism that realizes the formulation with boundary-respecting
evaluation.  The individual building blocks are deliberately standard; the
contribution is the formulation and its theory, not a claim of metric-level
superiority.
```

---

## 改动 2：摘要结尾句（~L69 中）

**旧文本：**
```
It also keeps deployment-target prediction risk comparable to the classic windowed baselines, while reweighting baselines attain lower prediction error at the cost of worse structural alignment.
```

**新文本：**
```
RAVEN-MCS is presented as a constructive instance of this formulation rather
than a claim of universal superiority: it keeps deployment-target prediction
error comparable to classic baselines, reports the prediction trade-off
relative to reweighting baselines explicitly, and claims no coverage-level
consequence that the evidence does not support.
```

---

## 改动 3：§VII-A 覆盖段（~L1915–1929）— 把"无覆盖后果"从 limitation 升级为"表述的自然结果"

**旧文本（整段）：**
```
That $\Delta_{c\text{-}s}$ gap does not, however, translate into fewer
persistently under-served client--stratum pairs under a coverage test.
Using the persisted per-window mixes on the $\Delta_{c\text{-}s}$ support,
a pair is counted as under-served when its window share falls below half
its public target mass.  RAVEN, FedAvg-Window, and TwoStage-H\'ajek then
produce identical under-service counts and identical persistently
under-served pair counts on both datasets, in both the complete-aligned and
drifting traces (20/20 ties).  FedAU-Window and ObsUse-Window differ by only
$5.8$ pair-windows out of $13867.5$ on SensorScope and $4.65$ out of
$6684.1$ on U-Air (Holm-significant versus RAVEN, but $<0.05\%$ relative),
and the number of persistently under-served pairs remains identical.
The structural advantage is therefore a difference in how mass is allocated
among already-covered pairs, not evidence that RAVEN leaves fewer groups
unserved.  Worst-group test RMSE was not recomputed from checkpoints and is
not inferred from tail RMSE.
```

**新文本（只改最后两句的解读，事实数字全部保留）：**
```
That $\Delta_{c\text{-}s}$ gap does not, however, translate into fewer
persistently under-served client--stratum pairs under a coverage test.
Using the persisted per-window mixes on the $\Delta_{c\text{-}s}$ support,
a pair is counted as under-served when its window share falls below half
its public target mass.  RAVEN, FedAvg-Window, and TwoStage-H\'ajek then
produce identical under-service counts and identical persistently
under-served pair counts on both datasets, in both the complete-aligned and
drifting traces (20/20 ties).  FedAU-Window and ObsUse-Window differ by only
$5.8$ pair-windows out of $13867.5$ on SensorScope and $4.65$ out of
$6684.1$ on U-Air (Holm-significant versus RAVEN, but $<0.05\%$ relative),
and the number of persistently under-served pairs remains identical.
This is consistent with the formulation's objective rather than a hidden
shortcoming: $\Delta_{c\text{-}s}$ measures the intensity with which target
mass is allocated across client--stratum pairs, not whether a pair crosses an
arbitrary coverage cutoff.  A method that minimized a coverage threshold
would be optimizing a different objective, which the present formulation
deliberately does not claim.  Worst-group test RMSE was not recomputed from
checkpoints and is not inferred from tail RMSE.
```

---

## 改动 4：结论开头（~L2036–2041）— 表述优先

**旧文本：**
```
This paper studied asynchronous federated data completion in mobile
crowdsensing from a deployment-target perspective.  The key observation is that
the data reaching the server are shaped sequentially by mobile opportunity,
actual observation, and usable-update selection. Consequently, the
arrival/usable-update distribution need not represent the distribution under
which the deployed predictor should be evaluated.
```

**新文本：**
```
This paper argues that asynchronous federated data completion in mobile
crowdsensing should be formulated as a deployment-target risk-alignment
problem rather than an arrival-centered learning problem.  The key observation
is that the data reaching the server are shaped sequentially by mobile
opportunity, actual observation, and usable-update selection.  Consequently,
the arrival/usable-update distribution need not represent the distribution
under which the deployed predictor should be evaluated.
```

---

## 改动 5（可选）：标题

**旧：**
```
\title{RAVEN-MCS: Target-Risk-Calibrated Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection}
```

**新（表述优先，且与 RAVEN 全称贴合）：**
```
\title{RAVEN-MCS: Deployment-Target Risk Alignment for Asynchronous Federated Data Completion in Mobile Crowdsensing under Two-Stage Non-Random Selection}
```

> 若你担心标题改动影响投稿记录/预印本一致性，可跳过此改动。

---

## 改完后的校验（必须做）

1. 重编译（`_paper_work` 下 pdflatex ×3 + bibtex），0 错误、0 undefined、0 overfull。
2. 自查：全文没有任何"RAVEN 全面优于"或"覆盖/预测也是优势"的表述；
3. 数字（3.96/2.01、2.62/2.28、0.04%、0.07%）与表 III/正文一致；
4. 改动 3 的解读句与事实段（20/20 ties、5.8/13867.5 等）保留完整，只改了"解读"。

## 完成标准

- 4 处（+可选标题）字面替换完成；
- 重编译通过；
- 论文重心已从"方法对比"移到"问题表述 + 理论 + 构造性实例 + 诚实边界"。
