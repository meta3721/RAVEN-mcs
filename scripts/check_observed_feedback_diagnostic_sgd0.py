"""One deterministic real-backend integration; intercepted local SGD, no trajectory."""
import sys,os,json,time,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_acquisition_45011_20261014'
import numpy as np,torch,pandas as pd
from types import SimpleNamespace
from dataclasses import replace,asdict
from raven_mcs_observed_feedback.authorization import SOURCE,DiagnosticCollectionAuthorization
from raven_mcs_observed_feedback.schema import ControlConfig,Registration,InputError,QValue
from raven_mcs_observed_feedback.design import DesignConfiguration
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.stage1 import freeze_stage1
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.controller import Controller
from raven_mcs_observed_feedback.diagnostic import shadow_actions
from raven_mcs_observed_feedback.acquisition import CausalProducer
from raven_mcs_observed_feedback.persistence import save_pair,restore_pair
from raven_mcs_observed_feedback.budget_client import RootClient,read_shared_json
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
torch.set_num_threads(1);torch.set_num_interop_threads(1)
root_budget=RootClient(Path(os.environ['OF_ROOT_BUDGET_PATH']))
config=ControlConfig(SOURCE,DesignConfiguration(True,'explicit_45011_whole_run_on'));auth=DiagnosticCollectionAuthorization()
def owner():return FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('SGD0_FIXED_INPUT_NOT_DATA_RUN',45011,100,2)),dataset=SimpleNamespace(),
    model=deterministic_common_ndmf(2,seed=0),aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.array([.5,.5]),num_groups=2,
    local_steps=1,learning_rate=.01,seed=45011,design_configuration=SharedDesign.from_dict(config.design.to_dict()))
app=dict(consumption_policy='reachability_stop/observed-feedback-v1',T=100,learning=dict(model='actual_CommonNDMF',optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,
    initial_model_hash='deterministic_SGD0_fixture',scaler='unit_fixture_no_dataset',feature_schema='actual_existing_features'),service=dict(kind='hand_notification_fixture'),stage1={},data_identity='SGD0_ONLY',target_identity='unit_mu2')
clock=dict(run_id='OF_SGD0_INTEGRATION',origin_utc='2026-10-14T00:00:00Z',unit='controlled_service_unit')
def connect(o,**extra):return connect_full_runner(o,config=config,q_model=DiagnosticPrior(),seed=45011,data_identity='SGD0_ONLY',target_identity='unit_mu2',
    probability_applicability=app,clock_namespace=clock,root_budget=root_budget,**extra)
def rejects(fn):
    try:fn()
    except (ValueError,RuntimeError):return True
    raise AssertionError('expected guard rejection')
rejects(lambda:connect(owner()))
rejects(lambda:connect(owner(),calibration_only=True,collection_authorization=replace(auth,seed=43001)))
r=connect(owner(),calibration_only=True,collection_authorization=auth,open_time=20.)
r.backend.freeze_stage1_context(0.)
r.model_version=6;r.backend.owner.clock.model_version=6
for v in range(7):r.backend.owner.model_versions[v]=copy.deepcopy(r.backend.owner.theta)
class Intercepted(Exception):pass
entered=[]
def intercept(*args,**kwargs):entered.append(kwargs);raise Intercepted('real ClientTrainer intercepted before any SGD')
r.backend.owner._trainer.train_step=intercept
records=[dict(spatial_id='0',absolute_time=0.,time_index=0,observed_value=1.,spatial_to_idx={'0':0},total_time_slots=1)]*2
def add(key,cid,download,flags=(1,1)):
    reg=Registration(key,cid,20.1,download,'tier-0','net-tier-0')
    s=freeze_stage1(config=config,target_opportunity=[.5,.5],lagged_opportunity=[.5,.5],p_obs=[.2,.2],observation=flags,group_ids=[0,1],num_groups=2,
        now=20.1,estimator_as_of=0.,estimator_version='SGD0_hand_input',provenance='fixed_unit_fixture')
    r.on_register(reg,s);return s
add('R0','outside',6,(0,0));assert not r.attempts['R0'].R and r.attempts['R0'].q.role=='outside_R'
add('E0','overage',0);assert not r.attempts['E0'].E and r.attempts['E0'].q.role=='structural_zero'
try:r.start_local_training('E0',records,authorization=auth)
except Intercepted:pass
else:raise AssertionError('authorized E0 must retain physical work path')
for j in range(3):add('ready'+str(j),'c'+str(j),6)
rejects(lambda:r.start_local_training('ready0',records,authorization=replace(auth,seed=44001)))
try:r.start_local_training('ready0',records,authorization=auth)
except Intercepted:pass
else:raise AssertionError('real trainer not reached')
assert len(entered)==2 and r.backend.local_optimizer_steps==0
rejects(lambda:QValue(.5,20.1,'unvalidated','reachability_stop/observed-feedback-v1','not_verified','fitted_not_validated','h').require(isolated_test=False))
before=r.snapshot().fingerprint;s=r.private_stage1['ready0'];r.private_stage1['ready0']=replace(s,masses=(.9,.1))
assert r.snapshot().fingerprint==before;r.private_stage1['ready0']=s
for j in range(44):add('extra'+str(j),'multi',6)
last=r.attempts['extra43'];assert last.public_encoding['raw_F_count']>43 and len(last.public_encoding['values'])==37
u=np.zeros(sum(x.numel() for x in r.backend.owner.theta.values()))
inputs=SimpleNamespace(clients=['unit'],strata={},pools={})
producer=CausalProducer(inputs,r,np.random.default_rng(0),np.random.default_rng(1))
producer.pending=[(20.4,'ready0','completion',u.copy())]
producer.next_clock=21;producer.next_client=0
store=PairedCheckpointStore(OUT/'SGD0_PAIR')
def sample_after(t):
    while True:
        x=read_shared_json(root_budget.path)
        if x['wall_stamp']>=t+.01:return x
        time.sleep(.005)
start=sample_after(time.perf_counter());cpu=time.process_time();wall=time.perf_counter()
marker=save_pair(r,store,'SGD0_queue',producer_state=dict(T=100.,tick=r.now/.1,next_grid_tick=202,clock_namespace=clock,state=producer.to_dict()),budget=root_budget,save_reserve=5.96875)
end=sample_after(time.perf_counter());save_delta=end['command_used']-start['command_used'];save_upper=max(save_delta+.02,time.process_time()-cpu+end['driver_CPU']-start['driver_CPU']+.02)
(OUT/'SGD0_SAVE_MEASUREMENT.json').write_text(json.dumps(dict(root_difference=save_delta,root_upper_CPU=save_upper,wall=time.perf_counter()-wall,
    reserve=max(5.96875,2*save_upper),sizes=json.loads(marker.read_text())['sizes'],representative='actual CommonNDMF7 versions, untrained real work, actual-sized pending tensor, 47 legal public in-flight keys; future growth unknown'),indent=2))
fresh=connect(owner(),calibration_only=True,collection_authorization=auth,open_time=20.)
restored,private=restore_pair(store,marker,identity=dict(method=r.config.method_version,seed=45011,clock_namespace=clock),backend=fresh.backend,root_budget=root_budget)
p2=CausalProducer(inputs,restored,np.random.default_rng(123),np.random.default_rng(321));p2.restore(private['state'])
assert sha256_json(producer.to_dict())==sha256_json(p2.to_dict()) and restored.snapshot().fingerprint==r.snapshot().fingerprint
p2.notices_through(20.4);assert 'c0' in restored.pool
for j in (1,2):restored.on_completion('ready'+str(j),20.4,update=u)
control=Controller(root_budget=root_budget,save_reserve=max(5.96875,2*save_upper),operation_root_ceiling=2.)
d=control.decide(restored);before=restored.snapshot().fingerprint;solves=restored.cache.solves;shadow=shadow_actions(restored,d)
assert restored.snapshot().fingerprint==before and restored.cache.solves==solves and not shadow['P2_recomputed']
restored.finish_observation();assert any(x.right_censored_at is not None and x.physical_service_censored_at is not None for x in restored.attempts.values())
assert r.backend.local_optimizer_steps==restored.backend.local_optimizer_steps==0
(OUT/'SGD0_RESULT.json').write_text(json.dumps(dict(status='PASS',real_backend='CommonNDMF/ClientTrainer',calibration_only=True,isolated_test=False,
    authorization_rejected=['production_prior','43001','44001','fitted_not_validated'],accepted_intercepted=2,R0_no_training=True,E0_work_retained=True,
    private_visibility=True,visible_completion=True,all_inflight_keys=True,encoding_columns=37,raw_F_over43=last.public_encoding['raw_F_count'],
    queue_RNG_pair_restore=True,shadow_readonly=True,SGD=0,save_marker=str(marker),save_upper_CPU=save_upper),indent=2))
print('SGD0_NEW_DIAGNOSTIC_CHAIN_PASS')
