"""Unique human-approved diagnostic collection; never a production credential."""
from dataclasses import dataclass
from . import METHOD_VERSION
from .schema import DependencyPending
SOURCE='user_20261014_OF_v1_first_acquisition'
@dataclass(frozen=True)
class DiagnosticCollectionAuthorization:
    source:str=SOURCE
    seed:int=45011
    method:str=METHOD_VERSION
    role:str='development_cost_and_bootstrap_fit_candidate'
    T:float=100.
    max_steps:int=5000
    CPU_limit:float=3600.
    def require(self,*,seed,source):
        if (self.source,self.seed,self.method,self.role,self.T,self.max_steps,self.CPU_limit)!=(SOURCE,45011,METHOD_VERSION,'development_cost_and_bootstrap_fit_candidate',100.,5000,3600.):
            raise DependencyPending('not the approved OF diagnostic batch')
        if seed!=self.seed or source!=self.source:raise DependencyPending('diagnostic seed/source mismatch')

PILOT_SOURCE='user_20261014_OF_v1_autonomous_pilot'
PILOT_STRATEGIES=('OF-v1','fixed_time_0.5','fixed_time_2','OF-no-Q-stop')
@dataclass(frozen=True)
class AutonomousPilotAuthorization:
    strategy:str
    source:str=PILOT_SOURCE
    seed:int=45001
    method:str=METHOD_VERSION
    role:str='P1_autonomous_P3_pre_pilot'
    T:float=100.
    max_steps:int=5000
    CPU_limit:float=3000.
    batch_steps:int=20000
    def require(self,*,seed,source):
        if self.strategy not in PILOT_STRATEGIES or (self.source,self.seed,self.method,self.role,self.T,self.max_steps,self.CPU_limit,self.batch_steps)!=(PILOT_SOURCE,45001,METHOD_VERSION,'P1_autonomous_P3_pre_pilot',100.,5000,3000.,20000):
            raise DependencyPending('not the approved four-arm autonomous diagnostic pilot')
        if seed!=self.seed or source!=self.source:raise DependencyPending('pilot seed/source mismatch')

def collection_authorization_from_dict(obj):
    if not obj:return None
    cls=PilotRecoveryAuthorization if 'extension' in obj else (AutonomousPilotAuthorization if 'strategy' in obj else DiagnosticCollectionAuthorization)
    return cls(**obj)

@dataclass(frozen=True)
class PilotRecoveryAuthorization(AutonomousPilotAuthorization):
    CPU_limit:float=4800.
    extension:str='user20261015_pilot_interruption_recovery'
    stage_CPU_limit:float=1800.
    stage_wall_limit:float=9000.
    def require(self,*,seed,source):
        if self.strategy not in ('fixed_time_0.5','fixed_time_2','OF-no-Q-stop') or (self.source,self.seed,self.method,self.role,self.T,self.max_steps,self.CPU_limit,self.batch_steps,self.extension,self.stage_CPU_limit,self.stage_wall_limit)!=(PILOT_SOURCE,45001,METHOD_VERSION,'P1_autonomous_P3_pre_pilot',100.,5000,4800.,20000,'user20261015_pilot_interruption_recovery',1800.,9000.):
            raise DependencyPending('not the approved remaining three-arm resource extension')
        if seed!=self.seed or source!=self.source:raise DependencyPending('pilot recovery seed/source mismatch')
