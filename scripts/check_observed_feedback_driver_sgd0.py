"""One fixed-input check of the changed producer/driver. No Traffic/RNG45011 consumption."""
import sys,json,os,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_continuation_45011_20261014'
import numpy as np,pandas as pd,torch
from types import SimpleNamespace
from raven_mcs_observed_feedback.authorization import SOURCE,DiagnosticCollectionAuthorization
from raven_mcs_observed_feedback.schema import ControlConfig
from raven_mcs_observed_feedback.design import DesignConfiguration
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.acquisition import CausalProducer
from raven_mcs_observed_feedback.accounting import CategoryAccountant
from raven_mcs_observed_feedback.execution import frozen_shadow_context
from raven_mcs_observed_feedback.controller import Controller
from raven_mcs_observed_feedback.diagnostic import shadow_actions
from raven_mcs_observed_feedback.persistence import save_pair,restore_pair
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
torch.set_num_threads(1);torch.set_num_interop_threads(1)
a=CategoryAccountant(OUT);config=ControlConfig(SOURCE,DesignConfiguration(True,'explicit_45011_whole_run_on'));auth=DiagnosticCollectionAuthorization()
app=dict(consumption_policy=config.method_version,T=100,learning=dict(model='fixed CommonNDMF',optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,initial_model_hash='test',scaler='fixed unit',feature_schema='existing'),service=dict(kind='fixed unit literal outcomes'),stage1={},data_identity='fixed_unit',target_identity='fixed_mu2')
clock=dict(run_id='OF_driver_SGD0_fixed_unit_NOT_45011_trajectory',origin_utc='2026-10-14T00:00:00Z',unit='controlled_service_unit')
def fresh():
 o=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('fixed_SGD0',0,100,2)),dataset=SimpleNamespace(),model=deterministic_common_ndmf(2,seed=0),aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.array([.5,.5]),num_groups=2,local_steps=1,learning_rate=.01,seed=45011,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target={('0','block0'):.5,('1','block0'):.5},pi_opp_joint={('0','block0'):.25,('1','block0'):.75})
 return connect_full_runner(o,config=config,q_model=DiagnosticPrior(),seed=45011,data_identity='fixed_unit',target_identity='fixed_mu2',probability_applicability=app,clock_namespace=clock,calibration_only=True,collection_authorization=auth,root_budget=a.root)
r=a.operation('setup',fresh,30.);r.backend.freeze_stage1_context(0.)
r.model_version=6;r.backend.owner.clock.model_version=6
for version in range(7):r.backend.owner.model_versions[version]=copy.deepcopy(r.backend.owner.theta)
i=SimpleNamespace(clients=['0','1'],strata={'0':['block0'],'1':['block0']},pools={('0','block0'):['u0'],('1','block0'):['u1']},opp={('0','block0'):.25,('1','block0'):.75},mu=(.5,.5),meta={'u0':dict(group=0,stratum='block0',spatial_id='0',absolute_time=0.,time_index=0),'u1':dict(group=1,stratum='block0',spatial_id='1',absolute_time=0.,time_index=0)},values={('0','u0'):1.,('1','u1'):1.},spatial={'0':0,'1':1},time_slots=1)
class Fixed:
 def __init__(self,opportunity=False):self.opportunity=opportunity;self.calls=0;self.bit_generator=np.random.default_rng(17).bit_generator
 def choice(self,values,size=None,**kw):return np.asarray(values[:size]) if size is not None else 0
 def random(self,size=None):
  if size is None:return 0.
  self.calls+=1;return np.zeros(size) if self.calls==1 else np.ones(size)
 def integers(self,low,high):return low
 def lognormal(self,mean,sd):return float(np.exp(mean))
p=CausalProducer(i,r,Fixed(True),Fixed());p.operation=a.operation
entered=[]
def intercepted(**kwargs):
 entered.append(kwargs);assert kwargs['local_steps']==1 and len(kwargs['observed_records'])==1
 assert r.backend.owner._trainer.learning_rate==.01
 return np.zeros(sum(x.numel() for x in r.backend.owner.theta.values())),0.
r.backend.owner._trainer.train_step=intercepted
p.register_current();p.register_current()
assert len(entered)==1 and r.attempts['000::0'].E==0 and r.attempts['000::1'].R==0
assert r.backend.work['000::0']['training_started'] and not r.backend.work['000::1']['training_started']
assert len(p.pending)==1 and not r.snapshot().pool and p.next_client==0 and p.next_clock==1 and p.active_registration is None
assert r.private_stage1['000::0'].ratio==(2.,) and r.private_stage1['000::1'].ratio==(2/3.,)
assert r.attempts['000::0'].q.role=='structural_zero'
context=frozen_shadow_context(r)
store=PairedCheckpointStore(OUT/'DRIVER_SGD0_PAIR')
marker=a.operation('save',lambda:save_pair(r,store,'driver_fixed',producer_state=dict(T=100.,tick=r.now/.1,next_grid_tick=1,clock_namespace=clock,state=p.to_dict()),budget=a.root,save_reserve=a.reserve),a.reserve)
fresh_r=fresh();restored,private=restore_pair(store,marker,identity=dict(method=config.method_version,seed=45011,clock_namespace=clock),backend=fresh_r.backend,root_budget=a.root)
pr=CausalProducer(i,restored,Fixed(True),Fixed());pr.restore(private['state'])
assert sha256_json(pr.to_dict())==sha256_json(p.to_dict()) and restored.snapshot().fingerprint==r.snapshot().fingerprint
# No new registration: only the one literal notification due at 1.15.
pr.next_clock=100;pr.notices_through(1.15)
assert restored.attempts['000::0'].physical_outcome=='completion' and not restored.pool
controller=Controller(root_budget=a.root,save_reserve=a.reserve,operation_root_ceiling=2.)
r.advance_time(.1);context=frozen_shadow_context(r)
d=a.operation('online',lambda:r.on_grid(.1,controller),2.,online=True)
before=r.snapshot().fingerprint;shadow=shadow_actions(context,d);assert before==r.snapshot().fingerprint
r.advance_time(1.);context=frozen_shadow_context(r)
d=a.operation('online',lambda:r.on_grid(1.,controller),2.,online=True);assert d.reason=='WARMUP' and r.window_id==1
p.after_close();assert r.backend.stage1_as_of==1. and not p.p_pending
value=dict(status='PASS',actual_SGD=0,intercepted_real_trainer_calls=1,unit_backend_counter=1,fixture_role='fixed arithmetic only, not Traffic or actual45011 RNG streams',real_backend='CommonNDMF/ClientTrainer',E0_work=True,R0_no_work=True,registration_stage1_frozen=True,actual_design_ratio=[2.,2/3.],event_order='register -> intercepted trainer -> private service queue -> due notification',queue_cursor_RNG_pair_restore=True,p_after_close=True,readonly_shadow=True,worker_PID=os.getpid(),root_id=a.root.read()['root_id'],max_online_root_upper=a.maxima['online'],save_marker=str(marker),old_SGD0_evidence_reused=str(ROOT/'results_observed_feedback_acquisition_45011_20261014/SGD0_RESULT.json'))
(OUT/'DRIVER_SGD0_RESULT.json').write_text(json.dumps(value,indent=2));print('CHANGED_DRIVER_SGD0_PASS')
