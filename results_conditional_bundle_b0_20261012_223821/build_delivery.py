"""Build Markdown delivery from existing B0 evidence; executes no experiments."""
from pathlib import Path
import hashlib,json,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
DOC=ROOT/'ccf-review-report/conditional_bundle_b0_20261012_223821'
sys.path.insert(0,str(ROOT/'src'))
from raven_mcs.control.persistence import source_inventory
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def write(path,value):
    with path.open('x',encoding='utf-8') as stream:
        stream.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False))
def link(name,label=None,root=OUT):return f'[{label or name}]({(root/name).as_posix()})'
ledger=read('BUDGET.json')
measured=sum(x['process_tree_cpu_seconds']+x['monitor_cpu_seconds'] for x in ledger['runs'])
spent=measured+ledger['interactive_allowance_seconds']
prior=180.078125
suite=ET.parse(OUT/'audited_delivery.xml').getroot().find('testsuite')
cases=[dict(name=x.attrib['name'],classname=x.attrib['classname'],time=float(x.attrib['time'])) for x in suite.findall('testcase')]
assert len(cases)==31 and not any(x.find('failure') is not None or x.find('error') is not None or x.find('skipped') is not None for x in suite.findall('testcase'))
assert 'SYNTAX_OK' in (OUT/'final_facility-syntax.log').read_text(encoding='utf-8')
assert 'ENVIRONMENT CHECK PASSED' in (OUT/'final_facility-environment.log').read_text(encoding='utf-8')
assert read('preservation-final_facility.json')['changed']==[] and spent<7200
iso=read('audited_delivery-isolation.json')
preview=read('audited_delivery-preview_application.json')['preview']
DOC.mkdir(parents=True,exist_ok=False)
identity=dict(method='reachability_stop/conditional-bundle-v2',base_method='raven_mcs/configured-design-v1',
    status='IMPLEMENTATION_READY_PENDING_CALIBRATION',workflow='WAITING_USER_REVIEW',
    complete_identity='NOT_GRANTED',configured_design='explicit_on_for_main_track',coverage_role='diagnostic_only',
    probability_event='joint_final_consumption_given_registration_and_positive_observation',
    q_freeze='per_attempt_at_registration',q_calibration='DEPENDENCY_PENDING',
    results='RESULTS_NOT_REVALIDATED',training_steps=0,synthetic_replays=0,real_replays=0,
    external_baselines='NOT_VALIDATED',original_queues_resumed=False,formal_confirmation=False)
write(OUT/'METHOD_IDENTITY.json',identity)
write(OUT/'NEW_PATH_TEST_RESULTS.json',dict(status='PASS_INDEPENDENT_B0_MODULES',
    new_path_tests=23,related_regression_tests=8,testcases=cases,log=str(OUT/'audited_delivery.log'),
    junit=str(OUT/'audited_delivery.xml'),source_inventory=source_inventory(ROOT),
    syntax_evidence=str(OUT/'final_facility-syntax.log'),environment_evidence=str(OUT/'final_facility-environment.log'),
    training=0,random_synthetic_control_replay=0,real_control_replay=0,q_calibration='DEPENDENCY_PENDING'))
write(OUT/'B0_STATE.json',identity|dict(cpu_accounted_seconds=spent,cpu_measured_tree_and_monitor_seconds=measured,
    interactive_allowance_seconds=300,original_prevalidation_previous_charge_seconds=prior,
    original_prevalidation_total_charge_seconds=spent+prior,remaining_original_8h_seconds=28800-spent-prior))
report=f'''# B0 实施报告：conditional-bundle-v2

状态：**IMPLEMENTATION_READY_PENDING_CALIBRATION / WAITING_USER_REVIEW**。性能：**RESULTS_NOT_REVALIDATED**。

本轮依据用户的 B0 授权，使用 ccf-experiment-designer；已完整读取外部实施指令及其引用的候选规格、修订协议、旧定位/失败报告、原主实验协议和 Design/Gate 对齐报告。附件中的后续实验内容作为规格资料，不作为运行授权。

## 1. 实际完成的实现

| 位置 | 本轮实现及职责 |
|---|---|
| {link('src/raven_mcs/control/schema.py','schema.py',ROOT)} | 锁定 Δ=0.1、D=4、H=8、四场景、age≤5、暖启动20、tail=2、0.02/0.20；显式 Design、合法当前快照和版本/数值检查 |
| {link('src/raven_mcs/control/lifecycle.py','lifecycle.py',ROOT)} | 注册、冻结 stage1/q、物理成功/失败、准入、替代、过期、唯一消费、空关闭及非空实际更新；真实状态和预测摘要分开 |
| {link('src/raven_mcs/control/predictor.py','predictor.py',ROOT)} | 竞争完成/通知失败/右删失风险表；风险集不足5不支持；在途 client/download 固定，未来联合标记保持 client/公开层/质量/下载年龄关联 |
| {link('src/raven_mcs/control/planner.py','planner.py',ROOT)} | 六类首次偏移、四条共同条件场景、跨窗消费/版本/debt/过期、固定2 tail、共同网格释放积分及首动作执行 |
| {link('src/raven_mcs/control/preview.py','preview.py',ROOT)} | 复用完整 RavenAggregator；校正质量→逐尝试 q→stage2 reference→debt/variance/staleness/P2；同约束纯L1 d 与实际 ell 分列 |
| {link('src/raven_mcs/control/probability.py','probability.py',ROOT)} | 注册前特征、逐尝试冻结值、policy/target/P2/predictor 适用范围、成熟0/1与删失；外部估计模型读取，缺依赖返回 pending，无自动拟合 |
| {link('src/raven_mcs/control/isolation.py','isolation.py',ROOT)}、{link('src/raven_mcs/control/process_budget.py','process_budget.py',ROOT)} | 可终止规划进程及 Windows Job 子进程树 CPU 计量；计算与退出均在原2 CPU秒内，超时执行固定2后备，设施阻塞/非法输入仍报错 |
| {link('src/raven_mcs/control/persistence.py','persistence.py',ROOT)} | 正式 manifest、独立目录、配置/目标/数据/完整源码包归属、不覆盖检查点、保存恢复及来源一致性核验 |
| {link('src/raven_mcs/training/dynamic_control.py','dynamic_control.py',ROOT)} | 实际 CommonNDMF / ClientTrainer 连接；已有 Hájek SGD 入口需单独训练授权及 q；真实服务器张量应用、variance/debt/版本同步；冻结 lagged stage1 上下文和训练配置恢复 |
| {link('src/raven_mcs/experiments/conditional_bundle.py','conditional_bundle.py',ROOT)} | 唯一正式会话 API：prepare / register_observations / decide / close / save / restore；无 EventTrace 回放循环或隐式训练 |
| {link('src/raven_mcs/correction/stage1.py','共享 stage1',ROOT)}、{link('src/raven_mcs/training/window_runner.py','window_runner.py',ROOT)} | 固定/动态路径共同质量与局部权重计算；新增 build_dynamic_control，动态拥有模型后禁止再次调用旧固定 run |
| {link('src/raven_mcs/utils/manifest.py','manifest.py',ROOT)} | 禁用 Git textconv 外部处理；明确源码包范围；显式根目录必须对应本 checkout，不能借用父仓库身份 |
| {link('configs/control/conditional_bundle_v2.json','配置模板',ROOT)}、{link('tests/control_b0','新增测试',ROOT)} | 必须显式填写 Design 及来源的模板；隔离手工有效输入，仅测试新关键路径 |

主轨配置恒 Design=on，Gate仅诊断。测试后续窗口可更换合法估计器，不改写已注册消息的 stage1/q。主轨 on/off 实验仍须分别整段固定；代码不按数据集名自动选择。

stage1 使用窗口前已有的 target/opportunity/p 快照，公开元数据需声明 as_of；当前观测仅用于冻结本条消息。正式会话拒绝缺 p，不借用旧函数的任意0.5回退。保留论文已有 p_min、q_min、a_max、d_max 和 cap/ESS 数值约束。

## 2. 已验证的真实计算路径

最终 **23项新增关键路径 + 8项相关回归 = 31 passed**，无跳过。最后全批测试用时 {float(suite.attrib['time']):.2f} 秒（pytest墙钟），日志 {link('audited_delivery.log')}、JUnit {link('audited_delivery.xml')}。语法及官方 Python3.11.9 环境检查通过，见 {link('final_facility-syntax.log')}、{link('final_facility-environment.log')}。

完整 P2 的手工有效非恒等输入：Design ratio=[0.2,0.4,0.6,0.8]。正式注册接口采用已有 p 模型的合法 cold-start prior0.2，实际群组质量=[3,7]，窗口中外部 p 改为0.4后当前消息仍保存原值。这里的 prior 是既有 observation 模型语义，并非动态 q 校准。

P2预览实测 d={preview['reachability']['d']:.12g}、完整权重 ell={preview['ell']:.12g}、实际权重可行残差={preview['solver']['normalized_weight_residual']:.12g}。d 的独立 SCS 值={preview['reachability']['secondary_value']:.12g}；另保存保守有效的 simplex 松弛对偶下界。d不替代ell，修复解不当作最优证书。日志同时保留求解器候选目标与实际归一化权重目标；本有效样例未触发修复。

实际 FullWindowRunner/CommonNDMF 后端应用预先构造张量后，模型参数、版本、variance及debt与预览计算一致；已有 ClientTrainer 已连接，SGD入口在本轮禁止，局部 optimizer steps=0。这是生产计算接口的行为证据，不是本地学习或预测表现证据。

联合支持样例实际调用多到达、跨窗和完整 P2：一步变体 CLOSE，H=8 变体 WAIT、首次偏移1。两者使用同一场景摘要。该样例仅证明机制路径确实不同，不计算总体收益。

## 3. 生命周期、隔离与恢复

下载版本合法性、晚到旧消息拒绝、较新替代、超龄5后过期、唯一消费、非空实际更新才版本+1均有行为断言。空关闭只推进窗口，保持最近释放、模型版本及debt。未成熟跨窗消息和右删失不标0，完成与消费分列。

DecisionSnapshot没有未来表、隐藏成功、未交付 stage1、更新张量、测试标签或旧U。相同当前快照在不同未来隐藏变量下动作相同；规划不修改真实状态。窗口内不能重拟合预测器/q；下窗更新后旧尝试仍使用旧冻结值。Gate/WARMUP/RESET诊断不改变 Design、实际权重或张量更新。

正式 manifest 保存、实际生产后端状态恢复、会话API磁盘恢复均通过：池、在途、消费集合、模型及下载版本、debt/variance、配置、局部优化器配置、lagged stage1、预测器、每条尝试 q/标签、随机键、最近释放、控制器计量可复原。相同确定性后缀的动作/状态、下一条注册输入一致；旧路径重复 run 被拒绝。验证数据身份明确标为隔离fixture，不冒充Traffic。

## 4. 规划开销与开发反馈

最终正常规划：{iso['normal']['p2_solves']}次完整P2、{iso['normal']['cache_hits']}次缓存命中，CPU {iso['normal']['control_cpu_seconds']:.6f}秒，墙钟 {iso['normal']['wall_seconds']:.6f}秒。受控超时：CPU {iso['timeout']['control_cpu_seconds']:.6f}秒、墙钟 {iso['timeout']['wall_seconds']:.6f}秒，子进程实际终止且执行 fixed_time_2。计量含子进程和监控；2 CPU秒不是仿真0.1时间单位或2墙钟秒。当前仅一个有效快照，不能外推总体后备率。

所有开发失败日志保留：Windows Job访问权限修复；Git textconv设施错误修复；sandbox临时目录重命名失败改用工作区独立临时目录；手工测试下载年龄占位期待错误改为真实非负历史lag；显式临时目录误借父仓库身份修复；原1秒退出等待改为同预算内计量退出；源码范围加入YAML后检查器误按Python解析，改为仅解析.py。均未改算法常数、放宽验收、跳过失败测试或用训练排错。

历史 whole-repository manifest **仅一次**隔离复现，60.901秒墙钟上限结束，子进程树CPU43.640625秒、监控0.359375秒，returncode124。见 {link('LEGACY_MANIFEST_ATTEMPT.json')}。没有复现到原native访问异常，不能声称全库异常已根治；全库无范围哈希路径仍未验证。本新路径保留 Git、环境、配置、数据、目标及整个源码包/控制配置归属，生产保存恢复已通过。未重复全库或历史E1_R2审计。

## 5. 未完成依赖与归属

动态 q_CALIBRATION=DEPENDENCY_PENDING。接口将 q 定义为策略下最终消费的联合概率，逐尝试注册时预测并冻结；不与旧 deadline-usable q 混用。到达、准入、替代和消费分别记录。顺序选择/正性及目标估计量推导见 {link('Q_CALIBRATION_PLAN.md',root=DOC)}；校准与可识别性都未获得证据，不继承风险保证。

事件源适配的公共目录/μ、公开资源时间可用性、真实工作载荷与服务时长关系、概率数据跨运行时间命名空间仍须在下一阶段先核验。已有独立接口允许外部提供窗口前成熟估计器；本轮没有拟合真实p/q或服务核，也没有实现自动批准/自动恢复队列。

完整 FedBuff / 指定FADAS及其优化器、输入/模型适配、成本均未在新系统复现；count-trigger不是这些完整外部方法。旧v1与旧基线只可按原身份对照，不能填新版主表。检测收益、任务不退步、预测改善三个结果均未获得。

历史保护清单52文件内容未变，见 {link('preservation-final_facility.json')}。旧STOP、P0、准备报告、论文、归档失败结果未覆盖。缓存处置：原始数据、合法划分与公共目录可在来源/时间核验后保留；Design/p依赖的stage1只有逐注册快照完全相同时才可考虑复用；旧U/tau/q、消费/版本、reference/debt/P2、训练位移、模型与预测全部隔离并按新策略重算。不得直接复用旧全轨迹或重标112条历史训练。简单预测器仅在相同任务/单位/评价权重下可重评分，当前未核验可直接比较。

## 6. 预算与交付状态

进程树/监控实测合计 {measured:.6f} CPU秒；交互读写、早期小设施尝试及文档生成预留记账300秒（非实测）。保守本轮 {spent:.6f} 秒={spent/3600:.6f} CPU设备小时，限7200秒。前轮准备记账180.078125秒；目前合计 {(spent+prior)/3600:.6f}/8小时，余 {(28800-spent-prior)/3600:.6f}小时。详情 {link('BUDGET.json')}。50–82人时是旧设计估计，不是本轮实测人员工作量；当前未测量人时。

训练0、随机合成控制回放0、真实控制回放0、正式确认0、旧队列恢复0。确定性fixture不计入600轨迹，不进入论文性能表。

Markdown交付仅在本文件夹；实际代码在src/configs/tests/scripts，JSON、日志、JUnit和检查点在独立results目录。机器状态 {link('METHOD_IDENTITY.json')}、{link('B0_STATE.json')}，逐测试证据 {link('NEW_PATH_TEST_RESULTS.json')}。下一批的具体申请见 {link('NEXT_STAGE_READINESS.md',root=DOC)}。独立模块验收完成，完整 IMPLEMENTATION_ALIGNED 未授予；等待用户批准校准、修订或终止。
'''
write(DOC/'B0_IMPLEMENTATION_REPORT.md',report)
qplan='''# 动态 q 校准方案：待审批，未执行

状态：DEPENDENCY_PENDING / WAITING_USER_REVIEW。本轮没有拟合q、生成校准轨迹或执行SGD。

## 1. 事件、时点与估计量

令 R_i 表示本次尝试已注册且有正的合法观测质量，H_i^- 是注册前合法历史；A_i 是物理完成且获准入，I_i 是最终被该策略消费。完成、准入、替代、过期和消费不是同一事件。定义

q_pi(H_i^-)=P_pi(I_i=1 | H_i^-,R_i=1)。

stage1的 m_i,g 使用注册时冻结的 Design/p 和实际合法O构造。stage2按该尝试被冻结的 q_i 形成 m_i,g/q_i 的裁剪参考质量，再归一化成 beta。这里是**联合消费概率接口**，不等同旧 q_usable（deadline到达/可用概率），不自动继承旧定理。若分解，必须同时估计 P(A=1|H,R) 与 P(I=1|A=1,H,R)，且 I⊆A 的系统语义成立；不能把第二项默认为1。

在强条件 E[I_i | H_i^-,m_i,R_i=1]=q_pi(H_i^-) 下，E[I_i m_i,g/q_i | H_i^-,R_i=1]=E[m_i,g | H_i^-,R_i=1]。一般情形多出 Cov(I_i,m_i,g|H_i^-,R_i=1)/q_i；关闭决策使用交付后组成，因此该条件并不由注册时预测或边际校准自动成立。必须另证顺序选择可忽略/条件充分性，或承认不能作目标风险保证。不能为了满足它偷偷添加未来payload到注册特征。

正性要求目标支撑上的合法尝试有正消费概率，并同时有Design机会和观测支撑。未出现的client/群组、必被替代的注册层、未知资源层等缺口单列。p_min/q_min/d_max/a_max是数值裁剪，不创造支撑；裁剪带来偏差，Hájek比值也非有限样本严格无偏。可识别性、校准与预测性能分开验收。

## 2. 已实现的唯一概率规则

逐尝试**注册时**，从窗口前冻结的q模型预测一次；q值、模型版本、证据ID、特征摘要和注册时点随尝试永久保存。关窗P2使用该尝试保存的值，跨窗不重新用新q赋值。预测未来注册仅调用当前冻结模型，使用预测时可见的公开历史；不能用预测结果反向拟合它。参数更换只在允许的后续窗口，不改写旧消息。

特征固定为注册时已知的model_age、公开device/network、最大配置截止余量、池/在途数量、policy及目标/P2/predictor配置身份和合法as_of。实际close、实际成功、未来组成/梯度、旧最终U、其他策略版本不可输入。当前线性数值编码为截距+age+最大余量+池数+在途数；公开资源层作为支持约束。是否足够属于待检验假设，不事后扩特征改善验证分数。

消费为成熟1；通知失败、不可逆替代、超龄过期、无观测为成熟0。尚在途/已入池待关闭不成熟；采集停止时仍不确定则右删失，不能标0。无观测尝试保留审计记录，但拟合上述 R=1 消费概率时排除。所有成熟正负样本保留，不只使用被消费样本。服务风险另记实际完成/通知失败/右删失，不拿消费0代替物理失败。

## 3. 启动循环与本策略数据

现有正式入口没有合法校准q；PendingQModel不给数值。隔离fixture不是部署先验。建议另批 **calibration_only** 采集模式，保留独立身份 π_boot，不作为完整方法通过或性能比较；当前生产代码没有该模式，需批准后添加严格范围的接入及测试。

π_boot 使用事先声明的消费 Bernoulli Beta(1,1)先验均值作为**诊断先验**，明确没有经验校准依据；不能冒充生产q、继承风险保证或作为最终验证。两条拟合采集轨迹使用完整候选控制/P2/lifecycle，实际产生本策略成熟记录。先验只解决采集启动，不形成完整方法证据。

仅在这两条拟合记录上按固定合法编码拟合一次q_A（L2=0.01，固定优化预算，不调特征/系数/阈值、不搜候选），冻结其参数。拟合侧bootstrap/先验策略与最终 π(q_A)不同，所以拟合记录不算最终校准证据。

再固定 **π_A=整个conditional-bundle-v2程序+q_A数值参数+完整P2/目标/Design+服务核及机会模型版本+共同学习配置**，在六条独立轨迹上验证。验证期间q_A参数不更新；服务核在共同暖启动20后固定，合法新事件只条件化、不重拟合。q_model的原数值用于控制和记录，不拿关窗结果重赋值。若验证通过，只提升同一数值模型的证据状态；若重拟合/改服务核/学习配置，策略已变，需要重新审批，而不是沿用旧验证。

正式模式只接受有证据的估计角色；校准模式必须与之分离。实际服务、variance和q相互影响：建议采集使用真实骨干及真实局部步骤。用零梯度/固定variance或仅固定暖启动的数据，只能验证相应代理策略，不能验证真实学习链q。这个新增训练/回放范围必须由用户另批。

## 4. 划分、数量与阈值（拟议冻结项）

使用Traffic训练划分、公开资源和事前目标目录；TEST标签不选策略或构造μ。拟用独立校准种子43001–43008：前2条拟合、后6条独立验证；这些种子**尚未完成污染审计**，批准后先审计，冲突即报批，不临时换种子。与开发41001–41003、确认42001–42020分离。

每条共享物理T=100和0.1网格，共同暖启动20；source生成/事件总线只向策略提供已发生信息，禁止旧最终完成表/U。统计数据的采集墙钟、来源run和运行内逻辑时间分别记录，跨运行历史必须证明在新窗口前已存在，不能把源run未来时刻直接伪装为当前历史。

拟合侧至少2000个R=1成熟尝试；验证侧至少10000个成熟尝试、六条独立轨迹、每个预先公开device×network主要层至少1000条。按client及最大余量/age/池数分别报告覆盖；最终适用域不得排除难层来凑总分。到期仍删失保留并报告；若删失非独立，complete-case校准不能通过，需先解决识别而非补0。

主验收采用固定10等宽概率箱，ECE的按轨迹重采样单侧95%上界≤0.05，整体|mean(q)-mean(I)|的同类上界≤0.03。按公开主要层报告校准偏差，层偏差绝对值的95%上界≤0.05；组数多时作Holm调整。Brier相对仅用拟合数据得到的截距参考，配对差的95%上界≤0。log loss、可靠性图、箱样本数、删失率、q裁剪占比一并报告。只用六簇区间须标有限精度；不足以越过门槛时停止，不增加种子或改阈值。

服务核按0.1格独立检查完成/失败风险、删失及预测时域支撑；风险集<5按现规格不支持。每个已知client只用同client/公开层的合法联合摘要。未知机会时钟、目标支撑和q外推域均需显式诊断。预测后备率与q支持缺失分列：前者允许规定后备，后者不能以固定2掩盖输入缺失。

上述是新校准批次的待审阈值，不改原P3/P5/P6门槛；未计算任何区间。即使校准通过，消费选择/目标估计的理论条件仍需独立通过，才能申请完整链。

## 5. 资源申请与停止条件

建议一次限定 **5 CPU设备小时**，计入原预验证8小时；GPU0、随机合成回放0。请求8条真实校准控制轨迹，真实SGD local_steps=1（既有Hájek SGD、LR0.01）最多35000局部optimizer steps，最大10000次规划调用。真实数据实际观测全部按冻结权重处理，不为赶预算抽掉困难记录；超出步骤/通信/时间限制停止并报批。

规划在2 CPU秒上限下10000调用的极端成本就达20000秒，超过本批18000秒；当前轻量fixture单调用约1.4–1.7秒并不能保证真实运行成本。因此5小时是硬上限，不是完成承诺；执行前先核验公共输入和工作量，按同协议实际记录累计开销，剩余不足不排下一轨迹、不自动扩额。计量含数据接口、一次拟合、服务核、真实训练、P2、子进程、保存、校准统计；训练子项上限2000 CPU秒，并计入总额。

本批的控制/优化配置专用于概率及接口校准，不是P4充分训练平台；以后改变完整学习配置也可能改变q对应的policy，必须重查适用范围。

首次确认信息违规、理论条件不能满足、关键数值失格、成熟数量/阈值未通过或预算不足，保存具体节点/对应参考/预算与未启动任务，进入WAITING_USER_REVIEW。不将校准迭代变成搜索实验。此计划尚未获授权，本轮不拟合、不采集。
'''
write(DOC/'Q_CALIBRATION_PLAN.md',qplan)
nextplan=f'''# 下一阶段就绪表与审批申请

状态：**IMPLEMENTATION_READY_PENDING_CALIBRATION / WAITING_USER_REVIEW**。以下都是申请，无后台队列、无自动执行。

## 1. 当前门槛

| 项目 | 状态 | 对后续的约束 |
|---|---|---|
| B0控制、联合消息、动态生命周期、完整P2预览/apply、恢复 | 独立模块通过，23项新测试 | 可作为实现证据；手工张量不算实际学习 |
| q时点、冻结、成熟/删失、policy记录 | 接口通过 | 动态q经验依据仍DEPENDENCY_PENDING |
| 本策略q校准、正性/消费选择条件 | 未完成 | 阻断B1完整真实链与风险保证 |
| 公共μ/资源、真实数据动态事件适配、服务载荷关系 | 待真实输入核验 | 禁止用旧隐藏tier、旧U或最终到达表替代 |
| B1真实16窗、恢复/物理单位重评分 | 未运行 | 不代表模型有效或检测收益 |
| P2 600轨迹、P3完整开发、P4训练平台、P5外部基线 | 未运行 | 原规定依次推进，不能跳级 |
| 完整FedBuff、指定FADAS | 未复现 | count-trigger与名称适配不算完整外部基线 |
| P6正式20种子/P7 | 未授权 | 完整开发、概率、完整外部基线和资源审核前不申请正式确认 |

方法定义与B0独立模块验收已分开完成；缺校准不是“候选未实现”，也不自动要求先跑性能平台。完整身份通过仍需必要概率/输入/实际计算证据一致。

## 2. 第一项申请：仅概率校准

具体定义、两个拟合加六个独立验证、诊断先验启动、固定 π(q_A)、理论条件、成熟样本数与阈值见 [Q_CALIBRATION_PLAN.md]({(DOC/'Q_CALIBRATION_PLAN.md').as_posix()})。建议5 CPU小时、8条真实校准轨迹、GPU0、随机合成0、真实局部SGD≤35000步且≤2000 CPU秒子预算。统计/来源核验不读TEST标签选择方法。

这比本轮授权新增真实采集/训练及一个明示的 calibration_only 身份，需要用户批准后实施；当前生产入口仍拒绝pending/test概率。校准过程中不得替换主候选系数、阈值或完整P2。完整风险保证还要独立解决顺序选择假设；若缺口需改变方法定义，先提交具体修订。

## 3. 第二项申请：校准及理论条件通过后，再批B1真实16窗

拟采用Traffic开发seed41001，仅真实train/val数据和窗口前公开目标。预先固定物理截止区间 **[20+4j,20+4(j+1))，j=0…15**，共同T=84。候选与fixed_time_2在相同16个物理区间、共享机会/服务随机原语上执行；动态应用窗口数可不同，不能挑16个好窗口或按结果改变区间。起始20暖启动纳入共同合法历史和资源计量。

复用B0正式会话及同一生命周期/P2/骨干，显式Design=on；Gate诊断；校准q/服务模型及完整学习配置冻结并匹配上述policy身份。q源run的时间/支撑映射在第一个实际训练前验收。若控制/版本/样本量改变服务时长，按共享随机原语和实际工作负载重新计算本策略时长，不盲用旧最终到达表。

请求 **1.5 CPU设备小时**，含训练、控制器、P2、数据读取、预测重评分和恢复；GPU0、随机合成0。两条真实完整前缀（候选、fixed2），各一次保存恢复，重跑共同最后4个截止区间作为短后缀（共两条短恢复回放，单独记账）。每注册时刻一次真实合法本地工作，local_steps=1、已有Hájek SGD LR0.01，server_eta=0.01，其他完整P2参数不变。暂以43客户端/每时间单位一次机会估计，含暖启动与两种策略/短后缀最大约8600局部步，拟设9000步硬上限；实际公开client/机会目录核验不同则先报批，不擅自丢消息。

1.5小时不是实测完成保证。候选完整84时间单位至多840次网格规划，最坏2CPU秒/次约1680秒，其他时间留给真实训练、fixed2与后缀。所有子过程计入5400秒总上限；预算或数据工作量不够即保留已完成前缀并等待，不增加额度或缩短到更容易区间。

首要检查：真实非恒等ratio、实际p/q来源/裁剪与reference重构、局部训练权重、debt/variance与下载版本、晚到/跨窗/替代/超龄/空池、唯一消费、每窗alpha残差≤1e−7、d与ell分列、修复前后目标。真实模型预测必须有限；以原物理单位重评分，相对差≤1e−6；检查点后相同合法后缀动作/模型/质量一致且不覆盖前缀。若预定真实输入没有覆盖某关键状态，报告覆盖不足并审批，不能插入模拟事件冒充真实16窗。

训练配置1步用于接口校验，不声称骨干充分训练、主实验成立或预测器胜过均值。校准若使用不同学习/控制版本，不可直接进本批；先核对policy概率依据。

## 4. 后续门槛及原预算

本轮保守记账 {spent/3600:.6f}小时；前轮准备0.050022小时，原8小时当前余额 {(28800-spent-prior)/3600:.6f}小时。申请校准5小时及B1 1.5小时后，按当前账面剩余 {(28800-spent-prior)/3600-6.5:.6f}小时供其他预验证。余额不意味着P2/P3必然够用；先估算600轨迹和三开发seed实际调用数/子进程成本，不足即再审资源，不能自动延长或减少规定批次。

B1仅接口验收。之后按修订协议P2→P3→P4→P5；保留P3的G/W原收益保护、2/3同向与合法动作差异门槛，P4简单预测器/充分训练及平台门槛，P5真实任务不退步和完整外部基线。P4/P5原12训练设备小时/最多60轨迹预算尚未激活。

正式确认申请必须同时具备：完整开发比较、适用q依据及必要理论、至少两项完整外部基线、确认种子污染审计、共同资源核验、按实测成本及20%设施/重试预算编制的正式预算。此时才申请42001–42020；当前不申请、不生成正式队列。

## 5. 入口及保持事项

新增正式API是 `raven_mcs.experiments.conditional_bundle.prepare_conditional_bundle` 与 `restore_conditional_bundle`。prepare需要真实FullWindowRunner、显式ControlConfig、公开数据/目标内容身份、窗口前stage1_as_of、冻结service/q；独立新run_dir与repo_root。registration使用 register_observations，再由授权事件总线按实际时间提供完成/失败；decide返回首动作，close只应用同快照P2一次。save检查点只创建新文件。没有命令行一键恢复旧实验。

旧 `FullWindowRunner.run` 与归档v1仍保留原身份；动态接管后禁止再用旧固定run。同名旧缓存不能复用：旧消费/版本/q/reference/debt/P2/更新/模型/预测须按新方法生成。原始合法数据和划分可保留；简单预测器需同任务/单位/评价权重重新核验。旧STOP及旧负结果不改。

请审阅并决定是否批准第一项限定校准，或要求修改/终止；B1建议在校准通过后另批。本轮到此停止新增运行，等待用户决定。
'''
write(DOC/'NEXT_STAGE_READINESS.md',nextplan)
rows=[]
for case in cases:
    rows.append(f"| {case['name']} | PASS | {case['time']:.3f}s |")
tests=f'''# 新增路径测试证据

结论：23项新路径、8项相关回归，合计31通过，无跳过。测试为隔离确定性fixture及已有纯聚合/设施回归，不是训练或控制收益实验。

最终完整日志 {link('audited_delivery.log')}，JUnit {link('audited_delivery.xml')}；配置格式相关检查器修正后，最终语法 {link('final_facility-syntax.log')}、环境 {link('final_facility-environment.log')}；结构化汇总 {link('NEW_PATH_TEST_RESULTS.json')}。

| 测试 | 结果 | pytest测试体墙钟 |
|---|---|---|
'''+ '\n'.join(rows)+f'''

## 可审查的实际值

- {link('audited_delivery-preview_application.json')}：完整P2实际alpha/beta/M/omega、d/ell、数值残差、原始/实际权重目标、实际张量应用。
- {link('audited_delivery-full_model_connection.json')}：真实CommonNDMF后端、原ClientTrainer、variance/debt及检查点；构造张量来源明确，SGD0。
- {link('audited_delivery-official_registration.json')}：正式register API、窗口冻结的非恒等ratio/p与[3,7]质量、窗口内修改忽略、下窗生效、旧消息不变。
- {link('audited_delivery-production_persistence.json')}：正式manifest/来源记录、保存恢复动作和完整状态后缀一致。
- {link('audited_delivery-official_disk_restore.json')}：正式会话恢复后下一次注册与控制器计量一致。
- {link('audited_delivery-public_registration.json')}：事前公开机会、在途版本保留、未来注册预测及逐尝试q冻结；全部测试概率明确isolated_test_input。
- {link('audited_delivery-risk_table.json')}：完成/失败/右删失的风险集算术，低支持拒绝。
- {link('audited_delivery-joint_support.json')}：共同消息束、一步CLOSE/跨窗WAIT差异；不当作普遍收益。
- {link('audited_delivery-isolation.json')}：正常{iso['normal']['control_cpu_seconds']:.6f} CPU秒/{iso['normal']['wall_seconds']:.6f}墙钟秒，受控超时{iso['timeout']['control_cpu_seconds']:.6f} CPU秒/{iso['timeout']['wall_seconds']:.6f}墙钟秒，实际子进程终止。

## 开发迭代保留

development2：16通过/1设施失败；development3：16通过/1保存设施失败；development4：17通过；development5：20通过/1手工期待错误；final：28通过/1显式Git根定位回归；acceptance：28通过/1进程退出设施反馈；acceptance2：29通过；session_acceptance：8个会话测试通过；delivery_acceptance、final_delivery、audited_delivery均31通过。audited_delivery首次语法子检查把配置YAML当Python，日志保留，最终final_facility只对.py做语法检查后通过。没有删除/跳过失败测试。

早期Windows Job设置错误及legacy-manifest-once设施上限记录保留。历史manifest仅隔离复现一次，未证明全库稳定；新正式存储路径通过。原226项Design测试不重复，全库测试与实际训练/回放未运行。测试内容/脚本和最终源码归属在汇总JSON中；旧52保护文件不变。
'''
write(DOC/'NEW_PATH_TEST_RESULTS.md',tests)
protected=read('PROTECTED_BEFORE.json')
changes=[p for p,h in protected.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changes
assert all(p.suffix=='.md' for p in DOC.iterdir())
for artifact in OUT.glob('audited_delivery-*.json'):
    json.loads(artifact.read_text(encoding='utf-8'))
write(OUT/'DELIVERY_CHECK.json',dict(status='PASS',markdown_files=[str(p) for p in sorted(DOC.iterdir())],
    protected_files=len(protected),historical_changes=changes,
    all_markdown_links_exist=all((OUT/x).exists() for x in (
        'audited_delivery-preview_application.json','audited_delivery-official_registration.json',
        'audited_delivery-official_disk_restore.json','audited_delivery-isolation.json',
        'NEW_PATH_TEST_RESULTS.json','METHOD_IDENTITY.json','B0_STATE.json')),
    source_inventory_sha256=hashlib.sha256(json.dumps(source_inventory(ROOT),sort_keys=True).encode()).hexdigest(),
    cpu_charged_seconds=spent,training=0,synthetic_replays=0,real_replays=0,
    final_status='IMPLEMENTATION_READY_PENDING_CALIBRATION / WAITING_USER_REVIEW'))
print(json.dumps(dict(documents=str(DOC),tests=len(cases),cpu_charged_seconds=spent,
    measured_cpu_seconds=measured,protected_files=len(protected)),ensure_ascii=False))
