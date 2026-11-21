# 原44001分支失败复核

A：PASS。旧数据、六份报告及其失败身份保留；本批没有续采。

原CSV共有989行。主集合20<t<100的已观测前缀为20.1—98.9，共789点，时间网格完整且无重复，所有快照路径存在。总动作差异、区间激活、区间机制差异均为0；分类为427个UNKNOWN_FIXED_TIME_2、346个CPU_TIMEOUT、16个RULE_FORCED。完整D为799点，尚缺10点。保留已有789点时，最大差异为10/799=1.251564%，小于原5%筛查线；至少需要ceil(799×0.05)=40个差异点。因此，不建议补齐原分支用于挽救这一筛查项。

这是必要条件的确定性上界，既不是统计显著性检验，也不是所有种子或整个研究方向的失败证明。T100模型及I(100)标签仍未完成；不能将前缀当完整采集或计算正式校准通过率。从t80恢复会替换已观测尾部，应另立分支，不能称为补齐原98.9状态，更不能覆盖原失败。

科学障碍分开处理：

- 粗界：可跟踪计划×场景记录中10183/10496=97.0179%的k=0，属于该记录层，不是97.02%的决策失败率。早期未知让独立全后缀绝对分数包络缺乏动作区分；仅调整名称、q数值或删除client不能解决支持缺口。
- 计算：346/789=43.8530%为超时后备。CSV中的P2/cache为空，旧Decision的默认0不能解释成未求解。未完成区间也不能用于证明这些点本来无区分能力。各开销的细分因果尚未计量；C失败后没有启动D的成本拆分。
- 调度与保存：旧根进程费用已包含外层监视，但旧内部保存时机未以根剩余额度统一准入，终止前未提交最新尾部。t80成对文件可恢复，98.9观察日志不是等价恢复点。本批B修复独立设施，未恢复旧轨迹。

[A原始复核证据](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/A_REVIEW.json)。[旧CSV](C:/Cursor/raven.mcs/results_re_interval_development_44001_20261013/DECISION_METRICS.csv)。旧报告和旧结果的逐文件保留核验见[最终核验](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/FINAL_VERIFICATION.json)。本批费用见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)。
