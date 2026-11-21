"""Small evidence/report writer. No learning, model scoring, solving or testing."""
import collections,csv,datetime,json,pathlib,re,time,ctypes
k32=ctypes.WinDLL('kernel32',use_last_error=True);k32.GetCurrentProcess.restype=ctypes.c_void_p;k32.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint]
if not k32.SetPriorityClass(k32.GetCurrentProcess(),0x4000):raise ctypes.WinError(ctypes.get_last_error())
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=pathlib.Path(__file__).resolve().parent;REPORT=ROOT/'ccf-review-report'/OUT.name.replace('results_','',1)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(n,s): (REPORT/n).write_text(s,encoding='utf-8')
a=load(OUT/'A_RESULT.json');b=load(OUT/'B_RESULT.json') if (OUT/'B_RESULT.json').exists() else None
validation=load(OUT/'C_VALIDATION.json') if (OUT/'C_VALIDATION.json').exists() else {}
execution=load(OUT/'gap/EXECUTION_RESULT.json') if (OUT/'gap/EXECUTION_RESULT.json').exists() else {}
full=validation.get('status')=='PASS'
old=load(OUT/'OLD_SUMMARY_SCALARS.json')
charges=[load(p) for p in sorted(OUT.glob('charge_*.json'))]
if not execution and (OUT/'gap/PROGRESS.json').exists():
 p=load(OUT/'gap/PROGRESS.json');c=next((x for x in charges if x['label']=='C'),{})
 execution=dict(status='FINAL_SUMMARY_MISSING',now=p['time'],time_role='last durable checkpoint, not actual stop time',next_grid_tick=p['grid']+1,last_complete_marker=p['last_complete_marker'],
  actual_new_SGD='UNKNOWN after last checkpoint; saved prefix '+str(p['new_SGD']),logical_SGD=p['logical_SGD'],parent_SGD=671,
  failure=dict(reason=c.get('limit') or c.get('returncode'),cause='UNKNOWN without final worker evidence',last_root_audit=c))
actual=sum(r['actual_CPU'] for r in charges if isinstance(r.get('actual_CPU'),(float,int)))
unmeasured=30.+20. # Preparation envelope + closeout envelope; UNKNOWN actual, not measured CPU.
charged=unmeasured+sum(r['charged_CPU'] for r in charges)
start=datetime.datetime.fromisoformat('2026-10-18T18:58:19.5477347+08:00');now=datetime.datetime.now(datetime.timezone.utc);wall=(now-start).total_seconds()
oldcost=dict(of=(493.984375,2.15625,2689.562009),fixed05=(168.265625,2388.,750.707479),fixed2=(526.90625,0.,2975.833990),noqstop=(552.15625,0.,2995.480840))
names=dict(of='OF-v1',fixed05='fixed_time_0.5',fixed2='fixed_time_2',noqstop='OF-no-Q-stop')
def original(g,w):
 gb=old['fixed05']['G_800'];wb=old['fixed05']['W_mean_post20_including_empty']
 return dict(rG=(gb-g)/gb,rW=(wb-w)/wb,dG=g-gb,match_route=(gb-g)/gb>=.02 and w<=1.05*wb,wait_route=(wb-w)/wb>=.05 and g-gb<=.01)
mechanism=None
if full:
 gs=validation['G'];ws=validation['W'];gh=old['noqstop']['G_800'];wh=old['noqstop']['W_mean_post20_including_empty']
 mechanism=dict(rG_H=(gs-gh)/gs,rW_H=(ws-wh)/ws,dG_H=gh-gs,match_route=(gs-gh)/gs>=.01 and wh<=1.05*ws,wait_route=(ws-wh)/ws>=.05 and gh-gs<=.01,
  simple_dominates_H=gs<=gh and ws<=wh and (gs<gh or ws<wh),H_dominates_simple=gh<=gs and wh<=ws and (gh<gs or wh<ws),G_H_minus_S=gh-gs,W_H_minus_S=wh-ws)
 status='L_MECHANISM_WORTH_LIMITED_REVISION' if mechanism['match_route'] or mechanism['wait_route'] else 'L_MECHANISM_UTILITY_NOT_ESTABLISHED'
else:
 err=json.dumps(execution.get('failure',validation),ensure_ascii=False)
 reason='RESOURCE' if any(k in err.upper() for k in ('MEMORY','HEADROOM','BUDGET','WALL','LIMIT')) else 'IMPLEMENTATION_OR_VALIDATION'
 status='INCONCLUSIVE_'+reason
rows=[]
for k,s in old.items():
 o=original(s['G_800'],s['W_mean_post20_including_empty']);cost=oldcost[k]
 rows.append(dict(strategy=names[k],seed=45001,T_actual=100,T_target=100,completion='HISTORICAL_FULL_T100_VERIFIED',q_role='diagnostic_prior_not_calibrated',G=s['G_800'],W=s['W_mean_post20_including_empty'],J=s['J_mean_nonempty_post20'],G_n=800,W_n=s['post20_closures'],J_n=s['post20_closures']-s.get('empty_closures',0),logical_SGD=s['logical_SGD'],physical_SGD_lower=s['total_physical_SGD_lower'],physical_SGD_upper=s['total_physical_SGD_upper'],new_SGD=0,registrations=s['registrations'],consumed=s['consumed'],closures=s['closures'],empty_closures=s['empty_closures'],P2_solves=s['P2_calculations'],cache_hits=s['cache_hits'],P2_count_scope='full_T100_historical_trace',new_P2_solves=0,new_cache_hits=0,historical_audited_path_CPU=cost[0],historical_conservative_occupancy_CPU=cost[1],historical_unknown_actual_CPU='UNKNOWN for lost fixed05 invocation' if k=='fixed05' else 'unmetered preparation not reassessed',historical_session_wall=cost[2],new_arm_root_CPU=0,new_batch_shared_CPU='reported once in RESOURCE_AND_BUDGET.md; not allocated repeatedly',original_rG=o['rG'],original_rW=o['rW'],original_dG=o['dG'],original_match_route=o['match_route'],original_wait_route=o['wait_route'],new_mechanism_gate=status if k=='noqstop' else 'NOT_PRIMARY_H_S_COMPARISON',metrics_source=str(s.get('final_complete_marker',''))))
ccharge=next((r for r in charges if r['label']=='C'),None)
new_original=original(validation['G'],validation['W']) if full else {}
rows.append(dict(strategy='GAP20-fixed-reference',seed=45001,T_actual=execution.get('now','UNKNOWN'),T_target=100,completion='NEW_FULL_T100_VERIFIED' if full else 'RIGHT_CENSORED_OR_UNVERIFIED_PREFIX',q_role='diagnostic_prior_not_calibrated',G=validation.get('G'),W=validation.get('W'),J=validation.get('J'),G_n=validation.get('G_denominator'),W_n=validation.get('W_denominator'),J_n=validation.get('J_denominator'),logical_SGD=execution.get('logical_SGD'),physical_SGD_lower=execution.get('logical_SGD'),physical_SGD_upper=execution.get('logical_SGD'),new_SGD=execution.get('actual_new_SGD',0),registrations=validation.get('registrations'),consumed=validation.get('consumed'),closures=validation.get('closures'),empty_closures=validation.get('empty_closures'),P2_solves=validation.get('P2_full_trace_solves'),cache_hits=validation.get('full_trace_cache_hits'),P2_count_scope='full_T100_with_borrowed_warmup',new_P2_solves=validation.get('P2_new_solves'),new_cache_hits=validation.get('cache_hits'),historical_audited_path_CPU='shared warmup only; not recharged',historical_conservative_occupancy_CPU=0,historical_unknown_actual_CPU='not recharged',historical_session_wall=0,new_arm_root_CPU=ccharge.get('actual_CPU','UNKNOWN') if ccharge else 'UNKNOWN',new_batch_shared_CPU='reported once in RESOURCE_AND_BUDGET.md; not allocated repeatedly',original_rG=new_original.get('rG'),original_rW=new_original.get('rW'),original_dG=new_original.get('dG'),original_match_route=new_original.get('match_route'),original_wait_route=new_original.get('wait_route'),new_mechanism_gate=status,metrics_source=str(OUT/'C_VALIDATION.json')))
with (OUT/'SMALL_VALIDATION_COMPARISON.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
decision=dict(status=status,state='WAITING_USER_REVIEW',A_pass=a['status']=='PASS',B_pass=b and b['status']=='PASS',C_full_valid=full,A_differences=a['differences'],mechanism=mechanism,new_simple_original_screen=new_original,old_OF_original_screen=original(old['of']['G_800'],old['of']['W_mean_post20_including_empty']),actual_new_SGD=execution.get('actual_new_SGD',0),q_calibrated=False,prediction_evaluated=False,full_P3=False,paper_modified=False,automatic_next_batch=False)
(OUT/'DECISION.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
resource=f'''# 资源与预算\n\n截至{now.isoformat()}，新增已审计完整根CPU={actual:.6f}秒；保守占用={unmeasured:.6f}秒（前置整理30、交付与关闭预留20，实耗UNKNOWN，非实测）。本轮预算记账={charged:.6f}/1000秒，余额={1000-charged:.6f}秒。若任一计量失败，另按其cap保守占用而非记为实测；本轮各计量原始行如下。\n\n墙钟：从首次只读准备2026-10-18T18:58:19.5477347+08:00至当前，活动保守包络={wall:.3f}/5400秒；worker会话墙钟分别列下，不能与活动包络相加。未申请额外旧余额。根费用包含worker树、监视器、启动和保存；独立PID总和仅作审计，不再相加。worker本地训练CPU、逐操作root上界、spent分类均是包含项，不与根费用叠加。\n\n'''
for r in charges:resource+='- '+json.dumps(r,ensure_ascii=False)+'\n'
resource+='\n历史费用仅作定位，不并入本轮：\n'
for k,v in oldcost.items():resource+=f'- {names[k]}：已审计路径根CPU {v[0]}秒，另保守占用{v[1]}秒，所列会话墙钟{v[2]}秒。来源：ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/RESULT_{k.upper()}.md。\n'
resource+='\nfixed05旧失联调用2388秒为保守占用，旧实际CPU及退出墙钟UNKNOWN；不将其标为实测算法成本。不重复累计旧批次或共享暖启动。\n'
resource+='\n概率适用身份：新strategy、collection_role、stop_rule和clock均已单独冻结。scope.service保留父服务模型整包元数据（其中旧CPU_limit=3000仅为继承标记），不作为本轮预算授权；本轮有效CPU上限1000由独立GapAuthorization和新根预算强制，注册历史保存当前根余量。既有注册保留原概率/时钟字段，新增注册采用新配置哈希。该诊断先验不提供概率跨策略校准保证。\n'
resource+=f'''\n本轮GPU=0，q-fit=0，A/B新增SGD=0，C实际新增SGD={execution.get('actual_new_SGD',0)}（上限5000），C逻辑SGD={execution.get('logical_SGD','UNKNOWN')}包含借用暖启动{execution.get('parent_SGD','UNKNOWN')}步。训练保护与概率校准尚未成立，不作RMSE或风险保证。\n\n单worker、单线程和既有单CPU affinity，BELOW_NORMAL优先级；未并行实验。内存来源与时间见gap/MEMORY_BEFORE_MODEL.json、MEMORY_BEFORE_TRAINING.json及MEMORY.jsonl；这些不是交付时当前读数。最低运行采样可用内存={execution.get('min_available_memory_bytes','UNKNOWN')}字节。低于2GiB连续30秒或明显卡顿则保存暂停；没有证据把历史卡顿/关机归因于硬件规格。\n'''
if (OUT/'PRIORITY_CORRECTION.json').exists():
 resource+='\n资源设置修复：19:20:37定点查询发现worker优先级仍为Normal，早期ctypes设置未核实生效；于2026-10-18T11:20:53.9196679Z将本轮worker和monitor明确设为BelowNormal并复读确认。原单CPU worker亲和性始终为1，监视器单独计量。修复仅影响调度，不修改科学源码、随机状态、服务模型或参数；此前Normal阶段如实保留，不宣称自启动全程后台优先级。证据：PRIORITY_CORRECTION.json。终审/交付worker采用显式Windows句柄类型并检查设置返回值。\n'
put('RESOURCE_AND_BUDGET.md',resource)
if full:
 h=old['noqstop'];v=validation
 prose=f'''# 小范围验证结论\n\n状态：{status}；WAITING_USER_REVIEW。A、B通过，唯一新增GAP20-fixed-reference轨迹完整有效到T100，800格G、全部post20正时长关闭W及辅助非空J采用原指标代码计算。\n\nA：129/799格（16.1452%）改变动作；自由582格中129格（22.1649%），全部CLOSE→WAIT。通过≥40格的投入筛查，不是效用证明。\n\nC：简单规则S G={v['G']:.16f}、W={v['W']:.16f}、J={v['J']:.16f}；分母分别800、{v['W_denominator']}、{v['J_denominator']}。历史参考H=no-Q-stop G={h['G_800']:.16f}、W={h['W_mean_post20_including_empty']:.16f}。G_H-G_S={mechanism['G_H_minus_S']:.16f}，W_H-W_S={mechanism['W_H_minus_S']:.16f}。\n\n主要机制门槛：rG_H={mechanism['rG_H']:.6%}、rW_H={mechanism['rW_H']:.6%}、dG_H={mechanism['dG_H']:.16f}。匹配路线（≥1%且等待≤S的1.05倍）={mechanism['match_route']}；等待路线（≥5%且dG≤.01）={mechanism['wait_route']}。简单规则是否同时G/W支配H：{mechanism['simple_dominates_H']}；H是否支配S：{mechanism['H_dominates_simple']}。互有取舍时不宣布统计等效，单种子不推断所有种子。\n\n原OF对fixed.5：G改善1.422627%、W增加18.796992%，原两条路线仍未通过。新简单规则S对fixed.5：rG={new_original['rG']:.6%}、rW={new_original['rW']:.6%}、dG={new_original['dG']:.16f}，原匹配路线={new_original['match_route']}、等待路线={new_original['wait_route']}。S收益不记给OF。OF/no-Q-stop旧G/W及关闭序列相同，额外Q停止贡献仍不获支持。\n\n新增SGD={e['actual_new_SGD'] if (e:=execution) else 0}，完整P2新求解={v['P2_new_solves']}、缓存={v['cache_hits']}；最大权重残差={v['max_weight_residual']:.3g}、组成绑定误差={v['max_composition_binding_error']:.3g}、完整在线请求根上界最大={v['max_actual_request_root_upper']:.6f}CPU秒。q=.5只是diagnostic_prior，calibration_only，不是校准概率；无新增预测评估或训练不退步保证。\n\n本轮比较是共同外生随机流下的自主轨迹；不同全局时间状态可能不同，不能解释为同状态反事实。A影子与C自主结果分别报告；800格/窗口/动作不是独立种子，没有新增显著性检验。C中同状态动态参考影子差异={v['dynamic_reference_shadow_differences_on_GAP_states']}格，仅解释动作，不产生影子G/W。\n\n建议：{'仅保留历史参考的有限修订价值，等待用户决定；不恢复完整P3。' if status=='L_MECHANISM_WORTH_LIMITED_REVISION' else '暂停当前OF-v1的规模扩展，等待用户决定；不自动更换方法或追加种子。'}\n\n有效证据：{OUT/'A_RESULT.json'}；{OUT/'B_RESULT.json'}；{OUT/'C_VALIDATION.json'}；{OUT/'SMALL_VALIDATION_COMPARISON.csv'}。最终合法配对点：{v['paired_checkpoint']}。冻结：gap/ARM_FROZEN_PLAN.json；逐格/消息/费用/内存：gap目录。原失败和旧模型只索引保留，未删除或覆盖。\n\n本轮未完成完整P3，未修改论文；概率校准、预测收益和训练保护仍待独立证据，不自动进入下一批。\n'''
 prose+='\n单位：G是最近非空释放的结构组失配ell（半L1距离）的800格均值，不是RMSE；W为受控逻辑服务单位的窗口时长，不是真实墙钟或注册到消费延迟。rG/rW为相对比例，dG为G的绝对差。J为原ell+.02age+.20duration/4的非空post20释放均值，只作辅助。\n'
 if status=='L_MECHANISM_UTILITY_NOT_ESTABLISHED':
  prose+='\n未达标分类：C阶段科学幅度筛查未过，资料、实现、数值及终点验证均已完成；不是设备故障或预算中断。未满足条件及实际差距即上列两条路线，不能由A动作差异直接推断效用。已知事实为此开发种子的自主G/W取舍；更广泛机制原因、其他种子及预测表现仍未评价，不归因于电脑配置。若继续，需要用户重新决定具体范围和预算，不在本批调参或增加策略。\n'
 put('DECISION_REPORT.md',prose)
else:
 put('FAILURE_REPORT.md',f'''# 小范围验证中断报告\n\n状态：{status}；WAITING_USER_REVIEW。A通过（129/799动作差异），B={b['status'] if b else '未完成'}；C未完成有效终审，不得标记科学失败。\n\n实际执行：{json.dumps(execution,ensure_ascii=False,indent=2)}\n\n验证：{json.dumps(validation,ensure_ascii=False,indent=2)}\n\n预期为完整有效T100后才比较H/S G/W。当前time={execution.get('now','UNKNOWN')}、next_tick={execution.get('next_grid_tick','UNKNOWN')}，最后合法恢复点={execution.get('last_complete_marker','UNKNOWN')}；前缀不补0，不外推终点G/W。若设备异常原因没有证据，根因UNKNOWN。已知错误仅以日志原文为准，不将机器中断判为科学无效。\n\n已审计新增CPU={actual:.6f}、保守占用={unmeasured:.6f}、记账={charged:.6f}、余额={1000-charged:.6f}秒；活动包络={wall:.3f}秒。详细分类与原始根审计见RESOURCE_AND_BUDGET.md。新增SGD={execution.get('actual_new_SGD',0)}，GPU=0，q-fit=0。预算、实现或设备依赖必须先解决，再由用户决定是否续行；本轮不自动重启、不从受OF影响的后20状态伪造独立对照。\n\n未评价C效用，不改变旧OF未通过原筛查的结论，不进入完整P3、不修改论文、不拟合q、不增加种子。有效资产、冻结和恢复点均保留于{OUT}，旧报告未覆盖。\n''')
scope=(REPORT/'SCOPE_AND_FREEZE.md').read_text(encoding='utf-8-sig');scope=scope.replace('当前 A、B 已通过，C 尚未启动；最终状态由后续 DECISION_REPORT 或 FAILURE_REPORT 统一记录。',f'最终状态：{status}；A/B通过，C完整有效={full}，WAITING_USER_REVIEW。')
scope=scope.replace('单worker、单线程、单CPU亲和性、后台低优先级。','单worker、计算线程1和单CPU亲和性；实际优先级核验及修复见RESOURCE_AND_BUDGET.md。')
put('SCOPE_AND_FREEZE.md',scope)
if full:
 implementation=(REPORT/'IMPLEMENTATION_NOTE.md').read_text(encoding='utf-8-sig')
 implementation+='\nC终审已核对ARM_FROZEN_PLAN的全部本地源文件哈希、核心source_closure、私有生产者游标及最终配对点。后续若获续行授权，应先核对冻结的local_source_hashes和private.local_adapter_hash，再通过本地restore_gap读取新授权；旧restore_pair工厂不识别新策略，未被改写。stage_c目录采用排他创建，不能直接重跑已完成臂。\n'
 put('IMPLEMENTATION_NOTE.md',implementation)
diag=(REPORT/'OFFLINE_MECHANISM_DIAGNOSIS.md').read_text(encoding='utf-8-sig');diag=diag.replace('其余登记、q数值、组成、质量、状态逐字段相同','除这些哈希外，登记、q数值、组成、质量和控制状态逐字段相同；哈希输入还包含运行时钟及当时登记历史（含根资源记录），不将哈希差异本身视为科学状态差异')
put('OFFLINE_MECHANISM_DIAGNOSIS.md',diag)
(OUT/'BUDGET_FINAL.json').write_text(json.dumps(dict(as_of=now.isoformat(),audited_actual_CPU=actual,unmetered_conservative_occupancy=unmeasured,charged_CPU=charged,remaining_CPU=1000-charged,active_wall_envelope=wall,charges=charges,state='WAITING_USER_REVIEW',note='delivery launcher final CPU is added in terminal closeout; no new experiment'),indent=2),encoding='utf-8')
print(json.dumps(decision,ensure_ascii=False))
