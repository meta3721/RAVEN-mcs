"""Read/restore the completed real prefix, with no notices, decisions, or SGD."""
import sys,json,os,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));OUT=ROOT/'results_observed_feedback_continuation_45011_20261014'
import numpy as np,pandas as pd,torch
from types import SimpleNamespace
from raven_mcs_observed_feedback.schema import ControlConfig
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.acquisition import CausalProducer
from raven_mcs_observed_feedback.persistence import restore_pair,source_closure
from raven_mcs_observed_feedback.budget_client import RootClient
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
torch.set_num_threads(1);torch.set_num_interop_threads(1)
f=json.loads((OUT/'ACQUISITION_FROZEN_PLAN.json').read_text());e=json.loads((OUT/'EXECUTION_RESULT.json').read_text());marker=Path(e['last_complete_marker'])
assert e['status']=='STARTED_PREFIX_INCOMPLETE' and e['actual_SGD']==32 and e['now']==1.07
identity=json.loads(marker.read_text())['identity'];store=PairedCheckpointStore(marker.parent)
packet,private=store.read(marker,expected_identity=identity)
assert packet['source_closure']==source_closure()
config=ControlConfig.from_dict(f['config']);scope=f['scope'];mu=f['public_target']['mu'];pi={(a,b):v for a,b,v in f['public_target']['pi_target']};opp={(a,b):v for a,b,v in scope['stage1']['pi_opp_joint']}
# A fresh seed0 test owner is only a shape holder. Restore loads the actual45011 tensors/RNG; nothing executes afterward.
o=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('RESTORE_READONLY_NOT_NEW_RUN',0,100,43)),dataset=SimpleNamespace(),model=deterministic_common_ndmf(43,seed=0),aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(mu),num_groups=len(mu),local_steps=1,learning_rate=.01,seed=45011,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=pi,pi_opp_joint=opp)
from raven_mcs_observed_feedback.authorization import DiagnosticCollectionAuthorization
budget=RootClient(Path(os.environ['OF_ROOT_BUDGET_PATH']))
test=connect_full_runner(o,config=config,q_model=DiagnosticPrior(),seed=45011,data_identity=scope['data_identity'],target_identity=scope['target_identity'],probability_applicability=scope,clock_namespace=f['clock_namespace'],calibration_only=True,collection_authorization=DiagnosticCollectionAuthorization(),root_budget=budget)
r,priv=restore_pair(store,marker,identity=identity,backend=test.backend,expected_config=config,expected_data=scope['data_identity'],expected_target=scope['target_identity'],root_budget=budget)
p=CausalProducer(SimpleNamespace(clients=sorted({a for a,b in opp})),r,np.random.default_rng(0),np.random.default_rng(1));p.restore(priv['state'])
assert sha256_json(p.to_dict())==sha256_json(private['state'])
assert sha256_json(r.checkpoint_state())==packet['state_hash']
assert r.backend.local_optimizer_steps==32 and len(p.training_samples)==32 and not r.ended
assert r.now==1.07 and private['next_grid_tick']==11 and p.next_clock==1 and p.next_client==3
assert all(rec.consumed is not None or rec.right_censored_at==1.07 for rec in r.attempts.values())
rows=[json.loads(line) for line in (OUT/'DECISION_METRICS.jsonl').read_text().splitlines()]
assert len(rows)==10 and [v['time'] for v in rows]==[round(t*.1,10) for t in range(1,11)]
assert all(v['actual_request_root_upper']<=2. for v in rows)
for row in rows:
 if row['preview']:
  assert abs(sum(row['preview']['alpha'])-1)<1e-7
  assert row['preview']['config']['design']['enabled'] if 'config' in row['preview'] else True
reasons={}
for rec in r.attempts.values():reasons[rec.terminal_reason or 'unmatured']=reasons.get(rec.terminal_reason or 'unmatured',0)+1
preserved=json.loads((ROOT/'results_observed_feedback_acquisition_45011_20261014/PROTECTED_HISTORY.json').read_text())
for path in (ROOT/'ccf-review-report/observed_feedback_acquisition_45011_20261014').glob('*.md'):
 preserved[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
changed=[path for path,h in preserved.items() if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=h]
assert not changed
value=dict(status='PASS',read_only=True,new_SGD=0,actual_prefix_SGD=32,marker=str(marker),source_closure_equal=True,model_state_hash_equal=True,private_producer_hash_equal=True,
 clock_namespace=r.clock_namespace,now=r.now,next_grid_tick=private['next_grid_tick'],next_clock=p.next_clock,next_client=p.next_client,active_registration=p.active_registration,
 attempts=len(r.attempts),R1=sum(x.R for x in r.attempts.values()),E0=sum(1-x.E for x in r.attempts.values()),consumed=len(r.consumed),unmatured=sum(x.consumed is None for x in r.attempts.values()),physical_pending_R1=sum(x.R and x.physical_outcome=='pending' for x in r.attempts.values()),reasons=reasons,
 pending_private_notices=len(p.pending),decisions=len(rows),regular_20_to_100_decisions=0,model_version=r.model_version,closures=len(r.closures),nonempty_closures=sum(not x['empty'] for x in r.closures),
 P=len(r.pool),F=len(r.in_flight),training_local_CPU=sum(x['CPU'] for x in p.training_samples),training_local_wall=sum(x['wall'] for x in p.training_samples),maximum_local_step_CPU=max(x['CPU'] for x in p.training_samples),maximum_local_step_wall=max(x['wall'] for x in p.training_samples),maximum_actual_request_root_upper=max(x['actual_request_root_upper'] for x in rows),
 P2_new_calculations=sum(x['p2_solves'] for x in rows),cache_hits=sum(x['cache_hits'] for x in rows),F_max_registration=max(x.public_encoding['raw_F_count'] for x in r.attempts.values()),public_encoding_resource_missing=sum(x.public_encoding['support']=='ENCODING_DOMAIN_OR_RESOURCE_MISSING' for x in r.attempts.values()),protected_unchanged=len(preserved),changed_history=changed,worker_PID=os.getpid())
(OUT/'PREFIX_RESTORE_CHECK.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))
