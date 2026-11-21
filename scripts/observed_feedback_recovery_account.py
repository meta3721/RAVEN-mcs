"""Same root admission/online bound; atomic category and durable session evidence."""
import json,os,time
from pathlib import Path
from observed_feedback_pilot_account import PilotAccount
from observed_feedback_recovery_io import durable_json,sync_existing
from raven_mcs_observed_feedback.accounting import BudgetStop
from raven_mcs_observed_feedback.budget_client import read_shared_json
class RecoveryAccount(PilotAccount):
 def after(self,stamp):
  deadline=time.perf_counter()+10.
  while True:
   v=read_shared_json(self.root.path)
   if v['finished']:raise RuntimeError('root budget unavailable / finished')
   if v['wall_stamp']>=stamp+.01:return v
   if time.perf_counter()>deadline:raise RuntimeError('root budget stale; no new operation')
   time.sleep(.005)
 def operation(self,category,fn,ceiling=2.,online=False):
  if self.current_category is not None:raise RuntimeError('nested category attribution prohibited')
  begin=self.after(time.perf_counter());cpu=time.process_time();wall=time.perf_counter();error=None;value=None;self.current_category=category
  try:
   if not self.root.can_plan(0 if category=='save' else self.reserve,operation_root_ceiling=ceiling):raise BudgetStop('ROOT_HEADROOM_'+category)
   value=fn()
  except Exception as exc:error=exc
  done=time.perf_counter();end=self.after(done);local=time.process_time()-cpu
  attribution=end['command_used']-self.last_cost+(self.bootstrap if self.last_cost==0 else 0.)
  self.last_cost=end['command_used'];self.spent[category]+=attribution
  delta=end['command_used']-begin['command_used'];monitor=end['driver_CPU']-begin['driver_CPU']
  upper=max(delta+.02,local+monitor+.02);self.maxima[category]=max(self.maxima.get(category,0.),upper)
  record=dict(index=len(self.records),category=category,attributed_root_CPU=attribution,request_root_difference=delta,root_upper_CPU=upper,worker_local_CPU=local,monitor_CPU=monitor,wall=time.perf_counter()-wall,root_id=end['root_id'],root_begin_sequence=begin['sequence'],root_end_sequence=end['sequence'],error=repr(error) if error else None,operation_kind=getattr(fn,'__name__','call'))
  self.records.append(record);self.current_category=None
  with (self.out/'COST_RECORDS.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
  durable_json(self.out/'CATEGORY_LIVE.json',dict(spent=self.spent,maxima=self.maxima,last_root_cost=self.last_cost,record_count=len(self.records)))
  if online:
   # Include the diagnostic publication and its synchronization in the actual
   # complete online request; claim that last gap once in the online category.
   final=self.after(time.perf_counter());extra=final['command_used']-self.last_cost
   self.last_cost=final['command_used'];self.spent[category]+=extra
   upper=max(upper,final['command_used']-begin['command_used']+.02,time.process_time()-cpu+final['driver_CPU']-begin['driver_CPU']+.02)
   record.update(attributed_root_CPU=attribution+extra,request_root_difference=final['command_used']-begin['command_used'],root_upper_CPU=upper,root_end_sequence=final['sequence'],wall=time.perf_counter()-wall)
   self.maxima[category]=max(self.maxima[category],upper)
  if online and upper>2.:raise BudgetStop('ONLINE_ROOT_REQUEST_EXCEEDS_2_CPU')
  if error:raise error
  return value
 def checkpoint_session(self,marker,runner,producer,next_grid,offset):
  marker=Path(marker);record=json.loads(marker.read_bytes())
  for name in (record['model'],record['private'],marker.name):sync_existing(marker.parent/name)
  for name in ('COST_RECORDS.jsonl','DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):
   path=self.out/name
   if path.exists():sync_existing(path)
  root=self.root.read()
  value=dict(schema='pilot_recovery_durable_session_v1',root_id=root['root_id'],worker_PID=os.getpid(),publisher_PID=root.get('publisher_PID'),launch=json.loads((self.out/'LAUNCH_COST.json').read_text()),UTC_epoch=time.time(),root_sample=root,CPU_role='root sample as of measured wall_stamp; later work UNKNOWN until next record/final PID audit',activity_wall=time.perf_counter()-self.session_start,registrations=len(runner.attempts),logical_SGD=runner.backend.local_optimizer_steps,physical_unknown_offset_upper=offset,physical_upper=runner.backend.local_optimizer_steps+offset,last_complete_marker=str(marker),next_grid=next_grid,producer_next_clock=producer.next_clock,producer_next_client=producer.next_client,model_version=runner.model_version)
  durable_json(self.out/'SESSION_DURABLE.json',value,previous=True)
  durable_json(self.root.path.with_name('CHECKPOINT_ROOT.json'),root,previous=True)
  durable_json(self.out/('SESSION_'+marker.stem+'.json'),value)
