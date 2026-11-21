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
