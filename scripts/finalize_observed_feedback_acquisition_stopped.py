"""Deliver explicit pre-acquisition stop, preserving all failed attempts."""
import json,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_acquisition_45011_20261014';REPORT=ROOT/'ccf-review-report/observed_feedback_acquisition_45011_20261014'
budget=json.loads((OUT/'BUDGET.json').read_text());sgd0=json.loads((OUT/'SGD0_RESULT.json').read_text())
assert sgd0['status']=='PASS' and sgd0['SGD']==0 and not (OUT/'ACQUISITION_FROZEN_PLAN.json').exists()
baseline=json.loads((OUT/'PROTECTED_HISTORY.json').read_text());changed=[p for p,h in baseline.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changed,changed
rows=budget['charges'];known=sum(r['root_CPU'] for r in rows if r.get('audit'));unknown=sum(r['root_CPU'] for r in rows if not r.get('audit'))
evidence=dict(status='ACQUISITION_INCOMPLETE',stage='SEED_AUDIT_NOT_COMPLETED',seed45011_prior_use='UNKNOWN_NOT_CLEARED',
    actual_45011_initialization=False,actual_45011_trajectory_started=False,SGD=0,GPU=0,q_fit=0,
    deterministic_sgd0_integration='PASS',real_data_trajectory_prefix=None,root_budget=budget,
    measured_audited_CPU=known,conservative_failed_meter_CPU=unknown,protected_files_checked=len(baseline),changed_history_files=[],
    stopping_reason='repair headroom 3.078125 CPU seconds cannot cover unresolved full audit; no category transfer authorized',state='WAITING_USER_REVIEW')
(OUT/'FINAL_EXECUTION_RESULT.json').write_text(json.dumps(evidence,indent=2))
with (OUT/'DECISION_METRICS.csv').open('x',newline='') as f:csv.writer(f).writerow(['time','actual_action','reason','quality','debt','patience','B','no_Q_action','fixed_0_5','fixed_2','root_CPU','status'])
docs={
'ACQUISITION_FREEZE.md':'''# 45011冻结状态：未进入真实初始化

本轮授权方法reachability_stop/observed-feedback-v1，角色development_cost_and_bootstrap_fit_candidate；T100、Δ.1、D4、age5、warmup20、θ.02/κ.10/ν.20，完整P2与configured Design=on保持，Gate仅诊断。真实CommonNDMF/ClientTrainer、local_steps1/LR.01/server_eta.01；最多5000实际局部SGD，GPU0，诊断Beta(1,1)均值.5，不拟合q。

这些是授权固定值，不是已发生的Traffic运行冻结。种子用途审计未完成，45011状态UNKNOWN_NOT_CLEARED，不代表发现冲突、也不能标未用。本批没有读取Traffic TRAIN创建真实owner，没有发布本run的实际data/target/model数值身份、RNG流或时钟；未执行B/C/D。不得将SGD0固定单元输入的模型或检查点冒充45011真实初始模型/轨迹。

最小诊断链已有代码和SGD0证据，但真实采集驱动/完整在线循环尚未实现验收。新acquisition模块包含拟议build/producer和四流映射，未在实际Traffic调用；不能标完整生产采集实现已通过。冻结旧结果、停止状态和身份不覆盖，旧43001/44001不恢复。待审计及未验证入口获准完成后，才可重新建立实际冻结计划并开始唯一轨迹。
''',
'DEVELOPMENT_ACQUISITION_REPORT.md':'''# 首条成本采集：ACQUISITION_INCOMPLETE

本批未能完成种子用途审计，因此没有开始唯一45011轨迹，实际局部SGD/GPU/q拟合均0。停止是审计工程与子预算问题，不是OF-v1数值、机制或性能负结果。

已完成实际代码：独立DiagnosticPrior和固定单方法/seed/source/role/T/5000步/3600秒授权；calibration_only从真实backend、runner/snapshot到preview/q.require接通，production拒绝prior、isolate和fitted_not_validated，旧43001/44001保护未改。增加37列OFq-public-state-1.1归档（F/(43+F)和原始F/公开header）、注册前根资源历史、独立物理服务删失及消费删失，窗口注册冻结语义保持；恢复携带诊断身份和根绑定。新增真实producer模块、无副作用no-Q/fixed影子及互斥分类账模块，实际采集循环未实现验收。

唯一确定性SGD0集成通过，使用实际CommonNDMF/ClientTrainer，isolate=false，训练在真正SGD前截断：错误43001/44001授权与生产prior/fitted角色拒绝；正确授权及E0工作到达真实trainer；R0不训练、私有摘要不进入snapshot，完成后才可见；F46不删记录、37列输出；实际大小私有pending tensor/队列与RNG的成对恢复及影子只读通过。SGD计数0，没有新增真实/随机控制轨迹、K43或四整套重测。

必要保存测量根差.812500、上界.832500 CPU秒，墙钟.942544秒；模型6026524字节、私有148230字节。代表固定单元输入的7个CommonNDMF版本/真实工作布局/47个合法公开在途key/一个实际大小pending张量，不代表Traffic增长状态。reserve保持至少5.968750秒。

审计实现过宽，依次Python逐行、分块、字串预筛及全树字段搜索触及各调用帽；它们未形成完整结果。一次根账发布PermissionError实耗缺失，独立保守计费，不能标该调用root审计通过。改用独立live账文件后有效根调用保留。失败和费用未删除，没有静默换seed、跨子账扩额或执行未获清除的轨迹。

真实T观察时域、成熟/消费/机制指标均N/A。CSV仅有列头，行数0，保存在独立results目录；MD目录只放MD。后续只等待审批补全审计/入口，不自动拟合、扩大开发或恢复旧任务。
''',
'MECHANISM_AND_SUPPORT_ANALYSIS.md':'''# 机制、支持和事件证据边界

真实45011轨迹未启动；常规20<t<100的799点、强制/非强制比例、OF/no-Q或fixed.5/2动作差异、P2自身Q效应、G/W/J均N/A，不填0或假分母，没有基线自主轨迹或配对收益。消费成熟/右删失与物理服务删失代码接通，SGD0前缀行为核验通过，但没有Traffic成熟/支持统计。不能把本次未启动当“debt作用0”。

F定义已按全部合法公开在途key实现，P按client一条。固定SGD0输入出现原始F46，编码F/(43+F)保留全部记录，共37列；此结果只证明接口与域处理，不证明Traffic正性、经验支持或概率校准。R0/E0与诊断prior语义未改，E0不以年龄节约实际训练工作的权限。

未运行真实TRAIN学习、真实服务、动态p更新、增长状态保存/请求分布或有限T100终点。两类删失与唯一消费的真实轨迹证据待后续；本批不声称校准、风险保证、充分训练、任务不退步或预测/控制收益。

[SGD0证据](C:/Cursor/raven.mcs/results_observed_feedback_acquisition_45011_20261014/SGD0_RESULT.json)；[零行实际决策CSV](C:/Cursor/raven.mcs/results_observed_feedback_acquisition_45011_20261014/DECISION_METRICS.csv)。
''',
'FAILURE_REPORT.md':f'''# 执行前审计未完成：停止依赖阶段

状态ACQUISITION_INCOMPLETE / SEED_AUDIT_NOT_COMPLETED / WAITING_USER_REVIEW。

预期：先证明45011没有旧执行/拟合/选择冲突，再冻结真实输入、首步测量并条件续行T100。实测：没有完整SEED_REVIEW，未证明无冲突，也没有发现经核实的冲突。首次逐行扫描耗39.984375秒；后续修复累计96.921875/100秒，剩余3.078125不足继续已知规模的完整审计。总预算尚有余额，但固定子帽不得自行挪用，因而停止B/C/D，不换种子。

确定原因：审计实现过宽，重复扫描大日志和全树文本，未先建立只需身份元数据的充分证据范围，消耗修复预算。这是本次实现选择造成的工程失败。未知：45011实际旧用途，搜索尚未覆盖的具体字段/资产；不把不完整搜索或未出现匹配冒充审计通过。一次根发布PermissionError来源未明确，完整实耗缺失，保守计费{unknown:.6f}秒而不写audit=true。

本批计费{budget['charged_CPU']:.6f}/3600 CPU秒：根审计成功调用实测{known:.6f}，失败计量保守{unknown:.6f}，阅读/编辑/交付保守30（对应实际未逐项计量UNKNOWN）。修复子帽不能跨账补额。独立SGD0测试及必要保存通过，实际SGD0；无真实Trajectory。

仍有效：诊断授权/生产保护、真实后端SGD0、37列/F46、私有可见性和队列/RNG成对恢复。{len(baseline)}个旧保护文件未改变，原失败/STOP/冷费用结论保留。代码在src/raven_mcs_observed_feedback中，实际Traffic producer与完整采集驱动未验收，不标完整实现通过。

可恢复状态：SGD0_PAIR/SGD0_queue.complete.json是已验证的固定单元输入成对点，仅可恢复该测试；它不是45011 Traffic前缀。45011真实run尚未初始化，无真实模型/队列/RNG前缀可续。未完成审计资产/代码/所有失败日志可保留继续工程审查，但不得从测试点或日志拼真实恢复状态。

取消/暂停：真实初始化、真实45011首步和T100采集、实际控制/影子记录及成熟统计；概率拟合、39条开发、充分训练、B1、旧任务和确认不启动。仅继续了不消费真实45011数据随机流的独立SGD0核验，没有借失败恢复实验。

继续所需决定：用户批准调整修复子预算及明确更小但充分的身份元数据审计范围，或终止本批。可建议在3600总帽不变下另行批准小额子账重分配；当前未执行、未自行缩小审计承诺。之后还须实现并核验真实在线驱动/根费用边界，不能只因SGD0通过就跳入采集。所有已花费用继续计入原账，不清零。

[完整预算](C:/Cursor/raven.mcs/results_observed_feedback_acquisition_45011_20261014/BUDGET.json)、[最终执行状态](C:/Cursor/raven.mcs/results_observed_feedback_acquisition_45011_20261014/FINAL_EXECUTION_RESULT.json)、[SGD0点](C:/Cursor/raven.mcs/results_observed_feedback_acquisition_45011_20261014/SGD0_PAIR/SGD0_queue.complete.json)。
''',
'RESOURCE_AND_BUDGET.md':f'''# 资源与预算

总计费**{budget['charged_CPU']:.6f}/3600 CPU秒**。有效根实测{known:.6f}秒；一次计量发布异常保守{unknown:.6f}秒、阅读/编辑/交付保守30秒，实耗缺口UNKNOWN。原BUDGET.measured_root_CPU字段是所有调用费用之和，包含异常的保守值，不能解读为全部实测；以这里和FINAL_EXECUTION_RESULT的分解为准。

子账：接线/SGD0 {budget['categories']['setup']:.6f}/180；修复{budget['categories']['repair']:.6f}/100；保存{budget['categories']['save']:.6f}/300；真实初始化/在线/训练/事件均0。有效保存计费来自同一SGD0调用根段分拆，未重复加Job或PID。独立SGD0整调用16.562500秒，其中保存.812500、setup15.750000。

全部调用墙钟合计{budget['wall_measured']:.6f}秒（含失败，不是开发撰写全过程），实际初始化/采集的2小时看门狗未启动；真实随机轨迹0、SGD0、GPU0、q拟合0。fixture函数拦截训练两次不算实际局部步。实际45011模型/数据和成本分布未测。

累计{budget['cumulative_charged_CPU']:.6f}秒，原5小时名义余额{budget['nominal_5hour_remaining_CPU']:.6f}秒；历史实耗缺口UNKNOWN，余额不授权扩额/恢复。总帽未耗尽，但修复余量3.078125秒不够未完成审计；固定子账没有自行重分配。

原始失败日志/各调用Job账/异常保守记录均保留。报告目录只有MD，DECISION_METRICS.csv在results目录，实际0行。旧保护资产{len(baseline)}项未改。下一步等待用户决定，不用残余预算启动依赖阶段。
''',
'NEXT_STAGE_READINESS.md':'''# 下一阶段：补接口/审计或暂停

**ACQUISITION_INCOMPLETE / SEED_AUDIT_NOT_COMPLETED / WAITING_USER_REVIEW**。

最小诊断链代码和独立真实后端SGD0核验通过；种子用途审计未完成，真实初始化/首步/唯一45011成本轨迹均未开始。完整真实在线驱动及费用分布也尚未验收，因此不申请概率或小规模配对开发，不标真实成本run完成。

建议选择“补接口/审计”或“暂停”：先由用户决定是否调整修复子帽及审计身份元数据范围，再在原账基础上完成必要审计与真实在线驱动；本次没有真实前缀可恢复。SGD0完整点仅属于固定单元测试，不能拿来接Traffic或旧43001/44001。

保留fixed.5及其他固定/count/GAP、去Q/去历史、匹配G/W、充分训练/简单预测基线、至少两项完整外部方法、独立确认原门槛；新颖性needs-search。本轮无控制收益、任务不退步、预测收益或校准结论。不会自动拟合、扩大实验或恢复旧任务。

[失败原因](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_acquisition_45011_20261014/FAILURE_REPORT.md)、[接线及SGD0](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_acquisition_45011_20261014/DEVELOPMENT_ACQUISITION_REPORT.md)、[资源](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_acquisition_45011_20261014/RESOURCE_AND_BUDGET.md)、[冻结缺项](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_acquisition_45011_20261014/ACQUISITION_FREEZE.md)、[机制证据](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_acquisition_45011_20261014/MECHANISM_AND_SUPPORT_ANALYSIS.md)。
'''}
for name,content in docs.items():(REPORT/name).write_text(content,encoding='utf-8')
closure={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src/raven_mcs_observed_feedback').glob('*.py')}
(OUT/'FINAL_SOURCE_CLOSURE.json').write_text(json.dumps(closure,indent=2))
(OUT/'FINAL_DELIVERY_CHECK.json').write_text(json.dumps(dict(reports=len(docs),MD_only=all(p.suffix=='.md' for p in REPORT.iterdir()),protected_files_checked=len(baseline),changed_history=[],
    actual_SGD=0,actual_45011_trajectory_started=False,SGD0='PASS',data_rows=0,state='WAITING_USER_REVIEW'),indent=2))
print(json.dumps(dict(status=evidence['status'],charged_CPU=budget['charged_CPU'],protected_files=len(baseline),reports=len(docs),actual_SGD=0)))
