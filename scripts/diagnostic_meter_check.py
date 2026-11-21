"""Execute the two fixed D1 facility tests, no experiment entry imported."""
from pathlib import Path
import json
import time
from windows_cpu_meter import run_metered

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_calibration_diagnostic_20261013_122013'

if __name__=='__main__':
    results=[]
    # Limits/tolerance saved in AUTHORIZATION before any readings.
    for mode,limit in [('normal',8),('timeout',2)]:
        r=run_metered([ROOT/'.venv_new/Scripts/python.exe','scripts/diagnostic_meter_workload.py','--mode',mode],
            OUT/f'D1_{mode}.log',cpu_limit=limit,wall_limit=20,cwd=ROOT)
        results.append(r)
        valid=r['audit_passed'] and r['process_tree_cpu_seconds']>0 and r['job_total_processes']>=3
        valid &= r['returncode']==0 if mode=='normal' else r['limit_reason']=='cpu' and r['returncode']==124 and r['process_tree_cpu_seconds']+r['monitor_cpu_seconds']<=limit
        if not valid:
            (OUT/'D1_FAILED.json').write_text(json.dumps(dict(mode=mode,result=r),indent=2))
            raise RuntimeError('D1 facility validation failed; no downstream calculation')
    (OUT/'D1_CHECK.json').write_text(json.dumps(dict(status='PASS',tests=results,driver_self_CPU=time.process_time(),training=0,q_fit=0,new_trajectories=0),indent=2))
    print(json.dumps(dict(status='PASS',tests=[dict(log=x['log'],cpu=x['process_tree_cpu_seconds'],monitor=x['monitor_cpu_seconds'],pids=x['job_total_processes'],delta=x['difference_seconds']) for x in results])))
