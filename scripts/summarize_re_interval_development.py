"""Frozen C statistics and final evidence checks; no fitting or extra trajectory."""
from pathlib import Path
from collections import Counter,defaultdict
import ast,csv,json
import sys
import numpy as np
from re_interval_development_budget import ROOT,OUT
from raven_mcs.utils.hashing import sha256_file,sha256_json
from raven_mcs.control.persistence import source_inventory,exclusive_json
from raven_mcs_re_interval.persistence import source_identity

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def stats(values):
    if not values:return dict(n=0,median=None,p90=None,p95=None,p99=None,max=None,sum=0)
    a=np.asarray(values);return dict(n=len(a),median=float(np.median(a)),p90=float(np.quantile(a,.9)),
        p95=float(np.quantile(a,.95)),p99=float(np.quantile(a,.99)),max=float(a.max()),sum=float(a.sum()))

if __name__=='__main__':
    suffix=sys.argv[1] if len(sys.argv)>1 else ''
    if (OUT/'ACQUISITION_RESULT.json').is_file():result=read(OUT/'ACQUISITION_RESULT.json')
    elif (OUT/'resume_same_44001.meter.json').is_file() and read(OUT/'resume_same_44001.meter.json')['limit_reason']:
        result=dict(status='CPU_SUBBUDGET_INTERRUPTION',checkpoint=str(OUT/'trajectory/PERIODIC_RESUME_tick0800.json'))
        pair=read(OUT/'trajectory/PERIODIC_RESUME_producer_tick0800.json')
        assert pair['checkpoint_hash']==sha256_file(Path(result['checkpoint']))
    else:result=read(OUT/('ACQUISITION_FAILURE_RESUME.json' if (OUT/'ACQUISITION_FAILURE_RESUME.json').exists() else 'ACQUISITION_FAILURE.json'))
    packet=read(result['checkpoint']);state=packet['state'];complete=result.get('status')=='COMPLETE_T100'
    rows=[json.loads(x) for x in (OUT/'DECISION_RECORDS.jsonl').read_text().splitlines() if x.strip()]
    D=[x for x in rows if 20<x['time']<100];both=[x for x in D if set(x['legal_actions'])=={'CLOSE','WAIT'}]
    activation=[x for x in both if x['decision']['proven'] and x['classification']=='INTERVAL_PROVEN']
    mech=[x for x in activation if x['decision']['action']!=x['shadow']]
    diff=[x for x in D if x['decision']['action']!=x['shadow']]
    forced_diff=[x for x in diff if x['classification']=='RULE_FORCED']
    count=lambda seq:Counter(x['classification'] for x in seq)
    flat=[]
    columns=['time','classification','pool','inflight','legal_actions','actual','shadow','shadow_legal','difference','mechanism_difference',
        'proven','N','k_by_plan_scenario','close_L','close_U','wait_L','wait_U','witness_offset','unknown_reasons',
        'CPU','wall','P2','cache','snapshot','closure_index','consumed_keys']
    for x in rows:
        d=x['decision'];groups={g['action']:g for g in d['action_intervals']}
        flat.append(dict(time=x['time'],classification=x['classification'],pool=x['pool'],inflight=x['inflight'],legal_actions='|'.join(x['legal_actions']),
            actual=d['action'],shadow=x['shadow'],shadow_legal=x['shadow_legal'],difference=d['action']!=x['shadow'],
            mechanism_difference=set(x['legal_actions'])=={'CLOSE','WAIT'} and d['proven'] and d['action']!=x['shadow'],proven=d['proven'],
            N=x['N'],k_by_plan_scenario=json.dumps([r['known_cells'] for r in d['intervals']]),
            close_L=groups.get('CLOSE',{}).get('L'),close_U=groups.get('CLOSE',{}).get('U'),wait_L=groups.get('WAIT',{}).get('L'),wait_U=groups.get('WAIT',{}).get('U'),
            witness_offset=d['selected_offset'],unknown_reasons=json.dumps(sorted({u['reason'] for u in d['unknown_support']})),
            CPU=d['control_cpu_seconds'],wall=d['wall_seconds'],P2=None if x['classification']=='CPU_TIMEOUT' else d['p2_solves'],cache=None if x['classification']=='CPU_TIMEOUT' else d['cache_hits'],snapshot=x['snapshot'],
            closure_index=x['closure_index'],consumed_keys='|'.join(x['consumed_keys'])))
    with (OUT/('DECISION_METRICS'+suffix+'.csv')).open('x',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(flat)
    support=read(OUT/'trajectory/SERVICE_FROZEN_AT_20.json') if (OUT/'trajectory/SERVICE_FROZEN_AT_20.json').is_file() else None
    reasons=Counter();unknown_cells=Counter();kdist=Counter();by_pool=defaultdict(list);paths=defaultdict(list)
    for x in D:
        for category in {u['reason'].split(':',1)[0] for u in x['decision']['unknown_support']}:reasons[category]+=1
        for u in { (u['key'],u['reason']) for u in x['decision']['unknown_support'] }:unknown_cells[u[1]]+=1
        for r in x['decision']['intervals']:
            for k in r['known_cells']:kdist[f'{k}/{x["N"]}']+=1
        bucket='0-2' if x['pool']<3 else ('3-9' if x['pool']<10 else '10+')
        by_pool[bucket].append(x);paths[x['classification']].append(x)
    attempts=list(state['attempts'].values());marks={x['key']:x for x in state['opportunity_marks']}
    R1=[a for a in attempts if marks[a['registration']['key']]['R']==1]
    eligible=[a for a in R1 if a['features']['model_age']<=5];E0=[a for a in R1 if a['features']['model_age']>5]
    closures=state['closures'];keys=[k for c in closures for k in c['preview']['keys']]
    frozen=read(OUT/'ACQUISITION_FROZEN_PLAN.json')
    active_sources=read(OUT/'ENGINEERING_PATCH_01.json')['after_sources'] if (OUT/'ENGINEERING_PATCH_01.json').exists() else frozen['sources']
    old=read(ROOT/'results_calibration_first_20261013/trajectory/SOURCE_CLOSURE.json')
    prior_protected=read(ROOT/'results_calibration_diagnostic_20261013_122013/PROTECTED_BEFORE.json')
    changed=[p for p,h in prior_protected.items() if sha256_file(Path(p))!=h]
    maxres=max((c['preview']['solver'].get('normalized_weight_residual',0.) for c in closures),default=0.)
    snapshots_ok=True
    for x in rows:
        snap=read(OUT/x['snapshot'])['snapshot']
        snapshots_ok &= snap['seed']==44001 and snap['config']==frozen['config'] and snap['isolated_test']==False and snap['calibration_only']==True
    checks=dict(method_identity=packet['method']==state['config']['method_version']==frozen['method'],seed=state['seed']==44001,
        original_source_closure=old==source_inventory(ROOT),revision_sources=packet['sources']==active_sources==source_identity(),
        protected_unchanged=not changed,unique_consumption=len(keys)==len(set(keys))==len(state['consumed']),
        labels_match_consumption=sum(a['consumed']==1 for a in attempts)==len(keys),P2_residual=maxres<=1e-7,
        SGD_budget=state['backend']['local_optimizer_steps']<=5000,
        actual_steps_equal_R1=state['backend']['local_optimizer_steps']==len(R1),
        E0_all_training_started=all(state['backend']['work'][a['registration']['key']]['training_started'] for a in E0),
        R0_none_training_started=all(not state['backend']['work'][a['registration']['key']]['training_started'] for a in attempts if marks[a['registration']['key']]['R']==0),
        q_registration_frozen=all(a['q']['frozen_at']==a['registration']['registered_at'] for a in attempts),
        q_roles=all(a['q']['role']==('outside_R' if marks[a['registration']['key']]['R']==0 else ('structural_zero' if a['features']['model_age']>5 else 'diagnostic_prior')) for a in attempts),
        D_count=(len(D)==799 if complete else True),decision_clock=(len(rows)==1000 if complete else True),
        snapshots_valid=snapshots_ok,all_planning_CPU_within2=all(x['decision']['control_cpu_seconds']<=2 for x in rows),
        deadline_domain=all(c['duration']<=4+1.1e-9 for c in closures),
        same_run_only=(support is None or all(o['clock_run_id']==state['clock_namespace']['run_id'] and o['time']<=20 for o in support['model']['joint_opportunities'])),
        all_mature_if_complete=(all(a['consumed'] is not None for a in attempts) if complete else True),
        conditional_history_cutoff=(support is None or all(r['observed_until']<=20 and r['registration_version']-r['registration']['downloaded_version']<=5 for r in support['conditional_service_records'])))
    if any(not bool(v) for v in checks.values()):classification='ACQUISITION_INVALID'
    elif not complete:classification='ACQUISITION_INCOMPLETE'
    elif activation and len(mech)/len(D)>=.05 and len(forced_diff)<len(diff)/2:classification='REQUEST_PAIRED_DEVELOPMENT_COMPARISON'
    else:classification='MECHANISM_EVIDENCE_INSUFFICIENT_WAITING_USER_REVIEW'
    summary=dict(status=classification,complete_T100=complete,T_observed=max(x['time'] for x in rows),recoverable_T=state['now'],
        checkpoint=result['checkpoint'],D=len(D),expected_complete_D=799,
        D_is_prefix=not complete,both_actions_legal=len(both),activation=len(activation),mechanism_difference=len(mech),
        mechanism_difference_D_ratio=len(mech)/len(D) if D else None,mechanism_difference_both_legal_ratio=len(mech)/len(both) if both else None,
        total_difference=len(diff),total_difference_D_ratio=len(diff)/len(D) if D else None,
        forced_difference=len(forced_diff),difference_by_class=dict(count(diff)),D_classification=dict(count(D)),
        all_classification=dict(count(rows)),endpoint=[x for x in rows if x['time']==100],checks=checks,
        unknown_reason_decision_counts=dict(reasons),unknown_query_counts=dict(unknown_cells),k_distribution=dict(kdist),
        unknown_trace_unavailable_CPU_timeout=sum(x['classification']=='CPU_TIMEOUT' and not x['decision']['intervals'] for x in D),
        pool_costs={b:dict(n=len(xs),CPU=stats([x['decision']['control_cpu_seconds'] for x in xs]),P2=stats([x['decision']['p2_solves'] for x in xs if x['classification']!='CPU_TIMEOUT']),
            classes=dict(count(xs))) for b,xs in by_pool.items()},
        path_costs={b:dict(n=len(xs),CPU=stats([x['decision']['control_cpu_seconds'] for x in xs]),wall=stats([x['decision']['wall_seconds'] for x in xs]),
            P2=stats([x['decision']['p2_solves'] for x in xs] if b!='CPU_TIMEOUT' else []),cache=stats([x['decision']['cache_hits'] for x in xs] if b!='CPU_TIMEOUT' else [])) for b,xs in paths.items()},
        planning_CPU=stats([x['decision']['control_cpu_seconds'] for x in rows]),planning_wall=stats([x['decision']['wall_seconds'] for x in rows]),
        record_counts_scope='latest complete recoverable checkpoint; not uncheckpointed observed tail',
        registrations=len(attempts),R0=len(attempts)-len(R1),R1=len(R1),R1_E0=len(E0),R1_E1=len(eligible),
        E_distribution=dict(Counter(m['registration_age'] for m in marks.values())),
        consumed=len(keys),closures=len(closures),empty_closures=sum(c['empty'] for c in closures),
        labels_censored=sum(a['consumed'] is None for a in attempts),physical_pending_R1=sum(a['physical_outcome']=='pending' for a in R1),
        terminal_reasons=dict(Counter(str(a['terminal_reason']) for a in attempts)),
        SGD=state['backend']['local_optimizer_steps'],max_P2_residual=maxres,changed_protected=changed,
        warmup_support=None if support is None else dict(registrations=len(support['model']['joint_opportunities']),
            conditional_service_records=len(support['conditional_service_records']),risk_cells=len(support['model']['cells']),
            supported_risk_cells=sum(c['risk']>=5 for c in support['model']['cells']),marks=len(support['model']['marks'])),
        q_fit=0,GPU=0,baseline_trajectories=0,control_benefit='NOT_MEASURED',prediction_benefit='NOT_MEASURED',q_calibration='NOT_COMPUTED',next_status='WAITING_USER_REVIEW')
    if support:
        mark_cells={(m['client'],*m['stratum']) for m in support['model']['marks']}
        opportunity_cells=Counter((o['client'],o['device_class'],o['network_class']) for o in support['model']['joint_opportunities'] if o['R']==1 and o['registration_age']<=5)
        summary['warmup_missing_mark_cells']=[dict(client=c,device=d,network=n,R1_E1_registrations=v) for (c,d,n),v in sorted(opportunity_cells.items()) if (c,d,n) not in mark_cells]
        summary['warmup_unsupported_risk_cells']=[c for c in support['model']['cells'] if c['risk']<5]
    summary['unknown_reason_count_definition']='deduplicated category presence per decision; timeout traces unavailable, not zero support'
    exclusive_json(OUT/('DEVELOPMENT_SUMMARY'+suffix+'.json'),summary)
    for p in (ROOT/'src/raven_mcs_re_interval').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    print(json.dumps({k:summary[k] for k in ('status','complete_T100','T_observed','D','both_actions_legal','activation','mechanism_difference','total_difference','forced_difference','D_classification','registrations','R1_E0','SGD','max_P2_residual','checks')},ensure_ascii=False))
    if not all(checks.values()):raise SystemExit(2)
