# 仅本恢复阶段的资源授权

用户交付20261015恢复指令授权：新增阶段1800 CPU秒、9000活动秒，原批CPU3000修订4800、总墙钟14400修订23400。旧CPU占用2983.859375和旧墙钟留账14373.550642固定保留，不退款、不从旧余额多借16.140625秒。旧失联调用2388是保守分配额占用，不能称实际算法耗时或经审计上界。

fixed05累计墙钟改9000，扣原包络6671.2后，本阶段该臂最多2328.8秒；fixed2/no-Q各7200且共同受阶段9000。每臂物理5000、总20000及每完整在线根请求2 CPU秒不变。GPU0、q=.5 diagnostic_prior，禁止扩种子、拟合q、B1、39条或正式确认。

新增PilotRecoveryAuthorization是原AutonomousPilotAuthorization的限定子类，只允许fixed05、fixed2、OF-no-Q-stop，明确CPU4800及stage1800/9000；原45011与原3000授权校验保持。反序列化按显式extension字段选择，旧授权不能假装覆盖新帽。原authorization.py完整归档，原hash与冻结闭包一致；仅该文件资源接口变化，新旧源码身份分列，不伪造“源码未变”。

资源迁移不改变数据、模型、学习、控制、注册p/q或原概率适用身份。原scope.service.CPU_limit=3000保留为原冻结身份字段，实际新帽在独立resource_extension明确列出，不作为生产概率或已校准身份。本恢复先证明原数值/随机状态完全等值，再只改变collection_authorization字段，另留迁移证据。

新账采用显式活动区间和已关闭/执行会话，不用目录年龄累加旧审批等待。工具外部执行授权等待由dispatch证据单列排除，没有运行worker；原开发时间和未知费用不删。初始化前读取/实现/交付CPU以30秒保守预留，实际未计量部分UNKNOWN；初始化前墙钟最终保守预留1500秒，并保留首次较小预留记录。机器连续账会记录剩余额度；4800仅为连续计费授权帽，不证明旧历史实际CPU已完整审计。

[RESOURCE_AUTHORITY.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/RESOURCE_AUTHORITY.json)、[SOURCE_RESOURCE_MIGRATION.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/SOURCE_RESOURCE_MIGRATION.json)、[活动区间](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/ACTIVITY_INTERVAL.json)。

初始化前等待口径补正：初次工具请求的设施文件2026-10-14 23:49:09 UTC创建后立即进入执行授权等待，阶段初始化直到2026-10-15 00:08:34.4985905 UTC才运行。保守选00:08:32为等待终点，1163秒确证没有worker；按本指令“审批等待不计活动执行”从1500总留额中单列排除，其余337秒仍保留为初始化前实际/未知活动留额。原1500登记、补正前活动账和全部证据独立保留；不删原开发或未知部分，不改变9000/23400上限或旧14373.550642。最终连续账使用337，原文1500指补正前总留额。[PREINITIALIZE_APPROVAL_CORRECTION.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/PREINITIALIZE_APPROVAL_CORRECTION.json)。

辅助费用补记：实验Job/PID根审计之外的读取、PowerShell状态查看及最终交付不假装已包含在训练作业根费用中。原30保守准备费之外另扣60保守辅助费，合计90；实际未知部分继续UNKNOWN。一次状态命令仅进程局部CPU0.5秒只作费额规划，不能据此推算精确根总量或证明90为上界。额外占用在原1800内部扣除，不退款、不借旧16.140625余额，也不重复加算已计量的root driver/PID。当前noQ调用硬帽950加此前774.78125及新增60仍小于1800，因此这次补记不使运行中的根准入超阶段总帽。墙钟已包含在显式活动区间，不重复加算。
