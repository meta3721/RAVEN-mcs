"""120-CPU-second authorized preparation; one cold request only."""
import argparse,json,sys,time,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from coordinated_windows_cpu_meter import run_coordinated_metered
OUT=ROOT/'results_observed_feedback_readiness_20261014'
REPORT=ROOT/'ccf-review-report/observed_feedback_readiness_20261014'
def used():return 30.+sum(json.loads(p.read_text())['charged_CPU'] for p in OUT.glob('charge_*.json'))
def ledger():
    rows=[dict(label=p.stem,**json.loads(p.read_text())) for p in sorted(OUT.glob('charge_*.json'))]
    v=dict(charged_CPU=used(),CPU_limit=120,measured_CPU=sum((r['job_CPU'] or 0)+r['driver_CPU'] for r in rows),
        conservative_read_edit_delivery_CPU=30,actual_unmetered_CPU='UNKNOWN',historical_actual_gap='UNKNOWN',
        prior_charged_CPU=4695.265625,cumulative_charged_CPU=4695.265625+used(),
        nominal_5hour_remaining_CPU=18000-4695.265625-used(),wall_invocations=sum(r['wall'] for r in rows),
        charges=rows,SGD=0,GPU=0,q_fit=0,real_random_trajectories=0,control_replay=0,status='WAITING_USER_REVIEW')
    assert used()<=120
    (OUT/'FINAL_BUDGET.json').write_text(json.dumps(v,indent=2));return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=30)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(CPU_limit=120,read_edit_delivery_reserve=30,
            cold_K43_requests=1,SGD=0,GPU=0,q_fit=0,collection_entry_implementation=False,prior_charged_CPU=4695.265625),indent=2))
        ledger();raise SystemExit(0)
    if (OUT/('charge_'+a.label+'.json')).exists():raise RuntimeError('label already charged')
    cap=min(a.cap,120-used()-3)
    if cap<1:raise RuntimeError('BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    from raven_mcs_execution import budget as shared
    from raven_mcs_observed_feedback.budget_client import AtomicPublisher
    shared.RootBudgetPublisher=AtomicPublisher
    (OUT/'LAUNCH_COST.json').write_text(json.dumps(dict(label=a.label,launcher_bootstrap_CPU=time.process_time())))
    start=time.perf_counter()
    try:
        r=run_coordinated_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=60,cwd=ROOT,
            budget_feedback=dict(path=str(OUT/'ROOT_BUDGET_LIVE.json'),prior_batch=used()+time.process_time(),
            prior_phase=used()+time.process_time(),batch_limit=120,phase_limit=120))
        charge=dict(charged_CPU=r['process_tree_cpu_seconds']+time.process_time(),job_CPU=r['process_tree_cpu_seconds'],
            driver_CPU=time.process_time(),wall=r['wall_seconds'],exit=r['returncode'],audit=r['audit_passed'],limit_reason=r['limit_reason'])
    except Exception as e:
        wall=time.perf_counter()-start
        charge=dict(charged_CPU=math.ceil(wall)+1+time.process_time(),job_CPU=None,driver_CPU=time.process_time(),wall=wall,
            exit=repr(e),audit=False,conservative_basis='one-CPU Job <= wall rounded up +1; measured driver separately')
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:json.dump(charge,f,indent=2)
    print(json.dumps(ledger()));raise SystemExit(0 if charge['audit'] and charge['exit']==0 else 1)
