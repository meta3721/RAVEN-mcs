"""Read-only evidence validation; no solver, training, replay or q fitting."""
import sys,json,math,csv,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2';PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs.utils.hashing import sha256_json
def read(name):return json.loads((OUT/name).read_text())
e=read('EXECUTION_RESULT.json');marker=Path(e['last_complete_marker']);store=PairedCheckpointStore(marker.parent)
identity=json.loads(marker.read_text())['identity'];packet,private=store.read(marker,expected_identity=identity);state=packet['state']
assert sha256_json(state)==packet['state_hash']
for path,h in packet['source_closure'].items():assert hashlib.sha256((ROOT/'src'/path).read_bytes()).hexdigest()==h
freeze=json.loads((PARENT/'ACQUISITION_FROZEN_PLAN.json').read_text())
assert identity['clock_namespace']==freeze['clock_namespace'] and state['seed']==45011 and state['config']==freeze['config'] and state['settings']==freeze['settings']
assert private['state']['next_clock']==100 if e['status']=='COMPLETE_T100_ACQUISITION' else True
rows=read('MERGED_DECISION_METRICS.json');assert [x['time'] for x in rows]==[round(k*.1,10) for k in range(1,len(rows)+1)]
assert len(rows)==len({x['time'] for x in rows})
with (OUT/'DECISION_METRICS.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
 for row in rows:writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})
prefix=[json.loads(x) for x in (PARENT/'DECISION_METRICS.jsonl').read_text().splitlines()];assert rows[:10]==prefix and len(rows)-10==sum(1 for _ in (OUT/'DECISION_METRICS.jsonl').open())
snapshots={}
for directory in (PARENT,OUT):
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
 assert e['now']==state['now']==100 and state['ended'] and e['next_grid_tick']==private['next_grid_tick']==1001 and len(rows)==1000
 assert private['state']['next_clock']==100 and private['state']['next_client']==0 and private['state']['active_registration'] is None
 assert len(labels)==4300 and all(x['at']>100 for x in private['state']['pending'])
 assert all(x['consumed'] is not None and x['right_censored_at'] is None for x in labels)
 assert all(not x['R'] or x['physical_outcome']!='pending' or (x['physical_service_censored_at']==100. and x['physical_service_censor_reason']=='finite_endpoint') for x in labels)
regular=[x for x in rows if 20<x['time']<100];nonforced=[x for x in regular if not x['shadow']['forced']]
def differences(part,field):return sum(x['action']!=x['shadow'][field] for x in part)
reasons=collections.Counter(x['reason'] for x in regular);labels_reason=collections.Counter(x['terminal_reason'] or 'unmatured' for x in labels)
qualities=collections.Counter()
for row in nonforced:
 comp=row['components'];assert abs(comp['quality']+comp['debt']+comp['patience']-row['B'])<1e-10
 qualities['positive_debt']+=int(comp['debt']>0);qualities['negative_debt']+=int(comp['debt']<0);qualities['nonzero_debt']+=int(comp['debt']!=0)
 qualities['quality_only_threshold_close']+=int(comp['quality']>=.02+1e-7)
 qualities['quality_plus_patience_threshold_close']+=int(comp['quality']+comp['patience']>=.02+1e-7)
component_ranges={name:dict(minimum=min(x['components'][name] for x in nonforced),maximum=max(x['components'][name] for x in nonforced),mean=sum(x['components'][name] for x in nonforced)/len(nonforced)) for name in ('quality','debt','patience','b','c_minus','c')} if nonforced else {}
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
records=read('OPERATION_RECORDS.json');enriched=[];previous_count=0;previous_R1=32
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
protected=json.loads((ROOT/'results_observed_feedback_rolling_45011_20261014_s1/PROTECTED_BEFORE.json').read_text())
for path,h in read('PROTECTED_BEFORE.json').items():
 if path in protected:assert protected[path]==h
 protected[path]=h
changed=[path for path,h in protected.items() if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=h];assert not changed
waste=json.loads((ROOT/'results_observed_feedback_rolling_45011_20261014_s1/INTERRUPTION_BOUND.json').read_text());assert e['actual_SGD']+waste['wasted_physical_SGD_upper']<=5000
eligible=[x for x in labels if x['R'] and x['E']];cells=collections.Counter((x['features']['model_age'],x['features']['device_class'],x['features']['network_class']) for x in eligible)
summary=dict(status='PASS',full_T100=full,paired_asset_readable=True,source_packages_unchanged=True,parent_prefix_rows_preserved=10,suffix_rows=len(rows)-10,total_grid_rows=len(rows),
 now=e['now'],logical_SGD=e['actual_SGD'],total_physical_SGD_lower=e['actual_SGD']+waste['wasted_physical_SGD_lower'],total_physical_SGD_upper=e['actual_SGD']+waste['wasted_physical_SGD_upper'],
 registrations=len(labels),R1=sum(x['R'] for x in labels),R0=sum(1-x['R'] for x in labels),E0=sum(1-x['E'] for x in labels),eligible_R1_E1=len(eligible),consumed=len(consumed_keys),unmatured=sum(x['consumed'] is None for x in labels),
 physical_pending_R1=sum(bool(x['R']) and x['physical_outcome']=='pending' for x in labels),label_terminal_reasons=dict(labels_reason),
 closures=len(closures),empty_closures=sum(x['empty'] for x in closures),post20_closures=sum(x['time']>20 for x in closures),
 model_version=state['model_version'],regular_grid_rows=len(regular),nonforced_rows=len(nonforced),regular_reason_counts=dict(reasons),
 no_Q_difference=differences(regular,'no_Q_stop'),fixed_0_5_difference=differences(regular,'fixed_time_0_5'),fixed_2_difference=differences(regular,'fixed_time_2'),
 nonforced_no_Q_difference=differences(nonforced,'no_Q_stop'),legal_both_actions=sum(len(x['shadow']['legal_actions'])==2 for x in regular),debt_terms=dict(qualities),component_ranges=component_ranges,
 G_800=G,G_fallback_count=fallback,W_mean_post20_including_empty=W,J_mean_nonempty_post20=J,
 P2_calculations=sum(x['p2_solves'] for x in rows),cache_hits=sum(x['cache_hits'] for x in rows),preview_status_counts=dict(statuses),solver_kind_counts=dict(solver_kinds),
 max_weight_residual=max_residual,max_binding_error=max_binding_error,max_actual_request_root_upper=max(x['actual_request_root_upper'] for x in rows),
 consumed_delay_mean=sum(consumed_delay)/len(consumed_delay) if consumed_delay else None,consumed_delay_max=max(consumed_delay,default=None),
 max_public_F_at_registration=max(x['public_encoding']['raw_F_count'] for x in labels),encoding_missing=sum(x['public_encoding']['support']=='ENCODING_DOMAIN_OR_RESOURCE_MISSING' for x in eligible),
 eligible_feature_cells=[dict(age=k[0],device=k[1],network=k[2],count=n) for k,n in sorted(cells.items())],
 final_checkpoint_sizes=json.loads(marker.read_text())['sizes'],max_save_upper=max(x['measured_max_root_upper'] for x in stats_saves),final_save_reserve=stats_saves[-1]['total_reserve'],
 final_complete_marker=str(marker),protected_assets_checked=len(protected),changed_history=changed,root_publication_partial_attempts='S1 preserved, not merged into final causal grid; SGD/cost accounted separately',
 evidence_roles=dict(q='diagnostic_prior_not_calibrated',shadows='same_state_actions_only_no_independent_model',performance='RESULTS_NOT_REVALIDATED',state='WAITING_USER_REVIEW'))
(OUT/'VALIDATION_AND_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
