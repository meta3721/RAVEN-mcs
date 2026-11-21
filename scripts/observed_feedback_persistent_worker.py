"""Resident math-input worker. Loads modules at startup, NEVER solves before READY."""
import sys,json,time,os,hashlib,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_persistent_cost_20261014'
sections=[]
def section(name,fn):
    cpu=time.process_time();wall=time.perf_counter();v=fn()
    sections.append(dict(name=name,CPU=time.process_time()-cpu,wall=time.perf_counter()-wall));return v
def load_modules():
    global np,ControlConfig,P2Settings,ReleaseSummary,Registration,Delivered,DesignConfiguration,IsolatedQ,ArrayBackend,DynamicWindowRunner,Controller,freeze_stage1,RootClient,METHOD_VERSION,methods,original_solve
    import numpy as np
    from raven_mcs_observed_feedback.schema import ControlConfig,P2Settings,ReleaseSummary,Registration,Delivered
    from raven_mcs_observed_feedback.design import DesignConfiguration
    from raven_mcs_observed_feedback.probability import IsolatedQ
    from raven_mcs_observed_feedback.array_backend import ArrayBackend
    from raven_mcs_observed_feedback.lifecycle import DynamicWindowRunner
    from raven_mcs_observed_feedback.controller import Controller
    from raven_mcs_observed_feedback.stage1 import freeze_stage1
    from raven_mcs_observed_feedback.budget_client import RootClient
    from raven_mcs_observed_feedback import METHOD_VERSION
    # The approved initialization may load fixed numerical modules, but no solve.
    from raven_mcs.aggregation import methods
    original_solve=methods.solve_p2
section('fixed_module_imports_no_solver_call',load_modules)
raw=section('static_input_parse',lambda:json.loads((OUT/'FROZEN_INPUT.json').read_text()))
solver_calls=[]
def measured_original_solver(*args,**kwargs):
    cpu=time.process_time();wall=time.perf_counter()
    try:return original_solve(*args,**kwargs)
    finally:solver_calls.append(dict(CPU=time.process_time()-cpu,wall=time.perf_counter()-wall))
methods.solve_p2=measured_original_solver # Instrumentation only: same original callable, arguments/result untouched.
def build():
    config=ControlConfig('authorized_math_fixture',DesignConfiguration(True,'explicit_preconfigured_fixture'))
    r=DynamicWindowRunner(config=config,settings=P2Settings(),mu=raw['mu'],q_model=IsolatedQ(),backend=ArrayBackend([0.]),seed=0,
        open_time=20.,isolated_test=True,data_identity='MATH_FIXTURE',target_identity='published_frozen_mu_172',
        probability_applicability=dict(consumption_policy=METHOD_VERSION,T=100,service={'kind':'public_math_fixture'}),
        clock_namespace=dict(run_id='cold_fixture_20261014',origin_utc='2026-10-14T00:00:00Z',unit='controlled_service_unit'))
    r.model_version=1;r.now=20.5;r.debt=tuple(max(0.,.01*(m-o)) for m,o in zip(raw['mu'],raw['prior_omega']))
    r.last_release=ReleaseSummary(20.,.5*sum(abs(m-o) for m,o in zip(raw['mu'],raw['prior_omega'])),0.,1.,tuple(raw['prior_omega']))
    stages_cpu=history_cpu=0.
    for c in raw['clients']:
        reg=Registration(c['key'],c['client'],c['registered_at'],c['downloaded_version'],c['device_class'],c['network_class'])
        at=time.process_time()
        summary=freeze_stage1(config=config,target_opportunity=c['target_opportunity'],lagged_opportunity=c['lagged_opportunity'],
            p_obs=c['p_obs'],observation=c['observation'],group_ids=c['group_ids'],num_groups=172,now=c['registered_at'],
            estimator_as_of=20.,estimator_version='public_math_fixture_only',provenance='frozen_explicit_input_no_future')
        stages_cpu+=time.process_time()-at;at=time.process_time()
        q=IsolatedQ(c['q']).predict_at_registration(r.registration_features(reg))
        history_cpu+=time.process_time()-at
        r.pool[c['client']]=Delivered(reg,summary,q,c['completed_at']);r.variance[c['client']]=c['variance']
    sections.append(dict(name='stage1_subsection_of_fixture_build',CPU=stages_cpu,overlapping=True))
    sections.append(dict(name='registration_history_subsection_of_fixture_build_43_calls',CPU=history_cpu,overlapping=True,
        role='old artificial fixture provenance reconstruction, not a required online controller computation'))
    return r
r=section('static_fixture_resources_and_conditional_history',build)
controller=Controller(root_budget=RootClient(OUT/'ROOT_BUDGET_LIVE.json'),save_reserve=5.96875,operation_root_ceiling=2.)
initial_fingerprint=r.snapshot().fingerprint;assert not solver_calls and not r.cache.values and r.cache.solves==0
ready=dict(kind='READY',pid=os.getpid(),CPU=time.process_time(),sections=sections,solver_calls=0,cache_entries=0,
    fingerprint=initial_fingerprint,input_hash=hashlib.sha256((OUT/'FROZEN_INPUT.json').read_bytes()).hexdigest(),resident=True)
print(json.dumps(ready,separators=(',',':')),flush=True)
responses=[];bindings=[];completed=0
for line in sys.stdin:
    local_cpu=time.process_time();wall=time.perf_counter();request=json.loads(line)
    if request['op']=='FINALIZE':
        before=time.process_time()
        numeric=bindings[0].numeric if bindings else None
        audit=dict(READY=ready,responses=responses,solver_calls=solver_calls,
            numeric=numeric.to_dict() if numeric else None,input_role=raw['role'],sections=sections,
            same_state_fingerprint=r.snapshot().fingerprint==initial_fingerprint,
            consumed_keys=len(r.consumed),closures=len(r.closures),SGD=r.backend.local_optimizer_steps,
            current_now=r.now,window_open=r.window_open,model_version=r.model_version)
        if numeric:
            a=np.asarray(numeric.alpha);omega=np.asarray(numeric.omega);mu=np.asarray(r.mu);beta=np.asarray(numeric.beta)
            pool=r.snapshot().pool;ages=np.asarray([r.model_version-m.registration.downloaded_version for m in pool])/5
            variance=np.asarray([r.variance[m.registration.client]/max(m.summary.effective_n,1.)+.0001 for m in pool])
            audit['objective_terms']=dict(debt=-float(np.asarray(r.debt)@omega),group=.5*float(np.square(omega-mu).sum()),
                reference=.5*float(np.square(a-beta).sum()),variance=.05*float((variance*np.square(a)).sum()),staleness=.1*float(ages@a))
        (OUT/'FULL_WORKER_AUDIT.json').write_text(json.dumps(audit,indent=2,allow_nan=False))
        print(json.dumps(dict(kind='FINALIZED',CPU=time.process_time(),dump_CPU=time.process_time()-before,
            completed_requests=completed,solver_calls=len(solver_calls))),flush=True);break
    if request['op']!='DECIDE' or request['label']!=('A' if completed==0 else 'B') or completed>=2:raise RuntimeError('unauthorized request')
    if request['input_hash']!=ready['input_hash']:raise RuntimeError('input identity changed')
    before_fp=r.snapshot().fingerprint;count_before=len(solver_calls)
    try:
        d=controller.decide(r,use_cache=True);p=d.preview
        assert r.snapshot().fingerprint==before_fp==initial_fingerprint
        assert p.fingerprint==r.snapshot().fingerprint
        from raven_mcs_observed_feedback.preview import p2_dependency_hash
        assert p.dependency_hash==p2_dependency_hash(r.snapshot())
        # Every field required by actual apply_release remains in the returned bound preview.
        assert np.allclose(np.asarray(p.M)@np.asarray(p.alpha),p.omega,rtol=0,atol=1e-12)
        binding_new=not bindings or p is not bindings[-1]
        reused_numeric=bool(bindings and p.numeric is bindings[0].numeric)
        bindings.append(p)
        payload=dict(kind='RESPONSE',label=request['label'],pid=os.getpid(),action=d.action,reason=d.reason,B=d.B,components=d.components,
            preview=dict(fingerprint=p.fingerprint,dependency_hash=p.dependency_hash,keys=p.keys,alpha=p.alpha,M=p.M,
                omega=p.omega,ell=p.ell,age=p.age),P2=d.p2_solves,cache=d.cache_hits,
            original_solver_calls=len(solver_calls)-count_before,solver_sections=solver_calls[count_before:],
            current_binding_valid=True,new_binding_object=binding_new,reused_numeric_object=reused_numeric,
            now=r.now,window_open=r.window_open,model_version=r.model_version,Controller_CPU=d.process_CPU,
            worker_CPU_before_response=time.process_time(),request_local_CPU_before_json=time.process_time()-local_cpu,
            request_local_wall_before_json=time.perf_counter()-wall,error=None)
    except Exception as exc:
        traceback.print_exc();payload=dict(kind='RESPONSE',label=request['label'],error=repr(exc),pid=os.getpid())
    serialized=json.dumps(payload,separators=(',',':'),allow_nan=False)
    print(serialized,flush=True)
    responses.append(dict(label=request['label'],response_bytes=len(serialized.encode()),
        request_CPU_including_response_serialization=time.process_time()-local_cpu,request_wall=time.perf_counter()-wall,
        success=payload['error'] is None));completed+=1
