# 唯一45011采集结果

**COMPLETE_T100_ACQUISITION / RESULTS_NOT_REVALIDATED / WAITING_USER_REVIEW**。实际到逻辑时间100.0、1000网格，逻辑SGD3281，物理累计3302—3303（含失败会话丢失工作），GPU0、q-fit0。真实Traffic TRAIN、事前公共目标、CommonNDMF/ClientTrainer与完整P2/显式Design on；服务为已声明受控随机源及实测CPU下界，不是移动设备物理回放。

注册4300，R13281/R01019，E0778，合格R1E12685。所有R1保留实际SGD工作，R0不训练；已完成工作账与逻辑SGD一致。真实关闭147（空0），模型版本147，消费1581key；消费集合与每次非空提交key严格一致，无重复，包括成功提交的零权重key。

常规20<t<100共799格，非强制604格；原因分布：{"MIN_CLIENTS": 195, "FEEDBACK_WAIT": 478, "FEEDBACK_TRIGGER": 126}。两种动作合法子集604格，仅辅助，不替换799分母。OF对no-Q-stop差异1/799（非强制1），对fixed.5差异192/799，对fixed2差异126/799。三影子仅同状态动作、复用原完整P2含Q；没有自主模型/控制轨迹或收益对比。

Q停止项同状态动作差异出现，仅证明本条机制可见。质量/历史L与耐心仍按原分量实际计算，计数：{"positive_debt": 48, "negative_debt": 556, "nonzero_debt": 604, "quality_only_threshold_close": 5, "quality_plus_patience_threshold_close": 127}；质量、κb、耐心、b、历史c_minus和当前c的最小/最大/均值：{"quality": {"minimum": -0.09830635661425902, "maximum": 0.036630708864413886, "mean": -0.02332847120046829}, "debt": {"minimum": -0.0001902617575315059, "maximum": 0.00010077404579981581, "mean": -7.299440354023847e-05}, "patience": {"minimum": 0.0049999999999997165, "maximum": 0.05, "mean": 0.02248344370860928}, "b": {"minimum": -0.0019026175753150587, "maximum": 0.001007740457998158, "mean": -0.0007299440354023852}, "c_minus": {"minimum": 0.8936414921269416, "maximum": 0.9790282033657737, "mean": 0.9514267913497956}, "c": {"minimum": 0.9088248259951611, "maximum": 1.0012248062015505, "mean": 0.9747552625502638}}。历史L影响质量参考，Q参与原P2和停止项；未运行去L或去P2-Q，不把使用L或原P2有Q直接说成因果增益。

no-Q差异占常规799格的0.1252%、非强制604格的0.1656%。唯一差异原始记录：[{"time": 60.2, "window": 83, "action": "WAIT", "reason": "FEEDBACK_WAIT", "B": 0.019911041885110874, "components": {"quality": 0.005007803758847573, "debt": -9.676187373691274e-05, "patience": 0.015000000000000215, "b": -0.0009676187373691273, "c_minus": 0.9740356705462767, "c": 0.9690278667874291}, "shadow": {"no_Q_stop": "CLOSE", "fixed_time_0_5": "WAIT", "fixed_time_2": "WAIT", "forced": false, "no_Q_B": 0.020007803758847788, "P2_recomputed": false, "legal_actions": ["CLOSE", "WAIT"]}, "actual_request_root_upper": 0.035625000000000004}]。稀少差异不能据非零即认定实质机制收益；固定影子比较也不替代自主基线或后续预定5%门槛。

单条描述指标：G800格=0.941141（无最近非空释放回退0格）；W按close_time>20全部关闭、含空和终点正时长窗口平均=0.629921。辅助J按非空post20释放的原ell+.02age+.20duration/4平均=0.986159，与G/W分母不同。注册到消费平均1.104965、最大2.580000，不混为W。

有限消费终点成熟：未成熟0；物理R1服务pending23单独右删失；终止原因{"no_observations": 1019, "consumed": 1581, "superseded": 60, "compute_failure": 422, "network_failure": 174, "expired": 1031, "horizon_unconsumed": 13}。T100行政消费0和物理右删失分开，旧1.07前缀注记未继承为最终标签。q始终诊断先验，不计算正式校准通过。37列归档、全部合法在途key，最大原始F38；合格样本编码缺失0，年龄/设备/网络支持计数在[VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/VALIDATION_AND_SUMMARY.json)，这不是经验校准/正性保证。

本条设备和网络按三个关联层级出现，未提供它们的独立交叉组合支持，也不据计数断言政策迁移正性。

P2新计算520、缓存105；预览状态{"optimal": 542, "full_P2_exact_singleton": 83}，权重可行残差最大4.441e-16，实际输入omega绑定误差0.000e+00，真实请求根最大0.363750秒。[DECISION_METRICS.csv](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/DECISION_METRICS.csv)、[ATTEMPT_LABELS.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/ATTEMPT_LABELS.json)、[PUBLICATION_BRIDGE.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/PUBLICATION_BRIDGE.json)。无检测收益、任务不退步或预测收益结论；性能和主实验未重验。

续行完整在线根分类23.187500 CPU秒，涵盖P2/缓存、控制及真实apply；未单独测量solver-only或cache-only费用。原完整点model/private字节[6301614, 4134777]，第一段[32700682, 4593467]，终点[179560368, 7493086]；检查点私有队列最大24、P最大7、F最大20，这些是检查点取样最大值，不冒充全事件最大值。[DESCRIPTIVE_MECHANISM_AND_COST.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/DESCRIPTIVE_MECHANISM_AND_COST.json)提供操作分类计数/请求差额/保守上界/墙钟；请求差额与上界之和不是新的实际总账。
