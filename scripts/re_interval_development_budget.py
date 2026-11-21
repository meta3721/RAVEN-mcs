"""Single 44001 development batch; suspended-start root meter and hard ledger."""
import argparse,json,time
from pathlib import Path
from windows_cpu_meter import run_metered
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_re_interval_development_44001_20261013'
REPORT=ROOT/'ccf-review-report/re_interval_development_44001_20261013'
def used():
    rows=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')]
    return 60+sum(max(r['charged_CPU'],r['job_CPU']+r['driver_CPU']) for r in rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=200)
    p.add_argument('--wall',type=float,default=120);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(seed=44001,role='development_activation_cost_only',
            method='reachability_stop/conditional-bundle-RE-interval-v3',T=100.,CPU_limit=2700.,planning_CPU_limit=2.,
            GPU=0,SGD_limit=5000,q_fit=0,trajectories=1,prior_charged_CPU=1929.453125,
            interactive_tail_reserve=60,watchdog_seconds=7200,
            instruction='C:/Users/szr/Desktop/record/1/research-protocols/re-interval-v3-single-development-acquisition-instruction-20261013.md'),indent=2))
        print(str(OUT));raise SystemExit(0)
    allowance=min(a.cap,2700-used()-5)
    if allowance<=1:raise RuntimeError('BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    r=run_metered(cmd,OUT/(a.label+'.log'),cpu_limit=allowance,wall_limit=a.wall,cwd=ROOT)
    driver=time.process_time()
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:
        json.dump(dict(charged_CPU=r['process_tree_cpu_seconds']+driver,job_CPU=r['process_tree_cpu_seconds'],
            driver_CPU=driver,wall=r['wall_seconds'],returncode=r['returncode'],accounting_pass=r['audit_passed'],limit_reason=r['limit_reason']),f,indent=2)
    print(json.dumps(dict(label=a.label,total_charged=used(),exit=r['returncode'],meter=r['audit_passed'],limit=r['limit_reason'])))
    if not r['audit_passed'] or r['limit_reason']:raise RuntimeError('FACILITY_OR_BUDGET_STOP')
    raise SystemExit(r['returncode'])
