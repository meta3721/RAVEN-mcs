"""Read-only retained-assets verification and MD reporting, no new P2 requests."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from observed_feedback_readiness_budget import OUT,REPORT
old=ROOT/'results_observed_feedback_implementation_20261013'
baseline=json.loads((old/'PROTECTED_BEFORE.json').read_text())
changed=[]
for p,h in baseline.items():
    path=Path(p)
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=h:changed.append(p)
assert not changed,changed
closure=json.loads((old/'FINAL_SOURCE_CLOSURE.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in closure.items())
cost=json.loads((OUT/'COLD_REQUEST_COST.json').read_text());n=json.loads((OUT/'COLD_NUMERIC_RESULT.json').read_text())
assert cost['request_count']==1 and cost['status']=='FAIL' and cost['numeric_pass'] and n['cache_solves']==1 and n['cache_hits']==0
assert len(n['numeric']['alpha'])==43 and len(n['numeric']['omega'])==172
docs=['Q_SCOPE_AND_FEATURE_CONTRACT.md','CALIBRATION_ENTRY_BINDING_PLAN.md','COLD_LARGE_POOL_PREFLIGHT.md','FIRST_ACQUISITION_REQUEST.md','NEXT_STAGE_READINESS.md']
assert all((REPORT/d).exists() for d in docs)
assert all(p.suffix=='.md' for p in REPORT.iterdir())
verify=dict(old_files_checked=len(baseline),changed_old_files=changed,old_source_closure_checked=len(closure),
    old_source_changed=[],reports_only_MD=True,request_count=1,SGD=0,GPU=0,q_fit=0,real_random_trajectories=0,
    collection_entry_implemented=False,status='PREPARATION_INCOMPLETE',cold_status=cost['status'],
    original_solver=n['numeric']['solver']['solver'],residual=n['numeric_residual'],
    prior_four_path_status=json.loads((old/'final_fields_validation/FOUR_PATH_RESULT.json').read_text())['status'])
with (OUT/'FINAL_DELIVERY_CHECK.json').open('x') as f:json.dump(verify,f,indent=2)
# Excludes report text intentionally: immutable raw evidence snapshot for future retention checks.
immutable=['AUTHORIZATION.json','FROZEN_INPUT.json','PRECHECK.json','COLD_REQUEST_STARTED.json',
    'COLD_NUMERIC_RESULT.json','COLD_REQUEST_COST.json','FINAL_DELIVERY_CHECK.json']
files=list((ROOT/'src/raven_mcs_observed_feedback').glob('*.py'))+[OUT/p for p in immutable]
(OUT/'SOURCE_AND_EVIDENCE_CLOSURE.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
print(json.dumps(verify))
