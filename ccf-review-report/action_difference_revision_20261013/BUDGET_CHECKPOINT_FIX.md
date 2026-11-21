# 限定计量协调与成对保存修复

B：PASS，独立设施验证通过。没有恢复v3采集入口，没有训练，也没有重做CPU燃烧或全项目测试。设施通过不代表生产采集已经接入或获准继续。

实际代码：

- [根预算接口](C:/Cursor/raven.mcs/src/raven_mcs_execution/budget.py)：唯一准入来源为根进程发布的互斥累计CPU；tree+driver各计一次，不额外加PID或内部Job。每次启动规划前必须提供包含外部监视的operation_root_ceiling，控制器2 CPU秒不能替代根操作费用上界。数据过期、根命名空间变化或已结束会拒绝新操作；反馈年龄按最大CPU速率扣减。
- [外层协调计量](C:/Cursor/raven.mcs/scripts/coordinated_windows_cpu_meter.py)：沿用旧Job设施，新增50毫秒根账反馈。指令、阶段与全批剩余取最小值；任一先耗尽即停止。旧windows_cpu_meter.py保留。调用预算入口[scripts/action_difference_revision_budget.py](C:/Cursor/raven.mcs/scripts/action_difference_revision_budget.py)记录失败、进程树与驱动，避免重复计费。
- [成对提交](C:/Cursor/raven.mcs/src/raven_mcs_execution/paired_checkpoint.py)：临时模型→临时私有生产者→哈希及内容身份/终点/游标校验→文件就位→原子发布.complete.json。恢复只接受完成标记、匹配方法/种子/跨运行时间命名空间、有效文件哈希与一致T/时钟游标。半对文件不属于恢复点。

一次必要的代表性保存测量使用旧t80实际大小的只读数据：模型44,534,030字节、私有文件14,639,710字节。完整写入、发布和读回CPU为2.734375秒，墙钟2.990260秒。事前保存余量取2×测量CPU+0.5=5.96875秒；这是测量基础上的工程余量，不是普适最坏情况保证。第一次测量在根账有充足额度时进行，初始1秒占位参数没有被当成生产保存保证。序列化布局变化不删除状态字段，私有输出更紧凑。

同一个确定性设施用例覆盖外部驱动费用增长、跳过新规划并申请保存、保存后停止、模型写完但私有文件未写时中断，以及旧完整点可读。外部增长为明确标记的建模账输入；真实测试费用仍由外部根计量。已发布02_before_stop完整点可验证，03_interrupted只留下pending，不能被选为完整点。旧legacy成对点仍可读。身份补充检查拒绝私有tick偏移；准入补充检查拒绝省略完整根费用上界，均复用同一用例及原测量，没有新增保存基准或轨迹。

normal保存间隔50个0.1网格点，near-budget为10点，并在下一根操作会侵入保存余量时先保存。保存费用纳入根账。生产调用还需绑定循环和实测完整根操作上界，不能只套用2秒控制器预算；间隔只能限制已成功提交之间的尾部，不能保证每种硬中断下尾部为零。如果已经没有保存余量，拒绝新保存并保留最后完整点。原始v3科学包和旧结果没有改写。

普通开发失败均保留：导入错误未启动子Job，保守计1 CPU秒；工作区不允许hardlink，首个提交实现失败后改为Windows原子独占rename。没有删测试或放松成对提交条件。对应失败调用也纳入阶段额度。没有再次证明Job计量；没有将设施成功解读为科学成功。

[单用例证据](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_FACILITY_RESULT.json)、[完整根准入](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_ADMISSION_CONTRACT_PASS.json)、[配对身份](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/B_PAIR_IDENTITY_PASS.json)、[保存完成标记](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/facility_pairs_rename/02_before_stop.complete.json)。实际计费与墙钟见[BUDGET_LEDGER.md](C:/Cursor/raven.mcs/ccf-review-report/action_difference_revision_20261013/BUDGET_LEDGER.md)。
