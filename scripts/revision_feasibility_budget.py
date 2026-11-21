"""240 CPU-second, zero-training revision feasibility batch; no run queue."""
import argparse,json,time
from pathlib import Path
from windows_cpu_meter import run_metered
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_revision_feasibility_20261013_125348'
REPORT=ROOT/'ccf-review-report/revision_feasibility_20261013_125348'

def used():
    rows=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')]
    return 30+sum(max(r['charged_CPU'],r['job_CPU']+r['driver_CPU']) for r in rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=45)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        data=dict(limit_CPU_seconds=240,interactive_tail_reserve=30,prior_charged_CPU=1862.296875,
            new_training=0,local_SGD=0,GPU=0,q_fit=0,real_acquisition=0,remaining_seeds_authorized=False,
            planning_CPU_limit=2,execution_order=['S1','S2','S3_if_S2_passes','S4'],
            source_instruction='C:/Users/szr/Desktop/record/1/research-protocols/conditional-bundle-revision-feasibility-instruction-20261013.md')
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(data,indent=2))
        print(json.dumps(data));raise SystemExit(0)
    allowance=min(a.cap,240-used()-3)
    if allowance<=.5:raise RuntimeError('BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    r=run_metered(cmd,OUT/(a.label+'.log'),cpu_limit=allowance,wall_limit=90,cwd=ROOT)
    driver_cpu=time.process_time();cost=r['process_tree_cpu_seconds']+driver_cpu
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:
        json.dump(dict(charged_CPU=cost,job_CPU=r['process_tree_cpu_seconds'],driver_CPU=driver_cpu,
            wall=r['wall_seconds'],returncode=r['returncode'],accounting_pass=r['audit_passed']),f,indent=2)
    print(json.dumps(dict(label=a.label,charged_CPU=cost,total_charged=used(),exit=r['returncode'],meter=r['audit_passed'])))
    if not r['audit_passed'] or r['limit_reason']:raise RuntimeError('FACILITY_OR_BUDGET_STOP')
    raise SystemExit(r['returncode'])
