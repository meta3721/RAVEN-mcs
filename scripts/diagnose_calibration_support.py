"""D2/D3: existing records only; no sampler, planner, q fit or model imports."""
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from diagnose_calibration_d0 import ROOT, OLD, OUT, read, save

def table(name, rows):
    with (OUT/name).open('x',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def layer(reg):return (reg['client'],reg['device_class'],reg['network_class'])

if __name__=='__main__':
    assert read(OUT/'D0_IDENTITY.json')['status']=='PASS'
    assert read(OUT/'D1_CHECK.json')['status']=='PASS'
    final=read(OLD/'trajectory/COMPLETE_T100_tick1000.json')['state']
    frozen=read(OLD/'trajectory/SERVICE_FROZEN_AT_20.json'); model=frozen['model']
    attempts=final['attempts'];hist=model['opportunity_history']; records=frozen['records']
    reason=Counter();actions=Counter();decisions=[]
    for i,d in enumerate(final['decisions'],1):
        t=round(i*.1,10) # Explicit fixed tick loop, not timestamp in raw decision.
        reason[d['reason']]+=1;actions[d['action']]+=1
        kind=('warmup' if d['reason']=='common_warmup' else 'hard_deadline' if d['reason']=='hard_deadline' else
            'endpoint' if d['reason']=='experiment_end' else 'timeout' if 'CPU_TIMEOUT' in d['reason'] else
            'support_fallback' if 'UNSUPPORTED_PREDICTION' in d['reason'] else 'conditional_bundle')
        decisions.append(dict(index=i,time_from_fixed_tick_loop=t,phase='warmup' if t<=20 else 'post_warmup',
            category=kind,reason=d['reason'],action=d['action'],selected_offset=d['selected_offset'],
            CPU_seconds=d['control_cpu_seconds'],wall_seconds=d['wall_seconds'],p2_solves=d['p2_solves']))
    table('DECISIONS.csv',decisions)
    table('DECISION_REASONS.csv',[dict(reason=k,n=v) for k,v in sorted(reason.items())])
    layers={layer(o):dict(client=o['client'],device=o['device_class'],network=o['network_class'],
        opportunities=0,R0=0,R1=0,completion=0,notified_failure=0,right_censored=0,compatible_marks=0,
        first_opportunity_key='',first_R1_key='',first_completion_key='') for o in hist}
    for o in hist:
        row=layers[layer(o)];row['opportunities']+=1
        row['first_opportunity_key']=row['first_opportunity_key'] or o['key']
        row['R0']+=int(attempts[o['key']]['terminal_reason']=='no_observations')
    for r in records:
        row=layers[layer(r['registration'])];row['R1']+=1;row[r['outcome']]+=1
        row['first_R1_key']=row['first_R1_key'] or r['registration']['key']
        if r['outcome']=='completion':row['first_completion_key']=row['first_completion_key'] or r['registration']['key']
    for m in model['marks']:layers[(m['client'],*m['stratum'])]['compatible_marks']+=1
    table('CLIENT_RESOURCE_SUPPORT.csv',[layers[k] for k in sorted(layers)])
    # Recompute risk arithmetic from cutoff-frozen exposures; never final outcomes.
    riskrows=[];cellchecks=[];first_unsupported={}
    for cell in model['cells']:
        device,network=cell['stratum'];l=cell['age_bin'];lo=(l-1)*.1;hi=l*.1
        risk=complete=fail=0
        for r in records:
            if (r['registration']['device_class'],r['registration']['network_class'])!=(device,network):continue
            dur=r['observed_until']-r['registration']['registered_at']
            in_bin=lo+1e-9<dur<=hi+1e-9
            risk+=int(dur>=hi-1e-9 or (r['outcome']!='right_censored' and in_bin))
            complete+=int(in_bin and r['outcome']=='completion');fail+=int(in_bin and r['outcome']=='notified_failure')
        cellchecks.append((risk,complete,fail)==(cell['risk'],cell['completions'],cell['failures']))
        if risk<5:first_unsupported.setdefault(device,l)
        riskrows.append(dict(device=device,network=network,service_age_bin=l,lower_duration=lo,upper_duration=hi,
            risk=risk,completions=complete,failures=fail,supported=risk>=5))
    table('SERVICE_RISK_CELLS.csv',riskrows)
    # Retain each causal raw service exposure and its clock, no private future.
    table('FROZEN_SERVICE_EXPOSURES.csv',[dict(key=r['registration']['key'],client=r['registration']['client'],
        device=r['registration']['device_class'],network=r['registration']['network_class'],
        registered_at=r['registration']['registered_at'],observed_until=r['observed_until'],
        duration=r['observed_until']-r['registration']['registered_at'],outcome=r['outcome'],
        registration_model_age=r['registration_version']-r['registration']['downloaded_version'],
        clock_run_id=frozen['clock_namespace']['run_id'],cutoff=frozen['source_cutoff']) for r in records])
    gaps=[v for v in layers.values() if not v['compatible_marks']]
    samples=[]
    for gap in gaps:
        key=gap['first_opportunity_key'];o=next(o for o in hist if o['key']==key)
        samples.append(dict(query_key=[gap['client'],gap['device'],gap['network']],opportunity=o,
            R0_keys=[o['key'] for o in hist if layer(o)==tuple(gap[k] for k in ('client','device','network')) and attempts[o['key']]['terminal_reason']=='no_observations'],
            frozen_service_records=[dict(registration=r['registration'],outcome=r['outcome'],observed_until=r['observed_until']) for r in records if layer(r['registration'])==tuple(gap[k] for k in ('client','device','network'))]))
    save('MISSING_MARK_SOURCE_EXAMPLES.json',samples)
    age=defaultdict(lambda:dict(R1=0,consumed=0,mature=0))
    for a in attempts.values():
        if a['terminal_reason']=='no_observations':continue
        v=age[a['features']['model_age']];v['R1']+=1;v['consumed']+=int(a['consumed']==1);v['mature']+=int(a['consumed'] is not None)
    table('REGISTRATION_AGE_SUPPORT.csv',[dict(age=k,**v) for k,v in sorted(age.items())])
    # One complete causal FAILED snapshot, selected a priori by earliest post-warmup
    # facility failure. Only deterministic support queries, NO scenario generation.
    prefix=read(OLD/'trajectory/FAILED_tick0201.json')['state']
    cellmap={(tuple(c['stratum']),c['age_bin']):c for c in model['cells']}
    pending=[]
    for item in prefix['in_flight'].values():
        reg=item['registration'];duration=prefix['now']-reg['registered_at'];first=math.floor(duration/.1+1e-9)+1
        marks=layers.get(layer(reg),{}).get('compatible_marks',0)
        risk=cellmap.get(((reg['device_class'],reg['network_class']),first),{}).get('risk',0)
        pending.append(dict(key=reg['key'],client=reg['client'],device=reg['device_class'],network=reg['network_class'],
            now=prefix['now'],registered_at=reg['registered_at'],elapsed_service=duration,
            current_model_age=prefix['model_version']-reg['downloaded_version'],first_queried_service_bin=first,
            first_bin_risk=risk,compatible_marks=marks,missing_mark=marks==0,first_bin_unsupported=risk<5))
    table('EARLIEST_CAUSAL_SNAPSHOT_SUPPORT.csv',pending)
    # Direct potential historical-clock gaps; no random draws and no frequency
    # claim about how often these would be encountered by a sampled scenario.
    batch=[]
    for clock in sorted({int(math.floor(o['time'])) for o in hist}):
        ops=[o for o in hist if int(math.floor(o['time']))==clock]
        missing=[o['key'] for o in ops if layers[layer(o)]['compatible_marks']==0]
        old=[o['key'] for o in ops if attempts[o['key']]['features']['model_age']>5]
        batch.append(dict(clock=clock,opportunities=len(ops),R0=sum(attempts[o['key']]['terminal_reason']=='no_observations' for o in ops),
            missing_mark_count=len(missing),missing_mark_keys=';'.join(missing),actual_age_gt5_count=len(old)))
    table('HISTORICAL_CLOCK_SUPPORT.csv',batch)
    # Historical completed marks can have been unable to enter the live pool.
    oldmarks=[m for m in model['marks'] if m['downloaded_age']>5]
    save('FROZEN_OVERSIZED_AGE_MARKS.json',[dict(client=m['client'],stratum=m['stratum'],registration_model_age=m['downloaded_age'],observed_at=m['observed_at']) for m in oldmarks])
    checks=dict(decisions_1000=len(decisions)==1000,warmup_200=sum(x['phase']=='warmup' for x in decisions)==200,
        fallbacks_792=sum(x['category']=='support_fallback' for x in decisions)==792,
        completions_503=len(model['marks'])==503,opportunity_cells_129=len(layers)==129,
        missing_mark_cells_4=len(gaps)==4,risk_arithmetic_all=all(cellchecks),cutoff_legal=all(r['observed_until']<=20 for r in records),
        age6to8_634=sum(v['R1'] for k,v in age.items() if k>5)==634,
        no_age6to8_consumption=all(v['consumed']==0 for k,v in age.items() if k>5),
        history_matches_registrations=all(all(o[k]==attempts[o['key']]['registration'][j] for k,j in [('client','client'),('time','registered_at'),('device_class','device_class'),('network_class','network_class')]) for o in hist))
    summary=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,decision_categories=dict(Counter(d['category'] for d in decisions)),
        reasons=dict(reason),actions=dict(actions),warmup_service_outcomes=dict(Counter(r['outcome'] for r in records)),
        warmup_opportunities=len(hist),warmup_R0=sum(row['R0'] for row in layers.values()),missing_mark_cells=gaps,
        first_unsupported_service_bin=first_unsupported,supported_risk_cells=sum(r['supported'] for r in riskrows),risk_cells=len(riskrows),
        age_support={str(k):v for k,v in age.items()},frozen_completed_marks_registration_age_gt5=len(oldmarks),
        earliest_causal_snapshot=dict(now=prefix['now'],in_flight=len(pending),overage=sum(r['current_model_age']>5 for r in pending),
            missing_mark_items=sum(r['missing_mark'] for r in pending),immediate_unsupported_risk_items=sum(r['first_bin_unsupported'] for r in pending),
            both_same_item=sum(r['missing_mark'] and r['first_bin_unsupported'] for r in pending)),
        physical_pending=sum(a['physical_outcome']=='pending' for a in attempts.values() if a['terminal_reason']!='no_observations'),
        no_planner_called=True,no_new_scenarios=True,no_q_fit=True,training_steps=0,
        future_R_semantics='all historical registrations are expanded; every expanded opportunity receives R1-completion-conditioned joint mark, with no R occurrence draw; service law itself conditions on R1',
        overlap_limit='Only deterministic gaps from frozen history and one saved causal snapshot. No 12-sample extrapolation or counterfactual full-trajectory fallback rate.')
    save('SUPPORT_SUMMARY.json',summary)
    print(json.dumps(summary,ensure_ascii=False))
    assert all(checks.values())
