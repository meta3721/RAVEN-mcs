"""Continuous original3600 budget; the former pilot estimate is not an admission gate."""
import argparse,json,sys,time,os,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from coordinated_windows_cpu_meter import run_coordinated_metered
OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s1'
REPORT=ROOT/'ccf-review-report/observed_feedback_rolling_45011_20261014_s1'
PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'
START=247.625
def usage():
    old=json.loads((PARENT/'BUDGET.json').read_text());assert old['charged_CPU']==START
    v=dict(old['categories']);v['setup']+=30.
    for p in OUT.glob('charge_*.json'):
        for k,x in json.loads(p.read_text())['categories'].items():v[k]+=x
    return v
def ledger():
    v=usage();rows=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')];used=sum(v.values());assert used<=3600
    value=dict(starting_charged_CPU=START,charged_CPU=used,CPU_limit=3600,remaining_CPU=3600-used,categories=v,
        new_audited_CPU=sum(r['root_CPU'] for r in rows if r['audit']),new_conservative_failed_CPU=sum(r['root_CPU'] for r in rows if not r['audit']),
        new_read_edit_delivery_conservative_CPU=30,prior_known_audited_CPU=178.03125,prior_conservative_CPU=69.59375,actual_unmetered_CPU='UNKNOWN',
        cumulative_original5h_charged_CPU=4765.234375+used,nominal_original5h_remaining_CPU=18000-4765.234375-used,
        historical_actual_gap='UNKNOWN',charges=rows,wall_measured=sum(r['wall'] for r in rows),category_role='transferable planning categories, not stopping caps',state='WAITING_USER_REVIEW')
    (OUT/'BUDGET.json').write_text(json.dumps(value,indent=2));return value
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--category',default='setup');p.add_argument('--cap',type=float,default=80);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        baseline=json.loads((ROOT/'results_observed_feedback_acquisition_45011_20261014/PROTECTED_HISTORY.json').read_text())
        for directory in (PARENT,ROOT/'ccf-review-report/observed_feedback_continuation_45011_20261014',ROOT/'ccf-review-report/observed_feedback_acquisition_45011_20261014'):
            for path in directory.rglob('*'):
                if path.is_file():baseline[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        (OUT/'PROTECTED_BEFORE.json').write_text(json.dumps(baseline,indent=2))
        print(json.dumps(ledger()));raise SystemExit(0)
    path=OUT/('charge_'+a.label+'.json');assert not path.exists()
    used=usage();remaining=3600-sum(used.values());cap=min(a.cap,remaining-8)
    if cap<1:raise RuntimeError('actual remaining budget insufficient')
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    from raven_mcs_execution import budget as shared
    from raven_mcs_observed_feedback.budget_client import AtomicPublisher
    shared.RootBudgetPublisher=AtomicPublisher
    bootstrap=time.process_time();(OUT/('LAUNCH_COST_'+a.label+'.json')).write_text(json.dumps(dict(label=a.label,bootstrap_CPU=bootstrap,used_categories=used)))
    if a.label.startswith('resume'):(OUT/'LAUNCH_COST.json').write_text(json.dumps(dict(label=a.label,bootstrap_CPU=bootstrap,used_categories=used)))
    live=OUT/('ROOT_BUDGET_'+a.label+'.json');os.environ['OF_ROOT_BUDGET_PATH']=str(live)
    consumed_wall=36.09939210000084+sum(json.loads(q.read_text())['wall'] for q in OUT.glob('charge_resume*.json'))
    wall_cap=max(1.,7200-consumed_wall) if a.label.startswith('resume') else 180
    start=time.perf_counter()
    try:
        result=run_coordinated_metered(command,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=wall_cap,cwd=ROOT,
            budget_feedback=dict(path=str(live),prior_batch=sum(used.values())+bootstrap,prior_phase=0,batch_limit=3600,phase_limit=3600))
        cost=result['process_tree_cpu_seconds']+time.process_time()
        if a.label.startswith('resume') and (OUT/'CATEGORY_LIVE.json').exists():
            cats=json.loads((OUT/'CATEGORY_LIVE.json').read_text())['spent'];cats['events']+=max(0.,cost-sum(cats.values()))
        else:cats={a.category:cost}
        row=dict(label=a.label,root_CPU=cost,job_CPU=result['process_tree_cpu_seconds'],driver_CPU=time.process_time(),categories=cats,wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed'],limit=result['limit_reason'],wall_watchdog_remaining_at_launch=wall_cap)
    except Exception as exc:
        wall=time.perf_counter()-start;cost=math.ceil(wall)+1+time.process_time();row=dict(label=a.label,root_CPU=cost,categories={a.category:cost},wall=wall,exit=repr(exc),audit=False,actual_CPU='UNKNOWN; conservative single-job CPU wall + driver bound')
    with path.open('x') as f:json.dump(row,f,indent=2)
    print(json.dumps(ledger()));raise SystemExit(0 if row['audit'] and row['exit']==0 else 1)
