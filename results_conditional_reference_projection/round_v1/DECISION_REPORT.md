# DECISION_REPORT

三种子筛选是 NO_GO_PREDICTIVE_SCREEN。分支 B 是 NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT。
全局 B* 按三种子平均 validation RMSE 选择，是 TwoStage-Hajek。联邦成本对手是 TwoStage-Hajek。
P 相对 B* 的平均 RMSE 相对差是 0.0008，有利种子 0/3，WorstGroup 相对差是 0.0010。
P 相对 Uniform 的平均 RMSE 相对差是 -0.0153，group pp 是 -6.0963。
P 相对 F 的平均 RMSE 相对差是 -0.0032，group pp 是 0.6892，client-stratum pp 是 -1.0248，CPU 比是 0.9778，wall 比是 0.9792。
简化条件的汇总是 PARTIAL_TRADEOFF_EVIDENCE。它没有部署合同，不能写成替代通过。
FedAU 和 ObsUse 没有本协议的合法逐单元 validation 资产，结论不包括这两条。
首批历史成本有 UNKNOWN 项，见 COST_LEDGER.json。新轨迹都使用了服务器参数克隆，绝对分数不能直接写成原论文方法的新收益。
比较使用三种子均值之比，不做显著性或非劣证明。相对差是 P 的均值除以对手均值再减 1，正数表示 P 更高。结构百分点是 50 乘以两者 L1 之差，正数表示 P 的错配更大。

预测筛没有通过。本路线不再追加种子、目标或新候选。
