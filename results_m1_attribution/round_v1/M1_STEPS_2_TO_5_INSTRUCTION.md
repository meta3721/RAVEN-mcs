# 方法一第 2 步到第 5 步指令

日期：2026-10-18。第 1 步已经写完并停止。预注册是 `results_m1_attribution/round_v1/M1_PREREG.md`，目标抄本是同目录 `M1_MU.json`。本文件授权按顺序执行第 2、3、4、5 步。任一步的停止条件成立，后面的步骤不跑。

```text
Mode: design
Venue and assumptions: IEEE TMC。只读正式轨迹上的已到达客户端。不训练，不改预测，不把距离写成 RMSE 下界。
No-fabrication status: 窗口数字只能来自本指令跑出的轨迹。不得把开发几何、跨窗 P0 的可调质量或主表数字填进结果格。第 4 步只核对本方案算的 μ_adj 是否与 P0_WINDOWS.csv 的 adj_A 一致。
Next CCFA owner: 执行者交本指令列出的文件。未经用户点名，不交给 ccf-paper-writer，不改 main.tex。
```

## 总约束

- 常数、归一、三项质量、四段距离、容差和分层以 `M1_PREREG.md` 为准。不改 \(\alpha_{\max}=0.5\)、\(E_{\min}=3\)、阈值 0.01，不改三个容差。
- 几何使用 `M1_MU.json` 的原始 `mu`。三个正式块的 `sum` 都大于 0，计算时每个值除以该块的 `sum`。不另写归一化文件。
- 新脚本只放在 `results_m1_attribution/round_v1/`。Python 使用 `.venv_new\Scripts\python.exe`。
- 不修改 `src/`、`TO_OVERLEAF_paper_tmc_r1_clean/`、`results_xw_pool/`、`results_reachability_detector_v1/`、`results_main_rebuild_r1/diagnose_geometry.py`。
- 不创建 `runs/`，不训练，不生成 EventTrace，不读 \(q^{\mathrm{use}}\)，不把开发轨迹的 `beta` 拷进来。
- 不打开 City Scanner 与 T-Drive 的轨迹。这两块和 Pilot 2 保持预注册里的 blocked 原句。
- 种子 41001–41003、45001，以及固定 \(K\in\{4,8,16\}\) 的子集，不进入。
- 不构造保留池，不使用 \(S_{\max}\) 过滤客户端。

## 客户端集合

与跨窗 P0 的到达窗集合 \(A_r\) 相同，才能做第 4 步核对。

一条已交付尝试是 `events.parquet` 里 `U=1` 的行。身份是 `(client_id, downloaded_version, window_id)`。同一身份出现两次，该块停止。组标签使用 `results_xw_pool/round_v1/p0_geometry.py` 里 `group_from_features` 的同一规则，对着该块归一后的 \(\mu\) 键。读不出唯一 \(\mu\) 键时，该块记为 blocked，不补标签，不写该块的窗口行。

关闭 \(r\) 的客户端集合：`window_id=r` 的已交付尝试，每个 `client_id` 只留 `downloaded_version` 最大的一条。不加年龄过滤。\(K=0\) 的关闭不写行。

窗口上的界是 \(\overline\alpha_r=\min\{1,\max\{0.5,1/K\}\}\)，\(\overline E_r=\min\{3,K\}\)。\(K\le 3\) 时可行集只有均匀权重。

\(W_g\) 沿用 `p0_geometry.py` 里 `feasible_interval` 与 `adjustable` 的算术，抄进新脚本，不改原文件。\(K\le 3\) 时 \(\mu_{\mathrm{adj}}=0\)。这个闭式只用于独热组行的区间宽度。本方案的组标签来自 `group_from_features`，因此行是独热的。出现混合组成行时标记 `row_type=mixed`，三项质量仍算，但不得用该闭式硬套距离恒等式。

## 四段距离

在客户端权重 \(\alpha\) 上最小化 \(\lVert M\alpha-\mu\rVert_1\)。\(\alpha\) 在单纯形上。四个问题是：

- \(d_{\mathrm{simplex}}\)：不再加约束
- \(d_{\mathrm{cap}}\)：再加 \(\alpha_k\le\overline\alpha_r\)
- \(d_{\mathrm{ESS}}\)：再加 \(\sum_k\alpha_k^2\le 1/\overline E_r\)
- \(d_{\mathcal C}\)：cap 与 ESS 都加

用已安装的凸求解器计算。不新装包。环境里没有可用求解器时，第 2 步停止，不改成网格搜索，也不把 \(d_{\mathrm{simplex}}\) 直接写成 \(2\mu_{\mathrm{miss}}\) 来通过恒等式。求解器可行性违约超过 \(10^{-7}\) 的窗口作废并停止该块。

独热窗口另算 \(2\mu_{\mathrm{miss}}\)，与求解器给出的 \(d_{\mathrm{simplex}}\) 比较。偏离超过 \(10^{-6}\) 则停止，并写出偏离，不改恒等式。

单调性：\(d_{\mathcal C}\ge d_{\mathrm{cap}}\ge d_{\mathrm{simplex}}\) 且 \(d_{\mathcal C}\ge d_{\mathrm{ESS}}\ge d_{\mathrm{simplex}}\)，容差 \(10^{-6}\)。三个增量都保留。

\(\mu_g=0\) 的组不进入三项质量。客户端组键不在 \(\mu\) 里时计入 `off_target_clients`。`group_from_features` 只返回 \(\mu\) 中的键，因此该计数预期为 0；出现非零时照实写入，不把这些客户端改派到别的组。

## 第 2 步：一次冒烟

只读这一条轨迹：

`artifacts/e3_formal_runs_r1/eventtraces/traffic/seed30001/training_eventtrace/events.parquet`

取其中第一个 \(K\ge 1\) 的关闭。检查三件事：三项质量之和与该窗正 \(\mu\) 之和的差不超过 \(10^{-8}\)；\(d_{\mathcal C}\ge d_{\mathrm{simplex}}\)；若该窗 \(K\le 3\)，则 \(\mu_{\mathrm{adj}}=0\)。同时检查独热恒等式和距离单调性。

通过时写 `M1_SMOKE.md`，只写窗口编号和哪些恒等式成立。不写该窗的质量或距离数字，不写 RMSE。通过只说明脚本读进了这条轨迹。

失败时写 `M1_SMOKE.md` 和偏离值，并写 `M1_STATUS.json` 为 `stopped`。不写 `M1_WINDOWS.csv`，不进入第 3 步。

## 第 3 步：三块的质量与距离

仅在第 2 步通过后执行。轨迹目录：

- NSW-Traffic：`artifacts/e3_formal_runs_r1/eventtraces/traffic`
- SensorScope：`artifacts/e3_formal_runs_r1/eventtraces/sensorscope`
- U-Air：`artifacts/e3_formal_runs_r1/eventtraces/uair`

每块使用该目录下已有的 `seed*/training_eventtrace/events.parquet`。不新增种子，不因为某个种子缺失而另找开发轨迹。

写出 `M1_WINDOWS.csv`，一行一个关闭。列至少包括：`block`，`seed`，`window`，`K`，`n_groups`，`row_type`，`off_target_clients`，`mu_miss`，`mu_pin`，`mu_adj`，`mu_positive`，`d_simplex`，`d_cap`，`d_ess`，`d_C`，`inc_cap`，`inc_ess`，`inc_joint`。

某一块在读组标签时 blocked：该块不写窗口行，原因写入 `M1_STATUS.json`。其他块继续。质量或距离恒等式失败：该块 `stopped`，写出偏离，不删窗口来换阈值，不进入第 4 步的均值。

## 第 4 步：核对可调质量

仅在第 3 步没有 `stopped` 时执行。打开 `results_xw_pool/round_v1/P0_WINDOWS.csv`。对三个正式块，按 `block,seed,window` 对齐。本方案的 \(\mu_{\mathrm{adj}}\) 必须与该文件的 `adj_A` 一致，容差 \(10^{-8}\)。窗口集合也必须一致：一边有而另一边没有的关闭算不一致。

不一致则整轮 `stopped`。不取平均，不改 \(W_g\) 的定义，不写 `M1_SUMMARY.csv`。

一致之后才写 `M1_SUMMARY.csv`。主行是块 \(\times\) 层，层只有 \(K\le 3\) 和 \(K>3\)。每行是该层里各种子均值，再对种子取均值。某个种子在该层没有窗口时，不把该种子算成 0，并在 `n_seeds` 里减去。列包括窗口数、三项质量、四个距离、三个增量、独热窗份额、组数均值。

描述性区间可以写在汇总里：对各种子的层内均值做百分位区间，10000 次，随机种子 20261019。不是通过线。不使用 20261018、20261007、20261002。全窗均值不作为主行。

## 第 5 步：估计位移

仅在第 4 步写出了 `M1_SUMMARY.csv` 之后执行。

只在每个已用种子目录内查看：`events.parquet` 的列名，以及 `metadata.json`、`trace_identity.json`、`e2_reuse_provenance.json`。这三份侧车文件不含逐窗投影前参考。若列名和这三份文件里没有与该窗客户端行对齐的 \(\widehat r\)，则不打开 `e2_reuse_provenance.json` 指向的源目录，不打开 `runs/`，不拟合 \(q\)。

此时写 `M1_ESTIMATE.csv`，只有表头：`block,seed,window,delta_ref,delta_dec`。`M1_STATUS.json` 里估计列记为 blocked，几何列仍可为 complete。

若确实存在逐窗、与客户端对齐的 \(\widehat r\)，才计算 \(\delta_{\mathrm{ref}}=\lVert\widehat r-\mu\rVert_1\) 和 \(\delta_{\mathrm{dec}}=\lVert\alpha(\widehat r)-\alpha(\mu)\rVert_1\)。两个向量都先归一到组和为 1。没有对齐的窗口留空，不插值。

## 状态文件

`M1_STATUS.json` 在本轮结束时必须存在。每个块是 `complete`、`blocked` 或 `stopped`。City Scanner 访问占用、Pilot 2、T-Drive 写入预注册中的 blocked 原因。另记作废窗口数。几何完成指未作废窗口满足质量分解和距离单调，且第 4 步对齐通过。估计列 blocked 不否定几何完成。

## 停止

出现任一条即停，不改定义后重跑：

- 冒烟恒等式失败。
- 质量三项之和偏离正 \(\mu\) 超过 \(10^{-8}\)。
- 距离违反单调性，超过 \(10^{-6}\)。
- 独热窗口上 \(d_{\mathrm{simplex}}\) 偏离 \(2\mu_{\mathrm{miss}}\)，超过 \(10^{-6}\)。
- \(K\le 3\) 的窗口出现非零 \(\mu_{\mathrm{adj}}\)。
- 与 `P0_WINDOWS.csv` 的 `adj_A` 或窗口集合不一致。
- 为估计列读取了 \(q^{\mathrm{use}}\)、开发 `beta`，或打开了 provenance 里的源轨迹目录。
- 使用了保留池、\(S_{\max}\) 过滤或开发几何的 cap。
- 需要修改 `src/` 或论文才能继续。
- 需要新装求解器或改用网格才能算距离。

三块窗口都落在同一类里仍然可以 complete。写出该类。不因此放宽阈值，不因此进入决策实验。

## 完成时目录里应有的文件

- 已有：`M1_PREREG.md`，`M1_MU.json`
- 第 2 步：`M1_SMOKE.md`
- 第 3 步通过后：`M1_WINDOWS.csv`
- 第 4 步通过后：`M1_SUMMARY.csv`
- 第 5 步：`M1_ESTIMATE.csv`
- 结束时：`M1_STATUS.json`

冒烟失败时，后四个测量文件不存在。第 4 步不一致时，不存在 `M1_SUMMARY.csv` 和 `M1_ESTIMATE.csv`。
