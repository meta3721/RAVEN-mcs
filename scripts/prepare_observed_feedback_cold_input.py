"""Freeze one deterministic fixture without importing a numerical library."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_observed_feedback_readiness_20261014'
old=ROOT/'results_observed_feedback_implementation_20261013'
closure=json.loads((old/'FINAL_SOURCE_CLOSURE.json').read_text())
changed=[p for p,h in closure.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
evidence=json.loads((old/'final_fields_validation/FOUR_PATH_RESULT.json').read_text())
assert evidence['status']=='PASS'
source=ROOT/'results_calibration_first_20261013/trajectory/FAILED_tick0201.json'
mu=json.loads(source.read_text())['state']['mu'] # ONLY published frozen target, never resume or future queue.
assert len(mu)==172 and abs(sum(mu)-1)<1e-9 and all(x>=0 for x in mu)
input=dict(role='isolated_deterministic_math_fixture_NOT_Traffic_state',K=43,mu=mu,
    target_source=str(source),target_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    source_fields_used=['state.mu'],now=20.5,window_open=20.,model_version=1,prior_group=171,
    prior_omega=[.7*m+(.3 if i==171 else 0) for i,m in enumerate(mu)],
    clients=[dict(client=f'fixture_client_{j:02d}',key=f'fixture_delivered_{j:02d}',group=(4*j)%172,
        registered_at=20.+(j%4)*.1,completed_at=20.4,downloaded_version=j%2,
        device_class='math_device',network_class='math_network',q=.5,variance=1.+j/43.,
        target_opportunity=[.7*m+(.3 if i==(4*j)%172 else 0) for i,m in enumerate(mu)],
        lagged_opportunity=[1/172]*172,p_obs=[.5]*172,observation=[1]*172,group_ids=list(range(172))) for j in range(43)],
    prior_state_basis='one conditional prior warmup singleton release with identical columns prior_omega; exact alpha=1/3; Q=max(0,.01*(mu-prior_omega)); no historical P2 executed',
    constraints=dict(sum_alpha=1,alpha_min=0,alpha_max=.5,sum_alpha_squared_max=1/3),
    settings=dict(lambda_group=1.,lambda_beta=1.,lambda_variance=.1,lambda_staleness=.1,e_min=3.,alpha_max=.5),
    request_boundary='FIRST root baseline 0: worker startup/import/init + only complete K43 judgement + numeric serialization + monitor. Exit in whole root ledger. No numerical prewarming or previous cache.',
    save_reserve_CPU=5.96875,root_operation_admission_ceiling=30.,SGD=0)
with (OUT/'FROZEN_INPUT.json').open('x') as f:json.dump(input,f,indent=2,allow_nan=False)
with (OUT/'PRECHECK.json').open('x') as f:json.dump(dict(previous_closure_files=len(closure),changed=changed,
    old_final_four_paths='PASS',input_hash=hashlib.sha256((OUT/'FROZEN_INPUT.json').read_bytes()).hexdigest()),f,indent=2)
print('INPUT_FROZEN; OLD_SOURCE_UNCHANGED; NO_NUMERICAL_IMPORT')
