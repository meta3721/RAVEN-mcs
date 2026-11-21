# fixed_time_0.5 — FULL_T100_VERIFIED

Traffic/45001；q=.5仅diagnostic_prior，未校准。T100/1000格/4300注册，真实模型与private终点可读；seed、数据、初值、概率策略身份与冻结一致。逻辑SGD3354；物理区间3354—4429，上界偏移仅计失联实际未知工作，不当测量值。模型版本178，关闭178（空0），消费1455唯一key。

G800=0.958859012，回退0；W(close_time>20全部正时长关闭含空/终点)=0.506329114，分母158；辅助非空post20 J=0.997308636。常规799格，自由499；原因{"MIN_CLIENTS": 300, "FIXED_TIME_WAIT": 342, "FIXED_TIME_TRIGGER": 157}。不替换原分母。

R13354/R0946/E0817/R1E12717；未成熟0，物理pending R1有限终点删失16。终态原因{"consumed": 1455, "superseded": 50, "compute_failure": 373, "network_failure": 163, "no_observations": 946, "expired": 1305, "horizon_unconsumed": 8}。消费等待平均/最大1.087533/2.700000。行政消费标签和物理服务终点分别处理，未给恢复前缀补0。

完整P2178、缓存0，权重残差3.331e-16、实际omega绑定误差0.000e+00。最大实际完整在线请求0.129375CPU秒；fixed05包含原750格既有实际记录，但失联后缀完整请求终审仍未知，不能声称历史丢失部分已验证。

该路径已审计实际根费用168.265625、另保守0.000000；所列会话墙钟750.707479。另保留失联调用2388保守占用，旧实际CPU/退出墙钟UNKNOWN，不加入实测算法耗时。恢复与新增臂采用持久root样本/检查点SESSION及独立外层PID终审；逐进程CPU是审计包含项，不再相加。终点模型/private字节[165745680, 5706787]，保存最大完整根上界7.926250，最终动态留额128.668768。

同状态影子no-Q差异None、fixed.5None、fixed2None。None为固定臂没有为影子额外求解P2；不同自主池的动作比较见主报告。

原始参数与数值证据：[VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/VALIDATION_AND_SUMMARY.json)、[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/trajectory/tick1000.complete.json)。旧OF直接复用已验终点，没有重跑；新概率风险和预测性能RESULTS_NOT_REVALIDATED。
