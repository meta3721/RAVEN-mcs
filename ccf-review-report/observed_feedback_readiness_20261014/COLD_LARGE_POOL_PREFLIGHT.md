# 唯一K43冷请求：数值通过，完整费用失败

2026-10-14，运行1次；GPU/SGD/q拟合/真实或随机轨迹/控制回放均0。结果：**P3_FAILED_COST**，暂停首条采集申请。完整根上界2.551250 CPU秒 >2，没有预热重试或降低规模。

运行前冻结results_observed_feedback_readiness_20261014/FROZEN_INPUT.json；SHA256=c880a4361ea0ec8fa3fc65b30cd9932347181c8591d39c6f003e829d5c695e5b。实际mu为既有公开冻结172维目标，仅提取历史文件state.mu；不恢复旧state、不使用旧标签或队列。数学fixture目录43个独立人工client、已到达合法注册/下载版本/质量，不能称为Traffic实际可达状态。

当前t20.5/o20/v1，43列均不同、年龄0或1、q=.5且role=isolated_test_input。每列实际freeze_stage1使用合法正的lagged opportunity、p=.5、配置Design=on与原重构/裁剪；不是直接拿原机会向量当实际组成。V非恒等、Q非零；Q和L来自事前声明的可构造条件历史（一轮3个相同列的精确单点暖启动释放），本批未执行历史回放或P2预热。该输入仅用于当前数学计算，不给后端伪造真实训练或消费轨迹。

原可行域Σalpha=1、0≤alpha≤.5、Σalpha²≤1/3。uniform点Σalpha²=1/43，且±.001(e0−e1)仍可行，存在真实自由度；未使用K3单点路径。cache_solves=1、hits=0，首次原数值P2经RavenAggregator调用CVXPY/CLARABEL，status=optimal、无fallback/repair。COLD_REQUEST_STARTED显示数值库cvxpy/scipy/clarabel在请求初始化前未加载。没有新增简化求解器或纯几何d。

实际权重min=.013546946319428311、max=.033436359305625905，ell=.05377794911333895、age=.05963816016280501。原候选约束残差7.993605777301127e−15；归一化实际alpha残差1.1102230246251565e−16，≤1e−7。完整alpha/beta/masses/M/omega、staleness/V/Q及原约束均保存在COLD_NUMERIC_RESULT.json和输入，全部有限。

实际目标各项：debt=−.000017347725520431715；group=.000055738161400763896；reference=.00212000360393372；variance=.000022490652305817034；staleness=.0059638160162805015；总实际目标=.00814470070840037。没有删除参考、方差或陈旧性项。数学B=.2682851023618531，quality=.24328510163689326/debt=7.249598461407181e−10/patience=.025，局部控制器返回CLOSE；超根费用的返回不被认定为获准实际控制决定，未提交模型。

费用边界事前固定：FIRST根基线0，包含新worker启动/导入/初始化、首次完整当前判断、原求解器、完整数值序列化及父监视。launcher bootstrap=.093750 CPU秒；结束后新根样本tree=2.375000、driver=.062500、command_used=2.437500；加bootstrap与.02保守量并取PID下界的max，得2.551250。worker完整请求CPU=2.343750，墙钟3.139084秒。局部Controller（含必要数值导入、原P2调用及判断）=1.187500 CPU秒；它不能替代完整费用。没有独立测出原求解器纯调用CPU；其完整调用包含在局部和根时间内，纯求解/导入/初始化的细分UNKNOWN，不能据此确定单一瓶颈。

整个冷调用含退出互斥账：Job=2.515625、driver=.156250、合计2.671875 CPU秒，墙钟3.398232秒、根审计通过。进程成功退出0表示证据保存成功，不是P3通过；判定以COLD_REQUEST_COST.status=FAIL为准。固定45 CPU秒仅为整次检查安全帽，root admission ceiling30是原请求费用的探测准入估计，均不是把2秒门槛提高。

证据：[固定输入](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FROZEN_INPUT.json)、[实际数值](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/COLD_NUMERIC_RESULT.json)、[完整请求账](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/COLD_REQUEST_COST.json)、[根完整账](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/cold_K43_once.meter.json)、[日志](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/cold_K43_once.log)。这是一条确定性检查，不证明运行分布或长期成本。
