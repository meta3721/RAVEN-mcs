"""Frozen S2 finite-branch proof check. No fitting, SGD or data collection."""
from dataclasses import asdict,replace
import copy
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np
from raven_mcs.control.schema import ControlConfig,P2Settings,Registration,ReleaseSummary,DecisionSnapshot
from raven_mcs.sag.r1l_design import DesignConfiguration
from raven_mcs.control.stage1 import freeze_stage1
from raven_mcs.control.probability import EvidenceLogisticQ,policy_context_hash
from raven_mcs.control.predictor import FrozenServiceModel,ForecastEvent
from raven_mcs.control.lifecycle import DynamicWindowRunner,ArrayBackend
from raven_mcs.control.planner import evaluate_plans,candidate_offsets,fixed_fallback,_ForecastState
from raven_mcs.utils.hashing import sha256_file,sha256_json
from revision_feasibility_budget import ROOT,OUT,REPORT

OLD=ROOT/'results_calibration_first_20261013'
VERSION='reachability_stop/conditional-bundle-RE-interval-v3'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)

def float_envelope(k=43,g=172):
    # Outward bounds for accepted alpha residual, nonnegative M/mu and sums.
    u=np.finfo(float).eps
    da=1e-7+8*k*u
    dm=1e-9+2*g*u
    gamma=2*g*u/(1-2*g*u)
    absalpha=1+(2*k+1)*da
    ell=.5*((1+gamma)*absalpha+(1+dm))*(1+gamma)
    age_upper=1+(k+1)*da
    duration=4+1e-9+1e-10+2*100*u
    arithmetic=64*(g+k+1)*u
    low=math.nextafter(-.02*k*da-arithmetic,-math.inf)
    high=math.nextafter(ell+.02*age_upper+.05*duration+arithmetic,math.inf)
    return dict(exact_lower=0,exact_upper=1.22,float_lower=low,float_upper=high,
        K_max=k,G=g,alpha_residual=1e-7,clock_comparison=1e-9,round_10_digits_half_unit=5e-11,
        numerical_margin_only=True)

def summary(config,mu,when,kind):
    n=len(mu)
    if kind=='mu':
        target=list(mu);opp=[1/n]*n;groups=list(range(n))
    else:
        target=[.1,.2,.3,.4];opp=[.25]*4;groups=[int(kind)]*4
    return freeze_stage1(config=config,target_opportunity=target,lagged_opportunity=opp,
        p_obs=[.5]*len(target),observation=[1]*len(target),group_ids=groups,num_groups=n,now=when,
        estimator_as_of=20.,estimator_version='S2_fixed_stage1',provenance='hand_authored_legal_fixture_not_TRAFFIC_samples')

def make_case():
    plan=read(OLD/'ACQUISITION_FROZEN_PLAN.json')
    # Read the frozen target from the validated current causal checkpoint.
    mu=tuple(read(OLD/'trajectory/FAILED_tick0201.json')['state']['mu'])
    config=ControlConfig('S1_frozen_finite_branch_fixture',DesignConfiguration(True,'S1_explicit_on'))
    q=EvidenceLogisticQ('S2_isolated_q_half_not_calibrated',20.,'S2_fixture',(0.,)*5,
        (('public_device','public_network'),),1000,
        policy_context_hash(config,P2Settings(),mu,'S2_frozen'),role='isolated_test_input')
    model=FrozenServiceModel('S2_frozen',20.,(),(),q.to_dict(),schedule_complete_until=100.)
    r=DynamicWindowRunner(config=config,settings=P2Settings(),mu=mu,predictor=model,q_model=q,
        backend=ArrayBackend([1.,2.,3.]),seed=26004,experiment_end=100.,open_time=20.,isolated_test=True,
        data_identity=sha256_json('S1_hand_authored_only'),target_identity=sha256_json(mu))
    # One legal preceding release supplies last_release and version1; no SGD.
    init=Registration('init','initial',20.,0,'public_device','public_network')
    r.on_register(init,summary(config,mu,20.,0));r.on_completion('init',20.,update=[.1,.2,.3])
    r.apply_release(r.preview_release())
    for i in range(4):
        reg=Registration(f'old{i}',f'c{i}',20.5,1,'public_device','public_network')
        r.on_register(reg,summary(config,mu,20.5,0))
    for i in range(4):r.on_completion(f'old{i}',21.,update=[.1,.2,.3])
    regs=[]
    for i in range(4):
        reg=Registration(f'new{i}',f'c{i}',21.6,1,'public_device','public_network')
        r.on_register(reg,summary(config,mu,21.6,'mu'));regs.append(reg)
    r.advance_time(22.)
    known=tuple(ForecastEvent(22.1,'completion',reg,summary(config,mu,21.6,'mu')) for reg in regs)
    assert np.allclose(np.array(known[0].summary.composition),mu,rtol=0,atol=1e-12)
    return r,known

def branch_events(r,known,early,mark_branch,tail_branch):
    t=22.2 if early else 28.9
    a=Registration('unknown_mark','c0',t,0,'public_device','public_network')
    b=Registration('unknown_tail','c0',round(t+.05,10),0,'public_device','public_network')
    events=list(known)+[ForecastEvent(t,'register',a),ForecastEvent(b.registered_at,'register',b)]
    if mark_branch=='failure':events.append(ForecastEvent(round(t+.1,10),'failure',a))
    else:events.append(ForecastEvent(round(t+.1,10),'completion',a,summary(r.config,r.mu,t,mark_branch)))
    if tail_branch!='pending':
        events.append(ForecastEvent(round(t+float(tail_branch),10),'completion',b,summary(r.config,r.mu,b.registered_at,'mu')))
    return tuple(sorted(events,key=lambda e:(e.time,0 if e.kind=='register' else 1,e.registration.key)))

def observed_evaluation(snapshot,model,events,*,horizon=8.,offsets=None):
    """Instrument the original evaluator; never substitute a reduced score/P2."""
    samples=[];closures=[];bounds=float_envelope(g=len(snapshot.mu))
    old_score=ReleaseSummary.score;old_release=_ForecastState.release
    def score(value,config):
        actual=old_score(value,config)
        assert bounds['float_lower']<=actual<=bounds['float_upper'],(value,actual,bounds)
        assert value.duration<=4+1.1001e-9
        samples.append(actual);return actual
    def release(state,cache,counters):
        old_release(state,cache,counters)
        closures.append(dict(time=state.now,version=state.version,debt=list(state.debt),consumed=sorted(state.consumed)))
    try:
        ReleaseSummary.score=score;_ForecastState.release=release
        cpu=time.process_time();wall=time.perf_counter()
        d=evaluate_plans(snapshot,model,(events,)*4,offsets=offsets,horizon=horizon)
        c=time.process_time()-cpu;w=time.perf_counter()-wall
    finally:ReleaseSummary.score=old_score;_ForecastState.release=old_release
    offsets=candidate_offsets(snapshot) if offsets is None else offsets
    n=int(round(horizon/.1));assert len(samples)==len(offsets)*4*n,(len(samples),len(offsets),n)
    cube=np.array(samples).reshape(len(offsets),4,n)
    for j,(_,value) in enumerate(d.plan_scores):assert abs(cube[j].mean()-value)<1e-12
    return d,cube,dict(CPU=c,wall=w,p2_solves=d.p2_solves,cache_hits=d.cache_hits,closures=closures)

def interval_decision(offsets,rows,fallback):
    grouped={}
    for a in ('CLOSE','WAIT'):
        inds=[i for i,o in enumerate(offsets) if (o==0)==(a=='CLOSE')]
        if not inds:continue
        lower=min(rows[i][0] for i in inds);upper=min(rows[i][1] for i in inds)
        witnesses=[i for i in inds if rows[i][1]<=upper+1e-7]
        grouped[a]=dict(L=lower,U=upper,witness_offset=min(offsets[i] for i in witnesses))
    if len(grouped)==1:return dict(action=next(iter(grouped)),reason='RULE_FORCED',groups=grouped,proven=False)
    winners=[a for a,x in grouped.items() if x['U']+1e-7<min(y['L'] for b,y in grouped.items() if a!=b)]
    assert len(winners)<=1
    return dict(action=winners[0] if winners else fallback.action,reason='INTERVAL_PROVEN' if winners else 'UNKNOWN_FIXED_TIME_2',
        groups=grouped,proven=bool(winners),fixed_time_2=fallback.action)

def inspect_causal_snapshot():
    s=read(OLD/'trajectory/FAILED_tick0201.json')['state'];f=read(OLD/'trajectory/SERVICE_FROZEN_AT_20.json')
    assert s['now']==20.1 and f['source_cutoff']==20
    marks={(m['client'],*m['stratum']) for m in f['model']['marks']}
    candidates=[]
    for o in f['model']['opportunity_history']:
        attempt=s['attempts'][o['key']]
        if attempt['terminal_reason']=='no_observations' or attempt['features']['model_age']>5:continue
        key=(o['client'],o['device_class'],o['network_class'])
        if key not in marks:
            at=math.floor(s['now'])+o['time']%1
            if at<=s['now']:at+=1
            candidates.append(dict(original_key=o['key'],query_key=key,possible_historical_batch_register_time=at))
    cutoff=min(x['possible_historical_batch_register_time'] for x in candidates)
    k=sum(round(s['now']+.1*i,10)<cutoff-1e-10 for i in range(1,81))
    return dict(snapshot='FAILED_tick0201.json',now=s['now'],pool=len(s['pool']),candidate_missing_marks=candidates,
        conservative_shared_state_cutoff=cutoff,exact_earliest_score_effect='not established; no tighter-prefix claim',
        N=80,k=k,total_four_scenario_cells=320,common_known_cells=4*k,can_prove_action=False,
        basis='union of legal historical batches, R/E from all <=20 registrations; coarse common envelope, not seeded replay',
        q_role='isolated_development_use_of_old_diagnostic_prior',no_new_scene_draw=True,no_final_state_input=True)

if __name__=='__main__':
    # Capture frozen specification and code before the first numerical use.
    save('S1_FROZEN_INPUTS.json',dict(method=VERSION,spec_sha256=sha256_file(REPORT/'REVISION_SPEC_FROZEN.md'),
        script_sha256=sha256_file(Path(__file__)),late_register=[28.9,28.95],early_register=[22.2,22.25],
        branch_product=[['mu',1,'failure'],[.3,.5,'pending']],source_mu='FAILED_tick0201.state.mu',
        constants='unchanged',no_search=True))
    r,known=make_case();snapshot=r.snapshot();before=copy.deepcopy(r.to_dict());offsets=candidate_offsets(snapshot)
    save('S2_INPUT_SNAPSHOT.json',dict(snapshot=asdict(snapshot),model=r.predictor.to_dict(),known_events=[asdict(e) for e in known]))
    result=dict(method=VERSION,envelope=float_envelope(),cases={},development_snapshot=inspect_causal_snapshot())
    all_checks=[]
    for name,early,k in [('late_unknown',False,68),('early_unknown',True,1)]:
        prefix,pcube,cost=observed_evaluation(snapshot,r.predictor,known,horizon=k*.1,offsets=offsets)
        b=result['envelope'];n=80;A=pcube.sum(axis=2).mean(axis=1)
        rows=[(math.nextafter((a+(n-k)*b['float_lower'])/n,-math.inf),
               math.nextafter((a+(n-k)*b['float_upper'])/n,math.inf)) for a in A]
        action=interval_decision(offsets,rows,fixed_fallback(snapshot,'fixed_time_2'))
        item=dict(k=k,N=n,intervals=[dict(offset=o,L=x[0],U=x[1]) for o,x in zip(offsets,rows)],
            decision=action,prefix_cost=cost,branches=[])
        for mark,tail in itertools.product(['mu',1,'failure'],[.3,.5,'pending']):
            events=branch_events(r,known,early,mark,tail)
            d,cube,measured=observed_evaluation(snapshot,r.predictor,events)
            same=np.allclose(cube[:,:,:k],pcube,rtol=0,atol=1e-12)
            included=all(lo<=v<=hi for (_,v),(lo,hi) in zip(d.plan_scores,rows))
            all_checks.extend([same,included])
            item['branches'].append(dict(mark=mark,tail=tail,decision=asdict(d),prefix_same=bool(same),included=bool(included),cost=measured))
        result['cases'][name]=item
        save('S2_'+name+'.json',item)
    late=result['cases']['late_unknown']['decision'];early=result['cases']['early_unknown']['decision']
    checks=dict(all_branch_intervals_contain=all(all_checks),late_nontrivial=late['proven'] and late['action']!=late['fixed_time_2'],
        early_fallback=not early['proven'] and early['reason']=='UNKNOWN_FIXED_TIME_2',
        actual_state_unchanged=r.to_dict()==before,SGD_zero=r.backend.local_optimizer_steps==0)
    result.update(checks=checks,status='PASS' if all(checks.values()) else 'FAIL',training=0,q_fit=0,new_acquisition=0)
    save('S2_RESULT.json',result)
    print(json.dumps(dict(status=result['status'],checks=checks,late=late,early=early,development=result['development_snapshot']),ensure_ascii=False))
    if not all(checks.values()):raise SystemExit(2)
