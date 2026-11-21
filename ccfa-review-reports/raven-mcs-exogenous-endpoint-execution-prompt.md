# Executable instruction: City Scanner forward scores under three target weights

```text
Mode: design, then one execution prompt. This file starts no run.
Venue: IEEE TMC revision of RAVEN-MCS. Evidence for how sensitive the published
       City Scanner RMSE_μ is to the region weights. No manuscript edit.
Contract: CCFA-Skills/ccf-experiment-designer. This is protocol planning, so no
          publication-prose preflight.
Corrections baked in before execution:
  the repro target is each seed's stored RMSE_μ, not a typed 10-seed mean;
  WorstGroup on this block does not move when only μ changes;
  Tail is not a stored City Scanner endpoint;
  TARGET_SPEC.json is not in the City Scanner round directory.
```

## Claim–evidence matrix

| claim | evidence | not evidence |
|---|---|---|
| The published City Scanner `RMSE_μ` moves when the region weights change from the stored test-region share to M1 or M2 | 50 frozen checkpoints, one forward pass, three weight vectors | a retrained model |
| Arm order is stable across the three weight vectors | rank of the five arm means under each vector | a significance claim |
| Design-on is consistent with this block's own region-level map | already in `CS_PHI_DECISION.json`; record the correction, do not remeasure it | `eq:design_gate`, which is key-level |

## Dataset and arms

City Scanner only, `results_c1_cityscanner/round_v1/runs/cityscanner_nyc_pm25/`. Arms: `fedavg_window`, `twostage_hajek`, `fedau_window`, `obsuse_window`, `raven`. Seeds 32001–32010. All five stored runs are Design-on. There is no Design-off arm on this block.

## Confirmed scoring path

`scripts/run_nodesign_supplement.py` already loads this dataset with `apply_train_zscore_standardization`, predicts with `raven_mcs.e3.real_runner.runner._predict`, and scores with `_mu_weights_for_test` and `rmse_mu`. The new script calls those functions. It does not reimplement the weight formula.

---

你在仓库 `C:\Cursor\raven.mcs` 里执行。这是推理，不是训练。不改 `src/`，不改 `TO_OVERLEAF_paper_tmc_r1_clean/`，不改 `results_c1_cityscanner/`，不覆盖 `results_exogenous_target/round_v1/` 里已经落盘的 `MAP_*.csv`、`DOWNLOAD_LOG.json`、`PROOF_SKELETON.md`。不提交，不推送。

### 先写进报告的更正，然后再做前向

`results_c1_cityscanner/round_v1/CS_PHI_DECISION.json` 的目标是 region 级：`pi_i_tar = mu_of_region_h_i`，`mu_split = test_units_region_share_no_Y`，四个 region 权重与 `MAP_MARGINALS.csv` 里 `control` 的 region 边际一致，`phi_train_unit = 0`，所以该块自己的规则 `Design_ON iff phi_train_unit == 0` 给出 `design_on = true`。这和它自己的图不矛盾。

`eq:design_gate` 的 `ρ_r` 是 `(client, stratum)` 键级。同一块上对照图的键级 `ρ_r = 14.35%`，按论文的门应为 off。附录里 City Scanner 那行的「覆盖 0」是 region 级检验的结构性零。

在 `EXECUTION_REPORT.md` 第 6 节第 1 点改成上面这段事实。不要写成「运行期与自己的图矛盾」。不要改论文。

`TARGET_SPEC.json` 不在 `results_c1_cityscanner/round_v1/`。不要去找它。`CS_PHI_DECISION.json`、`CS_TRAIN_SETUP.json`、`CS_ACCEPTED.json` 足够。

### 权重

三个长度为 4 的向量，下标是 `CS_TRAIN_SETUP.json` 的 `h_encoding`（`region0→0` … `region3→3`）。数值从文件读，不许手抄进代码后就不再核对。

| 名字 | 来源 |
|---|---|
| `run` | `CS_PHI_DECISION.json` 的 `mu`，按 `h_encoding` 排成向量。它必须与 `CS_TRAIN_SETUP.json` 的 `mu` 列表在 `1e-12` 以内一致，否则停止 |
| `M1` | `MAP_MARGINALS.csv` 中 `map=M1` 的四行 `region0`–`region3` 的 `pi_sum` |
| `M2` | 同文件 `map=M2` 的四行 |

读出来应分别为：

```text
run  0.23732057416267943  0.47464114832535886  0.0708133971291866   0.21722488038277513
M1   0.30607816093394624  0.367698221016265    0.06125064169088319  0.2649729763589055
M2   0.21684976820757978  0.3991468881250436   0.04379795668554715  0.34020538698182945
```

与文件不一致就停止。三个向量各自和为 1；若差在 `1e-12` 以内，用现有 `_mu_weights_for_test`，不要自己再归一化一次。

### 接线

新脚本 `scripts/exogenous_target_endpoints.py`。

1. 用 `run_nodesign_supplement._load_cityscanner()` 加载数据。这一步包含 `apply_train_zscore_standardization`。跳过它，复现门会失败。
2. 测试单元必须是 2090 个。不是就停止。
3. `final.pt` 是 `state_dict`（`window_runner` 里保存的 `self.theta`）。用 `deterministic_common_ndmf(dataset.num_spatial, seed=seed)` 建模型，再 `load_state_dict`。对象不是 `state_dict` 就停止。
4. 预测只用 `raven_mcs.e3.real_runner.runner._predict`。打分只用 `_mu_weights_for_test` 和 `rmse_mu`。
5. `scripts/run_c1_cityscanner.py` 是 2 字节空壳。不要恢复它，不要训练。

同一份 `y_pred` 配三个权重。不要为 M1、M2 各跑一遍前向。

### 复现门

先只跑 `fedavg_window` / seed 32001 / 权重 `run`。`RMSE_μ` 与该种子的 `CS_ACCEPTED.json` 之差绝对值必须 `≤ 1e-6`。不过就停止，写出差值，不要改模型、不要改标准化、不要改权重定义。

通过后跑满 5 个 arm × 10 个种子。每一个种子的 `run` 列都按同一容差对照它自己的 `CS_ACCEPTED.json`。第一个失败就停止，不继续换权重出表。

DeepSeek 给出的 10 种子均值（fedavg 0.23788、raven 0.25490、twostage 0.25095、fedau 0.25817、obsuse 0.25657）只做事后核对：全部种子通过后，把你从 `CS_ACCEPTED.json` 重新算出的均值四舍五入到 5 位小数，与这五个数比较。对不上就在报告里写明，不要把它当成门。

### 换权重之后要报的数

表 `results_exogenous_target/round_v1/ENDPOINT_TABLE.csv`，一行一个 `(arm, seed)`：

```text
arm, seed, n_test,
RMSE_run, RMSE_M1, RMSE_M2,
WG_run, WG_M1, WG_M2,
RMSE_R0, RMSE_R1, RMSE_R2, RMSE_R3,
repro_abs_diff
```

`RMSE_Rg` 是该 region 内测试单元的等权 RMSE。在 `_mu_weights_for_test` 下，region 内权重是均匀的，四个 `μ_g` 都为正时，这四个数以及它们的最大值 `WG` 不随 `μ` 改变。`WG_run`、`WG_M1`、`WG_M2` 若有任何一个差超过 `1e-8`，当作接线错误停止。它们相等就在报告里写明：最差 region 对这三套 region 权重不变。不要把这种不变解释成「最差组对目标图稳健」。

不要算 Tail。`CS_ACCEPTED.json` 没有 Tail。不要算 `Δ_group` 和 `Δ_c-s`。这两列保持 `TBD`：它们依赖没有落盘的窗口聚合权重，换 `μ` 打分得不到它们。

`ENDPOINT_TABLE.json` 记录：三个权重向量、2090、复现差值的最大值、模型类名、`state_dict` 的键数。不要把逐单元预测写进这个文件。

### 汇总，事先写死读法

对每个权重，五个 arm 按 10 种子 `RMSE_μ` 均值从小到大排名。另外给出每个 arm 相对 `fedavg_window` 的 10 对配对相对差的均值，以及 `RMSE` 更小的种子数。不做 Holm，不把配对差叫显著。

允许的结果，算完不许改：

- 三个排名相同。
- 排名在某一套权重下翻转。翻转写出来，不要丢掉该 arm，也不要改权重。
- M1 或 M2 相对 `run` 的移动可以接近 0。这仍然是结果。

### 这一层不能写的句子

- 不能写「模型在外生目标下重新训练过」。轨迹和 checkpoint 都是在运行期那张 region 图上训练的。
- 不能写 `eq:design_switch` 的切换点。本块没有 Design-off。
- 不能写键级 `ρ_r` 被这次前向验证或推翻。这次只动 region 权重。
- 不能写 M1/M2 下的 `Δ_group` 或 `Δ_c-s`。

### 报告

把 `EXECUTION_REPORT.md` 第 4 节从 `TBD` 改成实测：复现门的最大绝对差、三套权重下的五 arm 均值、排名是否相同、`WG` 三列是否相等。第 6 节第 1 点按文首的更正改写。其余各节不动。

### 验收

1. `fedavg` seed 32001 的 `repro_abs_diff ≤ 1e-6`，否则没有 `ENDPOINT_TABLE.csv`。
2. 表有 50 行，`n_test` 全是 2090。
3. `WG_run`、`WG_M1`、`WG_M2` 在每一行上彼此相差不超过 `1e-8`。
4. 论文文件没有 diff。`results_c1_cityscanner/` 没有新文件。
