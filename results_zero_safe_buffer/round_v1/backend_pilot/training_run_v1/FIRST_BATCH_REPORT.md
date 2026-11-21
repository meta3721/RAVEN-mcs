# FIRST_BATCH_REPORT

日期：2026-10-19。种子 33001。状态：**FIRST_BATCH_COMPLETE** / **TRAINING_VERIFIED**。

五臂顺序为 I-Proj-ZS、F1-Proj-ZS、F2-Proj-ZS、TwoStage-Hájek、FedAvg-Window。每臂 100 个 close，评分点是完成 20、30、…、100 个 close 之后的验证集。每臂 9 个点，合计 45 个点。每个臂目录下有 100 个 `close_XXX.pkl` 和 9 个科学评分模型。

九点平均 RMSE_mu（L）：

| 臂 | L | 第 100 close 的 RMSE_mu | 九点 WorstGroup 均值 | 服务器步数 |
| --- | ---: | ---: | ---: | ---: |
| I-Proj-ZS | 1.994358 | 1.616555 | 2.374640 | 100 |
| F1-Proj-ZS | 2.028126 | 1.814550 | 2.420551 | 50 |
| F2-Proj-ZS | 1.998193 | 1.855121 | 2.386935 | 33 |
| TwoStage-Hájek | 2.002018 | 1.615843 | 2.383037 | 100 |
| FedAvg-Window | 2.011914 | 1.636827 | 2.394708 | 100 |

这只是一个种子。F* 和 N* 要等三个种子都完成后再定。这一种子上 F1、F2 的 L 都高于 I，没有预测增益。

首次真实更新的公式误差是 0，见 `REAL_UPDATE_CHECKS.json`。F1 与 F2 在窗口 0 发生 HOLD，当时版本和优化器步数都是 0。I 在这一种子上每个窗口都有发布，没有 HOLD。

恢复：F1 和 F2 的进程内两窗口重放通过。F1 的同一断点 `close_000.pkl` 再由新进程重放窗口 1 和 2，`RESTORE_CHECK.json` 为 PASS，最大绝对误差 0，侧向评分差 0，不计入九点均值。规范轨迹仍是原臂目录里的那一条。

缓存计数与先前静态结果一致：参考零质量排除 451，`zero_replaces_positive` 为 0。F1 正质量提交 1030，F2 为 873。生命周期在 `LIFECYCLE_COUNTS.csv`。
