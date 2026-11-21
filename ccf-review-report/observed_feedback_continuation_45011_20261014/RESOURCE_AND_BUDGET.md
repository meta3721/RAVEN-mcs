# 原3600总帽的连续账

旧计费183.468750 + 新阅读/编辑/交付保守30 + 新根实测34.156250 = **247.625000/3600 CPU秒**。剩余3352.375000。旧实测143.875000、旧失败保守9.593750、两轮阅读/编辑/交付保守60；已知根实测合计178.031250，保守69.593750，实际缺口UNKNOWN。均累加，不从0重记。

新增根：种子定向审计6.875000、当前身份补充.171875、变更驱动SGD0 7.437500、唯一实际采集12.015625、只读真实prefix恢复7.656250；全部根审计通过。费用是tree+driver，PID和内层测量不重复加。唯一实际采集tree10.609375+driver1.406250，执行墙钟36.099392秒；2小时看门狗未触发。所有新增计量调用墙钟64.056053秒，开发撰写墙钟另计，非实验服务时间。

采集互斥账：初始化4.843750、在线.140625、训练.687500、事件/最终归档/退出2.578125、保存3.765625=12.015625。训练函数自身累计CPU.140625、墙钟2.763844、最大CPU.078125/墙钟2.656670；0或.015625的短步CPU受计时粒度影响，不能叫免费训练。外部监视始终计入根分类。

保存最大根上界1.035625秒，reserve保持5.968750。初始、pilot_prefix、pilot_complete和停止删失点均真实保存并计费；两个pilot点保存同模型/队列而计划字段不同，是多做的一次保存，费用没有删除。后续建议收敛为一个pilot完整点；当前真实源码不改，以保持prefix恢复身份。

计划分项可调配，setup220/init120/online1000/train800/events950/save360/repair150；累计分类setup137.875/init4.843750/online.140625/train.687500/events2.578125/save4.578125/repair96.921875。没有因repair接近100停下；此次是续行总费用计划不足。

累计计费5012.859375，原5小时名义余额12987.140625；历史实耗缺口UNKNOWN，名义余额不是下一批授权。[BUDGET.json](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/BUDGET.json)、[charge_acquire.json](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/charge_acquire.json)、[acquire.meter.json](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/acquire.meter.json)和[acquire.process.json](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/acquire.process.json)；worker24612由root记录核对，只读恢复worker19104不是新轨迹。
