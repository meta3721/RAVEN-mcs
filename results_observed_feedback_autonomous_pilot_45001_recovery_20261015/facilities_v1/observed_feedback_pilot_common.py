"""Four independent models; shared deterministic initial values/exogenous stream mapping."""
import sys,json,copy,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
import numpy as np,pandas as pd,torch
from types import SimpleNamespace
from datetime import datetime,timezone
from dataclasses import asdict
from raven_mcs_observed_feedback import METHOD_VERSION
from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization,PILOT_SOURCE,PILOT_STRATEGIES
from raven_mcs_observed_feedback.schema import ControlConfig
from raven_mcs_observed_feedback.design import DesignConfiguration
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.acquisition import CausalProducer
from raven_mcs_observed_feedback.persistence import source_closure
from raven_mcs.experiments.calibration_first import load_inputs
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
ARM_NAMES=dict(zip(PILOT_STRATEGIES,('of','fixed05','fixed2','noqstop')))
def streams():
 children=np.random.SeedSequence(45001).spawn(4);mapping=dict(zip(('model_init','local_dropout','opportunity_observation','service'),children))
 return mapping,{k:dict(entropy=v.entropy,spawn_key=list(v.spawn_key),mapped_seed=int(v.generate_state(1)[0])) for k,v in mapping.items()}
def build_arm(strategy,arm_out,budget,*,freeze=False):
 assert strategy in PILOT_STRATEGIES
 assert json.loads((OUT/'SEED_REVIEW.json').read_text())['status']=='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND'
 if not (OUT/'PUBLIC_CATALOGUE.parquet').exists():
  cols=['unit_id','spatial_id','absolute_time','time_index','target_group','opportunity_stratum','split','support_flag']
  pd.read_parquet(ROOT/'results_main_rebuild_r1/data/traffic/atomic_units.parquet',columns=cols).to_parquet(OUT/'PUBLIC_CATALOGUE.parquet',index=False)
 inputs=load_inputs(ROOT,OUT);mapping,states=streams()
 random.seed(states['model_init']['mapped_seed']);np.random.seed(states['model_init']['mapped_seed'])
 config=ControlConfig(PILOT_SOURCE,DesignConfiguration(True,'explicit_45001_all_four_arms_whole_run_on'))
 model=deterministic_common_ndmf(len(inputs.clients),seed=states['model_init']['mapped_seed'])
 owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('OF_AUTONOMOUS_PILOT_CAUSAL_NOT_REPLAY',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,
  aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,
  design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
 app=copy.deepcopy(json.loads((ROOT/'results_observed_feedback_continuation_45011_20261014/ACQUISITION_FROZEN_PLAN.json').read_text())['scope'])
 app.update(strategy=strategy,collection_role='P1_autonomous_P3_pre_pilot',data_identity=inputs.data_id,target_identity=inputs.target_id)
 app['learning']['initial_model_hash']=owner._theta_hash();app['learning']['scaler']=inputs.scaler
 app['service'].update(streams=states,CPU_limit=3000,batch='user20261014_autonomous_pilot_45001')
 app['stop_rule']=dict(strategy=strategy,theta=.02,kappa=0. if strategy=='OF-no-Q-stop' else .10,nu=.20,common_priority=['terminal','warmup_fixed1','deadline4','K<3_wait','free_strategy'])
 clock=dict(run_id='OF-v1/P1_autonomous_P3_pre_pilot/45001/'+strategy+'/'+arm_out.name,origin_utc=datetime.now(timezone.utc).isoformat(),unit='controlled_service_unit',UTC_bridge='actual notice UTC; logical service units are not elapsed UTC')
 auth=AutonomousPilotAuthorization(strategy)
 r=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=app,clock_namespace=clock,
  calibration_only=True,collection_authorization=auth,root_budget=budget)
 r.backend.freeze_stage1_context(0.);torch.manual_seed(states['local_dropout']['mapped_seed'])
 initial=r.backend.to_dict();initial_identity=dict(theta=owner._theta_hash(),backend_hash=sha256_json(initial),torch_rng_hash=sha256_json(initial['torch_rng']),data=inputs.data_id,target=inputs.target_id,config=config.to_dict(),settings=asdict(r.settings),streams=states)
 if freeze:
  with (OUT/'INITIAL_BACKEND.json').open('x') as f:json.dump(initial,f)
  shared=dict(initial_identity=initial_identity,source_closure=source_closure(),scope=json.loads((OUT/'PILOT_SCOPE.json').read_text()),mu=list(inputs.mu),public_target=inputs.target,seed=45001,
   strategy_stop_rules={s:dict(theta=.02,kappa=0. if s=='OF-no-Q-stop' else .10,nu=.20) for s in PILOT_STRATEGIES},initial_all_Q_zero=True,initial_L_empty=True)
  with (OUT/'PILOT_FROZEN_PLAN.json').open('x') as f:json.dump(shared,f,indent=2)
 else:
  shared=json.loads((OUT/'PILOT_FROZEN_PLAN.json').read_text());assert shared['source_closure']==source_closure();assert shared['initial_identity']==initial_identity,'INITIAL_PAIRING_MISMATCH'
  assert sha256_json(initial)==sha256_json(json.loads((OUT/'INITIAL_BACKEND.json').read_text()))
 p=AuditedProducer(inputs,r,np.random.default_rng(mapping['opportunity_observation']),np.random.default_rng(mapping['service']),arm_out)
 frozen=dict(method=METHOD_VERSION,strategy=strategy,seed=45001,config=config.to_dict(),settings=asdict(r.settings),scope=app,clock_namespace=clock,authorization=asdict(auth),initial_identity=initial_identity,source_closure=source_closure(),public_target=inputs.target)
 return inputs,r,p,frozen

def plain(x):
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,(list,tuple)):return [plain(v) for v in x]
 if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
 return x
class RecordedRNG:
 def __init__(self,rng,producer,stream):self.rng=rng;self.producer=producer;self.stream=stream
 @property
 def bit_generator(self):return self.rng.bit_generator
 def __getattr__(self,name):
  if name not in {'choice','random','integers','lognormal'}:return getattr(self.rng,name)
  def call(*args,**kwargs):
   result=getattr(self.rng,name)(*args,**kwargs)
   params=dict(args=plain(args),kwargs=plain(kwargs))
   self.producer.current_draws.append(dict(stream=self.stream,draw=name,parameters_hash=sha256_json(params),value=plain(result)))
   return result
  return call
class AuditedProducer(CausalProducer):
 def __init__(self,inputs,runner,opp_rng,service_rng,out):
  super().__init__(inputs,runner,opp_rng,service_rng);self.out=Path(out);self.current_draws=[]
  self.opportunity_rng=RecordedRNG(opp_rng,self,'opportunity_observation');self.service_rng=RecordedRNG(service_rng,self,'service')
 def register_current(self):
  key=f'{self.next_clock:03d}::{self.inputs.clients[self.next_client]}';self.current_draws=[]
  super().register_current()
  rec=self.runner.attempts[key];pending=next((x for x in self.pending if x[1]==key),None)
  value=dict(key=key,draws=self.current_draws,draws_hash=sha256_json(self.current_draws),R=rec.R,E=rec.E,downloaded_version=rec.registration.downloaded_version,
   actual_service_notice=None if pending is None else dict(at=pending[0],outcome=pending[2]),training_CPU=next((x['CPU'] for x in reversed(self.training_samples) if x['key']==key),None))
  with (self.out/'PRIVATE_EXOGENOUS_PAIRING.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')
