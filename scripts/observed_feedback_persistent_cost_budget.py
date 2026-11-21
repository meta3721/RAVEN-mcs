"""Authorized 90 CPU seconds: persistent mathematical worker, no training."""
import argparse,json,sys,time,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from coordinated_windows_cpu_meter import run_coordinated_metered
OUT=ROOT/'results_observed_feedback_persistent_cost_20261014'
REPORT=ROOT/'ccf-review-report/observed_feedback_persistent_cost_20261014'
def used():return 30.+sum(json.loads(p.read_text())['charged_CPU'] for p in OUT.glob('charge_*.json'))
def ledger():
    rows=[dict(label=p.stem,**json.loads(p.read_text())) for p in sorted(OUT.glob('charge_*.json'))]
    value=dict(charged_CPU=used(),CPU_limit=90,measured_root_CPU=sum((r['job_CPU'] or 0)+r['driver_CPU'] for r in rows),
        conservative_read_edit_delivery_CPU=30,unmetered_actual_CPU='UNKNOWN; within charged reserve',
        prior_charged_CPU=4730.046875,cumulative_charged_CPU=4730.046875+used(),
        nominal_5hour_remaining_CPU=18000-4730.046875-used(),historical_actual_gap='UNKNOWN',
        wall_invocations=sum(r['wall'] for r in rows),charges=rows,SGD=0,GPU=0,q_fit=0,
        real_random_trajectories=0,control_replay=0,state='WAITING_USER_REVIEW')
    assert value['charged_CPU']<=90
    (OUT/'FINAL_BUDGET.json').write_text(json.dumps(value,indent=2));return value
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=20.)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        frozen=ROOT/'results_observed_feedback_readiness_20261014/FROZEN_INPUT.json'
        (OUT/'FROZEN_INPUT.json').write_bytes(frozen.read_bytes())
        protected=json.loads((ROOT/'results_observed_feedback_implementation_20261013/PROTECTED_BEFORE.json').read_text())
        for directory in ('results_observed_feedback_readiness_20261014','ccf-review-report/observed_feedback_readiness_20261014'):
            for path in (ROOT/directory).rglob('*'):
                if path.is_file():protected[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in ('src/raven_mcs','src/raven_mcs_observed_feedback','src/raven_mcs_execution'):
            for path in (ROOT/directory).rglob('*.py'):protected[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        (OUT/'PROTECTED_BEFORE.json').write_text(json.dumps(protected,indent=2))
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(CPU_limit=90,initialization_CPU_limit=6,online_CPU_limit=2,
            new_workers_allowed=1,requests=['A_first_P2','B_same_input_cache'],input_hash=hashlib.sha256(frozen.read_bytes()).hexdigest(),
            SGD=0,GPU=0,q_fit=0,trajectories=0,collection_entry_implementation=False),indent=2))
        ledger();raise SystemExit(0)
    if (OUT/('charge_'+a.label+'.json')).exists():raise RuntimeError('already charged')
    cap=min(a.cap,90-used()-3)
    if cap<1:raise RuntimeError('BUDGET_EXHAUSTED')
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    from raven_mcs_execution import budget as shared
    from raven_mcs_observed_feedback.budget_client import AtomicPublisher
    shared.RootBudgetPublisher=AtomicPublisher
    (OUT/'LAUNCH_COST.json').write_text(json.dumps(dict(label=a.label,launcher_bootstrap_CPU=time.process_time())))
    wall=time.perf_counter()
    try:
        result=run_coordinated_metered(command,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=60,cwd=ROOT,
            budget_feedback=dict(path=str(OUT/'ROOT_BUDGET_LIVE.json'),prior_batch=used()+time.process_time(),
            prior_phase=used()+time.process_time(),batch_limit=90,phase_limit=90))
        charge=dict(charged_CPU=result['process_tree_cpu_seconds']+time.process_time(),job_CPU=result['process_tree_cpu_seconds'],
            driver_CPU=time.process_time(),wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed'],limit_reason=result['limit_reason'])
    except Exception as exc:
        duration=time.perf_counter()-wall
        charge=dict(charged_CPU=math.ceil(duration)+1+time.process_time(),job_CPU=None,driver_CPU=time.process_time(),
            wall=duration,exit=repr(exc),audit=False,conservative_basis='one-CPU job wall ceiling+1; disjoint driver CPU')
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:json.dump(charge,f,indent=2)
    if a.label=='persistent_A_B' and (OUT/'LIVE_PHASE_RESULT.json').exists():
        phases=json.loads((OUT/'LIVE_PHASE_RESULT.json').read_text())
        measured=sum(r['root_sample_difference_CPU'] for r in phases['measurements'])
        tail=charge['charged_CPU']-measured
        (OUT/'FINALIZATION_ROOT_COST.json').write_text(json.dumps(dict(total_measured_root_CPU=charge['charged_CPU'],
            measured_initial_and_requests_CPU=measured,remaining_root_CPU=tail,
            includes='all sample bridges/gaps, audit dump, verification, worker/parent shutdown and final monitor; disjoint from the listed phase sample intervals'),indent=2))
    print(json.dumps(ledger()));raise SystemExit(0 if charge['audit'] and charge['exit']==0 else 1)
