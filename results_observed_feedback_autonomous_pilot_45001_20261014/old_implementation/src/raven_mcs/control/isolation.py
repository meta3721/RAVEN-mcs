"""Killable planning worker with a two-CPU-second combined budget."""
from dataclasses import asdict, replace
import multiprocessing as mp
import os
import time
import traceback

from raven_mcs.control.schema import DecisionSnapshot, InputError
from raven_mcs.control.predictor import FrozenServiceModel
from raven_mcs.control.planner import Decision, fixed_fallback, validate_planning_inputs
from raven_mcs.control.process_budget import ProcessTreeBudget, wait_accounted


def _worker(connection, snapshot_payload, model_payload, test_fault):
    # Parent assigns the worker to a process-tree accounting Job before GO.
    if connection.recv()!='GO':return
    try:
        if test_fault=='burn_cpu':
            while True:
                sum(i*i for i in range(10000))
        from raven_mcs.control.planner import plan
        snapshot=DecisionSnapshot.from_dict(snapshot_payload)
        model=FrozenServiceModel.from_dict(model_payload)
        decision=plan(snapshot,model)
        connection.send(('ok',asdict(decision)))
    except Exception as exc:
        connection.send(('error',dict(type=type(exc).__name__,message=str(exc),trace=traceback.format_exc())))
    finally:connection.close()


class IsolatedController:
    def __init__(self):self.accounting=[]

    def decide(self,snapshot,model,*,test_fault=None):
        if test_fault is not None and (not snapshot.isolated_test or test_fault!='burn_cpu'):
            raise InputError("controlled fault only available in isolated tests")
        validate_planning_inputs(snapshot,model)
        wall=time.perf_counter();parent_cpu=time.process_time()
        if test_fault is None and (snapshot.now<=snapshot.config.warmup+1e-9 or
                snapshot.now-snapshot.window_open>=snapshot.config.deadline-1e-9):
            # These existing temporal rules do no scenario generation or P2.
            # Avoid spawning numerical workers solely to return the same rule.
            from raven_mcs.control.planner import plan
            decision=plan(snapshot,model)
            cpu=time.process_time()-parent_cpu
            if cpu>snapshot.config.planning_cpu_seconds:raise InputError('temporal rule CPU budget exceeded')
            record=dict(status='temporal_rule',child_tree_cpu_seconds=0.,parent_cpu_seconds=cpu,
                total_cpu_seconds=cpu,wall_seconds=time.perf_counter()-wall,exitcode=0,child_terminated=False,training_steps=0)
            self.accounting.append(record)
            return replace(decision,control_cpu_seconds=cpu,wall_seconds=record['wall_seconds'])
        context=mp.get_context('spawn'); parent,child=context.Pipe()
        process=context.Process(target=_worker,args=(child,asdict(snapshot),model.to_dict(),test_fault))
        budget=ProcessTreeBudget();status='not_started';decision=None;error=None
        try:
            # Numerical children must be single-threaded so the short sampling
            # reserve also bounds CPU across BLAS/solver threads.
            names=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')
            original={k:os.environ.get(k) for k in names}
            try:
                for k in names:os.environ[k]='1'
                process.start()
            finally:
                for k,v in original.items():
                    if v is None:os.environ.pop(k,None)
                    else:os.environ[k]=v
            child.close();budget.attach(process.pid);parent.send('GO')
            status=wait_accounted(process,budget,cpu_limit=snapshot.config.planning_cpu_seconds,
                                  parent_started=parent_cpu,wall_started=wall,pipe=parent)
            if status=='cpu_timeout':
                decision=fixed_fallback(snapshot,'CPU_TIMEOUT/fixed_time_2')
            elif status=='facility_stall':
                error=InputError("planning facility stalled; no valid action")
            elif parent.poll(.05):
                kind,payload=parent.recv()
                if kind=='error':error=InputError(f"{payload['type']}: {payload['message']}\n{payload['trace']}")
                else:
                    payload['plan_scores']=tuple(tuple(x) for x in payload['plan_scores'])
                    decision=Decision(**payload)
            else:error=InputError(f"planning worker exited without result: {process.exitcode}")
            # Native library cleanup can take wall time after sending a result.
            # Account it under the same CPU limit instead of imposing an
            # unrelated one-second exit deadline or allowing unmetered work.
            if process.is_alive():
                exit_status=wait_accounted(process,budget,
                    cpu_limit=snapshot.config.planning_cpu_seconds,
                    parent_started=parent_cpu,wall_started=wall)
                if exit_status=='cpu_timeout':
                    status=exit_status
                    if error is None:decision=fixed_fallback(snapshot,'CPU_TIMEOUT/fixed_time_2')
                elif exit_status=='facility_stall':
                    error=InputError('planning facility stalled during shutdown')
            process.join()
            cpu=budget.cpu_seconds()+time.process_time()-parent_cpu
            if cpu>snapshot.config.planning_cpu_seconds:
                error=InputError(f"planning CPU hard budget exceeded: {cpu:.6f}")
            record=dict(status=status,child_tree_cpu_seconds=budget.cpu_seconds(),
                parent_cpu_seconds=time.process_time()-parent_cpu,total_cpu_seconds=cpu,
                wall_seconds=time.perf_counter()-wall,exitcode=process.exitcode,
                child_terminated=status=='cpu_timeout',training_steps=0)
            self.accounting.append(record)
            if error is not None:raise error
            return replace(decision,control_cpu_seconds=cpu,wall_seconds=record['wall_seconds'])
        finally:
            if process.is_alive():
                budget.terminate();process.join(timeout=.2)
                if process.is_alive():process.terminate();process.join()
            parent.close();child.close();budget.close()

    def to_dict(self):return dict(accounting=self.accounting)
