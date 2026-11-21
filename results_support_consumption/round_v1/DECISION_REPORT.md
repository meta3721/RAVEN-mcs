# DECISION_REPORT

1. 跨窗口保留是否带来互补：主块状态是 NO_STRUCTURAL_ADVANTAGE。
2. 缓存是否改变消费时间：P1 账本分开记录了到达关闭和 committed 关闭。正权重仍待训练核验。
3. 是否优于普通缓存：还不能把主块说成优于普通缓存。
4. 是否变成任务收益：无新增训练、尚无预测收益结果。
5. 相对旧证据：这次回放实现了 HOLD/CONSUME，没有把旧 xw 池里当窗全消费的零结果改写成新机制。
6. 成本：见 BUDGET_LEDGER.json。P0=PASS，P1=NO_STRUCTURAL_ADVANTAGE，P2=PASS。
7. 独立确认：没有未参与模型选择的日期、区域或批次。P4 不能声称独立确认。

合并互补比例：0.09

无新增训练、尚无预测收益结果。
