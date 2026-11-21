"""Explicit resource migration, unchanged scientific identity and probability scope."""
import sys,json,hashlib,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from observed_feedback_pilot_common import *
from raven_mcs_observed_feedback.authorization import PilotRecoveryAuthorization
from raven_mcs_observed_feedback.lifecycle import DynamicWindowRunner
from observed_feedback_recovery_io import durable_json,file_hash
OLD=OUT
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
def require_resource_source_identity():
 migration=json.loads((OUT/'SOURCE_RESOURCE_MIGRATION.json').read_text());old=migration['old_manifest'];current=source_closure()
 assert set(old)==set(current)
 delta={p for p in old if old[p]!=current[p]};assert delta==set(migration['changed'])
 for p,v in migration['changed'].items():assert old[p]==v['old']==file_hash(v['archive']) and current[p]==v['new']
 return current
def fresh_arm(strategy,arm_out,budget):
 # Execute an isolated copy of the original builder with its guarded closure
 # comparator changed ONLY for the archived resource-authorization file.
 import observed_feedback_pilot_common as original
 current=require_resource_source_identity();old=json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text())['source_closure']
 def guarded_old_closure():require_resource_source_identity();return old
 saved=original.source_closure;original.source_closure=guarded_old_closure
 try:inputs,r,p,freeze=original.build_arm(strategy,arm_out,budget)
 finally:original.source_closure=saved
 before=r.checkpoint_state();r.collection_authorization=PilotRecoveryAuthorization(strategy);r.collection_authorization.require(seed=45001,source=r.config.source)
 after=r.checkpoint_state();oldauth=before.pop('collection_authorization');newauth=after.pop('collection_authorization');assert sha256_json(before)==sha256_json(after)
 freeze.update(source_closure=current,authorization=newauth,resource_extension=json.loads((OUT/'RESOURCE_AUTHORITY.json').read_text()),original_authorization=oldauth)
 return inputs,r,p,freeze
def restore_fixed05(arm_out,budget):
 require_resource_source_identity()
 parent=OLD/'fixed05';marker=parent/'trajectory/tick0750.complete.json';freeze=json.loads((parent/'ARM_FROZEN_PLAN.json').read_text());identity=json.loads(marker.read_text())['identity']
 packet,private=PairedCheckpointStore(marker.parent).read(marker,expected_identity=identity)
 assert packet['source_closure']==freeze['source_closure']==json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text())['source_closure']
 assert sha256_json(packet['state'])==packet['state_hash']
 (arm_out/'PUBLIC_CATALOGUE.parquet').write_bytes((OLD/'PUBLIC_CATALOGUE.parquet').read_bytes());inputs=load_inputs(ROOT,arm_out)
 assert inputs.data_id==freeze['scope']['data_identity'] and inputs.target_id==freeze['scope']['target_identity']
 config=ControlConfig.from_dict(freeze['config']);b=packet['state']['backend']
 with torch.device('meta'):model=CommonNDMF(num_spatial=len(inputs.clients))
 model.to_empty(device='cpu');reference=model.state_dict();model.load_state_dict({k:torch.tensor(v['values'],dtype=reference[k].dtype) for k,v in b['theta'].items()})
 owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('OF45001_ACTUAL_RESTORE',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
 holder=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=freeze['scope'],clock_namespace=freeze['clock_namespace'],calibration_only=True,collection_authorization=AutonomousPilotAuthorization('fixed_time_0.5'),root_budget=budget)
 # Original packet has its own archived computational identity. The only
 # allowed source delta has been checked above; no arbitrary hash replacement.
 r=DynamicWindowRunner.from_dict(packet['state'],backend=holder.backend,root_budget=budget)
 p=AuditedProducer(inputs,r,np.random.default_rng(0),np.random.default_rng(1),arm_out);p.restore(private['state'])
 assert sha256_json(r.checkpoint_state())==packet['state_hash'];assert sha256_json(p.to_dict())==sha256_json(private['state'])
 assert r.now==75 and r.backend.local_optimizer_steps==2493 and r.model_version==128 and private['next_grid_tick']==751 and p.next_clock==75 and p.next_client==0 and p.active_registration is None
 before=r.checkpoint_state();r.collection_authorization=PilotRecoveryAuthorization('fixed_time_0.5');r.collection_authorization.require(seed=45001,source=r.config.source)
 after=r.checkpoint_state();oldauth=before.pop('collection_authorization');newauth=after.pop('collection_authorization');assert sha256_json(before)==sha256_json(after)
 p.stop_after_steps=None;p.pause_requested=None
 freeze.update(source_closure=source_closure(),authorization=newauth,original_authorization=oldauth,resource_extension=json.loads((OUT/'RESOURCE_AUTHORITY.json').read_text()))
 return inputs,r,p,freeze,dict(status='PASS',original_state_hash_equal_before_any_SGD_or_events=True,producer_RNG_hash_equal=True,numerical_state_unchanged_by_resource_migration=True,only_state_delta='collection_authorization',original_run_id=identity['clock_namespace']['run_id'],original_clock=freeze['clock_namespace'],actual_resume_UTC=datetime.now(timezone.utc).isoformat(),checkpoint=str(marker),restored_now=75,restored_logical_SGD=2493,next_grid=751,unknown_old_physical_offset_upper=1075)
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.models.common_ndmf import CommonNDMF
