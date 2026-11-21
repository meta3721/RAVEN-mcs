"""Facility recovery preserves failed suffix, charges and physical-step bounds."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];s=ROOT/'results_observed_feedback_rolling_45011_20261014_s1'
rows=[json.loads(x) for x in (s/'COST_RECORDS.jsonl').read_text().splitlines()]
n=sum(x['category']=='training' and x['error'] is None for x in rows)
v=dict(completed_training_records=n,wasted_physical_SGD_lower=n,wasted_physical_SGD_upper=n+1,last_confirmed_grid=1.3,no_new_complete_pair=True,actual_CPU='UNKNOWN; conservative fee retained',cause='Root publication PermissionError; exact failing call not retained',recovery_source='original1.07 complete pair',replay_reason='ordinary facility recovery, not matching timing')
(s/'INTERRUPTION_BOUND.json').write_text(json.dumps(v,indent=2))
t=(ROOT/'scripts/observed_feedback_rolling_budget.py').read_text().replace('rolling_45011_20261014_s1','rolling_45011_20261014_s2')
t=t.replace('START=247.625','START=311.046875').replace("PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'","PARENT=ROOT/'results_observed_feedback_rolling_45011_20261014_s1'")
t=t.replace("v['setup']+=30.","v['setup']+=0.").replace('new_read_edit_delivery_conservative_CPU=30','new_read_edit_delivery_conservative_CPU=0').replace('prior_conservative_CPU=69.59375','prior_conservative_CPU=133.015625').replace('36.09939210000084+sum','66.4996431+sum')
t=t.replace('shared.RootBudgetPublisher=AtomicPublisher','from observed_feedback_root_publisher import SharingTolerantPublisher\n    shared.RootBudgetPublisher=SharingTolerantPublisher')
t=t.replace("live=OUT/('ROOT_BUDGET_'+a.label+'.json');os.environ['OF_ROOT_BUDGET_PATH']=str(live)","import tempfile\n    live_dir=Path(tempfile.mkdtemp(prefix='OF45011_root_'));live=live_dir/'root.json';os.environ['OF_ROOT_BUDGET_PATH']=str(live)\n    (OUT/('ROOT_FEEDBACK_PATH_'+a.label+'.json')).write_text(json.dumps(dict(path=str(live),reason='avoid workspace file-watcher sharing races; unchanged root semantics')))")
t=t.replace('exit=repr(exc),audit=False,actual_CPU=',"exit=repr(exc),exception_traceback=__import__('traceback').format_exc(),audit=False,actual_CPU=")
(ROOT/'scripts/observed_feedback_rolling_budget_s2.py').write_text(t)
t=(ROOT/'scripts/resume_observed_feedback_45011.py').read_text().replace('rolling_45011_20261014_s1','rolling_45011_20261014_s2')
t=t.replace('p.operation=a.operation',"original_operation=a.operation\n        def guarded_operation(category,fn,ceiling=2.,online=False):\n            if category=='training' and r.backend.local_optimizer_steps+"+str(n+1)+">=5000:raise RuntimeError('CUMULATIVE_PHYSICAL_SGD_LIMIT')\n            return original_operation(category,fn,ceiling,online)\n        p.operation=guarded_operation")
(ROOT/'scripts/resume_observed_feedback_45011_s2.py').write_text(t)
print(json.dumps(v))
