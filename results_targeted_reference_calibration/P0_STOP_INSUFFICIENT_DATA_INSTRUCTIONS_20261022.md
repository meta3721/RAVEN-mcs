# 停止指令：公开参考校准 P0 面板不足

日期：2026-10-22。依据是 `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_20261022_210125\EXPERIMENT_REPORT.md`。

本文件不授权新的筛选、P1、模型拟合、训练、换窗口、换区域、改支持门槛或改 POC 规则。

## 1. 冻结结论

`p0_same_value_screen_20261022_210125` 的状态是 `INSUFFICIENT_DATA`。面板已写出。P1 是 `NOT_RUN`。没有 RMSE、ContrastMAE、5% 收益或 2% 组差。

复核与上一份指令一致：同值多键 16 行，零键只有源行 8402。有效规则没有把两个不同浓度合成一个标签。被排除的设备日是 422 个，其中 421 个是同一设备日有两个不同参考值，1 个是 IA3 在 2019-01-27 的 FRM（源行 8402 与 8465）。

筛选结果：

| 条件 | 实测 | 门槛 |
| --- | ---: | ---: |
| 固定站点 | 8 | 10 |
| West | 6 | 4 |
| North | 2 | 4 |
| V 可评价日 | 0 | 20 |
| T 可评价日 | 0 | 40 |
| 从 2019-05-04 起的七天块 | 0 | 7 |

进入面板的只有 West 的 CA10、CA2、CA5、CA4、CA3、CA17，以及 North 的 WA1、WA3。当日门槛是 West 至少 5 站、North 至少 3 站。North 只有 2 站，任何一天都不可能可评价，所以 V 和 T 的可评价日都是 0。这不是把缺失写成 0。

这个结果只说明当前冻结面板不够做组差评价。它不说明校准有效，也不说明校准无效。

## 2. 执行

不要改下列目录里的状态、报告或表：

- `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_p1_20261022_161223`
- `C:\Users\szr\Desktop\record\1\results_targeted_reference_calibration\p0_identity_repair_20261022_175353`
- `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_redo_20261022_193538`
- `C:\Cursor\raven.mcs\results_targeted_reference_calibration\p0_same_value_screen_20261022_210125`

不要新建运行目录。不要读取 A/T 参考数值，不要实现或运行 M0–M4。不要为了让 North 达到 4 站或让可评价日达到 20/40 而降低门槛、更换 2019-01-26—2019-06-28、更换 West/North、删除当日 75% 规则、改选代表设备，或按最小 POC、第一条、平均值、与传感器的距离挑选参考。

继承 CPU 保持 12.765625 + 8.734375 秒。本指令的计算消耗记 0。最低可用内存曾到 1,033,367,552 字节，但墙钟只有 22 秒，没有连续 30 秒低于 1.5 GiB，不改写成 `RESOURCE_PAUSE`。

## 3. 若以后要另开一轮

必须先有单独批准的新目标定义，并且新建目录。当前这轮不能改成通过。可被单独提出、但本文件不批准的例子只有：

1. 停止这条公开数据上的组差校准路径。
2. 把目标从 West 对 North 的组差改成已经进入面板的固定站点上的站点校准。这不再是原主要终点。
3. 在打开标签之前，为每个站点预注册一个 POC，规则只能使用覆盖日数和 POC 标识，不能使用浓度或误差。这是新的参考定义，不是本轮筛选的续跑。

以上三项都不要在本指令下执行。
