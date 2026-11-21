# P3最终费用失败报告

日期：2026-10-14。**PREPARATION_INCOMPLETE / WAITING_USER_REVIEW**。失败阶段仅P3及依赖的P4申请；独立q和接线契约已完成，没有将冷请求失败解释成算法性能失败。

预期：一新worker、首次有自由度完整P2、K43/冻结172维mu，输入合法、数值有限、实际残差≤1e−7且完整当前请求≤2 CPU秒。实测：1个请求、无预热/cache命中、原CLARABEL完整P2optimal；实际残差1.1102230246251565e−16、全部数值有限，但完整根费用上界**2.551250** CPU秒，超出门槛.551250秒（27.5625%）。worker请求CPU2.343750也超过2秒，不是仅.02保守量造成失败。局部Controller1.187500≤2不能替代根结果；返回CLOSE没有提交模型或启动采集。

确定原因：新worker启动/导入/数学输入初始化、完整原P2/判断/序列化与父监视的合计未满足原请求边界。未分离的原因：原求解器纯CPU、CVXPY导入和历史构造各自占比UNKNOWN；当前证据不足将失败全部归因CLARABEL。数值残差不失败，没有公式冲突或已发现未来信息违规；人工conditional公共状态不称Traffic真实可达状态。μ仅取已公开冻结state.mu，旧标签、私有未来或模型未作为当前输入。

本批总计费**34.781250/120 CPU秒**，其中互斥Job+driver实测4.781250，阅读/编辑/交付30秒保守计费（未逐项实耗UNKNOWN）。计量调用墙钟合计5.742220秒；这是调用窗口总和，不是人工工作全部历时。冷调用含退出共2.671875 CPU秒；请求与整调用重叠，不再相加。累计4730.046875、原5小时名义余额13269.953125秒；旧实际缺口仍UNKNOWN，余额不授权后续。

保留证据：[输入](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FROZEN_INPUT.json)、[实际完整数值](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/COLD_NUMERIC_RESULT.json)、[请求费用](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/COLD_REQUEST_COST.json)、[完整冷Job账](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/cold_K43_once.meter.json)、[整批账](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FINAL_BUDGET.json)、[历史保留核验](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FINAL_DELIVERY_CHECK.json)。日志、输入、费用与失败原样保留，不把退出码0或局部返回动作当通过。

仍有效：旧隔离四路径及对应source closure；本次数值可行性和全部五项目标实际输出；新q事件/编码/发布/适用契约、真实采集接线计划。历史1614个保护文件无变动，12个OF源码闭包文件无变动；旧失败及停止状态未覆写。当前没有新的控制、任务性能不退步或预测收益证据。

暂停/不执行：首条真实采集申请及诊断入口实施、实际producer/局部SGD、q拟合与独立验证、39条开发、七条旧校准、B1、充分训练和正式确认；不恢复44001/t80或43001任务。本轮授权的一次冷请求已用完，没有追加第二次冷试验、小K/四用例、保存或Job设施重测。

继续所需：先审批有限工程费用修订。最小提案为≤90 CPU秒、GPU/SGD/拟合/轨迹/回放0，定位合并开销并优化重复历史构造/完整序列化，保留原算法与原边界；随后至多一次同输入新worker冷核验，不搜索输入。若改为启动单独计费的常驻worker模型，必须事前审批启动CPU帽、全批账与稳态边界修订，旧冷失败保持原判定。没有本批偷偷预加载或把门槛放宽。工程通过以后才可重新提出一个最小接线＋SGD0核验＋首条成本采集完整申请。
