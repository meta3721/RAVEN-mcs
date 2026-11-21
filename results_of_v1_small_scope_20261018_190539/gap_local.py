"""Explicit one-arm diagnostic adapter; original scientific packages unchanged."""
import copy, ctypes, json, pathlib, sys, time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import numpy as np, pandas as pd, torch
from types import SimpleNamespace
from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization, PILOT_SOURCE
from raven_mcs_observed_feedback.schema import InputError, ControlConfig, Registration, QValue, Stage1Summary, InFlight, ReleaseSummary, delivered_from_dict
from raven_mcs_observed_feedback.controller import Controller, Decision
from raven_mcs_observed_feedback.lifecycle import DynamicWindowRunner
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.probability import DiagnosticPrior, AttemptRecord
from raven_mcs_observed_feedback.persistence import source_closure
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.experiments.calibration_first import load_inputs
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import CommonNDMF
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
from observed_feedback_pilot_common import AuditedProducer
from observed_feedback_recovery_common import require_resource_source_identity
from observed_feedback_recovery_io import durable_json, file_hash
torch.set_num_threads(1);torch.set_num_interop_threads(1)
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
STRATEGY='GAP20-fixed-reference';ROLE='OF_v1_small_scope_20261018';APPROVAL='user_OF-v1-small-scope-validation-instructions'
PARENT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop'
FREEZE=json.loads((OUT/'FREEZE.json').read_text())

@dataclass(frozen=True)
class GapAuthorization(AutonomousPilotAuthorization):
    strategy:str=STRATEGY
    role:str=ROLE
    CPU_limit:float=1000.
    batch_steps:int=5000
    approval_source:str=APPROVAL
    calibration_only:bool=True
    GPU:int=0
    maximum_new_arms:int=1
    wall_limit:float=5400.
    def require(self,*,seed,source):
        expected=dict(strategy=STRATEGY,source=PILOT_SOURCE,seed=45001,method='reachability_stop/observed-feedback-v1',role=ROLE,T=100.,max_steps=5000,CPU_limit=1000.,batch_steps=5000,approval_source=APPROVAL,calibration_only=True,GPU=0,maximum_new_arms=1,wall_limit=5400.)
        if asdict(self)!=expected or seed!=45001 or source!=PILOT_SOURCE:raise InputError('outside unique GAP small-scope authority')

class GapController(Controller):
    def __init__(self,*,c_ref,**kw):
        super().__init__(**kw)
        if c_ref!=FREEZE['c_ref']:raise InputError('fixed reference differs from frozen warmup')
        self._c_ref=c_ref
    @property
    def c_ref(self):return self._c_ref
    def decide(self,runner,**kw):
        auth=runner.collection_authorization
        if type(auth) is not GapAuthorization or not runner.calibration_only or runner.isolated_test:raise InputError('GAP local diagnostic identity required')
        auth.require(seed=runner.seed,source=runner.config.source)
        if runner.probability_applicability['strategy']!=STRATEGY or kw:raise InputError('GAP strategy/override mismatch')
        start=time.process_time();s=runner.snapshot();elapsed=s.now-s.window_open
        if self.root_budget is None or self.save_reserve is None or self.operation_root_ceiling!=2.:raise InputError('full root binding required')
        if not self.root_budget.can_plan(self.save_reserve,operation_root_ceiling=2.):raise InputError('ROOT_ADMISSION_DENIED_SAVE_THEN_STOP')
        if abs(s.now-round(s.now/.1)*.1)>1e-9:raise InputError('decision outside original grid')
        solves=runner.cache.solves;hits=runner.cache.hits;preview=None;B=None;components=()
        if s.now==100.:action,reason='CLOSE','TERMINAL'
        elif s.now<=20.:action,reason=('CLOSE','WARMUP') if elapsed>=1-1e-9 else ('WAIT','WARMUP')
        elif elapsed>=4-1e-9:action,reason='CLOSE','DEADLINE'
        elif len(s.pool)<3:action,reason='WAIT','MIN_CLIENTS'
        else:action,reason=None,None
        if action is None or action=='CLOSE':
            if s.pool:preview=runner.preview_release()
        if action is None:
            c=preview.ell+.02*preview.age;norm=1+sum(s.debt)
            b=sum(q/norm*(o-m) for q,o,m in zip(s.debt,preview.omega,s.mu))
            quality=self.c_ref-c;patience=.20*min(1.,max(0.,elapsed/4.));B=quality+patience
            action='CLOSE' if B>=.02+1e-7 else 'WAIT';reason='GAP_TRIGGER' if action=='CLOSE' else 'GAP_WAIT'
            components=(('quality',quality),('debt',0.*b),('patience',patience),('b',b),('c_minus',self.c_ref),('c',c))
        cpu=time.process_time()-start
        if cpu>2.:raise InputError('CONTROLLER_LOCAL_CPU_TIMEOUT; root also required')
        return Decision(action,reason,preview,B,components,runner.cache.solves-solves,runner.cache.hits-hits,cpu)

def available_memory():
    class Status(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','extended')]
    v=Status();v.length=ctypes.sizeof(v)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(v)):raise ctypes.WinError()
    return dict(available_bytes=v.avail_phys,total_bytes=v.total_phys,wall_stamp=time.perf_counter(),UTC=datetime.now(timezone.utc).isoformat())

def restore_parent(tick,budget,*,tag):
    current=require_resource_source_identity()
    marker=PARENT/'trajectory'/('tick%04d.complete.json'%tick)
    record=json.loads(marker.read_text());packet,private=PairedCheckpointStore(marker.parent).read(marker,expected_identity=record['identity'])
    if packet['source_closure']!=current or packet['state_hash']!=sha256_json(packet['state']):raise InputError('parent source/content mismatch')
    inputs=load_inputs(ROOT,ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014')
    state=packet['state'];config=ControlConfig.from_dict(state['config'])
    if state['data_identity']!=inputs.data_id or state['target_identity']!=inputs.target_id:raise InputError('data/target identity changed')
    with torch.device('meta'):model=CommonNDMF(num_spatial=len(inputs.clients))
    model.to_empty(device='cpu');reference=model.state_dict()
    model.load_state_dict({k:torch.tensor(v['values'],dtype=reference[k].dtype) for k,v in state['backend']['theta'].items()})
    owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('GAP20_DIAGNOSTIC_BRANCH',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
    holder=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=state['probability_applicability'],clock_namespace=state['clock_namespace'],calibration_only=True,collection_authorization=state_auth(state),root_budget=budget)
    r=DynamicWindowRunner.from_dict(state,backend=holder.backend,root_budget=budget)
    p=AuditedProducer(inputs,r,np.random.default_rng(0),np.random.default_rng(1),OUT);p.restore(private['state'])
    if sha256_json(r.checkpoint_state())!=packet['state_hash'] or sha256_json(p.to_dict())!=sha256_json(private['state']):raise InputError('restoration scientific/RNG equality failed')
    before=r.snapshot();before_hash=packet['state_hash'];parent_SGD=r.backend.local_optimizer_steps
    old_attempts=sha256_json([x.to_dict() for x in r.attempts.values()])
    old_backend=sha256_json(state['backend']);old_producer=sha256_json(p.to_dict())
    app=copy.deepcopy(r.probability_applicability);app.update(strategy=STRATEGY,collection_role=ROLE,q_role='diagnostic_prior_not_calibrated')
    app['stop_rule']=dict(strategy=STRATEGY,c_ref=FREEZE['c_ref'],theta=.02,kappa=0.,nu=.20,common_priority=['terminal','warmup_fixed1','deadline4','K<3_wait','free_strategy'])
    # Service law, learning and already-registered probability records stay intact.
    clock=dict(run_id=STRATEGY+'/45001/'+OUT.name+'/'+tag,origin_utc=datetime.now(timezone.utc).isoformat(),unit='controlled_service_unit',UTC_bridge='branch logical t20 retains old registrations and RNG; publication UTC is actual wall time')
    r.collection_authorization=GapAuthorization();r.probability_applicability=app;r.clock_namespace=clock
    r.collection_authorization.require(seed=r.seed,source=r.config.source)
    after=r.snapshot()
    for name in ('now','window_open','model_version','revision','config','settings','mu','debt','pool','in_flight','last_release','variance','seed','experiment_end'):
        assert getattr(before,name)==getattr(after,name),name
    assert sha256_json([x.to_dict() for x in r.attempts.values()])==old_attempts
    assert sha256_json(r.backend.to_dict())==old_backend and sha256_json(p.to_dict())==old_producer
    p.pause_requested=None;p.stop_after_steps=None
    branch=dict(status='PASS',parent=str(marker),parent_identity=record['identity'],parent_marker_hash=file_hash(marker),parent_state_hash=before_hash,restored_scientific_and_RNG_equal=True,
      registered_messages_unchanged=True,new_scope=app,new_clock=clock,authorization=asdict(r.collection_authorization),parent_SGD=parent_SGD,parent_tick=tick,next_grid_tick=private['next_grid_tick'],c_ref=FREEZE['c_ref'],source_closure=current,
      allowed_state_changes=['collection_authorization','probability_applicability','clock_namespace'],local_adapter_hash=file_hash(__file__))
    return r,p,branch

def state_auth(state):
    from raven_mcs_observed_feedback.authorization import collection_authorization_from_dict
    return collection_authorization_from_dict(state['collection_authorization'])

def restore_gap(packet,private,budget):
    """Explicit local new-identity restore, without changing the old auth factory."""
    state=packet['state'];auth=GapAuthorization(**state['collection_authorization']);auth.require(seed=state['seed'],source=state['config']['source'])
    if packet['source_closure']!=source_closure() or packet['state_hash']!=sha256_json(state) or state.get('fault'):raise InputError('local GAP checkpoint identity/content/fault mismatch')
    # Build the real backend under the new diagnostic identity, then hydrate the
    # same fields as DynamicWindowRunner.from_dict. No old-arm impersonation.
    inputs=load_inputs(ROOT,ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014')
    if state['data_identity']!=inputs.data_id or state['target_identity']!=inputs.target_id:raise InputError('restore data identity mismatch')
    config=ControlConfig.from_dict(state['config'])
    with torch.device('meta'):model=CommonNDMF(num_spatial=len(inputs.clients))
    model.to_empty(device='cpu')
    reference=model.state_dict()
    model.load_state_dict({k:torch.tensor(v['values'],dtype=reference[k].dtype) for k,v in state['backend']['theta'].items()})
    owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('GAP_LOCAL_RESTORE',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
    r=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=state['probability_applicability'],clock_namespace=state['clock_namespace'],calibration_only=True,collection_authorization=auth,root_budget=budget,open_time=state['window_open'])
    for name in ('now','window_open','model_version','window_id','revision','variance','events','closures','decisions','diagnostics','rng_state','ended'):setattr(r,name,state[name])
    r.debt=tuple(state['debt']);r.pool={k:delivered_from_dict(v) for k,v in state['pool'].items()}
    r.in_flight={k:InFlight(Registration(**v['registration']),QValue(**v['q']),v['R'],v['E']) for k,v in state['in_flight'].items()}
    r.attempts={k:AttemptRecord.from_dict(v) for k,v in state['attempts'].items()};r.private_stage1={k:Stage1Summary.from_dict(v) for k,v in state['private_stage1'].items()}
    r.consumed=set(state['consumed']);r.last_release=ReleaseSummary(**dict(state['last_release'],omega=tuple(state['last_release']['omega']))) if state['last_release'] else None
    r.backend.restore(state['backend'])
    p=AuditedProducer(inputs,r,np.random.default_rng(0),np.random.default_rng(1),OUT);p.restore(private['state'])
    if sha256_json(r.checkpoint_state())!=packet['state_hash'] or sha256_json(p.to_dict())!=sha256_json(private['state']):raise InputError('GAP checkpoint roundtrip mismatch')
    if private.get('c_ref')!=FREEZE['c_ref']:raise InputError('GAP fixed reference persistence mismatch')
    return r,p
