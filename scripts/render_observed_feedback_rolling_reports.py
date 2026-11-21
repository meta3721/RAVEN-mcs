"""Render verified evidence after the final continuous ledger is charged."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2';REPORT=ROOT/'ccf-review-report/observed_feedback_rolling_45011_20261014_s2'
def read(name):return json.loads((OUT/name).read_text())
s=read('VALIDATION_AND_SUMMARY.json');b=read('BUDGET.json');e=read('EXECUTION_RESULT.json');check=read('RESUMPTION_CHECK.json');pub=read('ROOT_PUBLICATION_CHECK.json')
detail=read('DESCRIPTIVE_MECHANISM_AND_COST.json')
meter=read('resume_s2_workspace.meter.json');charge=read('charge_resume_s2_workspace.json');plans=[json.loads(line) for line in (OUT/'ROLLING_COST_PLANS.jsonl').read_text().splitlines()];enriched=read('ENRICHED_ROLLING_COST_SEGMENTS.json')
orig=ROOT/'results_observed_feedback_continuation_45011_20261014';base='C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/'
def link(name):return '['+name+']('+base+name+')'
def number(x):return 'N/A' if x is None else f'{x:.6f}'
def write(name,body):
 with (REPORT/name).open('x',encoding='utf-8') as f:f.write(body)
full=s['full_T100'];status='COMPLETE_T100_ACQUISITION' if full else 'STARTED_PREFIX_INCOMPLETE';q_visible=s['nonforced_no_Q_difference']>0
write('RESUMPTION_REPORT.md',f'''# 同一45011的实际恢复与续行

状态：**{status} / WAITING_USER_REVIEW**。原停止点now1.07、SGD32、model_version1、next_grid_tick11、next_clock1/client3被真实恢复；在任何新训练/通知前，模型和控制状态hash、producer/RNG hash、原数据/目标及源码闭包一致。恢复到1.1前先处理原未完成的注册/通知，没有调用build、换seed或重造45011初始模型。用meta分配形状后直接加载已存真实张量，未消耗初始化随机流。{link('RESUMPTION_CHECK.json')}。

parent_run_id仍为`{check['parent_run_id']}`；原逻辑UTC原点2026-10-14T08:49:32.778907+00:00，原受控服务单位与命名空间不变。实际本会话恢复UTC为{check['restore_UTC']}，worker PID{check['worker_PID']}，新root为`{check['root_id']}`。中间有人工等待/工程中断，不宣称物理墙钟连续部署。

三个冻结源码包raven_mcs、raven_mcs_observed_feedback、raven_mcs_execution保持不变，完整source_closure检查未删除。新增独立`resume_observed_feedback_45011_s2.py`、外部滚动账与根发布设施，不调用旧run入口。原模型、Q/V/L、方法参数、Design on/Gate仅诊断、q诊断先验.5、1步/.01/.01、服务采样/CPU下界及R0/E0工作保持。

第一次恢复会话S1在根发布PermissionError后被设施终止，未发布新完整点；其1.1—1.3三行与21—22个物理SGD的后缀不能拼成可恢复模型。保留日志和33.421875保守费用，恢复理由为普通设施故障，不是追求相同计时或选择结果。S2临时目录首发布又失败，保守2.171875，未有可用根样本，训练不能准入。随后改为工作区内独立反馈目录、逐序唯一临时文件和有界替换重试，保留原测量时间戳/剩余预算算法；该发布路径检查{pub['status']}，真正续行会话的独立PID审计{meter['audit_passed']}。

最终逻辑轨迹只拼原10行和成功续行{s['suffix_rows']}行，合计{s['total_grid_rows']}，无重复或缺口；S1丢失后缀独立保留而不并入正式网格。逻辑SGD{s['logical_SGD']}，加丢失物理工作后累计范围{s['total_physical_SGD_lower']}—{s['total_physical_SGD_upper']}，上界≤5000。开始观察时仅清除旧19条消费/16条物理前缀删失注记，控制快照不变；旧删失资产原样保留，后续成熟/终点重新形成合法标签。

最终完整点：{link('trajectory/'+Path(s['final_complete_marker']).name)}，model/private字节{s['final_checkpoint_sizes']}。只读成对内容、实际输入权重残差、omega/ell/age、唯一消费、q注册冻结和全网格验证通过。{link('VALIDATION_AND_SUMMARY.json')}。未运行第二条独立轨迹、旧43001/44001、q拟合或开发比较。

实际新增计算入口为[scripts/resume_observed_feedback_45011_s2.py](C:/Cursor/raven.mcs/scripts/resume_observed_feedback_45011_s2.py)，外部根账入口为[scripts/observed_feedback_rolling_budget_s2.py](C:/Cursor/raven.mcs/scripts/observed_feedback_rolling_budget_s2.py)，发布设施为[scripts/observed_feedback_root_publisher.py](C:/Cursor/raven.mcs/scripts/observed_feedback_root_publisher.py)。成功会话标签`resume_s2_workspace`的命令/进程证据保留在相应process/meter/log及charge资产中。该运行已完成，不应再次执行这一固定原1.07恢复入口；后续若获批准须从最终完整点建立新的显式入口和连续账。原build入口未作为恢复入口使用。
''')
write('COST_PLANNING_REVISION.md',f'''# 全程预测转为预警，实际根账准入

旧PILOT_COST_PLAN（4668.396250含保存余量）原样保留。首次根训练.234375含worker .078125和监视 .156250，是实际发生过的慢样本；不再把2×所有单项最大值×全部剩余注册当硬闸或可完成性的证明，也不删冷样本。真正准入仍要求有效根余量覆盖当前操作、动态完整保存和必要收尾；实际在线请求逐次≤2，累计物理SGD≤5000，总3600及原单轨迹墙钟7200仍为硬门槛。

滚动预测采用已完成段的实际根分类/注册或网格单位成本，以及最近完整段单位成本，保存按实测最大值和字节增长留额；预测超余额只标warning，不退出。原监视、事件顺序、服务时间、SGD工作没有通过优化省略。最近完整段与整个续行累计分别记录，旧冷初始化/失败/首次训练样本仍在父账和一阶预警资产中，未并作免费工作。

本会话沿原保存点后50格间隔，第一个正常点6.1；边界更新在21.1、26.1（已经覆盖20/25），之后同间隔，终点100。没有重放到5来补一个计时点。完整段汇总补充实际注册、R1、SGD、通知、网格、P2、各根分类、监视分解、操作墙钟、保存字节和队列；监视已包含根账，不再次加总。{link('ROLLING_COST_PLANS.jsonl')}、{link('ENRICHED_ROLLING_COST_SEGMENTS.json')}。

形成{len(plans)}份滚动记录，warning共{sum(x['warning'] for x in plans)}次，未以这些预测停止。保存最大根上界{number(s['max_save_upper'])} CPU秒，最后保存/收尾合计留额{number(s['final_save_reserve'])}；该经验余量不是未来费用保证。真实请求最大上界{number(s['max_actual_request_root_upper'])}。最后预测余额与成本见原始滚动文件；完成单条也不证明39条/其他q策略成本可行。

连续实际费用只加tree+driver。根publisher重试保持最初采样时间戳，RootClient仍拒绝过时样本；新反馈目录属于费用设施，原概率事件/方法/私有队列及数学实现闭包不改。故障费用和不精确部分完整保留。
''')
write('DEVELOPMENT_ACQUISITION_REPORT.md',f'''# 唯一45011采集结果

**{status} / RESULTS_NOT_REVALIDATED / WAITING_USER_REVIEW**。实际到逻辑时间{s['now']}、{s['total_grid_rows']}网格，逻辑SGD{s['logical_SGD']}，物理累计{s['total_physical_SGD_lower']}—{s['total_physical_SGD_upper']}（含失败会话丢失工作），GPU0、q-fit0。真实Traffic TRAIN、事前公共目标、CommonNDMF/ClientTrainer与完整P2/显式Design on；服务为已声明受控随机源及实测CPU下界，不是移动设备物理回放。

注册{s['registrations']}，R1{s['R1']}/R0{s['R0']}，E0{s['E0']}，合格R1E1{s['eligible_R1_E1']}。所有R1保留实际SGD工作，R0不训练；已完成工作账与逻辑SGD一致。真实关闭{s['closures']}（空{s['empty_closures']}），模型版本{s['model_version']}，消费{s['consumed']}key；消费集合与每次非空提交key严格一致，无重复，包括成功提交的零权重key。

常规20<t<100共{s['regular_grid_rows']}格，非强制{s['nonforced_rows']}格；原因分布：{json.dumps(s['regular_reason_counts'],ensure_ascii=False)}。两种动作合法子集{s['legal_both_actions']}格，仅辅助，不替换799分母。OF对no-Q-stop差异{s['no_Q_difference']}/799（非强制{s['nonforced_no_Q_difference']}），对fixed.5差异{s['fixed_0_5_difference']}/799，对fixed2差异{s['fixed_2_difference']}/799。三影子仅同状态动作、复用原完整P2含Q；没有自主模型/控制轨迹或收益对比。

Q停止项同状态动作差异{'出现，仅证明本条机制可见' if q_visible else '为0，不能把其他动作差异归给新增κ项'}。质量/历史L与耐心仍按原分量实际计算，计数：{json.dumps(s['debt_terms'],ensure_ascii=False)}；质量、κb、耐心、b、历史c_minus和当前c的最小/最大/均值：{json.dumps(s['component_ranges'],ensure_ascii=False)}。历史L影响质量参考，Q参与原P2和停止项；未运行去L或去P2-Q，不把使用L或原P2有Q直接说成因果增益。

no-Q差异占常规799格的{100*detail['no_Q_fraction_all_regular']:.4f}%、非强制{s['nonforced_rows']}格的{100*detail['no_Q_fraction_nonforced']:.4f}%。唯一差异原始记录：{json.dumps(detail['no_Q_cases'],ensure_ascii=False)}。稀少差异不能据非零即认定实质机制收益；固定影子比较也不替代自主基线或后续预定5%门槛。

单条描述指标：G800格={number(s['G_800'])}（无最近非空释放回退{s['G_fallback_count']}格）；W按close_time>20全部关闭、含空和终点正时长窗口平均={number(s['W_mean_post20_including_empty'])}。辅助J按非空post20释放的原ell+.02age+.20duration/4平均={number(s['J_mean_nonempty_post20'])}，与G/W分母不同。注册到消费平均{number(s['consumed_delay_mean'])}、最大{number(s['consumed_delay_max'])}，不混为W。

有限消费终点成熟：未成熟{s['unmatured']}；物理R1服务pending{s['physical_pending_R1']}单独右删失；终止原因{json.dumps(s['label_terminal_reasons'],ensure_ascii=False)}。T100行政消费0和物理右删失分开，旧1.07前缀注记未继承为最终标签。q始终诊断先验，不计算正式校准通过。37列归档、全部合法在途key，最大原始F{s['max_public_F_at_registration']}；合格样本编码缺失{s['encoding_missing']}，年龄/设备/网络支持计数在{link('VALIDATION_AND_SUMMARY.json')}，这不是经验校准/正性保证。

本条设备和网络按三个关联层级出现，未提供它们的独立交叉组合支持，也不据计数断言政策迁移正性。

P2新计算{s['P2_calculations']}、缓存{s['cache_hits']}；预览状态{json.dumps(s['preview_status_counts'],ensure_ascii=False)}，权重可行残差最大{s['max_weight_residual']:.3e}，实际输入omega绑定误差{s['max_binding_error']:.3e}，真实请求根最大{number(s['max_actual_request_root_upper'])}秒。{link('DECISION_METRICS.csv')}、{link('ATTEMPT_LABELS.json')}、{link('PUBLICATION_BRIDGE.json')}。无检测收益、任务不退步或预测收益结论；性能和主实验未重验。

续行完整在线根分类{charge['categories']['online']:.6f} CPU秒，涵盖P2/缓存、控制及真实apply；未单独测量solver-only或cache-only费用。原完整点model/private字节{detail['original_checkpoint_bytes']}，第一段{detail['first_checkpoint_bytes']}，终点{detail['final_checkpoint_bytes']}；检查点私有队列最大{detail['queue_max']}、P最大{detail['P_max_at_checkpoints']}、F最大{detail['F_max_at_checkpoints']}，这些是检查点取样最大值，不冒充全事件最大值。{link('DESCRIPTIVE_MECHANISM_AND_COST.json')}提供操作分类计数/请求差额/保守上界/墙钟；请求差额与上界之和不是新的实际总账。
''')
new_wall=sum(x['wall'] for x in json.loads((ROOT/'results_observed_feedback_rolling_45011_20261014_s1/BUDGET.json').read_text())['charges'])+sum(x['wall'] for x in b['charges'] if x['label'].startswith('resume'))
audited=178.03125+b['new_audited_CPU'];conservative=133.015625+b['new_conservative_failed_CPU']
write('RESOURCE_AND_BUDGET.md',f'''# 连续预算与实际执行墙钟

原批连续起点247.625000；本轮新增准备保守30、S1根异常保守33.421875、S2临时路径失败保守2.171875，加所有成功实测调用，最终**{b['charged_CPU']:.6f}/3600 CPU秒**，剩余{b['remaining_CPU']:.6f}。已知根实测{audited:.6f}、保守{conservative:.6f}，两者合计连续账；非实测/历史缺口仍UNKNOWN，不将原measured混合字段当全实测。{link('BUDGET.json')}。

真正成功续行根{charge['root_CPU']:.6f}=tree{charge['job_CPU']:.6f}+driver{charge['driver_CPU']:.6f}，PID独立审计{meter['audit_passed']}，不重复加PID、训练局部计时或监视。互斥分类{json.dumps(charge['categories'],ensure_ascii=False)}。恢复/冷导入单列，相关逻辑训练及监视全计入；原分项仅可调计划。

真正续行墙钟{charge['wall']:.6f}秒，前次采集36.099392、失败续行墙钟也算本单轨迹执行；累计实际执行墙钟{36.0993921+new_wall:.6f}/7200。人工停机和开发撰写不当服务时间；每次恢复均扣此前执行墙钟，未赠送7200。检查/统计调用墙钟另列账中，计算费用仍计入总帽。

逻辑SGD{s['logical_SGD']}，失败后缀额外21—22步独立归账，物理上界{s['total_physical_SGD_upper']}≤5000。保存/队列增长及完整段CPU/墙钟见{link('SAVE_MEASUREMENTS.jsonl')}、{link('ENRICHED_ROLLING_COST_SEGMENTS.json')}。最后成对字节{s['final_checkpoint_sizes']}，保存最大根上界{number(s['max_save_upper'])}、最终保留额{number(s['final_save_reserve'])}。

原5小时累计{b['cumulative_original5h_charged_CPU']:.6f}，名义余额{b['nominal_original5h_remaining_CPU']:.6f}；不是下一批授权，历史缺口UNKNOWN。全部旧报告/失败/STOP/成对点保留，受保护{s['protected_assets_checked']}资产hash未变。原S1丢失后缀不拼模型、未删除费用；根异常具体来源未知的部分保留未知，新临时路径失败调用已定位到os.replace权限。工作区唯一路径检查后实际根发布通过。

最终只读核验首调用因基础Python缺numpy未进入状态检查（SGD0），费用0.218750实测保留；改用本轨迹原依赖环境后通过，9.656250实测CPU。描述提取0.609375实测CPU，未回放、未重新求解或拟合。准备/阅读/修改/交付的30秒保守费用已在本轮S1起点加入，未把这些工作称为免费或实测。最终终点采集根账746.890625与交付连续账的差额来自上述核验/提取调用。
''')
mechanism='STOPPING_Q_EFFECT_OBSERVED' if q_visible else 'STOPPING_Q_EFFECT_NOT_OBSERVED'
write('NEXT_STAGE_READINESS.md',f'''# 下一阶段分别判定，等待用户决定

**{status} / {mechanism} / RESULTS_NOT_REVALIDATED / WAITING_USER_REVIEW**。

- 采集：{'通过；同一T100、1000格、原冻结注册全部处理，完整模型/private可读' if full else '未通过；仅可恢复前缀，见实际停止证据'}。
- 恢复：通过；真实原资产/数据/目标/源码一致，旧10行保留，失败后缀独立隔离，物理步数与费用不清零。
- 机制：no-Q-stop差异{s['no_Q_difference']}/799，非强制差异{s['nonforced_no_Q_difference']}/{s['nonforced_rows']}；{'本条停止κ效应可见但稀少，不据非零视为实质机制验收或收益' if q_visible else '新增停止κ效应未在本条出现，固定影子差异不能补证'}。L/Q实际分量已归档，去L与去P2-Q因果效应未测。
- 支持：年龄/设备/网络和编码域只给单条计数；q仍诊断先验，不具备概率拟合/校准、政策迁移或生产概率依据。
- 成本：完整暖启动/反馈/保存增长已测，可提出下一批成本方案；不将单条或warning预测当未来保证，失败计量部分仍UNKNOWN/保守列账。

本次不等于主实验通过，不证明检测收益、任务性能不退步或预测收益。建议暂停扩大采集。下一步申请仅为既有45011记录的机制与支持审查：核对阈值邻域、κb量级、L参考和概率适用身份，产出保留方法/终止/另行设计的具体选择；建议上限40 CPU秒、GPU0、SGD0、q-fit0、回放0。不得根据本条调θ/κ/ν或特征；若要方法变更、概率准备或小规模自主配对，由用户另行批准预算和方案。未具备直接申请39条或正式确认的证据。

保持fixed.5及其他固定/count/GAP、去Q/去历史、匹配G/W、充分训练/简单预测基线、至少两项完整外部基线与独立确认原门槛；新颖性needs-search。未自动拟合q、开展39条、充分训练、B1或20种子确认。原5小时名义余额不自动授权。
''')
if not full or e['failure']:
 write('FAILURE_REPORT.md',f'''# 实际终止/验收证据

状态{status}，失败{json.dumps(e['failure'],ensure_ascii=False)}。最后完整点{link('trajectory/'+Path(s['final_complete_marker']).name)}；最后保存时间{e['last_saved_time']}，实际到{e['now']}，累计逻辑SGD{s['logical_SGD']}，物理上界{s['total_physical_SGD_upper']}。只有有完整模型/private/游标/RNG的资产可恢复，日志不补齐丢失私有状态。

连续费用{b['charged_CPU']:.6f}/3600，CPU/墙钟与未知项见资源报告。仍有效的恢复、数学/信息与已观察成本证据保留，下一步等待用户针对具体阻塞决定；不改科学定义或放宽硬门槛。
''')
partial_report=ROOT/'ccf-review-report/observed_feedback_rolling_45011_20261014_s1/ENGINEERING_INTERRUPTION.md'
with partial_report.open('x',encoding='utf-8') as f:f.write('''# 初次续行的根发布中断

状态：ENGINEERING_SESSION_INTERRUPTED；后续独立S2已修复设施并完成T100，此处不覆盖旧失败。

阻塞步骤为外部root预算发布。预期逐序新鲜根样本继续支持预算准入；实测在原1.07真实资产恢复一致后、已确认1.1—1.3网格期间，发布PermissionError导致Job清理，尚未产生任何新complete model/private点。确切抛出调用位置未在S1异常中保留，根路径/原pending文件和进程日志保留，底层锁定或权限原因UNKNOWN；不改写成科学性能失败。

该会话真实执行墙钟30.400251秒；CPU完整PID审计缺失UNKNOWN，按单Job墙钟上界加driver保守33.421875计入，原批连续账311.046875/3600。21条成功训练操作记录对应额外物理SGD21；最多还有一个未记录训练操作，物理上界22。最后确认网格1.3仅为日志证据，绝不是新可恢复模型。

最后真正完整点仍为[original1.07 complete pair](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/trajectory/stopped_0011_0206.complete.json)，next_grid_tick11、SGD32、modelversion1，producer next_clock1/next_client3、原RNG和pending通知均可读。之后的SGD/队列没有完整私有状态，禁止从日志拼模型或补出完成点；允许恢复范围仅原1.07完整点。

仍有效成果是原身份/数据/源码/模型与producer恢复一致性、费用保守证据及部分决策描述。最小修复限定根发布共享冲突与反馈路径，保持源闭包、科学和服务语义；原预算不增加。S2临时路径首发布失败也保存2.171875保守费用（没有训练准入），再经工作区独立反馈目录、唯一临时文件、有界替换与原时间戳检查通过后执行成功。新会话为普通设施故障恢复，未为匹配计时重放或择优结果。

证据：[INTERRUPTION_BOUND.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/INTERRUPTION_BOUND.json)、[charge_resume_s1.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/charge_resume_s1.json)、[resume_s1.log](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s1/resume_s1.log)、原DECISION_METRICS与COST_RECORDS均独立保留。本会话三行部分决策不并入最终1000格；完整新状态与连续账见S2报告。
''')
check_delivery=dict(status=status,WAITING_USER_REVIEW=True,q_fit=0,GPU=0,automatic_next_batch=False,source_packages_unchanged=True,report_files=[p.name for p in REPORT.iterdir()],MD_only=all(p.suffix=='.md' for p in REPORT.iterdir()),charged_CPU=b['charged_CPU'],remaining_CPU=b['remaining_CPU'])
(OUT/'FINAL_DELIVERY_CHECK.json').write_text(json.dumps(check_delivery,indent=2));print(json.dumps(check_delivery))
