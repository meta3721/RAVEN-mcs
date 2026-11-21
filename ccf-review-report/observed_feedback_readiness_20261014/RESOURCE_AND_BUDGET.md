# 本轮资源与预算

日期2026-10-14。批准上限120 CPU秒；状态PREPARATION_INCOMPLETE / WAITING_USER_REVIEW。总计费**34.781250 CPU秒**：

- 冻结输入及核对旧闭包：Job .750000、driver .140625，计费.890625 CPU秒，墙钟.816957秒。
- 唯一K43冷请求整次调用（含退出）：Job2.515625、driver.156250，计费2.671875 CPU秒，墙钟3.398232秒。
- 旧结果/源码/交付核验：Job1.078125、driver.140625，计费1.218750 CPU秒，墙钟1.527031秒。
- 阅读、编辑及交付未逐项计量，保守计费30 CPU秒；对应实耗UNKNOWN，不能称实测30秒。

互斥树+driver实际合计4.781250秒，计量调用墙钟合计5.742220秒。阅读/编辑/交付包括一条PowerShell语法失败和不存在的只读文件查询，未启动实验或P2，计入上述保守项。本批剩余帽85.218750秒不授权追加请求。

唯一完整请求上界2.551250 CPU秒；该行与冷整调用重叠，不再加入总账。原Job设施及有限共享访问publisher复用，所有worker自启动前进入根Job、单CPU affinity/GPU关闭；根审计均通过。没有重复计量/成对设施基准。

原累计4695.265625，本批后4730.046875；原5小时名义余额13269.953125秒。历史实耗缺口与未逐项实耗UNKNOWN，不能以名义余额恢复旧任务或审批下一批。

SGD=0、GPU=0、q拟合=0、新真实/随机轨迹=0、真实控制回放=0，新增完整数值请求=1（K43），实际模型提交=0。没有实现真实diagnostic_prior采集入口或实际producer；旧代码及1614个保护文件、原STOP和失败保持。45001–45003未用，fixture seed0仅为无随机输入身份，不是新增数据轨迹。

报告目录只有7个MD文件；原始输入、数值、日志、根账与核验分别在results_observed_feedback_readiness_20261014。新增脚本仅冻结输入、一次冷检查、预算包裹及交付审计，非生产采集入口。本批生产源码无变更、无需重跑旧单元/四路径验收；新增检查脚本已实际运行，审计脚本通过；费用科学门槛失败与脚本执行正常分开报告。

[整批预算](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FINAL_BUDGET.json)、[历史保留](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/FINAL_DELIVERY_CHECK.json)、[实际冷费用](C:/Cursor/raven.mcs/results_observed_feedback_readiness_20261014/COLD_REQUEST_COST.json)。后续费用估计/硬帽因真实SGD与新队列成本缺失而暂停，见FIRST_ACQUISITION_REQUEST；不以5000步或1000×2编造充分训练/总成本证据。
