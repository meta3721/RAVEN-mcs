"""Read-only endpoint validation. Reuses the original G/W/J block verbatim."""
import ast, collections, csv, hashlib, json, math, pathlib, sys, traceback, ctypes
k32=ctypes.WinDLL('kernel32',use_last_error=True);k32.GetCurrentProcess.restype=ctypes.c_void_p;k32.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint]
if not k32.SetPriorityClass(k32.GetCurrentProcess(),0x4000):raise ctypes.WinError(ctypes.get_last_error())
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=pathlib.Path(__file__).resolve().parent;ARM=OUT/'gap'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.utils.hashing import sha256_json
from observed_feedback_recovery_io import durable_json,file_hash

def read(n):return json.loads((ARM/n).read_text(encoding='utf-8-sig'))
def rows(n):
 with (ARM/n).open() as f:
  for l in f:yield json.loads(l)
def main():
 result=dict(status='FAIL',new_training=0,new_inference=0,new_solver_calls=0,new_statistics_tests=0)
 try:
  e=read('EXECUTION_RESULT.json');full=e['status']=='COMPLETE_T100_ACQUISITION'
  if not full:
   result.update(status='INCOMPLETE_PREFIX_NOT_SCIENTIFIC_FAILURE',execution=e);durable_json(OUT/'C_VALIDATION.json',result);return 2
  marker=pathlib.Path(e['last_complete_marker']);identity=json.loads(marker.read_text(encoding='utf-8-sig'))['identity']
  packet,private=PairedCheckpointStore(marker.parent).read(marker,expected_identity=identity);s=packet['state'];freeze=read('ARM_FROZEN_PLAN.json')
  assert sha256_json(s)==packet['state_hash']
  assert s['now']==100. and s['ended'] and private['next_grid_tick']==1001
  assert s['seed']==45001 and s['calibration_only'] and not s['isolated_test']
  assert s['probability_applicability']==freeze['scope'] and s['clock_namespace']==freeze['clock_namespace']==identity['clock_namespace']
  assert s['config']==freeze['config'] and s['settings']==freeze['settings']
  assert s['collection_authorization']==freeze['branch']['authorization']
  assert private['c_ref']==freeze['c_ref']
  for p,h in packet['source_closure'].items():assert file_hash(ROOT/'src'/p)==h
  for p,h in freeze['local_source_hashes'].items():assert file_hash(OUT/p)==h
  assert s['backend']['local_training_config']==dict(optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01)
  assert s['backend']['theta']==s['backend']['versions'][str(s['model_version'])]
  initial=json.loads((ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014/INITIAL_BACKEND.json').read_text(encoding='utf-8-sig'))
  assert s['backend']['theta']!=initial['theta'],'NO_ACTUAL_MODEL_CHANGE'
  del initial
  assert e['actual_new_SGD']==s['backend']['local_optimizer_steps']-e['parent_SGD']<=5000
  assert sum(x['training_started'] for x in s['backend']['work'].values())==s['backend']['local_optimizer_steps']
  assert private['state']['next_clock']==100 and private['state']['next_client']==0 and private['state']['active_registration'] is None
  assert all(x['at']>100 for x in private['state']['pending'])
  counts=collections.Counter();max_residual=0.;max_binding=0.;max_root=0.;regular=free=difference=0;new_free=0;first=None
  for tick,(m,n) in enumerate(zip(rows('DECISION_METRICS.jsonl'),rows('DECISION_SNAPSHOTS.jsonl')),1):
   assert m['time']==n['time']==round(tick*.1,10)
   assert sha256_json(n['snapshot'])==n['fingerprint']==m['snapshot_hash']
   assert m['actual_request_root_upper']<=2.;max_root=max(max_root,m['actual_request_root_upper'])
   if first is None:first=m
   p=m['preview'];ss=n['snapshot']
   if p:
    a=p['alpha'];k=len(a);assert k==len(ss['pool']) and all(math.isfinite(x) for x in a)
    residual=max(0,abs(sum(a)-1),-min(a),max(a)-min(1,max(.5,1/k)),sum(x*x for x in a)-1/min(3,k));assert residual<=1e-7;max_residual=max(max_residual,residual)
    assert p['keys']==[x['registration']['key'] for x in ss['pool']]
    omega=[sum(x*y for x,y in zip(v,a)) for v in p['M']];err=max(abs(x-y) for x,y in zip(omega,p['omega']));assert err<=1e-10;max_binding=max(max_binding,err)
    assert abs(p['ell']-.5*sum(abs(x-y) for x,y in zip(omega,ss['mu'])))<1e-10
    ages=[(ss['model_version']-x['registration']['downloaded_version'])/5 for x in ss['pool']]
    assert abs(sum(x*y for x,y in zip(ages,a))-p['age'])<1e-10
   if 20<m['time']<100:
    regular+=1;counts[m['reason']]+=1
    if not m['shadow']['forced']:
     free+=1;c=m['components'];assert c['c_minus']==freeze['c_ref'] and c['debt']==0
     assert abs(m['B']-(freeze['c_ref']-p['ell']-.02*p['age']+.2*min(1,max(0,(m['time']-ss['window_open'])/4))))<1e-12
     difference+=m['action']!=m['shadow']['dynamic_reference_noQ']
  assert tick==1000 and regular==799
  closures=read('CLOSURES.json');assert closures==s['closures']
  consumed=[]
  for c in closures:
   assert c['configured_design']==c['actual_design']==1 and c['coverage_role']=='diagnostic_only'
   if not c['empty']:consumed.extend(c['preview']['keys'])
  assert len(consumed)==len(set(consumed)) and set(consumed)==set(s['consumed'])
  attempts=s['attempts'];assert len(attempts)==4300
  outcomes=collections.Counter();regns=collections.Counter();delays=[];new_identity=old_identity=0
  for key,x in attempts.items():
   assert x['consumed'] is not None and x['right_censored_at'] is None
   assert x['registration']['registered_at']==x['q']['frozen_at']
   assert sha256_json(s['private_stage1'][key])==x['stage1_hash']
   assert sha256_json(x['features'])==x['q']['feature_hash']
   if x['R'] and x['E']:assert x['q']['value']==.5 and x['q']['role']=='diagnostic_prior'
   if x['registration']['registered_at']>20:
    assert x['features']['clock_run_id']==s['clock_namespace']['run_id'];new_identity+=1
   else:assert x['features']['clock_run_id']==freeze['branch']['parent_identity']['clock_namespace']['run_id'];old_identity+=1
   if x['consumed']==1:
    assert key in set(consumed) and x['R']==x['E']==1 and x['physical_outcome']=='completion';delays.append(x['terminal_at']-x['registration']['registered_at'])
   if x['R'] and x['physical_outcome']=='pending':assert x['physical_service_censored_at']==100 and x['physical_service_censor_reason']=='finite_endpoint'
   outcomes[x['terminal_reason']]+=1;regns['R1']+=x['R'];regns['R0']+=not x['R'];regns['E0']+=not x['E'];regns['R1E1']+=bool(x['R'] and x['E'])
  def finite(v):
   if isinstance(v,list):return all(finite(x) for x in v)
   return isinstance(v,(int,float)) and math.isfinite(v)
  assert all(finite(v['values']) for v in s['backend']['theta'].values())
  # Execute the existing accepted metric code without rewriting its arithmetic.
  metric_path=ROOT/'scripts/verify_observed_feedback_recovery_arm_v2.py';text=metric_path.read_text(encoding='utf-8-sig');tree=ast.parse(text)
  block=next(n for n in tree.body if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='full' and any(isinstance(z,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='g' for t in z.targets) for z in n.body))
  metric_text=ast.get_source_segment(text,block);env=dict(full=True,closures=closures,fallback=0,G=None,W=None,J=None)
  exec(compile(ast.Module(body=[block],type_ignores=[]),str(metric_path),'exec'),env)
  records=read('OPERATION_RECORDS.json');actual_p2=sum(m['p2_solves'] for m in rows('DECISION_METRICS.jsonl') if m['time']>20)
  cache_hits=sum(m['cache_hits'] for m in rows('DECISION_METRICS.jsonl') if m['time']>20)
  full_trace_solves=sum(m['p2_solves'] for m in rows('DECISION_METRICS.jsonl'))
  full_trace_cache=sum(m['cache_hits'] for m in rows('DECISION_METRICS.jsonl'))
  result.update(status='PASS',strategy='GAP20-fixed-reference',full_T100=True,now=100.,seed=45001,G=env['G'],W=env['W'],J=env['J'],G_denominator=800,G_fallback_count=env['fallback'],W_denominator=len(env['post']),J_denominator=len(env['post_nonempty']),
   total_grids=tick,regular_grids=regular,free_grids=free,forced_grids=799-free,reason_counts=dict(counts),dynamic_reference_shadow_differences_on_GAP_states=difference,
   logical_SGD=s['backend']['local_optimizer_steps'],actual_new_SGD=e['actual_new_SGD'],parent_SGD=e['parent_SGD'],registrations=len(attempts),registration_counts=dict(regns),consumed=len(consumed),terminal_reasons=dict(outcomes),
   closures=len(closures),empty_closures=sum(c['empty'] for c in closures),model_version=s['model_version'],new_scope_registrations=new_identity,old_scope_registrations=old_identity,
   P2_new_solves=actual_p2,cache_hits=cache_hits,P2_full_trace_solves=full_trace_solves,full_trace_cache_hits=full_trace_cache,max_weight_residual=max_residual,max_composition_binding_error=max_binding,max_actual_request_root_upper=max_root,
   consumption_delay_mean=sum(delays)/len(delays),consumption_delay_max=max(delays),finite_model=True,actual_model_changed=True,paired_checkpoint=str(marker),final_pair_readable=True,
   metric_code_source=str(metric_path),metric_code_lines=[block.lineno,block.end_lineno],metric_code_hash=hashlib.sha256(metric_text.encode()).hexdigest(),full_P3=False,paper_modified=False)
  (OUT/'REUSED_GWJ_METRIC_BLOCK.txt').write_text(metric_text,encoding='utf-8')
 except Exception as exc:result.update(error=repr(exc),traceback=traceback.format_exc())
 durable_json(OUT/'C_VALIDATION.json',result);print(json.dumps(result,ensure_ascii=False))
 return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
