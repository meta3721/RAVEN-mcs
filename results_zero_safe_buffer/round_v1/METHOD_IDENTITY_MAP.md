# METHOD_IDENTITY_MAP

I-Proj-ZS、F1-Proj-ZS、F2-Proj-ZS 共用零质量隔离和 Stage-1 到达参考。服务器权重是 `argmin ||α−β||²`，β 由该次释放集合里冻结的正质量 m 归一。DistanceSolver 的最小 TV 权重只作诊断。

TwoStage-Hájek 使用 `TwoStageHajekAggregator`，权重是 beta_hat 的归一。它按自己的定义使用共同源事件里的合法训练观测，不因为缺少这套 m 而被剥掉样本。

FedAvg-Window 使用 `FedAvgWindowAggregator`，权重来自 raw_counts。同样不套用零质量隔离。

适配还没有在新事件流上跑过训练。缺的是注册模型快照、本地两步和一次服务器 SGD 的接线执行，不是用 0.5 或 oracle 填概率。完成前不能把这两臂标成 TRAINING_VERIFIED。

μ 保持 measured-O 冻结值 [0.6496975806451613, 0.1350806451612903, 0.07258064516129033, 0.14264112903225806]。
