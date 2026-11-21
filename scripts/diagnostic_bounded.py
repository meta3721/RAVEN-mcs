"""Sequential 900 CPU-second diagnostic ledger; no experiment queue."""
import argparse
import json
from pathlib import Path
import time
from validate_conditional_bundle_b0 import run_accounted

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_calibration_diagnostic_20261013_122013'

def used():
    d1=json.loads((OUT/'D1_CHECK.json').read_text())
    d0=json.loads((OUT/'D0_IDENTITY.json').read_text())
    value=90+d0['bootstrap_process_cpu']+d1['driver_self_CPU']+sum(x['process_tree_cpu_seconds'] for x in d1['tests'])
    for p in OUT.glob('charged_*.json'):
        r=json.loads(p.read_text());value+=r['job_CPU']+r['driver_lifetime_CPU_at_record']
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--cap',type=float,default=60)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    previous=used();allowance=min(a.cap,900-previous-5)
    if allowance<=.5:raise RuntimeError('DIAGNOSTIC_BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    r=run_accounted(cmd,OUT/(a.label+'.log'),cpu_limit=allowance,wall_limit=120)
    charge=dict(job_CPU=r['process_tree_cpu_seconds'],driver_lifetime_CPU_at_record=time.process_time(),
        monitor_already_in_driver=r['monitor_cpu_seconds'],wall=r['wall_seconds'],
        previous_charged=previous,returncode=r['returncode'],audit_passed=r['audit_passed'])
    with (OUT/('charged_'+a.label+'.json')).open('x') as f:json.dump(charge,f,indent=2)
    print(json.dumps(charge))
    if not r['audit_passed']:raise RuntimeError('ACCOUNTING_FAILURE')
    if r['limit_reason']:raise RuntimeError('BUDGET_STOP')
    raise SystemExit(r['returncode'])
