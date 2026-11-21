"""Human-authorized autonomous fixed/no-Q-stop arms;full shared lifecycle/P2."""
import time
from .authorization import AutonomousPilotAuthorization
from .controller import Controller,Decision
from .schema import InputError

class PilotController(Controller):
    def __init__(self,strategy,**kwargs):super().__init__(**kwargs);self.strategy=strategy
    def decide(self,runner,**kwargs):
        auth=runner.collection_authorization
        if not isinstance(auth,AutonomousPilotAuthorization) or not runner.calibration_only or runner.isolated_test:raise InputError('real autonomous diagnostic authorization required')
        auth.require(seed=runner.seed,source=runner.config.source)
        if self.strategy!=auth.strategy or runner.probability_applicability['strategy']!=self.strategy:raise InputError('autonomous strategy identity mismatch')
        if self.strategy=='OF-v1':return super().decide(runner,**kwargs)
        if kwargs:raise InputError('no implicit ablation/test override for autonomous arm')
        start=time.process_time();s=runner.snapshot();elapsed=s.now-s.window_open
        if self.root_budget is None or self.save_reserve is None or self.operation_root_ceiling!=2.:raise InputError('full root binding required')
        if not self.root_budget.can_plan(self.save_reserve,operation_root_ceiling=2.):raise InputError('ROOT_ADMISSION_DENIED_SAVE_THEN_STOP')
        if abs(s.now-round(s.now/.1)*.1)>1e-9:raise InputError('decision outside original grid')
        solves=runner.cache.solves;hits=runner.cache.hits;preview=None;B=None;components=()
        if s.now==100.:action,reason='CLOSE','TERMINAL'
        elif s.now<=20.:action,reason=('CLOSE','WARMUP') if elapsed>=1-1e-9 else ('WAIT','WARMUP')
        elif elapsed>=4-1e-9:action,reason='CLOSE','DEADLINE'
        elif len(s.pool)<3:action,reason='WAIT','MIN_CLIENTS'
        elif self.strategy.startswith('fixed_time_'):
            period=.5 if self.strategy=='fixed_time_0.5' else 2.
            action='CLOSE' if elapsed>=period-1e-9 else 'WAIT';reason='FIXED_TIME_TRIGGER' if action=='CLOSE' else 'FIXED_TIME_WAIT'
        elif self.strategy=='OF-no-Q-stop':action,reason=None,None
        else:raise InputError('unsupported autonomous arm')
        if action is None or action=='CLOSE':
            if s.pool:preview=runner.preview_release()
        if action is None:
            cminus=s.last_release.ell+.02*s.last_release.age if s.last_release else 1.
            c=preview.ell+.02*preview.age;norm=1+sum(s.debt)
            b=sum(q/norm*(o-m) for q,o,m in zip(s.debt,preview.omega,s.mu))
            quality=cminus-c;debt=0.*b;patience=.20*min(1.,max(0.,elapsed/4.));B=quality+debt+patience
            action='CLOSE' if B>=.02+1e-7 else 'WAIT';reason='FEEDBACK_TRIGGER' if action=='CLOSE' else 'FEEDBACK_WAIT'
            components=(('quality',quality),('debt',debt),('patience',patience),('b',b),('c_minus',cminus),('c',c))
        cpu=time.process_time()-start
        if cpu>2.:raise InputError('CONTROLLER_LOCAL_CPU_TIMEOUT;root also required')
        return Decision(action,reason,preview,B,components,runner.cache.solves-solves,runner.cache.hits-hits,cpu)
