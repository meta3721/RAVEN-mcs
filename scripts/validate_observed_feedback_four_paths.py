"""One resident worker, four frozen deterministic interface cases, zero SGD."""
import json,time,copy,traceback,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'results_observed_feedback_implementation_20261013'
ROOT=OUT.parent
BATCH=OUT
if len(sys.argv)>1:
    OUT=BATCH/sys.argv[1];OUT.mkdir(exist_ok=False)
# No scientific imports before the first request's start (baseline is root zero).
measurements=[];case_results={};request_number=0

def root_sample_after(wall):
    sharing_failures=0
    while True:
        try:
            from raven_mcs_observed_feedback.budget_client import read_shared_json
            value=read_shared_json(BATCH/'ROOT_BUDGET_LIVE.json')
        except PermissionError:
            sharing_failures+=1
            if sharing_failures>=10:raise
            time.sleep(.005);continue
        if not value['finished'] and value['wall_stamp']>=wall+.01:return value
        time.sleep(.005)

def operation(label,fn,*,judgement=False,first=False):
    global request_number
    begin=None if first else root_sample_after(time.perf_counter())
    cpu=time.process_time();wall=time.perf_counter()
    error=None
    try:value=fn()
    except Exception as exc:
        error=exc;value=None
    done=time.perf_counter();end=root_sample_after(done)
    charged=end['command_used']-(0. if first else begin['command_used'])
    if first:charged+=json.loads((BATCH/'LAUNCH_COST.json').read_text())['launcher_bootstrap_CPU']
    local=time.process_time()-cpu
    monitor_delta=end['driver_CPU']-(0. if first else begin['driver_CPU'])
    # Root Job statistics may be quantized/lagged at a short interval. Raising
    # the bound with the independently observed PID floor is conservative;
    # do not add that PID to the Job or change the root scheduling ledger.
    upper=max(charged+.02,local+monitor_delta+.02)
    row=dict(label=label,judgement=judgement,first_includes_startup=first,root_sample_difference_CPU=charged,
        conservative_root_upper_CPU=upper,process_CPU=local,root_monitor_delta_CPU=monitor_delta,PID_floor_not_added_to_batch=True,wall=time.perf_counter()-wall,
        root_id=end['root_id'],root_sequence=end['sequence'],P2=getattr(value,'p2_solves',None),cache=getattr(value,'cache_hits',None))
    if error is not None:row['error']=repr(error)
    measurements.append(row);flush()
    if judgement and upper>2.:raise RuntimeError('REPRESENTATIVE_ROOT_REQUEST_EXCEEDS_2_CPU: '+label)
    if error is not None:raise error
    return value

def flush():
    (OUT/'LIVE_FOUR_PATH_EVIDENCE.json').write_text(json.dumps(dict(measurements=measurements,cases=case_results),indent=2,allow_nan=False),encoding='utf-8')

def expect(exception,fn):
    try:fn()
    except exception as exc:return repr(exc)
    raise AssertionError('expected rejection: '+str(exception))

def make_runner(*,mu=(.5,.5),open_time=0.,backend=None,isolated=True,q=None):
    config=ControlConfig('OF-v1/frozen-interface-case',DesignConfiguration(True,'explicit_fixture_on'))
    return DynamicWindowRunner(config=config,settings=P2Settings(),mu=mu,q_model=q or IsolatedQ(),backend=backend or ArrayBackend([1.,2.,3.]),
        seed=26004,open_time=open_time,isolated_test=isolated,data_identity=sha256_json('explicit_math_fixture'),target_identity=sha256_json(mu),
        probability_applicability=dict(consumption_policy=METHOD_VERSION,T=100.,service={'resource_model':'interface_fixture_no_service_prediction'},
            learning={'mode':'SGD0 hand-authored tensor'},stage1={'role':'isolated_given_input'},data_identity='fixture',target_identity=sha256_json(mu)),
        clock_namespace=dict(run_id='OF-v1-math-fixture',origin_utc='2026-10-13T00:00:00Z',unit='controlled_service_unit'))

def summary(r,t,composition):
    return freeze_stage1(config=r.config,target_opportunity=list(composition),lagged_opportunity=[1/len(composition)]*len(composition),
        p_obs=[.5]*len(composition),observation=[1]*len(composition),group_ids=list(range(len(composition))),num_groups=len(composition),
        now=t,estimator_as_of=0.,estimator_version='declared-math-input',provenance='isolated_public_support_not_Traffic')

def add(r,key,cid,t,composition,*,complete=None,download=None,update=None):
    reg=Registration(key,cid,t,max(0,r.model_version-2) if download is None else download,'fixture_device','fixture_network')
    value=r.on_register(reg,summary(r,t,composition))
    if complete is not None:r.on_completion(key,complete,update=[.1,.2,.3] if update is None else update)
    return value

def fill(r,prefix,t,comp,*,completion=None,update=None):
    # All registration headers at t precede all notifications at completion.
    for i in range(3):add(r,prefix+str(i),'c'+str(i),t,comp,update=update)
    if completion is not None:
        for i in range(3):r.on_completion(prefix+str(i),completion,update=[.1,.2,.3] if update is None else update)

def close(r,t,reason='UNIT_FORCED'):
    r.advance_time(t);return r.apply_release(r.preview_release(),reason=reason)

def history(direction):
    r=make_runner();pure=(0.,1.) if direction=='first' else (1.,0.)
    tail=[(.8,.2),(.2,.8)] if direction=='first' else [(.2,.8),(.8,.2)]
    for i,comp in enumerate([pure]*6+tail,1):
        fill(r,'h'+str(i)+'_',i-.2,comp,completion=i-.1);close(r,float(i),'WARMUP')
    for i in range(9,21):close(r,float(i),'WARMUP')
    fill(r,'current_',20.1,(.8,.2),completion=20.2);r.advance_time(20.4)
    return r

def path1():
    a,b=operation('P1_construct_8_release_histories',lambda:(history('first'),history('second')))
    da=operation('P1_history_Q_first',lambda:controller.decide(a),judgement=True)
    db=operation('P1_history_Q_second',lambda:controller.decide(b),judgement=True)
    assert (da.action,db.action)==('CLOSE','WAIT')
    np.testing.assert_allclose(da.preview.alpha,db.preview.alpha,atol=1e-7,rtol=0)
    np.testing.assert_allclose(da.preview.omega,db.preview.omega,atol=1e-10,rtol=0)
    assert abs(da.preview.ell-db.preview.ell)<1e-10 and abs(da.preview.age-db.preview.age)<1e-10
    ablations=[operation('P1_no_Q_stop_'+x,lambda r=r:controller.decide(r,diagnostic_no_debt=True),judgement=True) for x,r in [('a',a),('b',b)]]
    assert [d.action for d in ablations]==['WAIT','WAIT']
    # Full P2 objective includes different raw Q even though singleton omega agrees.
    objective_diff=da.preview.solver['objective_actual_weights']-db.preview.solver['objective_actual_weights']
    assert abs(objective_diff+.018)<1e-8
    zero=make_runner()
    for i in range(1,4):fill(zero,'z'+str(i),i-.2,(.5,.5),completion=i-.1);close(zero,float(i),'WARMUP')
    for i in range(4,21):close(zero,float(i),'WARMUP')
    fill(zero,'zero_',20.1,(.5,.5),completion=20.2);zero.advance_time(20.4)
    boundary=operation('P1_patience_elapsed_0.4',lambda:controller.decide(zero),judgement=True)
    assert boundary.action=='WAIT' and abs(boundary.B-.02)<1e-10 and abs(dict(boundary.components)['b'])<1e-10
    zero.advance_time(20.5);later=operation('P1_patience_elapsed_0.5',lambda:controller.decide(zero),judgement=True)
    assert later.action=='CLOSE' and abs(later.B-.025)<1e-10
    mu=json.loads((ROOT/'results_calibration_first_20261013/trajectory/FAILED_tick0201.json').read_text())['state']['mu']
    assert len(mu)==172
    adapted=make_runner(mu=mu,open_time=20.);fill(adapted,'adapt_',20.1,mu,completion=20.2)
    target_check=operation('P1_actual_frozen_172_mu_adapter',lambda:controller.decide(adapted),judgement=True)
    assert len(target_check.preview.omega)==172 and target_check.preview.ell<1e-7
    return dict(status='PASS',histories='8 actual full-P2 warmup commits each; Q=0.03 directional, model_version=8; empty warmup to20',
        data_role='math_fixture_not_Traffic_reachability',debt=[a.debt,b.debt],actions=[da.to_dict(),db.to_dict()],
        no_Q_actions=[d.to_dict() for d in ablations],P2_Q_objective_difference=objective_diff,
        patience=[boundary.to_dict(),later.to_dict()],frozen_mu_172=target_check.to_dict(),SGD=0)

def path2():
    r=make_runner(open_time=20.);q=add(r,'old','c',20.,(.8,.2),complete=20.1,download=0)
    add(r,'new','c',20.1,(.2,.8));add(r,'failed','f',20.1,(.5,.5));add(r,'aged_pending','old_pending',20.1,(.5,.5),download=0)
    r.on_completion('new',20.2,update=[.1,.2,.3]);r.on_failure('failed',20.2,reason='network_failure')
    assert r.attempts['old'].terminal_reason=='superseded' and r.pool['c'].key=='new' and r.attempts['failed'].consumed==0
    frozen_q=asdict(q);p=r.private_stage1['new'].p_obs;ratio=r.private_stage1['new'].ratio
    before=r.snapshot().fingerprint
    # Deliberately perturb only an uncompleted private payload, not public header.
    r.private_stage1['aged_pending']=summary(r,20.1,(.99,.01))
    assert r.snapshot().fingerprint==before
    d=operation('P2_K_below_three',lambda:controller.decide(r),judgement=True);assert d.reason=='MIN_CLIENTS' and d.p2_solves==0
    r.diagnostic(gate=0,state='RESET');r.diagnostic(gate=1,state='WARMUP')
    assert r.snapshot().fingerprint==before and r.config.design.enabled
    expect(InputError,lambda:r.freeze_next_q(IsolatedQ(.9)))
    assert asdict(r.attempts['old'].q)==frozen_q and r.private_stage1['new'].p_obs==p and r.private_stage1['new'].ratio==ratio
    empty_summary=freeze_stage1(config=r.config,target_opportunity=[.5,.5],lagged_opportunity=[.5,.5],p_obs=[.5,.5],
        observation=[0,0],group_ids=[0,1],num_groups=2,now=20.2,estimator_as_of=0.,estimator_version='declared-math-input',provenance='R0-isolated')
    rq=r.on_register(Registration('R0','unobserved',20.2,0,'fixture_device','fixture_network'),empty_summary)
    assert rq.role=='outside_R' and r.attempts['R0'].R==0 and r.attempts['R0'].consumed==0
    expect(InputError,lambda:r.start_local_training('R0',[],authorization=None))
    expect(InputError,lambda:r.on_completion('aged_pending',20.2,update=[.1,.2,.3]))
    actual=[]
    for t in (24.,28.,32.,36.,40.,44.):
        if not r.pool:add(r,'deadline'+str(t),'c',t-.1,(.8,.2),complete=t-.05,download=r.model_version)
        r.advance_time(t);decision=operation('P2_deadline_'+str(t),lambda:controller.decide(r),judgement=True)
        assert decision.reason=='DEADLINE'
        actual.append(operation('P2_commit_'+str(t),lambda:r.apply_release(decision.preview,reason=decision.reason)))
    assert r.model_version==6 and r.attempts['aged_pending'].terminal_reason=='expired'
    same=(r.debt,copy.deepcopy(r.variance),r.last_release,r.model_version)
    r.advance_time(48.);empty=operation('P2_empty_deadline',lambda:controller.decide(r),judgement=True)
    r.apply_release(r.preview_release(),reason=empty.reason)
    assert same==(r.debt,r.variance,r.last_release,r.model_version)
    add(r,'pending_to_T','pending',48.1,(.5,.5),download=r.model_version)
    r.finish_observation();assert r.attempts['pending_to_T'].right_censored_at==48.1 and r.attempts['pending_to_T'].consumed is None
    for t in range(52,97,4):r.advance_time(float(t));r.apply_release(r.preview_release(),reason='EMPTY_DEADLINE')
    add(r,'terminal','c',99.8,(.5,.5),complete=99.9,download=r.model_version)
    r.advance_time(100.);terminal=operation('P2_terminal_smallK',lambda:controller.decide(r),judgement=True)
    r.apply_release(terminal.preview,reason='TERMINAL');r.finish_finite_endpoint()
    assert r.attempts['terminal'].consumed==1 and r.attempts['pending_to_T'].consumed==0
    expect(InputError,r.finish_finite_endpoint);assert len(r.consumed)==7
    warm=make_runner();add(warm,'warm','c',.8,(.8,.2),complete=.9);warm.advance_time(1.)
    wd=operation('P2_warmup_smallK',lambda:controller.decide(warm),judgement=True);assert wd.reason=='WARMUP'
    warm.apply_release(wd.preview,reason='WARMUP')
    # R0 and registration E0 never become inverse-factor pool records.
    reg=Registration('E0','excluded',20.4,0,'fixture_device','fixture_network')
    e=history('first')
    eq=e.on_register(reg,summary(e,20.4,(.5,.5)));assert eq.role=='structural_zero' and eq.value==0
    return dict(status='PASS',frozen_p=p,nonidentity_Design_ratio=ratio,configured_design=True,gate_role='diagnostic_only',
        private_future_perturbation_snapshot_unchanged=True,deadline_weights=[x['preview'] for x in actual],
        empty_preserves_Q_V_L_v=True,terminal_consumed=sorted(r.consumed),administrative_zero=asdict(r.attempts['pending_to_T']),
        warmup_preview=wd.preview.to_dict(),E0=asdict(eq),R0=asdict(rq),private_registration_change_rejected=True,unique_consumption=True,SGD=0)

def path3():
    r=history('first');old=r.preview_release();old_fingerprint=old.fingerprint;key=old.dependency_hash
    initial=operation('P3_initial_feedback',lambda:controller.decide(r),judgement=True)
    r.advance_time(20.5);new=operation('P3_clock_cache_hit',lambda:controller.decide(r),judgement=True)
    assert new.cache_hits==1 and new.p2_solves==0 and new.preview.numeric is old.numeric and new.preview.fingerprint!=old_fingerprint
    expect(InputError,lambda:r.apply_release(old));assert old.fingerprint==old_fingerprint
    add(r,'public_pending','q',20.5,(.99,.01),download=r.model_version)
    header=operation('P3_public_header_cache_hit',lambda:controller.decide(r),judgement=True)
    assert header.cache_hits==1 and header.preview.dependency_hash==key
    direct=operation('P3_uncached_original_complete_P2',lambda:controller.decide(r,use_cache=False),judgement=True)
    np.testing.assert_allclose(header.preview.alpha,direct.preview.alpha,rtol=0,atol=1e-7)
    np.testing.assert_allclose(header.preview.omega,direct.preview.omega,rtol=0,atol=1e-7)
    def original_reference():
        from raven_mcs_re_interval.preview import preview_release
        return preview_release(r.snapshot(),with_reachability=False)
    reference=operation('P3_independent_shared_original_preview_reference',original_reference)
    np.testing.assert_allclose(reference.alpha,direct.preview.alpha,rtol=0,atol=1e-7)
    np.testing.assert_allclose(reference.omega,direct.preview.omega,rtol=0,atol=1e-7)
    s=r.snapshot();variants={
        'Q':replace(s,debt=(s.debt[0]+.0001,s.debt[1])),
        'V':replace(s,variance=(('c0',2.),)),
        'version':replace(s,model_version=s.model_version+1),
        'configuration_source':replace(s,config=replace(s.config,source='explicit_fixture_other_source')),
        'pool_removed':replace(s,pool=s.pool[:-1])}
    misses=[]
    for name,state in variants.items():
        prior=r.cache.solves;bound=operation('P3_dependency_'+name,lambda state=state:r.cache.get(state))
        assert r.cache.solves==prior+1 and bound.dependency_hash!=key;misses.append(name)
    r.on_completion('public_pending',20.6,update=[.1,.2,.3]);arrived=operation('P3_arrival_cache_miss',lambda:controller.decide(r),judgement=True)
    assert arrived.p2_solves==1
    add(r,'replace_current','c0',20.6,(.3,.7),complete=20.7,download=r.model_version)
    replaced=operation('P3_replacement_cache_miss',lambda:controller.decide(r),judgement=True);assert replaced.p2_solves==1
    operation('P3_latest_binding_commit',lambda:r.apply_release(replaced.preview))
    consumed_key=r.preview_release().dependency_hash;assert consumed_key!=key
    assert old.numeric.reachability is None and abs(new.B-initial.B-.005)<1e-10
    return dict(status='PASS',clock_header_reuse=True,old_binding_rejected=True,old_fingerprint_unchanged=True,
        actual_matches_uncached=True,invalidated=misses+['arrival','replacement','consumption'],d=None,
        registered_q_unchanged=asdict(r.attempts['public_pending'].q),solves=r.cache.solves,hits=r.cache.hits,
        latest_weights=replaced.preview.to_dict(),no_action_cache=True)

def full_owner(config):
    import torch,pandas as pd
    from types import SimpleNamespace
    from raven_mcs.training.window_runner import FullWindowRunner
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf
    from raven_mcs.aggregation.methods import RavenAggregator
    from raven_mcs.aggregation.method_policy import get_method_policy
    from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
    from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
    torch.set_num_threads(1)
    return FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('OF_interface_no_replay',26004,2,100)),
        dataset=SimpleNamespace(),model=deterministic_common_ndmf(2,seed=26004),aggregator=RavenAggregator(),
        policy=get_method_policy('raven_mcs'),mu=np.array([.5,.5]),num_groups=2,local_steps=1,design_configuration=SharedDesign.from_dict(config.design.to_dict()))

def connect_owner(owner,config,*,q_model=None,isolated=True):
    from raven_mcs_observed_feedback.backend import connect_full_runner
    base=make_runner(open_time=20.)
    app=copy.deepcopy(base.probability_applicability)
    if not isolated:
        from raven_mcs.training.client import _flatten_params
        import hashlib
        app.update(learning=dict(model='CommonNDMF',optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,
            initial_model_hash=hashlib.sha256(_flatten_params(owner.theta).tobytes()).hexdigest(),scaler='explicit_fixture_no_data',feature_schema='actual_CommonNDMF_features'),
            data_identity=base.data_identity,target_identity=base.target_identity)
    return connect_full_runner(owner,config=config,q_model=q_model or IsolatedQ(),seed=26004,data_identity=base.data_identity,
        target_identity=base.target_identity,probability_applicability=app,clock_namespace=base.clock_namespace,
        isolated_test=isolated,open_time=20.)

def path4():
    from raven_mcs_observed_feedback.persistence import save_pair,restore_pair
    from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
    from raven_mcs_observed_feedback.budget_client import RootClient
    from raven_mcs.training.client import _flatten_params,ClientTrainer
    config=make_runner().config
    owner=operation('P4_real_CommonNDMF_ClientTrainer_setup',lambda:full_owner(config));r=connect_owner(owner,config)
    assert type(owner.model).__name__=='CommonNDMF' and isinstance(owner._trainer,ClientTrainer)
    owner._trainer.train_step=lambda *a,**k:(_ for _ in ()).throw(AssertionError('SGD called'))
    old=_flatten_params(owner.theta).copy();u=np.full_like(old,.1)
    for i in range(3):add(r,'real'+str(i),'c'+str(i),20.1,(.5,.5),download=0)
    for i in range(3):r.on_completion('real'+str(i),20.2,update=u*(i+1))
    expect(DependencyPending,lambda:r.start_local_training('real0',[],authorization=None))
    d=operation('P4_real_backend_current_judgement',lambda:controller.decide(r),judgement=True)
    expected=old-.01*sum(a*u*(i+1) for i,a in enumerate(d.preview.alpha))
    operation('P4_real_backend_success_commit',lambda:r.apply_release(d.preview))
    np.testing.assert_allclose(_flatten_params(owner.theta),expected,rtol=0,atol=1e-7)
    assert r.model_version==owner.clock.model_version==1 and r.last_release.omega==d.preview.omega
    assert all(v==1 for v in owner.variance_count.values()) and r.backend.local_optimizer_steps==0
    for i in range(3):add(r,'saved'+str(i),'n'+str(i),20.3,(.8,.2),download=1)
    for i in range(3):r.on_completion('saved'+str(i),20.4,update=u)
    expected_state=sha256_json(r.to_dict())
    store=PairedCheckpointStore(OUT/'OF_PAIR_STATE');budget=RootClient(BATCH/'ROOT_BUDGET_LIVE.json')
    producer=dict(T=100.,tick=204,clock_namespace=r.clock_namespace,role='explicit_fixture_no_live_producer',physical_future_queue=[])
    marker=operation('P4_pair_save',lambda:save_pair(r,store,'success',producer_state=producer,budget=budget,save_reserve=5.96875))
    identity=dict(method=METHOD_VERSION,seed=r.seed,clock_namespace=r.clock_namespace)
    other_owner=operation('P4_restore_real_owner_setup',lambda:full_owner(config));other=connect_owner(other_owner,config)
    restored,private=operation('P4_pair_restore',lambda:restore_pair(store,marker,identity=identity,backend=other.backend,
        expected_config=config,expected_data=r.data_identity,expected_target=r.target_identity))
    assert sha256_json(restored.to_dict())==expected_state
    rd=operation('P4_restored_current_judgement',lambda:controller.decide(restored),judgement=True)
    od=operation('P4_original_current_judgement',lambda:controller.decide(r),judgement=True)
    assert rd.action==od.action and abs(rd.B-od.B)<1e-10
    np.testing.assert_allclose(rd.preview.alpha,od.preview.alpha,atol=1e-7,rtol=0)
    legacy=expect(InputError,lambda:restore_pair(store,marker,identity=dict(identity,method='reachability_stop/conditional-bundle-RE-interval-v3'),backend=ArrayBackend([1.,2.,3.])))
    # Actual backend changes the model before the deliberately failing variance hook.
    fault_owner=operation('P4_fault_owner_setup',lambda:full_owner(config));fault=connect_owner(fault_owner,config)
    for i in range(3):add(fault,'fault'+str(i),'c'+str(i),20.1,(.5,.5),download=0)
    for i in range(3):fault.on_completion('fault'+str(i),20.2,update=u)
    fd=operation('P4_pre_fault_judgement',lambda:controller.decide(fault),judgement=True)
    old_fault_theta=_flatten_params(fault_owner.theta).copy();before_Q=fault.debt
    fault_owner._update_variance_state=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('injected_after_model_change'))
    error=expect(RuntimeError,lambda:operation('P4_apply_failure_injection',lambda:fault.apply_release(fd.preview)))
    assert fault.fault and not fault.consumed and fault.model_version==0 and fault.debt==before_Q
    assert not np.array_equal(old_fault_theta,_flatten_params(fault_owner.theta))
    expect(InputError,fault.snapshot);expect(InputError,fault.checkpoint_state)
    expect(InputError,lambda:save_pair(fault,store,'fault_should_not_publish',producer_state=producer,budget=budget,save_reserve=5.96875))
    assert not (store.root/'fault_should_not_publish.complete.json').exists()
    (OUT/'QUARANTINED_TRANSACTION_DIAGNOSTIC.json').write_text(json.dumps(fault.to_dict(),allow_nan=False))
    # Production dependency is explicit, not .5 or a predictor constructor.
    pending_owner=operation('P4_production_PendingQ_real_backend_setup',lambda:full_owner(config))
    pending=connect_owner(pending_owner,config,q_model=PendingQModel(),isolated=False)
    fill(pending,'pendingQ_',20.1,(.5,.5))
    for i in range(3):pending.on_completion('pendingQ_'+str(i),20.2,update=u)
    missing=expect(DependencyPending,lambda:operation('P4_pending_q_judgement',lambda:controller.decide(pending),judgement=True))
    return dict(status='PASS',model='CommonNDMF',trainer='ClientTrainer',backend=r.backend.kind,SGD=0,
        hand_authored_tensor_not_training=True,theta_matches_actual_weights=True,variance_updated_after_success=True,
        saved_state_hash=expected_state,restored_identical=True,restored_preview=rd.preview.to_dict(),
        legacy_rejection=legacy,transaction_strategy='FAULT_QUARANTINE',backend_changed_before_failure=True,
        fault=fault.fault,no_failed_checkpoint=True,pending_q_error=missing,
        probability_status='PRODUCTION_Q_PENDING',production_mode_pending_error_verified=True,local_training_authorization_rejected=True,
        necessary_saved_fields=['theta','versions','variance','stage1','Q','L.omega','q','p','Design','clock','torch_rng','numpy_rng','python_rng','stateless_optimizer_config'])

if __name__=='__main__':
    try:
        def bootstrap_first_request():
            global np,asdict,replace,sha256_json,DesignConfiguration,ControlConfig,P2Settings,Registration,InputError,DependencyPending
            global DynamicWindowRunner,ArrayBackend,IsolatedQ,PendingQModel,freeze_stage1,METHOD_VERSION,Controller,controller
            import numpy as np
            from dataclasses import asdict,replace
            from raven_mcs.utils.hashing import sha256_json
            from raven_mcs_observed_feedback.design import DesignConfiguration
            from raven_mcs_observed_feedback import METHOD_VERSION
            from raven_mcs_observed_feedback.schema import ControlConfig,P2Settings,Registration,InputError,DependencyPending
            from raven_mcs_observed_feedback.lifecycle import DynamicWindowRunner
            from raven_mcs_observed_feedback.array_backend import ArrayBackend
            from raven_mcs_observed_feedback.probability import IsolatedQ,PendingQModel
            from raven_mcs_observed_feedback.stage1 import freeze_stage1
            from raven_mcs_observed_feedback.controller import Controller
            from raven_mcs_observed_feedback.budget_client import RootClient
            controller=Controller(root_budget=RootClient(BATCH/'ROOT_BUDGET_LIVE.json'),save_reserve=5.96875,operation_root_ceiling=4.)
            r=make_runner(open_time=20.);r.advance_time(20.1)
            return controller.decide(r)
        first=operation('STARTUP_AND_FIRST_MIN_CLIENTS',bootstrap_first_request,judgement=True,first=True)
        assert first.reason=='MIN_CLIENTS' and first.p2_solves==0
        cold=make_runner(open_time=20.);fill(cold,'cold_',20.1,(.5,.5),completion=20.2)
        operation('COLD_COMPLETE_CURRENT_P2',lambda:controller.decide(cold),judgement=True)
        for name,fn in [('history_feedback',path1),('causal_lifecycle',path2),('numeric_cache_binding',path3),('transaction_real_backend_restore',path4)]:
            case_results[name]=operation(name,fn);flush()
        output=dict(status='PASS',cases=case_results,measurements=measurements,method=METHOD_VERSION,
            state='IMPLEMENTATION_VALIDATED_FOR_ISOLATED_INPUTS / PRODUCTION_Q_PENDING / PERFORMANCE_NOT_VALIDATED',
            SGD=0,GPU=0,q_fit=0,real_or_random_trajectories=0,facility_retests=0)
        with (OUT/'FOUR_PATH_RESULT.json').open('x') as f:json.dump(output,f,indent=2,allow_nan=False)
        print(json.dumps(dict(status=output['status'],cases={k:v['status'] for k,v in case_results.items()},judgements=sum(x['judgement'] for x in measurements))))
    except Exception as exc:
        failure=dict(error=repr(exc),trace=traceback.format_exc(),cases_completed=list(case_results),measurements=measurements,
            SGD=0,scope='same four frozen interface cases; ordinary engineering errors may be repaired')
        with (OUT/('FOUR_PATH_FAILED_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(failure,f,indent=2)
        print(traceback.format_exc());raise
