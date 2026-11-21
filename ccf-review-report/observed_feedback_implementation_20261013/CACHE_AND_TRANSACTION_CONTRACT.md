# 注册、缓存与事务契约

## 可见性及概率身份

on_register接受后端合法本地观测形成的private_summary，先固定注册时间/Design/p/ratio/R/E/q及私有摘要哈希，再backend.prepare_work。private_stage1及其hash只在生命周期私有持久化域，不进入控制snapshot；InFlight只含公开Registration、固定q与允许R/E。完成时摘要哈希必须与注册匹配，只有合法完成后Delivered进入P2。控制snapshot没有backend张量、私有未完成质量或未来队列字段。

RegistrationFeatures保留合法age/slack/count、政策/学习/服务/目标上下文及完整history_json/hash；history是当时Q/V/L、elapsed、已完成P与公开F。保留原始合法编码，不能只存无法校准的摘要hash。生产适用identity需明确学习字段与真实data/target，时钟有run_id/origin/unit；q模型只能在窗口边界冻结，旧消息q不改。没有未来预测器构造参数。IsolatedQ只有显式隔离模式可用，诊断prior没有本批入口，PendingQ不填常数；新q校准仍缺失。

## 数值与提交绑定

P2NumericResult为不可变tuple和solver_json；cache key覆盖全部pool摘要/key/注册q及身份、Q、V、当前版本、μ、完整设置、配置/Design和方法版本。时钟、revision、公开F改变而载荷不变时可复用。BoundReleasePreview另含当前snapshot fingerprint；每次命中验证dependency_hash和keys，再新建绑定，不修改旧对象。所有输入变化必须失效，纯d不参加控制。

apply_release核对最新指纹、依赖、keys/消费账、原可行残差≤1e−7及实际M、omega、ell；原STALE_PREVIEW行为保留。deadline/终点的小K采用相同退化可行约束，完整目标的单点解有精确Cauchy证明，其他情况调用原完整RavenAggregator。没有缓存动作、改注册q或删variance项。

## 提交及故障隔离

真实backend.apply成功后才更新v/Q/V/L、消费keys、窗口及backend同步。任何apply/后续同步异常标记fault；由于模型可能已改变，不能承诺回滚。故障态所有正常事件、snapshot、提交、checkpoint_state和恢复拒绝；to_dict只作为故障诊断。测试用真实CommonNDMF在模型改变后的variance hook注入失败，证实没有混成合法状态。处理故障需要另行审核或从旧完整点新分支恢复，本批不自动恢复。

完整检查点记录私有注册摘要/哈希、全部概率账与合法历史、Q/V/L实际omega、模型/版本/工作/已完成更新、源代码closure、学习配置、clock及RNG。cache丢弃重算。已有PairedCheckpointStore的完成标记/hash/identity/游标校验继续使用；OF层额外校验method/source/config/data/target和fault/注册摘要一致性。旧v3身份不可直接恢复。

## 根费用客户端补充

旧根预算/成对库源码保留。新RootClient打开live账时允许Windows共享delete，原子替换读到的是完整旧或新文件；schema/root_id/finished/stale和扣减规则不变。新AtomicPublisher仅在本批启动器本地绑定，暂态rename重试最多50毫秒，保留原测量stamp/cost而非重标时间，读者按年龄扣减。没有提高总预算或2秒，没有新增设施基准。

冻结边界文件保留原字节。实际请求上界另外取独立PID区间+monitor差的保守floor，以防短区间Job量化；这个max只能提高原根上界，PID不再加入总账，首次启动仍包含全部费用。具体最终样本与修复失败见资源报告；未来生产需绑定实测完整根操作上界及保存余量，不能用2秒局部CPU替代根准入。
