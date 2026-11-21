"""Archive only manifest-listed prior source; no old run or result modification."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';old=OUT/'old_implementation'
closure=json.loads((old/'source_closure.json').read_text());checks={}
for rel,h in closure.items():
 name=Path(rel).name
 source=old/name if rel in {'raven_mcs_observed_feedback/authorization.py','raven_mcs_observed_feedback/backend.py','raven_mcs_observed_feedback/lifecycle.py'} else ROOT/'src'/rel
 data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==h
 target=old/'src'/rel;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb') as f:f.write(data)
 checks[rel]=h
(old/'ARCHIVE_CHECK.json').write_text(json.dumps(dict(status='PASS',files=len(checks),source_closure=checks,no_old_execution=True),indent=2))
scripts=('run_observed_feedback_autonomous_pilot.py','observed_feedback_pilot_common.py','observed_feedback_pilot_account.py','observed_feedback_pilot_budget.py','observed_feedback_root_publisher.py')
(OUT/'IMPLEMENTATION_SCRIPT_FREEZE.json').write_text(json.dumps({n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in scripts},indent=2))
print(json.dumps(dict(status='PASS',archived_files=len(checks))))
