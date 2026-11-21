"""Full P2 numeric reuse separated from immutable, latest-state binding."""
from dataclasses import asdict,dataclass
import json
from .schema import InputError
from raven_mcs.utils.hashing import sha256_json

def dependency_payload(snapshot):
    return dict(method=snapshot.config.method_version,config=snapshot.config.to_dict(),settings=asdict(snapshot.settings),
        mu=snapshot.mu,debt=snapshot.debt,variance=snapshot.variance,version=snapshot.model_version,
        pool=[asdict(m) for m in snapshot.pool])
def p2_dependency_hash(snapshot):return sha256_json(dependency_payload(snapshot))

@dataclass(frozen=True)
class P2NumericResult:
    dependency_hash:str
    keys:tuple
    alpha:tuple
    beta:tuple
    masses:tuple
    M:tuple
    omega:tuple
    ell:float
    age:float
    solver_json:str
    reachability:None=None
    @property
    def solver(self):return json.loads(self.solver_json)
    def to_dict(self):
        obj=asdict(self);obj.pop('solver_json');obj['solver']=self.solver;return obj

@dataclass(frozen=True)
class BoundReleasePreview:
    fingerprint:str
    numeric:P2NumericResult
    def __getattr__(self,name):return getattr(self.numeric,name)
    def to_dict(self):return dict(fingerprint=self.fingerprint,**self.numeric.to_dict())

def compute_numeric(snapshot):
    # Same full shared aggregator and correction functions, without importing
    # historical control schemas / coverage-diagnostic package on an empty path.
    import numpy as np
    from raven_mcs.correction.second_stage import beta_hat,d_weight,two_stage_mass
    settings=snapshot.settings;pool=sorted(snapshot.pool,key=lambda m:m.registration.client)
    q=np.asarray([m.q.require(isolated_test=snapshot.isolated_test) for m in pool])
    masses=np.asarray([m.summary.total for m in pool]);M=np.asarray([m.summary.composition for m in pool]).T
    beta=beta_hat(two_stage_mass(masses,d_weight(q,d_max=settings.d_max,q_min=settings.q_min)))
    ages=np.asarray([snapshot.model_version-m.registration.downloaded_version for m in pool])/5
    variance_map=dict(snapshot.variance)
    variance=np.asarray([variance_map.get(m.registration.client,1.)/max(m.summary.effective_n,1.)+settings.v_floor for m in pool])
    k=len(pool)
    if min(settings.e_min,k)==k:
        # Full feasible set is a singleton: Cauchy-Schwarz gives sum(a^2)>=1/K
        # with equality iff every a=1/K. Original cap permits that point.
        # This solves the SAME full objective exactly, not a reduced objective.
        alpha=np.ones(k)/k
        solver=dict(status='full_P2_exact_singleton',objective=None,exact_feasible_set=True,
            original_cap=min(1.,max(settings.alpha_max,1/k)),original_ESS=min(settings.e_min,k))
    else:
        from raven_mcs.aggregation.base import WindowAggregateInput
        from raven_mcs.aggregation.methods import RavenAggregator
        payload=WindowAggregateInput(client_ids=[m.registration.client for m in pool],raw_counts=np.asarray([m.summary.observed_count for m in pool]),
            total_masses=masses,compositions=M,beta_hat=beta,staleness=ages,variance_diag=variance,debt=np.asarray(snapshot.debt),mu=np.asarray(snapshot.mu))
        aggregator=RavenAggregator(lambda_group=settings.lambda_group,lambda_beta=settings.lambda_beta,lambda_variance=settings.lambda_variance,
            lambda_staleness=settings.lambda_staleness,alpha_max=settings.alpha_max,e_min=settings.e_min,
            max_server_learning_rate=settings.max_server_learning_rate,instant_calibration=True)
        alpha=aggregator.compute_server_weights(payload);solver=aggregator.solve_results[-1]
    violation=residual(alpha,settings)
    if violation>1e-7:raise InputError('normalized actual P2 weights violate feasibility')
    omega=M@alpha
    solver['normalized_weight_residual']=violation;solver['objective_solver_candidate']=solver['objective']
    solver['objective_actual_weights']=float(-np.asarray(snapshot.debt)@omega+.5*settings.lambda_group*np.square(omega-np.asarray(snapshot.mu)).sum()
        +.5*settings.lambda_beta*np.square(alpha-beta).sum()+.5*settings.lambda_variance*(variance*np.square(alpha)).sum()+settings.lambda_staleness*(ages@alpha))
    if solver['objective'] is None:solver['objective']=solver['objective_actual_weights'];solver['objective_solver_candidate']=solver['objective_actual_weights']
    return P2NumericResult(p2_dependency_hash(snapshot),tuple(m.key for m in pool),tuple(alpha),tuple(beta),tuple(masses),
        tuple(tuple(row) for row in M),tuple(omega),float(.5*np.abs(omega-np.asarray(snapshot.mu)).sum()),float(alpha@ages),
        json.dumps(solver,sort_keys=True,allow_nan=False))

def residual(alpha,settings):
    import numpy as np
    a=np.asarray(alpha,dtype=float);k=len(a)
    if not k:return 0.
    if not np.all(np.isfinite(a)):return float('inf')
    return max(0.,abs(float(a.sum())-1),-float(a.min()),float(a.max())-min(1.,max(settings.alpha_max,1/k)),
        float(a@a)-1/min(settings.e_min,k))

def bind_numeric(snapshot,numeric):
    if numeric.dependency_hash!=p2_dependency_hash(snapshot):raise InputError('P2_DEPENDENCY_CHANGED')
    if numeric.keys!=tuple(m.key for m in snapshot.pool):raise InputError('numeric pool key mismatch')
    return BoundReleasePreview(snapshot.fingerprint,numeric)

class P2Cache:
    def __init__(self):self.values={};self.solves=0;self.hits=0
    def get(self,snapshot,*,use_cache=True):
        key=p2_dependency_hash(snapshot)
        if use_cache and key in self.values:self.hits+=1;numeric=self.values[key]
        else:
            numeric=compute_numeric(snapshot);self.solves+=int(bool(snapshot.pool))
            if use_cache:self.values[key]=numeric
        return bind_numeric(snapshot,numeric)
