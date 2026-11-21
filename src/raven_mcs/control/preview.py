"""Read-only complete RAVEN P2 and independent current L1 reachability."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
import cvxpy as cp

from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound
from raven_mcs.correction.second_stage import beta_hat, d_weight, two_stage_mass
from raven_mcs.control.schema import DecisionSnapshot, InputError


@dataclass(frozen=True)
class Reachability:
    d: float
    alpha: tuple[float,...]
    status: str
    residual: float
    lower_bound: float
    upper_bound: float
    bound_source: str
    secondary_value: float | None = None


@dataclass(frozen=True)
class ReleasePreview:
    fingerprint: str
    keys: tuple[str,...]
    alpha: tuple[float,...]
    beta: tuple[float,...]
    masses: tuple[float,...]
    M: tuple[tuple[float,...],...]
    omega: tuple[float,...]
    ell: float
    age: float
    solver: dict
    reachability: Reachability | None

    def to_dict(self): return asdict(self)


def residual(alpha, settings):
    a=np.asarray(alpha,dtype=float); k=len(a)
    if not k: return 0.
    if not np.all(np.isfinite(a)): return float('inf')
    return max(0.,abs(float(a.sum())-1),-float(a.min()),
               float(a.max())-alpha_bar(alpha_max=settings.alpha_max,n_active=k),
               float(a@a)-1/ess_ball_bound(e_min=settings.e_min,n_active=k))


def solve_current_l1(M, mu, settings):
    M=np.asarray(M,dtype=float); mu=np.asarray(mu,dtype=float); k=M.shape[1]
    if k == 0:
        return Reachability(1.,(), 'empty_no_release',0.,1.,1.,'empty convention')
    cap=alpha_bar(alpha_max=settings.alpha_max,n_active=k)
    ess=ess_ball_bound(e_min=settings.e_min,n_active=k)
    if ess == k:
        a=np.ones(k)/k
        d=float(.5*np.abs(M@a-mu).sum())
        return Reachability(d,tuple(a),'singleton_feasible_set',residual(a,settings),d,d,'singleton analytic')
    a=cp.Variable(k); t=cp.Variable(len(mu))
    constraints=[cp.sum(a)==1,a>=0,a<=cap,cp.sum_squares(a)<=1/ess,
                 M@a-mu<=t, -(M@a-mu)<=t]
    p=cp.Problem(cp.Minimize(.5*cp.sum(t)),constraints)
    p.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_gap_rel=1e-9,tol_feas=1e-9,max_iter=300)
    if p.status != 'optimal' or a.value is None or residual(a.value,settings)>1e-7:
        raise InputError(f"current L1 reference failed: {p.status}")
    candidate=np.asarray(a.value).copy()
    upper=float(.5*np.abs(M@candidate-mu).sum())
    # A feasible dual bound: for any ||y||_infty <= .5,
    # y'(M a-mu) >= min_j (M' y)_j-y'mu. The simplex relaxes cap/ESS,
    # giving a conservative but valid lower bound without claiming repairs optimal.
    y=np.asarray(constraints[-2].dual_value)-np.asarray(constraints[-1].dual_value)
    y=np.clip(y,-.5,.5)
    lower=max(0.,float(np.min(M.T@y)-y@mu))
    # Independent conic solver verifies the optimum numerically; not a rigorous
    # bound on true future reachability. Save both evidence types separately.
    p.solve(solver='SCS',eps=1e-8,max_iters=100000)
    if p.status not in {'optimal','optimal_inaccurate'} or a.value is None or residual(a.value,settings)>1e-7:
        raise InputError("independent current L1 reference failed")
    secondary=float(.5*np.abs(M@a.value-mu).sum())
    if abs(secondary-upper)>1e-6:
        raise InputError("current L1 independent reference disagrees")
    if lower > upper+1e-7:
        raise InputError("invalid L1 bound")
    return Reachability(upper,tuple(candidate),'independently_checked',residual(candidate,settings),
                        lower,upper,'simplex-relaxed dual + independent SCS',secondary)


def preview_release(snapshot: DecisionSnapshot, *, with_reachability=True):
    settings=snapshot.settings
    pool=sorted(snapshot.pool,key=lambda m:m.registration.client)
    if not pool:
        return ReleasePreview(snapshot.fingerprint,(),(),(),(),tuple(() for _ in snapshot.mu),
            tuple(0. for _ in snapshot.mu),1.,0.,{'status':'empty_no_release','residuals':{'constraint':0.}},
            solve_current_l1(np.empty((len(snapshot.mu),0)),snapshot.mu,settings) if with_reachability else None)
    q=np.asarray([m.q.require(isolated_test=snapshot.isolated_test,calibration_only=snapshot.calibration_only) for m in pool])
    masses=np.asarray([m.summary.total for m in pool])
    M=np.asarray([m.summary.composition for m in pool]).T
    beta=beta_hat(two_stage_mass(masses,d_weight(q,d_max=settings.d_max,q_min=settings.q_min)))
    ages=np.asarray([snapshot.model_version-m.registration.downloaded_version for m in pool])/snapshot.config.age_max
    variance_map=dict(snapshot.variance)
    variance=np.asarray([variance_map.get(m.registration.client,1.)/max(m.summary.effective_n,1.)
                         +settings.v_floor for m in pool])
    payload=WindowAggregateInput(client_ids=[m.registration.client for m in pool],
        raw_counts=np.asarray([m.summary.observed_count for m in pool]),total_masses=masses,
        compositions=M,beta_hat=beta,staleness=ages,variance_diag=variance,
        debt=np.asarray(snapshot.debt),mu=np.asarray(snapshot.mu))
    # A fresh instance has no side effects on the live aggregator's audit state.
    aggregator=RavenAggregator(lambda_group=settings.lambda_group,lambda_beta=settings.lambda_beta,
        lambda_variance=settings.lambda_variance,lambda_staleness=settings.lambda_staleness,
        alpha_max=settings.alpha_max,e_min=settings.e_min,
        max_server_learning_rate=settings.max_server_learning_rate,instant_calibration=True)
    alpha=aggregator.compute_server_weights(payload)
    violation=residual(alpha,settings)
    if violation > 1e-7:
        raise InputError("normalized actual P2 weights violate feasibility")
    solver=aggregator.solve_results[-1]
    solver['normalized_weight_residual']=violation
    omega=M@alpha
    # Solver's objective can precede its feasibility repair. Recompute the
    # objective of the weights actually used, retaining both audit values.
    solver['objective_solver_candidate']=solver['objective']
    solver['objective_actual_weights']=float(-np.asarray(snapshot.debt)@omega
        +.5*settings.lambda_group*np.square(omega-np.asarray(snapshot.mu)).sum()
        +.5*settings.lambda_beta*np.square(alpha-beta).sum()
        +.5*settings.lambda_variance*(variance*np.square(alpha)).sum()
        +settings.lambda_staleness*(ages@alpha))
    return ReleasePreview(snapshot.fingerprint,tuple(m.key for m in pool),tuple(alpha),tuple(beta),
        tuple(masses),tuple(tuple(row) for row in M),tuple(omega),
        float(.5*np.abs(omega-np.asarray(snapshot.mu)).sum()),float(alpha@ages),solver,
        solve_current_l1(M,snapshot.mu,settings) if with_reachability else None)
