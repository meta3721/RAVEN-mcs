# 同一45011的实际恢复与续行

状态：**COMPLETE_T100_ACQUISITION / WAITING_USER_REVIEW**。原停止点now1.07、SGD32、model_version1、next_grid_tick11、next_clock1/client3被真实恢复；在任何新训练/通知前，模型和控制状态hash、producer/RNG hash、原数据/目标及源码闭包一致。恢复到1.1前先处理原未完成的注册/通知，没有调用build、换seed或重造45011初始模型。用meta分配形状后直接加载已存真实张量，未消耗初始化随机流。[RESUMPTION_CHECK.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/RESUMPTION_CHECK.json)。

parent_run_id仍为`OF-v1/development_cost_and_bootstrap_fit_candidate/45011/results_observed_feedback_continuation_45011_20261014`；原逻辑UTC原点2026-10-14T08:49:32.778907+00:00，原受控服务单位与命名空间不变。实际本会话恢复UTC为2026-10-14T10:01:25.353578+00:00，worker PID27240，新root为`c82d4f786c5547a4b351461d4546acd2`。中间有人工等待/工程中断，不宣称物理墙钟连续部署。

三个冻结源码包raven_mcs、raven_mcs_observed_feedback、raven_mcs_execution保持不变，完整source_closure检查未删除。新增独立`resume_observed_feedback_45011_s2.py`、外部滚动账与根发布设施，不调用旧run入口。原模型、Q/V/L、方法参数、Design on/Gate仅诊断、q诊断先验.5、1步/.01/.01、服务采样/CPU下界及R0/E0工作保持。

第一次恢复会话S1在根发布PermissionError后被设施终止，未发布新完整点；其1.1—1.3三行与21—22个物理SGD的后缀不能拼成可恢复模型。保留日志和33.421875保守费用，恢复理由为普通设施故障，不是追求相同计时或选择结果。S2临时目录首发布又失败，保守2.171875，未有可用根样本，训练不能准入。随后改为工作区内独立反馈目录、逐序唯一临时文件和有界替换重试，保留原测量时间戳/剩余预算算法；该发布路径检查PASS，真正续行会话的独立PID审计True。

最终逻辑轨迹只拼原10行和成功续行990行，合计1000，无重复或缺口；S1丢失后缀独立保留而不并入正式网格。逻辑SGD3281，加丢失物理工作后累计范围3302—3303，上界≤5000。开始观察时仅清除旧19条消费/16条物理前缀删失注记，控制快照不变；旧删失资产原样保留，后续成熟/终点重新形成合法标签。

最终完整点：[trajectory/tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/trajectory/tick1000.complete.json)，model/private字节[179560368, 7493086]。只读成对内容、实际输入权重残差、omega/ell/age、唯一消费、q注册冻结和全网格验证通过。[VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/VALIDATION_AND_SUMMARY.json)。未运行第二条独立轨迹、旧43001/44001、q拟合或开发比较。

实际新增计算入口为[scripts/resume_observed_feedback_45011_s2.py](C:/Cursor/raven.mcs/scripts/resume_observed_feedback_45011_s2.py)，外部根账入口为[scripts/observed_feedback_rolling_budget_s2.py](C:/Cursor/raven.mcs/scripts/observed_feedback_rolling_budget_s2.py)，发布设施为[scripts/observed_feedback_root_publisher.py](C:/Cursor/raven.mcs/scripts/observed_feedback_root_publisher.py)。成功会话标签`resume_s2_workspace`的命令/进程证据保留在相应process/meter/log及charge资产中。该运行已完成，不应再次执行这一固定原1.07恢复入口；后续若获批准须从最终完整点建立新的显式入口和连续账。原build入口未作为恢复入口使用。
