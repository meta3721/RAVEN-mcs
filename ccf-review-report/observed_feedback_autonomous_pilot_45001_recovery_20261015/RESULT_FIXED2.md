# fixed_time_2 — FULL_T100_VERIFIED

Traffic/45001；q=.5仅diagnostic_prior，未校准。T100/1000格/4300注册，真实模型与private终点可读；seed、数据、初值、概率策略身份与冻结一致。逻辑SGD3354；物理区间3450—3450，上界偏移仅计失联实际未知工作，不当测量值。模型版本60，关闭60（空0），消费1492唯一key。

G800=0.843082579，回退0；W(close_time>20全部正时长关闭含空/终点)=2.000000000，分母40；辅助非空post20 J=0.949307946。常规799格，自由761；原因{"MIN_CLIENTS": 38, "FIXED_TIME_WAIT": 722, "FIXED_TIME_TRIGGER": 39}。不替换原分母。

R13354/R0946/E0817/R1E12717；未成熟0，物理pending R1有限终点删失16。终态原因{"consumed": 1492, "superseded": 407, "compute_failure": 451, "network_failure": 211, "no_observations": 946, "expired": 785, "horizon_unconsumed": 8}。消费等待平均/最大1.519001/3.930000。行政消费标签和物理服务终点分别处理，未给恢复前缀补0。

完整P260、缓存0，权重残差4.441e-16、实际omega绑定误差0.000e+00。最大实际完整在线请求0.348125CPU秒；fixed05包含原750格既有实际记录，但失联后缀完整请求终审仍未知，不能声称历史丢失部分已验证。

该路径已审计实际根费用526.906250、另保守0.000000；所列会话墙钟2975.833990。恢复与新增臂采用持久root样本/检查点SESSION及独立外层PID终审；逐进程CPU是审计包含项，不再相加。终点模型/private字节[229256810, 5713223]，保存最大完整根上界9.754375，最终动态留额36.695145。

同状态影子no-Q差异None、fixed.5None、fixed2None。None为固定臂没有为影子额外求解P2；不同自主池的动作比较见主报告。

原始参数与数值证据：[VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/VALIDATION_AND_SUMMARY.json)、[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/trajectory/tick1000.complete.json)。旧OF直接复用已验终点，没有重跑；新概率风险和预测性能RESULTS_NOT_REVALIDATED。
