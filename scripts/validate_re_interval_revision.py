"""Only the three authorized S3 checks; frozen S2 fixtures, no SGD/replay."""
from dataclasses import asdict,replace
import copy
import json
from pathlib import Path
import sys
import traceback
import numpy as np
import revision_feasibility_s2 as f
from raven_mcs_re_interval import METHOD_VERSION
from raven_mcs_re_interval import schema,probability,predictor,lifecycle,stage1
from raven_mcs_re_interval.isolation import IsolatedController
from raven_mcs_re_interval.persistence import save_checkpoint,restore_checkpoint
from raven_mcs_re_interval.planner import evaluate_interval_plans,fixed_fallback
from raven_mcs_re_interval.preview import residual
from revision_feasibility_budget import OUT,ROOT

# Reuse precisely the frozen fixture factory, substituting revision types only.
for module,names in [(schema,['ControlConfig','P2Settings','Registration','ReleaseSummary','DecisionSnapshot']),
    (probability,['EvidenceLogisticQ','policy_context_hash']),(predictor,['FrozenServiceModel','ForecastEvent']),
    (lifecycle,['DynamicWindowRunner','ArrayBackend']),(stage1,['freeze_stage1'])]:
    for name in names:setattr(f,name,getattr(module,name))

def put(name,obj):
    name=Path(name).stem+'_'+sys.argv[2]+'.json'
    with (OUT/name).open('x',encoding='utf-8') as h:json.dump(obj,h,ensure_ascii=False,indent=2,allow_nan=False)

def expect_error(fn):
    try:fn()
    except (schema.InputError,ValueError):return True
    raise AssertionError('expected explicit rejection')

def check_re():
    r,_=f.make_case();r.apply_release(r.preview_release()) # version2 at22, four clients
    for cycle in range(4):
        start=r.now
        for j in range(3):
            key=f'advance{cycle}_{j}';reg=schema.Registration(key,key,start+.1,r.model_version,'public_device','public_network')
            r.on_register(reg,f.summary(r.config,r.mu,start+.1,'mu'))
        for j in range(3):r.on_completion(f'advance{cycle}_{j}',start+.2,update=[.1,.2,.3])
        r.advance_time(start+4);r.apply_release(r.preview_release())
    assert r.model_version==6
    t=round(r.now+.1,10);positive=f.summary(r.config,r.mu,t,'mu')
    zero=replace(positive,masses=(0.,)*len(r.mu),local_weights=(0.,)*len(positive.local_weights),
                 observed_count=0,observed_positions=(),effective_n=0.)
    for key,version,s in [('R0',6,zero),('E0',0,positive),('ok',6,positive)]:
        r.on_register(schema.Registration(key,key,t,version,'public_device','public_network'),s)
    frozen={k:asdict(r.attempts[k].q) for k in ('R0','E0','ok')}
    assert [r.attempts[k].q.role for k in ('R0','E0','ok')]==['outside_R','structural_zero','isolated_test_input']
    for key in ('R0','E0'):expect_error(lambda:r.attempts[key].q.require(isolated_test=True))
    supported_features=r.attempts['ok'].features
    zero_model=probability.EvidenceQTable('explicit_zero',20.,'isolated_zero_support',
        ((f.sha256_json(asdict(supported_features)),0.),),role='isolated_test_input')
    zero_q=zero_model.predict_at_registration(supported_features)
    assert zero_q.role=='zero_support' and zero_q.value==0
    expect_error(lambda:zero_q.require(isolated_test=True))
    calls=[]
    def record_start(key,records,*,authorization):
        # Interface spy, not a training simulator: no update and zero optimizer calls.
        calls.append(key);r.backend.work[key]['training_started']=True;return dict(optimizer_steps=0)
    r.backend.start_local_training=record_start
    for key in ('E0','ok'):r.start_local_training(key,(),authorization='interface_only_NO_SGD')
    expect_error(lambda:r.start_local_training('R0',(),authorization='interface_only_NO_SGD'))
    r.on_completion('E0',t+.1,update=[.1,.2,.3]);r.on_completion('ok',t+.1,update=[.1,.2,.3])
    assert r.attempts['E0'].physical_outcome=='completion' and r.attempts['E0'].consumed==0
    assert set(r.pool)=={'ok'} and 'E0' in r.backend.work and 'R0' in r.backend.work
    preview=r.preview_release();assert preview.keys==('ok',)
    r.apply_release(preview)
    newq=replace(r.q_model,version='next_frozen_q',as_of=r.now,weights=(-1.,0.,0.,0.,0.))
    r.freeze_next_estimators(predictor=replace(r.predictor,as_of=r.now,q_model=newq.to_dict()),q_model=newq)
    assert frozen=={k:asdict(r.attempts[k].q) for k in frozen}
    path=OUT/('S3_new_identity_checkpoint_'+sys.argv[2]+'.json');save_checkpoint(path,r)
    restored=restore_checkpoint(path,backend=lifecycle.ArrayBackend([0.,0.,0.]))
    assert f.sha256_json(restored.to_dict())==f.sha256_json(r.to_dict())
    expect_error(lambda:restore_checkpoint(ROOT/'results_calibration_first_20261013/trajectory/FAILED_tick0201.json',backend=lifecycle.ArrayBackend([0.,0.,0.])))
    allmarks=tuple(predictor.OpportunityMark(**x) for x in r.opportunity_marks)
    history=tuple(x for x in allmarks if x.key in ('R0','E0','ok'))
    records=tuple(predictor.ServiceRecord(r.attempts[k].registration,r.now,
        'right_censored' if k=='R0' else 'completion',None if k=='R0' else r.private_stage1[k],6) for k in ('R0','E0','ok'))
    fitted=predictor.FrozenServiceModel.from_history(records,cutoff=r.now,version='RE_service_interface',
        q_model=r.q_model,joint_opportunities=history)
    assert [m.client for m in fitted.marks]==['ok'] and max(c.risk for c in fitted.cells)==1
    # Public fixture registrations repeat these exact joint records. Excluded
    # R/E records do not query the conditional kernel. Missing ok mark is unknown.
    opportunities=tuple(predictor.PublicOpportunity(x.key+'_next',x.client,r.now+.1,x.device_class,x.network_class,r.now) for x in history)
    model=replace(r.predictor,schedule_complete_until=100.,joint_opportunities=history,opportunities=opportunities,
        resource_model='exogenous_no_shared_contention')
    scenarios=model.sample_scenarios(r.snapshot())
    expect_error(lambda:replace(model,joint_opportunities=tuple(replace(o,clock_run_id='another_run') for o in history)).sample_scenarios(r.snapshot()))
    assert all(len(s.unknowns)==1 and s.unknowns[0].key=='ok_next' for s in scenarios)
    assert all({e.kind for e in s.events}=={'register_outside_R','register_ineligible','register'} for s in scenarios)
    unsafe=replace(model,resource_model='UNDECLARED').sample_scenarios(r.snapshot())
    assert all(sum(u.reason=='EXCLUDED_MESSAGE_RESOURCE_EFFECT_UNKNOWN' for u in s.unknowns)==2 for s in unsafe)
    assert r.backend.local_optimizer_steps==0
    return dict(status='PASS',q_records=frozen,backend_forwarded_training_calls=calls,SGD=0,
        physical_E0=asdict(r.attempts['E0']),all_registration_marks=len(allmarks),retained_records=[asdict(x) for x in history],
        inverse_denominator_keys=preview.keys,restore_identical=True,old_checkpoint_rejected=True,
        conditional_kernel_exclusions=True,unproved_resource_effects_remain_unknown=True,
        caveat='training interface spy and preserved work records; no physical training executed')

def check_unknown():
    r,known=f.make_case();original=copy.deepcopy(r.to_dict());controller=IsolatedController();out={}
    for name,t in [('late_unknown',28.9),('early_unknown',22.2)]:
        unknown=(predictor.UnknownSupport('unknown_mark',t,'NO_COMPATIBLE_MARK'),
                 predictor.UnknownSupport('unknown_tail',t+.05,'INSUFFICIENT_RISK'))
        scenes=(predictor.ConditionalScenario(known,unknown),)*4
        d=controller.decide(r.snapshot(),r.predictor,isolated_scenarios=scenes)
        result=dict(decision=asdict(d),accounting=controller.accounting[-1])
        put('S3_'+name+'_decision.json',result)
        assert d.reason!='CPU_TIMEOUT/fixed_time_2','MECHANISM_CPU_FAILURE'
        frozen=f.read(OUT/('S2_'+name+'.json'))
        for branch in frozen['branches']:
            for (offset,score),row in zip(branch['decision']['plan_scores'],d.intervals):
                assert offset==row['offset'] and row['L']<=score<=row['U']
        assert all(x['known_cells']==([68]*4 if name=='late_unknown' else [1]*4) for x in d.intervals)
        if name=='late_unknown':assert d.proven and d.action=='WAIT' and fixed_fallback(r.snapshot(),'fixed').action=='CLOSE'
        else:assert not d.proven and d.reason=='UNKNOWN_FIXED_TIME_2' and d.action=='CLOSE'
        out[name]=result
    assert r.to_dict()==original
    # Same frozen state with only two delivered clients: WAIT is rule-forced,
    # never reported as a successful interval comparison.
    forced=replace(r.snapshot(),pool=r.snapshot().pool[:2])
    forced_d=evaluate_interval_plans(forced,r.predictor,scenes)
    assert forced_d.reason=='RULE_FORCED' and not forced_d.proven and forced_d.action=='WAIT'
    return dict(status='PASS',decisions=out,enumerated_branches_reused=18,rule_forced=asdict(forced_d),SGD=0)

def check_supported():
    r,known=f.make_case();original=copy.deepcopy(r.to_dict())
    # Known completions plus a public complete empty future catalogue form a
    # full-support common subdomain. Each in-flight record completes next bin.
    cells=tuple(predictor.RiskCell(('public_device','public_network'),i,5,5 if i==5 else 0,0) for i in range(1,6))
    marks=tuple(predictor.JointMark(e.registration.client,e.registration.stratum,e.summary,20.,0) for e in known)
    # These causal empirical marks use exactly the frozen μ payload but their
    # historical Stage1 freeze must precede model.as_of=20.
    marks=tuple(replace(m,summary=f.summary(r.config,r.mu,20.,'mu')) for m in marks)
    model=replace(r.predictor,cells=cells,marks=marks)
    scenes=model.sample_scenarios(r.snapshot())
    assert all(not s.unknowns for s in scenes)
    assert all([e.time for e in s.events]==[22.1]*4 for s in scenes)
    tail_scenes=replace(model,cells=cells[:-1]).sample_scenarios(r.snapshot())
    assert all(len(s.unknowns)==4 and all(u.reason.startswith('INSUFFICIENT_RISK') and abs(u.earliest_effect_time-22.)<1e-9 for u in s.unknowns) for s in tail_scenes)
    controller=IsolatedController();d=controller.decide(r.snapshot(),model)
    result=dict(decision=asdict(d),accounting=controller.accounting[-1]);put('S3_supported_decision.json',result)
    assert d.reason!='CPU_TIMEOUT/fixed_time_2','FULL_SUPPORT_CPU_FAILURE'
    # Original complete v2 evaluator on its original frozen snapshot, matched q=.5.
    from raven_mcs.control.schema import DecisionSnapshot as OldSnapshot
    from raven_mcs.control.predictor import FrozenServiceModel as OldModel,ForecastEvent as OldEvent
    from raven_mcs.control.schema import Registration as OldReg,Stage1Summary as OldSummary
    from raven_mcs.control.planner import evaluate_plans
    raw=f.read(OUT/'S2_INPUT_SNAPSHOT.json')
    events=tuple(OldEvent(e['time'],e['kind'],OldReg(**e['registration']),OldSummary.from_dict(e['summary'])) for e in raw['known_events'])
    old=evaluate_plans(OldSnapshot.from_dict(raw['snapshot']),OldModel.from_dict(raw['model']),(events,)*4)
    for (offset,value),row in zip(old.plan_scores,d.intervals):
        assert offset==row['offset'] and row['L']<=value<=row['U'] and row['U']-row['L']<1e-10
    p=r.preview_release();assert r.to_dict()==original
    theta=r.backend.theta.copy();expected=theta.copy()
    for key,weight in zip(p.keys,p.alpha):expected-=r.settings.server_eta*weight*r.backend.updates[key]
    v=residual(p.alpha,r.settings);assert v<=1e-7
    r.apply_release(p)
    assert np.allclose(r.backend.theta,expected,rtol=0,atol=1e-15)
    assert r.backend.local_optimizer_steps==0 and set(p.keys).issubset(r.consumed)
    return dict(status='PASS',decision=result,old_complete_scores=old.plan_scores,preview_unchanged=True,
        actual_P2_residual=v,actual_weights=p.alpha,preview_masses=p.masses,preview_beta=p.beta,
        apply_theta=r.backend.theta.tolist(),expected_theta=expected.tolist(),SGD=0)

if __name__=='__main__':
    label=sys.argv[1];checks={'RE':check_re,'unknown':check_unknown,'supported':check_supported}
    try:
        result=checks[label]();put('S3_'+label+'_PASS.json',result);print(json.dumps(result,ensure_ascii=False))
    except Exception as exc:
        # Preserve ordinary development feedback. No automatic case or threshold changes.
        put('S3_'+label+'_FAIL_'+sys.argv[2]+'.json',dict(type=type(exc).__name__,error=str(exc),trace=traceback.format_exc()))
        raise
