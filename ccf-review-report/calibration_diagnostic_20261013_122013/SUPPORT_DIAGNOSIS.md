# D2 冻结历史与后备原因

状态：诊断完成；未改变控制器、服务核、R处理、常数或后备规则。全部算术来自首条既有记录，服务支持只用本run `t≤20` 冻结资料。没有调用规划器、抽取新场景或从最终状态逆造决策快照。

## 1000条正常决策

[DECISIONS.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/DECISIONS.csv) 保存逐条阶段、reason、动作、CPU/墙钟及P2次数；[DECISION_REASONS.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/DECISION_REASONS.csv) 保留完整原reason。原decision对象没有time，表中时间明确标为从固定0.1网格和连续决策序号推得，依据已验证的运行/恢复循环，未冒充原生日志时间戳。

|正常决策类型|全程条数|解释|
|---|---:|---|
|共同暖启动|200|t=0.1…20.0|
|支持后备|792|风险不足382；相容标记不足410|
|条件消息束|7|不是7次优于基线|
|实验终点|1|t=100|
|硬截止首原因|0|实际首原因中没有此项|
|CPU超时首原因|0|正常1000条中没有；另有已保存的T20.1工程失败|

全程792/1000=79.2%；暖启动后792/800=99.0%，800分母包含7条消息束及1条终点。WAIT940、CLOSE60。失败调用、只读修复核验均不混入1000条正常决策分母，原预算仍包含其成本。

## 客户端×公开资源格

暖启动共有860个注册机会，其中R=0为179、R=1为681。服务记录为503完成、155通知失败、23右删失；没有用20之后的完成回填冻结核。129个机会格中125格有相容完成标记。

|client/device/network|机会|R=0|R=1|完成|通知失败|右删失|
|---|---:|---:|---:|---:|---:|---:|
|56602/tier-0/net-tier-0|5|1|4|0|4|0|
|56975/tier-2/net-tier-2|3|2|1|0|1|0|
|57051/tier-2/net-tier-2|1|1|0|0|0|0|
|57106/tier-2/net-tier-2|1|1|0|0|0|0|

四格确实样本缺失，并非client、device、network拼接错误。860条机会逐一与原注册key、client、时间及资源字段匹配，全部一致；时间均属于同一run命名空间且≤20。两格有正观测尝试但全部失败，另两格根本没有正观测尝试。

例如`006::57051`在6.26注册，为tier-2/net-tier-2，R=0；该机会仍进入历史时钟，未来查询却要求同client×资源的正质量完成标记。`007::56602`在7.18注册，7.732489收到失败通知，与其余三个R=1失败共同解释该格缺标记。详见 [源记录到查询键实例](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/MISSING_MARK_SOURCE_EXAMPLES.json)。

全部129格见 [CLIENT_RESOURCE_SUPPORT.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/CLIENT_RESOURCE_SUPPORT.csv)；681条截止内服务暴露见 [FROZEN_SERVICE_EXPOSURES.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/FROZEN_SERVICE_EXPOSURES.csv)。23条删失只贡献其合法暴露，不记为失败。

## 服务时长尾部与模型版本age

从上述截止内暴露独立重算全部51个风险格，风险/完成/失败三项与冻结参数逐格相同；43格risk≥5，8格不足。

|资源层|首次不足格|服务时长区间|risk|
|---|---:|---|---:|
|tier-0|22|(2.1,2.2]|2|
|tier-1|15|(1.4,1.5]|4|
|tier-2|9|(0.8,0.9]|4|

实际首原因分别为tier-0格22共117次、tier-1格15共171次及格16共3次、tier-2格9共91次，合计382。条件残余服务从当前已等待时长的下一格查询，故能直接遇到格16；没有“先前格失败却继续忽略”的证据。完整表：[SERVICE_RISK_CELLS.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/SERVICE_RISK_CELLS.csv)。这里的age_bin是0.1单位服务时长，**不是模型版本age**。

## 未来R=1语义与异常传播

[采集器](C:/Cursor/raven.mcs/src/raven_mcs/experiments/calibration_first.py:139) 将所有注册加入opportunity_history；[冻结核](C:/Cursor/raven.mcs/src/raven_mcs/experiments/calibration_first.py:191) 则排除R=0后拟合服务风险。随后 [sample_scenarios](C:/Cursor/raven.mcs/src/raven_mcs/control/predictor.py:178) 重采样全部历史注册批次，对每个展开机会先选一个相同client×资源的完成标记，再从条件R=1的服务核抽结果。没有合法的R发生概率或R=0抽样环节。

因此实现输入是“全部注册机会”，服务/质量解释却是“正观测尝试”。并非每个未来机会一定最终完成，服务核仍能抽失败或未决；错误是每个机会都被当作需要正质量更新的R=1候选。历史179个R=0没有在这层保持其语义。不能用实际未来995条R=0的真值反向修复这次规划。原候选规格未定义这一R桥接，本轮将它记为定义缺项及实现接口不一致，不能默默将旧预测重解释为仅含R=1机会。

[样本生成](C:/Cursor/raven.mcs/src/raven_mcs/control/predictor.py:156) 对单一在途项、未来机会或任何一个场景抛出UnsupportedPrediction；[plan](C:/Cursor/raven.mcs/src/raven_mcs/control/planner.py:173) 在外层捕获后整项决策退回fixed_time_2。此前已经可支持的场景/计划不会继续比较。这是候选规定的全局后备规则，造成局部缺口传播，不能当成未实现的隐藏分支。

410条缺标记首原因可由源码错误串区分：145条来自未来机会查询，265条来自当前在途查询。风险不足382条不能仅凭错误串继续区分当前/未来来源；原日志没有记录该细项。缺标记和风险不足的真实重叠数量也不能由首原因相加推得。

真实生命周期在注册、时间推进和释放后均执行 [expire](C:/Cursor/raven.mcs/src/raven_mcs/control/lifecycle.py:212)，当前超龄在途会移除。最早完整的T20.1失败因果快照有14个在途项，0个超龄、0个缺标记、0个下一服务格立即不支持；它不排除该决策后续未来机会或更远尾部失败。只读查询详见 [EARLIEST_CAUSAL_SNAPSHOT_SUPPORT.csv](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/EARLIEST_CAUSAL_SNAPSHOT_SUPPORT.csv)。

另一方面，503个历史完成标记中60个注册时age>5。预测器先对抽到的这些未来标记查询服务支持，之后进入预测状态才应用过期规则；因此明知不能消费的未来标记仍可能触发全局支持后备。候选已有过期规则，但没有明确规定此时可跳过哪一层预测；改变检查顺序及动作需方法/实现一致性审批，本轮没有删除这些样本。表：[FROZEN_OVERSIZED_AGE_MARKS.json](C:/Cursor/raven.mcs/results_calibration_diagnostic_20261013_122013/FROZEN_OVERSIZED_AGE_MARKS.json)。

## 已知与未知

以上数据及源码足够定位主要瓶颈，因此规划器复现次数为0（授权上限12，未用）。没有每次决策的完整快照/逐查询轨迹，不能给出全1000条的重叠原因或“去掉某问题后后备率”的反事实。若将来批准采集，最小新增记录应是decision时间/快照引用、首个unsupported的current/future类别、注册/机会key、场景号、查询格/risk/mark数及注册R语义；这些用于定位原调用，不另生成场景或使用未来真值。

每次运行使用自身warmup20后冻结。增加其他运行的q训练记录不会补当前运行的这四格标记或尾部风险。当前99%后备说明首条上机制极少被执行，不能据此证明所有未运行种子或新q策略都必然失败；也不能由7次动作推导收益。
