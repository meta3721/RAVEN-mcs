"""Final document/evidence preservation check; no controller execution."""
import ast,json,hashlib,re
from pathlib import Path
from observed_feedback_preparation_budget import ROOT,OUT,REPORT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    protected=json.loads((OUT/'PROTECTED_BEFORE.json').read_text())
    changed=[p for p,h in protected.items() if not Path(p).is_file() or digest(Path(p))!=h]
    assert not changed,changed
    names=['METHOD_PREPARATION.md','METHOD_SPEC_CANDIDATE.md','PROPERTY_LEDGER.md','MINIMAL_EVIDENCE_PLAN.md','NEXT_STAGE_REQUEST.md']
    docs={n:(REPORT/n).read_text(encoding='utf-8') for n in names}
    assert all(p.suffix=='.md' for p in REPORT.iterdir())
    frozen=json.loads((OUT/'ARITHMETIC_INPUTS_FROZEN.json').read_text())
    assert digest(REPORT/'METHOD_SPEC_CANDIDATE.md')==frozen['spec_sha256']
    result=json.loads((OUT/'ARITHMETIC_RESULT.json').read_text())
    assert result['status']=='PASS_SPEC_ALGEBRA_ONLY' and result['history_effect']
    assert result['actual_P2_execution']==result['production_controller']==result['Traffic_empirical_evidence']==False
    for p in (ROOT/'scripts').glob('*observed_feedback*.py'):
        ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
    links=[]
    for name,text in docs.items():
        for path in re.findall(r'\]\((C:/[^)]+)\)',text):
            assert Path(path).is_file(),(name,path)
            links.append(path)
    assert not (ROOT/'src/raven_mcs_observed_feedback').exists(),'production module must not be implemented in preparation'
    assert '36条T100开发轨迹' in docs['MINIMAL_EVIDENCE_PLAN.md']
    assert '300 CPU秒上限' in docs['NEXT_STAGE_REQUEST.md']
    assert '规格可实现，申请下一次限定实现' in docs['NEXT_STAGE_REQUEST.md']
    output=dict(status='PASS_PREPARATION_DELIVERY_ONLY',protected_files=len(protected),changed_old_files=changed,
        frozen_method_spec_unchanged=True,required_reports=names,local_links_checked=len(links),MD_only=True,
        specification='SPEC_READY_FOR_LIMITED_IMPLEMENTATION',implementation='NOT_IMPLEMENTED',
        q='DEPENDENCY_PENDING',novelty='needs-search',performance='RESULTS_NOT_REVALIDATED',
        next_requested_CPU=300,next_request_authorized=False,new_trajectories=0,SGD=0,GPU=0,q_fit=0,random_replay=0,
        production_controller_implementation=0,facility_retests=0,final_state='WAITING_USER_REVIEW')
    with (OUT/'PREPARATION_FINAL_CHECK.json').open('x') as stream:json.dump(output,stream,indent=2)
    print(json.dumps(output))
