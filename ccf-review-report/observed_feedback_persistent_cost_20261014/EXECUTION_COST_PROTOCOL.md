# OF-v1常驻worker费用协议（运行前冻结）

日期2026-10-14。执行来源为用户的90 CPU秒常驻worker修订指令，使用ccf-experiment-designer。全批90 CPU秒，审查/编辑/交付保守预留30秒，其实际未逐项计量记UNKNOWN；其余启动、请求、输出、父监视、失败和退出按互斥Job+driver计费。SGD/GPU/q拟合/新真实或随机轨迹/控制回放均0，不实施采集入口。

旧完整冷失败2.551250 CPU秒保持FAIL；这份协议新定义一次性初始化与在线请求的工程验收，不能回写旧P3。B/θ/κ/ν/mu/Design、P2目标/求解精度/原约束、消息/概率消费定义均不改。原FROZEN_INPUT复制原字节，hash仍c880a4361ea0ec8fa3fc65b30cd9932347181c8591d39c6f003e829d5c695e5b；数学fixture不称真实Traffic状态。

## 三段与互斥归属

INITIALIZATION：根基线0，从Job创建（含venv解释器启动器、测试父进程及其新worker）到父进程完整接收/解析READY后的新根样本，含依赖/求解器模块导入、原固定输入解析、stage1及条件公共历史构造、配置校验和常驻资源。加启动器进入根meter前的bootstrap CPU。帽6 CPU秒。模块加载允许，READY前solve_p2次数与numeric cache必须0；禁止实际P2、参考解或提前权重缓存。fixture中43次registration_features历史构造是旧输入测试的附加溯源重建，分段实测但不说成每次控制器必需；当前不改变此构造，避免擅改固定输入。

ONLINE_REQUEST：父进程拿到有效固定请求后，以更新过的根begin样本建立边界，然后进行请求JSON编码/写管道；worker读取解析、身份/健康/根预算检查、合法snapshot、原必要P2或真实数值缓存、B/elapsed重新判断和最新绑定核验、完整必要返回编码/传输；父进程完整读取/解析响应，随后等该完成时刻之后的新根end样本。两次分别≤2 CPU秒，单独记录父/worker进程CPU和墙钟；不以内部Controller时间替代根时间。

FINALIZATION：完整审计只在A/B结束或失败后输出一次，包含所有beta/masses/M/alpha/omega、原solver日志/残差/目标各项；随后父进程比旧数值、验证输入/状态，关闭worker与自身，根meter最终回收。初始化及A/B样本段之外全部费用（采样桥/阶段间间隙、审计、检查、关闭、退出和最终monitor）由整次互斥账减已列的实际样本差归入remaining_root_CPU，不消失。各段+.02的验收上界可能保守重叠，不作为整批加法账；整批只用实际tree+driver。

父/worker和根meter使用同机Windows perf_counter单调时钟，READY/请求完成时间与ROOT_BUDGET_LIVE.wall_stamp桥接。begin/end均等目标时刻+.01后的新根样本；沿前批方法，上界=max(root差+.02，父CPU差+worker保留PID CPU差+互斥外层monitor差+.02)。初始化另计bootstrap。PID只做提高下界/量化复核，不再加入总账；before→after根差一段只归属一次。禁止移动online边界至求解之后。

## 必要返回和完整审计

旧Decision.to_dict/asdict与numeric/solver日志重复复制完整M；控制器实际返回不可变BoundReleasePreview，提交所需fields仍须在同worker保留。新管道返回action/reason/B/components、最新fingerprint/dependency_hash/keys、实际alpha/M/omega/ell/age与P2/cache计数，M不删且只传一次；worker同时保留原完整BoundReleasePreview及其beta/masses/solver_json。删去的在线重复内容只有solver日志中的另一份M/beta等审计副本和完整历史复写，它们不参加apply_release的绑定/实际权重/M/omega核验，FINALIZATION仍完整保存。没有预存动作或新简化求解器，没有模型提交接口授权。

局部计时仅包裹原methods.solve_p2 callable，原参数、精度、输入和返回不修改；预加载只导入固定模块。真实模型、数据、优化器、动态注册/通知处理未加载或执行，本次数学worker启动费用不作完整训练入口启动承诺。未来注册/当前状态更新须另列根费，不能借初始化吞掉全程在线事件费用。

## 固定核验

只启动同一个新常驻worker。A为READY后首次数值P2，cache为空，原RavenAggregator/CLARABEL。B输入/时钟保持完全相同，再运行同一controller：必须P2=0/cache=1、复用同numeric但新建当前BoundReleasePreview；它只验复用，不验真实激活。每次都重新计算动作，state fingerprint保持，禁止apply/model更新/新状态轨迹。

数值有限、实际alpha原残差≤1e−7；alpha/omega/ell/age与旧原结果按既有绝对1e−7、rtol0比较，不能事后加宽。A P2/cache/solver call为1/0/1，B为0/1/0。初始化≤6，A/B各≤2，全部根审计/费用归属有效才标PERSISTENT_REQUEST_COST_CHECK_PASSED。有效A的数值/性能失败立即停依赖核验、不用快B遮盖；初始化失败也不进入A。只有未形成有效A的普通工程错误可在原90秒内修复，保留失败账，不按线程/状态搜索到通过。

该文件在A/B运行前冻结；旧输入和旧失败保持，机器协议/source hash在FROZEN_EXECUTION.json。本轮通过也只支持另提一条诊断采集申请，结束WAITING_USER_REVIEW。
