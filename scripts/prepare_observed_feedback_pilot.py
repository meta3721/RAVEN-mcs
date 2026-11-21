"""Identity-metadata-only audit; publish preserved implementation and pilot scope."""
import json,hashlib,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
index=ROOT/'results_observed_feedback_acquisition_45011_20261014/AUDIT_INPUT_INVENTORY.txt'
preliminary=OUT/'SEED_REVIEW.json'
existing=json.loads(preliminary.read_text()) if preliminary.exists() else None
paths=[] if existing else index.read_text(encoding='utf-8').splitlines();checked=existing['identity_metadata_checked'] if existing else [];matches=[]
if existing:
 for hit in existing['matches']:
  assert not hit.get('named_asset')
  text=Path(hit['path']).read_text(encoding='utf-8-sig')
  positions=list(re.finditer(r'(?<!\d)45001(?!\d)',text))
  hashes=[m.span() for m in re.finditer(r'(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])',text)]
  assert all(any(start<=m.start() and m.end()<=end for start,end in hashes) for m in positions),'REAL_SEED_METADATA_CONFLICT'
 (OUT/'SEED_PRELIMINARY_HASH_FALSE_POSITIVES.json').write_text(json.dumps(existing,indent=2))
names=re.compile(r'(seed|identity|registry|index|freeze|frozen|selection|manifest|execution_result|usage|run_config|budget)',re.I)
for name in paths:
 p=Path(name)
 if p.suffix.lower() not in {'.json','.yaml','.yml','.toml'} or not names.search(p.name) or not p.exists() or p.stat().st_size>2000000:continue
 if 'results_observed_feedback_autonomous_pilot_45001' in str(p):continue
 checked.append(str(p));content=p.read_text(encoding='utf-8-sig',errors='replace')
 if re.search(r'(?<!\d)45001(?!\d)',content):matches.append(dict(path=str(p),contexts=[content[max(0,m.start()-80):m.end()+100] for m in re.finditer(r'(?<!\d)45001(?!\d)',content)]))
for parent in (ROOT,Path('C:/Users/szr/Desktop/record/1')):
 for p in parent.iterdir():
  if '45001' in p.name and p!=OUT:matches.append(dict(path=str(p),named_asset=True))
review=dict(seed=45001,status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not matches else 'REVIEW_REQUIRED',identity_metadata_checked=checked,matches=matches,hash_false_positives_resolved=len(existing['matches']) if existing else 0,
 reused_inventory=str(index),scope='existing identity index and current top-level run names; no model, prediction, data or giant log inspection',proposal_mentions='45001-45003 reserved only in prior Markdown, not executed')
(OUT/'SEED_REVIEW.json').write_text(json.dumps(review,indent=2));assert not matches,'SEED_CONFLICT_REVIEW_REQUIRED'
old=json.loads((ROOT/'results_observed_feedback_rolling_45011_20261014_s2/trajectory/tick1000.complete.json').read_text())
packet_path=ROOT/'results_observed_feedback_rolling_45011_20261014_s2/trajectory'
# Preserve the exact files to be edited and the old closure; historical pair/metrics remain immutable.
backup=OUT/'old_implementation';backup.mkdir(exist_ok=False)
for name in ('authorization.py','backend.py','lifecycle.py'):
 p=ROOT/'src/raven_mcs_observed_feedback'/name;(backup/name).write_bytes(p.read_bytes())
prior=json.loads((ROOT/'results_observed_feedback_continuation_45011_20261014/ACQUISITION_FROZEN_PLAN.json').read_text())
(backup/'source_closure.json').write_text(json.dumps(prior['source_closure'],indent=2))
history={str(ROOT/'results_observed_feedback_rolling_45011_20261014_s2'/name):hashlib.sha256((ROOT/'results_observed_feedback_rolling_45011_20261014_s2'/name).read_bytes()).hexdigest() for name in ('BUDGET.json','EXECUTION_RESULT.json','VALIDATION_AND_SUMMARY.json','FINAL_DELIVERY_CHECK.json')}
for p in (ROOT/'ccf-review-report/observed_feedback_rolling_45011_20261014_s2').iterdir():history[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'PROTECTED_HISTORY.json').write_text(json.dumps(history,indent=2))
scope=dict(batch='user20261014_autonomous_pilot_45001',seed=45001,strategies=['OF-v1','fixed_time_0.5','fixed_time_2','OF-no-Q-stop'],order=['OF-v1','fixed_time_0.5','fixed_time_2','OF-no-Q-stop'],
 source='user_20261014_OF_v1_autonomous_pilot',stage='P1_autonomous_P3_pre_pilot',T=100,CPU_limit=3000,wall_limit=14400,arm_wall_limit=7200,max_steps_each=5000,max_steps_all=20000,GPU=0,
 constants=dict(theta=.02,kappa=.10,nu=.20),main_baseline='fixed_time_0.5',screen=dict(wait_route=dict(rW_min=.05,dG_max=.01),match_route=dict(rG_min=.02,W_ratio_max=1.05)),
 q_role='diagnostic_prior_not_calibrated',q_value=.5,calibration_only=True,SGD='existing CommonNDMF/ClientTrainer local1 LR.01 server.01',no_search=True,no_automatic_expansion=True)
(OUT/'PILOT_SCOPE.json').write_text(json.dumps(scope,indent=2));print(json.dumps(dict(status=review['status'],identity_files=len(checked),scope=scope)))
