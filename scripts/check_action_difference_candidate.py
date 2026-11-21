"""One frozen early-unknown state: exact full-P2 paired counterexamples."""
from dataclasses import asdict
import itertools,json,time,copy,math
from pathlib import Path
import numpy as np
import revision_feasibility_s2 as f
from action_difference_revision_budget import ROOT,OUT,REPORT
from raven_mcs_re_interval import schema,probability,predictor,lifecycle,stage1
from raven_mcs_re_interval.planner import evaluate_plans,_ForecastState
from raven_mcs.utils.hashing import sha256_file,sha256_json

for module,names in [(schema,['ControlConfig','P2Settings','Registration','ReleaseSummary','DecisionSnapshot']),
    (probability,['EvidenceLogisticQ','policy_context_hash']),(predictor,['FrozenServiceModel','ForecastEvent']),
    (lifecycle,['DynamicWindowRunner','ArrayBackend']),(stage1,['freeze_stage1'])]:
    for name in names:setattr(f,name,getattr(module,name))

if __name__=='__main__':
    frozen=dict(spec_sha256=sha256_file(REPORT/'CANDIDATE_CHECK_FROZEN.md'),script_sha256=sha256_file(Path(__file__)),
        unknown_registration=[22.2,22.25],qualities=[0,1],completion_times=[22.3,22.7,23.2,24.2,29.9],
        first_failure=22.3,tail=['mu_at_22.6','failure_at_22.6','pending'],states=1,branches=33,
        purpose='legal-subset counterexamples; subset min/max are not outer bounds for full Z')
    (OUT/'C_FROZEN_INPUTS.json').write_text(json.dumps(frozen,indent=2))
    r,known=f.make_case();snapshot=r.snapshot();before=sha256_json(r.to_dict());offsets=(0.,.1,.5,1.,2.)
    primary=[('completion',quality,t) for quality,t in itertools.product([0,1],frozen['completion_times'])]+[('failure',None,22.3)]
    result=[];closures=[];original=_ForecastState.release
    def capture(state,cache,counters):
        original(state,cache,counters)
        closures.append(dict(time=state.now,version=state.version,open=state.open,debt=list(state.debt),
            consumed=sorted(state.consumed),last=asdict(state.last) if state.last else None))
    _ForecastState.release=capture;start_cpu=time.process_time();start_wall=time.perf_counter()
    try:
        for i,((kind,quality,t),tail) in enumerate(itertools.product(primary,frozen['tail'])):
            a=schema.Registration('early_unknown_mark','c0',22.2,0,'public_device','public_network')
            b=schema.Registration('early_unknown_tail','c0',22.25,0,'public_device','public_network')
            events=list(known)+[predictor.ForecastEvent(22.2,'register',a),predictor.ForecastEvent(22.25,'register',b)]
            events.append(predictor.ForecastEvent(t,kind,a,None if kind=='failure' else f.summary(r.config,r.mu,22.2,quality)))
            if tail!='pending':events.append(predictor.ForecastEvent(22.6,'completion' if tail=='mu_at_22.6' else 'failure',b,
                f.summary(r.config,r.mu,22.25,'mu') if tail=='mu_at_22.6' else None))
            events=tuple(sorted(events,key=lambda e:(e.time,0 if e.kind=='register' else 1,e.registration.key)))
            closures.clear();c=time.process_time();w=time.perf_counter()
            d=evaluate_plans(snapshot,r.predictor,(events,)*4,offsets=offsets)
            close=d.plan_scores[0][1];deltas={str(o):score-close for o,score in d.plan_scores[1:]}
            row=dict(branch=i,primary=dict(kind=kind,quality=quality,time=t),tail=tail,scores=d.plan_scores,deltas=deltas,
                P2=d.p2_solves,cache=d.cache_hits,CPU=time.process_time()-c,wall=time.perf_counter()-w,
                closures=copy.deepcopy(closures))
            result.append(row)
    finally:_ForecastState.release=original
    witnesses={}
    for p in offsets[1:]:
        key=str(p);values=[x['deltas'][key] for x in result]
        lo=min(values);hi=max(values)
        witnesses[key]=dict(subset_min=lo,subset_max=hi,negative_branch=values.index(lo),positive_branch=values.index(hi),
            full_set_lower_must_be_at_most=math.nextafter(lo+1e-10,math.inf),
            full_set_upper_must_be_at_least=math.nextafter(hi-1e-10,-math.inf),
            excludes_robust_WAIT=hi>1e-7+1e-10)
    no_wait=all(x['excludes_robust_WAIT'] for x in witnesses.values())
    no_close=any(x['subset_min']<-(1e-7+1e-10) for x in witnesses.values())
    immutable=before==sha256_json(r.to_dict()) and r.backend.local_optimizer_steps==0
    summary=dict(status='FAIL_NO_CERTIFIABLE_ACTION_ON_FROZEN_EARLY_CASE' if no_wait and no_close else 'REQUIRES_BOUND_PROOF',
        witnesses=witnesses,all_WAIT_have_legal_positive_counterexample=no_wait,CLOSE_has_legal_negative_counterexample=no_close,
        branches=33,full_P2=True,common_exogenous_diagonal_is_subset_not_constraint=True,
        input_state_unchanged=immutable,total_CPU=time.process_time()-start_cpu,total_wall=time.perf_counter()-start_wall,
        total_P2=sum(x['P2'] for x in result),total_cache=sum(x['cache'] for x in result),
        timing_role='in-process counterexample calculation; not production 2-CPU planning acceptance',
        training=0,new_trajectories=0,novelty='needs-search',D_authorized_to_run=not(no_wait and no_close))
    with (OUT/'C_BRANCHES.json').open('x') as out:json.dump(result,out,indent=2,allow_nan=False)
    with (OUT/'C_RESULT.json').open('x') as out:json.dump(summary,out,indent=2,allow_nan=False)
    assert immutable
    print(json.dumps(summary))
