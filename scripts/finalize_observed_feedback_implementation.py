"""Deliver actual four-path evidence, verify preservation, no new experiments."""
import ast,csv,json
from pathlib import Path
from observed_feedback_implementation_budget import ROOT,OUT,REPORT
from raven_mcs.utils.hashing import sha256_file

def report(name,text):
    with (REPORT/name).open('x',encoding='utf-8') as stream:stream.write(text)

if __name__=='__main__':
    results_path=OUT/'final_fields_validation/FOUR_PATH_RESULT.json'
    evidence=json.loads(results_path.read_text());cases=evidence['cases'];rows=evidence['measurements']
    assert evidence['status']=='PASS' and len(cases)==4 and all(c['status']=='PASS' for c in cases.values())
    requests=[r for r in rows if r['judgement']];assert all(r['conservative_root_upper_CPU']<=2 for r in requests)
    assert cases['transaction_real_backend_restore']['production_mode_pending_error_verified']
    protected=json.loads((OUT/'PROTECTED_BEFORE.json').read_text())
    changed=[p for p,h in protected.items() if not Path(p).is_file() or sha256_file(p)!=h];assert not changed,changed
    frozen=json.loads((OUT/'FROZEN_INPUTS.json').read_text())
    assert sha256_file(REPORT/'EXECUTION_BOUNDARY_FROZEN.md')==frozen['boundary_hash']
    assert sha256_file(ROOT/'ccf-review-report/observed_feedback_preparation_20261013/METHOD_SPEC_CANDIDATE.md')==frozen['spec_hash']
    source={str(p.relative_to(ROOT).as_posix()):sha256_file(p) for p in (ROOT/'src/raven_mcs_observed_feedback').glob('*.py')}
    for p in (ROOT/'src/raven_mcs_observed_feedback').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    for name in ('observed_feedback_implementation_budget.py','build_observed_feedback_package.py','validate_observed_feedback_four_paths.py','finalize_observed_feedback_implementation.py'):
        ast.parse((ROOT/'scripts'/name).read_text(encoding='utf-8'))
    (OUT/'FINAL_SOURCE_CLOSURE.json').write_text(json.dumps(source,indent=2))
    representatives=('STARTUP_AND_FIRST_MIN_CLIENTS','COLD_COMPLETE_CURRENT_P2','P1_history_Q_first','P1_no_Q_stop_a',
        'P2_K_below_three','P2_deadline_24.0','P2_empty_deadline','P2_terminal_smallK','P4_real_backend_success_commit','P4_pair_save','P4_pair_restore')
    facts=dict(judgement_count=len(requests),max_request_upper=max(r['conservative_root_upper_CPU'] for r in requests),
        representative={k:next(r for r in rows if r['label']==k) for k in representatives},
        P2_controller_evaluations=sum(r.get('P2') or 0 for r in requests),cache_controller_hits=sum(r.get('cache') or 0 for r in requests))
    (OUT/'RESOURCE_FACTS.json').write_text(json.dumps(facts,indent=2))
    with (OUT/'REQUEST_COSTS.csv').open('x',encoding='utf-8',newline='') as stream:
        fields=['label','judgement','first_includes_startup','root_sample_difference_CPU','conservative_root_upper_CPU','process_CPU',
            'root_monitor_delta_CPU','wall','P2','cache','error']
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    history=cases['history_feedback'];actions=history['actions'];patience=history['patience']
    report('IMPLEMENTATION_REPORT.md',r'''# OF-v1限定实现报告

状态：**IMPLEMENTATION_VALIDATED_FOR_ISOLATED_INPUTS / PRODUCTION_Q_PENDING / PERFORMANCE_NOT_VALIDATED**。只通过本批四条接口路径，没有训练、概率拟合、真实采集或控制回放。运行结束WAITING_USER_REVIEW。

实际新增独立包[src/raven_mcs_observed_feedback](C:/Cursor/raven.mcs/src/raven_mcs_observed_feedback/__init__.py)。schema/design冻结新方法及完整P2/configured-Design；probability记录注册固定q和完整合法历史JSON；stage1复用原校正函数；controller实现唯一B阈值；preview分离不可变数值与最新提交绑定；lifecycle管理私有注册、完成可见性、R/E/替代/过期/唯一消费/终点与故障隔离；backend接真实CommonNDMF/ClientTrainer；persistence接已有成对库并验证源码/模型/身份；budget_client接根账并处理Windows共享访问。

B=c_minus−(ell+0.02 age)+0.10 Qhat·(omega−μ)+0.20 elapsed/4，Qhat=Q/(1+||Q||1)，主动释放B≥0.02+1e−7。网格0.1/T100/D4/age5/minimum_clients3/warmup20及P2参数未改，Gate只诊断，没有未来服务预测器、固定2掩盖依赖或data-name开关。

必要工程修复保留全部失败：首次空池启动超过2秒，移除无关SAG/求解器导入后通过；冷P2加载也出现超限，改用原约束下的精确单点解，K>3仍由原完整RavenAggregator计算，所有目标项/质量重构保留。根账原子rename两次异常用保守费用记账，新客户端共享delete与publisher最多50毫秒重试保留原测量时间。测试边界不后移、2秒不提高。

单点解的依据为Σa=1及Σa²≤1/K，由Cauchy等式只能a=1/K；原cap允许该点，因此它是完整P2唯一解，不是删目标或替代为纯d。测试与原完整preview对照实际alpha/omega；有自由度的4-client路径实际运行原数值P2。首次小池成本不能证明43-client或冷有自由度大池通过。

真实后端SDK检查创建实际FullWindowRunner/CommonNDMF/ClientTrainer，以手工张量验证真实模型步、方差和版本同步，SGD=0；不称真实局部训练已验证。测试标数学fixture，172维真实冻结μ只做输入适配，人工client支持不改称Traffic目录。

旧源码/论文/结果/STOP与前批规格未覆盖；本批早期成功工程快照与最终字段验证分别保留，正式本批依据final_fields_validation结果和FINAL_SOURCE_CLOSURE，不把旧同名缓存当新build。Q适用/校准、充分学习、G/W/RMSE、完整外部基线与新颖性均待证据，没有新RAVEN收益主张。

[最终四路径原始证据](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/final_fields_validation/FOUR_PATH_RESULT.json)；[最终源码身份](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/FINAL_SOURCE_CLOSURE.json)；[保留核验](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/FINAL_DELIVERY_CHECK.json)。
''')
    report('FOUR_PATH_TEST_RESULTS.md',f'''# 四条关键路径验收

一个常驻worker依次执行，四项PASS。原始证据包括全部实际alpha/beta/mass/M/omega/ell/age、求解状态/残差、决策B各项、成熟/删失、模型及恢复摘要。新增字段验收是同一四用例范围的补齐，早期失败和成功记录保留。

1. 历史反馈：各用8次实际完整P2暖启动释放构造Q方向，再空关闭到20；v=8、Q约(0.03,0)/(0,0.03)，满足有限时域且有实际历史，不填任意大debt。当前3列、elapsed0.4、最近质量相同，P2组成与实际距离相同，动作{actions[0]['action']}/{actions[1]['action']}，B={actions[0]['B']:.12f}/{actions[1]['B']:.12f}；κ=0后均WAIT，P2原始Q仍保留，实际目标差{history['P2_Q_objective_difference']:.12f}。零质量变化/b=0时0.4的B={patience[0]['B']:.12f}为WAIT，0.5的B={patience[1]['B']:.12f}为CLOSE；参数与阈值未改。172维冻结μ输入适配通过，不称真实Traffic可达行为。

2. 生命周期：注册p/q/非恒等Design比率冻结，私有未完成质量扰动不改变snapshot，扰动摘要若试图完成则被注册哈希拒绝；R0为outside_R、E0为structural_zero，均不进入逆概率分母。较新替代、失败、K不足、age5过期、暖启动与deadline小K完整P2、空关闭Q/V/L/v不变、前缀删失及T100行政终止均通过。终点只关闭一次，共7个不同key消费，没有重复。Gate0/RESET及Gate1/WARMUP不切换Design。实现消费遍历preview全部keys而不筛正权重；当前实际权重样本没有零权重，不额外声称已触发零权重实例。

3. 缓存：时钟与公开inflight-only变化复用同一numeric并生成新绑定；旧绑定仍被拒绝、旧fingerprint未修改；B随elapsed增长0.005，没有动作缓存。Q/V/版本/配置source/池删项及真实入池/替代/消费使key失效。当前实际输出与未缓存新路径、原完整preview在既有容差内一致。记录d=null。该用例cache统计solves={cases['numeric_cache_binding']['solves']}、hits={cases['numeric_cache_binding']['hits']}，solver计数包含解析完整P2，不能称全是凸求解器调用。

4. 提交/恢复：真实CommonNDMF及ClientTrainer适配，手工实际更新张量经完整权重提交，模型差与权重计算一致，v/Q/V/L含omega在成功后更新；SGD调用被拦截。真实backend在模型改变后故意方差更新失败，runner进入FAULT_QUARANTINED，不标成功消费、不继续正常snapshot、不发布完整恢复点；诊断文件保留部分模型变化。成功使用已有成对库保存/恢复新方法、q/p/Design、源代码、模型/历史版本、方差、时钟和torch/numpy/python RNG及stateless SGD配置；恢复动作、实际P2和规范状态一致。旧v3身份拒绝。真实后端的非隔离模式PendingQ产生明确缺依赖错误，没有常数或固定窗口后备。

最终{len(requests)}个完整请求最大保守根上界{facts['max_request_upper']:.6f} CPU秒，全部≤2；提交/存储费用另列。Startup、相同用例普通错误修复及所有父/子/监视成本计入整批。未执行大池冷启动、真实训练、真实新轨迹、随机回放、论文实验或概率校准。

[原始证据](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/final_fields_validation/FOUR_PATH_RESULT.json)；[请求CSV](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/REQUEST_COSTS.csv)。
''')
    report('CACHE_AND_TRANSACTION_CONTRACT.md',r'''# 注册、缓存与事务契约

## 可见性及概率身份

on_register接受后端合法本地观测形成的private_summary，先固定注册时间/Design/p/ratio/R/E/q及私有摘要哈希，再backend.prepare_work。private_stage1及其hash只在生命周期私有持久化域，不进入控制snapshot；InFlight只含公开Registration、固定q与允许R/E。完成时摘要哈希必须与注册匹配，只有合法完成后Delivered进入P2。控制snapshot没有backend张量、私有未完成质量或未来队列字段。

RegistrationFeatures保留合法age/slack/count、政策/学习/服务/目标上下文及完整history_json/hash；history是当时Q/V/L、elapsed、已完成P与公开F。保留原始合法编码，不能只存无法校准的摘要hash。生产适用identity需明确学习字段与真实data/target，时钟有run_id/origin/unit；q模型只能在窗口边界冻结，旧消息q不改。没有未来预测器构造参数。IsolatedQ只有显式隔离模式可用，诊断prior没有本批入口，PendingQ不填常数；新q校准仍缺失。

## 数值与提交绑定

P2NumericResult为不可变tuple和solver_json；cache key覆盖全部pool摘要/key/注册q及身份、Q、V、当前版本、μ、完整设置、配置/Design和方法版本。时钟、revision、公开F改变而载荷不变时可复用。BoundReleasePreview另含当前snapshot fingerprint；每次命中验证dependency_hash和keys，再新建绑定，不修改旧对象。所有输入变化必须失效，纯d不参加控制。

apply_release核对最新指纹、依赖、keys/消费账、原可行残差≤1e−7及实际M、omega、ell；原STALE_PREVIEW行为保留。deadline/终点的小K采用相同退化可行约束，完整目标的单点解有精确Cauchy证明，其他情况调用原完整RavenAggregator。没有缓存动作、改注册q或删variance项。

## 提交及故障隔离

真实backend.apply成功后才更新v/Q/V/L、消费keys、窗口及backend同步。任何apply/后续同步异常标记fault；由于模型可能已改变，不能承诺回滚。故障态所有正常事件、snapshot、提交、checkpoint_state和恢复拒绝；to_dict只作为故障诊断。测试用真实CommonNDMF在模型改变后的variance hook注入失败，证实没有混成合法状态。处理故障需要另行审核或从旧完整点新分支恢复，本批不自动恢复。

完整检查点记录私有注册摘要/哈希、全部概率账与合法历史、Q/V/L实际omega、模型/版本/工作/已完成更新、源代码closure、学习配置、clock及RNG。cache丢弃重算。已有PairedCheckpointStore的完成标记/hash/identity/游标校验继续使用；OF层额外校验method/source/config/data/target和fault/注册摘要一致性。旧v3身份不可直接恢复。

## 根费用客户端补充

旧根预算/成对库源码保留。新RootClient打开live账时允许Windows共享delete，原子替换读到的是完整旧或新文件；schema/root_id/finished/stale和扣减规则不变。新AtomicPublisher仅在本批启动器本地绑定，暂态rename重试最多50毫秒，保留原测量stamp/cost而非重标时间，读者按年龄扣减。没有提高总预算或2秒，没有新增设施基准。

冻结边界文件保留原字节。实际请求上界另外取独立PID区间+monitor差的保守floor，以防短区间Job量化；这个max只能提高原根上界，PID不再加入总账，首次启动仍包含全部费用。具体最终样本与修复失败见资源报告；未来生产需绑定实测完整根操作上界及保存余量，不能用2秒局部CPU替代根准入。
''')
    report('NEXT_STAGE_REQUEST.md',r'''# 下一阶段请求

当前状态：IMPLEMENTATION_VALIDATED_FOR_ISOLATED_INPUTS / PRODUCTION_Q_PENDING / PERFORMANCE_NOT_VALIDATED；保持WAITING_USER_REVIEW。

唯一下一申请为**概率适用性及首条成本核验的准备**，上限120 CPU秒，训练/SGD/GPU/q拟合/随机及真实轨迹/真实控制回放均0。不是直接批准首条采集。范围：审查OF-v1注册合法历史编码、概率事件/成熟删失、q输入影响停止策略的自洽身份、真实观测/服务/学习配置、可用支持和首条采集所需calibration_only接口；给出限定轨迹数量/种子角色/SGD与CPU/保存预算及明确成败条件，等待用户批准。

本批已核验真实CommonNDMF/ClientTrainer接线、完整P2、缓存、故障隔离和保存恢复；未核验真实局部训练、scaler/优化平台、动态q校准、真实Traffic状态激活或43-client冷费用。不能用手工张量或数学目录代替这些证据。当前诊断prior没有OF-v1执行入口，不能擅自开一个常数q采集路径。概率表接口可接外部证据，当前无对应证据；更换q会改变选择过程，不能沿用旧43001/44001校准身份。

后续计划修订：新增fixed_time_0.5，暖启动/P2/目标/终点/资源均与其他策略相同；它直接检验零质量变化、零反馈下公式内生0.5释放形态。保留原其他9基线、OF及消融配置与3开发种子，原36条计划增至39条，不删旧基线维持原规模。按新完整费用重新估算并单独审批，45001–45003仍只预留且当前未使用。

原匹配收益路线、G/W保护、RMSE不退步、充分训练平台、至少两项完整外部基线及独立20种子确认门槛保持。动作不同只证明机制可辨识；跨窗口收益需相对去debt/去历史有实际G/W/成本证据。新颖性needs-search，无新RAVEN收益主张。

不自动启动新概率批、39条开发、旧七条校准、旧44001/t80恢复、B1或正式确认。若用户不继续，保留代码、原失败、隔离证据与预算账即可；余额不授权后续。

[实现报告](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_implementation_20261013/IMPLEMENTATION_REPORT.md)、[四路径结果](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_implementation_20261013/FOUR_PATH_TEST_RESULTS.md)、[契约](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_implementation_20261013/CACHE_AND_TRANSACTION_CONTRACT.md)、[资源预算](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_implementation_20261013/RESOURCE_AND_BUDGET.md)。
''')
    assert all(p.suffix=='.md' for p in REPORT.iterdir())
    final=dict(status='PASS_ISOLATED_IMPLEMENTATION_DELIVERY',old_files_checked=len(protected),changed_old_files=changed,
        frozen_spec_and_boundary_preserved=True,all_four_paths='PASS',final_evidence=str(results_path),
        verified_request_count=len(requests),max_root_request_upper=facts['max_request_upper'],
        real_backend='CommonNDMF/ClientTrainer SGD0 verified',production='PRODUCTION_Q_PENDING',performance='PERFORMANCE_NOT_VALIDATED',
        baseline_planned_trajectories=39,baseline_runs_executed=0,SGD=0,GPU=0,q_fit=0,
        real_or_random_trajectories=0,facility_retests=0,reserved_seeds_used=False,MD_only=True,final_state='WAITING_USER_REVIEW')
    with (OUT/'FINAL_DELIVERY_CHECK.json').open('x') as stream:json.dump(final,stream,indent=2)
    print(json.dumps(final))
