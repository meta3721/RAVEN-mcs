# RAVEN-MCS 方法定义卡

日期：2026-10-12。依据：本轮明确授权的默认方向及规范源文件；历史文件中的执行指令不构成本轮授权。

## 1. Design

- 变量：窗口配置 `D_t ∈ {on, off}`，对应 `eq:design_factor`。
- 确定时间：窗口开启前记录，窗口内保持不变，覆盖本地损失、正质量活跃集、参考重构和窗口关闭聚合。
- on：机会因子为 `pi_tar / max(pi_opp_hat, pi_min)`；off：观测对上的机会因子为 1，包括零目标质量对。
- 切换该因子会改变本地权重及后续活跃集；不是只替换服务器的一个权重向量。
- Obs、Use、P2、方差、陈旧项及 debt 的算法步骤保持相同，数值状态可以因训练分叉而不同。Gate=0 不表示这些部分关闭。

## 2. coverage Gate

- 输入：合法窗口前历史 `F_{t-}`、公共目标和状态描述、冻结预测器快照、已完成历史窗口的同块校准分数、前一完成窗口的失覆盖标志。
- 时点：窗口前计算 `C_hat_t`、校准分位数及 `C_LCB_t`；输出 `Gate_t = 1{C_LCB_t ≥ 0.05}`，WARMUP/RESET 输出 off。
- 输出还包括状态、块/快照标识、样本数及 LCB。当前窗口的真实 `C_t` 在完成后参与有效性审计和后续状态更新。
- 默认论文方法中只诊断覆盖，不写回 `D_t`。稳定区域的交换性条件、n≥19 和严格历史分数仍适用；算法状态本身不证明交换性。

## 3. target-support gate

- 保留 `eq:design_gate`：`rho_r = n_zero_r / n_r`，`D_r=on iff rho_r=0`。此处 r 是实验块，区别于窗口配置 `D_t`。
- 本轮纠正计数对象：SensorScope/U-Air 的已核对来源是全训练划分的唯一原子目录，而非当前窗口已交付更新。脚本 `scripts/compute_scd_phi.py::phi_train_unit` 与 `post_review/C2_scd_phi/tables/SCD_PHI.csv` 支持该对象，0/10285、2016/5688 原数值不变。
- 用途：离线零目标支持检查，规则输出与展示的固定设置相符。只有目录、client/stratum 映射和目标 lookup 在决策前确已可得，才能据此预配置后续窗口。
- 当前交付集在交付后才能获知，不能用于同窗口开启前的决定。无 Y/RMSE 不等于时间上可得。
- 不以此检查替代 A1/A5 正性与可识别性假设。不同块的 lookup 对象仍分开。
- `eq:design_switch` 保留为已测端点的事后权衡图，不是同次评测中的第二个在线开关步骤。

## 4. Design-on/off 实验臂

固定 on/off 分别指整条运行的全部窗口均使用相应因子。消融的 full 起点是两数据集上的固定 Design-on；移除 Design 得到固定 off，不从 U-Air 主比较所展示的 off 臂再移除一次。

历史 `raven` / `raven_wo_design` 是这些臂的结果来源标识。不能因当前注册表给 `raven_mcs` 加了 formal 标记，就把它们解释为 coverage-controlled 的训练。

## 5. 方法对应

| 对象 | Design 控制 | 本轮归属 |
|---|---|---|
| 论文 RAVEN-MCS | 窗口前显式配置；coverage Gate 只诊断 | 本轮默认方法定义 |
| RAVEN-Design / RAVEN-NoDesign | 整条运行固定 on/off | 配置实验臂；需按保存源版本核对全部组件 |
| 历史 E3 `raven`、E4 `raven_wo_design` | 历史固定因子路径 | 历史固定臂证据，不自动等于当前生产实现 |
| 当前代码 `raven_mcs` / formal aliases | `aggregate_coverage`，Design_t:=Gate_t | coverage-controlled 实现，仍待同步 |
| 覆盖压力审计 candidate | 保存记录 Design_t=Gate_t | 只引用其证书审计量，不重命名为固定臂结果 |
| 重建 Uniform 缓存及开发训练 | 继承当前 aggregate_coverage 损失路径 | 开发诊断，不是 configured-Design 的新增收益证据 |

作者尚需确认目录在决策前的可得时间、空目录的处理，以及默认部署是否采用该支持规则。未自行引入滞后 rho、当前窗口重算、自动 RESET 关闭 Design 或新目标公式。
