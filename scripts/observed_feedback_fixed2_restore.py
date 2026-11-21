"""Actual fixed2 t5 saved model/RNG, not another fresh trajectory."""
from observed_feedback_recovery_common import *
from observed_feedback_recovery_io import durable_json
def restore_fixed2(arm_out,budget):
 require_resource_source_identity();parent=OUT/'fixed2';marker=parent/'trajectory/tick0050.complete.json';freeze=json.loads((parent/'ARM_FROZEN_PLAN.json').read_text());identity=json.loads(marker.read_text())['identity']
 packet,private=PairedCheckpointStore(marker.parent).read(marker,expected_identity=identity);assert packet['source_closure']==source_closure() and sha256_json(packet['state'])==packet['state_hash']
 (arm_out/'PUBLIC_CATALOGUE.parquet').write_bytes((OLD/'PUBLIC_CATALOGUE.parquet').read_bytes());inputs=load_inputs(ROOT,arm_out);assert inputs.data_id==freeze['scope']['data_identity'] and inputs.target_id==freeze['scope']['target_identity']
 config=ControlConfig.from_dict(freeze['config']);b=packet['state']['backend']
 with torch.device('meta'):model=CommonNDMF(num_spatial=len(inputs.clients))
 model.to_empty(device='cpu');ref=model.state_dict();model.load_state_dict({k:torch.tensor(v['values'],dtype=ref[k].dtype) for k,v in b['theta'].items()})
 owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('ACTUAL_FIXED2_SAVED_RESTORE',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
 holder=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=freeze['scope'],clock_namespace=freeze['clock_namespace'],calibration_only=True,collection_authorization=PilotRecoveryAuthorization('fixed_time_2'),root_budget=budget)
 r=DynamicWindowRunner.from_dict(packet['state'],backend=holder.backend,root_budget=budget)
 p=AuditedProducer(inputs,r,np.random.default_rng(0),np.random.default_rng(1),arm_out);p.restore(private['state'])
 assert sha256_json(r.checkpoint_state())==packet['state_hash'] and sha256_json(p.to_dict())==sha256_json(private['state'])
 assert r.now==5 and r.backend.local_optimizer_steps==170 and r.model_version==5 and private['next_grid_tick']==51 and p.next_clock==5 and p.next_client==0 and p.active_registration is None
 p.stop_after_steps=None;p.pause_requested=None
 check=dict(status='PASS',original_state_hash_equal_before_any_SGD_or_events=True,producer_RNG_hash_equal=True,restored_now=5,restored_logical_SGD=170,next_grid=51,original_clock=freeze['clock_namespace'],actual_resume_UTC=datetime.now(timezone.utc).isoformat(),parent_marker=str(marker),known_prior_physical_steps=266,known_discarded_SGD=96,physical_guard='S+96+1<=5000',fresh_model_initialization=False)
 return inputs,r,p,freeze,check
