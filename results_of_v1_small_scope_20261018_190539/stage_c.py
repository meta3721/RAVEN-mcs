"""One authorized autonomous GAP arm, branching at common t20, never replaying future payloads."""
import csv, gc, os, traceback, collections, hashlib
from gap_local import *
from observed_feedback_recovery_account import RecoveryAccount
from raven_mcs_observed_feedback.persistence import save_pair
from raven_mcs_execution.budget import checkpoint_due
ARM=OUT/'gap';ARM.mkdir(exist_ok=False)
durable_json(ARM/'LAUNCH_COST.json',json.loads((OUT/'LAUNCH_COST.json').read_text()))

def append(name,value):
 with (ARM/name).open('a',encoding='utf-8') as f:f.write(json.dumps(value,allow_nan=False)+'\n')

def main():
 assert json.loads((OUT/'A_RESULT.json').read_text())['status']=='PASS'
 assert json.loads((OUT/'B_RESULT.json').read_text())['status']=='PASS'
 a=RecoveryAccount(ARM);a.reserve=40.;a.session_start=time.perf_counter()
 start=time.perf_counter();wall_cap=float(os.environ['OF_ARM_WALL_LIMIT']);low_since=None;min_mem=2**64;last_mem_log=0.
 r=p=None;branch=None;next_tick=201;last_saved=200;last_marker=None;save_capacity=22.;close_capacity=18.;base_steps=None;failure=None;status='NOT_STARTED'
 store=PairedCheckpointStore(ARM/'trajectory')
 def memcheck():
  nonlocal low_since,min_mem,last_mem_log
  m=available_memory();min_mem=min(min_mem,m['available_bytes']);now=time.perf_counter()
  if now-last_mem_log>=5.:append('MEMORY.jsonl',m);last_mem_log=now
  if m['available_bytes']<2*1024**3:
   if low_since is None:low_since=now
  else:low_since=None
  return low_since is not None and now-low_since>=30.
 def persist(name):
  nonlocal last_marker,last_saved,save_capacity
  assert source_closure()==branch['source_closure']
  private=dict(T=100.,tick=r.now/.1,next_grid_tick=next_tick,clock_namespace=r.clock_namespace,state=p.to_dict(),c_ref=FREEZE['c_ref'],
    parent_checkpoint=branch['parent'],parent_tick=200,parent_SGD=base_steps,decision_start_tick=201,role=ROLE,local_adapter_hash=file_hash(OUT/'gap_local.py'),driver_hash=file_hash(__file__))
  marker=a.operation('save',lambda:save_pair(r,store,name,producer_state=private,budget=a.root,save_reserve=a.reserve),save_capacity)
  a.checkpoint_session(marker,r,p,next_tick,0)
  last_marker=marker;last_saved=round(r.now/.1);save_capacity=max(save_capacity,2*a.maxima['save']*1.25);a.reserve=save_capacity+close_capacity
  append('SAVE_MEASUREMENTS.jsonl',dict(time=r.now,marker=str(marker),logical_SGD=r.backend.local_optimizer_steps,new_SGD=r.backend.local_optimizer_steps-base_steps,save_root_upper=a.maxima['save'],reserve=a.reserve,sizes=json.loads(marker.read_text())['sizes']))
  gc.collect()
  return marker
 try:
  m=available_memory();durable_json(ARM/'MEMORY_BEFORE_MODEL.json',m)
  if m['available_bytes']<2*1024**3:raise RuntimeError('MEMORY_BELOW_2GiB_BEFORE_TRAINING')
  r,p,branch=a.operation('initialization',lambda:restore_parent(200,a.root,tag='C_unique_autonomous_arm'),35.)
  p.out=ARM;base_steps=r.backend.local_optimizer_steps
  assert r.now==20. and r.model_version==20 and len(r.decisions)==200 and p.next_clock==20 and p.next_client==0 and p.active_registration is None
  assert r.last_release.time==20. and r.last_release.ell+.02*r.last_release.age==FREEZE['c_ref']
  m=available_memory();durable_json(ARM/'MEMORY_BEFORE_TRAINING.json',m)
  # Retain a 512MiB saving/growth allowance above the required 2GiB margin.
  if m['available_bytes']<2.5*1024**3:raise RuntimeError('MEMORY_SAVING_HEADROOM_BELOW_2GiB_PLUS_512MiB')
  frozen=dict(FREEZE,branch=branch,config=r.config.to_dict(),settings=asdict(r.settings),scope=r.probability_applicability,clock_namespace=r.clock_namespace,
    local_source_hashes={p.name:file_hash(p) for p in (OUT/'gap_local.py',OUT/'stage_c.py',OUT/'run_metered.py')},new_arm_freeze_UTC=datetime.now(timezone.utc).isoformat())
  durable_json(ARM/'ARM_FROZEN_PLAN.json',frozen)
  # The original records are common warmup only; no t>20 payloads are reused.
  for name in ('DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):
   n=860 if name.startswith('PRIVATE') else 200
   with (PARENT/name).open('rb') as src,(ARM/name).open('xb') as dest:
    for _ in range(n):dest.write(next(src))
  def guarded_operation(category,fn,ceiling=2.,online=False):
   if category=='training':
    if r.backend.local_optimizer_steps-base_steps+1>5000:raise RuntimeError('NEW_LOCAL_SGD_5000_LIMIT')
    if memcheck():raise RuntimeError('MEMORY_BELOW_2GiB_SUSTAINED_30s')
   return a.operation(category,fn,ceiling,online)
  p.operation=guarded_operation;p.pause_requested=memcheck
  control=GapController(c_ref=FREEZE['c_ref'],root_budget=a.root,save_reserve=a.reserve,operation_root_ceiling=2.)
  status='STARTED_PREFIX_INCOMPLETE';persist('tick0200_branch')
  while next_tick<=1000:
   if time.perf_counter()-start>=wall_cap-60:raise RuntimeError('ACTIVITY_WALL_SAVE_AND_STOP')
   at=round(next_tick*.1,10)
   if not p.notices_through(at):raise RuntimeError('MEMORY_PAUSE_SAVE_AND_STOP')
   context={}
   def pre():
    r.advance_time(at);s=r.snapshot();context.update(snapshot=asdict(s),fingerprint=s.fingerprint,window=r.window_id,last=s.last_release)
   a.operation('events',pre)
   control.save_reserve=a.reserve
   d=a.operation('online',lambda:r.on_grid(at,control),2.,online=True);online=a.records[-1]
   def diagnostics():
    forced=d.reason in {'TERMINAL','WARMUP','DEADLINE','MIN_CLIENTS'}
    dynamic_action=d.action;dynamic_B=None
    if not forced:
     L=context['last'];cm=L.ell+.02*L.age if L else 1.
     dynamic_B=cm-d.preview.ell-.02*d.preview.age+dict(d.components)['patience']
     dynamic_action='CLOSE' if dynamic_B>=.0200001 else 'WAIT'
     assert dict(d.components)['c_minus']==FREEZE['c_ref']
    append('DECISION_SNAPSHOTS.jsonl',dict(time=at,fingerprint=context['fingerprint'],snapshot=context['snapshot']))
    append('DECISION_METRICS.jsonl',dict(time=at,window=context['window'],snapshot_hash=context['fingerprint'],P=len(context['snapshot']['pool']),F=len(context['snapshot']['in_flight']),action=d.action,reason=d.reason,B=d.B,components=dict(d.components),preview=d.preview.to_dict() if d.preview else None,
     p2_solves=d.p2_solves,cache_hits=d.cache_hits,shadow=dict(forced=forced,dynamic_reference_noQ=dynamic_action,dynamic_B=dynamic_B,P2_recomputed=False),model_version_after=r.model_version,actual_request_root_upper=online['root_upper_CPU'],actual_request_root_difference=online['request_root_difference']))
    assert len(r.consumed)==sum(x.consumed==1 for x in r.attempts.values())
    if r.window_id!=context['window']:p.after_close();p.reclaim_terminal_storage()
   a.operation('events',diagnostics);next_tick+=1
   remaining=a.root.read()['effective_remaining']
   if next_tick==1001 or checkpoint_due(next_tick-1,last_saved,remaining=remaining,save_reserve=a.reserve,operation_root_ceiling=2.):
    persist('tick%04d'%(next_tick-1))
    durable_json(ARM/'PROGRESS.json',dict(time=r.now,grid=next_tick-1,new_SGD=r.backend.local_optimizer_steps-base_steps,logical_SGD=r.backend.local_optimizer_steps,registrations=len(r.attempts),model_version=r.model_version,P2_solves=r.cache.solves,cache_hits=r.cache.hits,root_CPU=a.root.read()['command_used'],remaining_effective_CPU=a.root.read()['effective_remaining'],reserve=a.reserve,last_complete_marker=str(last_marker),available_memory=available_memory()))
   if a.root.read()['effective_remaining']<a.reserve+4:raise RuntimeError('ROOT_HEADROOM_SAVE_AND_STOP')
   if memcheck():raise RuntimeError('MEMORY_BELOW_2GiB_SUSTAINED_30s')
  assert r.ended and r.now==100. and len(r.decisions)==1000 and p.next_clock==100 and p.active_registration is None
  assert r.backend.local_optimizer_steps-base_steps<=5000
  assert all(x.consumed is not None and x.right_censored_at is None for x in r.attempts.values())
  status='COMPLETE_T100_ACQUISITION'
 except Exception as exc:
  failure=dict(error=repr(exc),traceback=traceback.format_exc(),time=r.now if r else None,next_tick=next_tick)
  if r is not None and branch is not None and r.fault is None and not r.ended:
   try:r.finish_observation();persist('stopped_%04d'%next_tick)
   except Exception as save_exc:failure['save_error']=repr(save_exc)
 finally:
  if r is not None:
   def evidence():
    durable_json(ARM/'ATTEMPT_LABELS.json',[x.to_dict() for x in r.attempts.values()]);durable_json(ARM/'PUBLICATION_BRIDGE.json',p.publication_bridge)
    durable_json(ARM/'CLOSURES.json',r.closures);durable_json(ARM/'OPERATION_RECORDS.json',a.records)
   a.reserve=0.
   try:a.operation('events',evidence,close_capacity)
   except Exception as exc:
    failure=failure or {};failure['final_evidence_error']=repr(exc);status='STARTED_PREFIX_INCOMPLETE'
  durable_json(ARM/'EXECUTION_RESULT.json',dict(status=status,failure=failure,strategy=STRATEGY,seed=45001,now=r.now if r else None,next_grid_tick=next_tick,parent_checkpoint=branch['parent'] if branch else None,parent_SGD=base_steps,
    actual_new_SGD=r.backend.local_optimizer_steps-base_steps if r and base_steps is not None else 0,logical_SGD=r.backend.local_optimizer_steps if r else None,last_complete_marker=str(last_marker) if last_marker else None,
    GPU=0,q_fit=0,min_available_memory_bytes=min_mem,spent=a.spent,maxima=a.maxima,wall_seconds=time.perf_counter()-start,state='WAITING_USER_REVIEW',full_P3=False,paper_modified=False))
 print(status);return 0 if status=='COMPLETE_T100_ACQUISITION' else 2
if __name__=='__main__':raise SystemExit(main())
