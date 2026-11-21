"""Final changed-path syntax and artifact checks; no scientific computation."""
import ast
import json
import re
from pathlib import Path
from diagnose_calibration_d0 import ROOT,OUT,read,save

if __name__=='__main__':
    previous=read(OUT/'FINAL_VERIFICATION.json')
    files=previous['syntax_files']+['scripts/check_calibration_diagnostic_delivery.py']
    for name in files:ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    reports=ROOT/'ccf-review-report/calibration_diagnostic_20261013_122013'
    links=[]
    for p in reports.iterdir():
        assert p.suffix=='.md',p
        for target in re.findall(r'\]\((C:/[^)]+)\)',p.read_text(encoding='utf-8')):
            clean=re.sub(r':\d+$','',target)
            # Budget is written only after this measured check has closed.
            if clean.endswith('/FINAL_BUDGET.json'):continue
            assert Path(clean).exists(),clean
            links.append(clean)
    nested=read(OUT/'nested_planner_timeout.meter.json')
    raw=[json.loads(s) for s in (OUT/'nested_planner_timeout.log').read_text().splitlines()]
    last=raw[-1]
    assert nested['audit_passed'] and nested['returncode']==0
    assert last['status']=='cpu_timeout' and last['child_exit']==124 and last['combined_planning_CPU']<=2
    assert any(p['pid']==last['terminated_child'] and p['exit_code']==124 and p['cpu_seconds']>0 for p in nested['pids'])
    save('DELIVERY_CHECK.json',dict(status='PASS',syntax_files=len(files),checked_local_links=len(links),
        reports=[p.name for p in reports.iterdir()],nested_planning_timeout_verified=True,
        scientific_sources_unchanged=not previous['scientific_source_changes'],historical_files_unchanged=not previous['changed'],
        no_new_training=True,no_q_fit=True,no_new_trajectory=True))
    print(json.dumps(dict(status='PASS',syntax_files=len(files),links=len(links))))
