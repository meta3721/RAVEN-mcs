"""Read-only evidence validation; no solver, training, replay or q fitting."""
import sys,json,math,csv,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--arm',required=True,choices=('fixed05_resume1','fixed2','noqstop'));args=parser.parse_args()
OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015';OUT=BATCH/args.arm
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.utils.hashing import sha256_json
def read(name):return json.loads((OUT/name).read_text())
e=read('EXECUTION_RESULT.json');marker=Path(e['last_complete_marker']);store=PairedCheckpointStore(marker.parent)
identity=json.loads(marker.read_text())['identity'];packet,private=store.read(marker,expected_identity=identity);state=packet['state']
assert sha256_json(state)==packet['state_hash']
for path,h in packet['source_closure'].items():assert hashlib.sha256((ROOT/'src'/path).read_bytes()).hexdigest()==h
freeze=read('ARM_FROZEN_PLAN.json')
assert identity['clock_namespace']==freeze['clock_namespace'] and state['seed']==45001 and state['config']==freeze['config'] and state['settings']==freeze['settings']
assert private['state']['next_clock']==100 if e['status']=='COMPLETE_T100_ACQUISITION' else True
rows=read('MERGED_DECISION_METRICS.json');assert [x['time'] for x in rows]==[round(k*.1,10) for k in range(1,len(rows)+1)]
assert len(rows)==len({x['time'] for x in rows})
with (OUT/'DECISION_METRICS.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
 for row in rows:writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})
assert len(rows)==sum(1 for _ in (OUT/'DECISION_METRICS.jsonl').open())
snapshots={}
for directory in (OUT,):
 for line in (directory/'DECISION_SNAPSHOTS.jsonl').read_text().splitlines():
  x=json.loads(line);assert x['time'] not in snapshots;snapshots[x['time']]=x
assert len(snapshots)==len(rows)
max_residual=0.;max_binding_error=0.;statuses=collections.Counter();solver_kinds=collections.Counter()
for row in rows:
 s=snapshots[row['time']];assert sha256_json(s['snapshot'])==s['fingerprint']==row['snapshot_hash']
 assert row['actual_request_root_upper']<=2.
 pre=row['preview']
 if not pre:continue
 a=pre['alpha'];k=len(a);assert k==len(s['snapshot']['pool']) and all(math.isfinite(x) for x in a)
 violation=max(0.,abs(sum(a)-1),-min(a),max(a)-min(1.,max(.5,1/k)),sum(x*x for x in a)-1/min(3,k));max_residual=max(max_residual,violation);assert violation<=1e-7
 assert pre['keys']==[m['registration']['key'] for m in s['snapshot']['pool']]
 omega=[sum(x*w for x,w in zip(col,a)) for col in pre['M']]
 err=max(abs(x-y) for x,y in zip(omega,pre['omega']));max_binding_error=max(max_binding_error,err);assert err<=1e-10
 ell=.5*sum(abs(x-y) for x,y in zip(omega,s['snapshot']['mu']));assert abs(ell-pre['ell'])<=1e-10
 ages=[(s['snapshot']['model_version']-m['registration']['downloaded_version'])/5 for m in s['snapshot']['pool']];assert abs(sum(x*w for x,w in zip(ages,a))-pre['age'])<=1e-10
 for m in s['snapshot']['pool']:
  assert m['summary']['design_enabled'] and m['q']['role']=='diagnostic_prior' and m['q']['value']==.5
 statuses[pre['solver']['status']]+=1;solver_kinds[str(pre['solver'].get('solver','exact_singleton'))]+=1
closures=read('CLOSURES.json');consumed_keys=[]
for c in closures:
 assert c['configured_design']==c['actual_design']==1 and c['coverage_role']=='diagnostic_only'
 if not c['empty']:consumed_keys.extend(c['preview']['keys'])
assert len(consumed_keys)==len(set(consumed_keys)) and set(consumed_keys)==set(state['consumed'])
labels=read('ATTEMPT_LABELS.json');assert len(labels)==len(state['attempts']);bykey={x['registration']['key']:x for x in labels}
assert len(bykey)==len(labels)
for key,x in bykey.items():
 assert x==state['attempts'][key]
 assert x['registration']['registered_at']==x['q']['frozen_at']
 assert sha256_json(state['private_stage1'][key])==x['stage1_hash']
 if x['consumed']==1:assert key in set(consumed_keys) and x['R']==x['E']==1 and x['physical_outcome']=='completion'
 else:assert key not in set(consumed_keys)
assert sum(x['training_started'] for x in state['backend']['work'].values())==e['actual_SGD']==state['backend']['local_optimizer_steps']
assert state['backend']['local_training_config']==dict(optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01)
assert state['backend']['theta']==state['backend']['versions'][str(state['model_version'])]
def finite_tensor(value):
 if isinstance(value,list):return all(finite_tensor(x) for x in value)
 return isinstance(value,(int,float)) and math.isfinite(value)
for data in state['backend']['theta'].values():assert finite_tensor(data['values'])
full=e['status']=='COMPLETE_T100_ACQUISITION'
if full:
 assert state['backend']['theta']!=json.loads((OLD/'INITIAL_BACKEND.json').read_text())['theta'],'NO_ACTUAL_MODEL_CHANGE'
 assert e['now']==state['now']==100 and state['ended'] and e['next_grid_tick']==private['next_grid_tick']==1001 and len(rows)==1000
 assert private['state']['next_clock']==100 and private['state']['next_client']==0 and private['state']['active_registration'] is None
 assert len(labels)==4300 and all(x['at']>100 for x in private['state']['pending'])
 assert all(x['consumed'] is not None and x['right_censored_at'] is None for x in labels)
 assert all(not x['R'] or x['physical_outcome']!='pending' or (x['physical_service_censored_at']==100. and x['physical_service_censor_reason']=='finite_endpoint') for x in labels)
regular=[x for x in rows if 20<x['time']<100];nonforced=[x for x in regular if not x['shadow']['forced']]
def differences(part,field):
 if any(x['shadow'].get(field) is None for x in part):return None
 return sum(x['action']!=x['shadow'][field] for x in part)
reasons=collections.Counter(x['reason'] for x in regular);labels_reason=collections.Counter(x['terminal_reason'] or 'unmatured' for x in labels)
qualities=collections.Counter()
for row in nonforced:
 comp=row['components']
 if not comp:continue
 stop_kappa=0. if freeze['strategy']=='OF-no-Q-stop' else .10
 assert comp['debt']==stop_kappa*comp['b'],'STOP_RULE_BINDING_MISMATCH'
 assert abs(comp['quality']+comp['debt']+comp['patience']-row['B'])<1e-10
 qualities['positive_debt']+=int(comp['debt']>0);qualities['negative_debt']+=int(comp['debt']<0);qualities['nonzero_debt']+=int(comp['debt']!=0)
 qualities['quality_only_threshold_close']+=int(comp['quality']>=.02+1e-7)
 qualities['quality_plus_patience_threshold_close']+=int(comp['quality']+comp['patience']>=.02+1e-7)
component_rows=[x for x in nonforced if x['components']]
component_ranges={name:dict(minimum=min(x['components'][name] for x in component_rows),maximum=max(x['components'][name] for x in component_rows),mean=sum(x['components'][name] for x in component_rows)/len(component_rows)) for name in ('quality','debt','patience','b','c_minus','c')} if component_rows else {}
G=W=J=None;fallback=0
consumed_delay=[x['terminal_at']-x['registration']['registered_at'] for x in labels if x['consumed']==1]
stats_saves=[json.loads(line) for line in (OUT/'SAVE_MEASUREMENTS.jsonl').read_text().splitlines()]
if full:
 g=[];active=None;j=0
 nonempty=[x for x in closures if not x['empty']]
 for tick in range(201,1001):
  t=round(tick*.1,10)
  while j<len(nonempty) and nonempty[j]['time']<=t+1e-9:active=nonempty[j];j+=1
  g.append(active['preview']['ell'] if active else 1.);fallback+=int(active is None)
 G=sum(g)/800
 post=[x for x in closures if x['time']>20 and x['duration']>0]
 assert post;W=sum(x['duration'] for x in post)/len(post)
 post_nonempty=[x for x in post if not x['empty']]
 if post_nonempty:J=sum(x['preview']['ell']+.02*x['preview']['age']+.20*x['duration']/4 for x in post_nonempty)/len(post_nonempty)
plans=[json.loads(line) for line in (OUT/'ROLLING_COST_PLANS.jsonl').read_text().splitlines()]
records=read('OPERATION_RECORDS.json');enriched=[];previous_count=0;previous_R1=0
for plan in plans:
 current=plan['current'];seg=records[previous_count:current['cost_record_count']];event_records=[x for x in seg if x['category']=='events'];online_records=[x for x in seg if x['category']=='online'];save_records=[x for x in seg if x['category']=='save']
 enriched.append(dict(time=current['time'],registrations=plan['segment']['registrations'],R1=current['R1']-previous_R1,SGD=plan['segment']['SGD'],notices=plan['segment']['notices'],grids=plan['segment']['grid'],
  P2_calculations=sum(x['p2_solves'] for x in rows if current['time']-(plan['segment']['grid']*.1)<x['time']<=current['time']),root_categories=plan['segment']['spent'],
  monitor_CPU=plan['segment']['driver_CPU'],monitor_role='part of root, not additive',operation_wall=sum(x['wall'] for x in seg),
  online_max_upper=max([x['root_upper_CPU'] for x in online_records],default=0.),save_max_upper=max([x['root_upper_CPU'] for x in save_records],default=0.),
  checkpoint_bytes=current['checkpoint_bytes'],private_queue=current['private_queue'],forecast_warning=plan['warning'],proposed_remaining_CPU=plan['proposed_remaining_CPU'],
  actual_registration_branch_counts=plan['segment']['operation_counts']))
 previous_count=current['cost_record_count'];previous_R1=current['R1']
(OUT/'ENRICHED_ROLLING_COST_SEGMENTS.json').write_text(json.dumps(enriched,indent=2))
protected=json.loads((OLD/'PROTECTED_HISTORY.json').read_text());changed=[p for p,h in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not changed
offset=1075 if args.arm=='fixed05_resume1' else 0
assert e['physical_unknown_offset_upper']==offset and e['physical_upper']==e['actual_SGD']+offset
waste=dict(wasted_physical_SGD_lower=0,wasted_physical_SGD_upper=offset);assert e['physical_upper']<=5000
initial=read('ARM_INITIAL_CHECK.json');shared=json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text());assert initial['initial_identity']==shared['initial_identity']
assert state['collection_authorization']['strategy']==freeze['strategy']==state['probability_applicability']['strategy']
assert state['calibration_only'] and not state['isolated_test']
eligible=[x for x in labels if x['R'] and x['E']];cells=collections.Counter((x['features']['model_age'],x['features']['device_class'],x['features']['network_class']) for x in eligible)

from observed_feedback_recovery_common import require_resource_source_identity
require_resource_source_identity()
auth=state['collection_authorization'];assert auth['extension']=='user20261015_pilot_interruption_recovery' and auth['CPU_limit']==4800 and auth['stage_CPU_limit']==1800
assert (OUT/'SESSION_DURABLE.json').exists() and (OUT/'SESSION_DURABLE.json.previous').exists()
durable=json.loads((OUT/'SESSION_DURABLE.json').read_text());assert durable['logical_SGD']==e['actual_SGD'] and durable['next_grid']==1001
if args.arm=='fixed05_resume1':
 equality=json.loads((OUT/'RESUMPTION_CHECK.json').read_text());assert equality['original_state_hash_equal_before_any_SGD_or_events'] and equality['producer_RNG_hash_equal'] and equality['numerical_state_unchanged_by_resource_migration']
 for name,n in [('DECISION_METRICS.jsonl',750),('DECISION_SNAPSHOTS.jsonl',750),('PRIVATE_EXOGENOUS_PAIRING.jsonl',3225)]:
  with (OLD/'fixed05'/name).open('rb') as old,(OUT/name).open('rb') as new:
   assert all(next(old)==next(new) for _ in range(n)),'ORIGINAL_PREFIX_CHANGED'
 assert len(rows)==1000 and len(json.loads((OUT/'SUFFIX_DECISION_METRICS.jsonl').read_text().splitlines()[0]))>0
 # The saved prefix is the only state before75; old lost suffix is never read.
 assert state['clock_namespace']==equality['original_clock']

summary=dict(status='PASS',full_T100=full,effective_stop_rule=freeze['scope']['stop_rule'],actual_model_changed=True,paired_asset_readable=True,recorded_resource_migration_and_source_valid=True,parent_prefix_rows_preserved=750 if args.arm=='fixed05_resume1' else 0,suffix_rows=250 if args.arm=='fixed05_resume1' else len(rows),total_grid_rows=len(rows),
 now=e['now'],logical_SGD=e['actual_SGD'],total_physical_SGD_lower=e['actual_SGD']+waste['wasted_physical_SGD_lower'],total_physical_SGD_upper=e['actual_SGD']+waste['wasted_physical_SGD_upper'],
 registrations=len(labels),R1=sum(x['R'] for x in labels),R0=sum(1-x['R'] for x in labels),E0=sum(1-x['E'] for x in labels),eligible_R1_E1=len(eligible),consumed=len(consumed_keys),unmatured=sum(x['consumed'] is None for x in labels),
 physical_pending_R1=sum(bool(x['R']) and x['physical_outcome']=='pending' for x in labels),label_terminal_reasons=dict(labels_reason),
 closures=len(closures),empty_closures=sum(x['empty'] for x in closures),post20_closures=sum(x['time']>20 for x in closures),
 model_version=state['model_version'],regular_grid_rows=len(regular),nonforced_rows=len(nonforced),regular_reason_counts=dict(reasons),
 no_Q_difference=differences(regular,'no_Q_stop'),fixed_0_5_difference=differences(regular,'fixed_time_0_5'),fixed_2_difference=differences(regular,'fixed_time_2'),
 nonforced_no_Q_difference=differences(nonforced,'no_Q_stop'),legal_both_actions=sum(not x['shadow']['forced'] for x in regular),debt_terms=dict(qualities),component_ranges=component_ranges,
 G_800=G,G_fallback_count=fallback,W_mean_post20_including_empty=W,J_mean_nonempty_post20=J,
 P2_calculations=sum(x['p2_solves'] for x in rows),cache_hits=sum(x['cache_hits'] for x in rows),preview_status_counts=dict(statuses),solver_kind_counts=dict(solver_kinds),
 max_weight_residual=max_residual,max_binding_error=max_binding_error,max_actual_request_root_upper=max(x['actual_request_root_upper'] for x in rows),
 consumed_delay_mean=sum(consumed_delay)/len(consumed_delay) if consumed_delay else None,consumed_delay_max=max(consumed_delay,default=None),
 max_public_F_at_registration=max(x['public_encoding']['raw_F_count'] for x in labels),encoding_missing=sum(x['public_encoding']['support']=='ENCODING_DOMAIN_OR_RESOURCE_MISSING' for x in eligible),
 eligible_feature_cells=[dict(age=k[0],device=k[1],network=k[2],count=n) for k,n in sorted(cells.items())],
 final_checkpoint_sizes=json.loads(marker.read_text())['sizes'],max_save_upper=max(x['measured_max_root_upper'] for x in stats_saves),final_save_reserve=stats_saves[-1]['total_reserve'],
 final_complete_marker=str(marker),protected_assets_checked=len(protected),changed_history=changed,root_publication_partial_attempts='old fixed05 final PID/CPU unavailable; this recovery session has independent final audit' if args.arm=='fixed05_resume1' else 'none in this arm',strategy=freeze['strategy'],method=freeze['method'],seed=45001,q_role='diagnostic_prior_not_calibrated',configuration=freeze,initial_identity=initial['initial_identity'],
 evidence_roles=dict(q='diagnostic_prior_not_calibrated',shadows='same_state_actions_only_no_independent_model',performance='PREDICTION_RESULTS_NOT_REVALIDATED_SINGLE_SEED_CONTROL_PILOT_ONLY',state='WAITING_USER_REVIEW'))
(OUT/'VALIDATION_AND_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:summary[k] for k in ['status','strategy','full_T100','now','logical_SGD','total_physical_SGD_upper','G_800','W_mean_post20_including_empty','max_actual_request_root_upper']}))
