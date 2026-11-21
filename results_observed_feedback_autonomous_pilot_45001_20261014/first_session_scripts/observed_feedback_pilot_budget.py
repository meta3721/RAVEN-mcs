"""New authorized45001 pilot:3000 root CPU;14400 execution wall;no old debit."""
import argparse,json,sys,time,os,math,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
REPORT=ROOT/'ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014'
from coordinated_windows_cpu_meter import run_coordinated_metered
def ledger():
 rows=[json.loads(p.read_text()) for p in sorted(OUT.glob('charge_*.json'))]
 categories=dict(setup=30.,initialization=0.,online=0.,training=0.,events=0.,save=0.,repair=0.)
 for row in rows:
  for k,v in row['categories'].items():categories[k]+=v
 used=sum(categories.values());job_wall=sum(x['wall'] for x in rows)
 elapsed=time.time()-OUT.stat().st_ctime
 wall=max(job_wall,elapsed+600.)
 value=dict(batch='user20261014_autonomous_pilot_45001',authority='observed-feedback-v1-autonomous-pilot-instruction-20261014.md delivered by human',
  CPU_limit=3000,wall_limit=14400,charged_CPU=used,remaining_CPU=3000-used,wall_used=wall,remaining_wall=14400-wall,job_wall_measured=job_wall,active_since_batch_creation_wall=elapsed,preinitialize_wall_conservative=600.,wall_role='active elapsed includes development/waits/execute/delivery;600 conservatively covers preinitialize preparation; no human approval wait in this batch',categories=categories,charges=rows,
  actual_audited_CPU=sum(x['root_CPU'] for x in rows if x['audit']),conservative_CPU=30+sum(x['root_CPU'] for x in rows if not x['audit']),unmetered_actual_CPU='UNKNOWN',
  historical45011_batch_charged_CPU=757.375,historical_all_charged_CPU=5522.609375,historical_plus_new_charged_CPU=5522.609375+used,old_balance_role='display only; not authority or duplicate debit',state='WAITING_USER_REVIEW')
 (OUT/'BUDGET.json').write_text(json.dumps(value,indent=2));return value
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--arm');p.add_argument('--category',default='setup');p.add_argument('--cap',type=float,default=80);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 if a.initialize:
  OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False);print(json.dumps(ledger()));raise SystemExit()
 prior=ledger();path=OUT/('charge_'+a.label+'.json');assert not path.exists()
 cap=min(a.cap,prior['remaining_CPU']-8);assert cap>=1
 arm_out=OUT/a.arm if a.arm else OUT;arm_out.mkdir(exist_ok=True)
 cmd=a.command[1:] if a.command[:1]==['--'] else a.command
 from raven_mcs_execution import budget as shared
 from observed_feedback_root_publisher import SharingTolerantPublisher
 shared.RootBudgetPublisher=SharingTolerantPublisher
 bootstrap=time.process_time();launch=dict(label=a.label,bootstrap_CPU=bootstrap,used_categories=prior['categories'])
 (arm_out/'LAUNCH_COST.json').write_text(json.dumps(launch));(OUT/('launch_'+a.label+'.json')).write_text(json.dumps(launch))
 live=Path(tempfile.mkdtemp(prefix='root_feedback_',dir=arm_out))/'root.json';os.environ['OF_ROOT_BUDGET_PATH']=str(live)
 arm_wall=sum(x['wall'] for x in prior['charges'] if x.get('arm')==a.arm) if a.arm else 0
 wall_cap=min(prior['remaining_wall'],7200-arm_wall) if a.arm else min(prior['remaining_wall'],300)
 if wall_cap<=0:raise RuntimeError('CUMULATIVE_WALL_EXHAUSTED')
 os.environ['OF_ARM_WALL_LIMIT']=str(wall_cap)
 start=time.perf_counter()
 try:
  r=run_coordinated_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=wall_cap,cwd=ROOT,budget_feedback=dict(path=str(live),prior_batch=prior['charged_CPU']+bootstrap,prior_phase=0,batch_limit=3000,phase_limit=3000))
  cost=r['process_tree_cpu_seconds']+time.process_time()
  cats=json.loads((arm_out/'CATEGORY_LIVE.json').read_text())['spent'] if a.arm and (arm_out/'CATEGORY_LIVE.json').exists() and (arm_out/'CATEGORY_LIVE.json').stat().st_mtime>=time.time()-r['wall_seconds']-2. else {a.category:cost}
  if a.arm:cats['events']+=max(0,cost-sum(cats.values()))
  row=dict(label=a.label,arm=a.arm,root_CPU=cost,job_CPU=r['process_tree_cpu_seconds'],driver_CPU=time.process_time(),categories=cats,wall=r['wall_seconds'],exit=r['returncode'],audit=r['audit_passed'],limit=r['limit_reason'],root_feedback=str(live),wall_cap_at_launch=wall_cap)
 except Exception as exc:
  wall=time.perf_counter()-start;cost=math.ceil(wall)+1+time.process_time();row=dict(label=a.label,arm=a.arm,root_CPU=cost,categories={a.category:cost},wall=wall,exit=repr(exc),traceback=__import__('traceback').format_exc(),audit=False,actual_CPU='UNKNOWN; singleCPUwall+driver conservative bound')
 with path.open('x') as f:json.dump(row,f,indent=2)
 print(json.dumps(ledger()));raise SystemExit(0 if row['audit'] and row['exit']==0 else 1)
