# METHOD_SPEC — P0 未冻结候选

本轮主对象是 `reachability_stop/<版本待定>`；不是 coverage Gate，也不是旧离线可达性指标。底层方法 `raven_mcs/configured-design-v1`、主轨 Design=on、Gate仅诊断，沿用已完成226项专项证据，不重复小样例。

## 当前可执行资产与缺口

`src/raven_mcs/metrics/reachability_optimization.py::solve_epsilon_reach` 接受完整窗口组成矩阵、mu、eta、alpha_max、e_min和容差；对每窗非负、cap、simplex权重最小化累计偏差的L2范数，返回离线最优值和alpha。实际源码没有把e_min加入约束，也没有STOP/WAIT动作、到达预测、跨窗消息池、消费/过期或策略相关q。这不能替代协议要求的当前 `0.5*L1` 距离和相同可行集合。空块返回0也不是协议启动前空释放距离1的评分接口。此处是资产定位，未执行几何实验或更改旧指标。

现有资产伪代码：

```text
接收完整block的M_r、mu、eta_r
为每窗设置alpha >= 0、sum(alpha)=1、alpha <= cap
最小化 ||sum_r eta_r*(M_r*alpha_r-mu)||_2 / sum_r eta_r
返回solver状态、最优值和alpha
```

新候选必需的状态、合法信息、预测器、代价、动作、截止与跨窗保留规则：**尚无唯一可核验定义**。不编造旧v1的伪代码，不把配置on的聚合器重命名成新停止方法。

`FullWindowRunner` 按已给window_id执行，并读取EventTrace最终U和downloaded_version。它的完整训练/P2资产可继续使用，但尚不能直接冒充协议的动态系统：新控制器必须产生本策略的关闭、版本、交付与消费，Use/IPW还需对应完整选择过程。

## 冻结状态与主张

方法实质差异、算法版本、截止单位、总T、预测器拟合预算、controller CPU预算、消息生命周期、policy-specific q接口均未冻结。当前不承诺统计证书、时间一致保证、Bellman最优性或预测改善。C1/C2/C3均未形成新证据。

下一步先提供当前候选源码与入口，或批准独立新版本定义；P0未PASS之前不启动P1。
