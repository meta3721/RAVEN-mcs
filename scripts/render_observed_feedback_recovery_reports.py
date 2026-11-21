"""MD-only actual evidence report, with interrupted and actual resource scopes separate."""
import json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015';OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';REPORT=ROOT/'ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015'
def read(p):return json.loads(Path(p).read_text())
def link(p,label=None):return f'[{label or Path(p).name}]({Path(p).as_posix()})'
def put(name,text):
 path=REPORT/name;assert not path.exists();path.write_text(text,encoding='utf-8')
b=read(OUT/'BUDGET.json');result=read(OUT/'PILOT_COMPARISON.json');paths=dict(of=OLD/'of_resume1',fixed05=OUT/'fixed05_resume1',fixed2=OUT/'fixed2_resume1',noqstop=OUT/'noqstop');names=dict(of='OF-v1',fixed05='fixed_time_0.5',fixed2='fixed_time_2',noqstop='OF-no-Q-stop')
rows=[]
for arm,p in paths.items():
 v=p/'VALIDATION_AND_SUMMARY.json';e=p/'EXECUTION_RESULT.json'
 if arm in result['arms_completed']:
  s=read(v);fees=[r for r in b['charges'] if r.get('arm') and r['arm'].split('_resume')[0]==arm]
  if arm=='of':fees=[r for r in read(OLD/'BUDGET.json')['charges'] if r.get('arm') and r['arm'].split('_resume')[0]=='of']
  audited=sum(r['root_CPU'] for r in fees if r['audit']);conservative=sum(r['root_CPU'] for r in fees if not r['audit']);wall=sum(r['wall'] for r in fees)
  old_unknown='另保留失联调用2388保守占用，旧实际CPU/退出墙钟UNKNOWN，不加入实测算法耗时。' if arm=='fixed05' else ''
  body=f'''# {names[arm]} — FULL_T100_VERIFIED

Traffic/45001；q=.5仅diagnostic_prior，未校准。T100/1000格/4300注册，真实模型与private终点可读；seed、数据、初值、概率策略身份与冻结一致。逻辑SGD{s['logical_SGD']}；物理区间{s['total_physical_SGD_lower']}—{s['total_physical_SGD_upper']}，上界偏移仅计失联实际未知工作，不当测量值。模型版本{s['model_version']}，关闭{s['closures']}（空{s['empty_closures']}），消费{s['consumed']}唯一key。

G800={s['G_800']:.9f}，回退{s['G_fallback_count']}；W(close_time>20全部正时长关闭含空/终点)={s['W_mean_post20_including_empty']:.9f}，分母{s['post20_closures']}；辅助非空post20 J={s['J_mean_nonempty_post20']:.9f}。常规799格，自由{s['nonforced_rows']}；原因{json.dumps(s['regular_reason_counts'],ensure_ascii=False)}。不替换原分母。

R1{s['R1']}/R0{s['R0']}/E0{s['E0']}/R1E1{s['eligible_R1_E1']}；未成熟{s['unmatured']}，物理pending R1有限终点删失{s['physical_pending_R1']}。终态原因{json.dumps(s['label_terminal_reasons'],ensure_ascii=False)}。消费等待平均/最大{s['consumed_delay_mean']:.6f}/{s['consumed_delay_max']:.6f}。行政消费标签和物理服务终点分别处理，未给恢复前缀补0。

完整P2{s['P2_calculations']}、缓存{s['cache_hits']}，权重残差{s['max_weight_residual']:.3e}、实际omega绑定误差{s['max_binding_error']:.3e}。最大实际完整在线请求{s['max_actual_request_root_upper']:.6f}CPU秒；fixed05包含原750格既有实际记录，但失联后缀完整请求终审仍未知，不能声称历史丢失部分已验证。

该路径已审计实际根费用{audited:.6f}、另保守{conservative:.6f}；所列会话墙钟{wall:.6f}。{old_unknown}恢复与新增臂采用持久root样本/检查点SESSION及独立外层PID终审；逐进程CPU是审计包含项，不再相加。终点模型/private字节{s['final_checkpoint_sizes']}，保存最大完整根上界{s['max_save_upper']:.6f}，最终动态留额{s['final_save_reserve']:.6f}。

同状态影子no-Q差异{s['no_Q_difference']}、fixed.5{s['fixed_0_5_difference']}、fixed2{s['fixed_2_difference']}。None为固定臂没有为影子额外求解P2；不同自主池的动作比较见主报告。

原始参数与数值证据：{link(v)}、{link(s['final_complete_marker'])}。旧OF直接复用已验终点，没有重跑；新概率风险和预测性能RESULTS_NOT_REVALIDATED。
'''
  rows.append(dict(strategy=names[arm],G=s['G_800'],W=s['W_mean_post20_including_empty'],J=s['J_mean_nonempty_post20'],physical=[s['total_physical_SGD_lower'],s['total_physical_SGD_upper']],new_or_original_audited_root_CPU=audited))
 else:
  status=read(e) if e.exists() else dict(status='NOT_STARTED')
  body=f'# {names[arm]} — NOT_FULLY_VERIFIED\n\n{json.dumps(status,ensure_ascii=False)}\n\n无完整G800/W筛查结果，不以已完成有利臂替代缺臂。原配置保留，WAITING_USER_REVIEW。\n'
 put('RESULT_'+arm.upper()+'.md',body)
eq=OUT/'fixed05_resume1/RESUMPTION_CHECK.json';exe=OUT/'fixed05_resume1/EXECUTION_RESULT.json'
put('FIXED05_RESUMPTION_REPORT.md',f'''# fixed05真实恢复与结果归属

恢复等值核验：{json.dumps(read(eq) if eq.exists() else None,ensure_ascii=False)}。先在任何新SGD/事件前验证原state hash、producer/RNG hash，再只迁移collection_authorization；模型、Q/V/L、p历史、队列、消费、原run_id/UTC原点及概率身份保持。meta形状分配直接装载保存张量，不重新初始化45001模型。

{json.dumps(read(exe) if exe.exists() else None,ensure_ascii=False)}。原750行逐字节与新终审前缀相等，新成功250行单独SUFFIX保存后拼1000；原750之后失联日志不用于构造模型、随机状态或标签。原旧输出和NULL文件不覆盖。恢复实际UTC另列，人工停机/审批不当服务时间。

物理守卫S+1075+1≤5000。旧失联后缀物理0—1075未知；终点逻辑S另列，新实际根费用独立审计。若有新失败/重放须另外上界并重新核算，未自动重试真实模型轨迹。完整点与SESSION实际恢复候选是状态证据，日志不能拼模型。
''')
pair=read(OUT/'PAIRING_RESULT.json') if (OUT/'PAIRING_RESULT.json').exists() else dict(status='INCOMPLETE',missing=result['missing'])
put('PAIRING_CHECK.md',f'''# 四臂配对与内生差异

{json.dumps(pair,ensure_ascii=False)}。

四臂原共同45001数值初值、TRAIN/public目标/μ、scaler/映射、随机流来源保留，每臂独立模型/Q/V/L/p历史/缓存/消费。每key外生抽样hash/R全4300key核对；实际CPU下界、完成通知、下载版本、E及消费为策略/资源内生差异，全部保留，不强行复制OF完成轨迹。不同run_id/实际UTC原点与恢复原时钟区别记录。

相同q=.5只是诊断数值方案一致，不代表各臂真实消费概率相同。私有配对记录不进入控制器；新未读取TEST控制、未迁移45011模型/标签。
''')
put('PILOT_COMPARISON.md',f'''# 原四臂单种子预定筛查

**{result['status']} / WAITING_USER_REVIEW**。完整臂{result['arms_completed']}，缺{result['missing']}。实际描述量：{json.dumps(rows,ensure_ascii=False)}。

主对照事前fixed_time_0.5；rW=(Wb−Wof)/Wb、rG=(Gb−Gof)/Gb、dG=Gof−Gb，原等待路线rW≥.05且dG≤.01，或匹配路线rG≥.02且Wof≤1.05Wb。未改θ/κ/ν、阈值、基线或分母。

各基线实测与保护条件：{json.dumps(result.get('comparisons'),ensure_ascii=False)}。原主路线判定：{json.dumps(result.get('screen'),ensure_ascii=False)}。第二对照支配OF：{result.get('secondary_dominates_OF','NOT_EVALUATED')}；主幅度达到但第二对照效用风险：{result.get('utility_risk','NOT_EVALUATED')}。不以J选择有利结果，不要求临时新增“击败所有等待尺度”。

Q停止项自主判定：{result.get('Q_stop_claim','NOT_EVALUATED')}。κ=0仅停止式改变，完整P2-Q/Q更新/L/V等保留；自主799格动作、动态Q与版本、关闭序列变化分列在原机器指标。不同池的同全局时刻比较不是同状态反事实，OF同状态影子只作机制描述。

只是一种子诊断，不以800格/窗口作独立种子统计；不声称已校准概率、风险证书、任务不退步、RMSE收益、充分训练、完整外部方法或CCF A新颖性。无去L/去P2-Q，不归因它们的增益。{link(OUT/'PILOT_COMPARISON.json')}。
''')
put('RESOURCE_AND_BUDGET.md',f'''# 连续账、实际费用与未知范围

交付前连续账快照：新阶段{b['stage_charged_CPU']:.6f}/1800 CPU秒，实际审计{b['stage_actual_audited_CPU']:.6f}、保守{b['stage_conservative_CPU']:.6f}，未计量实际缺口UNKNOWN。旧2983.859375不变；连续占用{b['continuous_charged_CPU']:.6f}/4800，不能把旧未知CPU说成已测量。旧历史5522.609375加本批连续占用{b['historical_plus_continuous_CPU']:.6f}，不重复扣旧45011费用。

本阶段活动墙钟{b['stage_active_wall']:.6f}/9000；旧留账14373.550642，连续{b['continuous_wall_used']:.6f}/23400。初始化前保守{b['preinitialize_wall_conservative']}秒，明确工具执行授权等待{b['excluded_approval_wait_seconds']:.6f}单列排除，已关闭旧/新活动区间不随目录年龄继续增长。真实审计作业墙钟{b['job_actual_wall']:.6f}与活动开发墙钟分开。

fixed05原6671.2只是旧保守包络；新实际恢复墙钟见charge_fixed05_resume1，二者相加按修订9000限制核验。fixed2/noQ各原7200，且受阶段9000。新阶段实际Job树+driver互斥相加，PID和内层作业只审计不再加总。新增编译、设施检查、失败、恢复、监视、同步保存及交付均在阶段账；准备30保守费不当精确实测。

物理区间见四臂报告：fixed05逻辑S加0—1075旧失联偏移，上界S+1075；fixed2另有96已知重做步，物理下/上界均S+96；noQ按真实单次计数，OF3354保留。新增96重做后结构总上界16693≤20000（原16597保留作恢复前条件上界）。没有把1075/4643当实际消耗，也没有把未知工作当0。GPU0、拟合q0、额外种子0。

滚动估计只预警，慢样本保留；实际连续/阶段根余量、下一操作与动态保存/收尾留额决定准入，未要求估计最坏剩余整批必定能完成。{link(OUT/'BUDGET.json')}，最终交付与关闭后的费用补正另附。
''')
status=result['status'];q=result.get('Q_stop_claim','NOT_EVALUATED')
proposal=('仅建议另行提交45002/45003×四臂和完整A层的详细方案。按本阶段实际全臂根费用、保存增长和每seed三/四臂资源重新规划；未批准不实施。主幅度达到但若fixed2支配，先审查效用风险。' if status=='PILOT_UTILITY_PROMISING' else '停止新增实验，等待用户选择继续核验、修改方法或终止；不自动调参、换种子或永久终止研究。若缺臂，先按最后真实完整点和实际剩余工作申请资源，不能借不完整结果通过。')
put('NEXT_STAGE_READINESS.md',f'''# 下一阶段判定

**{status} / {q} / WAITING_USER_REVIEW**。

原四臂完整{len(result['arms_completed'])}/4。设施检查与资源授权迁移有独立证据；旧中断根因、精确CPU/退出墙钟仍UNKNOWN。所有完整新臂必须有真实终点成对状态、数值/消费/配对、实际完整在线2CPU和外层根PID审计证据；不追认旧丢失部分通过。

{proposal}

本批不自动拟合q、扩45002/45003、B1、39条或正式确认。P1预测保存/物理单位重评分、P2声明/证明账、P3完整A层/三种子、P4充分学习/简单预测基线、P5完整外部方法与概率依据、P6独立确认、P7机制消融仍各需证据。RESULTS_NOT_REVALIDATED专指未做的预测性能；控制描述收益与任务不退步、预测收益分开。
''')
if status!='PILOT_UTILITY_PROMISING':
 put('FAILURE_REPORT.md',f'''# 本阶段失败或未建立效用的具体范围

状态{status}。完整{len(result['arms_completed'])}/4，缺{result['missing']}。四臂完整时，本报告是原单种子科学幅度/保护条件未满足；缺臂时是设施/有效性/资源阶段未完成，科学筛查NOT_EVALUATED。各固定基线、主路线/保护条件：{json.dumps(result.get('comparisons'),ensure_ascii=False)}；主判定{json.dumps(result.get('screen'),ensure_ascii=False)}，Q停止项{q}。没有事后改门槛。

恢复/新增每臂EXECUTION_RESULT记录具体异常、now/下一格/最后完整模型-private和保存失败；旧失联后缀不复原、真实根因UNKNOWN。仍有效的OF终点、原t75、设施PASS、等值恢复与已完成臂证据保留，旧失败记录不覆盖。

本阶段账快照{b['stage_charged_CPU']:.6f}/1800、连续{b['continuous_charged_CPU']:.6f}/4800；新活动墙钟{b['stage_active_wall']:.6f}/9000。旧2388保守占用不是实际算法费用，已测/未知/保守分开。详见RESOURCE_AND_BUDGET最终补正。若是科学幅度失败，不能据此证明所有种子/同类方法不可能有效；若资源/设施失败，不能据缺臂宣布科学失败。

下一步仅提交明确所缺阶段与实际点、保持方法的最小资源/设施需求或待审批方法修订；未批准不扩预算、改方法、重跑OF或开展其他实验。
''')
delivery=dict(status=status,WAITING_USER_REVIEW=True,MD_only=all(p.suffix=='.md' for p in REPORT.iterdir()),files=[p.name for p in REPORT.iterdir()],stage_charged_CPU_snapshot=b['stage_charged_CPU'],q_fit=0,GPU=0,training_seeds=[45001],automatic_next_batch=False)
(OUT/'DELIVERY_CHECK.json').write_text(json.dumps(delivery,indent=2));print(json.dumps(delivery))

# Add concrete gate and recovery evidence; never infer utility from a partial arm.
def append(name,text):
 with (REPORT/name).open('a',encoding='utf-8') as f:f.write('\n'+text+'\n')
if result.get('comparisons'):
 paragraphs=[]
 for key in ('fixed05','fixed2'):
  z=result['comparisons'][key]
  paragraphs.append(f"对{names[key]}：rW={100*z['rW']:.6f}%，rG={100*z['rG']:.6f}%，dG={z['dG']:.9f}，W比={z['W_ratio']:.9f}；等待路线{z['wait_route']}（质量保护{z['protects_wait_quality']}），匹配路线{z['match_route']}（等待保护{z['protects_match_wait']}）。自主799格动作不同{z['autonomous_action_difference_799']}，动态Q不同{z['dynamic_Q_different_grids']}，模型版本不同{z['model_version_different_grids']}。")
 append('PILOT_COMPARISON.md','\n\n'.join(paragraphs))
 if (REPORT/'FAILURE_REPORT.md').exists():append('FAILURE_REPORT.md','\n\n'.join(paragraphs)+'\n\n四臂若全部完整，则失败发生在原D科学幅度筛查，而非中断或资源终审。无需再训练即可报告本单种子是否达幅；任何下一方法或新种子另需用户审批。')
else:
 for arm in result['missing']:
  p=paths[arm];file=p/'EXECUTION_RESULT.json';e=read(file) if file.exists() else dict(status='NOT_STARTED')
  failure=e.get('failure') or {};actual=e.get('now',0);missing=100-actual
  append('FAILURE_REPORT.md',f"具体受阻臂{names[arm]}：预期T100/1000格/4300注册；当前{e.get('status')}、t={actual}、下一格{e.get('next_grid_tick')}、逻辑SGD={e.get('actual_SGD')}，错误{failure.get('error','not started')}，最后完整点{e.get('last_complete_marker')}，保存错误{failure.get('save_error','none recorded')}。最后持久化后的工作仅按真实记录解释；若无可用终审则UNKNOWN，不从日志拼模型。证据{link(file)}。")
  if actual>0:
   fees=[r for r in b['charges'] if r.get('arm') and r['arm'].split('_resume')[0]==arm]
   cpu=sum(r['root_CPU'] for r in fees if r['audit']);wall=sum(r['wall'] for r in fees if r.get('wall_role')=='measured')
   # Cumulative observed unit rates provide a proposal, not a completion guarantee.
   plan_cpu=round(max(60.,cpu/max(actual,1)*missing*1.5+80.),1);plan_wall=round(max(300.,wall/max(actual,1)*missing*1.5+180.),1)
   msg=f"保持原方法的最小续行申请建议：{names[arm]}还缺约{missing:.3f}服务单位；据本臂累计实测单元费用、1.5倍增长规划及核验/保存余量，建议新增申请约{plan_cpu}CPU秒/{plan_wall}活动墙钟秒/GPU0。此为规划非保证，恢复前需重新核验实际点、已花墙钟及物理重做上界，不能自动重置每臂限额或直接按日志续行。"
   append('FAILURE_REPORT.md',msg);append('NEXT_STAGE_READINESS.md',msg)
if (OUT/'fixed2_resume1/RESUMPTION_CHECK.json').exists():
 eq2=read(OUT/'fixed2_resume1/RESUMPTION_CHECK.json')
 put('FIXED2_RESUMPTION_REPORT.md',f"# fixed2普通设施暂停与真实恢复\n\n{json.dumps(eq2,ensure_ascii=False)}\n\n原t8.11暂停点/完整费用保留；恢复t5有完整训练帧与私有抽样上下文，50原始行逐字节保留、950新成功行独立拼接。未重建初值，不依据效用选择恢复点。原物理266−保存170=96已知重做，最终物理为逻辑S+96；原费用和274.534386秒不回退，后续恢复仍扣剩余7200及阶段9000。SESSION通用offset字段是守卫保守偏移，终审将这96明确归为已知重做，非未知失联工作。\n")
