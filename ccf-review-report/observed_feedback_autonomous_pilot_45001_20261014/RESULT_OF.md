# OF-v1独立实际轨迹

状态FULL_T100_VERIFIED；seed45001，q diagnostic_prior=.5/未校准。T100/网格1000/注册4300，逻辑SGD3354，物理范围3354—3354，模型版本153、关闭153（空0）、消费1539唯一key。

G800=0.945218023，回退0格；W(close_time>20全部关闭含空/正时长终点)=0.601503759，分母133；辅助非空post20 J=0.989879799。常规799格、自由582格，原因{"MIN_CLIENTS": 217, "FEEDBACK_WAIT": 450, "FEEDBACK_TRIGGER": 132}，不把自由分母替换799。

R13354/R0946/E0817/R1E12717；消费平均/最大等待1.100156/2.670000。未成熟0，物理pending R1右删失16；原因{"consumed": 1539, "superseded": 74, "compute_failure": 388, "network_failure": 174, "no_observations": 946, "expired": 1172, "horizon_unconsumed": 7}。终点行政消费0与物理未结束分开，不继承前缀删失。

P2501/cache102；实际权重可行残差3.331e-16、omega绑定0.000e+00，最大实际完整请求0.160625CPU秒。完整在线根分类23.390625，不是独立solver-only/cache-only费用。该臂计费496.140625：已审计实测493.984375=tree392.546875+driver101.437500，保守2.156250，墙钟2689.562009。全部调用均有PID审计：False；保守失败调用的实际缺口仍UNKNOWN。

终点model/private字节[174821982, 5678396]、保存最大根上界10.004375、留额136.887325。原始配置、所有标签/权重/snapshot/根费用/完整状态与指针：[of_resume1/VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/VALIDATION_AND_SUMMARY.json)、[of_resume1/trajectory/tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/trajectory/tick1000.complete.json)。

同状态影子no-Q差异0、fixed.5差异193、fixed2差异132；None表示该fixed臂未为无必要影子额外求解P2。自主同全局时刻动作差异另见比较报告。未证明预测任务不退步、RMSE或生产概率。
