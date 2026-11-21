# SCORING_ALIGNMENT

真实 validation 单元已按 unit_id 对齐。四个组都有样本，没有缺组再归一化。
两个廉价基线的 validation 预测与数据集目标的最大差不超过 1e-6。公式差分别是 Delivered-SpatialMean 0.0, Delivered-CellBlockMean 0.0。
FedAU 和 ObsUse 仍只有历史汇总值，状态 MISSING，不阻断五臂，也不能写成已经被超过。
旧 JO 汇总没有逐单元预测，本轮终点不用那张表填入。
