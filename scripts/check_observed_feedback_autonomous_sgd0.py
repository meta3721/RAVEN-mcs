"""One fixed-input critical-path check; intercept actual trainer;SGD0,no data trajectory."""
import os,sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
import numpy as np,torch,pandas as pd
from types import SimpleNamespace
from dataclasses import replace,asdict
from observed_feedback_pilot_common import build_arm
from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization,DiagnosticCollectionAuthorization,PILOT_SOURCE,PILOT_STRATEGIES,collection_authorization_from_dict
from raven_mcs_observed_feedback.schema import ControlConfig,Registration
from raven_mcs_observed_feedback.design import DesignConfiguration
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.stage1 import freeze_stage1
from raven_mcs_observed_feedback.pilot_controller import PilotController
from raven_mcs_observed_feedback.controller import Controller
from raven_mcs_observed_feedback.budget_client import RootClient
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
torch.set_num_threads(1);torch.set_num_interop_threads(1)
budget=RootClient(Path(os.environ['OF_ROOT_BUDGET_PATH']))
init_out=OUT/'initialization_only';init_out.mkdir(exist_ok=True)
inputs,common,p,freeze=build_arm('OF-v1',init_out,budget,freeze=not (OUT/'PILOT_FROZEN_PLAN.json').exists())
assert common.backend.local_optimizer_steps==0 and common.model_version==0 and not any(common.debt) and common.last_release is None
def rejects(fn):
 try:fn()
 except (ValueError,RuntimeError):return
 raise AssertionError('protection did not reject')
for s in PILOT_STRATEGIES:
 a=AutonomousPilotAuthorization(s);a.require(seed=45001,source=PILOT_SOURCE);assert collection_authorization_from_dict(asdict(a))==a
 rejects(lambda:a.require(seed=45011,source=PILOT_SOURCE))
 rejects(lambda:replace(a,strategy='unsupported').require(seed=45001,source=PILOT_SOURCE))
old=DiagnosticCollectionAuthorization();old.require(seed=45011,source=old.source);rejects(lambda:old.require(seed=45001,source=old.source))
config=ControlConfig(PILOT_SOURCE,DesignConfiguration(True,'fixed_input_explicit_on'))
def make(strategy):
 owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('FIXED_INPUT_SGD0_NO45001_TRAJECTORY',45001,100,3)),dataset=SimpleNamespace(),
  model=deterministic_common_ndmf(3,seed=0),aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.array([.5,.5]),num_groups=2,local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()))
 app=dict(consumption_policy=config.method_version,strategy=strategy,collection_role='P1_autonomous_P3_pre_pilot',T=100.,learning=dict(model='CommonNDMF_fixed_input',optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,initial_model_hash=owner._theta_hash(),scaler='fixed_input',feature_schema='existing'),service={'fixed_input':True},stage1={},data_identity='SGD0_fixed_input',target_identity='mu2')
 kwargs=dict(config=config,q_model=DiagnosticPrior(),seed=45001,data_identity='SGD0_fixed_input',target_identity='mu2',probability_applicability=app,clock_namespace=dict(run_id='SGD0_'+strategy,origin_utc='2026-10-14T00:00:00Z',unit='controlled_service_unit'),collection_authorization=AutonomousPilotAuthorization(strategy),root_budget=budget)
 rejects(lambda:connect_full_runner(owner,**kwargs))
 r=connect_full_runner(owner,calibration_only=True,open_time=20.,**kwargs);r.backend.freeze_stage1_context(0.);return r
arms={s:make(s) for s in PILOT_STRATEGIES}
assert len({id(r.backend.owner.model) for r in arms.values()})==4 and len({id(r.pool) for r in arms.values()})==4 and len({id(r.cache) for r in arms.values()})==4
checks=[]
for s,r in arms.items():
 ctrl=PilotController(s,root_budget=budget,save_reserve=34.808867,operation_root_ceiling=2.)
 saved_now,saved_open=r.now,r.window_open;r.now=1.;r.window_open=0.
 assert ctrl.decide(r).reason=='WARMUP' and ctrl.decide(r).action=='CLOSE'
 r.now=saved_now;r.window_open=saved_open
 entered=[]
 class Intercepted(Exception):pass
 def intercept(*args,**kwargs):entered.append(True);raise Intercepted()
 r.backend.owner._trainer.train_step=intercept
 for j in range(3):
  summary=freeze_stage1(config=config,target_opportunity=[.5,.5],lagged_opportunity=[.25,.25],p_obs=[.5,.5],observation=[1,1],group_ids=[0,1],num_groups=2,now=20.1,estimator_as_of=0.,estimator_version='fixed_input',provenance='hand_input_no_data_trajectory')
  r.on_register(Registration('k'+str(j),'c'+str(j),20.1,0,'tier-0','net-tier-0'),summary)
 records=[dict(spatial_id='0',absolute_time=0.,time_index=0,observed_value=1.,spatial_to_idx={'0':0,'1':1,'2':2},total_time_slots=1)]*2
 try:r.start_local_training('k0',records,authorization=r.collection_authorization)
 except Intercepted:pass
 else:raise AssertionError('real trainer not reached')
 assert entered and r.backend.local_optimizer_steps==0
 u=np.zeros(sum(t.numel() for t in r.backend.owner.theta.values()))
 for j in range(3):r.on_completion('k'+str(j),20.2,update=u)
 r.advance_time(20.5);d=ctrl.decide(r)
 if s=='fixed_time_2':assert d.action=='WAIT' and d.p2_solves==0
 if s=='fixed_time_0.5':assert d.action=='CLOSE'
 if s=='OF-v1':assert d.action==Controller(root_budget=budget,save_reserve=34.808867,operation_root_ceiling=2.).decide(r).action
 r.advance_time(24.);actual=r.on_grid(24.,ctrl);assert actual.reason=='DEADLINE' and r.model_version==1 and len(r.consumed)==3
 assert r.closures[-1]['configured_design']==r.closures[-1]['actual_design']==1
 # Current original warmup/terminal priorities; no trajectory or producer replay.
 r.advance_time(24.1);assert ctrl.decide(r).reason=='MIN_CLIENTS'
 r.now=100.;r.window_open=99.9;end=r.on_grid(100.,ctrl);assert end.reason=='TERMINAL' and r.ended
 checks.append(dict(strategy=s,trainer_intercepted=True,initial_decision=d.action,real_full_P2_apply=True,consumed=3,SGD=0))
assert all(r.backend.local_optimizer_steps==0 for r in arms.values())
result=dict(status='PASS',cases=checks,seed_authorization=True,old45011_protection=True,production_prior_rejected=True,isolated_bypass=False,independent_models_and_state=True,
 common_initial_identity=freeze['initial_identity'],SGD=0,GPU=0,q_fit=0,scope='one fixed-input critical-path check; actual initial45001 model frozen only, no45001 producer advancement')
(OUT/'SGD0_AUTONOMOUS_CHECK.json').write_text(json.dumps(result,indent=2));print('AUTONOMOUS_SGD0_PASS')
