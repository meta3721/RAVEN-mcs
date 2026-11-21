# 方法、对手与共享契约

本文件记录协议规格和代码里已经能定位的接口。抽样器没有运行。参数个数没有清点。

## 选择与聚合

四区域 `mu_g=0.25`。`a_j=mu_g*n_j/N_g`。缺组日不把 mu 重新归一化，缺组质量记下来，贡献为零。

`k=ceil(K/4)`。`k>=G_present` 时，现有组先各得 1 个名额，其余名额给 `k*mu_g/sum_present(mu)-k_g` 最大且未饱和的组；并列用 region0、region1、region2、region3 的顺序。`K=0` 跳过，`K=1` 全选。`k<G_present` 时，三个配额臂回退到全局目标质量 PPS，该日仍保留，并且不算通过可选择性门槛。

组内 `w_j=(n_j/N_g)*h_j`，再做 capped PPS 和 0.2 探索。`p_j` 必须是固定样本量抽样的一阶包含概率。主聚合是

`theta_next=theta+eta_server*sum_j I_j*a_j*delta_j/p_j`。

不附加 Hájek 归一化、ESS 投影或 P2。

比较臂是：全局 Uniform、全局目标质量 PPS、区域配额加组内 Uniform、区域配额加组内质量 PPS、全局历史幅度 PPS、候选联合策略、全库存目标更新。区域配额加组内质量 PPS 保留。候选不是未经修改的完整 RAVEN。

`h_j` 只来自本臂已收到的 `norm(delta_j)/sqrt(d)`。EMA 系数 0.2，7 日过期，截断到组先验的 [0.5, 2]，无历史时先验为 1，正值下界 `1e-12`。历史在本轮选择之后才更新。

## 从代码读到的契约

| 项 | 状态 | 位置 |
|---|---|---|
| 骨干 | Common-NDMF：空间嵌入 32，时间支路输出 32，融合宽 128，头为 128 到 64 到 32 到 1 | `src/raven_mcs/models/common_ndmf.py` 第 13–39 行 |
| 参数维数 d | UNKNOWN。没有清点，不能把嵌入宽度当成总参数量 | 同上 |
| 服务器 eta、本地学习率、本地步数 | UNKNOWN。历史 measured-O 运行用过 0.01、0.01 和 2，类默认局部步数是 5。新协议还没有单独冻结其中哪一个 | `ClientTrainer` 调用参数 |
| 本地批 | 现有 `train_step` 把该客户端全部观测放进一次前向，没有 DataLoader，也没有 `drop_last` | `src/raven_mcs/training/client.py` 第 70–96 行 |
| 本地损失 | 现有路径调用 `local_hajek_loss`。新协议要求已观测库存上的样本均值，不自动沿用 Obs/Use 逆概率权重 | 同文件第 90 行 |
| 初始化 | 历史投影路线要求服务器参数独立克隆。新协议同样要求克隆，但本次没有执行 | 协议规格 |
| 预热 | `TemporalSplitConfig` 把训练时间槽的前 `ceil(20%)` 标成 `is_warmup`，仍属于 train | `src/raven_mcs/data/split.py` 第 18–22、87–89 行 |
| 划分 | 默认按唯一时间槽 60/20/20。换 seed 或重切旧记录不能当成新的独立证据 | 同文件第 44–48 行 |

最小适配位置是日后的独立驱动：不要调用旧事件 runner，也不要调用 `local_hajek_loss`。被选客户端只在自己的 O=1 合法记录上计算样本均值损失。这个契约还没有用数据验证张量形状。

## 未确定项

本地步数、服务器步长、精确参数维数和 scaler 是否只使用预热截止前的统计，都是 UNKNOWN。这些空缺会改变更新定义和嵌入索引。它们本应阻止 `PASS_P0_AWAIT_REVIEW`，但本次主状态是资源中断，不是把这些空缺当成已经失败的数值测试。
