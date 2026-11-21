# B0 实施报告：conditional-bundle-v2

状态：**IMPLEMENTATION_READY_PENDING_CALIBRATION / WAITING_USER_REVIEW**。性能：**RESULTS_NOT_REVALIDATED**。

本轮依据用户的 B0 授权，使用 ccf-experiment-designer；已完整读取外部实施指令及其引用的候选规格、修订协议、旧定位/失败报告、原主实验协议和 Design/Gate 对齐报告。附件中的后续实验内容作为规格资料，不作为运行授权。

## 1. 实际完成的实现

| 位置 | 本轮实现及职责 |
|---|---|
| [schema.py](C:/Cursor/raven.mcs/src/raven_mcs/control/schema.py) | 锁定 Δ=0.1、D=4、H=8、四场景、age≤5、暖启动20、tail=2、0.02/0.20；显式 Design、合法当前快照和版本/数值检查 |
| [lifecycle.py](C:/Cursor/raven.mcs/src/raven_mcs/control/lifecycle.py) | 注册、冻结 stage1/q、物理成功/失败、准入、替代、过期、唯一消费、空关闭及非空实际更新；真实状态和预测摘要分开 |
| [predictor.py](C:/Cursor/raven.mcs/src/raven_mcs/control/predictor.py) | 竞争完成/通知失败/右删失风险表；风险集不足5不支持；在途 client/download 固定，未来联合标记保持 client/公开层/质量/下载年龄关联 |
| [planner.py](C:/Cursor/raven.mcs/src/raven_mcs/control/planner.py) | 六类首次偏移、四条共同条件场景、跨窗消费/版本/debt/过期、固定2 tail、共同网格释放积分及首动作执行 |
| [preview.py](C:/Cursor/raven.mcs/src/raven_mcs/control/preview.py) | 复用完整 RavenAggregator；校正质量→逐尝试 q→stage2 reference→debt/variance/staleness/P2；同约束纯L1 d 与实际 ell 分列 |
| [probability.py](C:/Cursor/raven.mcs/src/raven_mcs/control/probability.py) | 注册前特征、逐尝试冻结值、policy/target/P2/predictor 适用范围、成熟0/1与删失；外部估计模型读取，缺依赖返回 pending，无自动拟合 |
| [isolation.py](C:/Cursor/raven.mcs/src/raven_mcs/control/isolation.py)、[process_budget.py](C:/Cursor/raven.mcs/src/raven_mcs/control/process_budget.py) | 可终止规划进程及 Windows Job 子进程树 CPU 计量；计算与退出均在原2 CPU秒内，超时执行固定2后备，设施阻塞/非法输入仍报错 |
| [persistence.py](C:/Cursor/raven.mcs/src/raven_mcs/control/persistence.py) | 正式 manifest、独立目录、配置/目标/数据/完整源码包归属、不覆盖检查点、保存恢复及来源一致性核验 |
| [dynamic_control.py](C:/Cursor/raven.mcs/src/raven_mcs/training/dynamic_control.py) | 实际 CommonNDMF / ClientTrainer 连接；已有 Hájek SGD 入口需单独训练授权及 q；真实服务器张量应用、variance/debt/版本同步；冻结 lagged stage1 上下文和训练配置恢复 |
| [conditional_bundle.py](C:/Cursor/raven.mcs/src/raven_mcs/experiments/conditional_bundle.py) | 唯一正式会话 API：prepare / register_observations / decide / close / save / restore；无 EventTrace 回放循环或隐式训练 |
| [共享 stage1](C:/Cursor/raven.mcs/src/raven_mcs/correction/stage1.py)、[window_runner.py](C:/Cursor/raven.mcs/src/raven_mcs/training/window_runner.py) | 固定/动态路径共同质量与局部权重计算；新增 build_dynamic_control，动态拥有模型后禁止再次调用旧固定 run |
| [manifest.py](C:/Cursor/raven.mcs/src/raven_mcs/utils/manifest.py) | 禁用 Git textconv 外部处理；明确源码包范围；显式根目录必须对应本 checkout，不能借用父仓库身份 |
| [配置模板](C:/Cursor/raven.mcs/configs/control/conditional_bundle_v2.json)、[新增测试](C:/Cursor/raven.mcs/tests/control_b0) | 必须显式填写 Design 及来源的模板；隔离手工有效输入，仅测试新关键路径 |

主轨配置恒 Design=on，Gate仅诊断。测试后续窗口可更换合法估计器，不改写已注册消息的 stage1/q。主轨 on/off 实验仍须分别整段固定；代码不按数据集名自动选择。

stage1 使用窗口前已有的 target/opportunity/p 快照，公开元数据需声明 as_of；当前观测仅用于冻结本条消息。正式会话拒绝缺 p，不借用旧函数的任意0.5回退。保留论文已有 p_min、q_min、a_max、d_max 和 cap/ESS 数值约束。

## 2. 已验证的真实计算路径

最终 **23项新增关键路径 + 8项相关回归 = 31 passed**，无跳过。最后全批测试用时 27.16 秒（pytest墙钟），日志 [audited_delivery.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery.log)、JUnit [audited_delivery.xml](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/audited_delivery.xml)。语法及官方 Python3.11.9 环境检查通过，见 [final_facility-syntax.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/final_facility-syntax.log)、[final_facility-environment.log](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/final_facility-environment.log)。

完整 P2 的手工有效非恒等输入：Design ratio=[0.2,0.4,0.6,0.8]。正式注册接口采用已有 p 模型的合法 cold-start prior0.2，实际群组质量=[3,7]，窗口中外部 p 改为0.4后当前消息仍保存原值。这里的 prior 是既有 observation 模型语义，并非动态 q 校准。

P2预览实测 d=6.66133814775e-16、完整权重 ell=0.000472960717274、实际权重可行残差=1.11022302463e-16。d 的独立 SCS 值=1.20051746322e-11；另保存保守有效的 simplex 松弛对偶下界。d不替代ell，修复解不当作最优证书。日志同时保留求解器候选目标与实际归一化权重目标；本有效样例未触发修复。

实际 FullWindowRunner/CommonNDMF 后端应用预先构造张量后，模型参数、版本、variance及debt与预览计算一致；已有 ClientTrainer 已连接，SGD入口在本轮禁止，局部 optimizer steps=0。这是生产计算接口的行为证据，不是本地学习或预测表现证据。

联合支持样例实际调用多到达、跨窗和完整 P2：一步变体 CLOSE，H=8 变体 WAIT、首次偏移1。两者使用同一场景摘要。该样例仅证明机制路径确实不同，不计算总体收益。

## 3. 生命周期、隔离与恢复

下载版本合法性、晚到旧消息拒绝、较新替代、超龄5后过期、唯一消费、非空实际更新才版本+1均有行为断言。空关闭只推进窗口，保持最近释放、模型版本及debt。未成熟跨窗消息和右删失不标0，完成与消费分列。

DecisionSnapshot没有未来表、隐藏成功、未交付 stage1、更新张量、测试标签或旧U。相同当前快照在不同未来隐藏变量下动作相同；规划不修改真实状态。窗口内不能重拟合预测器/q；下窗更新后旧尝试仍使用旧冻结值。Gate/WARMUP/RESET诊断不改变 Design、实际权重或张量更新。

正式 manifest 保存、实际生产后端状态恢复、会话API磁盘恢复均通过：池、在途、消费集合、模型及下载版本、debt/variance、配置、局部优化器配置、lagged stage1、预测器、每条尝试 q/标签、随机键、最近释放、控制器计量可复原。相同确定性后缀的动作/状态、下一条注册输入一致；旧路径重复 run 被拒绝。验证数据身份明确标为隔离fixture，不冒充Traffic。

## 4. 规划开销与开发反馈

最终正常规划：2次完整P2、23次缓存命中，CPU 1.468750秒，墙钟 7.551125秒。受控超时：CPU 1.921875秒、墙钟 2.119798秒，子进程实际终止且执行 fixed_time_2。计量含子进程和监控；2 CPU秒不是仿真0.1时间单位或2墙钟秒。当前仅一个有效快照，不能外推总体后备率。

所有开发失败日志保留：Windows Job访问权限修复；Git textconv设施错误修复；sandbox临时目录重命名失败改用工作区独立临时目录；手工测试下载年龄占位期待错误改为真实非负历史lag；显式临时目录误借父仓库身份修复；原1秒退出等待改为同预算内计量退出；源码范围加入YAML后检查器误按Python解析，改为仅解析.py。均未改算法常数、放宽验收、跳过失败测试或用训练排错。

历史 whole-repository manifest **仅一次**隔离复现，60.901秒墙钟上限结束，子进程树CPU43.640625秒、监控0.359375秒，returncode124。见 [LEGACY_MANIFEST_ATTEMPT.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/LEGACY_MANIFEST_ATTEMPT.json)。没有复现到原native访问异常，不能声称全库异常已根治；全库无范围哈希路径仍未验证。本新路径保留 Git、环境、配置、数据、目标及整个源码包/控制配置归属，生产保存恢复已通过。未重复全库或历史E1_R2审计。

## 5. 未完成依赖与归属

动态 q_CALIBRATION=DEPENDENCY_PENDING。接口将 q 定义为策略下最终消费的联合概率，逐尝试注册时预测并冻结；不与旧 deadline-usable q 混用。到达、准入、替代和消费分别记录。顺序选择/正性及目标估计量推导见 [Q_CALIBRATION_PLAN.md](C:/Cursor/raven.mcs/ccf-review-report/conditional_bundle_b0_20261012_223821/Q_CALIBRATION_PLAN.md)；校准与可识别性都未获得证据，不继承风险保证。

事件源适配的公共目录/μ、公开资源时间可用性、真实工作载荷与服务时长关系、概率数据跨运行时间命名空间仍须在下一阶段先核验。已有独立接口允许外部提供窗口前成熟估计器；本轮没有拟合真实p/q或服务核，也没有实现自动批准/自动恢复队列。

完整 FedBuff / 指定FADAS及其优化器、输入/模型适配、成本均未在新系统复现；count-trigger不是这些完整外部方法。旧v1与旧基线只可按原身份对照，不能填新版主表。检测收益、任务不退步、预测改善三个结果均未获得。

历史保护清单52文件内容未变，见 [preservation-final_facility.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/preservation-final_facility.json)。旧STOP、P0、准备报告、论文、归档失败结果未覆盖。缓存处置：原始数据、合法划分与公共目录可在来源/时间核验后保留；Design/p依赖的stage1只有逐注册快照完全相同时才可考虑复用；旧U/tau/q、消费/版本、reference/debt/P2、训练位移、模型与预测全部隔离并按新策略重算。不得直接复用旧全轨迹或重标112条历史训练。简单预测器仅在相同任务/单位/评价权重下可重评分，当前未核验可直接比较。

## 6. 预算与交付状态

进程树/监控实测合计 349.734375 CPU秒；交互读写、早期小设施尝试及文档生成预留记账300秒（非实测）。保守本轮 649.734375 秒=0.180482 CPU设备小时，限7200秒。前轮准备记账180.078125秒；目前合计 0.230503/8小时，余 7.769497小时。详情 [BUDGET.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/BUDGET.json)。50–82人时是旧设计估计，不是本轮实测人员工作量；当前未测量人时。

训练0、随机合成控制回放0、真实控制回放0、正式确认0、旧队列恢复0。确定性fixture不计入600轨迹，不进入论文性能表。

Markdown交付仅在本文件夹；实际代码在src/configs/tests/scripts，JSON、日志、JUnit和检查点在独立results目录。机器状态 [METHOD_IDENTITY.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/METHOD_IDENTITY.json)、[B0_STATE.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/B0_STATE.json)，逐测试证据 [NEW_PATH_TEST_RESULTS.json](C:/Cursor/raven.mcs/results_conditional_bundle_b0_20261012_223821/NEW_PATH_TEST_RESULTS.json)。下一批的具体申请见 [NEXT_STAGE_READINESS.md](C:/Cursor/raven.mcs/ccf-review-report/conditional_bundle_b0_20261012_223821/NEXT_STAGE_READINESS.md)。独立模块验收完成，完整 IMPLEMENTATION_ALIGNED 未授予；等待用户批准校准、修订或终止。
