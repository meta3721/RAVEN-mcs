"""Exactly one cold full-P2 request; no acquisition, fitting or SGD."""
import sys,time,json,traceback,hashlib
from pathlib import Path
START_WALL=time.perf_counter()
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_readiness_20261014'
from raven_mcs_observed_feedback.budget_client import RootClient
from raven_mcs_observed_feedback.schema import ControlConfig,P2Settings,ReleaseSummary,Registration,Delivered
from raven_mcs_observed_feedback.design import DesignConfiguration
from raven_mcs_observed_feedback.probability import IsolatedQ
from raven_mcs_observed_feedback.array_backend import ArrayBackend
from raven_mcs_observed_feedback.lifecycle import DynamicWindowRunner
from raven_mcs_observed_feedback.controller import Controller
from raven_mcs_observed_feedback.stage1 import freeze_stage1
from raven_mcs_observed_feedback import METHOD_VERSION
raw=json.loads((OUT/'FROZEN_INPUT.json').read_text())
with (OUT/'COLD_REQUEST_STARTED.json').open('x') as f:json.dump(dict(input_hash=hashlib.sha256((OUT/'FROZEN_INPUT.json').read_bytes()).hexdigest(),
    numerical_libraries_imported=[k for k in ('cvxpy','scipy','clarabel') if k in sys.modules],requests_allowed=1),f)
assert not any(k in sys.modules for k in ('cvxpy','scipy','clarabel'))
config=ControlConfig('authorized_math_fixture',DesignConfiguration(True,'explicit_preconfigured_fixture'))
r=DynamicWindowRunner(config=config,settings=P2Settings(),mu=raw['mu'],q_model=IsolatedQ(),backend=ArrayBackend([0.]),seed=0,
    open_time=20.,isolated_test=True,data_identity='MATH_FIXTURE',target_identity='published_frozen_mu_172',
    probability_applicability=dict(consumption_policy=METHOD_VERSION,T=100,service={'kind':'public_math_fixture'}),
    clock_namespace=dict(run_id='cold_fixture_20261014',origin_utc='2026-10-14T00:00:00Z',unit='controlled_service_unit'))
r.model_version=1;r.now=20.5
r.debt=tuple(max(0.,.01*(m-o)) for m,o in zip(raw['mu'],raw['prior_omega']))
r.last_release=ReleaseSummary(20.,.5*sum(abs(m-o) for m,o in zip(raw['mu'],raw['prior_omega'])),0.,1.,tuple(raw['prior_omega']))
for c in raw['clients']:
    reg=Registration(c['key'],c['client'],c['registered_at'],c['downloaded_version'],c['device_class'],c['network_class'])
    summary=freeze_stage1(config=config,target_opportunity=c['target_opportunity'],lagged_opportunity=c['lagged_opportunity'],
        p_obs=c['p_obs'],observation=c['observation'],group_ids=c['group_ids'],num_groups=172,now=c['registered_at'],
        estimator_as_of=20.,estimator_version='public_math_fixture_only',provenance='frozen_explicit_input_no_future')
    q=IsolatedQ(c['q']).predict_at_registration(r.registration_features(reg))
    r.pool[c['client']]=Delivered(reg,summary,q,c['completed_at']);r.variance[c['client']]=c['variance']
# Conditional lawful public snapshot only: no actual producer or commit. No fake backend update/trajectory.
snapshot=r.snapshot();assert len(snapshot.pool)==43 and not r.cache.values
controller=Controller(root_budget=RootClient(OUT/'ROOT_BUDGET_LIVE.json'),save_reserve=5.96875,operation_root_ceiling=30.)
solver_start=time.process_time();decision=None;error=None
try:decision=controller.decide(r,use_cache=True)
except Exception as e:error=repr(e);traceback.print_exc()
numeric=decision.preview.numeric if decision else next(iter(r.cache.values.values()),None)
result=dict(status='PENDING_ROOT_COST',error=error,decision=decision.to_dict() if decision else None,
    numeric=numeric.to_dict() if numeric else None,cache_solves=r.cache.solves,cache_hits=r.cache.hits,
    judgement_local_CPU=time.process_time()-solver_start,worker_CPU_to_serialize=time.process_time(),SGD=0,
    role=raw['role'],prior_state_basis=raw['prior_state_basis'])
if numeric:
    import numpy as np
    a=np.asarray(numeric.alpha);M=np.asarray(numeric.M);mu=np.asarray(r.mu);Q=np.asarray(r.debt);beta=np.asarray(numeric.beta)
    ages=np.asarray([1-m.registration.downloaded_version for m in snapshot.pool])/5
    vv=np.asarray([r.variance[m.registration.client]/max(m.summary.effective_n,1.)+.0001 for m in snapshot.pool])
    terms=dict(debt=-float(Q@np.asarray(numeric.omega)),group=.5*float(np.square(np.asarray(numeric.omega)-mu).sum()),
        reference=.5*float(np.square(a-beta).sum()),variance=.05*float((vv*np.square(a)).sum()),staleness=.1*float(ages@a))
    result.update(objective_terms=terms,variance_diagonal=vv.tolist(),staleness=ages.tolist(),debt=list(r.debt),
        distinct_columns=bool(np.any(M[:,0]!=M[:,1])),uniform_squared_norm=1/43,
        feasible_free_direction='alpha=uniform +/- .001*(e0-e1); interior cap/ESS/nonnegative hold',
        numerical_finite=bool(np.all(np.isfinite(a)) and np.all(np.isfinite(M)) and all(np.isfinite(x) for x in terms.values())),
        numeric_residual=numeric.solver['normalized_weight_residual'])
# Serialization is inside the request; sampling waits for a published root AFTER the completed serialization.
(OUT/'COLD_NUMERIC_RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False))
done=time.perf_counter();reader=RootClient(OUT/'ROOT_BUDGET_LIVE.json')
while True:
    sample=reader.read()
    if sample['wall_stamp']>done+.01:break
    time.sleep(.01)
bootstrap=json.loads((OUT/'LAUNCH_COST.json').read_text())['launcher_bootstrap_CPU']
upper=sample['command_used']+.02+bootstrap
upper=max(upper,time.process_time()+sample['driver_CPU']+.02+bootstrap)
numeric_pass=bool(numeric and result['numerical_finite'] and result['numeric_residual']<=1e-7)
status='PASS' if numeric_pass and not error and upper<=2 else 'FAIL'
(OUT/'COLD_REQUEST_COST.json').write_text(json.dumps(dict(status=status,numeric_pass=numeric_pass,
    conservative_root_upper_CPU=upper,root_sample=sample,launcher_bootstrap_CPU=bootstrap,
    worker_process_CPU=time.process_time(),request_wall=time.perf_counter()-START_WALL,
    error=error,decision_accepted=not error,first_request_includes_startup=True,request_count=1),indent=2))
print(json.dumps(dict(status=status,root_upper=upper,numeric_pass=numeric_pass,error=error)))
