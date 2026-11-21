"""Continue the exact failed 44001 prefix, not a replacement acquisition."""
from dataclasses import asdict
import json,os,time
import torch
from re_interval_development_budget import ROOT,OUT,used
from restore_re_interval_development_state import restore_bundle
from raven_mcs_re_interval.development_acquisition import checkpoint_pair
from raven_mcs_re_interval.planner import candidate_offsets,fixed_fallback
from raven_mcs.control.persistence import exclusive_json
from raven_mcs.control.process_budget import ProcessTreeBudget
from raven_mcs.utils.hashing import sha256_json

if __name__=='__main__':
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    failure=json.loads((OUT/'ACQUISITION_FAILURE.json').read_text())
    session,producer,first=restore_bundle(ROOT,OUT,failure['checkpoint'],OUT/'trajectory/FAILED_producer_tick0202.json',
        engineering_patch=OUT/'ENGINEERING_PATCH_01.json')
    r=session.runner;meter=ProcessTreeBudget();meter.attach(os.getpid());start=time.perf_counter();remaining=2700-used()-100
    previous_wall=failure['wall'];tick=first;status='PREFIX';metrics=(OUT/'DECISION_RECORDS.jsonl').open('a',encoding='utf-8')
    assert first==202 and len(r.decisions)==201 and r.backend.local_optimizer_steps==663
    exclusive_json(OUT/'RESUME_IDENTITY.json',dict(from_tick=first,completed_decisions=201,SGD_start=663,
        same_producer_rng=True,same_torch_rng=True,no_repeat_training_before_202=True,
        engineering_bridge='ENGINEERING_PATCH_01.json',method_unchanged=True,ledger_CPU_start=used()))
    try:
        for tick in range(first,1001):
            if meter.cpu_seconds()>remaining-200 or previous_wall+time.perf_counter()-start>7000:
                status='CPU_BUDGET_PREFIX' if meter.cpu_seconds()>remaining-200 else 'WATCHDOG_PREFIX';tick-=1;break
            now=round(tick*.1,10)
            if tick!=first:producer.notices_through(now);r.advance_time(now)
            snapshot=r.snapshot();before=sha256_json(asdict(snapshot));shadow=fixed_fallback(snapshot,'shadow_fixed_time_2')
            legal=sorted({'CLOSE' if o==0 else 'WAIT' for o in candidate_offsets(snapshot)})
            if now-snapshot.window_open>=4-1e-9:legal=['CLOSE']
            snapshot_path=f'snapshots/tick{tick:04d}.json';payload=dict(snapshot=asdict(snapshot),predictor_parameter_hash=snapshot.service_parameters_hash)
            if (OUT/snapshot_path).exists():
                assert sha256_json(json.loads((OUT/snapshot_path).read_text()))==sha256_json(payload)
            else:exclusive_json(OUT/snapshot_path,payload)
            decision=session.controller.decide(snapshot,r.predictor)
            if sha256_json(asdict(r.snapshot()))!=before:raise RuntimeError('planning/shadow mutated actual state')
            row=dict(tick=tick,time=now,window_open=snapshot.window_open,snapshot=snapshot_path,pool=len(snapshot.pool),inflight=len(snapshot.in_flight),
                N=int(round((min(now+8.,100.)-now)/.1)),candidate_offsets=candidate_offsets(snapshot),legal_actions=legal,
                shadow=shadow.action,shadow_legal=shadow.action in legal,decision=asdict(decision),
                classification='ENDPOINT_GRID' if tick==1000 else ('HARD_DEADLINE' if decision.reason=='hard_deadline' else
                    ('CPU_TIMEOUT' if 'CPU_TIMEOUT' in decision.reason else decision.reason)),
                accounting_index=len(session.controller.accounting)-1,closure_index=None,consumed_keys=[])
            r.decisions.append(dict(time=now,**asdict(decision)))
            if decision.action=='CLOSE':
                closure=session.close();producer.after_close();row['closure_index']=len(r.closures)-1;row['consumed_keys']=closure['preview']['keys']
            metrics.write(json.dumps(row,allow_nan=False)+'\n');metrics.flush();producer.reclaim_terminal_storage()
            if tick%100==0:
                if tick%200==0:checkpoint_pair(session,producer,tick,'PERIODIC_RESUME')
                print(json.dumps(dict(tick=tick,registrations=len(r.attempts),SGD=r.backend.local_optimizer_steps,
                    resume_CPU=meter.cpu_seconds(),resume_wall=time.perf_counter()-start)),flush=True)
        else:status='COMPLETE_T100';r.finish_finite_endpoint()
        if status!='COMPLETE_T100':r.finish_observation()
        path=checkpoint_pair(session,producer,tick,status)
        exclusive_json(OUT/'ACQUISITION_RESULT.json',dict(status=status,T_observed=r.now,T_target=100.,tick=tick,checkpoint=str(path),
            method=r.config.method_version,seed=44001,registrations=len(r.attempts),SGD=r.backend.local_optimizer_steps,
            training_CPU=producer.training_cpu,training_wall=producer.training_wall,resume_process_tree_CPU=meter.cpu_seconds(),
            initial_execution_wall=previous_wall,resume_wall=time.perf_counter()-start,planning_calls=len(r.decisions),
            q_role='diagnostic_prior_NOT_CALIBRATED',q_fit=0,GPU=0,next_status='WAITING_USER_REVIEW'))
    except Exception as exc:
        import traceback
        r.finish_observation();path=checkpoint_pair(session,producer,tick,'FAILED_RESUME')
        exclusive_json(OUT/'ACQUISITION_FAILURE_RESUME.json',dict(error=str(exc),trace=traceback.format_exc(),tick=tick,now=r.now,
            CPU=meter.cpu_seconds(),wall=time.perf_counter()-start,SGD=r.backend.local_optimizer_steps,checkpoint=str(path),status='WAITING_USER_REVIEW'))
        raise
    finally:metrics.close()
