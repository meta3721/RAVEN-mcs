# 初次续行的根发布中断

状态：ENGINEERING_SESSION_INTERRUPTED；后续独立S2已修复设施并完成T100，此处不覆盖旧失败。

阻塞步骤为外部root预算发布。预期逐序新鲜根样本继续支持预算准入；实测在原1.07真实资产恢复一致后、已确认1.1—1.3网格期间，发布PermissionError导致Job清理，尚未产生任何新complete model/private点。确切抛出调用位置未在S1异常中保留，根路径/原pending文件和进程日志保留，底层锁定或权限原因UNKNOWN；不改写成科学性能失败。

该会话真实执行墙钟30.400251秒；CPU完整PID审计缺失UNKNOWN，按单Job墙钟上界加driver保守33.421875计入，原批连续账311.046875/3600。21条成功训练操作记录对应额外物理SGD21；最多还有一个未记录训练操作，物理上界22。最后确认网格1.3仅为日志证据，绝不是新可恢复模型。

最后真正完整点仍为[original1.07 complete pair](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/trajectory/stopped_0011_0206.complete.json)，next_grid_tick11、SGD32、modelversion1，producer next_clock1/next_client3、原RNG和pending通知均可读。之后的SGD/队列没有完整私有状态，禁止从日志拼模型或补出完成点；允许恢复范围仅原1.07完整点。

仍有效成果是原身份/数据/源码/模型与producer恢复一致性、费用保守证据及部分决策描述。最小修复限定根发布共享冲突与反馈路径，保持源闭包、科学和服务语义；原预算不增加。S2临时路径首发布失败也保存2.171875保守费用（没有训练准入），再经工作区独立反馈目录、唯一临时文件、有界替换与原时间戳检查通过后执行成功。新会话为普通设施故障恢复，未为匹配计时重放或择优结果。

证据：[INTERRUPTION_BOUND.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/INTERRUPTION_BOUND.json)、[charge_resume_s1.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/charge_resume_s1.json)、[resume_s1.log](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/resume_s1.log)、原DECISION_METRICS与COST_RECORDS均独立保留。本会话三行部分决策不并入最终1000格；完整新状态与连续账见S2报告。
