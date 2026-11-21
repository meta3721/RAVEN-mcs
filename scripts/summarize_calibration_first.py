"""Read-only final evidence/cost summary. No fitting or calibration tests."""
if __name__=='__main__':
    from pathlib import Path
    import json,platform,sys
    from collections import Counter
    import numpy as np
    import torch,cvxpy
    from raven_mcs.control.persistence import source_inventory,exclusive_json
    from raven_mcs.control.schema import Stage1Summary
    from raven_mcs.utils.hashing import sha256_json,sha256_file

    root=Path(__file__).resolve().parents[1];out=root/'results_calibration_first_20261013'
    result=json.loads((out/'FIRST_ACQUISITION_RESULT.json').read_text(encoding='utf-8'))
    packet=json.loads(Path(result['checkpoint']).read_text(encoding='utf-8'));state=packet['state']
    plan=json.loads((out/'ACQUISITION_FROZEN_PLAN.json').read_text(encoding='utf-8'))
    rows=list(state['attempts'].values());positive=[r for r in rows if r['terminal_reason']!='no_observations']
    checks=dict(state_content_hash=packet['state_hash']==sha256_json(state),
        current_core_sources_match=packet['source_closure']==source_inventory(root),
        target_T_unchanged=state['experiment_end']==100.,clock_namespace_matches=state['clock_namespace']==plan['clock_namespace'],
        applicability_matches=state['probability_applicability']==plan['scope'],
        all_q_diagnostic_prior=all(r['q']['role']=='diagnostic_prior' and r['q']['value']==.5 for r in rows),
        all_q_registration_frozen=all(r['q']['frozen_at']==r['registration']['registered_at'] for r in rows),
        all_record_namespaces=all(r['features']['clock_run_id']==state['clock_namespace']['run_id'] for r in rows),
        all_stage1_configured_on=all(s['design_enabled'] is True for s in state['private_stage1'].values()),
        actual_optimizer_matches=state['backend']['local_training_config']==dict(optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01),
        actual_steps_match_positive_attempts=state['backend']['local_optimizer_steps']==len(positive),
        no_duplicate_consumption=len(state['consumed'])==sum(r['consumed']==1 for r in rows),
        no_extra_seed_trajectory=not result['remaining_trajectories_executed'],
        finite_model=all(np.isfinite(np.asarray(v['values'])).all() for v in state['backend']['theta'].values()))
    if result['status']=='COMPLETE_T100':checks['all_consumption_labels_mature']=all(r['consumed'] in (0,1) for r in rows)
    failed=json.loads((out/'trajectory/FAILED_tick0201.json').read_text(encoding='utf-8'))
    support_age={}
    for r in positive:
        age=str(r['features']['model_age']);row=support_age.setdefault(age,dict(R1=0,consumed=0,mature=0,censored=0))
        row['R1']+=1;row['consumed']+=int(r['consumed']==1);row['mature']+=int(r['consumed'] is not None);row['censored']+=int(r['consumed'] is None)
    per_client=Counter(r['registration']['client'] for r in positive)
    service=json.loads((out/'trajectory/SERVICE_FROZEN_AT_20.json').read_text(encoding='utf-8'))
    checks['no_future_service_fit']=all(r['observed_until']<=20 and r['registration']['registered_at']<=20 for r in service['records'])
    checks['parameter_hash_matches']=all(r['features']['service_parameters_hash']==service['parameter_hash'] for r in positive if r['registration']['registered_at']>20)
    ledger=json.loads((out/'BUDGET.json').read_text(encoding='utf-8'))
    charged=ledger['interactive_allowance_seconds']+sum(r['process_tree_cpu_seconds']+r['monitor_cpu_seconds'] for r in ledger['runs'])+sum(x['charged_cpu_seconds'] for x in ledger.get('supplemental_charges',[]))
    if not all(checks.values()):raise RuntimeError(str({k:v for k,v in checks.items() if not v}))
    summary=dict(checks=checks,result=result,support_age=support_age,
        client_counts=dict(min=min(per_client.values()),max=max(per_client.values()),clients=len(per_client)),
        old_failed_planning_accounting=failed['controller']['accounting'][-1],
        empirical_service_fit_exposures=dict(Counter(r['outcome'] for r in service['records'])),
        realized_service_kernel=service['parameter_hash'],
        charged_cpu_before_this_summary=charged,
        storage_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
        runtime=dict(python=sys.version,torch=torch.__version__,cvxpy=cvxpy.__version__,platform=platform.platform(),
            CPU_only=True,OMP_threads=1,model_device='cpu',GPU_steps=0),
        formal_calibration_statistics='NOT_COMPUTED',fit='NOT_EXECUTED',
        support_note='registration age>5 structurally cannot be consumed; clipping/prior cannot create support',
        first_run_fit_eligibility='requires user review of recorded engineering interruption; not automatically calibration evidence')
    exclusive_json(out/'FINAL_EVIDENCE_SUMMARY.json',summary)
    print(json.dumps(dict(checks=checks,support_age=support_age,client_counts=summary['client_counts'],runtime=summary['runtime'],storage_bytes=summary['storage_bytes']),ensure_ascii=False))
