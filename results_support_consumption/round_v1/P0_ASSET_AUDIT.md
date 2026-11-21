# P0_ASSET_AUDIT

## 参考重建

### measured-O seed 33001
- trace_hash: `213a7f5a4512f36369434652dfd3fd220d681488f0490e003d7c051477d9cb57`
- n_rows: 4144
- n_u1: 1637
- n_u0: 2507
- n_u1_tau_above_smax: 0
- n_u0_tau_above_smax: 734
- n_u1_arrival_close_ne_window: 0
- n_positive: 1186
- n_zero_mass: 451
- n_one_hot: 1186
- n_mixed: 0
- max_abs_composition_error: 0.0
- min_positive_mass: 0.08174256357865448
- 首个正质量窗口: `{"window_id": 0, "history_rows_before_window": 0, "p_hat_source": "prior_rate", "attempt_id": "g0017_0024|0|0", "m": 7.797037315472935, "composition": [1.0, 0.0, 0.0, 0.0], "observed_group_counts": [1, 0, 0, 0], "one_hot_explained_by_single_group": true}`
- q_use、oracle 概率和 target_value 没有进入参考。

### visit seed 32001
- trace_hash: `0178b5fe84ce98afb5511ae10320402bf3759e8455d0809be01436e96b106386`
- n_rows: 3556
- n_u1: 849
- n_u0: 2707
- n_u1_tau_above_smax: 0
- n_u0_tau_above_smax: 660
- n_u1_arrival_close_ne_window: 0
- n_positive: 630
- n_zero_mass: 219
- n_one_hot: 630
- n_mixed: 0
- max_abs_composition_error: 0.0
- min_positive_mass: 0.35364170585179433
- 首个正质量窗口: `{"window_id": 0, "history_rows_before_window": 0, "p_hat_source": "prior_rate", "attempt_id": "g0015_0177|0|0", "m": 1.0159852109612875, "composition": [1.0, 0.0, 0.0, 0.0], "observed_group_counts": [1, 0, 0, 0], "one_hot_explained_by_single_group": true}`
- q_use、oracle 概率和 target_value 没有进入参考。

## 原 U

原 U 同时要求 compute、network、deadline、staleness 和观测。`staleness_pass = tau <= S_max`。
因此原 U 已经包含版本陈旧。新臂仍按自己的下载版本再过滤，不沿用 trace 里的 downloaded_version。

## 检查点

- results_joint_ou\round_v1: 完整 final.pt 50 个，未完成且排除 []
- results_c1_cityscanner\round_v1: 完整 final.pt 50 个，未完成且排除 []

本次不加载任何历史 checkpoint。partial 且没有 final.pt 的目录排除。

## 调度器

固定测试创建了一次非神经网络的版本更新，并完成了状态恢复。没有 SGD，也没有预测。

## 资源

- CPU 秒: 2.937500
- wall 秒: 3.928007
- 峰值 RSS 字节: 222945280
- 最小可用内存字节: 4283580416
