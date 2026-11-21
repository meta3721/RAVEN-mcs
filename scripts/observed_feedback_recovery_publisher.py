"""Validated live root samples plus persistent first/periodic/final evidence."""
import time,os
from raven_mcs_execution.budget import RootBudgetPublisher
from observed_feedback_recovery_io import durable_json
class RecoveryPublisher(RootBudgetPublisher):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.durable_wall=-float('inf')
 def publish(self,tree_cpu,driver_cpu,*,force=False,finished=False):
  now=time.perf_counter()
  if not force and now-self.last_wall<.05:return
  self.sequence+=1;cost=tree_cpu+driver_cpu
  payload=dict(schema='root_disjoint_CPU_v1',root_id=self.root_id,sequence=self.sequence,wall_stamp=now,
   tree_CPU=tree_cpu,driver_CPU=driver_cpu,command_used=cost,batch_used=self.config['prior_batch']+cost,
   phase_used=self.config['prior_phase']+cost,remaining=min(self.command_limit-cost,self.config['batch_limit']-self.config['prior_batch']-cost,self.config['phase_limit']-self.config['prior_phase']-cost),
   finished=finished,maximum_CPU_rate=2.,feedback_interval=.05,cost_rule='tree + driver only; PID / inner job included, never added',publisher_PID=os.getpid())
  durable_json(self.path,payload);self.last_wall=now
  if force or finished or now-self.durable_wall>=5.:
   durable_json(self.path.with_name('LAST_VALID_ROOT.json'),payload,previous=True);self.durable_wall=now
