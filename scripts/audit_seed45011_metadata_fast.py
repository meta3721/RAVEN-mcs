"""Fast actual seed-field membership audit, excludes numeric value tables."""
import subprocess,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_acquisition_45011_20261014'
roots=[str(ROOT),'C:/Users/szr/Desktop/record/1']
rg=os.environ.get('OF_AUDIT_RG',r'C:\Users\szr\.codex\bin\rg.exe')
import shutil
rg=shutil.which('rg') or rg
exclude=['!**/.git/**','!**/.venv*/**','!**/node_modules/**','!**/__pycache__/**','!**/raw/**','!**/data/**','!**/datasets/**',
    '!**/results_observed_feedback_acquisition_45011_20261014/**','!**/site-packages/**']
globs=[]
for g in exclude:globs+=['-g',g]
inventory_file=OUT/'AUDIT_INPUT_INVENTORY.txt'
if inventory_file.exists():inventory=inventory_file.read_text(encoding='utf-8').splitlines()
else:
    inventory=subprocess.run([rg,'--files','--hidden',*globs,*roots],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True).stdout.splitlines()
    inventory_file.write_text('\n'.join(inventory),encoding='utf-8')
named=[p for p in inventory if '45011' in Path(p).name and Path(p).suffix.lower() not in {'.py','.md','.txt'}]
textglobs=[]
for g in ('*.json','*.jsonl','*.yaml','*.yml','*.toml','*.py'):textglobs+=['-g',g]
owned=['!**/scripts/*observed_feedback*acquisition*.py','!**/scripts/*seed45011*.py','!**/raven_mcs_observed_feedback/authorization.py','!**/raven_mcs_observed_feedback/acquisition.py']
for g in owned:globs+=['-g',g]
needles=[]
for field in ('seed','random_seed','acquisition_seed','model_seed','owner_seed','acquisition','model_initialization'):
    for sep in (':',': ','=', '= '):
        for q in ('"',"'",''):
            needles+=['-e',q+field+q+sep+'45011']
r=subprocess.run([rg,'--json','--hidden','--fixed-strings',*globs,*textglobs,*needles,*roots],capture_output=True,text=True,encoding='utf-8',errors='replace')
if r.returncode not in (0,1):raise RuntimeError(r.stderr)
matches=[]
for line in r.stdout.splitlines():
    d=json.loads(line)
    if d['type']=='match':matches.append(dict(path=d['data']['path']['text'],line=d['data']['line_number'],context=d['data']['lines']['text'][:300]))
status='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND' if not named and not matches else 'REVIEW_REQUIRED'
with (OUT/'SEED_REVIEW.json').open('x') as f:json.dump(dict(seed=45011,status=status,inventory_count=len(inventory),named_assets=named,actual_seed_field_matches=matches,
    scope=roots,proposal_documents='Prior MD references are proposed future use, not execution; retain previous report provenance',
    exclusions=exclude+owned,audit_limit='Raw value tables and binary contents excluded; binary filenames and companion metadata seed identities checked; arbitrary unlabelled integers are not seed-use evidence'),f,indent=2)
print(json.dumps(dict(status=status,inventory=len(inventory),matches=len(matches),named=len(named))))
