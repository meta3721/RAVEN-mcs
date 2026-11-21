"""Classify stored exact matches, preserving the initial audit unchanged."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_calibration_first_20261013'
x=json.loads((OUT/'SEED_AND_INPUT_AUDIT.json').read_text(encoding='utf-8'))
classified=[];conflicts=[]
for row in x['review_required']:
    text=re.sub(r'\b[0-9a-f]{64}\b','[digest]',row['text'])
    reason=None
    if '43001' not in text:reason='SHA256 substring; associated actual run seed30014, not seed43001'
    if Path(row['path']).name=='build_delivery.py' and 'results_conditional_bundle_b0_20261012_223821' in Path(row['path']).parts:
        reason='source of the already reviewed B0 proposal text; no execution'
    classified.append(dict(**row,classification=reason or 'unresolved'))
    if reason is None:conflicts.append(row)
result=dict(seed=43001,initial_audit=str(OUT/'SEED_AND_INPUT_AUDIT.json'),classified=classified,
    conflicts=conflicts,status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not conflicts and not x['seed_named_assets'] and not x['unreadable'] else 'REVIEW_REQUIRED',
    evidence_scope='98710 local text files plus binary asset filename/companion metadata inventory; external inaccessible history not asserted')
(OUT/'SEED_REVIEW.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(result['status'],len(classified),'classified',len(conflicts),'conflicts')
