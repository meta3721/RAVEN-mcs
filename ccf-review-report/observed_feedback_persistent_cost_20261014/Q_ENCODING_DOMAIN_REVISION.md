# F_count适用域补正提案

状态：SOURCE_CONTRACT_CHECKED / PROPOSED_ENCODING_REVISION_NOT_IMPLEMENTED。本批只核对定义、不拟合；旧Q_SCOPE_AND_FEATURE_CONTRACT.md原文保持。本补正不改OF方法或诊断prior，只修改尚未实现/拟合的概率编码适用域，随首条采集申请供审批。

源事实：CausalTrafficProducer.next_registration按clock+.05+.01*client_index注册，next_clock<100；register_current完成一次注册后无busy/client-in-flight检查，client循环完即进入下一clock。SERVICE.occupancy写的是one registration/client/clock，不是one outstanding/client。服务持续时长有长尾且没有强制<1；同client可以有多次不同key在途。DevelopmentProducer沿用相同调度语义。OF lifecycle.in_flight按key保存，未以client去重；P则按client保存最多一条。因此P_count≤43在该目录成立，F_count≤43不能从43个client推出。

定位：[生产者调度](C:/Cursor/raven.mcs/src/raven_mcs/experiments/calibration_first.py:120)、[无busy限制的注册及cursor推进](C:/Cursor/raven.mcs/src/raven_mcs/experiments/calibration_first.py:123)、[旧开发注册](C:/Cursor/raven.mcs/src/raven_mcs_re_interval/development_acquisition.py:76)、[OF按key在途账](C:/Cursor/raven.mcs/src/raven_mcs_observed_feedback/lifecycle.py:110)。未执行生产者、服务采样或真实轨迹。

拟议编码版本OFq-public-state-1.1：保持原37个数值列和公开device/network分层，仅将F_count/43列改名F_count_scaled=F_count/(43+F_count)，使用事前目录client数43作尺度，有限非负整数F均合法，不从拟合资料估均值/截断。原支持域P/F≤43改为P≤43、F为全部合法公开在途header的非负计数；F不得大于当前累计合法注册数，计数/历史一致且有限。它不是“覆盖支持已成立”，拟合/验证的经验支持仍须独立统计。

全部尝试保留，不按每client只选一个F、不把F>43删除或clip成43、不将物理pending队列与控制可见F混同。消息过期后离开可用F，其物理工作和全量尝试/删失账仍保留。F_mean_age/F_oldest_age继续由当前合法F和实际版本计算，结构为空规则不变。其他列、L/P/V空flag、四个交互项、lambda1 logistic ridge方案不变，无特征扩展或门槛搜索。

由于没有现成拟合模型，本提案不重新标记任何旧模型或缓存。下一批即使只用diagnostic_prior也应归档原始F_count与完整公开F；如审批包含本修订，编码/发布身份记录1.1，否则未来泛化模型仍Pending，不能强行声称旧1.0域覆盖新数据。首条诊断采集不要求泛化模型已经拟合/校准，不用这个依赖阻止受授权的独立学习接口。
