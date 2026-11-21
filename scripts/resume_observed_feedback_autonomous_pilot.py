"""Resume the actual stopped OF-v1 trajectory. No build(), fit, or new seed stream."""
import sys,json,os,time,traceback,hashlib,copy,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';PARENT=BATCH/'of';OUT=BATCH/'of_resume1'
import numpy as np,pandas as pd,torch
from types import SimpleNamespace
from datetime import datetime,timezone
from dataclasses import asdict
from observed_feedback_pilot_account import PilotAccount as RollingAccount
from raven_mcs_observed_feedback.schema import ControlConfig
from raven_mcs_observed_feedback.probability import DiagnosticPrior
from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization
from raven_mcs_observed_feedback.backend import connect_full_runner
from observed_feedback_pilot_common import AuditedProducer as CausalProducer
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
    a=RollingAccount(OUT);r=p=None;last_marker=None;next_tick=333;last_saved=332.9;last_sizes=None;previous_segment=None;status='RESUMPTION_NOT_STARTED';failure=None
    save_capacity=121.5559578169703;closing_capacity=15.331367;started_wall=time.perf_counter();wall_cap=float(os.environ['OF_ARM_WALL_LIMIT']);a.reserve=save_capacity+closing_capacity
    store=PairedCheckpointStore(OUT/'trajectory')
    parent_marker=Path(json.loads((PARENT/'EXECUTION_RESULT.json').read_text())['last_complete_marker'])
    freeze=json.loads((PARENT/'ARM_FROZEN_PLAN.json').read_text());identity=json.loads(parent_marker.read_text())['identity']
    original_closure=freeze['source_closure'];prefix_rows=[json.loads(line) for line in (PARENT/'DECISION_METRICS.jsonl').read_text().splitlines()]
    def append(name,obj):
        with (OUT/name).open('a',encoding='utf-8') as stream:stream.write(json.dumps(obj,allow_nan=False)+'\n')
    def restore_actual():
        assert original_closure==source_closure(),'FROZEN_COMPUTATIONAL_SOURCE_CHANGED'
        parent=PairedCheckpointStore(parent_marker.parent);packet,private=parent.read(parent_marker,expected_identity=identity)
        assert packet['source_closure']==original_closure
        (OUT/'PUBLIC_CATALOGUE.parquet').write_bytes((BATCH/'PUBLIC_CATALOGUE.parquet').read_bytes())
        inputs=load_inputs(ROOT,OUT)
        scope=freeze['scope'];assert inputs.data_id==scope['data_identity'] and inputs.target_id==scope['target_identity'],'DATA_OR_TARGET_IDENTITY_CHANGED'
        config=ControlConfig.from_dict(freeze['config']);b=packet['state']['backend']
        # Shape allocation on meta consumes no model-initialization RNG. Populate directly from actual saved tensors.
        with torch.device('meta'):model=CommonNDMF(num_spatial=len(inputs.clients))
        model.to_empty(device='cpu')
        reference=model.state_dict();actual={k:torch.tensor(v['values'],dtype=reference[k].dtype) for k,v in b['theta'].items()}
        model.load_state_dict(actual)
        owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('OF45001_ACTUAL_RESTORE',45001,100,len(inputs.clients))),dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,learning_rate=.01,seed=45001,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
        shape_holder=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45001,data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=scope,clock_namespace=freeze['clock_namespace'],calibration_only=True,collection_authorization=AutonomousPilotAuthorization('OF-v1'),root_budget=a.root)
        restored,priv=restore_pair(parent,parent_marker,identity=identity,backend=shape_holder.backend,expected_config=config,expected_data=inputs.data_id,expected_target=inputs.target_id,root_budget=a.root)
        producer=CausalProducer(inputs,restored,np.random.default_rng(0),np.random.default_rng(1),OUT);producer.restore(priv['state'])
        assert sha256_json(restored.checkpoint_state())==packet['state_hash']
        assert sha256_json(producer.to_dict())==sha256_json(private['state'])
        assert restored.now==packet['state']['now'] and restored.backend.local_optimizer_steps==1134 and priv['next_grid_tick']==333 and producer.active_registration is None
        assert len(prefix_rows)==332 and len(restored.decisions)==332
        producer.stop_after_steps=None;producer.pause_requested=None
        return restored,producer,dict(status='PASS',model_and_control_state_hash_equal=True,producer_and_RNG_state_hash_equal=True,source_closure_equal=True,
            data_identity_equal=True,target_identity_equal=True,restored_now=restored.now,restored_SGD=1134,model_version=restored.model_version,next_grid_tick=333,next_clock=producer.next_clock,next_client=producer.next_client,
            no_new_SGD_or_notices_before_equality=True,model_construction='meta shape allocation populated directly with saved actual tensors; no45001 initialization or RNG draws',
            parent_run_id=identity['clock_namespace']['run_id'],parent_checkpoint=str(parent_marker),decision_start_tick=333,
            session_id=OUT.name,worker_PID=os.getpid(),root_id=a.root.read()['root_id'],restore_UTC=datetime.now(timezone.utc).isoformat(),
            original_clock_namespace=freeze['clock_namespace'],wall_continuity='manual downtime excluded; continuation is logical/service trajectory only')
    def persist(name):
        nonlocal last_marker,last_saved,last_sizes,save_capacity,closing_capacity,previous_segment
        assert source_closure()==original_closure
        private=dict(T=100.,tick=r.now/.1,next_grid_tick=next_tick,clock_namespace=r.clock_namespace,state=p.to_dict(),
            parent_run_id=identity['clock_namespace']['run_id'],parent_checkpoint=str(parent_marker),decision_start_tick=333,
            account=dict(base=a.base,spent=a.spent,save_capacity=save_capacity,closing_capacity=closing_capacity),pilot_complete=True,
            rolling_previous_segment=previous_segment,session_id=OUT.name,worker_PID=os.getpid())
        marker=a.operation('save',lambda:save_pair(r,store,name,producer_state=private,budget=a.root,save_reserve=a.reserve),save_capacity)
        sizes=json.loads(marker.read_text())['sizes'];growth=max(1.,sum(sizes)/sum(last_sizes)) if last_sizes else 1.25
        last_sizes=sizes;last_marker=marker;last_saved=r.now/.1
        save_capacity=max(save_capacity,5.96875,2*a.maxima['save']*growth)
        closing_capacity=max(closing_capacity,8.,1.5*a.maxima['save']);a.reserve=save_capacity+closing_capacity
        append('SAVE_MEASUREMENTS.jsonl',dict(marker=str(marker),time=r.now,SGD=r.backend.local_optimizer_steps,sizes=sizes,measured_max_root_upper=a.maxima['save'],growth_factor=growth,save_capacity=save_capacity,closing_capacity=closing_capacity,total_reserve=a.reserve))
        return marker
    try:
        r,p,check=a.operation('initialization',restore_actual,80.)
        (OUT/'RESUMPTION_CHECK.json').write_text(json.dumps(check,indent=2));status='STARTED_PREFIX_INCOMPLETE';last_marker=parent_marker
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
            if category=='training' and r.backend.local_optimizer_steps>=5000:raise RuntimeError('CUMULATIVE_PHYSICAL_SGD_LIMIT')
            return original_operation(category,fn,ceiling,online)
        p.operation=guarded_operation
        control=Controller('OF-v1',root_budget=a.root,save_reserve=a.reserve,operation_root_ceiling=2.)
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
                shadow=shadow_actions(context['shadow'],d)
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
                    (OUT/'PROGRESS.json').write_text(json.dumps(dict(time=r.now,SGD=r.backend.local_optimizer_steps,grid=next_tick-1,registrations=len(r.attempts),model_version=r.model_version,root_batch_CPU=a.root.read()['batch_used'],remaining_effective_CPU=a.root.read()['effective_remaining'],reserve=a.reserve,forecast_warning=value['warning'],last_complete_marker=str(last_marker)),indent=2))
                a.operation('events',summary)
            if a.root.read()['effective_remaining']<a.reserve+4.:raise RuntimeError('ACTUAL_HEADROOM_INSUFFICIENT_SAVE_AND_STOP')
        assert r.ended and r.now==100. and next_tick==1001 and p.next_clock==100 and p.active_registration is None
        assert r.backend.local_optimizer_steps<=5000 and len(r.decisions)==1000
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
                (OUT/'ARM_FROZEN_PLAN.json').write_bytes((PARENT/'ARM_FROZEN_PLAN.json').read_bytes())
                (OUT/'ARM_INITIAL_CHECK.json').write_bytes((PARENT/'ARM_INITIAL_CHECK.json').read_bytes())
                (OUT/'ATTEMPT_LABELS.json').write_text(json.dumps([x.to_dict() for x in r.attempts.values()],allow_nan=False))
                (OUT/'PUBLICATION_BRIDGE.json').write_text(json.dumps(p.publication_bridge))
                (OUT/'CLOSURES.json').write_text(json.dumps(r.closures))
                suffix=[json.loads(line) for line in (OUT/'DECISION_METRICS.jsonl').read_text().splitlines()] if (OUT/'DECISION_METRICS.jsonl').exists() else []
                merged=prefix_rows+suffix
                assert len({x['time'] for x in merged})==len(merged),'DUPLICATE_GRID'
                assert [x['time'] for x in merged]==[round(t*.1,10) for t in range(1,len(merged)+1)],'GRID_GAP'
                (OUT/'MERGED_DECISION_METRICS.json').write_text(json.dumps(merged))
                for name in ('DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):
                    suffix=(OUT/name).read_bytes();(OUT/('SUFFIX_'+name)).write_bytes(suffix);(OUT/name).write_bytes((PARENT/name).read_bytes()+suffix)
                (OUT/'OPERATION_RECORDS.json').write_text(json.dumps(a.records))
            # Complete model/private pair already exists; reserve only final evidence, not another future checkpoint.
            old_reserve=a.reserve;a.reserve=0.
            try:a.operation('events',final_evidence,closing_capacity)
            except Exception as exc:
                if failure is None:failure=dict(error='FINAL_EVIDENCE_FAILED',detail=repr(exc));status='STARTED_PREFIX_INCOMPLETE'
            a.reserve=old_reserve
        (OUT/'EXECUTION_RESULT.json').write_text(json.dumps(dict(status=status,failure=failure,actual_SGD=r.backend.local_optimizer_steps if r else 1134,GPU=0,q_fit=0,
            now=r.now if r else 33.29,next_grid_tick=next_tick,last_complete_marker=str(last_marker) if last_marker else str(parent_marker),last_saved_time=last_saved*.1,
            parent_run_id=identity['clock_namespace']['run_id'],parent_checkpoint=str(parent_marker),decision_start_tick=333,source_packages_changed=False,strategy='OF-v1',seed=45001,
            spent=a.spent,maxima=a.maxima,worker_PID=os.getpid(),session_id=OUT.name,state='WAITING_USER_REVIEW'),indent=2))
    print(status);return 0 if status=='COMPLETE_T100_ACQUISITION' else 2
if __name__=='__main__':raise SystemExit(main())
