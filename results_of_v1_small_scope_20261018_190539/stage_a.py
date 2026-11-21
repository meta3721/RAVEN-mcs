"""A: read-only, streaming fixed-state action comparison; no model imports."""
import ctypes, csv, datetime, hashlib, json, math, pathlib, statistics, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=pathlib.Path(__file__).resolve().parent
REPORT=ROOT/'ccf-review-report'/OUT.name.replace('results_','',1)
REPORT.mkdir(exist_ok=True)
OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
paths=dict(of=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1',noqstop=OLD/'noqstop',fixed05=OLD/'fixed05_resume1',fixed2=OLD/'fixed2_resume1')
def load(p):
 with p.open(encoding='utf-8-sig') as f:return json.load(f)
def save(n,x): (OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
def rows(p):
 with p.open(encoding='utf-8-sig') as f:
  for line in f:yield json.loads(line)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
summaries={k:load(p/'VALIDATION_AND_SUMMARY.json') for k,p in paths.items()}
for k,s in summaries.items():
 assert s['status']=='PASS' and s['full_T100'] and s['now']==100 and s['total_grid_rows']==1000,(k,'invalid endpoint')
 assert pathlib.Path(s['final_complete_marker']).exists(),(k,'missing paired marker')
 assert s['G_fallback_count']==0
for k,g,w in [('of',.9452180232558112,.6015037593984962),('noqstop',.9452180232558112,.6015037593984962),('fixed05',.9588590116279057,.5063291139240507),('fixed2',.8430825786217807,2.)]:
 assert summaries[k]['G_800']==g and summaries[k]['W_mean_post20_including_empty']==w
closures={k:load(paths[k]/'CLOSURES.json') for k in ('of','noqstop')}
warm={k:[c for c in cs if c['time']<=20] for k,cs in closures.items()}
assert len(warm['of'])==len(warm['noqstop'])==20
for a,b in zip(warm['of'],warm['noqstop']):
 for k in ('time','duration','empty','version','reason','configured_design','actual_design','coverage_role'):assert a[k]==b[k],('warmup',k)
 for k in ('keys','alpha','beta','masses','M','omega','ell','age'):assert a['preview'][k]==b['preview'][k],('warmup preview',k)
last=[c for c in warm['noqstop'] if not c['empty']][-1]
cref=last['preview']['ell']+.02*last['preview']['age']
freeze=dict(strategy='GAP20-fixed-reference',seed=45001,T=100,q=.5,q_role='diagnostic_prior_not_calibrated',calibration_only=True,c_ref=cref,
 reference_time=last['time'],reference_ell=last['preview']['ell'],reference_age=last['preview']['age'],reference_source=str(paths['noqstop']/'CLOSURES.json'),
 frozen_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),threshold=.02+1e-7,formula='c_ref - (preview.ell + .02*preview.age) + .20*clip(elapsed/4,0,1)',
 scientific_change='dynamic last-release reference replaced by fixed warmup reference; stop kappa=0; full P2 Q unchanged',
 instruction='C:/Users/szr/Desktop/record/1/ccfa-review-reports/OF-v1-small-scope-validation-instructions.md',CPU_limit=1000,wall_limit=5400,GPU=0,new_SGD_limit=5000,new_autonomous_arms_limit=1)
if (OUT/'FREEZE.json').exists():
 old=load(OUT/'FREEZE.json');assert old['c_ref']==cref and old['formula']==freeze['formula'];freeze=old
else:save('FREEZE.json',freeze) # Freeze from warmup BEFORE examining post-20 actions.
snapshot_streams={k:rows(paths[k]/'DECISION_SNAPSHOTS.jsonl') for k in ('of','noqstop')}
metrics={k:rows(paths[k]/'DECISION_METRICS.jsonl') for k in ('of','noqstop')}
result=[]; free=[]; max_omega=0; max_c_error=0; warmup_identity={}
for tick,(om,nm,os,ns) in enumerate(zip(metrics['of'],metrics['noqstop'],snapshot_streams['of'],snapshot_streams['noqstop']),1):
 t=round(tick/10,1); assert all(x['time']==t for x in (om,nm,os,ns))
 if tick==201:
  a=os['snapshot']; b=ns['snapshot']
  for k in ('now','window_open','model_version','revision','config','settings','mu','debt','last_release','variance','seed','experiment_end','isolated_test','calibration_only','service_parameters_hash','q_model_version'):
   assert a[k]==b[k],('warmup scientific state',k)
  excluded_q_hashes=[]
  for collection in ('pool','in_flight'):
   assert len(a[collection])==len(b[collection])
   for i,(aa,bb) in enumerate(zip(a[collection],b[collection])):
    aa=json.loads(json.dumps(aa));bb=json.loads(json.dumps(bb))
    ah=aa['q'].pop('feature_hash');bh=bb['q'].pop('feature_hash')
    assert aa==bb,('warmup scientific message',collection,i)
    if ah!=bh:excluded_q_hashes.append(collection+'/'+str(i)+'/q/feature_hash')
  assert a['last_release']['time']==last['time']
  warmup_identity=dict(scientific_fields_equal=True,probability_applicability_equal=a['probability_applicability']==b['probability_applicability'],clock_namespace_equal=a['clock_namespace']==b['clock_namespace'],
   of_scope_strategy=a['probability_applicability'].get('strategy'),noq_scope_strategy=b['probability_applicability'].get('strategy'),model_version=a['model_version'],strategy_dependent_q_feature_hash_paths=excluded_q_hashes)
 if not 20<t<100:continue
 assert om['action']==nm['action']
 assert os['snapshot']['debt']==ns['snapshot']['debt']
 assert om['model_version_after']==nm['model_version_after']
 forced=nm['shadow']['forced']; row=dict(time=t,window=nm['window'],original_action=nm['action'],shadow_action=nm['action'],forced=forced,reason=nm['reason'],c_minus=None,c_ref=cref,c_t=None,patience=None,B_gap=None,threshold=.0200001,reference_difference=None,different=False)
 if not forced:
  p=nm['preview']; assert p and len(p['keys'])>=3
  assert p['alpha']==om['preview']['alpha'] and p['omega']==om['preview']['omega']
  elapsed=t-ns['snapshot']['window_open']; patience=.2*max(0,min(elapsed/4,1)); ct=p['ell']+.02*p['age']
  cm=ns['snapshot']['last_release']['ell']+.02*ns['snapshot']['last_release']['age']
  assert math.isclose(patience,nm['components']['patience'],abs_tol=1e-12)
  assert math.isclose(cm,nm['components']['c_minus'],abs_tol=1e-12)
  max_c_error=max(max_c_error,abs(ct-nm['components']['c']))
  assert abs(nm['B']-(cm-ct+patience))<1e-12
  for m,w in zip(p['M'],p['omega']):max_omega=max(max_omega,abs(sum(v*a for v,a in zip(m,p['alpha']))-w))
  bg=cref-ct+patience; action='CLOSE' if bg>=.0200001 else 'WAIT'
  row.update(shadow_action=action,c_minus=cm,c_t=ct,patience=patience,B_gap=bg,reference_difference=cm-cref,different=action!=nm['action'])
  free.append(row)
 result.append(row)
assert tick==1000 and len(result)==799 and len(free)==582
assert max_c_error<1e-12 and max_omega<1e-12
diff=[r for r in result if r['different']];selected=diff[:2]+sorted(diff[2:],key=lambda r:(-abs(r['reference_difference']),r['time']))[:3]
values=sorted(r['reference_difference'] for r in free)
def percentile(q):
 pos=(len(values)-1)*q; lo=int(pos);return values[lo]+(values[min(lo+1,len(values)-1)]-values[lo])*(pos-lo)
out=dict(stage='A',status='PASS' if len(diff)>=40 else 'LOW_OBSERVED_L_LEVERAGE',c_ref=cref,total_regular_grids=799,free_grids=len(free),forced_grids=799-len(free),
 differences=len(diff),fraction_all=len(diff)/799,fraction_free=len(diff)/len(free),different_windows=len({r['window'] for r in diff}),
 CLOSE_to_WAIT=sum(r['original_action']=='CLOSE' for r in diff),WAIT_to_CLOSE=sum(r['original_action']=='WAIT' for r in diff),
 reference_difference=dict(min=min(values),p05=percentile(.05),p25=percentile(.25),median=percentile(.5),p75=percentile(.75),p95=percentile(.95),max=max(values),mean=statistics.mean(values)),
 representative_cases=selected,warmup=warmup_identity,warmup_closures_equal=20,max_composition_binding_error=max_omega,max_current_cost_error=max_c_error,new_SGD=0,new_GPU=0,new_q_fit=0,new_autonomous_replay=0,
 legal_t20_marker=str(paths['noqstop']/'trajectory/tick0200.complete.json'),
 input_hashes={str(paths[k]/n):sha(paths[k]/n) for k in ('of','noqstop') for n in ('CLOSURES.json','DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','VALIDATION_AND_SUMMARY.json')})
assert pathlib.Path(out['legal_t20_marker']).exists()
save('A_RESULT.json',out)
with (OUT/'A_PER_GRID.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
save('OLD_SUMMARY_SCALARS.json',{k:{f:v for f,v in s.items() if isinstance(v,(int,float,bool)) or f in ('label_terminal_reasons','final_complete_marker','q_role','strategy')} for k,s in summaries.items()})
print(json.dumps(out,ensure_ascii=False))
