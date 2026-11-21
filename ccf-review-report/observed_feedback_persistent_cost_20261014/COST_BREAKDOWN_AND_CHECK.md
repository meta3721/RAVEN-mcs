# 同输入常驻费用核验

结论：**PERSISTENT_REQUEST_COST_CHECK_PASSED**。仅支持重提一条限定诊断采集申请；旧P3完整冷失败保持FAIL，不代表生产概率、真实训练/激活、控制收益或预测收益通过。

## 实测三段

一次新常驻数学worker，同一PID16604；READY前实际solver调用0、numeric cache0。原输入字节/hash不变，172维mu、K43和全部原目标/约束保持。没有预先权重或参考求解。

- INITIALIZATION：完整根上界**3.051250 CPU秒≤6**，实际根样本段3.031250秒（含launcher bootstrap .093750），墙钟3.578576秒。worker到READY构造的本地CPU2.640625；固定模块导入1.765625秒、静态输入解析小于CPU计时分辨率、fixture资源/条件历史构造.796875秒。构造内stage1 .046875、43次历史重建.750000为重叠子段，不能再次相加；它是旧人工输入溯源构造费用，不是所有在线判断必须构造历史。真实模型/数据/优化器没有加载。
- A：READY后第一次完整在线判断，根上界**.270000 CPU秒≤2**、根差.250000秒，墙钟.310232秒；真实worker含响应序列化/flush的本地CPU.250000秒，Controller .140625秒。原完整P2/CLARABEL调用1，原求解函数实测.031250 CPU秒、墙钟.026149秒；P2/cache=1/0。导入模块在本轮明确的初始化段计费，求解未提前。
- B：同worker、同输入/时钟再次判断，根上界**.176250 CPU秒≤2**、根差.156250秒，墙钟.200331秒；真实worker含响应的本地CPU.140625秒、Controller .046875秒；P2/cache=0/1，无新原求解函数调用。新BoundReleasePreview对象复用同一numeric，当前fingerprint/dependency_hash正确；没有缓存动作。时钟未改变，不能把本项称跨时钟或真实激活新证据。

必要管道响应A161521/B161479字节（含换行），保留真实alpha、M、omega、ell/age、keys、配置依赖/当前指纹和决定/B各项。worker仍保留完整原BoundReleasePreview；没有删去提交所需质量矩阵。完整solver日志/beta/masses及全部目标在结束阶段输出一次，避免旧asdict及日志M重复复制，未将实际求解移出online。

整个A/B调用含关闭/退出Job3.500000 +启动器/外层驱动.281250 =**3.781250 CPU秒**，墙钟4.666787秒。初始化+A+B实际样本段合计3.437500；余下**.343750 CPU秒**包括样本桥/段间间隙、完整审计、父数值核对、进程关闭/退出及最终monitor，全部纳入根账。worker完整审计dump另测.031250秒、关闭/输出本地墙钟.253005秒；这些是余下账的组成，不另加总额。+.02验收上界不是可直接累加的实际消费账。

## 数值及行为一致

原RavenAggregator/CLARABEL optimal，1次真实数值求解。实际alpha约束残差1.1102230246251565e−16≤1e−7；原候选约束残差约7.99e−15。数值有限；alpha/omega/ell/age与旧结果最大绝对差分别0/0/0/0，既有1e−7、rtol0条件通过。实际ell=.05377794911333895、age=.05963816016280501。

完整实际目标debt=−.000017347725520431715、group=.000055738161400763896、reference=.00212000360393372、variance=.000022490652305817034、staleness=.0059638160162805015；没有纯d替代、降维、改cap/ESS或求解容差。动作仍CLOSE/B=.2682851023618531，是原数学输入的当前判断，未应用更新；model_version1/t20.5/o20、state fingerprint保持，consumed/closures/SGD均0。

## 计量字段补正与限制

审计发现新测试父进程的Popen句柄对应venv启动器，不是实际解释器；原记录worker_process_CPU=0的API字段不能解释为真实worker费用。根Job从启动前覆盖全部后代，真实worker PID16604在保留PID审计中CPU3.281250秒、root_job_member=true，因此整账没有漏费。

MEASUREMENT_ADDENDUM用已保存的真实worker process_time（含响应序列化）与父CPU及互斥外层monitor重新取max保守下界，初始化/A/B上界仍分别3.051250/.270000/.176250，未降低原上界，也未把PID再加入总账。实际PID逐段直接API差没有采到，不能编造；真实worker自报区间及最终保留PID总量分别披露。没有因此重新运行A/B，执行源码/原记录与补正独立保存。下一真实采集接线应直接绑定READY实际PID或等价的明确worker区间，自报与根账交叉核验，不能再把启动器句柄当worker。

原冷请求2.551250计的是旧冷边界；本次是事前批准的一次初始化+常驻请求协议，不能说旧超限消失或全归因求解器。这里只是两个确定性成本点，不能外推真实增长状态的延迟分布。动态注册/通知/p更新、真实SGD/模型提交、私有队列增长与恢复成本均未执行，必须在后续根账独立计量。

## 保存与归属

1657个保护文件核验无变化，含旧报告/失败/STOP及生产源码；原输入逐字节相同，运行前协议/脚本hash匹配。旧q与旧终态未复用，没有诊断采集入口、真实producer、训练或回放。仅新增独立常驻测试worker、父请求通道、预算及审计脚本；既有控制器/聚合器源码未修改。新真实采集入口还未实施。

证据：[结果](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/PERSISTENT_COST_RESULT.json)、[完整原数值审计](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/FULL_WORKER_AUDIT.json)、[根Job账](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/persistent_A_B.meter.json)、[剩余根费用](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/FINALIZATION_ROOT_COST.json)、[字段补正](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/MEASUREMENT_ADDENDUM.json)、[历史保留](C:/Cursor/raven.mcs/results_observed_feedback_persistent_cost_20261014/FINAL_DELIVERY_CHECK.json)。
