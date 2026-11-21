"""45011 continuation: total cap unchanged, category plans transferable by addendum."""
import argparse,json,sys,time,math,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from coordinated_windows_cpu_meter import run_coordinated_metered
OUT=ROOT/'results_observed_feedback_continuation_45011_20261014'
REPORT=ROOT/'ccf-review-report/observed_feedback_continuation_45011_20261014'
OLD=ROOT/'results_observed_feedback_acquisition_45011_20261014'
CAPS=dict(setup=220.,initialization=120.,online=1000.,training=800.,events=950.,save=360.,repair=150.)
def usage():
    v=json.loads((OLD/'BUDGET.json').read_text())['categories'];v['setup']+=30.
    for p in OUT.glob('charge_*.json'):
        row=json.loads(p.read_text())
        for k,c in row['categories'].items():v[k]+=c
    return v
def ledger():
    v=usage();used=sum(v.values());assert used<=3600
    rows=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')]
    value=dict(charged_CPU=used,CPU_limit=3600,plans=CAPS,category_roles='transferable plans and warnings; not stopping caps',categories=v,measured_continuation_root_CPU=sum(r['root_CPU'] for r in rows),
        read_edit_delivery_conservative_CPU=30,unmetered_actual_CPU='UNKNOWN',prior_charged_CPU=4765.234375,
        cumulative_charged_CPU=4765.234375+used,nominal_5hour_remaining_CPU=18000-4765.234375-used,
        historical_actual_gap='UNKNOWN',charges=rows,wall_measured=sum(r['wall'] for r in rows),state='WAITING_USER_REVIEW')
    (OUT/'BUDGET.json').write_text(json.dumps(value,indent=2));return value
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--category',default='setup');p.add_argument('--cap',type=float,default=60)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False);(OUT/'SOURCE_BEFORE').mkdir()
        for path in (ROOT/'src/raven_mcs_observed_feedback').glob('*.py'):(OUT/'SOURCE_BEFORE'/path.name).write_bytes(path.read_bytes())
        baseline=json.loads((ROOT/'results_observed_feedback_implementation_20261013/PROTECTED_BEFORE.json').read_text())
        for directory in ('results_observed_feedback_readiness_20261014','results_observed_feedback_persistent_cost_20261014',
                'ccf-review-report/observed_feedback_readiness_20261014','ccf-review-report/observed_feedback_persistent_cost_20261014'):
            for path in (ROOT/directory).rglob('*'):
                if path.is_file():baseline[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        (OUT/'PROTECTED_HISTORY.json').write_text(json.dumps(baseline,indent=2))
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(method='reachability_stop/observed-feedback-v1',seed=45011,T=100,
            role='development_cost_and_bootstrap_fit_candidate',CPU_limit=3600,caps=CAPS,SGD_limit=5000,GPU=0,q_fit=0,watchdog_seconds=7200),indent=2))
        ledger();raise SystemExit(0)
    if (OUT/('charge_'+a.label+'.json')).exists():raise RuntimeError('already charged')
    used=usage();remaining=3600-sum(used.values());cap=min(a.cap,remaining-3)
    if cap<1:raise RuntimeError('budget exhausted')
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    from raven_mcs_execution import budget as shared
    from raven_mcs_observed_feedback.budget_client import AtomicPublisher
    shared.RootBudgetPublisher=AtomicPublisher
    (OUT/'LAUNCH_COST.json').write_text(json.dumps(dict(label=a.label,bootstrap_CPU=time.process_time(),used_categories=used)))
    start=time.perf_counter()
    live_path=OUT/('ROOT_BUDGET_'+a.label+'.json')
    os.environ['OF_ROOT_BUDGET_PATH']=str(live_path)
    try:
        result=run_coordinated_metered(command,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=7200 if a.label=='acquire' else 180,cwd=ROOT,
            budget_feedback=dict(path=str(live_path),prior_batch=sum(used.values())+time.process_time(),
                prior_phase=0,batch_limit=3600,phase_limit=3600))
        cost=result['process_tree_cpu_seconds']+time.process_time()
        if a.label=='acquire' and (OUT/'CATEGORY_LIVE.json').exists():
            cats=json.loads((OUT/'CATEGORY_LIVE.json').read_text())['spent'];cats['events']+=max(0.,cost-sum(cats.values()))
        elif a.label=='sgd0_integration' and (OUT/'SGD0_SAVE_MEASUREMENT.json').exists():
            save_cost=json.loads((OUT/'SGD0_SAVE_MEASUREMENT.json').read_text())['root_difference']
            cats={'save':save_cost,a.category:max(0.,cost-save_cost)}
        else:cats={a.category:cost}
        row=dict(label=a.label,root_CPU=cost,job_CPU=result['process_tree_cpu_seconds'],driver_CPU=time.process_time(),categories=cats,
            wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed'],limit=result['limit_reason'])
    except Exception as e:
        wall=time.perf_counter()-start;cost=math.ceil(wall)+1+time.process_time()
        row=dict(label=a.label,root_CPU=cost,categories={a.category:cost},wall=wall,exit=repr(e),audit=False,actual_CPU='UNKNOWN; conservative oneCPU job wall bound')
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:json.dump(row,f,indent=2)
    print(json.dumps(ledger()));raise SystemExit(0 if row['audit'] and row['exit']==0 else 1)
