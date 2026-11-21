"""Verify scoped preservation and changed syntax; no scientific execution."""
import ast
import json
from pathlib import Path
from diagnose_calibration_d0 import ROOT, OUT, OLD, read, save, digest

if __name__=='__main__':
    before=read(OUT/'PROTECTED_BEFORE.json')
    changed=[p for p,h in before.items() if not Path(p).is_file() or digest(p)!=h]
    sources=read(OLD/'trajectory/SOURCE_CLOSURE.json')
    scientific_changes=[p for p,h in sources.items() if digest(ROOT/p)!=h]
    files=['scripts/windows_cpu_meter.py','scripts/validate_conditional_bundle_b0.py',
        'scripts/diagnostic_meter_workload.py','scripts/diagnostic_meter_check.py',
        'scripts/diagnostic_legacy_meter_repro.py','scripts/diagnostic_bounded.py',
        'scripts/diagnose_calibration_d0.py','scripts/diagnose_calibration_support.py',
        'scripts/finalize_calibration_diagnostic.py']
    for p in files:ast.parse((ROOT/p).read_text(encoding='utf-8'),filename=p)
    support=read(OUT/'SUPPORT_SUMMARY.json')
    r=support['reasons']
    future=sum(n for s,n in r.items() if 'NO_COMPATIBLE_MARK' in s and ':(' not in s)
    inflight=sum(n for s,n in r.items() if 'NO_COMPATIBLE_MARK' in s and ':(' in s)
    save('FINAL_VERIFICATION.json',dict(status='PASS' if not changed and not scientific_changes else 'FAIL',
        protected_files=len(before),changed=changed,scientific_source_changes=scientific_changes,
        syntax_files=files,syntax_passed=True,missing_mark_first_reason=dict(future_opportunity=future,in_flight=inflight),
        D0=read(OUT/'D0_IDENTITY.json')['status'],D1=read(OUT/'D1_CHECK.json')['status'],D2=support['status'],
        planner_replays=0,new_trajectories=0,local_SGD=0,q_fit=0,GPU=0))
    print(json.dumps(dict(protected_files=len(before),changed=changed,scientific_source_changes=scientific_changes,
        syntax_files=len(files),future_missing_mark=future,inflight_missing_mark=inflight)))
    assert not changed and not scientific_changes
