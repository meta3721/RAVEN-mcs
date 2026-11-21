"""Revision worker, suspended-start full-tree CPU meter, no training entry."""
from dataclasses import asdict, replace
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time

from .schema import InputError
from .planner import Decision, fixed_fallback, validate_planning_inputs


class IsolatedController:
    def __init__(self):self.accounting=[]

    def decide(self,snapshot,model,*,isolated_scenarios=None):
        wall=time.perf_counter();cpu0=time.process_time()
        validate_planning_inputs(snapshot,model)
        if isolated_scenarios is not None and not snapshot.isolated_test:
            raise InputError('explicit test scenarios forbidden in production')
        root=Path(__file__).resolve().parents[2]
        spec=importlib.util.spec_from_file_location('revision_windows_meter',root/'scripts/windows_cpu_meter.py')
        meter=importlib.util.module_from_spec(spec);spec.loader.exec_module(meter)
        with tempfile.TemporaryDirectory(prefix='RE_interval_') as td:
            path=Path(td);request=path/'input.json';response=path/'output.json'
            request.write_text(json.dumps(dict(snapshot=asdict(snapshot),model=model.to_dict(),
                scenarios=None if isolated_scenarios is None else [s.to_dict() for s in isolated_scenarios]),allow_nan=False))
            allowance=2-(time.process_time()-cpu0)-.05
            if allowance<=.2:
                result=fixed_fallback(snapshot,'CPU_TIMEOUT/fixed_time_2');record=dict(status='parent_cpu_timeout',process_tree_cpu_seconds=0.)
            else:
                record=meter.run_metered([sys.executable,'-m','raven_mcs_re_interval.worker',str(request),str(response)],
                    path/'worker.log',cpu_limit=allowance,wall_limit=60,cwd=root)
                if not record['audit_passed']:raise InputError('planning process-tree accounting failed')
                if record['limit_reason']=='wall':raise InputError('planning facility stalled')
                if record['limit_reason']=='cpu':result=fixed_fallback(snapshot,'CPU_TIMEOUT/fixed_time_2')
                elif record['returncode']!=0:
                    raise InputError('planning worker failed: '+(path/'worker.log').read_text(errors='replace'))
                else:
                    payload=json.loads(response.read_text());result=Decision(**payload)
        cpu=record['process_tree_cpu_seconds']+time.process_time()-cpu0
        record.update(total_cpu_seconds=cpu,decision_wall_seconds=time.perf_counter()-wall,
            training_steps=0,startup_included=True,method='RE_interval_v3')
        self.accounting.append(record)
        if cpu>2:raise InputError(f'planning CPU hard budget exceeded: {cpu}')
        return replace(result,control_cpu_seconds=cpu,wall_seconds=record['decision_wall_seconds'])

    def to_dict(self):return dict(accounting=self.accounting)
