# 45001中断审查与有限工作上界

2026-10-15。使用 ccf-experiment-designer 执行用户交付的限定恢复指令。旧四臂批次为 PAIRING_INCOMPLETE，未进行科学效用筛查；OF已完成，fixed05原保存到t75，另两臂原未运行。

原失联调用的最终meter/charge/EXECUTION_RESULT没有发布，CATEGORY_LIVE与root反馈存在全NULL内容。进程首次观察消失时间2026-10-14 22:46:22（北京时间），确切退出时间与根因UNKNOWN。窄区间System事件41/6008/7/51/55/153查询被系统访问控制拒绝；未据此推断断电、内存不足、算法问题或磁盘故障。没有进行全项目日志扫描或重复K43基准。原NULL文件、模型、报告与费用原样保留。

复用已核验t75成对资产：750格，3225注册，逻辑SGD2493，模型版本128，producer75/client0，无active_registration。窄范围核对冻结入口、单次fixed05进程启动记录、CausalProducer单向100×43注册、backend local_steps=1及training_started重复保护；异常离开当前采集，没有内部训练重试或既有fixed05恢复会话。

上述条件下，失联后缀至多1075步；原单次会话物理上界3568，恢复剩余部分至多1075步，因此fixed05物理合计上界4643，整批上界3354+4643+4300+4300=16597。全部是结构上界，未知后缀不计为0，不补造训练结果。此前留到5000的松上界保留为历史记录，本次另行补正。新的失败或重放须另外计入，不能重复使用同一1075偏移无限重试。

机器证据：[FINITE_WORK_AUDIT.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/FINITE_WORK_AUDIT.json)、[旧保存点核验](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/INTERRUPTED_PREFIX_CHECK.json)。历史中断的精确CPU与墙钟仍UNKNOWN，此步数论证不消除资源未知。
