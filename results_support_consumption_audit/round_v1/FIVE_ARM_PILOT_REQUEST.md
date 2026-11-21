# FIVE_ARM_PILOT_REQUEST

状态：待批准。本文件不是训练授权，本次没有执行。

目的：在 measured-O 上判断普通缓存相对强即时聚合是否改善预测任务。结果不能写成支持感知调度或完整 P2 的成功，也不能写成 RAVEN 已有应用收益。

## 队列

主块 measured-O，种子 33001、33002、33003。每条轨迹 100 个关闭。共 15 条：

1. I-Proj seed 33001
2. F1-Proj seed 33001
3. F2-Proj seed 33001
4. TwoStage-Hájek seed 33001
5. FedAvg-Window seed 33001
6. I-Proj seed 33002
7. F1-Proj seed 33002
8. F2-Proj seed 33002
9. TwoStage-Hájek seed 33002
10. FedAvg-Window seed 33002
11. I-Proj seed 33003
12. F1-Proj seed 33003
13. F2-Proj seed 33003
14. TwoStage-Hájek seed 33003
15. FedAvg-Window seed 33003

S-Proj 和完整 P2 不在本批。两种普通缓存都要训练并完整报告，不能事先只留几何均值更好的 F2，也不能看 test 再选等待尺度。

## 臂

1. I-Proj：同一到达参考，到达关闭立即消费。
2. F1-Proj：普通缓存，最老正质量消息年龄达到 1 时释放。
3. F2-Proj：普通缓存，年龄达到 2 时释放。
4. TwoStage-Hájek：完整强即时基线，保持该方法自己的定义。
5. FedAvg-Window：完整强即时基线，保持该方法自己的定义。

I/F1/F2 使用同一个新参考。外部基线不复制旧 q 模型来声称已经适配。共同部分是已交付事件流、注册时本臂最新版本、Stage-1 组成、固定关闭网格和 100 窗终点。各臂自己产生本地更新，不复用旧梯度、旧下载版本或旧预测。

## 当前还没有的后端

静态阅读，没有执行 SGD。

- I/F1/F2 的聚合权重必须是参考投影 `argmin_{α in C} ||α−β||²`。现有 DistanceSolver 只返回最小几何距离权重，不能代替这个投影。
- TwoStage-Hájek 与 FedAvg-Window 在本协议入口里会直接拒绝执行。旧 window runner 有它们的训练路径，但那是旧事件和旧 q 定义，不是本协议的适配。适配完成前记 BASELINE_NOT_READY，不能删掉这两臂后宣布成功。
- 需要补齐的接口：按本臂版本生成模型更新、服务器聚合、九个检查点评分、以及模型/优化器/客户端快照/pending/RNG/账本/预算的联合恢复。只恢复调度器计数不够。
- 训练长度、本地 2 步、CommonNDMF、服务器学习率 0.01、一次加权 SGD 维持已冻结配置。

没有这些后端的完整实测，时间估算是未知。批准后的第一组完整配对只用于估计剩余成本；外推超过剩余预算就暂停，不能缩短 100 窗或减少本地步。

## 已量化的缓存损失

这些是开发回放的描述，不是预测收益。

- I-Proj 正质量 committed：3569/3569 = 1.000000
- I-Proj 正质量 superseded：0/3569 = 0.000000
- I-Proj 正质量 expired：0/3569 = 0.000000
- I-Proj 正质量 endpoint_unconsumed：0/3569 = 0.000000
- I-Proj 正质量 overflow：0/3569 = 0.000000
- F1-Proj 正质量 committed：3019/3569 = 0.845895
- F1-Proj 正质量 superseded：548/3569 = 0.153544
- F1-Proj 正质量 expired：0/3569 = 0.000000
- F1-Proj 正质量 endpoint_unconsumed：0/3569 = 0.000000
- F1-Proj 正质量 overflow：2/3569 = 0.000560
- F2-Proj 正质量 committed：2525/3569 = 0.707481
- F2-Proj 正质量 superseded：1023/3569 = 0.286635
- F2-Proj 正质量 expired：0/3569 = 0.000000
- F2-Proj 正质量 endpoint_unconsumed：8/3569 = 0.002242
- F2-Proj 正质量 overflow：13/3569 = 0.003642

全队列驻留、右删失和分组质量去向见 A2_QUEUE_RESIDENCE.csv 与 A1_LOSS_BY_GROUP.csv。
用户若批准训练，同时接受 H=2 这个实验性最大等待。普通缓存可以比立即方法等得更久；等待不要求短于立即方法，也不能藏进平均值里不报。

## 成功与失败

主指标 L 是关闭 20、30、…、100 九个检查点 RMSE_mu 的等权平均。WorstGroupRMSE 先在每个检查点取组间最大，再对九个检查点平均。保存九个权重快照和尺度、特征映射。

33001 的五臂先检查接口、数据公平和实测成本。不因这一种子预测差就换种子或改 F1/F2。三个种子都完成才做判断。

在 validation 上：

- 按三 seed 平均 L，在 F1/F2 中选一个共用的 F*，两者结果都保留。
- 同口径在 I-Proj、TwoStage-Hájek、FedAvg-Window 中选 N*。不用旧主表代替。
- `gain = 1 - mean(L_F*)/mean(L_N*)` 至少 2%，且至少 2/3 的配对种子方向有利。
- F* 相对 N* 的最终 RMSE_mu 和九点平均 WorstGroupRMSE 恶化都不超过 1%。
- 正质量消息硬驻留不超过 2，版本上限不违反，终点不延期；未提交和零权重比例完整报告。
- 部署必需路径 CPU 不超过 N* 的 1.20 倍，wall 不超过 1.25 倍。新诊断费用单列，并计入硬预算。

这是探索性筛选。F* 和 N* 都由同一 validation 选择，不宣称显著，也不宣称独立确认。

- 只胜过 I、未胜过 N*：`BUFFER_NOT_COMPETITIVE_WITH_STRONG_BASELINE`
- 只有几何 D 改善：`GEOMETRY_GAIN_WITHOUT_TASK_GAIN`
- 点提升不足 2%：`FAIL_PRACTICAL_SCREEN`
- 质量通过但成本失败：`TASK_GAIN_COST_UNRESOLVED`
- 资源中断且配对未完成：`RESOURCE_BLOCKED`，不宣布科学失败

未满足时不追加种子、不换 mu、不新增评价端点、不用 S 或 P2 补救。通过后另案申请独立确认，不直接扩到十个种子。

## 预算与恢复

建议上限：2400 CPU 秒、60 分钟活动 wall，覆盖 15 条轨迹的后端核验、训练、评分、报告和失败尝试。这是申请上限，不是本轮授权，也不是成本预测。

断点必须保存模型、真实优化器、版本、客户端生成更新时的模型快照、pending 和 in-flight 更新、RNG、消费台账、评估进度和累计预算。

批准前不训练。本轮无新增训练，没有新增预测收益；五臂申请尚未执行。
