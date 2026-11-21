"""External Windows publication facility. Timestamp, CPU and admission semantics unchanged."""
import json,os,time,uuid
from raven_mcs_execution.budget import RootBudgetPublisher
class SharingTolerantPublisher(RootBudgetPublisher):
    def publish(self,tree_cpu,driver_cpu,*,force=False,finished=False):
        now=time.perf_counter()
        if not force and now-self.last_wall<.05:return
        self.sequence+=1;cost=tree_cpu+driver_cpu
        payload=dict(schema='root_disjoint_CPU_v1',root_id=self.root_id,sequence=self.sequence,wall_stamp=now,
            tree_CPU=tree_cpu,driver_CPU=driver_cpu,command_used=cost,batch_used=self.config['prior_batch']+cost,
            phase_used=self.config['prior_phase']+cost,remaining=min(self.command_limit-cost,self.config['batch_limit']-self.config['prior_batch']-cost,self.config['phase_limit']-self.config['prior_phase']-cost),
            finished=finished,maximum_CPU_rate=2.,feedback_interval=.05,cost_rule='tree + driver only; PID / inner job are included, never added')
        temp=self.path.with_name(self.path.name+'.'+str(self.sequence)+'.'+uuid.uuid4().hex+'.pending')
        with temp.open('x',encoding='utf-8') as f:json.dump(payload,f)
        for attempt in range(90):
            try:os.replace(temp,self.path);self.last_wall=now;return
            except PermissionError:
                if attempt==89:raise
                time.sleep(.01)
        # Never refresh the measured timestamp on retries; existing stale-sample guards remain active.
