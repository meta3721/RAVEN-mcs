# 本轮范围与冻结

授权文件：C:/Users/szr/Desktop/record/1/ccfa-review-reports/OF-v1-small-scope-validation-instructions.md。使用 ccf-experiment-designer。最终状态：L_MECHANISM_UTILITY_NOT_ESTABLISHED；A/B通过，C完整有效=True，WAITING_USER_REVIEW。

研究问题：动态最近释放参考相对固定暖启动参考是否改变决策，以及自主执行后的 G/W 是否支持历史参考的实际价值。唯一新增策略 GAP20-fixed-reference，Traffic，开发种子45001；这是具名诊断对照，不是OF新版。q=.5，diagnostic_prior，calibration_only，q-fit=0，GPU=0。

c_ref=0.9168365859958755，来自 C:\Cursor\raven.mcs\results_observed_feedback_autonomous_pilot_45001_recovery_20261015\noqstop\CLOSURES.json 中 t=20.0 的真实非空释放：ell=0.9069767441860466，保存时age=0.4929920904914447；固定参考不随时间老化。冻结时间 2026-10-18T11:05:14.147624+00:00，在流式检查t>20动作之前写入FREEZE.json，未搜索参考或阈值。

唯一科学改变：OF-no-Q-stop的动态c_minus替换为c_ref；额外停止项kappa仍为0。底层完整P2的Q、债务/方差/滞后更新、约束和真实训练不变。公式 B=c_ref-(ell+.02age)+.20clip(elapsed/4,0,1)，阈值.0200001。终点→暖启动fixed1→deadline4→K<3 WAIT→自由规则优先级不变。

预算：完整根新增CPU1000秒、活动墙钟5400秒、实际新增局部SGD不超过5000、最多一臂。采用既有Windows Job根计量、RecoveryPublisher和RecoveryAccount；单worker、计算线程1和单CPU亲和性；实际优先级核验及修复见RESOURCE_AND_BUDGET.md。前置非计量整理保守占用30CPU秒，实际值UNKNOWN，计入A及总预算，不写成实测。A建议60、B120、C700、保存交付预留120秒，均包含在总上限内。活动起点保守取2026-10-18T18:58:19.5477347+08:00，目录后缀为本次实际建档时间。

A门槛≥40/799格差异：实际129格，通过。C须完整有效且H=旧no-Q-stop相对S=新GAP满足(rG_H≥1%且W_H≤1.05W_S)或(rW_H≥5%且G_H-G_S≤.01)。原OF对fixed.5的2%/5%屏障保持独立不变。所有状态等待用户复核，不进入完整P3、不修改论文、不拟合q、不扩种子。

合法C分叉只允许旧noqstop/trajectory/tick0200.complete.json；B使用tick0350仅作SGD0接口验证，不作为C起点。旧注册字段与随机流保留；新消息采用独立策略、概率适用身份及run时钟。
