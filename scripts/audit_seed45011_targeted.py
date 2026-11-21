"""Bounded identity audit; reuses the already enumerated inventory, not log bodies."""
import csv,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'results_observed_feedback_acquisition_45011_20261014'
OUT=ROOT/'results_observed_feedback_continuation_45011_20261014'
started=time.process_time()
inventory=(OLD/'AUDIT_INPUT_INVENTORY.txt').read_text(encoding='utf-8').splitlines()
roots=[ROOT,Path('C:/Users/szr/Desktop/record/1/results_reachability_stopping_v1'),ROOT/'ccf-review-report',ROOT/'ccfa-review-reports',Path('C:/Users/szr/Desktop/record/1/ccfa-review-reports')]
name=re.compile(r'(config|manifest|freeze|frozen|seed|execution|result|summary|plan|authorization|run[_-]|readiness|acquisition_request)',re.I)
skip=re.compile(r'(protected|source.closure|hash|inventory|model|prediction|decision|timeline|cost.records|root.budget|charge_|budget)',re.I)
fields=re.compile(r'(seed|random.stream|run_id|method|dataset|role|status|source|actual.*(SGD|train|traject|initial)|^SGD$|local_optimizer_steps)',re.I)
selected=[];omissions=[];records=[];matches=[];documents=[];unresolved=[]
for raw in inventory:
 p=Path(raw)
 if not any(p.is_relative_to(r) for r in roots):continue
 if p.is_relative_to(ROOT) and not (p.parts[len(ROOT.parts)].startswith('results') or p.is_relative_to(ROOT/'ccf-review-report') or p.is_relative_to(ROOT/'ccfa-review-reports')):continue
 if p.suffix.lower() not in {'.json','.yaml','.yml','.toml','.csv','.md'} or not name.search(p.name) or skip.search(p.name):continue
 if not p.exists():omissions.append(dict(path=str(p),reason='no_longer_accessible'));continue
 if p.stat().st_size>1048576:omissions.append(dict(path=str(p),reason='large_identity_candidate_not_read',bytes=p.stat().st_size));continue
 selected.append(p)
(OUT/'AUDIT_SCOPE.json').write_text(json.dumps(dict(inventory_source=str(OLD/'AUDIT_INPUT_INVENTORY.txt'),inventory_reused=True,roots=[str(r) for r in roots],fields=fields.pattern,selected=[str(p) for p in selected],omissions=omissions,excluded='tensors, source/hash inventories, row predictions/decisions/timelines, logs; source code is authorization, not execution identity'),indent=2))
def extract(obj,prefix='',depth=0):
 result={}
 if depth>8:return result
 if isinstance(obj,dict):
  for k,v in obj.items():
   key=prefix+'.'+str(k)
   if fields.search(str(k)) and (not isinstance(v,(dict,list)) or 'seed' in str(k).lower() or 'stream' in str(k).lower()):result[key]=v
   elif isinstance(v,(dict,list)) and len(v)<300:result.update(extract(v,key,depth+1))
 elif isinstance(obj,list) and len(obj)<300:
  for n,v in enumerate(obj):result.update(extract(v,prefix+'.'+str(n),depth+1))
 return result
def has_seed(v):
 if isinstance(v,(list,dict)):return any(has_seed(x) for x in (v.values() if isinstance(v,dict) else v))
 return v==45011 or str(v).strip()=='45011'
for p in selected:
 if time.process_time()-started>54:raise RuntimeError('AUDIT_CPU_INTERNAL_HEADROOM_STOP')
 try:
  if p.suffix.lower()=='.json':identity=extract(json.loads(p.read_text(encoding='utf-8-sig')))
  elif p.suffix.lower()=='.csv':
   with p.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);keys=[k for k in (reader.fieldnames or []) if fields.search(k)]
    identity={'rows':[{k:row[k] for k in keys} for row in reader]} if keys else {}
  else:
   lines=[dict(line=n+1,text=line[:1200]) for n,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines()) if re.search(r'(?<![\da-f])45011(?![\da-f])',line,re.I)]
   if lines:documents.append(dict(path=str(p),mentions=lines,classification='document_proposed_authorization_or_current_SGD0; cross_checked_against_execution_identity'))
   continue
  records.append(dict(path=str(p),identity=identity))
  seed_fields={k:v for k,v in identity.items() if 'seed' in k.lower() and has_seed(v)}
  if identity.get('rows'):
   seed_fields={'rows':[r for r in identity['rows'] if any('seed' in k.lower() and has_seed(v) for k,v in r.items())]}
   if not seed_fields['rows']:seed_fields={}
  if not seed_fields:continue
  current=p.is_relative_to(OLD)
  if current:
   classification='current_authorization_or_NOT_STARTED_or_SGD0_fixture'
   text=json.dumps(identity)
   if 'actual_45011_trajectory_started' in text and any(v is True for k,v in identity.items() if 'actual_45011_trajectory_started' in k):unresolved.append(str(p))
  else:
   classification='prior_identity_requires_review';unresolved.append(str(p))
  matches.append(dict(path=str(p),seed_fields=seed_fields,classification=classification,identity=identity))
 except (ValueError,UnicodeError) as exc:omissions.append(dict(path=str(p),reason='parse_error',error=repr(exc)));unresolved.append(str(p))
missing_roots=[str(r) for r in roots if not r.exists()]
uncertain=[x for x in omissions if '45011' in x['path']]
unresolved+= [x['path'] for x in uncertain]
status='REVIEW_REQUIRED' if unresolved or missing_roots else 'NO_PRIOR_SELECTION_OR_EXECUTION_FOUND'
value=dict(seed=45011,status=status,conclusion='Within the listed accessible identity records, no prior actual execution/fitting/selection conflict found' if status.startswith('NO_') else 'Unresolved identity records; no seed clearance',scope=[str(r) for r in roots],inventory_count=len(inventory),identity_assets=len(records),matches=matches,document_mentions=documents,unresolved=unresolved,missing_roots=missing_roots,omissions=omissions,not_accessed=['arbitrary external history','binary tensor contents','full logs/decisions/prediction rows','protocol proposals outside execution/report roots'],CPU_local=time.process_time()-started,current_run='NOT_STARTED; deterministic SGD0 fixture is not independent cost trajectory')
(OUT/'IDENTITY_RECORDS.json').write_text(json.dumps(records,indent=2))
(OUT/'SEED_REVIEW.json').write_text(json.dumps(value,indent=2));print(json.dumps(dict(status=status,identities=len(records),matches=len(matches),unresolved=unresolved,omissions=len(omissions),CPU=value['CPU_local'])))
if unresolved or missing_roots:raise SystemExit(2)
