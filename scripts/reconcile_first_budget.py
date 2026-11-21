"""Preserve raw counters; record the inner Job and unresolved CPU boundary."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1];out=root/'results_calibration_first_20261013'
budget=json.loads((out/'BUDGET.json').read_text(encoding='utf-8'))
result=json.loads((out/'FIRST_ACQUISITION_RESULT.json').read_text(encoding='utf-8'))
raw=next(x for x in budget['runs'] if x['log'].endswith('resume-first-same-spec.log'))
if raw['process_tree_cpu_seconds']!=0:raise RuntimeError('unexpected raw accounting')
if budget.get('supplemental_charges'):raise RuntimeError('budget already reconciled')
entry=dict(reason='raw outer Job=0 after self-owned inner Job; substitute persisted inner measurement, preserve raw record',
    source='FIRST_ACQUISITION_RESULT.json/resumed_segment_process_tree_cpu_seconds',
    measured_cpu_seconds=result['resumed_segment_process_tree_cpu_seconds'],
    unmeasured_startup_tail_reserve_seconds=120.,
    charged_cpu_seconds=result['resumed_segment_process_tree_cpu_seconds']+120.,
    actual_full_lifecycle_CPU='NOT_EXACTLY_RECONSTRUCTABLE',
    budget_gate='ACCOUNTING_BOUNDARY_PENDING_REVIEW',
    reserve_is_not_actual_CPU=True)
budget['supplemental_charges']=[entry]
(out/'BUDGET_RECONCILIATION.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'BUDGET.json').write_text(json.dumps(budget,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(entry))
