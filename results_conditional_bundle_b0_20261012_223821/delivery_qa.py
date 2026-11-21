"""Read-only final delivery audit, covered by the B0 interactive allowance."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
DOC=ROOT/'ccf-review-report/conditional_bundle_b0_20261012_223821'
sys.path.insert(0,str(ROOT/'src'))
from raven_mcs.control.persistence import source_inventory
links=[]
for file in DOC.glob('*.md'):
    for target in re.findall(r'\]\((C:/[^)]+)\)',file.read_text(encoding='utf-8')):
        links.append(target)
        assert Path(target).exists(),target
saved=json.loads((OUT/'NEW_PATH_TEST_RESULTS.json').read_text(encoding='utf-8'))
assert saved['source_inventory']==source_inventory(ROOT),'source changed after tests'
history=json.loads((OUT/'PROTECTED_BEFORE.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in history.items())
assert all(p.suffix=='.md' for p in DOC.iterdir())
report=dict(status='PASS',markdown_links_checked=len(links),source_files_checked=len(saved['source_inventory']),
    historical_files_checked=len(history),training=0,synthetic_replays=0,real_replays=0,
    state='IMPLEMENTATION_READY_PENDING_CALIBRATION / WAITING_USER_REVIEW')
with (OUT/'FINAL_QA.json').open('x',encoding='utf-8') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
