"""MD-only pilot delivery; all quantitative values from verified trajectories."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';REPORT=ROOT/'ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014'
def read(p):return json.loads((OUT/p).read_text())
def raw(p):return f'[{p}](C:/Cursor/raven.mcs/{OUT.name}/{p})'
def put(name,text):
 with (REPORT/name).open('x',encoding='utf-8') as f:f.write(text)
scope=read('PILOT_SCOPE.json');freeze=read('PILOT_FROZEN_PLAN.json');seed=read('SEED_REVIEW.json');sgd0=read('SGD0_AUTONOMOUS_CHECK.json');b=read('BUDGET.json');result=read('PILOT_COMPARISON.json')
put('PILOT_FREEZE.md',f'''# 45001四臂自主单种子诊断冻结

本批由用户交付20261014自主pilot指令授权：Traffic/45001，OF-v1→fixed_time_0.5→fixed_time_2→OF-no-Q-stop，四臂独立T100。总3000CPU秒/GPU0/14400墙钟，单臂7200、物理SGD≤5000、整批≤20000、实际完整在线请求≤2秒；未用旧余额作为授权。主对照事前固定fixed_time_0.5，第二对照fixed_time_2完整保留。

冻结科学配置θ=.02/κ=.10/ν=.20，no-Q-stop仅κ=0；T100/Δ.1/D4/age5/warmup20、Design全程on/Gate仅诊断、q=.5仅diagnostic_prior。共同优先级终点→warmup fixed1→deadline4→K<3 WAIT→自由策略。fixed触发period−1e−9，OF阈值.02+1e−7。完整P2、Q更新、L/V、lagged p、ClientTrainer local1/LR.01/server.01保留。

等待筛查rW≥.05且dG≤.01；或匹配筛查rG≥.02且Wof≤1.05Wb。只对事前主对照判断单种子申请价值，不新增全等待尺度必须皆胜的闸，也不临时改J或基线。800格/窗口不作为独立种子做统计。

45001用途核验：{seed['status']}，复用既有输入索引，检查{len(seed['identity_metadata_checked'])}份身份元数据；计划预留不算已用。首次字符串审计八处命中均为64位历史校验值内的子串，保留初步结果并逐项验证排除，未换seed/扩大搜索。{raw('SEED_REVIEW.json')}。

共同初值身份：{json.dumps(freeze['initial_identity'],ensure_ascii=False)}。全部真实初值和四流映射在第一臂注册前冻结，Q=0/L空，每臂独立模型、池、状态与缓存；45011只供接口/费用参考，不迁移模型/标签。每臂自己的run_id/UTC/probability strategy均在ARM_FROZEN_PLAN记录。TRAIN/public μ/catalogue/scaler身份一致，无TEST控制读取。{raw('PILOT_FROZEN_PLAN.json')}、{raw('INITIAL_BACKEND.json')}。
''')
put('STRATEGY_IMPLEMENTATION_REPORT.md',f'''# 新增自主入口及必要检查

实际入口[scripts/run_observed_feedback_autonomous_pilot.py](C:/Cursor/raven.mcs/scripts/run_observed_feedback_autonomous_pilot.py)，通过[scripts/observed_feedback_pilot_budget.py](C:/Cursor/raven.mcs/scripts/observed_feedback_pilot_budget.py)登记新连续账。策略参数仅允许四个冻结名称。初始化/外生流配对位于observed_feedback_pilot_common.py；根账与滚动预警采用独立pilot_account及已验root发布设施。

authorization.py增加独立AutonomousPilotAuthorization（45001/用户source/P1阶段/四策略/T100/3000/5000每臂及20000整批），原45011授权逻辑保留。backend.py仅将明确pilot授权纳入相同真实训练保护；lifecycle.py增加策略适用身份核验和授权反序列化。新pilot_controller.py对OF委托原Controller，对fixed和κ=0执行相同强制优先级、完整当前P2与真实apply。未将isolated_test置true或用零更新替代实际训练。

固定等待不调用P2；非空关闭调用完整P2并经同一runner执行模型/consume/版本/debt/variance/L，after-close仍更新lagged p。no-Q-stop保存完整P2的Q，绝不称删除全部debt。公开controller看当前snapshot；私有producer随机日志不进入决策。

SGD0固定输入新增关键路径结果{sgd0['status']}：四种策略授权与序列化、旧45011保护、production prior拒绝、模型/缓存/池独立、共同warmup/deadline/MIN_CLIENTS/terminal、fixed等待零P2和真实非空P2/apply/consume；真实ClientTrainer仅拦截进入、未执行SGD。初次fixture把通知20.2错误配到time1，被未来消息检查拒绝；修正fixture顺序后通过，未删保护或改方法。CPU与错误日志均保留。{raw('SGD0_AUTONOMOUS_CHECK.json')}。

修改前三个包的全部manifest列明源码已独立归档old_implementation/src，旧闭包逐文件hash通过；旧45011成对资产/指标/STOP/报告原样保存，不改为45001结果。新增策略计算模块和脚本有新闭包及独立身份；不是用新hash冒充旧实现。{raw('old_implementation/ARCHIVE_CHECK.json')}、{raw('IMPLEMENTATION_SCRIPT_FREEZE.json')}。
''')
completed=result['arms_completed'];details=[]
for arm in completed:
 loc=result['result_paths'][arm];s=read(loc+'/VALIDATION_AND_SUMMARY.json');e=read(loc+'/EXECUTION_RESULT.json')
 fees=[x for x in b['charges'] if x.get('arm') and x['arm'].split('_resume')[0]==arm]
 charge=dict(root_CPU=sum(x['root_CPU'] for x in fees),audited_CPU=sum(x['root_CPU'] for x in fees if x['audit']),conservative_CPU=sum(x['root_CPU'] for x in fees if not x['audit']),job_CPU=sum(x.get('job_CPU',0) for x in fees),driver_CPU=sum(x.get('driver_CPU',0) for x in fees),wall=sum(x['wall'] for x in fees),audit=all(x['audit'] for x in fees),categories={'online':sum(x['categories'].get('online',0) for x in fees)})
 text=f'''# {s['strategy']}独立实际轨迹

状态FULL_T100_VERIFIED；seed45001，q diagnostic_prior=.5/未校准。T100/网格{s['total_grid_rows']}/注册{s['registrations']}，逻辑SGD{s['logical_SGD']}，物理范围{s['total_physical_SGD_lower']}—{s['total_physical_SGD_upper']}，模型版本{s['model_version']}、关闭{s['closures']}（空{s['empty_closures']}）、消费{s['consumed']}唯一key。

G800={s['G_800']:.9f}，回退{s['G_fallback_count']}格；W(close_time>20全部关闭含空/正时长终点)={s['W_mean_post20_including_empty']:.9f}，分母{s['post20_closures']}；辅助非空post20 J={s['J_mean_nonempty_post20']:.9f}。常规799格、自由{s['nonforced_rows']}格，原因{json.dumps(s['regular_reason_counts'])}，不把自由分母替换799。

R1{s['R1']}/R0{s['R0']}/E0{s['E0']}/R1E1{s['eligible_R1_E1']}；消费平均/最大等待{s['consumed_delay_mean']:.6f}/{s['consumed_delay_max']:.6f}。未成熟{s['unmatured']}，物理pending R1右删失{s['physical_pending_R1']}；原因{json.dumps(s['label_terminal_reasons'])}。终点行政消费0与物理未结束分开，不继承前缀删失。

P2{s['P2_calculations']}/cache{s['cache_hits']}；实际权重可行残差{s['max_weight_residual']:.3e}、omega绑定{s['max_binding_error']:.3e}，最大实际完整请求{s['max_actual_request_root_upper']:.6f}CPU秒。完整在线根分类{charge['categories'].get('online',0):.6f}，不是独立solver-only/cache-only费用。该臂计费{charge['root_CPU']:.6f}：已审计实测{charge['audited_CPU']:.6f}=tree{charge['job_CPU']:.6f}+driver{charge['driver_CPU']:.6f}，保守{charge['conservative_CPU']:.6f}，墙钟{charge['wall']:.6f}。全部调用均有PID审计：{charge['audit']}；保守失败调用的实际缺口仍UNKNOWN。

终点model/private字节{s['final_checkpoint_sizes']}、保存最大根上界{s['max_save_upper']:.6f}、留额{s['final_save_reserve']:.6f}。原始配置、所有标签/权重/snapshot/根费用/完整状态与指针：{raw(loc+'/VALIDATION_AND_SUMMARY.json')}、{raw(loc+'/trajectory/'+Path(s['final_complete_marker']).name)}。

同状态影子no-Q差异{s['no_Q_difference']}、fixed.5差异{s['fixed_0_5_difference']}、fixed2差异{s['fixed_2_difference']}；None表示该fixed臂未为无必要影子额外求解P2。自主同全局时刻动作差异另见比较报告。未证明预测任务不退步、RMSE或生产概率。
'''
 put('RESULT_'+arm.upper()+'.md',text);details.append(dict(arm=arm,strategy=s['strategy'],G=s['G_800'],W=s['W_mean_post20_including_empty'],CPU=charge['root_CPU']))
pair=read('PAIRING_RESULT.json') if (OUT/'PAIRING_RESULT.json').exists() else dict(status='INCOMPLETE',missing=result['missing'])
put('PAIRING_CHECK.md',f'''# 共同初值与外生随机配对

状态{pair['status']}。共同数值初值/配置/数据/μ及四RNG流在运行前冻结；每臂独立对象、文件目录、run_id和真实UTC原点，不加载45011终态。每key机会/观察及service各次抽样调用、参数hash和值归档PRIVATE_EXOGENOUS_PAIRING，控制器不读私有记录。

核验结果：{json.dumps(pair,ensure_ascii=False)}。R与原抽样可配对；E、下载版本、p历史、模型、池、消费、CPU下界及实际到达为内生/资源差异，未强制复制OF结果。相同q数值只是输入方案相同，不代表跨策略消费概率相同。服务为原受控外生抽样及实测局部CPU下界，不是设备物理回放。
''')
put('PILOT_COMPARISON.md',f'''# 自主单种子G/W预定筛查

**{result['status']} / WAITING_USER_REVIEW**。四臂完成{len(completed)}/4；完成臂：{json.dumps(details,ensure_ascii=False)}。主对照fixed_time_0.5始终不变，fixed2作为完整第二对照保留；G/W均越小越好。

各基线rW/rG/dG/两条路线及保护条件、自主799格动作差异、Q/版本与关闭序列变化：{json.dumps(result.get('comparisons'),ensure_ascii=False)}。不同池的自主动作是同全局时刻比较；OF原记录同状态影子单列，不作为自主收益替代。

主对照预定筛查：{json.dumps(result.get('screen'),ensure_ascii=False)}。第二对照同时支配OF：{result.get('secondary_dominates_OF','UNKNOWN')}；主路线虽达但第二对照风险：{result.get('utility_risk','UNKNOWN')}。不以J择优，不把本种子或800格当独立确认/显著性。

Q停止项判定{result.get('Q_stop_claim','UNKNOWN')}：仅κ=0自主臂保留原完整P2-Q；报告双指标及轨迹，不根据结果调κ。可见的单种子Pareto描述改善也不等于泛化或正式因果收益。未运行去L或去P2-Q，不给它们的因果收益主张。

{raw('PILOT_COMPARISON.json')}。本批只检验诊断先验下冻结配置的控制描述量；无已校准q、生产风险保证、RMSE不退步、充分训练或完整外部方法领先结论。
''')
put('RESOURCE_AND_BUDGET.md',f'''# 新批费用、墙钟和历史分列

新批连续计费{b['charged_CPU']:.6f}/3000 CPU秒，余{b['remaining_CPU']:.6f}。实测根{b['actual_audited_CPU']:.6f}、保守{b['conservative_CPU']:.6f}、非实测实际缺口UNKNOWN。准备/阅读/交付30保守秒单列；所有失败/修复/检查/monitor/save保留。tree+driver互斥相加，PID审计和训练/监视分解不再加总。

全批墙钟留账{b['wall_used']:.6f}/14400：自批目录创建活动墙钟{b['active_since_batch_creation_wall']:.6f}含开发/执行/工具等待/交付，另预留前期未直接计量600秒保守墙钟；各测量调用实际墙钟合计{b['job_wall_measured']:.6f}另列。此处不是服务逻辑时间，也不包含结束后的用户审批等待。每臂独立7200限制，恢复必须扣该臂旧执行墙钟。

旧45011批757.375不重扣，新批历史总展示{b['historical_plus_new_charged_CPU']:.6f}；旧余额不是授权。根费用与所有进程/错误日志见{raw('BUDGET.json')}。滚动估计为预警，保留慢样本；真实总帽/下一操作/动态保存+收尾准入。旧45011保存9.738750、留额34.808867只作规划起点，各臂更新后的实测值见逐臂报告和SAVE_MEASUREMENTS。

新增工程反馈：基础文本索引编码错误修为UTF-8；身份数值匹配排除八个hash子串；SGD0手输入未来消息被合法保护拒绝，调整测试时间顺序后通过。均未放宽方法或科学验收，费用完整保留。旧源码及报告保持，新增比较不重标45011结果。
''')
if result['status']=='PILOT_UTILITY_PROMISING':
 next_text='仅具备提交45002/45003及完整A层方案的单种子条件；建议两新种子×四自主臂加原A层缺项的独立完整方案先审，按本批每臂实际根费用和保存增长规划，不能直接把一个种子费用当保证。若fixed2同时支配，先审查效用风险。未经用户批准不扩种子或拟合q。'
else:
 next_text='停止新增实验并等待用户决定再验证、方法修订或终止；保留本批成果，不推断所有种子/整类方法不可能有效。不改θ/κ/ν、不删基线、不扩大预算。'
put('NEXT_STAGE_READINESS.md',f'''# 逐阶段判定与下一步边界

**{result['status']} / {result.get('Q_stop_claim','Q_STOP_NOT_EVALUATED')} / WAITING_USER_REVIEW**。

采集/自主整合：{len(completed)}/4完整，缺{result['missing']}；具体有效性与资源均见真实终点验收。P1 OF及固定自主链获得本批证据，预测保存/物理单位重评分等要求尚未补，不标全部P1/P3通过。

效用：按事前fixed.5双路线{result.get('screen')}，仅单种子筛查。Q停止贡献独立判定，完整OF胜固定也不自动归给Q。概率支持仅单条每臂计数，q仍prior；无去L/去P2-Q。资源只是本种子配置费用，不保证全39条。

{next_text}

原P1预测核验、P2声明/证明账、P3全A层三种子、P4充分训练/简单预测器、P5至少两完整外部基线及概率依据、P6独立确认、P7机制消融与新颖性独立检索仍待完成。不将经验控制器说成原可达性证书，不编造alpha保证。不自动启动下一批。
''')
if result['status']!='PILOT_UTILITY_PROMISING':
 put('FAILURE_REPORT.md',f'''# 本批失败／未建立效用的范围

状态{result['status']}。资源/有效性完成{len(completed)}/4，科学筛查与资源失败分列。主对照路线及各保护条件实测{json.dumps(result.get('comparisons'),ensure_ascii=False)}；缺臂{result['missing']}。完整时原因是预定幅度/保护条件未满足，不是资源耗尽；未完整时不得用已完成有利对照通过。

真实完整点和已保存前缀见各臂EXECUTION_RESULT及trajectory；未完成臂的具体错误/后缀需原证据，日志不能拼模型。费用{b['charged_CPU']:.6f}/3000、全批墙钟{b['wall_used']:.6f}/14400，历史加新{b['historical_plus_new_charged_CPU']:.6f}。仍有效的真实学习/完整P2/恢复/因果输入/消费和成本证据保留。

各臂共同外生服务与CPU下界差异见PAIRING_CHECK；结果只覆盖本开发seed及诊断prior，生产概率、学习平台和其他种子未知。继续须用户明确选择、审批具体方案及所缺资源；本批不增加预算或改方法。
''')
(OUT/'DELIVERY_CHECK.json').write_text(json.dumps(dict(status=result['status'],WAITING_USER_REVIEW=True,MD_only=all(p.suffix=='.md' for p in REPORT.iterdir()),files=[p.name for p in REPORT.iterdir()],charged_CPU=b['charged_CPU'],q_fit=0,GPU=0),indent=2))
print(json.dumps(dict(status=result['status'],files=len(list(REPORT.iterdir())))))
