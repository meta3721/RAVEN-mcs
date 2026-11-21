# A1_LOSS_DIAGNOSIS

口径：m>0 为正质量，m=0 为零质量。状态数来自旧 P1_EVENT_LEDGER，替换关系来自与旧动作逐项一致的旁路重放。

- I-Proj 33001 positive: 候选 1186，committed 1186，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- I-Proj 33001 zero: 候选 451，committed 451，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- I-Proj 33002 positive: 候选 1198，committed 1198，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- I-Proj 33002 zero: 候选 463，committed 463，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- I-Proj 33003 positive: 候选 1185，committed 1185，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- I-Proj 33003 zero: 候选 445，committed 445，superseded 0，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33001 positive: 候选 1186，committed 1013，superseded 173，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33001 zero: 候选 451，committed 434，superseded 17，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33002 positive: 候选 1198，committed 1012，superseded 184，overflow 2，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33002 zero: 候选 463，committed 436，superseded 26，overflow 1，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33003 positive: 候选 1185，committed 994，superseded 191，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F1-Proj 33003 zero: 候选 445，committed 412，superseded 33，overflow 0，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F2-Proj 33001 positive: 候选 1186，committed 851，superseded 333，overflow 2，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F2-Proj 33001 zero: 候选 451，committed 253，superseded 49，overflow 4，expired 145，endpoint 0，version_rejected 0，not_delivered 0
- F2-Proj 33002 positive: 候选 1198，committed 848，superseded 335，overflow 7，expired 0，endpoint 8，version_rejected 0，not_delivered 0
- F2-Proj 33002 zero: 候选 463，committed 274，superseded 46，overflow 6，expired 125，endpoint 12，version_rejected 0，not_delivered 0
- F2-Proj 33003 positive: 候选 1185，committed 826，superseded 355，overflow 4，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- F2-Proj 33003 zero: 候选 445，committed 268，superseded 58，overflow 3，expired 116，endpoint 0，version_rejected 0，not_delivered 0
- S-Proj 33001 positive: 候选 1186，committed 868，superseded 313，overflow 5，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- S-Proj 33001 zero: 候选 451，committed 315，superseded 52，overflow 6，expired 78，endpoint 0，version_rejected 0，not_delivered 0
- S-Proj 33002 positive: 候选 1198，committed 886，superseded 311，overflow 1，expired 0，endpoint 0，version_rejected 0，not_delivered 0
- S-Proj 33002 zero: 候选 463，committed 262，superseded 43，overflow 9，expired 149，endpoint 0，version_rejected 0，not_delivered 0
- S-Proj 33003 positive: 候选 1185，committed 849，superseded 316，overflow 4，expired 0，endpoint 16，version_rejected 0，not_delivered 0
- S-Proj 33003 zero: 候选 445，committed 252，superseded 50，overflow 3，expired 131，endpoint 9，version_rejected 0，not_delivered 0

主块零质量新消息替换仍 pending 的正质量旧消息：198 次，客户端 43 个。
主块正质量消息被同客户端替换：2511 次；其中终结年龄小于 2 的 2019 次。
主块正质量溢出时池内另有零质量消息：25 次。
主块 expired 合计：正质量 0，零质量 744。

最早的零质量替换正质量示例：
- close 2 old g0019_0028|1|0 m=0.9523342185430544 -> new g0019_0028|2|0 m=0.0 group [0.0, 0.9523342185430544, 0.0, 0.0]
- close 2 old g0019_0028|1|0 m=0.9523342185430544 -> new g0019_0028|2|0 m=0.0 group [0.0, 0.9523342185430544, 0.0, 0.0]
- close 2 old g0019_0029|0|0 m=5.476490495391705 -> new g0019_0029|2|0 m=0.0 group [0.0, 5.476490495391705, 0.0, 0.0]
- close 2 old g0019_0029|0|0 m=5.476490495391705 -> new g0019_0029|2|0 m=0.0 group [0.0, 5.476490495391705, 0.0, 0.0]
- close 2 old g0019_0029|1|0 m=0.6722359189715679 -> new g0019_0029|2|0 m=0.0 group [0.0, 0.6722359189715679, 0.0, 0.0]

最早的期限前正质量替换示例：
- close 1 age 1 old g0017_0026|0|0 m=48.475956934051766 -> g0017_0026|1|0 m=4.43364056517054
- close 1 age 1 old g0017_0026|0|0 m=48.475956934051766 -> g0017_0026|1|0 m=4.43364056517054
- close 1 age 1 old g0017_0026|0|0 m=48.475956934051766 -> g0017_0026|1|0 m=4.43364056517054
- close 1 age 1 old g0017_0027|0|0 m=12.458866525942932 -> g0017_0027|1|0 m=4.800309676216777
- close 1 age 1 old g0017_0027|0|0 m=12.458866525942932 -> g0017_0027|1|0 m=4.800309676216777

主块被替换正质量消息的观测 ID 计数 7674。其中被直接替换者覆盖 0，未进入该臂任何 committed 消息的观测 ID 计数 7674。
这是观测 ID 的计数，不是独特全局 ID 的因果损失证明。unique_observation_loss 按臂在 A1_OBSERVATION_RETENTION.csv 的 n_absent_from_committed 中可复查。
m 的合计是冻结参考质量，不是总体概率，也不是预测贡献。
positive_weight_used=UNKNOWN。committed 还不等于优化器正权重。

本轮无新增训练，没有新增预测收益。
