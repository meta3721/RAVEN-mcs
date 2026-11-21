# Z1_DECISION

- 状态：READY_FOR_BACKEND_IMPLEMENTATION

- F1 相对新 I 的 D 降幅：{'gaps': [0.035841733853507834, 0.045650201631440714, 0.04755040322884755], 'equal': 0.043014112904598695, 'improved_seeds': 3}
- F2 相对新 I 的 D 降幅：{'gaps': [0.04308467743309541, 0.051814516138870025, 0.04888608871299154], 'equal': 0.047928427428318994, 'improved_seeds': 3}

旧规则重放与已审计轨迹一致。新规则只把 m=0 隔离出有效池。
- F1-Proj 33001: 首个动作分歧 {'window_id': 1, 'old_reason': 'AGE_RELEASE', 'new_reason': 'AGE_RELEASE'}; 正质量 committed 1013 -> 1030
- F2-Proj 33001: 首个动作分歧 {'window_id': 2, 'old_reason': 'DEADLINE_RELEASE', 'new_reason': 'DEADLINE_RELEASE'}; 正质量 committed 851 -> 873
- F1-Proj 33002: 首个动作分歧 {'window_id': 1, 'old_reason': 'AGE_RELEASE', 'new_reason': 'AGE_RELEASE'}; 正质量 committed 1012 -> 1036
- F2-Proj 33002: 首个动作分歧 {'window_id': 2, 'old_reason': 'DEADLINE_RELEASE', 'new_reason': 'DEADLINE_RELEASE'}; 正质量 committed 848 -> 883
- F1-Proj 33003: 首个动作分歧 {'window_id': 1, 'old_reason': 'AGE_RELEASE', 'new_reason': 'AGE_RELEASE'}; 正质量 committed 994 -> 1004
- F2-Proj 33003: 首个动作分歧 {'window_id': 2, 'old_reason': 'DEADLINE_RELEASE', 'new_reason': 'DEADLINE_RELEASE'}; 正质量 committed 826 -> 866

D 是最小可行 TV 距离，不是参考投影的失配，也不是预测收益。

Z3 未执行、无新增预测收益。
