"""Scoped preservation, syntax and evidence check; no additional experiment."""
import ast
import json
from pathlib import Path
from revision_feasibility_budget import ROOT,OUT,REPORT,used
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.control.persistence import source_inventory
from raven_mcs_re_interval.persistence import source_identity

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

if __name__=='__main__':
    protected=read(ROOT/'results_calibration_diagnostic_20261013_122013/PROTECTED_BEFORE.json')
    changed=[p for p,h in protected.items() if not Path(p).is_file() or sha256_file(Path(p))!=h]
    old=read(ROOT/'results_calibration_first_20261013/trajectory/SOURCE_CLOSURE.json')
    old_source_ok=old==source_inventory(ROOT)
    freeze=read(OUT/'S1_FROZEN_INPUTS.json')
    frozen_ok=(freeze['script_sha256']==sha256_file(ROOT/'scripts/revision_feasibility_s2.py') and
               freeze['spec_sha256']==sha256_file(REPORT/'REVISION_SPEC_FROZEN.md'))
    files=sorted((ROOT/'src/raven_mcs_re_interval').glob('*.py'))
    files += [ROOT/'scripts'/x for x in ('validate_re_interval_revision.py','revision_feasibility_s2.py',
        'revision_feasibility_budget.py','prepare_interval_revision_package.py','finalize_re_interval_revision.py')]
    for p in files:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    checks={name:read(OUT/f'S3_{name}_PASS_{tag}.json')['status'] for name,tag in
        [('RE','clock_final'),('unknown','final'),('supported','final')]}
    decisions={}
    for name in ('late_unknown','early_unknown','supported'):
        packet=read(OUT/f'S3_{name}_decision_final.json');d=packet['decision'];a=packet['accounting']
        decisions[name]={k:d[k] for k in ('action','reason','proven','control_cpu_seconds','wall_seconds','p2_solves','cache_hits')}
        assert a['audit_passed'] and a['difference_seconds']==0 and d['control_cpu_seconds']<=2
    assert all(x=='PASS' for x in checks.values()) and not changed and old_source_ok and frozen_ok
    charges=[read(p) for p in OUT.glob('charge_*.json')]
    assert all(c['accounting_pass'] and c['returncode'] in (0,1) for c in charges)
    result=dict(status='REVISION_IMPLEMENTED_NOT_PERFORMANCE_VALIDATED',next_state='WAITING_USER_REVIEW',
        S2=read(OUT/'S2_RESULT.json')['status'],S3=checks,decisions=decisions,
        protected_files=len(protected),changed_protected=changed,old_source_closure_identical=old_source_ok,
        old_source_files=len(old),S1_unchanged=frozen_ok,syntax_files=[str(p.relative_to(ROOT)) for p in files],
        final_revision_source_identity=source_identity(),budget_before_this_final_check=used(),
        development_snapshot_addendum=dict(pool=1,legal_actions=['WAIT'],status='RULE_FORCED',
            proven=False,k=0,N=80,conservative_cutoff=20.18,real_activation_evidence=False),
        training=0,SGD=0,q_fit=0,GPU=0,new_real_trajectory=0,random_synthetic_replay=0,
        q_status='DEPENDENCY_PENDING; isolated q=0.5 is not calibrated',
        cancelled_or_not_started=['43002-43008','B1','formal_confirmation','paper_changes'])
    with (OUT/'FINAL_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
    print(json.dumps({k:result[k] for k in ('status','next_state','S3','decisions','protected_files','old_source_files','S1_unchanged')},ensure_ascii=False))
