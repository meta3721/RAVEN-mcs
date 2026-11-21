# A0_FINDINGS

- 状态：PASS
- 问题：无

measured-O 的三 seed 等权平均 D 由 P1_SUMMARY.csv 的 mean_D 直接平均，不把窗口当作独立重复。
与指令中的核对值比较只用于发现读数错误；结果列来自 CSV。四种方法的差都不超过 1e-8。
S-Proj 互补释放是 [8, 8, 11]，合计 27/300。
正质量交付合计 3569。跨窗提交比例的分母是各种子自己的 positive_delivered。

平均驻留和 p95 驻留来自运行器 `_arm_summary`：只累计 state 为 committed 且 m>0 的消息。
它不是全交付队列的平均等待。未提交消息没有被记成等待 0，但也没有进入这个均值。

P1_SUMMARY 的 cpu_seconds 和 wall_seconds 随同一阶段往后递增，是阶段监控快照。
不能把各臂相加，也没有每臂独立耗时；每臂耗时记 unavailable。
实际成本只汇总 BUDGET_LEDGER 的各次执行：
- P0 RESOURCE_EXIT: CPU 0.15625 s, wall 0.0 s
- P0 RESOURCE_EXIT: CPU 0.109375 s, wall 0.011848099995404482 s
- P0 PASS: CPU 2.953125 s, wall 3.9490694999985863 s
- P1 NO_STRUCTURAL_ADVANTAGE: CPU 8.859375 s, wall 9.289178599981824 s
- P2 INVALID_IMPLEMENTATION: CPU 2.125 s, wall 2.385370600008173 s
- P2 PASS: CPU 2.21875 s, wall 2.489281899994239 s
- 账本 CPU 合计 16.421875 s，wall 合计 18.124749 s。
其中两次 P0 RESOURCE_EXIT 发生在重型导入之前，不代表回放成本。

来源：P1_SUMMARY.csv、P1_WINDOW_METRICS.csv、P1_STATUS.json、BUDGET_LEDGER.json。
