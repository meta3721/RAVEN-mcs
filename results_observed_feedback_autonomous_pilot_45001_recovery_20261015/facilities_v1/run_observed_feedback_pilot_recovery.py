"""Authorized fresh45001 autonomous arm;real causal learning/lifecycle, no fitting."""
import sys,json,os,time,traceback,hashlib,copy,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from observed_feedback_recovery_common import fresh_arm as build_arm,OUT as BATCH,OLD,ARM_NAMES,restore_fixed05,require_resource_source_identity
from observed_feedback_recovery_io import durable_json
from pathlib import Path
args=argparse.ArgumentParser();args.add_argument('--strategy',required=True,choices=list(ARM_NAMES));args=args.parse_args();STRATEGY=args.strategy
OUT=BATCH/('fixed05_resume1' if STRATEGY=='fixed_time_0.5' else ARM_NAMES[STRATEGY]);OUT.mkdir(exist_ok=True)
import numpy as np,pandas as pd,torch
from types import SimpleNamespace
from datetime import datetime,timezone
from dataclasses import asdict
from observed_feedback_recovery_account import RecoveryAccount as RollingAccount
from raven_mcs_observed_feedback.schema import ControlConfig
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.authorization import DiagnosticCollectionAuthorization
from raven_mcs_observed_feedback.backend import connect_full_runner
from raven_mcs_observed_feedback.acquisition import CausalProducer
from raven_mcs_observed_feedback.pilot_controller import PilotController as Controller
from raven_mcs_observed_feedback.diagnostic import shadow_actions
from raven_mcs_observed_feedback.execution import frozen_shadow_context
from raven_mcs_observed_feedback.persistence import restore_pair,save_pair,source_closure
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs_execution.budget import checkpoint_due
from raven_mcs.experiments.calibration_first import load_inputs
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import CommonNDMF
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.utils.hashing import sha256_json
torch.set_num_threads(1);torch.set_num_interop_threads(1)

def main():
    a=RollingAccount(OUT);a.session_start=time.perf_counter();r=p=None;last_marker=None;next_tick=1;last_saved=0;last_sizes=None;previous_segment=dict(time=0.,registrations=0,R1=0,SGD=0,notices=0,grid=0,spent=dict.fromkeys(a.spent,0.),driver_CPU=0.,cost_record_count=0);status='RESUMPTION_NOT_STARTED';failure=None
    save_capacity=113.33740118986273 if STRATEGY=='fixed_time_0.5' else 19.4775;closing_capacity=15.331367;started_wall=time.perf_counter();wall_cap=float(os.environ['OF_ARM_WALL_LIMIT']);a.reserve=save_capacity+closing_capacity
    store=PairedCheckpointStore(OUT/'trajectory')
    parent_marker=OLD/'fixed05/trajectory/tick0750.complete.json' if STRATEGY=='fixed_time_0.5' else None;freeze=json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text());original_closure=require_resource_source_identity();prefix_rows=[];identity={};offset=1075 if STRATEGY=='fixed_time_0.5' else 0
    if parent_marker:
        for line in (OLD/'fixed05/DECISION_METRICS.jsonl').open():
            row=json.loads(line)
            if row['time']>75:break
            prefix_rows.append(row)
        assert len(prefix_rows)==750
        next_tick=751;last_saved=750
        previous_segment.update(time=75.,registrations=3225,SGD=2493,grid=750,R1=2493)
    def append(name,obj):
        with (OUT/name).open('a',encoding='utf-8') as stream:stream.write(json.dumps(obj,allow_nan=False)+'\n')
    def build_fresh():
        nonlocal identity
        if parent_marker:
            inputs,runner,producer,frozen,equality=restore_fixed05(OUT,a.root)
            durable_json(OUT/'RESUMPTION_CHECK.json',equality)
        else:inputs,runner,producer,frozen=build_arm(STRATEGY,OUT,a.root)
        assert source_closure()==original_closure
        if not parent_marker:assert runner.now==0. and runner.model_version==0 and runner.backend.local_optimizer_steps==0 and not any(runner.debt) and runner.last_release is None
        identity=dict(method=runner.config.method_version,seed=45001,clock_namespace=runner.clock_namespace)
        assert not (OUT/'ARM_FROZEN_PLAN.json').exists();durable_json(OUT/'ARM_FROZEN_PLAN.json',frozen)
        return runner,producer,dict(status='PASS',strategy=STRATEGY,initial_identity=frozen['initial_identity'],initial_Q_zero=not any(runner.debt),initial_L_empty=runner.last_release is None,isolated_test=False,calibration_only=True,SGD=runner.backend.local_optimizer_steps)
    def persist(name):
        nonlocal last_marker,last_saved,last_sizes,save_capacity,closing_capacity,previous_segment
        assert source_closure()==original_closure
        private=dict(T=100.,tick=r.now/.1,next_grid_tick=next_tick,clock_namespace=r.clock_namespace,state=p.to_dict(),
            parent_run_id=identity.get('clock_namespace',{}).get('run_id') if parent_marker else None,parent_checkpoint=str(parent_marker) if parent_marker else None,decision_start_tick=751 if parent_marker else 1,
            account=dict(base=a.base,spent=a.spent,save_capacity=save_capacity,closing_capacity=closing_capacity),rolling_budget_enabled=True,
            rolling_previous_segment=previous_segment,session_id=OUT.name,worker_PID=os.getpid())
        marker=a.operation('save',lambda:save_pair(r,store,name,producer_state=private,budget=a.root,save_reserve=a.reserve),save_capacity)
        a.checkpoint_session(marker,r,p,next_tick,offset)
        sizes=json.loads(marker.read_text())['sizes'];growth=max(1.,sum(sizes)/sum(last_sizes)) if last_sizes else 1.25
        last_sizes=sizes;last_marker=marker;last_saved=r.now/.1
        save_capacity=max(save_capacity,5.96875,2*a.maxima['save']*growth)
        closing_capacity=max(closing_capacity,8.,1.5*a.maxima['save']);a.reserve=save_capacity+closing_capacity
        append('SAVE_MEASUREMENTS.jsonl',dict(marker=str(marker),time=r.now,SGD=r.backend.local_optimizer_steps,sizes=sizes,measured_max_root_upper=a.maxima['save'],growth_factor=growth,save_capacity=save_capacity,closing_capacity=closing_capacity,total_reserve=a.reserve))
        return marker
    try:
        assert json.loads((OLD/'SGD0_AUTONOMOUS_CHECK.json').read_text())['status']=='PASS'
        r,p,check=a.operation('initialization',build_fresh,80.)
        durable_json(OUT/'ARM_INITIAL_CHECK.json',check);status='STARTED_PREFIX_INCOMPLETE';last_marker=parent_marker
        if not parent_marker:persist('tick0000_initial')
        else:a.checkpoint_session(parent_marker,r,p,next_tick,offset)
        # Retain old censored snapshot; reopening observation clears only administrative annotations, not control/producer/RNG.
        before=r.snapshot().fingerprint;cleared=dict(consumption=0,physical=0)
        for rec in r.attempts.values():
            if rec.consumed is None and rec.right_censored_at is not None:rec.right_censored_at=None;cleared['consumption']+=1
            if rec.R and rec.physical_outcome=='pending' and rec.physical_service_censor_reason=='observation_prefix':
                rec.physical_service_censored_at=None;rec.physical_service_censor_reason=None;cleared['physical']+=1
        assert r.snapshot().fingerprint==before
        (OUT/'CENSOR_REOPENING.json').write_text(json.dumps(dict(old_prefix_preserved=True,annotations_cleared=cleared,control_snapshot_unchanged=True,full_endpoint_not_assigned=True),indent=2))
        original_operation=a.operation
        def guarded_operation(category,fn,ceiling=2.,online=False):
            if category=='training' and r.backend.local_optimizer_steps+offset+1>5000:raise RuntimeError('CUMULATIVE_PHYSICAL_SGD_LIMIT')
            return original_operation(category,fn,ceiling,online)
        p.operation=guarded_operation
        control=Controller(STRATEGY,root_budget=a.root,save_reserve=a.reserve,operation_root_ceiling=2.)
        while next_tick<=1000:
            if time.perf_counter()-started_wall>=wall_cap-60.:raise RuntimeError('WALL_HEADROOM_SAVE_AND_STOP')
            at=round(next_tick*.1,10)
            if not p.notices_through(at):raise RuntimeError('PILOT_PAUSE_NOT_CLEARED')
            context={}
            def pre():
                r.advance_time(at);snap=r.snapshot();context.update(snapshot=asdict(snap),fingerprint=snap.fingerprint,shadow=frozen_shadow_context(r),window=r.window_id)
            a.operation('events',pre)
            control.save_reserve=a.reserve
            d=a.operation('online',lambda:r.on_grid(at,control),2.,online=True)
            online_record=a.records[-1]
            def diagnostics():
                shadow=shadow_actions(context['shadow'],d) if STRATEGY in ('OF-v1','OF-no-Q-stop') else dict(forced=d.reason in {'TERMINAL','WARMUP','DEADLINE','MIN_CLIENTS'},no_Q_stop=None,no_Q_B=None,P2_recomputed=False,OF_same_state=None)
                assert len(r.consumed)==sum(x.consumed==1 for x in r.attempts.values()),'CONSUMPTION_COUNT_MISMATCH'
                append('DECISION_SNAPSHOTS.jsonl',dict(time=at,fingerprint=context['fingerprint'],snapshot=context['snapshot']))
                row=dict(time=at,window=context['window'],snapshot_hash=context['fingerprint'],P=len(context['snapshot']['pool']),F=len(context['snapshot']['in_flight']),action=d.action,reason=d.reason,B=d.B,components=dict(d.components),preview=d.preview.to_dict() if d.preview else None,
                    p2_solves=d.p2_solves,cache_hits=d.cache_hits,shadow=shadow,model_version_after=r.model_version,
                    actual_request_root_upper=online_record['root_upper_CPU'],actual_request_root_difference=online_record['request_root_difference'])
                append('DECISION_METRICS.jsonl',row)
                if r.window_id!=context['window']:p.after_close();p.reclaim_terminal_storage()
            a.operation('events',diagnostics)
            next_tick+=1
            remaining=a.root.read()['effective_remaining']
            if next_tick==1001 or checkpoint_due(next_tick-1,last_saved,remaining=remaining,save_reserve=a.reserve,operation_root_ceiling=2.):
                persist('tick%04d'%(next_tick-1))
                def summary():
                    nonlocal previous_segment
                    value=a.rolling_summary(r,p,next_tick-1,last_sizes,previous_segment);previous_segment=value['current'];append('ROLLING_COST_PLANS.jsonl',value)
                    durable_json(OUT/'PROGRESS.json',dict(time=r.now,SGD=r.backend.local_optimizer_steps,physical_upper=r.backend.local_optimizer_steps+offset,grid=next_tick-1,registrations=len(r.attempts),model_version=r.model_version,root_batch_CPU=a.root.read()['batch_used'],remaining_effective_CPU=a.root.read()['effective_remaining'],reserve=a.reserve,forecast_warning=value['warning'],last_complete_marker=str(last_marker)))
                a.operation('events',summary)
            if a.root.read()['effective_remaining']<a.reserve+4.:raise RuntimeError('ACTUAL_HEADROOM_INSUFFICIENT_SAVE_AND_STOP')
        assert r.ended and r.now==100. and next_tick==1001 and p.next_clock==100 and p.active_registration is None
        assert r.backend.local_optimizer_steps+offset<=5000 and len(r.decisions)==1000
        assert all(x.consumed is not None and x.right_censored_at is None for x in r.attempts.values())
        assert all(not x.R or x.physical_outcome!='pending' or x.physical_service_censored_at==100. for x in r.attempts.values())
        status='COMPLETE_T100_ACQUISITION'
    except Exception as exc:
        failure=dict(error=repr(exc),traceback=traceback.format_exc(),time=r.now if r else None,SGD=r.backend.local_optimizer_steps if r else None,next_grid_tick=next_tick)
        if r is not None and r.fault is None and not r.ended:
            try:
                r.finish_observation();persist('stopped_%04d_%05d'%(next_tick,len(a.records)))
            except Exception as save_exc:failure['save_error']=repr(save_exc)
    finally:
        if r is not None:
            def final_evidence():
                durable_json(OUT/'ATTEMPT_LABELS.json',[x.to_dict() for x in r.attempts.values()])
                durable_json(OUT/'PUBLICATION_BRIDGE.json',p.publication_bridge)
                durable_json(OUT/'CLOSURES.json',r.closures)
                suffix=[json.loads(line) for line in (OUT/'DECISION_METRICS.jsonl').read_text().splitlines()] if (OUT/'DECISION_METRICS.jsonl').exists() else []
                merged=prefix_rows+suffix
                assert len({x['time'] for x in merged})==len(merged),'DUPLICATE_GRID'
                assert [x['time'] for x in merged]==[round(t*.1,10) for t in range(1,len(merged)+1)],'GRID_GAP'
                durable_json(OUT/'MERGED_DECISION_METRICS.json',merged)
                if parent_marker:
                    for name in ('DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):
                        suffix_bytes=(OUT/name).read_bytes();(OUT/('SUFFIX_'+name)).write_bytes(suffix_bytes)
                        limit=3225 if name=='PRIVATE_EXOGENOUS_PAIRING.jsonl' else 750
                        with (OLD/'fixed05'/name).open('rb') as stream:original_prefix=b''.join(next(stream) for _ in range(limit))
                        assert len(original_prefix.splitlines())==limit
                        (OUT/name).write_bytes(original_prefix+suffix_bytes)
                durable_json(OUT/'OPERATION_RECORDS.json',a.records)
            # Complete model/private pair already exists; reserve only final evidence, not another future checkpoint.
            old_reserve=a.reserve;a.reserve=0.
            try:a.operation('events',final_evidence,closing_capacity)
            except Exception as exc:
                if failure is None:failure=dict(error='FINAL_EVIDENCE_FAILED',detail=repr(exc));status='STARTED_PREFIX_INCOMPLETE'
            a.reserve=old_reserve
        durable_json(OUT/'EXECUTION_RESULT.json',dict(status=status,failure=failure,actual_SGD=r.backend.local_optimizer_steps if r else 0,GPU=0,q_fit=0,
            now=r.now if r else (75. if parent_marker else 0.),next_grid_tick=next_tick,last_complete_marker=str(last_marker) if last_marker else str(parent_marker),last_saved_time=last_saved*.1,
            parent_run_id=identity.get('clock_namespace',{}).get('run_id') if parent_marker else None,parent_checkpoint=str(parent_marker) if parent_marker else None,decision_start_tick=751 if parent_marker else 1,source_packages_changed=True,source_change_role='resource-only explicit authorization migration; original archive retained',strategy=STRATEGY,seed=45001,
            spent=a.spent,maxima=a.maxima,worker_PID=os.getpid(),session_id=OUT.name,state='WAITING_USER_REVIEW',physical_unknown_offset_upper=offset,physical_upper=(r.backend.local_optimizer_steps if r else (2493 if parent_marker else 0))+offset,root_final_audit='external .meter.json plus .worker_exit.json'))
    print(status);return 0 if status=='COMPLETE_T100_ACQUISITION' else 2
if __name__=='__main__':raise SystemExit(main())
