import json, time, traceback, csv, gc
from dataclasses import asdict,replace
from types import SimpleNamespace
from gap_local import *
from observed_feedback_recovery_account import RecoveryAccount
from raven_mcs_observed_feedback.persistence import save_pair

def main():
 a=RecoveryAccount(OUT);a.reserve=25.; result=dict(stage='B',status='FAIL',new_SGD=0)
 try:
  r,p,branch=a.operation('initialization',lambda:restore_parent(350,a.root,tag='B_SGD0_interface_test'),30.)
  initial_steps=r.backend.local_optimizer_steps
  control=GapController(c_ref=FREEZE['c_ref'],root_budget=a.root,save_reserve=a.reserve,operation_root_ceiling=2.)
  d=a.operation('online',lambda:control.decide(r),2.,online=True)
  with (OUT/'A_PER_GRID.csv').open() as f:expected=next(x for x in csv.DictReader(f) if float(x['time'])==35.)
  assert d.action==expected['shadow_action'] and abs(d.B-float(expected['B_gap']))<1e-12
  assert d.preview is not None
  old_last=r.last_release;old_Q=r.debt;old_version=r.model_version;calls=[];original=r.backend.apply
  def recorded(keys,alpha,eta,version):
   calls.append(dict(keys=list(keys),alpha=list(alpha),eta=eta,version=version));return original(keys,alpha,eta,version)
  r.backend.apply=recorded
  close=a.operation('online',lambda:r.apply_release(d.preview,reason='B_SGD0_PREVIEW_APPLY_VERIFICATION'),2.,online=True)
  r.backend.apply=original
  assert len(calls)==1 and calls[0]['keys']==list(d.preview.keys) and calls[0]['alpha']==list(d.preview.alpha) and calls[0]['eta']==.01
  assert r.model_version==old_version+1 and r.last_release!=old_last and control.c_ref==FREEZE['c_ref']
  assert tuple(close['preview']['alpha'])==tuple(d.preview.alpha) and tuple(close['preview']['omega'])==tuple(d.preview.omega)
  assert r.backend.local_optimizer_steps==initial_steps
  # Same priority, tested without any synthetic messages or autonomous replay.
  s=r.snapshot();priority=[]
  for now,opened,pool,reason,action in [(100.,99.,s.pool,'TERMINAL','CLOSE'),(20.,19.,s.pool,'WARMUP','CLOSE'),(19.5,19.,s.pool,'WARMUP','WAIT'),(24.,20.,(), 'DEADLINE','CLOSE'),(20.1,20.,(),'MIN_CLIENTS','WAIT')]:
   # Priority-only call stub, never a valid lifecycle snapshot or replay input.
   priority_snapshot=SimpleNamespace(now=now,window_open=opened,pool=pool)
   proxy=SimpleNamespace(collection_authorization=r.collection_authorization,calibration_only=True,isolated_test=False,seed=45001,config=r.config,probability_applicability=r.probability_applicability,cache=r.cache,
    snapshot=lambda value=priority_snapshot:value,preview_release=lambda:d.preview)
   out=control.decide(proxy);assert (out.reason,out.action)==(reason,action);priority.append(dict(now=now,reason=out.reason,action=out.action))
  from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization
  denied=[]
  for auth,seed in [(AutonomousPilotAuthorization(STRATEGY),45001),(GapAuthorization(),45011)]:
   try:auth.require(seed=seed,source=PILOT_SOURCE)
   except InputError:denied.append(True)
   else:raise AssertionError('unauthorized strategy/seed accepted')
  p.after_close();p.reclaim_terminal_storage()
  private=dict(T=100.,tick=r.now/.1,next_grid_tick=351,clock_namespace=r.clock_namespace,state=p.to_dict(),c_ref=control.c_ref,role='B_SGD0_interface_test_not_autonomous_evidence')
  marker=a.operation('save',lambda:save_pair(r,PairedCheckpointStore(OUT/'B_checkpoints'),'SGD0_post_apply',producer_state=private,budget=a.root,save_reserve=a.reserve),20.)
  expected_hash=sha256_json(r.checkpoint_state());expected_producer=sha256_json(p.to_dict());identity=json.loads(marker.read_text())['identity']
  del r,p,private;gc.collect()
  packet,private=PairedCheckpointStore(marker.parent).read(marker,expected_identity=identity)
  r,p=a.operation('initialization',lambda:restore_gap(packet,private,a.root),25.)
  assert sha256_json(r.checkpoint_state())==expected_hash and sha256_json(p.to_dict())==expected_producer
  assert r.backend.local_optimizer_steps==initial_steps
  result.update(status='PASS',formula_input_time=35.,formula_expected_action=expected['shadow_action'],formula_B=d.B,formula_matches_A=True,
   actual_backend_apply=calls[0],preview_binding_equal=True,fixed_reference_after_release=control.c_ref,last_release_changed=True,
   priority=priority,old_strategy_and_seed_guards_preserved=all(denied),local_new_identity_roundtrip=True,roundtrip_marker=str(marker),
   source_closure_unchanged=source_closure()==branch['source_closure'],parent_branch=branch,available_memory=available_memory(),new_SGD=r.backend.local_optimizer_steps-initial_steps)
 except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
 attempts=list(OUT.glob('B_RESULT_attempt*.json'));durable_json(OUT/('B_RESULT_attempt%d.json'%(len(attempts)+1)),result)
 if result['status']=='PASS':durable_json(OUT/'B_RESULT.json',result)
 print(json.dumps({k:v for k,v in result.items() if k not in ('parent_branch','actual_backend_apply')}))
 return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
