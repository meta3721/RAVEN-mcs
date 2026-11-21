# P0 资产定位补正

日期：2026-10-12。状态：**WAITING_USER_REVIEW**。本轮授权仅为方法准备，使用 ccf-experiment-designer 的 design / standard 工作流。

## 补正结论

旧候选确实存在，位于 [results_reachability_stopping_v1](C:/Users/szr/Desktop/record/1/results_reachability_stopping_v1/)。可执行源码为 [run_geometry_gate.py](C:/Users/szr/Desktop/record/1/results_reachability_stopping_v1/run_geometry_gate.py)，方法身份为 `target_gain_stop/v1`。同目录保留冻结配置、协议、六策略配对结果、逐关窗与决策记录、停止报告和停止后审计。

原 [P0_REPORT.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_v2_p0_20261012_215621/P0_REPORT.md) 的检索范围是项目 live src/scripts，未覆盖该 Desktop 目录。其“本机未定位原始 v1 源码/运行文件”现已补正；不能继续据此认定旧候选不存在。原 [METHOD_SPEC.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_v2_p0_20261012_215621/METHOD_SPEC.md) 中的离线 L2 函数仍不是停止策略，但也不是旧 v1 的实际实现。

原 P0 报告、failure_evidence、EXECUTION_STATE 与旧 v1 STOP 均原样保留。补正不把旧 P0 改写成 PASS，也不把旧候选的 G2 失败改写成成功。本轮已经具备旧方法来源和一个具体新候选规格；新规格尚未实施，运行身份仍未验收。

## 已完成的只读证据核验

完整读取旧控制器、审计脚本及全部协议/报告/配置；读取六策略 MAIN_COMPARISON、closures、timeline，以及 target_gain_stop 的 decisions。没有执行或导入旧控制器、没有调用其 load/execute/main，没有启动停止后审计脚本中的校准扰动，也没有生成新事件或轨迹。

本轮另用标准库对**已有文件**核验：800 个共同评分时点/策略；关窗版本顺序、消息唯一消费、权重约束、关窗分数与时间网格拼接。六策略 J 与原表的最大绝对差为 1.11e−16，已存权重最大约束残差为 3.33e−16。此处复算使用已存 distance/age，未独立重建 atomic Q 和真实到达版本；那些检查仍以历史 COMPLETED_ARTEFACT_AUDIT 为来源，不冒充本轮新验证。

旧 v1 依赖的项目 atomic_units.parquet 与 seed41001 training_eventtrace/events.parquet 均存在；未加载、重建或修改这些数据。这只证明路径存在，不证明其内容版本与当年完全相同。旧脚本使用绝对 ROOT，复现必须另获批准，并显式核对依赖版本；不能直接运行写入原 OUT 的 main。

结构化证据：[SAVED_EVIDENCE_AUDIT.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/SAVED_EVIDENCE_AUDIT.json)、[SOURCE_INVENTORY.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/SOURCE_INVENTORY.json)。37 个保护文件前后内容一致，其中旧 v1 25 个、原 P0 Markdown 4 个、原 P0 结构化材料 8 个；__pycache__ 未读取或执行。

## 当前归属

| 对象 | 身份与状态 | 允许用途 |
|---|---|---|
| 旧 v1 | target_gain_stop/v1；STOP_GEOMETRY_WAIT_BASELINE | 历史控制代理负证据、源码机制诊断 |
| 原 P0 | 当时 live 目录定位不足；WAITING_USER_REVIEW | 保留发现范围与审批历史，引用时附本补正 |
| 新候选 | reachability_stop/conditional-bundle-v2；PROPOSED_NOT_IMPLEMENTED | 方法审查、实施成本与验证计划 |
| configured-Design | 已有身份专项证据 | 可复用完整聚合器资产；不等于新动态控制通过 |

没有新检测收益、预测不退步或预测收益。本轮状态保持 WAITING_USER_REVIEW，旧取消任务不恢复。
