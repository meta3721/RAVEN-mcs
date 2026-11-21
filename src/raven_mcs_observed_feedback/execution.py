"""The single authorized causal acquisition loop; no fitting or comparison run."""
import csv,json,os,time,traceback,copy
from pathlib import Path
from types import SimpleNamespace
from dataclasses import asdict
from .acquisition import build
from .accounting import CategoryAccountant,BudgetStop
from .controller import Controller
from .diagnostic import shadow_actions
from .persistence import save_pair,restore_pair,source_closure
from . import METHOD_VERSION
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
from raven_mcs_execution.budget import checkpoint_due

def frozen_shadow_context(r):
    return SimpleNamespace(**{k:getattr(r,k) for k in ('calibration_only','isolated_test','collection_authorization','seed','config','now','window_open')})

def run(root,out):
    account=CategoryAccountant(out);r=None;p=None;last_marker=None;last_saved_tick=0;next_grid_tick=1;pilot=False;pilot_base=None;pilot_plan=None
    store=PairedCheckpointStore(out/'trajectory');status='NOT_STARTED';failure=None
    def append(name,value):
        with (out/name).open('a',encoding='utf-8') as f:f.write(json.dumps(value,allow_nan=False)+'\n')
    def persist(name):
        nonlocal last_marker,last_saved_tick
        private=dict(T=100.,tick=r.now/.1,next_grid_tick=next_grid_tick,clock_namespace=r.clock_namespace,state=p.to_dict(),
            account=dict(base=account.base,spent=account.spent,reserve=account.reserve),pilot_complete=pilot,pilot_plan=pilot_plan,worker_PID=os.getpid())
        marker=account.operation('save',lambda:save_pair(r,store,name,producer_state=private,budget=account.root,save_reserve=account.reserve),account.reserve)
        last_marker=marker;last_saved_tick=r.now/.1
        save_max=account.maxima['save'];account.reserve=max(account.reserve,2*save_max,5.96875)
        sizes=json.loads(marker.read_text())['sizes']
        append('SAVE_MEASUREMENTS.jsonl',dict(marker=str(marker),logical_time=r.now,actual_SGD=r.backend.local_optimizer_steps,sizes=sizes,reserve=account.reserve,root_upper=save_max))
        return marker
    def pilot_estimate():
        nonlocal pilot_plan
        remaining_reg=(100-p.next_clock)*len(p.inputs.clients)-p.next_client
        remaining_grid=1001-next_grid_tick
        train_max=account.maxima.get('training',0.)
        # Plans only. Future conic/queue/history growth is not a probability bound.
        online_max=max(account.maxima.get('online',0.),.270000)
        event_max=max(account.maxima.get('events',0.),.02)
        save_max=account.maxima.get('save',0.)
        estimates=dict(training=2*train_max*remaining_reg,online=2*online_max*remaining_grid,
            events=2*event_max*(3*remaining_reg+remaining_grid),save=2*save_max*(1+(1000-next_grid_tick)//50)*3)
        available=account.root.read()['effective_remaining']
        pilot_plan=dict(time=r.now,actual_SGD=r.backend.local_optimizer_steps,remaining_registrations=remaining_reg,remaining_grids=remaining_grid,
            maximum_observed_local_SGD_CPU=max([x['CPU'] for x in p.training_samples],default=0.),root_maxima=account.maxima.copy(),
            estimated_remaining_CPU=estimates,available_root_CPU=available,save_reserve=account.reserve,
            allowed=sum(estimates.values())+account.reserve<=available,limitations='32 steps/60 root CPU warmup prefix; later solver, queue and history growth unobserved; 3x save-growth planning allowance is not a bound')
        (out/'PILOT_COST_PLAN.json').write_text(json.dumps(pilot_plan,indent=2))
    try:
        inputs,r,p,freeze=account.operation('initialization',lambda:build(root,out,account.root),120.)
        freeze.update(worker_PID=os.getpid(),real_executable=__import__('sys').executable,root_id=account.root.read()['root_id'],source_closure=source_closure(),
            actual_online_boundary='fresh root start -> admission -> advance/grid snapshot/Controller/full P2/apply/model/debt/variance/consume/endpoint -> fresh root end; shadow, p-after-close and diagnostics separately metered',
            batch_used_before_execution=sum(account.base.values()),plan_roles='category amounts are planning warnings under continuation addendum; total3600, SGD5000 and actual requests2 remain hard')
        with (out/'ACQUISITION_FROZEN_PLAN.json').open('x') as f:json.dump(freeze,f,indent=2)
        append('WORKER_READY.jsonl',dict(PID=os.getpid(),actual_interpreter=True,root_id=freeze['root_id'],logical=0.,q_role='diagnostic_prior',GPU=0))
        p.operation=account.operation
        persist('tick0000_initial');status='STARTED_PREFIX_INCOMPLETE';pilot_base=account.root.read()['command_used']
        p.stop_after_steps=32;p.pause_requested=lambda: not pilot and account.root.read()['command_used']-pilot_base>=60.
        controller=Controller(root_budget=account.root,save_reserve=account.reserve,operation_root_ceiling=2.)
        while next_grid_tick<=1000:
            at=round(next_grid_tick*.1,10)
            ready=p.notices_through(at)
            if not ready:
                if pilot:raise RuntimeError('unexpected producer pause')
                # Partial-grid point keeps the next grid cursor, all completed registrations and pending notices.
                persist('pilot_prefix');pilot_estimate();pilot=True
                persist('pilot_complete')
                if not pilot_plan['allowed']:raise BudgetStop('PILOT_REMAINING_COST_PLAN_EXCEEDS_AVAILABLE_TOTAL')
                p.stop_after_steps=None;p.pause_requested=None
                continue
            context={}
            def pre():
                r.advance_time(at);s=r.snapshot();context['snapshot']=asdict(s);context['fingerprint']=s.fingerprint
                context['shadow']=frozen_shadow_context(r);context['window_id']=r.window_id
            account.operation('events',pre)
            controller.save_reserve=account.reserve
            d=account.operation('online',lambda:r.on_grid(at,controller),2.,online=True)
            def diagnostics():
                shadow=shadow_actions(context['shadow'],d)
                if len(r.consumed)!=sum(rec.consumed==1 for rec in r.attempts.values()):raise RuntimeError('CONSUMPTION_COUNT_MISMATCH')
                append('DECISION_SNAPSHOTS.jsonl',dict(time=at,fingerprint=context['fingerprint'],snapshot=context['snapshot']))
                row=dict(time=at,window=context['window_id'],snapshot_hash=context['fingerprint'],P=len(context['snapshot']['pool']),F=len(context['snapshot']['in_flight']),
                    action=d.action,reason=d.reason,B=d.B,components=dict(d.components),preview=d.preview.to_dict() if d.preview else None,
                    p2_solves=d.p2_solves,cache_hits=d.cache_hits,shadow=shadow,model_version_after=r.model_version,
                    actual_request_root_upper=account.records[-1]['root_upper_CPU'],actual_request_root_difference=account.records[-1]['request_root_difference'])
                append('DECISION_METRICS.jsonl',row)
                if r.window_id!=context['window_id']:p.after_close();p.reclaim_terminal_storage()
            account.operation('events',diagnostics)
            next_grid_tick+=1
            remaining=account.root.read()['effective_remaining']
            if next_grid_tick==1001 or checkpoint_due(next_grid_tick-1,last_saved_tick,remaining=remaining,save_reserve=account.reserve,operation_root_ceiling=2.):
                persist('tick%04d'%(next_grid_tick-1))
            if remaining<account.reserve+8.:raise BudgetStop('NEAR_TOTAL_BUDGET_SAVE_AND_STOP')
        assert r.ended and r.now==100 and next_grid_tick==1001
        status='COMPLETE_T100_ACQUISITION'
    except Exception as exc:
        failure=dict(error=repr(exc),traceback=traceback.format_exc(),logical_time=r.now if r else None,root_used=account.root.read().get('batch_used'))
        if r is not None and r.fault is None and not r.ended:
            try:
                # Censor only the saved observation prefix; resumption may resolve censoring later.
                r.finish_observation();persist('stopped_%04d_%04d'%(next_grid_tick,len(account.records)))
            except Exception as save_exc:failure['save_error']=repr(save_exc)
    finally:
        if r is not None:
            def final_evidence():
                (out/'ATTEMPT_LABELS.json').write_text(json.dumps([rec.to_dict() for rec in r.attempts.values()],allow_nan=False))
                (out/'PUBLICATION_BRIDGE.json').write_text(json.dumps(p.publication_bridge))
            try:account.operation('events',final_evidence,2.)
            except Exception as exc:
                if failure is None:failure=dict(error='FINAL_EVIDENCE_FAILED',detail=repr(exc));status='STARTED_PREFIX_INCOMPLETE'
            count=r.backend.local_optimizer_steps
        else:count=0
        (out/'EXECUTION_RESULT.json').write_text(json.dumps(dict(status=status,failure=failure,actual_SGD=count,GPU=0,q_fit=0,
            now=r.now if r else None,next_grid_tick=next_grid_tick,pilot=pilot,pilot_plan=pilot_plan,last_complete_marker=str(last_marker) if last_marker else None,
            last_saved_logical_time=last_saved_tick*.1,spent=account.spent,maxima=account.maxima,worker_PID=os.getpid(),state='WAITING_USER_REVIEW'),indent=2))
    return status
