"""Resume only the approved first acquisition after the entry import fix.

Preserves the failed checkpoint, source closure, namespace, RNG and target100.
Imports remain in __main__ to keep planning workers independent of training.
"""
if __name__=='__main__':
    import argparse,json,os,time,traceback
    from collections import Counter
    from pathlib import Path
    import numpy as np
    import torch
    from raven_mcs.experiments.calibration_first import load_inputs,owner_for,CausalTrafficProducer,checkpoint_pair
    from raven_mcs.experiments.conditional_bundle import restore_conditional_bundle
    from raven_mcs.control.schema import ControlConfig,InputError
    from raven_mcs.control.persistence import exclusive_json
    from raven_mcs.control.process_budget import ProcessTreeBudget
    from raven_mcs.utils.hashing import sha256_file

    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--mode',choices=['calibration_only'],required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];out=a.out.resolve();out.relative_to(root)
    check=json.loads((out/'PREFIX_PLANNER_CHECK.json').read_text(encoding='utf-8'))
    if not check['no_model_or_lifecycle_change'] or check['decision']['control_cpu_seconds']>2:
        raise InputError('same-specification facility repair has not passed')
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    inputs=load_inputs(root,out);path=out/'trajectory/FAILED_tick0201.json'
    packet=json.loads(path.read_text(encoding='utf-8'));state=packet['state']
    private=json.loads((path.parent/'FAILED_producer.json').read_text(encoding='utf-8'))
    if private['checkpoint_hash']!=sha256_file(path) or private['T']!=100. or private['clock_namespace']!=state['clock_namespace']:
        raise InputError('prefix private/public pair mismatch')
    owner=owner_for(inputs,ControlConfig.from_dict(state['config']))
    session=restore_conditional_bundle(owner,path,repo_root=root,expected_config=ControlConfig.from_dict(state['config']),
        expected_data_identity=inputs.data_id,expected_target_identity=inputs.target_id)
    producer=CausalTrafficProducer(inputs,session);producer.restore(private['state'])
    torch.set_rng_state(torch.tensor(private['torch_rng'],dtype=torch.uint8))
    if session.runner.now!=20.1 or session.runner.backend.local_optimizer_steps!=686:
        raise InputError('unexpected resume prefix, not the authorized first trajectory')
    exclusive_json(out/'RESUME_IDENTITY.json',dict(parent_checkpoint=str(path),parent_hash=sha256_file(path),
        core_source_closure_unchanged=True,driver_sha256=sha256_file(Path(__file__)),
        fix='Windows __mp_main__ no longer imports the real training entry',
        no_method_parameter_change=True,seed=43001,T=100.,clock_namespace=state['clock_namespace'],
        existing_SGD_steps=686,no_retraining_prefix=True))
    budget=json.loads((out/'BUDGET.json').read_text());used=budget['interactive_allowance_seconds']+sum(x['process_tree_cpu_seconds']+x['monitor_cpu_seconds'] for x in budget['runs'])
    remaining=3600-used-30;meter=ProcessTreeBudget();meter.attach(os.getpid());wall=time.perf_counter();status='PREFIX'
    try:
        for tick in range(201,1001):
            if meter.cpu_seconds()>=remaining-180:status='CPU_BUDGET_PREFIX';tick-=1;break
            now=round(tick*.1,10);producer.notices_through(now);session.runner.advance_time(now)
            decision=session.decide()
            if decision.action=='CLOSE':session.close();producer.after_close()
            producer.reclaim_terminal_storage()
            if tick%100==0:
                checkpoint_pair(session,producer,tick)
                print(json.dumps(dict(tick=tick,T=100,registrations=len(session.runner.attempts),SGD_steps=session.runner.backend.local_optimizer_steps,
                    segment_cpu=meter.cpu_seconds(),segment_wall=time.perf_counter()-wall)),flush=True)
        else:status='COMPLETE_T100';session.runner.finish_finite_endpoint()
        if status!='COMPLETE_T100':session.runner.finish_observation()
        terminal=session.save(f'{status}_tick{tick:04d}.json')
        exclusive_json(session.run_dir/(status+'_producer.json'),dict(checkpoint=terminal.name,checkpoint_hash=sha256_file(terminal),tick=tick,T=100.,
            state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist(),clock_namespace=session.runner.clock_namespace))
        records=list(session.runner.attempts.values());positive=[r for r in records if r.terminal_reason!='no_observations'];decisions=session.runner.decisions
        support={}
        for r in positive:
            layer=f'{r.registration.device_class}/{r.registration.network_class}'
            row=support.setdefault(layer,dict(R1=0,mature=0,consumed=0,censored=0))
            row['R1']+=1;row['mature']+=int(r.consumed is not None);row['consumed']+=int(r.consumed==1);row['censored']+=int(r.consumed is None)
        fb=sum('fixed_time_2' in d['reason'] for d in decisions)
        report=dict(status=status,T_target=100,T_observed=session.runner.now,checkpoint=str(terminal),registrations=len(records),
            positive_observation_attempts=len(positive),mature=sum(r.consumed is not None for r in positive),consumed=sum(r.consumed==1 for r in positive),
            censored=sum(r.consumed is None for r in positive),physical_pending=sum(r.physical_outcome=='pending' for r in positive),
            terminal_reasons=dict(Counter(r.terminal_reason for r in records)),support=support,client_support=len({r.registration.client for r in positive}),
            age_support=dict(Counter(r.features.model_age for r in positive)),
            feature_support={name:dict(min=min(getattr(r.features,name) for r in positive),max=max(getattr(r.features,name) for r in positive))
                for name in ['maximum_deadline_slack','pool_count','in_flight_count']},
            observed_target_groups=len({g for r in positive for g,m in enumerate(session.runner.private_stage1[r.registration.key].masses) if m>0}),target_groups=len(inputs.mu),
            predictor_supported_cells=sum(c.risk>=5 for c in session.runner.predictor.cells),predictor_total_cells=len(session.runner.predictor.cells),
            planning_calls=len(decisions),fallback_calls=fb,fallback_proportion=fb/len(decisions),post_warmup_fallback_proportion=sum('fixed_time_2' in d['reason'] for d in decisions[200:])/len(decisions[200:]),
            decision_reasons=dict(Counter(d['reason'] for d in decisions)),
            local_sgd_steps=session.runner.backend.local_optimizer_steps,training_cpu_seconds=producer.training_cpu,training_wall_seconds=producer.training_wall,
            resumed_segment_process_tree_cpu_seconds=meter.cpu_seconds(),resumed_segment_wall_seconds=time.perf_counter()-wall,
            planner_cpu_seconds=sum(x['total_cpu_seconds'] for x in session.controller.accounting),planner_wall_seconds=sum(x['wall_seconds'] for x in session.controller.accounting),
            historical_failed_planning_calls=sum(x['total_cpu_seconds']>2 for x in session.controller.accounting),
            max_successful_planning_CPU=max(d['control_cpu_seconds'] for d in decisions),
            max_actual_weight_residual=max((c['preview']['solver'].get('normalized_weight_residual',0.) for c in session.runner.closures),default=0.),
            gpu=0,q_role='diagnostic_prior',q_fitted=False,q_calibration_pass='NOT_COMPUTED',next_status='WAITING_USER_REVIEW',
            remaining_trajectories_executed=0,B1_executed=False,formal_executed=False)
        exclusive_json(out/'FIRST_ACQUISITION_RESULT.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception as exc:
        session.runner.finish_observation();failed=session.save(f'RESUME_FAILED_tick{tick:04d}.json')
        exclusive_json(session.run_dir/'RESUME_FAILED_producer.json',dict(checkpoint=failed.name,checkpoint_hash=sha256_file(failed),
            tick=tick,T=100.,state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist(),clock_namespace=session.runner.clock_namespace))
        exclusive_json(out/'RESUME_FAILURE.json',dict(error=str(exc),trace=traceback.format_exc(),tick=tick,now=session.runner.now,CPU=meter.cpu_seconds(),
            wall=time.perf_counter()-wall,SGD_steps=session.runner.backend.local_optimizer_steps,checkpoint=str(failed),status='WAITING_USER_REVIEW'))
        raise
