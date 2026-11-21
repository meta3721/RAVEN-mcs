# 自主单种子G/W预定筛查

**PAIRING_INCOMPLETE / WAITING_USER_REVIEW**。四臂完成1/4；完成臂：[{"arm": "of", "strategy": "OF-v1", "G": 0.9452180232558112, "W": 0.6015037593984962, "CPU": 496.140625}]。主对照fixed_time_0.5始终不变，fixed2作为完整第二对照保留；G/W均越小越好。

各基线rW/rG/dG/两条路线及保护条件、自主799格动作差异、Q/版本与关闭序列变化：null。不同池的自主动作是同全局时刻比较；OF原记录同状态影子单列，不作为自主收益替代。

主对照预定筛查：null。第二对照同时支配OF：UNKNOWN；主路线虽达但第二对照风险：UNKNOWN。不以J择优，不把本种子或800格当独立确认/显著性。

Q停止项判定UNKNOWN：仅κ=0自主臂保留原完整P2-Q；报告双指标及轨迹，不根据结果调κ。可见的单种子Pareto描述改善也不等于泛化或正式因果收益。未运行去L或去P2-Q，不给它们的因果收益主张。

[PILOT_COMPARISON.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/PILOT_COMPARISON.json)。本批只检验诊断先验下冻结配置的控制描述量；无已校准q、生产风险保证、RMSE不退步、充分训练或完整外部方法领先结论。
