# 方法、对手与共享契约

抽样性质由 `run_p0_audit.py` 在至多 5 个客户端上枚举。结果见 `SAMPLING_CHECKS.json`。这里不把它写成预测结论。

## 目标与配额

四区域 `mu_g=0.25`。`a_j=mu_g*n_j/N_g`。缺组不重新归一化，缺组质量累加后写入 `missing_target_mass`，该组贡献为零。

`K` 是当日合法客户端数。`k=ceil(K/4)`；`K=0` 时 `k=0`；`K=1` 时全选。`k>=G_present` 时每个现有组先得 1 个名额，其余名额给 `k*mu_g/sum_present(mu)-k_g` 最大且未饱和的组，并列按 region0、region1、region2、region3。`k<G_present` 时，区域配额加组内 Uniform、区域配额加组内质量 PPS、候选联合策略这三个配额臂回退到全局目标质量 PPS。该日保留，并且不计入可选择性通过日。43 日里没有出现这个回退。

组内 `w_j=(n_j/N_g)*h_j`。`p_tilde_j=min(1, lambda_g*w_j)` 且和为 `k_g`。`p_j=0.2*k_g/K_g+0.8*p_tilde_j`。抽样是固定样本量的系统抽样，一阶包含概率就是这个 `p_j`。普通加权无放回的输入权重不是最终包含概率。

主聚合：

`theta_next = theta + eta_server * sum_j I_j * a_j * delta_j / p_j`

不附加 Hájek 归一化、ESS 投影或 P2。`k=0` 时所有 `p_j=0`，不计算逆概率项。

## 七个比较对象

1. 全局 Uniform：精确均匀包含概率 `k/K`，固定抽取 k 个。
2. 全局目标质量 PPS：分数 `a_j`。
3. 区域配额加组内 Uniform：组内包含概率 `k_g/K_g`。
4. 区域配额加组内质量 PPS：分数 `n_j/N_g`。保留，不从对照中删除。
5. 全局历史幅度 PPS：分数 `h_j`。
6. 候选联合策略：组内分数 `(n_j/N_g)*h_j`。它不是未经修改的完整 RAVEN。
7. 全库存目标更新：`I_j=1`、`p_j=1`，和为 `sum_j a_j*delta_j`。

所有 PPS 臂共用 capped PPS、0.2 探索和同一系统抽样，只替换分数和是否分层。Uniform 不用 0.2 混合。

`h_j` 只来自本臂已经收到的 `norm(delta_j)/sqrt(d)`。第一条有效历史直接作为 EMA。之后 EMA 系数 0.2，7 日过期，截断到组先验的 [0.5, 2]。组先验是该区域 7 日内有效客户端 EMA 的中位数，每个客户端计一次；没有历史时先验为 1，下界 `1e-12`。历史在本轮选择之后才更新。冷启动时 `h_j` 相同，候选联合策略和组内质量 PPS 的包含概率相同。这是预期行为。1825 个合法客户端日里，1658 个在此前 7 日内有过合法出现，比例 0.9084931506849315，重复间隔中位数 1 日。这只是历史信息的上界，不是已经收到更新的比例。

## 共享训练契约

| 项 | 取值 | 来源 |
|---|---|---|
| 骨干 | Common-NDMF，空间嵌入 32，时间支路 32，融合宽 128，头 128→64→32→1，dropout 0.1，无客户端嵌入 | `common_ndmf.py` 第 13–47 行 |
| 词表 | 预热 train 网格 118 个。未知网格拒绝，不映射到下标 0 | 本次计数；现有 `processed_dataset.py` 第 104–105 行使用全部 atomic 网格 348 个，含后续 split |
| 参数个数 d | 33121。全部 atomic 词表对应 40481，与旧投影路线记录过的更新宽度一致，但那一口径依赖后续网格，本协议不用 | 由模块定义清点，没有实例化模型 |
| dtype | float32 | PyTorch `nn.Linear` / `nn.Embedding` 默认 |
| 初始化 | `deterministic_common_ndmf`：`torch.manual_seed` 后构造模型。各臂复制同一 `state_dict`，不共享可变存储。具体整数种子留到 P1 登记，过程本身没有歧义 | `common_ndmf.py` 第 85–92 行 |
| 标准化 | 只用 1722 条预热 train 目标。均值 7.235721204740506，总体标准差 2.5343724212040586。不调用 `apply_train_zscore_standardization`，因为它拟合全部 train 标签 | `processed_dataset.py` 第 115–118 行是旧路径 |
| 趋势分母 | 决策日结束时已经出现的时间槽数。不用全表最大 `time_index` | 旧路径在 `window_runner.py` 第 900 行 |
| 本地目标 | 该客户端当日合法记录上的样本均值平方误差 | 新契约。旧 `client.py` 第 90 行调用 `local_hajek_loss` |
| 本地优化 | 手写 SGD，学习率 0.01 | `ClientTrainer` 第 28 行；`build_full_runner` 第 1504 行 |
| 本地步数 | 2 | `scripts/run_joint_ou_cs_p2.py` 第 75 行。类默认值 5 不是这条数据的入口 |
| 批 | 该客户端当日全部合法记录一次前向。没有 DataLoader，没有 `drop_last`，没有放回抽样。至少 1 条才构成批次 | `client.py` 第 55–89 行 |
| 服务器步长 | 0.01 | `FullWindowRunner.eta`，`window_runner.py` 第 139 行；measured-O 入口没有覆盖它 |
| 随机流 | 选择用独立的 NumPy 生成器。本地 dropout 和初始化使用另一条随机流 | 新契约，本次未执行 |

最小适配位置是日后的独立驱动：不调用旧事件 runner，不调用 `local_hajek_loss`，词表和标准化只使用预热截止前的数据。本次没有修改生产代码。
