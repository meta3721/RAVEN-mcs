# 唯一候选规格：observed-feedback-v1

规格状态：SPEC_READY_FOR_LIMITED_IMPLEMENTATION；运行状态：WAITING_USER_REVIEW。本文件定义下一次实现的唯一候选，当前没有实现生产控制器。方法标识固定为`reachability_stop/observed-feedback-v1`，简称OF-v1；它不是旧v3、动作差值证书或旧RAVEN性能结果的新名称。

## 1. 对象、依赖与冻结配置

对象是部署公共目标μ驱动的跨窗口经验释放控制。控制输出只有CLOSE/WAIT，输入只有已可见的实际状态；没有未来场景、服务/质量预测、隐藏完成表、训练梯度或测试标签输入。完整configured-Design P2和真实学习后端仍是共同底层。

沿用Δ=0.1、T=100、最长窗口D=4、age_max=5、非强制释放至少3个不同client，t≤20共同fixed_time_1暖启动。P2参数固定为λ_group=1、λ_beta=1、λ_variance=0.1、λ_staleness=0.1、alpha_max=0.5、e_min=3、server_eta=0.01、max_server_learning_rate=1、d_max=10、q_min=0.05、v_floor=1e−4；小K沿用cap=max(0.5,1/K)、ESS=min(3,K)。不放松概率裁剪、数值有效性或聚合约束。

Design在窗口打开前显式冻结，on使用原lagged opportunity/design ratio，off因子1；比较运行全程固定on/off，coverage Gate只诊断，WARMUP/RESET不切换Design。主后续轨道预配置Design=on；另一个Design配置需单列身份。消息注册的p/q与校正摘要不因关窗重写。

新控制参数一次事前固定，不做开发搜索：释放收益阈值θ=0.02，debt反馈强度κ=0.10，耐心强度ν=0.20。θ表示启动非强制释放所需的代理改善幅度；κ使归一化debt的最大贡献约0.10；ν使无事件时每格增加0.20×0.1/4=0.005的释放压力。代理陈旧性系数a_w=0.02沿用已有定义。耐心项是新控制规则的一部分，虽与旧J的等待系数数值相同，也不称为旧方法工程修复。θ不是性能验收门槛，κ不是风险保证。

旧H8、四场景、minimum_risk=5属于未来经验预测模块；新控制不调用该模块，不能声称该模块已通过或其支持缺口消失。已有risk计数和概率支持审计可继续记录，不能把5个观测当成校准证明。旧辅助J保留原系数，单独评价。原G/W、RMSE及独立确认门槛保留。

## 2. 状态与可见输入

状态为(t,o,v,window_id,revision,P,F,A,C,Q,V,L,config,q_model_identity,clock_namespace)：

- t为当前时刻，o为当前窗口打开时刻，v为实际模型版本；P为每client最多一条合法实际到达未消费消息，F为已注册未终止尝试的公开头，A为全量尝试账，C为已消费key集合。
- Q为原非负跨窗口目标debt；V为已完成模型更新形成的方差估计。L保存最近一次非空实际释放的time、omega、ell、age、duration；旧ReleaseSummary只有标量，新增omega须由该次实际preview保存，不从未来或最终模型反推。
- 初始化t=o=0、v=0、Q=0、P/F/C为空、L为空、V按共同底层初始化。模型初始化、学习配置和概率适用身份独立冻结；本批不选择或训练模型。
- μ、目标目录及Design配置在运行前可见；注册header在注册时可见；完成/失败只在通知时可见；完成摘要、p/q、下载版本和质量只有实际交付后进入P2输入。未完成消息的私有stage1或真实未来服务表不能进入控制快照。Q/V/L只来自过去实际提交。

R=1表示该次实际观测/校正质量非空；E=1表示注册时v−downloaded_version≤5。注册时固定q=P(I(100)=1|H_reg,R=1,E=1,policy,learning,service,endpoint)，其中I是该尝试在τ≤100至少一次实际服务器消费；注册区间[0,100)。没有R或E的记录仍记物理工作，但不进入逆概率分母。年龄单调超过5、被较新消息替代、明确失败、已消费或完成时无合法质量的消息不进入当前P。

新q适用身份必须包含OF-v1所有控制参数、完整P2/Design/目标、学习模型/优化器/学习率/局部步数/样本协议/缩放器/初始模型、观测及stage1模型、公开资源/服务参数、T=100及运行时钟命名空间。历史反馈影响消费选择，注册特征设计须包含当时Q、L、窗口elapsed、P/F的合法摘要或具有充分性依据的编码；不能自动沿用旧仅age/count特征。q仍是待补外部依赖，不在本规格里伪造拟合值。它可使用过去合法信息，但值必须在注册时冻结；新概率模型只在获准的下一窗口边界更新，旧消息继续持有原q。

完整T100时尚未消费的尝试在I(100)上终止为0，物理服务本身仍可能删失；预算前缀右删失，不标0。各run的逻辑时间不能跨run直接比较；使用run_id、origin_utc和controlled_service_unit，同一run恢复原命名空间，跨run迁移另立发布桥。去掉未来预测不获得q正性、无偏性或校准保证。诊断先验只允许另获批准的calibration_only路径；本批没有使用先验或拟合。

## 3. 当前完整P2与反馈量

对合法非空P，以原完整P2求实际使用的a，保留beta、mass、M、方差、staleness、debt、μ及所有可行约束。定义：

    omega_t = M_t a_t
    ell_t = 0.5 ||omega_t − mu||_1
    age_t = Σ_j a_t,j (v − downloaded_version_j)/5
    c_t = ell_t + 0.02 age_t
    c_minus = L.ell + 0.02 L.age，若L为空则为1
    Qhat = Q / (1 + ||Q||_1)
    b_t = Qhat · (omega_t − mu)
    u_t = clip((t−o)/4, 0, 1)
    B_t = c_minus − c_t + 0.10 b_t + 0.20 u_t

c_minus使用上次释放时的实际陈旧性，不随墙钟人工重新老化；actual模型版本改变后的消息年龄在当前P2重算。b>0表示当前组成相对于μ更多覆盖历史欠覆盖方向，b<0表示加重该方向缺口。只使用真实P2的ell；纯几何d=min_a 0.5||Ma−μ||_1属于独立诊断，不参与触发。没有L时的1是沿用未释放几何缺口约定，不是优质虚拟释放。

## 4. 唯一决策与生命周期

每个网格先处理截至t的真实因果通知并过期，再按以下优先级判断；同时间先注册，再完成/失败，其他相同类型按key稳定排序。调度不得读取未到时的真实队列；外层生产者只发布当前到时事件。

1. t=100：处理全部τ≤100通知后只关闭仍打开的窗口一次；非空P不受K≥3限制，执行实际完整P2；空P记录空关闭。禁止同一时点正常关闭后重复终点关闭。注册t=100不属于新尝试。标记有限终点，终止。
2. t≤20：elapsed≥1时共同暖启动关闭，否则WAIT；非空关闭仍需实际P2，空关闭无需P2。Q/V/L按真实提交更新，t=20不清零历史。
3. elapsed≥4：共同deadline强制关闭，非空P即使K<3仍以原退化约束完整P2释放；空P执行空关闭。
4. K<3：WAIT，reason=MIN_CLIENTS，未进入自由动作比较，无需P2。
5. 其他状态：取当前完整P2预览并计算B；仅当B≥θ+1e−7时CLOSE，否则WAIT。阈值附近保守WAIT，规则强制动作仍优先。记录B的质量差、debt项、耐心项及完整实际预览。

注册：冻结Design、p、q和stage1，验证header/模型版本/R/E，记录尝试并开始合法物理工作；控制器只见公开header。到达：先验证实际更新数值及摘要，完成年龄≤5且未终止时接受；同client比较(registered_at,key)，拒绝更老到达，对被替代旧项记录superseded。失败：只按已收到的明确计算/网络失败通知终止。过期：版本年龄>5移出P/F，不能悄悄作为q=0的可校正输入。

非空释放是单一提交事务：确认最新快照、合法key与数值约束→以preview实际权重调用共同backend.apply→成功后C加入keys、P清空、v加1、更新V，保存L的实际omega/ell/age/duration，再执行Q←[Q+0.01(μ−omega)]_+。随后o←t、window_id与revision推进，执行新版本过期，冻结下一窗口配置/模型。后台更新失败不能标记消息已消费或推进Q/L；未来实现必须提供事务回滚/一致检查，不把部分提交点当合法恢复点。

空关闭只记time/duration/reason/empty并打开下一窗口；Q、L、v和V保持不变，不插入ell=0，也不遗忘最近非空释放。正常结束残留消费一次；预算中断不得调用完整终点逻辑，保存原T=100的可恢复前缀并删失。

伪代码：

```text
on_grid(t):
    ingest_only_notified_events_through(t); expire_by_actual_version()
    snapshot = lawful_snapshot()
    if t == T: close_open_window_once(snapshot, TERMINAL); finish_T(); return
    if t <= 20:
        if elapsed >= 1: close_actual_or_empty(snapshot, WARMUP)
        else: record(WAIT, WARMUP)
        return
    if elapsed >= D: close_actual_or_empty(snapshot, DEADLINE); return
    if K < 3: record(WAIT, MIN_CLIENTS); return
    preview = complete_actual_P2(snapshot, reachability_d_not_in_control)
    B = c_minus - preview.c + kappa * Qhat_dot(preview.omega-mu) + nu*elapsed/D
    record(snapshot_binding, preview, B_components)
    if B >= theta + 1e-7: commit_actual_release(preview, FEEDBACK_TRIGGER)
    else: record(WAIT, FEEDBACK_WAIT)
```

输入缺失/非有限、q身份不符或未校准、更新/求解数值失格、预算不足时报告具体依赖并停止受影响运行，不能以Gate=0切换Design、以旧q重构质量、以固定2掩盖失败。实际P2求解超2 CPU秒时保存前缀与失败证据，不声称当前决定已完成。合法deadline和warmup只省未来预测，不省非空真实聚合。

## 5. 非强制状态的统一处理

没有新消息时，P2、Q、c_minus不变，耐心项每格增加0.005；可在达到同一阈值后关闭，也可能一直未达而由deadline关闭，不猜下一条消息。低ell但高age通过c_t的0.02 age成本进入同一判断；不另加为了制造差异的年龄触发。高ell且接近deadline时耐心项逐步抵消不利质量差，最终deadline强制关闭。历史残留欠覆盖通过实际P2的Q以及额外b项作用于同一规则；当前构成确实偿债时提高释放倾向，否则降低。

同当前池、同elapsed和同最近释放c_minus仍可因Q方向不同改变CLOSE/WAIT；即便P2权重因相同列/单点可行域而相同，停止规则也保留可识别debt作用。本批的精确算式只检查这一代数作用，不代替真实数据验证。

## 6. P2缓存、计量与恢复

完整P2数值缓存key包括：按client排序的消息key、下载版本、实际交付摘要/质量/有效样本、注册p/q及身份、当前v、全部原始Q、V、μ与目标版本、完整P2参数、Design配置/实际因子及实现版本。到达入池、替代、过期、消费、debt/方差/模型版本/目标/设置变更均使缓存失效。仅clock/revision、in-flight公开header变化且不改变P2载荷时可复用数值；每格仍重新计算elapsed与B，不能缓存CLOSE/WAIT动作。

当前旧preview.fingerprint包含整个快照，apply_release会拒绝旧时钟预览。未来实现应把P2数值结果与提交绑定分开：缓存命中后核验P2依赖相同，再对最新snapshot创建新的只读preview绑定，核对实际M/omega/keys与剩余年龄资格；不得关闭STALE_PREVIEW检查或直接改旧指纹骗过提交。绑定重建、序列化、缓存、进程/监视费用均计入实际controller和根账。

纯d的额外凸诊断不影响实际P2权重，可以在已冻结当前输入上另计离线诊断成本；未算则null，不能填ell或0。正常/近预算保存使用上一批通过的根预算和成对完成标记设施。复用工作进程、事件改变时求P2是下一次实现建议，尚未证明总单次2秒。根操作准入另需包含监视的完整费用上界和保存余量，不能只看内部2秒。

保存字段覆盖全生命周期、backend、Q/V/L（含omega）、配置、q/p模型与适用身份、所有概率账、窗口/时钟游标；数值缓存可丢弃重算。恢复不得导入旧v3方法快照冒充OF-v1；如做只读接口转换，须验证字段/概率身份并明确不可用于生产恢复。本批设施本身不重复测试。

## 7. 下一次实现接口与结果身份

建议新增独立`src/raven_mcs_observed_feedback/`，schema定义本规格新版本，controller接受无预测器的合法snapshot；lifecycle使用上述共同语义，preview共享完整P2数值内核并保留实际提交检查，probability接收新版本注册冻结q。旧ControlConfig和QValue绑定旧METHOD_VERSION，旧runner强制需要FrozenServiceModel，不能只改名字或塞假预测器复用。

下一次只实现这些独立路径及必要公共纯函数复用，不覆写旧v1/v2/v3、冻结方法或STOP报告。日志分别记录method/config、configured/actual Design、Gate诊断、q角色/适用身份、L/Q、P2载荷/实际alpha/omega/ell/age、B各项、强制原因、触发与去debt影子动作、P2/cache/controller/root成本、提交与恢复身份。检测证书字段应为空/不适用；反馈触发不是INTERVAL_PROVEN。

规格可实现只表明更新与阈值语义完整。新q、真实P2行为、2秒费用、任务保护和控制收益均需后续证据，当前性能状态RESULTS_NOT_REVALIDATED。
