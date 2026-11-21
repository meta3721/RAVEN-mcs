"""Read-only source/provenance audit for one method specification."""
import json,hashlib
from pathlib import Path
from observed_feedback_preparation_budget import ROOT,OUT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    prior=ROOT/'results_action_difference_revision_20261013'
    reports=ROOT/'ccf-review-report/action_difference_revision_20261013'
    texts={p.name:p.read_text(encoding='utf-8') for p in reports.glob('*.md')}
    assert len(texts)==8
    old=json.loads((prior/'PROTECTED_BEFORE.json').read_text())
    for p,h in old.items():assert digest(Path(p))==h,p
    extra={str(p):digest(p) for base in (prior,reports,ROOT/'src/raven_mcs_re_interval',ROOT/'src/raven_mcs/control',
        ROOT/'src/raven_mcs_execution') for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    extra[str(ROOT/'TO_OVERLEAF_paper_tmc_r1_clean/main.tex')]=digest(ROOT/'TO_OVERLEAF_paper_tmc_r1_clean/main.tex')
    v1=Path('C:/Users/szr/Desktop/record/1/results_reachability_stopping_v1')
    for name in ('run_geometry_gate.py','STOP_REPORT.md','PROTOCOL.md','FROZEN_CONFIG.json','MAIN_COMPARISON.csv'):
        extra[str(v1/name)]=digest(v1/name)
    protected={**old,**extra}
    schema=(ROOT/'src/raven_mcs_re_interval/schema.py').read_text()
    lifecycle=(ROOT/'src/raven_mcs_re_interval/lifecycle.py').read_text()
    preview=(ROOT/'src/raven_mcs_re_interval/preview.py').read_text()
    checks=dict(actual_ell='.5*np.abs(omega-np.asarray(snapshot.mu)).sum()' in preview,
        P2_debt='debt=np.asarray(snapshot.debt)' in preview,
        R_E='R=int(summary.total>0);E=int(features.model_age<=self.config.age_max)' in lifecycle,
        old_config_version_frozen='configuration changes frozen RE-interval-v3 definition' in schema,
        old_future_constructor='predictor: FrozenServiceModel' in lifecycle,
        registered_q_frozen="rec.q,self.now" in lifecycle,
        at_most_once='duplicate consumption or preview key mismatch' in lifecycle,
        empty_leaves_state='if preview.keys:' in lifecycle,
        actual_release_updates_debt='self.debt=tuple(update_debt' in lifecycle)
    assert all(checks.values()),checks
    result=dict(status='PASS',prior_reports_read=sorted(texts),checks=checks,protected_count=len(protected),
        old_candidate_status=json.loads((prior/'C_RESULT.json').read_text())['status'],
        prior_charged=json.loads((prior/'FINAL_BUDGET.json').read_text())['cumulative_application_charged_CPU'],
        no_new_controller=True,no_future_or_private_event_inputs=True,mode='source_and_report_audit_only')
    assert result['prior_charged']==4535.093750
    with (OUT/'PROTECTED_BEFORE.json').open('x') as stream:json.dump(protected,stream,indent=2)
    with (OUT/'SOURCE_AUDIT.json').open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result))
