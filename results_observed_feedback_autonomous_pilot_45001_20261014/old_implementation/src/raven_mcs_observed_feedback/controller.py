"""Frozen observed feedback; returns a current preview, never commits a model."""
from dataclasses import dataclass,asdict
import time
from .schema import InputError,DependencyPending

@dataclass(frozen=True)
class Decision:
    action:str
    reason:str
    preview:object=None
    B:float|None=None
    components:tuple=()
    p2_solves:int=0
    cache_hits:int=0
    process_CPU:float=0.
    def to_dict(self):
        obj=asdict(self);obj['preview']=self.preview.to_dict() if self.preview else None;return obj

class Controller:
    def __init__(self,*,root_budget=None,save_reserve=None,operation_root_ceiling=None):
        self.root_budget=root_budget;self.save_reserve=save_reserve;self.operation_root_ceiling=operation_root_ceiling
    def decide(self,runner,*,diagnostic_no_debt=False,use_cache=True):
        start=time.process_time();s=runner.snapshot();elapsed=s.now-s.window_open
        if self.root_budget is not None:
            if self.save_reserve is None or self.operation_root_ceiling is None:raise InputError('explicit save reserve and full root operation ceiling required')
            if not self.root_budget.can_plan(self.save_reserve,operation_root_ceiling=self.operation_root_ceiling):raise InputError('ROOT_ADMISSION_DENIED_SAVE_THEN_STOP')
        elif not s.isolated_test:raise DependencyPending('ROOT_BUDGET_BINDING_PENDING')
        if abs(s.now-round(s.now/.1)*.1)>1e-9:raise InputError('decision outside original grid')
        if diagnostic_no_debt and not s.isolated_test:raise InputError('ablation shadow only authorized for isolated test')
        solves=runner.cache.solves;hits=runner.cache.hits
        if s.now==s.experiment_end:action,reason='CLOSE','TERMINAL'
        elif s.now<=20:
            action,reason=('CLOSE','WARMUP') if elapsed>=1-1e-9 else ('WAIT','WARMUP')
        elif elapsed>=4-1e-9:action,reason='CLOSE','DEADLINE'
        elif len(s.pool)<3:action,reason='WAIT','MIN_CLIENTS'
        else:action,reason=None,None
        preview=None;B=None;components=()
        if action is None or action=='CLOSE':
            if s.pool:preview=runner.preview_release(use_cache=use_cache)
        if action is None:
            cminus=s.last_release.ell+.02*s.last_release.age if s.last_release else 1.
            c=preview.ell+.02*preview.age
            norm=1+sum(s.debt);b=sum(q/norm*(o-m) for q,o,m in zip(s.debt,preview.omega,s.mu))
            kappa=0. if diagnostic_no_debt else .10
            quality=cminus-c;debt=kappa*b;patience=.20*min(1.,max(0.,elapsed/4.))
            B=quality+debt+patience
            action='CLOSE' if B>=.02+1e-7 else 'WAIT';reason='FEEDBACK_TRIGGER' if action=='CLOSE' else 'FEEDBACK_WAIT'
            components=(('quality',quality),('debt',debt),('patience',patience),('b',b),('c_minus',cminus),('c',c))
        cpu=time.process_time()-start
        if cpu>2.:raise InputError('CONTROLLER_LOCAL_CPU_TIMEOUT; root cost also required')
        return Decision(action,reason,preview,B,components,runner.cache.solves-solves,runner.cache.hits-hits,cpu)
