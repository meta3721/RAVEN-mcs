# 动作差值失败后的方法准备

结论选择：**规格可实现，申请下一次限定实现**。当前为WAITING_USER_REVIEW，尚未实现或验收。主技能ccf-idea-optimizer采用标准模式整理唯一局部机制，ccf-experiment-designer负责证据与门槛；没有启动其他候选、文献搜索、训练或采集。

## 依据与研究对象

读取上一批8份报告并核对实际接口。旧v3的原789点零差异、最多10/799上界保留。动作差值候选在一个人工初态、广泛合法未来集合和全分支优势判据下失败；33个子集极值不是全联合外界，该失败不等于Traffic方法失败。上一批的根预算/成对提交设施独立有效，未接入新生产采集，当前不重复设施测试。

新对象是“当前可观测部署目标缺口的经验反馈控制”。改动的科学含义是放弃要求每个未知状态都有对全部未来占优的首动作，改用真实可见的当前释放质量、上次真实释放质量与debt方向决定释放。没有收紧未知未来集合，也没有挑另一个人工初态来修复旧证书。旧科学失败身份不变。

唯一候选OF-v1的因果链为：当前完整P2实际omega/ell/age＋上次真实质量＋欠覆盖debt方向→可观测释放收益与耐心项→改变非强制时刻→等待G/W变化→另行验证任务不退步。预期收益是待检验主张，不是结果。

## 机制与源码差异

规格给出B=c_minus−(ell+0.02 age)+0.10 Qhat·(omega−μ)+0.20 elapsed/4，达到0.02+1e−7才主动关闭，保留暖启动、最小client、deadline和终点优先级。原P2的Q更新与约束不变；额外debt项用于停止，而不是再改聚合权重。参数只固定一次，未在44001上搜索。

单窗口触发只看当前缺口；OF-v1还对当前结果相对最近实际结果的变化及偿债方向作反应。固定窗口只看时钟；OF-v1在时钟相同但历史debt方向不同的状态可给不同决定。二者是否形成实测增益尚未知。去掉debt触发而保留P2的Q，可以分辨新增停止反馈与原聚合反馈；去掉所有停止历史的当前缺口基线回答普通提前关窗是否足够。

真实接口发现：旧ControlConfig/QValue把版本锁为v3，DynamicWindowRunner要求FrozenServiceModel，preview的提交指纹包含时钟，P2同时依赖原始Q与方差。因此需要独立新版本schema/lifecycle及缓存绑定接口，不能仅改方法名、塞一个假未来预测器或直接复用旧时钟指纹。当前只交付这些修改位置和规格，旧源码未改。

## 目标和评价语义

G是共同t=20.1—100.0的800网格点上最近一次非空实际释放ell的平均；未有非空释放前ell=1，单列该比例；空关闭不伪造新质量。控制动作筛查D是20<t<100的799点，不能混用800格与799决策分母。辅助旧J继续采用ell+0.02 age+0.20 duration/4，不能用新的B替代J评价。

W沿用原mean_window_duration：对close_time>20的全部已关闭窗口（含空关闭及终点正时长窗口）平均duration。原v1源码的post列表未剔除空窗口；新比较也不得只留非空或有利窗口。若没有可计窗口或T100未完，不能补成W=0或当完整结果。另报注册到消费延迟，不把它混成W。

纯几何d是同一M/约束的最小L1距离，实际ell来自完整P2真正使用的权重；本候选用ell，d单列诊断。旧v1几何投影及未校正组成的数值、旧v3概率/训练结果不能直接作为OF-v1的完整共同底层指标。原始数据和Design无关划分可保留；依赖停止策略的U/q、版本/训练、参考质量、模型、预测及G/W必须按新身份重算。

选择后续“匹配收益路线”，因为主对象是目标缺口：P3平均G相对下降≥2%、W不超过基线1.05倍、至少2/3配对种子方向一致，且≥5%非暖启动合法点有策略差异。差异仍只是筛查，不等于收益。P5保持G≥2%改善、W保护≤5%、最终RMSE_mu平均配对相对退步≤1%；P6保留相应单侧95%界、收益下界>0和完整外部比较。没有降低原标准。

## 准备证据、挑战与缺口

源码核对通过；简单精确算式显示同池同当前质量下debt方向可改变阈值符号，κ=0后差异消失。这支持“规则不是固定窗口或无历史阈值”的规格判断，不支持Traffic实际激活、实现正确性或2秒成本。

近邻重叠挑战：可能只是已知事件触发/队列漂移控制组合。当前不主张理论或方法新颖性，标needs-search；后续核对target-aware event triggering、drift-plus-penalty/virtual queues、异步缓冲与age/count停止、online change/stopping和目标校准聚合等类别。没有引述不存在的文献或评估CCF A竞争力，投稿目标暂按已有TMC/系统学习场景，适配性待证据。

证据挑战：改善可能仅来自普通提前关闭、弱固定基线、策略相关q变化或少训练。计划冻结多个固定/当前缺口基线、去debt/去最近质量消融、共同完整后端和资源，并保留P4训练平台与P5完整外部比较。真实任务收益、概率校准和单次完整成本属于needs-evidence；未发现需未知未来的定义缺口。

设计可修复风险是完整P2事件缓存与新概率特征接口；证据风险是真实历史状态作用、G/W收益和任务保护；requires-new-result为新策略q及完整学习/控制比较；novelty/venue-fit为needs-search。保留旧失败，不写论文、不提前编码新收益。

交付：[完整规格](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/METHOD_SPEC_CANDIDATE.md)、[性质账](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/PROPERTY_LEDGER.md)、[最小证据计划](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/MINIMAL_EVIDENCE_PLAN.md)、[下一批申请](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/NEXT_STAGE_REQUEST.md)。本批费用见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_preparation_20261013/BUDGET_LEDGER.md)。
