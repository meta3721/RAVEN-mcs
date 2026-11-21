# 下一批最小接线计划（尚未实施）

OF-v1公式、参数、configured Design和完整P2不变。现有IsolatedQ/isolate与FutureTrainingAuthorization保护保留。下一批可将下列开发、必要SGD0验收和首条成本采集合成一个限定审批批次；本次P3费用失败，申请当前暂停。

1. probability.py新增OF专用DiagnosticPrior，kind/role均明确diagnostic_prior，值Beta(1,1)均值.5、版本绑定π_boot，不创建EvidenceQTable假证据。按Q_SCOPE_AND_FEATURE_CONTRACT归档编码及资源字段，新增物理删失字段；本次不拟合。发布桥及模型角色解析分别实施，Pending仍拒绝实际生产分母。
2. schema/lifecycle新增明确calibration_only入口标志与调用权限，生产继续拒绝prior/fitted_not_validated/isolate。只有批准批次可用独立DiagnosticCollectionAuthorization，明确method/seed/stage/source/T100/local_steps1/LR.01、GPU0、最多5000SGD和整批根CPU上限；旧43001及现有生产授权类型不能代用。把calibration_only从snapshot一路传至preview的q.require，不能只改日志。正常生产仍要求完整已验证q；不要通过isolated_test=true绕过。
3. backend接实际FullWindowRunner/CommonNDMF/ClientTrainer，独立诊断授权校验后调用原真实学习后端；不得移除旧生产FutureTrainingAuthorization或给旧43001泛化权限。冻结真实架构/初始化/scaler/学习配置；每次真实SGD累计计步并根准入。E0保留注册原工作但不入聚合，R0沿原无观测语义不产生训练输入；与消息消费账分开。
4. 新独立脚本入口scripts/acquire_observed_feedback_diagnostic.py（计划名，当前文件不存在）。创建本run真实因果producer，事件只在到时公开，stage1注册冻结且完成前私有；公共目录/目标/配置在运行前公开。不得用旧trace中的未来表控制、不接假FrozenServiceModel、不让历史终态成为新模型初始值。学习与服务分别RNG，实际通知稳定排序；当前私有服务队列只由producer保存而不进入控制snapshot。
5. worker常驻、根预算从启动前纳入Job，保持tree+driver唯一账。新worker启动/导入/初始化和第一次自由P2均保留费用；需要预加载或调整进程结构时事前声明启动成本、启动CPU帽及全批计费，并另定义稳态请求；当前2秒冷失败仍失败，不能改回当前证据。见FAILURE_REPORT的有限工程提案。
6. 每窗口成功实际提交后更新V/Q/L、窗口后滞后p估计器，并在新窗口打开前冻结下一配置/p/q。仅利用此前真实通知；注册旧消息保持原p/q/Design。无模型验证证据时整个π_boot运行始终.5，不逐窗按观测校准。
7. 成对保存包括真实模型/历史版本、全部backend work/update、私有stage1/producer待处理服务队列、p/q配置和概率账、Q/V/L、学习/service/python/numpy/torch RNG与同run clock。使用已有PairedCheckpointStore完成标记，校验source/身份/游标；cache丢弃重算。保存失败或部分模型故障须隔离，不能从日志拼成恢复点。终点T100仅关闭一次；预算停止用可恢复前缀与删失，不缩短T。

必要新增关键路径仅验收这些改动：诊断授权正确/错误seed及生产prior拒绝；真实后端SGD0接线和私有完成可见性；p/q窗口边界；含真实producer队列的成对恢复及T100/前缀删失。复用前批缓存/提交与设施证据，不再重跑四整套或Job基准。SGD0检验不是实际训练通过。

预计一次局部开发1–2个开发日，CPU开发核验暂估150秒；人员时间不是设备时。冷启动修订未获准且费用未过前，任何采集总额都是条件估计，不能执行。实现后如果必须改B/P2、读未来或取消保护才能接通，报告冲突而不换方法。普通开发错误在批准原预算内修复。

当前未实施项：诊断入口/授权、泛化编码器/q模型、跨run发布桥、真实producer队列持久化及物理删失字段、真实局部SGD采集；现有四路径接口证据仍只属于隔离输入。
