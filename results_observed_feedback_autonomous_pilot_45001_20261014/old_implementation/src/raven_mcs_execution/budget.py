"""The root's disjoint CPU ledger is the only admission authority."""
import json,os,time,uuid
from pathlib import Path

class RootBudgetPublisher:
    def __init__(self,config,command_limit):
        self.config=config;self.command_limit=command_limit;self.path=Path(config['path'])
        self.root_id=uuid.uuid4().hex;self.sequence=0;self.last_wall=-float('inf')
    def publish(self,tree_cpu,driver_cpu,*,force=False,finished=False):
        now=time.perf_counter()
        if not force and now-self.last_wall<.05:return
        self.sequence+=1;cost=tree_cpu+driver_cpu
        payload=dict(schema='root_disjoint_CPU_v1',root_id=self.root_id,sequence=self.sequence,wall_stamp=now,
            tree_CPU=tree_cpu,driver_CPU=driver_cpu,command_used=cost,
            batch_used=self.config['prior_batch']+cost,phase_used=self.config['prior_phase']+cost,
            remaining=min(self.command_limit-cost,self.config['batch_limit']-self.config['prior_batch']-cost,
                self.config['phase_limit']-self.config['prior_phase']-cost),
            finished=finished,maximum_CPU_rate=2.,feedback_interval=.05,
            cost_rule='tree + driver only; PID / inner job are included, never added')
        temp=self.path.with_suffix('.pending')
        temp.write_text(json.dumps(payload),encoding='utf-8');os.replace(temp,self.path)
        self.last_wall=now

class RootBudgetReader:
    def __init__(self,path):self.path=Path(path);self.root_id=None
    def read(self):
        v=json.loads(self.path.read_text())
        if v['schema']!='root_disjoint_CPU_v1' or v['finished']:raise RuntimeError('root budget unavailable / finished')
        if self.root_id is None:self.root_id=v['root_id']
        if self.root_id!=v['root_id']:raise RuntimeError('root budget namespace changed')
        age=max(0.,time.perf_counter()-v['wall_stamp'])
        if age>1:raise RuntimeError('root budget stale; no new operation')
        v['effective_remaining']=v['remaining']-v['maximum_CPU_rate']*age-.05
        return v
    def can_plan(self,save_reserve,*,operation_root_ceiling):
        # Caller must include external monitoring in this root-operation bound.
        # The controller's separate 2-CPU limit alone is not a root-cost bound.
        if operation_root_ceiling<=0:raise ValueError('positive full-root operation ceiling required')
        return self.read()['effective_remaining']>=save_reserve+operation_root_ceiling
    def require_save(self,save_reserve):
        if self.read()['effective_remaining']<save_reserve:raise RuntimeError('save headroom exhausted; retain published checkpoint and stop')

def checkpoint_due(tick,last_tick,*,remaining,save_reserve,operation_root_ceiling):
    # Normal loss <=50 grid points; near-budget loss <=10. Every save is billed.
    interval=10 if remaining<=4*save_reserve+operation_root_ceiling else 50
    return tick-last_tick>=interval or remaining<save_reserve+operation_root_ceiling
