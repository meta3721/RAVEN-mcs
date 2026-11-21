# 实现、行为验收与结果归属

状态：REVISION_IMPLEMENTED_NOT_PERFORMANCE_VALIDATED；WAITING_USER_REVIEW。

## 新旧实质差异

| 项目 | 原 conditional-bundle-v2 | RE-interval-v3 |
|---|---|---|
| q对象 | 原策略联合消费概率；旧采集使用诊断先验 | I(100)在 H、R=1、E=1下的条件消费概率；策略身份另立 |
| 历史机会 | 机会时钟与完成标记分别处理；年龄取完成标记 | 从全部注册联合取 R/client/资源/age/时钟/来源 |
| R=0 / E=0 | 原路径仍可能查询不适用的服务/质量预测 | 记录条件外/结构零；不进入逆概率；保留原物理工作 |
| 无标记/尾部不足 | 任一不支持可导致整体预测后备 | 显式未知及作用时刻，保留确定前缀，后缀全范围 |
| 首动作选择 | 比较点评分及offset | 正offset归入WAIT，组内上下界各取最小值；充分分离才证明动作 |
| 唯一合法首动作 | 易与方法激活混计 | RULE_FORCED，proven=false |
| 保存恢复 | v2身份与原闭包 | 新方法、q事件和新源码闭包；拒绝旧检查点 |

完整 P2、μ、评分系数、H8、Δ0.1、D4、四场景、age5、risk≥5、minimum_clients=3、fixed_time_2及2 CPU秒上限保持不变。方法是粗区间后缀传播，没有新增更强差值分析、跨client填补或门槛调整。

## 实际代码

全部新方法文件位于 `C:/Cursor/raven.mcs/src/raven_mcs_re_interval/`，没有修改原 `src/raven_mcs/`。

- `schema.py`：独立方法身份；outside_R、structural_zero、zero_support与pending的值/分母约束。
- `probability.py`、`calibration_identity.py`：限定域q事件、配置与学习/服务/终点适用身份；本批不拟合。
- `lifecycle.py`：全部注册机会日志、E=0训练接口保留、物理完成与消费资格分离、注册时q冻结。
- `predictor.py`：全部注册的联合机会重采样；条件服务核；缺标记和尾部未知；跨运行时钟拒绝隐式混用。
- `planner.py`：原完整P2的确定前缀，浮点评分外扩，四场景等权区间，CLOSE/WAIT分组、严格1e−7判据及后备。
- `preview.py`、`stage1.py`：保持原完整实现，仅导入新版本数据类型；实际P2继续调用同一原聚合器。
- `isolation.py`、`interval_isolation.py`、`worker.py`：正式决策入口、只计算一个决策的子进程及全树计量。使用已经修复的 `scripts/windows_cpu_meter.py`，创建时挂起、入Job后才执行，覆盖venv启动器的子解释器。
- `persistence.py`：独占创建检查点；保存方法、I(100)条件域和计算源码闭包；恢复校验后使用真实runner状态。
- `__init__.py`：新身份常量。

定向检查脚本：`scripts/validate_re_interval_revision.py`。S2冻结脚本 `scripts/revision_feasibility_s2.py` 未改动。预算、版本分离准备及最终核验脚本分别为 `revision_feasibility_budget.py`、`prepare_interval_revision_package.py`、`finalize_re_interval_revision.py`。

## 三个定向检查

### 1. R/E、实际消息与保存恢复：PASS

证据：原始目录中的 `S3_RE_PASS_clock_final.json`、`S3_new_identity_checkpoint_clock_final.json`。

同一确定性runner到版本6后登记三类记录：R0、注册age6的E0、R1/E1。分别得到outside_R零、structural_zero零及隔离正q。前两者调用逆概率接口明确拒绝；域内明确零支持单独标记zero_support，也不能通过q_min变成正数。

E0与合格记录都到达原后端训练入口；本批用接口记录器断言调用，实际优化器步数0。R0保留工作/尝试记录，按原无观测语义不启动训练。E0物理完成被记录，消费标签保持0，真实P2预览只包含合格key。这里验证的是调用和账的保留，不声称已执行真实局部训练。

下一窗口切换q模型后旧记录q完全不变。JSON保存恢复后的规范化完整状态一致；旧v2检查点被拒绝。全部注册的R/age日志包含三类记录；条件服务历史仅使用适用记录。机会预测不对R0/E0查询条件核。若未声明资源无共享竞争，排除记录的资源效应转为未知；跨运行机会时钟明确拒绝。

原生产者 `src/raven_mcs/experiments/calibration_first.py:CausalTrafficProducer.register_current` 按固定公共登记时钟、每条独立服务抽样与实测本地CPU下界产生完成通知，没有共享服务队列。本修订没有更改该生产者。`exogenous_no_shared_contention`仅适用于这种已核对模型；其他资源模型保持未知。本批没有将该生产者绑定到新真实采集入口。

### 2. 未知与首动作：PASS

证据：`S2_late_unknown.json`、`S2_early_unknown.json`；最终运行证据 `S3_unknown_PASS_final.json`、`S3_late_unknown_decision_final.json`、`S3_early_unknown_decision_final.json`。

复用冻结的18个完整分支分数和状态轨迹，覆盖缺标记、尾部未决、同client较新替代及后续模型版本/debt。S3没有重选用例或移动未知时点。晚期场景每个计划均保留68/80格，四场景均保留；早期均为1/80。区间包含所有已枚举分支。

晚期 WAIT：[0.08924998709914835,0.2722506657846237]；CLOSE：[0.32356917314565986,0.5065698518311355]。严格分离成立，见证offset0.1，实际首动作与fixed_time_2不同。早期区间重叠，记录UNKNOWN_FIXED_TIME_2，动作CLOSE。只有WAIT候选时返回RULE_FORCED，不计区间证明。

两次真实隔离控制器调用均保留2秒上限，包含启动、真实P2和退出；CPU分别1.375和1.328125秒。没有提前缓存一次实际求解供限时调用使用；缓存只在一次决策内部共享。

### 3. 全支持、完整P2与应用：PASS

证据：`S3_supported_PASS_final.json`、`S3_supported_decision_final.json`。

同一冻结状态的已知完成和完整公共空未来目录，配合合法同client历史标记与足够风险集，经过正式预测器产生四个无未知场景。另在同一用例移除尾部风险单元，预测器准确记录尾部未知；这只是接口断言，不增加回放轨迹。

全支持五个offset的区间包含旧完整v2路径同输入得分，区间宽度小于1e−10；首个WAIT得分约0.105。实际预览保持原runner完整状态，P2残差1.1102230246251565e−16≤1e−7；预览权重约各1/4，真实apply后模型为[0.9980000000000001,1.9960000000000002,2.9939999999999998]，与使用预览权重对实际后端更新的计算一致。可行域并非单点，最优权重在这个对称用例恰为均匀，不能据此声称权重优化收益。

完整支持路径CPU1.265625秒、墙钟1.549351秒，P2求解4次、缓存命中21次。三条路径的当前L1双求解也包含在CPU中。

## 开发修复记录与适用限制

首次R/E检查在JSON恢复后的Python对象直接比较处失败。JSON把嵌套元组变成列表；改为比较规范化序列化完整状态，后续通过。原失败日志、JSON、检查点和计费均保留，没有删除/跳过断言或减少被比较字段。

数值积分在S3增加长度相关浮点外扩，遵循事前证明，不收紧区间。后续补齐了域内零支持、检查点源码身份和跨运行时钟拒绝检查。没有改变评分、用例或科学门槛。

超时设施沿用上一批已验收的挂起启动Job/PID计量；本批正常决策再次通过独立核对，没有重复旧CPU燃烧验收。新控制器保留真实CPU超时后的fixed_time_2分支；本批三个决策未超时，不能称为新超时压力实验。

证明域限定为原43客户端、172群组、合法0.1全局关闭/决策网格、T100和完整P2数值约束。动态共享资源模型和跨运行历史迁移未被实现为已支持预测，均需显式依据。新策略的概率校准仍缺失；隔离0.5输入不能进入生产，诊断先验只允许明确的calibration_only身份。

## 入口

新版调用 `raven_mcs_re_interval.lifecycle.DynamicWindowRunner`、`raven_mcs_re_interval.isolation.IsolatedController.decide` 以及 `raven_mcs_re_interval.persistence.save_checkpoint/restore_checkpoint`。正常decide不传手工场景；`isolated_scenarios`仅在isolated_test=true时接受。子进程入口 `python -m raven_mcs_re_interval.worker INPUT_JSON OUTPUT_JSON` 只处理一个已有快照，无数据采集与训练调度。

旧版仍从 `raven_mcs.control` 与原 `scripts/run_calibration_first.py` 使用原身份。本批没有运行旧入口，也没有提供自动遍历种子的新入口。下一次真实开发需单独批准并绑定生产者、完整学习适用身份、公共资源声明及新run_id。
